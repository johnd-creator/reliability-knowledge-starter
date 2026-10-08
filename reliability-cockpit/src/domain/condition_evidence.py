"""Canonical bounded evidence; source identifiers stay under sources.pi.

No value coercion, inferred equipment identity or health interpretation.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, ValidationInfo, field_validator, model_validator

MAX_SIGNALS = 5
# Full PI WebIds include encoded paths; the real pilot reference is 203 chars.
# Bound only Attribute refs independently from canonical IDs / mapping refs.
MAX_ATTRIBUTE_REF_LENGTH = 512

class EvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    @field_validator("*", mode="before")
    @classmethod
    def timestamp_representation(cls, value, info: ValidationInfo):
        annotation = cls.model_fields[info.field_name].annotation
        if (annotation is datetime or datetime in get_args(annotation)) and value is not None and not isinstance(value, (str, datetime)):
            raise ValueError("timestamps require ISO-8601 strings or aware datetime objects")
        return value

    @field_validator("*", mode="after")
    @classmethod
    def aware_times(cls, value):
        if isinstance(value, datetime) and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("evidence timestamps must be timezone-aware")
        return value

class PiLineage(EvidenceModel):
    pi_source_id: Literal["CENTRAL_PI"]
    af_server_ref: str = Field(min_length=1, max_length=200)
    af_database_ref: str = Field(min_length=1, max_length=200)
    af_element_ref: str = Field(min_length=1, max_length=200)
    mapping_role: Literal["PRIMARY_EQUIPMENT"]
    mapping_status: Literal["VERIFIED"]

    @field_validator("af_server_ref", "af_database_ref", "af_element_ref")
    @classmethod
    def exact_refs(cls, value):
        if value != value.strip():
            raise ValueError("explicit exact references required")
        return value

class EvidenceSources(EvidenceModel):
    pi: PiLineage

class PiAttributeLineage(PiLineage):
    attribute_ref: str = Field(min_length=1, max_length=MAX_ATTRIBUTE_REF_LENGTH)
    attribute_name: str | None = Field(default=None, max_length=240)

class EvidenceAttributeSources(EvidenceModel):
    pi: PiAttributeLineage

class SelectedPiAttribute(EvidenceModel):
    attribute_ref: str = Field(min_length=1, max_length=MAX_ATTRIBUTE_REF_LENGTH)

    @field_validator("attribute_ref")
    @classmethod
    def exact_ref(cls, value):
        if not value.strip() or value != value.strip():
            raise ValueError("exact selected reference required")
        return value

class SignalSources(EvidenceModel):
    pi: SelectedPiAttribute

class SignalSelection(EvidenceModel):
    signal_id: str = Field(min_length=1, max_length=200)
    mapping_id: str = Field(min_length=1, max_length=200)
    sources: SignalSources
    semantic_name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,79}$")
    approval_status: Literal["APPROVED", "RETIRED"]
    approved_by: str = Field(min_length=1, max_length=160)
    approved_at: datetime
    evidence_ref: str = Field(min_length=1, max_length=500)

    @property
    def attribute_ref(self):
        return self.sources.pi.attribute_ref

    @field_validator("approved_by", "evidence_ref")
    @classmethod
    def nonblank(cls, value):
        if not value.strip() or value != value.strip():
            raise ValueError("explicit approval provenance required")
        return value

class ProjectionPlan(EvidenceModel):
    contract_version: Literal["1.0"] = "1.0"
    canonical_asset_id: str = Field(min_length=1, max_length=200)
    mapping_id: str = Field(min_length=1, max_length=200)
    sources: EvidenceSources
    signals: tuple[SignalSelection, ...] = Field(min_length=1, max_length=MAX_SIGNALS)

    @model_validator(mode="after")
    def approved_subset(self):
        if any(s.mapping_id != self.mapping_id or s.approval_status != "APPROVED" for s in self.signals):
            raise ValueError("only explicitly approved signals for this mapping are usable")
        for key in ("signal_id", "attribute_ref", "semantic_name"):
            if len({getattr(s, key) for s in self.signals}) != len(self.signals):
                raise ValueError("duplicate selected signal")
        return self

class DigitalState(EvidenceModel):
    name: StrictStr | None = Field(default=None, max_length=4096)
    code: StrictInt | StrictFloat | None = None
    is_system: StrictBool | None = None

    @field_validator("code")
    @classmethod
    def finite_value(cls, value):
        if type(value) is float and not math.isfinite(value):
            raise ValueError("finite digital state code required")
        return value

class EvidenceProvenance(EvidenceModel):
    source_boundary: Literal["GOVERNED_PI_SOURCE"] = "GOVERNED_PI_SOURCE"
    selection_evidence_ref: str = Field(min_length=1, max_length=500)
    selection_approved_by: str = Field(min_length=1, max_length=160)
    selection_approved_at: datetime

class ConditionEvidence(EvidenceModel):
    contract_version: Literal["1.0"] = "1.0"
    canonical_asset_id: str = Field(min_length=1, max_length=200)
    mapping_id: str = Field(min_length=1, max_length=200)
    signal_id: str = Field(min_length=1, max_length=200)
    semantic_name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,79}$")
    sources: EvidenceAttributeSources
    value_type: Literal["NUMERIC", "TEXT", "DIGITAL_STATE", "BOOLEAN", "NULL"]
    value: StrictInt | StrictFloat | StrictStr | StrictBool | DigitalState | None
    unit: str | None = Field(max_length=40)
    source_timestamp: datetime | None
    collected_at: datetime
    quality_good: StrictBool | None
    quality_questionable: StrictBool | None
    quality_substituted: StrictBool | None
    quality_annotated: StrictBool | None
    evidence_status: Literal["EVIDENCE_AVAILABLE", "BAD_QUALITY", "UNKNOWN_VALUE", "UNKNOWN_QUALITY"]
    provenance: EvidenceProvenance

    @property
    def attribute_ref(self):
        return self.sources.pi.attribute_ref

    @model_validator(mode="after")
    def typed_value_and_status(self):
        value = self.value
        if isinstance(value, str) and len(value) > 4096:
            raise ValueError("selected evidence text exceeds bounded storage")
        valid = {"NUMERIC": type(value) in (int, float), "TEXT": type(value) is str,
                 "BOOLEAN": type(value) is bool, "DIGITAL_STATE": isinstance(value, DigitalState), "NULL": value is None}
        if not valid[self.value_type] or (type(value) is float and not math.isfinite(value)):
            raise ValueError("value must retain its explicit source type")
        if self.evidence_status != quality_status(value, self.quality_good, self.quality_questionable):
            raise ValueError("evidence status contradicts source quality/value")
        return self

def quality_status(value, good, questionable):
    if good is False or questionable is True:
        return "BAD_QUALITY"
    if value is None:
        return "UNKNOWN_VALUE"
    if good is None:
        return "UNKNOWN_QUALITY"
    return "EVIDENCE_AVAILABLE"

class SignalResult(EvidenceModel):
    signal_id: str
    status: Literal["COLLECTED", "SOURCE_UNAVAILABLE", "PROJECTION_ERROR"]
    evidence: ConditionEvidence | None = None

    @model_validator(mode="after")
    def result_shape(self):
        if (self.status == "COLLECTED") != (self.evidence is not None):
            raise ValueError("collected results require evidence; failures cannot contain a value")
        return self

class EvidenceBatch(EvidenceModel):
    plan: ProjectionPlan
    results: tuple[SignalResult, ...] = Field(max_length=MAX_SIGNALS)
    collector_last_success_at: datetime | None = None

    @model_validator(mode="after")
    def exact_selection(self):
        ids = [r.signal_id for r in self.results]
        selected = {s.signal_id: s for s in self.plan.signals}
        if len(ids) != len(set(ids)) or not set(ids) <= selected.keys():
            raise ValueError("batch contains duplicate/unselected signals")
        for r in self.results:
            if r.evidence is None:
                continue
            e, s = r.evidence, selected[r.signal_id]
            if (e.canonical_asset_id != self.plan.canonical_asset_id or e.mapping_id != self.plan.mapping_id
                or e.sources.pi.model_dump(exclude={"attribute_ref", "attribute_name"}) != self.plan.sources.pi.model_dump() or e.signal_id != s.signal_id
                or e.attribute_ref != s.attribute_ref or e.semantic_name != s.semantic_name
                or e.provenance != EvidenceProvenance(selection_evidence_ref=s.evidence_ref,
                   selection_approved_by=s.approved_by, selection_approved_at=s.approved_at)):
                raise ValueError("evidence lineage/selection does not match governed plan")
        return self

class FreshnessPolicy(EvidenceModel):
    """Legacy explicit mode OR component mode; unset never inherits another policy."""
    collector_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    source_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    projection_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    maximo_wo_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    mart_factual_projection_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    pi_collector_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    condition_source_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    condition_projection_max_age_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)

    @field_validator("*", mode="before")
    @classmethod
    def not_boolean_policy(cls, value):
        if isinstance(value, bool):
            raise ValueError("numeric policy required, not boolean")
        return value

    @model_validator(mode="after")
    def exclusive_modes(self):
        legacy = (self.collector_max_age_seconds, self.source_max_age_seconds, self.projection_max_age_seconds)
        if any(v is not None for v in legacy) and self.component_mode:
            raise ValueError("legacy and component freshness policies cannot be mixed")
        return self

    @property
    def component_mode(self):
        return any(getattr(self, f) is not None for f in type(self).model_fields
                   if f not in {"collector_max_age_seconds", "source_max_age_seconds", "projection_max_age_seconds"})

    @classmethod
    def from_environment(cls):
        import os
        # Whitespace is not a blank policy; invalid values fail at model validation.
        return cls(**{f: os.getenv("NADI_" + f.upper()) or None for f in cls.model_fields})

    def threshold(self, dimension, component=None):
        dimension = dimension.upper()
        if dimension not in {"COLLECTOR", "SOURCE", "PROJECTION"}:
            raise ValueError("unknown freshness dimension")
        fields = {("MAXIMO", "COLLECTOR"): "maximo_wo_max_age_seconds",
                  ("RELIABILITY_MART", "PROJECTION"): "mart_factual_projection_max_age_seconds",
                  ("PI_COLLECTOR", "COLLECTOR"): "pi_collector_max_age_seconds",
                  ("PI_CONDITION_PROJECTION", "SOURCE"): "condition_source_max_age_seconds",
                  ("PI_CONDITION_PROJECTION", "PROJECTION"): "condition_projection_max_age_seconds"}
        if self.component_mode:
            field = fields.get((component, dimension))
            return getattr(self, field) if field else None
        return getattr(self, dimension.lower() + "_max_age_seconds")

    def state(self, dimension: str, timestamp: datetime | None, now: datetime, *, component=None):
        threshold = self.threshold(dimension, component)
        if timestamp is None or threshold is None:
            return dimension + "_UNKNOWN"
        # SQLite indexed columns lose offsets; canonical handoff rejects naive times.
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age = (now - timestamp).total_seconds()
        if age < 0:
            return dimension + "_UNKNOWN"
        return dimension + ("_CURRENT" if age <= threshold else "_STALE")
