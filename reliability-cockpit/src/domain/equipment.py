"""Equipment domain model — mirrors schemas/equipment.schema.json.

Field names are vendor-neutral; raw Maximo values live in `maximo_source`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.types import Numeric, OptionalDatetime


@dataclass(slots=True)
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
    extra: dict | None = None  # overflow vendor keys from the collector view


@dataclass(slots=True)
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

    @property
    def sorted_key(self) -> tuple[str, str]:
        return (self.id or "", self.name or "")