"""Bounded SELECT-only contextual references from the existing canonical Mart.

No source client, acquisition trigger, source credentials or writes.
"""

from datetime import datetime
from sqlalchemy import select
from src.domain.engineering import Principal, EngineeringError
from src.domain.maintenance_context import (
    ExistingWorkOrderReference,
    MaintenanceSources,
    MaximoWorkOrderIdentity,
)
from src.repositories.mart_reader import MartQueryRepository
from src.repositories.mart_models import MaintenanceEventMart
from src.services.engineering_evidence import aware


class LocalMaintenanceIntelligence:
    def __init__(self, mart_database):
        self.database = mart_database
        self.assets = MartQueryRepository(mart_database)

    def gate(self, actor, asset):
        if not isinstance(actor, Principal) or not actor.roles:
            raise EngineeringError("AUTHENTICATION_REQUIRED", 401)
        if asset not in actor.asset_ids or self.assets.get_asset(asset) is None:
            raise EngineeringError("NOT_FOUND", 404)

    def shape(self, row):
        raw = (row.provenance or {}).get("ingested_at")
        try:
            collected = (
                aware(datetime.fromisoformat(raw.replace("Z", "+00:00")))
                if isinstance(raw, str)
                else None
            )
        except ValueError:
            collected = None
        return ExistingWorkOrderReference(
            canonical_asset_id=row.equipment_id,
            canonical_record_id=row.canonical_id,
            record_status=row.status,
            work_type=row.event_type,
            source_changed_at=aware(row.source_changed_at),
            collected_at=collected,
            projected_at=aware(row.mart_updated_at),
            sources=MaintenanceSources(
                maximo=MaximoWorkOrderIdentity(source_record_ref=row.work_order_id)
            ),
        )

    def query(self, asset):
        return select(MaintenanceEventMart).where(
            MaintenanceEventMart.equipment_id == asset,
            MaintenanceEventMart.site_code == "BSR",
            MaintenanceEventMart.organization_code == "IP",
            MaintenanceEventMart.work_order_id.is_not(None),
        )

    def work_orders(self, actor, asset, *, offset=0, limit=25):
        self.gate(actor, asset)
        if (
            type(offset) is not int
            or type(limit) is not int
            or not 0 <= offset <= 10000
            or not 1 <= limit <= 100
        ):
            raise EngineeringError("INVALID_PAGINATION", 422)
        with self.database.read_session() as s:
            rows = list(
                s.scalars(
                    self.query(asset)
                    .order_by(MaintenanceEventMart.canonical_id)
                    .offset(offset)
                    .limit(limit + 1)
                )
            )
            return {
                "items": [self.shape(row) for row in rows[:limit]],
                "offset": offset,
                "limit": limit,
                "has_more": len(rows) > limit,
            }

    def resolve_work_order(self, actor, asset, record_id):
        self.gate(actor, asset)
        with self.database.read_session() as s:
            rows = list(
                s.scalars(
                    self.query(asset)
                    .where(MaintenanceEventMart.canonical_id == record_id)
                    .limit(2)
                )
            )
            if not rows:
                raise EngineeringError("EVIDENCE_NOT_FOUND", 404)
            if len(rows) != 1:
                raise EngineeringError("EVIDENCE_AMBIGUOUS", 422)
            return self.shape(rows[0])
