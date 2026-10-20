"""Provisional source transcription, separate from canonical measurements.

Dates and labels retain their reported precision and meaning. These records
never approve asset/point binding, formula evaluation, limits, or diagnosis.
"""
from datetime import date, datetime, time
import math
import re
from typing import Annotated, Literal

from pydantic import Field, StrictInt, StrictStr, field_validator, model_validator
from src.domain.condition_evidence import EvidenceModel
from src.domain.inspection_measurement import ExtensionScalar
from src.domain.text import NONBLANK_TEXT_PATTERN

NonblankLabel = Annotated[StrictStr, Field(min_length=1, max_length=2000, pattern=NONBLANK_TEXT_PATTERN)]
HeaderCell = Annotated[StrictStr, Field(max_length=40,
    pattern=r"^\$?[A-Z]{1,3}\$?[1-9][0-9]{0,6}(?::\$?[A-Z]{1,3}\$?[1-9][0-9]{0,6})?$")]


class CapturedScalar(EvidenceModel):
    raw_value: ExtensionScalar = None

    @field_validator("raw_value")
    @classmethod
    def finite(cls, value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("finite source scalar required")
        return value


class CaptureClock(CapturedScalar):
    role: Literal["ACQUISITION", "SAMPLE", "ANALYSIS", "REPORT", "UNSPECIFIED"] = "UNSPECIFIED"
    precision: Literal["DATE", "DATETIME", "LOCAL_DATETIME", "TIME", "RAW", "UNKNOWN"] = "UNKNOWN"
    value: StrictStr | None = Field(default=None, max_length=80)
    source_label: StrictStr | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def reported_precision(self):
        if self.precision in {"RAW", "UNKNOWN"}:
            if self.value is not None:
                raise ValueError("uninterpreted source clocks cannot assert a calendar value")
            return self
        if self.raw_value is None or isinstance(self.raw_value, bool) or self.value is None:
            raise ValueError("original source scalar and explicit calendar value required")
        if self.precision == "DATE":
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", self.value):
                raise ValueError("date-only requires YYYY-MM-DD")
            date.fromisoformat(self.value)
        elif self.precision == "TIME":
            if not re.fullmatch(r"[0-9]{2}:[0-9]{2}(?::[0-9]{2}(?:\.[0-9]{1,6})?)?", self.value):
                raise ValueError("time-only cannot assert date or timezone")
            time.fromisoformat(self.value)
        else:
            local = r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}(?::[0-9]{2}(?:\.[0-9]{1,6})?)?"
            suffix = r"(?:[Zz]|[+-][0-9]{2}:[0-9]{2})" if self.precision == "DATETIME" else ""
            if not re.fullmatch(local + suffix, self.value):
                raise ValueError("clock precision and timezone representation disagree")
            parsed = datetime.fromisoformat(self.value.replace("t", "T").replace("z", "+00:00").replace("Z", "+00:00"))
            if self.precision == "DATETIME" and parsed.utcoffset() is None:
                raise ValueError("DATETIME requires an explicit timezone offset")
            if self.precision == "LOCAL_DATETIME" and parsed.tzinfo is not None:
                raise ValueError("local datetime cannot assert a timezone")
        # Source report clocks are retained as source claims, not compared with
        # record entry time or copied into measured_at/inspected_at.
        return self


class CaptureContext(CapturedScalar):
    role: Literal["ACQUISITION", "OPERATING_CONTEXT", "LAB", "INSTRUMENT", "PROCEDURE", "CAMERA", "SAMPLE", "REPORT"]
    label: StrictStr = Field(min_length=1, max_length=200, pattern=NONBLANK_TEXT_PATTERN)
    unit: StrictStr | None = Field(default=None, max_length=80)


class CaptureRow(CapturedScalar):
    row_id: StrictStr = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_.:-]+$")
    source_label: NonblankLabel
    source_field_id: StrictStr | None = Field(default=None, max_length=120)
    value_region: HeaderCell | None = None
    unit: StrictStr | None = Field(default=None, max_length=80)
    source_point: StrictStr | None = Field(default=None, max_length=200)
    source_axis: StrictStr | None = Field(default=None, max_length=80)
    header_cells: tuple[HeaderCell, ...] = Field(default=(), max_length=20)
    value_origin: Literal["SOURCE_LITERAL", "SOURCE_FORMULA_RESULT", "MANUAL_REPORTED", "UNKNOWN"] = "UNKNOWN"
    row_role: Literal["INPUT", "REFERENCE", "SOURCE_ASSESSMENT"] = "INPUT"
    contexts: tuple[CaptureContext, ...] = Field(default=(), max_length=20)
    clock: CaptureClock | None = None


class InputCapture(EvidenceModel):
    schema_version: Literal["1.0"] = "1.0"
    purpose: Literal["PROVISIONAL_INPUT_ONLY"] = "PROVISIONAL_INPUT_ONLY"
    source_ref: StrictStr = Field(min_length=1, max_length=120, pattern=NONBLANK_TEXT_PATTERN)
    source_asset_label: StrictStr | None = Field(default=None, max_length=2000)
    source_sheet_label: StrictStr | None = Field(default=None, max_length=2000)
    source_sha256: StrictStr | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    sheet_index: StrictInt | None = Field(default=None, ge=0)
    profile_id: StrictStr = Field(min_length=1, max_length=120, pattern=NONBLANK_TEXT_PATTERN)
    profile_version: StrictStr = Field(min_length=1, max_length=80, pattern=NONBLANK_TEXT_PATTERN)
    clocks: tuple[CaptureClock, ...] = Field(default=(), max_length=12)
    rows: tuple[CaptureRow, ...] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def row_identity(self):
        if len({row.row_id for row in self.rows}) != len(self.rows):
            raise ValueError("capture row IDs must be unique within the profile")
        return self
