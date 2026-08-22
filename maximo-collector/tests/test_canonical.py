"""Hermetic MX-007R canonical boundary tests; no network or database."""

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
from src.canonical_identity import canonical_id
from src.contracts.mapping_drift import assert_mapping_contract
from src.contracts.validator import ContractValidationError, validate_record
from src.services.canonical import CANONICAL_CONFIGS, CanonicalCollector
from tests.fixtures.canonical_payloads import ASSET, BHM, FMEA, OVERHAUL, RCFA, WORK_ORDER


class FakeCanonicalClient:
    def __init__(self, records_by_object):
        self.records_by_object = records_by_object
        self.calls = []

    def iterate(self, object_structure, **kwargs):
        self.calls.append((object_structure, kwargs))
        yield from self.records_by_object.get(object_structure, [])


class CanonicalMapperTest(unittest.TestCase):
    def test_identity_is_deterministic_and_scope_safe(self):
        first = canonical_id("asset", "MXASSET", "<asset>", "BSR", "IP")
        self.assertEqual(first, canonical_id("asset", "MXASSET", "<asset>", "BSR", "IP"))
        self.assertNotEqual(first, canonical_id("asset", "MXASSET", "<asset>", "OTHER", "IP"))

    def test_all_synthetic_mappers_validate(self):
        records = [
            ("asset_master", asset_master_from_payload(ASSET)),
            ("maintenance_event", maintenance_event_from_payload(WORK_ORDER)),
            ("fmea_assessment", fmea_assessment_from_payload(FMEA)),
            ("rcfa_analysis", rcfa_analysis_from_payload(RCFA)),
            ("asset_health_assessment", asset_health_assessment_from_payload(BHM)),
            ("overhaul_event", overhaul_event_from_payload(OVERHAUL)),
        ]
        for entity, record in records:
            validated = validate_record(entity, record)
            self.assertEqual(validated["contract_version"], "1.0")
            self.assertEqual(validated["provenance"]["source_system"], "MAXIMO")

    def test_asset_master_uses_scoped_source_number_not_raw_id(self):
        record = asset_master_from_payload(ASSET)
        self.assertEqual(record["source_asset_number"], "<asset-number>")
        self.assertTrue(record["canonical_id"].startswith("asset:MAXIMO:MXASSET:BSR:IP:"))
        self.assertEqual(record["relationship_evidence"]["location_ref"]["status"], "DIRECT_VERIFIED")

    def test_maintenance_preserves_legacy_shape_and_source_value(self):
        record = maintenance_event_from_payload(WORK_ORDER)
        self.assertTrue(record["id"].startswith("maintenance_event:MAXIMO:MXWODETAIL:BSR:IP:"))
        self.assertTrue(record["work_order_id"].startswith("workorder:MAXIMO:MXWODETAIL:BSR:IP:"))
        self.assertEqual(record["work_type"], "PM")
        self.assertEqual(record["event_type"], "PM")
        self.assertEqual(record["relationship_evidence"]["equipment_id"]["status"], "DIRECT_VERIFIED")

    def test_fmea_mapping_and_identity_roles(self):
        record = fmea_assessment_from_payload(FMEA)
        self.assertEqual(record["source_record_id"], "<fmea-id>")
        self.assertEqual(record["source_number"], "<fmea-number>")
        self.assertTrue(record["asset_ref"].startswith("asset:MAXIMO:MXASSET:BSR:IP:"))
        self.assertTrue(record["failure_code_ref"].startswith("failure_code:MAXIMO:MXFAILURECODE:BSR:IP:"))
        self.assertNotEqual(record["source_record_id"], record["organization_code"])
        self.assertEqual(record["relationship_evidence"]["asset_ref"]["status"], "DIRECT_VERIFIED")

    def test_rcfa_relationships_remain_null_and_unresolved(self):
        record = rcfa_analysis_from_payload(RCFA)
        for field in ("asset_ref", "location_ref", "workorder_ref", "failure_event_ref"):
            self.assertIsNone(record[field])
            self.assertEqual(record["relationship_evidence"][field]["status"], "UNRESOLVED")

    def test_bhm_keeps_eid_as_source_attribute_only(self):
        record = asset_health_assessment_from_payload(BHM)
        self.assertEqual(record["source_record_id"], "<bhm-id>")
        self.assertEqual(record["sources"]["maximo"]["eid"], "<unknown-eid>")
        self.assertNotEqual(record["source_record_id"], record["sources"]["maximo"]["eid"])
        self.assertTrue(record["asset_ref"].startswith("asset:MAXIMO:MXASSET:BSR:IP:"))

    def test_overhaul_direct_workorder_and_derived_asset(self):
        workorder = maintenance_event_from_payload(WORK_ORDER)
        record = overhaul_event_from_payload(OVERHAUL, workorder_index={WORK_ORDER["wonum"]: workorder})
        self.assertEqual(record["workorder_ref"], workorder["work_order_id"])
        self.assertEqual(record["asset_ref"], workorder["equipment_id"])
        self.assertEqual(record["relationship_evidence"]["workorder_ref"]["status"], "DIRECT_VERIFIED")
        self.assertEqual(record["relationship_evidence"]["asset_ref"]["status"], "DERIVED_VERIFIED_PATH")
        self.assertEqual(record["unresolved_source_attributes"]["performance_test"], "<unresolved-performance-test>")
        self.assertNotEqual(record["source_record_id"], WORK_ORDER["wonum"])

    def test_overhaul_missing_workorder_keeps_asset_null(self):
        record = overhaul_event_from_payload(OVERHAUL, workorder_index={})
        self.assertIsNone(record["asset_ref"])
        self.assertEqual(record["relationship_evidence"]["asset_ref"]["status"], "DERIVED_VERIFIED_PATH")

    def test_no_raw_payload_or_deferred_source_ingestion(self):
        record = asset_master_from_payload(ASSET)
        text = repr(record)
        self.assertNotIn("href", text)
        self.assertNotIn("createdby", text)
        self.assertNotIn("collectionref", text)
        for deferred in ("IPFMEAITEM", "IPBHMMEASUREMENT", "DMD_OPLOGABN", "IPMSMSFAILUREMECHANI"):
            self.assertNotIn(deferred, CANONICAL_CONFIGS)

    def test_missing_required_provenance_and_version_are_rejected(self):
        record = asset_master_from_payload(ASSET)
        invalid = copy.deepcopy(record)
        del invalid["provenance"]
        with self.assertRaises(ContractValidationError):
            validate_record("asset_master", invalid)
        invalid = copy.deepcopy(record)
        invalid["contract_version"] = "2.0"
        with self.assertRaises(ContractValidationError):
            validate_record("asset_master", invalid)


class CanonicalCollectorTest(unittest.TestCase):
    def test_allowlisted_collection_uses_bsr_scope_and_emits_records(self):
        client = FakeCanonicalClient({"iprcfa": [RCFA]})
        result = CanonicalCollector(client).collect_rcfa()
        self.assertEqual(result.stats.source_records_read, 1)
        self.assertEqual(result.stats.canonical_records_emitted, 1)
        self.assertEqual(client.calls[0][1]["where"], 'siteid="BSR"')
        self.assertEqual(client.calls[0][1]["required_scope"], 'siteid="BSR"')

    def test_smoke_limit_bounds_records_and_pages(self):
        client = FakeCanonicalClient({"iprcfa": [RCFA, RCFA]})
        result = CanonicalCollector(client).collect_rcfa(max_records=1)
        self.assertEqual(result.stats.source_records_read, 1)
        self.assertEqual(result.stats.canonical_records_emitted, 1)
        self.assertEqual(client.calls[0][1]["max_pages"], 1)
        self.assertEqual(result.completeness, "CAPPED")

    def test_explicit_max_pages_enables_bounded_multi_page_mode(self):
        client = FakeCanonicalClient({"iprcfa": [RCFA, {**RCFA, "rcfaid": "<rcfa-id-2>"}]})
        result = CanonicalCollector(client).collect_rcfa(max_records=3, max_pages=2)
        self.assertEqual(result.stats.source_records_read, 2)
        self.assertEqual(client.calls[0][1]["max_pages"], 2)
        self.assertEqual(result.completeness, "EXHAUSTED")

    def test_source_record_cap_is_not_emitted_record_cap(self):
        rejected = {**ASSET, "assetid": "<asset-id-2>", "eq11": "OTHER"}
        client = FakeCanonicalClient({"mxasset": [rejected, rejected, rejected, ASSET]})
        result = CanonicalCollector(client).collect_assets(max_records=3, max_pages=2)
        self.assertEqual(result.stats.source_records_read, 3)
        self.assertEqual(result.stats.canonical_records_emitted, 0)
        self.assertEqual(result.completeness, "CAPPED")

    def test_overhaul_resolution_uses_existing_records_without_extra_client_call(self):
        client = FakeCanonicalClient({"ip_dom_oh": [OVERHAUL]})
        workorder = maintenance_event_from_payload(WORK_ORDER)
        result = CanonicalCollector(client).collect_overhauls([workorder])
        self.assertEqual(result.records[0]["asset_ref"], workorder["equipment_id"])
        self.assertEqual(len(client.calls), 1)

    def test_mapping_drift_guard_requires_verified_relationships(self):
        self.assertTrue(assert_mapping_contract())


if __name__ == "__main__":
    unittest.main()
