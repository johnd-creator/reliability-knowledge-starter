"""ReliabilityKPI domain model — mirrors schemas/reliability-kpi.schema.json.

Computed by the cockpit (not a direct Maximo field). Units explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from src.domain.types import Numeric


@dataclass(slots=True)
class ReliabilityKpi:
    id: str
    equipment_id: str | None = None
    metric: str | None = None  # MTBF | MTTR | AVAILABILITY | PM_COMPLIANCE
    value: Numeric = None
    unit: str | None = None  # hours | percent | count
    period_start: date | None = None
    period_end: date | None = None
    computed_at: datetime | None = None
    inputs: dict | None = None