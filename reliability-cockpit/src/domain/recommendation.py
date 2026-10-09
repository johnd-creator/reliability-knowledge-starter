"""NADI-owned engineering proposals, never source work-order commands."""

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal
from pydantic import Field, StrictStr, field_validator, model_validator
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import (
    Priority,
    EvidenceKind,
    EvidenceReference,
    CaseStatus,
    NONBLANK_TEXT_PATTERN,
)
from src.domain.human_records import HumanRecord
from src.domain.maintenance_context import ExistingWorkOrderReference

RecordRef = Annotated[
    StrictStr, Field(min_length=1, max_length=240, pattern=r"^[A-Za-z0-9_.:-]+$")
]


class EvidenceSelection(EvidenceModel):
    kind: EvidenceKind
    record_id: RecordRef
    mode: Literal["LIVE_REFERENCE", "FROZEN_SNAPSHOT"] = "FROZEN_SNAPSHOT"


class FollowUpStatus(StrEnum):
    PROPOSED = "PROPOSED"
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    VERIFIED = "VERIFIED"


class RecommendationDraft(EvidenceModel):
    canonical_asset_id: StrictStr = Field(
        min_length=1, max_length=200, pattern=r"^[A-Za-z0-9_.:-]+$"
    )
    case_ref: RecordRef
    evidence_selections: tuple[EvidenceSelection, ...] = Field(
        default=(), max_length=20
    )
    rationale: StrictStr = Field(
        min_length=1, max_length=6000, pattern=NONBLANK_TEXT_PATTERN
    )
    proposed_action: StrictStr = Field(
        min_length=1, max_length=6000, pattern=NONBLANK_TEXT_PATTERN
    )
    priority: Priority = Priority.NORMAL
    responsible_team_ref: StrictStr | None = Field(
        default=None, max_length=160, pattern=r"^[A-Za-z0-9_.:@-]+$"
    )
    responsible_person_ref: StrictStr | None = Field(
        default=None, max_length=160, pattern=r"^[A-Za-z0-9_.:@-]+$"
    )
    target_date: date | None = None
    existing_work_order_ref: RecordRef | None = None

    @field_validator("rationale", "proposed_action")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("nonblank engineering proposal required")
        return value

    @model_validator(mode="after")
    def distinct_evidence(self):
        identities = [(x.kind, x.record_id) for x in self.evidence_selections]
        if len(identities) != len(set(identities)):
            raise ValueError("duplicate evidence selection")
        return self


class ReviewedCaseLink(EvidenceModel):
    case_id: RecordRef
    revision: int = Field(ge=1, strict=True)
    stable_version: StrictStr = Field(pattern=r"^[a-f0-9]{64}$")
    reviewer: StrictStr = Field(min_length=1, max_length=160)
    reviewed_at: datetime


class CompletionVerification(EvidenceModel):
    reviewer: StrictStr = Field(min_length=1, max_length=160)
    verified_at: datetime
    reason: StrictStr = Field(min_length=1, max_length=6000, pattern=NONBLANK_TEXT_PATTERN)
    evidence: tuple[EvidenceReference, ...] = Field(min_length=1, max_length=20)
    scope: Literal["NADI_LOCAL_FOLLOW_UP_ONLY"] = "NADI_LOCAL_FOLLOW_UP_ONLY"


class Recommendation(RecommendationDraft, HumanRecord):
    reviewed_case: ReviewedCaseLink | None = None
    completion_verification: CompletionVerification | None = None
    supporting_evidence: tuple[EvidenceReference, ...] = Field(
        default=(), max_length=20
    )
    existing_work_order: ExistingWorkOrderReference | None = None
    follow_up_status: FollowUpStatus = FollowUpStatus.PROPOSED
    provenance: Literal["NADI_ENGINEERING_RECOMMENDATION"] = (
        "NADI_ENGINEERING_RECOMMENDATION"
    )
    action_authorization: Literal["NOT_A_MAINTENANCE_AUTHORIZATION"] = (
        "NOT_A_MAINTENANCE_AUTHORIZATION"
    )
    follow_up_scope: Literal["NADI_LOCAL_FOLLOW_UP_ONLY"] = "NADI_LOCAL_FOLLOW_UP_ONLY"

    @model_validator(mode="after")
    def factual_links(self):
        if len(self.supporting_evidence) != len(self.evidence_selections):
            raise ValueError("evidence selection resolution required")
        for selected, ref in zip(self.evidence_selections, self.supporting_evidence):
            if (selected.kind, selected.record_id, selected.mode) != (
                ref.kind,
                ref.record_id,
                ref.mode,
            ) or ref.canonical_asset_id != self.canonical_asset_id:
                raise ValueError("exact asset evidence required")
        if (self.existing_work_order_ref is None) != (self.existing_work_order is None):
            raise ValueError("existing WO resolution required")
        if self.existing_work_order and (
            self.existing_work_order.canonical_asset_id != self.canonical_asset_id
            or self.existing_work_order.canonical_record_id
            != self.existing_work_order_ref
        ):
            raise ValueError("exact existing WO reference required")
        if self.reviewed_case and self.reviewed_case.case_id != self.case_ref:
            raise ValueError("reviewed case identity mismatch")
        if (self.follow_up_status == FollowUpStatus.VERIFIED) != (self.completion_verification is not None):
            raise ValueError("completion verification required")
        if self.completion_verification:
            v = self.completion_verification
            if v.reviewer in {self.created_by, *self.contributors, self.responsible_person_ref}:
                raise ValueError("independent completion reviewer required")
            if not self.created_at <= v.verified_at <= self.updated_at:
                raise ValueError("completion chronology invalid")
            if any(r.canonical_asset_id != self.canonical_asset_id or r.mode != "FROZEN_SNAPSHOT" for r in v.evidence):
                raise ValueError("exact frozen completion evidence required")
        if (
            self.follow_up_status != FollowUpStatus.PROPOSED
            and self.status != CaseStatus.APPROVED
        ):
            raise ValueError("review required before local follow-up")
        return self
