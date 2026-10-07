"""Bounded newest-first WO acquisition; no speculative date predicates."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from src.adapters.maximo.oslc_client import (
    OslcError, OslcPaginationError, OslcPaginationLimitError,
    OslcRequestBudgetExceeded, oslc_timestamp,
)
from src.services.sync import SyncStats

LOG = logging.getLogger(__name__)


def sync_recent_work_orders(client, store, config, *, recovery_floor=None):
    """Advance only after ordered exhaustion or a fully validated cursor boundary.

    Missing routine cursors require explicit recovery; a recovery floor is a
    traversal boundary, never a cursor seed. Partial rows replay on restart.
    Entire pages are validated before writes/early stop, including out-of-prefix
    timestamps. No fallback to unordered traversal when ordering is rejected.
    """
    if (config.entity_name != "work_order" or config.object_structure != "mxwodetail"
            or config.order_by != "-changedate" or config.watermark_field != "changedate"
            or not config.allowed_prefixes or config.scope_clause != 'siteid="BSR"'
            or not config.cursor_requires_zero_errors):
        raise ValueError("WO recency requires verified ordering, BSR scope and strict cursor safety")
    cursor = store.get_cursor(config.object_structure)
    stats = SyncStats(config.object_structure, mode="incremental" if cursor else "full")
    evidence = stats.recency
    evidence.update(cursor_before=_iso(cursor), cursor_after=_iso(cursor),
                    source_rows_read=0, prefix_accepted=0, prefix_skipped=0,
                    newest_source_change=None, oldest_source_change=None,
                    pages=0, requests=0, stop_reason=None)
    evidence.update(recovery_floor=_iso(recovery_floor), page_cap=config.max_pages,
                    request_budget=config.request_limit, page_size=config.page_size)
    if cursor is None and recovery_floor is None:
        return _operational_stop(store, stats, "BOOTSTRAP_REQUIRED")
    cutoff = recovery_floor if recovery_floor is not None else cursor
    before_requests = client.request_telemetry["business_requests"]
    newest = oldest = previous = candidate = None
    identities = set()
    reason = "SOURCE_EXHAUSTED"
    where = config.scope_clause
    if config.prefix_query:
        values = ','.join(f'"{p}%"' for p in config.allowed_prefixes)
        where += f' and wonum in [{values}]'
    try:
        with client.bounded_requests(config.request_limit):
            for page in client.iterate_pages(
                config.object_structure, where=where, required_scope=config.scope_clause,
                select=list(config.select) or None, order_by="-changedate",
                page_size=config.page_size, max_pages=config.max_pages,
                identity_field="wonum", strict_members=True,
            ):
                evidence["pages"] += 1
                stats.rows_seen += len(page)
                evidence["prefix_accepted"] += sum(
                    str(raw.get("wonum") or "").strip().upper().startswith(config.allowed_prefixes)
                    for raw in page
                )
                evidence["prefix_skipped"] = stats.rows_seen - evidence["prefix_accepted"]
                changes = []
                # Validate the whole page, rather than trusting its first old row.
                for raw in page:
                    change = oslc_timestamp(raw.get("changedate"))
                    if change is None or change.tzinfo is None:
                        raise OslcError("missing or invalid change timestamp")
                    changes.append(change)
                    newest = change if newest is None else max(newest, change)
                    oldest = change if oldest is None else min(oldest, change)
                    if previous is not None and change > previous:
                        reason = "ORDER_VIOLATION"
                        raise OslcError("source did not honor descending changedate")
                    previous = change
                    if (str(raw.get("siteid") or "").upper() != "BSR"
                            or str(raw.get("orgid") or "").upper() != "IP"):
                        reason = "SCOPE_ERROR"
                        raise OslcError("source row violates BSR/IP scope")
                boundary = False
                for raw, change in zip(page, changes):
                    prefix_match = str(raw.get("wonum") or "").strip().upper().startswith(config.allowed_prefixes)
                    if change < cutoff:
                        boundary = True
                        stats.skipped += 1
                        continue
                    if not prefix_match:
                        stats.skipped += 1
                        continue
                    try:
                        entity = config.mapper(raw)
                        identity = str(getattr(entity, "id", "") or "").strip()
                        if not identity.upper().startswith(config.allowed_prefixes):
                            raise ValueError("invalid mapped WO identity")
                        if identity in identities:
                            stats.duplicate_ids += 1
                            stats.skipped += 1
                            continue
                        identities.add(identity)
                        if store.is_unchanged(config.entity_name, identity, config.compare_column, change):
                            stats.unchanged += 1
                            stats.skipped += 1
                        else:
                            outcome = store.upsert_for(config.entity_name, entity)
                            stats.upserted += 1
                            if outcome in ("inserted", "updated", "unchanged"):
                                setattr(stats, outcome, getattr(stats, outcome) + 1)
                        candidate = change if candidate is None else max(candidate, change)
                    except Exception:
                        reason = "MAPPING_OR_STORE_ERROR"
                        raise
                if boundary:
                    reason = "RECOVERY_FLOOR_REACHED" if recovery_floor is not None else (
                        "CURSOR_REACHED" if candidate and candidate > cursor else "NO_NEW_ROWS"
                    )
                    break
    except Exception as error:
        stats.complete = False
        stats.mode = "partial"
        stats.errors += 1
        stats.pagination_error = type(error).__name__
        if isinstance(error, OslcPaginationLimitError):
            reason = "PAGE_LIMIT"
        elif isinstance(error, OslcPaginationError):
            reason = "PAGINATION_ERROR"
        elif isinstance(error, OslcRequestBudgetExceeded):
            reason = "REQUEST_BUDGET"
        elif reason == "SOURCE_EXHAUSTED":
            reason = "SOURCE_ERROR"
        LOG.warning("WO recency partial reason=%s error_class=%s", reason, type(error).__name__)
    if recovery_floor is not None:
        evidence["recovery_floor_reached"] = stats.complete and oldest is not None and oldest <= recovery_floor
        if stats.complete and (not evidence["recovery_floor_reached"] or candidate is None):
            return _finish_unreconciled(client, store, stats, evidence, before_requests, newest, oldest)
        # Changes after this run started must remain eligible on the next cycle.
        if candidate is not None:
            candidate = min(candidate, stats.started_at)
    # No changes to a pre-existing watermark on any incomplete traversal.
    after = max(cursor, candidate) if cursor and candidate else candidate or cursor
    if stats.complete and after is not None:
        try:
            store.set_cursor(config.object_structure, after, stats.rows_seen)
        except Exception as error:
            stats.complete = False
            stats.mode = "partial"
            stats.errors += 1
            stats.pagination_error = type(error).__name__
            reason = "CURSOR_STORE_ERROR"
            after = cursor
    else:
        after = cursor
    stats.watermark = after
    stats.finished_at = datetime.now(timezone.utc)
    evidence.update(validated_pages=evidence["pages"], pages=client.last_iteration_pages,
                    source_rows_read=stats.rows_seen, cursor_after=_iso(after),
                    newest_source_change=_iso(newest), oldest_source_change=_iso(oldest),
                    requests=client.request_telemetry["business_requests"] - before_requests,
                    stop_reason=reason, complete=stats.complete)
    store.record_run(stats)
    LOG.info("WO recency %s", json.dumps(evidence, sort_keys=True))
    return stats


def _iso(value):
    return value.isoformat() if value is not None else None


def _operational_stop(store, stats, reason):
    stats.complete = False
    stats.mode = "partial"
    stats.finished_at = datetime.now(timezone.utc)
    stats.recency.update(stop_reason=reason, complete=False)
    store.record_run(stats)
    LOG.warning("WO recency %s", json.dumps(stats.recency, sort_keys=True))
    return stats


def _finish_unreconciled(client, store, stats, evidence, before_requests, newest, oldest):
    evidence.update(newest_source_change=_iso(newest), oldest_source_change=_iso(oldest),
                    validated_pages=evidence["pages"], pages=client.last_iteration_pages,
                    requests=client.request_telemetry["business_requests"] - before_requests,
                    source_rows_read=stats.rows_seen)
    return _operational_stop(store, stats, "RECOVERY_FLOOR_NOT_REACHED")


def bootstrap_recent_work_orders(client, store, config):
    """Explicit recovery, serialized and anchored before any source/local upsert.

    The durable floor lives in existing collect_run evidence, not sync_cursor.
    A retry reuses it even if partial progress raised the local WO maximum.
    """
    if not config.prefix_query or not 1 <= (config.page_size or 25) <= 25:
        raise ValueError("bootstrap requires verified prefix query and page size 1..25")
    if not 1 <= config.max_pages <= 1000 or not 1 <= config.request_limit <= 2000:
        raise ValueError("bootstrap requires explicit finite page/request ceilings")
    with store.work_order_recovery_lock() as acquired:
        if not acquired:
            return _operational_stop(store, SyncStats(config.object_structure), "BOOTSTRAP_BUSY")
        cursor = store.get_cursor(config.object_structure)
        if cursor is not None:
            stats = SyncStats(config.object_structure, watermark=cursor)
            stats.recency.update(cursor_before=_iso(cursor), cursor_after=_iso(cursor), requests=0, pages=0)
            return _operational_stop(store, stats, "BOOTSTRAP_NOT_REQUIRED")
        floor = store.prepare_work_order_recovery_floor()
        if floor is None or floor.tzinfo is None or floor > datetime.now(timezone.utc):
            stats = SyncStats(config.object_structure)
            stats.recency.update(cursor_before=None, cursor_after=None, requests=0, pages=0,
                                 recovery_floor=_iso(floor))
            return _operational_stop(store, stats, "BOOTSTRAP_BLOCKED")
        return sync_recent_work_orders(client, store, config, recovery_floor=floor)
