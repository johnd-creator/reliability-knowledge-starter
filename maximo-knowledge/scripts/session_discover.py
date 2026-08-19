#!/usr/bin/env python3
"""Interactive, browser-session Maximo discovery.

The user completes Maximo's login form manually in a visible browser. This
process never receives or prints the credential values and never writes browser
storage state. After login, all discovery requests are GET/HEAD/OPTIONS only
and use the in-memory browser context session.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urljoin

try:
    from discover import (
        Config,
        DiscoveryError,
        OSLC_CATALOG_ROOT,
        READ_ONLY_METHODS,
        discover_oslc,
        now_utc,
        parse_payload,
        write_json,
    )
except ImportError:  # pragma: no cover - package import path
    from .discover import (
        Config,
        DiscoveryError,
        OSLC_CATALOG_ROOT,
        READ_ONLY_METHODS,
        discover_oslc,
        now_utc,
        parse_payload,
        write_json,
    )


class BrowserSessionClient:
    """Adapter exposing the same safe request interface as ReadOnlyClient."""

    def __init__(self, request_context: Any, base_url: str, timeout_ms: int, rate_limit_seconds: float):
        self.request_context = request_context
        self.base_url = base_url.rstrip("/")
        self.timeout_ms = timeout_ms
        self.rate_limit_seconds = rate_limit_seconds
        self.last_request = 0.0

    def request(self, method: str, path: str) -> tuple[int, Mapping[str, str], bytes]:
        method = method.upper()
        if method not in READ_ONLY_METHODS:
            raise DiscoveryError(f"blocked non-read-only method: {method}")
        delay = self.rate_limit_seconds - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)
        url = path if path.startswith(("http://", "https://")) else urljoin(self.base_url + "/", path.lstrip("/"))
        response = self.request_context.fetch(url, method=method, timeout=self.timeout_ms, fail_on_status_code=False)
        self.last_request = time.monotonic()
        return response.status, response.headers, response.body()


def import_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise DiscoveryError(
            "Playwright is required for browser-session discovery; install requirements.txt and run 'python -m playwright install chromium'"
        ) from error
    return sync_playwright


def login_url(config: Config) -> str:
    path = os.getenv("MAXIMO_LOGIN_PATH", "/webclient/login/login.jsp?appservauth=true")
    return urljoin(config.base_url + "/", path.lstrip("/"))


def oas_url(config: Config) -> str:
    return urljoin(config.base_url + "/", config.oas_path.lstrip("/"))


def run_session(args: argparse.Namespace) -> int:
    config = Config.from_environment()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stage_root = args.output_root / timestamp
    stage_root.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {
        "system": "maximo",
        "started_at": now_utc(),
        "scope": args.scope,
        "resources": args.resource,
        "authentication": "manual_browser_session",
        "session_persisted": False,
        "requests_allowed": sorted(READ_ONLY_METHODS),
        "status": "started",
        "errors": [],
    }

    sync_playwright = import_playwright()
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=args.headless)
        except Exception as error:  # pragma: no cover - depends on local browser install
            raise DiscoveryError(f"could not launch Chromium: {error}") from error
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(login_url(config), wait_until="domcontentloaded", timeout=int(config.timeout_seconds * 1000))
            print("Browser Maximo sudah dibuka.")
            print("Silakan login manual di browser. Credential tidak dibaca oleh CLI.")
            input("Setelah login berhasil, tekan Enter di terminal ini untuk melanjutkan... ")
            client = BrowserSessionClient(context.request, config.base_url, int(config.timeout_seconds * 1000), config.rate_limit_seconds)
            oslc_root = args.oslc_root
            probe_status, _probe_headers, probe_body = client.request("GET", oslc_root)
            report["oslc_catalog_status"] = probe_status
            try:
                parse_payload(probe_body)
                probe_ok = 200 <= probe_status < 300
            except DiscoveryError:
                probe_ok = False
            if not probe_ok:
                raise DiscoveryError(
                    f"OSLC catalog GET returned HTTP {probe_status} with non-JSON body; "
                    "session may not be authenticated"
                )
            selected = discover_oslc(client, stage_root, args.scope, args.resource, oslc_root=oslc_root)
            report["object_structure_count"] = len(selected)
            report["samples_included"] = True
            report["status"] = "completed"
        except KeyboardInterrupt:
            report["status"] = "cancelled"
            raise
        except Exception as error:
            report["status"] = "failed"
            report["errors"].append(str(error))
            raise
        finally:
            report["finished_at"] = now_utc()
            write_json(stage_root / "run-report.json", report)
            context.close()
            browser.close()
    print(f"Staging discovery tersimpan di {stage_root}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Login manual ke Maximo lalu discovery dengan session browser")
    parser.add_argument("command", choices=["run", "login", "discover"], nargs="?", default="run")
    parser.add_argument("--scope", choices=["reliability-core"], default="reliability-core")
    parser.add_argument("--resource", action="append", default=[], help="select a resource; repeatable (default: all when no scope)")
    parser.add_argument(
        "--oslc-root",
        default=OSLC_CATALOG_ROOT,
        help=f"OSLC service-provider catalog path (default: {OSLC_CATALOG_ROOT})",
    )
    parser.add_argument(
        "--verify-samples",
        action="store_true",
        help="accepted for compatibility; OSLC discovery always includes one minimal sample per object",
    )
    parser.add_argument("--headless", action="store_true", help="only use when login is supplied through an approved browser flow")
    parser.add_argument("--output-root", type=Path, default=Path("discovery/runs"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "login":
        print("Gunakan 'run' untuk mempertahankan session dan melakukan discovery dalam proses yang sama.")
        return 0
    return run_session(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DiscoveryError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
