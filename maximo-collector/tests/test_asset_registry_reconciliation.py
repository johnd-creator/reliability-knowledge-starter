"""Synthetic tests for MX-011A; no production report rows are used."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.services.asset_registry_reconciliation import (
    EquipmentSnapshot,
    LocalReconciliationInput,
    MartAssetSnapshot,
    MartMaintenanceSnapshot,
    UnsupportedRegistryFileFormat,
    WorkOrderSnapshot,
    parse_registry_file,
    reconcile_registry,
)


class RegistryParserTest(unittest.TestCase):
    def test_html_export_discovers_header_and_ignores_person_fields(self):
        html = """<html><head><title>List of Assets</title></head><body>
        <table><tr><th>Site</th><th>Asset</th><th>Parent</th><th>Last Wellness</th>
        <th>System Owner</th><th>Insert by</th></tr>
        <tr><td>BSR</td><td>REG-A</td><td>REG-P</td><td>Healthy</td><td>PERSON-SECRET</td><td>USER-SECRET</td></tr>
        <tr><td>BSR</td><td>REG-A</td><td>REG-P</td><td></td><td>PERSON-SECRET</td><td>USER-SECRET</td></tr>
        <tr><td>BSR</td><td></td><td></td><td></td><td>PERSON-SECRET</td><td>USER-SECRET</td></tr>
        </table></body></html>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.xls"
            path.write_text(html, encoding="utf-8")
            snapshot = parse_registry_file(path)

        self.assertEqual(snapshot.sheet, "List of Assets")
        self.assertEqual(snapshot.rows, 3)
        self.assertEqual(sum(1 for row in snapshot.records if row.asset), 2)
        self.assertEqual(snapshot.field_present["last_wellness"], 1)
        self.assertNotIn("PERSON-SECRET", str(snapshot))
        self.assertNotIn("USER-SECRET", str(snapshot))

    def test_binary_xls_is_rejected_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "binary.xls"
            path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"unsupported")
            with self.assertRaisesRegex(UnsupportedRegistryFileFormat, "UNSUPPORTED_REGISTRY_FILE_FORMAT"):
                parse_registry_file(path)


class ReconciliationTest(unittest.TestCase):
    def setUp(self):
        html = """<html><head><title>List of Assets</title></head><body><table>
        <tr><th>Site</th><th>Asset</th><th>Parent</th><th>Maintenance Strategi</th></tr>
        <tr><td>BSR</td><td>REG-A</td><td>REG-P</td><td>PM</td></tr>
        <tr><td>BSR</td><td>REG-A</td><td>REG-P</td><td></td></tr>
        <tr><td>BSR</td><td>REG-B</td><td></td><td>CM</td></tr>
        </table></body></html>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.xls"
            path.write_text(html, encoding="utf-8")
            self.registry = parse_registry_file(path)

        self.equipment = (
            EquipmentSnapshot("REG-A", status="OPERATING", equipment_class="PUMP", unit="U1", parent_id="REG-P"),
            EquipmentSnapshot("REG-P", status="OPERATING", equipment_class="SYSTEM", unit="U1"),
            EquipmentSnapshot("REG-B", status="OPERATING", equipment_class="PUMP", unit="U1"),
            EquipmentSnapshot("CHILD-1", status="OPERATING", equipment_class="PART", unit="U1", parent_id="REG-A"),
            EquipmentSnapshot("BROKEN", status="OPERATING", equipment_class="PART", unit="U1", parent_id="UNKNOWN"),
            EquipmentSnapshot("CYCLE-A", status="OPERATING", equipment_class="PART", unit="U1", parent_id="CYCLE-B"),
            EquipmentSnapshot("CYCLE-B", status="OPERATING", equipment_class="PART", unit="U1", parent_id="CYCLE-A"),
        )
        changed = datetime(2026, 8, 20, tzinfo=timezone.utc)
        self.local = LocalReconciliationInput(
            equipment=self.equipment,
            work_orders=(
                WorkOrderSnapshot("REG-A", changed),
                WorkOrderSnapshot("CHILD-1", changed),
                WorkOrderSnapshot("BROKEN", changed),
                WorkOrderSnapshot("MISSING", changed),
                WorkOrderSnapshot(None, None),
            ),
            mart_assets=(
                MartAssetSnapshot("asset:MAXIMO:MXASSET:BSR:IP:REG-A", "REG-A"),
                MartAssetSnapshot("asset:MAXIMO:MXASSET:BSR:IP:NOT-REG", "NOT-REG"),
            ),
            mart_maintenance=(
                MartMaintenanceSnapshot("asset:MAXIMO:MXASSET:BSR:IP:REG-A"),
                MartMaintenanceSnapshot("CHILD-1"),
            ),
        )

    def test_matching_hierarchy_and_work_order_relationships(self):
        report = reconcile_registry(self.registry, self.local)
        self.assertEqual(report["registry_reconciliation"]["exact_equipment_matches"], 2)
        self.assertEqual(report["registry_file"]["duplicate_asset_values"], 1)
        self.assertEqual(report["hierarchy"]["direct_registry_parent"], 1)
        self.assertEqual(report["hierarchy"]["registry_ancestor_found"], 1)
        self.assertEqual(report["hierarchy"]["broken_parent_reference"], 1)
        self.assertEqual(report["hierarchy"]["cycle_encountered"], 2)
        relationships = report["work_order_relationships"]["all"]
        self.assertEqual(relationships["direct_registry_asset"], 1)
        self.assertEqual(relationships["non_registry_with_registry_ancestor"], 1)
        self.assertEqual(relationships["equipment_with_no_registry_ancestor"], 1)
        self.assertEqual(relationships["equipment_target_missing_from_collector"], 1)
        self.assertEqual(relationships["without_equipment"], 1)

    def test_mart_and_business_fields_are_aggregate_only(self):
        report = reconcile_registry(self.registry, self.local)
        mart = report["current_mart"]
        self.assertEqual(mart["asset_master_total"], 2)
        self.assertEqual(mart["asset_master_matching_registry"], 1)
        self.assertEqual(mart["maintenance_references_unresolved"], 1)
        self.assertEqual(mart["unresolved_references_with_registry_ancestor"], 1)
        self.assertEqual(report["business_report_field_coverage"]["maintenance_strategy"]["count"], 2)
        rendered = str(report)
        self.assertNotIn("REG-A", rendered)
        self.assertNotIn("CHILD-1", rendered)
        self.assertNotIn("MISSING", rendered)


if __name__ == "__main__":
    unittest.main()
