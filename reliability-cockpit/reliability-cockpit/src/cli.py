"""CLI for the reliability-cockpit sidecar.

Data source: maximo-collector API (:8002), not a direct Maximo connection.
The cockpit is a pure dashboard — it reads contract-shaped data from the
collector's local Postgres store.
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import uvicorn
from dateutil import parser as date_parser

from src.adapters.collector_client import CollectorClient, CollectorClientError
from src.repositories.database import get_database, Database
from src.repositories.store import CockpitStore
from src.services.kpi import compute_all as kpi_compute_all
from src.services.kpi import KpiPeriod
from src.services.kpi import KpiService
from src.services.sync import SyncStats, SyncService

LOG = logging.getLogger(__name__)


def cmd_init_db(args: argparse.Namespace) -> int:
    Database(get_database()).create_all()
    LOG.info("cockpit tables created")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    db = get_database()
    store = CockpitStore(db)
    client = CollectorClient()
    service = SyncService(client, store)

    object_names = args.objects or [
        "equipment", "workorder", "servicerequest", "person", "item", "labor",
    ]

    for resource in object_names:
        try:
            stats = service.sync(resource)
        except CollectorClientError as error:
            LOG.error("sync %s failed: %s", resource, error)
        else:
            LOG.info("%s: %d rows seen, %d upserted, %d skipped, watermark %s",
                     resource, stats.rows_seen, stats.upserted, stats.skipped, stats.watermark)

    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from src.api.app import create_app

    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


def cmd_kpi(args: argparse.Namespace) -> int:
    store = CockpitStore(get_database())
    service = KpiService(store)
    period_end: datetime = args.period_end or datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    period_start: datetime = args.period_start or (period_end - timedelta(days=89))
    period = KpiPeriod(start=period_start, end=period_end)
    kpis = kpi_compute_all(period, equipment_id=args.equipment)
    by_metric: dict[str, int] = {}
    for kpi in kpis:
        by_metric[kpi.metric] = by_metric.get(kpi.metric, 0) + 1
    print(f"KPI period {period.start.date()} .. {period.end.date()}: {len(kpis)} computed & persisted")
    for metric, count in sorted(by_metric.items()):
        print(f"  {metric:<16} {count}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cockpit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="create cockpit local tables")

    sync = sub.add_parser("sync", help="delta-sync data from maximo-collector API")
    sync.add_argument("objects", nargs="*", help="resource name(s) (equipment|workorder|servicerequest|person|item|labor); default all")
    sync.set_defaults(func=cmd_sync)

    kpi = sub.add_parser("kpi", help="compute + persist reliability KPIs from synced work orders")
    kpi.add_argument("--equipment", help="limit to one equipment id; default: all equipment")
    kpi.add_argument(
        "--from",
        dest="period_start",
        type=lambda s: date_parser.isoparse(s).datetime() if hasattr(date_parser.isoparse(s), 'datetime') else None,
        help="period start ISO date; default: 90 days before --to",
    )
    kpi.add_argument(
        "--to",
        dest="period_end",
        type=lambda s: date_parser.isoparse(s).datetime() if hasattr(date_parser.isoparse(s), 'datetime') else None,
        help="period end ISO date; default: today midnight",
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
    from src.config import load_env, AppConfig

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
