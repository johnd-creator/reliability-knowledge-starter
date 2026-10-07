"""Storage round trips and actual ASGI API serialization, no external database."""
import asyncio
import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import inspect, text
from src.api.app import create_app, _store
from src.config import DbConfig
from src.domain.models import Snapshot, TimeseriesPoint
from src.repositories.database import Database, Base
from src.repositories.models import SnapshotOrm, TimeseriesOrm
from src.repositories.store import CollectorStore

TS = datetime(2026, 10, 7, tzinfo=timezone.utc)
DIGITAL = {"Name": "Stopped", "Value": 0, "IsSystem": False}


async def request(app, path):
    messages = []
    async def receive(): return {"type": "http.request", "body": b"", "more_body": False}
    async def send(message): messages.append(message)
    await app({"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "GET",
               "scheme": "http", "path": path, "raw_path": path.encode(), "query_string": b"",
               "root_path": "", "headers": [], "client": ("127.0.0.1", 1), "server": ("test", 80)}, receive, send)
    return messages[0]["status"], json.loads(b"".join(message.get("body", b"") for message in messages[1:]))


class PersistenceTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(DbConfig(dsn="sqlite+pysqlite:///:memory:"))
        Base.metadata.create_all(self.db.engine)
        self.addCleanup(self.db.engine.dispose)
        self.store = CollectorStore(self.db)

    def test_all_value_types_snapshot_round_trip_and_upsert(self):
        for value, kind in ((DIGITAL, "DIGITAL_STATE"), ("OFF", "TEXT"), (False, "BOOLEAN"), (None, "NULL"), (12.5, "NUMERIC")):
            snap = Snapshot("A", 12.5 if kind == "NUMERIC" else None, False, "bar", TS,
                            source_value=value, value_type=kind, value_questionable=True,
                            value_substituted=False, value_annotated=True)
            self.store.upsert_snapshot(snap)
            stored = self.store.get_snapshot("A")
            self.assertEqual(stored.source_value, value)
            self.assertEqual(stored.value, snap.value)
            self.assertEqual(stored.value_type, kind)
            self.assertEqual((stored.units, stored.value_good, stored.value_questionable, stored.value_substituted, stored.value_annotated), ("bar", False, True, False, True))
            self.assertEqual(self.store.list_snapshots()[0].source_value, value)
        self.assertEqual(len(self.store.list_snapshots()), 1)

    def test_timeseries_upsert_preserves_values_flags_and_deduplication(self):
        point = TimeseriesPoint("A", TS, None, False, units="bar", source_value=DIGITAL,
                                value_type="DIGITAL_STATE", value_questionable=True,
                                value_substituted=False, value_annotated=True)
        self.assertEqual(self.store.bulk_insert_timeseries([point, point]), 1)
        self.assertEqual(self.store.bulk_insert_timeseries([point]), 1)
        result = self.store.query_timeseries("A")[0]
        self.assertEqual(result.source_value, DIGITAL)
        self.assertEqual((result.value, result.units, result.value_type, result.value_good, result.value_questionable, result.value_substituted, result.value_annotated), (None, "bar", "DIGITAL_STATE", False, True, False, True))
        self.assertEqual(self.store.timeseries_count(), 1)

    def test_old_domain_constructors_remain_compatible(self):
        self.store.upsert_snapshot(Snapshot("OLD", 7.0, True, "MW", TS))
        self.store.bulk_insert_timeseries([TimeseriesPoint("OLD", TS, 7.0, True)])
        self.assertIsNone(self.store.get_snapshot("OLD").source_value)
        self.assertIsNone(self.store.query_timeseries("OLD")[0].value_type)
        self.assertEqual(self.store.get_snapshot("OLD").value, 7.0)

    def test_api_routes_serialize_richer_evidence_and_legacy_fields(self):
        snap = Snapshot("A", None, False, "bar", TS, source_value=DIGITAL,
                        value_type="DIGITAL_STATE", value_questionable=True, value_substituted=False, value_annotated=True)
        point = TimeseriesPoint("A", TS, None, False, units="bar", source_value=DIGITAL,
                                value_type="DIGITAL_STATE", value_questionable=True, value_substituted=False, value_annotated=True)
        class Store:
            def get_snapshot(self, attr): return snap
            def list_snapshots(self, **kwargs): return [snap]
            def query_timeseries(self, *args, **kwargs): return [point]
        app = create_app()
        app.dependency_overrides[_store] = lambda: Store()
        for path in ("/snapshots/A", "/snapshots", "/timeseries/A"):
            status, body = asyncio.run(request(app, path))
            self.assertEqual(status, 200)
            item = body[0] if isinstance(body, list) else body["points"][0] if "points" in body else body
            self.assertEqual(item["source_value"], DIGITAL)
            self.assertIsNone(item["value"])
            self.assertEqual((item["value_type"], item["units"], item["value_good"], item["value_questionable"], item["value_substituted"], item["value_annotated"]), ("DIGITAL_STATE", "bar", False, True, False, True))
            self.assertIn("2026-10-07", item.get("source_timestamp", item.get("timestamp")))
        self.assertFalse(any("governed" in route.path for route in app.routes))


class MigrationCompatibilityTest(unittest.TestCase):
    def test_additive_migration_matches_models_and_preserves_legacy_rows(self):
        sql = (Path(__file__).resolve().parents[1] / "migrations/004_signal_quality_fields.sql").read_text()
        operations = re.findall(r"ALTER TABLE (pi_\w+)\s+(.+?);", sql, re.S)
        self.assertEqual(len(operations), 2)
        self.assertNotRegex(sql.upper(), r"\b(DROP|TRUNCATE|DELETE|UPDATE)\b")
        db = Database(DbConfig(dsn="sqlite+pysqlite:///:memory:"))
        self.addCleanup(db.engine.dispose)
        with db.engine.begin() as conn:
            conn.execute(text("CREATE TABLE pi_snapshot (attribute_id VARCHAR(200) PRIMARY KEY, value FLOAT, value_good BOOLEAN, units VARCHAR(40), source_timestamp TIMESTAMP, collected_at TIMESTAMP)"))
            conn.execute(text("CREATE TABLE pi_timeseries (attribute_id VARCHAR(200), timestamp TIMESTAMP, value FLOAT, value_good BOOLEAN, collected_at TIMESTAMP, PRIMARY KEY(attribute_id,timestamp))"))
            conn.execute(text("INSERT INTO pi_snapshot (attribute_id,value) VALUES ('OLD',7)"))
            conn.execute(text("INSERT INTO pi_timeseries (attribute_id,timestamp,value) VALUES ('OLD','2026-10-07',7)"))
            # Execute the same additive columns on SQLite; PostgreSQL IF NOT EXISTS
            # syntax is checked below but no production/Postgres migration is run.
            for table, additions in operations:
                for column, datatype in re.findall(r"ADD COLUMN IF NOT EXISTS (\w+) ([A-Z]+(?:\(\d+\))?)", additions):
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {datatype}"))
        inspector = inspect(db.engine)
        for model in (SnapshotOrm, TimeseriesOrm):
            columns = {c["name"]: c for c in inspector.get_columns(model.__tablename__)}
            self.assertEqual(set(columns), set(model.__table__.columns.keys()))
            for field in ("source_value", "value_type", "value_questionable", "value_substituted", "value_annotated"):
                self.assertTrue(columns[field]["nullable"])
        store = CollectorStore(db)
        self.assertEqual(store.get_snapshot("OLD").value, 7)
        self.assertIsNone(store.get_snapshot("OLD").value_type)
        self.assertEqual(store.query_timeseries("OLD")[0].value, 7)
        self.assertIsNone(store.query_timeseries("OLD")[0].source_value)
        with db.engine.connect() as conn:
            for table in ("pi_snapshot", "pi_timeseries"):
                self.assertEqual(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar(), 1)


if __name__ == "__main__":
    unittest.main()
