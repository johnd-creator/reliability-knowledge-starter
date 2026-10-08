"""Collector-owned, read-only source boundary for externally resolved mappings.

This is an internal library, not a public source-proxy API. The trusted caller
must resolve unique active mappings in the Mart; self-declared request bodies
are not governance proof. No mapping store or credential lives in NADI here.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from urllib.parse import quote

from src.adapters.pi.client import PiClient, PiClientError, extract_recorded, extract_snapshot, _source_units
from src.domain.governed import GovernedAfTarget, validate_governed_af_target
from src.domain.models import Snapshot, TimeseriesPoint
from src.domain.source_diagnostics import SourceFailureCode


def _limit(value: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PiClientError("source count must be a positive integer")
    return min(value, maximum)


def _window(start: str, end: str) -> tuple[datetime, datetime]:
    try:
        first = datetime.fromisoformat(start.replace("Z", "+00:00"))
        last = datetime.fromisoformat(end.replace("Z", "+00:00"))
        if first.tzinfo is None or last.tzinfo is None or not timedelta(0) < last - first <= timedelta(hours=24):
            raise ValueError
        return first, last
    except (AttributeError, TypeError, ValueError):
        raise PiClientError("governed history requires an explicit aware interval of at most 24 hours") from None


class GovernedSourceBoundary:
    """Bounded operations; each operation revalidates target and source lineage."""

    def __init__(self, client: PiClient):
        self._client = client

    def get_element(self, target: GovernedAfTarget) -> dict:
        target = validate_governed_af_target(target)
        element = self._client.get_af_element(target.af_element_ref)
        if element.get("WebId") != target.af_element_ref:
            raise PiClientError("AF element identity mismatch", failure_code=SourceFailureCode.CONTRACT_INVALID)
        self._client.require_resource_link(element, "Database", f"/assetdatabases/{quote(target.af_database_ref, safe='')}")
        database = self._client.get_af_database(target.af_database_ref)
        if database.get("WebId") != target.af_database_ref:
            raise PiClientError("AF database identity mismatch", failure_code=SourceFailureCode.CONTRACT_INVALID)
        self._client.require_resource_link(database, "AssetServer", f"/assetservers/{quote(target.af_server_ref, safe='')}")
        return element

    def list_attributes(self, target: GovernedAfTarget, *, max_count: int = 100) -> list[dict]:
        validate_governed_af_target(target)
        count = _limit(max_count, 100)
        self.get_element(target)
        items = self._client.list_af_attributes(target.af_element_ref, max_count=count)
        refs = set()
        for item in items:
            ref = item.get("WebId")
            if not isinstance(ref, str) or not ref.strip() or ref in refs:
                raise PiClientError("AF attribute list has missing or duplicate identity", failure_code=SourceFailureCode.CONTRACT_INVALID)
            refs.add(ref)
            self._client.require_resource_link(item, "Element", f"/elements/{quote(target.af_element_ref, safe='')}")
        return items

    def get_attribute(self, target: GovernedAfTarget, attribute_ref: str) -> dict:
        validate_governed_af_target(target)
        if not isinstance(attribute_ref, str) or not attribute_ref.strip() or attribute_ref != attribute_ref.strip():
            raise PiClientError("an explicit attribute reference is required")
        # No arbitrary attribute can reach value/history merely by presenting
        # an unrelated VERIFIED element. Only the bounded direct list is usable.
        items = self.list_attributes(target)
        if not any(item["WebId"] == attribute_ref for item in items):
            raise PiClientError("attribute is outside bounded governed element listing", failure_code=SourceFailureCode.CONTRACT_INVALID)
        metadata = self._client.get_af_attribute(attribute_ref)
        if metadata.get("WebId") != attribute_ref:
            raise PiClientError("AF attribute identity mismatch", failure_code=SourceFailureCode.CONTRACT_INVALID)
        self._client.require_resource_link(metadata, "Element", f"/elements/{quote(target.af_element_ref, safe='')}")
        return metadata

    def get_snapshot(self, target: GovernedAfTarget, attribute_ref: str) -> Snapshot:
        return self.get_evidence_snapshot(target, attribute_ref)[1]

    def get_evidence_snapshot(self, target: GovernedAfTarget, attribute_ref: str) -> tuple[str | None, Snapshot]:
        """Source-returned name and typed snapshot, with one bounded lineage check."""
        attribute = self.get_attribute(target, attribute_ref)
        payload = self._client.get_af_attribute_value(attribute)
        snapshot = extract_snapshot(payload, attribute_ref, units=_source_units({}, attribute.get("DefaultUnitsName")))
        if snapshot.source_timestamp is None:
            raise PiClientError("governed snapshot requires an aware source timestamp", failure_code=SourceFailureCode.CONTRACT_INVALID)
        name = attribute.get("Name")
        return name if isinstance(name, str) else None, snapshot

    def get_recorded(self, target: GovernedAfTarget, attribute_ref: str, *,
                     start_time: str, end_time: str, max_count: int = 20) -> list[TimeseriesPoint]:
        validate_governed_af_target(target)
        start, end = _window(start_time, end_time)
        count = _limit(max_count, 20)
        attribute = self.get_attribute(target, attribute_ref)
        payload = self._client.get_af_attribute_recorded(
            attribute, start_time=start_time, end_time=end_time, max_count=count)
        points = extract_recorded(payload, attribute_ref)
        if len(points) != len(payload["Items"]) or any(not start <= point.timestamp <= end for point in points):
            raise PiClientError("governed history has missing or out-of-window timestamps")
        # AF units are evidence when a stream response omits them.
        fallback_units = _source_units({}, attribute.get("DefaultUnitsName"))
        if fallback_units:
            points = [replace(point, units=point.units or fallback_units) for point in points]
        return points
