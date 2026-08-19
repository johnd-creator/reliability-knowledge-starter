"""Read-only OSLC client for Maximo (GET/HEAD/OPTIONS only).

Safety mirrors maximo-knowledge discovery rules:
  * Every request is GET/HEAD/OPTIONS; anything else raises OslcError.
  * Site scope (siteid="BSR") is applied by default; the caller may override
    `maximo_site` but should keep the default unless the data is truly public.
  * Rate limiting (sleep) honors server-side limits.
  * Response size is capped.
  * Credentials are never stored or logged.

Delta sync uses the `changedate` watermark (verified on MXASSET/MXWODETAIL).
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Iterator, Mapping
from urllib.parse import quote, urlencode

import requests

from src.config import MaximoConfig

LOG = logging.getLogger(__name__)

READ_ONLY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

OSLC_MEMBER_KEYS = ("_member", "member", "oslc:member", "rdfs:member")


class OslcError(RuntimeError):
    """Raised for non-read-only requests, transport failures or bad payloads."""


def _quote(value: str) -> str:
    return quote(value, safe="")


class OslcClient:
    def __init__(self, config: MaximoConfig, session: requests.Session | None = None):
        self._config = config
        self._session = session or requests.Session()
        self._last_request = 0.0
        self._cookie = config.session_cookie
        if config.auth_mode != "none" and config.token:
            self._session.headers["Authorization"] = f"Bearer {config.token}"

    # -- low-level request ------------------------------------------------
    def request(self, method: str, path: str) -> requests.Response:
        method = method.upper()
        if method not in READ_ONLY_METHODS:
            raise OslcError(f"blocked non-read-only method for Maximo: {method}")
        delay = self._config.rate_limit_seconds - (time.monotonic() - self._last_request)
        if delay > 0:
            time.sleep(delay)
        url = path if path.startswith(("http://", "https://")) else self._config.base_url + path
        headers = {"Cookie": self._cookie} if self._cookie else None
        resp = self._session.request(method, url, headers=headers, timeout=self._config.timeout_seconds)
        self._last_request = time.monotonic()
        if len(resp.content) > self._config.max_response_bytes:
            raise OslcError(
                f"Maximo {method} {path} returned oversized body "
                f"({len(resp.content)} > {self._config.max_response_bytes} bytes)"
            )
        return resp

    def get(self, path: str) -> requests.Response:
        return self.request("GET", path)

    # -- OSLC helpers -----------------------------------------------------
    def object_path(self, object_structure: str, *, select: list[str] | None = None) -> str:
        suffix = ""
        if select:
            suffix = urlencode({"oslc.select": ",".join(select)})
        return f"{self._config.oslc_root}/{object_structure}?{suffix}" if suffix else f"{self._config.oslc_root}/{object_structure}"

    def iterate(
        self,
        object_structure: str,
        *,
        where: str | None = None,
        select: list[str] | None = None,
        order_by: str = "-changedate",
        max_pages: int = 1000,
    ) -> Iterator[Mapping[str, Any]]:
        """Paginate through an OSLC object structure (GET only)."""
        where = where or f'siteid="{self._config.site_id}"'
        params: list[tuple[str, str]] = [
            ("oslc.paging", "true"),
            ("oslc.pageSize", str(self._config.page_size)),
            ("oslc.where", where),
        ]
        if order_by:
            params.append(("oslc.orderBy", order_by))
        if select:
            params.append(("oslc.select", ",".join(select)))

        base = f"{self._config.oslc_root}/{object_structure}"
        url = f"{base}?{urlencode(params, doseq=True)}"
        pages = 0
        while url and pages < max_pages:
            pages += 1
            resp = self.get(url)
            if resp.status_code == 403 or "login" in resp.headers.get("Content-Type", ""):
                raise OslcError(f"Maximo returned HTTP {resp.status_code}; session is not authenticated")
            resp.raise_for_status()
            payload = resp.json()
            members = _extract_members(payload)
            for member in members:
                yield member
            url = _next_page_url(payload)
        if not url and not _extract_members(payload):
            LOG.debug("no results for %s; check OSLC query", object_structure)


def _extract_members(payload: Any) -> list[Mapping[str, Any]]:
    """Extract member records from an OSLC collection.

    Mirrors the verified Maximo response shape documented in maximo-knowledge:
    records live under ``_member`` (primary), with generic OSLC fallbacks.
    """
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


def _next_page_url(payload: Mapping[str, Any]) -> str | None:
    """Return the next-page URL from an OSLC response.

    Maximo nests the next-page link under ``oslc:responseInfo`` (verified in
    maximo-knowledge/CONTEXT.md); a top-level ``oslc:nextPage``/``nextPage``
    is honored as a fallback for other OSLC flavors.
    """
    if not isinstance(payload, Mapping):
        return None
    info = payload.get("oslc:responseInfo")
    info = info if isinstance(info, Mapping) else {}
    next_url = info.get("oslc:nextPage") or payload.get("oslc:nextPage") or payload.get("nextPage")
    return str(next_url) if next_url else None


# -- scalar coercion helpers (Maximo booleans are often strings) ----------
def oslc_boolean(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def oslc_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def oslc_timestamp(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    text = str(value)
    if len(text) >= 19 and text[10] == "T":
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def oslc_pop_text(member: Mapping[str, Any], key: str) -> str | None:
    value = member.get(key)
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("value") or value.get("rdf:label") or value.get("@value")
    value = str(value).strip()
    return value or None


def oslc_pop_bool(member: Mapping[str, Any], key: str) -> bool | None:
    return oslc_boolean(member.get(key))


def oslc_pop_number(member: Mapping[str, Any], key: str) -> float | None:
    return oslc_number(member.get(key))