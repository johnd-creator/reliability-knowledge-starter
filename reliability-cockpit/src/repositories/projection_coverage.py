"""Disabled B4 reader: explicit existing Mart engine, bounded SELECT-only snapshot.

No writer/admin, Collector implementation, source client, cursor, environment
fallback or API import. Capability fingerprints are reviewed against 004/005/006.
Only aggregate counts and run UUIDs leave this internal repository.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import time
import uuid
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.domain.projection_coverage import (Activity,CoverageSnapshot,DomainCoverage,DOMAINS,
    MANIFEST_FIELDS,DEBT_FIELDS,REPLAY_FIELDS)
from src.repositories.mart_database import MartDatabase

EPOCH='contract1.0-local-mapper-b1-v1'
POLICY='deferred-v1-BSR-IP-WO-BSR'
REPLAY='replay-v1-exact-id'
SCOPE={'source':'MAXIMO','site':'BSR','organization':'IP','wo_prefixes':['BSR']}
TABLES=('mart_capture_domain','mart_capture_run','mart_capture_item','mart_capture_target',
        'mart_deferred_family','mart_deferred_version','mart_deferred_dependency','mart_deferred_event',
        'mart_deferred_occurrence','mart_replay_queue','mart_replay_event')
ACTIVE=('OPEN','ELIGIBLE_FOR_RETRY','BLOCKED_NEEDS_REVIEW')
TERMINAL=('PROJECTED','UNCHANGED','EXPECTED_EXCLUSION')
# Pinned from the reviewed B3 fixture, including functions/columns/indexes/triggers.
CATALOG_SIGNATURE='c36d02ad2f137456ee38d247c23c0d0ad0519a676f3098359c70e96c70a40afa'
# B5: exact 001→006 SQL canonical indexes differ from ORM create_all.
# Both reviewed complete catalogs remain pinned; no index/guard is ignored.
SQL_CATALOG_SIGNATURE='45e77c7cc8b51de1d10d5e77d29a84607b0f5fbcbc657361e94559d65e25d6a2'
REVIEWED_CATALOGS=frozenset((CATALOG_SIGNATURE,SQL_CATALOG_SIGNATURE))
DEFAULT_REPLAY_DIGEST='a1a514e98b9d0f239db10b1f0bbd147bfba3474d837bcc774ac527dff6fa5d08'

class EvidenceUnavailable(RuntimeError):
    pass

@dataclass(frozen=True)
class CoverageLimits:
    rows: int = 1000
    runs: int = 32
    seconds: int = 5
    queries: int = 64
    bytes: int = 4*1024*1024

    def __post_init__(self):
        values=(self.rows,self.runs,self.seconds,self.queries,self.bytes)
        if any(type(v) is not int for v in values) or not (1<=self.rows<=2000 and 1<=self.runs<=64
            and 1<=self.seconds<=10 and 16<=self.queries<=128 and 8192<=self.bytes<=8*1024*1024):
            raise ValueError('invalid bounded coverage limits')

def encode(value):
    def scalar(v):
        if isinstance(v,datetime): return v.astimezone(timezone.utc).isoformat()
        raise TypeError('invalid evidence scalar')
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,
                      allow_nan=False,default=scalar).encode()

class BoundedRead:
    def __init__(self,s,limits):
        self.s=s; self.limits=limits; self.deadline=time.monotonic()+limits.seconds
        self.queries=1; self.bytes=0
        self.statement_timeout_ms=int(s.scalar(text("SELECT setting::int FROM pg_settings WHERE name='statement_timeout'")))
        if self.statement_timeout_ms<=0: raise EvidenceUnavailable('TIMEOUT_UNVERIFIED')

    def rows(self,sql,params=None,limit=None):
        remaining=self.deadline-time.monotonic(); self.queries+=1
        if remaining<=0 or self.queries>self.limits.queries: raise EvidenceUnavailable('EVIDENCE_LIMIT')
        self.s.execute(text("SELECT set_config('statement_timeout',:v,true)"),{'v':str(min(self.statement_timeout_ms,max(1,int(remaining*1000))))})
        cap=self.limits.rows if limit is None else limit
        result=[dict(r) for r in self.s.execute(text(sql+' LIMIT :_bound'),dict(params or {},_bound=cap+1)).mappings()]
        if len(result)>cap: raise EvidenceUnavailable('EVIDENCE_LIMIT')
        self.bytes+=len(encode(result))
        if self.bytes>self.limits.bytes or time.monotonic()>self.deadline: raise EvidenceUnavailable('EVIDENCE_LIMIT')
        return result


def catalog_signature(b):
    params={'tables':list(TABLES)+list(DOMAINS)}
    columns=b.rows('''SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod) AS type,
        a.attnotnull FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
        WHERE c.relnamespace=current_schema()::regnamespace AND c.relname=ANY(:tables)
        AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum''',params,limit=1000)
    constraints=b.rows('''SELECT r.relname,c.conname,c.contype,pg_get_constraintdef(c.oid) AS definition
        FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid
        WHERE r.relnamespace=current_schema()::regnamespace AND r.relname=ANY(:tables)
        AND c.contype<>'n' ORDER BY r.relname,c.conname''',params,limit=1000)
    indexes=b.rows('''SELECT tablename,indexname,indexdef AS definition FROM pg_indexes
        WHERE schemaname=current_schema() AND tablename=ANY(:tables) ORDER BY tablename,indexname''',params,limit=1000)
    triggers=b.rows('''SELECT c.relname,t.tgname,t.tgtype,t.tgenabled,t.tgdeferrable,t.tginitdeferred,
        p.proname FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_proc p ON p.oid=t.tgfoid
        WHERE c.relnamespace=current_schema()::regnamespace AND c.relname=ANY(:tables)
        AND NOT t.tgisinternal ORDER BY c.relname,t.tgname''',params,limit=1000)
    functions=b.rows('''SELECT p.proname,p.prosrc,p.prosecdef,p.provolatile,p.proconfig FROM pg_proc p
        JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname=current_schema()
        AND p.proname IN ('mart_capture_item_guard','mart_capture_run_guard','mart_deferred_append_only',
        'mart_deferred_audit_guard','mart_deferred_family_guard','mart_deferred_version_guard',
        'mart_replay_queue_guard','mart_replay_audit_guard') ORDER BY p.proname''',limit=1000)
    schema=b.rows('SELECT current_schema() AS name',limit=1)[0]['name']
    data=[columns,constraints,indexes,triggers,functions]
    # Schema qualifier differences in private fixtures are not capability changes.
    for group in data:
        for row in group:
            if 'definition' in row:
                row['definition']=row['definition'].replace('"'+schema+'".','CAPTURE_SCHEMA.').replace(schema+'.','CAPTURE_SCHEMA.')
    if set(r['relname'] for r in columns)!=set(TABLES)|set(DOMAINS): raise EvidenceUnavailable('CAPABILITY_MISSING')
    return hashlib.sha256(encode(data)).hexdigest()

class ProjectionCoverageReader:
    def __init__(self,database=None,*,enabled=False,expected_database=None,limits=None,
                 replay_digest=DEFAULT_REPLAY_DIGEST,policy_expires_at=None,clock=None):
        self.database=database; self.enabled=enabled is True; self.expected_database=expected_database
        self.limits=limits or CoverageLimits(); self.replay_digest=replay_digest
        if policy_expires_at is not None and policy_expires_at.tzinfo is None:
            raise ValueError('aware evidence policy expiry required')
        self.policy_expires_at=policy_expires_at
        self.clock=clock or (lambda:datetime.now(timezone.utc))

    def read(self):
        now=self.clock()
        if not self.enabled: return CoverageSnapshot.unknown(now,'DISABLED','DISABLED')
        if self.database is None: return CoverageSnapshot.unknown(now,'MART_NOT_CONFIGURED','NOT_CONFIGURED')
        if (not isinstance(self.database,MartDatabase) or not self.expected_database or
                self.database.engine.dialect.name!='postgresql'):
            return CoverageSnapshot.unknown(now,'DATABASE_IDENTITY_UNVERIFIED')
        if self.policy_expires_at is not None and now>=self.policy_expires_at:
            return CoverageSnapshot.unknown(now,'POLICY_EXPIRED','BLOCKED')
        try:
            with self.database.read_snapshot() as s:
                b=BoundedRead(s,self.limits)
                identity=b.rows("SELECT current_database() AS db,current_setting('transaction_read_only') AS ro",limit=1)[0]
                if identity!={'db':self.expected_database,'ro':'on'}:
                    return CoverageSnapshot.unknown(now,'DATABASE_IDENTITY_UNVERIFIED')
                role=b.rows('''SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles
                    WHERE rolname=current_user''',limit=1)[0]
                privileges=b.rows('''SELECT c.relname,has_table_privilege(current_user,c.oid,
                    'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR
                    has_any_column_privilege(current_user,c.oid,'INSERT,UPDATE,REFERENCES') AS writable FROM pg_class c
                    WHERE c.relnamespace=current_schema()::regnamespace
                    AND c.relname=ANY(:tables)''',{'tables':list(TABLES)+list(DOMAINS)},limit=64)
                authority=b.rows('''SELECT has_schema_privilege(current_user,current_schema(),'CREATE') AS schema_create,
                    has_database_privilege(current_user,current_database(),'CREATE,TEMPORARY') AS db_create''',limit=1)[0]
                if any(role.values()) or any(authority.values()) or any(p['writable'] for p in privileges):
                    return CoverageSnapshot.unknown(now,'READER_ROLE_UNVERIFIED','BLOCKED')
                if catalog_signature(b) not in REVIEWED_CATALOGS:
                    return CoverageSnapshot.unknown(now,'CAPABILITY_DRIFT','BLOCKED')
                domains=[]
                for domain in DOMAINS:
                    domains.append(self._domain(b,domain,now))
                return CoverageSnapshot(now,'VERIFIED',tuple(domains))
        except EvidenceUnavailable as error:
            return CoverageSnapshot.unknown(now,str(error),'BLOCKED' if str(error) in ('DEBT_SCOPE_UNVERIFIED','INCOMPATIBLE_EPOCH') else 'UNKNOWN')
        except (SQLAlchemyError,ValueError,KeyError,TypeError):
            # Never return driver messages, payloads, DSNs or private identities.
            return CoverageSnapshot.unknown(now,'EVIDENCE_UNAVAILABLE')

    @staticmethod
    def _activity(run):
        mode='FULL' if run['scope']==SCOPE else 'RECOVERY_BY_ID'
        return Activity(str(uuid.UUID(run['id'])),run['status'],run['started_at'],run['completed_at'],
                        mode,run['sealed'],run['continuation'])

    def _targets(self,b,domain,receipts):
        ids=list({r['target_id'] for r in receipts if r['target_id'] is not None})
        if not ids: return
        # Table name is from fixed DOMAINS only. Row JSON is byte-capped in SQL;
        # canonical values stay private and are used only to recheck B1 digest.
        rows=b.rows(f'''SELECT canonical_id,CASE WHEN octet_length(to_jsonb(t)::text)<=8192
            THEN to_jsonb(t) ELSE NULL END AS record FROM {domain} t
            WHERE canonical_id=ANY(:ids) AND site_code='BSR' AND organization_code='IP' ''',{'ids':ids})
        actual={}
        times={'source_updated_at','source_changed_at','actual_start','actual_finish','mart_created_at','mart_updated_at'}
        floats={'duration_hours','labor_hours','downtime_hours'}
        for row in rows:
            record=row['record']
            if record is None: raise EvidenceUnavailable('EVIDENCE_LIMIT')
            for key in times & record.keys():
                if record[key] is not None: record[key]=datetime.fromisoformat(record[key])
            for key in floats & record.keys():
                if record[key] is not None: record[key]=float(record[key])
            actual[row['canonical_id']]=hashlib.sha256(encode(record)).hexdigest()
        sidecars=b.rows('''SELECT canonical_id,target_digest FROM mart_capture_target
            WHERE domain=:domain AND canonical_id=ANY(:ids)''',{'domain':domain,'ids':ids})
        sidecar={r['canonical_id']:r['target_digest'] for r in sidecars}
        for r in receipts:
            if r['target_id'] is not None and sidecar.get(r['target_id'])!=actual.get(r['target_id']):
                raise EvidenceUnavailable('TARGET_ATTRIBUTION_INVALID')
            if r['target_id'] is not None and actual.get(r['target_id'])!=r['target_digest']:
                raise EvidenceUnavailable('TARGET_PROOF_INVALID')

    def _domain(self,b,domain,now):
        base={'domain':domain}; reasons=set()
        lease=b.rows('SELECT * FROM mart_capture_domain WHERE domain=:domain',base,limit=1)
        runs=b.rows('''SELECT id,manifest_id,domain,epoch,CASE WHEN octet_length(scope::text)<=1024 THEN scope ELSE NULL END AS scope,sealed,item_count,byte_count,manifest_digest,
            continuation,status,started_at,completed_at FROM mart_capture_run WHERE domain=:domain
            ORDER BY started_at DESC,id''',base,limit=self.limits.runs)
        if not lease or not runs: return DomainCoverage(domain,reasons=('NO_CANDIDATE_HISTORY',))
        lease=lease[0]; byrun={r['id']:r for r in runs}
        if lease['latest_run'] not in byrun: raise EvidenceUnavailable('RUN_POINTER_UNVERIFIED')
        latest=byrun[lease['latest_run']]
        for r in runs:
            if r['epoch']!=EPOCH: raise EvidenceUnavailable('INCOMPATIBLE_EPOCH')
            scope=r['scope']
            if scope!=SCOPE and not (isinstance(scope,dict) and set(scope)==set(SCOPE)|{
                'capture_mode','family_id','source_id','policy_epoch','replay_epoch'} and
                all(scope[k]==v for k,v in SCOPE.items()) and scope['capture_mode']=='RECOVERY_BY_ID' and
                scope['policy_epoch']==POLICY and scope['replay_epoch']==REPLAY):
                raise EvidenceUnavailable('SCOPE_UNVERIFIED')
        params=dict(base,ids=list(byrun))
        items=b.rows('''SELECT run_id,ordinal,source_id,fingerprint,disposition,reason,acked_at,target_id,target_digest
            FROM mart_capture_item WHERE run_id=ANY(:ids) ORDER BY run_id,ordinal''',params)
        grouped={rid:[] for rid in byrun}
        for i in items: grouped[i['run_id']].append(i)
        reconciled={}
        def reconcile(r):
            if r['id'] in reconciled: return reconciled[r['id']]
            rows=grouped[r['id']]
            counts=dict.fromkeys(MANIFEST_FIELDS,0); counts['captured']=r['item_count']
            counts['acknowledged']=sum(i['acked_at'] is not None for i in rows)
            for field,state in [('projected','PROJECTED'),('unchanged','UNCHANGED'),('excluded','EXPECTED_EXCLUSION'),
                                ('deferred','DEFERRED'),('failed','FAILED')]:
                counts[field]=sum(i['disposition']==state for i in rows)
            counts['unprocessed']=sum(i['acked_at'] is None for i in rows)
            if r['sealed']:
                digest=hashlib.sha256()
                for ordinal,i in enumerate(rows,1):
                    if i['ordinal']!=ordinal: raise EvidenceUnavailable('MANIFEST_PROOF_INVALID')
                    digest.update(encode([ordinal,i['source_id'],i['fingerprint']]))
                    if i['disposition']=='EXPECTED_EXCLUSION' and (domain!='maintenance_event' or
                            i['source_id'].startswith('BSR') or i['reason']!='APPROVED_WO_PREFIX'):
                        raise EvidenceUnavailable('EXCLUSION_UNVERIFIED')
                if len(rows)!=r['item_count'] or digest.hexdigest()!=r['manifest_digest']:
                    raise EvidenceUnavailable('MANIFEST_PROOF_INVALID')
            if r['continuation']>counts['acknowledged'] or any(i['acked_at'] is None for i in rows if i['ordinal']<=r['continuation']):
                raise EvidenceUnavailable('MANIFEST_PROOF_INVALID')
            reconciled[r['id']]=counts
            return counts
        manifest=reconcile(latest)
        families=b.rows('''SELECT id,domain,source_system,source_object,source_id,scope_key,policy_epoch,mapper_epoch,current_id
            FROM mart_deferred_family WHERE domain=:domain ORDER BY id''',dict(base,policy=POLICY,epoch=EPOCH))
        if any(f['scope_key']!='BSR:IP:WO_BSR' or f['policy_epoch']!=POLICY or f['mapper_epoch']!=EPOCH for f in families):
            raise EvidenceUnavailable('DEBT_SCOPE_UNVERIFIED')
        fids=[f['id'] for f in families]
        versions=b.rows('SELECT * FROM mart_deferred_version WHERE family_id=ANY(:fids) ORDER BY family_id,version',{'fids':fids})
        vmap={v['id']:v for v in versions}; current=[]
        for f in families:
            if f['current_id'] not in vmap: raise EvidenceUnavailable('DEBT_POINTER_UNVERIFIED')
            current.append((f,vmap[f['current_id']]))
        current_ids={f['id']:f['current_id'] for f in families}
        if any(v['state'] in ACTIVE and v['id']!=current_ids[v['family_id']] for v in versions):
            raise EvidenceUnavailable('DEBT_POINTER_UNVERIFIED')
        debt=dict.fromkeys(DEBT_FIELDS,0)
        for _,v in current:
            key={'OPEN':'open','ELIGIBLE_FOR_RETRY':'eligible','BLOCKED_NEEDS_REVIEW':'blocked','RESOLVED':'resolved'}.get(v['state'])
            if key is None: raise EvidenceUnavailable('DEBT_POINTER_UNVERIFIED')
            debt[key]+=1
        debt['outstanding']=debt['open']+debt['eligible']+debt['blocked']
        debt['superseded']=sum(v['state']=='SUPERSEDED_BY_NEW_VERSION' for v in versions)
        occurrences=b.rows('''SELECT o.run_id,o.ordinal,o.obligation_id FROM mart_deferred_occurrence o
            JOIN mart_capture_run r ON r.id=o.run_id WHERE r.domain=:domain ORDER BY o.run_id,o.ordinal''',base)
        linked={(o['run_id'],o['ordinal']):o['obligation_id'] for o in occurrences}
        debt['unlinked']=len({i['source_id'] for i in items if i['disposition'] in ('DEFERRED','FAILED') and (i['run_id'],i['ordinal']) not in linked})
        for i in items:
            if i['disposition'] in ('DEFERRED','FAILED') and (i['run_id'],i['ordinal']) in linked and linked[(i['run_id'],i['ordinal'])] not in vmap:
                raise EvidenceUnavailable('DEBT_SCOPE_UNVERIFIED')
        event_ids=list({v['resolution_event'] for _,v in current if v['state']=='RESOLVED'})
        events=b.rows('''SELECT id,obligation_id,action,evidence_run,evidence_ordinal,target_digest FROM mart_deferred_event
            WHERE id=ANY(:ids)''',{'ids':event_ids})
        emap={e['id']:e for e in events}; imap={(i['run_id'],i['ordinal']):i for i in items}
        proof=[]
        for f,v in current:
            if v['state']!='RESOLVED': continue
            e=emap.get(v['resolution_event']); i=imap.get((e['evidence_run'],e['evidence_ordinal'])) if e else None
            if (not e or not i or e['action']!='RESOLVED' or e['obligation_id']!=v['id'] or
                i['source_id']!=f['source_id'] or i['fingerprint']!=v['fingerprint'] or
                i['disposition'] not in TERMINAL or i['acked_at'] is None or
                not byrun[i['run_id']]['sealed'] or v['scope_proof']!='PROVEN' or
                i['target_digest']!=e['target_digest'] or v['last_event']!=v['resolution_event'] or
                linked.get((i['run_id'],i['ordinal']))!=v['id']):
                raise EvidenceUnavailable('RESOLUTION_PROOF_INVALID')
            reconcile(byrun[i['run_id']])
            proof.append(i)
        queues=b.rows('''SELECT family_id,obligation_id,scope_key,policy_epoch,replay_epoch,policy_digest,phase,reason,run_id,owner,fence,probes,attempts,due_at
            FROM mart_replay_queue WHERE domain=:domain ORDER BY family_id''',dict(base,policy=POLICY,replay=REPLAY))
        replay=dict.fromkeys(REPLAY_FIELDS,0); fm={f['id']:f for f in families}
        for q in queues:
            if q['family_id'] not in fm: raise EvidenceUnavailable('QUEUE_SCOPE_UNVERIFIED')
            replay[q['phase']]+=1
            if (q['policy_digest']!=self.replay_digest or q['scope_key']!='BSR:IP:WO_BSR' or
                    q['policy_epoch']!=POLICY or q['replay_epoch']!=REPLAY): replay['policy_mismatch']+=1
            if q['obligation_id']!=fm[q['family_id']]['current_id']:
                replay['stale_claims']+=1; continue
            if q['phase'] in ('CLAIMED','CAPTURED','WRITING','PROJECTED'):
                if lease['lease_until']<=now: replay['expired_claims']+=1
                if (q['run_id'],q['owner'],q['fence'])!=(lease['latest_run'],lease['owner'],lease['fence']):
                    replay['stale_claims']+=1
            if q['phase']=='DONE':
                v=vmap[q['obligation_id']]; e=emap.get(v['resolution_event'])
                if v['state']!='RESOLVED' or not e or e['evidence_run']!=q['run_id']:
                    raise EvidenceUnavailable('REPLAY_PROOF_INVALID')
        complete=byrun.get(lease['last_complete_run']) if lease['last_complete_run'] else None
        complete_ok=False
        if complete:
            c=reconcile(complete)
            complete_ok=(complete['scope']==SCOPE and complete['status']=='COMPLETE' and complete['sealed'] and
                complete['completed_at'] is not None and lease['last_complete_at'] is not None
                and complete['completed_at']<=lease['last_complete_at']<=now and c['unprocessed']==c['deferred']==c['failed']==0
                and c['acknowledged']==c['captured'])
            if not complete_ok: raise EvidenceUnavailable('COMPLETE_PROOF_INVALID')
            proof.extend(grouped[complete['id']])
        elif lease['last_complete_run']: raise EvidenceUnavailable('COMPLETE_PROOF_UNAVAILABLE')
        proof.extend(i for i in grouped[latest['id']] if i['acked_at'] is not None and i['disposition'] in TERMINAL)
        self._targets(b,domain,proof)
        if debt['outstanding']: reasons.add('OUTSTANDING_DEBT')
        if debt['unlinked']: reasons.add('UNLINKED_HISTORY')
        if replay['policy_mismatch']: reasons.add('POLICY_INCOMPATIBLE')
        if replay['stale_claims'] or replay['expired_claims']: reasons.add('CLAIM_RECONCILIATION_REQUIRED')
        if replay['BLOCKED']: reasons.add('BLOCKED_REPLAY')
        if any(replay[p] for p in ('PENDING','CLAIMED','CAPTURED','WRITING','FAILED','PROJECTED')):
            reasons.add('REPLAY_NOT_RECONCILED')
        if latest['status']!='COMPLETE' or latest['scope']!=SCOPE: reasons.add('LATEST_NOT_COMPLETE')
        if latest['status'] in ('CAPTURING','SEALED') or manifest['unprocessed']:
            reasons.add('INCOMPLETE_MANIFEST')
        if not complete_ok: reasons.add('NO_VERIFIED_COMPLETE')
        state='VERIFIED' if not reasons else 'BLOCKED' if reasons & {'POLICY_INCOMPATIBLE','BLOCKED_REPLAY'} else 'INCOMPLETE'
        return DomainCoverage(domain,self._activity(latest),self._activity(complete) if complete else None,
                              manifest,debt,replay,state,complete_ok,tuple(sorted(reasons)),proof_complete=state=='VERIFIED')
