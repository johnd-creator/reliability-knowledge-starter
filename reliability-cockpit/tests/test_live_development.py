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
  with patch.object(control,'active',return_value=False),patch.object(control,'git',side_effect=['','a'*40]),patch.object(control,'run') as run:
   control.switch('reviewed')
   self.assertEqual(run.call_args.args[0],['git','switch','--detach','reviewed'])
 def test_credential_environment_not_inherited(self):
  with patch.dict(os.environ,{'PI_PASSWORD':'synthetic','DATABASE_URL':'synthetic','MAXIMO_TOKEN':'synthetic'}),patch.object(control,'git',return_value='a'*40):
   env=control.common_env()
   self.assertFalse(any(s.startswith(('PI_','MAXIMO_','DATABASE_URL=','RELIABILITY_MART_DATABASE_URL=')) for s in env))
 def test_database_container_identity_required(self):
  class Result: returncode=0;stdout=json.dumps([{'Config':{'Labels':{}}}])
  with patch.object(control.subprocess,'run',return_value=Result()),self.assertRaisesRegex(RuntimeError,'UNEXPECTED_DATABASE'):control.db()
