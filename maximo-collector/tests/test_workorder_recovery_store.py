"""Local-only real store queries/anchor persistence; SQLite, no Maximo."""
from datetime import datetime, timezone
import unittest
from unittest.mock import Mock

from src.config import DbConfig
from src.repositories.database import Database
from src.repositories.models import WorkOrderOrm, SyncCursorOrm, CollectRunOrm
from src.repositories.store import CollectorStore


class RecoveryStoreTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(DbConfig("sqlite+pysqlite:///:memory:"))
        self.db.create_all()
        self.store = CollectorStore(self.db)
        self.addCleanup(self.db.engine.dispose)

    def seed(self, name, day):
        with self.db.session() as session:
            session.add(WorkOrderOrm(id=name, source_changed_at=datetime(2026, 8, day, tzinfo=timezone.utc)))
            session.commit()

    def test_latest_change_query_is_read_only_without_cursor_or_run(self):
        self.seed("BSRa", 20)
        self.seed("BSRb", 21)
        self.assertEqual(self.store.latest_work_order_change().day, 21)
        with self.db.session() as session:
            self.assertEqual(session.query(SyncCursorOrm).count(), 0)
            self.assertEqual(session.query(CollectRunOrm).count(), 0)

    def test_floor_is_durable_across_partial_upserts_and_new_store_instance(self):
        self.seed("BSRa", 21)
        self.assertEqual(self.store.prepare_work_order_recovery_floor().day, 21)
        self.seed("BSRb", 22)
        self.assertEqual(CollectorStore(self.db).prepare_work_order_recovery_floor().day, 21)
        self.assertEqual(self.store.latest_work_order_change().day, 22)
        with self.db.session() as session:
            self.assertEqual(session.query(SyncCursorOrm).count(), 0)
            marker = session.query(CollectRunOrm).one()
            self.assertEqual(marker.object_structure, "mxwodetail-recovery-floor")
            self.assertEqual(marker.upserted, 0)

    def test_no_local_timestamp_produces_no_floor_marker(self):
        with self.db.session() as session:
            session.add(WorkOrderOrm(id="BSRa"))
            session.commit()
        self.assertIsNone(self.store.latest_work_order_change())
        self.assertIsNone(self.store.prepare_work_order_recovery_floor())
        with self.db.session() as session:
            self.assertEqual(session.query(CollectRunOrm).count(), 0)

    def test_recovery_advisory_lock_released_even_after_error(self):
        connection = Mock()
        connection.scalar.return_value = True
        db = Mock()
        db.engine.connect.return_value.__enter__ = Mock(return_value=connection)
        db.engine.connect.return_value.__exit__ = Mock(return_value=False)
        store = CollectorStore(db)
        with self.assertRaises(RuntimeError):
            with store.work_order_recovery_lock() as acquired:
                self.assertTrue(acquired)
                raise RuntimeError("interrupted")
        self.assertIn("pg_advisory_unlock", str(connection.execute.call_args.args[0]))
        self.assertEqual(connection.commit.call_count, 2)
