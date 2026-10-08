"""Validate a documentation approval register without runtime/source operations.

Run from reliability-cockpit: python docs/validation/nadi-p1-fresh-gov-02-validation.py
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import date,timedelta
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()))
from src.domain.condition_evidence import FreshnessPolicy

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REGISTER=HERE.parent/'nadi-p1-fresh-gov-02-approval-register.json'
r=json.loads(REGISTER.read_text())
expected={'MAXIMO_WO':660,'MART_FACTUAL':660,'PI_COLLECTOR':1800,'CONDITION_SOURCE':None,'CONDITION_PROJECTION':None}
assert {x['component']:x['owner_approved_threshold_seconds'] for x in r['components']}==expected
assert {x['component']:x['proposed_threshold_seconds'] for x in r['components']}==expected
assert r['owner_approval']['owner']=='Fauzi' and r['owner_approval']['status']=='PROJECT_OWNER_APPROVED'
assert r['owner_approval']['approval_date']=='2026-10-08'
assert r['owner_approval']['approval_timestamp'] is r['owner_approval']['approval_timezone'] is None
assert r['owner_approval']['timestamp_precision']=='DATE_ONLY'
assert not r['owner_approval']['external_digital_signature_claimed']
assert not r['owner_approval']['external_authenticated_approval_claimed']
assert not r['owner_approval']['source_acquisition_authorized']
assert r['expiry']['approval_expiry_calendar_date']==(date.fromisoformat(r['owner_approval']['approval_date'])+timedelta(days=7)).isoformat()
assert r['expiry']['expires_at'] is None and r['expiry']['activation_blocker']=='APPROVAL_EXPIRY_TIMESTAMP_UNRESOLVED'
assert r['activation_authorization']['status']=='ACTIVATION_NOT_AUTHORIZED' and not r['activation_authorization']['executed']
assert r['history'][0]['event']=='PROPOSED' and r['history'][0]['owner_approval_at_that_checkpoint']=='PENDING'
assert r['history'][1]['event']=='PROJECT_OWNER_APPROVED'
for c in r['components']:
    assert c['owner']=='Fauzi' and c['owner_decision']=='PROJECT_OWNER_APPROVED'
    assert c['technical_reviewer'] is c['component_owner'] is c['endorsement_evidence_ref'] is c['endorsement_timestamp'] is None
    assert c['current_production_threshold_seconds'] is None
    assert all(c[f] is None for f in ('actual_activation_timestamp','review_24h_due_at','review_72h_due_at','approval_expiry_at'))
    assert c['component_owner_endorsement_status']==('COMPONENT_ENDORSEMENT_PENDING' if expected[c['component']] else 'NOT_REQUIRED_FOR_KEEP_UNSET')
env={'NADI_'+f.upper():'' for f in FreshnessPolicy.model_fields}
for c in r['components']:env[c['setting']]=str(c['owner_approved_threshold_seconds']) if c['owner_approved_threshold_seconds'] else ''
with patch.dict('os.environ',env,clear=True):
    p=FreshnessPolicy.from_environment();assert p.component_mode
    assert p.maximo_wo_max_age_seconds==p.mart_factual_projection_max_age_seconds==660
    assert p.pi_collector_max_age_seconds==1800
    assert p.condition_source_max_age_seconds is p.condition_projection_max_age_seconds is None
    assert p.collector_max_age_seconds is p.source_max_age_seconds is p.projection_max_age_seconds is None
preserved=[]
for suffix in ('input.json','results.json','simulation.py'):
    path='reliability-cockpit/docs/validation/nadi-p1-fresh-gov-01-'+suffix
    old=subprocess.check_output(['git','-C',str(ROOT),'show',r['reviewed_pr_head']+':'+path])
    assert old==(ROOT/path).read_bytes();preserved.append(path)
print(json.dumps({'status':'PASS','scope':'OFFLINE_DOCUMENTATION_AND_CLEARED_ENVIRONMENT_ONLY','owner_decision':'PROJECT_OWNER_APPROVED',
 'components_validated':5,'component_endorsements_pending':3,'activation':'ACTIVATION_NOT_AUTHORIZED',
 'approval_time_precision':'DATE_ONLY','expiry_exact_instant':None,'expiry_calendar_reference':'2026-10-15',
 'actual_activation_and_review_clocks':None,'hypothetical_parser':'PASS','original_decision_artifacts_unchanged':preserved,
 'production_environment_writes':0,'production_source_gets':0,'production_mutations':0},indent=2))
