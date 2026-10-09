"""Bundle compatibility, isolated PostgreSQL concurrency and trusted-session E2E."""

import json, os, unittest
from pathlib import Path
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
from sqlalchemy import create_engine, select, text, inspect
from sqlalchemy.engine import make_url
from src.domain.engineering import Principal, Role, EngineeringError
from src.domain.manual_inspection import ManualInspection
from src.domain.recommendation import Recommendation
from src.domain.maintenance_context import ExistingWorkOrderReference
from src.repositories.application_boundary import ApplicationStore
from src.repositories.human_records import (
    HumanRecordBase,
    HumanRecordRepository,
    RecordRow,
    RevisionRow,
    HumanReceiptRow,
)
from src.services.application_identity import SessionAuthority, IdentityBase, SessionRow
from src.services.human_records import InspectionService
from src.api.human_records import build_inspection_router, build_recommendation_router
import test_manual_inspection as manual
import test_recommendation as recommendation
import test_application_identity as identity

ROOT = Path(__file__).resolve().parents[1]


class BundleContractTest(unittest.TestCase):
    def test_models_and_generated_schemas_have_no_drift(self):
        for model, filename in (
            (ManualInspection, "manual-inspection.schema.json"),
            (Recommendation, "engineering-recommendation.schema.json"),
            (ExistingWorkOrderReference, "existing-work-order-reference.schema.json"),
        ):
            actual = json.loads(
                (
                    ROOT.parent / "reliability-data-contracts/schemas" / filename
                ).read_text()
            )
            Draft202012Validator.check_schema(actual)
            generated = model.model_json_schema()
            for key, value in generated.items():
                self.assertEqual(actual[key], value, filename + ":" + key)

    def test_positive_and_negative_complete_contracts(self):
        for fixture, filename in (
            (manual.InspectionTest(), "manual-inspection.schema.json"),
            (
                recommendation.RecommendationTest(),
                "engineering-recommendation.schema.json",
            ),
        ):
            fixture.setUp()
            try:
                document = fixture.create().model_dump(mode="json")
                validator = Draft202012Validator(
                    json.loads(
                        (
                            ROOT.parent
                            / "reliability-data-contracts/schemas"
                            / filename
                        ).read_text()
                    ),
                    format_checker=FormatChecker(),
                )
                validator.validate(document)
                for extra in (
                    {"health_score": 100},
                    {"revision": True},
                    {"status": "HEALTHY"},
                    (
                        {"observations": [" "]}
                        if "observations" in document
                        else {"rationale": " "}
                    ),
                ):
                    self.assertTrue(
                        list(validator.iter_errors({**document, **extra})), extra
                    )
            finally:
                fixture.tearDown()

    def test_method_extension_keys_and_values_match_domain_constraints(self):
        fixture = manual.InspectionTest()
        fixture.setUp()
        try:
            document = fixture.create().model_dump(mode="json")
            validator = Draft202012Validator(
                json.loads(
                    (ROOT.parent / "reliability-data-contracts/schemas/manual-inspection.schema.json").read_text()
                ),
                format_checker=FormatChecker(),
            )
            # Preserve allowed scalar types, empty extensions and exact limits.
            for extension in (
                {},
                {"sample_id": "synthetic", "value": 0, "decimal": 1.25, "flag": False, "unknown": None},
                {"A" + "a" * 79: "x" * 2000},
                {f"field_{i}": None for i in range(20)},
            ):
                with self.subTest(valid_extension=extension):
                    candidate = {**document, "method_extension": extension}
                    validator.validate(candidate)
                    self.assertEqual(
                        ManualInspection.model_validate(candidate).method_extension,
                        extension,
                    )
            # Invalid keys must not bypass scalar validation via additionalProperties.
            for extension in (
                {"unsafe-key": 1},
                {"unsafe-key": {"nested": "bypass"}},
                {"": None},
                {"1field": "invalid"},
                {"white space": True},
                {"A" + "a" * 80: 0},
                {"sample_id": {"nested": "invalid"}},
                {"sample_id": [1]},
                {"sample_id": "x" * 2001},
                {f"field_{i}": None for i in range(21)},
            ):
                with self.subTest(invalid_extension=extension):
                    candidate = {**document, "method_extension": extension}
                    self.assertTrue(list(validator.iter_errors(candidate)))
                    with self.assertRaises(ValidationError):
                        ManualInspection.model_validate(candidate)
        finally:
            fixture.tearDown()

    def test_public_routes_unmounted_and_candidate_metadata_isolated(self):
        from src.api.app import create_app
        from src.repositories.database import Base

        with patch.dict(
            os.environ,
            {
                "NADI_ENGINEERING_WORKSPACE_ENABLED": "true",
                "NADI_ENGINEERING_DEMO_ENABLED": "true",
            },
        ):
            self.assertFalse(
                any(
                    getattr(r, "path", "").startswith("/v1/engineering")
                    for r in create_app().routes
                )
            )
        self.assertFalse(
            set(Base.metadata.tables) & set(HumanRecordBase.metadata.tables)
        )
        self.assertFalse(set(Base.metadata.tables) & set(IdentityBase.metadata.tables))

    def test_human_paths_have_no_source_or_admin_boundary(self):
        for file in (
            "src/services/human_records.py",
            "src/services/recommendation.py",
            "src/services/application_evidence.py",
            "src/services/maximo_intelligence.py",
            "src/api/human_records.py",
            "src/repositories/human_records.py",
            "src/services/application_identity.py",
        ):
            content = (ROOT / file).read_text()
            for forbidden in (
                "PiClient",
                "OslcClient",
                "PI_PASSWORD",
                "MAXIMO_READ_ONLY_TOKEN",
                "RELIABILITY_MART_ADMIN_DATABASE_URL",
                "requests.get",
                "get_database(",
                "os.environ",
            ):
                self.assertNotIn(forbidden, content, file)

    def test_trusted_session_to_inspection_and_revoked_mutation_denial(self):
        fixture = manual.InspectionTest()
        fixture.setUp()
        try:
            IdentityBase.metadata.create_all(fixture.engine)
            provider = identity.FixtureProvider()
            authority = SessionAuthority(
                ApplicationStore(
                    fixture.engine, expected_database="fixture_test", isolated=True
                ),
                provider,
                origins={"https://nadi.example.invalid"},
                idle_seconds=300,
                absolute_seconds=3600,
                clock=lambda: manual.NOW,
            )
            token, csrf = authority.establish("author")
            app = FastAPI()
            app.include_router(
                build_inspection_router(
                    fixture.service,
                    enabled=True,
                    trusted_principal_dependency=authority.dependency(),
                )
            )
            with TestClient(app, base_url="https://nadi.example.invalid") as client:
                client.cookies.set(authority.COOKIE, token)
                headers = {
                    "Origin": "https://nadi.example.invalid",
                    "X-CSRF-Token": csrf,
                    "Content-Type": "application/json",
                    "X-Actor": "reviewer",
                }
                r = client.post(
                    "/v1/engineering/inspections",
                    headers=headers,
                    json={"request_id": "session-create", "draft": fixture.draft},
                )
                self.assertEqual(r.status_code, 201, r.text)
                self.assertEqual(r.json()["created_by"], "author")
                record = r.json()
                authority.revoke(fixture.author, token)
                r = client.post(
                    f"/v1/engineering/inspections/{record['record_id']}/submit",
                    headers=headers,
                    json={"request_id": "revoked-submit", "expected_revision": 1},
                )
                self.assertEqual(r.status_code, 401)
                self.assertEqual(
                    fixture.service.get(fixture.author, record["record_id"]).revision, 1
                )
        finally:
            fixture.tearDown()


@unittest.skipUnless(
    os.getenv("NADI_APPLICATION_TEST_DSN"),
    "isolated local application PostgreSQL fixture not configured",
)
class ApplicationPostgresTest(unittest.TestCase):
    def setUp(self):
        url = make_url(os.environ["NADI_APPLICATION_TEST_DSN"])
        if url.host not in {"127.0.0.1", "localhost"} or not url.database.endswith(
            "_test"
        ):
            raise RuntimeError("disposable local *_test only")
        self.engine = create_engine(url)
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public")
            c.exec_driver_sql(
                "CREATE TABLE synthetic_existing_facts(id text PRIMARY KEY); INSERT INTO synthetic_existing_facts VALUES ('preserved')"
            )
            for migration in (
                "002_engineering_workspace.sql",
                "003_application_identity.sql",
                "004_human_records.sql",
            ):
                c.exec_driver_sql(
                    (ROOT / "application-migrations" / migration).read_text()
                )
        self.store = ApplicationStore(
            self.engine, expected_database=url.database, isolated=True
        )
        self.repo = HumanRecordRepository(self.store)
        self.service = InspectionService(
            self.repo, manual.FixtureCatalog(), enabled=True, clock=lambda: manual.NOW
        )
        self.actor = Principal(
            principal_id="author", roles={Role.AUTHOR}, asset_ids={manual.ASSET}
        )
        self.draft = dict(
            canonical_asset_id=manual.ASSET,
            method="VIBRATION",
            method_version="proposal-1",
            inspector_ref="author",
        )
        self.row = self.service.command(self.actor, "CREATE", self.draft, "create")

    def tearDown(self):
        self.engine.dispose()

    def test_application_migrations_preserve_facts_and_match_models(self):
        with self.engine.connect() as c:
            self.assertEqual(
                c.scalar(text("SELECT count(*) FROM synthetic_existing_facts")), 1
            )
        for metadata in (HumanRecordBase.metadata, IdentityBase.metadata):
            for table in metadata.sorted_tables:
                self.assertEqual(
                    set(table.columns.keys()),
                    {x["name"] for x in inspect(self.engine).get_columns(table.name)},
                )
        # The candidate files intentionally fail on re-execution: deployment runner/ledger review is still a gate.
        with self.assertRaises(Exception):
            with self.engine.begin() as c:
                c.exec_driver_sql(
                    (ROOT / "application-migrations/004_human_records.sql").read_text()
                )
        self.assertEqual(self.service.get(self.actor, self.row.record_id).revision, 1)

    def test_concurrent_edits_have_one_winner_and_one_atomic_audit(self):
        barrier = Barrier(2)
        original = self.repo.get

        def read(c, kind, record_id):
            row = original(c, kind, record_id)
            barrier.wait(timeout=10)
            return row

        self.repo.get = read

        def change(i):
            try:
                return self.service.command(
                    self.actor,
                    "UPDATE",
                    {**self.draft, "operating_context": str(i)},
                    "edit" + str(i),
                    record_id=self.row.record_id,
                    expected_revision=1,
                ).revision
            except EngineeringError as error:
                return error.code

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(change, [1, 2]))
        self.repo.get = original
        self.assertCountEqual(results, [2, "REVISION_CONFLICT"])
        self.assertEqual(len(self.service.history(self.actor, self.row.record_id)), 2)
        with self.engine.connect() as c:
            self.assertEqual(
                c.scalar(text("SELECT count(*) FROM nadi_human_record_receipt")), 2
            )

    def test_duplicate_request_has_one_record_and_receipt(self):
        barrier = Barrier(2)
        original = self.repo.receipt

        def receipt(c, actor, request, fingerprint):
            row = original(c, actor, request, fingerprint)
            barrier.wait(timeout=10)
            return row

        self.repo.receipt = receipt

        def create(i):
            try:
                return self.service.command(
                    self.actor, "CREATE", self.draft, "same-create"
                ).revision
            except EngineeringError as error:
                return error.code

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(create, [1, 2]))
        self.assertCountEqual(results, [1, "REQUEST_CONFLICT"])
        self.repo.receipt = original
        with self.engine.connect() as c:
            self.assertEqual(
                c.scalar(text("SELECT count(*) FROM nadi_human_record")), 2
            )
            self.assertEqual(
                c.scalar(text("SELECT count(*) FROM nadi_human_record_revision")), 2
            )

    def test_append_only_writer_and_select_only_reader_grants(self):
        with self.engine.begin() as c:
            c.exec_driver_sql(
                "DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='bundle_fixture_writer') THEN CREATE ROLE bundle_fixture_writer; END IF; IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='bundle_fixture_reader') THEN CREATE ROLE bundle_fixture_reader; END IF; END $$"
            )
            c.exec_driver_sql(
                "GRANT USAGE ON SCHEMA public TO bundle_fixture_writer,bundle_fixture_reader"
            )
            c.exec_driver_sql(
                "GRANT SELECT,INSERT,UPDATE ON nadi_human_record,nadi_application_session TO bundle_fixture_writer"
            )
            c.exec_driver_sql(
                "GRANT SELECT,INSERT ON nadi_human_record_revision,nadi_human_record_receipt,nadi_security_activity TO bundle_fixture_writer"
            )
            c.exec_driver_sql(
                "GRANT SELECT ON ALL TABLES IN SCHEMA public TO bundle_fixture_reader"
            )
        for role, sql in (
            ("bundle_fixture_reader", "UPDATE nadi_human_record SET revision=9"),
            ("bundle_fixture_writer", "DELETE FROM nadi_human_record_revision"),
            (
                "bundle_fixture_writer",
                "UPDATE nadi_human_record_revision SET action='forged'",
            ),
            ("bundle_fixture_writer", "TRUNCATE nadi_security_activity"),
            ("bundle_fixture_writer", "CREATE TABLE forged(id int)"),
        ):
            with self.assertRaises(Exception):
                with self.engine.begin() as c:
                    c.exec_driver_sql("SET LOCAL ROLE " + role)
                    c.exec_driver_sql(sql)
        with self.engine.begin() as c:
            c.exec_driver_sql("SET LOCAL ROLE bundle_fixture_reader")
            self.assertEqual(
                c.scalar(text("SELECT count(*) FROM nadi_human_record")), 1
            )

    def test_session_revocation_serializes_after_inflight_command(self):
        provider = identity.FixtureProvider()
        authority = SessionAuthority(
            self.store,
            provider,
            origins={"https://nadi.example.invalid"},
            idle_seconds=300,
            absolute_seconds=3600,
            clock=lambda: manual.NOW,
        )
        token, csrf = authority.establish("author")
        leased = Event()
        release = Event()
        finished = Event()

        def operation():
            with authority.lease(
                token,
                method="POST",
                origin="https://nadi.example.invalid",
                csrf=csrf,
                content_type="application/json",
            ) as principal:
                leased.set()
                release.wait(10)
                self.service.command(
                    principal,
                    "UPDATE",
                    {**self.draft, "operating_context": "inflight"},
                    "inflight",
                    record_id=self.row.record_id,
                    expected_revision=1,
                )

        def revoke():
            authority.revoke(self.actor, token)
            finished.set()

        with ThreadPoolExecutor(max_workers=2) as pool:
            op = pool.submit(operation)
            self.assertTrue(leased.wait(10))
            rev = pool.submit(revoke)
            self.assertFalse(finished.wait(0.1))
            release.set()
            op.result(10)
            rev.result(10)
        with self.assertRaises(EngineeringError):
            with authority.lease(token):
                self.fail("revoked lease accepted")
        self.assertEqual(self.service.get(self.actor, self.row.record_id).revision, 2)
