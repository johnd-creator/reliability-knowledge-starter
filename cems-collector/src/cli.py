#!/usr/bin/env python3
"""CLI for the CEMS collector.

Read-only against the PLC (Modbus FC03/FC04 only). Commands:
  init-db        - create collector local tables
  load-registry  - upsert stacks + parameters from the YAML registry
  collect        - polling loop (or a single cycle with --once)
  aggregate      - aggregate the last completed 5-minute window
  diagnose       - read-only probe of every registry parameter
  serve          - start the FastAPI app on :8003

Configuration comes from the environment (.env): see .env.example.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import threading
from datetime import datetime

from src.config import CemsConfig, load_env
from src.repositories.database import get_database
from src.repositories.store import CollectorStore

load_env()

LOG = logging.getLogger(__name__)


def cmd_init_db(args: argparse.Namespace) -> int:
    get_database().create_all()
    print("cems-collector local tables created (Postgres)")
    return 0


def cmd_load_registry(args: argparse.Namespace) -> int:
    from src.services.registry import load_registry

    config = CemsConfig.from_environment()
    registry = load_registry(config)
    store = CollectorStore(get_database())
    store.upsert_stacks(registry.stacks)
    store.upsert_parameters(registry.parameters)
    print(
        f"registry loaded: {len(registry.stacks)} stacks, "
        f"{len(registry.parameters)} parameters "
        f"(default stack scope {config.stack_id!r})"
    )
    return 0


def _collect_service(store: CollectorStore, config: CemsConfig):
    from src.adapters.modbus.client import ModbusClient
    from src.services.collect import CollectService

    client = ModbusClient(config)
    return CollectService(client, store, config)


def cmd_collect(args: argparse.Namespace) -> int:
    config = CemsConfig.from_environment()
    service = _collect_service(CollectorStore(get_database()), config)

    if args.once:
        stats = service.collect_once()
        print(
            f"collect cycle: {stats.rows_seen} read, {stats.upserted} stored, "
            f"{stats.errors} read-errors, {stats.skipped} failed-transforms"
        )
        return 0 if stats.errors == 0 else 1

    stop = threading.Event()

    def _stop(signum, frame):
        LOG.info("received signal %s, shutting down", signum)
        stop.set()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    LOG.info(
        "collecting stack %s from %s:%s every %ss (Ctrl-C to stop)",
        config.stack_id, config.host, config.port, config.poll_interval_seconds,
    )
    service.run_forever(stop_flag=stop)
    return 0


def cmd_aggregate(args: argparse.Namespace) -> int:
    from src.services.aggregate import AggregationService

    config = CemsConfig.from_environment()
    service = AggregationService(CollectorStore(get_database()), config)

    def _parse(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise SystemExit(f"--{value} must be ISO-8601") from exc

    if args.start or args.end:
        if not (args.start and args.end):
            print("backfill needs both --start and --end (ISO-8601)")
            return 1
        results = service.backfill(_parse(args.start), _parse(args.end), force=True)
        total = sum(r.upserted for r in results)
        print(f"backfill: {len(results)} windows, {total} rows upserted")
        return 0

    stats = service.aggregate(force=args.force)
    if stats.skipped:
        print(f"window already aggregated (cursor={stats.watermark}) — skipped")
        return 0
    print(f"aggregated window: {stats.rows_seen} series, {stats.upserted} rows upserted")
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    """Probe every registry parameter read-only; report values + plausibility."""
    from src.adapters.modbus.client import ModbusClient
    from src.adapters.modbus.diagnostics import is_plausible_probe_value
    from src.services.registry import load_registry

    config = CemsConfig.from_environment()
    registry = load_registry(config)
    client = ModbusClient(config)

    exit_code = 0
    plausible_count = 0
    print(f"probing {len(registry.parameters)} parameters at {config.host}:{config.port} "
          f"(unit {config.unit_id}, stack {config.stack_id})")
    for spec in registry.parameters:
        try:
            result = client.read_parameter(spec.modbus)
            plausible = is_plausible_probe_value(spec.code, result.value)
            if plausible:
                plausible_count += 1
            print(
                f"{spec.code}: value={result.value:.6g} unit={spec.unit} "
                f"registers={list(result.registers)} "
                f"context={result.context} plausible={ 'yes' if plausible else 'NO' }"
            )
        except Exception as error:  # noqa: BLE001 — diagnosis continues per parameter
            exit_code = 1
            print(f"{spec.code}: error; {type(error).__name__}: {error}")
    print(f"plausible: {plausible_count}/{len(registry.parameters)}")
    if plausible_count == 0:
        exit_code = 2
    return exit_code


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from src.api.app import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="cemscollector", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="create collector local tables")

    sub.add_parser("load-registry", help="load stacks + parameters from the YAML registry")

    collect = sub.add_parser("collect", help="poll the PLC continuously (read-only)")
    collect.add_argument("--once", action="store_true", help="run a single cycle and exit")

    aggregate = sub.add_parser("aggregate", help="aggregate the last completed window")
    aggregate.add_argument("--start", help="ISO-8601 backfill start (needs --end)")
    aggregate.add_argument("--end", help="ISO-8601 backfill end (needs --start)")
    aggregate.add_argument("--force", action="store_true", help="recompute even if cursor says done")

    sub.add_parser("diagnose", help="read-only probe of every registry parameter")

    serve = sub.add_parser("serve", help="start the FastAPI app")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8003)

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    if args.command == "init-db":
        return cmd_init_db(args)
    if args.command == "load-registry":
        return cmd_load_registry(args)
    if args.command == "collect":
        return cmd_collect(args)
    if args.command == "aggregate":
        return cmd_aggregate(args)
    if args.command == "diagnose":
        return cmd_diagnose(args)
    if args.command == "serve":
        return cmd_serve(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
