#!/usr/bin/env python3
"""Read-only PI Web API discovery CLI.

Mirrors the maximo-knowledge discovery safety model:
  * GET / HEAD / OPTIONS only — anything else raises DiscoveryError.
  * Network access requires an explicit --execute flag.
  * Credentials are never stored or logged; read-only credentials (Basic auth
    via PI_USERNAME/PI_PASSWORD, or Bearer via PI_TOKEN) are supplied via env.
  * All saved samples are sanitized.
  * Every record carries a status: unknown | documented | verified | forbidden.

Offline mode emits the *documented* PI Web API endpoint catalog:

    python scripts/discover_pi.py --documented

With authorized access and explicit --execute, walk the hierarchy:

    python scripts/discover_pi.py --probe-system --execute
    python scripts/discover_pi.py --list-dataservers --execute
    python scripts/discover_pi.py --list-points --server <name> [--name-filter F] --execute
    python scripts/discover_pi.py --point --path "\\\\server\\tag" --execute
    python scripts/discover_pi.py --stream-value --webid <id> --execute
    python scripts/discover_pi.py --stream-recorded --webid <id> --start ... --end ... --execute
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

READ_ONLY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class DiscoveryError(RuntimeError):
    """Raised for non-read-only requests, transport failures, or bad payloads."""


# --------------------------------------------------------------------------- env
def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


@dataclass(frozen=True)
class Config:
    base_url: str
    timeout_seconds: int = 30
    rate_limit_seconds: float = 1.0
    max_response_bytes: int = 1_048_576
    verify_tls: bool = True
    username: str | None = None
    password: str | None = None
    token: str | None = None

    @classmethod
    def from_environment(cls) -> "Config":
        return cls(
            base_url=os.getenv("PI_WEB_API_BASE_URL", "https://piwebapi.example.internal/piwebapi").rstrip("/"),
            timeout_seconds=int(os.getenv("PI_TIMEOUT_SECONDS", "30")),
            rate_limit_seconds=float(os.getenv("PI_RATE_LIMIT_SECONDS", "1.0")),
            max_response_bytes=int(os.getenv("PI_MAX_RESPONSE_BYTES", str(1_048_576))),
            verify_tls=os.getenv("PI_VERIFY_TLS", "1") == "1",
            username=os.getenv("PI_USERNAME") or None,
            password=os.getenv("PI_PASSWORD") or None,
            token=os.getenv("PI_TOKEN") or None,
        )

    def auth_kwargs(self) -> dict[str, Any]:
        """Resolve request auth from credentials without ever logging them."""
        if self.username and self.password is not None:
            return {"auth": (self.username, self.password)}
        if self.token:
            return {"headers": {"Authorization": f"Bearer {self.token}"}}
        return {}


# ------------------------------------------------------------------------- utils
def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sanitize(value: Any) -> Any:
    """Strip values that must never be persisted (credentials / auth artifacts)."""
    forbidden = {"accesstoken", "token", "authorization", "set-cookie", "cookie", "password"}
    if isinstance(value, dict):
        return {k: sanitize(v) for k, v in value.items() if k.lower() not in forbidden}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    return value


# ---------------------------------------------------------- documented endpoints
# The PI Web API surface below is documented public OSIsoft behavior. It is
# NOT instance-verified; status stays "documented" until an authorized probe
# confirms it on this organization's PI server.
DOCUMENTED_ENDPOINTS: list[dict[str, Any]] = [
    {
        "system": "pi",
        "resource": "system",
        "endpoint": "/",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "PI Web API root: links to top-level collections (dataservers, assetdatabases, ...).",
        "parameters": [],
        "important_fields": ["Links"],
        "relationships": ["dataservers", "assetdatabases"],
        "use_cases": ["reachability-check", "link-discovery"],
        "notes": ["Use as the first reachability probe in --probe-system."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "dataservers",
        "endpoint": "/dataservers",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "List PI Data Archive servers known to the Web API.",
        "parameters": [{"name": "search", "required": False}],
        "important_fields": ["Name", "WebId", "ServerVersion", "IsConnected", "Links"],
        "relationships": ["points"],
        "use_cases": ["server-inventory"],
        "notes": ["Server WebId feeds /dataservers/{webId}/points."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "points",
        "endpoint": "/dataservers/{webId}/points",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "List PI Points on a data server (paginated by MaxCount).",
        "parameters": [
            {"name": "webId", "required": True, "in": "path"},
            {"name": "nameFilter", "required": False},
            {"name": "maxCount", "required": False},
            {"name": "startIndex", "required": False},
        ],
        "important_fields": ["Name", "WebId", "PointType", "Units", "Descriptor", "Links"],
        "relationships": ["streams"],
        "use_cases": ["point-catalog", "tag-mapping"],
        "notes": [
            "Do NOT brute-force WebIds or tag names (AGENTS rule 4).",
            "Record Units and PointType whenever a point is discovered (AGENTS rule 9).",
        ],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "point-by-path",
        "endpoint": "/points",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "Resolve a single point by its canonical path (\\\\server\\tag).",
        "parameters": [{"name": "path", "required": True}],
        "important_fields": ["Name", "WebId", "Units", "PointType"],
        "relationships": ["streams"],
        "use_cases": ["tag-lookup"],
        "notes": ["Use only for tags whose names are already authorized/known."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "stream-value",
        "endpoint": "/streams/{webId}/value",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "Current (snapshot) value of a stream.",
        "parameters": [{"name": "webId", "required": True, "in": "path"}],
        "important_fields": ["Value", "Units", "Timestamp", "Good", "IsSubstituted"],
        "relationships": ["points"],
        "use_cases": ["live-indicator", "running-status"],
        "notes": ["Snapshot only; not history. Record Units + data type."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "stream-recorded",
        "endpoint": "/streams/{webId}/recorded",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "Recorded (raw archive) values for a stream within a time range.",
        "parameters": [
            {"name": "webId", "required": True, "in": "path"},
            {"name": "startTime", "required": False},
            {"name": "endTime", "required": False},
            {"name": "maxCount", "required": False},
        ],
        "important_fields": ["Items[].Value", "Items[].Timestamp", "Items[].Good"],
        "relationships": ["points"],
        "use_cases": ["history", "trend-analysis"],
        "notes": ["Prefer bounded time ranges to respect rate limits."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "stream-interpolated",
        "endpoint": "/streams/{webId}/interpolated",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "Interpolated values at regular intervals for a stream.",
        "parameters": [
            {"name": "webId", "required": True, "in": "path"},
            {"name": "startTime", "required": False},
            {"name": "endTime", "required": False},
            {"name": "interval", "required": False},
        ],
        "important_fields": ["Items[].Value", "Items[].Timestamp"],
        "relationships": ["points"],
        "use_cases": ["aligned-history", "kpi-window"],
        "notes": ["Useful for fixed-window reliability KPIs."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "assetdatabases",
        "endpoint": "/assetdatabases",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "List AF (Asset Framework) databases.",
        "parameters": [],
        "important_fields": ["Name", "WebId", "Links"],
        "relationships": ["elements"],
        "use_cases": ["af-navigation"],
        "notes": ["Entry point for AF element/attribute hierarchy."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "elements",
        "endpoint": "/elements/{webId}/elements",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "Child elements of an AF element (hierarchy navigation).",
        "parameters": [{"name": "webId", "required": True, "in": "path"}],
        "important_fields": ["Name", "WebId", "Links"],
        "relationships": ["attributes", "elements"],
        "use_cases": ["asset-hierarchy"],
        "notes": ["Walk to map AF elements to Maximo assets."],
        "verified_at": None,
    },
    {
        "system": "pi",
        "resource": "attributes",
        "endpoint": "/elements/{webId}/attributes",
        "method": "GET",
        "status": "documented",
        "access": "unknown",
        "description": "Attributes of an AF element (measurements / properties).",
        "parameters": [{"name": "webId", "required": True, "in": "path"}],
        "important_fields": ["Name", "WebId", "Type", "DefaultUnitsName", "Links"],
        "relationships": ["streams"],
        "use_cases": ["condition-monitoring", "bearing-temp", "vibration", "mw"],
        "notes": ["Record Type + DefaultUnitsName with every attribute (AGENTS rule 9)."],
        "verified_at": None,
    },
]


# --------------------------------------------------------------------- requests
def _request(method: str, url: str, config: Config, *, auth_headers: dict | None) -> tuple[int, bytes]:
    """Read-only HTTP request with rate limiting and size cap. No credential logging."""
    method = method.upper()
    if method not in READ_ONLY_METHODS:
        raise DiscoveryError(f"blocked non-read-only method for PI: {method}")
    import requests  # imported lazily so offline mode needs no network deps

    time.sleep(config.rate_limit_seconds)
    extra: dict[str, Any] = {"headers": auth_headers} if auth_headers else config.auth_kwargs()
    resp = requests.request(
        method, url, timeout=config.timeout_seconds, verify=config.verify_tls, **extra
    )
    if len(resp.content) > config.max_response_bytes:
        raise DiscoveryError(
            f"PI {method} {url} returned oversized body ({len(resp.content)} > {config.max_response_bytes} bytes)"
        )
    return resp.status_code, resp.content


def _get_json(path_or_url: str, config: Config) -> tuple[int, Any]:
    """GET a PI endpoint, return (status_code, parsed-json-or-raw-text)."""
    url = path_or_url if path_or_url.startswith(("http://", "https://")) else config.base_url + path_or_url
    status, body = _request("GET", url, config, auth_headers=None)
    try:
        return status, sanitize(json.loads(body.decode("utf-8")))
    except (ValueError, UnicodeDecodeError):
        return status, body.decode("utf-8", errors="replace")


# --------------------------------------------------------------------- commands
def cmd_documented(args: argparse.Namespace, repo_root: Path) -> int:
    catalog = {
        "system": "pi",
        "source": "documented (public OSIsoft PI Web API surface)",
        "instance_verified": False,
        "generated_at": now_utc(),
        "resources": DOCUMENTED_ENDPOINTS,
        "instructions": (
            "All entries are status=documented. After an authorized --execute probe, "
            "flip matching entries to verified (or forbidden) and fill verified_at."
        ),
    }
    write_json(repo_root / "discovery" / "endpoints.json", catalog)
    print(f"wrote {len(DOCUMENTED_ENDPOINTS)} documented PI Web API endpoints -> discovery/endpoints.json")
    print("All status=documented (not instance-verified). Run --probe-system --execute when access is authorized.")
    return 0


def _stage_dir(repo_root: Path) -> Path:
    stage = repo_root / "discovery" / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stage.mkdir(parents=True, exist_ok=True)
    return stage


def cmd_probe_system(args: argparse.Namespace, repo_root: Path) -> int:
    if not args.execute:
        print("--probe-system requires --execute (network access is opt-in). Nothing done.")
        return 1
    config = Config.from_environment()
    url = config.base_url + "/"
    status, body = _request("GET", url, config, auth_headers=None)
    auth_mode = "basic" if config.username else ("bearer" if config.token else "anonymous")
    record = {
        "system": "pi",
        "resource": "system",
        "endpoint": "/",
        "method": "GET",
        "status": "verified" if 200 <= status < 300 else "forbidden",
        "access": f"http_{status}",
        "verified_at": now_utc(),
        "base_url": config.base_url,
        "auth_mode": auth_mode,
        "notes": [],
    }
    if 200 <= status < 300:
        try:
            payload = sanitize(json.loads(body.decode("utf-8")))
            record["sample"] = payload
            record["links"] = sorted((payload.get("Links") or {}).keys()) if isinstance(payload, dict) else []
        except (ValueError, UnicodeDecodeError):
            record["notes"].append("non-JSON 2xx body; not parsed")
    else:
        record["notes"].append(f"non-2xx; auth_mode={auth_mode}")
    report = {"started_at": now_utc(), "scope": "system", "requests_allowed": sorted(READ_ONLY_METHODS), "results": [record]}
    write_json(_stage_dir(repo_root) / "run-report.json", report)
    print(f"PI system probe HTTP {status} -> status={record['status']} (auth={auth_mode})")
    return 0


def cmd_list_dataservers(args: argparse.Namespace, repo_root: Path) -> int:
    if not args.execute:
        print("--list-dataservers requires --execute (network access is opt-in). Nothing done.")
        return 1
    config = Config.from_environment()
    status, payload = _get_json("/dataservers", config)
    servers: list[dict[str, Any]] = []
    if status == 200 and isinstance(payload, dict):
        for item in payload.get("Items", []) or []:
            servers.append({
                "name": item.get("Name"),
                "web_id": item.get("WebId"),
                "server_version": item.get("ServerVersion"),
                "is_connected": item.get("IsConnected"),
                "path": item.get("Path"),
                "status": "verified",
                "verified_at": now_utc(),
            })
    result = {
        "system": "pi",
        "endpoint": "/dataservers",
        "access": f"http_{status}",
        "status": "verified" if servers else ("forbidden" if status in (401, 403) else "unknown"),
        "verified_at": now_utc(),
        "data_servers": servers,
        "count": len(servers),
    }
    write_json(repo_root / "discovery" / "dataservers.json", result)
    print(f"/dataservers HTTP {status}: {len(servers)} data server(s)")
    for s in servers:
        print(f"  - {s['name']}  connected={s['is_connected']}  web_id={_short(s['web_id'])}")
    return 0


def _short(value: Any, n: int = 12) -> str:
    if value is None:
        return "(none)"
    s = str(value)
    return s if len(s) <= n else s[:n] + "..."


def cmd_list_points(args: argparse.Namespace, repo_root: Path) -> int:
    if not args.execute:
        print("--list-points requires --execute (network access is opt-in). Nothing done.")
        return 1
    config = Config.from_environment()
    server_id = _resolve_server(args.server, config, repo_root)
    params: dict[str, Any] = {"maxCount": str(args.max_count)}
    if args.name_filter:
        params["nameFilter"] = args.name_filter
    path = f"/dataservers/{quote(server_id, safe='')}/points?{urlencode(params, doseq=True)}"
    status, payload = _get_json(path, config)
    points: list[dict[str, Any]] = []
    if status == 200 and isinstance(payload, dict):
        for item in payload.get("Items", []) or []:
            points.append({
                "name": item.get("Name"),
                "web_id": item.get("WebId"),
                "point_type": item.get("PointType"),
                "units": item.get("Units"),
                "descriptor": item.get("Descriptor"),
                "path": item.get("Path"),
                "status": "verified",
                "verified_at": now_utc(),
            })
    result = {
        "system": "pi",
        "endpoint": f"/dataservers/{{webId}}/points",
        "server": args.server,
        "name_filter": args.name_filter,
        "access": f"http_{status}",
        "status": "verified" if points else ("forbidden" if status in (401, 403) else "unknown"),
        "verified_at": now_utc(),
        "points": points,
        "count": len(points),
        "note": "Truncated sample (maxCount cap). Do not brute-force tags (AGENTS rule 4).",
    }
    write_json(repo_root / "discovery" / "points.json", result)
    print(f"/dataservers/{args.server}/points HTTP {status}: {len(points)} point(s) (maxCount={args.max_count})")
    for p in points[:20]:
        print(f"  - {p['name']:<40} type={p['point_type']:<10} units={p['units']}")
    if len(points) > 20:
        print(f"  ... and {len(points) - 20} more (see discovery/points.json)")
    return 0


def _resolve_server(server: str, config: Config, repo_root: Path) -> str:
    """Resolve a server name to its WebId, using the cached dataservers catalog when possible."""
    catalog_path = repo_root / "discovery" / "dataservers.json"
    if catalog_path.exists():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            for s in catalog.get("data_servers", []) or []:
                if s.get("name") == server or s.get("web_id") == server:
                    return s["web_id"]
        except (ValueError, KeyError):
            pass
    # fall back: list dataservers live (read-only)
    status, payload = _get_json("/dataservers", config)
    if status == 200 and isinstance(payload, dict):
        for item in payload.get("Items", []) or []:
            if item.get("Name") == server:
                return item["WebId"]
    raise DiscoveryError(f"could not resolve data server '{server}'; run --list-dataservers first")


def cmd_point(args: argparse.Namespace, repo_root: Path) -> int:
    if not args.execute:
        print("--point requires --execute (network access is opt-in). Nothing done.")
        return 1
    config = Config.from_environment()
    params = {"path": args.path}
    path = f"/points?{urlencode(params, doseq=True)}"
    status, payload = _get_json(path, config)
    record: dict[str, Any] = {
        "system": "pi",
        "endpoint": "/points?path=",
        "lookup_path": args.path,
        "access": f"http_{status}",
        "status": "verified" if status == 200 else ("forbidden" if status in (401, 403) else "unknown"),
        "verified_at": now_utc(),
    }
    if status == 200 and isinstance(payload, dict):
        record["name"] = payload.get("Name")
        record["web_id"] = payload.get("WebId")
        record["point_type"] = payload.get("PointType")
        record["units"] = payload.get("Units")
        record["descriptor"] = payload.get("Descriptor")
        print(f"/points?path HTTP {status}: {record['name']} web_id={_short(record.get('web_id'))} units={record.get('units')}")
    else:
        record["notes"] = "point path not resolved; verify the tag name is authorized"
        print(f"/points?path HTTP {status}: not resolved")
    write_json(_stage_dir(repo_root) / "point-lookup.json", record)
    return 0


def _resolve_webid(webid_or_path: str, config: Config, repo_root: Path) -> str:
    """If given a WebId return it; if a path (\\\\server\\tag) resolve it read-only."""
    if webid_or_path.startswith("\\\\") or webid_or_path.startswith("/"):
        params = {"path": webid_or_path}
        status, payload = _get_json(f"/points?{urlencode(params, doseq=True)}", config)
        if status == 200 and isinstance(payload, dict):
            return payload.get("WebId")
        raise DiscoveryError(f"could not resolve path '{webid_or_path}' to a WebId (HTTP {status})")
    return webid_or_path


def cmd_stream_value(args: argparse.Namespace, repo_root: Path) -> int:
    if not args.execute:
        print("--stream-value requires --execute (network access is opt-in). Nothing done.")
        return 1
    config = Config.from_environment()
    web_id = _resolve_webid(args.webid, config, repo_root)
    path = f"/streams/{quote(web_id, safe='')}/value"
    status, payload = _get_json(path, config)
    record: dict[str, Any] = {
        "system": "pi",
        "endpoint": "/streams/{webId}/value",
        "web_id": web_id,
        "access": f"http_{status}",
        "status": "verified" if status == 200 else ("forbidden" if status in (401, 403) else "unknown"),
        "verified_at": now_utc(),
        "sample": payload if status == 200 else None,
    }
    write_json(_stage_dir(repo_root) / "stream-value.json", record)
    # keep a clean human-readable sample in samples/
    if status == 200 and isinstance(payload, dict):
        clean = {k: payload.get(k) for k in ("Timestamp", "Value", "UnitsAbbreviation", "Good", "IsSubstituted")}
        clean["_note"] = "SANITIZED TEMPLATE — replace with verified snapshot"
        write_json(repo_root / "samples" / "stream-value.sample.json", clean)
        print(f"/streams/value HTTP {status}: value={clean.get('Value')} {clean.get('UnitsAbbreviation')} good={clean.get('Good')}")
    else:
        print(f"/streams/value HTTP {status}: failed")
    return 0


def cmd_stream_recorded(args: argparse.Namespace, repo_root: Path) -> int:
    if not args.execute:
        print("--stream-recorded requires --execute (network access is opt-in). Nothing done.")
        return 1
    config = Config.from_environment()
    web_id = _resolve_webid(args.webid, config, repo_root)
    params = {"maxCount": str(args.max_count)}
    if args.start:
        params["startTime"] = args.start
    if args.end:
        params["endTime"] = args.end
    path = f"/streams/{quote(web_id, safe='')}/recorded?{urlencode(params, doseq=True)}"
    status, payload = _get_json(path, config)
    items = []
    if status == 200 and isinstance(payload, dict):
        items = payload.get("Items", []) or []
    record = {
        "system": "pi",
        "endpoint": "/streams/{webId}/recorded",
        "web_id": web_id,
        "start": args.start,
        "end": args.end,
        "max_count": args.max_count,
        "access": f"http_{status}",
        "status": "verified" if status == 200 else ("forbidden" if status in (401, 403) else "unknown"),
        "verified_at": now_utc(),
        "items_returned": len(items),
        "sample": items[:5],
    }
    write_json(_stage_dir(repo_root) / "stream-recorded.json", record)
    print(f"/streams/recorded HTTP {status}: {len(items)} value(s) (capped at {args.max_count})")
    for v in items[:5]:
        print(f"  - {v.get('Timestamp')}  value={v.get('Value')}  good={v.get('Good')}")
    return 0


# ------------------------------------------------------------------------ entry
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="discover_pi", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--documented", action="store_true", help="emit the documented PI Web API endpoint catalog (offline)")
    p.add_argument("--probe-system", action="store_true", help="GET / to test reachability (needs --execute)")
    p.add_argument("--list-dataservers", action="store_true", help="GET /dataservers inventory (needs --execute)")
    p.add_argument("--list-points", action="store_true", help="GET /dataservers/{webId}/points (needs --execute)")
    p.add_argument("--server", help="data server name (for --list-points)")
    p.add_argument("--name-filter", help="PI point name filter / wildcard (for --list-points)")
    p.add_argument("--max-count", type=int, default=100, help="max items per request (default 100, respects rate limits)")
    p.add_argument("--point", action="store_true", help="resolve a single point by --path (needs --execute)")
    p.add_argument("--path", help="canonical PI path, e.g. \\\\server\\tag (for --point)")
    p.add_argument("--stream-value", action="store_true", help="GET /streams/{webId}/value snapshot (needs --execute)")
    p.add_argument("--stream-recorded", action="store_true", help="GET /streams/{webId}/recorded history (needs --execute)")
    p.add_argument("--webid", help="point WebId or path (for --stream-value / --stream-recorded)")
    p.add_argument("--start", help="recorded start time (for --stream-recorded)")
    p.add_argument("--end", help="recorded end time (for --stream-recorded)")
    p.add_argument("--execute", action="store_true", help="opt-in to any network access")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parent.parent
    if args.documented:
        return cmd_documented(args, repo_root)
    if args.probe_system:
        return cmd_probe_system(args, repo_root)
    if args.list_dataservers:
        return cmd_list_dataservers(args, repo_root)
    if args.list_points:
        return cmd_list_points(args, repo_root)
    if args.point:
        return cmd_point(args, repo_root)
    if args.stream_value:
        return cmd_stream_value(args, repo_root)
    if args.stream_recorded:
        return cmd_stream_recorded(args, repo_root)
    parse_args(["--help"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DiscoveryError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)
