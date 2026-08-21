"""Synthetic MX-011C baseline tests; no production report or rows are used."""

from __future__ import annotations

import unittest
from src.adapters.maximo.oslc_client import OslcPaginationLimitError
from src.services.asset_baseline import (
    asset_baseline_config,
    probe_asset_projection,
    validate_registry_snapshot,
)
from src.services.asset_registry_reconciliation import RegistryRecord, RegistrySnapshot


SYNTHETIC_ASSET = {
    "assetnum": "SYNTHETIC-ASSET-001",
    "assetid": "1",
    "description": "synthetic equipment",
    "siteid": "BSR",
    "orgid": "IP",
    "status": "OPERATING",
    "assettype": "PUMP",
    "eq11": "CS01",
    "changedate": "2026-08-20T00:00:00Z",
}


class FakeProjectionClient:
    def __init__(self, *, detail_requests: int = 0, truncate: bool = True):
        self.detail_requests = detail_requests
        self.truncate = truncate
        self.last_iteration_pages = 0
        self.request_telemetry = {
            "business_requests": 0,
            "status_counts": {},
            "detail_requests": 0,
        }

    def iterate(self, object_structure, **kwargs):
        self.last_iteration_pages = 1
        self.request_telemetry["business_requests"] += 1
        self.request_telemetry["detail_requests"] += self.detail_requests
        yield dict(SYNTHETIC_ASSET)
        if self.truncate:
            raise OslcPaginationLimitError(
                object_structure,
                pages=1,
                max_pages=1,
                next_page_fingerprint="synthetic-page",
            )


class AssetBaselineTest(unittest.TestCase):
    def test_projection_config_is_bounded_and_explicit(self):
        config = asset_baseline_config(page_size=100, max_pages=100)
        self.assertEqual(config.object_structure, "mxapiasset")
        self.assertEqual(config.required_values, (("eq11", "CS01"),))
        self.assertEqual(config.scope_clause, 'siteid="BSR"')
        self.assertEqual(config.order_by, "-changedate")
        self.assertEqual(config.page_size, 100)
        self.assertEqual(config.max_pages, 100)
        self.assertIn("failurecode", config.select)
        self.assertTrue(config.cursor_requires_zero_errors)

    def test_projection_probe_maps_without_detail_requests(self):
        result = probe_asset_projection(
            FakeProjectionClient(),
            asset_baseline_config(page_size=50, max_pages=200),
        )
        self.assertTrue(result["passed"])
        self.assertTrue(result["projection_safe"])
        self.assertEqual(result["rows"], 1)
        self.assertEqual(result["mapped"], 1)
        self.assertEqual(result["detail_requests"], 0)
        self.assertTrue(result["pagination_truncated"])

    def test_projection_probe_rejects_detail_request_path(self):
        result = probe_asset_projection(
            FakeProjectionClient(detail_requests=1),
            asset_baseline_config(),
        )
        self.assertFalse(result["passed"])
        self.assertFalse(result["projection_safe"])

    def test_registry_validation_is_fingerprint_and_shape_bound(self):
        snapshot = RegistrySnapshot(
            format="html-table",
            sheet="List of Assets",
            rows=1,
            records=(RegistryRecord("SYNTHETIC-ASSET-001", None, frozenset()),),
            field_present={},
            byte_size=1,
            sha256="synthetic-fingerprint",
        )
        validate_registry_snapshot(snapshot, expected_sha256="synthetic-fingerprint", expected_rows=1)
        with self.assertRaisesRegex(Exception, "REGISTRY_FINGERPRINT_MISMATCH"):
            validate_registry_snapshot(snapshot, expected_sha256="other", expected_rows=1)


if __name__ == "__main__":
    unittest.main()
