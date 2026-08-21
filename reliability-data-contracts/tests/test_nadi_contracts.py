import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).parents[1]
SCHEMA_DIR = ROOT / "schemas"


def load_schema(name):
    return json.loads((SCHEMA_DIR / name).read_text())


def provenance(obj, source_object, record_id):
    obj["contract_version"] = "1.0"
    obj["provenance"] = {
        "source_system": "MAXIMO",
        "source_application": "RELIABILITY",
        "source_object": source_object,
        "source_record_id": record_id,
        "source_site": "BSR",
        "source_organization": "IP",
    }
    return obj


class NadiContractTests(unittest.TestCase):
    def test_new_schemas_are_valid_draft_2020_12(self):
        for name in (
            "asset-master.schema.json",
            "fmea-assessment.schema.json",
            "rcfa-analysis.schema.json",
            "asset-health-assessment.schema.json",
            "overhaul-event.schema.json",
            "maintenance-event.schema.json",
        ):
            Draft202012Validator.check_schema(load_schema(name))

    def test_synthetic_v1_records_validate(self):
        examples = {
            "asset-master.schema.json": provenance(
                {"canonical_id": "asset:MAXIMO:MXASSET:BSR:IP:<asset>", "source_asset_number": "<asset>"},
                "MXASSET", "<asset>",
            ),
            "fmea-assessment.schema.json": provenance(
                {"canonical_id": "fmea:MAXIMO:IPFMEA:BSR:IP:<id>", "source_record_id": "<id>", "asset_ref": "asset:example", "relationship_evidence": {"asset_ref": {"status": "DIRECT_VERIFIED"}}},
                "IPFMEA", "<id>",
            ),
            "rcfa-analysis.schema.json": provenance(
                {"canonical_id": "rcfa:MAXIMO:IPRCFA:BSR:IP:<id>", "source_record_id": "<id>", "asset_ref": None, "workorder_ref": None, "relationship_evidence": {"asset_ref": {"status": "UNRESOLVED"}, "workorder_ref": {"status": "UNRESOLVED"}}},
                "IPRCFA", "<id>",
            ),
            "asset-health-assessment.schema.json": provenance(
                {"canonical_id": "bhm:MAXIMO:IPBHM:BSR:IP:<id>", "source_record_id": "<id>", "asset_ref": "asset:example", "relationship_evidence": {"asset_ref": {"status": "DIRECT_VERIFIED"}}},
                "IPBHM", "<id>",
            ),
            "overhaul-event.schema.json": provenance(
                {"canonical_id": "oh:MAXIMO:IP_DOM_OH:BSR:IP:<id>", "source_record_id": "<id>", "workorder_ref": "wo:example", "asset_ref": None, "relationship_evidence": {"workorder_ref": {"status": "DIRECT_VERIFIED"}, "asset_ref": {"status": "DERIVED_VERIFIED_PATH", "path": ["IP_DOM_OH.wonum", "MXWODETAIL.wonum", "MXWODETAIL.assetnum"]}}},
                "IP_DOM_OH", "<id>",
            ),
        }
        for schema_name, example in examples.items():
            errors = sorted(Draft202012Validator(load_schema(schema_name)).iter_errors(example), key=lambda e: e.path)
            self.assertEqual([], errors, schema_name)

    def test_maintenance_event_keeps_legacy_shape_and_accepts_v1_metadata(self):
        example = provenance(
            {"id": "<wo>", "equipment_id": "<asset>", "canonical_id": "event:example", "provenance": None},
            "MXWODETAIL", "<wo>",
        )
        # `provenance()` creates the v1 object; the schema's nullable field is
        # intentionally tested with a real object below instead of null.
        example["provenance"] = {
            "source_system": "MAXIMO", "source_object": "MXWODETAIL", "source_record_id": "<wo>"
        }
        errors = list(Draft202012Validator(load_schema("maintenance-event.schema.json")).iter_errors(example))
        self.assertEqual([], errors)

    def test_mapping_identity_and_relationship_integrity(self):
        mapping = json.loads((ROOT / "mappings/maximo-nadi-reliability.json").read_text())
        rows = mapping["mappings"]
        self.assertTrue(any(r["source_object"] == "IPFMEA" and r["source_field"] == "assetnum" and r["canonical_field"] == "asset_ref" and r["evidence"] == "DIRECT_VERIFIED" for r in rows))
        self.assertTrue(any(r["source_object"] == "IPBHM" and r["source_field"] == "assetnum" and r["canonical_field"] == "asset_ref" for r in rows))
        self.assertTrue(any(r["source_object"] == "IP_DOM_OH" and r["source_field"] == "wonum" and r["canonical_field"] == "workorder_ref" for r in rows))
        self.assertTrue(any(r["source_object"] == "IP_DOM_OH" and r["canonical_field"] == "asset_ref" and r["evidence"] == "DERIVED_VERIFIED_PATH" for r in rows))
        self.assertTrue(any(r["source_object"] == "IPRCFA" and r["canonical_field"] == "asset_ref" and r["evidence"] == "UNRESOLVED" for r in rows))
        bad_identity = {"siteid", "orgid", "assetnum", "wonum"}
        for row in rows:
            if row["canonical_field"] in {"source_record_id", "source_number"}:
                self.assertNotIn(row["source_field"], bad_identity, row)

    def test_relationship_graph_and_deferred_registry(self):
        graph = json.loads((ROOT / "catalog/nadi-reliability-relationship-graph.json").read_text())
        edges = {(e["from"], e["to"], e["field"]): e["evidence"] for e in graph["edges"]}
        self.assertEqual("DIRECT_VERIFIED", edges[("fmea_assessment", "asset_master", "asset_ref")])
        self.assertEqual("DERIVED_VERIFIED_PATH", edges[("overhaul_event", "asset_master", "asset_ref")])
        self.assertEqual("UNRESOLVED", edges[("rcfa_analysis", "asset_master", "asset_ref")])
        deferred = json.loads((ROOT / "catalog/nadi-reliability-deferred.json").read_text())["deferred_contracts"]
        self.assertEqual({"IPFMEAITEM", "IPBHMMEASUREMENT", "DMD_OPLOGABN", "IPMSMSFAILUREMECHANI"}, {x["source_resource"] for x in deferred})


if __name__ == "__main__":
    unittest.main()
