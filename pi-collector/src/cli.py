#!/usr/bin/env python3
"""CLI for the PI time-series collector.

Read-only against PI Web API. Commands:
  init-db            - create collector local tables (TimescaleDB hypertable)
  load-registry      - load verified attributes from pi-knowledge mapping YAML
  collect-snapshots  - fetch current snapshot for all active attributes
  backfill           - fetch interpolated history for a time range
  backfill-recorded  - download ALL raw recorded data (heavy, off-hours only)
  run                - continuous daemon: snapshots + delta sync on interval
  serve              - start the FastAPI app

Credentials are never stored; use PI_USERNAME/PI_PASSWORD (Basic auth) or
PI_TOKEN (Bearer) via the environment or .env.
"""

from __future__ import annotations

import argparse
import logging
import signal
import socket
import sys
import time
from datetime import datetime

from src.config import AppConfig, load_env
from src.repositories.database import get_database
from src.repositories.store import CollectorStore


class CycleTimeoutError(RuntimeError):
    """Raised when a daemon cycle exceeds its hard timeout (SIGALRM).

    A single hung syscall — DNS resolution (getaddrinfo), a dead pooled
    connection, a half-open TCP read — is NOT bounded by the requests read
    timeout. Observed 2026-08-19: one snapshot request stalled the daemon for
    2h39m. SIGALRM interrupts any blocking C call (PEP 475), so this is the
    only reliable per-cycle bound.
    """


def _on_cycle_timeout(signum: int, frame: object) -> None:
    raise CycleTimeoutError("cycle hard timeout exceeded (hung syscall?)")


def _iso_local(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_init_db(args: argparse.Namespace) -> int:
    db = get_database()
    db.create_all()
    print("pi-collector local tables created (Postgres/TimescaleDB)")
    return 0


def cmd_load_registry(args: argparse.Namespace) -> int:
    from src.services.registry import load_registry

    config = AppConfig.from_environment()
    path = args.registry or config.registry_path
    registrations = load_registry(path)
    store = CollectorStore(get_database())
    for reg in registrations:
        store.upsert_registration(reg)
    print(f"loaded {len(registrations)} verified attributes from {path}")
    if args.prune:
        pruned = store.prune_not_in([r.attribute_id for r in registrations])
        print(f"pruned {pruned} registry row(s) no longer verified upstream (deactivated)")
    sites = {r.site for r in registrations}
    for s in sorted(sites):
        count = sum(1 for r in registrations if r.site == s)
        print(f"  site {s}: {count} attributes")
    return 0


def cmd_collect_snapshots(args: argparse.Namespace) -> int:
    from src.adapters.pi.client import PiClient
    from src.config import PiApiConfig
    from src.services.collector import CollectorService

    config = PiApiConfig.from_environment()
    client = PiClient(config)
    store = CollectorStore(get_database())
    service = CollectorService(client, store)
    stats = service.collect_snapshots()
    extra = f", {len(stats.deactivated_attributes)} deactivated (PI Point gone)" if stats.deactivated_attributes else ""
    print(
        f"snapshot: {stats.rows_collected} OK, {stats.errors} errors, "
        f"{stats.attributes_seen} attributes{extra}"
    )
    return 0


def cmd_backfill(args: argparse.Namespace) -> int:
    from src.adapters.pi.client import PiClient
    from src.config import AppConfig
    from src.services.collector import CollectorService

    config = AppConfig.from_environment()
    client = PiClient(config.pi)
    store = CollectorStore(get_database())
    service = CollectorService(client, store, safety=config.safety)
    stats = service.backfill(
        start_time=args.start,
        end_time=args.end,
        interval=args.interval,
        attribute_id=args.attribute,
        skip_downloaded=not args.no_skip,
    )
    print(
        f"backfill {args.start}..{args.end} @{args.interval}: "
        f"{stats.rows_collected} points, {stats.errors} errors, "
        f"{stats.attributes_seen} attributes, {stats.attributes_skipped} skipped"
    )
    return 0


def cmd_backfill_recorded(args: argparse.Namespace) -> int:
    from src.adapters.pi.client import PiClient
    from src.config import AppConfig
    from src.services.collector import CollectorService

    config = AppConfig.from_environment()
    client = PiClient(config.pi)
    store = CollectorStore(get_database())
    service = CollectorService(client, store, safety=config.safety)
    stats = service.backfill_recorded(
        start_time=args.start,
        end_time=args.end,
        attribute_id=args.attribute,
        max_count_per_page=args.max_count,
        enforce_off_hours=not args.force,
        skip_downloaded=not args.no_skip,
    )
    if stats.aborted:
        print(f"ABORTED: {stats.abort_reason}")
        return 1
    print(stats.summary())
    if stats.requests_made >= config.safety.max_requests_per_session:
        print(f"\nNOTE: circuit breaker limit ({config.safety.max_requests_per_session} requests) reached.")
        print("Partial data is saved. Re-run the same command to resume from where it stopped.")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    from src.adapters.pi.client import PiClient
    from src.config import AppConfig
    from src.services.collector import CollectorService

    config = AppConfig.from_environment()
    client = PiClient(config.pi)
    store = CollectorStore(get_database())
    service = CollectorService(client, store, safety=config.safety)

    interval_seconds = args.interval_seconds
    mode = args.mode
    cycle_timeout = args.cycle_timeout_seconds

    # Safety net 1: bound any socket op lacking an explicit timeout (covers
    # connect phases of urllib3; DNS getaddrinfo is only covered by the alarm).
    socket.setdefaulttimeout(max(config.pi.timeout_seconds * 3, 60))
    # Safety net 2: hard wall per cycle — interrupts even hung C syscalls.
    signal.signal(signal.SIGALRM, _on_cycle_timeout)

    print(f"continuous collector: mode={mode}, interval={interval_seconds}s, "
          f"cycle-timeout={cycle_timeout}s")
    print("press Ctrl+C to stop")

    cycle = 0
    while True:
        cycle += 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n--- cycle {cycle} @ {now_str} ---", flush=True)

        signal.alarm(cycle_timeout)
        try:
            if mode == "snapshot":
                stats = service.collect_snapshots()
                print(f"  snapshot: {stats.rows_collected} OK, {stats.errors} errors")
            elif mode == "recorded-delta":
                last = store.get_cursor("recorded-delta")
                start = _iso_local(last) if last else "*-1h"
                stats = service.backfill_recorded(
                    start_time=start,
                    end_time="*",
                    enforce_off_hours=False,
                )
                store.set_cursor("recorded-delta", stats.rows_collected)
                print(f"  recorded-delta: {stats.rows_collected} points, {stats.errors} errors")
                if stats.aborted:
                    print(f"  WARNING: {stats.abort_reason}")
            elif mode == "interpolated":
                stats = service.backfill(
                    start_time=f"*-{args.lookback}",
                    end_time="*",
                    interval=args.resolution,
                )
                print(f"  interpolated: {stats.rows_collected} points, {stats.errors} errors")
        except CycleTimeoutError as error:
            print(f"  CYCLE TIMEOUT after {cycle_timeout}s: {error} — "
                  f"partial data is committed; next cycle resumes cleanly")
        except Exception as error:  # noqa: BLE001
            print(f"  ERROR: {error}")
        finally:
            signal.alarm(0)

        time.sleep(interval_seconds)


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from src.api.app import create_app

    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="picollector", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="create collector local tables")

    load = sub.add_parser("load-registry", help="load verified attributes from pi-knowledge YAML")
    load.add_argument("--registry", help="path to YAML (default: PI_REGISTRY_PATH)")
    load.add_argument("--prune", action="store_true",
                      help="deactivate registry rows no longer verified upstream (broken/removed)")
    load.set_defaults(func=cmd_load_registry)

    snap = sub.add_parser("collect-snapshots", help="fetch current snapshot for all active attributes")
    snap.set_defaults(func=cmd_collect_snapshots)

    bf = sub.add_parser("backfill", help="fetch interpolated history for a time range")
    bf.add_argument("--start", required=True, help='start time (e.g. "*-7d" or ISO-8601)')
    bf.add_argument("--end", default="*", help='end time (default: "*" = now)')
    bf.add_argument("--interval", default="1h", help="interpolation interval (default: 1h)")
    bf.add_argument("--attribute", help="limit to one attribute_id")
    bf.add_argument("--no-skip", action="store_true",
                    help="re-download already-downloaded ranges (default: skip via watermark)")
    bf.set_defaults(func=cmd_backfill)

    bfr = sub.add_parser("backfill-recorded", help="download ALL raw recorded data (heavy, off-hours only)")
    bfr.add_argument("--start", required=True, help='start time (ISO-8601 e.g. "2024-01-01T00:00:00Z")')
    bfr.add_argument("--end", default="*", help='end time (default: "*" = now)')
    bfr.add_argument("--attribute", help="limit to one attribute_id")
    bfr.add_argument("--max-count", type=int, default=5000, help="PI maxCount per page (default 5000)")
    bfr.add_argument("--force", action="store_true", help="bypass off-hours check (use with caution)")
    bfr.add_argument("--no-skip", action="store_true",
                     help="re-download already-downloaded ranges (default: skip via watermark)")
    bfr.set_defaults(func=cmd_backfill_recorded)

    run = sub.add_parser("run", help="continuous daemon: snapshots or delta sync on interval")
    run.add_argument("--mode", choices=["snapshot", "recorded-delta", "interpolated"], default="snapshot",
                     help="collection mode (default: snapshot)")
    run.add_argument("--interval-seconds", type=int, default=300, help="seconds between cycles (default 300 = 5 min)")
    run.add_argument("--cycle-timeout-seconds", type=int, default=1800,
                     help="hard wall-clock timeout per cycle (default 1800 = 30 min). "
                          "A normal snapshot cycle takes ~9 min; a hung syscall is "
                          "interrupted at this bound and the cycle is retried.")
    run.add_argument("--lookback", default="1h", help="lookback for interpolated mode (default 1h)")
    run.add_argument("--resolution", default="1m", help="resolution for interpolated mode (default 1m)")
    run.set_defaults(func=cmd_run)

    serve = sub.add_parser("serve", help="start FastAPI app")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8001)
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
