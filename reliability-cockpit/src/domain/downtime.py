"""Downtime event domain model — mirrors schemas/downtime.schema.json.

Computed concept until the Maximo Downtime Report object is verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.types import Numeric, OptionalDatetime


@dataclass(slots=True)
class Downtime:
    id: str
    equipment_id: str | None = None
    started_at: OptionalDatetime = None
    ended_at: OptionalDatetime = None
    duration_hours: Numeric = None
    work_order_id: str | None = None
    cause: str | None = None
    source_origin: str | None = None  # MXWODETAIL | MXASSET | DOWNTIMEREPORT (future)