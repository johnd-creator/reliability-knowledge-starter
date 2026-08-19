"""Item (spare part) domain model — mirrors schemas/item.schema.json."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.types import OptionalDatetime


@dataclass(slots=True)
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