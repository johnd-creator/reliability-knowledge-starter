"""Unit tests for adapter mappers and OSLC helpers (no network, no DB)."""

from __future__ import annotations

import unittest

from src.adapters.maximo.mappers import (
    equipment_from_payload,
    item_from_payload,
    labor_from_payload,
    person_from_payload,
    service_request_from_payload,
    work_order_from_payload,
)
from src.adapters.maximo.oslc_client import (
    oslc_number,
    oslc_pop_bool,
    oslc_pop_text,
    oslc_timestamp,
)


class OslcHelpersTest(unittest.TestCase):
    def test_boolean_text(self):
        self.assertTrue(oslc_pop_bool({"isrunning": "1"}, "isrunning"))
        self.assertTrue(oslc_pop_bool({"isrunning": "true"}, "isrunning"))
        self.assertFalse(oslc_pop_bool({"isrunning": "0"}, "isrunning"))
        self.assertIsNone(oslc_pop_bool({"isrunning": ""}, "isrunning"))
        self.assertIsNone(oslc_pop_bool({}, "isrunning"))

    def test_number(self):
        self.assertEqual(oslc_number("12.5"), 12.5)
        self.assertEqual(oslc_number(7), 7.0)
        self.assertIsNone(oslc_number("abc"))

    def test_timestamp(self):
        self.assertIsNotNone(oslc_timestamp("2026-08-12T07:00:00Z"))
        self.assertIsNone(oslc_timestamp(""))
        self.assertIsNone(oslc_timestamp(None))

    def test_text_dict_value(self):
        self.assertEqual(oslc_pop_text({"description": {"value": "pump"}}, "description"), "pump")
        self.assertIsNone(oslc_pop_text({"description": None}, "description"))


class MapperTest(unittest.TestCase):
    def test_equipment(self):
        payload = {
            "assetnum": "CS10CVA02GA000-001",
            "description": "Boiler Feed Pump 1A",
            "location": "BRAY-1",
            "siteid": "BSR",
            "orgid": "IP",
            "status": "OPERATING",
            "assettype": "PRODUCTION",
            "plant": "TU",
            "eq11": "CS01",
            "isrunning": "1",
            "children": "0",
            "priority": 0,
            "parent": "CS10CV-001",
            "ancestor": "CS-001",
            "installdate": "2011-08-22T00:00:00+07:00",
            "changedate": "2026-08-12T07:00:00Z",
            "totdowntime": "12.5",
            "issafety": "0",
        }
        eq = equipment_from_payload(payload)
        self.assertEqual(eq.id, "CS10CVA02GA000-001")
        self.assertEqual(eq.status, "OPERATING")
        self.assertEqual(eq.unit, "CS01")
        self.assertTrue(eq.is_running)
        self.assertFalse(eq.has_children)
        self.assertEqual(eq.downtime_total_hours, 12.5)
        self.assertIsNotNone(eq.source_changed_at)
        self.assertEqual(eq.maximo_source.siteid, "BSR")

    def test_work_order(self):
        payload = {
            "wonum": "WO-100",
            "assetnum": "CS10CVA02GA000-001",
            "location": "BRAY-1",
            "status": "COMP",
            "worktype": "CM",
            "reportdate": "2026-01-01T00:00:00+07:00",
            "changedate": "2026-01-03T08:00:00+07:00",
            "downtime": "0",
            "estdur": "8",
            "actlabhrs": "6.5",
            "wopriority": "2",
            "workorderid": 42,
        }
        wo = work_order_from_payload(payload)
        self.assertEqual(wo.id, "WO-100")
        self.assertEqual(wo.work_type, "CM")
        self.assertEqual(wo.estimated_duration_hours, 8.0)
        self.assertEqual(wo.actual_labor_hours, 6.5)
        self.assertEqual(wo.sources["maximo"]["workorderid"], 42)

    def test_service_request(self):
        payload = {
            "ticketid": "SR-1",
            "status": "APPR",
            "assetnum": "CS10CVA02GA000-001",
            "reportedbyname": "Operator A",
            "reportdate": "2026-08-12T07:00:00Z",
            "cxarlingkungan": "Medium",
            "ticketuid": 99,
        }
        sr = service_request_from_payload(payload)
        self.assertEqual(sr.id, "SR-1")
        self.assertEqual(sr.risk_area_environment, "Medium")
        self.assertEqual(sr.sources["maximo"]["ticketuid"], 99)

    def test_person_does_not_store_email(self):
        payload = {"personid": "P01", "displayname": "John Doe", "email_collectionref": "/email/1"}
        person = person_from_payload(payload)
        self.assertEqual(person.id, "P01")
        self.assertFalse(hasattr(person, "email"))
        self.assertFalse(hasattr(person, "phone"))

    def test_item(self):
        payload = {"itemnum": "SP-001", "itemtype": "SPARE", "rotating": "1", "inspectionrequired": "0"}
        item = item_from_payload(payload)
        self.assertEqual(item.id, "SP-001")
        self.assertTrue(item.is_rotating)
        self.assertFalse(item.inspection_required)

    def test_labor(self):
        payload = {"laborcode": "L1", "personid": "P01", "assigned": "1", "reportedhrs": "168"}
        labor = labor_from_payload(payload)
        self.assertEqual(labor.id, "L1")
        self.assertTrue(labor.is_assigned)
        self.assertEqual(labor.reported_hours, 168.0)


if __name__ == "__main__":
    unittest.main()