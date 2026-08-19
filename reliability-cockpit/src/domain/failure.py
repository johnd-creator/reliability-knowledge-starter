"""Failure event domain model — mirrors schemas/failure.schema.json.

Computed concept: the Maximo FAILURECODE master is still read-forbidden,
so failure events are inferred from work-order failure data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.types import Numeric, OptionalDatetime


@dataclass(slots=True)
class Failure:
    id: str
    equipment_id: str | None = None
    failure_code: str | None = None
    work_order_id: str | None = None
    occurred_at: OptionalDatetime = None
    downtime_hours: Numeric = None
    description: str | None = None
    source_origin: str | None = None  # MXWODETAIL | MXFAILURECODE (future)