"""Hermetic development isolation and non-destructive lifecycle regressions."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from qa.live_server import checked_url, private_json
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('dev_control',ROOT/'deploy/development/nadi-dev.py')
control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control)
class LiveDevelopmentTest(unittest.TestCase):
 def test_exact_disposable_database_identity(self):
  self.assertEqual(checked_url('postgresql+psycopg://nadi_dev_fixture:synthetic@127.0.0.1:15443/nadi_live_dev_test').database,'nadi_live_dev_test')
 def test_other_host_port_owner_database_and_query_rejected(self):
  base='postgresql+psycopg://nadi_dev_fixture:synthetic@127.0.0.1:15443/nadi_live_dev_test'
  for dsn in [base.replace('127.0.0.1','maximo-db'),base.replace('15443','5432'),base.replace('nadi_live_dev_test','maximo_collector'),base.replace('nadi_dev_fixture','owner'),base+'?host=remote', 'sqlite://']:
   with self.subTest(dsn=dsn),self.assertRaises(RuntimeError):checked_url(dsn)
 def test_private_configuration_read(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'config.json';p.write_text('{"fixture":true}');p.chmod(0o600)
   self.assertEqual(private_json(p),{'fixture':True})
 def test_world_readable_config_denied(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'config.json';p.write_text('{}');p.chmod(0o644)
   with self.assertRaises(RuntimeError):private_json(p)
 def test_symlink_config_denied(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'config.json';p.write_text('{}');p.chmod(0o600);link=Path(d)/'link';link.symlink_to(p)
   with self.assertRaises(RuntimeError):private_json(link)
 def test_switch_requires_stopped_services(self):
  with patch.object(control,'active',return_value=True),patch.object(control,'run') as run:
   with self.assertRaisesRegex(RuntimeError,'STOP_PREVIEW'):control.switch('reviewed')
   run.assert_not_called()
 def test_dirty_switch_denied(self):
  with patch.object(control,'active',return_value=False),patch.object(control,'git',return_value=' M file'),patch.object(control,'run') as run:
   with self.assertRaisesRegex(RuntimeError,'DIRTY_WORKTREE'):control.switch('reviewed')
   run.assert_not_called()
 def test_clean_switch_uses_detach_no_reset_or_pull(self):
  with patch.object(control,'active',return_value=False),patch.object(control,'git',side_effect=['','a'*40,'']),patch.object(control,'run') as run:
   control.switch('reviewed')
   self.assertEqual(run.call_args.args[0],['git','switch','--detach','reviewed'])
 def test_credential_environment_not_inherited(self):
  with patch.dict(os.environ,{'PI_PASSWORD':'synthetic','DATABASE_URL':'synthetic','MAXIMO_TOKEN':'synthetic'}),patch.object(control,'git',return_value='a'*40):
   env=control.common_env()
   self.assertFalse(any(s.startswith(('PI_','MAXIMO_','DATABASE_URL=','RELIABILITY_MART_DATABASE_URL=')) for s in env))
 def test_database_container_identity_required(self):
  class Result: returncode=0;stdout=json.dumps([{'Config':{'Labels':{}}}])
  with patch.object(control.subprocess,'run',return_value=Result()),self.assertRaisesRegex(RuntimeError,'UNEXPECTED_DATABASE'):control.db()

 def test_main_is_default_and_mismatch_does_not_switch(self):
  with patch.object(control,'git',side_effect=['a'*40,'b'*40]) as git,patch.object(control,'run') as run:
   with self.assertRaisesRegex(RuntimeError,'SELECT_REVIEWED_REF_FIRST'):control.selected_ref()
   self.assertEqual(git.call_args_list[0].args,('rev-parse','--verify','origin/main^{commit}'))
   run.assert_not_called()
 def test_explicit_preview_must_match_checked_out_commit(self):
  with patch.object(control,'git',side_effect=['a'*40,'a'*40]) as git:
   self.assertEqual(control.selected_ref('reviewed-branch'),'a'*40)
   self.assertEqual(git.call_args_list[0].args,('rev-parse','--verify','reviewed-branch^{commit}'))
 def test_preflight_ref_failure_preserves_runtime(self):
  with patch.object(control,'load'),patch.object(control,'selected_ref',side_effect=RuntimeError('unreviewed')),patch.object(control,'run') as run:
   with self.assertRaises(RuntimeError):control.reload()
   run.assert_not_called()
 def test_stop_preserves_existing_fixture_container(self):
  with patch.object(control,'stop_unit') as stop,patch.object(control,'run') as run:
   control.stop()
   self.assertEqual([call.args[0] for call in stop.call_args_list],list(control.UNITS))
   run.assert_not_called()
 def test_unknown_rollback_owner_rejected_before_primary_stop(self):
  with tempfile.TemporaryDirectory() as d,patch.object(control,'STATE',Path(d)),patch.object(control,'container',return_value={'Id':'other'}),patch.object(control,'run') as run:
   (Path(d)/'frontend-rollback.json').write_text('{"id":"original","image":"preserved"}')
   with self.assertRaisesRegex(RuntimeError,'ROLLBACK_CONTAINER_ID_CHANGED'):control.rollback()
   run.assert_not_called()
 def test_cutover_failure_restores_preserved_frontend(self):
  value={'Id':'original','Config':{'Image':'preserved','Labels':{}},'State':{'Running':True}}
  with tempfile.TemporaryDirectory() as d,patch.object(control,'STATE',Path(d)),patch.object(control,'preflight'),patch.object(control,'git',return_value=''),patch.object(control,'active',return_value=False),patch.object(control,'container',return_value=value),patch.object(control,'primary_busy',return_value=False),patch.object(control,'api_start'),patch.object(control,'web_start',side_effect=RuntimeError('startup failure')),patch.object(control,'rollback') as rollback,patch.object(control,'run') as run:
   with self.assertRaisesRegex(RuntimeError,'startup failure'):control.cutover('reviewed')
   rollback.assert_called_once()
   self.assertEqual(run.call_args.args[0],['docker','stop',control.WEB_CONTAINER])
 def test_legacy_retirement_requires_healthy_primary(self):
  with patch.object(control,'ready',side_effect=RuntimeError('not ready')),patch.object(control,'run') as run:
   with self.assertRaises(RuntimeError):control.retire_legacy()
   run.assert_not_called()
 def test_reload_denies_competing_legacy_process(self):
  with patch.object(control,'preflight'),patch.object(control,'active',return_value=True),patch.object(control,'stop') as stop:
   with self.assertRaisesRegex(RuntimeError,'RETIRE_LEGACY'):control.reload('reviewed')
   stop.assert_not_called()

 def test_absent_transient_unit_is_safe_to_stop(self):
  class Result: returncode=5
  with patch.object(control.subprocess,'run',return_value=Result()):control.stop_unit(control.UNITS[1])
 def test_stop_failure_does_not_report_success(self):
  class Result: returncode=1
  with patch.object(control.subprocess,'run',return_value=Result()),self.assertRaisesRegex(RuntimeError,'UNIT_STOP_FAILED'):control.stop_unit(control.UNITS[1])
