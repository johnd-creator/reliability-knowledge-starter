"""Vendor-neutral domain models for collected PI data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AttributeRegistration:
    attribute_id: str
    site: str
    unit: str
    equipment: str
    parameter: str
    business_name: str
    position: str | None = None
    unit_of_measure: str | None = None
    web_id: str | None = None
    af_path: str | None = None


@dataclass(frozen=True)
class Snapshot:
    attribute_id: str
    value: float | None
    value_good: bool | None
    units: str | None
    source_timestamp: datetime | None
    collected_at: datetime | None = None
    value_type: str | None = None
    value_questionable: bool | None = None
    value_substituted: bool | None = None
    value_annotated: bool | None = None


@dataclass(frozen=True)
class TimeseriesPoint:
    attribute_id: str
    timestamp: datetime
    value: float | None
    value_good: bool | None
    units: str | None = None
    value_type: str | None = None
    value_questionable: bool | None = None
    value_substituted: bool | None = None
    value_annotated: bool | None = None
