"""Provisional source input: strict types, precision, history and native parity."""
import copy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
from src.domain.engineering import EngineeringError, EvidenceKind, Principal, Role
from src.domain.manual_inspection import InspectionDraft, ManualInspection
from src.domain.pdm_input_capture import CaptureClock, InputCapture
from src.repositories.human_records import RecordRow
from src.services.reviewed_inspection_evidence import ReviewedInspectionCatalog
from src.api.engineering_qa import create_qa_app
import test_bundle_c_integration as fixture

ROOT = Path(__file__).resolve().parents[1]


def capture():
    return dict(source_ref="WB-SYNTHETIC", source_asset_label="Synthetic source equipment, unbound",
        source_sheet_label="  Synthetic original sheet label  ", source_sha256="a" * 64, sheet_index=0,
        profile_id="synthetic-input", profile_version="provisional-input-1", clocks=[dict(
            role="SAMPLE", precision="DATE", raw_value="2099/01/02", value="2099-01-02",
            source_label="Synthetic sample date")], rows=[dict(row_id="row-1", source_label="Synthetic source quantity",
            raw_value=0, unit="source unit", source_point="source point only", source_axis="source axis only",
            header_cells=["B2", "C2:D2"], value_origin="SOURCE_LITERAL", row_role="INPUT",
            contexts=[dict(role="LAB", label="Reported lab", raw_value="Synthetic lab")],
            clock=dict(role="REPORT", precision="LOCAL_DATETIME", raw_value="2099-01-03 10:20",
                value="2099-01-03T10:20"))])


def legacy_document(version):
    return dict(contract_version=version, record_id="inspection:SYNTHETIC:LEGACY",
        canonical_asset_id="asset:SYNTHETIC:CAPTURE", method="OTHER", method_version="candidate-1",
        inspector_ref="author", created_by="author", created_at="2026-10-09T10:00:00Z",
        updated_at="2026-10-09T13:00:00Z", revision=4, observations=["Synthetic legacy record"],
        status="APPROVED", submitted_at="2026-10-09T11:00:00Z", review_started_by="reviewer",
        review_started_at="2026-10-09T12:00:00Z", review=dict(reviewer="reviewer", decision="APPROVED",
            rationale="Independent record review only", decided_at="2026-10-09T13:00:00Z"))


class CaptureContractTest(unittest.TestCase):
    def test_merged_header_rows_keep_distinct_field_ids_and_value_regions(self):
        source = capture()
        row = source["rows"][0]
        source["rows"] = [{**row, "row_id": "r-1", "source_field_id": "source-column-B",
            "value_region": "B3:B100", "header_cells": ["B2:D2"]},
            {**row, "row_id": "r-2", "source_field_id": "source-column-C",
            "value_region": "C3:C100", "header_cells": ["B2:D2"]}]
        result = InputCapture.model_validate_json(json.dumps(source)).model_dump(mode="json")
        self.assertEqual(result["rows"][0]["source_label"], result["rows"][1]["source_label"])
        self.assertEqual(result["rows"][0]["header_cells"], result["rows"][1]["header_cells"])
        self.assertEqual([row["source_field_id"] for row in result["rows"]], ["source-column-B", "source-column-C"])
        self.assertEqual([row["value_region"] for row in result["rows"]], ["B3:B100", "C3:C100"])

    def test_source_scalars_units_labels_and_origins_roundtrip_without_coercion(self):
        source = capture()
        source["rows"] = [dict(row_id=f"r-{i}", source_label="  Exact source label\nline two  ",
            raw_value=value, unit=" mg KOH/g ", value_origin=origin, row_role=role)
            for i, (value, origin, role) in enumerate(((0, "SOURCE_LITERAL", "INPUT"),
                (-0.0, "MANUAL_REPORTED", "INPUT"), ("0", "SOURCE_LITERAL", "INPUT"),
                (False, "UNKNOWN", "INPUT"), (None, "UNKNOWN", "INPUT"),
                ("Synthetic formula result", "SOURCE_FORMULA_RESULT", "REFERENCE"),
                ("Synthetic reported warning", "MANUAL_REPORTED", "SOURCE_ASSESSMENT")))]
        parsed = InputCapture.model_validate_json(json.dumps(source))
        self.assertEqual(parsed.source_asset_label, source["source_asset_label"])
        self.assertEqual(parsed.source_sheet_label, source["source_sheet_label"])
        for expected, row in zip(source["rows"], parsed.rows):
            self.assertEqual(row.raw_value, expected["raw_value"])
            self.assertIs(type(row.raw_value), type(expected["raw_value"]))
            self.assertEqual((row.source_label, row.unit), (expected["source_label"], expected["unit"]))
            self.assertEqual((row.value_origin, row.row_role), (expected["value_origin"], expected["row_role"]))
        self.assertEqual(math.copysign(1, parsed.rows[1].raw_value), -1)
        self.assertEqual(parsed.purpose, "PROVISIONAL_INPUT_ONLY")

    def test_clock_precisions_preserve_originals_without_inventing_timezone_or_midnight(self):
        examples = [dict(precision="DATE", raw_value=20990102, value="2099-01-02"),
            dict(precision="DATETIME", raw_value="synthetic reported offset time", value="2099-01-02T10:20:30+07:00"),
            dict(precision="LOCAL_DATETIME", raw_value="02/01/2099 10:20", value="2099-01-02T10:20"),
            dict(precision="TIME", raw_value="10:20", value="10:20"),
            dict(precision="RAW", raw_value=12345, value=None),
            dict(precision="UNKNOWN", raw_value=None, value=None)]
        for example in examples:
            with self.subTest(precision=example["precision"]):
                row = CaptureClock.model_validate(example)
                self.assertEqual(row.model_dump(mode="json")["value"], example["value"])
                self.assertEqual(row.raw_value, example["raw_value"])
        for example in (dict(precision="DATE", raw_value="bad", value="2026-02-30"),
                dict(precision="DATE", raw_value="bad", value="2026-01-02T00:00:00Z"),
                dict(precision="DATETIME", raw_value="bad", value="2026-01-02T10:20"),
                dict(precision="LOCAL_DATETIME", raw_value="bad", value="2026-01-02T10:20Z"),
                dict(precision="TIME", raw_value="bad", value="24:01"),
                dict(precision="TIME", raw_value="bad", value="10:20+07:00"),
                dict(precision="RAW", raw_value="unknown", value="2026-01-02"),
                dict(precision="UNKNOWN", raw_value=None, value="2026-01-02"),
                dict(precision="DATE", raw_value=None, value="2026-01-02"),
                dict(precision="DATE", raw_value=False, value="2026-01-02")):
            with self.subTest(invalid=example), self.assertRaises(ValidationError):
                CaptureClock.model_validate(example)

    def test_strict_capture_bounds_finite_scalars_and_no_hidden_authority(self):
        invalid = []
        for key, value in (("purpose", "ENGINEER_APPROVED"), ("source_sha256", "invalid"),
                ("sheet_index", True), ("sheet_index", -1), ("rows", []), ("approved", True)):
            invalid.append({**capture(), key: value})
        row = capture()["rows"][0]
        invalid.extend([{**capture(), "rows": [row] * 2},
            {**capture(), "rows": [{**row, "row_id": str(i)} for i in range(101)]},
            {**capture(), "rows": [{**row, "raw_value": [1]}]},
            {**capture(), "rows": [{**row, "header_cells": ["=HYPERLINK(unsafe)"]}]},
            {**capture(), "rows": [{**row, "canonical_point_id": "guessed"}]},
            {**capture(), "rows": [{**row, "raw_value": "x" * 2001}]},
            {**capture(), "rows": [{**row, "contexts": [{"role": "ARBITRARY", "label": "X"}]}]}])
        for value in (float("inf"), float("-inf"), float("nan")):
            invalid.extend([{**capture(), "rows": [{**row, "raw_value": value}]},
                {**capture(), "clocks": [dict(raw_value=value)]},
                {**capture(), "rows": [{**row, "contexts": [dict(role="LAB", label="X", raw_value=value)]}]}])
        for index, data in enumerate(invalid):
            with self.subTest(case=index), self.assertRaises(ValidationError):
                InputCapture.model_validate(data)

    def test_native_legacy_json_and_existing_evidence_digests_are_byte_compatible(self):
        # Witnesses computed from unmodified main35f native models before adding
        # input_capture. Adding default null must not silently invalidate pins.
        hashes = {"1.0": "d338769072a913247618962fdac9f0354bb47b71f12140462e5533f414fa23f3",
            "1.1": "006463493f56f271f5c8c27d9ee88a2e844fd8a1b14e25607e8bebbf2e50021c"}
        for version, expected in hashes.items():
            row = ManualInspection.model_validate(legacy_document(version))
            self.assertNotIn("input_capture", row.model_dump())
            self.assertEqual(sha256(row.model_dump_json().encode()).hexdigest(), expected)
            author = Principal(principal_id="author", roles={Role.AUTHOR}, asset_ids={row.canonical_asset_id})
            class Inspections:
                def get(self, actor, record):
                    return row
            catalog = ReviewedInspectionCatalog(None, Inspections(), lambda actor: author)
            ref = catalog.resolve(row.canonical_asset_id, EvidenceKind.MANUAL_INSPECTION,
                row.record_id, "FROZEN_SNAPSHOT", "author", datetime(2026, 10, 20, tzinfo=timezone.utc))
            self.assertEqual(ref.stable_version, expected)

    def test_capture_requires_1_2_and_cannot_mix_with_native_measurements(self):
        data = dict(canonical_asset_id="asset:SYNTHETIC:CAPTURE", method="OTHER",
            method_version="provisional-input-1", inspector_ref="author", input_capture=capture())
        for extra in (dict(measurements=[dict(quantity="Synthetic", value=1)]), dict(method_extension={"input_capture": {}})):
            with self.assertRaises(ValidationError):
                InspectionDraft.model_validate({**data, **extra})
        for version in ("1.0", "1.1"):
            with self.assertRaises(ValidationError):
                ManualInspection.model_validate({**legacy_document(version), "input_capture": capture()})
        with self.assertRaises(ValidationError):
            ManualInspection.model_validate(legacy_document("1.2"))

    def test_published_input_and_record_schemas_match_domain(self):
        for model, filename in ((InputCapture, "pdm-input-capture.schema.json"),
                (ManualInspection, "manual-inspection.schema.json")):
            actual = json.loads((ROOT.parent / "reliability-data-contracts/schemas" / filename).read_text())
            Draft202012Validator.check_schema(actual)
            for key, value in model.model_json_schema().items():
                self.assertEqual(actual[key], value)
        schema = json.loads((ROOT.parent / "reliability-data-contracts/schemas/pdm-input-capture.schema.json").read_text())
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(InputCapture.model_validate(capture()).model_dump(mode="json"))


class CaptureWorkflowTest(unittest.TestCase):
    application_engine = fixture.BundleCIntegrationTest.application_engine
    setUp = fixture.BundleCIntegrationTest.setUp
    tearDown = fixture.BundleCIntegrationTest.tearDown
    call = fixture.BundleCIntegrationTest.call
    step = fixture.BundleCIntegrationTest.step

    def draft(self):
        return dict(canonical_asset_id=self.asset, method="OTHER", method_version="provisional-input-1",
            input_capture=capture())

    def create(self, key="capture-create", draft=None):
        return self.call("POST", "inspections", dict(request_id=key, draft=dict(
            inspector_ref="author", **(draft or self.draft()))), expected=201)

    def test_create_update_replay_review_history_and_case_refusal(self):
        draft = self.draft()
        row = self.create(draft=draft)
        self.assertEqual(row["contract_version"], "1.2")
        self.assertEqual(row["measurements"], [])
        self.assertIsNone(row["inspected_at"])
        self.assertEqual(row["input_capture"]["clocks"][0]["value"], "2099-01-02")
        self.assertEqual(row["canonical_asset_id"], self.asset)
        self.assertNotEqual(row["canonical_asset_id"], row["input_capture"]["source_asset_label"])
        self.assertEqual(self.create(draft=draft), row)
        source = copy.deepcopy(draft)
        source["input_capture"]["rows"][0]["raw_value"] = "Synthetic corrected input"
        changed = self.call("PUT", "inspections/" + row["record_id"], dict(request_id="capture-edit",
            expected_revision=row["revision"], draft=dict(inspector_ref="author", **source)))
        self.call("PUT", "inspections/" + row["record_id"], dict(request_id="stale-capture-edit",
            expected_revision=row["revision"], draft=dict(inspector_ref="author", **draft)), expected=409)
        changed = self.step("inspections", changed, "submit")
        changed = self.step("inspections", changed, "begin_review", dict(reason="Source transcription review"), "reviewer")
        approved = self.step("inspections", changed, "review", dict(decision="APPROVED", reason="Record review only"), "reviewer")
        self.assertEqual((approved["approval_scope"], approved["field_approval"], approved["assessment"]),
            ("NADI_RECORD_REVIEW_ONLY", "ENGINEER_FIELDS_PENDING", "NOT_ASSESSED"))
        history = self.call("GET", "inspections/" + row["record_id"] + "/history")
        self.assertEqual(history[0]["snapshot"], row)
        self.assertEqual(len(history), approved["revision"])
        self.assertEqual(history[-1]["snapshot"]["input_capture"], approved["input_capture"])
        events = self.call("GET", "inspections/measurement-history")
        self.assertEqual(events["items"], [])
        case = self.call("POST", "cases", dict(request_id="capture-case", draft=dict(canonical_asset_id=self.asset,
            title="Synthetic capture is not Case evidence", problem_statement="Do not infer measurement semantics")), expected=201)
        failure = self.call("POST", "cases/" + case["case_id"] + "/evidence", dict(request_id="capture-link",
            expected_revision=case["revision"], kind="MANUAL_INSPECTION", record_id=row["record_id"],
            mode="FROZEN_SNAPSHOT", expected_inspection_revision=approved["revision"]), expected=409)
        self.assertEqual(failure["detail"]["code"], "PROVISIONAL_INPUT_NOT_CASE_EVIDENCE")
        self.assertEqual(self.call("GET", "cases/" + case["case_id"]), case)
        # Owning-store guard also rejects a forged previously-created reference.
        from types import SimpleNamespace
        ref = SimpleNamespace(kind="MANUAL_INSPECTION", record_id=row["record_id"])
        with self.engine.begin() as connection, self.assertRaises(EngineeringError) as error:
            self.catalog.guard_evidence(connection, self.directory("author"), self.asset, (ref,))
        self.assertEqual(error.exception.code, "PROVISIONAL_INPUT_NOT_CASE_EVIDENCE")

    def test_authority_asset_and_mixed_measurement_rejections(self):
        for extra in (dict(field_approval="ENGINEER_APPROVED"), dict(assessment="HEALTHY"),
                dict(measurements=[dict(quantity="Guessed quantity", value=0)])):
            # Bare BundleC's session lease predates the QA app's sanitized
            # validation boundary. Validate malformed DTOs directly here;
            # actual QA HTTP malformed-input qualification is a separate gate.
            with self.assertRaises(ValidationError):
                InspectionDraft.model_validate(dict(inspector_ref="author", **{**self.draft(), **extra}))
        self.call("POST", "inspections", dict(request_id="foreign-capture", draft=dict(
            inspector_ref="author", **{**self.draft(), "canonical_asset_id": "asset:SYNTHETIC:FOREIGN"})), expected=404)
        row = self.create()
        submitted = self.step("inspections", row, "submit")
        self.step("inspections", submitted, "begin_review", dict(reason="Self review"), expected=403)
        self.assertEqual(self.call("GET", "inspections/" + row["record_id"]), submitted)


@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable QA PostgreSQL fixture not configured")
class CaptureQaValidationPostgresTest(CaptureWorkflowTest):
    application_engine = fixture.BundleCPostgresIntegrationTest.application_engine

    def setUp(self):
        super().setUp()
        app = create_qa_app(authority=self.authority, cases=self.cases, inspections=self.inspections,
            recommendations=self.recommendations, context=self.context, environment="development")
        self.client.close()
        self.client = TestClient(app, base_url="https://nadi.example.invalid")

    def test_invalid_http_dtos_are_sanitized_422_without_mutation(self):
        original = self.inspections.list(self.directory("author"))
        invalid = []
        for extra in (dict(field_approval="SYNTHETIC-PRIVATE-MARKER"),
                dict(measurements=[dict(quantity="SYNTHETIC-PRIVATE-MARKER", value=0)])):
            invalid.append({**self.draft(), **extra})
        for clock in (dict(precision="DATE", raw_value="SYNTHETIC-PRIVATE-MARKER", value="2026-02-30"),
                dict(precision="DATETIME", raw_value="SYNTHETIC-PRIVATE-MARKER", value="2026-01-02T10:20")):
            data = self.draft()
            data["input_capture"]["clocks"] = [clock]
            invalid.append(data)
        data = self.draft()
        data["input_capture"]["purpose"] = "SYNTHETIC-PRIVATE-MARKER"
        invalid.append(data)
        for data in invalid:
            failure = self.call("POST", "inspections", dict(request_id="invalid-capture",
                draft=dict(inspector_ref="author", **data)), expected=422)
            self.assertEqual(failure, {"detail": {"code": "INVALID_REQUEST"}})
            self.assertNotIn("SYNTHETIC-PRIVATE-MARKER", json.dumps(failure))
        # Send actual JSON tokens rather than a client-side finite-only encoder,
        # proving the API rejects nonfinite numeric input itself.
        token, csrf = self.credentials["author"]
        self.client.cookies.set(self.authority.COOKIE, token)
        for value in (float("nan"), float("inf"), float("-inf")):
            data = self.draft()
            data["input_capture"]["rows"][0]["raw_value"] = value
            response = self.client.post("/v1/engineering/inspections", content=json.dumps(dict(
                request_id="nonfinite-input", draft=dict(inspector_ref="author", **data))),
                headers={"Origin": "https://nadi.example.invalid", "Content-Type": "application/json", "X-CSRF-Token": csrf})
            self.assertEqual(response.status_code, 422, response.text)
            self.assertEqual(response.json(), {"detail": {"code": "INVALID_REQUEST"}})
        self.assertEqual(self.inspections.list(self.directory("author")), original)
        # Failed request cleanup released its lease, allowing a valid request.
        self.assertEqual(self.create()["revision"], 1)

    def test_store_outage_remains_503_and_csrf_revocation_still_deny(self):
        with patch.object(self.authority.engine, "begin", side_effect=SQLAlchemyError("SYNTHETIC-PRIVATE-STORE")):
            failure = self.call("GET", "inspections", expected=503)
        self.assertEqual(failure, {"detail": {"code": "IDENTITY_STORE_UNAVAILABLE"}})
        row = self.create()
        self.call("POST", "inspections/" + row["record_id"] + "/submit", dict(request_id="csrf-denied",
            expected_revision=row["revision"]), headers={"X-CSRF-Token": "invalid"}, expected=403)
        self.assertEqual(self.call("GET", "inspections/" + row["record_id"]), row)
        self.authority.revoke(self.directory("author"), self.credentials["author"][0])
        self.call("GET", "inspections", expected=401)
