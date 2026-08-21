"""Hermetic tests for the explicit MX-011R bounded loader."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.adapters.maximo.canonical_mappers import (
    asset_health_assessment_from_payload,
    asset_master_from_payload,
    fmea_assessment_from_payload,
    maintenance_event_from_payload,
    overhaul_event_from_payload,
    rcfa_analysis_from_payload,
)
from src.config import DbConfig, MaximoConfig
from src.repositories.database import Database
from src.repositories.store import CollectorStore
from src.services.canonical import CanonicalCollection, CanonicalStats
from src.services.controlled_mart_load import (
    INITIAL_CONTROLLED_PROFILE,
    ControlledMartLoader,
)
from src.services.mart import MartWriter
from tests.fixtures.canonical_payloads import ASSET, BHM, FMEA, OVERHAUL, RCFA, WORK_ORDER


class FakeStore:
    def __init__(self):
        self.runs = []
        self.cursor_calls = []

    def count(self, *_args, **_kwargs):
        return 0

    def record_run(self, run):
        self.runs.append(run)

    def set_cursor(self, *args):
        self.cursor_calls.append(args)
        raise AssertionError("controlled Mart load must not update SyncCursor")


class FakeWriter:
    def __init__(self):
        self.calls = []
        self._db = None

    def persist_collection(self, collection, *, dry_run=False):
        self.calls.append((collection.canonical_entity, dry_run))
        return SimpleNamespace(
            records_inserted=0 if dry_run else len(collection.records),
            records_updated=0,
            records_unchanged=0,
            records_rejected=0,
        )


class FakeCollector:
    def __init__(self):
        asset = asset_master_from_payload(ASSET)
        workorder = maintenance_event_from_payload(WORK_ORDER)
        self.records = {
            "mxasset": asset,
            "mxwodetail": workorder,
            "ipfmea": fmea_assessment_from_payload(FMEA),
            "ipbhm": asset_health_assessment_from_payload(BHM),
            "iprcfa": rcfa_analysis_from_payload(RCFA),
            "ip_dom_oh": overhaul_event_from_payload(OVERHAUL, workorder_index={WORK_ORDER["wonum"]: workorder}),
        }
        self.entities = {
            "mxasset": "asset_master",
            "mxwodetail": "maintenance_event",
            "ipfmea": "fmea_assessment",
            "ipbhm": "asset_health_assessment",
            "iprcfa": "rcfa_analysis",
            "ip_dom_oh": "overhaul_event",
        }
        self.calls = []
        self.collect_all_called = False

    def _one(self, source, **kwargs):
        self.calls.append((source, kwargs))
        return CanonicalCollection(
            self.entities[source],
            records=[self.records[source]],
            stats=CanonicalStats(source_records_read=1, canonical_records_emitted=1),
            completeness="EXHAUSTED",
            pages=1,
        )

    def collect_assets(self, **kwargs): return self._one("mxasset", **kwargs)
    def collect_workorders(self, **kwargs): return self._one("mxwodetail", **kwargs)
    def collect_fmea(self, **kwargs): return self._one("ipfmea", **kwargs)
    def collect_bhm(self, **kwargs): return self._one("ipbhm", **kwargs)
    def collect_rcfa(self, **kwargs): return self._one("iprcfa", **kwargs)

    def collect_overhauls(self, workorder_records, **kwargs):
        self.calls.append(("ip_dom_oh", {**kwargs, "workorder_records": workorder_records}))
        return self._one("ip_dom_oh", **kwargs)

    def collect_all(self):
        self.collect_all_called = True
        raise AssertionError("MX-011R must not use collect_all")


class ControlledMartLoadTest(unittest.TestCase):
    def test_duplicate_canonical_ids_are_removed_before_mart_writer(self):
        collector = FakeCollector()
        collection = CanonicalCollection(
            "maintenance_event",
            records=[collector.records["mxwodetail"], collector.records["mxwodetail"]],
            stats=CanonicalStats(source_records_read=2, canonical_records_emitted=2),
            completeness="CAPPED",
        )
        duplicates = ControlledMartLoader._deduplicate_collection(collection)
        self.assertEqual(duplicates, 1)
        self.assertEqual(len(collection.records), 1)
        self.assertEqual(collection.stats.canonical_records_emitted, 1)
        self.assertEqual(collection.stats.records_skipped, 1)

    def test_profile_is_finite_and_derives_safe_page_budgets(self):
        config = MaximoConfig(rate_limit_seconds=0)
        self.assertEqual(INITIAL_CONTROLLED_PROFILE.max_pages_for("mxasset", config), 3)
        self.assertEqual(INITIAL_CONTROLLED_PROFILE.max_pages_for("mxwodetail", config), 20)
        for source in ("ipfmea", "ipbhm", "iprcfa", "ip_dom_oh"):
            self.assertEqual(INITIAL_CONTROLLED_PROFILE.max_pages_for(source, config), 1)

    def test_dry_run_uses_three_records_one_page_and_bounded_workorder_index(self):
        collector = FakeCollector()
        writer = FakeWriter()
        store = FakeStore()
        result = ControlledMartLoader(
            collector, writer, store, MaximoConfig(rate_limit_seconds=0)
        ).run(dry_run=True)

        self.assertEqual(len(result.reports), 6)
        self.assertFalse(result.stopped)
        self.assertFalse(collector.collect_all_called)
        self.assertEqual(len(writer.calls), 6)
        self.assertTrue(all(dry_run for _, dry_run in writer.calls))
        self.assertTrue(all(report.source_ceiling == 3 for report in result.reports))
        self.assertTrue(all(report.page_ceiling == 1 for report in result.reports))
        overhaul_call = next(kwargs for source, kwargs in collector.calls if source == "ip_dom_oh")
        self.assertEqual(len(overhaul_call["workorder_records"]), 1)
        self.assertEqual(store.cursor_calls, [])

    def test_actual_rerun_is_idempotent_and_does_not_update_cursor(self):
        db = Database(DbConfig("sqlite+pysqlite:///:memory:"))
        db.create_all()
        try:
            collector = FakeCollector()
            writer = MartWriter(db)
            store = CollectorStore(db)
            loader = ControlledMartLoader(
                collector, writer, store, MaximoConfig(rate_limit_seconds=0)
            )
            first = loader.run(source="ipfmea")
            second = loader.run(source="ipfmea")
            self.assertEqual(first.reports[0].inserted, 1)
            self.assertEqual(second.reports[0].unchanged, 1)
            self.assertEqual(store.get_cursor("IPFMEA"), None)
            self.assertEqual(store.list_runs(1)[0].mode, "mart-initial")
        finally:
            db.engine.dispose()


if __name__ == "__main__":
    unittest.main()
