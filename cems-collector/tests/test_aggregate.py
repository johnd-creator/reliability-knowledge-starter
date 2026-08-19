"""AggregationService tests with a FakeStore — hermetic, no DB."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.config import CemsConfig
from src.domain.models import AggregatedReading
from src.services.aggregate import AggregationService, floor_to_interval

NOW = datetime(2026, 8, 19, 12, 3, 45, tzinfo=timezone.utc)


class FakeStore:
    def __init__(self, aggregates=None):
        self.aggregates = aggregates or []
        self.upserted = []
        self.cursors: dict[str, datetime | None] = {}
        self.runs = []

    def get_cursor(self, scope):
        return self.cursors.get(scope)

    def set_cursor(self, scope, watermark, rows_seen):
        self.cursors[scope] = watermark

    def window_aggregate(self, window_start, window_end, stack_id=None):
        self.window = (window_start, window_end)
        return self.aggregates

    def upsert_5min(self, aggregates):
        self.upserted.extend(aggregates)
        return len(aggregates)

    def record_run(self, run):
        self.runs.append(run)


def make_service(store):
    config = CemsConfig(aggregation_interval_minutes=5).validate_runtime_safety()
    return AggregationService(store, config)


class TestFloorToInterval(unittest.TestCase):
    def test_floors_to_five_minutes(self):
        self.assertEqual(floor_to_interval(NOW, 5), NOW.replace(hour=12, minute=0, second=0, microsecond=0))

    def test_exact_boundary_stays(self):
        boundary = NOW.replace(hour=12, minute=5, second=0, microsecond=0)
        self.assertEqual(floor_to_interval(boundary, 5), boundary)

    def test_midnight_rollover(self):
        late = NOW.replace(hour=0, minute=2, second=10)
        self.assertEqual(floor_to_interval(late, 5), late.replace(hour=0, minute=0, second=0, microsecond=0))


class TestAggregate(unittest.TestCase):
    def test_aggregates_last_completed_window(self):
        aggregates = [
            AggregatedReading("SO2", "1", NOW.replace(minute=0), 100.0, 50.0, 150.0, 60)
        ]
        store = FakeStore(aggregates)
        stats = make_service(store).aggregate(now=NOW)

        # window = [11:55, 12:00)
        self.assertEqual(
            store.window,
            (
                NOW.replace(hour=11, minute=55, second=0, microsecond=0),
                NOW.replace(hour=12, minute=0, second=0, microsecond=0),
            ),
        )
        self.assertEqual(stats.rows_seen, 1)
        self.assertEqual(stats.upserted, 1)
        self.assertEqual(store.upserted, aggregates)
        self.assertEqual(
            store.cursors["aggregation:5m"],
            NOW.replace(hour=12, minute=0, second=0, microsecond=0),
        )
        self.assertEqual(len(store.runs), 1)
        self.assertEqual(store.runs[0].run_type, "aggregate")

    def test_cursor_prevents_reprocessing(self):
        store = FakeStore([AggregatedReading("SO2", "1", NOW, 1.0, 1.0, 1.0, 1)])
        service = make_service(store)
        service.aggregate(now=NOW)
        first_runs = len(store.runs)
        stats = service.aggregate(now=NOW)
        self.assertEqual(stats.skipped, 1)
        self.assertEqual(stats.upserted, 0)
        self.assertEqual(len(store.runs), first_runs + 1)

    def test_force_reprocesses(self):
        store = FakeStore([AggregatedReading("SO2", "1", NOW, 1.0, 1.0, 1.0, 1)])
        service = make_service(store)
        service.aggregate(now=NOW)
        stats = service.aggregate(now=NOW, force=True)
        self.assertEqual(stats.upserted, 1)

    def test_new_window_after_cursor_advances(self):
        store = FakeStore([])
        service = make_service(store)
        service.aggregate(now=NOW)
        later = NOW + timedelta(minutes=7)
        stats = service.aggregate(now=later)
        self.assertEqual(stats.skipped, 0)

    def test_backfill_iterates_windows(self):
        store = FakeStore([])
        service = make_service(store)
        start = NOW.replace(hour=11, minute=0, second=0, microsecond=0)
        end = NOW.replace(hour=12, minute=0, second=0, microsecond=0)
        results = service.backfill(start, end)
        self.assertEqual(len(results), 12)  # 60 minutes / 5


if __name__ == "__main__":
    unittest.main()
