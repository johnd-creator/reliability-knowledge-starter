"""Governed PI source boundary over the existing :class:`PiClient`.

The technical registry collector remains available for broad inventory and
local trending. This boundary is the only place that accepts an Asset-to-AF
target, and it requires a VERIFIED PRIMARY_EQUIPMENT CENTRAL_PI target that
was resolved by an external governance/orchestration layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from src.adapters.pi.client import (
    PiClient,
    extract_recorded,
    extract_snapshot,
)
from src.domain.governed import GovernedAfTarget, validate_governed_af_target
from src.domain.models import Snapshot, TimeseriesPoint


class GovernedSourceBoundary:
    """Read AF context and PI-backed values for one validated target.

    This class never loads or writes the Reliability Mart and never discovers
    an Asset-to-AF relationship. The caller supplies explicit AF attribute
    references returned from the bounded AF attribute listing.
    """

    def __init__(self, client: PiClient):
        self._client = client

    @staticmethod
    def _validate(target: GovernedAfTarget) -> GovernedAfTarget:
        return validate_governed_af_target(target)

    def get_element(self, target: GovernedAfTarget) -> dict:
        target = self._validate(target)
        return self._client.get_af_element(target.af_element_ref)

    def list_attributes(self, target: GovernedAfTarget, *, max_count: int = 100) -> list[dict]:
        target = self._validate(target)
        bounded_count = max(1, min(max_count, 100))
        return self._client.list_af_attributes(target.af_element_ref, max_count=bounded_count)

    def get_attribute(self, target: GovernedAfTarget, attribute_ref: str) -> dict:
        self._validate(target)
        return self._client.get_af_attribute(attribute_ref)

    def get_snapshot(
        self,
        target: GovernedAfTarget,
        attribute_ref: str,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> Snapshot:
        self._validate(target)
        attribute = metadata or self._client.get_af_attribute(attribute_ref)
        payload = self._client.get_af_attribute_value(attribute)
        units = attribute.get("DefaultUnitsName") if isinstance(attribute, Mapping) else None
        return extract_snapshot(payload, attribute_ref, units=units)

    def get_recorded(
        self,
        target: GovernedAfTarget,
        attribute_ref: str,
        *,
        start_time: str,
        end_time: str,
        max_count: int = 20,
        metadata: Mapping[str, Any] | None = None,
    ) -> list[TimeseriesPoint]:
        self._validate(target)
        attribute = metadata or self._client.get_af_attribute(attribute_ref)
        payload = self._client.get_af_attribute_recorded(
            attribute,
            start_time=start_time,
            end_time=end_time,
            max_count=max(1, min(max_count, 20)),
        )
        return extract_recorded(payload, attribute_ref)
