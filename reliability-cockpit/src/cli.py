#!/usr/bin/env python3
"""CLI for the Reliability Cockpit.

The Cockpit reads only from local collector APIs. Commands:
  init-db         - create cockpit local tables
  sync [objects]  - delta-sync contract-shaped Maximo collector objects
  kpi             - compute + persist reliability KPIs from synced work orders
  run             - continuously sync the collector and refresh KPIs
  serve           - start the FastAPI app
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import threading
from datetime import date, timedelta

from src.config import CollectorConfig, load_env
from src.repositories.database import get_database
from src.repositories.store import CockpitStore
from src.services.kpi import KpiPeriod, KpiService
from src.services.sync import SyncService

LOG = logging.getLogger(__name__)

AVAILABLE_SOURCES = {
    "mxasset": ("mxasset", "equipment"),
    "mxwodetail": ("mxwodetail", "workorder"),
    "mxapisr": ("mxapisr", "servicerequest"),
    "mxperson": ("mxperson", "person"),
    "mxitem": ("mxitem", "item"),
    "mxapilabor": ("mxapilabor", "labor"),
}


def cmd_init_db(args: argparse.Namespace) -> int:
    db = get_database()
    db.create_all()
    print("cockpit local tables created (Postgres)")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    from src.adapters.collector_client import CollectorClient

    config = CollectorConfig.from_environment()
    client = CollectorClient(config.maximo_api_base, timeout_seconds=config.timeout_seconds)
    store = CockpitStore(get_database())
    service = SyncService(client, store)

    selected = args.objects or [name for name, _ in AVAILABLE_SOURCES.values()]
    results = []
    for object_structure, resource in AVAILABLE_SOURCES.values():
        if object_structure not in selected and resource not in selected:
            continue
        results.append(service.sync(resource))
    for stats in results:
        print(
            f"{stats.resource:<14} mode={stats.mode:<11} seen={stats.rows_seen:<6} "
            f"upserted={stats.upserted}"
        )
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run Cockpit-only refresh loops without reaching any source system."""
    stop = threading.Event()

    def _stop(signum, frame):
        LOG.info("received signal %s, stopping Cockpit worker", signum)
        stop.set()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    LOG.info("starting Cockpit refresh worker every %ss", args.interval_seconds)
    while not stop.is_set():
        try:
            sync_exit = cmd_sync(argparse.Namespace(objects=[]))
            if sync_exit == 0:
                cmd_kpi(argparse.Namespace(equipment=None, period_end=None, period_start=None))
            else:
                LOG.warning("collector sync failed; KPI refresh skipped for this cycle")
        except Exception as error:  # noqa: BLE001 - worker must survive a transient collector outage
            LOG.exception("Cockpit refresh cycle failed: %s", error)
        stop.wait(args.interval_seconds)
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

    run = sub.add_parser("run", help="continuously sync collector data and refresh KPIs")
    run.add_argument("--interval-seconds", type=int, default=300)
    run.set_defaults(func=cmd_run)

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
