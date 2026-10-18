"""Metadata-only update/recovery simulation. No services, DBs or network."""
import contextlib,hashlib,importlib.util,json,os,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
P=Path(__file__).resolve().parents[2]/'deploy/development/install_auth03_controller.py';s=importlib.util.spec_from_file_location('auth03_install',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
A='a'*40;B='b'*40
class UpdateTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.base=self.root/'.nadi-dev';self.state=self.base/'state';self.old=self.state/'controller-releases/old';self.old.mkdir(parents=True,mode=0o700);(self.state/'local-dev-01').mkdir(mode=0o700)
  self.wrapper=self.base/'nadi-dev';self.manifest=self.state/'local-development-release.json';self.active=self.state/'local-dev-01/active.json'
  files={n:('old '+n).encode() for n in m.FILES}
  for n,b in files.items():m.write(self.old/n,b)
  value={'root':str(self.base/'pdm-ui-fix-01'),'sha':A,'workflow_sha':A,'fixture':{'schema':'same'}}
  record={'source_sha':A,'files':{n:m.digest(b) for n,b in files.items()},'installation_binding':{'ROOT':str(self.base/'worktree'),'change':'ROOT binding only'}}
  m.write(self.wrapper,('#!/bin/sh\nexec /usr/bin/python3 '+repr(str(self.old/'nadi-dev.py'))+' "$@"\n').encode(),0o700);m.write(self.manifest,json.dumps(record).encode());m.write(self.active,json.dumps(value).encode());m.write(self.state/'localhost.pem',b'synthetic public certificate')
  self.before=[p.read_bytes() for p in [self.wrapper,self.manifest,self.active]];self.fail_status=False
 def tearDown(self):self.tmp.cleanup()
 def module(self,name,path):
  c=SimpleNamespace(STATE=self.state);outer=self
  class Manager:
   @contextlib.contextmanager
   def transaction(self):yield
   def status(self,session_file=None):
    if outer.fail_status and c.STATE==outer.state:raise RuntimeError('SIMULATED_POST_INSTALL_FAILURE')
    return {'transport_process_readiness':'VERIFIED','authentication':{'authorized_session':'NOT_PROBED_NO_SESSION'}}
   def fixture_probe(self,value):return value['fixture']
   def replace(self,name,value):
    p=outer.state/'local-dev-01'/name;p.write_text(json.dumps(value));p.chmod(0o600)
   def save(self,name,value):m.write(outer.state/'local-dev-01'/name,json.dumps(value).encode())
  c.local_controller=lambda:Manager();return c
 def run_update(self):
  def blobs(args):return b'ROOT = Path(__file__).resolve().parents[2]\n' if args[-1].endswith('/nadi-dev.py') else b'new reviewed source\n'
  with patch.object(m.subprocess,'check_output',side_effect=blobs),patch.object(m,'module',side_effect=self.module):return m.install(self.root,B,A,A)
 def test_pins_new_release_retains_old_and_does_not_change_serving_source(self):
  r=self.run_update();self.assertEqual(r['controller_sha'],B);self.assertFalse(r['services_restarted']);self.assertEqual(json.loads(self.active.read_text())['sha'],A);self.assertEqual(json.loads(self.active.read_text())['workflow_sha'],A);self.assertEqual(json.loads(self.active.read_text())['readiness_controller_sha'],B)
  self.assertEqual(len(list((self.state/'controller-releases').iterdir())),2);self.assertEqual((self.old/'nadi-dev.py').read_bytes(),b'old nadi-dev.py')
 def test_unexpected_existing_release_blocks_before_update(self):
  with self.assertRaisesRegex(RuntimeError,'UPDATE_BASELINE_CHANGED'):m.install(self.root,B,B,A)
  self.assertEqual([p.read_bytes() for p in [self.wrapper,self.manifest,self.active]],self.before)
 def test_dirty_or_tampered_private_controller_blocks(self):
  (self.old/'local_development.py').write_bytes(b'tampered')
  with self.assertRaisesRegex(RuntimeError,'OLD_CONTROLLER_INTEGRITY_FAILED'):self.run_update()
 def test_post_install_failure_restores_metadata_only(self):
  self.fail_status=True
  with self.assertRaisesRegex(RuntimeError,'SIMULATED_POST_INSTALL_FAILURE'):self.run_update()
  self.assertEqual([p.read_bytes() for p in [self.wrapper,self.manifest,self.active]],self.before)
 def test_interrupted_wrapper_swap_restores_already_changed_manifest(self):
  original=m.os.replace
  def fail(src,dst):
   if str(src).endswith('-wrapper.tmp'):raise OSError('synthetic wrapper failure')
   return original(src,dst)
  with patch.object(m.os,'replace',side_effect=fail):
   with self.assertRaises(OSError):self.run_update()
  self.assertEqual([p.read_bytes() for p in [self.wrapper,self.manifest,self.active]],self.before)
 def test_wrong_serving_source_is_not_repaired_by_switching(self):
  with self.assertRaisesRegex(RuntimeError,'UPDATE_BASELINE_CHANGED'):m.install(self.root,B,A,B)
  self.assertEqual([p.read_bytes() for p in [self.wrapper,self.manifest,self.active]],self.before)
