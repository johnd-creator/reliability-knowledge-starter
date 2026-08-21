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
        for field, aliases in REGISTRY_FIELD_ALIASES.items():
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
class LocalReconciliationInput:
    equipment: tuple[EquipmentSnapshot, ...]
    work_orders: tuple[WorkOrderSnapshot, ...]
    mart_assets: tuple[MartAssetSnapshot, ...] = ()
    mart_maintenance: tuple[MartMaintenanceSnapshot, ...] = ()


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
        "hierarchy": hierarchy,
        "work_order_relationships": {
            "all": work_orders,
            "recent_local_period": _recent_work_order_profile(local.work_orders, equipment_by_id, registry_ids),
        },
        "current_mart": _mart_profile(local.mart_assets, local.mart_maintenance, registry_ids, equipment_by_id),
        "business_report_field_coverage": _business_field_profile(registry),
    }
    report["architecture_decision"] = _architecture_decision(
        local.equipment, registry_ids, work_orders, hierarchy
    )
    return report


def reconcile_registry_file(path: str | Path, database: Any) -> dict[str, Any]:
    return reconcile_registry(parse_registry_file(path), load_local_reconciliation_input(database))
