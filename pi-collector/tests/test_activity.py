"""Hermetic tests for the daily collector-uptime aggregation.

'Full green' = collector runs covered all 24 local hours of a day, not a
single short session. See store.accumulate_run_coverage.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from src.repositories.store import ACTIVITY_TZ, accumulate_run_coverage

UTC = timezone.utc


def utc(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


class AccumulateRunCoverageTest(unittest.TestCase):
    def test_single_short_session_covers_one_hour(self):
        # one 8-minute snapshot run -> only 1 hour bucket covered
        runs = [(utc(2026, 8, 17, 2, 2), utc(2026, 8, 17, 2, 10))]
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ)
        # 02:02 UTC = 09:02 WIB same day
        self.assertEqual(days, [
            {"date": "2026-08-17", "runs": 1, "hours_covered": 1},
        ])

    def test_daemon_all_day_is_full_coverage(self):
        # snapshot cycle every 30 min for an entire local day, plus one
        # cycle at 00:30 WIB so the midnight hour is also covered
        runs = [(utc(2026, 8, 16, 17, 30), utc(2026, 8, 16, 17, 38))]  # 00:30 WIB
        start = utc(2026, 8, 16, 18, 0)  # 17 Aug 01:00 WIB
        cursor = start
        while cursor < utc(2026, 8, 17, 16, 30):  # 17 Aug 23:30 WIB
            runs.append((cursor, cursor + timedelta(minutes=8)))
            cursor += timedelta(minutes=30)
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ)
        by_date = {d["date"]: d for d in days}
        self.assertEqual(by_date["2026-08-17"]["hours_covered"], 24)
        self.assertEqual(by_date["2026-08-17"]["runs"], 46)
        # the 00:30 WIB cycle belongs to the 17th local, not the 16th
        self.assertNotIn("2026-08-16", by_date)

    def test_run_spanning_midnight_credits_both_days(self):
        # night run 22:00 WIB -> 02:00 WIB next day (15:00-19:00 UTC)
        runs = [(utc(2026, 8, 17, 15, 0), utc(2026, 8, 17, 19, 0))]
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ)
        by_date = {d["date"]: d for d in days}
        self.assertEqual(by_date["2026-08-17"]["hours_covered"], 2)  # 22:00, 23:00
        self.assertEqual(by_date["2026-08-18"]["hours_covered"], 3)  # 00:00, 01:00, 02:00

    def test_utc_day_boundary_differs_from_local(self):
        # 17 Aug 23:30 WIB = 16:30 UTC same calendar date, but 18 Aug 05:00 WIB
        # local-day bucketing must use Asia/Jakarta, not UTC
        runs = [(utc(2026, 8, 17, 16, 30), utc(2026, 8, 17, 16, 40))]
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ)
        self.assertEqual(days[0]["date"], "2026-08-17")

    def test_unfinished_run_counts_started_hour(self):
        runs = [(utc(2026, 8, 17, 2, 0), None)]
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ)
        self.assertEqual(days[0]["hours_covered"], 1)

    def test_gapped_daemon_counts_distinct_hours(self):
        # daemon ran 2 cycles in the same hour -> still 1 hour covered
        runs = [
            (utc(2026, 8, 17, 2, 0), utc(2026, 8, 17, 2, 8)),
            (utc(2026, 8, 17, 2, 20), utc(2026, 8, 17, 2, 28)),
        ]
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ)
        self.assertEqual(days[0]["runs"], 2)
        self.assertEqual(days[0]["hours_covered"], 1)

    def test_custom_timezone(self):
        # same instant, different bucket in UTC vs Jakarta
        runs = [(utc(2026, 8, 17, 20, 0), utc(2026, 8, 17, 20, 10))]
        days = accumulate_run_coverage(runs, tz=ZoneInfo("UTC"))
        self.assertEqual(days[0]["date"], "2026-08-17")
        jakarta = accumulate_run_coverage(runs, tz=ACTIVITY_TZ)
        self.assertEqual(jakarta[0]["date"], "2026-08-18")  # 03:00 WIB next day


class BackfillDataCoverageTest(unittest.TestCase):
    """Backfilled history must light up past days (data buckets, no runs)."""

    def test_backfill_only_day_counts_data_hours(self):
        # 1h-interval backfill wrote points 10:00..23:00 WIB on Aug 15
        buckets = [datetime(2026, 8, 15, h) for h in range(10, 24)]  # naive local
        days = accumulate_run_coverage([], tz=ACTIVITY_TZ, data_buckets=buckets)
        self.assertEqual(days, [{"date": "2026-08-15", "runs": 0, "hours_covered": 14}])

    def test_backfill_full_day_is_full_green_coverage(self):
        buckets = [datetime(2026, 8, 16, h) for h in range(24)]
        days = accumulate_run_coverage([], tz=ACTIVITY_TZ, data_buckets=buckets)
        self.assertEqual(days[0]["hours_covered"], 24)
        self.assertEqual(days[0]["runs"], 0)

    def test_union_of_run_hours_and_data_hours(self):
        # collector ran 05:00-05:10 WIB; data exists at 06:00 and 07:00
        runs = [(utc(2026, 8, 16, 22, 0), utc(2026, 8, 16, 22, 10))]  # 05:00 WIB
        buckets = [datetime(2026, 8, 17, 6), datetime(2026, 8, 17, 7)]
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ, data_buckets=buckets)
        self.assertEqual(days[0]["hours_covered"], 3)  # hours 5, 6, 7
        self.assertEqual(days[0]["runs"], 1)

    def test_backfill_today_union_with_session(self):
        # today: 8-min session at 09:00 WIB + backfill data 00:00..10:00
        runs = [(utc(2026, 8, 17, 2, 0), utc(2026, 8, 17, 2, 8))]
        buckets = [datetime(2026, 8, 17, h) for h in range(11)]
        days = accumulate_run_coverage(runs, tz=ACTIVITY_TZ, data_buckets=buckets)
        self.assertEqual(days[0]["hours_covered"], 11)  # 0-10 union session hour 9


if __name__ == "__main__":
    unittest.main()
