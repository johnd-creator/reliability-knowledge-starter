"""Person domain model — mirrors schemas/person.schema.json.

Personal contact values (email/phone) are intentionally NOT stored.
Maximo exposes only collectionref URLs; the cockpit leaves them null.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.types import OptionalDatetime


@dataclass(slots=True)
class Person:
    id: str
    display_name: str | None = None
    first_name: str | None = None
    status: str | None = None
    status_changed_at: OptionalDatetime = None
    location_org: str | None = None