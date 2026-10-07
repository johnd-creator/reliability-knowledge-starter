"""Opt-in PostgreSQL tests, confined to a disposable *_test database."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from src.config import MartDbConfig
from src.repositories.asset_af_mapping_store import AssetAfMappingCommandStore, MappingValidationError
from src.repositories.mart_database import MartDatabase
from src.repositories.mart_models import MartBase, AssetAfMappingMart
from src.services.asset_af_mapping_admin import AssetAfMappingAdminService
from src.services.mart_migrations import (BASE_TABLES, FILES, LEDGER, ROOT, MartMigrationError,
    admin_engine, reader_role, run_migrations)
from src.services.reliability import ReliabilityQueryService
from src.repositories.mart_reader import MartQueryRepository
import test_asset_af_mapping_admin as fixtures
from test_asset_af_mapping_admin import _asset, ASSET_ID, NOW


class MartAdminConfigTest(unittest.TestCase):
    def test_no_reader_or_legacy_admin_fallback(self):
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite://", "RELIABILITY_MART_DATABASE_URL": "sqlite://"}, clear=True):
            with self.assertRaises(MartMigrationError):
                admin_engine()
            with self.assertRaises(MappingValidationError):
                AssetAfMappingCommandStore.from_environment()


@unittest.skipUnless(os.getenv("NADI_MART_TEST_DSN"), "disposable PostgreSQL fixture not configured")
class MartPostgresMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = make_url(os.environ["NADI_MART_TEST_DSN"])
        if cls.url.host not in {"127.0.0.1", "localhost"} or not cls.url.database.endswith("_test"):
            raise RuntimeError("integration fixture must be local disposable *_test")
        cls.engine = create_engine(cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public")
        MartBase.metadata.create_all(self.engine, tables=[t for t in MartBase.metadata.sorted_tables if t.name != "asset_af_mapping"])
        with self.engine.begin() as c:
            for t in ["equipment", "work_order", "collect_run", "equipment_status_history", "item", "labor", "person", "service_request"]:
                c.exec_driver_sql(f"CREATE TABLE {t} (id text PRIMARY KEY)")
            c.exec_driver_sql("CREATE TABLE sync_cursor (scope text PRIMARY KEY, watermark timestamptz)")
            c.exec_driver_sql("CREATE TABLE mart_projection_state (projection_key text PRIMARY KEY, watermark timestamptz)")
            c.exec_driver_sql("INSERT INTO sync_cursor VALUES ('mxwodetail', '2026-10-07T12:00:00Z')")

    def migrate(self, **kwargs):
        return run_migrations(self.engine, expected_database=self.url.database, **kwargs)

    def test_status_does_not_create_schema_or_ledger(self):
        result = self.migrate()
        self.assertFalse(result["ready"])
        self.assertEqual(len(result["migrations"]), 2)
        self.assertNotIn(LEDGER, inspect(self.engine).get_table_names())
        self.assertNotIn("asset_af_mapping", inspect(self.engine).get_table_names())

    def test_wrong_database_fails_without_ddl(self):
        with self.assertRaises(MartMigrationError):
            run_migrations(self.engine, expected_database="cockpit", apply=True)
        self.assertNotIn(LEDGER, inspect(self.engine).get_table_names())

    def test_missing_existing_owner_anchors_fail_closed(self):
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP TABLE work_order")
        with self.assertRaises(MartMigrationError):
            self.migrate(apply=True)

    def test_explicit_atomic_apply_and_idempotency_preserve_facts(self):
        result = self.migrate(apply=True)
        self.assertTrue(result["ready"])
        self.assertEqual(result["applied"], list(FILES))
        self.assertEqual(result["before"], result["after"])
        self.assertEqual(self.migrate(apply=True)["applied"], [])
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(text("SELECT count(*) FROM asset_af_mapping")), 0)
            self.assertEqual(c.scalar(text("SELECT count(*) FROM sync_cursor")), 1)

    def test_require_ready_fails_when_pending(self):
        with self.assertRaises(MartMigrationError):
            self.migrate(require_ready=True)

    def test_untracked_schema_is_not_silently_adopted(self):
        with self.engine.begin() as c:
            c.exec_driver_sql((ROOT / FILES[0]).read_text())
        with self.assertRaises(MartMigrationError):
            self.migrate(apply=True)

    def test_checksum_drift_is_rejected(self):
        self.migrate(apply=True)
        with self.engine.begin() as c:
            c.exec_driver_sql(f"UPDATE {LEDGER} SET sha256='bad'")
        with self.assertRaises(MartMigrationError):
            self.migrate(apply=True)

    def test_ledger_with_missing_schema_is_rejected(self):
        self.migrate(apply=True)
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP TABLE asset_af_mapping")
        with self.assertRaises(MartMigrationError):
            self.migrate()

    def test_schema_drift_is_rejected(self):
        self.migrate(apply=True)
        with self.engine.begin() as c:
            c.exec_driver_sql("ALTER TABLE asset_af_mapping DROP CONSTRAINT ck_asset_af_mapping_retired_provenance")
        with self.assertRaises(MartMigrationError):
            self.migrate(require_ready=True)

    def test_failed_second_migration_rolls_back_both_and_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in FILES:
                (Path(directory) / name).write_bytes((ROOT / name).read_bytes())
            with (Path(directory) / FILES[1]).open("a") as stream:
                stream.write("\nSELECT 1 / 0;\n")
            with self.assertRaises(MartMigrationError):
                self.migrate(apply=True, directory=Path(directory))
        self.assertNotIn(LEDGER, inspect(self.engine).get_table_names())
        self.assertNotIn("asset_af_mapping", inspect(self.engine).get_table_names())

    def test_single_governance_owner_lease(self):
        from src.services.mart_migrations import LEASE_KEY
        with self.engine.begin() as c:
            c.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": LEASE_KEY})
            with self.assertRaises(MartMigrationError):
                self.migrate(apply=True)

    def test_mapping_lifecycle_on_canonical_postgres_schema(self):
        from src.repositories.mart_models import ReliabilityAssetRegistryMart
        self.migrate(apply=True)
        with Session(self.engine) as session:
            session.add(_asset())
            session.add(ReliabilityAssetRegistryMart(asset_ref=ASSET_ID, source_asset_number="SYNTHETIC", site_code="BSR", organization_code="IP", registry_source="TEST", snapshot_sha256="a"*64, snapshot_row_count=1, snapshot_imported_at=NOW))
            session.commit()
        store = AssetAfMappingCommandStore(self.engine)
        reader = MartDatabase(MartDbConfig(dsn=str(self.url.render_as_string(hide_password=False))))
        service = ReliabilityQueryService(MartQueryRepository(reader))
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = fixtures.AssetAfMappingAdminTest._write_csv(directory, [fixtures.AssetAfMappingAdminTest._row()])
                admin = AssetAfMappingAdminService(store)
                self.assertEqual(admin.import_csv(path, dry_run=True).accepted, 1)
                with self.engine.connect() as c:
                    self.assertEqual(c.scalar(text("SELECT count(*) FROM asset_af_mapping")), 0)
                self.assertEqual(admin.import_csv(path, dry_run=False).accepted, 1)
            row = service.repository.list_asset_af_mappings(ASSET_ID)[0]
            self.assertEqual(service.asset_af_mapping(ASSET_ID).mapping_state, "UNMAPPED")
            store.verify(row.id, verified_by="fixture-reviewer", evidence_ref="synthetic-only")
            self.assertEqual(service.asset_af_mapping(ASSET_ID).mapping_state, "MAPPED")
            store.retire(row.id, retired_by="fixture-reviewer", retirement_note="test completed")
            self.assertEqual(service.asset_af_mapping(ASSET_ID).mapping_state, "UNMAPPED")
        finally:
            reader.engine.dispose()

    def test_reader_role_selects_mart_and_cannot_write_even_with_readonly_off(self):
        self.migrate(apply=True)
        password = "synthetic-reader-password-at-least-24"
        reader_role(self.engine, expected_database=self.url.database, apply=True, password=password)
        reader_role(self.engine, expected_database=self.url.database, apply=True, password=password)
        reader = create_engine(self.url.set(username="nadi_mart_reader", password=password))
        try:
            with reader.begin() as c:
                self.assertEqual(c.scalar(text("SELECT count(*) FROM reliability_asset_registry")), 0)
                self.assertEqual(c.scalar(text("SHOW transaction_read_only")), "on")
            for statement in ["DELETE FROM asset_af_mapping", "INSERT INTO sync_cursor VALUES ('illegal',now())", "ALTER TABLE asset_master ADD COLUMN illegal int"]:
                with self.assertRaises(DBAPIError):
                    with reader.begin() as c:
                        c.exec_driver_sql("SET TRANSACTION READ WRITE")
                        c.exec_driver_sql(statement)
        finally:
            reader.dispose()

    def test_existing_privileged_reader_is_rejected(self):
        self.migrate(apply=True)
        reader_role(self.engine, expected_database=self.url.database, apply=True, password="synthetic-reader-password-at-least-24")
        with self.engine.begin() as c:
            c.exec_driver_sql("GRANT INSERT ON asset_af_mapping TO nadi_mart_reader")
        with self.assertRaises(MartMigrationError):
            reader_role(self.engine, expected_database=self.url.database, apply=True)
