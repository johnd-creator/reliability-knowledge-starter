"""Source-free engineering decision simulation; never applies configuration.

Run from reliability-cockpit using its reviewed Python environment:
python docs/validation/nadi-p1-fresh-gov-01-simulation.py
"""
import copy
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path.cwd()))
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.integration_status import IntegrationStatus
from src.services.phase1_readiness import phase1_readiness

HERE=Path(__file__).resolve().parent
INPUT=HERE/'nadi-p1-fresh-gov-01-input.json'
data=json.loads(INPUT.read_text())
NOW=datetime.fromisoformat(data['observed_at'])
P=FreshnessPolicy(maximo_wo_max_age_seconds=660,mart_factual_projection_max_age_seconds=660,pi_collector_max_age_seconds=1800)
SYNTHETIC=FreshnessPolicy(maximo_wo_max_age_seconds=660,mart_factual_projection_max_age_seconds=660,pi_collector_max_age_seconds=1800,condition_source_max_age_seconds=60,condition_projection_max_age_seconds=60)
def component(doc,key):return next(c for c in doc['components'] if c['component']==key)
def fresh(doc,key,dimension,times,policy):
    states=[policy.state(dimension,datetime.fromisoformat(t.replace('Z','+00:00')) if t else None,NOW,component=key).split('_',1)[1] for t in times]
    state='STALE' if 'STALE' in states else 'CURRENT' if states and all(s=='CURRENT' for s in states) else 'UNKNOWN'
    field={'COLLECTOR':'collection_freshness','SOURCE':'source_freshness','PROJECTION':'projection_freshness'}[dimension]
    component(doc,key)[field]={'state':state,'observed_at':min((t for t in times if t),default=None),'max_age_seconds':policy.threshold(dimension,key)}
def baseline(policy):
    doc=copy.deepcopy(data['status']);doc['observed_at']=data['observed_at']
    for key,times,dimension in [('MAXIMO',[data['maximo_success']],'COLLECTOR'),('RELIABILITY_MART',data['mart_successes'],'PROJECTION'),('PI_COLLECTOR',[data['pi_success']],'COLLECTOR'),('PI_CONDITION_PROJECTION',[data['source_timestamp']],'SOURCE'),('PI_CONDITION_PROJECTION',[data['projected_at']],'PROJECTION')]:
        fresh(doc,key,dimension,times,policy)
    return doc
def evaluate(doc):return phase1_readiness(IntegrationStatus.model_validate(doc),evidence_origin='OPERATOR_DOCUMENT').model_dump(mode='json')
def check(name,doc,expected):
    result=evaluate(doc);g={x['gate']:x for x in result['gates']}
    for gate,verdict in expected.items():assert g[gate]['verdict']==verdict,(name,gate,g[gate])
    return {'case':name,'overall':result['verdict'],'gates':result['gates'],'assertions':'PASS'}

results=[]
results.append(check('actual_policy_unset',baseline(FreshnessPolicy()),{'P1-MAXIMO-CURRENT':'UNKNOWN','P1-MART-CURRENT':'UNKNOWN','P1-PI-COLLECTOR-CURRENT':'UNKNOWN','P1-CONDITION-PROJECTION-READY':'UNKNOWN'}))
base=baseline(P)
results.append(check('hypothetical_660_660_1800_only',base,{'P1-MAXIMO-CURRENT':'PASS','P1-MART-CURRENT':'PASS','P1-PI-COLLECTOR-CURRENT':'PASS','P1-CONDITION-PROJECTION-READY':'UNKNOWN'}))
for name,key,dim,age,gate in [('wo_stale','MAXIMO','COLLECTOR',661,'P1-MAXIMO-CURRENT'),('one_projector_stale','RELIABILITY_MART','PROJECTION',661,'P1-MART-CURRENT'),('pi_stale','PI_COLLECTOR','COLLECTOR',1801,'P1-PI-COLLECTOR-CURRENT')]:
    d=copy.deepcopy(base);times=[(NOW-timedelta(seconds=age)).isoformat()]
    if key=='RELIABILITY_MART':times.append(NOW.isoformat())
    fresh(d,key,dim,times,P);results.append(check(name,d,{gate:'PARTIAL'}))
d=copy.deepcopy(base);fresh(d,'RELIABILITY_MART','PROJECTION',[NOW.isoformat(),None],P)
results.append(check('missing_second_projector',d,{'P1-MART-CURRENT':'UNKNOWN'}))
d=copy.deepcopy(base);fresh(d,'PI_COLLECTOR','COLLECTOR',[None],P)
results.append(check('missing_pi_success',d,{'P1-PI-COLLECTOR-CURRENT':'UNKNOWN'}))
d=copy.deepcopy(base);fresh(d,'MAXIMO','COLLECTOR',[(NOW+timedelta(seconds=1)).isoformat()],P)
results.append(check('future_completion',d,{'P1-MAXIMO-CURRENT':'UNKNOWN'}))
d=copy.deepcopy(base);component(d,'PI_COLLECTOR')['availability']='UNAVAILABLE'
results.append(check('collector_unavailable',d,{'P1-PI-COLLECTOR-CURRENT':'UNKNOWN'}))
d=copy.deepcopy(base);component(d,'MAXIMO')['degraded_reasons']=['COLLECTOR_ERRORS']
results.append(check('latest_wo_error',d,{'P1-MAXIMO-CURRENT':'PARTIAL'}))
for name,source,projection,quality,verdict in [('good_quality_stale_source','1970-01-01T00:00:00+00:00',NOW.isoformat(),'GOOD','PARTIAL'),('stale_projection',NOW.isoformat(),(NOW-timedelta(seconds=61)).isoformat(),'GOOD','PARTIAL'),('bad_quality_recent_times',NOW.isoformat(),NOW.isoformat(),'BAD','PARTIAL')]:
    d=copy.deepcopy(base);fresh(d,'PI_CONDITION_PROJECTION','SOURCE',[source],SYNTHETIC);fresh(d,'PI_CONDITION_PROJECTION','PROJECTION',[projection],SYNTHETIC)
    c=component(d,'PI_CONDITION_PROJECTION');c['quality']=quality;c['state']='CURRENT' if quality=='GOOD' else 'DEGRADED';c['degraded_reasons']=[] if quality=='GOOD' else ['BAD_QUALITY']
    results.append(check(name,d,{'P1-CONDITION-PROJECTION-READY':verdict}))
d=copy.deepcopy(base);d['coverage']['verified_mapping_assets']=0;d['coverage']['approved_signal_assets']=0;d['coverage']['projected_assets']=0
results.append(check('unverified_scope_never_verified',d,{'P1-IDENTITY-MAPPING-READY':'BLOCKED','P1-SIGNAL-SELECTION-READY':'BLOCKED','P1-CONDITION-PROJECTION-READY':'BLOCKED'}))
assert P.state('COLLECTOR',None,NOW,component='PI_COLLECTOR')=='COLLECTOR_UNKNOWN'
assert P.state('SOURCE',NOW,NOW,component='PI_CONDITION_PROJECTION')=='SOURCE_UNKNOWN'
assert P.state('PROJECTION',NOW,NOW,component='PI_CONDITION_PROJECTION')=='PROJECTION_UNKNOWN'
for key,dim,threshold in [('MAXIMO','COLLECTOR',660),('RELIABILITY_MART','PROJECTION',660),('PI_COLLECTOR','COLLECTOR',1800)]:
    assert P.state(dim,NOW-timedelta(seconds=threshold),NOW,component=key)==dim+'_CURRENT'
    assert P.state(dim,NOW-timedelta(seconds=threshold+1),NOW,component=key)==dim+'_STALE'
print(json.dumps({'scope':'OFFLINE_HYPOTHETICAL_ONLY','source_gets':0,'production_mutations':0,'cases':len(results),'all_assertions':'PASS','collector_null_preserved':True,'threshold_boundaries':'PASS','results':results},indent=2))
