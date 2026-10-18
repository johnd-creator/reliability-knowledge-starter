"""AUTH03 hermetic readiness contracts. Never contacts a service or database."""
import importlib.util,json,os,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
P=Path(__file__).resolve().parents[2]/'deploy/development/local_development.py'
s=importlib.util.spec_from_file_location('auth03_readiness',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
A='a'*40;B='b'*40
class ReadinessTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.origin='https://localhost:3000';self.c=SimpleNamespace(STATE=self.root,BASE=self.root,ORIGIN=self.origin,UNITS=('api','web'))
  self.d=m.LocalDevelopment(self.c)
  self.redirect={'status':307,'location':'/login?returnTo=%2F','cache_control':'private, no-store','data':None}
  self.anon={'status':401,'data':{'detail':{'code':'AUTHENTICATION_REQUIRED'}},'cache_control':'no-store'}
  self.invalid={'status':401,'data':{'detail':{'code':'SESSION_INVALID'}},'cache_control':'no-store'}
  self.d.probe=Mock(side_effect=[self.redirect,self.anon,self.invalid])
 def tearDown(self):self.tmp.cleanup()
 def deny(self,code,call):
  with self.assertRaisesRegex(RuntimeError,'^'+code+'$'):call()
 def test_known_redirect_and_exact_denials_are_separate_from_positive_session(self):
  self.assertEqual(self.d.auth_readiness()['authorized_session'],'NOT_PROBED_NO_SESSION')
 def test_arbitrary_redirect_is_not_success(self):
  for location in ['https://evil.test','/assets','/login?next=evil',None]:
   self.d.probe=Mock(return_value=dict(self.redirect,location=location));self.deny('ANONYMOUS_LOGIN_BOUNDARY_FAILED',self.d.auth_readiness)
 def test_302_200_503_and_missing_nostore_are_not_auth_health(self):
  for item in [dict(self.redirect,status=302),dict(self.redirect,status=200),dict(self.redirect,status=503),dict(self.redirect,cache_control='')]:
   self.d.probe=Mock(return_value=item);self.deny('ANONYMOUS_LOGIN_BOUNDARY_FAILED',self.d.auth_readiness)
 def test_arbitrary_401_from_wrong_server_is_denied(self):
  self.d.probe=Mock(side_effect=[self.redirect,dict(self.anon,data={'error':'not nadi'})]);self.deny('ANONYMOUS_API_BOUNDARY_FAILED',self.d.auth_readiness)
 def test_invalid_session_must_be_rejected_by_real_contract(self):
  for status in [200,403,503]:
   self.d.probe=Mock(side_effect=[self.redirect,self.anon,dict(self.invalid,status=status)]);self.deny('INVALID_SESSION_ACCEPTED_OR_UNVERIFIED',self.d.auth_readiness)
 def session_file(self,mode=0o600):
  p=self.root/'session.json';p.write_text(json.dumps({'cookie':'__Host-nadi_session='+'a'*43}));p.chmod(mode);return p
 def test_actual_session_capability_requires_gateway_success(self):
  p=self.session_file();who={'status':200,'data':{'subject':'local:fixture','roles':['AUTHOR'],'asset_ids':['asset:A']}}
  self.d.probe=Mock(side_effect=[self.redirect,self.anon,self.invalid,who,{'status':200,'data':{'status':'ok'}}]);self.assertEqual(self.d.auth_readiness(p)['authorized_session'],'VERIFIED')
 def test_expired_session_is_not_downgraded_to_optional(self):
  p=self.session_file();self.d.probe=Mock(side_effect=[self.redirect,self.anon,self.invalid,self.invalid]);self.deny('AUTHORIZED_SESSION_INVALID_OR_EXPIRED',lambda:self.d.auth_readiness(p))
 def test_authorized_session_does_not_imply_factual_gateway_health(self):
  p=self.session_file();who={'status':200,'data':{'subject':'local:fixture','roles':['ADMIN'],'asset_ids':[]}}
  self.d.probe=Mock(side_effect=[self.redirect,self.anon,self.invalid,who,{'status':503,'data':None}]);self.deny('AUTHORIZED_GATEWAY_FAILED',lambda:self.d.auth_readiness(p))
 def test_session_file_must_be_private(self):
  p=self.session_file(0o644);self.deny('PRIVATE_LOCAL_STATE_REQUIRED',lambda:self.d.auth_readiness(p))
 def test_session_file_must_not_be_symlink(self):
  p=self.session_file();link=self.root/'link';link.symlink_to(p);self.deny('PRIVATE_LOCAL_STATE_REQUIRED',lambda:self.d.auth_readiness(link))
 def test_session_file_does_not_accept_username_or_role_authority(self):
  p=self.session_file();p.write_text(json.dumps({'username':'admin','roles':['ADMIN']}));self.deny('PRIVATE_SESSION_FILE_INVALID',lambda:self.d.auth_readiness(p))
 def test_probe_refuses_nonlocal_targets_before_io(self):
  d=m.LocalDevelopment(self.c);self.deny('READINESS_TARGET_DENIED',lambda:d.probe('https://evil.test/'))
 def test_probe_refuses_cookie_forwarding_to_backends(self):
  d=m.LocalDevelopment(self.c);self.deny('READINESS_COOKIE_DENIED',lambda:d.probe('http://127.0.0.1:8000/health','__Host-nadi_session='+'a'*43))
 def test_probe_refuses_header_injection(self):
  d=m.LocalDevelopment(self.c);self.deny('READINESS_COOKIE_DENIED',lambda:d.probe(self.origin+'/', 'a\r\nx:y'))
 def setup_process_readiness(self,patches=None):
  value={'root':str(self.root),'sha':A,'workflow_sha':A,'node':'/node22','readiness_controller_sha':A,'expected_api_parent':{'parent':'unchanged'}}
  self.d.release=Mock(return_value=A);self.d.unit=Mock(return_value={'parent':'unchanged'})
  self.d.owners=Mock(side_effect=[{'listeners':{'1':{'exe':'/node22'}}},{'listeners':{'2':{'exe':str((self.root/'python-runtime/bin/python').resolve())}}}])
  backend={'source':'SYNTHETIC_LOCAL_DEVELOPMENT','source_sha':A,'current_sha':A,'bootstrap_sha':A,'database':'DISPOSABLE_TEST','database_identity':m.DB,'environment':'DEVELOPMENT','engineering':True}
  front={'contract':'NADI_LOCAL_TRANSPORT_V1','origin':self.origin,'guard':'SERVER_SESSION_AUTHORITY','frontend_sha':A,'launched_sha':A,'dirty':True}
  qa={'status':'READY','authentication':'LOCAL_SESSION_AUTHORITY'};fact={'status':'ok'}
  if patches:
   target,key,val=patches;[backend,front,qa,fact][target][key]=val
  self.d.request=Mock(side_effect=[backend,front,qa,fact]);self.d.auth_readiness=Mock(return_value={'authorized_session':'NOT_PROBED_NO_SESSION'});return value
 def test_complete_transport_profile_keeps_dirty_and_sha(self):
  value=self.setup_process_readiness()
  with patch.object(m,'source',return_value=self.root):self.assertTrue(self.d.readiness(value)['dirty'])
 def test_wrong_sha_database_stale_backend_and_bootstrap_fail_closed(self):
  for change in [(0,'source_sha',B),(0,'database_identity','wrong_test'),(1,'launched_sha',B),(2,'status','UNAVAILABLE'),(3,'status','missing'),(0,'bootstrap_sha',B),(0,'current_sha',B)]:
   value=self.setup_process_readiness(change)
   with patch.object(m,'source',return_value=self.root):self.deny('LOCAL_PAIR_NOT_READY',lambda:self.d.readiness(value))
 def test_unverified_authentication_capability_is_not_ready(self):
  value=self.setup_process_readiness((2,'authentication','UNAVAILABLE'))
  with patch.object(m,'source',return_value=self.root):self.deny('AUTHENTICATION_CAPABILITY_UNVERIFIED',lambda:self.d.readiness(value))
 def test_changed_controller_pin_fails_before_runtime_io(self):
  value=self.setup_process_readiness();value['readiness_controller_sha']=B;self.deny('LAUNCHER_CONTROLLER_MISMATCH',lambda:self.d.readiness(value));self.d.owners.assert_not_called()
 def test_process_replacement_still_fails(self):
  value=self.setup_process_readiness();value['expected_web']={'old':'identity'}
  with patch.object(m,'source',return_value=self.root):self.deny('UNEXPECTED_FRONTEND_PROCESS_OR_LISTENER_REPLACEMENT',lambda:self.d.readiness(value))
