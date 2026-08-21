"""Read-only, vendor-neutral Reliability Mart API."""

from __future__ import annotations

from datetime import datetime
from typing import Generic, Literal, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from src.repositories.mart_database import MartDatabase, MartDatabaseConfigError, get_mart_database
from src.repositories.mart_reader import MartQueryRepository, QueryPage
from src.services.reliability import ReliabilityQueryService, TimelineEvent

router = APIRouter(prefix="/v1/reliability", tags=["reliability-mart"])
Sort = Literal["updated_desc", "updated_asc", "status", "date_desc", "date_asc", "created_desc", "created_asc"]


class PageMeta(BaseModel):
    total: int
    offset: int
    limit: int
    has_more: bool


PageItem = TypeVar("PageItem")


class Page(BaseModel, Generic[PageItem]):
    items: list[PageItem]
    meta: PageMeta


class AssetView(BaseModel):
    canonical_id: str
    contract_version: str
    source_asset_number: str | None = None
    description: str | None = None
    status: str | None = None
    location_ref: str | None = None
    parent_asset_ref: str | None = None
    site_code: str
    organization_code: str
    asset_type: str | None = None
    plant: str | None = None
    unit: str | None = None
    source_updated_at: datetime | None = None


class MaintenanceView(BaseModel):
    canonical_id: str
    contract_version: str
    id: str
    equipment_id: str
    work_order_id: str | None = None
    event_type: str | None = None
    status: str | None = None
    actual_start: datetime | None = None
    actual_finish: datetime | None = None
    duration_hours: float | None = None
    labor_hours: float | None = None
    downtime_hours: float | None = None
    failure_code: str | None = None
    source_changed_at: datetime | None = None
    site_code: str
    organization_code: str


class FmeaView(BaseModel):
    canonical_id: str
    contract_version: str
    source_record_id: str | None = None
    source_number: str | None = None
    revision: str | None = None
    lifecycle_status: str | None = None
    description: str | None = None
    asset_ref: str | None = None
    failure_code_ref: str | None = None
    site_code: str
    organization_code: str
    source_updated_at: datetime | None = None
    status_changed_at: datetime | None = None


class RcfaView(BaseModel):
    canonical_id: str
    contract_version: str
    source_record_id: str | None = None
    source_number: str | None = None
    revision: str | None = None
    lifecycle_status: str | None = None
    category: str | None = None
    asset_ref: str | None = None
    location_ref: str | None = None
    workorder_ref: str | None = None
    failure_event_ref: str | None = None
    site_code: str
    organization_code: str
    source_created_at: datetime | None = None
    requested_at: datetime | None = None
    relationship_status: str = "UNRESOLVED"


class HealthView(BaseModel):
    canonical_id: str
    contract_version: str
    source_record_id: str | None = None
    revision: str | None = None
    lifecycle_status: str | None = None
    description: str | None = None
    function_description: str | None = None
    asset_ref: str | None = None
    site_code: str
    organization_code: str
    source_created_at: datetime | None = None
    source_updated_at: datetime | None = None
    status_changed_at: datetime | None = None


class OverhaulView(BaseModel):
    canonical_id: str
    contract_version: str
    source_record_id: str | None = None
    source_number: str | None = None
    lifecycle_status: str | None = None
    workorder_ref: str | None = None
    asset_ref: str | None = None
    site_code: str
    organization_code: str
    planned_start_at: datetime | None = None
    planned_finish_at: datetime | None = None
    actual_start_at: datetime | None = None
    actual_finish_at: datetime | None = None
    progress: object | None = None
    unresolved_attributes_present: bool = False


class TimelineView(BaseModel):
    event_id: str
    event_type: Literal["MAINTENANCE", "FMEA", "ASSET_HEALTH", "OVERHAUL"]
    event_at: datetime | None = None
    summary: str | None = None
    status: str | None = None
    canonical_ref: str


class IntegrityView(BaseModel):
    asset_refs_total: int = 0
    asset_refs_resolved: int = 0
    asset_refs_unresolved: int = 0
    workorder_refs_total: int = 0
    workorder_refs_resolved: int = 0
    workorder_refs_unresolved: int = 0
    technical_asset_context_total: int = 0
    registered_assets_total: int = 0
    registered_assets_resolved: int = 0
    registered_assets_unresolved: int = 0
    maintenance_registered_total: int = 0


class RegistryView(BaseModel):
    registered_asset_count: int
    snapshot_sha256: str | None = None
    snapshot_row_count: int | None = None
    snapshot_imported_at: datetime | None = None
    source: str


EvidenceClass = Literal["VERIFIED", "DERIVED_SAFE", "BUSINESS_SEMANTICS_REQUIRED", "DATA_NOT_AVAILABLE", "DEFERRED"]


class EvidenceValue(BaseModel):
    value: int
    evidence_class: EvidenceClass


class DecisionScopeView(BaseModel):
    site_code: Literal["BSR"]
    organization_code: Literal["IP"]
    registry_scope: str
    maintenance_source: str
    date_basis: str


class DataMaturityView(BaseModel):
    asset_maintenance: str
    controlled_domains: str
    rcfa_relationship: str
    technical_context: str


class DecisionSummaryView(BaseModel):
    registered_assets: EvidenceValue
    maintenance_activity_7d: EvidenceValue
    maintenance_activity_30d: EvidenceValue
    maintenance_activity_90d: EvidenceValue
    assets_active_7d: EvidenceValue
    assets_active_30d: EvidenceValue
    assets_active_90d: EvidenceValue


class ActivityTrendView(BaseModel):
    period_start: datetime
    period_end: datetime
    event_count: EvidenceValue


class DistributionView(BaseModel):
    value: str
    count: EvidenceValue


class ActivityConcentrationView(BaseModel):
    asset_ref: str
    source_asset_number: str
    description: str | None = None
    event_count: EvidenceValue
    latest_activity: datetime | None = None


class RecordAvailabilityView(BaseModel):
    fmea_records: EvidenceValue
    fmea_assets_represented: EvidenceValue
    asset_health_records: EvidenceValue
    asset_health_assets_represented: EvidenceValue
    rcfa_records: EvidenceValue
    overhaul_records: EvidenceValue


class DecisionOverviewView(BaseModel):
    scope: DecisionScopeView
    data_maturity: DataMaturityView
    window_days: Literal[7, 30, 90]
    window_start: datetime
    as_of: datetime
    summary: DecisionSummaryView
    maintenance_activity: list[ActivityTrendView]
    status_distribution: list[DistributionView]
    work_type_distribution: list[DistributionView]
    activity_concentration: list[ActivityConcentrationView]
    record_availability: RecordAvailabilityView
    integrity: IntegrityView


class ContextView(BaseModel):
    asset: AssetView
    maintenance: list[MaintenanceView]
    fmea: list[FmeaView]
    health: list[HealthView]
    overhauls: list[OverhaulView]
    rcfa_relationship_status: Literal["UNRESOLVED"]
    relationship_health: IntegrityView


def _db() -> MartDatabase:
    try:
        database = get_mart_database()
        if not database.healthcheck():
            raise MartDatabaseConfigError("Reliability Mart health check failed")
        return database
    except (MartDatabaseConfigError, ValueError, SQLAlchemyError) as error:
        raise HTTPException(status_code=503, detail="Reliability Mart is unavailable") from error


def _service(db: MartDatabase = Depends(_db)) -> ReliabilityQueryService:
    return ReliabilityQueryService(MartQueryRepository(db))


def _page(page: QueryPage, converter) -> dict:
    return {"items": [converter(item) for item in page.items], "meta": PageMeta(total=page.total, offset=page.offset, limit=page.limit, has_more=page.has_more)}


def _asset(row) -> AssetView:
    return AssetView.model_validate({k: getattr(row, k) for k in AssetView.model_fields})


def _maintenance(row) -> MaintenanceView:
    return MaintenanceView.model_validate({k: getattr(row, k) for k in MaintenanceView.model_fields})


def _fmea(row) -> FmeaView:
    return FmeaView.model_validate({k: getattr(row, k) for k in FmeaView.model_fields})


def _rcfa(row) -> RcfaView:
    return RcfaView.model_validate({k: getattr(row, k) for k in RcfaView.model_fields if hasattr(row, k)})


def _health(row) -> HealthView:
    return HealthView.model_validate({k: getattr(row, k) for k in HealthView.model_fields})


def _overhaul(row) -> OverhaulView:
    return OverhaulView.model_validate({k: getattr(row, k) for k in OverhaulView.model_fields if k not in {"unresolved_attributes_present"}} | {"unresolved_attributes_present": bool(row.unresolved_source_attributes)})


def _timeline(row: TimelineEvent) -> TimelineView:
    return TimelineView.model_validate(row.__dict__)


def _validate_range(start: datetime | None, end: datetime | None) -> None:
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="date range start must not be after end")


def _evidence(value: int, evidence_class: EvidenceClass) -> EvidenceValue:
    return EvidenceValue(value=value, evidence_class=evidence_class)


def _decision_overview(raw: dict[str, object], window_days: int) -> DecisionOverviewView:
    summary = raw["summary"]
    records = raw["records"]
    assert isinstance(summary, dict)
    assert isinstance(records, dict)
    return DecisionOverviewView(
        scope=DecisionScopeView(
            site_code="BSR",
            organization_code="IP",
            registry_scope="reliability_asset_registry",
            maintenance_source="Local Collector → Reliability Mart",
            date_basis="COALESCE(actual_start, source_changed_at)",
        ),
        data_maturity=DataMaturityView(
            asset_maintenance="CURRENT LOCAL PROJECTION",
            controlled_domains="CONTROLLED MART POPULATION",
            rcfa_relationship="RELATIONSHIP UNRESOLVED",
            technical_context="TECHNICAL CONTEXT",
        ),
        window_days=window_days,
        window_start=raw["window_start"],
        as_of=raw["as_of"],
        summary=DecisionSummaryView(
            registered_assets=_evidence(int(raw["registered_assets"]), "VERIFIED"),
            maintenance_activity_7d=_evidence(int(summary["maintenance_activity_7d"]), "DERIVED_SAFE"),
            maintenance_activity_30d=_evidence(int(summary["maintenance_activity_30d"]), "DERIVED_SAFE"),
            maintenance_activity_90d=_evidence(int(summary["maintenance_activity_90d"]), "DERIVED_SAFE"),
            assets_active_7d=_evidence(int(summary["assets_active_7d"]), "DERIVED_SAFE"),
            assets_active_30d=_evidence(int(summary["assets_active_30d"]), "DERIVED_SAFE"),
            assets_active_90d=_evidence(int(summary["assets_active_90d"]), "DERIVED_SAFE"),
        ),
        maintenance_activity=[
            ActivityTrendView(
                period_start=row["period_start"],
                period_end=row["period_end"],
                event_count=_evidence(int(row["event_count"]), "DERIVED_SAFE"),
            )
            for row in raw["trend"]
        ],
        status_distribution=[
            DistributionView(value=row["value"], count=_evidence(int(row["count"]), "DERIVED_SAFE"))
            for row in raw["status_distribution"]
        ],
        work_type_distribution=[
            DistributionView(value=row["value"], count=_evidence(int(row["count"]), "DERIVED_SAFE"))
            for row in raw["work_type_distribution"]
        ],
        activity_concentration=[
            ActivityConcentrationView(
                asset_ref=row["asset_ref"],
                source_asset_number=row["source_asset_number"],
                description=row["description"],
                event_count=_evidence(int(row["event_count"]), "DERIVED_SAFE"),
                latest_activity=row["latest_activity"],
            )
            for row in raw["activity_concentration"]
        ],
        record_availability=RecordAvailabilityView(
            fmea_records=_evidence(int(records["fmea_records"]), "VERIFIED"),
            fmea_assets_represented=_evidence(int(records["fmea_assets_represented"]), "DERIVED_SAFE"),
            asset_health_records=_evidence(int(records["asset_health_records"]), "VERIFIED"),
            asset_health_assets_represented=_evidence(int(records["asset_health_assets_represented"]), "DERIVED_SAFE"),
            rcfa_records=_evidence(int(records["rcfa_records"]), "VERIFIED"),
            overhaul_records=_evidence(int(records["overhaul_records"]), "VERIFIED"),
        ),
        integrity=IntegrityView(**raw["integrity"]),
    )


@router.get("/assets", response_model=Page[AssetView], summary="List Reliability Mart assets")
def list_assets(
    status: str | None = None,
    unit: str | None = None,
    asset_type: str | None = None,
    site_code: Literal["BSR"] = "BSR",
    organization_code: Literal["IP"] = "IP",
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: Literal["updated_desc", "updated_asc", "status"] = "updated_desc",
    service: ReliabilityQueryService = Depends(_service),
):
    page = service.repository.list_assets(status=status, unit=unit, asset_type=asset_type, offset=offset, limit=limit, sort=sort)
    return _page(page, _asset)


@router.get("/registry", response_model=RegistryView, summary="Current registered Reliability Asset snapshot")
def registry(service: ReliabilityQueryService = Depends(_service)) -> RegistryView:
    return RegistryView(**service.repository.registry_summary())


@router.get("/decision-overview", response_model=DecisionOverviewView, summary="Bounded factual Reliability decision overview")
def decision_overview(
    window_days: int = Query(30, enum=[7, 30, 90]),
    service: ReliabilityQueryService = Depends(_service),
) -> DecisionOverviewView:
    if window_days not in {7, 30, 90}:
        raise HTTPException(status_code=422, detail="window_days must be one of 7, 30, or 90")
    return _decision_overview(service.repository.decision_overview(window_days=window_days), window_days)


@router.get("/assets/{canonical_id}", response_model=AssetView)
def get_asset(canonical_id: str, service: ReliabilityQueryService = Depends(_service)) -> AssetView:
    row = service.repository.get_asset(canonical_id)
    if row is None:
        raise HTTPException(status_code=404, detail="asset not found")
    return _asset(row)


@router.get("/assets/{canonical_id}/context", response_model=ContextView)
def asset_context(canonical_id: str, service: ReliabilityQueryService = Depends(_service)) -> ContextView:
    context = service.asset_context(canonical_id)
    if context is None:
        raise HTTPException(status_code=404, detail="asset not found")
    return ContextView(
        asset=_asset(context["asset"]),
        maintenance=[_maintenance(row) for row in context["maintenance"].items],
        fmea=[_fmea(row) for row in context["fmea"].items],
        health=[_health(row) for row in context["health"].items],
        overhauls=[_overhaul(row) for row in context["overhauls"].items],
        rcfa_relationship_status=context["rcfa_relationship_status"],
        relationship_health=IntegrityView(**context["relationship_health"]),
    )


@router.get("/assets/{canonical_id}/fmea", response_model=Page[FmeaView])
def asset_fmea(canonical_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), service: ReliabilityQueryService = Depends(_service)):
    if service.repository.get_asset(canonical_id) is None:
        raise HTTPException(status_code=404, detail="asset not found")
    return _page(service.repository.list_fmea(asset_ref=canonical_id, offset=offset, limit=limit), _fmea)


@router.get("/assets/{canonical_id}/health-assessments", response_model=Page[HealthView])
def asset_health(canonical_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), service: ReliabilityQueryService = Depends(_service)):
    if service.repository.get_asset(canonical_id) is None:
        raise HTTPException(status_code=404, detail="asset not found")
    return _page(service.repository.list_health(asset_ref=canonical_id, offset=offset, limit=limit), _health)


@router.get("/assets/{canonical_id}/health/latest", response_model=HealthView)
def latest_health(canonical_id: str, service: ReliabilityQueryService = Depends(_service)) -> HealthView:
    if service.repository.get_asset(canonical_id) is None:
        raise HTTPException(status_code=404, detail="asset not found")
    row = service.repository.latest_health(canonical_id)
    if row is None:
        raise HTTPException(status_code=404, detail="health assessment not found")
    return _health(row)


@router.get("/assets/{canonical_id}/timeline", response_model=Page[TimelineView])
def asset_timeline(canonical_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), service: ReliabilityQueryService = Depends(_service)):
    if service.repository.get_asset(canonical_id) is None:
        raise HTTPException(status_code=404, detail="asset not found")
    return _page(service.timeline(canonical_id, offset=offset, limit=limit), _timeline)


@router.get("/maintenance-events", response_model=Page[MaintenanceView])
def maintenance_events(
    asset_ref: str | None = None, work_order_id: str | None = None, status: str | None = None, event_type: str | None = None,
    date_from: datetime | None = None, date_to: datetime | None = None, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200),
    sort: Literal["date_desc", "date_asc", "status"] = "date_desc", service: ReliabilityQueryService = Depends(_service),
):
    _validate_range(date_from, date_to)
    return _page(service.repository.list_maintenance(asset_ref=asset_ref, work_order_id=work_order_id, status=status, event_type=event_type, date_from=date_from, date_to=date_to, offset=offset, limit=limit, sort=sort), _maintenance)


@router.get("/fmea", response_model=Page[FmeaView])
def fmea(asset_ref: str | None = None, lifecycle_status: str | None = None, source_number: str | None = None, updated_from: datetime | None = None, updated_to: datetime | None = None, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), sort: Literal["updated_desc", "updated_asc", "status"] = "updated_desc", service: ReliabilityQueryService = Depends(_service)):
    _validate_range(updated_from, updated_to)
    return _page(service.repository.list_fmea(asset_ref=asset_ref, lifecycle_status=lifecycle_status, source_number=source_number, updated_from=updated_from, updated_to=updated_to, offset=offset, limit=limit, sort=sort), _fmea)


@router.get("/asset-health", response_model=Page[HealthView])
def asset_health_list(asset_ref: str | None = None, lifecycle_status: str | None = None, updated_from: datetime | None = None, updated_to: datetime | None = None, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), sort: Literal["updated_desc", "updated_asc", "status"] = "updated_desc", service: ReliabilityQueryService = Depends(_service)):
    _validate_range(updated_from, updated_to)
    return _page(service.repository.list_health(asset_ref=asset_ref, lifecycle_status=lifecycle_status, updated_from=updated_from, updated_to=updated_to, offset=offset, limit=limit, sort=sort), _health)


@router.get("/rcfa", response_model=Page[RcfaView])
def rcfa(lifecycle_status: str | None = None, category: str | None = None, source_number: str | None = None, asset_ref: str | None = None, created_from: datetime | None = None, created_to: datetime | None = None, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), sort: Literal["created_desc", "created_asc", "status"] = "created_desc", service: ReliabilityQueryService = Depends(_service)):
    if asset_ref is not None:
        raise HTTPException(status_code=422, detail="asset_ref filter is unavailable because RCFA asset relationship is unresolved")
    _validate_range(created_from, created_to)
    return _page(service.repository.list_rcfa(lifecycle_status=lifecycle_status, category=category, source_number=source_number, created_from=created_from, created_to=created_to, offset=offset, limit=limit, sort=sort), _rcfa)


@router.get("/overhauls", response_model=Page[OverhaulView])
def overhauls(asset_ref: str | None = None, workorder_ref: str | None = None, lifecycle_status: str | None = None, planned_from: datetime | None = None, planned_to: datetime | None = None, actual_from: datetime | None = None, actual_to: datetime | None = None, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), sort: Literal["date_desc", "date_asc", "status"] = "date_desc", service: ReliabilityQueryService = Depends(_service)):
    _validate_range(planned_from, planned_to)
    _validate_range(actual_from, actual_to)
    return _page(service.repository.list_overhauls(asset_ref=asset_ref, workorder_ref=workorder_ref, lifecycle_status=lifecycle_status, planned_from=planned_from, planned_to=planned_to, actual_from=actual_from, actual_to=actual_to, offset=offset, limit=limit, sort=sort), _overhaul)


@router.get("/integrity", response_model=IntegrityView)
def integrity(service: ReliabilityQueryService = Depends(_service)) -> IntegrityView:
    return IntegrityView(**service.repository.integrity_summary())
