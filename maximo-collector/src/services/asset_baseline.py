"""Bounded, auditable initial MXAPIASSET baseline repair.

This module owns the operator workflow for MX-011C. It deliberately reuses
the existing ``SyncService`` and ``equipment_from_payload`` path; it does not
create a second Equipment mapper or touch Reliability Mart tables.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from src.adapters.maximo.auth import MaximoAuth
from src.adapters.maximo.mappers import equipment_from_payload
from src.adapters.maximo.oslc_client import (
    ASSET_DETAIL_FIELDS,
    OslcClient,
    OslcPaginationLimitError,
    oslc_pop_text,
)
from src.api.app import sync_config_for
from src.config import MaximoConfig
from src.repositories.database import Database
from src.repositories.store import CollectorStore
from src.services.asset_registry_reconciliation import (
    RegistrySnapshot,
    load_local_reconciliation_input,
    parse_registry_file,
    reconcile_registry,
)
from src.services.sync import ObjectSyncConfig, SyncService


EXPECTED_REGISTRY_SHA256 = "aa0bd8fd22275aea3ecf8654ee37878106123b7dbdf58135fb783e853ee66a5f"
EXPECTED_REGISTRY_ROWS = 845
ASSET_BASELINE_PAGE_SIZE = 50
ASSET_BASELINE_MAX_PAGES = 200
ASSET_BASELINE_REQUEST_BUDGET = 150


class AssetBaselineBlocked(RuntimeError):
    """A safe precondition prevented the baseline from starting."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def validate_registry_snapshot(
    registry: RegistrySnapshot,
    *,
    expected_sha256: str = EXPECTED_REGISTRY_SHA256,
    expected_rows: int = EXPECTED_REGISTRY_ROWS,
) -> None:
    """Reject an unexpected production report before any Maximo request."""
    unique_assets = {row.asset for row in registry.records if row.asset}
    if registry.sha256 != expected_sha256:
        raise AssetBaselineBlocked("REGISTRY_FINGERPRINT_MISMATCH")
    if registry.rows != expected_rows or len(unique_assets) != expected_rows:
        raise AssetBaselineBlocked("REGISTRY_SHAPE_MISMATCH")


def asset_baseline_config(
    runtime_config: MaximoConfig | None = None,
    *,
    page_size: int = ASSET_BASELINE_PAGE_SIZE,
    max_pages: int = ASSET_BASELINE_MAX_PAGES,
) -> ObjectSyncConfig:
    """Return the explicit, cursor-safe MXAPIASSET initial-baseline config."""
    runtime = runtime_config or MaximoConfig.from_environment()
    if page_size < 1 or page_size > runtime.page_size:
        raise ValueError("asset baseline page_size is outside the configured Maximo bound")
    if max_pages < 1:
        raise ValueError("asset baseline max_pages must be at least 1")
    return replace(
        sync_config_for("mxapiasset"),
        page_size=page_size,
        max_pages=max_pages,
        select=tuple(ASSET_DETAIL_FIELDS),
        watermark_query=False,
        cursor_requires_zero_errors=True,
    )


def _source_where(config: ObjectSyncConfig) -> str:
    where = config.scope_clause
    for field, value in config.required_values:
        where = f'{where} and {field}="{value}"'
    return where


def probe_asset_projection(client: Any, config: ObjectSyncConfig) -> dict[str, Any]:
    """Map one bounded page without persisting it.

    ``max_pages=1`` can legitimately raise ``OslcPaginationLimitError`` when
    the source advertises another page. That is a successful bounded probe;
    the full run is responsible for proving exhaustion.
    """
    before = dict(client.request_telemetry)
    rows = mapped = missing_required = invalid_scope = mapping_errors = 0
    truncated = False
    try:
        for raw in client.iterate(
            config.object_structure,
            where=_source_where(config),
            required_scope=config.scope_clause,
            select=list(config.select),
            order_by=config.order_by,
            # Probe the actual repair page size so a response-cap failure is
            # discovered before any local row is written.
            page_size=config.page_size or ASSET_BASELINE_PAGE_SIZE,
            max_pages=1,
            identity_field="assetnum",
        ):
            rows += 1
            assetnum = oslc_pop_text(raw, "assetnum")
            siteid = oslc_pop_text(raw, "siteid")
            eq11 = oslc_pop_text(raw, "eq11")
            if not assetnum or not eq11:
                missing_required += 1
            if siteid != "BSR" or eq11 != "CS01":
                invalid_scope += 1
            try:
                equipment_from_payload(raw)
                mapped += 1
            except Exception:  # aggregate-only probe result
                mapping_errors += 1
    except OslcPaginationLimitError:
        truncated = True
    after = dict(client.request_telemetry)
    before_requests = int(before.get("business_requests", 0) or 0)
    after_requests = int(after.get("business_requests", 0) or 0)
    before_details = int(before.get("detail_requests", 0) or 0)
    after_details = int(after.get("detail_requests", 0) or 0)
    detail_requests = max(after_details - before_details, 0)
    return {
        "rows": rows,
        "mapped": mapped,
        "missing_required": missing_required,
        "invalid_scope": invalid_scope,
        "mapping_errors": mapping_errors,
        "pagination_truncated": truncated,
        "business_requests": max(after_requests - before_requests, 0),
        "detail_requests": detail_requests,
        "projection_safe": detail_requests == 0,
        "passed": bool(
            rows
            and mapped == rows
            and missing_required == 0
            and invalid_scope == 0
            and mapping_errors == 0
            and detail_requests == 0
        ),
    }


def _coverage_summary(report: dict[str, Any]) -> dict[str, Any]:
    coverage = report["registry_reconciliation"]
    recent = report["work_order_relationships"]["recent_local_period"]
    recent_relationships = recent.get("relationship_distribution", {}) if recent.get("available") else {}
    return {
        "collector_equipment": report["collector_equipment"]["total"],
        "registry_assets": coverage["registry_assets_total"],
        "registry_matched": coverage["exact_equipment_matches"],
        "registry_missing": coverage["registry_assets_missing_from_collector"],
        "registry_coverage_percentage": coverage["exact_match_percentage"],
        "registry_parents_present": coverage["parents_matching_collector"],
        "registry_parents_missing": coverage["parents_missing_from_collector"],
        "recent_rows": recent.get("rows", 0),
        "recent_direct_registry_target_missing": recent_relationships.get(
            "direct_registry_target_missing_from_collector", 0
        ),
        "recent_non_registry_target_missing": recent_relationships.get(
            "equipment_target_missing_from_collector", 0
        ),
        "historical_direct_registry_target_missing": report["work_order_relationships"]["all"].get(
            "direct_registry_target_missing_from_collector", 0
        ),
    }


def run_asset_baseline(
    registry_path: str | Path,
    database: Database,
    *,
    client: Any | None = None,
    dry_run: bool = False,
    page_size: int = ASSET_BASELINE_PAGE_SIZE,
    max_pages: int = ASSET_BASELINE_MAX_PAGES,
    request_budget: int = ASSET_BASELINE_REQUEST_BUDGET,
) -> dict[str, Any]:
    """Run the bounded current Asset baseline and return sanitized aggregates."""
    registry = parse_registry_file(registry_path)
    validate_registry_snapshot(registry)
    local_before = load_local_reconciliation_input(database)
    pre_report = reconcile_registry(registry, local_before)
    store = CollectorStore(database)

    cursor_before = {
        "mxapiasset": store.get_cursor("mxapiasset"),
        "mxasset": store.get_cursor("mxasset"),
    }
    if cursor_before["mxapiasset"] is not None:
        raise AssetBaselineBlocked("MXAPIASSET_CURSOR_ALREADY_EXISTS")

    runtime = MaximoConfig.from_environment()
    config = asset_baseline_config(runtime, page_size=page_size, max_pages=max_pages)
    if client is None:
        client = OslcClient(runtime, MaximoAuth(runtime), request_budget=request_budget)
    probe = probe_asset_projection(client, config)
    if not probe["passed"]:
        raise AssetBaselineBlocked("ASSET_PROJECTION_PROBE_FAILED")

    result: dict[str, Any] = {
        "status": "DRY_RUN" if dry_run else "RUNNING",
        "registry": {
            "format": registry.format,
            "sheet": registry.sheet,
            "rows": registry.rows,
            "unique_assets": len({row.asset for row in registry.records if row.asset}),
            "sha256": registry.sha256,
        },
        "pre_repair": _coverage_summary(pre_report),
        "cursor_before": {
            name: value.isoformat() if value else None for name, value in cursor_before.items()
        },
        "source": {
            "object_structure": config.object_structure,
            "scope": config.scope_clause,
            "required_values": dict(config.required_values),
            "order_by": config.order_by,
            "page_size": config.page_size,
            "max_pages": config.max_pages,
            "request_budget": request_budget,
            "projection": list(config.select),
        },
        "probe": probe,
    }
    if dry_run:
        result["status"] = "DRY_RUN"
        result["complete"] = False
        result["writes"] = {"equipment_inserted": 0, "equipment_updated": 0, "equipment_upserted": 0, "skipped": 0, "errors": 0}
        result["request_telemetry"] = dict(client.request_telemetry)
        return result

    stats = SyncService(client, store, site_id=runtime.site_id).sync(config)
    local_after = load_local_reconciliation_input(database)
    post_report = reconcile_registry(registry, local_after)
    post_summary = _coverage_summary(post_report)
    post_history = post_report["sync_history"]
    cursor_after = post_history["cursor"]["mxapiasset"]
    result.update(
        {
            "status": "COMPLETE" if stats.complete and post_summary["registry_missing"] == 0 else "PARTIAL",
            "complete": stats.complete,
            "pages": int(getattr(client, "last_iteration_pages", 0) or 0),
            "rows_seen": stats.rows_seen,
            "stats": {
                "upserted": stats.upserted,
                "inserted": getattr(stats, "inserted", 0),
                "updated": getattr(stats, "updated", 0),
                "unchanged": getattr(stats, "unchanged", 0),
                "skipped": stats.skipped,
                "errors": stats.errors,
                "pagination_error": stats.pagination_error,
                "watermark": stats.watermark.isoformat() if stats.watermark else None,
            },
            "post_repair": post_summary,
            "cursor_after": cursor_after,
            "collect_run": post_history["latest_by_object"].get("mxapiasset"),
            "request_telemetry": dict(client.request_telemetry),
            "writes": {
                "equipment_inserted": getattr(stats, "inserted", 0),
                "equipment_updated": getattr(stats, "updated", 0),
                "equipment_upserted": stats.upserted,
                "skipped": stats.skipped,
                "errors": stats.errors,
                "deleted": 0,
                "mart": 0,
            },
        }
    )
    return result
