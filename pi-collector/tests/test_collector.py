"""Unit tests for the collector service (client + store faked)."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from typing import Any

from src.domain.models import AttributeRegistration, Snapshot, TimeseriesPoint
from src.services.collector import CollectorService


SAMPLE_ATTRS = [
    AttributeRegistration(
        attribute_id="BSR-BSR1-turbine-bearing_temperature-bearing_1_left",
        site="BSR", unit="BSR1", equipment="BSR1.Turbine",
        parameter="bearing_temperature",
        business_name="Bearing 1 Left Temperature",
        unit_of_measure="degC",
        web_id="F1DPwebid1",
    ),
    AttributeRegistration(
        attribute_id="BSR-BSR1-turbine-vibration-bearing_1x",
        site="BSR", unit="BSR1", equipment="BSR1.Turbine",
        parameter="vibration",
        business_name="Bearing 1X Vibration",
        unit_of_measure="um",
        web_id="F1DPwebid2",
    ),
]


class FakeClient:
    def __init__(self):
        self.snapshot_calls: list[str] = []
        self.interpolated_calls: list[tuple[str, str, str, str]] = []

    def get_snapshot(self, web_id: str) -> dict:
        self.snapshot_calls.append(web_id)
        return {
            "Timestamp": "2026-08-14T04:30:00Z",
            "Value": 77.5 if "webid1" in web_id else 51.2,
            "UnitsAbbreviation": "deg C" if "webid1" in web_id else "um",
            "Good": True,
        }

    def get_interpolated(self, web_id: str, *, start_time: str, end_time: str, interval: str, max_count: int = 5000) -> dict:
        self.interpolated_calls.append((web_id, start_time, end_time, interval))
        return {
            "Items": [
                {"Timestamp": "2026-08-14T03:00:00Z", "Value": 77.0, "Good": True},
                {"Timestamp": "2026-08-14T04:00:00Z", "Value": 77.5, "Good": True},
            ]
        }


class FakeStore:
    def __init__(self):
        self.snapshots: list[Snapshot] = []
        self.timeseries: list[TimeseriesPoint] = []
        self.cursors: dict[str, int] = {}
        self.runs: list = []
        self.progress: dict[tuple[str, str], datetime] = {}

    def list_active_attributes(self) -> list[AttributeRegistration]:
        return SAMPLE_ATTRS

    def upsert_snapshot(self, snap: Snapshot) -> None:
        self.snapshots.append(snap)

    def bulk_insert_timeseries(self, points: list[TimeseriesPoint]) -> int:
        self.timeseries.extend(points)
        return len(points)

    def set_cursor(self, scope: str, rows_seen: int) -> None:
        self.cursors[scope] = rows_seen

    def record_run(self, stats) -> None:
        self.runs.append(stats)

    def get_backfill_progress(self, interval: str) -> dict[str, datetime]:
        return {
            attr_id: ts
            for (attr_id, iv), ts in self.progress.items()
            if iv == interval
        }

    def record_backfill_progress(
        self, attribute_id: str, interval: str, last_timestamp: datetime
    ) -> None:
        self.progress[(attribute_id, interval)] = last_timestamp


class CollectorSnapshotTest(unittest.TestCase):
    def test_collect_snapshots_upserts_all(self):
        client = FakeClient()
        store = FakeStore()
        service = CollectorService(client, store)  # type: ignore[arg-type]
        stats = service.collect_snapshots()
        self.assertEqual(stats.attributes_seen, 2)
        self.assertEqual(stats.rows_collected, 2)
        self.assertEqual(stats.errors, 0)
        self.assertEqual(len(store.snapshots), 2)
        self.assertEqual(store.cursors["snapshot"], 2)
        # the run itself must be logged for the activity graph
        self.assertEqual(len(store.runs), 1)
        self.assertEqual(store.runs[0].scope, "snapshot")
        self.assertIsNotNone(store.runs[0].finished_at)

    def test_collect_continues_on_error(self):
        client = FakeClient()
        store = FakeStore()
        original = client.get_snapshot

        def fail_snapshot(web_id):
            if "webid2" in web_id:
                raise RuntimeError("simulated network error")
            return original(web_id)

        client.get_snapshot = fail_snapshot  # type: ignore
        service = CollectorService(client, store)  # type: ignore[arg-type]
        stats = service.collect_snapshots()
        self.assertEqual(stats.rows_collected, 1)
        self.assertEqual(stats.errors, 1)


class GoneDeactivationTest(unittest.TestCase):
    """410 Gone attributes must be deactivated, not retried forever."""

    def test_gone_attribute_deactivated(self):
        from src.adapters.pi.client import PiGoneError

        class GoneClient:
            def get_snapshot(self, web_id):
                if "webid2" in web_id:
                    raise PiGoneError("PI returned HTTP 410 Gone: PI Point not found")
                return {"Timestamp": "2026-08-14T04:30:00Z", "Value": 50.0, "Good": True}

        class Store:
            def __init__(self):
                self.deactivated = []

            def list_active_attributes(self):
                return SAMPLE_ATTRS

            def upsert_snapshot(self, snap):
                self.saved = snap

            def deactivate_attribute(self, attribute_id):
                self.deactivated.append(attribute_id)

            def set_cursor(self, scope, rows):
                pass

            def record_run(self, stats):
                pass

        store = Store()
        service = CollectorService(GoneClient(), store)  # type: ignore[arg-type]
        stats = service.collect_snapshots()
        # gone attribute (webid2) deactivated, healthy one (webid1) saved
        self.assertEqual(store.deactivated, [SAMPLE_ATTRS[1].attribute_id])
        self.assertEqual(len(stats.deactivated_attributes), 1)
        self.assertEqual(stats.rows_collected, 1)
        self.assertEqual(stats.errors, 1)


class CollectorBackfillTest(unittest.TestCase):
    def test_backfill_inserts_timeseries(self):
        client = FakeClient()
        store = FakeStore()
        service = CollectorService(client, store)  # type: ignore[arg-type]
        stats = service.backfill("*-1d", "*", interval="1h")
        self.assertEqual(stats.attributes_seen, 2)
        self.assertEqual(stats.rows_collected, 4)  # 2 points × 2 attrs
        self.assertEqual(len(store.timeseries), 4)
        self.assertIn("backfill:1h", store.cursors)

    def test_backfill_single_attribute(self):
        client = FakeClient()
        store = FakeStore()
        service = CollectorService(client, store)  # type: ignore[arg-type]
        stats = service.backfill("*-1d", "*", interval="1h", attribute_id=SAMPLE_ATTRS[0].attribute_id)
        self.assertEqual(stats.attributes_seen, 1)
        self.assertEqual(stats.rows_collected, 2)


class BackfillSkipDownloadedTest(unittest.TestCase):
    """Watermark-based skip: don't re-download what we already have."""

    def _service(self, store):
        return CollectorService(FakeClient(), store)  # type: ignore[arg-type]

    def test_fresh_attribute_downloads_full_range(self):
        store = FakeStore()
        service = self._service(store)
        stats = service.backfill("*-1d", "*", interval="1h")
        self.assertEqual(stats.attributes_skipped, 0)
        self.assertEqual(stats.requests_made, 2)
        # watermarks recorded per attribute
        self.assertEqual(len(store.progress), 2)
        for (_, iv) in store.progress:
            self.assertEqual(iv, "1h")

    def test_complete_watermark_skips_attribute(self):
        store = FakeStore()
        # watermark past the requested end (+1 interval margin) -> full skip,
        # zero PI requests. Watermark == end would still fetch one boundary
        # point (margin refresh); beyond it there is nothing left to fetch.
        end = datetime(2026, 8, 17, 4, 0, tzinfo=timezone.utc)
        watermark = end + timedelta(hours=2)
        store.progress[(SAMPLE_ATTRS[0].attribute_id, "1h")] = watermark
        store.progress[(SAMPLE_ATTRS[1].attribute_id, "1h")] = watermark
        service = self._service(store)
        stats = service.backfill("2026-08-15T04:00:00Z", "2026-08-17T04:00:00Z", interval="1h")
        self.assertEqual(stats.attributes_skipped, 2)
        self.assertEqual(stats.requests_made, 0)
        self.assertEqual(stats.rows_collected, 0)

    def test_partial_watermark_clamps_start(self):
        store = FakeStore()
        now = datetime.now(timezone.utc)
        # attr0 downloaded up to 30 min ago -> start clamped to watermark-1h
        watermark = now - timedelta(minutes=30)
        store.progress[(SAMPLE_ATTRS[0].attribute_id, "1h")] = watermark
        # attr1 has nothing -> downloads from the full start
        client = FakeClient()
        seen_starts: list[str] = []
        original = client.get_interpolated

        def spy(web_id, *, start_time, end_time, interval, max_count=5000):
            seen_starts.append(start_time)
            return original(web_id, start_time=start_time, end_time=end_time,
                            interval=interval, max_count=max_count)

        client.get_interpolated = spy  # type: ignore
        service = CollectorService(client, store)  # type: ignore[arg-type]
        stats = service.backfill("*-2d", "*", interval="1h")
        self.assertEqual(stats.attributes_skipped, 0)
        self.assertEqual(stats.requests_made, 2)
        # attr0's effective start must be later than the requested start
        requested_start = _iso_like(now - timedelta(days=2))
        self.assertNotEqual(seen_starts[0], requested_start)
        self.assertGreater(seen_starts[0], requested_start)

    def test_no_skip_forces_redownload(self):
        store = FakeStore()
        store.progress[(SAMPLE_ATTRS[0].attribute_id, "1h")] = datetime.now(timezone.utc)
        store.progress[(SAMPLE_ATTRS[1].attribute_id, "1h")] = datetime.now(timezone.utc)
        service = self._service(store)
        stats = service.backfill("*-1d", "*", interval="1h", skip_downloaded=False)
        self.assertEqual(stats.attributes_skipped, 0)
        self.assertEqual(stats.requests_made, 2)

    def test_watermark_not_shared_across_intervals(self):
        store = FakeStore()
        store.progress[(SAMPLE_ATTRS[0].attribute_id, "1h")] = datetime.now(timezone.utc)
        service = self._service(store)
        # 1m backfill must not be blocked by the 1h watermark
        stats = service.backfill("*-1d", "*", interval="1m")
        self.assertEqual(stats.attributes_skipped, 0)
        self.assertEqual(stats.requests_made, 2)


def _iso_like(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class IntervalParserTest(unittest.TestCase):
    def test_units(self):
        from src.services.collector import _interval_to_timedelta
        self.assertEqual(_interval_to_timedelta("30s"), timedelta(seconds=30))
        self.assertEqual(_interval_to_timedelta("5m"), timedelta(minutes=5))
        self.assertEqual(_interval_to_timedelta("1h"), timedelta(hours=1))
        self.assertEqual(_interval_to_timedelta("2d"), timedelta(days=2))
        self.assertEqual(_interval_to_timedelta("1w"), timedelta(weeks=1))
        self.assertIsNone(_interval_to_timedelta("bogus"))


if __name__ == "__main__":
    unittest.main()
