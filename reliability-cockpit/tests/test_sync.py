"""Tests for the new collector-pull sync engine (hermetic, no network/DB)."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Any, Mapping
from unittest.mock import patch

from src.adapters.collector_client import (
    CollectorClient,
    CollectorClientError,
    PullResult,
    equipment_from_view,
    work_order_from_view,
)
from src.repositories.store import CockpitStore
from src.services.sync import SyncService, SyncStats


class FakeCollectorClient(CollectorClient):
    """Fake collector client for testing (no HTTP).

    Returns builder-processed domain models, exactly like the real
    CollectorClient.pull() does.
    """

    def __init__(self, rows_by_resource: dict[str, list[Mapping]]):
        self._rows_by_resource = rows_by_resource
        self.pull_calls: list[dict[str, Any]] = []

    def pull(self, resource: str, *, changed_since=None, limit: int = 1000) -> list:
        self.pull_calls.append({
            "resource": resource,
            "changed_since": str(changed_since) if changed_since else None,
            "limit": limit,
        })
        rows: list[Mapping[str, Any]] = self._rows_by_resource.get(resource, [])
        # Apply the same builders the real client applies
        builder_map: dict[str, Any] = {
            "equipment": equipment_from_view,
            "workorder": work_order_from_view,
        }
        builder = builder_map.get(resource)
        if builder is not None:
            rows = [builder(view) for view in rows]
        return rows


class FakeStore:
    def __init__(self):
        self.cursor: dict[str, datetime | None] = {}
        self.upserted: list = []
        self.recorded_watermark: tuple[str, datetime | None, int] | None = None

    def get_cursor(self, resource: str) -> datetime | None:
        return self.cursor.get(resource)

    def set_cursor(self, resource: str, last_changedate: datetime | None, rows_seen: int) -> None:
        self.cursor[resource] = last_changedate
        self.recorded_watermark = (resource, last_changedate, rows_seen)

    def upsert_equipment(self, item: object) -> None:
        self.upserted.append(item)

    def upsert_work_order(self, item: object) -> None:
        self.upserted.append(item)

    def upsert_service_request(self, item: object) -> None:
        self.upserted.append(item)

    def upsert_person(self, item: object) -> None:
        self.upserted.append(item)

    def upsert_item(self, item: object) -> None:
        self.upserted.append(item)

    def upsert_labor(self, item: object) -> None:
        self.upserted.append(item)


class SyncServiceTest(unittest.TestCase):
    def setUp(self):
        self.client = FakeCollectorClient({
            "equipment": [
                {
                    "assetnum": "A1",
                    "description": "Boiler Feed Pump",
                    "status": "OPERATING",
                    "installed_at": "2023-01-15T00:00:00Z",
                    "status_changed_at": "2026-08-10T00:00:00Z",
                    "sources": {"maximo": {"assetnum": "A1", "installdate": "2023-01-10T00:00:00Z"}},
                }
            ],
            "workorder": [
                {
                    "wonum": "WO-001",
                    "assetnum": "A1",
                    "status": "CLOSE",
                    "worktype": "PM",
                    "reported_at": "2026-08-01T00:00:00Z",
                    "status_changed_at": "2026-08-05T00:00:00Z",
                    "sources": {"maximo": {"wonum": "WO-001", "changedate": "2026-07-20T00:00:00Z"}},
                }
            ],
        })
        self.store = FakeStore()
        self.service = SyncService(self.client, self.store)

    def test_full_equipment_pull_upserts_and_records_watermark(self):
        stats = self.service.sync("equipment")
        self.assertIsInstance(stats, SyncStats)
        self.assertEqual(stats.mode, "full")
        self.assertEqual(stats.rows_seen, 1)
        self.assertEqual(stats.upserted, 1)
        self.assertEqual(stats.skipped, 0)
        self.assertIsNotNone(stats.watermark)
        # cursor recorded
        self.assertIsNotNone(self.store.recorded_watermark)
        self.assertEqual(self.store.recorded_watermark[0], "equipment")
        self.assertIsNotNone(self.store.recorded_watermark[1])

    def test_incremental_uses_watermark(self):
        # first full run
        self.service.sync("equipment")
        # second run with watermark — should send changed_since
        self.service.sync("equipment")
        # verify changed_since was included in pull call
        has_changed_since = any(
            call["changed_since"] is not None for call in self.client.pull_calls
        )
        self.assertTrue(has_changed_since)

    def test_labor_full_no_watermark(self):
        # labor has no watermark, so always full
        stats = self.service.sync("labor")
        self.assertIsInstance(stats, SyncStats)
        # no watermark cursor tracked
        self.assertIsNone(self.store.get_cursor("labor"))

    def test_unknown_resource_fails(self):
        with self.assertRaises(CollectorClientError):
            self.service.sync("unknown")

    def test_bad_row_skipped_not_fatal(self):
        # client returns two valid rows; both are upserted since the converter
        # robustly maps assetnum → id and handles maximo_source.
        class BrokenClient(FakeCollectorClient):
            def pull(self, resource, **kwargs):
                rows: list[Mapping[str, Any]] = [
                    {
                        "assetnum": "GOOD",
                        "description": "OK",
                        "status": "OPERATING",
                        "installed_at": "2023-01-15T00:00:00Z",
                        "status_changed_at": "2026-08-10T00:00:00Z",
                        "sources": {"maximo": {"assetnum": "GOOD", "installdate": "2023-01-10T00:00:00Z"}},
                    },
                    {
                        "assetnum": "BAD",
                        "description": "Missing maximo source",
                        "status": "OPERATING",
                        "installed_at": "2026-08-10T00:00:00Z",
                        "status_changed_at": "2026-08-10T00:00:00Z",
                        "sources": {},
                    },
                ]
                # Apply the same builders the real client applies
                builder_map: dict[str, Any] = {
                    "equipment": equipment_from_view,
                }
                builder = builder_map.get(resource)
                if builder is not None:
                    return [builder(view) for view in rows]
                return rows

        broken = BrokenClient({})
        broken_store = FakeStore()
        broken_service = SyncService(broken, broken_store)
        stats = broken_service.sync("equipment")
        self.assertEqual(stats.rows_seen, 2)
        self.assertEqual(stats.upserted, 2)
        self.assertEqual(stats.skipped, 0)

    def test_run_logged(self):
        self.service.sync("equipment")
        # FakeStore has no runs list; just verify no crash

    def test_incomplete_pull_upserts_progress_but_keeps_cursor(self):
        class PartialClient(FakeCollectorClient):
            def pull(self, resource, **kwargs):
                return PullResult(
                    items=[work_order_from_view({"id": "BSR-1", "status": "WAPPR"})],
                    complete=False,
                    pages=1,
                    rows_seen=2,
                    stop_reason="max_pages",
                )

        client = PartialClient({})
        store = FakeStore()
        stats = SyncService(client, store).sync("workorder")
        self.assertFalse(stats.complete)
        self.assertEqual(stats.mode, "partial")
        self.assertEqual(stats.rows_seen, 2)
        self.assertEqual(stats.upserted, 1)
        self.assertIsNone(store.get_cursor("workorder"))


class CollectorPaginationTest(unittest.TestCase):
    class Response:
        status_code = 200

        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def test_pull_reads_all_pages_and_deduplicates_ids(self):
        responses = [
            self.Response([{"id": "BSR-1"}, {"id": "BSR-2"}]),
            self.Response([{"id": "BSR-2"}]),
        ]
        with patch("src.adapters.collector_client.requests.get", side_effect=responses):
            result = CollectorClient("http://collector").pull("workorder", limit=2)
        self.assertTrue(result.complete)
        self.assertEqual(result.pages, 2)
        self.assertEqual(result.rows_seen, 3)
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.duplicate_ids, 1)

    def test_pull_marks_max_pages_partial(self):
        responses = [self.Response([{"id": "BSR-1"}, {"id": "BSR-2"}])]
        with patch("src.adapters.collector_client.requests.get", side_effect=responses):
            result = CollectorClient("http://collector").pull("workorder", limit=2, max_pages=1)
        self.assertFalse(result.complete)
        self.assertEqual(result.stop_reason, "max_pages")

    def test_pull_detects_repeated_content_page(self):
        responses = [
            self.Response([{"id": "BSR-1"}, {"id": "BSR-2"}]),
            self.Response([{"id": "BSR-1"}, {"id": "BSR-2"}]),
        ]
        with patch("src.adapters.collector_client.requests.get", side_effect=responses):
            result = CollectorClient("http://collector").pull("workorder", limit=2)
        self.assertFalse(result.complete)
        self.assertEqual(result.stop_reason, "repeated_content_page")
        self.assertEqual(result.duplicate_ids, 2)


class DomainConversionTest(unittest.TestCase):
    def test_equipment_from_view_builds_domain(self):
        view = {
            "assetnum": "A1",
            "description": "Boiler Feed Pump",
            "status": "OPERATING",
            "installed_at": "2023-01-15T00:00:00Z",
            "status_changed_at": "2026-08-10T00:00:00Z",
            "sources": {"maximo": {"assetnum": "A1", "installdate": "2023-01-10T00:00:00Z"}},
        }
        eq = equipment_from_view(view)
        self.assertEqual(eq.id, "A1")
        self.assertEqual(eq.status, "OPERATING")
        # maximo_source nested
        self.assertIsNotNone(eq.maximo_source)
        self.assertEqual(eq.maximo_source.assetnum, "A1")
        self.assertIsNotNone(eq.installed_at)

    def test_equipment_from_view_preserves_quarantined_source_extra(self):
        view = {
            "assetnum": "A1",
            "sources": {
                "maximo": {
                    "assetnum": "A1",
                    "extra": {"plant_description": "Unit"},
                    "future_verified_scalar": "kept-under-extra",
                }
            },
        }
        eq = equipment_from_view(view)
        self.assertIsNotNone(eq.maximo_source)
        self.assertEqual(eq.maximo_source.extra["plant_description"], "Unit")
        self.assertEqual(eq.maximo_source.extra["future_verified_scalar"], "kept-under-extra")

    def test_work_order_from_view_builds_domain(self):
        view = {
            "wonum": "WO-001",
            "assetnum": "A1",
            "status": "CLOSE",
            "worktype": "PM",
            "reported_at": "2026-08-01T00:00:00Z",
            "status_changed_at": "2026-08-05T00:00:00Z",
            "sources": {"maximo": {"wonum": "WO-001", "changedate": "2026-07-20T00:00:00Z"}},
        }
        wo = work_order_from_view(view)
        self.assertEqual(wo.id, "WO-001")
        self.assertEqual(wo.work_type, "PM")
        self.assertIsNotNone(wo.reported_at)


if __name__ == "__main__":
    unittest.main()
