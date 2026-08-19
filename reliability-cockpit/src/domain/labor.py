"""Labor domain model — mirrors schemas/labor.schema.json."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.types import Numeric


@dataclass(slots=True)
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