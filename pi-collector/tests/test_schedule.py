"""Hermetic tests for the /schedule countdown computation."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.services.schedule import (
    STATE_IDLE,
    STATE_RUNNING,
    STATE_SCHEDULED,
    compute_schedule,
)

UTC = timezone.utc
NOW = datetime(2026, 8, 18, 3, 0, 0, tzinfo=UTC)


class ScheduleStateTest(unittest.TestCase):
    def test_running_when_snapshot_writes_are_fresh(self):
        info = compute_schedule(
            NOW - timedelta(minutes=3), NOW,
            interval_seconds=300,
            latest_activity_at=NOW - timedelta(seconds=30),
        )
        self.assertEqual(info.state, STATE_RUNNING)
        self.assertTrue(info.active)
        self.assertIsNone(info.next_run_at)  # countdown suspended while running

    def test_not_running_when_activity_is_stale(self):
        info = compute_schedule(
            NOW - timedelta(minutes=3), NOW,
            interval_seconds=300,
            latest_activity_at=NOW - timedelta(seconds=200),
        )
        self.assertNotEqual(info.state, STATE_RUNNING)

    def test_scheduled_next_run_is_last_plus_interval(self):
        last = NOW - timedelta(minutes=2)
        info = compute_schedule(last, NOW, interval_seconds=300)
        self.assertEqual(info.state, STATE_SCHEDULED)
        self.assertEqual(info.next_run_at, last + timedelta(seconds=300))
        self.assertTrue(info.active)

    def test_idle_without_history(self):
        info = compute_schedule(None, NOW, interval_seconds=300)
        self.assertEqual(info.state, STATE_IDLE)
        self.assertFalse(info.active)
        self.assertIsNone(info.next_run_at)

    def test_no_flap_when_cycle_duration_exceeds_interval(self):
        # real case: cycle takes 433s > 300s interval; daemon period ~733s.
        # 10 minutes after the last cycle END must still be "scheduled",
        # not idle (the old 2x-interval threshold flapped here).
        info = compute_schedule(
            NOW - timedelta(minutes=10), NOW,
            interval_seconds=300,
            last_cycle_duration_seconds=433,
        )
        self.assertEqual(info.state, STATE_SCHEDULED)

    def test_idle_past_deadline_with_duration(self):
        # deadline = 300 + 433 + 120 = 853s after last run
        info = compute_schedule(
            NOW - timedelta(minutes=15), NOW,
            interval_seconds=300,
            last_cycle_duration_seconds=433,
        )
        self.assertEqual(info.state, STATE_IDLE)
        self.assertFalse(info.active)

    def test_idle_without_duration_assumes_two_intervals(self):
        info = compute_schedule(
            NOW - timedelta(minutes=13), NOW, interval_seconds=300
        )
        self.assertEqual(info.state, STATE_IDLE)

    def test_next_run_in_past_but_within_deadline_stays_scheduled(self):
        # between "sleep ended" and "first snapshot write" the countdown is
        # at zero but the collector is not idle yet
        info = compute_schedule(
            NOW - timedelta(minutes=6), NOW,
            interval_seconds=300,
            last_cycle_duration_seconds=433,
        )
        self.assertEqual(info.state, STATE_SCHEDULED)
        self.assertLess(info.next_run_at, NOW)  # countdown clamps to 0 in UI

    def test_naive_datetimes_treated_as_utc(self):
        info = compute_schedule(None, datetime(2026, 8, 18, 3, 0, 0), 300)
        self.assertEqual(info.state, STATE_IDLE)

    def test_nonpositive_interval_falls_back(self):
        info = compute_schedule(None, NOW, interval_seconds=0)
        self.assertEqual(info.interval_seconds, 300)

    def test_countdown_uses_completion_not_cycle_start(self):
        completed=NOW-timedelta(seconds=100)
        info=compute_schedule(completed,NOW,interval_seconds=300,last_cycle_duration_seconds=508.142)
        self.assertEqual(info.next_run_at, completed+timedelta(seconds=300))
        self.assertEqual(info.last_cycle_duration_seconds+info.interval_seconds,808.142)

    def test_recent_finished_cycle_does_not_claim_still_running(self):
        info=compute_schedule(NOW-timedelta(seconds=10),NOW,interval_seconds=300,
                              latest_activity_at=NOW-timedelta(seconds=11),last_cycle_duration_seconds=508)
        self.assertEqual(info.state,STATE_SCHEDULED)
        self.assertEqual(info.next_run_at,NOW+timedelta(seconds=290))

    def test_future_write_is_not_activity_evidence(self):
        info=compute_schedule(None,NOW,latest_activity_at=NOW+timedelta(seconds=1))
        self.assertEqual(info.state,STATE_IDLE)


class ScheduleApiSemanticsTests(unittest.TestCase):
    def test_additive_duration_pause_and_completion_metadata(self):
        import asyncio
        from unittest.mock import patch
        from src.api.app import create_app,_store
        from test_signal_persistence_api import request
        completed=datetime.now(UTC)-timedelta(seconds=10)
        class Store:
            def last_snapshot_cycle(self):return completed,508.142
            def latest_snapshot_activity(self):return completed-timedelta(seconds=1)
        app=create_app();app.dependency_overrides[_store]=lambda:Store()
        with patch.dict('os.environ',{'PI_SNAPSHOT_INTERVAL_SECONDS':'300'},clear=True):
            status,body=asyncio.run(request(app,'/schedule'))
        self.assertEqual(status,200)
        self.assertEqual(body['interval_seconds'],300)
        self.assertEqual(body['pause_seconds'],300)
        self.assertAlmostEqual(body['effective_start_to_start_seconds'],808.142)
        self.assertEqual(body['last_cycle_duration_seconds'],508.142)
        self.assertEqual(datetime.fromisoformat(body['next_run_at']),completed+timedelta(seconds=300))
        self.assertEqual(body['state'],'scheduled')

    def test_no_duration_does_not_invent_effective_cadence(self):
        import asyncio
        from src.api.app import create_app,_store
        from test_signal_persistence_api import request
        class Store:
            def last_snapshot_cycle(self):return None,None
            def latest_snapshot_activity(self):return None
        app=create_app();app.dependency_overrides[_store]=lambda:Store()
        status,body=asyncio.run(request(app,'/schedule'))
        self.assertEqual(status,200)
        self.assertIsNone(body['effective_start_to_start_seconds'])
        self.assertIsNone(body['next_run_at'])


if __name__ == "__main__":
    unittest.main()
