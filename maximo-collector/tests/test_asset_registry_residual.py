"""Synthetic tests for bounded registered-Asset residual repair."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from src.services.asset_registry_reconciliation import (
    EquipmentSnapshot,
    LocalReconciliationInput,
    RegistryRecord,
    RegistrySnapshot,
)
from src.services.asset_registry_residual import (
    PRIMARY_REQUEST_LIMIT,
    TOTAL_REQUEST_LIMIT,
    derive_residual_ids,
    lookup_residual,
    run_asset_registry_residual_repair,
)


SYNTHETIC_RESIDUAL = "SYNTHETIC-RESIDUAL-001"
SYNTHETIC_EXISTING = "SYNTHETIC-EXISTING-001"


def synthetic_payload(assetnum: str = SYNTHETIC_RESIDUAL, **overrides):
    payload = {
        "assetnum": assetnum,
        "assetid": "1",
        "description": "synthetic equipment",
        "siteid": "BSR",
        "orgid": "IP",
        "status": "OPERATING",
        "assettype": "PUMP",
        "eq11": "CS01",
        "changedate": "2026-08-20T00:00:00Z",
    }
    payload.update(overrides)
    return payload


class FakeExactClient:
    def __init__(self, rows=None, *, paginate=False):
        self.rows = list(rows or [])
        self.paginate = paginate
        self.calls = []
        self.request_telemetry = {"business_requests": 0, "detail_requests": 0, "status_counts": {}}

    def iterate(self, object_structure, **kwargs):
        self.calls.append((object_structure, kwargs))
        self.request_telemetry["business_requests"] += 1
        self.request_telemetry["status_counts"]["200"] = self.request_telemetry["status_counts"].get("200", 0) + 1
        yield from self.rows
        if self.paginate:
            from src.adapters.maximo.oslc_client import OslcPaginationLimitError

            raise OslcPaginationLimitError(
                object_structure, pages=1, max_pages=1, next_page_fingerprint="synthetic"
            )


class ResidualLookupTest(unittest.TestCase):
    def test_residual_derivation_is_local_and_normalized(self):
        registry = RegistrySnapshot(
            format="html-table",
            sheet="List of Assets",
            rows=2,
            records=(
                RegistryRecord("synthetic-residual-001", None, frozenset()),
                RegistryRecord(SYNTHETIC_EXISTING, None, frozenset()),
            ),
            field_present={},
            byte_size=1,
            sha256="synthetic",
        )
        local = LocalReconciliationInput(
            equipment=(EquipmentSnapshot(SYNTHETIC_EXISTING),),
            work_orders=(),
        )
        self.assertEqual(derive_residual_ids(registry, local), (SYNTHETIC_RESIDUAL,))

    def test_exact_mxapiasset_lookup_maps_one_row(self):
        client = FakeExactClient([synthetic_payload()])
        result = lookup_residual(client, "mxapiasset", SYNTHETIC_RESIDUAL)
        self.assertEqual(result.outcome, "FOUND")
        self.assertEqual(result.requests, 1)
        self.assertIsNotNone(result.equipment)
        self.assertEqual(result.equipment.id, SYNTHETIC_RESIDUAL)
        self.assertIn('assetnum="SYNTHETIC-RESIDUAL-001"', client.calls[0][1]["where"])

    def test_not_found_and_identity_mismatch_are_distinct(self):
        not_found = lookup_residual(FakeExactClient(), "mxapiasset", SYNTHETIC_RESIDUAL)
        mismatch = lookup_residual(
            FakeExactClient([synthetic_payload("SYNTHETIC-OTHER-001")]),
            "mxapiasset",
            SYNTHETIC_RESIDUAL,
        )
        self.assertEqual(not_found.outcome, "NOT_FOUND")
        self.assertEqual(mismatch.outcome, "IDENTITY_MISMATCH")

    def test_scope_mapping_and_pagination_safety(self):
        scope = lookup_residual(
            FakeExactClient([synthetic_payload(eq11="CS02")]),
            "mxapiasset",
            SYNTHETIC_RESIDUAL,
        )
        ambiguous = lookup_residual(
            FakeExactClient([synthetic_payload()], paginate=True),
            "mxapiasset",
            SYNTHETIC_RESIDUAL,
        )
        with patch(
            "src.services.asset_registry_residual.equipment_from_payload",
            side_effect=ValueError("synthetic mapping failure"),
        ):
            mapping = lookup_residual(
                FakeExactClient([synthetic_payload()]),
                "mxapiasset",
                SYNTHETIC_RESIDUAL,
            )
        self.assertEqual(scope.outcome, "SCOPE_MISMATCH")
        self.assertEqual(ambiguous.outcome, "SOURCE_IDENTITY_AMBIGUITY")
        self.assertEqual(mapping.outcome, "MAPPING_ERROR")

    def test_mxasset_fallback_is_diagnostic_only(self):
        primary = FakeExactClient()
        fallback = FakeExactClient([synthetic_payload()])
        result = lookup_residual(primary, "mxapiasset", SYNTHETIC_RESIDUAL)
        self.assertEqual(result.outcome, "NOT_FOUND")
        fallback_result = lookup_residual(
            fallback, "mxasset", SYNTHETIC_RESIDUAL, map_result=False
        )
        self.assertEqual(fallback_result.outcome, "FOUND")
        self.assertEqual(fallback_result.equipment, None)


class ResidualRepairSafetyTest(unittest.TestCase):
    def test_complete_registry_repair_upserts_without_cursor_or_full_run(self):
        registry = RegistrySnapshot(
            format="html-table",
            sheet="List of Assets",
            rows=2,
            records=(
                RegistryRecord(SYNTHETIC_EXISTING, None, frozenset()),
                RegistryRecord(SYNTHETIC_RESIDUAL, None, frozenset()),
            ),
            field_present={},
            byte_size=1,
            sha256="synthetic",
        )
        local_before = LocalReconciliationInput(
            equipment=(EquipmentSnapshot(SYNTHETIC_EXISTING),),
            work_orders=(),
        )
        local_after = LocalReconciliationInput(
            equipment=(EquipmentSnapshot(SYNTHETIC_EXISTING), EquipmentSnapshot(SYNTHETIC_RESIDUAL)),
            work_orders=(),
        )

        def report(missing: int, total: int):
            return {
                "collector_equipment": {"total": total},
                "registry_reconciliation": {
                    "registry_assets_total": 2,
                    "exact_equipment_matches": 2 - missing,
                    "registry_assets_missing_from_collector": missing,
                    "exact_match_percentage": 100.0 if not missing else 50.0,
                    "parents_matching_collector": 0,
                    "parents_missing_from_collector": 0,
                },
                "work_order_relationships": {
                    "recent_local_period": {
                        "available": True,
                        "rows": 0,
                        "relationship_distribution": {},
                    },
                    "all": {"direct_registry_target_missing_from_collector": 0},
                },
            }

        class FakeStore:
            def __init__(self, _database):
                self.upserts = []

            def get_cursor(self, scope):
                return None

            def upsert_equipment(self, equipment):
                self.upserts.append(equipment)
                return "inserted"

        client = FakeExactClient([synthetic_payload()])
        with (
            patch("src.services.asset_registry_residual.parse_registry_file", return_value=registry),
            patch("src.services.asset_registry_residual.validate_registry_snapshot"),
            patch(
                "src.services.asset_registry_residual.load_local_reconciliation_input",
                side_effect=[local_before, local_after],
            ),
            patch(
                "src.services.asset_registry_residual.reconcile_registry",
                side_effect=[report(1, 1), report(0, 2)],
            ),
            patch("src.services.asset_registry_residual.CollectorStore", FakeStore),
        ):
            result = run_asset_registry_residual_repair("synthetic.xls", object(), client=client)

        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["post_repair"]["registry_missing"], 0)
        self.assertEqual(result["writes"]["inserted"], 1)
        self.assertEqual(result["request_audit"]["total"], 1)
        self.assertLessEqual(result["request_audit"]["primary"], PRIMARY_REQUEST_LIMIT)
        self.assertLessEqual(result["request_audit"]["total"], TOTAL_REQUEST_LIMIT)
        self.assertEqual(result["cursor_after"], {"mxapiasset": None, "mxasset": None})
        self.assertFalse(result["collect_run_recorded"])
        self.assertFalse(result["full_technical_baseline_complete"])


if __name__ == "__main__":
    unittest.main()
