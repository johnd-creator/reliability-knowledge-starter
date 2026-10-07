"""Offline catalog checks and opt-in tests on an isolated TimescaleDB only."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from sqlalchemy import create_engine, inspect, text
from src.services.migrations import discover, migrate, MigrationError, LOCK_KEY

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def put(self, name, sql="SELECT 1;"):
        (self.path / name).write_text(sql)

    def test_numeric_order(self):
        self.put("10_ten.sql"); self.put("2_two.sql")
        self.assertEqual([m.number for m in discover(self.path)], [2, 10])

    def test_duplicate_prefix(self):
        self.put("001_first.sql"); self.put("1_other.sql")
        with self.assertRaisesRegex(MigrationError, "Duplicate"):
            discover(self.path)

    def test_bad_filename(self):
        self.put("manual.sql")
        with self.assertRaises(MigrationError): discover(self.path)

    def test_empty_catalog(self):
        with self.assertRaises(MigrationError): discover(self.path)

    def test_outer_transaction_only(self):
        self.put("004_quality.sql", "-- comment\nBEGIN;\nSELECT 1;\nCOMMIT;\n")
        self.assertEqual(discover(self.path)[0].sql, "SELECT 1;")

    def test_embedded_transaction_rejected(self):
        self.put("005_bad.sql", "SELECT 1;\nCOMMIT;")
        with self.assertRaises(MigrationError): discover(self.path)

    def test_reviewed_do_block_retained(self):
        self.assertIn("DO $$", discover(MIGRATIONS)[0].sql)

    def test_sqlite_cannot_certify_migration(self):
        with self.assertRaisesRegex(MigrationError, "PostgreSQL"):
            migrate(create_engine("sqlite://"), MIGRATIONS)


@unittest.skipUnless(os.getenv("PI_MIGRATION_TEST_DSN"), "isolated Timescale test DSN required")
class TimescaleMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(os.environ["PI_MIGRATION_TEST_DSN"])
        with cls.engine.connect() as connection:
            if connection.scalar(text("SELECT current_database()")) != "pi_runtime_test":
                raise RuntimeError("Refusing destructive fixture outside pi_runtime_test")
        cls.catalog = discover(MIGRATIONS)

    @classmethod
    def tearDownClass(cls): cls.engine.dispose()

    def setUp(self):
        with self.engine.begin() as connection:
            for table in ("pi_schema_migration", "pi_backfill_progress", "pi_collect_run",
                          "pi_collect_cursor", "pi_snapshot", "pi_timeseries", "pi_attribute_registry"):
                connection.execute(text(f"DROP TABLE IF EXISTS public.{table} CASCADE"))
            with connection.connection.driver_connection.cursor() as cursor:
                for migration in self.catalog[:3]: cursor.execute(migration.sql, prepare=False)
            connection.execute(text("INSERT INTO pi_attribute_registry(attribute_id,is_active) VALUES('fixture',true)"))
            connection.execute(text("INSERT INTO pi_snapshot(attribute_id,value,value_good,source_timestamp) VALUES('fixture',12.5,false,'2026-08-14T00:00:00Z')"))
            connection.execute(text("INSERT INTO pi_timeseries(attribute_id,timestamp,value,value_good) VALUES('fixture','2026-08-14T00:00:00Z',12.5,false)"))
            connection.execute(text("INSERT INTO pi_collect_cursor(scope,rows_seen) VALUES('snapshot',1)"))
            connection.execute(text("INSERT INTO pi_collect_run(scope,started_at,rows_collected) VALUES('snapshot','2026-08-14T00:00:00Z',1)"))
            connection.execute(text("INSERT INTO pi_backfill_progress(attribute_id,interval,last_timestamp) VALUES('fixture','1h','2026-08-14T00:00:00Z')"))
        self.no_source = patch("requests.Session.request", side_effect=AssertionError("Migration must not call source"))
        self.no_source.start(); self.addCleanup(self.no_source.stop)

    def test_status_is_readonly(self):
        self.assertEqual([r['status'] for r in migrate(self.engine, MIGRATIONS)], ['PENDING']*4)
        with self.engine.connect() as c: self.assertFalse(inspect(c).has_table('pi_schema_migration'))

    def test_upgrade_legacy_rows_and_hypertable(self):
        self.assertEqual([r['status'] for r in migrate(self.engine, MIGRATIONS, apply=True)], ['APPLIED']*4)
        with self.engine.connect() as c:
            for table in ('pi_snapshot','pi_timeseries'):
                row = c.execute(text(f"SELECT value,value_good,source_value,value_type,value_questionable FROM {table}")).one()
                self.assertEqual(tuple(row), (12.5, False, None, None, None))
            self.assertEqual(c.scalar(text("SELECT count(*) FROM timescaledb_information.hypertables WHERE hypertable_name='pi_timeseries'")), 1)
            for table in ('pi_attribute_registry','pi_collect_cursor','pi_collect_run','pi_backfill_progress'):
                self.assertEqual(c.scalar(text(f'SELECT count(*) FROM {table}')),1)

    def test_idempotency_retains_ledger_timestamps(self):
        migrate(self.engine, MIGRATIONS, apply=True)
        with self.engine.connect() as c: before=c.execute(text('SELECT * FROM pi_schema_migration ORDER BY number')).all()
        migrate(self.engine, MIGRATIONS, apply=True)
        with self.engine.connect() as c: self.assertEqual(before,c.execute(text('SELECT * FROM pi_schema_migration ORDER BY number')).all())

    def test_compatible_partial_quality_schema(self):
        with self.engine.begin() as c:
            c.execute(text('ALTER TABLE pi_snapshot ADD COLUMN value_type VARCHAR(40)'))
            c.execute(text("UPDATE pi_snapshot SET value_type='LEGACY'"))
        migrate(self.engine, MIGRATIONS, apply=True)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(text('SELECT value_type FROM pi_snapshot')),'LEGACY')
            self.assertIsNone(c.scalar(text('SELECT source_value FROM pi_snapshot')))

    def test_incompatible_schema_blocks_without_forcing(self):
        with self.engine.begin() as c: c.execute(text('ALTER TABLE pi_snapshot ADD COLUMN source_value TEXT'))
        with self.assertRaisesRegex(MigrationError,'Incompatible'):
            migrate(self.engine, MIGRATIONS, apply=True)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(text('SELECT max(number) FROM pi_schema_migration')),3)
            self.assertNotIn('source_value',[r['name'] for r in inspect(c).get_columns('pi_timeseries')])

    def test_checksum_drift_rejected(self):
        migrate(self.engine, MIGRATIONS, apply=True)
        with self.engine.begin() as c: c.execute(text("UPDATE pi_schema_migration SET checksum='wrong' WHERE number=4"))
        with self.assertRaisesRegex(MigrationError,'drift'): migrate(self.engine, MIGRATIONS)

    def test_history_gap_rejected(self):
        migrate(self.engine, MIGRATIONS, apply=True)
        with self.engine.begin() as c: c.execute(text('DELETE FROM pi_schema_migration WHERE number=2'))
        with self.assertRaisesRegex(MigrationError,'ordered prefix'): migrate(self.engine, MIGRATIONS, apply=True)

    def test_failed_file_rolls_back_and_is_not_recorded(self):
        migrate(self.engine, MIGRATIONS, apply=True)
        with tempfile.TemporaryDirectory() as directory:
            for m in self.catalog: (Path(directory)/m.name).write_bytes((MIGRATIONS/m.name).read_bytes())
            (Path(directory)/'005_failure.sql').write_text('ALTER TABLE pi_snapshot ADD COLUMN should_rollback BOOLEAN; SELECT missing_field FROM pi_snapshot;')
            with self.assertRaisesRegex(MigrationError,'rolled back'): migrate(self.engine,directory,apply=True)
        with self.engine.connect() as c:
            self.assertNotIn('should_rollback',[r['name'] for r in inspect(c).get_columns('pi_snapshot')])
            self.assertEqual(c.scalar(text('SELECT count(*) FROM pi_schema_migration')),4)

    def test_active_owner_refuses_migration(self):
        with self.engine.connect().execution_options(isolation_level='AUTOCOMMIT') as owner:
            owner.execute(text('SELECT pg_advisory_lock(:key)'),{'key':LOCK_KEY})
            try:
                with self.assertRaisesRegex(MigrationError,'owns the lease'): migrate(self.engine,MIGRATIONS,apply=True)
            finally: owner.execute(text('SELECT pg_advisory_unlock(:key)'),{'key':LOCK_KEY})

    def test_worker_owner_lease_and_release(self):
        import sys
        from src.services.runtime_worker import run_owned_worker
        with self.engine.connect().execution_options(isolation_level='AUTOCOMMIT') as owner:
            owner.execute(text('SELECT pg_advisory_lock(:key)'),{'key':LOCK_KEY})
            try:
                with self.assertRaisesRegex(MigrationError,'owns the lease'): run_owned_worker(self.engine,[sys.executable,'-c','raise AssertionError()'])
            finally: owner.execute(text('SELECT pg_advisory_unlock(:key)'),{'key':LOCK_KEY})
        self.assertEqual(run_owned_worker(self.engine,[sys.executable,'-c','pass']),0)
        migrate(self.engine,MIGRATIONS,apply=True)  # wrapper released its lock

    def test_missing_existing_table_refuses_apply(self):
        with self.engine.begin() as c: c.execute(text('DROP TABLE pi_backfill_progress'))
        with self.assertRaisesRegex(MigrationError,'required table missing'): migrate(self.engine,MIGRATIONS,apply=True)
        with self.engine.connect() as c: self.assertFalse(inspect(c).has_table('pi_schema_migration'))
