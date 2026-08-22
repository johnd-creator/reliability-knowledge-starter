"""Hermetic tests for bounded, privacy-safe Work Order profiling."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.services.workorder_profile import (
    RECENT_ORDER,
    WorkOrderPopulationProfiler,
    classify_can_dominance,
    summarize_rows,
)


def row(
    wonum: str,
    *,
    status: str = "CAN",
    worktype: str = "PM",
    changedate: str = "2026-08-20T00:00:00Z",
    assetnum: str | None = "ASSET-1",
    orgid: str = "IP",
    siteid: str = "BSR",
) -> dict[str, object]:
    return {
        "wonum": wonum,
        "assetnum": assetnum,
        "siteid": siteid,
        "orgid": orgid,
        "status": status,
        "worktype": worktype,
        "changedate": changedate,
        "reportdate": None,
        "actstart": None,
        "actfinish": None,
        "downtime": "0",
        "actlabhrs": "0",
    }


class ProfileAggregationTest(unittest.TestCase):
    def test_status_worktype_dates_and_presence_are_aggregated(self):
        rows = [
            row("BSR-1", status="CAN", worktype="PM", changedate="2026-08-01T00:00:00Z"),
            row("BSR-2", status="APPR", worktype="CM", changedate="2026-08-02T00:00:00Z", assetnum=None),
            row("OTHER-1", status="CAN", worktype="PM", changedate="2026-08-03T00:00:00Z"),
        ]
        profile = summarize_rows(rows, order_by=None, source_cap=3, page_size=25)
        self.assertEqual(profile.source_rows_read, 3)
        self.assertEqual(profile.prefix_matched, 2)
        self.assertEqual(profile.prefix_skipped, 1)
        self.assertEqual(profile.status_before_prefix["CAN"]["count"], 2)
        self.assertEqual(profile.status_distribution["CAN"]["count"], 1)
        self.assertEqual(profile.work_type_distribution["CM"]["count"], 1)
        self.assertEqual(profile.changedate.minimum, "2026-08-01T00:00:00+00:00")
        self.assertEqual(profile.changedate.maximum, "2026-08-02T00:00:00+00:00")
        self.assertEqual(profile.asset_present, 1)
        self.assertEqual(profile.canonical_eligible, 1)
        self.assertEqual(profile.eligibility_exclusions["missing_assetnum"], 1)

    def test_report_does_not_expose_row_values(self):
        profile = summarize_rows(
            [row("TEST-WO-001", assetnum="TEST-ASSET-001")],
            order_by=None,
            source_cap=1,
            page_size=25,
        )
        rendered = str(profile.as_dict())
        self.assertNotIn("TEST-WO-001", rendered)
        self.assertNotIn("TEST-ASSET-001", rendered)

    def test_ordering_and_duplicate_observability_is_aggregate_only(self):
        rows = [
            row("BSR-1", changedate="2026-08-03T00:00:00Z"),
            row("BSR-1", changedate="2026-08-03T00:00:00Z"),
            row("BSR-2", changedate="2026-08-04T00:00:00Z"),
            row("BSR-3", changedate="not-a-date"),
        ]
        profile = summarize_rows(rows, order_by="-changedate", source_cap=4, page_size=25)
        self.assertEqual(profile.changedate_order_violations, 1)
        self.assertEqual(profile.missing_changedate, 1)
        self.assertEqual(profile.duplicate_source_identities, 1)
        self.assertEqual(profile.changedate_ties, 1)
        self.assertNotIn("BSR-1", str(profile.as_dict()))


class ClassificationTest(unittest.TestCase):
    def test_default_order_bias(self):
        default = summarize_rows([row(f"BSR-{i}") for i in range(90)] + [row(f"BSR-X{i}", status="APPR") for i in range(10)], order_by=None, source_cap=100, page_size=25)
        recent = summarize_rows([row(f"BSR-R{i}", status="CAN") for i in range(15)] + [row(f"BSR-Y{i}", status="APPR") for i in range(85)], order_by=RECENT_ORDER, source_cap=100, page_size=25)
        self.assertIn("DEFAULT_ORDER_SAMPLING_BIAS", classify_can_dominance(default, recent))

    def test_source_population_dominated(self):
        default = summarize_rows([row(f"BSR-{i}") for i in range(82)] + [row(f"BSR-X{i}", status="APPR") for i in range(18)], order_by=None, source_cap=100, page_size=25)
        recent = summarize_rows([row(f"BSR-R{i}") for i in range(79)] + [row(f"BSR-Y{i}", status="APPR") for i in range(21)], order_by=RECENT_ORDER, source_cap=100, page_size=25)
        self.assertIn("SOURCE_POPULATION_DOMINATED", classify_can_dominance(default, recent))


class ProbeTest(unittest.TestCase):
    def test_profile_records_pages_after_bounded_iterator_is_consumed(self):
        class FakeClient:
            last_iteration_pages = 0

            def iterate(self, *_args, **_kwargs):
                self.last_iteration_pages = 2
                yield row("BSR-1")

        profile = WorkOrderPopulationProfiler(FakeClient(), source_cap=25, page_size=25, max_pages=1).profile_source(None)
        self.assertEqual(profile.pages, 2)

    def test_probe_forwards_recent_order_once(self):
        calls = []

        class FakeClient:
            last_iteration_pages = 0

            def iterate(self, object_structure, **kwargs):
                calls.append((object_structure, kwargs))
                self.last_iteration_pages = 1
                yield row("BSR-1")

        result = WorkOrderPopulationProfiler(FakeClient(), source_cap=25, page_size=25, max_pages=1).probe_recent_order()
        self.assertTrue(result.supported)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]["order_by"], "-changedate")
        self.assertEqual(calls[0][1]["max_pages"], 1)

    def test_http_400_marks_recent_order_unsupported_without_retry(self):
        calls = []

        class FakeClient:
            last_iteration_pages = 1

            def iterate(self, *_args, **_kwargs):
                calls.append(1)
                error = RuntimeError("unsupported")
                error.response = SimpleNamespace(status_code=400)
                raise error
                yield  # pragma: no cover

        result = WorkOrderPopulationProfiler(FakeClient(), source_cap=25, page_size=25, max_pages=1).probe_recent_order()
        self.assertFalse(result.supported)
        self.assertEqual(result.http_status, 400)
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
