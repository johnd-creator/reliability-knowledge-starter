#!/usr/bin/env python3
"""Read-only Maximo OAS discovery and minimal sample mapper.

The production safety boundary is deliberate: business resources only receive
GET/HEAD/OPTIONS. Form authentication has one narrow exception: a controlled
POST to the exact ``/j_security_check`` endpoint, with credentials from the
environment and cookies retained in memory only. No other POST, PUT, PATCH,
DELETE, or MERGE is permitted.
"""

from __future__ import annotations

import argparse
import base64
import http.cookiejar
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import HTTPRedirectHandler, HTTPCookieProcessor, Request, build_opener

LOG = logging.getLogger(__name__)

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


READ_ONLY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE", "MERGE"})
LOGIN_PATH = "/j_security_check"
LOGIN_MODES = frozenset({"form", "login"})
DEFAULT_SCOPE = {
    "asset",
    "location",
    "workorder",
    "preventivemaintenance",
    "failurecode",
    "meter",
    "labor",
    "materials",
}
SENSITIVE_KEY = re.compile(
    r"(?:password|passwd|secret|token|authorization|cookie|session|csrf|apikey|api_key|private.?key)",
    re.IGNORECASE,
)
PERSONAL_KEY = re.compile(
    r"(?:email|e_mail|phone|telephone|mobile|ssn|social.?security|username|user_name)",
    re.IGNORECASE,
)

RESOURCE_LINK_KEYS = ("rdf:resource", "href", "resource", "@id")
MAXIMO_BUSINESS_NAMESPACES = frozenset({"spi"})
NAMESPACE_METADATA_NAMESPACES = frozenset({"rdf", "oslc", "dcterms", "rdfs"})
DEFAULT_SITE_ID = "BSR"
DEFAULT_ORG_ID = "IP"

# These clauses are not inferred from the object names. They are the exact
# BSR-scoped query shape used by MX-006R for the listed resources. Keeping the
# allowlist explicit prevents this discovery tool from trying arbitrary scope
# fields against production. A detail contract records this provenance as
# PRIOR_LIVE_QUERY until a field itself is exposed by the detail response.
PRIOR_LIVE_BSR_SCOPE_RESOURCES = frozenset(
    {
        "IPFMEA",
        "IPFMEAITEM",
        "IPRCFA",
        "IPRCFAFDT",
        "IPBHM",
        "IPBHMMEASUREMENT",
        "IPMSMSFAILUREMECHANI",
        "DMD_OPLOGABN",
        "IP_DOM_OH",
        "DOM_INSPEKSIMESIN",
        "IP_DOM_OH_SCOPE_PM",
        "MXAPIFAILURECODE",
        "MXAPILOCATION",
        "MXAPIPM",
        "MXAPIMETER",
        "MXAPIJOBPLAN",
    }
)
MX006B_EXPLICIT_TARGETS = frozenset(
    {
        "IPFMEA",
        "IPFMEAITEM",
        "IPRCFA",
        "IPBHM",
        "IPBHMMEASUREMENT",
        "IPMSMSFAILUREMECHANI",
        "DMD_OPLOGABN",
        "IP_DOM_OH",
        "DOM_INSPEKSIMESIN",
        "IP_DOM_OH_SCOPE_PM",
        "IPRCFAFDT",
        "MXAPIFAILURECODE",
        "MXAPILOCATION",
        "MXAPIPM",
        "MXAPIMETER",
        "MXAPIJOBPLAN",
    }
)


class DiscoveryError(RuntimeError):
    """A safe, user-facing discovery failure."""


@dataclass(frozen=True)
class Config:
    base_url: str
    oas_path: str
    auth_mode: str
    token: str
    username: str
    password: str
    timeout_seconds: float
    rate_limit_seconds: float
    max_response_bytes: int

    @classmethod
    def from_environment(cls, require_base_url: bool = True) -> "Config":
        load_dotenv()
        base_url = os.getenv("MAXIMO_BASE_URL", "").strip().rstrip("/")
        if require_base_url and not base_url:
            raise DiscoveryError("MAXIMO_BASE_URL is required")
        return cls(
            base_url=base_url,
            oas_path=os.getenv("MAXIMO_OAS_PATH", "/oslc/oas").strip(),
            auth_mode=os.getenv("MAXIMO_AUTH_MODE", "none").strip().lower(),
            token=os.getenv("MAXIMO_TOKEN", "") or os.getenv("MAXIMO_READ_ONLY_TOKEN", ""),
            username=os.getenv("MAXIMO_USERNAME", ""),
            password=os.getenv("MAXIMO_PASSWORD", ""),
            timeout_seconds=float(os.getenv("MAXIMO_TIMEOUT_SECONDS", "30")),
            rate_limit_seconds=float(os.getenv("MAXIMO_RATE_LIMIT_SECONDS", "1")),
            max_response_bytes=int(os.getenv("MAXIMO_MAX_RESPONSE_BYTES", "1048576")),
        )


def load_dotenv(path: Path | str = ".env") -> None:
    """Load simple KEY=VALUE entries without overriding process variables."""

    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def _origin_parts(url: str) -> tuple[str, str, int | None]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise DiscoveryError("Maximo URL must use HTTP(S) with a hostname")
    if parsed.username or parsed.password:
        raise DiscoveryError("Maximo URL must not contain embedded credentials")
    try:
        port = parsed.port
    except ValueError as error:
        raise DiscoveryError("Maximo URL contains an invalid port") from error
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    return parsed.scheme.lower(), parsed.hostname.lower(), port


def resolve_same_origin_url(base_url: str, candidate: str) -> str:
    """Resolve one Maximo link and enforce the configured HTTP origin.

    The origin check intentionally compares scheme, hostname, and effective
    port only. The application path may differ (for example, a returned
    detail link may be rooted at ``/maximo/oslc``), but credentials are never
    sent to another origin.
    """

    if not base_url:
        raise DiscoveryError("MAXIMO_BASE_URL is required to validate a resource link")
    base = base_url.rstrip("/")
    base_origin = _origin_parts(base)
    parsed_candidate = urlparse(candidate)
    if parsed_candidate.scheme or parsed_candidate.netloc:
        resolved = candidate
    else:
        # Maximo commonly returns both /oslc/... and oslc/... links. Resolve
        # both beneath the configured application base, while rejecting
        # network-path references (//other-host/...) as absolute URLs.
        resolved = urljoin(base + "/", candidate.lstrip("/"))
    candidate_origin = _origin_parts(resolved)
    if candidate_origin != base_origin:
        raise DiscoveryError(
            "Maximo resource link returned a different origin; refusing to "
            "send the authenticated session outside MAXIMO_BASE_URL"
        )
    return resolved


def safe_resource_path(url: str) -> str:
    """Return structural URL evidence without persisting hostnames or IDs."""

    parsed = urlparse(url)
    path = parsed.path or "/"
    parts = [part for part in path.split("/") if part]
    if parts:
        parts[-1] = "<resource-id>"
        path = "/" + "/".join(parts)
    return path


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_document(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8-sig")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        if yaml is None:
            raise DiscoveryError(
                "OAS is not JSON and PyYAML is unavailable; install requirements.txt"
            )
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise DiscoveryError("OAS document must be a JSON/YAML object")
    if not value.get("openapi") and not value.get("swagger"):
        raise DiscoveryError("response is not an OpenAPI/Swagger document")
    if not isinstance(value.get("paths", {}), dict):
        raise DiscoveryError("OAS document has no valid paths object")
    return value


def scalar_type(schema: Mapping[str, Any] | None) -> str | None:
    if not isinstance(schema, Mapping):
        return None
    if isinstance(schema.get("type"), str):
        return str(schema["type"])
    if isinstance(schema.get("$ref"), str):
        return schema["$ref"].rsplit("/", 1)[-1]
    if "properties" in schema:
        return "object"
    return None


def schema_properties(schema: Mapping[str, Any] | None, limit: int = 100) -> list[str]:
    if not isinstance(schema, Mapping):
        return []
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        items = schema.get("items")
        return schema_properties(items if isinstance(items, Mapping) else None, limit)
    return [str(key) for key in list(properties)[:limit] if not SENSITIVE_KEY.search(str(key))]


def response_fields(operation: Mapping[str, Any]) -> list[str]:
    fields: list[str] = []
    responses = operation.get("responses", {})
    if not isinstance(responses, Mapping):
        return fields
    for response in responses.values():
        if not isinstance(response, Mapping):
            continue
        content = response.get("content", {})
        if isinstance(content, Mapping):
            for media in content.values():
                if isinstance(media, Mapping):
                    fields.extend(schema_properties(media.get("schema")))
        schema = response.get("schema")
        fields.extend(schema_properties(schema if isinstance(schema, Mapping) else None))
    return dedupe(fields)


def dedupe(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def normalize_resource(value: str) -> str:
    value = value.lower().replace("_", "").replace("-", "").replace(" ", "")
    aliases = {
        "wo": "workorder",
        "workorders": "workorder",
        "pm": "preventivemaintenance",
        "pms": "preventivemaintenance",
        "failurecodes": "failurecode",
        "meters": "meter",
    }
    return aliases.get(value, value)


def infer_resource(path: str, operation: Mapping[str, Any]) -> str:
    tags = operation.get("tags")
    if isinstance(tags, list) and tags and isinstance(tags[0], str):
        return normalize_resource(tags[0])
    parts = [part for part in urlparse(path).path.split("/") if part and not part.startswith("{")]
    return normalize_resource(parts[-1] if parts else "unknown")


def parameter_metadata(parameters: Iterable[Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for parameter in parameters:
        if not isinstance(parameter, Mapping):
            continue
        name = str(parameter.get("name", ""))
        if not name or SENSITIVE_KEY.search(name):
            continue
        schema = parameter.get("schema")
        result.append(
            {
                "name": name,
                "in": parameter.get("in"),
                "required": bool(parameter.get("required", False)),
                "type": scalar_type(schema if isinstance(schema, Mapping) else None)
                or scalar_type(parameter),
            }
        )
    return result


def operation_entries(oas: Mapping[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path, path_item in oas.get("paths", {}).items():
        if not isinstance(path_item, Mapping):
            continue
        shared = path_item.get("parameters", [])
        shared = shared if isinstance(shared, list) else []
        for method, operation in path_item.items():
            method_upper = str(method).upper()
            if method_upper not in READ_ONLY_METHODS or not isinstance(operation, Mapping):
                continue
            operation_parameters = operation.get("parameters", [])
            parameters = shared + (operation_parameters if isinstance(operation_parameters, list) else [])
            entries.append(
                {
                    "resource": infer_resource(str(path), operation),
                    "path": str(path),
                    "method": method_upper,
                    "operation": operation,
                    "parameters": parameter_metadata(parameters),
                }
            )
    return entries


def endpoint_record(entry: Mapping[str, Any], verified: Mapping[str, Any] | None = None) -> dict[str, Any]:
    operation = entry["operation"]
    record: dict[str, Any] = {
        "resource": entry["resource"],
        "endpoint": entry["path"],
        "method": entry["method"],
        "status": "documented",
        "access": "unknown",
        "description": str(operation.get("description") or operation.get("summary") or ""),
        "parameters": entry["parameters"],
        "important_fields": response_fields(operation),
        "relationships": [],
        "use_cases": use_cases_for(entry["resource"]),
        "notes": [],
        "verified_at": None,
    }
    if verified:
        record.update(verified)
    return record


def use_cases_for(resource: str) -> list[str]:
    mapping = {
        "workorder": ["work-order-history", "failure-analysis"],
        "asset": ["asset-reliability", "asset-history"],
        "location": ["location-hierarchy", "asset-context"],
        "preventivemaintenance": ["preventive-maintenance-analysis"],
        "failurecode": ["failure-analysis"],
        "meter": ["condition-monitoring"],
        "labor": ["work-order-resource-analysis"],
        "materials": ["spare-parts-analysis"],
    }
    return mapping.get(resource, [])


def sanitize(value: Any, key: str = "") -> Any:
    if SENSITIVE_KEY.search(key) or PERSONAL_KEY.search(key):
        return "<REDACTED>"
    if isinstance(value, Mapping):
        return {
            str(k): sanitize(v, str(k))
            for k, v in value.items()
            if not SENSITIVE_KEY.search(str(k)) and not PERSONAL_KEY.search(str(k))
        }
    if isinstance(value, list):
        return [sanitize(item, key) for item in value[:20]]
    if isinstance(value, str) and len(value) > 1000:
        return value[:1000] + "<TRUNCATED>"
    return value


def response_structure(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(k): response_structure(v)
            for k, v in list(value.items())[:100]
            if not SENSITIVE_KEY.search(str(k)) and not PERSONAL_KEY.search(str(k))
        }
    if isinstance(value, list):
        return [response_structure(value[0])] if value else []
    return type(value).__name__


def capability_record(oas: Mapping[str, Any], entries: list[Mapping[str, Any]]) -> dict[str, Any]:
    names = {p["name"].lower() for e in entries for p in e["parameters"] if p.get("name")}
    return {
        "system": "maximo",
        "capabilities": {
            "openapi_available": True,
            "filtering": bool({"oslc.where", "where"} & names),
            "sorting": bool({"oslc.orderby", "orderby"} & names),
            "pagination": bool({"oslc.pageno", "oslc.pagesize", "pagesize"} & names),
            "field_selection": bool({"oslc.select", "select"} & names),
            "related_objects": any("relationship" in str(e["operation"]).lower() for e in entries),
        },
        "openapi_version": oas.get("openapi") or oas.get("swagger"),
        "endpoint_count": len(entries),
        "last_updated": now_utc(),
    }


class ReadOnlyClient:
    def __init__(self, config: Config):
        self.config = config
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = build_opener(NoRedirectHandler(), HTTPCookieProcessor(self.cookie_jar))
        self._last_request = 0.0
        self._logged_in = False
        self._login_attempts = 0
        self._reauth_attempts = 0

    @property
    def logged_in(self) -> bool:
        """Whether the in-memory client currently has an authenticated mode."""
        return self._logged_in

    def _effective_rate_limit(self) -> float:
        # Live knowledge probes are deliberately slower than the collector.
        # A zero value remains useful for hermetic unit tests.
        return 0.0 if self.config.rate_limit_seconds <= 0 else max(self.config.rate_limit_seconds, 5.0)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json, application/yaml, text/yaml, */*",
            "User-Agent": "maximo-knowledge-readonly/1.0",
        }
        if self.config.auth_mode in {"bearer", "token"}:
            if not self.config.token:
                raise DiscoveryError("MAXIMO_TOKEN is required for bearer auth")
            headers["Authorization"] = f"Bearer {self.config.token}"
        elif self.config.auth_mode == "basic":
            if not self.config.username or not self.config.password:
                raise DiscoveryError("MAXIMO_USERNAME and MAXIMO_PASSWORD are required for basic auth")
            raw = f"{self.config.username}:{self.config.password}".encode()
            headers["Authorization"] = "Basic " + base64.b64encode(raw).decode()
        elif self.config.auth_mode in LOGIN_MODES:
            # Form credentials belong only in the one-time login body, never
            # in headers on business requests.
            pass
        elif self.config.auth_mode != "none":
            raise DiscoveryError(f"unsupported MAXIMO_AUTH_MODE: {self.config.auth_mode}")
        return headers

    def _resolve_url(self, path: str) -> str:
        return resolve_same_origin_url(self.config.base_url, path)

    def _login_url(self) -> str:
        # LOGIN_PATH is a constant; it is never accepted from CLI arguments.
        return urljoin(self.config.base_url + "/", LOGIN_PATH.lstrip("/"))

    def _is_approved_login_url(self, url: str) -> bool:
        actual = urlparse(url)
        expected = urlparse(self._login_url())
        return (
            actual.scheme == expected.scheme
            and actual.netloc == expected.netloc
            and actual.path == expected.path
            and not actual.query
            and not actual.fragment
        )

    def _rate_limit(self) -> None:
        delay = self._effective_rate_limit() - (time.monotonic() - self._last_request)
        if delay > 0:
            time.sleep(delay)

    @staticmethod
    def _has_session_cookie(cookie_jar: http.cookiejar.CookieJar) -> bool:
        return any(cookie.name in {"JSESSIONID", "LtpaToken2"} for cookie in cookie_jar)

    @staticmethod
    def _looks_like_login_response(status: int, headers: Mapping[str, str], body: bytes, response_url: str = "") -> bool:
        if status in (401, 403):
            return True
        location = str(headers.get("Location", "")).lower()
        if "login" in location or "j_security_check" in location:
            return True
        content_type = str(headers.get("Content-Type", "")).lower()
        if "html" not in content_type:
            return False
        text = body[:4096].decode("utf-8", errors="ignore").lower()
        return any(marker in text or marker in response_url.lower() for marker in ("login.jsp", "loginerror.jsp", "j_security_check"))

    def _raw_request(self, request: Request) -> tuple[int, Mapping[str, str], bytes, str]:
        try:
            with self.opener.open(request, timeout=self.config.timeout_seconds) as response:
                return response.status, response.headers, read_limited(response, self.config.max_response_bytes), str(getattr(response, "url", ""))
        except HTTPError as error:
            return error.code, error.headers, read_limited(error, self.config.max_response_bytes), str(getattr(error, "url", ""))
        except URLError as error:
            raise DiscoveryError(f"network error for {request.get_method()} {redact_url(request.full_url)}: {error.reason}") from error

    def authenticate(self, *, reauthentication: bool = False) -> tuple[int, Mapping[str, str], bytes]:
        """Perform at most one initial login and one expiry re-login."""
        if self.config.auth_mode not in LOGIN_MODES:
            self._logged_in = True
            return 200, {}, b""
        if reauthentication:
            if self._reauth_attempts >= 1:
                raise DiscoveryError("AUTHENTICATION FAILED: re-login limit reached")
            self._reauth_attempts += 1
        else:
            if self._login_attempts >= 1:
                raise DiscoveryError("AUTHENTICATION FAILED: login limit reached")
            self._login_attempts += 1
        if not self.config.username or not self.config.password:
            raise DiscoveryError("form/login auth requires MAXIMO_USERNAME and MAXIMO_PASSWORD")
        LOG.info("Maximo authentication attempt started")
        self._rate_limit()
        url = self._login_url()
        body = urlencode({"j_username": self.config.username, "j_password": self.config.password}).encode("utf-8")
        request = Request(
            url,
            data=body,
            headers={"Accept": "text/html", "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        status, headers, response_body, response_url = self._raw_request(request)
        self._last_request = time.monotonic()
        if not self._has_session_cookie(self.cookie_jar) or self._looks_like_login_response(status, headers, response_body, response_url):
            self._logged_in = False
            raise DiscoveryError("AUTHENTICATION FAILED: Maximo login did not establish a valid read-only session")
        self._logged_in = True
        LOG.info("Maximo authentication successful; session remains in memory")
        return status, headers, response_body

    def _ensure_authenticated(self) -> None:
        if self.config.auth_mode in LOGIN_MODES and not self._logged_in:
            self.authenticate()
        elif self.config.auth_mode in {"bearer", "token", "basic"}:
            # Header validation happens here, before the business GET.
            self._headers()
            self._logged_in = True

    def request(self, method: str, path: str) -> tuple[int, Mapping[str, str], bytes]:
        method = method.upper()
        url = self._resolve_url(path)
        if method == "POST" and self._is_approved_login_url(url):
            return self.authenticate()
        if method not in READ_ONLY_METHODS or method in MUTATING_METHODS:
            raise DiscoveryError(f"blocked business method: {method}")
        self._ensure_authenticated()
        self._rate_limit()
        request = Request(url, headers=self._headers(), method=method)
        self._last_request = time.monotonic()
        status, headers, body, response_url = self._raw_request(request)
        if self.config.auth_mode in LOGIN_MODES and self._looks_like_login_response(status, headers, body, response_url):
            if self._reauth_attempts >= 1:
                raise DiscoveryError("AUTHENTICATION FAILED: session expired after controlled re-login")
            self._logged_in = False
            self.cookie_jar.clear()
            LOG.warning("Maximo session expired; one controlled re-authentication")
            self.authenticate(reauthentication=True)
            self._rate_limit()
            retry = Request(url, headers=self._headers(), method=method)
            self._last_request = time.monotonic()
            status, headers, body, _ = self._raw_request(retry)
            if self._looks_like_login_response(status, headers, body):
                raise DiscoveryError("AUTHENTICATION FAILED: session expired after controlled re-login")
        return status, headers, body


class NoRedirectHandler(HTTPRedirectHandler):
    """Keep redirects as evidence instead of following them to another host."""

    def redirect_request(self, request: Request, *args: Any, **kwargs: Any) -> None:
        return None


def read_limited(response: Any, limit: int) -> bytes:
    body = response.read(limit + 1)
    if len(body) > limit:
        raise DiscoveryError(f"response exceeded MAXIMO_MAX_RESPONSE_BYTES ({limit})")
    return body


def redact_url(url: str) -> str:
    parsed = urlparse(url)
    query = [(key, "<REDACTED>" if SENSITIVE_KEY.search(key) else value) for key, value in parse_qsl(parsed.query)]
    return urlunparse(parsed._replace(query=urlencode(query)))


def minimal_query(entry: Mapping[str, Any]) -> tuple[dict[str, str], list[str]]:
    query: dict[str, str] = {}
    missing: list[str] = []
    for parameter in entry["parameters"]:
        name = str(parameter.get("name") or "")
        location = parameter.get("in")
        if location == "path" and parameter.get("required"):
            missing.append(name)
        elif location == "query" and name.lower() in {"oslc.pagesize", "pagesize", "limit", "maxpagesize"}:
            query[name] = "1"
    return query, missing


def url_with_query(path: str, query: Mapping[str, str]) -> str:
    if not query:
        return path
    parsed = urlparse(path)
    return urlunparse(parsed._replace(query=urlencode(parse_qsl(parsed.query) + list(query.items()))))


def select_entries(entries: list[dict[str, Any]], scope: str | None, resources: list[str]) -> list[dict[str, Any]]:
    requested = {normalize_resource(item) for item in resources}
    if scope == "reliability-core":
        requested |= DEFAULT_SCOPE
    if not requested:
        return entries
    return [entry for entry in entries if normalize_resource(entry["resource"]) in requested]


def object_structures(entries: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    structures: dict[str, dict[str, Any]] = {}
    for entry in entries:
        match = re.search(r"/(?:oslc/)?(?:os|objectstructures?)/([^/{?]+)", str(entry["path"]), re.IGNORECASE)
        if not match:
            continue
        name = match.group(1)
        item = structures.setdefault(name, {"name": name, "endpoints": [], "methods": [], "status": "documented"})
        item["endpoints"].append(entry["path"])
        item["methods"] = dedupe([*item["methods"], entry["method"]])
    return {"system": "maximo", "object_structures": list(structures.values()), "last_updated": now_utc()}


# --- OSLC object-structure discovery ----------------------------------------
# Maximo exposes its real resource surface through OSLC Object Structures at
# /oslc/os rather than through a fully populated OAS `paths` object. The helpers
# below enumerate and describe those structures using business GET/HEAD/OPTIONS
# only and degrade gracefully to a documented seed when the catalog cannot be parsed.

OSLC_MEMBER_KEYS = (
    "_member",
    "member",
    "oslc:member",
    "rdfs:member",
    "oslc:serviceProvider",
    "items",
    "entry",
)
OSLC_CATALOG_NAME_KEYS = (
    "oslc:name",
    "name",
    "oslc:label",
    "dcterms:title",
    "title",
    "_name",
    "objectStructure",
)
OSLC_OBJECT_ROOT = "/oslc/os"
OSLC_CATALOG_ROOT = "/oslc/"
OSLC_MINIMAL_PARAM = "_maxitems=1"
DETAIL_COLLECTION_SELECT = "href"

# Well-documented public Maximo integration object structures. Marked
# `documented` (from public Maximo knowledge) until verified against this
# specific instance. Used as a safe fallback/seed and to map names to
# reliability resources.
SEED_OBJECT_STRUCTURES = [
    {"name": "MXASSET", "resource": "asset"},
    {"name": "MXWODETAIL", "resource": "workorder"},
    {"name": "MXWORKORDER", "resource": "workorder"},
    {"name": "MXLOCATIONS", "resource": "location"},
    {"name": "MXPM", "resource": "preventivemaintenance"},
    {"name": "MXFAILURECODE", "resource": "failurecode"},
    {"name": "MXMETER", "resource": "meter"},
    {"name": "MXLABOR", "resource": "labor"},
    {"name": "MXLABORCRAFT", "resource": "labor"},
    {"name": "MXINVSTEM", "resource": "materials"},
    {"name": "MXINVENTORY", "resource": "materials"},
    {"name": "MXITEM", "resource": "materials"},
    {"name": "MXJOBPLAN", "resource": "jobplan"},
    {"name": "MXSR", "resource": "sr"},
    {"name": "MXPERSON", "resource": "person"},
    {"name": "MXSERVICEITEM", "resource": "sr"},
]


def is_internal_field(key: str) -> bool:
    """A Maximo OSLC internal/namespace field (_rowstamp, oslc:, rdf:, ...)."""
    key = str(key)
    if not key:
        return True
    namespace, separator, local_name = key.partition(":")
    if separator and namespace.lower() in MAXIMO_BUSINESS_NAMESPACES:
        return is_internal_field(local_name)
    return key.startswith("_") or bool(separator)


def normalized_business_key(key: str) -> str | None:
    """Normalize only the known Maximo business namespace.

    OSLC/RDF metadata remains metadata. In particular, this function does not
    strip arbitrary prefixes because doing so would turn protocol fields into
    false business contracts.
    """

    text = str(key)
    namespace, separator, local_name = text.partition(":")
    if separator and namespace.lower() in MAXIMO_BUSINESS_NAMESPACES:
        text = local_name
    if is_internal_field(text) or text in RESOURCE_LINK_KEYS:
        return None
    if SENSITIVE_KEY.search(text) or PERSONAL_KEY.search(text):
        return None
    return text


def business_fields(value: Any) -> list[str]:
    """Top-level business field names from a record or collection (non-internal)."""
    if isinstance(value, Mapping):
        return dedupe(
            normalized
            for key in value
            if (normalized := normalized_business_key(str(key))) is not None
        )
    if isinstance(value, list):
        for item in value:
            if isinstance(item, Mapping):
                return business_fields(item)
    return []


def oslc_members(payload: Any) -> list[Mapping[str, Any]]:
    """Extract member records from an OSLC collection, tolerant of shapes."""
    if isinstance(payload, list):
        return [m for m in payload if isinstance(m, Mapping)]
    if isinstance(payload, Mapping):
        for key in OSLC_MEMBER_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                return [m for m in value if isinstance(m, Mapping)]
            if isinstance(value, Mapping):
                return [value]
    return []


def resource_link(member: Mapping[str, Any]) -> str | None:
    """Return one explicitly supported OSLC detail link, if present."""

    for key in RESOURCE_LINK_KEYS:
        value = member.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def is_pure_resource_link_member(member: Mapping[str, Any]) -> bool:
    """A link-only member has no normalized business fields of its own."""

    return resource_link(member) is not None and not business_fields(member)


def normalize_detail_record(value: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Split one detail object into business fields and protocol metadata names."""

    business: dict[str, Any] = {}
    metadata: list[str] = []
    for key, raw_value in value.items():
        normalized = normalized_business_key(str(key))
        if normalized is None:
            metadata.append(str(key))
            continue
        business[normalized] = raw_value
    return business, dedupe(metadata)


def inferred_value_type(value: Any, field: str = "") -> str:
    """Infer a small, contract-oriented primitive type without coercion."""

    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, Mapping):
        return "object/reference"
    if isinstance(value, list):
        return "collection-reference" if "collectionref" in field.lower() else "unknown"
    if isinstance(value, str):
        text = value.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:", text):
            return "datetime"
        return "string"
    return "unknown"


def detail_field_types(business: Mapping[str, Any]) -> dict[str, str]:
    return {str(field): inferred_value_type(value, str(field)) for field, value in business.items()}


def structural_example(business: Mapping[str, Any]) -> dict[str, str]:
    """Save types, not live values, as a detail sample."""

    return {field: f"<{value_type}>" for field, value_type in detail_field_types(business).items()}


RELATIONSHIP_FIELD_PATTERNS: dict[str, tuple[str, ...]] = {
    "asset": ("assetnum", "assetid", "asset", "equipment", "equipmentid"),
    "location": ("location", "locationid", "locnum"),
    "site": ("siteid", "site"),
    "organization": ("orgid", "organization", "organizationid"),
    "workorder": ("wonum", "workorder", "workorderid"),
    "status": ("status",),
    "timestamp": ("date", "datetime", "timestamp", "time"),
}


def relationship_evidence(fields: Iterable[str]) -> list[str]:
    lowered = {field.lower(): field for field in fields}
    relationships: list[str] = []
    for relationship, patterns in RELATIONSHIP_FIELD_PATTERNS.items():
        matches = [lowered[name] for name in lowered if name in patterns]
        if relationship == "timestamp":
            matches = [
                field
                for field in fields
                if any(pattern in field.lower() for pattern in patterns)
            ]
        if matches:
            label = "timestamp" if relationship == "timestamp" else relationship
            relationships.append(f"{label}: {', '.join(dedupe(matches))} (VERIFIED field evidence)")
    return relationships


def primary_key_evidence(fields: Iterable[str]) -> dict[str, str] | None:
    candidates = [field for field in fields if _looks_like_identifier(field)]
    if not candidates:
        return None
    return {"field": candidates[0], "confidence": "CANDIDATE"}


def error_diagnostics(status: int, body: bytes) -> dict[str, Any]:
    """Keep only bounded, sanitized Maximo error metadata."""

    code: str | None = None
    reason = f"HTTP {status}; sanitized error detail unavailable"
    try:
        payload = parse_payload(body)
    except DiscoveryError:
        payload = None
    if isinstance(payload, Mapping):
        for key in ("errorcode", "errorCode", "code", "BMXAA"):
            value = payload.get(key)
            if value:
                match = re.search(r"BMX[A-Z0-9]+", str(value), re.IGNORECASE)
                code = match.group(0).upper() if match else "<sanitized>"
                break
        for key in ("message", "errorMessage", "description", "reason", "error"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                reason = sanitize(value.strip()[:240], key)
                break
    elif body:
        match = re.search(rb"BMX[A-Z0-9]+", body[:4096], re.IGNORECASE)
        if match:
            code = match.group(0).decode("ascii", errors="ignore").upper()
    return {"http_status": status, "maximo_error_code": code, "reason": reason, "raw_response_saved": False}


def oslc_pagination_info(payload: Any) -> dict[str, Any]:
    base = payload if isinstance(payload, Mapping) else {}
    info = base.get("oslc:responseInfo")
    info = info if isinstance(info, Mapping) else {}

    def _get(name: str) -> Any:
        return info.get(name, base.get(name))

    total = _get("oslc:totalCount")
    if total is None:
        total = _get("totalCount")
    try:
        total = int(total) if total is not None else None
    except (TypeError, ValueError):
        total = None
    return {
        "total_count": total,
        "next_page": bool(_get("oslc:nextPage")),
        "prev_page": bool(_get("oslc:prevPage")),
    }


def parse_object_structure_catalog(payload: Any) -> list[str]:
    """Return object-structure names from a catalog collection, order-preserving."""
    names: list[str] = []
    seen: set[str] = set()
    for member in oslc_members(payload):
        for attr in OSLC_CATALOG_NAME_KEYS:
            value = member.get(attr) if isinstance(member, Mapping) else None
            if isinstance(value, str) and value.strip():
                cleaned = value.strip()
                if cleaned.lower() not in seen:
                    seen.add(cleaned.lower())
                    names.append(cleaned)
                break
    return names


def _looks_like_identifier(field: str) -> bool:
    lowered = field.lower()
    return (
        lowered.endswith("num")
        or lowered.endswith("code")
        or lowered.endswith("id")
        or lowered.endswith("key")
    )


def object_structure_record(
    name: str,
    resource: str,
    *,
    members: list[Mapping[str, Any]] | None = None,
    pagination: Mapping[str, Any] | None = None,
    status: str = "documented",
    access: str = "unknown",
    verified_at: str | None = None,
    notes: list[str] | None = None,
    scope: Mapping[str, Any] | None = None,
    detail_dereference: Mapping[str, Any] | None = None,
    field_types: Mapping[str, str] | None = None,
    metadata_fields: Iterable[str] | None = None,
    primary_key: str | Mapping[str, str] | None = None,
    http_diagnostics: Mapping[str, Any] | None = None,
    endpoint: str | None = None,
) -> dict[str, Any]:
    members = members or []
    fields = dedupe(sum((business_fields(m) for m in members), []))
    sample = None
    if members:
        business, _metadata = normalize_detail_record(members[0])
        sample = sanitize(business)
    return {
        "system": "maximo",
        "object_structure": name,
        "resource": resource,
        "status": status,
        "access": access,
        "endpoint": endpoint or minimal_object_query(name),
        "primary_key": primary_key,
        "field_candidates": [f for f in fields if _looks_like_identifier(f)][:50],
        "important_fields": fields[:100],
        "field_types": dict(field_types or {}),
        "metadata_fields": list(metadata_fields or []),
        "pagination": dict(pagination) if pagination else {},
        "sample": sample,
        "use_cases": use_cases_for(resource),
        "relationships": [],
        "notes": list(notes or []),
        "verified_at": verified_at,
        "scope": dict(scope or {}),
        "detail_dereference": dict(detail_dereference or {}),
        "http_diagnostics": dict(http_diagnostics or {}),
    }


def seed_object_structures() -> list[dict[str, Any]]:
    return [dict(item) for item in SEED_OBJECT_STRUCTURES]


def scope_clause_for(name: str) -> str | None:
    """Return only a previously evidenced BSR scope clause."""

    if str(name).upper() in PRIOR_LIVE_BSR_SCOPE_RESOURCES:
        return f'siteid="{DEFAULT_SITE_ID}"'
    return None


def minimal_object_query(
    name: str,
    scope_clause: str | None = None,
    select: str | None = None,
) -> str:
    return minimal_object_query_with_select(name, scope_clause, select)


def minimal_object_query_with_select(
    name: str,
    scope_clause: str | None = None,
    select: str | None = None,
) -> str:
    query = [("_maxitems", "1")]
    if scope_clause:
        query.append(("oslc.where", scope_clause))
    if select:
        query.append(("oslc.select", select))
    return f"{OSLC_OBJECT_ROOT}/{name}?{urlencode(query)}"


def validate_object_structure_record(record: Mapping[str, Any]) -> None:
    required = {"system", "object_structure", "resource", "status"}
    missing = required - set(record)
    if missing:
        raise DiscoveryError("object record missing required fields: " + ", ".join(sorted(missing)))
    if record["status"] not in {"unknown", "documented", "verified", "forbidden", "deprecated"}:
        raise DiscoveryError(f"invalid object status: {record['status']}")
    if record["status"] == "verified" and not record.get("verified_at"):
        raise DiscoveryError("verified object record must have verified_at")
    if contains_sensitive_key(record):
        raise DiscoveryError("object record contains a sensitive field name")


def enumerate_object_structures(client: Any, oslc_root: str = OSLC_CATALOG_ROOT) -> dict[str, Any]:
    """GET the OSLC object-structure catalog safely.

    Falls back to a documented seed when the catalog cannot be read or parsed,
    so discovery can continue without guessing. Returns a dict with `source`,
    `object_structures` (name/resource/status) and `notes`.
    """
    result: dict[str, Any] = {"source": "oslc-catalog", "object_structures": [], "notes": []}
    fallback = [
        {"name": item["name"], "resource": item["resource"], "status": "documented"}
        for item in seed_object_structures()
    ]
    try:
        status, _headers, body = client.request("GET", oslc_root)
    except DiscoveryError as error:
        result["source"] = "seed-fallback"
        result["notes"].append(f"catalog GET failed: {error}")
        result["object_structures"] = fallback
        return result
    if status < 200 or status >= 300:
        result["source"] = "seed-fallback"
        result["notes"].append(f"catalog GET returned HTTP {status}; using documented seed")
        result["object_structures"] = fallback
        return result
    try:
        payload = parse_payload(body)
    except DiscoveryError as error:
        result["source"] = "seed-fallback"
        result["notes"].append(f"catalog body unparseable: {error}")
        result["object_structures"] = fallback
        return result
    names = parse_object_structure_catalog(payload)
    seed_only = False
    if not names:
        result["source"] = "seed-fallback"
        result["notes"].append("catalog returned no member names; using documented seed")
        names = [item["name"] for item in seed_object_structures()]
        seed_only = True
    seed_by_name = {item["name"].lower(): item for item in seed_object_structures()}
    ordered: list[dict[str, Any]] = []
    for name in names:
        seed = seed_by_name.get(name.lower())
        resource = seed["resource"] if seed else normalize_resource(name)
        ordered.append(
            {
                "name": name,
                "resource": resource,
                "status": "documented" if seed_only else "verified",
            }
        )
    result["object_structures"] = ordered
    return result


def describe_object_structure(
    client: Any,
    name: str,
    resource: str,
    *,
    base_status: str = "documented",
    verify_detail: bool = False,
) -> dict[str, Any]:
    """GET one collection record and optionally one same-origin detail record.

    The detail mode is intentionally one-level and one-record only. It never
    follows ``oslc:nextPage`` or any collection reference found in the detail
    payload.
    """
    scope_clause = scope_clause_for(name) if verify_detail else None
    path = minimal_object_query_with_select(
        name,
        scope_clause,
        DETAIL_COLLECTION_SELECT if verify_detail else None,
    )
    notes: list[str] = []
    pagination: dict[str, Any] = {}
    members: list[Mapping[str, Any]] = []
    status = base_status
    access = "unknown"
    verified_at: str | None = None
    scope: dict[str, Any] = {}
    if scope_clause:
        scope = {
            "field": "siteid",
            "value": DEFAULT_SITE_ID,
            "status": "PRIOR_LIVE_QUERY",
            "evidence": "MX-006R used this BSR-scoped clause and received a bounded response; detail field evidence remains required.",
        }
    detail: dict[str, Any] = {
        "attempted": False,
        "collection_records": 0,
        "detail_records": 0,
        "maximum_dereference_depth": 1,
        "pagination_followed": False,
    }
    detail_fields: list[str] = []
    detail_types: dict[str, str] = {}
    detail_metadata: list[str] = []
    detail_primary_key: str | Mapping[str, str] | None = None
    detail_relationships: list[str] = []
    diagnostics: dict[str, Any] = {}
    try:
        http_status, _headers, body = client.request("GET", path)
    except DiscoveryError as error:
        notes.append(f"describe GET failed: {error}")
        record = object_structure_record(
            name,
            resource,
            status=base_status,
            access="error",
            notes=notes,
            scope=scope,
            detail_dereference=detail,
            endpoint=path,
        )
        validate_object_structure_record(record)
        return record
    access = f"http_{http_status}"
    if 200 <= http_status < 300:
        status = "verified"
        verified_at = now_utc()
        try:
            payload = parse_payload(body)
        except DiscoveryError as error:
            notes.append(f"describe body unparseable: {error}")
            payload = None
        if payload is not None:
            members = oslc_members(payload)[:1]
            detail["collection_records"] = len(members)
            pagination = oslc_pagination_info(payload)
            if not members:
                notes.append("response had no OSLC members; structure not sampled")
            elif verify_detail:
                member = members[0]
                if is_pure_resource_link_member(member):
                    detail["attempted"] = True
                    link = resource_link(member)
                    try:
                        base_url = getattr(getattr(client, "config", None), "base_url", "")
                        resolved = resolve_same_origin_url(str(base_url), str(link))
                        detail["resource_path"] = safe_resource_path(resolved)
                        detail_status, _detail_headers, detail_body = client.request("GET", resolved)
                        detail["http_status"] = detail_status
                        if 200 <= detail_status < 300:
                            detail["detail_records"] = 1
                            detail["status"] = "VERIFIED"
                            detail_payload = parse_payload(detail_body)
                            if not isinstance(detail_payload, Mapping):
                                notes.append("detail GET returned a non-object JSON payload")
                            else:
                                business, detail_metadata = normalize_detail_record(detail_payload)
                                detail_fields = list(business)
                                detail_types = detail_field_types(business)
                                detail_primary_key = primary_key_evidence(detail_fields)
                                detail_relationships = relationship_evidence(detail_fields)
                        else:
                            detail["status"] = "UNKNOWN"
                            detail["error"] = error_diagnostics(detail_status, detail_body)
                            notes.append(f"detail GET returned HTTP {detail_status}")
                    except DiscoveryError as error:
                        detail["status"] = "BLOCKED"
                        notes.append(f"detail dereference blocked: {error}")
                else:
                    detail["status"] = "INLINE_BUSINESS_RECORD"
                    business, detail_metadata = normalize_detail_record(member)
                    detail_fields = list(business)
                    detail_types = detail_field_types(business)
                    detail_primary_key = primary_key_evidence(detail_fields)
                    detail_relationships = relationship_evidence(detail_fields)
                    notes.append("inline business member used; no detail GET was necessary")
    elif http_status == 403:
        status = "forbidden"
    else:
        notes.append(f"describe GET returned HTTP {http_status}")
        diagnostics = error_diagnostics(http_status, body)
    if verify_detail and detail_fields:
        detail["fields"] = detail_fields[:100]
        detail["field_types"] = detail_types
        detail["metadata_fields"] = detail_metadata[:100]
    record = object_structure_record(
        name,
        resource,
        members=[] if verify_detail and detail_fields else members,
        pagination=pagination,
        status=status,
        access=access,
        verified_at=verified_at,
        notes=notes,
        scope=scope,
        detail_dereference=detail,
        field_types=detail_types,
        metadata_fields=detail_metadata,
        primary_key=detail_primary_key,
        http_diagnostics=diagnostics,
        endpoint=path,
    )
    if verify_detail and detail_fields:
        record["important_fields"] = detail_fields[:100]
        record["field_candidates"] = [f for f in detail_fields if _looks_like_identifier(f)][:50]
        record["sample"] = {field: f"<{detail_types[field]}>" for field in detail_fields}
        record["relationships"] = detail_relationships
    validate_object_structure_record(record)
    return record


def filter_object_structures(
    items: list[Mapping[str, Any]], scope: str | None, resources: list[str]
) -> list[Mapping[str, Any]]:
    requested = {normalize_resource(item) for item in resources}
    if scope == "reliability-core":
        requested |= DEFAULT_SCOPE
    if not requested:
        return list(items)
    return [item for item in items if normalize_resource(str(item["resource"])) in requested]


def discover_oslc(
    client: Any,
    output_dir: Path,
    scope: str | None,
    resources: list[str],
    oslc_root: str = OSLC_CATALOG_ROOT,
    *,
    verify_detail: bool = False,
) -> list[dict[str, Any]]:
    """Enumerate and describe OSLC object structures; write per-object catalogs."""
    enumeration = enumerate_object_structures(client, oslc_root)
    selected = filter_object_structures(enumeration["object_structures"], scope, resources)
    if not selected and resources:
        # The authenticated catalog endpoint may reject a catalog query while
        # an explicitly catalogued resource remains safely reachable. This is
        # an allowlisted target handoff, not name/path brute force.
        explicit: list[dict[str, str]] = []
        for requested in resources:
            candidate = str(requested).upper()
            if candidate in MX006B_EXPLICIT_TARGETS:
                explicit.append({"name": candidate, "resource": normalize_resource(candidate), "status": "documented"})
        selected = explicit
        if selected:
            enumeration["notes"].append("catalog selection used explicit MX-006B allowlisted targets")
    objects_dir = output_dir / "discovery" / "objects"
    summary: list[dict[str, Any]] = []
    discovered: list[dict[str, Any]] = []
    server_error_count = 0
    for item in selected:
        record = describe_object_structure(
            client,
            str(item["name"]),
            str(item["resource"]),
            base_status=str(item["status"]),
            verify_detail=verify_detail,
        )
        record["catalog_source"] = enumeration["source"]
        record["notes"] = [*record["notes"], *enumeration["notes"]]
        observed_statuses: list[int] = []
        access = record.get("access")
        if isinstance(access, str) and access.startswith("http_"):
            try:
                observed_statuses.append(int(access.removeprefix("http_")))
            except ValueError:
                pass
        detail_status = record.get("detail_dereference", {}).get("http_status")
        if isinstance(detail_status, int):
            observed_statuses.append(detail_status)
        if 429 in observed_statuses:
            raise DiscoveryError("HTTP 429 encountered during bounded Maximo verification; stopping without retry")
        server_error_count += sum(1 for observed in observed_statuses if isinstance(observed, int) and 500 <= observed < 600)
        if server_error_count >= 2:
            raise DiscoveryError("repeated HTTP 5xx responses during bounded Maximo verification; stopping live run")
        write_json(objects_dir / f"{safe_filename(str(item['name']))}.json", record)
        discovered.append(record)
        summary.append(
            {
                "name": record["object_structure"],
                "resource": record["resource"],
                "endpoint": record["endpoint"],
                "status": record["status"],
                "access": record["access"],
                "field_count": len(record["important_fields"]),
                "detail_status": record.get("detail_dereference", {}).get("status"),
                "verified_at": record["verified_at"],
            }
        )
    catalog = {
        "system": "maximo",
        "catalog_version": 3 if verify_detail else 2,
        "source": enumeration["source"],
        "last_updated": now_utc(),
        "notes": enumeration["notes"],
        "object_structures": summary,
    }
    write_json(output_dir / "discovery" / "object-structures.json", catalog)
    return discovered


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate_endpoint_record(record: Mapping[str, Any]) -> None:
    required = {"resource", "endpoint", "method", "status"}
    missing = required - set(record)
    if missing:
        raise DiscoveryError("endpoint record missing required fields: " + ", ".join(sorted(missing)))
    if record["method"] not in READ_ONLY_METHODS:
        raise DiscoveryError(f"endpoint record contains non-read-only method: {record['method']}")
    if record["status"] not in {"unknown", "documented", "verified", "forbidden", "deprecated"}:
        raise DiscoveryError(f"invalid endpoint status: {record['status']}")
    if record["status"] == "verified" and not record.get("verified_at"):
        raise DiscoveryError("verified endpoint record must have verified_at")
    if contains_sensitive_key(record):
        raise DiscoveryError("endpoint record contains a sensitive field name")


def contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(SENSITIVE_KEY.search(str(key)) or contains_sensitive_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_sensitive_key(item) for item in value)
    return False


def write_discovery_catalogs(oas: Mapping[str, Any], selected: list[dict[str, Any]], catalog_root: Path) -> None:
    catalog_root.mkdir(parents=True, exist_ok=True)
    records = [endpoint_record(entry) for entry in selected]
    for record in records:
        validate_endpoint_record(record)
    write_json(catalog_root / "endpoints.json", {"system": "maximo", "catalog_version": 2, "last_updated": now_utc(), "resources": records})
    write_json(catalog_root / "capabilities.json", capability_record(oas, selected))
    write_json(catalog_root / "object-structures.json", object_structures(selected))


def discover_oas(oas: Mapping[str, Any], output_dir: Path, scope: str | None, resources: list[str], catalog_root: Path | None = None) -> list[dict[str, Any]]:
    selected = select_entries(operation_entries(oas), scope, resources)
    write_discovery_catalogs(oas, selected, catalog_root or output_dir / "discovery")
    return selected


def parse_payload(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        if yaml is None:
            raise DiscoveryError("sample is not JSON and PyYAML is unavailable")
        value = yaml.safe_load(raw.decode("utf-8"))
        if value is None:
            raise DiscoveryError("empty sample")
        return value


def top_level_fields(value: Any) -> list[str]:
    if isinstance(value, Mapping):
        return [str(key) for key in value if not SENSITIVE_KEY.search(str(key)) and not PERSONAL_KEY.search(str(key))]
    if isinstance(value, list) and value and isinstance(value[0], Mapping):
        return top_level_fields(value[0])
    return []


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_-]+", "_", value.lower()).strip("_")
    return cleaned or "unknown"


def verify_samples(client: ReadOnlyClient, entries: list[dict[str, Any]], output_dir: Path, catalog_root: Path | None = None) -> None:
    endpoint_path = catalog_root or output_dir / "discovery"
    endpoint_path = endpoint_path / "endpoints.json"
    catalog = json.loads(endpoint_path.read_text(encoding="utf-8"))
    by_key = {(item["resource"], item["endpoint"], item["method"]): item for item in catalog["resources"]}
    for entry in entries:
        query, missing = minimal_query(entry)
        record = by_key[(entry["resource"], entry["path"], entry["method"])]
        if missing:
            record["notes"].append("sample skipped; required path parameters need an explicitly approved value: " + ", ".join(missing))
            continue
        status, headers, body = client.request(entry["method"], url_with_query(entry["path"], query))
        record["verified_at"] = now_utc()
        record["access"] = f"http_{status}"
        record["status"] = "verified" if 200 <= status < 300 else "forbidden" if status == 403 else "unknown"
        record["notes"].append(f"sample status: HTTP {status}")
        if status < 200 or status >= 300 or entry["method"] == "HEAD":
            continue
        try:
            payload = sanitize(parse_payload(body))
        except DiscoveryError:
            record["notes"].append("sample body was not JSON/YAML; structure not saved")
            continue
        record["important_fields"] = dedupe([*record["important_fields"], *top_level_fields(payload)])
        sample_root = catalog_root / "samples" if catalog_root else output_dir / "samples"
        write_json(sample_root / f"{safe_filename(entry['resource'])}.sample.json", {"system": "maximo", "resource": entry["resource"], "endpoint": entry["path"], "method": entry["method"], "status": status, "retrieved_at": record["verified_at"], "response_structure": response_structure(payload), "sample": payload})
        validate_endpoint_record(record)
    write_json(endpoint_path, catalog)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover Maximo OAS and endpoint metadata safely")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--oas-file", type=Path, help="parse a local OpenAPI JSON/YAML file")
    source.add_argument("--fetch-oas", action="store_true", help="fetch MAXIMO_OAS_PATH with GET")
    source.add_argument(
        "--enumerate-oslc",
        action="store_true",
        help="enumerate OSLC object structures via GET /oslc/os and describe each (requires --execute)",
    )
    parser.add_argument(
        "--verify-detail",
        action="store_true",
        help="follow at most one same-origin resource link for each selected OSLC record (requires --enumerate-oslc and --execute)",
    )
    parser.add_argument("--oslc-root", default=OSLC_CATALOG_ROOT, help="OSLC service-provider catalog path")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="allow read-only business requests; form/login may authenticate only at /j_security_check",
    )
    parser.add_argument("--verify-samples", action="store_true", help="GET one minimal sample for selected operations")
    parser.add_argument("--scope", choices=["reliability-core"], help="limit discovery to reliability domains")
    parser.add_argument("--resource", action="append", default=[], help="select a resource; repeatable")
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    parser.add_argument("--dry-run", action="store_true", help="show the plan without writing or fetching")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = Config.from_environment(require_base_url=not bool(args.oas_file))
    if args.dry_run:
        source = str(args.oas_file) if args.oas_file else redact_url(urljoin(config.base_url + "/", config.oas_path.lstrip("/")))
        print(json.dumps({"source": source, "execute": False, "verify_samples": args.verify_samples, "verify_detail": args.verify_detail, "scope": args.scope, "resources": args.resource}, indent=2))
        return 0
    if args.enumerate_oslc:
        if not args.execute:
            raise DiscoveryError("OSLC enumeration requires explicit --execute")
        client = ReadOnlyClient(config)
        discovered = discover_oslc(
            client,
            args.output_dir,
            args.scope,
            args.resource,
            args.oslc_root,
            verify_detail=args.verify_detail,
        )
        verified = sum(1 for item in discovered if item["status"] == "verified")
        print(f"Discovered {len(discovered)} OSLC object structures ({verified} verified)")
        return 0
    if args.verify_detail:
        raise DiscoveryError("--verify-detail requires --enumerate-oslc")
    if args.oas_file:
        raw = args.oas_file.read_bytes()
    else:
        if not args.execute:
            raise DiscoveryError("network access requires explicit --execute")
        status, _, raw = ReadOnlyClient(config).request("GET", config.oas_path)
        if status < 200 or status >= 300:
            raise DiscoveryError(f"OAS GET returned HTTP {status}; no endpoint mapping written")
    oas = parse_document(raw)
    entries = discover_oas(oas, args.output_dir, args.scope, args.resource)
    if args.verify_samples:
        if not args.execute:
            raise DiscoveryError("sample verification requires explicit --execute")
        verify_samples(ReadOnlyClient(config), entries, args.output_dir)
    print(f"Discovered {len(entries)} read-only operations")
    if args.verify_samples:
        print("Minimal samples verified with GET-only requests")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DiscoveryError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
