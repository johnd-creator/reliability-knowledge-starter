"""Allowlisted read model for the Maximo Collector Data Explorer.

The Explorer deliberately reads the approved ``sources.maximo`` block that is
already stored alongside canonical Mart records. It never stores or returns a
complete OSLC response and never accepts arbitrary object/table names.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from src.repositories import mart_models as mart
from src.repositories.store import CollectorStore
from src.services.canonical import CANONICAL_CONFIGS
from src.services.mart import MartIntegrityAuditor

SITE = "BSR"
ORGANIZATION = "IP"


@dataclass(frozen=True)
class ExplorerResource:
    key: str
    label: str
    module: str
    source_object: str
    canonical_entity: str
    model: type
    changed_column: str
    primary_fields: tuple[str, ...]
    search_columns: tuple[str, ...]
    order_columns: Mapping[str, str]

    @property
    def selected_fields(self) -> tuple[str, ...]:
        return tuple(CANONICAL_CONFIGS[self.key].select)


SOURCE_APPLICATIONS = {
    "MXASSET": None,
    "MXWODETAIL": None,
    "IPFMEA": "RELIABILITY",
    "IPRCFA": "RELIABILITY",
    "IPBHM": "RELIABILITY",
    "IP_DOM_OH": "DOMINION",
}

RESOURCE_SPECS: dict[str, ExplorerResource] = {
    "MXASSET": ExplorerResource(
        "mxasset", "Asset", "Maximo core", "MXASSET", "asset_master", mart.AssetMasterMartOrm,
        "source_updated_at", ("source_asset_number", "status", "unit", "source_updated_at"),
        ("canonical_id", "source_asset_number", "description", "status", "unit", "asset_type"),
        {"updated_desc": "source_updated_at", "updated_asc": "source_updated_at", "status": "status", "source_number": "source_asset_number"},
    ),
    "MXWODETAIL": ExplorerResource(
        "mxwodetail", "Work Orders", "Maximo core", "MXWODETAIL", "maintenance_event", mart.MaintenanceEventMartOrm,
        "source_changed_at", ("work_order_id", "equipment_id", "status", "actual_start"),
        ("canonical_id", "id", "work_order_id", "equipment_id", "status", "event_type"),
        {"updated_desc": "source_changed_at", "updated_asc": "source_changed_at", "status": "status", "source_number": "work_order_id"},
    ),
    "IPFMEA": ExplorerResource(
        "ipfmea", "FMEA", "Reliability", "IPFMEA", "fmea_assessment", mart.FmeaAssessmentMartOrm,
        "source_updated_at", ("source_number", "asset_ref", "lifecycle_status", "revision", "source_updated_at"),
        ("canonical_id", "source_record_id", "source_number", "asset_ref", "lifecycle_status", "description", "failure_code_ref"),
        {"updated_desc": "source_updated_at", "updated_asc": "source_updated_at", "status": "lifecycle_status", "source_number": "source_number"},
    ),
    "IPRCFA": ExplorerResource(
        "iprcfa", "RCFA", "Reliability", "IPRCFA", "rcfa_analysis", mart.RcfaAnalysisMartOrm,
        "source_created_at", ("source_number", "lifecycle_status", "category", "source_created_at"),
        ("canonical_id", "source_record_id", "source_number", "lifecycle_status", "category"),
        {"updated_desc": "source_created_at", "updated_asc": "source_created_at", "status": "lifecycle_status", "source_number": "source_number"},
    ),
    "IPBHM": ExplorerResource(
        "ipbhm", "Asset Health / BHM", "Reliability", "IPBHM", "asset_health_assessment", mart.AssetHealthAssessmentMartOrm,
        "source_updated_at", ("source_record_id", "asset_ref", "lifecycle_status", "function_description", "source_updated_at"),
        ("canonical_id", "source_record_id", "asset_ref", "lifecycle_status", "description", "function_description"),
        {"updated_desc": "source_updated_at", "updated_asc": "source_updated_at", "status": "lifecycle_status", "source_number": "source_record_id"},
    ),
    "IP_DOM_OH": ExplorerResource(
        "ip_dom_oh", "Overhaul / DOMINION", "DOMINION", "IP_DOM_OH", "overhaul_event", mart.OverhaulEventMartOrm,
        "source_updated_at", ("source_number", "workorder_ref", "asset_ref", "lifecycle_status", "actual_start_at"),
        ("canonical_id", "source_record_id", "source_number", "workorder_ref", "asset_ref", "lifecycle_status"),
        {"updated_desc": "source_updated_at", "updated_asc": "source_updated_at", "status": "lifecycle_status", "source_number": "source_number"},
    ),
}

DEFERRED_RESOURCES = (
    {"source_object": "IPFMEAITEM", "label": "FMEA item detail", "reason": "Deferred source contract"},
    {"source_object": "IPBHMMEASUREMENT", "label": "BHM measurement", "reason": "Deferred source contract"},
    {"source_object": "DMD_OPLOGABN", "label": "Operator abnormal observation", "reason": "Deferred source contract"},
    {"source_object": "IPMSMSFAILUREMECHANI", "label": "Failure mechanism", "reason": "Deferred source contract"},
)

_SAFE_PROVENANCE = (
    "source_system", "source_application", "source_object", "source_record_id",
    "source_number", "source_site", "source_organization", "source_created_at",
    "source_updated_at", "ingested_at",
)


def _iso(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_safe(child) for child in value]
    return value


def _source_data(row: Any, spec: ExplorerResource) -> dict[str, Any]:
    maximo = ((getattr(row, "sources", None) or {}).get("maximo") or {})
    # The projection is the committed CanonicalSourceConfig.select list. A
    # source block can grow later without widening this API accidentally.
    return {field: _json_safe(maximo.get(field)) for field in spec.selected_fields}


def _canonical_data(row: Any) -> dict[str, Any]:
    excluded = {"sources", "provenance", "relationship_evidence"}
    return {
        ("class" if column.name == "class_label" else column.name): _json_safe(getattr(row, column.name))
        for column in row.__table__.columns
        if column.name not in excluded
    }


def _provenance(row: Any) -> dict[str, Any]:
    value = getattr(row, "provenance", None) or {}
    return {key: _json_safe(value.get(key)) for key in _SAFE_PROVENANCE if key in value}


def mapping_rows(resource: ExplorerResource) -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parents[3] / "reliability-data-contracts" / "mappings" / "maximo-nadi-reliability.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        document = {"mappings": []}
    return [
        {
            "source_field": item.get("source_field"),
            "canonical_field": item.get("canonical_field"),
            "transformation": item.get("transformation"),
            "nullable": item.get("nullable"),
            "evidence": item.get("evidence"),
            "notes": item.get("notes") or None,
        }
        for item in document.get("mappings", [])
        if item.get("source_object", "").upper() == resource.source_object
        and item.get("canonical_entity") == resource.canonical_entity
    ]


class DataExplorerService:
    def __init__(self, store: CollectorStore):
        self.store = store

    @staticmethod
    def resolve_resource(resource: str) -> ExplorerResource:
        try:
            return RESOURCE_SPECS[resource.upper()]
        except KeyError as error:
            raise KeyError(resource) from error

    @staticmethod
    def resolve_entity(entity: str) -> ExplorerResource:
        for spec in RESOURCE_SPECS.values():
            if spec.canonical_entity == entity:
                return spec
        raise KeyError(entity)

    def _filters(self) -> dict[str, str]:
        return {"site_code": SITE, "organization_code": ORGANIZATION}

    def _last_run(self, spec: ExplorerResource) -> Any | None:
        runs = self.store.list_runs(100)
        return next((run for run in runs if str(run.object_structure).upper() == spec.source_object), None)

    def _count(self, spec: ExplorerResource) -> int:
        return self.store.count(spec.model, exact_filters=self._filters())

    def resource_metadata(self, resource: str) -> dict[str, Any]:
        spec = self.resolve_resource(resource)
        run = self._last_run(spec)
        record_count = self._count(spec)
        return {
            "resource_key": spec.source_object,
            "source_system": "MAXIMO",
            "source_application": SOURCE_APPLICATIONS.get(spec.source_object),
            "source_object": spec.source_object,
            "label": spec.label,
            "module": spec.module,
            "scope": {"site": SITE, "organization": ORGANIZATION},
            "selected_fields": list(spec.selected_fields),
            "canonical_target": spec.canonical_entity,
            "contract_version": "1.0",
            "records": record_count,
            "last_sync": _json_safe(run.finished_at) if run else None,
            "status": "READY" if record_count else "CONFIGURED_EMPTY",
            "primary_fields": list(spec.primary_fields),
            "deferred": False,
        }

    def resources(self) -> dict[str, Any]:
        return {
            "resources": [self.resource_metadata(resource) for resource in RESOURCE_SPECS],
            "deferred": list(DEFERRED_RESOURCES),
            "integrity": self.integrity(),
        }

    def integrity(self) -> dict[str, int]:
        """Reuse the Mart logical-reference audit without exposing row values."""
        return MartIntegrityAuditor(self.store._db).audit()

    def _rows(
        self,
        spec: ExplorerResource,
        *,
        offset: int,
        limit: int,
        q: str | None,
        sort: str,
    ) -> tuple[list[Any], int]:
        if sort not in spec.order_columns:
            raise ValueError(f"unsupported sort: {sort}")
        rows = self.store.list_rows(
            spec.model,
            changed_column=spec.changed_column,
            order_column=spec.order_columns[sort],
            order_desc=sort.endswith("_desc"),
            offset=offset,
            limit=limit,
            exact_filters=self._filters(),
            search=q,
            search_columns=spec.search_columns,
        )
        return rows, self.store.count(
            spec.model,
            exact_filters=self._filters(),
            search=q,
            search_columns=spec.search_columns,
        )

    def source_records(self, resource: str, *, offset: int = 0, limit: int = 50, q: str | None = None, sort: str = "updated_desc") -> dict[str, Any]:
        spec = self.resolve_resource(resource)
        rows, total = self._rows(spec, offset=offset, limit=limit, q=q, sort=sort)
        return {
            "resource": self.resource_metadata(spec.source_object),
            "items": [
                {
                    "canonical_id": row.canonical_id,
                    "contract_version": row.contract_version,
                    "source_data": _source_data(row, spec),
                    "source_updated_at": _iso(getattr(row, spec.changed_column, None)),
                }
                for row in rows
            ],
            "meta": {"total": total, "offset": offset, "limit": limit, "has_more": offset + len(rows) < total},
        }

    def mart_records(self, entity: str, *, offset: int = 0, limit: int = 50, q: str | None = None, sort: str = "updated_desc") -> dict[str, Any]:
        spec = self.resolve_entity(entity)
        rows, total = self._rows(spec, offset=offset, limit=limit, q=q, sort=sort)
        return {
            "entity": spec.canonical_entity,
            "items": [_canonical_data(row) for row in rows],
            "meta": {"total": total, "offset": offset, "limit": limit, "has_more": offset + len(rows) < total},
        }

    def record_detail(self, resource: str, canonical_id: str) -> dict[str, Any]:
        spec = self.resolve_resource(resource)
        rows = self.store.list_rows(spec.model, exact_filters={**self._filters(), "canonical_id": canonical_id}, limit=1)
        if not rows:
            raise KeyError(canonical_id)
        row = rows[0]
        return {
            "resource": self.resource_metadata(spec.source_object),
            "canonical_id": row.canonical_id,
            "source_data": _source_data(row, spec),
            "canonical": _canonical_data(row),
            "provenance": _provenance(row),
            "relationship_evidence": _json_safe(getattr(row, "relationship_evidence", None) or {}),
            "mapping": mapping_rows(spec),
        }

    def mapping(self, resource: str) -> dict[str, Any]:
        spec = self.resolve_resource(resource)
        return {
            "source_object": spec.source_object,
            "canonical_entity": spec.canonical_entity,
            "contract_version": "1.0",
            "fields": mapping_rows(spec),
        }
