"""Delta-sync engine: pull verified OSLC objects into the collector store.

Ported from the reliability-cockpit sync engine this collector replaces.
Full sync on first run; incremental afterwards via the per-object watermark
(changedate / statusdate). A row that fails to map is logged and skipped.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from src.adapters.maximo.oslc_client import OslcClient, OslcPaginationError, oslc_timestamp
from src.domain import models as domain
from src.repositories.store import CollectorStore

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class ObjectSyncConfig:
    object_structure: str
    entity_name: str
    mapper: Callable[[dict], object]
    watermark_field: str | None = "changedate"
    order_by: str | None = "-changedate"
    scope_clause: str = 'siteid="BSR"'
    compare_column: str | None = "source_changed_at"
    prefix_field: str | None = None
    allowed_prefixes: tuple[str, ...] = ()
    required_values: tuple[tuple[str, str], ...] = ()
    batch_size: int = 1
    select: tuple[str, ...] = ()
    page_size: int | None = None


@dataclass
class SyncStats:
    object_structure: str
    mode: str = "full"  # full | incremental | partial
    rows_seen: int = 0
    upserted: int = 0
    skipped: int = 0
    errors: int = 0
    duplicate_ids: int = 0
    complete: bool = True
    pagination_error: str | None = None
    watermark: datetime | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class SyncService:
    """Synchronizes Maximo objects into the collector Postgres store."""

    def __init__(self, client: OslcClient, store: CollectorStore, site_id: str = "BSR"):
        if site_id != "BSR":
            raise ValueError("collector sync is restricted to site BSR")
        self._client = client
        self._store = store
        self._site_id = site_id

    def sync(self, config: ObjectSyncConfig) -> SyncStats:
        stats = SyncStats(object_structure=config.object_structure)
        watermark = None
        if config.watermark_field:
            watermark = self._store.get_cursor(config.object_structure)
            if watermark is not None:
                stats.mode = "incremental"

        where = config.scope_clause
        if config.prefix_field and config.allowed_prefixes:
            # Maximo's OSLC parser on this instance rejects ``like``
            # (BMXAA8744E). Its verified wildcard form is an ``in`` list.
            prefix_values = ",".join(f'"{prefix}%"' for prefix in config.allowed_prefixes)
            where = f"{where} and {config.prefix_field} in [{prefix_values}]"
        for field_name, expected_value in config.required_values:
            where = f'{where} and {field_name}="{expected_value}"'
        if stats.mode == "incremental" and watermark is not None:
            iso = watermark.isoformat(timespec="seconds")
            where = f'{where} and {config.watermark_field} >= "{iso}"'

        seen = 0
        last_change: datetime | None = None
        pending: list[object] = []
        seen_entity_ids: set[str] = set()

        def flush_pending() -> None:
            if not pending:
                return
            if config.batch_size > 1 and hasattr(self._store, "upsert_many_for"):
                unique: dict[object, object] = {}
                for index, entity in enumerate(pending):
                    entity_id = getattr(entity, "id", None)
                    unique[entity_id if entity_id is not None else ("row", index)] = entity
                duplicate_count = len(pending) - len(unique)
                if duplicate_count:
                    stats.skipped += duplicate_count
                self._store.upsert_many_for(config.entity_name, list(unique.values()))
                pending_count = len(unique)
            else:
                for queued in pending:
                    self._store.upsert_for(config.entity_name, queued)
                pending_count = len(pending)
            stats.upserted += pending_count
            pending.clear()

        try:
            for raw in self._client.iterate(
                config.object_structure,
                where=where,
                required_scope=config.scope_clause,
                select=list(config.select) or None,
                order_by=config.order_by,
                page_size=config.page_size,
                identity_field=config.prefix_field,
            ):
                seen += 1
                if config.prefix_field and config.allowed_prefixes:
                    raw_value = str(raw.get(config.prefix_field) or "").strip().upper()
                    if not raw_value.startswith(config.allowed_prefixes):
                        stats.skipped += 1
                        LOG.warning(
                            "skip %s row outside configured prefix scope",
                            config.object_structure,
                        )
                        continue
                invalid_required_value = next(
                    (
                        (field_name, expected_value)
                        for field_name, expected_value in config.required_values
                        if str(raw.get(field_name) or "").strip().upper() != expected_value.upper()
                    ),
                    None,
                )
                if invalid_required_value:
                    field_name, expected_value = invalid_required_value
                    stats.skipped += 1
                    LOG.warning(
                        "skip %s row outside required %s=%s scope",
                        config.object_structure, field_name, expected_value,
                    )
                    continue
                change = None
                if config.watermark_field:
                    change = oslc_timestamp(raw.get(config.watermark_field))
                    if change is not None and (last_change is None or change > last_change):
                        last_change = change
                try:
                    entity = config.mapper(raw)
                    entity_id = str(
                        getattr(entity, "id", None)
                        or (entity.get("id") if isinstance(entity, dict) else None)
                        or (entity.get("wonum") if isinstance(entity, dict) else None)
                        or ""
                    ).strip()
                    if config.entity_name == "work_order":
                        allowed = tuple(prefix.upper() for prefix in config.allowed_prefixes)
                        if not entity_id or not entity_id.upper().startswith(allowed):
                            stats.skipped += 1
                            LOG.warning(
                                "skip %s mapped row outside configured prefix scope",
                                config.object_structure,
                            )
                            continue
                    if entity_id and entity_id in seen_entity_ids:
                        stats.duplicate_ids += 1
                        stats.skipped += 1
                        continue
                    if entity_id:
                        seen_entity_ids.add(entity_id)
                    if (
                        config.compare_column
                        and change is not None
                        and self._store.is_unchanged(
                            config.entity_name,
                            entity_id or None,
                            config.compare_column,
                            change,
                        )
                    ):
                        stats.skipped += 1
                        continue
                    pending.append(entity)
                    if len(pending) >= max(1, config.batch_size):
                        flush_pending()
                    if config.entity_name == "equipment":
                        self._store.record_equipment_status(entity)
                except Exception as error:  # noqa: BLE001 — one bad row must not abort the sync
                    stats.skipped += 1
                    stats.errors += 1
                    LOG.warning(
                        "skip %s row outcome=skipped error_class=%s",
                        config.object_structure,
                        type(error).__name__,
                    )
        except OslcPaginationError as error:
            # Rows already yielded are valid local progress. Flush them, but
            # never move a watermark for a traversal that was not complete.
            flush_pending()
            stats.complete = False
            stats.mode = "partial"
            stats.pagination_error = type(error).__name__
            stats.errors += 1
            LOG.warning(
                "partial %s sync reason=%s pages=%d",
                config.object_structure,
                type(error).__name__,
                error.pages,
            )
        flush_pending()
        stats.rows_seen = seen
        stats.watermark = last_change or watermark
        stats.finished_at = datetime.now(timezone.utc)
        if config.watermark_field and stats.complete:
            self._store.set_cursor(config.object_structure, stats.watermark, seen)
        self._store.record_run(stats)
        LOG.info(
            "%s sync %s: %d seen, %d upserted, %d skipped, watermark=%s",
            stats.mode, stats.object_structure, seen, stats.upserted, stats.skipped, stats.watermark,
        )
        return stats
