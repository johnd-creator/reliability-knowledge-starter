"""ORM models for the cockpit local store (normalized contracts).

Naming follows reliability-data-contracts (vendor-neutral, snake_case).
Raw source identifiers are kept under columns prefixed `src_*` where useful.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.repositories.database import Base


class CockpitModel(Base):
    __abstract__ = True


class EquipmentOrm(CockpitModel):
    __tablename__ = "equipment"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)  # assetnum
    name: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    location_id: Mapped[Optional[str]] = mapped_column(String(80))
    equipment_class: Mapped[Optional[str]] = mapped_column(String(40))
    unit: Mapped[Optional[str]] = mapped_column(String(40))
    status: Mapped[Optional[str]] = mapped_column(String(40))
    status_description: Mapped[Optional[str]] = mapped_column(String(80))
    is_running: Mapped[Optional[bool]] = mapped_column(Boolean)
    priority: Mapped[Optional[int]] = mapped_column(Integer)
    parent_id: Mapped[Optional[str]] = mapped_column(String(80))
    ancestor_id: Mapped[Optional[str]] = mapped_column(String(80))
    has_children: Mapped[Optional[bool]] = mapped_column(Boolean)
    failure_code: Mapped[Optional[str]] = mapped_column(String(40))
    is_safety_critical: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_calibration: Mapped[Optional[bool]] = mapped_column(Boolean)
    installed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    source_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    purchase_price: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    replacement_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    total_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    downtime_total_hours: Mapped[Optional[float]] = mapped_column(Float)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(120))
    vendor: Mapped[Optional[str]] = mapped_column(String(120))
    src_assetid: Mapped[Optional[int]] = mapped_column(Integer)
    src_siteid: Mapped[Optional[str]] = mapped_column(String(20))
    src_orgid: Mapped[Optional[str]] = mapped_column(String(20))


class WorkOrderOrm(CockpitModel):
    __tablename__ = "work_order"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)  # wonum
    equipment_id: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    location_id: Mapped[Optional[str]] = mapped_column(String(80))
    status: Mapped[Optional[str]] = mapped_column(String(40))
    status_description: Mapped[Optional[str]] = mapped_column(String(80))
    work_type: Mapped[Optional[str]] = mapped_column(String(40))
    work_class: Mapped[Optional[str]] = mapped_column(String(40))
    description: Mapped[Optional[str]] = mapped_column(Text)
    reported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    source_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scheduled_finish: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    target_completion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    estimated_duration_hours: Mapped[Optional[float]] = mapped_column(Float)
    downtime_hours: Mapped[Optional[float]] = mapped_column(Float)
    priority: Mapped[Optional[str]] = mapped_column(String(20))
    priority_description: Mapped[Optional[str]] = mapped_column(String(80))
    reported_by: Mapped[Optional[str]] = mapped_column(String(40))
    supervisor: Mapped[Optional[str]] = mapped_column(String(40))
    lead: Mapped[Optional[str]] = mapped_column(String(40))
    failure_code: Mapped[Optional[str]] = mapped_column(String(40))
    is_task: Mapped[Optional[bool]] = mapped_column(Boolean)
    parent_wo: Mapped[Optional[str]] = mapped_column(String(80))
    has_children: Mapped[Optional[bool]] = mapped_column(Boolean)
    estimated_labor_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    estimated_material_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    actual_labor_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    actual_material_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    actual_labor_hours: Mapped[Optional[float]] = mapped_column(Float)
    src_workorderid: Mapped[Optional[int]] = mapped_column(Integer)


class ServiceRequestOrm(CockpitModel):
    __tablename__ = "service_request"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)  # ticketid
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(40))
    status_description: Mapped[Optional[str]] = mapped_column(String(80))
    work_type: Mapped[Optional[str]] = mapped_column(String(40))
    equipment_id: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    location_id: Mapped[Optional[str]] = mapped_column(String(80))
    reported_by: Mapped[Optional[str]] = mapped_column(String(40))
    reported_by_name: Mapped[Optional[str]] = mapped_column(String(120))
    reported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    source_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    affected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_finish: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    target_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    target_finish: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    internal_priority: Mapped[Optional[str]] = mapped_column(String(20))
    reported_priority: Mapped[Optional[str]] = mapped_column(String(20))
    actual_labor_hours: Mapped[Optional[float]] = mapped_column(Float)
    actual_labor_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    risk_area_environment: Mapped[Optional[str]] = mapped_column(String(80))
    risk_area_process: Mapped[Optional[str]] = mapped_column(String(80))
    risk_area_human: Mapped[Optional[str]] = mapped_column(String(80))
    risk_area_reputation: Mapped[Optional[str]] = mapped_column(String(80))
    class_label: Mapped[Optional[str]] = mapped_column(String(40))
    src_ticketuid: Mapped[Optional[int]] = mapped_column(Integer)


class PersonOrm(CockpitModel):
    __tablename__ = "person"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # personid
    display_name: Mapped[Optional[str]] = mapped_column(String(160))
    first_name: Mapped[Optional[str]] = mapped_column(String(120))
    status: Mapped[Optional[str]] = mapped_column(String(40))
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    location_org: Mapped[Optional[str]] = mapped_column(String(80))


class ItemOrm(CockpitModel):
    __tablename__ = "item"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)  # itemnum
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(40))
    item_type: Mapped[Optional[str]] = mapped_column(String(40))
    lot_type: Mapped[Optional[str]] = mapped_column(String(40))
    issue_unit: Mapped[Optional[str]] = mapped_column(String(20))
    order_unit: Mapped[Optional[str]] = mapped_column(String(20))
    is_rotating: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_kit: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_crew: Mapped[Optional[bool]] = mapped_column(Boolean)
    inspection_required: Mapped[Optional[bool]] = mapped_column(Boolean)
    meter_name: Mapped[Optional[str]] = mapped_column(String(40))
    item_set_id: Mapped[Optional[str]] = mapped_column(String(40))
    status_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class LaborOrm(CockpitModel):
    __tablename__ = "labor"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # laborcode
    person_id: Mapped[Optional[str]] = mapped_column(String(40))
    status: Mapped[Optional[str]] = mapped_column(String(40))
    status_description: Mapped[Optional[str]] = mapped_column(String(80))
    work_site: Mapped[Optional[str]] = mapped_column(String(80))
    is_assigned: Mapped[Optional[bool]] = mapped_column(Boolean)
    availability_factor: Mapped[Optional[float]] = mapped_column(Float)
    reported_hours: Mapped[Optional[float]] = mapped_column(Float)
    year_to_date_other_hours: Mapped[Optional[float]] = mapped_column(Float)
    year_to_date_refused_hours: Mapped[Optional[float]] = mapped_column(Float)


class ReliabilityKpiOrm(CockpitModel):
    __tablename__ = "reliability_kpi"
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    equipment_id: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    metric: Mapped[Optional[str]] = mapped_column(String(40))
    value: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    period_end: Mapped[Optional[date]] = mapped_column(Date)
    computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    inputs_json: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("equipment_id", "metric", "period_start", "period_end", name="uq_kpi_scope"),)


class SyncCursorOrm(CockpitModel):
    __tablename__ = "sync_cursor"
    object_structure: Mapped[str] = mapped_column(String(60), primary_key=True)
    last_changedate: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rows_seen: Mapped[Optional[int]] = mapped_column(Integer)