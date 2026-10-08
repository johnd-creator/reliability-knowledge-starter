"""Isolated human inspection lifecycle and security-negative contracts."""

import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from pydantic import ValidationError
from sqlalchemy import create_engine, select, func
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.domain.engineering import Principal, Role, EngineeringError
from src.domain.manual_inspection import (
    InspectionDraft,
    ManualMeasurement,
    AttachmentMetadata,
    METHOD_PROPOSALS,
)
from src.repositories.application_boundary import ApplicationStore
from src.repositories.human_records import (
    HumanRecordBase,
    HumanRecordRepository,
    RecordRow,
    RevisionRow,
    HumanReceiptRow,
)
from src.services.human_records import InspectionService
from src.api.human_records import build_inspection_router

ASSET = "asset:SYNTHETIC:A"
NOW = datetime(2026, 10, 9, tzinfo=timezone.utc)


class FixtureCatalog:
    def registered(self, asset):
        return asset == ASSET

    def validate_case(self, actor, asset, case):
        if asset != ASSET or case != "case:SYNTHETIC:ONE":
            raise EngineeringError("CASE_NOT_ACCESSIBLE", 422)


class InspectionTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
        )
        HumanRecordBase.metadata.create_all(self.engine)
        self.repo = HumanRecordRepository(
            ApplicationStore(
                self.engine, expected_database="fixture_test", isolated=True
            )
        )
        self.catalog = FixtureCatalog()
        self.now = NOW
        self.service = InspectionService(
            self.repo, self.catalog, enabled=True, clock=lambda: self.now
        )
        self.author = Principal(
            principal_id="author", roles={Role.AUTHOR}, asset_ids={ASSET}
        )
        self.reviewer = Principal(
            principal_id="reviewer", roles={Role.REVIEWER}, asset_ids={ASSET}
        )
        self.foreign = Principal(
            principal_id="foreign", roles={Role.AUTHOR}, asset_ids={"asset:SYNTHETIC:B"}
        )
        self.draft = dict(
            canonical_asset_id=ASSET,
            method="VIBRATION",
            method_version="proposal-1",
            inspector_ref="author",
            inspected_at=NOW.isoformat(),
            measurements=[
                dict(
                    quantity="velocity",
                    value=1.2,
                    unit="mm/s",
                    measured_at=NOW.isoformat(),
                )
            ],
            observations=["Human observation"],
            interpretations=["Unverified hypothesis"],
            case_refs=["case:SYNTHETIC:ONE"],
        )

    def tearDown(self):
        self.engine.dispose()

    def create(self, request="create"):
        return self.service.command(self.author, "CREATE", self.draft, request)

    def change(self, row, action, payload, actor=None, request=None):
        self.now += timedelta(seconds=1)
        return self.service.command(
            actor or self.author,
            action,
            payload,
            request or action.lower(),
            record_id=row.record_id,
            expected_revision=row.revision,
        )

    def code(self, code, fn):
        with self.assertRaises(EngineeringError) as ctx:
            fn()
        self.assertEqual(ctx.exception.code, code)

    def test_original_values_units_null_and_quality(self):
        for value in (None, 0, 1.2, "trace", True):
            m = ManualMeasurement(
                quantity="reported quantity", value=value, unit="original"
            )
            self.assertEqual(m.value, value)
            self.assertEqual(type(m.value), type(value))
            self.assertEqual(m.quality, "UNKNOWN")
        row = self.create()
        self.assertEqual(row.assessment, "NOT_ASSESSED")
        self.assertEqual(row.field_approval, "ENGINEER_FIELDS_PENDING")

    def test_nonfinite_and_extra_fields_rejected(self):
        for value in (float("nan"), float("inf")):
            with self.assertRaises(ValidationError):
                ManualMeasurement(quantity="x", value=value)
        with self.assertRaises(ValidationError):
            InspectionDraft(**self.draft, health_score=100)

    def test_method_extensions_are_proposals_not_thresholds(self):
        self.assertEqual(len(METHOD_PROPOSALS), 6)
        for method in METHOD_PROPOSALS:
            draft = InspectionDraft(
                **{
                    **self.draft,
                    "method": method,
                    "method_extension": {"sample_id": "synthetic"},
                }
            )
            self.assertEqual(draft.method_extension["sample_id"], "synthetic")
        with self.assertRaises(ValidationError):
            InspectionDraft(**{**self.draft, "method_extension": {"unsafe-key": 1}})

    def test_workflow_independent_review_and_immutable_history(self):
        row = self.create()
        submitted = self.change(row, "SUBMIT", {})
        reviewed = self.change(
            submitted,
            "REVIEW",
            {"decision": "APPROVED", "reason": "Record checked; no health claim"},
            self.reviewer,
        )
        self.assertEqual(reviewed.status, "APPROVED")
        self.assertEqual(reviewed.approval_scope, "NADI_RECORD_REVIEW_ONLY")
        history = self.service.history(self.author, row.record_id)
        self.assertEqual([x["revision"] for x in history], [1, 2, 3])
        self.assertEqual(history[0]["snapshot"]["status"], "DRAFT")
        self.assertEqual(history[2]["actor"], "reviewer")

    def test_creator_even_with_reviewer_role_cannot_review(self):
        submitted = self.change(self.create(), "SUBMIT", {})
        actor = self.author.model_copy(
            update={"roles": frozenset({Role.AUTHOR, Role.REVIEWER})}
        )
        self.code(
            "INDEPENDENT_REVIEWER_REQUIRED",
            lambda: self.change(
                submitted, "REVIEW", {"decision": "APPROVED", "reason": "x"}, actor
            ),
        )

    def test_reject_revise_approve_reopen(self):
        row = self.change(self.create(), "SUBMIT", {})
        row = self.change(
            row, "REVIEW", {"decision": "REJECTED", "reason": "Clarify"}, self.reviewer
        )
        row = self.change(row, "REVISE", {"reason": "Correction"})
        row = self.change(row, "SUBMIT", {}, request="submit2")
        row = self.change(
            row,
            "REVIEW",
            {"decision": "APPROVED", "reason": "Checked"},
            self.reviewer,
            request="review2",
        )
        row = self.change(row, "REOPEN", {"reason": "New investigation"}, self.reviewer)
        self.assertEqual(row.status, "DRAFT")
        self.assertIsNone(row.review)

    def test_replay_no_duplicate_or_fake_timestamp(self):
        row = self.create()
        self.now += timedelta(hours=1)
        replay = self.create()
        self.assertEqual(row, replay)
        with self.engine.connect() as c:
            for table in (RecordRow, RevisionRow, HumanReceiptRow):
                self.assertEqual(c.scalar(select(func.count()).select_from(table)), 1)
        changed = {**self.draft, "operating_context": "changed"}
        self.code(
            "IDEMPOTENCY_CONFLICT",
            lambda: self.service.command(self.author, "CREATE", changed, "create"),
        )

    def test_revision_conflict_and_asset_immutable(self):
        row = self.create()
        self.change(row, "UPDATE", {**self.draft, "operating_context": "new"})
        self.code(
            "REVISION_CONFLICT",
            lambda: self.change(row, "UPDATE", self.draft, request="stale"),
        )
        current = self.service.get(self.author, row.record_id)
        self.code(
            "ASSET_IMMUTABLE",
            lambda: self.change(
                current,
                "UPDATE",
                {**self.draft, "canonical_asset_id": "asset:SYNTHETIC:B"},
                request="move",
            ),
        )

    def test_foreign_asset_and_nonowner_denied_before_pagination(self):
        row = self.create()
        self.code("NOT_FOUND", lambda: self.service.get(self.foreign, row.record_id))
        self.assertEqual(self.service.list(self.foreign)["total"], 0)
        other = self.author.model_copy(update={"principal_id": "other"})
        self.assertEqual(self.service.list(other)["total"], 0)
        self.code("NOT_FOUND", lambda: self.service.history(other, row.record_id))

    def test_asset_and_case_must_resolve_exactly(self):
        with patch.object(self.catalog, "registered", return_value=False):
            self.code("ASSET_NOT_REGISTERED", self.create)
        self.draft["case_refs"] = ["case:SYNTHETIC:OTHER"]
        self.code("CASE_NOT_ACCESSIBLE", self.create)

    def test_inspector_cannot_be_impersonated(self):
        self.draft["inspector_ref"] = "technician"
        self.code("INSPECTOR_ATTRIBUTION_REQUIRED", self.create)

    def test_terminal_mutation_blocked(self):
        row = self.change(self.create(), "SUBMIT", {})
        self.code("INVALID_TRANSITION", lambda: self.change(row, "UPDATE", self.draft))
        row = self.change(
            row, "REVIEW", {"decision": "APPROVED", "reason": "x"}, self.reviewer
        )
        self.code(
            "INVALID_TRANSITION",
            lambda: self.change(row, "UPDATE", self.draft, request="late"),
        )

    def test_atomic_rollback_on_audit_failure(self):
        with patch.object(
            self.repo,
            "save",
            side_effect=EngineeringError("PERSISTENCE_UNAVAILABLE", 503),
        ):
            self.code("PERSISTENCE_UNAVAILABLE", self.create)
        self.assertEqual(self.service.list(self.author)["total"], 0)

    def test_attachments_metadata_only_and_safe_bounded(self):
        metadata = dict(
            attachment_ref="attachment:fixture",
            filename="synthetic.pdf",
            content_type="application/pdf",
            size_bytes=12,
        )
        self.assertEqual(
            AttachmentMetadata(**metadata).status, "METADATA_ONLY_NOT_UPLOADED"
        )
        for extra in (
            {"filename": "../secret"},
            {"size_bytes": True},
            {"size_bytes": 10485761},
            {"url": "https://private.invalid"},
        ):
            with self.assertRaises(ValidationError):
                AttachmentMetadata(**{**metadata, **extra})

    def test_bounded_and_nonblank_contract(self):
        for extra in (
            {"method_version": " "},
            {"observations": [" "]},
            {"interpretations": ["x"] * 21},
            {"measurements": [{"quantity": "x"}] * 101},
            {"case_refs": ["x" * 101]},
        ):
            with self.assertRaises(ValidationError):
                InspectionDraft(**{**self.draft, **extra})

    def test_future_inspection_and_naive_time_rejected(self):
        for timestamp in ("2026-10-10T00:00:00Z", "2026-10-09T00:00:00"):
            self.draft["inspected_at"] = timestamp
            with self.assertRaises(ValidationError):
                self.create()

    def test_api_requires_injected_trusted_identity(self):
        self.assertFalse(build_inspection_router(self.service, enabled=True).routes)
        app = FastAPI()
        app.include_router(
            build_inspection_router(
                self.service,
                enabled=True,
                trusted_principal_dependency=lambda: self.author,
            )
        )
        with TestClient(app) as client:
            r = client.post(
                "/v1/engineering/inspections",
                json={"request_id": "api", "draft": self.draft},
            )
            self.assertEqual(r.status_code, 201, r.text)
            self.assertEqual(r.json()["created_by"], "author")
            invalid = client.post(
                "/v1/engineering/inspections",
                json={
                    "request_id": "invalid",
                    "draft": {**self.draft, "inspector_ref": "forged"},
                },
            )
            self.assertEqual(invalid.status_code, 422)

    def test_feature_disabled_even_if_service_has_store(self):
        self.service.enabled = False
        self.code("FEATURE_DISABLED", self.create)
