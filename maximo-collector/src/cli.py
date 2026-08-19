#!/usr/bin/env python3
"""CLI for the Maximo collector.

Read-only against Maximo (auto-login per maximo-knowledge recipe). Commands:
  init-db         - create collector local tables
  sync [objects]  - sync operational objects (asset refresh is explicit)
  serve           - start the FastAPI app on :8002

Credentials come from the environment (.env): MAXIMO_USERNAME/MAXIMO_PASSWORD
(login mode) or MAXIMO_READ_ONLY_TOKEN (token mode).
"""

from __future__ import annotations

import argparse
import logging
import sys

from src.config import MaximoConfig, load_env
from src.repositories.database import get_database
from src.repositories.store import CollectorStore

load_env()

LOG = logging.getLogger(__name__)

AVAILABLE_OBJECTS = ["mxapiasset", "mxwodetail", "mxapisr", "mxperson", "mxitem", "mxapilabor"]
DEFAULT_OBJECTS = ["mxwodetail", "mxapisr", "mxapilabor", "mxperson", "mxitem"]


def _sync_service(store: CollectorStore):
    from src.adapters.maximo.auth import MaximoAuth
    from src.adapters.maximo.oslc_client import OslcClient
    from src.services.sync import SyncService

    config = MaximoConfig.from_environment()
    client = OslcClient(config, MaximoAuth(config))
    return SyncService(client, store, site_id=config.site_id), config


def cmd_init_db(args: argparse.Namespace) -> int:
    db = get_database()
    db.create_all()
    seeded = CollectorStore(db).seed_equipment_status_history()
    print("maximo-collector local tables created (Postgres)")
    if seeded:
        print(f"seeded {seeded} existing equipment status observations")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    from src.api.app import sync_config_for

    store = CollectorStore(get_database())
    service, config = _sync_service(store)

    selected = args.objects or DEFAULT_OBJECTS
    exit_code = 0
    for name in selected:
        try:
            cfg = sync_config_for(name)
        except KeyError:
            print(f"unknown object: {name} (available: {', '.join(AVAILABLE_OBJECTS)})")
            exit_code = 1
            continue
        try:
            stats = service.sync(cfg)
        except Exception as error:  # noqa: BLE001 — report one object failure and continue
            LOG.error("sync %s failed: %s", name, error)
            exit_code = 1
            continue
        print(
            f"{stats.mode} sync {stats.object_structure}: "
            f"{stats.rows_seen} seen, {stats.upserted} upserted, "
            f"{stats.skipped} skipped, watermark={stats.watermark}"
        )
    return exit_code


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from src.api.app import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="mxcollector", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="create collector local tables")

    sync = sub.add_parser(
        "sync",
        help="sync operational objects (asset refresh requires explicit mxapiasset)",
    )
    sync.add_argument("objects", nargs="*", help=f"any of: {', '.join(AVAILABLE_OBJECTS)} (or aliases)")

    serve = sub.add_parser("serve", help="start the FastAPI app")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8002)

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    if args.command == "init-db":
        return cmd_init_db(args)
    if args.command == "sync":
        return cmd_sync(args)
    if args.command == "serve":
        return cmd_serve(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
