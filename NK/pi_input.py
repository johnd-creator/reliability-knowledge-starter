"""Read stored PI snapshots through the collector API. No source or DB writes."""
from __future__ import annotations
import json
import math
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
import yaml

ROOT = Path(__file__).resolve().parent
FEATURES = ['Gross Load', 'PS', 'Coal flow', 'SFC', 'Main Steam Press', 'Main Steam Temp', 'Main Steam Flow', 'Economizer Inlet Temp', 'APH A In O2', 'APH A in flue gas temp', 'Condensor Vacuum', 'Feedwater Flow', 'Total Air Flow']

class InputError(ValueError):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise InputError('Collector mengalihkan request; periksa alamat API.')

@dataclass(frozen=True)
class Settings:
    api_base: str = 'http://127.0.0.1:8001'
    timeout: int = 10
    max_age: int = 900
    max_skew: int = 300
    refresh: int = 60
    @classmethod
    def load(cls):
        env = {}
        path = ROOT / '.env'
        if path.exists():
            for line in path.read_text().splitlines():
                if '=' in line and not line.lstrip().startswith('#'):
                    k, v = line.split('=', 1); env[k.strip()] = v.strip().strip('\"\'')
        def get(key, default): return os.environ.get(key, env.get(key, default))
        s = cls(get('PI_COLLECTOR_API_BASE', cls.api_base), int(get('NK_PI_TIMEOUT_SECONDS', '10')), int(get('NK_PI_MAX_AGE_SECONDS','900')), int(get('NK_PI_MAX_SKEW_SECONDS','300')), int(get('NK_PI_REFRESH_SECONDS','60')))
        u = urlsplit(s.api_base)
        if u.scheme not in ('http','https') or not u.hostname or u.username or u.password or u.query or u.fragment:
            raise InputError('Alamat PI Collector tidak valid.')
        if min(s.timeout,s.max_age,s.refresh) < 1 or s.max_skew < 0:
            raise InputError('Batas waktu konfigurasi NK tidak valid.')
        return s

class CollectorReader:
    def __init__(self, settings): self.settings = settings
    def get(self, path):
        try:
            req = Request(self.settings.api_base.rstrip('/') + path, method='GET', headers={'Accept':'application/json'})
            with build_opener(NoRedirect()).open(req, timeout=self.settings.timeout) as response:
                data = response.read(2_097_153)
            if len(data) > 2_097_152: raise InputError('Respons collector terlalu besar.')
            return json.loads(data)
        except InputError: raise
        except Exception as ex: raise InputError('PI Collector tidak dapat dibaca ('+type(ex).__name__+').') from None
    def read(self):
        attrs, snaps = self.get('/attributes'), self.get('/snapshots?limit=5000')
        if not isinstance(attrs,list) or not isinstance(snaps,list): raise InputError('Format respons collector tidak sesuai.')
        for records in (attrs, snaps):
            ids = [r.get('attribute_id') for r in records if isinstance(r,dict)]
            if len(ids)!=len(records) or any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
                raise InputError('Identitas atribut collector tidak valid atau duplikat.')
        return attrs, snaps


def verified_registry():
    path = ROOT.parent / 'pi-knowledge/mappings/bsr1-parameters.yaml'
    data = yaml.safe_load(path.read_text())
    result = {}
    def slug(s): return re.sub('[^a-z0-9]+','_',s.lower()).strip('_')
    for eq, group in data['equipment'].items():
        for parameter, entries in group['parameters'].items():
            for e in entries:
                if e.get('status')!='verified' or e.get('stream_status')!='ok' or not e.get('web_id'): continue
                parts=[data['site'],data['unit'],slug(eq),parameter,slug(e['name'])]
                if e.get('position'): parts.append(slug(e['position']))
                result['-'.join(parts)]={**e,'equipment':eq}
    return result


def load_mapping():
    data = json.loads((ROOT/'pi_feature_mapping.json').read_text())
    if not isinstance(data,dict) or not isinstance(data.get('features'),dict) or list(data['features']) != FEATURES:
        raise InputError('Urutan fitur pemetaan tidak cocok dengan model.')
    if any(not isinstance(m,dict) for m in data['features'].values()):
        raise InputError('Format pemetaan fitur tidak valid.')
    return data


def convert(value, source, target):
    aliases={'degC':'°C','C':'°C','MPa':'MPa','kPa':'kPa','kpa':'kPa','bar':'bar','MW':'MW','t/h':'t/h','%':'%','kg/kWh':'kg/kWh','mmHg':'mmHg'}
    source, target=aliases.get(source,source), aliases.get(target,target)
    if not source or not target: raise InputError('Satuan sumber/training belum dikonfirmasi.')
    if source == target: return value
    pressure={'kPa':1,'MPa':1000,'bar':100,'mmHg':0.133322368}
    if source in pressure and target in pressure: return value * pressure[source] / pressure[target]
    raise InputError('Konversi satuan belum didukung.')

@dataclass
class FeatureBatch:
    rows: list
    values: list | None
    errors: list


def build_features(mapping, attrs, snapshots, settings, registry=None, now=None):
    registry = verified_registry() if registry is None else registry
    now = now or datetime.now(timezone.utc)
    attr_by_id={a['attribute_id']:a for a in attrs}
    snap_by_id={s['attribute_id']:s for s in snapshots}
    rows=[]; errors=[]; values=[]; timestamps=[]
    for feature in FEATURES:
        m=mapping['features'][feature]; ident=m.get('attribute_id'); a=attr_by_id.get(ident); s=snap_by_id.get(ident)
        row={'Fitur':feature,'Atribut':ident or 'Belum dipetakan','Nilai':None,'Satuan':m.get('training_unit',''),'Waktu sumber':'','Status':''}
        try:
            if m.get('status')!='verified' or not m.get('evidence_ref','').strip(): raise InputError('Pemetaan dan satuan training belum dikonfirmasi.')
            known=registry.get(ident)
            if not known or not a or a.get('web_id')!=known['web_id']: raise InputError('Atribut tidak cocok dengan registry PI terverifikasi.')
            if not s: raise InputError('Snapshot belum tersedia.')
            if s.get('value_good') is not True or any(s.get(k) is not False for k in ('value_questionable','value_substituted')):
                raise InputError('Kualitas snapshot buruk atau belum diketahui.')
            v=s.get('value')
            if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v): raise InputError('Nilai bukan angka valid.')
            stamp_text=s.get('source_timestamp')
            if not isinstance(stamp_text,str): raise InputError('Timestamp sumber belum tersedia.')
            stamp=datetime.fromisoformat(stamp_text.replace('Z','+00:00'))
            if stamp.tzinfo is None: raise InputError('Timestamp sumber tanpa timezone.')
            age=(now-stamp).total_seconds()
            if age < -5 or age>settings.max_age: raise InputError('Data kedaluwarsa atau timestamp di masa depan.')
            observed_unit=s.get('units') or a.get('unit_of_measure') or known.get('unit')
            source=m.get('source_unit','')
            if observed_unit and observed_unit!=source: raise InputError('Satuan snapshot berbeda dengan pemetaan.')
            if not observed_unit and not m.get('source_unit_confirmed'): raise InputError('Satuan sumber belum dikonfirmasi.')
            value=convert(v,source,m.get('training_unit',''))
            if not math.isfinite(value): raise InputError('Hasil konversi bukan angka valid.')
            row.update({'Nilai':value,'Waktu sumber':stamp.isoformat(),'Status':'OK'})
            values.append(value);timestamps.append(stamp)
        except (InputError,ValueError,TypeError) as ex:
            message=str(ex) if isinstance(ex,InputError) else 'Timestamp atau pemetaan tidak valid.'
            row['Status']=message;errors.append(feature+': '+message)
        rows.append(row)
    if timestamps and (max(timestamps)-min(timestamps)).total_seconds()>settings.max_skew:
        errors.append('Waktu sumber antarfitur terlalu berjauhan.')
    return FeatureBatch(rows,values if not errors else None,errors)
