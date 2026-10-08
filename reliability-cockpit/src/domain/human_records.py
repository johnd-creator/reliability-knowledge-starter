"""Common reviewed human records; independent of source/Mart mutation."""

from datetime import datetime
from typing import Literal
from pydantic import Field, StrictInt, StrictStr, model_validator
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import CaseStatus, ReviewDecision


class HumanRecord(EvidenceModel):
    contract_version: Literal["1.0"] = "1.0"
    record_id: StrictStr = Field(min_length=1, max_length=100)
    status: CaseStatus = CaseStatus.DRAFT
    created_by: StrictStr = Field(min_length=1, max_length=160)
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None = None
    revision: StrictInt = Field(ge=1)
    contributors: tuple[StrictStr, ...] = Field(default=(), max_length=100)
    review: ReviewDecision | None = None
    approval_scope: Literal["NADI_RECORD_REVIEW_ONLY"] = "NADI_RECORD_REVIEW_ONLY"

    @model_validator(mode="after")
    def lifecycle(self):
        terminal = self.status in {CaseStatus.APPROVED, CaseStatus.REJECTED}
        if terminal != (self.review is not None):
            raise ValueError("review decision/status mismatch")
        if self.updated_at < self.created_at or (
            self.submitted_at
            and not self.created_at <= self.submitted_at <= self.updated_at
        ):
            raise ValueError("human record chronology invalid")
        if self.status != CaseStatus.DRAFT and self.submitted_at is None:
            raise ValueError("submitted revision required")
        if self.review:
            if not self.submitted_at <= self.review.decided_at <= self.updated_at:
                raise ValueError("review chronology invalid")
            excluded = {
                self.created_by,
                *self.contributors,
                getattr(self, "inspector_ref", None),
                getattr(self, "responsible_person_ref", None),
            }
            if self.review.decision != self.status or self.review.reviewer in excluded:
                raise ValueError("independent record review required")
        return self
