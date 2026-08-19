"""FastAPI app: read-only contract-shaped views + sync triggers.

Consumers (the reliability cockpit) pull from these endpoints; they never
touch Maximo. Field names follow reliability-data-contracts; vendor values
stay quarantined under ``sources``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from src.adapters.maximo.mappers import (
    equipment_from_payload,
    item_from_payload,
    labor_from_payload,
    person_from_payload,
    service_request_from_payload,
    work_order_from_payload,
)
from src.config import MaximoConfig
from src.repositories import models as orm
from src.repositories.database import Database, get_database
from src.repositories.store import CollectorStore
from src.services.sync import ObjectSyncConfig, SyncService

# object_structure -> (entity_name, mapper, watermark_field, order_by, changed_column)
OBJECTS: dict[str, dict[str, Any]] = {
    # MXAPIASSET is the preferred verified asset structure. MXASSET remains
    # available for explicit backwards-compatible runs, but is not part of
    # the default list so the same equipment is not synced twice.
    "mxapiasset": dict(
        entity="equipment", mapper=equipment_from_payload,
        watermark="changedate", order_by="-changedate", changed_column="source_changed_at",
        orm=orm.EquipmentOrm, scope='siteid="BSR"', compare_column="source_changed_at",
    ),
    "mxasset": dict(
        entity="equipment", mapper=equipment_from_payload,
        watermark="changedate", order_by="-changedate", changed_column="source_changed_at",
        orm=orm.EquipmentOrm, scope='siteid="BSR"', compare_column="source_changed_at",
    ),
    "mxwodetail": dict(
        entity="work_order", mapper=work_order_from_payload,
        watermark="changedate", order_by="-changedate", changed_column="source_changed_at",
        orm=orm.WorkOrderOrm, scope='siteid="BSR"', compare_column="source_changed_at",
    ),
    "mxapisr": dict(
        entity="service_request", mapper=service_request_from_payload,
        watermark="changedate", order_by="-changedate", changed_column="source_changed_at",
        orm=orm.ServiceRequestOrm, scope='siteid="BSR"', compare_column="source_changed_at",
    ),
    "mxperson": dict(
        entity="person", mapper=person_from_payload,
        watermark="statusdate", order_by="-statusdate", changed_column="status_changed_at",
        orm=orm.PersonOrm, scope='locationorg="IP"', compare_column="status_changed_at",
    ),
    "mxitem": dict(
        entity="item", mapper=item_from_payload,
        watermark="statusdate", order_by="-statusdate", changed_column="status_changed_at",
        orm=orm.ItemOrm, scope='site="BSR"', compare_column="status_changed_at",
    ),
    "mxapilabor": dict(
        entity="labor", mapper=labor_from_payload,
        watermark=None, order_by=None, changed_column=None,
        orm=orm.LaborOrm, scope='worksite="BSR"', compare_column=None,
    ),
}
# alias: friendly names
ALIASES = {
    "equipment": "mxapiasset", "workorder": "mxwodetail", "work-orders": "mxwodetail",
    "servicerequest": "mxapisr", "person": "mxperson", "item": "mxitem", "labor": "mxapilabor",
}


def resolve_object(name: str) -> str:
    key = name.lower()
    if key in OBJECTS:
        return key
    if key in ALIASES:
        return ALIASES[key]
    raise KeyError(name)


def sync_config_for(object_structure: str) -> ObjectSyncConfig:
    canonical = resolve_object(object_structure)
    spec = OBJECTS[canonical]
    return ObjectSyncConfig(
        object_structure=canonical,
        entity_name=spec["entity"],
        mapper=spec["mapper"],
        watermark_field=spec["watermark"],
        order_by=spec["order_by"],
        scope_clause=spec["scope"],
        compare_column=spec["compare_column"],
    )


def _store(db: Database = Depends(get_database)) -> CollectorStore:
    return CollectorStore(db)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _serialize(row: Any) -> dict:
    out: dict[str, Any] = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        # The ORM keeps the database column name ``class_label`` to avoid a
        # Python keyword; the public contract calls this field ``class``.
        key = "class" if column.name == "class_label" else column.name
        out[key] = _iso(value) if isinstance(value, datetime) else value
    return out


def create_app() -> FastAPI:
    app = FastAPI(title="Maximo Collector API", version="0.1.0")

    @app.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok"}

    def _list_endpoint(orm_cls, changed_column: str | None):
        def endpoint(
            changed_since: str | None = Query(None, help="ISO-8601; only rows changed after this"),
            limit: int = Query(1000, ge=1, le=10000),
            store: CollectorStore = Depends(_store),
        ) -> list[dict]:
            since = datetime.fromisoformat(changed_since) if changed_since else None
            rows = store.list_rows(
                orm_cls, changed_column=changed_column, changed_since=since, limit=limit
            )
            return [_serialize(r) for r in rows]
        return endpoint

    app.get("/equipment", tags=["equipment"])(_list_endpoint(orm.EquipmentOrm, "source_changed_at"))

    @app.get("/equipment/{asset_id}/status-history", tags=["equipment"])
    def equipment_status_history(
        asset_id: str,
        limit: int = Query(100, ge=1, le=1000),
        store: CollectorStore = Depends(_store),
    ) -> list[dict]:
        return [_serialize(r) for r in store.list_equipment_status_history(asset_id, limit)]
    app.get("/work-orders", tags=["work-orders"])(_list_endpoint(orm.WorkOrderOrm, "source_changed_at"))
    app.get("/service-requests", tags=["service-requests"])(_list_endpoint(orm.ServiceRequestOrm, "source_changed_at"))
    app.get("/persons", tags=["persons"])(_list_endpoint(orm.PersonOrm, "status_changed_at"))
    app.get("/items", tags=["items"])(_list_endpoint(orm.ItemOrm, "status_changed_at"))
    app.get("/labor", tags=["labor"])(_list_endpoint(orm.LaborOrm, None))

    @app.get("/sync/status", tags=["sync"])
    def sync_status(store: CollectorStore = Depends(_store)) -> dict:
        return {
            obj: {
                "watermark": _iso(store.get_cursor(obj)),
                "rows": store.count(spec["orm"]),
            }
            for obj, spec in OBJECTS.items()
        }

    @app.get("/collect-runs", tags=["sync"])
    def collect_runs(
        limit: int = Query(20, ge=1, le=100),
        store: CollectorStore = Depends(_store),
    ) -> list[dict]:
        return [_serialize(r) for r in store.list_runs(limit)]

    @app.get("/stats", tags=["system"])
    def stats(store: CollectorStore = Depends(_store)) -> dict:
        last_run = store.latest_run()
        return {
            "site": "BSR",
            "org": "IP",
            "read_only": True,
            "resources": {
                spec["entity"]: store.count(spec["orm"])
                for key, spec in OBJECTS.items()
                if key != "mxasset"
            },
            "last_run": _serialize(last_run) if last_run else None,
        }

    @app.post("/sync/{name}", tags=["sync"])
    def trigger_sync(name: str, store: CollectorStore = Depends(_store)) -> dict:
        """Trigger one object's sync (login + GET-only)."""
        from src.adapters.maximo.auth import MaximoAuth
        from src.adapters.maximo.oslc_client import OslcClient

        try:
            object_structure = resolve_object(name)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown object: {name}")
        config = MaximoConfig.from_environment()
        client = OslcClient(config, MaximoAuth(config))
        service = SyncService(client, store, site_id=config.site_id)
        stats = service.sync(sync_config_for(object_structure))
        return {
            "object_structure": stats.object_structure,
            "mode": stats.mode,
            "rows_seen": stats.rows_seen,
            "upserted": stats.upserted,
            "skipped": stats.skipped,
            "watermark": _iso(stats.watermark),
        }

    return app
