"""Source-controlled PI ownership/configuration checks; no source or DB needed."""
import argparse
from pathlib import Path
import unittest
from unittest.mock import patch
import yaml
from src.cli import cmd_worker

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless((ROOT / "compose.yaml").exists(), "root Compose fixture not mounted")
class RuntimeWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.services=yaml.safe_load((ROOT/'compose.yaml').read_text())['services']

    def test_single_opt_in_snapshot_owner(self):
        worker=self.services['pi-worker']
        self.assertEqual(worker['profiles'],['pi-collection'])
        self.assertEqual(worker['restart'],'no')
        self.assertEqual(worker['command'][:2],['picollector','worker'])
        self.assertNotIn('backfill',' '.join(worker['command']))
        self.assertEqual(worker['environment']['DATABASE_URL'],self.services['pi-api']['environment']['DATABASE_URL'])

    def test_api_and_migrate_have_no_source_credentials(self):
        for service in ('pi-api','pi-migrate'):
            self.assertNotIn('env_file',self.services[service])
            self.assertFalse(any(key.startswith('PI_') for key in self.services[service]['environment']))
        self.assertEqual(self.services['pi-migrate']['command'],['picollector','migrate'])

    def test_main_mart_uses_existing_owner(self):
        dsn=self.services['cockpit-api']['environment']['RELIABILITY_MART_DATABASE_URL']
        self.assertIn('@maximo-db/maximo_collector',dsn)


class WorkerConfigTests(unittest.TestCase):
    def test_invalid_interval_stops_before_db_or_source(self):
        with patch('src.cli.get_database',side_effect=AssertionError('No DB expected')):
            self.assertEqual(cmd_worker(argparse.Namespace(interval_seconds=0)),2)

    def test_explicit_snapshot_command_and_lease(self):
        with patch('src.cli.get_database') as db, patch('src.services.runtime_worker.run_owned_worker',return_value=0) as owner:
            self.assertEqual(cmd_worker(argparse.Namespace(interval_seconds=300)),0)
            owner.assert_called_once_with(db.return_value.engine,['picollector','run','--mode','snapshot','--interval-seconds','300'])
