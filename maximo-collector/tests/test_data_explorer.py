"""Hermetic Data Explorer API/service tests; no Maximo network."""

from __future__ import annotations

import copy
import unittest

from src.adapters.maximo.canonical_mappers import (
    asset_health_assessment_from_payload,
    asset_master_from_payload,
    fmea_assessment_from_payload,
    maintenance_event_from_payload,
    overhaul_event_from_payload,
    rcfa_analysis_from_payload,
)
from src.api.app import create_app
from src.config import DbConfig
from src.repositories.database import Database
from src.repositories.store import CollectorStore
from src.services.canonical import CanonicalCollection
from src.services.data_explorer import DataExplorerService, RESOURCE_SPECS
from src.services.mart import MartWriter
from tests.fixtures.canonical_payloads import ASSET, BHM, FMEA, OVERHAUL, RCFA, WORK_ORDER


class DataExplorerTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(DbConfig("sqlite+pysqlite:///:memory:"))
        self.db.create_all()
        self.writer = MartWriter(self.db)
        self.store = CollectorStore(self.db)
        self.service = DataExplorerService(self.store)
        self.records = self._records()
        for entity, record in self.records.items():
            self.writer.persist_collection(CanonicalCollection(entity, records=[record]))

    def tearDown(self):
        self.db.engine.dispose()

    @staticmethod
    def _records():
        asset = asset_master_from_payload(ASSET)
        work_order = maintenance_event_from_payload(WORK_ORDER)
        return {
            "asset_master": asset,
            "maintenance_event": work_order,
            "fmea_assessment": fmea_assessment_from_payload(FMEA),
            "rcfa_analysis": rcfa_analysis_from_payload(RCFA),
            "asset_health_assessment": asset_health_assessment_from_payload(BHM),
            "overhaul_event": overhaul_event_from_payload(OVERHAUL, workorder_index={WORK_ORDER["wonum"]: work_order}),
        }

    def test_resource_catalog_has_six_sources_and_deferred_are_not_browsable(self):
        catalog = self.service.resources()
        self.assertEqual({item["source_object"] for item in catalog["resources"]}, set(RESOURCE_SPECS))
        self.assertEqual(len(catalog["resources"]), 6)
        self.assertEqual(len(catalog["deferred"]), 4)
        self.assertIn("integrity", catalog)
        self.assertEqual(catalog["integrity"]["asset_reference_total"], 4)
        self.assertEqual(catalog["integrity"]["asset_reference_resolved"], 4)
        with self.assertRaises(KeyError):
            self.service.resolve_resource("IPFMEAITEM")

    def test_source_preview_is_selected_field_allowlist_only(self):
        result = self.service.source_records("IPFMEA", limit=50)
        self.assertEqual(result["meta"]["total"], 1)
        source = result["items"][0]["source_data"]
        self.assertEqual(set(source), set(RESOURCE_SPECS["IPFMEA"].selected_fields))
        self.assertNotIn("href", source)
        self.assertNotIn("fmea_asset_collectionref", source)

    def test_source_allowlist_does_not_leak_unexpected_json_keys(self):
        with self.db.session() as session:
            from src.repositories.mart_models import FmeaAssessmentMartOrm
            row = session.get(FmeaAssessmentMartOrm, self.records["fmea_assessment"]["canonical_id"])
            sources = copy.deepcopy(row.sources)
            sources["maximo"]["password"] = "synthetic-secret"
            sources["maximo"]["unexpected"] = "must-not-escape"
            row.sources = sources
            session.commit()
        source = self.service.record_detail("IPFMEA", self.records["fmea_assessment"]["canonical_id"])["source_data"]
        self.assertNotIn("password", source)
        self.assertNotIn("unexpected", source)

    def test_record_detail_has_safe_source_canonical_provenance_evidence_and_mapping(self):
        detail = self.service.record_detail("IPFMEA", self.records["fmea_assessment"]["canonical_id"])
        self.assertIn("source_data", detail)
        self.assertIn("canonical", detail)
        self.assertIn("provenance", detail)
        self.assertIn("relationship_evidence", detail)
        self.assertIn("mapping", detail)
        self.assertEqual(detail["provenance"]["source_system"], "MAXIMO")
        self.assertEqual(detail["relationship_evidence"]["asset_ref"]["status"], "DIRECT_VERIFIED")
        self.assertTrue(any(item["source_field"] == "assetnum" for item in detail["mapping"]))
        self.assertNotIn("sources", detail["canonical"])

    def test_all_six_mart_entities_are_paginated_and_empty_state_is_explicit(self):
        entities = {item["entity"] for item in [self.service.mart_records(entity) for entity in (
            "asset_master", "maintenance_event", "fmea_assessment", "rcfa_analysis", "asset_health_assessment", "overhaul_event"
        )]}
        self.assertEqual(len(entities), 6)
        self.assertEqual(self.service.mart_records("fmea_assessment", limit=1)["meta"]["limit"], 1)

        empty_db = Database(DbConfig("sqlite+pysqlite:///:memory:"))
        empty_db.create_all()
        empty = DataExplorerService(CollectorStore(empty_db)).resource_metadata("IPFMEA")
        self.assertEqual(empty["records"], 0)
        self.assertEqual(empty["status"], "CONFIGURED_EMPTY")
        empty_db.engine.dispose()

    def test_api_is_get_only_and_has_bounded_query_parameters(self):
        app = create_app()
        paths = app.openapi()["paths"]
        explorer_paths = [path for path in paths if path.startswith("/data-explorer")]
        self.assertEqual(len(explorer_paths), 8)
        for path in explorer_paths:
            self.assertEqual(set(paths[path]), {"get"})
        params = paths["/data-explorer/resources/{resource}/records"]["get"]["parameters"]
        limit = next(item for item in params if item["name"] == "limit")
        self.assertEqual(limit["schema"]["maximum"], 200)

    def test_unknown_record_and_entity_are_rejected(self):
        with self.assertRaises(KeyError):
            self.service.record_detail("IPFMEA", "not-present")
        with self.assertRaises(KeyError):
            self.service.mart_records("raw_sql_table")


if __name__ == "__main__":
    unittest.main()
