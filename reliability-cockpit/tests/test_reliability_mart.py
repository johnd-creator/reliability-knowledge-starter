"""Hermetic tests for the MX-010R Reliability Mart read boundary."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import insert
from sqlalchemy.orm import Session

from src.api import reliability as reliability_api
from src.api.app import create_app
from src.config import MartDbConfig
from src.repositories.mart_database import MartDatabase, ReadOnlySession
from src.repositories.mart_models import (
    AssetHealthAssessmentMart,
    AssetMasterMart,
    FmeaAssessmentMart,
    MaintenanceEventMart,
    MartBase,
    OverhaulEventMart,
    RcfaAnalysisMart,
    ReliabilityAssetRegistryMart,
)
from src.repositories.mart_reader import MartQueryRepository
from src.services.reliability import ReliabilityQueryService


NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
ASSET_A = "asset:MAXIMO:MXASSET:BSR:IP:ASSET-A"
ASSET_B = "asset:MAXIMO:MXASSET:BSR:IP:ASSET-B"
TECHNICAL_ASSET = "asset:MAXIMO:MXASSET:BSR:IP:TECHNICAL"


def _common(canonical_id: str, entity: str) -> dict:
    return {
        "canonical_id": canonical_id,
        "contract_version": "1.0",
        "site_code": "BSR",
        "organization_code": "IP",
        "provenance": {
            "source_system": "MAXIMO",
            "source_application": "RELIABILITY",
            "source_object": entity,
            "source_record_id": f"synthetic-{entity}",
            "source_site": "BSR",
            "source_organization": "IP",
        },
        "relationship_evidence": {},
        "sources": {"maximo": {"source_object": entity}},
        "mart_created_at": NOW,
        "mart_updated_at": NOW,
    }


class ReliabilityMartReadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.database = MartDatabase(MartDbConfig(dsn="sqlite+pysqlite:///:memory:"))
        MartBase.metadata.create_all(cls.database.engine)
        with Session(cls.database.engine) as session:
            session.add_all([
                AssetMasterMart(**_common(ASSET_A, "MXASSET"), source_asset_number="ASSET-A", description="Synthetic asset A", status="OPERATING", asset_type="PUMP", unit="UNIT-A", source_updated_at=NOW),
                AssetMasterMart(**_common(ASSET_B, "MXASSET"), source_asset_number="ASSET-B", description="Synthetic asset B", status="IDLE", asset_type="MOTOR", unit="UNIT-B", source_updated_at=NOW),
                AssetMasterMart(**_common(TECHNICAL_ASSET, "MXASSET"), source_asset_number="TECHNICAL", description="Technical context", status="OPERATING", asset_type="COMPONENT", unit="UNIT-A", source_updated_at=NOW),
                ReliabilityAssetRegistryMart(asset_ref=ASSET_A, source_asset_number="ASSET-A", site_code="BSR", organization_code="IP", registry_source="MAXIMO_LIST_OF_ASSETS", snapshot_sha256="a" * 64, snapshot_row_count=2, snapshot_imported_at=NOW),
                ReliabilityAssetRegistryMart(asset_ref=ASSET_B, source_asset_number="ASSET-B", site_code="BSR", organization_code="IP", registry_source="MAXIMO_LIST_OF_ASSETS", snapshot_sha256="a" * 64, snapshot_row_count=2, snapshot_imported_at=NOW),
                AssetMasterMart(**_common("asset:OTHER:OTHER", "MXASSET") | {"site_code": "OTHER", "organization_code": "OTHER", "source_asset_number": "OUTSIDE"}),
                MaintenanceEventMart(**_common("maintenance:EVENT-A", "MXWODETAIL"), id="EVENT-A", equipment_id=ASSET_A, work_order_id="WO-REF-A", event_type="CORRECTIVE", status="COMPLETE", actual_start=NOW, actual_finish=NOW, source_changed_at=NOW),
                MaintenanceEventMart(**_common("maintenance:EVENT-B", "MXWODETAIL"), id="EVENT-B", equipment_id=ASSET_B, work_order_id="WO-REF-B", event_type="PM", status="CAN", actual_start=None, actual_finish=None, source_changed_at=NOW),
                FmeaAssessmentMart(**_common("fmea:FMEA-A", "IPFMEA"), source_record_id="FMEA-A", source_number="FMEA-N-A", revision="1", lifecycle_status="ACTIVE", description="Synthetic FMEA", asset_ref=ASSET_A, failure_code_ref="FC-A", source_updated_at=NOW, status_changed_at=NOW),
                AssetHealthAssessmentMart(**_common("bhm:BHM-A", "IPBHM"), source_record_id="BHM-A", revision="1", lifecycle_status="ACTIVE", description="Synthetic health", function_description="Synthetic function", asset_ref=ASSET_A, source_created_at=NOW, source_updated_at=NOW, status_changed_at=NOW),
                OverhaulEventMart(**_common("oh:OH-A", "IP_DOM_OH"), source_record_id="OH-A", source_number="OH-N-A", lifecycle_status="COMPLETE", workorder_ref="WO-REF-A", asset_ref=ASSET_A, planned_start_at=NOW, actual_start_at=NOW, progress=100, source_created_at=NOW, source_updated_at=NOW, unresolved_source_attributes={"performance_test": None}),
                OverhaulEventMart(**_common("oh:OH-MISSING", "IP_DOM_OH"), source_record_id="OH-MISSING", source_number="OH-N-MISSING", lifecycle_status="OPEN", workorder_ref="WO-MISSING", asset_ref=None, planned_start_at=NOW, source_created_at=NOW, source_updated_at=NOW),
                RcfaAnalysisMart(**_common("rcfa:RCFA-A", "IPRCFA"), source_record_id="RCFA-A", source_number="RCFA-N-A", lifecycle_status="OPEN", category="ROOT", asset_ref=None, location_ref=None, workorder_ref=None, failure_event_ref=None, source_created_at=NOW, requested_at=NOW),
            ])
            session.commit()
        cls.repository = MartQueryRepository(cls.database)
        cls.service = ReliabilityQueryService(cls.repository)

    def test_asset_scope_and_pagination(self):
        page = self.repository.list_assets(limit=1)
        self.assertEqual(page.total, 2)
        self.assertEqual(len(page.items), 1)
        self.assertTrue(page.has_more)
        self.assertIsNone(self.repository.get_asset("asset:OTHER:OTHER"))
        self.assertIsNone(self.repository.get_asset(TECHNICAL_ASSET))

    def test_entity_filters_and_latest_health(self):
        self.assertEqual(self.repository.list_maintenance(asset_ref=ASSET_A).total, 1)
        self.assertEqual(self.repository.list_maintenance(work_order_id="WO-REF-A").total, 1)
        self.assertEqual(self.repository.list_fmea(asset_ref=ASSET_A).total, 1)
        self.assertEqual(self.repository.list_health(asset_ref=ASSET_A).total, 1)
        self.assertEqual(self.repository.latest_health(ASSET_A).canonical_id, "bhm:BHM-A")
        self.assertEqual(self.repository.list_overhauls(asset_ref=ASSET_A).total, 1)
        self.assertEqual(self.repository.list_overhauls(workorder_ref="WO-MISSING").total, 1)
        self.assertEqual(self.repository.list_rcfa(category="ROOT").total, 1)

    def test_timeline_is_bounded_vendor_neutral_and_excludes_rcfa(self):
        timeline = self.service.timeline(ASSET_A, limit=50)
        self.assertEqual(timeline.total, 4)
        self.assertEqual({event.event_type for event in timeline.items}, {"MAINTENANCE", "FMEA", "ASSET_HEALTH", "OVERHAUL"})
        self.assertNotIn("IPRCFA", {event.event_type for event in timeline.items})

    def test_context_does_not_invent_rcfa_relationship(self):
        context = self.service.asset_context(ASSET_A)
        self.assertEqual(context["rcfa_relationship_status"], "UNRESOLVED")
        self.assertEqual(len(context["maintenance"].items), 1)
        self.assertEqual(len(context["fmea"].items), 1)

    def test_integrity_counts_resolved_and_unresolved_logical_refs(self):
        result = self.repository.integrity_summary()
        self.assertEqual(result["asset_refs_total"], 5)
        self.assertEqual(result["asset_refs_resolved"], 5)
        self.assertEqual(result["asset_refs_unresolved"], 0)
        self.assertEqual(result["workorder_refs_total"], 2)
        self.assertEqual(result["workorder_refs_resolved"], 1)
        self.assertEqual(result["workorder_refs_unresolved"], 1)
        self.assertEqual(result["registered_assets_total"], 2)
        self.assertEqual(result["registered_assets_resolved"], 2)
        self.assertEqual(result["maintenance_registered_total"], 2)

    def test_maintenance_date_filter_falls_back_to_source_changed_at(self):
        self.assertEqual(self.repository.list_maintenance(date_from=NOW).total, 2)

    def test_registry_summary_is_aggregate_only(self):
        result = self.repository.registry_summary()
        self.assertEqual(result["registered_asset_count"], 2)
        self.assertEqual(result["snapshot_row_count"], 2)
        self.assertNotIn("asset_ref", result)

    def test_work_order_reference_uses_scoped_work_order_field(self):
        rows = self.repository.list_maintenance(work_order_id="WO-REF-A").items
        self.assertEqual(rows[0].canonical_id, "maintenance:EVENT-A")
        self.assertNotEqual(rows[0].canonical_id, "WO-REF-A")

    def test_read_only_facade_blocks_dml(self):
        with self.database.read_session() as session:
            self.assertIsInstance(session, ReadOnlySession)
            with self.assertRaises(RuntimeError):
                session.execute(insert(AssetMasterMart).values(canonical_id="blocked"))
            with self.assertRaises(AttributeError):
                session.commit  # type: ignore[attr-defined]


class ReliabilityMartApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not hasattr(ReliabilityMartReadTest, "database"):
            ReliabilityMartReadTest.setUpClass()
        cls.database = ReliabilityMartReadTest.database
        cls.app = create_app()
        cls.service = ReliabilityQueryService(MartQueryRepository(cls.database))

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test_vendor_neutral_assets_and_legacy_routes_are_present(self):
        body = reliability_api.list_assets(offset=0, limit=1, service=self.service)
        self.assertEqual(body["meta"].total, 2)
        self.assertNotIn("sources", body["items"][0].model_dump())
        paths = self.app.openapi()["paths"]
        self.assertIn("/equipment", paths)
        self.assertIn("/work-orders", paths)
        self.assertIn("/v1/reliability/assets", paths)

    def test_scope_and_filter_safety(self):
        asset_schema = self.app.openapi()["paths"]["/v1/reliability/assets"]["get"]["parameters"]
        site_parameter = next(item for item in asset_schema if item["name"] == "site_code")
        limit_parameter = next(item for item in asset_schema if item["name"] == "limit")
        self.assertEqual(site_parameter["schema"]["const"], "BSR")
        self.assertEqual(limit_parameter["schema"]["maximum"], 200)
        with self.assertRaises(HTTPException) as error:
            reliability_api.rcfa(asset_ref=ASSET_A, service=self.service)
        self.assertEqual(error.exception.status_code, 422)

    def test_context_timeline_and_unresolved_overhaul(self):
        context = reliability_api.asset_context(ASSET_A, service=self.service)
        self.assertEqual(context.rcfa_relationship_status, "UNRESOLVED")
        timeline = reliability_api.asset_timeline(ASSET_A, offset=0, limit=50, service=self.service)["items"]
        self.assertEqual(len(timeline), 4)
        overhauls = reliability_api.overhauls(workorder_ref="WO-MISSING", offset=0, limit=50, service=self.service)
        self.assertIsNone(overhauls["items"][0].asset_ref)

    def test_missing_asset_is_404_and_integrity_is_aggregate_only(self):
        with self.assertRaises(HTTPException) as error:
            reliability_api.get_asset("not-found", service=self.service)
        self.assertEqual(error.exception.status_code, 404)
        body = reliability_api.integrity(service=self.service).model_dump()
        self.assertEqual(body["workorder_refs_unresolved"], 1)
        self.assertNotIn("canonical_id", body)
        with self.assertRaises(HTTPException) as technical_error:
            reliability_api.get_asset(TECHNICAL_ASSET, service=self.service)
        self.assertEqual(technical_error.exception.status_code, 404)

    def test_registry_endpoint_is_available(self):
        body = reliability_api.registry(service=self.service)
        self.assertEqual(body.registered_asset_count, 2)


if __name__ == "__main__":
    unittest.main()
