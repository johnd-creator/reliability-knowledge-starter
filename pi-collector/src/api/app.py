"""FastAPI application exposing collected PI time-series data.

Designed for multiple consumers: trending dashboards, ML feature pipelines,
and the reliability cockpit. All endpoints are read-only views over the
collector store.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.repositories import get_database
from src.repositories.database import Database
from src.repositories.store import CollectorStore

LOG = logging.getLogger(__name__)


class AttributeView(BaseModel):
    attribute_id: str
    site: str | None = None
    unit: str | None = None
    equipment: str | None = None
    parameter: str | None = None
    business_name: str | None = None
    position: str | None = None
    unit_of_measure: str | None = None
    web_id: str | None = None
    af_path: str | None = None


class SnapshotView(BaseModel):
    attribute_id: str
    value: float | None = None
    value_good: bool | None = None
    units: str | None = None
    value_type: str | None = None
    value_questionable: bool | None = None
    value_substituted: bool | None = None
    value_annotated: bool | None = None
    source_timestamp: str | None = None
    collected_at: str | None = None


class TimeseriesPointView(BaseModel):
    timestamp: str
    value: float | None = None
    value_good: bool | None = None
    units: str | None = None
    value_type: str | None = None
    value_questionable: bool | None = None
    value_substituted: bool | None = None
    value_annotated: bool | None = None


class TimeseriesResponse(BaseModel):
    attribute_id: str
    points: list[TimeseriesPointView]
    count: int


class StatsView(BaseModel):
    registered_attributes: int
    total_timeseries_points: int
    snapshots_collected_today: int = 0
    last_snapshot_cursor: str | None = None
    last_backfill_cursor: str | None = None


class HeatmapDay(BaseModel):
    date: str
    count: int


class HeatmapResponse(BaseModel):
    attribute_id: str
    days: list[HeatmapDay]
    max_count: int
    total_points: int


class ActivityDay(BaseModel):
    date: str
    runs: int
    hours_covered: int  # 0-24 local hours with at least one collector run


class ActivityResponse(BaseModel):
    days: list[ActivityDay]
    target_hours_per_day: int = 24


class CollectResponse(BaseModel):
    status: str
    message: str
    stats: dict | None = None


class ScheduleView(BaseModel):
    interval_seconds: int
    state: str  # running | scheduled | idle
    last_run_at: str | None = None
    next_run_at: str | None = None
    active: bool


def _store(db: Database = Depends(get_database)) -> CollectorStore:
    return CollectorStore(db)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def create_app() -> FastAPI:
    app = FastAPI(title="PI Collector API", version="0.1.0")

    @app.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/attributes", response_model=list[AttributeView], tags=["registry"])
    def list_attributes(
        equipment: str | None = None,
        parameter: str | None = None,
        store: CollectorStore = Depends(_store),
    ) -> list[AttributeView]:
        attrs = store.list_active_attributes()
        if equipment:
            attrs = [a for a in attrs if a.equipment == equipment]
        if parameter:
            attrs = [a for a in attrs if a.parameter == parameter]
        return [
            AttributeView(
                attribute_id=a.attribute_id,
                site=a.site,
                unit=a.unit,
                equipment=a.equipment,
                parameter=a.parameter,
                business_name=a.business_name,
                position=a.position,
                unit_of_measure=a.unit_of_measure,
                web_id=a.web_id,
                af_path=a.af_path,
            )
            for a in attrs
        ]

    @app.get("/snapshots", response_model=list[SnapshotView], tags=["snapshots"])
    def list_snapshots(
        equipment: str | None = None,
        limit: int = Query(500, ge=1, le=5000),
        store: CollectorStore = Depends(_store),
    ) -> list[SnapshotView]:
        items = store.list_snapshots(equipment=equipment, limit=limit)
        return [
            SnapshotView(
                attribute_id=i.attribute_id,
                value=i.value,
                value_good=i.value_good,
                units=i.units,
                value_type=i.value_type,
                value_questionable=i.value_questionable,
                value_substituted=i.value_substituted,
                value_annotated=i.value_annotated,
                source_timestamp=_iso(i.source_timestamp),
                collected_at=_iso(i.collected_at),
            )
            for i in items
        ]

    @app.get("/snapshots/{attribute_id}", response_model=SnapshotView, tags=["snapshots"])
    def get_snapshot(attribute_id: str, store: CollectorStore = Depends(_store)) -> SnapshotView:
        snap = store.get_snapshot(attribute_id)
        if snap is None:
            raise HTTPException(status_code=404, detail="snapshot not found; run collect-snapshots")
        return SnapshotView(
            attribute_id=snap.attribute_id,
            value=snap.value,
            value_good=snap.value_good,
            units=snap.units,
            value_type=snap.value_type,
            value_questionable=snap.value_questionable,
            value_substituted=snap.value_substituted,
            value_annotated=snap.value_annotated,
            source_timestamp=_iso(snap.source_timestamp),
            collected_at=_iso(snap.collected_at),
        )

    @app.get("/timeseries/{attribute_id}", response_model=TimeseriesResponse, tags=["timeseries"])
    def get_timeseries(
        attribute_id: str,
        start: str | None = Query(None, help="ISO-8601 start timestamp"),
        end: str | None = Query(None, help="ISO-8601 end timestamp"),
        limit: int = Query(10000, ge=1, le=100000),
        store: CollectorStore = Depends(_store),
    ) -> TimeseriesResponse:
        start_dt = datetime.fromisoformat(start) if start else None
        end_dt = datetime.fromisoformat(end) if end else None
        points = store.query_timeseries(
            attribute_id, start=start_dt, end=end_dt, limit=limit
        )
        return TimeseriesResponse(
            attribute_id=attribute_id,
            points=[
                TimeseriesPointView(
                    timestamp=_iso(p.timestamp),
                    value=p.value,
                    value_good=p.value_good,
                    units=p.units,
                    value_type=p.value_type,
                    value_questionable=p.value_questionable,
                    value_substituted=p.value_substituted,
                    value_annotated=p.value_annotated,
                )
                for p in points
            ],
            count=len(points),
        )

    @app.get("/heatmap/{attribute_id}", response_model=HeatmapResponse, tags=["heatmap"])
    def get_heatmap(
        attribute_id: str,
        days: int = Query(365, ge=1, le=3650),
        store: CollectorStore = Depends(_store),
    ) -> HeatmapResponse:
        data = store.heatmap(attribute_id, days=days)
        max_count = max((d["count"] for d in data), default=0)
        total = sum(d["count"] for d in data)
        return HeatmapResponse(
            attribute_id=attribute_id,
            days=[HeatmapDay(**d) for d in data],
            max_count=max_count,
            total_points=total,
        )

    @app.get("/activity", response_model=ActivityResponse, tags=["system"])
    def collector_activity(
        days: int = Query(365, ge=1, le=3650),
        store: CollectorStore = Depends(_store),
    ) -> ActivityResponse:
        """Daily collector uptime (GitHub-style activity graph data).

        A day is "full green" when collector runs covered all 24 local hours —
        i.e. the collector ran continuously that day, not a single session.
        """
        data = store.collector_activity(days=days)
        return ActivityResponse(days=[ActivityDay(**d) for d in data])

    @app.post("/collect/snapshots", response_model=CollectResponse, tags=["collect"])
    def trigger_collect_snapshots(store: CollectorStore = Depends(_store)) -> CollectResponse:
        """Trigger a snapshot collection run (background)."""
        from src.config import PiApiConfig
        from src.adapters.pi.client import PiClient
        from src.services.collector import CollectorService

        try:
            client = PiClient(PiApiConfig.from_environment())
            service = CollectorService(client, store)
            stats = service.collect_snapshots()
            return CollectResponse(
                status="ok",
                message=f"collected {stats.rows_collected}/{stats.attributes_seen} snapshots ({stats.errors} errors)",
                stats={
                    "attributes_seen": stats.attributes_seen,
                    "rows_collected": stats.rows_collected,
                    "errors": stats.errors,
                },
            )
        except Exception as error:
            return CollectResponse(status="error", message=str(error))

    @app.post("/collect/backfill", response_model=CollectResponse, tags=["collect"])
    def trigger_backfill(
        start: str = Query(..., help='Start time, e.g. "*-7d"'),
        end: str = Query("*", help='End time, default "*" (now)'),
        interval: str = Query("1h", help="Interpolation interval"),
        skip: bool = Query(True, help="Skip ranges already downloaded (watermark)"),
        store: CollectorStore = Depends(_store),
    ) -> CollectResponse:
        """Trigger a backfill run."""
        from src.config import PiApiConfig
        from src.adapters.pi.client import PiClient
        from src.services.collector import CollectorService

        try:
            client = PiClient(PiApiConfig.from_environment())
            service = CollectorService(client, store)
            stats = service.backfill(
                start_time=start, end_time=end, interval=interval,
                skip_downloaded=skip,
            )
            return CollectResponse(
                status="ok",
                message=f"backfilled {stats.rows_collected} points ({stats.errors} errors, {stats.attributes_skipped} attributes skipped)",
                stats={
                    "attributes_seen": stats.attributes_seen,
                    "rows_collected": stats.rows_collected,
                    "errors": stats.errors,
                    "attributes_skipped": stats.attributes_skipped,
                },
            )
        except Exception as error:
            return CollectResponse(status="error", message=str(error))

    @app.get("/schedule", response_model=ScheduleView, tags=["system"])
    def schedule(store: CollectorStore = Depends(_store)) -> ScheduleView:
        """Snapshot collector schedule for the web countdown.

        States: ``running`` (a cycle is writing snapshots right now),
        ``scheduled`` (alive, next cycle at next_run_at), ``idle`` (not
        running — the UI shows a warning instead of counting down).
        """
        from datetime import datetime, timezone

        from src.config import CollectSafetyConfig
        from src.services.schedule import compute_schedule

        safety = CollectSafetyConfig.from_environment()
        last_run, duration = store.last_snapshot_cycle()
        info = compute_schedule(
            last_run,
            datetime.now(timezone.utc),
            interval_seconds=safety.snapshot_interval_seconds,
            last_cycle_duration_seconds=duration,
            latest_activity_at=store.latest_snapshot_activity(),
        )
        return ScheduleView(
            interval_seconds=info.interval_seconds,
            state=info.state,
            last_run_at=_iso(info.last_run_at),
            next_run_at=_iso(info.next_run_at),
            active=info.active,
        )

    @app.get("/stats", response_model=StatsView, tags=["system"])
    def stats(store: CollectorStore = Depends(_store)) -> StatsView:
        attrs = store.list_active_attributes()
        total_points = store.timeseries_count()
        return StatsView(
            registered_attributes=len(attrs),
            total_timeseries_points=total_points,
            snapshots_collected_today=store.snapshot_writes_today(),
            last_snapshot_cursor=_iso(store.get_cursor("snapshot")),
            last_backfill_cursor=_iso(store.last_backfill_at()),
        )

    return app
