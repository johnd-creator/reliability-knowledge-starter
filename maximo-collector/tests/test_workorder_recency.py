"""Cursor loss/regression tests: fakes, no DB or network."""
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace
import unittest

import requests

from src.adapters.maximo.oslc_client import OslcError, OslcPaginationLimitError, OslcRequestBudgetExceeded
from src.services.sync import ObjectSyncConfig, SyncService

CURSOR = datetime(2026, 8, 21, tzinfo=timezone.utc)


def row(name, day=21):
    return dict(wonum=name, changedate=f"2026-08-{day:02d}T00:00:00Z", siteid="BSR", orgid="IP")


class Store:
    def __init__(self, cursor=CURSOR):
        self.cursor = cursor
        self.rows = {}
        self.runs = []
        self.cursor_writes = 0
    def get_cursor(self, scope): return self.cursor
    def set_cursor(self, scope, change, seen):
        self.cursor = change
        self.cursor_writes += 1
    def record_run(self, stats): self.runs.append(stats)
    def is_unchanged(self, kind, identity, column, change):
        return identity in self.rows and self.rows[identity].change == change
    def upsert_for(self, kind, entity):
        outcome = "updated" if entity.id in self.rows else "inserted"
        self.rows[entity.id] = entity
        return outcome


class Client:
    def __init__(self, pages):
        self.pages = pages
        self.request_telemetry = {"business_requests": 0}
        self.calls = []
        self.last_iteration_pages = 0
    @contextmanager
    def bounded_requests(self, limit):
        self.limit = limit
        yield
    def iterate_pages(self, name, **kwargs):
        self.calls.append(kwargs)
        for page in self.pages:
            if self.last_iteration_pages >= kwargs["max_pages"]:
                raise OslcPaginationLimitError(name, pages=self.last_iteration_pages, max_pages=kwargs["max_pages"], next_page_fingerprint="test")
            if self.request_telemetry["business_requests"] >= self.limit:
                raise OslcRequestBudgetExceeded("budget")
            self.last_iteration_pages += 1
            self.request_telemetry["business_requests"] += 1
            if isinstance(page, Exception): raise page
            yield page
    def iterate(self, name, **kwargs):
        # Historical backfill continues through old rows, without recency cutoff.
        self.calls.append(kwargs)
        for page in self.pages:
            yield from page


def mapper(raw):
    return SimpleNamespace(id=raw["wonum"], change=datetime.fromisoformat(raw["changedate"].replace("Z", "+00:00")))

CFG = ObjectSyncConfig("mxwodetail", "work_order", mapper,
    prefix_field="wonum", allowed_prefixes=("BSR",), prefix_query=True,
    watermark_query=False, recent_work_orders=True, cursor_requires_zero_errors=True,
    page_size=25, max_pages=20, request_limit=40)


class RecencyTest(unittest.TestCase):
    def run_sync(self, pages, store=None, config=CFG):
        store = store or Store()
        client = Client(pages)
        stats = SyncService(client, store).sync(config)
        return stats, store, client

    def test_newest_first_and_newer_upsert(self):
        stats, store, client = self.run_sync([[row("BSR1", 22), row("BSR2", 21), row("BSR0", 20)]])
        self.assertEqual(client.calls[0]["order_by"], "-changedate")
        self.assertIn('wonum in ["BSR%"]', client.calls[0]["where"])
        self.assertNotIn(">=", client.calls[0]["where"])
        self.assertEqual(set(store.rows), {"BSR1", "BSR2"})
        self.assertEqual(store.cursor.day, 22)
        self.assertEqual(stats.recency["stop_reason"], "CURSOR_REACHED")

    def test_no_new_cycle_costs_one_page(self):
        stats, store, client = self.run_sync([[row("BSR0", 20)], [row("BSRold", 19)]])
        self.assertEqual(client.request_telemetry["business_requests"], 1)
        self.assertEqual(stats.recency["stop_reason"], "NO_NEW_ROWS")
        self.assertEqual(store.cursor, CURSOR)

    def test_ties_continue_across_pages(self):
        stats, store, client = self.run_sync([[row("BSRa")], [row("BSRb"), row("BSRc")], [row("BSRold", 20)]])
        self.assertEqual(len(store.rows), 3)
        self.assertEqual(stats.recency["pages"], 3)
        self.assertTrue(stats.complete)

    def test_equal_cursor_is_idempotent(self):
        store = Store()
        self.run_sync([[row("BSRa"), row("BSRold", 20)]], store)
        stats, store, _ = self.run_sync([[row("BSRa"), row("BSRold", 20)]], store)
        self.assertEqual(stats.upserted, 0)
        self.assertEqual(stats.unchanged, 1)
        self.assertEqual(len(store.rows), 1)

    def test_out_of_order_after_old_row_cannot_stop_or_write(self):
        stats, store, _ = self.run_sync([[row("BSRold", 20), row("BSRnew", 22)]])
        self.assertFalse(stats.complete)
        self.assertEqual(stats.recency["stop_reason"], "ORDER_VIOLATION")
        self.assertFalse(store.rows)
        self.assertEqual(store.cursor_writes, 0)

    def test_order_checked_across_pages(self):
        stats, store, _ = self.run_sync([[row("BSRa", 22)], [row("BSRb", 23)]])
        self.assertFalse(stats.complete)
        self.assertEqual(store.cursor, CURSOR)

    def test_partial_pagination_retains_cursor_and_progress(self):
        stats, store, _ = self.run_sync([[row("BSRa", 22)], [row("BSRb")]], config=replace(CFG, max_pages=1))
        self.assertEqual(stats.recency["stop_reason"], "PAGE_LIMIT")
        self.assertIn("BSRa", store.rows)
        self.assertEqual(store.cursor_writes, 0)
        stats, store, _ = self.run_sync([[row("BSRa", 22), row("BSRb"), row("BSRold", 20)]], store)
        self.assertEqual(stats.upserted, 1)
        self.assertEqual(store.cursor.day, 22)

    def test_source_failure_preserves_cursor(self):
        stats, store, _ = self.run_sync([[row("BSRa", 22)], requests.ReadTimeout()])
        self.assertEqual(stats.recency["stop_reason"], "SOURCE_ERROR")
        self.assertEqual(store.cursor_writes, 0)

    def test_mapping_error_preserves_cursor(self):
        def bad(raw): raise ValueError("bad")
        stats, store, _ = self.run_sync([[row("BSRa", 22)]], config=replace(CFG, mapper=bad))
        self.assertFalse(stats.complete)
        self.assertEqual(stats.recency["stop_reason"], "MAPPING_OR_STORE_ERROR")
        self.assertEqual(store.cursor_writes, 0)

    def test_prefix_guard_remains_local(self):
        stats, store, _ = self.run_sync([[row("OTHER", 22), row("BSRa"), row("BSRold", 20)]])
        self.assertEqual(set(store.rows), {"BSRa"})
        self.assertEqual(stats.recency["prefix_skipped"], 1)
        self.assertEqual(store.cursor, CURSOR)

    def test_unsupported_order_fails_closed(self):
        stats, store, client = self.run_sync([requests.HTTPError("unsupported")])
        self.assertFalse(stats.complete)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(store.cursor_writes, 0)

    def test_unordered_config_rejected_before_source(self):
        with self.assertRaises(ValueError):
            self.run_sync([], config=replace(CFG, order_by=None))

    def test_historical_backfill_is_independent(self):
        stats, store, client = self.run_sync([[row("BSRa", 22), row("BSRold", 19)]],
            config=replace(CFG, recent_work_orders=False, watermark_field=None, order_by=None))
        self.assertEqual(set(store.rows), {"BSRa", "BSRold"})
        self.assertEqual(store.cursor_writes, 0)
        self.assertNotIn(">=", client.calls[0]["where"])

    def test_missing_cursor_never_seeded_from_partial_batch(self):
        stats, store, _ = self.run_sync([[row("BSRa", 22)], [row("BSRb")]],
            store=Store(None), config=replace(CFG, max_pages=1))
        self.assertFalse(stats.complete)
        self.assertIsNone(store.cursor)
        self.assertEqual(store.cursor_writes, 0)

    def test_request_budget_does_not_move_cursor(self):
        stats, store, _ = self.run_sync([[row("BSRa", 22)], [row("BSRb")]], config=replace(CFG, request_limit=1))
        self.assertEqual(stats.recency["stop_reason"], "REQUEST_BUDGET")
        self.assertEqual(store.cursor_writes, 0)

    def test_missing_timestamp_and_scope_fail_closed(self):
        for mutation in ({"changedate": ""}, {"siteid": "OTHER"}, {"orgid": "OTHER"}):
            with self.subTest(mutation=mutation):
                stats, store, _ = self.run_sync([[{**row("BSRa", 22), **mutation}]])
                self.assertFalse(stats.complete)
                self.assertEqual(store.cursor_writes, 0)

    def test_duplicate_identity_only_latest_version_written(self):
        stats, store, _ = self.run_sync([[row("BSRa", 22), row("BSRa"), row("BSRold", 20)]])
        self.assertEqual(stats.duplicate_ids, 1)
        self.assertEqual(store.rows["BSRa"].change.day, 22)

    def test_complete_small_bootstrap_can_establish_cursor(self):
        stats, store, _ = self.run_sync([[row("BSRa", 22), row("BSRb")]], store=Store(None))
        self.assertTrue(stats.complete)
        self.assertEqual(stats.recency["stop_reason"], "SOURCE_EXHAUSTED")
        self.assertEqual(store.cursor.day, 22)

    def test_store_failure_preserves_cursor(self):
        class BrokenStore(Store):
            def upsert_for(self, *args): raise RuntimeError("store unavailable")
        stats, store, _ = self.run_sync([[row("BSRa", 22)]], store=BrokenStore())
        self.assertFalse(stats.complete)
        self.assertEqual(stats.recency["stop_reason"], "MAPPING_OR_STORE_ERROR")
        self.assertEqual(store.cursor_writes, 0)
