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
