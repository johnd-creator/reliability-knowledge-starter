"""Human engineering judgment and bounded canonical evidence, contract v1.0."""
from __future__ import annotations

from enum import StrEnum
from datetime import datetime
from typing import Literal
import json
import re

from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator, model_validator
from src.domain.condition_evidence import EvidenceModel, ConditionEvidence


class CaseStatus(StrEnum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Category(StrEnum):
    INVESTIGATION = "INVESTIGATION"
    MAINTENANCE = "MAINTENANCE"
    CONDITION = "CONDITION"


class Priority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class Role(StrEnum):
    AUTHOR = "AUTHOR"
    REVIEWER = "REVIEWER"


class Principal(EvidenceModel):
    """Only constructed by a trusted server adapter; never a request DTO."""
    principal_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_.:@-]{0,159}$")
    roles: frozenset[Role]
    asset_ids: frozenset[str]


class Investigation(EvidenceModel):
    observed_symptoms: tuple[str, ...] = Field(default=(), max_length=20)
    operating_context: str = Field(default="", max_length=6000)
    hypotheses: tuple[str, ...] = Field(default=(), max_length=20)
    observations: tuple[str, ...] = Field(default=(), max_length=20)
    open_questions: tuple[str, ...] = Field(default=(), max_length=20)
    proposed_next_checks: tuple[str, ...] = Field(default=(), max_length=20)

    @field_validator("observed_symptoms", "hypotheses", "observations", "open_questions", "proposed_next_checks")
    @classmethod
    def bounded_items(cls, values):
        if any(not s.strip() or len(s) > 2000 for s in values):
            raise ValueError("bounded nonblank investigation items required")
        return values


class CaseDraft(EvidenceModel):
    title: str = Field(min_length=1, max_length=200)
    problem_statement: str = Field(min_length=1, max_length=12000)
    canonical_asset_id: str = Field(min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_.:-]+$")
    category: Category = Category.INVESTIGATION
    priority: Priority = Priority.NORMAL
    assigned_engineer: str | None = Field(default=None, max_length=160)
    investigation: Investigation = Field(default_factory=Investigation)

    @field_validator("title", "problem_statement")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("nonblank case information required")
        return value


class EvidenceKind(StrEnum):
    ASSET = "ASSET"
    MAINTENANCE = "MAINTENANCE"
    WORK_ORDER = "WORK_ORDER"
    FMEA = "FMEA"
    RCFA = "RCFA"
    CONDITION = "CONDITION"
    DATA_TRUST = "DATA_TRUST"


class EvidenceSnapshot(EvidenceModel):
    """Allowlisted canonical facts, never raw vendor payloads or source URLs."""
    label: str = Field(min_length=1, max_length=240)
    summary: str | None = Field(default=None, max_length=2000)
    condition: ConditionEvidence | None = None
    availability: Literal["AVAILABLE", "PARTIAL", "UNKNOWN"] = "UNKNOWN"


class EvidenceReference(EvidenceModel):
    reference_id: str = Field(min_length=1, max_length=100)
    record_id: str = Field(min_length=1, max_length=240, pattern=r"^[a-zA-Z0-9_.:-]+$")
    canonical_asset_id: str = Field(min_length=1, max_length=200)
    kind: EvidenceKind
    source: Literal["CANONICAL_MART", "NADI_CONDITION", "NADI_DATA_TRUST"]
    mode: Literal["LIVE_REFERENCE", "FROZEN_SNAPSHOT"]
    stable_version: str = Field(min_length=1, max_length=160)
    source_timestamp: datetime | None = None
    observed_at: datetime
    linked_at: datetime
    linked_by: str = Field(min_length=1, max_length=160)
    identity_status: Literal["VERIFIED"]
    signal_approval: Literal["APPROVED", "NOT_APPLICABLE"]
    freshness: Literal["CURRENT", "STALE", "UNKNOWN"] = "UNKNOWN"
    freshness_policy_ref: str | None = Field(default=None, max_length=200)
    unit: str | None = Field(default=None, max_length=40)
    quality_good: StrictBool | None = None
    quality_questionable: StrictBool | None = None
    quality_substituted: StrictBool | None = None
    quality_annotated: StrictBool | None = None
    snapshot: EvidenceSnapshot | None = None

    @model_validator(mode="after")
    def canonical_shape(self):
        if (self.mode == "FROZEN_SNAPSHOT") != (self.snapshot is not None):
            raise ValueError("only frozen references contain snapshots")
        if self.kind == EvidenceKind.CONDITION:
            if self.source != "NADI_CONDITION" or self.signal_approval != "APPROVED":
                raise ValueError("condition identity and signal approval required")
        elif self.kind == EvidenceKind.DATA_TRUST:
            if self.source != "NADI_DATA_TRUST" or self.signal_approval != "NOT_APPLICABLE":
                raise ValueError("data trust source required")
        elif self.source != "CANONICAL_MART" or self.signal_approval != "NOT_APPLICABLE":
            raise ValueError("canonical factual source required")
        if self.snapshot:
            if len(self.snapshot.model_dump_json().encode()) > 16384:
                raise ValueError("canonical snapshot exceeds 16KiB")
            condition = self.snapshot.condition
            if self.kind == EvidenceKind.CONDITION and condition is None:
                raise ValueError("condition snapshot requires canonical evidence")
            if condition:
                if self.kind != EvidenceKind.CONDITION or condition.canonical_asset_id != self.canonical_asset_id:
                    raise ValueError("condition snapshot asset mismatch")
                for field in ("unit", "source_timestamp", "quality_good", "quality_questionable", "quality_substituted", "quality_annotated"):
                    if getattr(self, field) != getattr(condition, field):
                        raise ValueError("snapshot provenance mismatch")
        return self


class InvestigationNote(EvidenceModel):
    note_id: str
    text: str = Field(min_length=1, max_length=12000)
    actor: str
    created_at: datetime


class ReviewDecision(EvidenceModel):
    reviewer: str
    decision: Literal["APPROVED", "REJECTED"]
    rationale: str = Field(min_length=1, max_length=6000)
    decided_at: datetime


class EngineeringCase(CaseDraft):
    contract_version: Literal["1.0"] = "1.0"
    case_id: str
    status: CaseStatus = CaseStatus.DRAFT
    created_at: datetime
    updated_at: datetime
    created_by: str
    contributors: tuple[str, ...] = Field(default=(), max_length=100)
    revision: int = Field(ge=1)
    provenance: Literal["HUMAN_ENGINEERING_RECORD"] = "HUMAN_ENGINEERING_RECORD"
    notes: tuple[InvestigationNote, ...] = Field(default=(), max_length=100)
    evidence: tuple[EvidenceReference, ...] = Field(default=(), max_length=30)
    review: ReviewDecision | None = None

    @model_validator(mode="after")
    def invariants(self):
        terminal = self.status in {CaseStatus.APPROVED, CaseStatus.REJECTED}
        if terminal != (self.review is not None):
            raise ValueError("terminal case requires review decision")
        if self.review:
            if self.review.decision != self.status or self.review.reviewer in {self.created_by, self.assigned_engineer, *self.contributors}:
                raise ValueError("independent authorized review required")
        if any(r.canonical_asset_id != self.canonical_asset_id for r in self.evidence):
            raise ValueError("cross-asset evidence forbidden")
        if len({(r.kind, r.record_id) for r in self.evidence}) != len(self.evidence):
            raise ValueError("duplicate evidence forbidden")
        if self.updated_at < self.created_at:
            raise ValueError("case timestamps contradict")
        return self


class CaseEvent(EvidenceModel):
    case_id: str
    revision: int = Field(ge=1)
    previous_revision: int = Field(ge=0)
    actor: str
    action: Literal["CREATE", "UPDATE", "NOTE", "LINK", "SUBMIT", "REVIEW", "REVISE", "REOPEN"]
    occurred_at: datetime
    changed_fields: tuple[str, ...]
    reason: str | None = Field(default=None, max_length=6000)


class EngineeringError(Exception):
    def __init__(self, code: str, status: int = 409):
        self.code, self.status = code, status
        super().__init__(code)
