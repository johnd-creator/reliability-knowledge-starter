import importlib.util,json,os,tempfile,unittest,copy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
T=Path(__file__).resolve().parents[2];D=T/'deploy/development/pdm_history_111/controller'
spec=importlib.util.spec_from_file_location('local_compat_test',D/'local_development.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CompatTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.state=self.base/'state';self.state.mkdir(mode=0o700)
  self.c=SimpleNamespace(STATE=self.state,BASE=self.base,ROOT=self.base/'old',NAME='owned',UNITS=('api','web'))
  self.c.write_private=lambda p,s:self.write(p,s)
  self.d=m.LocalDevelopment(self.c);self.d.state.mkdir(mode=0o700)
  self.old=self.base/'old';self.new=self.base/'new'
  for root in [self.old,self.new]:
   (root/'reliability-cockpit/web/node_modules').mkdir(parents=True);self.write(root/'reliability-cockpit/web/node_modules/.package-lock.json','same')
  self.config=self.d.state/'config.json';self.accounts=self.state/'accounts.json';self.write(self.accounts,'{}')
  self.write(self.config,json.dumps({'source_root':str(self.old),'workflow_sha':'a'*40,'accounts_file':str(self.accounts)}));self.write(self.state/'local-development-release.json','{}')
  self.previous={'sha':m.COMPAT_FROM,'root':str(self.old),'workflow_sha':'a'*40,'config_path':str(self.config),'before':{'web':{'pid':1},'api':{'pid':2}},'generated_hash':'stable'}
  self.db={'Id':'owned-id','State':{'Running':True},'NetworkSettings':{'Ports':{'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':'15443'}]}}};self.c.db=Mock(side_effect=lambda:copy.deepcopy(self.db))
  self.fixture={'schema_sha256':'same','ledger':[{'name':'007_pdm_source_history.sql','status':'APPLIED'}],'records':{'raw_sha256':'x','normalized_sha256':'x','counts':{'human':1}}};self.d.fixture_probe=Mock(side_effect=lambda _:copy.deepcopy(self.fixture));self.d.contract_objects=Mock(return_value=copy.deepcopy(m.COMPAT_OBJECTS));self.d.readiness=Mock();self.d.release=Mock()
 def tearDown(self):self.tmp.cleanup()
 def write(self,p,s):
  with Path(p).open('x') as f:os.chmod(p,0o600);f.write(s)
 def evidence(self):return self.d.compatibility_evidence(self.previous,self.new,m.COMPAT_TO)
 def approve(self,value=None):
  p=self.d.state/'compatibility-test.json';self.write(p,json.dumps(value if value is not None else self.evidence()));self.d.compatibility={'receipt':str(p),'sha256':m.digest(p)};return p
 def denied(self,code,f):
  with self.assertRaisesRegex(RuntimeError,code):f()
 def test_exact_private_receipt_passes(self):
  self.approve();self.assertEqual(len(self.d.approved_compatibility(self.previous,self.new,m.COMPAT_TO)),64)
 def test_scope_other_from_denied(self):
  self.previous['sha']='b'*40;self.denied('COMPATIBILITY_SCOPE_NOT_APPROVED',self.evidence);self.d.fixture_probe.assert_not_called()
 def test_scope_other_to_denied(self):self.denied('COMPATIBILITY_SCOPE_NOT_APPROVED',lambda:self.d.compatibility_evidence(self.previous,self.new,'b'*40))
 def test_preserved_mode_not_mixed(self):
  self.d.preservation={'receipt':'x'};self.denied('COMPATIBILITY_SCOPE_NOT_APPROVED',self.evidence)
 def test_objects_changed_denied(self):
  self.d.contract_objects.return_value={};self.denied('COMPATIBILITY_SOURCE_OBJECTS_CHANGED',self.evidence)
 def test_schema_or_current_records_differ_denied(self):
  for key in ['schema_sha256','records']:
   with self.subTest(key=key):
    altered=dict(self.fixture,**{key:'changed'});self.d.fixture_probe.side_effect=[self.fixture,altered];self.denied('COMPATIBILITY_SCHEMA_RECORDS_OR_LEDGER_DIFFER',self.evidence)
 def test_config_source_denied(self):
  v=json.loads(self.config.read_text());v['source_root']='wrong';self.config.write_text(json.dumps(v));self.denied('ACTIVE_FIXTURE_SOURCE_MISMATCH',self.evidence)
 def test_unexpected_database_listener_denied(self):
  self.db['NetworkSettings']['Ports']['5432/tcp'][0]['HostIp']='0.0.0.0';self.denied('EXISTING_DEVELOPMENT_POSTGRES_REQUIRED',self.evidence)
 def test_receipt_tampered_denied(self):
  p=self.approve();p.write_text('{}');self.denied('COMPATIBILITY_RECEIPT_DIGEST_CHANGED',lambda:self.d.approved_compatibility(self.previous,self.new,m.COMPAT_TO))
 def test_receipt_public_or_symlink_denied(self):
  p=self.approve();p.chmod(0o644);self.denied('PRIVATE_PRESERVATION_OBJECT_REQUIRED',lambda:self.d.approved_compatibility(self.previous,self.new,m.COMPAT_TO));p.chmod(0o600);q=p.with_name('link.json');q.symlink_to(p);self.d.compatibility['receipt']=str(q)
  with self.assertRaises(OSError):self.d.approved_compatibility(self.previous,self.new,m.COMPAT_TO)
 def test_receipt_wrong_location_denied(self):
  p=self.base/'receipt.json';self.write(p,json.dumps(self.evidence()));self.d.compatibility={'receipt':str(p),'sha256':m.digest(p)};self.denied('COMPATIBILITY_RECEIPT_LOCATION_DENIED',lambda:self.d.approved_compatibility(self.previous,self.new,m.COMPAT_TO))
 def test_stale_process_or_config_or_db_receipt_denied(self):
  self.approve();self.previous['before']['api']['pid']=3;self.denied('COMPATIBILITY_RECEIPT_STALE_OR_MISMATCHED',lambda:self.d.approved_compatibility(self.previous,self.new,m.COMPAT_TO))
 def test_missing_receipt_default_guard_remains(self):
  with patch.object(m,'output',side_effect=['old','changed']):self.denied('FIXTURE_CONTRACT_CHANGE_REQUIRES_SEPARATE_APPROVAL',lambda:self.d.fixture_contract(self.previous,self.new,m.COMPAT_TO))
 def recovery(self,probes):
  self.d.validate_backup=Mock();self.d.fixture_probe=Mock(side_effect=probes);self.d.repository=Mock();self.d.c.db=Mock(return_value={'Id':'owned-id','State':{'Running':True}})
  p=dict(self.previous,generated_hash='stable');v={'previous':p,'config_hash':m.digest(self.config),'accounts_hash':m.digest(self.accounts),'db_container_id':'owned-id','fixture':self.fixture}
  with patch.object(m,'source'),patch.object(m,'old_source',return_value='stable'),patch.object(m,'node_pin'):
   self.d.validate_recovery(v)
 def test_recovery_allows_current_compatible_native_append(self):
  now=dict(self.fixture,records={'raw_sha256':'new','normalized_sha256':'new','counts':{'human':2}});self.recovery([now,now])
 def test_legacy_recovery_allows_enriched_compatible_probe(self):
  now=dict(self.fixture,records={'raw_sha256':'new','normalized_sha256':'new','counts':{'human':2}});self.fixture={k:v for k,v in self.fixture.items() if k!='records'};self.recovery([now,now])
 def test_recovery_schema_drift_denied(self):self.denied('FIXTURE_SCHEMA_OR_LEDGER_CHANGED',lambda:self.recovery([dict(self.fixture,schema_sha256='changed'),self.fixture]))
 def test_recovery_old_model_unreadable_denied(self):self.denied('EXISTING_RECORD_NOT_READABLE',lambda:self.recovery([RuntimeError('EXISTING_RECORD_NOT_READABLE')]))
 def test_recovery_serialization_mismatch_denied(self):self.denied('ROLLBACK_RECORD_COMPATIBILITY_FAILED',lambda:self.recovery([self.fixture,dict(self.fixture,records={})]))
 def test_pending_007_forward_transition_is_denied(self):
  self.fixture['ledger'][0]['status']='PENDING'
  self.denied('PR111_EXACT_007_APPLIED_REQUIRED',self.evidence)
 def test_original_110_transition_no_longer_approved(self):
  self.previous['sha']='891dfee8a6606cbab64553a829863518f89e2cac'
  self.denied('COMPATIBILITY_SCOPE_NOT_APPROVED',self.evidence)
 def test_bridge_file_missing_from_release_is_denied(self):
  from unittest.mock import patch
  del self.d.release
  record={'source_sha':'1ec93d6f3507321617903d169451d77fdcc1216e','files':{n:'x' for n in ['nadi-dev.py','local_development.py','local_fixture.py','frontend_preview.py']}}
  with patch.object(m,'private',return_value=record):self.denied('UNREVIEWED_LOCAL_CONTROLLER_RELEASE',self.d.release)
 def test_changed_controller_file_is_denied(self):
  del self.d.release
  record={'source_sha':'1ec93d6f3507321617903d169451d77fdcc1216e','files':{n:'x' for n in ['nadi-dev.py','local_development.py','local_fixture.py','frontend_preview.py','pdm_007_bridge.py']}}
  with patch.object(m,'private',return_value=record):self.denied('LOCAL_CONTROLLER_RELEASE_CHANGED',self.d.release)

 def test_exact_five_file_amendment_release_is_explicit(self):
  del self.d.release
  record={'source_sha':'1ec93d6f3507321617903d169451d77fdcc1216e','files':{n:m.digest(D/n) for n in ['nadi-dev.py','local_development.py','local_fixture.py','frontend_preview.py','pdm_007_bridge.py']},'local_amendment':{'approved_from':m.COMPAT_FROM,'approved_to':m.COMPAT_TO,'bridge_schema_sha256':'7dc4b17be2b6281887fcd02fe2042794d8a5f1d67bf05cdad3856d54c8f56411'}}
  with patch.object(m,'private',return_value=record):self.assertEqual(self.d.release(),record['source_sha'])
 def test_amendment_scope_or_schema_cannot_be_broadened(self):
  del self.d.release
  record={'source_sha':'1ec93d6f3507321617903d169451d77fdcc1216e','files':{n:m.digest(D/n) for n in ['nadi-dev.py','local_development.py','local_fixture.py','frontend_preview.py','pdm_007_bridge.py']},'local_amendment':{'approved_from':m.COMPAT_FROM,'approved_to':m.COMPAT_TO,'bridge_schema_sha256':'7dc4b17be2b6281887fcd02fe2042794d8a5f1d67bf05cdad3856d54c8f56411'}}
  for key in ['approved_from','approved_to','bridge_schema_sha256']:
   altered=copy.deepcopy(record);altered['local_amendment'][key]='unapproved'
   with patch.object(m,'private',return_value=altered):self.denied('EXACT_HISTORY_BRIDGE_CONTROLLER_AMENDMENT_REQUIRED',self.d.release)

if __name__=='__main__':unittest.main(verbosity=2)
