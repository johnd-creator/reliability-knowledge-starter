"""Explicitly bounded initial load orchestration for the Reliability Mart.

This module intentionally has one profile and no unlimited mode. It reuses the
canonical collector and MartWriter; it does not create a second ingestion path.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from src.adapters.maximo.oslc_client import OslcRequestBudgetExceeded
from src.config import MaximoConfig
from src.repositories import mart_models
from src.repositories.store import CollectorStore
from src.services.canonical import CanonicalCollection, CanonicalCollector, canonical_config_for
from sqlalchemy import inspect, text

from src.services.mart import MartIntegrityAuditor, MartWriter

CONTROLLED_REQUEST_BUDGET = 100
DRY_RUN_SOURCE_CAP = 3
RESOURCE_ORDER = ("mxasset", "mxwodetail", "ipfmea", "ipbhm", "iprcfa", "ip_dom_oh")


@dataclass(frozen=True)
class ControlledProfile:
    name: str
    source_ceilings: Mapping[str, int]

    def ceiling_for(self, source: str) -> int:
        try:
            return self.source_ceilings[source]
        except KeyError as error:
            raise KeyError(f"source is not in controlled profile: {source}") from error

    def max_pages_for(self, source: str, runtime_config: MaximoConfig, ceiling: int | None = None) -> int:
        ceiling = ceiling or self.ceiling_for(source)
        config = canonical_config_for(source, runtime_config)
        page_size = min(config.page_size or runtime_config.page_size, ceiling)
        return max(1, math.ceil(ceiling / page_size))


INITIAL_CONTROLLED_PROFILE = ControlledProfile(
    name="initial-controlled",
    source_ceilings={
        "mxasset": 300,
        "mxwodetail": 500,
        "ipfmea": 100,
        "ipbhm": 100,
        "iprcfa": 100,
        "ip_dom_oh": 100,
    },
)

PROFILES = {INITIAL_CONTROLLED_PROFILE.name: INITIAL_CONTROLLED_PROFILE}
SOURCE_ALIASES = {
    source.lower(): source
    for source in RESOURCE_ORDER
}
SOURCE_ALIASES.update({"mxapiasset": "mxasset", "ipdomoh": "ip_dom_oh"})

ENTITY_MODELS = {
    "asset_master": mart_models.AssetMasterMartOrm,
    "maintenance_event": mart_models.MaintenanceEventMartOrm,
    "fmea_assessment": mart_models.FmeaAssessmentMartOrm,
    "asset_health_assessment": mart_models.AssetHealthAssessmentMartOrm,
    "rcfa_analysis": mart_models.RcfaAnalysisMartOrm,
    "overhaul_event": mart_models.OverhaulEventMartOrm,
}


def verify_mart_database(db: Any, maximo_config: MaximoConfig) -> None:
    """Verify the configured writer target without printing its DSN."""
    if db.engine.url.get_backend_name() != "postgresql":
        raise RuntimeError("MART_DATABASE_TARGET_MUST_BE_POSTGRESQL")
    database_host = (db.engine.url.host or "").lower()
    maximo_host = (maximo_config.base_url.split("//", 1)[-1].split("/", 1)[0].split(":", 1)[0]).lower()
    if database_host and maximo_host and database_host == maximo_host:
        raise RuntimeError("MART_DATABASE_TARGET_AMBIGUOUS_WITH_MAXIMO_ORIGIN")
    with db.engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        tables = set(inspect(db.engine).get_table_names())
    missing = set(ENTITY_MODELS) - tables
    if missing:
        raise RuntimeError("MART_TABLES_MISSING")


@dataclass
class ControlledResourceReport:
    source: str
    canonical_entity: str
    source_ceiling: int
    page_ceiling: int
    source_records_read: int = 0
    canonical_records_emitted: int = 0
    records_skipped: int = 0
    mapping_errors: int = 0
    validation_errors: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    rejected: int = 0
    pages: int = 0
    completeness: str = "FAILED"
    failure_class: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "canonical_entity": self.canonical_entity,
            "source_ceiling": self.source_ceiling,
            "page_ceiling": self.page_ceiling,
            "source_records_read": self.source_records_read,
            "canonical_records_emitted": self.canonical_records_emitted,
            "records_skipped": self.records_skipped,
            "mapping_errors": self.mapping_errors,
            "validation_errors": self.validation_errors,
            "inserted": self.inserted,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "rejected": self.rejected,
            "pages": self.pages,
            "completeness": self.completeness,
            "failure_class": self.failure_class,
        }


@dataclass
class ControlledLoadResult:
    profile: str
    dry_run: bool
    reports: list[ControlledResourceReport] = field(default_factory=list)
    pre_counts: dict[str, int] = field(default_factory=dict)
    post_counts: dict[str, int] = field(default_factory=dict)
    stopped: bool = False
    stop_reason: str | None = None
    integrity: dict[str, int] = field(default_factory=dict)

    def as_dict(self, telemetry: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "dry_run": self.dry_run,
            "reports": [report.as_dict() for report in self.reports],
            "pre_counts": dict(self.pre_counts),
            "post_counts": dict(self.post_counts),
            "stopped": self.stopped,
            "stop_reason": self.stop_reason,
            "integrity": dict(self.integrity),
            "request_telemetry": dict(telemetry or {}),
        }


@dataclass(frozen=True)
class _ControlledRun:
    object_structure: str
    mode: str
    rows_seen: int
    upserted: int
    skipped: int
    errors: int
    watermark: None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def resolve_profile(name: str) -> ControlledProfile:
    try:
        return PROFILES[name]
    except KeyError as error:
        raise ValueError(f"unsupported controlled profile: {name}") from error


def resolve_source(name: str) -> str:
    try:
        return SOURCE_ALIASES[name.strip().lower()]
    except KeyError as error:
        raise ValueError(f"unsupported controlled source: {name}") from error


class ControlledMartLoader:
    """Run only the bounded ``initial-controlled`` profile."""

    def __init__(
        self,
        collector: CanonicalCollector,
        writer: MartWriter,
        store: CollectorStore,
        runtime_config: MaximoConfig,
        *,
        profile: ControlledProfile = INITIAL_CONTROLLED_PROFILE,
    ):
        self.collector = collector
        self.writer = writer
        self.store = store
        self.runtime_config = runtime_config
        self.profile = profile

    def _pre_counts(self) -> dict[str, int]:
        return {
            entity: self.store.count(model, exact_filters={"site_code": "BSR", "organization_code": "IP"})
            for entity, model in ENTITY_MODELS.items()
        }

    def _collect(
        self,
        source: str,
        *,
        source_cap: int,
        page_cap: int,
        workorder_records: list[Mapping[str, Any]],
    ) -> CanonicalCollection:
        kwargs = {"max_records": source_cap, "max_pages": page_cap}
        if source == "mxasset":
            return self.collector.collect_assets(**kwargs)
        if source == "mxwodetail":
            return self.collector.collect_workorders(**kwargs)
        if source == "ipfmea":
            return self.collector.collect_fmea(**kwargs)
        if source == "ipbhm":
            return self.collector.collect_bhm(**kwargs)
        if source == "iprcfa":
            return self.collector.collect_rcfa(**kwargs)
        if source == "ip_dom_oh":
            return self.collector.collect_overhauls(workorder_records, **kwargs)
        raise ValueError(f"unsupported controlled source: {source}")

    @staticmethod
    def _deduplicate_collection(collection: CanonicalCollection) -> int:
        """Remove repeated canonical IDs within one bounded source batch.

        Maximo can repeat a member across adjacent pages. Source-read counts
        remain unchanged; only the canonical batch sent to MartWriter is
        de-duplicated so one transaction cannot fail on its own primary key.
        """
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        duplicates = 0
        for record in collection.records:
            identity = str(record.get("canonical_id") or "")
            if identity and identity in seen:
                duplicates += 1
                continue
            if identity:
                seen.add(identity)
            unique.append(record)
        if duplicates:
            collection.records = unique
            collection.stats.canonical_records_emitted = len(unique)
            collection.stats.records_skipped += duplicates
        return duplicates

    @staticmethod
    def _report_from_collection(
        source: str,
        collection: CanonicalCollection,
        source_cap: int,
        page_cap: int,
    ) -> ControlledResourceReport:
        return ControlledResourceReport(
            source=source,
            canonical_entity=collection.canonical_entity,
            source_ceiling=source_cap,
            page_ceiling=page_cap,
            source_records_read=collection.stats.source_records_read,
            canonical_records_emitted=collection.stats.canonical_records_emitted,
            records_skipped=collection.stats.records_skipped,
            mapping_errors=collection.stats.mapping_errors,
            validation_errors=collection.stats.validation_errors,
            pages=collection.pages,
            completeness=collection.completeness,
            failure_class=collection.failure_class,
        )

    @staticmethod
    def _status_code(error: Exception) -> int | None:
        response = getattr(error, "response", None)
        status = getattr(response, "status_code", None)
        return int(status) if status is not None else None

    def _must_stop(self, error: Exception, failed_sources: set[str], source: str) -> str | None:
        if isinstance(error, OslcRequestBudgetExceeded):
            return "REQUEST_BUDGET_EXCEEDED"
        status = self._status_code(error)
        if status == 429:
            return "HTTP_429"
        if status in {401, 403}:
            return "AUTH_OR_SCOPE_FAILURE"
        if status is not None and 500 <= status <= 599:
            failed_sources.add(f"{source}:5xx:{status}")
            if len(failed_sources) >= 2:
                return "REPEATED_HTTP_5XX"
        return None

    def run(
        self,
        *,
        dry_run: bool = False,
        source: str | None = None,
        source_cap_override: int | None = None,
    ) -> ControlledLoadResult:
        selected = [resolve_source(source)] if source else list(RESOURCE_ORDER)
        if source_cap_override is not None:
            if not source:
                raise ValueError("source_cap_override requires --entity")
            if source_cap_override < 1 or source_cap_override > self.profile.ceiling_for(selected[0]):
                raise ValueError("source_cap_override is outside the controlled profile ceiling")
        result = ControlledLoadResult(self.profile.name, dry_run, pre_counts=self._pre_counts())
        workorder_records: list[Mapping[str, Any]] = []
        failed_servers: set[str] = set()

        for item in selected:
            cap = DRY_RUN_SOURCE_CAP if dry_run else (source_cap_override or self.profile.ceiling_for(item))
            page_cap = 1 if dry_run else self.profile.max_pages_for(item, self.runtime_config, cap)
            try:
                collection = self._collect(
                    item,
                    source_cap=cap,
                    page_cap=page_cap,
                    workorder_records=workorder_records,
                )
            except Exception as error:  # sanitized classification only
                config = canonical_config_for(item, self.runtime_config)
                report = ControlledResourceReport(
                    source=item,
                    canonical_entity=config.canonical_entity,
                    source_ceiling=cap,
                    page_ceiling=page_cap,
                    failure_class=type(error).__name__,
                )
                result.reports.append(report)
                stop_reason = self._must_stop(error, failed_servers, item)
                if stop_reason:
                    result.stopped = True
                    result.stop_reason = stop_reason
                    break
                continue

            self._deduplicate_collection(collection)
            report = self._report_from_collection(item, collection, cap, page_cap)
            result.reports.append(report)
            if item == "mxwodetail":
                workorder_records = list(collection.records)

            try:
                write_stats = self.writer.persist_collection(collection, dry_run=dry_run)
            except Exception as error:  # DB/contract failures stop honest reporting
                report.completeness = "FAILED"
                report.failure_class = type(error).__name__
                result.stopped = True
                result.stop_reason = "PERSISTENCE_FAILURE"
                break

            report.inserted = write_stats.records_inserted
            report.updated = write_stats.records_updated
            report.unchanged = write_stats.records_unchanged
            report.rejected = write_stats.records_rejected
            if not dry_run:
                self.store.record_run(_ControlledRun(
                    object_structure=item.upper(),
                    # CollectRunOrm.mode is an existing VARCHAR(20); keep the
                    # controlled-load marker within that legacy boundary.
                    mode="mart-initial",
                    rows_seen=report.source_records_read,
                    upserted=report.inserted + report.updated + report.unchanged,
                    skipped=report.records_skipped,
                    errors=report.mapping_errors + report.validation_errors,
                ))
                result.post_counts[collection.canonical_entity] = self.store.count(
                    ENTITY_MODELS[collection.canonical_entity],
                    exact_filters={"site_code": "BSR", "organization_code": "IP"},
                )

        if not dry_run:
            result.integrity = MartIntegrityAuditor(self.writer._db).audit()
            result.post_counts.update({
                entity: self.store.count(model, exact_filters={"site_code": "BSR", "organization_code": "IP"})
                for entity, model in ENTITY_MODELS.items()
            })
        return result
