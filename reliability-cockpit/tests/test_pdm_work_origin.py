"""Work origin is human context on the existing owning inspection/revision store."""
import copy
import json
import os
import unittest
from hashlib import sha256
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
from src.domain.manual_inspection import InspectionDraft, ManualInspection
import test_bundle_c_integration as fixture
from test_pdm_input_capture import capture, legacy_document

DEPT = dict(source="DEPARTMENT_REQUEST", requesting_department="  Synthetic EPA  ", reported_asset_label="  Belt conveyor / belum terverifikasi  ")
PM = dict(source="PDM_PM_52_WEEK", reported_asset_label="Synthetic unknown source asset")

class OriginContractTest(unittest.TestCase):
    def test_legacy_native_digests_unchanged_and_origin_absent(self):
        for version, expected in {"1.0":"d338769072a913247618962fdac9f0354bb47b71f12140462e5533f414fa23f3", "1.1":"006463493f56f271f5c8c27d9ee88a2e844fd8a1b14e25607e8bebbf2e50021c"}.items():
            record=ManualInspection.model_validate(legacy_document(version))
            self.assertNotIn("work_origin",record.model_dump())
            self.assertEqual(sha256(record.model_dump_json().encode()).hexdigest(),expected)

    def test_capture_legacy_digest_unchanged(self):
        record=ManualInspection.model_validate({**legacy_document("1.2"),"input_capture":capture()})
        self.assertNotIn("work_origin",record.model_dump())
        self.assertEqual(sha256(record.model_dump_json().encode()).hexdigest(),"6c0f6ce97a03e7bb6a49c331389b37c5eecd6e0f697d71aa6a6aa1bf04926394")

    def test_exact_reported_labels_no_binding_or_department_coercion(self):
        for origin in (DEPT,PM):
            row=ManualInspection.model_validate({**legacy_document("1.3"),"work_origin":origin})
            self.assertEqual(row.work_origin.model_dump(mode="json"),origin)
            self.assertEqual(row.canonical_asset_id,"asset:SYNTHETIC:CAPTURE")

    def test_conditional_department_bounds_and_extra_authority_rejected(self):
        bad=[{}, {"source":"UNKNOWN"}, {"source":"DEPARTMENT_REQUEST"}, {**DEPT,"requesting_department":None},
             {**DEPT,"requesting_department":" "},{**DEPT,"requesting_department":"x"*161},{**DEPT,"requesting_department":False},
             {**PM,"requesting_department":"EPA"},{**PM,"requesting_department":None},{**PM,"reported_asset_label":10},
             {**PM,"reported_asset_label":"x"*201},{**PM,"reported_asset_label":" "},{**PM,"reported_asset_label":""},
             {**PM,"canonical_asset_id":"invented"},{**PM,"operator_approved":True},{**PM,"diagnosis":"invented"}]
        for origin in bad:
            with self.subTest(origin=origin),self.assertRaises(ValidationError):
                ManualInspection.model_validate({**legacy_document("1.3"),"work_origin":origin})

    def test_version_matrix_for_origin_native_and_capture(self):
        for version in ("1.0","1.1","1.2","1.3"):
            for provisional in (False,True):
                for origin in (None,DEPT,PM):
                    data={**legacy_document(version),**({"input_capture":capture()} if provisional else {}),**({"work_origin":origin} if origin else {})}
                    valid=(version=="1.3" if origin else version=="1.2" if provisional else version in {"1.0","1.1"})
                    with self.subTest(version=version,capture=provisional,origin=origin):
                        if valid:ManualInspection.model_validate(data)
                        else:
                            with self.assertRaises(ValidationError):ManualInspection.model_validate(data)

    def test_published_schema_matches_and_accepts_only_typed_source(self):
        p=Path(__file__).resolve().parents[2]/"reliability-data-contracts/schemas/manual-inspection.schema.json"
        schema=json.loads(p.read_text());Draft202012Validator.check_schema(schema)
        for key,value in ManualInspection.model_json_schema().items():self.assertEqual(schema[key],value)
        validator=Draft202012Validator(schema,format_checker=FormatChecker())
        for origin in (DEPT,PM):validator.validate(ManualInspection.model_validate({**legacy_document("1.3"),"work_origin":origin}).model_dump(mode="json"))
        self.assertTrue(list(validator.iter_errors({**legacy_document("1.3"),"work_origin":dict(source="PDM_PM_52_WEEK",requesting_department="EPA")})))

class OriginWorkflowTest(unittest.TestCase):
    application_engine=fixture.BundleCIntegrationTest.application_engine
    setUp=fixture.BundleCIntegrationTest.setUp
    tearDown=fixture.BundleCIntegrationTest.tearDown
    call=fixture.BundleCIntegrationTest.call
    step=fixture.BundleCIntegrationTest.step

    def draft(self,origin=DEPT,provisional=False):
        return dict(canonical_asset_id=self.asset,method="OTHER",method_version="synthetic-origin-1",inspector_ref="author",
            **({"work_origin":copy.deepcopy(origin)} if origin else {}),
            **({"input_capture":capture()} if provisional else {"observations":["Synthetic PM finding"]}))
    def create(self,draft,key="origin-create"):
        return self.call("POST","inspections",dict(request_id=key,draft=draft),expected=201)
    def test_native_create_replay_update_cas_review_revise_history_readback(self):
        original=self.draft();row=self.create(original)
        self.assertEqual(row["contract_version"],"1.3");self.assertEqual(row["work_origin"],DEPT)
        self.assertEqual(self.create(original),row)
        updated=self.call("PUT","inspections/"+row["record_id"],dict(request_id="origin-edit",expected_revision=1,draft=self.draft(PM)))
        self.call("PUT","inspections/"+row["record_id"],dict(request_id="origin-stale",expected_revision=1,draft=original),expected=409)
        self.assertEqual(self.call("GET","inspections/"+row["record_id"]),updated)
        submitted=self.step("inspections",updated,"submit")
        self.step("inspections",submitted,"begin_review",dict(reason="self review denied"),expected=403)
        reviewing=self.step("inspections",submitted,"begin_review",dict(reason="Independent context review"),"reviewer")
        returned=self.step("inspections",reviewing,"review",dict(decision="RETURNED",reason="Clarify context"),"reviewer")
        revised=self.step("inspections",returned,"revise",dict(reason="Retain recorded source"))
        self.assertEqual(revised["work_origin"],PM)
        history=self.call("GET","inspections/"+row["record_id"]+"/history")
        self.assertEqual(history[0]["snapshot"]["work_origin"],DEPT)
        self.assertTrue(all(event["snapshot"]["work_origin"]==PM for event in history[1:]))
        self.assertNotIn("requesting_department",revised["work_origin"])

    def test_explicit_origin_clear_keeps_legacy_snapshot_and_downgrades_native_contract(self):
        row=self.create(self.draft())
        changed=self.call("PUT","inspections/"+row["record_id"],dict(request_id="clear-origin",expected_revision=1,draft=self.draft(None)))
        self.assertEqual(changed["contract_version"],"1.1");self.assertNotIn("work_origin",changed)
        self.assertEqual(self.call("GET","inspections/"+row["record_id"]),changed)
        self.assertEqual(self.call("GET","inspections/"+row["record_id"]+"/history")[0]["snapshot"]["work_origin"],DEPT)

    def test_capture_origin_and_workbook_asset_labels_remain_distinct(self):
        row=self.create(self.draft(PM,True));self.assertEqual(row["contract_version"],"1.3")
        self.assertEqual(row["input_capture"]["source_asset_label"],capture()["source_asset_label"])
        self.assertEqual(row["work_origin"],PM);self.assertNotEqual(row["canonical_asset_id"],PM["reported_asset_label"])
        self.assertEqual(self.call("GET","inspections/measurement-history")["items"],[])

    def test_legacy_revise_does_not_fabricate_origin_and_explicit_origin_can_be_added(self):
        row=self.create(self.draft(None));self.assertEqual(row["contract_version"],"1.1");self.assertNotIn("work_origin",row)
        new=self.call("PUT","inspections/"+row["record_id"],dict(request_id="explicit-origin",expected_revision=1,draft=self.draft(PM)))
        self.assertEqual(new["contract_version"],"1.3")
        self.assertNotIn("work_origin",self.call("GET","inspections/"+row["record_id"]+"/history")[0]["snapshot"])

    def test_session_scope_csrf_reviewer_and_attribution_boundaries(self):
        row=self.create(self.draft());path="inspections/"+row["record_id"]
        self.call("PUT",path,dict(request_id="reviewer-write",expected_revision=1,draft=self.draft()),actor="reviewer",expected=403)
        self.call("POST","inspections",dict(request_id="csrf-origin",draft=self.draft()),headers={"X-CSRF-Token":"incorrect"},expected=403)
        grant=self.provider.grants["author"]
        self.provider.grants["author"]=grant.model_copy(update={"principal":grant.principal.model_copy(update={"asset_ids":frozenset({"asset:SYNTHETIC:FOREIGN"})})})
        self.call("GET",path,expected=404)

@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable QA PostgreSQL fixture not configured")
class OriginPostgresWorkflowTest(OriginWorkflowTest):
    application_engine=fixture.BundleCPostgresIntegrationTest.application_engine


@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable QA PostgreSQL fixture not configured")
class OriginQaValidationPostgresTest(unittest.TestCase):
    application_engine=fixture.BundleCPostgresIntegrationTest.application_engine
    tearDown=fixture.BundleCIntegrationTest.tearDown
    call=fixture.BundleCIntegrationTest.call
    draft=OriginWorkflowTest.draft
    create=OriginWorkflowTest.create
    def setUp(self):
        fixture.BundleCIntegrationTest.setUp(self)
        from fastapi.testclient import TestClient
        from src.api.engineering_qa import create_qa_app
        app=create_qa_app(authority=self.authority,cases=self.cases,inspections=self.inspections,
            recommendations=self.recommendations,context=self.context,environment="development")
        self.client.close();self.client=TestClient(app,base_url="https://nadi.example.invalid")

    def test_invalid_origin_http_422_sanitized_and_no_persistence_then_valid_write(self):
        for origin in (dict(source="DEPARTMENT_REQUEST"),dict(source="PDM_PM_52_WEEK",requesting_department="PRIVATE-SYNTHETIC-MARKER"),
                dict(source="GUESSED"),{**DEPT,"reported_asset_label":False},{**PM,"operator_approved":True}):
            failure=self.call("POST","inspections",dict(request_id="invalid-origin",draft=self.draft(origin)),expected=422)
            self.assertEqual(failure,{"detail":{"code":"INVALID_REQUEST"}})
            self.assertNotIn("PRIVATE-SYNTHETIC-MARKER",json.dumps(failure))
        self.assertEqual(self.call("GET","inspections")["items"],[])
        self.assertEqual(self.create(self.draft())["revision"],1)

    def test_inspector_attribution_foreign_asset_and_revocation_deny_origin_writes(self):
        draft=self.draft();draft["inspector_ref"]="reviewer"
        self.call("POST","inspections",dict(request_id="spoofed-origin",draft=draft),expected=422)
        draft=self.draft();draft["canonical_asset_id"]="asset:SYNTHETIC:FOREIGN"
        self.call("POST","inspections",dict(request_id="foreign-origin",draft=draft),expected=404)
        row=self.create(self.draft())
        self.authority.revoke(self.directory("author"),self.credentials["author"][0])
        self.call("GET","inspections/"+row["record_id"],expected=401)
        self.call("PUT","inspections/"+row["record_id"],dict(request_id="revoked-origin",expected_revision=1,draft=self.draft(PM)),expected=401)
