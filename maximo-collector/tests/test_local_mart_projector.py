"""Hermetic tests for the zero-Maximo local Mart projection."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.config import DbConfig
from src.repositories import mart_models, models
from src.repositories.database import Database
from src.services.asset_registry_reconciliation import RegistryRecord, RegistrySnapshot
from src.services.local_mart_projector import (
    CollectorMartProjector,
    RegistryImportError,
    import_registry_snapshot,
)


NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


def _databases() -> tuple[Database, Database]:
    collector = Database(DbConfig("sqlite+pysqlite:///:memory:"))
    mart = Database(DbConfig("sqlite+pysqlite:///:memory:"))
    collector.create_all()
    mart.create_all()
    return collector, mart


class LocalMartProjectorTest(unittest.TestCase):
    def test_local_projection_is_idempotent_and_retains_can(self):
        collector, mart = _databases()
        with collector.session() as session:
            session.add(models.EquipmentOrm(
                id="ASSET-1", description="Synthetic", unit="CS01", status="OPERATING",
                source_changed_at=NOW, sources={"maximo": {"assetnum": "ASSET-1", "siteid": "BSR", "orgid": "IP", "eq11": "CS01", "changedate": NOW.isoformat()}},
            ))
            session.add(models.WorkOrderOrm(
                id="BSR-001", equipment_id="ASSET-1", status="CAN", work_type="PM",
                source_changed_at=NOW, actual_labor_hours=2.5,
            ))
            session.commit()

        projector = CollectorMartProjector(collector, mart, batch_size=1)
        first = projector.project_all()
        second = projector.project_all()
        with mart.session() as session:
            self.assertEqual(session.query(mart_models.AssetMasterMartOrm).count(), 1)
            maintenance = session.query(mart_models.MaintenanceEventMartOrm).one()
            self.assertEqual(maintenance.status, "CAN")
            self.assertEqual(session.query(mart_models.MartProjectionStateOrm).count(), 2)
        self.assertEqual(first["asset_master"]["inserted"], 1)
        self.assertEqual(first["maintenance_event"]["inserted"], 1)
        self.assertEqual(second["asset_master"]["unchanged"], 1)
        self.assertEqual(second["maintenance_event"]["unchanged"], 1)

    def test_unproven_scope_is_skipped_without_mart_write(self):
        collector, mart = _databases()
        with collector.session() as session:
            session.add(models.EquipmentOrm(id="ASSET-UNKNOWN", unit="CS01", status="OPERATING", sources={"maximo": {"assetnum": "ASSET-UNKNOWN"}}))
            session.commit()
        report = CollectorMartProjector(collector, mart).project("asset_master")
        self.assertEqual(report.skipped_unproven_scope, 1)
        with mart.session() as session:
            self.assertEqual(session.query(mart_models.AssetMasterMartOrm).count(), 0)

    def test_registry_activation_is_atomic_and_resolves_asset_master(self):
        collector, mart = _databases()
        with collector.session() as session:
            session.add(models.EquipmentOrm(
                id="ASSET-1", unit="CS01", source_changed_at=NOW,
                sources={"maximo": {"assetnum": "ASSET-1", "siteid": "BSR", "orgid": "IP", "eq11": "CS01", "changedate": NOW.isoformat()}},
            ))
            session.commit()
        projector = CollectorMartProjector(collector, mart)
        projector.project("asset_master")
        snapshot = RegistrySnapshot(
            format="html-table", sheet="List of Assets", rows=1,
            records=(RegistryRecord("ASSET-1", None, frozenset(), site="BSR", unit="CS01", status="OPERATING"),),
            field_present={}, byte_size=1, sha256="b" * 64,
        )
        result = import_registry_snapshot(snapshot, collector, mart)
        self.assertEqual(result["resolved"], 1)
        with mart.session() as session:
            self.assertEqual(session.query(mart_models.ReliabilityAssetRegistryMartOrm).count(), 1)

    def test_invalid_future_snapshot_does_not_replace_existing_relation(self):
        collector, mart = _databases()
        with collector.session() as session:
            session.add(models.EquipmentOrm(
                id="ASSET-1", unit="CS01", source_changed_at=NOW,
                sources={"maximo": {"assetnum": "ASSET-1", "siteid": "BSR", "orgid": "IP", "eq11": "CS01", "changedate": NOW.isoformat()}},
            ))
            session.commit()
        projector = CollectorMartProjector(collector, mart)
        projector.project("asset_master")
        valid = RegistrySnapshot(
            format="html-table", sheet="List of Assets", rows=1,
            records=(RegistryRecord("ASSET-1", None, frozenset(), site="BSR"),), field_present={}, byte_size=1, sha256="c" * 64,
        )
        import_registry_snapshot(valid, collector, mart)
        invalid = RegistrySnapshot(
            format="html-table", sheet="List of Assets", rows=1,
            records=(RegistryRecord("ASSET-1", None, frozenset(), site="OTHER"),), field_present={}, byte_size=1, sha256="d" * 64,
        )
        with self.assertRaises(RegistryImportError):
            import_registry_snapshot(invalid, collector, mart)
        with mart.session() as session:
            self.assertEqual(session.query(mart_models.ReliabilityAssetRegistryMartOrm).count(), 1)


if __name__ == "__main__":
    unittest.main()
