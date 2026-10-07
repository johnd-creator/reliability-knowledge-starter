"""Source-controlled PI ownership/configuration checks; no source or DB needed."""
import argparse
from pathlib import Path
import unittest
from unittest.mock import patch
import yaml
from src.cli import cmd_worker, parse_args

SOURCE_NAMES = {'PI_WEB_API_BASE_URL','PI_USERNAME','PI_PASSWORD','PI_TOKEN',
                'PI_TIMEOUT_SECONDS','PI_RATE_LIMIT_SECONDS','PI_MAX_RESPONSE_BYTES','PI_VERIFY_TLS'}

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
            self.assertFalse(SOURCE_NAMES & set(self.services[service]['environment']))
        self.assertEqual(self.services['pi-migrate']['command'],['picollector','migrate'])

    def test_main_mart_requires_explicit_existing_reader(self):
        dsn=self.services['cockpit-api']['environment']['RELIABILITY_MART_DATABASE_URL']
        self.assertEqual(dsn, '${RELIABILITY_MART_DATABASE_URL:?set SELECT-only existing Mart DSN in .env.platform}')
        # Inspect the checked-in example only; never load operator credentials.
        example = dict(line.split('=', 1) for line in (ROOT / '.env.platform.example').read_text().splitlines()
                       if line and not line.startswith('#') and '=' in line)
        self.assertIn('@maximo-db/maximo_collector', example['RELIABILITY_MART_DATABASE_URL'])
        self.assertIn('nadi_mart_reader:', example['RELIABILITY_MART_DATABASE_URL'])
        self.assertNotIn('RELIABILITY_MART_ADMIN_DATABASE_URL', self.services['cockpit-api']['environment'])

    def test_worker_has_no_secondary_env_file(self):
        self.assertNotIn('env_file', self.services['pi-worker'])
        self.assertEqual(self.services['pi-worker']['environment']['PI_CONFIG_MODE'],'managed')

    def test_required_source_settings_are_explicit_and_worker_only(self):
        worker=self.services['pi-worker']['environment']
        self.assertTrue(SOURCE_NAMES <= set(worker))
        for name in SOURCE_NAMES:
            self.assertTrue(worker[name].startswith('${'+name+':-'))
        for service, definition in self.services.items():
            if service != 'pi-worker':
                self.assertFalse(SOURCE_NAMES & set(definition.get('environment',{})),service)

    def test_pause_metadata_shared_without_credentials(self):
        worker=self.services['pi-worker']['environment']
        self.assertEqual(worker['PI_SNAPSHOT_INTERVAL_SECONDS'], self.services['pi-api']['environment']['PI_SNAPSHOT_INTERVAL_SECONDS'])
        self.assertEqual(self.services['pi-worker']['command'][2], '--pause-seconds')

    def test_bulk_backfill_settings_not_exported_to_snapshot_owner(self):
        worker=self.services['pi-worker']['environment']
        self.assertFalse({'PI_MAX_REQUESTS_PER_SESSION','PI_BACKFILL_CHUNK_DAYS','PI_MAX_CONSECUTIVE_ERRORS',
                          'PI_PAUSE_BETWEEN_ATTRIBUTES','PI_OFF_HOURS_START','PI_OFF_HOURS_END','PI_RECORDED_INTERVAL_SECONDS'} & set(worker))


class WorkerConfigTests(unittest.TestCase):
    def test_invalid_interval_stops_before_db_or_source(self):
        with patch('src.cli.get_database',side_effect=AssertionError('No DB expected')):
            self.assertEqual(cmd_worker(argparse.Namespace(interval_seconds=0)),2)

    def test_explicit_snapshot_command_and_lease(self):
        with patch('src.cli.get_database') as db, patch('src.services.runtime_worker.run_owned_worker',return_value=0) as owner:
            self.assertEqual(cmd_worker(argparse.Namespace(interval_seconds=300)),0)
            owner.assert_called_once_with(db.return_value.engine,['picollector','run','--mode','snapshot','--pause-seconds','300'])


class ManagedConfigurationTests(unittest.TestCase):
    def test_managed_load_env_never_reads_dotenv_files(self):
        from src.config import load_env
        with patch.dict('os.environ',{'PI_CONFIG_MODE':'managed'},clear=True), patch('src.config._load_dotenv',side_effect=AssertionError('No dotenv allowed')):
            load_env()

    def test_standalone_dotenv_loading_retained(self):
        from src.config import load_env
        with patch.dict('os.environ',{},clear=True), patch('src.config._load_dotenv') as loader:
            load_env()
            self.assertEqual(loader.call_count,2)

    def test_existing_interval_env_still_means_pause(self):
        from src.config import CollectSafetyConfig
        with patch.dict('os.environ',{'PI_SNAPSHOT_INTERVAL_SECONDS':'420'},clear=True):
            self.assertEqual(CollectSafetyConfig.from_environment().snapshot_interval_seconds,420)
            for command in ('worker','run'):
                self.assertEqual(parse_args([command]).interval_seconds,420)

    def test_old_cli_alias_and_new_pause_option_match(self):
        with patch.dict('os.environ',{},clear=True):
            for command in ('worker','run'):
                self.assertEqual(parse_args([command,'--interval-seconds','420']).interval_seconds,
                                 parse_args([command,'--pause-seconds','420']).interval_seconds)

    def test_explicit_cli_pause_overrides_environment(self):
        with patch.dict('os.environ',{'PI_SNAPSHOT_INTERVAL_SECONDS':'420'},clear=True):
            self.assertEqual(parse_args(['worker','--pause-seconds','600']).interval_seconds,600)
