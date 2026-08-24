"""Read-only ORM mappings for Reliability Mart Contract v1.

This module describes existing MX-009R tables. It is deliberately not
registered with the legacy Cockpit ``Base`` and has no ``create_all`` path in
the application.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, text
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


class AssetAfMappingMart(MartBase):
    """NADI-owned, governed Maximo Asset to PI AF identity relation."""

    __tablename__ = "asset_af_mapping"
    __table_args__ = (
        CheckConstraint(
            "mapping_status IN ('PROPOSED', 'VERIFIED', 'RETIRED')",
            name="ck_asset_af_mapping_status",
        ),
        CheckConstraint(
            "mapping_role = 'PRIMARY_EQUIPMENT'",
            name="ck_asset_af_mapping_role",
        ),
        CheckConstraint(
            "evidence_method IN ('NATIVE_IDENTIFIER', 'GOVERNED_LOOKUP', 'MANUAL_VERIFICATION', 'MIGRATED_VERIFIED')",
            name="ck_asset_af_mapping_evidence",
        ),
        CheckConstraint(
            "mapping_status <> 'VERIFIED' OR ("
            "verified_at IS NOT NULL AND "
            "NULLIF(trim(coalesce(verified_by, '')), '') IS NOT NULL AND "
            "(NULLIF(trim(coalesce(verification_note, '')), '') IS NOT NULL OR "
            "NULLIF(trim(coalesce(evidence_ref, '')), '') IS NOT NULL)"
            ")",
            name="ck_asset_af_mapping_verified_provenance",
        ),
        CheckConstraint(
            "mapping_status <> 'PROPOSED' OR (verified_at IS NULL AND verified_by IS NULL)",
            name="ck_asset_af_mapping_proposed_provenance",
        ),
        CheckConstraint(
            "mapping_status <> 'RETIRED' OR ("
            "retired_at IS NOT NULL AND "
            "NULLIF(trim(coalesce(retired_by, '')), '') IS NOT NULL AND "
            "NULLIF(trim(coalesce(retirement_note, '')), '') IS NOT NULL"
            ")",
            name="ck_asset_af_mapping_retired_provenance",
        ),
        Index(
            "uq_asset_af_mapping_active_exact",
            "canonical_asset_id",
            "af_element_ref",
            "mapping_role",
            unique=True,
            postgresql_where=text("mapping_status IN ('PROPOSED', 'VERIFIED')"),
            sqlite_where=text("mapping_status IN ('PROPOSED', 'VERIFIED')"),
        ),
        Index("ix_asset_af_mapping_asset_status", "canonical_asset_id", "mapping_status"),
        Index("ix_asset_af_mapping_af_element", "af_element_ref"),
    )

    id: Mapped[str] = mapped_column(String(200), primary_key=True)
    canonical_asset_id: Mapped[str] = mapped_column(
        String(200),
        ForeignKey("asset_master.canonical_id", ondelete="RESTRICT"),
        nullable=False,
    )
    pi_source_id: Mapped[str] = mapped_column(String(80), nullable=False)
    af_server_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    af_database_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    af_element_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    mapping_role: Mapped[str] = mapped_column(String(40), nullable=False)
    mapping_status: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence_method: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[str | None] = mapped_column(String(160))
    verification_note: Mapped[str | None] = mapped_column(Text)
    evidence_ref: Mapped[str | None] = mapped_column(String(500))
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retired_by: Mapped[str | None] = mapped_column(String(160))
    retirement_note: Mapped[str | None] = mapped_column(Text)
    source_assetnum_snapshot: Mapped[str | None] = mapped_column(String(160))
    source_siteid_snapshot: Mapped[str | None] = mapped_column(String(40))
    source_orgid_snapshot: Mapped[str | None] = mapped_column(String(40))
    af_path_snapshot: Mapped[str | None] = mapped_column(String(500))
    af_element_name_snapshot: Mapped[str | None] = mapped_column(String(240))
