"""SQLAlchemy ORM models for the collector store."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.repositories.database import Base


class AttributeRegistryOrm(Base):
    __tablename__ = "pi_attribute_registry"

    attribute_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    site: Mapped[str | None] = mapped_column(String(20))
    unit: Mapped[str | None] = mapped_column(String(20))
    equipment: Mapped[str | None] = mapped_column(String(120))
    parameter: Mapped[str | None] = mapped_column(String(60))
    business_name: Mapped[str | None] = mapped_column(Text)
    position: Mapped[str | None] = mapped_column(String(120))
    unit_of_measure: Mapped[str | None] = mapped_column(String(40))
    web_id: Mapped[str | None] = mapped_column(Text)
    af_path: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    registered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SnapshotOrm(Base):
    __tablename__ = "pi_snapshot"

    attribute_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    value: Mapped[float | None] = mapped_column(Float)
    value_good: Mapped[bool | None] = mapped_column(Boolean)
    units: Mapped[str | None] = mapped_column(String(40))
    source_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TimeseriesOrm(Base):
    __tablename__ = "pi_timeseries"

    attribute_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    value: Mapped[float | None] = mapped_column(Float)
    value_good: Mapped[bool | None] = mapped_column(Boolean)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CollectRunOrm(Base):
    """One row per collector run (snapshot cycle, backfill, daemon cycle).

    Powers the GitHub-style activity graph: a day is 'full green' only when
    collector runs cover all 24 local hours of that day.
    """

    __tablename__ = "pi_collect_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope: Mapped[str] = mapped_column(String(80))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attributes_seen: Mapped[int] = mapped_column(Integer, default=0)
    rows_collected: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    requests_made: Mapped[int] = mapped_column(Integer, default=0)
    aborted: Mapped[bool] = mapped_column(Boolean, default=False)
    abort_reason: Mapped[str | None] = mapped_column(Text)


class BackfillProgressOrm(Base):
    """Per-(attribute_id, interval) backfill watermark for skip-downloaded.

    interval is the interpolation interval ("1m", "1h", ...) or "recorded"
    for raw backfill-recorded runs.
    """

    __tablename__ = "pi_backfill_progress"

    attribute_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    interval: Mapped[str] = mapped_column(String(20), primary_key=True)
    last_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CollectCursorOrm(Base):
    __tablename__ = "pi_collect_cursor"

    scope: Mapped[str] = mapped_column(String(80), primary_key=True)
    last_collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rows_seen: Mapped[int | None] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
