"""Read-only ORM mappings for Reliability Mart Contract v1.

This module describes existing MX-009R tables. It is deliberately not
registered with the legacy Cockpit ``Base`` and has no ``create_all`` path in
the application.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class MartBase(DeclarativeBase):
    pass


_json = JSONB().with_variant(JSON(), "sqlite")


class AssetMasterMart(MartBase):
    __tablename__ = "asset_master"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_asset_number: Mapped[str | None] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(80))
    location_ref: Mapped[str | None] = mapped_column(String(200))
    parent_asset_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40))
    organization_code: Mapped[str | None] = mapped_column(String(40))
    asset_type: Mapped[str | None] = mapped_column(String(120))
    plant: Mapped[str | None] = mapped_column(String(120))
    unit: Mapped[str | None] = mapped_column(String(120))
    criticality: Mapped[object | None] = mapped_column(_json)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mart_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MaintenanceEventMart(MartBase):
    __tablename__ = "maintenance_event"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    id: Mapped[str] = mapped_column(String(200), nullable=False)
    equipment_id: Mapped[str] = mapped_column(String(200), nullable=False)
    work_order_id: Mapped[str | None] = mapped_column(String(200))
    event_type: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str | None] = mapped_column(String(80))
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_finish: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_hours: Mapped[float | None] = mapped_column(Float)
    labor_hours: Mapped[float | None] = mapped_column(Float)
    downtime_hours: Mapped[float | None] = mapped_column(Float)
    failure_code: Mapped[str | None] = mapped_column(String(200))
    reported_by: Mapped[str | None] = mapped_column(String(120))
    lead: Mapped[str | None] = mapped_column(String(120))
    source_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    site_code: Mapped[str | None] = mapped_column(String(40))
    organization_code: Mapped[str | None] = mapped_column(String(40))
    sources: Mapped[dict | None] = mapped_column(_json)
    provenance: Mapped[dict | None] = mapped_column(_json)
    relationship_evidence: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mart_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FmeaAssessmentMart(MartBase):
    __tablename__ = "fmea_assessment"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160))
    source_number: Mapped[str | None] = mapped_column(String(160))
    revision: Mapped[str | None] = mapped_column(String(80))
    lifecycle_status: Mapped[str | None] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text)
    asset_ref: Mapped[str | None] = mapped_column(String(200))
    failure_code_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40))
    organization_code: Mapped[str | None] = mapped_column(String(40))
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mart_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RcfaAnalysisMart(MartBase):
    __tablename__ = "rcfa_analysis"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160))
    source_number: Mapped[str | None] = mapped_column(String(160))
    revision: Mapped[str | None] = mapped_column(String(80))
    lifecycle_status: Mapped[str | None] = mapped_column(String(80))
    category: Mapped[str | None] = mapped_column(String(160))
    asset_ref: Mapped[str | None] = mapped_column(String(200))
    location_ref: Mapped[str | None] = mapped_column(String(200))
    workorder_ref: Mapped[str | None] = mapped_column(String(200))
    failure_event_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40))
    organization_code: Mapped[str | None] = mapped_column(String(40))
    source_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mart_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AssetHealthAssessmentMart(MartBase):
    __tablename__ = "asset_health_assessment"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160))
    revision: Mapped[str | None] = mapped_column(String(80))
    lifecycle_status: Mapped[str | None] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text)
    function_description: Mapped[str | None] = mapped_column(Text)
    asset_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40))
    organization_code: Mapped[str | None] = mapped_column(String(40))
    source_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mart_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OverhaulEventMart(MartBase):
    __tablename__ = "overhaul_event"

    canonical_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    contract_version: Mapped[str] = mapped_column(String(10), nullable=False)
    source_record_id: Mapped[str | None] = mapped_column(String(160))
    source_number: Mapped[str | None] = mapped_column(String(160))
    lifecycle_status: Mapped[str | None] = mapped_column(String(80))
    workorder_ref: Mapped[str | None] = mapped_column(String(200))
    asset_ref: Mapped[str | None] = mapped_column(String(200))
    site_code: Mapped[str | None] = mapped_column(String(40))
    organization_code: Mapped[str | None] = mapped_column(String(40))
    planned_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_finish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_finish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    progress: Mapped[object | None] = mapped_column(_json)
    source_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    unresolved_source_attributes: Mapped[dict | None] = mapped_column(_json)
    provenance: Mapped[dict] = mapped_column(_json, nullable=False)
    relationship_evidence: Mapped[dict] = mapped_column(_json, nullable=False)
    sources: Mapped[dict | None] = mapped_column(_json)
    mart_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mart_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ReliabilityAssetRegistryMart(MartBase):
    """Read-only mapping of the current business Asset registry projection."""

    __tablename__ = "reliability_asset_registry"

    asset_ref: Mapped[str] = mapped_column(String(200), primary_key=True)
    source_asset_number: Mapped[str] = mapped_column(String(160), nullable=False)
    site_code: Mapped[str] = mapped_column(String(40), nullable=False)
    organization_code: Mapped[str] = mapped_column(String(40), nullable=False)
    registry_source: Mapped[str] = mapped_column(String(120), nullable=False)
    snapshot_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshot_row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
