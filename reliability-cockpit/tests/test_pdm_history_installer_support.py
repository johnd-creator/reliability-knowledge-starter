from pathlib import Path
import importlib.util,tempfile,unittest,os
from unittest.mock import patch
P=Path(__file__).resolve().parents[2]/'deploy/development/pdm_history_111/install_prepared.py';s=importlib.util.spec_from_file_location('install_test',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class InstallerTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.w=self.root/'wrapper';self.r=self.root/'manifest';m.write(self.w,b'oldw',0o700);m.write(self.r,b'oldm')
 def tearDown(self):self.tmp.cleanup()
 def call(self,verify=lambda:None):m.atomic_metadata(self.w,self.r,b'neww',b'newm',verify)
 def test_success_atomic_and_private(self):
  self.call();self.assertEqual(self.w.read_bytes(),b'neww');self.assertEqual(self.r.read_bytes(),b'newm');self.assertEqual(self.w.stat().st_mode&0o777,0o700);self.assertEqual(self.r.stat().st_mode&0o777,0o600)
 def test_failed_positive_readiness_restores_metadata(self):
  with self.assertRaises(RuntimeError):self.call(lambda:(_ for _ in ()).throw(RuntimeError('unhealthy')))
  self.assertEqual(self.w.read_bytes(),b'oldw');self.assertEqual(self.r.read_bytes(),b'oldm')
 def test_partial_swap_failure_restores_manifest(self):
  original=m.os.replace;calls=0
  def fail(a,b):
   nonlocal calls
   calls+=1
   if calls==2:raise OSError('wrapper swap failure')
   return original(a,b)
  with patch.object(m.os,'replace',side_effect=fail):
   with self.assertRaises(OSError):self.call()
  self.assertEqual(self.w.read_bytes(),b'oldw');self.assertEqual(self.r.read_bytes(),b'oldm')
 def test_uncertain_completed_swap_checked_and_restored(self):
  original=m.os.replace;calls=0
  def fail(a,b):
   nonlocal calls
   calls+=1;v=original(a,b)
   if calls==2:raise OSError('uncertain after successful swap')
   return v
  with patch.object(m.os,'replace',side_effect=fail):
   with self.assertRaises(OSError):self.call()
  self.assertEqual(self.w.read_bytes(),b'oldw');self.assertEqual(self.r.read_bytes(),b'oldm')
 def test_concurrent_unknown_metadata_not_overwritten(self):
  def changed():self.w.write_bytes(b'unknown');raise RuntimeError('changed')
  with self.assertRaisesRegex(RuntimeError,'CONTROLLER_RECOVERY_CONCURRENT_CHANGE'):self.call(changed)
  self.assertEqual(self.w.read_bytes(),b'unknown')
 def test_public_and_symlink_metadata_denied(self):
  self.r.chmod(0o644)
  with self.assertRaisesRegex(RuntimeError,'PRIVATE_INSTALL_FILE_REQUIRED'):self.call()
  self.r.chmod(0o600);target=self.root/'target';self.r.rename(target);self.r.symlink_to(target)
  with self.assertRaisesRegex(RuntimeError,'PRIVATE_INSTALL_FILE_REQUIRED'):self.call()
 def test_published_source_can_be_readable_but_not_writable_by_others(self):
  p=self.root/'published.py';p.write_bytes(b'# synthetic public source');p.chmod(0o644)
  self.assertEqual(m.source_read(p),p.read_bytes())
  p.chmod(0o666)
  with self.assertRaisesRegex(RuntimeError,'REVIEWED_SOURCE_FILE_REQUIRED'):m.source_read(p)
 def test_private_review_is_required_before_any_installer_action(self):
  with self.assertRaisesRegex(RuntimeError,'EXACT_PRIVATE_REVIEW_APPROVAL_REQUIRED'):m.install()
  with self.assertRaisesRegex(RuntimeError,'EXACT_PRIVATE_REVIEW_APPROVAL_REQUIRED'):m.install('relative.json')
  self.assertEqual(self.w.read_bytes(),b'oldw');self.assertEqual(self.r.read_bytes(),b'oldm')

if __name__=='__main__':unittest.main(verbosity=2)

# Whole installer on private synthetic metadata. Runtime probes are test doubles;
# no installed path, service, account, database or collector is contacted.
class PreparedInstallTest(unittest.TestCase):
 def setUp(self):
  import json,hashlib
  from types import SimpleNamespace
  from contextlib import nullcontext
  self.tmp=tempfile.TemporaryDirectory();self.t=Path(self.tmp.name);self.r=self.t/'repo';self.state=self.r/'.nadi-dev/state';self.release=self.state/'controller-releases/old';self.release.mkdir(parents=True);(self.state/'local-dev-01').mkdir()
  self.source=self.t/'candidate';self.source.mkdir();self.e=self.t/'review-evidence';self.e.mkdir()
  self.patchers=[patch.object(m,'T',self.t),patch.object(m,'R',self.r),patch.object(m,'STATE',self.state),patch.object(m,'SOURCE',self.source)]
  for p in self.patchers:p.start()
  self.addCleanup(lambda:[p.stop() for p in self.patchers]);self.addCleanup(self.tmp.cleanup)
  original=Path(__file__).resolve().parents[2]/'deploy/development/pdm_history_111/controller'
  oldnames=set(m.FILES)-{'pdm_007_bridge.py'}
  for name in m.FILES:m.write(self.source/name,(original/name).read_bytes())
  for name in oldnames:m.write(self.release/name,b'# SYNTHETIC previous controller\n')
  self.oldrecord={'source_sha':'1ec93d6f3507321617903d169451d77fdcc1216e','files':{n:m.sha(m.read(self.release/n)) for n in oldnames}}
  self.wrapper=self.r/'.nadi-dev/nadi-dev';m.write(self.wrapper,('#!/bin/sh\nexec /usr/bin/python3 '+str(self.release/'nadi-dev.py')+' "$@"\n').encode(),0o700)
  self.manifest=self.state/'local-development-release.json';m.write(self.manifest,json.dumps(self.oldrecord).encode())
  self.active=self.state/'local-dev-01/active.json';m.write(self.active,json.dumps({'sha':'e84eaec0e38e57cf0f057abaeda04e34739b01f8'}).encode())
  m.write(self.state/'localhost.pem',b'SYNTHETIC certificate placeholder');(self.state/'python-runtime').mkdir()
  checksums=__import__('json').loads((Path(__file__).resolve().parents[2]/'deploy/development/pdm_history_111/runtime_contract.json').read_text())['migrations']
  self.oldprobe={'ledger':[{'name':n,'checksum':h,'status':'APPLIED'} for n,h in checksums.items() if n!='007_pdm_source_history.sql'],'records':{'counts':{'human':35}},'schema_sha256':'SYNTHETIC_SAME_SCHEMA'}
  self.newprobe=dict(self.oldprobe,ledger=self.oldprobe['ledger']+[{'name':'007_pdm_source_history.sql','checksum':checksums['007_pdm_source_history.sql'],'status':'PENDING'}])
  from unittest.mock import Mock
  self.old=SimpleNamespace(status=Mock(return_value={'transport_process_readiness':'VERIFIED'}),fixture_probe=Mock(return_value=self.oldprobe),unit=Mock(return_value={'stable':True}))
  self.new=SimpleNamespace(status=Mock(return_value={'transport_process_readiness':'VERIFIED'}),fixture_probe=Mock(side_effect=lambda _:self.newprobe),unit=Mock(return_value={'stable':True}),transaction=lambda:nullcontext())
  c=SimpleNamespace(UNITS=('synthetic-api','synthetic-web'),local_controller=lambda:self.old)
  newc=SimpleNamespace(local_controller=lambda:self.new)
  self.modules=patch.object(m,'module',side_effect=[c,newc,newc]);self.modules.start();self.addCleanup(self.modules.stop)
  approval={'verdict':'GO','files':{n:m.sha(m.read(self.source/n)) for n in m.FILES},'installer_sha256':m.sha(Path(m.__file__).read_bytes()),'expected_installed_manifest_sha256':m.sha(m.read(self.manifest)),'expected_installed_wrapper_sha256':m.sha(m.read(self.wrapper)),'expected_active_state_sha256':m.sha(m.read(self.active))}
  m.write(self.e/'history-111-reviewed-controller-release.json',json.dumps(approval).encode());self.before=(m.read(self.wrapper),m.read(self.manifest),m.read(self.active))
 def test_pre007_install_keeps_active_and_units_and_exposes_pending(self):
  import contextlib,io,json
  with contextlib.redirect_stdout(io.StringIO()):m.install(self.e/'history-111-reviewed-controller-release.json')
  self.assertEqual(m.read(self.active),self.before[2]);record=json.loads(m.read(self.manifest));self.assertEqual(set(record['files']),set(m.FILES));self.assertEqual(record['local_amendment']['approved_to'],'85e6bb61eb5cb724e436846b9bdeee31709dffd4');self.assertEqual(self.newprobe['ledger'][-1]['status'],'PENDING')
 def test_bad_bridge_probe_is_refused_before_metadata_swap(self):
  self.newprobe['ledger'][-1]['status']='APPLIED'
  with self.assertRaisesRegex(RuntimeError,'CONTROLLER_INSTALL_BRIDGE_BASELINE_CHANGED'):m.install(self.e/'history-111-reviewed-controller-release.json')
  self.assertEqual((m.read(self.wrapper),m.read(self.manifest),m.read(self.active)),self.before)
 def test_failed_install_readiness_restores_metadata_preserves_active(self):
  from unittest.mock import Mock
  self.new.status=Mock(side_effect=[{'transport_process_readiness':'VERIFIED'},RuntimeError('SYNTHETIC final readiness failed')])
  with self.assertRaisesRegex(RuntimeError,'SYNTHETIC final readiness failed'):m.install(self.e/'history-111-reviewed-controller-release.json')
  self.assertEqual((m.read(self.wrapper),m.read(self.manifest),m.read(self.active)),self.before)
