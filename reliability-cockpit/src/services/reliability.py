"""Vendor-neutral Reliability Mart read services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.repositories.mart_reader import MartQueryRepository, QueryPage
from src.services.asset_af_mapping import AssetAfMappingResolution, mapping_from_row, resolve_asset_af_mapping


@dataclass(frozen=True)
class TimelineEvent:
    event_id: str
    event_type: str
    event_at: datetime | None
    summary: str | None
    status: str | None
    canonical_ref: str


class ReliabilityQueryService:
    def __init__(self, repository: MartQueryRepository):
        self.repository = repository

    def asset_context(self, canonical_id: str, section_limit: int = 5) -> dict[str, Any] | None:
        asset = self.repository.get_asset(canonical_id)
        if asset is None:
            return None
        bounded = min(max(section_limit, 1), 10)
        return {
            "asset": asset,
            "maintenance": self.repository.list_maintenance(asset_ref=canonical_id, limit=bounded),
            "fmea": self.repository.list_fmea_workspace(asset_ref=canonical_id, limit=bounded),
            "health": self.repository.list_health(asset_ref=canonical_id, limit=bounded),
            "overhauls": self.repository.list_overhauls(asset_ref=canonical_id, limit=bounded),
            "rcfa_relationship_status": "UNRESOLVED",
            "relationship_health": self.repository.integrity_summary(),
        }

    def timeline(self, canonical_id: str, offset: int = 0, limit: int = 50) -> QueryPage:
        if self.repository.get_asset(canonical_id) is None:
            return QueryPage([], 0, offset, limit)
        maintenance = self.repository.list_maintenance(asset_ref=canonical_id, limit=limit).items
        fmea = self.repository.list_fmea(asset_ref=canonical_id, limit=limit).items
        health = self.repository.list_health(asset_ref=canonical_id, limit=limit).items
        overhauls = self.repository.list_overhauls(asset_ref=canonical_id, limit=limit).items
        events: list[TimelineEvent] = []
        for row in maintenance:
            events.append(TimelineEvent(row.canonical_id, "MAINTENANCE", row.actual_start or row.source_changed_at, row.event_type, row.status, row.canonical_id))
        for row in fmea:
            events.append(TimelineEvent(row.canonical_id, "FMEA", row.status_changed_at or row.source_updated_at, row.description, row.lifecycle_status, row.canonical_id))
        for row in health:
            events.append(TimelineEvent(row.canonical_id, "ASSET_HEALTH", row.status_changed_at or row.source_updated_at or row.source_created_at, row.description, row.lifecycle_status, row.canonical_id))
        for row in overhauls:
            if row.asset_ref is not None:
                events.append(TimelineEvent(row.canonical_id, "OVERHAUL", row.actual_start_at or row.planned_start_at or row.source_updated_at, row.source_number, row.lifecycle_status, row.canonical_id))
        events.sort(key=lambda item: (item.event_at is not None, item.event_at or datetime.min), reverse=True)
        total = len(events)
        return QueryPage(events[offset:offset + limit], total, offset, limit)

    def asset_af_mapping(self, canonical_id: str) -> AssetAfMappingResolution:
        rows = self.repository.list_asset_af_mappings(canonical_id)
        return resolve_asset_af_mapping(canonical_id, [mapping_from_row(row) for row in rows])
