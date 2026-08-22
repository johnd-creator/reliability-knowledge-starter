"""Read-only query repository for the MX-009R Reliability Mart."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, TypeVar

from sqlalchemy import Select, asc, case, desc, func, select

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


def _raw_work_type(column: Any) -> Any:
    """Read the quarantined source Work Type on PostgreSQL and SQLite."""

    return func.nullif(func.trim(column["maximo"]["worktype"].as_string()), "")


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

    def _gap_days(self, later: Any, earlier: Any) -> Any:
        if self.database.engine.dialect.name == "sqlite":
            return func.julianday(later) - func.julianday(earlier)
        return func.extract("epoch", later - earlier) / 86400.0

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

    def decision_overview(
        self,
        *,
        window_days: int = 30,
        as_of: datetime | None = None,
    ) -> dict[str, object]:
        """Return bounded, read-only aggregates for the NADI decision surface.

        The method deliberately keeps all maintenance metrics on the Registry
        join.  It never selects maintenance rows into Python; only grouped and
        scalar aggregate results cross the Mart boundary.
        """
        if window_days not in {7, 30, 90}:
            raise ValueError("window_days must be one of 7, 30, or 90")
        current = as_of or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        window_start = current - timedelta(days=window_days)
        date_column = func.coalesce(MaintenanceEventMart.actual_start, MaintenanceEventMart.source_changed_at)
        maintenance_scope = (
            select(MaintenanceEventMart)
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == MaintenanceEventMart.equipment_id)
            .where(
                MaintenanceEventMart.site_code == SITE_CODE,
                MaintenanceEventMart.organization_code == ORGANIZATION_CODE,
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            )
        ).subquery()
        scoped_date = func.coalesce(maintenance_scope.c.actual_start, maintenance_scope.c.source_changed_at)

        week_start = datetime(current.year, current.month, current.day, tzinfo=current.tzinfo) - timedelta(days=current.weekday())
        trend_starts = [week_start - timedelta(weeks=offset) for offset in range(11, -1, -1)]
        trend_counts = [
            func.count(maintenance_scope.c.canonical_id).filter(
                scoped_date >= start,
                scoped_date < start + timedelta(weeks=1),
            ).label(f"week_{index}")
            for index, start in enumerate(trend_starts)
        ]

        summary_statement = select(
            func.count(maintenance_scope.c.canonical_id).filter(scoped_date >= current - timedelta(days=7), scoped_date <= current).label("maintenance_7d"),
            func.count(maintenance_scope.c.canonical_id).filter(scoped_date >= current - timedelta(days=30), scoped_date <= current).label("maintenance_30d"),
            func.count(maintenance_scope.c.canonical_id).filter(scoped_date >= current - timedelta(days=90), scoped_date <= current).label("maintenance_90d"),
            func.count(func.distinct(maintenance_scope.c.equipment_id)).filter(scoped_date >= current - timedelta(days=7), scoped_date <= current).label("assets_active_7d"),
            func.count(func.distinct(maintenance_scope.c.equipment_id)).filter(scoped_date >= current - timedelta(days=30), scoped_date <= current).label("assets_active_30d"),
            func.count(func.distinct(maintenance_scope.c.equipment_id)).filter(scoped_date >= current - timedelta(days=90), scoped_date <= current).label("assets_active_90d"),
        )
        status_value = func.coalesce(maintenance_scope.c.status, "UNKNOWN")
        raw_work_type = _raw_work_type(maintenance_scope.c.sources)
        canonical_work_type = func.nullif(func.trim(maintenance_scope.c.event_type), "")
        work_type_value = func.coalesce(raw_work_type, canonical_work_type, "UNKNOWN")
        window_statement = select(
            status_value.label("value"),
            func.count(maintenance_scope.c.canonical_id).label("count"),
        ).where(scoped_date >= window_start, scoped_date <= current).group_by(status_value).order_by(status_value)
        work_type_statement = select(
            work_type_value.label("value"),
            func.count(maintenance_scope.c.canonical_id).label("count"),
        ).where(scoped_date >= window_start, scoped_date <= current).group_by(work_type_value).order_by(work_type_value)
        concentration_count = func.count(maintenance_scope.c.canonical_id).label("event_count")
        concentration_latest = func.max(scoped_date).label("latest_activity")
        concentration_statement = (
            select(
                ReliabilityAssetRegistryMart.asset_ref,
                ReliabilityAssetRegistryMart.source_asset_number,
                AssetMasterMart.description,
                concentration_count,
                concentration_latest,
            )
            .select_from(maintenance_scope)
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == maintenance_scope.c.equipment_id)
            .outerjoin(AssetMasterMart, AssetMasterMart.canonical_id == maintenance_scope.c.equipment_id)
            .where(scoped_date >= window_start, scoped_date <= current)
            .group_by(
                ReliabilityAssetRegistryMart.asset_ref,
                ReliabilityAssetRegistryMart.source_asset_number,
                AssetMasterMart.description,
            )
            .order_by(desc(concentration_count), desc(concentration_latest), asc(ReliabilityAssetRegistryMart.source_asset_number), asc(ReliabilityAssetRegistryMart.asset_ref))
            .limit(10)
        )
        trend_statement = select(*trend_counts)

        records_statement = select(
            select(func.count(FmeaAssessmentMart.canonical_id)).where(
                FmeaAssessmentMart.site_code == SITE_CODE,
                FmeaAssessmentMart.organization_code == ORGANIZATION_CODE,
            ).scalar_subquery().label("fmea_records"),
            select(func.count(func.distinct(FmeaAssessmentMart.asset_ref))).select_from(FmeaAssessmentMart).join(
                ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == FmeaAssessmentMart.asset_ref
            ).where(
                FmeaAssessmentMart.site_code == SITE_CODE,
                FmeaAssessmentMart.organization_code == ORGANIZATION_CODE,
                FmeaAssessmentMart.asset_ref.is_not(None),
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            ).scalar_subquery().label("fmea_assets_represented"),
            select(func.count(AssetHealthAssessmentMart.canonical_id)).where(
                AssetHealthAssessmentMart.site_code == SITE_CODE,
                AssetHealthAssessmentMart.organization_code == ORGANIZATION_CODE,
            ).scalar_subquery().label("asset_health_records"),
            select(func.count(func.distinct(AssetHealthAssessmentMart.asset_ref))).select_from(AssetHealthAssessmentMart).join(
                ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == AssetHealthAssessmentMart.asset_ref
            ).where(
                AssetHealthAssessmentMart.site_code == SITE_CODE,
                AssetHealthAssessmentMart.organization_code == ORGANIZATION_CODE,
                AssetHealthAssessmentMart.asset_ref.is_not(None),
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            ).scalar_subquery().label("asset_health_assets_represented"),
            select(func.count(RcfaAnalysisMart.canonical_id)).where(
                RcfaAnalysisMart.site_code == SITE_CODE,
                RcfaAnalysisMart.organization_code == ORGANIZATION_CODE,
            ).scalar_subquery().label("rcfa_records"),
            select(func.count(OverhaulEventMart.canonical_id)).where(
                OverhaulEventMart.site_code == SITE_CODE,
                OverhaulEventMart.organization_code == ORGANIZATION_CODE,
            ).scalar_subquery().label("overhaul_records"),
        )
        registry_statement = select(func.count(ReliabilityAssetRegistryMart.asset_ref)).where(
            ReliabilityAssetRegistryMart.site_code == SITE_CODE,
            ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
        )

        with self.database.read_session() as session:
            summary = session.execute(summary_statement).one()
            trend = session.execute(trend_statement).one()
            statuses = session.execute(window_statement).all()
            work_types = session.execute(work_type_statement).all()
            concentration = session.execute(concentration_statement).all()
            records = session.execute(records_statement).one()
            registered_assets = int(session.scalar(registry_statement) or 0)

        integrity = self.integrity_summary()
        summary_values = summary._mapping
        trend_values = trend._mapping
        record_values = records._mapping
        return {
            "registered_assets": registered_assets,
            "summary": {
                "maintenance_activity_7d": int(summary_values["maintenance_7d"] or 0),
                "maintenance_activity_30d": int(summary_values["maintenance_30d"] or 0),
                "maintenance_activity_90d": int(summary_values["maintenance_90d"] or 0),
                "assets_active_7d": int(summary_values["assets_active_7d"] or 0),
                "assets_active_30d": int(summary_values["assets_active_30d"] or 0),
                "assets_active_90d": int(summary_values["assets_active_90d"] or 0),
            },
            "trend": [
                {"period_start": start, "period_end": start + timedelta(weeks=1), "event_count": int(trend_values[f"week_{index}"] or 0)}
                for index, start in enumerate(trend_starts)
            ],
            "status_distribution": [{"value": row.value, "count": int(row.count)} for row in statuses],
            "work_type_distribution": [{"value": row.value, "count": int(row.count)} for row in work_types],
            "activity_concentration": [
                {
                    "asset_ref": row.asset_ref,
                    "source_asset_number": row.source_asset_number,
                    "description": row.description,
                    "event_count": int(row.event_count),
                    "latest_activity": row.latest_activity,
                }
                for row in concentration
            ],
            "records": {key: int(record_values[key] or 0) for key in record_values.keys()},
            "integrity": integrity,
            "window_start": window_start,
            "as_of": current,
        }

    def maintenance_investigation(
        self,
        *,
        window_days: int = 90,
        min_events: int = 2,
        offset: int = 0,
        limit: int = 25,
        sort: str = "event_count_desc",
        as_of: datetime | None = None,
    ) -> dict[str, object]:
        """Return bounded Registry-scoped repeat-activity aggregates.

        Repeat activity is deliberately an event-count description.  The
        query uses SQL window functions for chronology and never loads raw
        maintenance rows into Python.
        """
        if window_days not in {30, 90, 180}:
            raise ValueError("window_days must be one of 30, 90, or 180")
        if min_events not in {2, 3, 5}:
            raise ValueError("min_events must be one of 2, 3, or 5")
        if sort not in {"event_count_desc", "latest_activity_desc", "latest_gap_asc"}:
            raise ValueError("unsupported maintenance investigation sort")

        current = as_of or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        window_start = current - timedelta(days=window_days)
        activity_date = func.coalesce(MaintenanceEventMart.actual_start, MaintenanceEventMart.source_changed_at)
        raw_work_type = _raw_work_type(MaintenanceEventMart.sources)
        canonical_work_type = func.nullif(func.trim(MaintenanceEventMart.event_type), "")
        work_type = func.coalesce(raw_work_type, canonical_work_type, "UNKNOWN")

        scoped = (
            select(
                MaintenanceEventMart.equipment_id.label("asset_ref"),
                ReliabilityAssetRegistryMart.source_asset_number.label("source_asset_number"),
                MaintenanceEventMart.canonical_id.label("event_ref"),
                activity_date.label("activity_date"),
                work_type.label("work_type"),
            )
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == MaintenanceEventMart.equipment_id)
            .where(
                MaintenanceEventMart.site_code == SITE_CODE,
                MaintenanceEventMart.organization_code == ORGANIZATION_CODE,
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
                activity_date >= window_start,
                activity_date <= current,
                activity_date.is_not(None),
            )
            .subquery()
        )
        latest_rank = func.row_number().over(
            partition_by=scoped.c.asset_ref,
            order_by=(desc(scoped.c.activity_date), desc(scoped.c.event_ref)),
        ).label("latest_rank")
        prior_activity = func.lag(scoped.c.activity_date).over(
            partition_by=scoped.c.asset_ref,
            order_by=(asc(scoped.c.activity_date), asc(scoped.c.event_ref)),
        ).label("prior_activity")
        chronology = select(scoped, latest_rank, prior_activity).subquery()

        event_count = func.count(chronology.c.event_ref).label("event_count")
        latest_activity = func.max(chronology.c.activity_date).label("latest_activity")
        previous_activity = func.max(case((chronology.c.latest_rank == 2, chronology.c.activity_date), else_=None)).label("previous_activity")
        minimum_gap = func.min(self._gap_days(chronology.c.activity_date, chronology.c.prior_activity)).label("minimum_gap_days")
        latest_work_type = func.max(case((chronology.c.latest_rank == 1, chronology.c.work_type), else_=None)).label("latest_work_type")
        aggregate = (
            select(
                chronology.c.asset_ref,
                event_count,
                latest_activity,
                previous_activity,
                minimum_gap,
                latest_work_type,
            )
            .group_by(chronology.c.asset_ref)
            .subquery()
        )

        type_count = func.count(chronology.c.event_ref).label("type_event_count")
        type_counts = select(chronology.c.asset_ref, chronology.c.work_type, type_count).group_by(chronology.c.asset_ref, chronology.c.work_type).subquery()
        type_rank = func.row_number().over(
            partition_by=type_counts.c.asset_ref,
            order_by=(desc(type_counts.c.type_event_count), asc(type_counts.c.work_type)),
        ).label("type_rank")
        dominant_type = select(type_counts, type_rank).subquery()

        asset_statement = (
            select(
                aggregate.c.asset_ref,
                ReliabilityAssetRegistryMart.source_asset_number,
                AssetMasterMart.description,
                aggregate.c.event_count,
                aggregate.c.latest_activity,
                aggregate.c.previous_activity,
                self._gap_days(aggregate.c.latest_activity, aggregate.c.previous_activity).label("latest_gap_days"),
                aggregate.c.minimum_gap_days,
                aggregate.c.latest_work_type,
                dominant_type.c.work_type.label("dominant_work_type"),
            )
            .select_from(aggregate)
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == aggregate.c.asset_ref)
            .outerjoin(AssetMasterMart, AssetMasterMart.canonical_id == aggregate.c.asset_ref)
            .outerjoin(dominant_type, (dominant_type.c.asset_ref == aggregate.c.asset_ref) & (dominant_type.c.type_rank == 1))
            .where(
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
                aggregate.c.event_count >= min_events,
            )
        )
        tie_breakers = (asc(ReliabilityAssetRegistryMart.source_asset_number), asc(aggregate.c.asset_ref))
        if sort == "latest_activity_desc":
            asset_statement = asset_statement.order_by(desc(aggregate.c.latest_activity), *tie_breakers)
        elif sort == "latest_gap_asc":
            asset_statement = asset_statement.order_by(self._gap_days(aggregate.c.latest_activity, aggregate.c.previous_activity).nulls_last(), *tie_breakers)
        else:
            asset_statement = asset_statement.order_by(desc(aggregate.c.event_count), *tie_breakers)

        summary_statement = select(
            select(func.count(ReliabilityAssetRegistryMart.asset_ref)).where(
                ReliabilityAssetRegistryMart.site_code == SITE_CODE,
                ReliabilityAssetRegistryMart.organization_code == ORGANIZATION_CODE,
            ).scalar_subquery().label("registered_assets"),
            select(func.count()).select_from(scoped).scalar_subquery().label("maintenance_events"),
            select(func.count()).select_from(aggregate).scalar_subquery().label("assets_with_activity"),
            select(func.count()).select_from(aggregate).where(aggregate.c.event_count >= 2).scalar_subquery().label("assets_with_2plus_events"),
            select(func.count()).select_from(aggregate).where(aggregate.c.event_count >= 3).scalar_subquery().label("assets_with_3plus_events"),
            select(func.coalesce(func.sum(case((aggregate.c.event_count > 1, aggregate.c.event_count - 1), else_=0)), 0)).select_from(aggregate).scalar_subquery().label("repeat_activity_events"),
        )

        with self.database.read_session() as session:
            summary = session.execute(summary_statement).one()._mapping
            total = int(session.scalar(select(func.count()).select_from(asset_statement.order_by(None).subquery())) or 0)
            rows = session.execute(asset_statement.offset(offset).limit(limit)).all()

        assets = [
            {
                "asset_ref": row.asset_ref,
                "source_asset_number": row.source_asset_number,
                "description": row.description,
                "event_count": int(row.event_count or 0),
                "repeat_activity_events": max(int(row.event_count or 0) - 1, 0),
                "latest_activity": row.latest_activity,
                "previous_activity": row.previous_activity,
                "latest_gap_days": float(row.latest_gap_days) if row.latest_gap_days is not None else None,
                "minimum_gap_days": float(row.minimum_gap_days) if row.minimum_gap_days is not None else None,
                "latest_work_type": row.latest_work_type,
                "dominant_work_type": row.dominant_work_type,
            }
            for row in rows
        ]
        return {
            "scope": {
                "site_code": SITE_CODE,
                "organization_code": ORGANIZATION_CODE,
                "registry_scope": "reliability_asset_registry",
                "date_basis": "COALESCE(actual_start, source_changed_at)",
                "interpretation": "ACTIVITY_NOT_FAILURE",
            },
            "window": {"days": window_days, "start": window_start, "as_of": current},
            "summary": {key: int(summary[key] or 0) for key in summary.keys()},
            "assets": assets,
            "meta": {"total": total, "offset": offset, "limit": limit, "has_more": offset + len(assets) < total},
            "evidence": {
                "repeat_activity": "DERIVED_SAFE",
                "work_type_source": "sources.maximo.worktype → event_type → UNKNOWN",
                "activity_date": "Activity date uses actual start when available, otherwise source change time.",
                "repeat_failure": "BUSINESS_SEMANTICS_REQUIRED",
            },
        }
