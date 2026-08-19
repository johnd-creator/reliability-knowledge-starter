"""Contract-shaped domain models.

Field names follow reliability-data-contracts (snake_case, vendor-neutral);
raw Maximo identifiers are quarantined under a ``sources``-style block
(``MaximoEquipmentSource`` / ``sources["maximo"]``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

Numeric = float | int | None
OptionalDatetime = datetime | None


@dataclass(slots=True, frozen=True)
class MaximoEquipmentSource:
    assetnum: str | None = None
    assetid: int | None = None
    location: str | None = None
    siteid: str | None = None
    orgid: str | None = None
    status: str | None = None
    assettype: str | None = None
    plant: str | None = None
    eq11: str | None = None
    parent: str | None = None
    ancestor: str | None = None
    children: bool | None = None
    isrunning: bool | None = None
    installdate: OptionalDatetime = None
    changedate: OptionalDatetime = None
    totdowntime: Numeric = None
    # Additional verified MXAPIASSET fields. Kept in the Maximo quarantine
    # instead of becoming vendor fields in the core equipment contract.
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Equipment:
    id: str
    name: str | None = None
    description: str | None = None
    location_id: str | None = None
    equipment_class: str | None = None
    unit: str | None = None
    status: str | None = None
    status_description: str | None = None
    is_running: bool | None = None
    priority: int | None = None
    parent_id: str | None = None
    ancestor_id: str | None = None
    has_children: bool | None = None
    failure_code: str | None = None
    is_safety_critical: bool | None = None
    is_calibration: bool | None = None
    installed_at: OptionalDatetime = None
    status_changed_at: OptionalDatetime = None
    source_changed_at: OptionalDatetime = None
    purchase_price: Numeric = None
    replacement_cost: Numeric = None
    total_cost: Numeric = None
    downtime_total_hours: Numeric = None
    manufacturer: str | None = None
    vendor: str | None = None
    maximo_source: MaximoEquipmentSource | None = field(default=None)


@dataclass(slots=True, frozen=True)
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


@dataclass(slots=True, frozen=True)
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
    status_changed_at: OptionalDatetime = None
    sources: dict | None = field(default=None)


@dataclass(slots=True, frozen=True)
class Person:
    id: str
    display_name: str | None = None
    first_name: str | None = None
    status: str | None = None
    status_changed_at: OptionalDatetime = None
    location_org: str | None = None


@dataclass(slots=True, frozen=True)
class Item:
    id: str
    description: str | None = None
    status: str | None = None
    item_type: str | None = None
    lot_type: str | None = None
    issue_unit: str | None = None
    order_unit: str | None = None
    is_rotating: bool | None = None
    is_kit: bool | None = None
    is_crew: bool | None = None
    inspection_required: bool | None = None
    meter_name: str | None = None
    item_set_id: str | None = None
    status_changed_at: OptionalDatetime = None


@dataclass(slots=True, frozen=True)
class Labor:
    id: str
    person_id: str | None = None
    status: str | None = None
    status_description: str | None = None
    work_site: str | None = None
    is_assigned: bool | None = None
    availability_factor: Numeric = None
    reported_hours: Numeric = None
    year_to_date_other_hours: Numeric = None
    year_to_date_refused_hours: Numeric = None
