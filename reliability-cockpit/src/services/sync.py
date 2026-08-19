"""Pull-sync engine: fetch contract-shaped rows from the maximo-collector
API into the cockpit store.

The cockpit is a pure dashboard — it never talks to Maximo. Delta pulls use
the per-resource watermark (row source-changed timestamp); a full pull runs
when the cursor is absent. One bad row is logged and skipped.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.adapters.collector_client import CollectorClient, CollectorClientError, RESOURCES
from src.repositories.store import CockpitStore

LOG = logging.getLogger(__name__)


@dataclass
class SyncStats:
    resource: str
    mode: str = "full"  # full | incremental
    rows_seen: int = 0
    upserted: int = 0
    skipped: int = 0
    watermark: datetime | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class SyncService:
    """Pulls collector views into the cockpit Postgres store."""

    def __init__(self, client: CollectorClient, store: CockpitStore):
        self._client = client
        self._store = store

    def sync(self, resource: str) -> SyncStats:
        if resource not in RESOURCES:
            raise CollectorClientError(f"unknown resource: {resource}")
        stats = SyncStats(resource=resource)
        has_watermark = RESOURCES[resource][2]
        watermark = self._store.get_cursor(resource) if has_watermark else None
        if watermark is not None:
            stats.mode = "incremental"

        rows = self._client.pull(resource, changed_since=watermark)
        last_change: datetime | None = None
        for domain in rows:
            stats.rows_seen += 1
            changed = getattr(domain, "source_changed_at", None) or getattr(
                domain, "status_changed_at", None
            )
            if changed is not None and (last_change is None or changed > last_change):
                last_change = changed
            try:
                self._upsert(domain)
                stats.upserted += 1
            except Exception as error:  # noqa: BLE001 — one bad row never aborts
                stats.skipped += 1
                LOG.warning("skip %s row %s: %s", resource, getattr(domain, "id", "?"), error)
        stats.watermark = last_change or watermark
        stats.finished_at = datetime.now(timezone.utc)
        if has_watermark:
            self._store.set_cursor(resource, stats.watermark, stats.rows_seen)
        LOG.info(
            "%s pull %s: %d seen, %d upserted, %d skipped, watermark=%s",
            stats.mode, resource, stats.rows_seen, stats.upserted, stats.skipped, stats.watermark,
        )
        return stats

    def _upsert(self, domain: object) -> None:
        from src.domain.equipment import Equipment
        from src.domain.item import Item
        from src.domain.labor import Labor
        from src.domain.person import Person
        from src.domain.service_request import ServiceRequest
        from src.domain.work_order import WorkOrder

        if isinstance(domain, Equipment):
            self._store.upsert_equipment(domain)
        elif isinstance(domain, WorkOrder):
            self._store.upsert_work_order(domain)
        elif isinstance(domain, ServiceRequest):
            self._store.upsert_service_request(domain)
        elif isinstance(domain, Person):
            self._store.upsert_person(domain)
        elif isinstance(domain, Item):
            self._store.upsert_item(domain)
        elif isinstance(domain, Labor):
            self._store.upsert_labor(domain)
        else:
            raise TypeError(f"unsupported domain model: {type(domain).__name__}")
