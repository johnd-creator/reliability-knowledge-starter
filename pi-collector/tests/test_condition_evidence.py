"""Collector-owned explicit selection and guarded handoff regression."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import Mock
from src.cli import parse_args, cmd_condition_evidence
from src.services.condition_evidence import collect_condition_evidence

spec = importlib.util.spec_from_file_location("condition_fixture", Path(__file__).parent / "fixtures" / "condition_source.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

def plan():
    return {"contract_version": "1.0", "canonical_asset_id": "SYNTHETIC-ASSET", "mapping_id": "SYNTHETIC-MAPPING",
        "sources": {"pi": {"pi_source_id": "CENTRAL_PI", "af_server_ref": "SYNTHETIC-SERVER", "af_database_ref": "SYNTHETIC-DB",
            "af_element_ref": "SYNTHETIC-ELEMENT", "mapping_role": "PRIMARY_EQUIPMENT", "mapping_status": "VERIFIED"}},
        "signals": [{"signal_id": "SYNTHETIC-SIGNAL", "mapping_id": "SYNTHETIC-MAPPING", "sources": {"pi": {"attribute_ref": "SYNTHETIC-ATTRIBUTE"}},
            "semantic_name": "motor_current", "approval_status": "APPROVED", "approved_by": "fixture-reviewer",
            "approved_at": fixture.NOW.isoformat(), "evidence_ref": "synthetic-only"}]}

class ConditionSourceTest(unittest.TestCase):
    def test_actual_governed_client_lineage_and_only_selected_value(self):
        batch, calls = fixture.fixture_batch(plan())
        e = batch["results"][0]["evidence"]
        self.assertEqual(e["value"], 12.5)
        self.assertEqual(e["value_type"], "NUMERIC")
        self.assertEqual(e["sources"]["pi"]["attribute_ref"], "SYNTHETIC-ATTRIBUTE")
        self.assertEqual(len(calls), 5)
        self.assertTrue(all(c[0] == "GET" for c in calls))
        self.assertFalse(any("UNSELECTED_SYNTHETIC/value" in c[1] for c in calls))
        self.assertEqual(calls[2][2]["maxCount"], "100")

    def test_reject_mapping_states_before_source(self):
        for status in ("PROPOSED", "AMBIGUOUS", "RETIRED", "UNMAPPED"):
            p = plan(); p["sources"]["pi"]["mapping_status"] = status
            boundary = Mock()
            with self.assertRaises(ValueError):
                collect_condition_evidence(boundary, p)
            boundary.get_evidence_snapshot.assert_not_called()

    def test_wrong_source_role_and_unapproved_selection_no_source(self):
        for location, key, value in (("pi", "pi_source_id", "OTHER"), ("pi", "mapping_role", "SECONDARY"),
                                    ("signal", "approval_status", "RETIRED"), ("signal", "mapping_id", "OTHER"),
                                    ("signal", "approved_by", " ")):
            p = plan(); row = p["sources"]["pi"] if location == "pi" else p["signals"][0]; row[key] = value
            boundary = Mock()
            with self.assertRaises(ValueError): collect_condition_evidence(boundary, p)
            boundary.get_evidence_snapshot.assert_not_called()

    def test_empty_duplicate_and_433_signals_rejected_before_source(self):
        for count in (0, 2, 433):
            p = plan(); p["signals"] *= count
            boundary = Mock()
            with self.assertRaises(ValueError): collect_condition_evidence(boundary, p)
            boundary.get_evidence_snapshot.assert_not_called()

    def test_value_types_units_quality_and_epoch_preserved(self):
        variants = [{"Value": "RUNNING"}, {"Value": {"Name": "RUN", "Value": 1, "IsSystem": False}},
                    {"Value": None}, {"Value": True}, {"Good": False, "Questionable": True, "Substituted": True, "Annotated": True}]
        for variant in variants:
            variant.update({"Timestamp": "1970-01-01T00:00:00Z", "UnitsAbbreviation": "degC"})
            batch, _ = fixture.fixture_batch(plan(), {"motor_current": variant})
            e = batch["results"][0]["evidence"]
            expected = variant.get("Value", 12.5)
            if isinstance(expected, dict):
                expected = {"name": expected.get("Name"), "code": expected.get("Value"), "is_system": expected.get("IsSystem")}
            self.assertEqual(e["value"], expected)
            self.assertEqual(e["unit"], "degC")
            self.assertTrue(e["source_timestamp"].startswith("1970-01-01"))
            if variant.get("Good") is False: self.assertEqual(e["evidence_status"], "BAD_QUALITY")

    def test_unavailable_is_safe_partial_result_without_exception_details(self):
        batch, calls = fixture.fixture_batch(plan(), {"motor_current": {"unavailable": True}})
        self.assertEqual(batch["results"][0]["status"], "SOURCE_UNAVAILABLE")
        self.assertNotIn("secret", json.dumps(batch))
        self.assertEqual(len(calls), 5)

    def test_cli_default_dry_run_no_source_client(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"; path.write_text(json.dumps(plan()))
            args = parse_args(["condition-evidence", "--plan-file", str(path)])
            self.assertFalse(args.execute)
            with patch("src.adapters.pi.client.PiClient") as client:
                self.assertEqual(cmd_condition_evidence(args), 0)
                client.assert_not_called()

    def test_cli_execute_has_exclusive_private_bounded_output(self):
        import tempfile
        from unittest.mock import patch
        p=plan()
        boundary=fixture.SyntheticBoundary(fixture.PiClient(fixture.PiApiConfig(base_url=fixture.BASE), session=fixture.SyntheticSession(p,{})))
        with tempfile.TemporaryDirectory() as directory:
            inp=Path(directory)/"plan.json";inp.write_text(json.dumps(p))
            output=Path(directory)/"evidence.json"
            args=parse_args(["condition-evidence","--plan-file",str(inp),"--output",str(output),"--execute"])
            with patch("src.services.governed_source.GovernedSourceBoundary",return_value=boundary),patch("src.adapters.pi.client.time.sleep"):
                self.assertEqual(cmd_condition_evidence(args),0)
            self.assertEqual(output.stat().st_mode & 0o777,0o600)
            self.assertEqual(json.loads(output.read_text())["results"][0]["status"],"COLLECTED")
            with patch("src.adapters.pi.client.PiClient") as client:
                self.assertEqual(cmd_condition_evidence(args),2)
                client.assert_not_called()
