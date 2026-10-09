"""Extensible manual measurement envelope, NOT a diagnostic/health score."""

from datetime import datetime
from enum import StrEnum
import math
from typing import Annotated, Literal
from pydantic import (
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import InvestigationItem, NONBLANK_TEXT_PATTERN
from src.domain.human_records import HumanRecord


class InspectionMethod(StrEnum):
    VIBRATION = "VIBRATION"
    IR_THERMOGRAPHY = "IR_THERMOGRAPHY"
    MCSA = "MCSA"
    TRIBOLOGY = "TRIBOLOGY"
    DGA = "DGA"
    OTHER = "OTHER"


from src.domain.inspection_measurement import ExtensionScalar, ManualMeasurement
ExtensionKey = Annotated[StrictStr, Field(pattern=r"^[A-Za-z][A-Za-z0-9_]{0,79}$")]

class InspectionStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    IN_REVIEW = "IN_REVIEW"  # Legacy accepted record, not a new submission state.
    APPROVED = "APPROVED"
    RETURNED = "RETURNED"
    REJECTED = "REJECTED"

class InspectionReview(EvidenceModel):
    reviewer: StrictStr
    decision: Literal["APPROVED", "RETURNED", "REJECTED"]
    rationale: StrictStr = Field(min_length=1,max_length=6000,pattern=NONBLANK_TEXT_PATTERN)
    decided_at: datetime

class AttachmentMetadata(EvidenceModel):
    attachment_ref: StrictStr = Field(pattern=r"^attachment:[A-Za-z0-9_.:-]{1,90}$")
    filename: StrictStr = Field(
        min_length=1,
        max_length=200,
        pattern=r"^[^/\\]+$",
        json_schema_extra={
            "allOf": [
                {"pattern": NONBLANK_TEXT_PATTERN},
                {"not": {"enum": [".", ".."]}},
            ]
        },
    )
    content_type: Literal[
        "application/pdf", "image/png", "image/jpeg", "text/csv", "text/plain"
    ]
    size_bytes: StrictInt = Field(ge=0, le=10485760)
    sha256: StrictStr | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    status: Literal["METADATA_ONLY_NOT_UPLOADED"] = "METADATA_ONLY_NOT_UPLOADED"

    @field_validator("filename")
    @classmethod
    def basename(cls, value):
        if not value.strip() or "/" in value or "\\" in value or value in {".", ".."}:
            raise ValueError("safe attachment basename required")
        return value


class InspectionDraft(EvidenceModel):
    canonical_asset_id: StrictStr = Field(
        min_length=1, max_length=200, pattern=r"^[A-Za-z0-9_.:-]+$"
    )
    method: InspectionMethod
    method_version: StrictStr = Field(
        min_length=1, max_length=80, pattern=NONBLANK_TEXT_PATTERN
    )
    inspector_ref: StrictStr = Field(
        min_length=1, max_length=160, pattern=NONBLANK_TEXT_PATTERN
    )
    inspected_at: datetime | None = None
    operating_context: StrictStr | None = Field(default=None, max_length=6000)
    measurements: tuple[ManualMeasurement, ...] = Field(default=(), max_length=100)
    observations: tuple[InvestigationItem, ...] = Field(default=(), max_length=20)
    interpretations: tuple[InvestigationItem, ...] = Field(default=(), max_length=20)
    attachments: tuple[AttachmentMetadata, ...] = Field(default=(), max_length=10)
    case_refs: tuple[
        Annotated[
            StrictStr,
            Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$"),
        ],
        ...,
    ] = Field(default=(), max_length=10)
    method_extension: dict[ExtensionKey, ExtensionScalar] = Field(
        default_factory=dict, max_length=20,
        json_schema_extra={"additionalProperties": False},
    )

    @field_validator("method_version", "inspector_ref")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("nonblank identity/version required")
        return value

    @field_validator("method_extension")
    @classmethod
    def finite_extension(cls, value):
        if any(isinstance(v, float) and not math.isfinite(v) for v in value.values()):
            raise ValueError("nonfinite extension")
        return value


class ManualInspection(InspectionDraft, HumanRecord):
    contract_version: Literal["1.0", "1.1"] = "1.1"
    status: InspectionStatus = InspectionStatus.DRAFT
    review: InspectionReview | None = None
    review_started_by: StrictStr | None = None
    review_started_at: datetime | None = None

    @model_validator(mode="after")
    def lifecycle(self):
        terminal = self.status in {InspectionStatus.APPROVED, InspectionStatus.RETURNED, InspectionStatus.REJECTED}
        if terminal != (self.review is not None):
            raise ValueError("review decision/status mismatch")
        if self.updated_at < self.created_at or (self.submitted_at and not self.created_at <= self.submitted_at <= self.updated_at):
            raise ValueError("inspection chronology invalid")
        if self.status != InspectionStatus.DRAFT and self.submitted_at is None:
            raise ValueError("submitted revision required")
        if (self.review_started_at is None) != (self.review_started_by is None):
            raise ValueError("review start identity/time required together")
        excluded = {self.created_by, *self.contributors, self.inspector_ref}
        if self.status == InspectionStatus.UNDER_REVIEW and self.review_started_at is None:
            raise ValueError("review must start explicitly")
        if self.review_started_at and (not self.submitted_at or not self.submitted_at <= self.review_started_at <= self.updated_at or self.review_started_by in excluded):
            raise ValueError("independent review start required")
        if self.review and (self.review.decision != self.status or self.review.reviewer in excluded or not self.submitted_at <= self.review.decided_at <= self.updated_at):
            raise ValueError("independent review/chronology required")
        if self.review and self.review_started_by and (self.review.reviewer != self.review_started_by or self.review.decided_at < self.review_started_at):
            raise ValueError("review assigned to another reviewer")
        return self

    provenance: Literal["NADI_MANUAL_INSPECTION"] = "NADI_MANUAL_INSPECTION"
    field_approval: Literal["ENGINEER_FIELDS_PENDING"] = "ENGINEER_FIELDS_PENDING"
    assessment: Literal["NOT_ASSESSED"] = "NOT_ASSESSED"

    @model_validator(mode="after")
    def measurement_chronology(self):
        if self.inspected_at and self.inspected_at > self.updated_at:
            raise ValueError("future inspection")
        if any(
            m.measured_at and m.measured_at > self.updated_at for m in self.measurements
        ):
            raise ValueError("future measurement")
        return self


# Field proposals, not approved required fields or standards/thresholds.
METHOD_PROPOSALS = {
    "VIBRATION": (
        "measurement_point",
        "axis",
        "quantity",
        "frequency_band",
        "sensor",
        "load_context",
    ),
    "IR_THERMOGRAPHY": (
        "target_area",
        "emissivity",
        "ambient_context",
        "camera",
        "reference_area",
    ),
    "MCSA": (
        "phase",
        "sensor",
        "sampling_context",
        "operating_load",
        "frequency_context",
    ),
    "TRIBOLOGY": (
        "sample_point",
        "sample_id",
        "lubricant_reference",
        "laboratory",
        "sampling_context",
    ),
    "DGA": (
        "sample_id",
        "sampling_location",
        "laboratory",
        "reported_gas_quantity",
        "report_version",
    ),
    "OTHER": ("method_name", "procedure_reference", "quantity", "equipment_context"),
}
