"""Read-only reconciliation of the Maximo asset registry and local equipment.

The Maximo ``List of Assets`` export is an HTML table with an ``.xls`` suffix.
This module deliberately keeps the report as an ephemeral input: it parses
only identifiers needed for matching and boolean field-presence facts, then
emits aggregate metrics.  It never writes a report row, collector row, Mart
row, or cursor.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import unquote

from sqlalchemy import select

from src.repositories import mart_models
from src.repositories import models as collector_models


REGISTRY_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "last_wellness": ("lastwellness",),
    "current_condition": ("kondisisaatini", "kondisisekarang"),
    "last_work_order": ("lastwo",),
    "last_acr": ("lastacr",),
    "last_mpi": ("lastmpi",),
    "maintenance_strategy": ("maintenancestrategi", "maintenancestrategy"),
    "judgement_date": ("tanggaljudgement", "judgementdate"),
    "recommended_program": ("rekomendasiprogram", "recommendedprogram"),
    "wo_engineering_judgement": ("woengjudgement", "woengineeringjudgement"),
    "wo_engineering_judgement_status": ("woengjudgementstatus", "woengineeringjudgementstatus"),
}

REGISTRY_ANALYSIS_ALIASES: dict[str, tuple[str, ...]] = {
    "site": ("site",),
    "unit": ("unit",),
    "status": ("status",),
    "area_serp": ("areaserp",),
    "install_date": ("installdate",),
    "created_date": ("createddate",),
}
REGISTRY_PRESENCE_ALIASES = {**REGISTRY_FIELD_ALIASES, **REGISTRY_ANALYSIS_ALIASES}

_PI_FIELDS = {"systemowner", "insertby"}


class UnsupportedRegistryFileFormat(ValueError):
    """The supplied file is not the supported HTML export form."""


def normalize_identifier(value: object | None) -> str | None:
    """Return the matching form without exposing or persisting source text."""
    if value is None:
        return None
    text = str(value).strip()
    return text.upper() if text else None


def _header_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def _nonblank(value: object | None) -> bool:
    return value is not None and bool(str(value).strip())


class _HtmlTableParser(HTMLParser):
    """Small standard-library parser for the Maximo HTML table export."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.title_parts: list[str] = []
        self._in_title = False
        self._in_row = False
        self._in_cell = False
        self._cell_parts: list[str] = []
        self._row: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag == "tr":
            if self._in_row:
                self._finish_row()
            self._in_row = True
            self._row = []
        elif tag in {"td", "th"} and self._in_row:
            if self._in_cell:
                self._finish_cell()
            self._in_cell = True
            self._cell_parts = []
        elif tag == "br" and self._in_cell:
            self._cell_parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag in {"td", "th"} and self._in_cell:
            self._finish_cell()
        elif tag == "tr" and self._in_row:
            self._finish_row()

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_cell:
            self._cell_parts.append(data)

    def _finish_cell(self) -> None:
        value = re.sub(r"\s+", " ", "".join(self._cell_parts)).strip()
        self._row.append(value)
        self._cell_parts = []
        self._in_cell = False

    def _finish_row(self) -> None:
        if self._in_cell:
            self._finish_cell()
        if self._row:
            self.rows.append(self._row)
        self._row = []
        self._in_row = False


@dataclass(frozen=True, slots=True)
class RegistryRecord:
    asset: str | None
    parent: str | None
    present_fields: frozenset[str]
    site: str | None = None
    unit: str | None = None
    status: str | None = None
    area_serp: str | None = None
    install_date_present: bool = False
    created_date_present: bool = False


@dataclass(frozen=True, slots=True)
class RegistrySnapshot:
    format: str
    sheet: str
    rows: int
    records: tuple[RegistryRecord, ...]
    field_present: Mapping[str, int]
    byte_size: int
    sha256: str


def _supported_html(data: bytes) -> bool:
    sample = data[:8192].lstrip().lower()
    return b"<html" in sample or b"<table" in sample or b"<tr" in sample


def _read_html_export(path: str | Path) -> tuple[bytes, str]:
    source = Path(path)
    data = source.read_bytes()
    if data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1") or data.startswith(b"PK\x03\x04"):
        raise UnsupportedRegistryFileFormat("UNSUPPORTED_REGISTRY_FILE_FORMAT")
    if not _supported_html(data):
        raise UnsupportedRegistryFileFormat("UNSUPPORTED_REGISTRY_FILE_FORMAT")
    return data, source.name


def parse_registry_file(path: str | Path) -> RegistrySnapshot:
    """Parse the supported HTML-export ``.xls`` and retain aggregate facts."""
    data, _name = _read_html_export(path)
    parser = _HtmlTableParser()
    parser.feed(data.decode("utf-8", errors="replace"))
    parser.close()

    header_index = None
    header_row: list[str] | None = None
    for index, row in enumerate(parser.rows):
        keys = {_header_key(cell) for cell in row}
        if "asset" in keys and "parent" in keys and "site" in keys:
            header_index = index
            header_row = row
            break
    if header_index is None or header_row is None:
        raise ValueError("REGISTRY_HEADER_NOT_FOUND")

    positions: dict[str, int] = {}
    for index, cell in enumerate(header_row):
        key = _header_key(cell)
        if key == "asset":
            positions["asset"] = index
        elif key == "parent":
            positions["parent"] = index
        for field, aliases in REGISTRY_PRESENCE_ALIASES.items():
            if key in aliases:
                positions[field] = index

    records: list[RegistryRecord] = []
    field_counts: Counter[str] = Counter()
    for row in parser.rows[header_index + 1 :]:
        # Ignore repeated headings and separator rows while retaining rows
        # that have a blank Asset but contain a report field.
        if [_header_key(cell) for cell in row] == [_header_key(cell) for cell in header_row]:
            continue
        padded = row + [""] * max(0, len(header_row) - len(row))
        if not any(_nonblank(cell) for cell in padded):
            continue
        present = frozenset(
            field for field, position in positions.items()
            if field not in {"asset", "parent"} and position < len(padded) and _nonblank(padded[position])
        )
        field_counts.update(present)
        records.append(
            RegistryRecord(
                asset=normalize_identifier(padded[positions["asset"]]),
                parent=normalize_identifier(padded[positions["parent"]]),
                present_fields=present,
                site=_category(padded[positions["site"]]) if "site" in positions else None,
                unit=_category(padded[positions["unit"]]) if "unit" in positions else None,
                status=_category(padded[positions["status"]]) if "status" in positions else None,
                area_serp=_category(padded[positions["area_serp"]]) if "area_serp" in positions else None,
                install_date_present=(
                    "install_date" in positions and _nonblank(padded[positions["install_date"]])
                ),
                created_date_present=(
                    "created_date" in positions and _nonblank(padded[positions["created_date"]])
                ),
            )
        )

    title = re.sub(r"\s+", " ", "".join(parser.title_parts)).strip() or "List of Assets"
    return RegistrySnapshot(
        format="html-table",
        sheet=title,
        rows=len(records),
        records=tuple(records),
        field_present=dict(field_counts),
        byte_size=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


@dataclass(frozen=True, slots=True)
class EquipmentSnapshot:
    id: str
    status: str | None = None
    unit: str | None = None
    equipment_class: str | None = None
    parent_id: str | None = None
    ancestor_id: str | None = None
    has_children: bool | None = None
    source_changed_at: datetime | None = None
    status_changed_at: datetime | None = None
    source_eq11: str | None = None
    source_plant: str | None = None


@dataclass(frozen=True, slots=True)
class WorkOrderSnapshot:
    equipment_id: str | None = None
    source_changed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class MartAssetSnapshot:
    canonical_id: str
    source_asset_number: str | None
    site_code: str | None = None
    organization_code: str | None = None


@dataclass(frozen=True, slots=True)
class MartMaintenanceSnapshot:
    equipment_id: str | None
    site_code: str | None = None
    organization_code: str | None = None


@dataclass(frozen=True, slots=True)
class CursorSnapshot:
    scope: str
    watermark: datetime | None
    rows_seen: int | None


@dataclass(frozen=True, slots=True)
class CollectRunSnapshot:
    object_structure: str
    mode: str
    rows_seen: int
    upserted: int
    skipped: int
    errors: int
    watermark: datetime | None
    started_at: datetime
    finished_at: datetime | None


@dataclass(frozen=True, slots=True)
class LocalReconciliationInput:
    equipment: tuple[EquipmentSnapshot, ...]
    work_orders: tuple[WorkOrderSnapshot, ...]
    mart_assets: tuple[MartAssetSnapshot, ...] = ()
    mart_maintenance: tuple[MartMaintenanceSnapshot, ...] = ()
    cursors: tuple[CursorSnapshot, ...] = ()
    collect_runs: tuple[CollectRunSnapshot, ...] = ()


def load_local_reconciliation_input(database: Any) -> LocalReconciliationInput:
    """Read only required columns from Collector and local Mart tables."""
    with database.session() as session:
        equipment_rows = session.execute(
            select(
                collector_models.EquipmentOrm.id,
                collector_models.EquipmentOrm.status,
                collector_models.EquipmentOrm.unit,
                collector_models.EquipmentOrm.equipment_class,
                collector_models.EquipmentOrm.parent_id,
                collector_models.EquipmentOrm.ancestor_id,
                collector_models.EquipmentOrm.has_children,
                collector_models.EquipmentOrm.source_changed_at,
                collector_models.EquipmentOrm.status_changed_at,
                collector_models.EquipmentOrm.sources,
            )
        ).mappings()
        work_order_rows = session.execute(
            select(
                collector_models.WorkOrderOrm.equipment_id,
                collector_models.WorkOrderOrm.source_changed_at,
            )
        ).mappings()
        mart_asset_rows = session.execute(
            select(
                mart_models.AssetMasterMartOrm.canonical_id,
                mart_models.AssetMasterMartOrm.source_asset_number,
                mart_models.AssetMasterMartOrm.site_code,
                mart_models.AssetMasterMartOrm.organization_code,
            )
        ).mappings()
        mart_maintenance_rows = session.execute(
            select(
                mart_models.MaintenanceEventMartOrm.equipment_id,
                mart_models.MaintenanceEventMartOrm.site_code,
                mart_models.MaintenanceEventMartOrm.organization_code,
            )
        ).mappings()
        cursor_rows = session.execute(
            select(
                collector_models.SyncCursorOrm.scope,
                collector_models.SyncCursorOrm.watermark,
                collector_models.SyncCursorOrm.rows_seen,
            ).where(collector_models.SyncCursorOrm.scope.in_(("mxapiasset", "mxasset")))
        ).mappings()
        collect_run_rows = session.execute(
            select(
                collector_models.CollectRunOrm.object_structure,
                collector_models.CollectRunOrm.mode,
                collector_models.CollectRunOrm.rows_seen,
                collector_models.CollectRunOrm.upserted,
                collector_models.CollectRunOrm.skipped,
                collector_models.CollectRunOrm.errors,
                collector_models.CollectRunOrm.watermark,
                collector_models.CollectRunOrm.started_at,
                collector_models.CollectRunOrm.finished_at,
            ).where(collector_models.CollectRunOrm.object_structure.in_(("mxapiasset", "mxasset")))
            .order_by(collector_models.CollectRunOrm.started_at.desc())
        ).mappings()
        return LocalReconciliationInput(
            equipment=tuple(
                EquipmentSnapshot(
                    id=normalize_identifier(row["id"]) or "",
                    status=_category(row["status"]),
                    unit=_category(row["unit"]),
                    equipment_class=_category(row["equipment_class"]),
                    parent_id=normalize_identifier(row["parent_id"]),
                    ancestor_id=normalize_identifier(row["ancestor_id"]),
                    has_children=row["has_children"],
                    source_changed_at=row["source_changed_at"],
                    status_changed_at=row["status_changed_at"],
                    source_eq11=_category((row["sources"] or {}).get("maximo", {}).get("eq11")),
                    source_plant=_category((row["sources"] or {}).get("maximo", {}).get("plant")),
                )
                for row in equipment_rows
            ),
            work_orders=tuple(
                WorkOrderSnapshot(
                    equipment_id=normalize_identifier(row["equipment_id"]),
                    source_changed_at=row["source_changed_at"],
                )
                for row in work_order_rows
            ),
            mart_assets=tuple(
                MartAssetSnapshot(
                    canonical_id=normalize_identifier(row["canonical_id"]) or "",
                    source_asset_number=normalize_identifier(row["source_asset_number"]),
                    site_code=_category(row["site_code"]),
                    organization_code=_category(row["organization_code"]),
                )
                for row in mart_asset_rows
            ),
            mart_maintenance=tuple(
                MartMaintenanceSnapshot(
                    equipment_id=normalize_identifier(row["equipment_id"]),
                    site_code=_category(row["site_code"]),
                    organization_code=_category(row["organization_code"]),
                )
                for row in mart_maintenance_rows
            ),
            cursors=tuple(
                CursorSnapshot(
                    scope=row["scope"],
                    watermark=row["watermark"],
                    rows_seen=row["rows_seen"],
                )
                for row in cursor_rows
            ),
            collect_runs=tuple(
                CollectRunSnapshot(
                    object_structure=row["object_structure"],
                    mode=row["mode"],
                    rows_seen=row["rows_seen"],
                    upserted=row["upserted"],
                    skipped=row["skipped"],
                    errors=row["errors"],
                    watermark=row["watermark"],
                    started_at=row["started_at"],
                    finished_at=row["finished_at"],
                )
                for row in collect_run_rows
            ),
        )


def _category(value: object | None) -> str | None:
    if not _nonblank(value):
        return None
    return str(value).strip()


def _distribution(values: Iterable[object | None], total: int | None = None) -> dict[str, Any]:
    values = list(values)
    denominator = len(values) if total is None else total
    counts: Counter[str] = Counter("NULL" if value is None or not str(value).strip() else str(value) for value in values)
    counts.setdefault("NULL", 0)
    return {
        "counts": dict(sorted(counts.items())),
        "percentages": {
            key: round(count * 100 / denominator, 1) if denominator else 0.0
            for key, count in sorted(counts.items())
        },
    }


def _presence(values: Iterable[object | None]) -> dict[str, Any]:
    values = list(values)
    count = sum(1 for value in values if _nonblank(value))
    return {"count": count, "total": len(values), "percentage": round(count * 100 / len(values), 1) if values else 0.0}


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _date_range(values: Iterable[datetime | None]) -> dict[str, Any]:
    present = [value for value in values if value is not None]
    return {
        "present": len(present),
        "min": _iso(min(present)) if present else None,
        "max": _iso(max(present)) if present else None,
    }


def _metric(count: int, total: int) -> dict[str, Any]:
    return {"count": count, "total": total, "percentage": round(count * 100 / total, 1) if total else 0.0}


def _registry_gap_profile(
    records: tuple[RegistryRecord, ...], equipment_ids: set[str]
) -> dict[str, Any]:
    missing = [record for record in records if record.asset and record.asset not in equipment_ids]
    return {
        "rows": len(missing),
        "site": _distribution(record.site for record in missing),
        "unit": _distribution(record.unit for record in missing),
        "status": _distribution(record.status for record in missing),
        "area_serp": _distribution(record.area_serp for record in missing),
        "identifier_length": _length_distribution(record.asset for record in missing),
        "suffix_class": dict(sorted(Counter(_suffix_pattern(record.asset) for record in missing).items())),
        "install_date_present": _presence(record.install_date_present for record in missing),
        "created_date_present": _presence(record.created_date_present for record in missing),
        "parent_present": _presence(record.parent for record in missing),
        "parent_found_in_collector": sum(1 for record in missing if record.parent in equipment_ids),
        "parent_not_found_in_collector": sum(1 for record in missing if record.parent and record.parent not in equipment_ids),
    }


def _registry_unit_matrix(
    records: tuple[RegistryRecord, ...], equipment_ids: set[str]
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[RegistryRecord]] = {}
    for record in records:
        grouped.setdefault(record.unit or "NULL", []).append(record)
    result: dict[str, dict[str, Any]] = {}
    for unit, rows in sorted(grouped.items()):
        matched = sum(1 for row in rows if row.asset in equipment_ids)
        result[unit] = {
            "registry_count": len(rows),
            "collector_exact_matches": matched,
            "registry_missing": len(rows) - matched,
            "match_percentage": round(matched * 100 / len(rows), 1) if rows else 0.0,
        }
    return result


def _registry_parent_gap_profile(
    records: tuple[RegistryRecord, ...], equipment_ids: set[str]
) -> dict[str, Any]:
    parents = {record.parent for record in records if record.parent}
    missing = parents - equipment_ids
    missing_rows = [record for record in records if record.parent in missing]
    children_per_parent = Counter(record.parent for record in missing_rows if record.parent)
    return {
        "registry_parents": len(parents),
        "parents_present_in_collector": len(parents - missing),
        "parents_missing_from_collector": len(missing),
        "missing_parent_identifier_length": _length_distribution(missing),
        "missing_parent_suffix_class": dict(sorted(Counter(_suffix_pattern(value) for value in missing).items())),
        "missing_parent_children_total": len(missing_rows),
        "missing_parent_children_unit": _distribution(record.unit for record in missing_rows),
        "children_per_missing_parent": dict(sorted(Counter(children_per_parent.values()).items())),
    }


def _eq11_alignment(
    records: tuple[RegistryRecord, ...], equipment_by_id: Mapping[str, EquipmentSnapshot]
) -> dict[str, Any]:
    matched = [record for record in records if record.asset and record.asset in equipment_by_id]
    equipment_unit_agreement = sum(
        1 for record in matched
        if record.unit and equipment_by_id[record.asset].unit and record.unit == equipment_by_id[record.asset].unit
    )
    source_eq11_present = sum(
        1 for record in matched if equipment_by_id[record.asset].source_eq11
    )
    registry_eq11_agreement = sum(
        1 for record in matched
        if record.unit and equipment_by_id[record.asset].source_eq11 == record.unit
    )
    collector_eq11_agreement = sum(
        1 for record in matched
        if equipment_by_id[record.asset].unit and equipment_by_id[record.asset].source_eq11
        and equipment_by_id[record.asset].unit == equipment_by_id[record.asset].source_eq11
    )
    if not matched or not source_eq11_present:
        semantic_equivalence = "UNKNOWN"
    elif registry_eq11_agreement == source_eq11_present:
        semantic_equivalence = "YES"
    else:
        semantic_equivalence = "NO"
    return {
        "matched_rows": len(matched),
        "registry_unit_vs_collector_unit": _metric(equipment_unit_agreement, len(matched)),
        "registry_unit_vs_sources_maximo_eq11": _metric(registry_eq11_agreement, source_eq11_present),
        "collector_unit_vs_sources_maximo_eq11": _metric(collector_eq11_agreement, source_eq11_present),
        "sources_maximo_eq11_present": source_eq11_present,
        "semantic_equivalence": semantic_equivalence,
    }


def _run_projection(run: CollectRunSnapshot) -> dict[str, Any]:
    return {
        "object_structure": run.object_structure,
        "mode": run.mode,
        "rows_seen": run.rows_seen,
        "upserted": run.upserted,
        "skipped": run.skipped,
        "errors": run.errors,
        "watermark": _iso(run.watermark),
        "started_at": _iso(run.started_at),
        "finished_at": _iso(run.finished_at),
    }


def _sync_history_profile(
    cursors: tuple[CursorSnapshot, ...], runs: tuple[CollectRunSnapshot, ...]
) -> dict[str, Any]:
    expected_scopes = ("mxapiasset", "mxasset")
    cursor_by_scope = {row.scope: row for row in cursors}
    cursor_report = {
        scope: {
            "exists": scope in cursor_by_scope,
            "watermark": _iso(cursor_by_scope[scope].watermark) if scope in cursor_by_scope else None,
            "rows_seen": cursor_by_scope[scope].rows_seen if scope in cursor_by_scope else None,
        }
        for scope in expected_scopes
    }
    mode_counts = Counter(run.mode for run in runs)
    object_counts = Counter(run.object_structure for run in runs)
    latest_by_mode: dict[str, dict[str, Any]] = {}
    for mode in ("full", "incremental", "partial"):
        mode_runs = [run for run in runs if run.mode == mode]
        if mode_runs:
            latest_by_mode[mode] = _run_projection(max(mode_runs, key=lambda run: run.started_at))
    latest_by_object: dict[str, dict[str, Any]] = {}
    for object_structure in expected_scopes:
        object_runs = [run for run in runs if run.object_structure == object_structure]
        if object_runs:
            latest_by_object[object_structure] = _run_projection(max(object_runs, key=lambda run: run.started_at))
    return {
        "cursor": cursor_report,
        "collect_runs_total": len(runs),
        "collect_runs_by_mode": dict(sorted(mode_counts.items())),
        "collect_runs_by_object": dict(sorted(object_counts.items())),
        "runs_with_errors": sum(1 for run in runs if run.errors),
        "partial_runs": mode_counts.get("partial", 0),
        "latest_by_mode": latest_by_mode,
        "latest_by_object": latest_by_object,
        "full_traversal_observed": bool(mode_counts.get("full")),
        "partial_traversal_observed": bool(mode_counts.get("partial")),
    }


def _sync_configuration_profile() -> dict[str, Any]:
    """Return config facts without constructing an HTTP client or requesting Maximo."""
    from src.api.app import sync_config_for
    from src.config import MaximoConfig

    runtime = MaximoConfig.from_environment()
    objects: dict[str, dict[str, Any]] = {}
    for object_structure in ("mxapiasset", "mxasset"):
        config = sync_config_for(object_structure)
        objects[object_structure] = {
            "scope": config.scope_clause,
            "required_values": dict(config.required_values),
            "equipment_unit": runtime.equipment_unit,
            "order_by": config.order_by,
            "watermark_field": config.watermark_field,
            "page_size": config.page_size or runtime.page_size,
            "max_pages": config.max_pages,
            "watermark_query": config.watermark_query,
        }
    return {"runtime_equipment_unit": runtime.equipment_unit, "objects": objects}


def _historical_work_order_profile(
    work_orders: tuple[WorkOrderSnapshot, ...],
    equipment_by_id: Mapping[str, EquipmentSnapshot],
    registry_ids: set[str],
) -> dict[str, Any]:
    dated = [row.source_changed_at for row in work_orders if row.source_changed_at is not None]
    if not dated:
        return {"available": False, "reason": "NO_SOURCE_CHANGED_AT"}
    latest = max(dated)
    if latest.tzinfo is None:
        latest = latest.replace(tzinfo=timezone.utc)
    bands = (
        ("0-30_days", timedelta(days=0), timedelta(days=30)),
        ("31-90_days", timedelta(days=30), timedelta(days=90)),
        ("91-365_days", timedelta(days=90), timedelta(days=365)),
        ("1-3_years", timedelta(days=365), timedelta(days=1095)),
        ("over_3_years", timedelta(days=1095), None),
    )
    buckets: dict[str, list[WorkOrderSnapshot]] = {name: [] for name, _start, _end in bands}
    undated = 0
    for row in work_orders:
        if row.source_changed_at is None:
            undated += 1
            continue
        timestamp = row.source_changed_at
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age = max(timedelta(0), latest - timestamp)
        for index, (name, start, end) in enumerate(bands):
            lower_bound = age >= start if index == 0 else age > start
            if lower_bound and (end is None or age <= end):
                buckets[name].append(row)
                break
    output: dict[str, Any] = {}
    for name, rows in buckets.items():
        with_equipment = [row for row in rows if row.equipment_id]
        missing = [row for row in with_equipment if row.equipment_id not in equipment_by_id]
        known = [row for row in with_equipment if row.equipment_id in equipment_by_id]
        direct = [row for row in with_equipment if row.equipment_id in registry_ids]
        direct_missing = [row for row in direct if row.equipment_id not in equipment_by_id]
        non_registry = [row for row in with_equipment if row.equipment_id not in registry_ids]
        non_registry_missing = [row for row in non_registry if row.equipment_id not in equipment_by_id]
        output[name] = {
            "total": len(rows),
            "with_equipment": len(with_equipment),
            "direct_registry_target": len(direct),
            "direct_registry_target_missing_from_collector": len(direct_missing),
            "known_collector_equipment": len(known),
            "missing_collector_equipment": len(missing),
            "equipment_target_missing_from_collector": len(non_registry_missing),
            "missing_percentage": round(len(missing) * 100 / len(with_equipment), 1) if with_equipment else 0.0,
        }
    populated = [value for value in output.values() if value["with_equipment"]]
    recent = output["0-30_days"]
    oldest = next((output[name] for name in ("over_3_years", "1-3_years", "91-365_days") if output[name]["with_equipment"]), None)
    historical_gap = bool(
        oldest and recent["with_equipment"] and oldest["missing_percentage"] > recent["missing_percentage"] + 10.0
    )
    return {
        "available": True,
        "latest_local_timestamp": _iso(latest),
        "undated_rows": undated,
        "buckets": output,
        "historical_gap_classification": "HISTORICAL_EQUIPMENT_COVERAGE_GAP" if historical_gap else "NEEDS_MORE_EVIDENCE",
        "bucket_count": len(populated),
    }


def _boolean_distribution(values: Iterable[bool | None]) -> dict[str, int]:
    result = {"true": 0, "false": 0, "null": 0}
    for value in values:
        result["null" if value is None else str(bool(value)).lower()] += 1
    return result


def _length_distribution(values: Iterable[str | None]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for value in values:
        counts["blank" if not value else f"length_{len(value)}"] += 1
    return dict(sorted(counts.items()))


def _suffix_pattern(value: str | None) -> str:
    if not value:
        return "blank"
    match = re.search(r"-(\d+)$", value)
    return f"numeric_suffix_{len(match.group(1))}_digits" if match else "no_numeric_suffix"


def _parent_profile(values: Iterable[str | None]) -> dict[str, Any]:
    values = list(values)
    nonblank = [value for value in values if value]
    return {
        "present": len(nonblank),
        "blank": len(values) - len(nonblank),
        "unique": len(set(nonblank)),
        "identifier_length_distribution": _length_distribution(nonblank),
        "suffix_pattern_distribution": dict(sorted(Counter(_suffix_pattern(value) for value in nonblank).items())),
    }


@dataclass(frozen=True, slots=True)
class _HierarchyResolution:
    found: bool
    direct: bool
    broken: bool
    cycle: bool
    depth: int


def _resolve_registry_ancestor(
    start: str,
    equipment_by_id: Mapping[str, EquipmentSnapshot],
    registry_ids: set[str],
) -> _HierarchyResolution:
    if start in registry_ids:
        return _HierarchyResolution(True, False, False, False, 0)
    current = start
    visited: set[str] = set()
    depth = 0
    while True:
        if current in visited:
            return _HierarchyResolution(False, False, False, True, depth)
        visited.add(current)
        row = equipment_by_id.get(current)
        if row is None:
            return _HierarchyResolution(False, False, True, False, depth)
        parent = row.parent_id
        if not parent:
            return _HierarchyResolution(False, False, False, False, depth)
        depth += 1
        if parent in registry_ids:
            return _HierarchyResolution(True, depth == 1, False, False, depth)
        if parent not in equipment_by_id:
            return _HierarchyResolution(False, False, True, False, depth)
        current = parent


def _hierarchy_profile(equipment: tuple[EquipmentSnapshot, ...], registry_ids: set[str]) -> dict[str, Any]:
    by_id = {row.id: row for row in equipment if row.id}
    non_registry = [row for row in equipment if row.id not in registry_ids]
    direct = found = no_ancestor = broken = cycle = max_depth = 0
    for row in non_registry:
        resolution = _resolve_registry_ancestor(row.id, by_id, registry_ids)
        direct += int(resolution.direct)
        found += int(resolution.found)
        no_ancestor += int(not resolution.found)
        broken += int(resolution.broken)
        cycle += int(resolution.cycle)
        max_depth = max(max_depth, resolution.depth)
    return {
        "non_registry_equipment_total": len(non_registry),
        "direct_registry_parent": direct,
        "registry_ancestor_found": found,
        "indirect_registry_ancestor": max(found - direct, 0),
        "no_registry_ancestor": no_ancestor,
        "broken_parent_reference": broken,
        "cycle_encountered": cycle,
        "maximum_observed_hierarchy_depth": max_depth,
    }


def _equipment_group_profile(rows: Iterable[EquipmentSnapshot]) -> dict[str, Any]:
    rows = tuple(rows)
    return {
        "total": len(rows),
        "identifier_length_distribution": _length_distribution([row.id for row in rows]),
        "status": _distribution(row.status for row in rows),
        "equipment_class": _distribution(row.equipment_class for row in rows),
        "unit": _distribution(row.unit for row in rows),
        "source_plant": _distribution(row.source_plant for row in rows),
        "parent_present": _presence(row.parent_id for row in rows),
        "ancestor_present": _presence(row.ancestor_id for row in rows),
        "has_children": _boolean_distribution(row.has_children for row in rows),
    }


def _registry_parent_reconciliation(
    records: tuple[RegistryRecord, ...], equipment_by_id: Mapping[str, EquipmentSnapshot]
) -> dict[str, int]:
    registry_rows = [record for record in records if record.asset and record.asset in equipment_by_id]
    exact = different = report_present_collector_missing = collector_present_report_blank = both_missing = 0
    for record in registry_rows:
        collector_parent = equipment_by_id[record.asset].parent_id
        if record.parent and collector_parent:
            if record.parent == collector_parent:
                exact += 1
            else:
                different += 1
        elif record.parent and not collector_parent:
            report_present_collector_missing += 1
        elif collector_parent and not record.parent:
            collector_present_report_blank += 1
        else:
            both_missing += 1
    return {
        "matched_registry_rows": len(registry_rows),
        "exact_agreement": exact,
        "different": different,
        "report_parent_present_collector_missing": report_present_collector_missing,
        "collector_parent_present_report_blank": collector_present_report_blank,
        "both_missing": both_missing,
    }


def _work_order_profile(
    work_orders: tuple[WorkOrderSnapshot, ...],
    equipment_by_id: Mapping[str, EquipmentSnapshot],
    registry_ids: set[str],
) -> dict[str, Any]:
    result = {
        "total": len(work_orders),
        "with_equipment": sum(1 for row in work_orders if row.equipment_id),
        "without_equipment": sum(1 for row in work_orders if not row.equipment_id),
        "direct_registry_asset": 0,
        "direct_registry_target_missing_from_collector": 0,
        "non_registry_with_registry_ancestor": 0,
        "equipment_with_no_registry_ancestor": 0,
        "equipment_target_missing_from_collector": 0,
    }
    for work_order in work_orders:
        equipment_id = work_order.equipment_id
        if not equipment_id:
            continue
        if equipment_id in registry_ids:
            result["direct_registry_asset"] += 1
            if equipment_id not in equipment_by_id:
                result["direct_registry_target_missing_from_collector"] += 1
        elif equipment_id not in equipment_by_id:
            result["equipment_target_missing_from_collector"] += 1
        elif _resolve_registry_ancestor(equipment_id, equipment_by_id, registry_ids).found:
            result["non_registry_with_registry_ancestor"] += 1
        else:
            result["equipment_with_no_registry_ancestor"] += 1
    return result


def _recent_work_order_profile(
    work_orders: tuple[WorkOrderSnapshot, ...],
    equipment_by_id: Mapping[str, EquipmentSnapshot],
    registry_ids: set[str],
    days: int = 30,
) -> dict[str, Any]:
    dated = [row.source_changed_at for row in work_orders if row.source_changed_at is not None]
    if not dated:
        return {"available": False, "reason": "NO_SOURCE_CHANGED_AT"}
    latest = max(dated)
    if latest.tzinfo is None:
        latest = latest.replace(tzinfo=timezone.utc)
    start = latest - timedelta(days=days)
    recent = tuple(
        row for row in work_orders
        if row.source_changed_at is not None and (
            row.source_changed_at.replace(tzinfo=timezone.utc) if row.source_changed_at.tzinfo is None else row.source_changed_at
        ) >= start
    )
    return {
        "available": True,
        "period_days": days,
        "period_start": start.isoformat(),
        "period_end": latest.isoformat(),
        "rows": len(recent),
        "relationship_distribution": _work_order_profile(recent, equipment_by_id, registry_ids),
    }


def _mart_profile(
    mart_assets: tuple[MartAssetSnapshot, ...],
    mart_maintenance: tuple[MartMaintenanceSnapshot, ...],
    registry_ids: set[str],
    equipment_by_id: Mapping[str, EquipmentSnapshot],
) -> dict[str, Any]:
    scoped_assets = tuple(
        row for row in mart_assets
        if (row.site_code or "BSR") == "BSR" and (row.organization_code or "IP") == "IP"
    )
    scoped_maintenance = tuple(
        row for row in mart_maintenance
        if (row.site_code or "BSR") == "BSR" and (row.organization_code or "IP") == "IP"
    )
    mart_asset_sources = {row.source_asset_number for row in scoped_assets if row.source_asset_number}
    mart_asset_canonical = {row.canonical_id for row in scoped_assets if row.canonical_id}
    registry_asset_master = sum(1 for row in scoped_assets if row.source_asset_number in registry_ids)
    unresolved = 0
    unresolved_in_collector = 0
    unresolved_with_ancestor = 0
    for row in scoped_maintenance:
        ref = row.equipment_id
        source_value = _source_asset_from_reference(ref)
        resolved = bool(ref and (ref in mart_asset_canonical or source_value in mart_asset_sources))
        if resolved:
            continue
        unresolved += 1
        equipment_id = source_value if source_value in equipment_by_id else ref
        if equipment_id and equipment_id in equipment_by_id:
            unresolved_in_collector += 1
            if _resolve_registry_ancestor(equipment_id, equipment_by_id, registry_ids).found:
                unresolved_with_ancestor += 1
    return {
        "asset_master_total": len(scoped_assets),
        "asset_master_matching_registry": registry_asset_master,
        "registry_assets_absent_from_mart": len(registry_ids - mart_asset_sources),
        "asset_master_not_in_registry": len(scoped_assets) - registry_asset_master,
        "maintenance_references_total": len(scoped_maintenance),
        "maintenance_references_resolved": len(scoped_maintenance) - unresolved,
        "maintenance_references_unresolved": unresolved,
        "unresolved_references_found_in_collector_equipment": unresolved_in_collector,
        "unresolved_references_with_registry_ancestor": unresolved_with_ancestor,
    }


def _source_asset_from_reference(value: str | None) -> str | None:
    if not value:
        return None
    prefix = "ASSET:MAXIMO:MXASSET:BSR:IP:"
    if value.startswith(prefix):
        return normalize_identifier(unquote(value[len(prefix) :]))
    return value


def _business_field_profile(snapshot: RegistrySnapshot) -> dict[str, Any]:
    return {
        field: {"count": snapshot.field_present.get(field, 0), "total": snapshot.rows,
                "percentage": round(snapshot.field_present.get(field, 0) * 100 / snapshot.rows, 1) if snapshot.rows else 0.0}
        for field in REGISTRY_FIELD_ALIASES
    }


def _coverage_diagnosis(
    registry_gap: dict[str, Any],
    unit_matrix: dict[str, dict[str, Any]],
    collector_unit_distribution: dict[str, Any],
    config: dict[str, Any],
    alignment: dict[str, Any],
    history: dict[str, Any],
) -> dict[str, Any]:
    required_unit = config.get("runtime_equipment_unit")
    missing_by_unit = registry_gap.get("unit", {}).get("counts", {})
    same_unit_missing = int(missing_by_unit.get(required_unit, 0)) if required_unit else 0
    outside_unit_missing = max(int(registry_gap.get("rows", 0)) - same_unit_missing, 0)
    classifications: list[str] = []
    if same_unit_missing and alignment.get("semantic_equivalence") == "YES":
        classifications.append("COLLECTOR_SYNC_INCOMPLETE")
        if not history.get("cursor_exists") and not history.get("collect_runs_total"):
            classifications.append("COLLECTOR_LOCAL_STATE_STALE")
    if outside_unit_missing:
        classifications.append("COLLECTOR_SCOPE_FILTER_GAP")
    if not classifications:
        classifications.append("NEEDS_MORE_EVIDENCE")
    equipment_counts = collector_unit_distribution.get("counts", {})
    return {
        "classifications": classifications,
        "evidence": {
            "missing_registry_assets": registry_gap.get("rows", 0),
            "missing_with_required_unit": same_unit_missing,
            "missing_outside_required_unit": outside_unit_missing,
            "required_unit": required_unit,
            "eq11_alignment": alignment.get("semantic_equivalence"),
            "cursor_exists": any(item.get("exists") for item in history.get("cursor", {}).values()),
            "partial_asset_runs": history.get("partial_runs", 0),
            "full_asset_runs": history.get("collect_runs_by_mode", {}).get("full", 0),
        },
        "phase_a_explains_gap": bool(same_unit_missing and alignment.get("semantic_equivalence") == "YES"),
        "targeted_maximo_verification_needed": bool(
            not history.get("cursor_exists") and not history.get("collect_runs_total")
        ),
        "collector_population_coherence": (
            "ACCUMULATED_MULTI_SCOPE_POPULATION"
            if any(unit != required_unit and unit != "NULL" for unit in equipment_counts)
            else "SINGLE_SCOPE_POPULATION"
        ),
        "unit_matrix": unit_matrix,
    }


def deterministic_missing_registry_sample(
    records: tuple[RegistryRecord, ...],
    equipment_ids: set[str],
    sample_size: int = 10,
) -> tuple[str, ...]:
    """Select a stable in-memory sample without exposing identifiers."""
    if not 1 <= sample_size <= 10:
        raise ValueError("sample_size must be between 1 and 10")
    missing = sorted({record.asset for record in records if record.asset and record.asset not in equipment_ids})
    return tuple(sorted(missing, key=lambda value: hashlib.sha256(value.encode()).hexdigest())[:sample_size])


def verify_missing_registry_sample(
    records: tuple[RegistryRecord, ...],
    equipment_ids: set[str],
    client: Any,
    sample_size: int = 10,
) -> dict[str, Any]:
    """Verify a deterministic bounded sample through the two verified asset structures.

    The caller supplies a GET-only ``OslcClient`` with a request budget. This
    function keeps sampled identifiers in memory and reports only counts.
    """
    sample = deterministic_missing_registry_sample(records, equipment_ids, sample_size)
    found: dict[str, int] = {"mxapiasset": 0, "mxasset": 0}
    both = neither = 0
    for asset in sample:
        asset_found: dict[str, bool] = {}
        escaped = asset.replace("\\", "\\\\").replace('"', '\\"')
        where = f'siteid="BSR" and assetnum="{escaped}"'
        for object_structure in ("mxapiasset", "mxasset"):
            member = next(
                client.iterate(
                    object_structure,
                    where=where,
                    required_scope='siteid="BSR"',
                    select=["assetnum", "siteid", "orgid", "eq11"],
                    page_size=1,
                    max_pages=1,
                ),
                None,
            )
            asset_found[object_structure] = member is not None
            found[object_structure] += int(member is not None)
        if asset_found["mxapiasset"] and asset_found["mxasset"]:
            both += 1
        elif not asset_found["mxapiasset"] and not asset_found["mxasset"]:
            neither += 1
    return {
        "executed": True,
        "sample_size": len(sample),
        "found_in_mxapiasset": found["mxapiasset"],
        "found_in_mxasset": found["mxasset"],
        "found_in_both": both,
        "found_in_neither": neither,
        "request_telemetry": client.request_telemetry,
    }


def _architecture_decision(
    equipment: tuple[EquipmentSnapshot, ...],
    registry_ids: set[str],
    work_orders: dict[str, Any],
    hierarchy: dict[str, Any],
) -> dict[str, Any]:
    ancestor_work_orders = work_orders["non_registry_with_registry_ancestor"]
    equipped_work_orders = work_orders["with_equipment"]
    recent = work_orders.get("recent_local_period") or {}
    recent_ancestor_work_orders = (
        ((recent.get("relationship_distribution") or {}).get("non_registry_with_registry_ancestor", 0))
        if recent.get("available") else 0
    )
    if not equipment or not registry_ids or work_orders["total"] == 0:
        decision = "NEEDS_MORE_EVIDENCE"
        reason = "local equipment, registry, or work-order population is empty"
    elif ancestor_work_orders > 0 and (
        recent_ancestor_work_orders > 0 or ancestor_work_orders / max(equipped_work_orders, 1) >= 0.01
    ):
        decision = "MODEL_B_FULL_HIERARCHY_WITH_REGISTRY_CLASSIFICATION"
        reason = "a material Work Order population references non-registry Equipment that resolves to a registry Asset ancestor"
    elif ancestor_work_orders > 0 or hierarchy["registry_ancestor_found"] > 0:
        decision = "MODEL_C_SEPARATE_REGISTRY_RELATION"
        reason = "the hierarchy contains registry ancestors, but the observed Work Order ancestor relationship is sparse or absent in the recent local period"
    elif work_orders["equipment_with_no_registry_ancestor"] > 0 or work_orders["equipment_target_missing_from_collector"] > 0:
        decision = "MODEL_C_SEPARATE_REGISTRY_RELATION"
        reason = "Work Order references extend beyond direct registry assets, but the local hierarchy does not resolve all of them"
    elif work_orders["direct_registry_asset"] == work_orders["with_equipment"]:
        decision = "MODEL_A_REGISTRY_ONLY"
        reason = "all locally resolvable Work Order equipment references directly match the registry"
    else:
        decision = "NEEDS_MORE_EVIDENCE"
        reason = "local relationships do not establish a stable target model"
    return {
        "decision": decision,
        "evidence": reason,
        "equipment_meaning": "broader Maximo equipment identity used for hierarchy and relationship context",
        "registered_reliability_asset_meaning": "Asset row present in the supplied List of Assets registry snapshot",
        "non_registry_equipment_meaning": "Collector Equipment not present in the registry snapshot; role remains unclassified",
        "recommended_mart_treatment": (
            "retain relationship-capable Equipment hierarchy and represent registry membership as a separate, evidence-backed projection; do not add a classification schema in MX-011A"
        ),
        "recommended_nadi_scope": "registered reliability assets by default, with lower-level Equipment retained for relationship context",
        "hierarchy_ancestor_rows": hierarchy["registry_ancestor_found"],
    }


def reconcile_registry(
    registry: RegistrySnapshot,
    local: LocalReconciliationInput,
) -> dict[str, Any]:
    """Build a privacy-safe aggregate reconciliation report."""
    records = registry.records
    registry_ids = {record.asset for record in records if record.asset}
    asset_occurrences = Counter(record.asset for record in records if record.asset)
    equipment_by_id = {row.id: row for row in local.equipment if row.id}
    registry_parents = {record.parent for record in records if record.parent}
    parents_found = registry_parents & set(equipment_by_id)
    equipment_in_registry = [row for row in local.equipment if row.id in registry_ids]
    non_registry = [row for row in local.equipment if row.id not in registry_ids]
    hierarchy = _hierarchy_profile(local.equipment, registry_ids)
    work_orders = _work_order_profile(local.work_orders, equipment_by_id, registry_ids)
    recent_work_orders = _recent_work_order_profile(local.work_orders, equipment_by_id, registry_ids)
    sync_configuration = _sync_configuration_profile()
    sync_history = _sync_history_profile(local.cursors, local.collect_runs)
    registry_gap = _registry_gap_profile(records, set(equipment_by_id))
    unit_matrix = _registry_unit_matrix(records, set(equipment_by_id))
    parent_gap = _registry_parent_gap_profile(records, set(equipment_by_id))
    eq11_alignment = _eq11_alignment(records, equipment_by_id)

    report = {
        "registry_file": {
            "format": registry.format,
            "sheet": registry.sheet,
            "rows": registry.rows,
            "nonblank_asset_rows": sum(1 for record in records if record.asset),
            "unique_assets": len(registry_ids),
            "duplicate_asset_values": sum(1 for count in asset_occurrences.values() if count > 1),
            "duplicate_asset_rows": sum(count - 1 for count in asset_occurrences.values() if count > 1),
            "blank_assets": sum(1 for record in records if not record.asset),
            "unique_parents": len(registry_parents),
            "parent_profile": _parent_profile([record.parent for record in records]),
            "asset_identifier_length_distribution": _length_distribution(registry_ids),
            "asset_suffix_pattern_distribution": dict(sorted(Counter(_suffix_pattern(value) for value in registry_ids).items())),
            "sha256": registry.sha256,
            "byte_size": registry.byte_size,
        },
        "collector_equipment": {
            "total": len(local.equipment),
            "id_present": sum(1 for row in local.equipment if row.id),
            "duplicate_ids": len(local.equipment) - len(equipment_by_id),
            "status": _distribution(row.status for row in local.equipment),
            "unit": _distribution(row.unit for row in local.equipment),
            "equipment_class": _distribution(row.equipment_class for row in local.equipment),
            "parent_present": _presence(row.parent_id for row in local.equipment),
            "ancestor_present": _presence(row.ancestor_id for row in local.equipment),
            "has_children": _boolean_distribution(row.has_children for row in local.equipment),
            "source_changed_at": _date_range(row.source_changed_at for row in local.equipment),
            "status_changed_at": _date_range(row.status_changed_at for row in local.equipment),
            "created_or_observed_at": {
                "available": False,
                "reason": "Equipment ORM has no created_at or observed_at column",
            },
        },
        "registry_reconciliation": {
            "registry_assets_total": len(registry_ids),
            "exact_equipment_matches": len(registry_ids & set(equipment_by_id)),
            "registry_assets_missing_from_collector": len(registry_ids - set(equipment_by_id)),
            "exact_match_percentage": round(len(registry_ids & set(equipment_by_id)) * 100 / len(registry_ids), 1) if registry_ids else 0.0,
            "registry_parents_total": len(registry_parents),
            "parents_matching_collector": len(parents_found),
            "parents_missing_from_collector": len(registry_parents - set(equipment_by_id)),
            "parent_match_percentage": round(len(parents_found) * 100 / len(registry_parents), 1) if registry_parents else 0.0,
            "hierarchy_consistency": _registry_parent_reconciliation(records, equipment_by_id),
        },
        "registry_vs_non_registry": {
            "registry_equipment": _equipment_group_profile(equipment_in_registry),
            "non_registry_equipment": _equipment_group_profile(non_registry),
            "strong_candidate_classification_rule_found": False,
            "candidate_only": True,
        },
        "registry_gap_breakdown": registry_gap,
        "registry_unit_matrix": unit_matrix,
        "registry_parent_gap": parent_gap,
        "eq11_registry_alignment": eq11_alignment,
        "sync_configuration": sync_configuration,
        "sync_history": sync_history,
        "hierarchy": hierarchy,
        "work_order_relationships": {
            "all": work_orders,
            "recent_local_period": recent_work_orders,
            "age_buckets": _historical_work_order_profile(local.work_orders, equipment_by_id, registry_ids),
        },
        "current_mart": _mart_profile(local.mart_assets, local.mart_maintenance, registry_ids, equipment_by_id),
        "business_report_field_coverage": _business_field_profile(registry),
    }
    report["coverage_diagnosis"] = _coverage_diagnosis(
        registry_gap,
        unit_matrix,
        report["collector_equipment"]["unit"],
        sync_configuration,
        eq11_alignment,
        sync_history,
    )
    report["architecture_decision"] = _architecture_decision(
        local.equipment, registry_ids, work_orders, hierarchy
    )
    return report


def reconcile_registry_file(path: str | Path, database: Any) -> dict[str, Any]:
    return reconcile_registry(parse_registry_file(path), load_local_reconciliation_input(database))
