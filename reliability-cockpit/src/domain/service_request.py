"""ServiceRequest domain model — mirrors schemas/service-request.schema.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.types import Numeric, OptionalDatetime


@dataclass(slots=True)
class ServiceRequest:
    id: str
    description: str | None = None
    status: str | None = None
    status_description: str | None = None
    work_type: str | None = None
    equipment_id: str | None = None
    location_id: str | None = None
    reported_by: str | None = None
    reported_by_name: str | None = None
    reported_at: OptionalDatetime = None
    source_changed_at: OptionalDatetime = None
    affected_at: OptionalDatetime = None
    actual_start: OptionalDatetime = None
    actual_finish: OptionalDatetime = None
    target_start: OptionalDatetime = None
    target_finish: OptionalDatetime = None
    internal_priority: str | None = None
    reported_priority: str | None = None
    actual_labor_hours: Numeric = None
    actual_labor_cost: Numeric = None
    risk_area_environment: str | None = None
    risk_area_process: str | None = None
    risk_area_human: str | None = None
    risk_area_reputation: str | None = None
    class_label: str | None = None
    sources: dict | None = field(default=None)