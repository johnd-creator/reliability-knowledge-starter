"""WorkOrder domain model — mirrors schemas/work-order.schema.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.types import Numeric, OptionalDatetime


@dataclass(slots=True)
class WorkOrder:
    id: str
    equipment_id: str | None = None
    location_id: str | None = None
    status: str | None = None
    status_description: str | None = None
    work_type: str | None = None
    work_class: str | None = None
    description: str | None = None
    reported_at: OptionalDatetime = None
    source_changed_at: OptionalDatetime = None
    status_changed_at: OptionalDatetime = None
    scheduled_start: OptionalDatetime = None
    scheduled_finish: OptionalDatetime = None
    target_completion: OptionalDatetime = None
    estimated_duration_hours: Numeric = None
    downtime_hours: Numeric = None
    priority: str | None = None
    priority_description: str | None = None
    reported_by: str | None = None
    supervisor: str | None = None
    lead: str | None = None
    failure_code: str | None = None
    is_task: bool | None = None
    parent_wo: str | None = None
    has_children: bool | None = None
    estimated_labor_cost: Numeric = None
    estimated_material_cost: Numeric = None
    actual_labor_cost: Numeric = None
    actual_material_cost: Numeric = None
    actual_labor_hours: Numeric = None
    sources: dict | None = field(default=None)