"""SQLAlchemy ORM models — contract-shaped store.

Column names are vendor-neutral snake_case. Raw Modbus configuration is
quarantined in the JSONB ``sources`` column under the ``cems`` key.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.repositories.database import Base

_json = JSONB().with_variant(JSON(), "sqlite")


class StackOrm(Base):
    __tablename__ = "stack"

    stack_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    code: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    description: Mapped[str | None] = mapped_column(Text)
    maintenance_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    maintenance_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ParameterOrm(Base):
    __tablename__ = "parameter"
    __table_args__ = (
        UniqueConstraint("code", "stack_id", name="uq_parameter_code_stack"),
    )

    code: Mapped[str] = mapped_column(String(30), primary_key=True)
    stack_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="documented")
    collect_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    threshold: Mapped[float | None] = mapped_column(Float)
    normalization_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    maintenance_override_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    o2_reference: Mapped[float | None] = mapped_column(Float)
    adjust_factor: Mapped[float] = mapped_column(Float, default=1.0)
    adjust_constant: Mapped[float] = mapped_column(Float, default=0.0)
    sources: Mapped[dict | None] = mapped_column(_json)


class ReadingOrm(Base):
    """Append-only raw + normalized time-series (port of DAZ qdb.data_realtime)."""

    __tablename__ = "reading_realtime"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parameter_code: Mapped[str] = mapped_column(String(30))
    stack_id: Mapped[str] = mapped_column(String(10))
    value_raw: Mapped[float | None] = mapped_column(Float)
    value_normalized: Mapped[float | None] = mapped_column(Float)
    value_correction: Mapped[float | None] = mapped_column(Float)
    value_final: Mapped[float | None] = mapped_column(Float)
    transformation_status: Mapped[str] = mapped_column(String(20), default="ok")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Reading5MinOrm(Base):
    """5-minute aggregates (port of DAZ sensor_data / qdb.data_5min)."""

    __tablename__ = "reading_5min"
    __table_args__ = (
        UniqueConstraint("parameter_code", "stack_id", "window_start", name="uq_reading_5min_window"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parameter_code: Mapped[str] = mapped_column(String(30))
    stack_id: Mapped[str] = mapped_column(String(10))
    avg_value: Mapped[float] = mapped_column(Float, default=0.0)
    min_value: Mapped[float] = mapped_column(Float, default=0.0)
    max_value: Mapped[float] = mapped_column(Float, default=0.0)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SyncCursorOrm(Base):
    __tablename__ = "sync_cursor"

    scope: Mapped[str] = mapped_column(String(80), primary_key=True)
    watermark: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rows_seen: Mapped[int | None] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CollectRunOrm(Base):
    """One row per collect/aggregate run — observability."""

    __tablename__ = "collect_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_type: Mapped[str] = mapped_column(String(20))  # "collect" | "aggregate"
    mode: Mapped[str] = mapped_column(String(20), default="full")
    rows_seen: Mapped[int] = mapped_column(Integer, default=0)
    upserted: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    watermark: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
