#!/usr/bin/env python3
"""CLI for the reliability cockpit sidecar.

Read-only against Maximo. Commands:
  init-db         - create cockpit local tables
  sync [objects]  - delta-sync verified Maximo objects into the cockpit store
  kpi             - compute + persist reliability KPIs from synced work orders
  serve           - start the FastAPI app

Credentials are never stored; use MAXIMO_READ_ONLY_TOKEN or an out-of-band
session cookie (MAXIMO_SESSION_COOKIE).
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, timedelta

from src.config import MaximoConfig, load_env
from src.repositories.database import get_database
from src.repositories.store import CockpitStore
from src.services.kpi import KpiPeriod, KpiService
from src.services.sync import ObjectSyncConfig, SyncService

LOG = logging.getLogger(__name__)

AVAILABLE_SOURCES = {
    "mxasset": ("mxasset", "equipment"),
    "mxwodetail": ("mxwodetail", "workorder"),
    "mxapisr": ("mxapisr", "servicerequest"),
    "mxperson": ("mxperson", "person"),
    "mxitem": ("mxitem", "item"),
    "mxapilabor": ("mxapilabor", "labor"),
}


def _mapper_for(resource: str):
    from src.adapters.maximo import (
        equipment_from_payload,
        item_from_payload,
        labor_from_payload,
        person_from_payload,
        service_request_from_payload,
        work_order_from_payload,
    )

    return {
        "equipment": equipment_from_payload,
        "workorder": work_order_from_payload,
        "servicerequest": service_request_from_payload,
        "person": person_from_payload,
        "item": item_from_payload,
        "labor": labor_from_payload,
    }[resource]


def cmd_init_db(args: argparse.Namespace) -> int:
    db = get_database()
    db.create_all()
    print("cockpit local tables created (Postgres)")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    from src.adapters.maximo import OslcClient

    config = MaximoConfig.from_environment()
    client = OslcClient(config)
    store = CockpitStore(get_database())
    service = SyncService(client, store, site_id=config.site_id)

    selected = args.objects or [name for name, _ in AVAILABLE_SOURCES.values()]
    results = []
    for object_structure, resource in AVAILABLE_SOURCES.values():
        if object_structure not in selected and resource not in selected:
            continue
        results.append(service.sync(ObjectSyncConfig(object_structure=object_structure, mapper=_mapper_for(resource))))
    for stats in results:
        print(
            f"{stats.object_structure:<14} mode={stats.mode:<11} seen={stats.rows_seen:<6} "
            f"upserted={stats.upserted}"
        )
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from src.api.app import create_app

    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


def cmd_kpi(args: argparse.Namespace) -> int:
    store = CockpitStore(get_database())
    service = KpiService(store)
    period_end: date = args.period_end or date.today()
    period_start: date = args.period_start or (period_end - timedelta(days=89))
    period = KpiPeriod(start=period_start, end=period_end)
    kpis = service.compute_all(period, equipment_id=args.equipment)
    by_metric: dict[str, int] = {}
    for kpi in kpis:
        by_metric[kpi.metric] = by_metric.get(kpi.metric, 0) + 1
    print(f"KPI period {period.start} .. {period.end}: {len(kpis)} computed & persisted")
    for metric, count in sorted(by_metric.items()):
        print(f"  {metric:<16} {count}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cockpit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="create cockpit local tables")

    sync = sub.add_parser("sync", help="delta-sync verified Maximo objects")
    sync.add_argument("objects", nargs="*", help="object structure(s) or resource name(s); default all")
    sync.set_defaults(func=cmd_sync)

    kpi = sub.add_parser("kpi", help="compute + persist reliability KPIs from synced work orders")
    kpi.add_argument("--equipment", help="limit to one equipment id; default: all equipment")
    kpi.add_argument(
        "--from",
        dest="period_start",
        type=date.fromisoformat,
        help="period start YYYY-MM-DD (default: 90 days before --to)",
    )
    kpi.add_argument(
        "--to",
        dest="period_end",
        type=date.fromisoformat,
        help="period end YYYY-MM-DD (default: today)",
    )
    kpi.set_defaults(func=cmd_kpi)

    serve = sub.add_parser("serve", help="start FastAPI app")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.set_defaults(func=cmd_serve)

    parser.set_defaults(func=cmd_init_db)
    parser.set_defaults(command="init-db")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    load_env()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - CLI top-level error output
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)