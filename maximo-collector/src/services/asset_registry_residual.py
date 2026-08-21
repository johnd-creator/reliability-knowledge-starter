"""Bounded completion of the current registered Asset projection.

This workflow deliberately does not claim that the broad MXAPIASSET technical
population is complete. It derives the residual business registry membership
locally, verifies each residual by exact identity, and reuses the existing
Equipment mapper/store path.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import requests

from src.adapters.maximo.auth import MaximoAuth
from src.adapters.maximo.mappers import equipment_from_payload
from src.adapters.maximo.oslc_client import (
    ASSET_DETAIL_FIELDS,
    OslcClient,
    OslcError,
    OslcPaginationLimitError,
    oslc_pop_text,
)
from src.api.app import sync_config_for
from src.config import MaximoConfig
from src.repositories.database import Database
from src.repositories.store import CollectorStore
from src.services.asset_baseline import (
    EXPECTED_REGISTRY_ROWS,
    EXPECTED_REGISTRY_SHA256,
    validate_registry_snapshot,
)
from src.services.asset_registry_reconciliation import (
    LocalReconciliationInput,
    RegistrySnapshot,
    load_local_reconciliation_input,
    normalize_identifier,
    parse_registry_file,
    reconcile_registry,
)


PRIMARY_REQUEST_LIMIT = 30
TOTAL_REQUEST_LIMIT = 50
EXACT_PAGE_SIZE = 2


class AssetRegistryResidualBlocked(RuntimeError):
    """A safe precondition prevented residual repair from starting."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class ResidualLookup:
    outcome: str
    requests: int = 0
    detail_requests: int = 0
    equipment: object | None = None
    reason: str | None = None


def derive_residual_ids(
    registry: RegistrySnapshot,
    local: LocalReconciliationInput,
) -> tuple[str, ...]:
    """Derive registry IDs absent from local Equipment without exposing them."""
    registry_ids = {
        normalized
        for row in registry.records
        if (normalized := normalize_identifier(row.asset)) is not None
    }
    equipment_ids = {
        normalized
        for row in local.equipment
        if (normalized := normalize_identifier(row.id)) is not None
    }
    return tuple(sorted(registry_ids - equipment_ids))


def _exact_config(object_structure: str) -> Any:
    """Build a one-page exact lookup config using the approved projection."""
    return replace(
        sync_config_for(object_structure),
        page_size=EXACT_PAGE_SIZE,
        max_pages=1,
        select=tuple(ASSET_DETAIL_FIELDS),
        order_by=None,
        watermark_query=False,
    )


def _where_for(config: Any, requested_id: str) -> str:
    # Registry identifiers are normalized before this point. Escaping keeps
    # the exact predicate bounded even if a future export contains a quote.
    escaped = requested_id.replace("\\", "\\\\").replace('"', '\\"')
    where = config.scope_clause
    for field, value in config.required_values:
        where = f'{where} and {field}="{value}"'
    return f'{where} and assetnum="{escaped}"'


def _telemetry_delta(client: Any, before: dict[str, Any]) -> tuple[int, int]:
    after = dict(getattr(client, "request_telemetry", {}))
    requests_after = int(after.get("business_requests", 0) or 0)
    details_after = int(after.get("detail_requests", 0) or 0)
    return (
        max(requests_after - int(before.get("business_requests", 0) or 0), 0),
        max(details_after - int(before.get("detail_requests", 0) or 0), 0),
    )


def lookup_residual(
    client: Any,
    object_structure: str,
    requested_id: str,
    *,
    map_result: bool = True,
) -> ResidualLookup:
    """Perform one exact, one-page identity lookup.

    The requested identity is never included in the returned aggregate
    result. A pagination continuation is treated as ambiguity because this
    workflow is intentionally forbidden from enumerating a residual.
    """
    config = _exact_config(object_structure)
    before = dict(getattr(client, "request_telemetry", {}))
    rows: list[dict[str, Any]] = []
    try:
        for raw in client.iterate(
            config.object_structure,
            where=_where_for(config, requested_id),
            required_scope=config.scope_clause,
            select=list(config.select),
            order_by=None,
            page_size=EXACT_PAGE_SIZE,
            max_pages=1,
            identity_field="assetnum",
        ):
            rows.append(dict(raw))
    except OslcPaginationLimitError:
        requests_used, detail_requests = _telemetry_delta(client, before)
        return ResidualLookup(
            "SOURCE_IDENTITY_AMBIGUITY",
            requests=requests_used,
            detail_requests=detail_requests,
        )
    except (OslcError, requests.RequestException) as error:
        requests_used, detail_requests = _telemetry_delta(client, before)
        return ResidualLookup(
            "SOURCE_ERROR",
            requests=requests_used,
            detail_requests=detail_requests,
            reason=type(error).__name__,
        )

    requests_used, detail_requests = _telemetry_delta(client, before)
    if not rows:
        return ResidualLookup(
            "NOT_FOUND",
            requests=requests_used,
            detail_requests=detail_requests,
        )

    returned_ids = {
        normalized
        for row in rows
        if (normalized := normalize_identifier(oslc_pop_text(row, "assetnum"))) is not None
    }
    if len(rows) != 1 or returned_ids != {requested_id}:
        return ResidualLookup(
            "IDENTITY_MISMATCH" if requested_id not in returned_ids else "SOURCE_IDENTITY_AMBIGUITY",
            requests=requests_used,
            detail_requests=detail_requests,
        )

    row = rows[0]
    if oslc_pop_text(row, "siteid") != "BSR" or oslc_pop_text(row, "eq11") != "CS01":
        return ResidualLookup(
            "SCOPE_MISMATCH",
            requests=requests_used,
            detail_requests=detail_requests,
        )

    if not map_result:
        return ResidualLookup(
            "FOUND",
            requests=requests_used,
            detail_requests=detail_requests,
        )

    try:
        equipment = equipment_from_payload(row)
    except Exception:
        return ResidualLookup(
            "MAPPING_ERROR",
            requests=requests_used,
            detail_requests=detail_requests,
        )
    return ResidualLookup(
        "FOUND",
        requests=requests_used,
        detail_requests=detail_requests,
        equipment=equipment,
    )


def _coverage_summary(report: dict[str, Any]) -> dict[str, Any]:
    coverage = report["registry_reconciliation"]
    recent = report["work_order_relationships"]["recent_local_period"]
    relationships = recent.get("relationship_distribution", {}) if recent.get("available") else {}
    return {
        "collector_equipment": report["collector_equipment"]["total"],
        "registry_assets": coverage["registry_assets_total"],
        "registry_matched": coverage["exact_equipment_matches"],
        "registry_missing": coverage["registry_assets_missing_from_collector"],
        "registry_coverage_percentage": coverage["exact_match_percentage"],
        "registry_parents_present": coverage["parents_matching_collector"],
        "registry_parents_missing": coverage["parents_missing_from_collector"],
        "recent_rows": recent.get("rows", 0),
        "recent_direct_registry_target_missing": relationships.get(
            "direct_registry_target_missing_from_collector", 0
        ),
        "recent_non_registry_target_missing": relationships.get(
            "equipment_target_missing_from_collector", 0
        ),
        "historical_direct_registry_target_missing": report["work_order_relationships"]["all"].get(
            "direct_registry_target_missing_from_collector", 0
        ),
    }


def _new_client(runtime: MaximoConfig, budget: int) -> OslcClient:
    return OslcClient(runtime, MaximoAuth(runtime), request_budget=budget)


def run_asset_registry_residual_repair(
    registry_path: str | Path,
    database: Database,
    *,
    client: Any | None = None,
    fallback_client: Any | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Complete only current registry membership using bounded exact lookups."""
    registry = parse_registry_file(registry_path)
    validate_registry_snapshot(
        registry,
        expected_sha256=EXPECTED_REGISTRY_SHA256,
        expected_rows=EXPECTED_REGISTRY_ROWS,
    )
    local_before = load_local_reconciliation_input(database)
    pre_report = reconcile_registry(registry, local_before)
    residual_ids = derive_residual_ids(registry, local_before)
    store = CollectorStore(database)
    cursor_before = {
        "mxapiasset": store.get_cursor("mxapiasset"),
        "mxasset": store.get_cursor("mxasset"),
    }
    if cursor_before["mxapiasset"] is not None:
        raise AssetRegistryResidualBlocked("MXAPIASSET_CURSOR_ALREADY_EXISTS")

    result: dict[str, Any] = {
        "status": "RUNNING",
        "registry": {
            "format": registry.format,
            "sheet": registry.sheet,
            "rows": registry.rows,
            "unique_assets": len({row.asset for row in registry.records if row.asset}),
            "sha256": registry.sha256,
        },
        "pre_repair": _coverage_summary(pre_report),
        "residuals_derived": len(residual_ids),
        "source": {
            "primary": "MXAPIASSET",
            "fallback": "MXASSET",
            "scope": 'siteid="BSR"',
            "required": 'eq11="CS01"',
            "page_size": EXACT_PAGE_SIZE,
            "max_pages": 1,
            "primary_request_ceiling": PRIMARY_REQUEST_LIMIT,
            "total_request_ceiling": TOTAL_REQUEST_LIMIT,
            "business_methods": ["GET"],
        },
        "cursor_before": {
            name: value.isoformat() if value else None for name, value in cursor_before.items()
        },
    }

    if not residual_ids:
        result["status"] = "COMPLETE"
        result["dry_run"] = dry_run
        result["post_repair"] = _coverage_summary(pre_report)
        result["writes"] = {"inserted": 0, "updated": 0, "deleted": 0}
        result["request_audit"] = {"primary": 0, "fallback": 0, "total": 0, "detail_requests": 0}
        result["cursor_after"] = {"mxapiasset": None, "mxasset": None}
        return result

    runtime = MaximoConfig.from_environment()
    primary = client or _new_client(runtime, PRIMARY_REQUEST_LIMIT)
    fallback = fallback_client
    primary_requests = fallback_requests = detail_requests = 0
    found = not_found = identity_ambiguity = scope_mismatch = mapping_errors = 0
    fallback_found = fallback_not_found = 0
    inserted = updated = 0
    stopped_reason: str | None = None

    for residual_id in residual_ids:
        if primary_requests >= PRIMARY_REQUEST_LIMIT:
            stopped_reason = "PRIMARY_REQUEST_CEILING"
            break
        lookup = lookup_residual(primary, "mxapiasset", residual_id)
        primary_requests += lookup.requests
        detail_requests += lookup.detail_requests
        if primary_requests > PRIMARY_REQUEST_LIMIT:
            stopped_reason = "PRIMARY_REQUEST_CEILING"
            break
        if lookup.outcome == "FOUND":
            found += 1
            if not dry_run:
                outcome = store.upsert_equipment(lookup.equipment)
                if outcome == "inserted":
                    inserted += 1
                elif outcome == "updated":
                    updated += 1
            continue
        if lookup.outcome == "NOT_FOUND":
            not_found += 1
            if fallback is None:
                remaining_budget = TOTAL_REQUEST_LIMIT - primary_requests
                if remaining_budget < 1:
                    stopped_reason = "TOTAL_REQUEST_CEILING"
                    break
                fallback = _new_client(runtime, remaining_budget)
            if primary_requests + fallback_requests >= TOTAL_REQUEST_LIMIT:
                stopped_reason = "TOTAL_REQUEST_CEILING"
                break
            fallback_lookup = lookup_residual(fallback, "mxasset", residual_id, map_result=False)
            fallback_requests += fallback_lookup.requests
            detail_requests += fallback_lookup.detail_requests
            if primary_requests + fallback_requests > TOTAL_REQUEST_LIMIT:
                stopped_reason = "TOTAL_REQUEST_CEILING"
                break
            if fallback_lookup.outcome == "FOUND":
                fallback_found += 1
            elif fallback_lookup.outcome == "NOT_FOUND":
                fallback_not_found += 1
            elif fallback_lookup.outcome == "SCOPE_MISMATCH":
                scope_mismatch += 1
                stopped_reason = "SCOPE_MISMATCH"
                break
            elif fallback_lookup.outcome in {"SOURCE_IDENTITY_AMBIGUITY", "IDENTITY_MISMATCH"}:
                identity_ambiguity += 1
                stopped_reason = fallback_lookup.outcome
                break
            else:
                stopped_reason = fallback_lookup.reason or fallback_lookup.outcome
                break
            continue
        if lookup.outcome == "SOURCE_IDENTITY_AMBIGUITY" or lookup.outcome == "IDENTITY_MISMATCH":
            identity_ambiguity += 1
            stopped_reason = lookup.outcome
            break
        if lookup.outcome == "SCOPE_MISMATCH":
            scope_mismatch += 1
            stopped_reason = "SCOPE_MISMATCH"
            break
        if lookup.outcome == "MAPPING_ERROR":
            mapping_errors += 1
            continue
        stopped_reason = lookup.reason or lookup.outcome
        break

    local_after = load_local_reconciliation_input(database)
    post_report = reconcile_registry(registry, local_after)
    post_summary = _coverage_summary(post_report)
    result.update(
        {
            "status": "DRY_RUN" if dry_run else (
                "COMPLETE" if post_summary["registry_missing"] == 0 and stopped_reason is None else "PARTIAL"
            ),
            "dry_run": dry_run,
            "post_repair": post_summary,
            "outcome": {
                "found_in_mxapiasset": found,
                "not_found_in_mxapiasset": not_found,
                "identity_ambiguity": identity_ambiguity,
                "scope_mismatch": scope_mismatch,
                "mapping_errors": mapping_errors,
                "found_in_mxasset": fallback_found,
                "not_found_in_mxasset": fallback_not_found,
                "stopped_reason": stopped_reason,
            },
            "request_audit": {
                "primary": primary_requests,
                "fallback": fallback_requests,
                "total": primary_requests + fallback_requests,
                "detail_requests": detail_requests,
                "primary_ceiling": PRIMARY_REQUEST_LIMIT,
                "total_ceiling": TOTAL_REQUEST_LIMIT,
                "request_ceiling_exceeded": primary_requests > PRIMARY_REQUEST_LIMIT
                or primary_requests + fallback_requests > TOTAL_REQUEST_LIMIT,
                "primary_telemetry": dict(getattr(primary, "request_telemetry", {})),
                "fallback_telemetry": dict(getattr(fallback, "request_telemetry", {})) if fallback else {},
            },
            "writes": {"inserted": inserted, "updated": updated, "deleted": 0},
            "cursor_after": {"mxapiasset": None, "mxasset": None},
            "collect_run_recorded": False,
            "full_technical_baseline_complete": False,
        }
    )
    return result
