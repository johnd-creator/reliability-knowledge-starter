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
  self.manager.web_start(self.front,self.new,'/private/manifest');args=self.c.start_unit.call_args.args
  self.assertEqual(args[0],'nadi-primary-web');self.assertEqual(args[1],self.front/'reliability-cockpit/web')
  self.assertIn('3000',args[2]);self.assertIn('localhost',args[2]);self.assertIn('--experimental-https',args[2]);self.assertIn('NADI_DEV_LAUNCHED_SHA='+self.new,args[3]);self.c.api_start.assert_not_called()

 def test_known_next_generated_reference_restored_exactly(self):
  web=self.front/'reliability-cockpit/web';web.mkdir(parents=True);p=web/'next-env.d.ts'
  original='/// <reference path="./.next/types/routes.d.ts" />\n'
  p.write_text(original.replace('.next/', '.next-primary-dev/'))
  with patch.object(m,'git',side_effect=[self.new,original.strip()]):self.manager.restore_generated_types(self.front,self.new)
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
