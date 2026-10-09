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


ExtensionScalar = (
    Annotated[StrictStr, Field(max_length=2000)]
    | StrictInt
    | StrictFloat
    | StrictBool
    | None
)
ExtensionKey = Annotated[StrictStr, Field(pattern=r"^[A-Za-z][A-Za-z0-9_]{0,79}$")]


class ManualMeasurement(EvidenceModel):
    quantity: StrictStr = Field(
        min_length=1, max_length=120, pattern=NONBLANK_TEXT_PATTERN
    )
    value: ExtensionScalar = None
    unit: StrictStr | None = Field(default=None, max_length=40)
    measured_at: datetime | None = None
    point_ref: StrictStr | None = Field(default=None, max_length=200)
    quality: Literal["UNKNOWN", "INSPECTOR_REPORTED"] = "UNKNOWN"
    provenance: Literal["HUMAN_ENTERED_MEASUREMENT"] = "HUMAN_ENTERED_MEASUREMENT"

    @field_validator("value")
    @classmethod
    def finite(cls, value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("nonfinite measurement")
        return value


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
