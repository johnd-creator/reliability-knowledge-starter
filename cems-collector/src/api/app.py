"""FastAPI app: read-only contract-shaped views + local collect triggers.

Consumers (dashboards, the reliability cockpit) pull from these endpoints;
they never touch the PLC. Field names are vendor-neutral snake_case; Modbus
details stay quarantined under ``sources.cems``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query

from src.config import CemsConfig
from src.repositories import models as orm
from src.repositories.database import Database, get_database
from src.repositories.store import CollectorStore


def _store(db: Database = Depends(get_database)) -> CollectorStore:
    return CollectorStore(db)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _parse_optional_datetime(value: str | None, name: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{name} must be ISO-8601") from exc


def _serialize(row: Any) -> dict:
    out: dict[str, Any] = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        out[column.name] = _iso(value) if isinstance(value, datetime) else value
    return out


def create_app() -> FastAPI:
    app = FastAPI(title="CEMS Collector API", version="0.1.0")
    config = CemsConfig.from_environment()

    @app.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/stacks", tags=["registry"])
    def stacks(store: CollectorStore = Depends(_store)) -> list[dict]:
        return [_serialize(r) for r in store.list_stacks()]

    @app.get("/parameters", tags=["registry"])
    def parameters(
        stack_id: str | None = Query(None),
        store: CollectorStore = Depends(_store),
    ) -> list[dict]:
        return [_serialize(r) for r in store.list_parameters(stack_id or config.stack_id)]

    @app.get("/latest", tags=["readings"])
    def latest_readings(
        stack_id: str | None = Query(None),
        store: CollectorStore = Depends(_store),
    ) -> list[dict]:
        return [_serialize(r) for r in store.latest_readings(stack_id or config.stack_id)]

    @app.get("/readings", tags=["readings"])
    def readings(
        parameter: str | None = Query(None),
        stack_id: str | None = Query(None),
        status: str | None = Query(None, description="ok | failed"),
        since: str | None = Query(None, help="ISO-8601; observed_at >= value"),
        until: str | None = Query(None, help="ISO-8601; observed_at < value"),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=1, le=10000),
        store: CollectorStore = Depends(_store),
    ) -> list[dict]:
        rows = store.list_readings(
            parameter_code=parameter,
            stack_id=stack_id or config.stack_id,
            status=status,
            since=_parse_optional_datetime(since, "since"),
            until=_parse_optional_datetime(until, "until"),
            offset=offset,
            limit=limit,
        )
        return [_serialize(r) for r in rows]

    @app.get("/readings/5min", tags=["readings"])
    def readings_5min(
        parameter: str | None = Query(None),
        stack_id: str | None = Query(None),
        since: str | None = Query(None, help="ISO-8601; window_start >= value"),
        until: str | None = Query(None, help="ISO-8601; window_start < value"),
        offset: int = Query(0, ge=0),
        limit: int = Query(1000, ge=1, le=10000),
        store: CollectorStore = Depends(_store),
    ) -> list[dict]:
        rows = store.list_5min(
            parameter_code=parameter,
            stack_id=stack_id or config.stack_id,
            since=_parse_optional_datetime(since, "since"),
            until=_parse_optional_datetime(until, "until"),
            offset=offset,
            limit=limit,
        )
        return [_serialize(r) for r in rows]

    @app.get("/collect-runs", tags=["runs"])
    def collect_runs(
        limit: int = Query(20, ge=1, le=100),
        store: CollectorStore = Depends(_store),
    ) -> list[dict]:
        return [_serialize(r) for r in store.list_runs(limit)]

    @app.get("/stats", tags=["system"])
    def stats(store: CollectorStore = Depends(_store)) -> dict:
        last_run = store.latest_run()
        return {
            "stack_id": config.stack_id,
            "read_only": True,
            "resources": {
                "stacks": store.count(orm.StackOrm),
                "parameters": store.count(orm.ParameterOrm),
                "reading_realtime": store.count(orm.ReadingOrm),
                "reading_5min": store.count(orm.Reading5MinOrm),
            },
            "last_run": _serialize(last_run) if last_run else None,
        }

    @app.post("/collect/once", tags=["runs"])
    def trigger_collect(store: CollectorStore = Depends(_store)) -> dict:
        """Trigger one local collect cycle (read-only against the PLC)."""
        from src.adapters.modbus.client import ModbusClient
        from src.services.collect import CollectService

        client = ModbusClient(config)
        stats = CollectService(client, store, config).collect_once()
        return {
            "run_type": stats.run_type,
            "rows_seen": stats.rows_seen,
            "upserted": stats.upserted,
            "errors": stats.errors,
            "skipped": stats.skipped,
            "watermark": _iso(stats.watermark),
        }

    @app.post("/aggregate", tags=["runs"])
    def trigger_aggregate(store: CollectorStore = Depends(_store)) -> dict:
        """Trigger aggregation of the last completed window (local store only)."""
        from src.services.aggregate import AggregationService

        stats = AggregationService(store, config).aggregate()
        return {
            "run_type": stats.run_type,
            "rows_seen": stats.rows_seen,
            "upserted": stats.upserted,
            "skipped": stats.skipped,
            "watermark": _iso(stats.watermark),
        }

    return app
