"""Tests for safety mechanisms: circuit breaker, off-hours gate, chunking."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.config import CollectSafetyConfig
from src.services.collector import (
    CollectorService,
    CollectStats,
    CircuitBreakerError,
    _chunk_time_range,
    _iso,
)


class ChunkTimeRangeTest(unittest.TestCase):
    def test_single_chunk_when_short_range(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        end = datetime(2026, 1, 3, tzinfo=timezone.utc)  # 2 days
        chunks = _chunk_time_range(start, end, chunk_days=7)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], (start, end))

    def test_multiple_chunks(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        end = datetime(2026, 1, 22, tzinfo=timezone.utc)  # 21 days
        chunks = _chunk_time_range(start, end, chunk_days=7)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0][0], start)
        self.assertEqual(chunks[-1][1], end)  # last chunk ends at end

    def test_exact_multiple(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        end = datetime(2026, 1, 15, tzinfo=timezone.utc)  # 14 days
        chunks = _chunk_time_range(start, end, chunk_days=7)
        self.assertEqual(len(chunks), 2)


class OffHoursTest(unittest.TestCase):
    def test_weekend_always_off_hours(self):
        cfg = CollectSafetyConfig(off_hours_weekend=True)
        sunday = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)  # Sunday noon
        self.assertTrue(cfg.is_off_hours(sunday))

    def test_weekday_outside_window(self):
        cfg = CollectSafetyConfig(off_hours_start=22, off_hours_end=6, off_hours_weekend=True)
        wednesday_noon = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        self.assertFalse(cfg.is_off_hours(wednesday_noon))

    def test_weekday_overnight(self):
        cfg = CollectSafetyConfig(off_hours_start=22, off_hours_end=6, off_hours_weekend=True)
        wednesday_night = datetime(2026, 8, 12, 23, 0, tzinfo=timezone.utc)  # 11pm Wed
        self.assertTrue(cfg.is_off_hours(wednesday_night))

    def test_weekday_early_morning(self):
        cfg = CollectSafetyConfig(off_hours_start=22, off_hours_end=6, off_hours_weekend=True)
        thursday_early = datetime(2026, 8, 13, 3, 0, tzinfo=timezone.utc)  # 3am Thu
        self.assertTrue(cfg.is_off_hours(thursday_early))

    def test_weekend_disabled(self):
        cfg = CollectSafetyConfig(off_hours_weekend=False, off_hours_start=22, off_hours_end=6)
        sunday_noon = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
        self.assertFalse(cfg.is_off_hours(sunday_noon))


class CircuitBreakerTest(unittest.TestCase):
    def setUp(self):
        from src.domain.models import AttributeRegistration
        from src.adapters.pi.client import PiClientError

        self.PiClientError = PiClientError
        self.attrs = [
            AttributeRegistration(
                attribute_id="test-attr-1", site="BSR", unit="BSR1",
                equipment="Test", parameter="test",
                business_name="Test Attr", web_id="wid1",
            ),
        ]

    def test_max_requests_trips(self):
        safety = CollectSafetyConfig(max_requests_per_session=2, max_consecutive_errors=100)
        stats = CollectStats(scope="test")
        stats.requests_made = 2
        service = CollectorService(client=None, store=None, safety=safety)  # type: ignore[arg-type]
        self.assertTrue(service._check_circuit_breaker(stats, 0))
        self.assertTrue(stats.aborted)
        self.assertIn("max_requests_per_session", stats.abort_reason)

    def test_consecutive_errors_trip(self):
        safety = CollectSafetyConfig(max_requests_per_session=9999, max_consecutive_errors=5)
        stats = CollectStats(scope="test")
        service = CollectorService(client=None, store=None, safety=safety)  # type: ignore[arg-type]
        self.assertTrue(service._check_circuit_breaker(stats, 5))
        self.assertTrue(stats.aborted)
        self.assertIn("max_consecutive_errors", stats.abort_reason)

    def test_below_thresholds_ok(self):
        safety = CollectSafetyConfig(max_requests_per_session=100, max_consecutive_errors=10)
        stats = CollectStats(scope="test")
        stats.requests_made = 50
        service = CollectorService(client=None, store=None, safety=safety)  # type: ignore[arg-type]
        self.assertFalse(service._check_circuit_breaker(stats, 3))
        self.assertFalse(stats.aborted)


class BackfillRecordedOffHoursTest(unittest.TestCase):
    def test_aborts_outside_off_hours(self):
        from src.domain.models import AttributeRegistration

        safety = CollectSafetyConfig(
            off_hours_start=22, off_hours_end=6, off_hours_weekend=True,
        )
        # Force a weekday noon — outside off-hours
        wednesday_noon = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        self.assertFalse(safety.is_off_hours(wednesday_noon))

        class Store:
            def record_run(self, stats): pass

        service = CollectorService(client=None, store=Store(), safety=safety)  # type: ignore[arg-type]
        stats = service.backfill_recorded(
            start_time="2024-01-01T00:00:00Z",
            end_time="*",
            enforce_off_hours=True,
        )
        self.assertTrue(stats.aborted)
        self.assertIn("outside off-hours", stats.abort_reason)

    def test_force_override_skips_off_hours(self):
        safety = CollectSafetyConfig(max_requests_per_session=9999)

        class FakeStore:
            def list_active_attributes(self): return []
            def set_cursor(self, scope, rows): pass
            def record_run(self, stats): pass
            def get_backfill_progress(self, interval): return {}
            def record_backfill_progress(self, attribute_id, interval, last_timestamp): pass

        service = CollectorService(client=None, store=FakeStore(), safety=safety)  # type: ignore[arg-type]
        stats = service.backfill_recorded(
            start_time="2024-01-01T00:00:00Z",
            end_time="2024-01-02T00:00:00Z",
            enforce_off_hours=False,
            attributes=[],
        )
        self.assertFalse(stats.aborted)


class PiTimeParserTest(unittest.TestCase):
    def test_parse_now(self):
        service = CollectorService(client=None, store=None)  # type: ignore[arg-type]
        result = service._parse_pi_time("*")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result.second, datetime.now(timezone.utc).second, delta=5)

    def test_parse_relative_days(self):
        service = CollectorService(client=None, store=None)  # type: ignore[arg-type]
        result = service._parse_pi_time("*-7d")
        self.assertIsNotNone(result)
        expected = datetime.now(timezone.utc) - timedelta(days=7)
        self.assertAlmostEqual(result.timestamp(), expected.timestamp(), delta=5)

    def test_parse_iso(self):
        service = CollectorService(client=None, store=None)  # type: ignore[arg-type]
        result = service._parse_pi_time("2024-06-15T08:00:00Z")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 15)

    def test_parse_invalid(self):
        service = CollectorService(client=None, store=None)  # type: ignore[arg-type]
        result = service._parse_pi_time("not-a-time")
        self.assertIsNone(result)


class RecordedPaginationTest(unittest.TestCase):
    """Test iter_recorded timestamp-cursor pagination with a fake session."""

    def _make_client(self, handler):
        from src.adapters.pi.client import PiClient
        from src.config import PiApiConfig

        class FakeResponse:
            def __init__(self, payload):
                self.status_code = 200
                self.content = b"x"
                self._payload = payload

            def json(self):
                return self._payload

            def raise_for_status(self):
                pass

        class FakeSession:
            def __init__(self):
                self.calls = []

            def request(self, method, url, **kwargs):
                self.calls.append(kwargs.get("params"))
                return FakeResponse(handler(kwargs.get("params") or {}))

        cfg = PiApiConfig(base_url="https://pi.example/piwebapi", rate_limit_seconds=0)
        client = PiClient(cfg, session=FakeSession())
        return client

    @staticmethod
    def _page(ts_list, has_next_link=False):
        items = [{"Timestamp": t, "Value": 1.0} for t in ts_list]
        payload = {"Items": items}
        if has_next_link:
            payload["Links"] = {
                "Next": "https://pi.example/piwebapi/streams/X/recorded?startTime=next&maxCount=5000"
            }
        return payload

    def test_cursor_pagination_advances(self):
        """Full pages advance the cursor; partial pages stop."""

        def handler(params):
            start = params["startTime"]
            if start == "2026-01-01T00:00:00Z":
                return self._page([f"2026-01-01T00:0{i}:00Z" for i in range(5)])
            elif start == "2026-01-01T00:04:00Z":
                return self._page([f"2026-01-01T00:0{i}:00Z" for i in (4, 5, 6)])
            return {"Items": []}

        client = self._make_client(handler)
        pages_yielded = list(client.iter_recorded(
            "X", start_time="2026-01-01T00:00:00Z", end_time="2026-01-02T00:00:00Z", max_count=5,
        ))
        self.assertEqual(len(pages_yielded), 2)
        self.assertEqual(client._session.calls[1]["startTime"], "2026-01-01T00:04:00Z")

    def test_stops_when_no_progress(self):
        """If the boundary doesn't advance, stop (infinite-loop guard)."""

        def handler(params):
            return self._page([f"2026-01-01T00:0{i}:00Z" for i in range(5)])

        client = self._make_client(handler)
        pages_yielded = list(client.iter_recorded(
            "X", start_time="2026-01-01T00:00:00Z", end_time="2026-01-02T00:00:00Z", max_count=5,
        ))
        self.assertLessEqual(len(pages_yielded), 2)

    def test_partial_first_page_stops(self):
        def handler(params):
            return self._page(["2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"])

        client = self._make_client(handler)
        pages_yielded = list(client.iter_recorded(
            "X", start_time="2026-01-01T00:00:00Z", end_time="2026-01-02T00:00:00Z", max_count=5,
        ))
        self.assertEqual(len(pages_yielded), 1)

    def test_extract_recorded(self):
        from src.adapters.pi.client import extract_recorded
        payload = {"Items": [
            {"Timestamp": "2026-01-01T00:00:00Z", "Value": 77.5, "Good": True},
            {"Timestamp": "2026-01-01T00:01:00Z", "Value": None, "Good": False},
            {"Value": 99.0},  # no timestamp — skipped
        ]}
        points = extract_recorded(payload, "attr-1")
        self.assertEqual(len(points), 2)
        self.assertAlmostEqual(points[0].value, 77.5)
        self.assertIsNone(points[1].value)


class StatsSummaryTest(unittest.TestCase):
    def test_complete_summary(self):
        stats = CollectStats(scope="test", rows_collected=100, requests_made=50, errors=2, attributes_seen=10)
        s = stats.summary()
        self.assertIn("100 rows", s)
        self.assertIn("complete", s)

    def test_aborted_summary(self):
        stats = CollectStats(scope="test", aborted=True, abort_reason="circuit breaker")
        s = stats.summary()
        self.assertIn("ABORTED", s)
        self.assertIn("circuit breaker", s)


if __name__ == "__main__":
    unittest.main()
