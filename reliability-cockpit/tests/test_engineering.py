"""Source-free case workflow, auth, evidence and isolated persistence acceptance."""
import copy
import json
import os
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, select, text, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import make_url
from src.api.app import create_app
from src.api.engineering import build_router
from src.domain.engineering import *
from src.repositories.engineering import CaseRepository, EngineeringBase, CaseRow, EventRow, ReceiptRow
from src.services.engineering import CaseService

NOW = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
ASSET = "asset:SYNTHETIC:FEEDER-A"
OTHER = "asset:SYNTHETIC:OTHER"
AUTHOR = Principal(principal_id="engineer-fixture", roles={Role.AUTHOR}, asset_ids={ASSET})
REVIEWER = Principal(principal_id="reviewer-fixture", roles={Role.REVIEWER}, asset_ids={ASSET})
OUTSIDER = Principal(principal_id="other-fixture", roles={Role.AUTHOR}, asset_ids={ASSET})
DRAFT = dict(title="Synthetic flow investigation", problem_statement="Investigate a synthetic observation.", canonical_asset_id=ASSET)
ROOT = Path(__file__).resolve().parents[1]


class FixtureCatalog:
    def registered(self, asset_id):
        return asset_id == ASSET

    def resolve(self, asset, kind, record_id, mode, actor, now):
        if record_id != "record:synthetic":
            raise EngineeringError("EVIDENCE_NOT_FOUND", 404)
        if kind not in {EvidenceKind.ASSET, EvidenceKind.DATA_TRUST}:
            raise EngineeringError("NO_APPROVED_EVIDENCE", 422)
        return EvidenceReference(reference_id="ref:synthetic", record_id=record_id, canonical_asset_id=asset,
            kind=kind, source="NADI_DATA_TRUST" if kind == EvidenceKind.DATA_TRUST else "CANONICAL_MART",
            mode=mode, stable_version="fixture-v1", observed_at=now, linked_at=now, linked_by=actor,
            identity_status="VERIFIED", signal_approval="NOT_APPLICABLE", freshness="UNKNOWN",
            snapshot=EvidenceSnapshot(label="Synthetic local evidence", availability="PARTIAL") if mode == "FROZEN_SNAPSHOT" else None)


class EngineeringTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool,
            connect_args={"check_same_thread": False})
        EngineeringBase.metadata.create_all(self.engine)
        self.repo = CaseRepository(self.engine)
        self.catalog = FixtureCatalog()
        self.service = CaseService(self.repo, self.catalog,
            directory=lambda name: {AUTHOR.principal_id: AUTHOR, REVIEWER.principal_id: REVIEWER}.get(name),
            enabled=True, clock=lambda: NOW)
        self.actor = AUTHOR
        app = FastAPI()
        app.include_router(build_router(self.service, enabled=True, trusted_principal_dependency=lambda: self.actor))
        self.client = TestClient(app, raise_server_exceptions=False)
        self.case = self.service.command(AUTHOR, "CREATE", DRAFT, "create-1")

    def tearDown(self):
        self.client.close(); self.engine.dispose()

    def command(self, action, payload=None, actor=AUTHOR, revision=None, request=None):
        return self.service.command(actor, action, payload or {}, request or action.lower(),
            case_id=self.case.case_id, expected_revision=revision or self.case.revision)

    def assert_code(self, code, operation):
        with self.assertRaises(EngineeringError) as ctx: operation()
        self.assertEqual(ctx.exception.code, code)

    def test_create_contract_actor_and_revision(self):
        self.assertEqual((self.case.revision, self.case.created_by, self.case.status), (1, AUTHOR.principal_id, "DRAFT"))
        self.assertEqual(self.case.provenance, "HUMAN_ENGINEERING_RECORD")
        self.assertEqual(self.service.history(AUTHOR, self.case.case_id)[0].previous_revision, 0)

    def test_client_actor_review_fields_forbidden(self):
        for field in ("created_by", "status", "reviewer", "revision", "sources"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                CaseDraft.model_validate(dict(DRAFT, **{field:"spoofed"}))

    def test_contract_blank_large_naive_and_unknown_status(self):
        for extra in ({"title":" "}, {"problem_statement":"x"*12001}, {"priority":"CRITICAL"}):
            with self.assertRaises(ValidationError): CaseDraft.model_validate(dict(DRAFT, **extra))
        with self.assertRaises(ValidationError): EngineeringCase.model_validate(dict(self.case.model_dump(), created_at=NOW.replace(tzinfo=None)))

    def test_no_auth_denies_reads_and_writes(self):
        self.assert_code("AUTHENTICATION_REQUIRED", lambda:self.service.get(None, self.case.case_id))
        self.assert_code("AUTHENTICATION_REQUIRED", lambda:self.service.command(None, "CREATE", DRAFT, "x"))
        self.actor=None
        self.assertEqual(self.client.get("/v1/engineering/cases").status_code, 401)

    def test_owner_and_scope_enforced(self):
        self.assert_code("NOT_FOUND", lambda:self.service.get(OUTSIDER,self.case.case_id))
        self.assert_code("NOT_FOUND", lambda:self.service.get(Principal(principal_id="no-scope", roles={Role.REVIEWER},asset_ids={OTHER}), self.case.case_id))
        self.assertEqual(self.service.list(OUTSIDER)["total"],0)
        self.assert_code("NOT_FOUND", lambda:self.command("NOTE", {"text":"attempt"}, actor=OUTSIDER))

    def test_no_role_is_forbidden(self):
        self.assert_code("FORBIDDEN", lambda:self.service.list(Principal(principal_id="no-role",roles=set(),asset_ids={ASSET})))

    def test_unknown_asset_and_assignment(self):
        actor=Principal(principal_id="engineer",roles={Role.AUTHOR},asset_ids={OTHER})
        self.assert_code("ASSET_NOT_REGISTERED",lambda:self.service.command(actor,"CREATE",dict(DRAFT,canonical_asset_id=OTHER),"other"))
        self.assert_code("INVALID_ASSIGNEE",lambda:self.service.command(AUTHOR,"CREATE",dict(DRAFT,assigned_engineer="spoof"),"assign"))

    def test_update_and_hypotheses_not_facts(self):
        self.case=self.command("UPDATE",dict(DRAFT,investigation={"hypotheses":["Synthetic hypothesis"],"observations":["Human observation"]}))
        self.assertEqual(self.case.revision,2)
        self.assertEqual(self.case.investigation.hypotheses,("Synthetic hypothesis",))
        self.assertEqual(self.case.evidence,())

    def test_stale_revision_and_asset_change(self):
        self.command("NOTE",{"text":"first"})
        self.assert_code("REVISION_CONFLICT",lambda:self.command("NOTE",{"text":"second"},request="second"))
        self.assertEqual(self.service.get(AUTHOR,self.case.case_id).revision,2)
        self.assert_code("ASSET_IMMUTABLE",lambda:self.command("UPDATE",dict(DRAFT,canonical_asset_id=OTHER),revision=2))

    def test_create_and_change_replay_preserve_times_audit(self):
        replay=self.service.command(AUTHOR,"CREATE",DRAFT,"create-1")
        self.assertEqual(replay,self.case)
        noted=self.command("NOTE",{"text":"note"})
        self.service.clock=lambda:NOW+timedelta(days=1)
        self.assertEqual(self.command("NOTE",{"text":"note"}),noted)
        self.assertEqual(len(self.service.history(AUTHOR,self.case.case_id)),2)
        self.assert_code("IDEMPOTENCY_CONFLICT",lambda:self.command("NOTE",{"text":"different"}))

    def test_valid_review_reject_revise_approve_reopen(self):
        self.case=self.command("SUBMIT")
        self.assert_code("INVALID_TRANSITION",lambda:self.command("NOTE",{"text":"after submit"}))
        self.case=self.command("REVIEW",{"decision":"REJECTED","reason":"Need evidence"},actor=REVIEWER)
        self.case=self.command("REVISE",{"reason":"Revise evidence"})
        self.case=self.command("SUBMIT",request="submit-2")
        self.case=self.command("REVIEW",{"decision":"APPROVED","reason":"Fixture reviewed"},actor=REVIEWER,request="review-2")
        self.assertEqual(self.case.review.reviewer,REVIEWER.principal_id)
        self.assert_code("INDEPENDENT_REVIEWER_REQUIRED",lambda:self.command("REOPEN",{"reason":"redo"}))
        self.case=self.command("REOPEN",{"reason":"New question"},actor=REVIEWER)
        self.assertEqual(self.case.status,"DRAFT")
        self.assertIsNone(self.case.review)
        history=self.service.history(REVIEWER,self.case.case_id)
        self.assertEqual([e.revision for e in history],list(range(1,8)))
        self.assertEqual(history[-1].reason,"New question")

    def test_self_approval_and_author_role_reviewer_rejected(self):
        self.case=self.command("SUBMIT")
        self.assert_code("INDEPENDENT_REVIEWER_REQUIRED",lambda:self.command("REVIEW",{"decision":"APPROVED","reason":"x"}))
        both=Principal(principal_id=AUTHOR.principal_id, roles={Role.AUTHOR,Role.REVIEWER},asset_ids={ASSET})
        self.assert_code("INDEPENDENT_REVIEWER_REQUIRED",lambda:self.command("REVIEW",{"decision":"APPROVED","reason":"x"},actor=both))

    def test_assignee_cannot_review_own_work(self):
        assigned=Principal(principal_id="assigned",roles={Role.AUTHOR,Role.REVIEWER},asset_ids={ASSET})
        self.service.directory=lambda _:assigned
        self.case=self.command("UPDATE",dict(DRAFT,assigned_engineer="assigned"))
        self.case=self.command("SUBMIT",actor=assigned)
        self.assert_code("INDEPENDENT_REVIEWER_REQUIRED",lambda:self.command("REVIEW",{"decision":"APPROVED","reason":"x"},actor=assigned))

    def test_previous_assignee_cannot_approve_after_unassignment(self):
        assigned=Principal(principal_id="assigned",roles={Role.AUTHOR,Role.REVIEWER},asset_ids={ASSET})
        self.service.directory=lambda _:assigned
        self.case=self.command("UPDATE",dict(DRAFT,assigned_engineer="assigned"))
        self.case=self.command("NOTE",{"text":"My work"},actor=assigned)
        self.case=self.command("UPDATE",DRAFT,request="unassign")
        self.case=self.command("SUBMIT")
        self.assert_code("INDEPENDENT_REVIEWER_REQUIRED",lambda:self.command("REVIEW",{"decision":"APPROVED","reason":"x"},actor=assigned))

    def test_review_without_submit_or_reason_rejected(self):
        self.assert_code("INVALID_TRANSITION",lambda:self.command("REVIEW",{"decision":"APPROVED","reason":"x"},actor=REVIEWER))
        self.case=self.command("SUBMIT")
        self.assert_code("REVIEW_RATIONALE_REQUIRED",lambda:self.command("REVIEW",{"decision":"APPROVED","reason":" "},actor=REVIEWER))

    def test_notes_plain_text_attributed_and_bounded(self):
        self.case=self.command("NOTE",{"text":"<script>alert('untrusted')</script>"})
        self.assertEqual(self.case.notes[0].actor,AUTHOR.principal_id)
        self.assertEqual(self.case.notes[0].text,"<script>alert('untrusted')</script>")
        with self.assertRaises(ValidationError):self.command("NOTE",{"text":"x"*12001},request="large")

    def test_frozen_reference_and_duplicate(self):
        self.case=self.command("LINK",{"kind":"ASSET","record_id":"record:synthetic","mode":"FROZEN_SNAPSHOT"})
        ref=self.case.evidence[0]
        self.assertEqual(ref.freshness,"UNKNOWN")
        self.assertEqual(self.service.live_evidence(AUTHOR,self.case.case_id,ref.reference_id),ref)
        with self.assertRaises(ValidationError):ref.freshness="CURRENT"
        self.assert_code("DUPLICATE_EVIDENCE",lambda:self.command("LINK",{"kind":"ASSET","record_id":"record:synthetic","mode":"FROZEN_SNAPSHOT"},request="link-2"))

    def test_live_reference_rechecks_missing(self):
        self.case=self.command("LINK",{"kind":"ASSET","record_id":"record:synthetic","mode":"LIVE_REFERENCE"})
        self.assertIsNone(self.case.evidence[0].snapshot)
        self.catalog.resolve=Mock(side_effect=EngineeringError("EVIDENCE_NOT_FOUND",404))
        self.assert_code("EVIDENCE_NOT_FOUND",lambda:self.service.live_evidence(AUTHOR,self.case.case_id,self.case.evidence[0].reference_id))

    def test_unknown_unapproved_and_cross_asset_reference(self):
        self.assert_code("EVIDENCE_NOT_FOUND",lambda:self.command("LINK",{"kind":"ASSET","record_id":"missing","mode":"FROZEN_SNAPSHOT"}))
        self.assert_code("NO_APPROVED_EVIDENCE",lambda:self.command("LINK",{"kind":"CONDITION","record_id":"record:synthetic","mode":"FROZEN_SNAPSHOT"}))
        original=self.catalog.resolve
        self.catalog.resolve=lambda *args:original(*args).model_copy(update={"canonical_asset_id":OTHER})
        self.assert_code("EVIDENCE_IDENTITY_INVALID",lambda:self.command("LINK",{"kind":"ASSET","record_id":"record:synthetic","mode":"FROZEN_SNAPSHOT"}))

    def test_data_trust_partial_unknown_snapshot(self):
        self.case=self.command("LINK",{"kind":"DATA_TRUST","record_id":"record:synthetic","mode":"FROZEN_SNAPSHOT"})
        self.assertEqual(self.case.evidence[0].snapshot.availability,"PARTIAL")
        self.assertEqual(self.case.evidence[0].freshness,"UNKNOWN")

    def test_invalid_reference_quality_freshness_status_url(self):
        ref=self.catalog.resolve(ASSET,EvidenceKind.ASSET,"record:synthetic","FROZEN_SNAPSHOT",AUTHOR.principal_id,NOW)
        for extra in ({"freshness":"HEALTHY"},{"identity_status":"AMBIGUOUS"},{"quality_good":"true"},{"record_id":"https://source.invalid/data"},{"snapshot":{"label":"x","raw_vendor_payload":{}}}):
            with self.subTest(extra=extra),self.assertRaises(ValidationError):EvidenceReference.model_validate(dict(ref.model_dump(),**extra))

    def test_pagination_and_filter_bounds(self):
        for n in range(3):self.service.command(AUTHOR,"CREATE",dict(DRAFT,title=str(n)),f"create-{n+2}")
        page=self.service.list(AUTHOR,offset=1,limit=2,status="DRAFT",asset_id=ASSET)
        self.assertEqual((page["total"],len(page["items"]),page["has_more"]),(4,2,True))
        self.assertEqual(self.service.list(REVIEWER)["total"],4)
        self.assert_code("INVALID_PAGINATION",lambda:self.service.list(AUTHOR,limit=101))

    def test_transaction_rolls_back_case_audit_and_receipt(self):
        original=self.repo.save
        def broken(*args):
            original(*args)
            raise EngineeringError("FIXTURE_TRANSACTION_FAILURE",503)
        self.repo.save=broken
        self.assert_code("FIXTURE_TRANSACTION_FAILURE",lambda:self.command("NOTE",{"text":"should rollback"}))
        self.assertEqual(self.service.get(AUTHOR,self.case.case_id).revision,1)
        with self.engine.connect() as c:
            self.assertEqual(len(c.execute(select(EventRow)).all()),1)
            self.assertEqual(len(c.execute(select(ReceiptRow)).all()),1)

    def test_database_failure_sanitized(self):
        EngineeringBase.metadata.drop_all(self.engine)
        self.assert_code("PERSISTENCE_UNAVAILABLE",lambda:self.service.list(AUTHOR))
        response=self.client.get("/v1/engineering/cases")
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json(),{"detail":{"code":"PERSISTENCE_UNAVAILABLE"}})

    def test_default_disabled_and_missing_adapter_routes(self):
        self.assertEqual(build_router(self.service).routes,[])
        self.assertEqual(build_router(self.service,enabled=True).routes,[])
        self.service.enabled=False
        self.assert_code("FEATURE_DISABLED",lambda:self.service.get(AUTHOR,self.case.case_id))
        self.assertEqual(build_router(self.service,enabled=True,trusted_principal_dependency=lambda:AUTHOR).routes,[])

    def test_production_factory_never_exposes_engineering_writes(self):
        with patch.dict(os.environ,{"NADI_ENGINEERING_WORKSPACE_ENABLED":"true","X_USER":"spoof"}):
            self.assertFalse(any(getattr(r,"path","").startswith("/v1/engineering") for r in create_app().routes))

    def test_api_workflow_and_serialization(self):
        response=self.client.post("/v1/engineering/cases",json={"request_id":"api-create","draft":DRAFT})
        self.assertEqual(response.status_code,201,response.text)
        case=response.json()
        self.assertEqual(case["created_by"],AUTHOR.principal_id)
        submit=self.client.post(f"/v1/engineering/cases/{case['case_id']}/submit",json={"request_id":"api-submit","expected_revision":1})
        self.assertEqual(submit.status_code,200,submit.text)
        self.actor=REVIEWER
        review=self.client.post(f"/v1/engineering/cases/{case['case_id']}/review",json={"request_id":"api-review","expected_revision":2,"decision":"APPROVED","reason":"Synthetic review"})
        self.assertEqual(review.status_code,200,review.text)
        self.assertEqual(review.json()["status"],"APPROVED")
        self.assertEqual(self.client.get(f"/v1/engineering/cases/{case['case_id']}/history").status_code,200)

    def test_api_reviewer_impersonation_and_bad_filters(self):
        url=f"/v1/engineering/cases/{self.case.case_id}/review"
        body={"request_id":"spoof","expected_revision":1,"decision":"APPROVED","reason":"x","reviewer":REVIEWER.principal_id}
        self.assertEqual(self.client.post(url,json=body,headers={"X-User":REVIEWER.principal_id}).status_code,422)
        body.pop("reviewer")
        self.assertEqual(self.client.post(url,json=body,headers={"X-User":REVIEWER.principal_id}).status_code,403)
        self.assertEqual(self.client.get("/v1/engineering/cases?limit=10001").status_code,422)
        self.assertEqual(self.client.get("/v1/engineering/cases?status=HEALTHY").status_code,422)

    def test_case_json_schema_matches_model(self):
        from jsonschema import Draft202012Validator, FormatChecker
        schema=json.loads((ROOT.parent/"reliability-data-contracts/schemas/engineering-case.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema,format_checker=FormatChecker()).validate(self.case.model_dump(mode="json"))

    def test_no_source_or_admin_imports_and_metadata_separation(self):
        from src.repositories.database import Base
        self.assertNotIn("engineering_case",Base.metadata.tables)
        for relative in ("src/api/engineering.py","src/services/engineering.py","src/services/engineering_evidence.py","src/repositories/engineering.py"):
            source=(ROOT/relative).read_text()
            for forbidden in ("PiClient","PI_PASSWORD","MAXIMO_READ_ONLY_TOKEN","RELIABILITY_MART_ADMIN_DATABASE_URL","get_database(","requests.get"):
                self.assertNotIn(forbidden,source)


class CanonicalEvidenceTest(unittest.TestCase):
    def setUp(self):
        # Existing fully synthetic VERIFIED selection -> Collector fixture -> Mart.
        from test_condition_evidence import ConditionProjectionTest
        self.fixture=ConditionProjectionTest();self.fixture.setUp()
        self.fixture.project(self.fixture.source_document())
        from src.services.engineering_evidence import LocalEvidenceCatalog
        from src.domain.condition_evidence import FreshnessPolicy
        self.catalog=LocalEvidenceCatalog(self.fixture.reader(),policy=FreshnessPolicy(),clock=lambda:self.fixture.read().items[0].evidence.collected_at)
        from test_asset_af_mapping_admin import ASSET_ID
        self.asset=ASSET_ID

    def tearDown(self):self.fixture.tearDown()

    def reference(self,kind="CONDITION",record="synthetic-current",mode="FROZEN_SNAPSHOT"):
        return self.catalog.resolve(self.asset,EvidenceKind(kind),record,mode,AUTHOR.principal_id,NOW)

    def test_condition_preserves_unit_type_quality_timestamp_unknown(self):
        ref=self.reference();e=ref.snapshot.condition
        self.assertEqual((e.value,e.value_type,e.unit),(12.5,"NUMERIC","A"))
        self.assertEqual(ref.source_timestamp,e.source_timestamp)
        self.assertEqual(ref.freshness,"UNKNOWN")
        self.assertEqual(ref.quality_good,e.quality_good)
        self.assertEqual(ref.signal_approval,"APPROVED")

    def test_bad_quality_null_text_and_stale_preserved(self):
        from src.domain.condition_evidence import FreshnessPolicy
        from src.services.engineering_evidence import LocalEvidenceCatalog
        from test_condition_evidence import NOW as SOURCE_NOW
        for value_type in ("TEXT","DIGITAL_STATE","BOOLEAN","NULL","BAD_QUALITY","STALE"):
            with self.subTest(value_type=value_type):
                # Disposable fresh fixture avoids same-timestamp/payload conflicts.
                self.fixture.tearDown();self.fixture.setUp()
                variant_values={"TEXT":{"Value":"Synthetic text"},"DIGITAL_STATE":{"Value":{"Name":"Synthetic state","Value":2,"IsSystem":False}},"BOOLEAN":{"Value":True},"NULL":{"Value":None},"BAD_QUALITY":{"Good":False},"STALE":{"Timestamp":"1970-01-01T00:00:00Z"}}
                variants={"motor_current":variant_values[value_type]}
                self.fixture.project(self.fixture.source_document(variants))
                self.catalog=LocalEvidenceCatalog(self.fixture.reader(),policy=FreshnessPolicy(source_max_age_seconds=60),clock=lambda:SOURCE_NOW+timedelta(minutes=2))
                ref=self.reference()
                self.assertEqual(ref.freshness,"STALE")
                if value_type=="NULL":self.assertIsNone(ref.snapshot.condition.value)
                if value_type=="BAD_QUALITY":self.assertEqual(ref.snapshot.condition.evidence_status,"BAD_QUALITY")

    def test_retired_unapproved_ambiguous_missing_and_rcfa_rejected(self):
        from src.repositories.condition_models import ConditionSignalSelectionMart
        with self.assertRaises(EngineeringError):self.reference(record="unapproved")
        with self.assertRaises(EngineeringError):self.reference(kind="RCFA",record="rcfa:synthetic")
        self.fixture.store.retire_signal("synthetic-current")
        with self.assertRaises(EngineeringError):self.reference()

    def test_no_arbitrary_snapshot_vendor_fields_or_mismatched_unit(self):
        ref=self.reference().model_dump(mode="json")
        ref["unit"]="invented-unit"
        with self.assertRaises(ValidationError):EvidenceReference.model_validate(ref)

    def test_immutable_snapshot_survives_missing_live_record(self):
        ref=self.reference()
        self.fixture.store.retire_signal("synthetic-current")
        self.assertEqual(ref.snapshot.condition.value,12.5)
        with self.assertRaises(EngineeringError):self.reference(mode="LIVE_REFERENCE")


@unittest.skipUnless(os.getenv("NADI_ENGINEERING_TEST_DSN"),"disposable PostgreSQL engineering fixture not configured")
class EngineeringPostgresTest(EngineeringTest):
    def setUp(self):
        super().setUp()
        url=make_url(os.environ["NADI_ENGINEERING_TEST_DSN"])
        if url.host not in {"localhost","127.0.0.1"} or not url.database.endswith("_test"):
            raise RuntimeError("engineering fixture must be disposable local *_test")
        self.engine.dispose()
        self.engine=create_engine(url)
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public")
            c.exec_driver_sql("CREATE TABLE synthetic_existing_facts(id text PRIMARY KEY)")
            c.exec_driver_sql("INSERT INTO synthetic_existing_facts VALUES ('preserved')")
            c.exec_driver_sql((ROOT/"application-migrations/002_engineering_workspace.sql").read_text())
        self.repo.engine=self.engine
        self.case=self.service.command(AUTHOR,"CREATE",DRAFT,"create-1")

    def test_migration_preserves_existing_application_tables(self):
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(text("SELECT count(*) FROM synthetic_existing_facts")),1)

    def test_schema_compatible_with_metadata(self):
        from sqlalchemy import inspect
        tables=inspect(self.engine)
        for table in EngineeringBase.metadata.sorted_tables:
            self.assertEqual({c.name for c in table.columns},{c["name"] for c in tables.get_columns(table.name)})


    def test_concurrent_edit_compare_and_swap(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier = Barrier(2)
        original_get = self.repo.get
        def simultaneous_read(connection, case_id):
            case = original_get(connection, case_id)
            barrier.wait(timeout=10)
            return case
        self.repo.get = simultaneous_read
        def edit(number):
            try:
                return self.service.command(AUTHOR, "NOTE", {"text": f"Concurrent synthetic note {number}"},
                    f"race-{number}", case_id=self.case.case_id, expected_revision=1).revision
            except EngineeringError as exc:
                return exc.code
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(edit, (1, 2)))
        finally:
            self.repo.get = original_get
        self.assertCountEqual(outcomes, [2, "REVISION_CONFLICT"])
        persisted = self.service.get(AUTHOR, self.case.case_id)
        self.assertEqual((persisted.revision, len(persisted.notes)), (2, 1))
        with self.engine.connect() as connection:
            self.assertEqual(len(connection.execute(select(EventRow)).all()), 2)
            self.assertEqual(len(connection.execute(select(ReceiptRow)).all()), 2)

    def test_candidate_writer_cannot_tamper_with_audit(self):
        from sqlalchemy.exc import DBAPIError
        with self.engine.begin() as c:
            if not c.scalar(text("SELECT 1 FROM pg_roles WHERE rolname='engineering_fixture_writer'")):
                c.exec_driver_sql("CREATE ROLE engineering_fixture_writer NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS")
            c.exec_driver_sql("GRANT USAGE ON SCHEMA public TO engineering_fixture_writer")
            c.exec_driver_sql("GRANT SELECT,INSERT,UPDATE ON engineering_case TO engineering_fixture_writer")
            c.exec_driver_sql("GRANT SELECT,INSERT ON engineering_case_event,engineering_case_receipt TO engineering_fixture_writer")
        for sql in ("UPDATE engineering_case_event SET revision=99", "DELETE FROM engineering_case_event", "TRUNCATE engineering_case_event", "ALTER TABLE engineering_case ADD COLUMN illicit text"):
            with self.subTest(sql=sql),self.engine.connect() as c:
                c.exec_driver_sql("SET ROLE engineering_fixture_writer")
                with self.assertRaises(DBAPIError):c.exec_driver_sql(sql)
                c.rollback()
                c.exec_driver_sql("RESET ROLE")
        with self.engine.begin() as c:
            c.exec_driver_sql("SET LOCAL ROLE engineering_fixture_writer")
            self.assertEqual(c.scalar(text("SELECT count(*) FROM engineering_case_event")),1)


class EngineeringFixtureContractTest(unittest.TestCase):
    def test_ui_synthetic_documents_validate_python_and_json_contract(self):
        from jsonschema import Draft202012Validator, FormatChecker
        fixture=json.loads((ROOT/"web/fixtures/engineering-workspace.json").read_text())
        schema=json.loads((ROOT.parent/"reliability-data-contracts/schemas/engineering-case.schema.json").read_text())
        self.assertTrue(fixture["synthetic"])
        for document in fixture["cases"]:
            EngineeringCase.model_validate(document)
            Draft202012Validator(schema,format_checker=FormatChecker()).validate(document)
        EvidenceReference.model_validate(fixture["available_evidence"])

    def test_generated_json_contract_has_no_model_drift(self):
        schema=json.loads((ROOT.parent/"reliability-data-contracts/schemas/engineering-case.schema.json").read_text())
        generated=EngineeringCase.model_json_schema()
        self.assertEqual({key:value for key,value in schema.items() if key not in {"$schema","$id"}}, generated)

    def test_auth_disabled_nav_and_demo_development_only(self):
        source=(ROOT/"web/lib/engineering.ts").read_text()
        self.assertIn('environment.NODE_ENV === "development"',source)
        self.assertIn('environment.NADI_ENGINEERING_WORKSPACE_ENABLED !== "true"',source)
        view=(ROOT/"web/components/EngineeringWorkspace.tsx").read_text()
        self.assertIn('SYNTHETIC LOCAL DEMO',view)
        self.assertNotIn('dangerouslySetInnerHTML',view)
        self.assertNotIn('fetch(',view)
