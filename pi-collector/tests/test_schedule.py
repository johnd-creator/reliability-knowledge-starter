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


if __name__ == "__main__":
    unittest.main()
