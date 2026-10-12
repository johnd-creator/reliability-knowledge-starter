"""Hermetic: no listeners, DB writes or process effects in lifecycle regressions."""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch
PATH=Path(__file__).resolve().parents[2]/'deploy/development/frontend_preview.py'
spec=importlib.util.spec_from_file_location('frontend_preview_test',PATH)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FrontendPreviewTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.state=Path(self.temp.name);self.backend=self.state/'backend';self.front=self.state/'front'
  self.c=SimpleNamespace(ROOT=self.backend,BASE=self.state,STATE=self.state,UNITS=('qa-api.service','nadi-primary-web.service'),LEGACY_WEB='legacy.service',ORIGIN='https://localhost:3000',NAME='fixture',__file__=__file__,load=Mock(),db=Mock(return_value={'State':{'Running':True}}),active=Mock(return_value=False),stop_unit=Mock(),primary_busy=Mock(return_value=False),start_unit=Mock(),api_start=Mock(side_effect=AssertionError('FORBIDDEN_API_START')),write_private=lambda path,data:(path.write_text(data),path.chmod(0o600)))
  self.manager=m.FrontendPreview(self.c);self.old='b'*40;self.new='a'*40
  self.approval={'version':1,'frontend_root':str(self.front),'frontend_sha':self.new,'backend_root':str(self.backend),'backend_sha':self.old,'compatibility_digest':'c'*64,'launcher_sha256':'d'*64,'backup_sha256':'e'*64,'approved_at':'2026-10-11T00:00:00Z'}
  self.previous={'root':str(self.backend),'sha':self.old,'manifest':None,'api_unit':{'MainPID':'11'},'backup':str(self.state/'backup.dump')}
 def test_success_stops_only_frontend_and_records_pair(self):
  with patch.object(self.manager,'preflight',return_value=(self.approval,self.previous)),patch.object(self.manager,'unit',return_value=self.previous['api_unit']),patch.object(self.manager,'wait_ready'),patch.object(self.manager,'verify_owner'),patch.object(self.manager,'web_start') as start:self.manager.select(self.front,self.new,'backup')
  self.c.stop_unit.assert_called_once_with(self.c.UNITS[1]);self.c.api_start.assert_not_called()
  self.assertEqual(start.call_args.args[:2],(self.front,self.new))
  state=m.private_json(self.manager.pointer);record=m.private_json(state['manifest'])
  self.assertEqual(record['approval_id'],hashlib.sha256(m.canonical(self.approval).encode()).hexdigest())
  self.assertEqual(m.private_json(state['recovery'])['previous']['sha'],self.old)
 def test_preflight_failure_preserves_runtime(self):
  with patch.object(self.manager,'preflight',side_effect=RuntimeError('mismatch')):
   with self.assertRaises(RuntimeError):self.manager.select(self.front,self.new,'backup')
  self.c.stop_unit.assert_not_called();self.c.start_unit.assert_not_called()
 def test_failure_recovers_old_frontend(self):
  with patch.object(self.manager,'preflight',return_value=(self.approval,self.previous)),patch.object(self.manager,'unit',return_value=self.previous['api_unit']),patch.object(self.manager,'wait_ready',side_effect=RuntimeError('bad')),patch.object(self.manager,'web_start'),patch.object(self.manager,'restore') as restore:
   with self.assertRaises(RuntimeError):self.manager.select(self.front,self.new,'backup')
   restore.assert_called_once_with(self.previous)
  self.c.stop_unit.assert_called_once_with(self.c.UNITS[1]);self.c.api_start.assert_not_called()
 def test_api_change_refused_before_candidate_start(self):
  with patch.object(self.manager,'preflight',return_value=(self.approval,self.previous)),patch.object(self.manager,'unit',return_value={'MainPID':'22'}),patch.object(self.manager,'web_start') as start,patch.object(self.manager,'restore') as restore:
   with self.assertRaisesRegex(RuntimeError,'QA_API_CHANGED'):self.manager.select(self.front,self.new,'backup')
   start.assert_not_called();restore.assert_called_once()
 def test_restore_only_frontend(self):
  with patch.object(self.manager,'web_start') as start,patch.object(self.manager,'wait_ready'),patch.object(self.manager,'unit',return_value=self.previous['api_unit']),patch.object(m,'git',return_value=self.old):self.manager.restore(self.previous)
  start.assert_called_once_with(self.previous['root'],self.old,None);self.c.stop_unit.assert_called_once_with(self.c.UNITS[1]);self.c.api_start.assert_not_called()
 def test_rollback_repeats_preflight(self):
  p=self.state/'recovery.json';self.c.write_private(p,json.dumps({'previous':self.previous}))
  with patch.object(self.manager,'select') as select:self.manager.rollback(p)
  select.assert_called_once_with(self.previous['root'],self.old,self.previous['backup'])
 def test_runtime_difference_refused(self):
  with patch.object(m,'git',side_effect=['a','b']):
   with self.assertRaisesRegex(RuntimeError,'CONTRACT_DIFFERENCE'):m.compatible(self.front,self.backend,self.new,self.old)
 def test_dependency_difference_refused(self):
  with patch.object(m,'git',side_effect=['same','same']*len(m.COMPATIBILITY_PATHS)+['{"dependencies":{"next":"15"}}','{"dependencies":{"next":"16"}}']):
   with self.assertRaisesRegex(RuntimeError,'DEPENDENCY_DIFFERENCE'):m.compatible(self.front,self.backend,self.new,self.old)
 def test_equal_source_returns_digest(self):
  with patch.object(m,'git',side_effect=['same','same']*len(m.COMPATIBILITY_PATHS)+['{}','{}']):self.assertRegex(m.compatible(self.front,self.backend,self.new,self.old),r'^[a-f0-9]{64}$')
 def test_stale_status_refused(self):
  with patch.object(self.manager,'request',return_value={'sha':self.new,'stale':True}):
   with self.assertRaisesRegex(RuntimeError,'READINESS'):self.manager.readiness(self.new,self.old,'manifest')
 def test_split_requires_matching_approval(self):
  data={'sha':self.new,'launched_sha':self.new,'backend_sha':self.old,'stale':False,'dirty':False,'backend':'AVAILABLE','factual_backend':'AVAILABLE','database_identity':'nadi_live_dev_test','engineering':True,'compatibility':'VERIFIED_SOURCE_EQUIVALENT','compatibility_approval':'wrong'}
  with patch.object(self.manager,'request',return_value=data),patch.object(m,'private_json',return_value={'approval_id':'right'}):
   with self.assertRaisesRegex(RuntimeError,'UNAPPROVED'):self.manager.readiness(self.new,self.old,'manifest')
 def test_source_sha_must_be_exact(self):
  self.front.mkdir()
  with patch.object(m,'git',return_value=self.old):
   with self.assertRaisesRegex(RuntimeError,'EXACT_REVIEWED'):self.manager.source(self.front,self.new)
 def test_dirty_source_refused(self):
  self.front.mkdir()
  with patch.object(m,'git',side_effect=[self.new,'/repo/.git','/repo/.git',' M file']):
   with self.assertRaisesRegex(RuntimeError,'DIRTY_FRONTEND'):self.manager.source(self.front,self.new)
 def test_unrelated_repo_refused(self):
  self.front.mkdir()
  with patch.object(m,'git',side_effect=[self.new,'/a/.git','/b/.git']):
   with self.assertRaisesRegex(RuntimeError,'UNRELATED'):self.manager.source(self.front,self.new)
 def test_world_readable_state_refused(self):
  p=self.state/'manifest';p.write_text('{}');p.chmod(0o644)
  with self.assertRaisesRegex(RuntimeError,'PRIVATE'):m.private_json(p)
 def test_symlink_refused(self):
  p=self.state/'manifest';self.c.write_private(p,'{}');link=self.state/'link';link.symlink_to(p)
  with self.assertRaisesRegex(RuntimeError,'PRIVATE'):m.private_json(link)
 def test_unsafe_backup_no_restore_call(self):
  p=self.state/'backup-20261011-000000.dump';p.write_bytes(b'x'*2000);p.chmod(0o644)
  with patch.object(m.subprocess,'run') as run:
   with self.assertRaisesRegex(RuntimeError,'BACKUP'):self.manager.backup(p)
   run.assert_not_called()
 def test_missing_api_never_started(self):
  with patch.object(self.manager,'unit',return_value={'ActiveState':'inactive'}):
   with self.assertRaisesRegex(RuntimeError,'UNCHANGED_QA'):self.manager.backend()
  self.c.api_start.assert_not_called()
 def test_web_command_fixed_local_https(self):
  with patch.object(self.manager,'runtime',return_value={'path':'/private/node22'}):self.manager.web_start(self.front,self.new,self.state/'frontend-approval-aaaa.json')
  args=self.c.start_unit.call_args.args
  self.assertEqual(args[2][0],'/private/node22');self.assertNotIn('/home/linuxbrew/.linuxbrew/bin',args[3][-1])
  self.assertEqual(args[0],'nadi-primary-web');self.assertEqual(args[1],self.front/'reliability-cockpit/web')
  self.assertIn('3000',args[2]);self.assertIn('localhost',args[2]);self.assertIn('--experimental-https',args[2]);self.assertIn('NADI_DEV_LAUNCHED_SHA='+self.new,args[3]);self.c.api_start.assert_not_called()

 def test_known_next_generated_reference_restored_exactly(self):
  web=self.front/'reliability-cockpit/web';web.mkdir(parents=True);p=web/'next-env.d.ts'
  original='/// <reference path="./.next/types/routes.d.ts" />\n'
  p.write_text(original.replace('.next/', '.next-primary-dev/'))
  with patch.object(m,'git',side_effect=[self.new,original.strip(),' M reliability-cockpit/web/next-env.d.ts',self.new]):self.manager.restore_generated_types(self.front,self.new)
  self.assertEqual(p.read_text(),original)
 def test_unrelated_generated_edit_never_discarded(self):
  web=self.front/'reliability-cockpit/web';web.mkdir(parents=True);p=web/'next-env.d.ts';p.write_text('user changes\n')
  with patch.object(m,'git',side_effect=[self.new,'/// <reference path="./.next/types/routes.d.ts" />']):
   with self.assertRaisesRegex(RuntimeError,'UNEXPECTED_GENERATED'):self.manager.restore_generated_types(self.front,self.new)
  self.assertEqual(p.read_text(),'user changes\n')
 def test_launcher_release_requires_matching_private_hashes(self):
  p=self.state/'controller-release.json';self.c.write_private(p,json.dumps({'source_sha':self.new,'controller_sha256':'wrong','helper_sha256':'wrong'}))
  with self.assertRaisesRegex(RuntimeError,'UNREVIEWED_FRONTEND_CONTROLLER'):self.manager.launcher_release()
 def test_busy_port_does_not_start_candidate(self):
  self.c.primary_busy.return_value=True
  with patch.object(self.manager,'preflight',return_value=(self.approval,self.previous)),patch.object(self.manager,'web_start') as start,patch.object(self.manager,'restore') as restore:
   with self.assertRaisesRegex(RuntimeError,'NOT_RELEASED'):self.manager.select(self.front,self.new,'backup')
   start.assert_not_called();restore.assert_called_once()

 def test_exact_generated_change_audited(self):
  self.test_known_next_generated_reference_restored_exactly()
  records=list(self.state.glob('frontend-generated-*.json'))
  self.assertEqual(len(records),1)
  value=m.private_json(records[0]);self.assertIn('.next-primary-dev',value['diff'])
  self.assertNotEqual(value['before_sha256'],value['after_sha256'])
 def test_generated_change_with_other_dirt_never_restored(self):
  web=self.front/'reliability-cockpit/web';web.mkdir(parents=True);p=web/'next-env.d.ts'
  original='/// <reference path="./.next/types/routes.d.ts" />\n';changed=original.replace('.next/', '.next-primary-dev/');p.write_text(changed)
  for dirt in [' M other.ts\n M reliability-cockpit/web/next-env.d.ts','M  reliability-cockpit/web/next-env.d.ts','?? untracked']:
   with patch.object(m,'git',side_effect=[self.new,original.strip(),dirt]):
    with self.assertRaisesRegex(RuntimeError,'UNRELATED_GENERATED'):self.manager.restore_generated_types(self.front,self.new)
   self.assertEqual(p.read_text(),changed)
  self.assertFalse(list(self.state.glob('frontend-generated-*.json')))
 def test_worker_generations_preserve_history(self):
  manifest=self.state/'frontend-approval-aaaa.json';self.c.write_private(manifest,json.dumps({'approval_id':'c'*64}))
  identity={'worker_pid':21,'parent_pid':11,'start_ticks':'100','invocation_id':'d'*32}
  self.manager.record_worker(self.front,manifest,identity)
  self.manager.record_worker(self.front,manifest,{**identity,'worker_pid':22,'start_ticks':'200'})
  self.assertEqual(m.private_json(self.manager.worker_path(manifest))['generation'],2)
  self.assertEqual(len(list(self.state.glob('frontend-worker-aaaa-generation-*.json'))),2)
 def test_unexpected_worker_during_startup_fails_closed(self):
  manifest=self.state/'frontend-approval-aaaa.json';self.c.write_private(manifest,json.dumps({'approval':{'frontend_root':str(self.front)}}))
  with patch.object(self.manager,'worker_identity',side_effect=[{'worker_pid':21},{'worker_pid':22}]),patch.object(self.manager,'record_worker'),patch.object(self.manager,'restore_generated_types'),patch.object(self.manager,'readiness',side_effect=RuntimeError('FRONTEND_ONLY_READINESS_FAILED')),patch.object(m.time,'sleep'):
   with self.assertRaisesRegex(RuntimeError,'NEXT_WORKER_CHANGED'):self.manager.wait_ready(self.new,self.old,manifest)
 def test_worker_path_cannot_escape_private_state(self):
  for path in ['/tmp/frontend-approval-aaaa.json',str(self.state/'unreviewed.json')]:
   with self.assertRaisesRegex(RuntimeError,'PRIVATE_WORKER'):self.manager.worker_path(path)


 def test_generated_crlf_edit_is_not_known_transformation(self):
  web=self.front/'reliability-cockpit/web';web.mkdir(parents=True);p=web/'next-env.d.ts'
  original='/// <reference path="./.next/types/routes.d.ts" />\n';p.write_bytes(original.replace('.next/','.next-primary-dev/').replace('\n','\r\n').encode())
  with patch.object(m,'git',side_effect=[self.new,original.strip()]):
   with self.assertRaisesRegex(RuntimeError,'UNEXPECTED_GENERATED'):self.manager.restore_generated_types(self.front,self.new)
  self.assertIn(b'\r\n',p.read_bytes())
 def test_worker_identity_is_listener_not_supervisor(self):
  identity_stat='21 (next-server (v15.5.9)) '+' '.join(['S','11']+['0']*17+['777'])
  with patch.object(self.manager,'verify_owner',return_value={'MainPID':'11'}),patch.object(m,'output',side_effect=['LISTEN 0 511 [::1]:3000 [::]:* users:(("next-server",pid=21,fd=19))','d'*32]),patch.object(Path,'read_text',return_value=identity_stat):
   value=self.manager.worker_identity(self.front)
  self.assertEqual(value['worker_pid'],21);self.assertEqual(value['parent_pid'],11);self.assertEqual(value['start_ticks'],'777')
 def test_parent_change_is_not_approved(self):
  with patch.object(self.manager,'verify_owner',return_value={'MainPID':'12'}),patch.object(m,'output',return_value='pid=21'),patch.object(Path,'read_text',return_value='21 (worker) S 11 '+'0 '*18):
   with self.assertRaisesRegex(RuntimeError,'PARENT_CHANGED'):self.manager.worker_identity(self.front)

class PinnedNodeRuntimeTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.state=Path(self.temp.name);self.binary=self.state/'node22';self.binary.write_bytes(b'fixture-node-binary');self.binary.chmod(0o700)
  directory=self.state/'frontend-node-bin';directory.mkdir(mode=0o700);(directory/'node').symlink_to(self.binary)
  self.pin={'node_path':str(self.binary),'node_sha256':hashlib.sha256(self.binary.read_bytes()).hexdigest(),'node_version':'22.23.1','v8_version':'12.4','libnode_sha256':{}}
  self.actual={'execPath':str(self.binary),'node':'22.23.1','v8':'12.4','libnode':[]}
  self.manager=m.FrontendPreview(SimpleNamespace(STATE=self.state))
  self.process=SimpleNamespace(stdout=json.dumps(self.actual))
  self.save()
 def save(self):
  p=self.state/'frontend-runtime.json';p.write_text(json.dumps(self.pin));p.chmod(0o600)
 def test_verified_absolute_node22_and_clean_environment(self):
  with patch.object(m.subprocess,'run',return_value=self.process) as run:
   result=self.manager.runtime()
  self.assertEqual(result['version'],'22.23.1');self.assertEqual(result['path'],str(self.binary))
  self.assertEqual(run.call_args.args[0][0],str(self.binary));self.assertNotIn('NODE_OPTIONS',run.call_args.kwargs['env']);self.assertEqual(run.call_args.kwargs['env']['PATH'],'/usr/bin:/bin')
 def test_node25_refused_even_with_matching_pin(self):
  self.pin['node_version']='25.6.1';self.actual['node']='25.6.1';self.save()
  with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps(self.actual))):
   with self.assertRaisesRegex(RuntimeError,'NODE_22_VERSION'):self.manager.runtime()
 def test_changed_binary_refused_before_execution(self):
  self.binary.write_bytes(b'changed')
  with patch.object(m.subprocess,'run') as run:
   with self.assertRaisesRegex(RuntimeError,'HASH_CHANGED'):self.manager.runtime()
   run.assert_not_called()
 def test_wrong_patch_or_v8_refused(self):
  for field,value in [('node','22.24.0'),('v8','14.1')]:
   actual={**self.actual,field:value}
   with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps(actual))):
    with self.assertRaisesRegex(RuntimeError,'NODE_22_VERSION'):self.manager.runtime()
 def test_path_symlink_and_world_writable_binary_refused(self):
  self.pin['node_path']=str(self.state/'frontend-node-bin/node');self.save()
  with self.assertRaisesRegex(RuntimeError,'BINARY_REQUIRED'):self.manager.runtime()
  self.pin['node_path']=str(self.binary);self.save();self.binary.chmod(0o777)
  with self.assertRaisesRegex(RuntimeError,'BINARY_REQUIRED'):self.manager.runtime()
 def test_child_node_cannot_fallback_to_other_binary(self):
  alias=self.state/'frontend-node-bin/node';alias.unlink();other=self.state/'node25';other.write_bytes(b'other');alias.symlink_to(other)
  with patch.object(m.subprocess,'run',return_value=self.process):
   with self.assertRaisesRegex(RuntimeError,'CHILD_NODE'):self.manager.runtime()
 def test_shared_libnode_hash_changes_refused(self):
  lib=self.state/'libnode.so.127';lib.write_bytes(b'fixture-v8');lib.chmod(0o600)
  self.pin['libnode_sha256']={str(lib):hashlib.sha256(lib.read_bytes()).hexdigest()};self.actual['libnode']=[str(lib)];self.save()
  with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps(self.actual))):self.manager.runtime()
  lib.write_bytes(b'changed-v8')
  with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps(self.actual))):
   with self.assertRaisesRegex(RuntimeError,'LIBRARY_CHANGED'):self.manager.runtime()
 def test_extra_shared_library_refused(self):
  with patch.object(m.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps({**self.actual,'libnode':['/unknown/libnode.so']}))):
   with self.assertRaisesRegex(RuntimeError,'LIBRARY_CHANGED'):self.manager.runtime()
 def test_private_pin_permissions_enforced(self):
  (self.state/'frontend-runtime.json').chmod(0o644)
  with self.assertRaisesRegex(RuntimeError,'PRIVATE_FRONTEND_STATE'):self.manager.runtime()
 def test_runtime_failure_prevents_frontend_selection_stop(self):
  c=SimpleNamespace(STATE=self.state,load=lambda:{'application_dsn':'postgresql://nadi_dev_fixture:x@127.0.0.1:15443/nadi_live_dev_test'},stop_unit=Mock())
  manager=m.FrontendPreview(c)
  with patch.object(manager,'launcher_release',return_value=('a'*40,'b'*64)),patch.object(manager,'runtime',side_effect=RuntimeError('PIN_REFUSED')):
   with self.assertRaisesRegex(RuntimeError,'PIN_REFUSED'):manager.select('/candidate','a'*40,'backup')
  c.stop_unit.assert_not_called()

 def test_missing_pin_never_uses_system_node(self):
  (self.state/'frontend-runtime.json').unlink()
  with patch.object(m.subprocess,'run') as run:
   with self.assertRaisesRegex(RuntimeError,'NODE_CONFIG_REQUIRED'):self.manager.runtime()
   run.assert_not_called()
 def test_node_execution_failure_fails_closed(self):
  with patch.object(m.subprocess,'run',side_effect=m.subprocess.TimeoutExpired('node',10)):
   with self.assertRaisesRegex(RuntimeError,'NODE_EXECUTION_FAILED'):self.manager.runtime()
