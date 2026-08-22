"""Hermetic Work Orders API pagination tests (no network or Postgres)."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.api.app import WorkOrderPage, create_app
from src.config import DbtConfig
from src.domain.work_order import WorkOrder
from src.repositories.database import Database
from src.repositories.store import CockpitStore


class FakeStore:
    def __init__(self):
        self.rows = [
            WorkOrder(id=f"BSR-{index:03d}", equipment_id="EQ-1" if index < 3 else "EQ-2")
            for index in range(5)
        ]

    def count_work_orders(self, equipment_id=None, status=None):
        return sum(
            1 for row in self.rows
            if (not equipment_id or row.equipment_id == equipment_id)
            and (not status or row.status == status)
        )

    def list_work_orders(self, equipment_id=None, offset=0, limit=50, status=None):
        rows = [
            row for row in self.rows
            if (not equipment_id or row.equipment_id == equipment_id)
            and (not status or row.status == status)
        ]
        return rows[offset:offset + limit]

    def list_work_order_statuses(self):
        return sorted({row.status for row in self.rows if row.status})


def work_order_endpoint():
    return next(route.endpoint for route in create_app().routes if route.path == "/work-orders")


class WorkOrderApiPaginationTest(unittest.TestCase):
    def test_first_middle_last_and_empty_pages(self):
        endpoint = work_order_endpoint()
        store = FakeStore()

        first = endpoint(None, 0, 2, store)
        middle = endpoint(None, 2, 2, store)
        last = endpoint(None, 4, 2, store)
        empty = endpoint(None, 6, 2, store)

        self.assertIsInstance(first, WorkOrderPage)
        self.assertEqual((first.total, first.offset, first.limit), (5, 0, 2))
        self.assertTrue(first.has_more)
        self.assertEqual(len(first.items), 2)
        self.assertEqual(len(middle.items), 2)
        self.assertFalse(last.has_more)
        self.assertEqual(len(last.items), 1)
        self.assertEqual(empty.items, [])
        self.assertEqual(empty.total, 5)

    def test_equipment_filter_uses_same_total_and_items_filter(self):
        page = work_order_endpoint()("EQ-1", 0, 50, FakeStore())
        self.assertEqual(page.total, 3)
        self.assertEqual(len(page.items), 3)
        self.assertTrue(all(item.equipment_id == "EQ-1" for item in page.items))

    def test_default_includes_all_statuses_and_explicit_filter_is_local(self):
        store = FakeStore()
        store.rows[0].status = "CLOSE"
        store.rows[1].status = "CAN"
        all_page = work_order_endpoint()(None, 0, 50, store)
        close_page = work_order_endpoint()(None, 0, 50, store, "CLOSE")
        self.assertEqual(all_page.total, 5)
        self.assertEqual(close_page.total, 1)
        self.assertEqual(close_page.items[0].status, "CLOSE")

    def test_route_declares_safe_default_and_maximum_limit(self):
        route = next(route for route in create_app().routes if route.path == "/work-orders")
        limit = next(param for param in route.dependant.query_params if param.name == "limit")
        metadata = {type(item).__name__: item for item in limit.field_info.metadata}
        self.assertEqual(limit.field_info.default, 50)
        self.assertEqual(metadata["Le"].le, 200)


class WorkOrderStorePaginationTest(unittest.TestCase):
    def test_count_filter_and_stable_reported_order(self):
        db = Database(DbtConfig(dsn="sqlite:///:memory:"))
        db.create_all()
        store = CockpitStore(db)
        same_time = datetime(2026, 8, 20, tzinfo=timezone.utc)
        store.upsert_work_order(WorkOrder(id="BSR-2", equipment_id="EQ-1", reported_at=same_time))
        store.upsert_work_order(WorkOrder(id="BSR-1", equipment_id="EQ-1", reported_at=same_time))
        store.upsert_work_order(WorkOrder(id="BSR-3", equipment_id="EQ-2", status="CLOSE", reported_at=None))

        self.assertEqual(store.count_work_orders(), 3)
        self.assertEqual(store.count_work_orders("EQ-1"), 2)
        page = store.list_work_orders(offset=0, limit=2)
        self.assertEqual([item.id for item in page], ["BSR-1", "BSR-2"])
        self.assertEqual([item.id for item in store.list_work_orders(offset=2, limit=2)], ["BSR-3"])
        self.assertEqual(store.count_work_orders(status="CLOSE"), 1)
        self.assertEqual([item.id for item in store.list_work_orders(status="CLOSE")], ["BSR-3"])


if __name__ == "__main__":
    unittest.main()
