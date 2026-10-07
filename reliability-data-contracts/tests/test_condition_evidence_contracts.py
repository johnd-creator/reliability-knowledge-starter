"""Synthetic-only evidence schema compatibility and negative contract tests."""
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]

def fixture(name):
    return json.loads((ROOT/"examples/condition-evidence"/(name+".json")).read_text())

def validator(name):
    return Draft202012Validator(json.loads((ROOT/"schemas"/(name+".schema.json")).read_text()), format_checker=FormatChecker())

class ConditionContractTest(unittest.TestCase):
    def test_all_repository_schemas_valid_draft_2020_12(self):
        for path in (ROOT/"schemas").glob("*.schema.json"):
            Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_synthetic_evidence_plan_and_selection_validate(self):
        plan=fixture("synthetic-plan")
        validator("condition-projection-plan").validate(plan)
        validator("condition-signal-selection").validate(plan["signals"][0])
        validator("condition-evidence").validate(fixture("synthetic-evidence"))

    def test_numeric_text_digital_boolean_null_preserved(self):
        for kind,value in (("NUMERIC",0),("TEXT","RUNNING"),("DIGITAL_STATE",{"name":"RUN","code":1,"is_system":False}),
                           ("BOOLEAN",False),("NULL",None)):
            obj=fixture("synthetic-evidence");obj.update(value_type=kind,value=value)
            if value is None:obj["evidence_status"]="UNKNOWN_VALUE"
            validator("condition-evidence").validate(obj)
            self.assertEqual(json.loads(json.dumps(obj))["value"],value)

    def test_no_numeric_coercion_or_type_mismatch(self):
        for value in ("12",True,None):
            obj=fixture("synthetic-evidence");obj["value"]=value
            self.assertTrue(list(validator("condition-evidence").iter_errors(obj)))

    def test_quality_and_nullable_metadata_remain_explicit(self):
        obj=fixture("synthetic-evidence")
        obj.update(quality_good=False,quality_questionable=True,quality_substituted=True,quality_annotated=True,evidence_status="BAD_QUALITY",unit=None,source_timestamp=None)
        validator("condition-evidence").validate(obj)
        obj["quality_good"]="false"
        self.assertTrue(list(validator("condition-evidence").iter_errors(obj)))

    def test_naive_timestamp_and_secret_raw_fields_rejected(self):
        for field,value in (("source_timestamp","2026-10-07T12:00:00"),("Authorization","secret"),("raw_payload",{})):
            obj=fixture("synthetic-evidence");obj[field]=value
            self.assertTrue(list(validator("condition-evidence").iter_errors(obj)))

    def test_quality_status_cannot_claim_available_when_bad_or_unknown(self):
        for update in ({"quality_good":False},{"quality_questionable":True},{"quality_good":None}):
            obj=fixture("synthetic-evidence");obj.update(update)
            self.assertTrue(list(validator("condition-evidence").iter_errors(obj)))
        plan=fixture("synthetic-plan");plan["signals"][0]["approval_status"]="RETIRED"
        self.assertTrue(list(validator("condition-projection-plan").iter_errors(plan)))

    def test_source_identifiers_quarantined(self):
        obj=fixture("synthetic-evidence")
        for field in ("pi_source_id","af_element_ref","attribute_ref","attribute_name"):
            self.assertNotIn(field,obj)
            self.assertIn(field,obj["sources"]["pi"])
        self.assertIn("attribute_ref",fixture("synthetic-plan")["signals"][0]["sources"]["pi"])

    def test_mapping_gate_and_signal_count_bound(self):
        for status in ("PROPOSED","AMBIGUOUS","RETIRED","UNMAPPED"):
            plan=fixture("synthetic-plan");plan["sources"]["pi"]["mapping_status"]=status
            self.assertTrue(list(validator("condition-projection-plan").iter_errors(plan)))
        plan=fixture("synthetic-plan");plan["signals"]*=433
        self.assertTrue(list(validator("condition-projection-plan").iter_errors(plan)))
