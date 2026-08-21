"""SQLAlchemy models for the NADI Reliability Mart v1.

These tables store validated canonical records, not raw Maximo responses. The
legacy collector tables remain in ``models.py`` and continue to coexist with
this persistence boundary.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, Integer, JSON, String, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.repositories.database import Base

_json = JSONB().with_variant(JSON(), "sqlite")


class MartDateTime(TypeDecorator):
    """Timezone-preserving timestamp type for PostgreSQL and SQLite tests."""

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[no-untyped-def]
        if dialect.name == "sqlite":
            return dialect.type_descriptor(String(40))
        return dialect.type_descriptor(DateTime(timezone=True))

    def process_bind_param(self, value, dialect):  # type: ignore[no-untyped-def]
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Mart timestamps must preserve timezone information")
        return value.isoformat() if dialect.name == "sqlite" else value

    def process_result_value(self, value, dialect):  # type: ignore[no-untyped-def]
        if value is None:
            return None
        if dialect.name == "sqlite" and isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AssetMasterMartOrm(Base):
    __tablename__ = "asset_master"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_asset_number: Mapped[str | None] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(80))
    location_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    parent_asset_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40), index=True)
    organization_code: Mapped[str | None] = mapped_column(String(40), index=True)
    asset_type: Mapped[str | None] = mapped_column(String(120))
    plant: Mapped[str | None] = mapped_column(String(120))
    unit: Mapped[str | None] = mapped_column(String(120), index=True)
    criticality: Mapped[object | None] = mapped_column(_json)
    source_updated_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)
    mart_updated_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)


class MaintenanceEventMartOrm(Base):
    __tablename__ = "maintenance_event"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    id: Mapped[str] = mapped_column(String(200), nullable=False)
    equipment_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    work_order_id: Mapped[str | None] = mapped_column(String(200), index=True)
    event_type: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str | None] = mapped_column(String(80), index=True)
    actual_start: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    actual_finish: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    duration_hours: Mapped[float | None] = mapped_column(Float)
    labor_hours: Mapped[float | None] = mapped_column(Float)
    downtime_hours: Mapped[float | None] = mapped_column(Float)
    failure_code: Mapped[str | None] = mapped_column(String(200))
    reported_by: Mapped[str | None] = mapped_column(String(120))
    lead: Mapped[str | None] = mapped_column(String(120))
    source_changed_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    site_code: Mapped[str | None] = mapped_column(String(40), index=True)
    organization_code: Mapped[str | None] = mapped_column(String(40), index=True)
    sources: Mapped[dict | None] = mapped_column(_json)
    provenance: Mapped[dict | None] = mapped_column(_json)
    relationship_evidence: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)
    mart_updated_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)


class FmeaAssessmentMartOrm(Base):
    __tablename__ = "fmea_assessment"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160), index=True)
    source_number: Mapped[str | None] = mapped_column(String(160), index=True)
    revision: Mapped[str | int | None] = mapped_column(String(80))
    lifecycle_status: Mapped[str | None] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    asset_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    failure_code_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40), index=True)
    organization_code: Mapped[str | None] = mapped_column(String(40), index=True)
    source_updated_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    status_changed_at: Mapped[datetime | None] = mapped_column(MartDateTime())
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)
    mart_updated_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)


class RcfaAnalysisMartOrm(Base):
    __tablename__ = "rcfa_analysis"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160), index=True)
    source_number: Mapped[str | None] = mapped_column(String(160), index=True)
    revision: Mapped[str | int | None] = mapped_column(String(80))
    lifecycle_status: Mapped[str | None] = mapped_column(String(80), index=True)
    category: Mapped[str | None] = mapped_column(String(160))
    asset_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    location_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    workorder_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    failure_event_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40), index=True)
    organization_code: Mapped[str | None] = mapped_column(String(40), index=True)
    source_created_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    requested_at: Mapped[datetime | None] = mapped_column(MartDateTime())
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)
    mart_updated_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)


class AssetHealthAssessmentMartOrm(Base):
    __tablename__ = "asset_health_assessment"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160), index=True)
    revision: Mapped[str | int | None] = mapped_column(String(80))
    lifecycle_status: Mapped[str | None] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    function_description: Mapped[str | None] = mapped_column(Text)
    asset_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    site_code: Mapped[str | None] = mapped_column(String(40), index=True)
    organization_code: Mapped[str | None] = mapped_column(String(40), index=True)
    source_created_at: Mapped[datetime | None] = mapped_column(MartDateTime())
    source_updated_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    status_changed_at: Mapped[datetime | None] = mapped_column(MartDateTime())
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)
    mart_updated_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)


class OverhaulEventMartOrm(Base):
    __tablename__ = "overhaul_event"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160), index=True)
    source_number: Mapped[str | None] = mapped_column(String(160), index=True)
    lifecycle_status: Mapped[str | None] = mapped_column(String(80), index=True)
    workorder_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    asset_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    site_code: Mapped[str | None] = mapped_column(String(40), index=True)
    organization_code: Mapped[str | None] = mapped_column(String(40), index=True)
    planned_start_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    planned_finish_at: Mapped[datetime | None] = mapped_column(MartDateTime())
    actual_start_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    actual_finish_at: Mapped[datetime | None] = mapped_column(MartDateTime())
    progress: Mapped[object | None] = mapped_column(_json)
    source_created_at: Mapped[datetime | None] = mapped_column(MartDateTime())
    source_updated_at: Mapped[datetime | None] = mapped_column(MartDateTime(), index=True)
    unresolved_source_attributes: Mapped[dict | None] = mapped_column(_json)
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)
    mart_updated_at: Mapped[datetime] = mapped_column(MartDateTime(), nullable=False, default=_utc_now)


# Explicit composite indexes make the main logical join paths obvious in the
# schema, while the single-column indexes above support entity-local filters.
Index("ix_asset_master_scope_asset", AssetMasterMartOrm.site_code, AssetMasterMartOrm.organization_code, AssetMasterMartOrm.source_asset_number)
Index("ix_maintenance_event_scope_work_order", MaintenanceEventMartOrm.site_code, MaintenanceEventMartOrm.organization_code, MaintenanceEventMartOrm.work_order_id)
