"""Read-only Work Order population profiling.

The profiler deliberately keeps only aggregate facts in memory.  It reuses
the guarded :class:`OslcClient` for BSR-scoped GET-only traversal and never
calls the collector store, MartWriter, or SyncCursor.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import islice
from typing import Any, Iterable, Mapping

from src.adapters.maximo.oslc_client import OslcClient, oslc_number, oslc_timestamp

WORK_ORDER_OBJECT = "mxwodetail"
WORK_ORDER_SCOPE = 'siteid="BSR"'
WORK_ORDER_SELECT = (
    "wonum", "assetnum", "siteid", "orgid", "status", "worktype",
    "reportdate", "changedate", "actstart", "actfinish", "downtime", "actlabhrs",
)
DEFAULT_ORDER: str | None = None
RECENT_ORDER = "-changedate"
DEFAULT_SOURCE_CAP = 500
DEFAULT_PAGE_SIZE = 25
DEFAULT_MAX_PAGES = 20


def _value(row: Mapping[str, Any], key: str) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bucket(value: str | None) -> str:
    return value if value else "NULL"


def _percentage(count: int, total: int) -> float:
    return round(100 * count / total, 1) if total else 0.0


def _distribution(values: Iterable[str | None], total: int) -> dict[str, dict[str, int | float]]:
    counts: dict[str, int] = {}
    for value in values:
        key = _bucket(value)
        counts[key] = counts.get(key, 0) + 1
    return {
        key: {"count": count, "percentage": _percentage(count, total)}
        for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    }


@dataclass(frozen=True)
class DateRange:
    minimum: str | None
    maximum: str | None
    present: int

    def as_dict(self) -> dict[str, Any]:
        return {"min": self.minimum, "max": self.maximum, "present": self.present}


@dataclass(frozen=True)
class WorkOrderProfile:
    order_by: str | None
    source_cap: int
    page_size: int
    pages: int
    source_rows_read: int
    prefix_matched: int
    prefix_skipped: int
    scope_matched: int
    scope_mismatched: int
    canonical_eligible: int
    eligibility_exclusions: dict[str, int]
    organization_distribution: dict[str, dict[str, int | float]]
    status_before_prefix: dict[str, dict[str, int | float]]
    status_distribution: dict[str, dict[str, int | float]]
    work_type_distribution: dict[str, dict[str, int | float]]
    changedate: DateRange
    reportdate: DateRange
    actual_start_present: int
    actual_finish_present: int
    asset_present: int
    downtime_gt_zero: int
    labor_gt_zero: int

    @property
    def can_percentage(self) -> float:
        return float(self.status_distribution.get("CAN", {}).get("percentage", 0.0))

    def as_dict(self) -> dict[str, Any]:
        total = self.source_rows_read
        return {
            "order_by": self.order_by,
            "source_cap": self.source_cap,
            "page_size": self.page_size,
            "pages": self.pages,
            "source_rows_read": total,
            "prefix_matched": self.prefix_matched,
            "prefix_skipped": self.prefix_skipped,
            "prefix_match_percentage": _percentage(self.prefix_matched, total),
            "scope_matched": self.scope_matched,
            "scope_mismatched": self.scope_mismatched,
            "canonical_eligible": self.canonical_eligible,
            "eligibility_exclusions": dict(self.eligibility_exclusions),
            "organization_distribution": self.organization_distribution,
            "status_before_prefix": self.status_before_prefix,
            "status_distribution": self.status_distribution,
            "work_type_distribution": self.work_type_distribution,
            "changedate": self.changedate.as_dict(),
            "reportdate": self.reportdate.as_dict(),
            "actual_start_present": self.actual_start_present,
            "actual_start_percentage": _percentage(self.actual_start_present, self.prefix_matched),
            "actual_finish_present": self.actual_finish_present,
            "actual_finish_percentage": _percentage(self.actual_finish_present, self.prefix_matched),
            "asset_present": self.asset_present,
            "asset_percentage": _percentage(self.asset_present, self.prefix_matched),
            "downtime_gt_zero": self.downtime_gt_zero,
            "labor_gt_zero": self.labor_gt_zero,
        }


@dataclass(frozen=True)
class RecentOrderProbe:
    supported: bool
    http_status: int | None
    pages: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "order_by": RECENT_ORDER,
            "supported": self.supported,
            "http_status": self.http_status,
            "pages": self.pages,
        }


def _date_range(rows: list[Mapping[str, Any]], field: str) -> DateRange:
    values: list[datetime] = []
    for row in rows:
        value = row.get(field)
        if value in (None, ""):
            continue
        parsed = oslc_timestamp(value)
        if parsed is not None:
            values.append(parsed)
    return DateRange(
        minimum=min(values).isoformat() if values else None,
        maximum=max(values).isoformat() if values else None,
        present=len(values),
    )


def summarize_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    order_by: str | None,
    source_cap: int,
    page_size: int,
    pages: int = 0,
    prefixes: tuple[str, ...] = ("BSR",),
) -> WorkOrderProfile:
    """Aggregate rows without retaining row-level values in the report."""
    bounded = list(rows)
    total = len(bounded)
    normalized_prefixes = tuple(prefix.upper() for prefix in prefixes)
    prefix_rows = [
        row for row in bounded
        if (_value(row, "wonum") or "").upper().startswith(normalized_prefixes)
    ]
    scope_rows = [
        row for row in prefix_rows
        if _value(row, "siteid") == "BSR" and _value(row, "orgid") == "IP"
    ]
    eligibility_exclusions = {
        "missing_wonum": sum(_value(row, "wonum") is None for row in prefix_rows),
        "missing_assetnum": sum(_value(row, "assetnum") is None for row in prefix_rows),
        "missing_siteid": sum(_value(row, "siteid") is None for row in prefix_rows),
        "missing_orgid": sum(_value(row, "orgid") is None for row in prefix_rows),
    }
    canonical_eligible = sum(
        all(_value(row, field) is not None for field in ("wonum", "assetnum", "siteid", "orgid"))
        and _value(row, "siteid") == "BSR"
        and _value(row, "orgid") == "IP"
        for row in prefix_rows
    )
    return WorkOrderProfile(
        order_by=order_by,
        source_cap=source_cap,
        page_size=page_size,
        pages=pages,
        source_rows_read=total,
        prefix_matched=len(prefix_rows),
        prefix_skipped=total - len(prefix_rows),
        scope_matched=len(scope_rows),
        scope_mismatched=len(prefix_rows) - len(scope_rows),
        canonical_eligible=canonical_eligible,
        eligibility_exclusions=eligibility_exclusions,
        organization_distribution=_distribution((_value(row, "orgid") for row in bounded), total),
        status_before_prefix=_distribution((_value(row, "status") for row in bounded), total),
        status_distribution=_distribution((_value(row, "status") for row in prefix_rows), len(prefix_rows)),
        work_type_distribution=_distribution((_value(row, "worktype") for row in prefix_rows), len(prefix_rows)),
        changedate=_date_range(prefix_rows, "changedate"),
        reportdate=_date_range(prefix_rows, "reportdate"),
        actual_start_present=sum(_value(row, "actstart") is not None for row in prefix_rows),
        actual_finish_present=sum(_value(row, "actfinish") is not None for row in prefix_rows),
        asset_present=sum(_value(row, "assetnum") is not None for row in prefix_rows),
        downtime_gt_zero=sum((oslc_number(row.get("downtime")) or 0) > 0 for row in prefix_rows),
        labor_gt_zero=sum((oslc_number(row.get("actlabhrs")) or 0) > 0 for row in prefix_rows),
    )


def _http_status(error: Exception) -> int | None:
    response = getattr(error, "response", None)
    status = getattr(response, "status_code", None)
    return int(status) if status is not None else None


def _is_unsupported_order(error: Exception) -> bool:
    return _http_status(error) == 400


class WorkOrderPopulationProfiler:
    """Profile bounded source slices through the existing guarded client."""

    def __init__(
        self,
        client: OslcClient,
        *,
        source_cap: int = DEFAULT_SOURCE_CAP,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_pages: int = DEFAULT_MAX_PAGES,
        prefixes: tuple[str, ...] = ("BSR",),
    ):
        if source_cap < 1 or page_size < 1 or max_pages < 1:
            raise ValueError("source_cap, page_size, and max_pages must be positive")
        if source_cap > page_size * max_pages:
            raise ValueError("source_cap cannot exceed page_size * max_pages")
        self.client = client
        self.source_cap = source_cap
        self.page_size = page_size
        self.max_pages = max_pages
        self.prefixes = prefixes

    def profile_source(self, order_by: str | None) -> WorkOrderProfile:
        iterator = self.client.iterate(
            WORK_ORDER_OBJECT,
            where=WORK_ORDER_SCOPE,
            required_scope=WORK_ORDER_SCOPE,
            select=list(WORK_ORDER_SELECT),
            order_by=order_by,
            page_size=self.page_size,
            max_pages=self.max_pages,
        )
        rows = list(islice(iterator, self.source_cap))
        return summarize_rows(
            rows,
            order_by=order_by,
            source_cap=self.source_cap,
            page_size=self.page_size,
            pages=int(getattr(self.client, "last_iteration_pages", 0) or 0),
            prefixes=self.prefixes,
        )

    def probe_recent_order(self) -> RecentOrderProbe:
        """Issue exactly one bounded iteration for ``-changedate``."""
        try:
            iterator = self.client.iterate(
                WORK_ORDER_OBJECT,
                where=WORK_ORDER_SCOPE,
                required_scope=WORK_ORDER_SCOPE,
                select=list(WORK_ORDER_SELECT),
                order_by=RECENT_ORDER,
                page_size=self.page_size,
                max_pages=1,
            )
            next(iterator, None)
            return RecentOrderProbe(True, None, int(getattr(self.client, "last_iteration_pages", 0) or 0))
        except Exception as error:  # probe errors are classified, never retried speculatively
            if _is_unsupported_order(error):
                return RecentOrderProbe(False, 400, int(getattr(self.client, "last_iteration_pages", 0) or 0))
            raise

    def compare(self, *, current_mart_can_percentage: float | None = None) -> dict[str, Any]:
        default = self.profile_source(DEFAULT_ORDER)
        probe = self.probe_recent_order()
        recent = self.profile_source(RECENT_ORDER) if probe.supported else None
        classifications = classify_can_dominance(
            default,
            recent,
            current_mart_can_percentage=current_mart_can_percentage,
        )
        return {
            "default": default.as_dict(),
            "recent_order_probe": probe.as_dict(),
            "recent": recent.as_dict() if recent else None,
            "comparison": compare_profiles(default, recent),
            "classifications": list(classifications),
            "primary_classification": classifications[0],
        }


def compare_profiles(default: WorkOrderProfile, recent: WorkOrderProfile | None) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "CAN_percentage": {"default": default.can_percentage},
        "changedate": {"default": default.changedate.as_dict()},
        "asset_percentage": {"default": _percentage(default.asset_present, default.prefix_matched)},
        "actual_start_percentage": {"default": _percentage(default.actual_start_present, default.prefix_matched)},
        "labor_gt_zero_percentage": {"default": _percentage(default.labor_gt_zero, default.prefix_matched)},
    }
    if recent is not None:
        metrics["CAN_percentage"]["recent"] = recent.can_percentage
        metrics["changedate"]["recent"] = recent.changedate.as_dict()
        metrics["asset_percentage"]["recent"] = _percentage(recent.asset_present, recent.prefix_matched)
        metrics["actual_start_percentage"]["recent"] = _percentage(recent.actual_start_present, recent.prefix_matched)
        metrics["labor_gt_zero_percentage"]["recent"] = _percentage(recent.labor_gt_zero, recent.prefix_matched)
    return metrics


def classify_can_dominance(
    default: WorkOrderProfile,
    recent: WorkOrderProfile | None,
    *,
    current_mart_can_percentage: float | None = None,
) -> tuple[str, ...]:
    """Classify only measurable differences; otherwise remain inconclusive."""
    classifications: list[str] = []
    if recent is not None:
        delta = default.can_percentage - recent.can_percentage
        if delta >= 20:
            classifications.append("DEFAULT_ORDER_SAMPLING_BIAS")
        elif default.can_percentage >= 75 and recent.can_percentage >= 75 and abs(delta) <= 10:
            classifications.append("SOURCE_POPULATION_DOMINATED")
    before_can = float(default.status_before_prefix.get("CAN", {}).get("percentage", 0.0))
    if abs(before_can - default.can_percentage) >= 10:
        classifications.append("PREFIX_FILTER_INTERACTION")
    if current_mart_can_percentage is not None and abs(current_mart_can_percentage - default.can_percentage) >= 10:
        classifications.append("CURRENT_MART_SOURCE_DIFFERENCE")
    return tuple(classifications or ("INCONCLUSIVE",))
