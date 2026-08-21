"""Read-only query repository for the MX-009R Reliability Mart."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import Select, asc, desc, func, select

from src.repositories.mart_models import (
    AssetHealthAssessmentMart,
    AssetMasterMart,
    FmeaAssessmentMart,
    MaintenanceEventMart,
    OverhaulEventMart,
    RcfaAnalysisMart,
    ReliabilityAssetRegistryMart,
)
from src.repositories.mart_database import MartDatabase

T = TypeVar("T")
SITE_CODE = "BSR"
ORGANIZATION_CODE = "IP"


@dataclass(frozen=True)
class QueryPage:
    items: list[Any]
    total: int
    offset: int
    limit: int

    @property
    def has_more(self) -> bool:
        return self.offset + len(self.items) < self.total


def _page(session: Any, statement: Select[Any], offset: int, limit: int) -> QueryPage:
    count_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = int(session.scalar(count_statement) or 0)
    items = list(session.scalars(statement.offset(offset).limit(limit)).all())
    return QueryPage(items=items, total=total, offset=offset, limit=limit)


class MartQueryRepository:
    """SQL-only read access to the six canonical Mart entities.

    Scope is applied in every method as defense in depth.  This repository has
    no persistence methods and receives a ``MartDatabase`` that exposes only a
    read-only session wrapper.
    """

    def __init__(self, database: MartDatabase):
        self.database = database

    @staticmethod
    def _scope(statement: Select[Any], model: type) -> Select[Any]:
        return statement.where(
            model.site_code == SITE_CODE,
            model.organization_code == ORGANIZATION_CODE,
        )

    @staticmethod
    def _sort(statement: Select[Any], column: Any, reverse: bool = True) -> Select[Any]:
        return statement.order_by(desc(column) if reverse else asc(column), asc(column))

    def list_assets(
        self,
        *,
        status: str | None = None,
        unit: str | None = None,
        asset_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
        sort: str = "updated_desc",
    ) -> QueryPage:
        statement = self._scope(
            select(AssetMasterMart)
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == AssetMasterMart.canonical_id)
            .where(
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            ),
            AssetMasterMart,
        )
        if status:
            statement = statement.where(AssetMasterMart.status == status)
        if unit:
            statement = statement.where(AssetMasterMart.unit == unit)
        if asset_type:
            statement = statement.where(AssetMasterMart.asset_type == asset_type)
        if sort == "status":
            statement = self._sort(statement, AssetMasterMart.status, False)
        else:
            statement = self._sort(statement, AssetMasterMart.source_updated_at, sort != "updated_asc")
        with self.database.read_session() as session:
            return _page(session, statement, offset, limit)

    def get_asset(self, canonical_id: str) -> AssetMasterMart | None:
        statement = self._scope(
            select(AssetMasterMart)
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == AssetMasterMart.canonical_id)
            .where(
                AssetMasterMart.canonical_id == canonical_id,
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            ),
            AssetMasterMart,
        )
        with self.database.read_session() as session:
            return session.scalar(statement)

    def list_maintenance(
        self,
        *,
        asset_ref: str | None = None,
        work_order_id: str | None = None,
        status: str | None = None,
        event_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
        sort: str = "date_desc",
    ) -> QueryPage:
        statement = self._scope(
            select(MaintenanceEventMart)
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == MaintenanceEventMart.equipment_id)
            .where(
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            ),
            MaintenanceEventMart,
        )
        if asset_ref:
            statement = statement.where(MaintenanceEventMart.equipment_id == asset_ref)
        if work_order_id:
            statement = statement.where(MaintenanceEventMart.work_order_id == work_order_id)
        if status:
            statement = statement.where(MaintenanceEventMart.status == status)
        if event_type:
            statement = statement.where(MaintenanceEventMart.event_type == event_type)
        date_column = func.coalesce(MaintenanceEventMart.actual_start, MaintenanceEventMart.source_changed_at)
        if date_from:
            statement = statement.where(date_column >= date_from)
        if date_to:
            statement = statement.where(date_column <= date_to)
        column = MaintenanceEventMart.status if sort == "status" else date_column
        statement = self._sort(statement, column, sort not in {"date_asc"})
        with self.database.read_session() as session:
            return _page(session, statement, offset, limit)

    def list_fmea(
        self,
        *,
        asset_ref: str | None = None,
        lifecycle_status: str | None = None,
        source_number: str | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
        sort: str = "updated_desc",
    ) -> QueryPage:
        statement = self._scope(select(FmeaAssessmentMart), FmeaAssessmentMart)
        if asset_ref:
            statement = statement.where(FmeaAssessmentMart.asset_ref == asset_ref)
        if lifecycle_status:
            statement = statement.where(FmeaAssessmentMart.lifecycle_status == lifecycle_status)
        if source_number:
            statement = statement.where(FmeaAssessmentMart.source_number == source_number)
        if updated_from:
            statement = statement.where(FmeaAssessmentMart.source_updated_at >= updated_from)
        if updated_to:
            statement = statement.where(FmeaAssessmentMart.source_updated_at <= updated_to)
        column = FmeaAssessmentMart.lifecycle_status if sort == "status" else FmeaAssessmentMart.source_updated_at
        statement = self._sort(statement, column, sort != "updated_asc")
        with self.database.read_session() as session:
            return _page(session, statement, offset, limit)

    def list_health(
        self,
        *,
        asset_ref: str | None = None,
        lifecycle_status: str | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
        sort: str = "updated_desc",
    ) -> QueryPage:
        statement = self._scope(select(AssetHealthAssessmentMart), AssetHealthAssessmentMart)
        if asset_ref:
            statement = statement.where(AssetHealthAssessmentMart.asset_ref == asset_ref)
        if lifecycle_status:
            statement = statement.where(AssetHealthAssessmentMart.lifecycle_status == lifecycle_status)
        if updated_from:
            statement = statement.where(AssetHealthAssessmentMart.source_updated_at >= updated_from)
        if updated_to:
            statement = statement.where(AssetHealthAssessmentMart.source_updated_at <= updated_to)
        column = AssetHealthAssessmentMart.lifecycle_status if sort == "status" else AssetHealthAssessmentMart.source_updated_at
        statement = self._sort(statement, column, sort != "updated_asc")
        with self.database.read_session() as session:
            return _page(session, statement, offset, limit)

    def latest_health(self, asset_ref: str) -> AssetHealthAssessmentMart | None:
        statement = self._scope(
            select(AssetHealthAssessmentMart).where(AssetHealthAssessmentMart.asset_ref == asset_ref),
            AssetHealthAssessmentMart,
        ).order_by(
            desc(AssetHealthAssessmentMart.status_changed_at),
            desc(AssetHealthAssessmentMart.source_updated_at),
            desc(AssetHealthAssessmentMart.source_created_at),
        )
        with self.database.read_session() as session:
            return session.scalar(statement.limit(1))

    def list_rcfa(
        self,
        *,
        lifecycle_status: str | None = None,
        category: str | None = None,
        source_number: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
        sort: str = "created_desc",
    ) -> QueryPage:
        statement = self._scope(select(RcfaAnalysisMart), RcfaAnalysisMart)
        if lifecycle_status:
            statement = statement.where(RcfaAnalysisMart.lifecycle_status == lifecycle_status)
        if category:
            statement = statement.where(RcfaAnalysisMart.category == category)
        if source_number:
            statement = statement.where(RcfaAnalysisMart.source_number == source_number)
        if created_from:
            statement = statement.where(RcfaAnalysisMart.source_created_at >= created_from)
        if created_to:
            statement = statement.where(RcfaAnalysisMart.source_created_at <= created_to)
        column = RcfaAnalysisMart.lifecycle_status if sort == "status" else RcfaAnalysisMart.source_created_at
        statement = self._sort(statement, column, sort != "created_asc")
        with self.database.read_session() as session:
            return _page(session, statement, offset, limit)

    def list_overhauls(
        self,
        *,
        asset_ref: str | None = None,
        workorder_ref: str | None = None,
        lifecycle_status: str | None = None,
        planned_from: datetime | None = None,
        planned_to: datetime | None = None,
        actual_from: datetime | None = None,
        actual_to: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
        sort: str = "date_desc",
    ) -> QueryPage:
        statement = self._scope(select(OverhaulEventMart), OverhaulEventMart)
        if asset_ref:
            statement = statement.where(OverhaulEventMart.asset_ref == asset_ref)
        if workorder_ref:
            statement = statement.where(OverhaulEventMart.workorder_ref == workorder_ref)
        if lifecycle_status:
            statement = statement.where(OverhaulEventMart.lifecycle_status == lifecycle_status)
        if planned_from:
            statement = statement.where(OverhaulEventMart.planned_start_at >= planned_from)
        if planned_to:
            statement = statement.where(OverhaulEventMart.planned_start_at <= planned_to)
        if actual_from:
            statement = statement.where(OverhaulEventMart.actual_start_at >= actual_from)
        if actual_to:
            statement = statement.where(OverhaulEventMart.actual_start_at <= actual_to)
        column = OverhaulEventMart.lifecycle_status if sort == "status" else OverhaulEventMart.actual_start_at
        statement = self._sort(statement, column, sort != "date_asc")
        with self.database.read_session() as session:
            return _page(session, statement, offset, limit)

    def integrity_summary(self) -> dict[str, int]:
        with self.database.read_session() as session:
            technical_asset_total = session.scalar(select(func.count(AssetMasterMart.canonical_id)).where(
                AssetMasterMart.site_code == SITE_CODE,
                AssetMasterMart.organization_code == ORGANIZATION_CODE,
            )) or 0
            registered_total = session.scalar(select(func.count(ReliabilityAssetRegistryMart.asset_ref)).where(
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            )) or 0
            registered_resolved = session.scalar(select(func.count(ReliabilityAssetRegistryMart.asset_ref)).join(
                AssetMasterMart, ReliabilityAssetRegistryMart.asset_ref == AssetMasterMart.canonical_id
            ).where(
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            )) or 0
            maintenance_registered_total = session.scalar(select(func.count(MaintenanceEventMart.canonical_id)).join(
                ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == MaintenanceEventMart.equipment_id
            ).where(
                MaintenanceEventMart.site_code == SITE_CODE,
                MaintenanceEventMart.organization_code == ORGANIZATION_CODE,
            )) or 0
            asset_total = session.scalar(select(func.count(FmeaAssessmentMart.canonical_id)).where(
                FmeaAssessmentMart.site_code == SITE_CODE,
                FmeaAssessmentMart.organization_code == ORGANIZATION_CODE,
                FmeaAssessmentMart.asset_ref.is_not(None),
            )) or 0
            asset_total += session.scalar(select(func.count(AssetHealthAssessmentMart.canonical_id)).where(
                AssetHealthAssessmentMart.site_code == SITE_CODE,
                AssetHealthAssessmentMart.organization_code == ORGANIZATION_CODE,
                AssetHealthAssessmentMart.asset_ref.is_not(None),
            )) or 0
            asset_total += session.scalar(select(func.count(MaintenanceEventMart.canonical_id)).where(
                MaintenanceEventMart.site_code == SITE_CODE,
                MaintenanceEventMart.organization_code == ORGANIZATION_CODE,
                MaintenanceEventMart.equipment_id.is_not(None),
            )) or 0
            asset_total += session.scalar(select(func.count(OverhaulEventMart.canonical_id)).where(
                OverhaulEventMart.site_code == SITE_CODE,
                OverhaulEventMart.organization_code == ORGANIZATION_CODE,
                OverhaulEventMart.asset_ref.is_not(None),
            )) or 0
            asset_master_ids = select(AssetMasterMart.canonical_id).where(
                AssetMasterMart.site_code == SITE_CODE,
                AssetMasterMart.organization_code == ORGANIZATION_CODE,
            )
            asset_resolved = session.scalar(select(func.count(FmeaAssessmentMart.canonical_id)).where(
                FmeaAssessmentMart.site_code == SITE_CODE,
                FmeaAssessmentMart.organization_code == ORGANIZATION_CODE,
                FmeaAssessmentMart.asset_ref.in_(asset_master_ids),
            )) or 0
            asset_resolved += session.scalar(select(func.count(AssetHealthAssessmentMart.canonical_id)).where(
                AssetHealthAssessmentMart.site_code == SITE_CODE,
                AssetHealthAssessmentMart.organization_code == ORGANIZATION_CODE,
                AssetHealthAssessmentMart.asset_ref.in_(asset_master_ids),
            )) or 0
            asset_resolved += session.scalar(select(func.count(MaintenanceEventMart.canonical_id)).where(
                MaintenanceEventMart.site_code == SITE_CODE,
                MaintenanceEventMart.organization_code == ORGANIZATION_CODE,
                MaintenanceEventMart.equipment_id.in_(asset_master_ids),
            )) or 0
            asset_resolved += session.scalar(select(func.count(OverhaulEventMart.canonical_id)).where(
                OverhaulEventMart.site_code == SITE_CODE,
                OverhaulEventMart.organization_code == ORGANIZATION_CODE,
                OverhaulEventMart.asset_ref.in_(asset_master_ids),
            )) or 0
            work_total = session.scalar(select(func.count(OverhaulEventMart.canonical_id)).where(
                OverhaulEventMart.site_code == SITE_CODE,
                OverhaulEventMart.organization_code == ORGANIZATION_CODE,
                OverhaulEventMart.workorder_ref.is_not(None),
            )) or 0
            work_resolved = session.scalar(select(func.count(OverhaulEventMart.canonical_id)).where(
                OverhaulEventMart.site_code == SITE_CODE,
                OverhaulEventMart.organization_code == ORGANIZATION_CODE,
                OverhaulEventMart.workorder_ref.in_(
                    select(MaintenanceEventMart.work_order_id).where(
                        MaintenanceEventMart.site_code == SITE_CODE,
                        MaintenanceEventMart.organization_code == ORGANIZATION_CODE,
                        MaintenanceEventMart.work_order_id.is_not(None),
                    )
                ),
            )) or 0
        return {
            "asset_refs_total": int(asset_total),
            "asset_refs_resolved": int(min(asset_resolved, asset_total)),
            "asset_refs_unresolved": int(max(asset_total - asset_resolved, 0)),
            "workorder_refs_total": int(work_total),
            "workorder_refs_resolved": int(work_resolved),
            "workorder_refs_unresolved": int(work_total - work_resolved),
            "technical_asset_context_total": int(technical_asset_total),
            "registered_assets_total": int(registered_total),
            "registered_assets_resolved": int(registered_resolved),
            "registered_assets_unresolved": int(registered_total - registered_resolved),
            "maintenance_registered_total": int(maintenance_registered_total),
        }

    def registry_summary(self) -> dict[str, object]:
        with self.database.read_session() as session:
            row = session.execute(
                select(
                    func.count(ReliabilityAssetRegistryMart.asset_ref),
                    func.max(ReliabilityAssetRegistryMart.snapshot_sha256),
                    func.max(ReliabilityAssetRegistryMart.snapshot_row_count),
                    func.max(ReliabilityAssetRegistryMart.snapshot_imported_at),
                ).where(
                    ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                    ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
                )
            ).one()
        return {
            "registered_asset_count": int(row[0] or 0),
            "snapshot_sha256": row[1],
            "snapshot_row_count": row[2],
            "snapshot_imported_at": row[3],
            "source": "MAXIMO_LIST_OF_ASSETS",
        }
