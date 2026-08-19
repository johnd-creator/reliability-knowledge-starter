"""Read-only PI Web API client (GET/HEAD/OPTIONS only).

Safety mirrors pi-knowledge discovery rules:
  * Every request is GET/HEAD/OPTIONS; anything else raises PiClientError.
  * Rate limiting (sleep) honors server-side limits.
  * Response size is capped.
  * Credentials are never stored or logged.

Supports Basic auth (PI_USERNAME/PI_PASSWORD) and Bearer (PI_TOKEN).
"""

from __future__ import annotations

import logging
import socket
import time
from datetime import datetime, timezone
from typing import Any, Iterator, Mapping
from urllib.parse import quote, urlencode

import requests
from requests.adapters import HTTPAdapter

from src.config import PiApiConfig

LOG = logging.getLogger(__name__)

READ_ONLY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def _keepalive_socket_options() -> list[tuple[int, int, int]]:
    """TCP keepalive options so silently-dead pooled connections are detected
    (idle 60s, probe every 30s, drop after 5 failed probes) instead of
    blocking a read forever. Linux-specific constants are guarded."""
    opts = [(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)]
    if hasattr(socket, "TCP_KEEPIDLE"):
        opts.append((socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60))
    if hasattr(socket, "TCP_KEEPINTVL"):
        opts.append((socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30))
    if hasattr(socket, "TCP_KEEPCNT"):
        opts.append((socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5))
    return opts


class KeepaliveAdapter(HTTPAdapter):
    """HTTPAdapter that applies TCP keepalive to every pooled connection."""

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs["socket_options"] = _keepalive_socket_options()
        super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)


def new_session() -> requests.Session:
    """Build a Session with TCP keepalive mounted (see PiClient.__init__)."""
    session = requests.Session()
    adapter = KeepaliveAdapter(pool_connections=4, pool_maxsize=4)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class PiClientError(RuntimeError):
    """Raised for non-read-only requests, transport failures or bad payloads."""


class PiGoneError(PiClientError):
    """Raised on HTTP 410 Gone — the referenced PI Point no longer exists.

    Verified behavior on this PI deployment (2026-08-14): AF attributes keep
    their WebId, but the underlying PI Point referenced via ConfigString may
    have been deleted from the data archive. The API answers 410 with
    "PI Point not found '\\\\<server>\\<tag>'". Callers should treat these
    attributes as permanently broken (deactivate), not retry.
    """


def _quote(value: str) -> str:
    return quote(value, safe="")


def _parse_timestamp(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    text = str(value)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _coerce_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class PiClient:
    """Read-only PI Web API client."""

    def __init__(self, config: PiApiConfig, session: requests.Session | None = None):
        self._config = config
        # default session carries TCP keepalive: a pooled connection killed by
        # a network blip then raises quickly instead of hanging a read forever
        # (observed 2026-08-19: daemon stalled 2h39m on one such request)
        self._session = session or new_session()
        self._last_request = 0.0

    # -- low-level request ------------------------------------------------
    def request(self, method: str, path: str, *, params: dict | None = None) -> requests.Response:
        method = method.upper()
        if method not in READ_ONLY_METHODS:
            raise PiClientError(f"blocked non-read-only method for PI: {method}")
        delay = self._config.rate_limit_seconds - (time.monotonic() - self._last_request)
        if delay > 0:
            time.sleep(delay)
        url = path if path.startswith(("http://", "https://")) else self._config.base_url + path
        extra = self._config.auth_kwargs()
        resp = self._session.request(
            method, url, params=params, timeout=self._config.timeout_seconds,
            verify=self._config.verify_tls, **extra,
        )
        self._last_request = time.monotonic()
        if len(resp.content) > self._config.max_response_bytes:
            raise PiClientError(
                f"PI {method} {path} returned oversized body "
                f"({len(resp.content)} > {self._config.max_response_bytes} bytes)"
            )
        return resp

    def get_json(self, path: str, *, params: dict | None = None) -> dict:
        resp = self.request("GET", path, params=params)
        if resp.status_code == 401:
            raise PiClientError(f"PI returned HTTP 401; authentication failed for {path}")
        if resp.status_code == 410:
            detail = ""
            try:
                detail = resp.json().get("Errors", [""])[0]
            except Exception:
                pass
            raise PiGoneError(f"PI returned HTTP 410 Gone for {path}: {detail}")
        resp.raise_for_status()
        return resp.json()

    # -- PI Web API helpers ----------------------------------------------
    def get_snapshot(self, web_id: str) -> dict:
        """GET /streams/{webId}/value — current snapshot value."""
        return self.get_json(f"/streams/{_quote(web_id)}/value")

    def get_interpolated(
        self,
        web_id: str,
        *,
        start_time: str,
        end_time: str,
        interval: str = "1h",
        max_count: int = 5000,
    ) -> dict:
        """GET /streams/{webId}/interpolated — interpolated values for a time range."""
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "interval": interval,
            "maxCount": str(max_count),
        }
        return self.get_json(f"/streams/{_quote(web_id)}/interpolated", params=params)

    def get_recorded(
        self,
        web_id: str,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        max_count: int = 1000,
    ) -> dict:
        """GET /streams/{webId}/recorded — raw archive values."""
        params: dict[str, str] = {"maxCount": str(max_count)}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return self.get_json(f"/streams/{_quote(web_id)}/recorded", params=params)

    def iter_recorded(
        self,
        web_id: str,
        *,
        start_time: str,
        end_time: str,
        max_count: int = 1000,
        max_pages: int = 1000,
    ) -> Iterator[dict]:
        """Iterate through ALL recorded values using timestamp-cursor pagination.

        This PI deployment does NOT return ``Links.Next`` in recorded responses
        (verified 2026-08-14), so pagination advances the cursor to the last
        item's timestamp and re-queries. Boundary items repeat across pages;
        callers must treat inserts as idempotent (the store upserts by
        (attribute_id, timestamp), so duplicates are harmless).

        Safety: bounded by ``max_pages``. Each request goes through the rate
        limiter and size cap in ``request()``.
        """
        current_start = start_time
        pages = 0
        last_boundary: str | None = None
        while pages < max_pages:
            pages += 1
            payload = self.get_json(
                f"/streams/{_quote(web_id)}/recorded",
                params={
                    "startTime": current_start,
                    "endTime": end_time,
                    "maxCount": str(max_count),
                },
            )
            yield payload
            items = payload.get("Items") or []
            if len(items) < max_count:
                return  # final page — under the cap means no more data
            # Prefer server-provided Next link when present
            next_url = (payload.get("Links") or {}).get("Next")
            if next_url:
                base = self._config.base_url
                if next_url.startswith(base):
                    next_url = next_url[len(base):]
                # advance cursor from the URL's startTime if parseable, else items
                current_start = self._start_from_url(next_url) or items[-1].get("Timestamp", current_start)
                continue
            # Timestamp-cursor fallback: advance to last item's timestamp
            boundary = items[-1].get("Timestamp") if items else None
            if not boundary or boundary == last_boundary:
                return  # no progress — stop to avoid infinite loop
            last_boundary = boundary
            current_start = boundary

    def _start_from_url(self, url: str) -> str | None:
        """Extract startTime parameter from a Next link URL, if present."""
        from urllib.parse import parse_qs, urlparse

        try:
            qs = parse_qs(urlparse(url).query)
            values = qs.get("startTime")
            return values[0] if values else None
        except Exception:
            return None


# -- payload parsing helpers ---------------------------------------------------
def extract_snapshot(snapshot_payload: Mapping[str, Any], attribute_id: str, units: str | None = None):
    """Parse a PI /streams/{webId}/value response into a Snapshot domain object."""
    from src.domain.models import Snapshot

    raw_value = snapshot_payload.get("Value")
    # PI digital states may return dicts; coerce numeric values only
    value = _coerce_float(raw_value)
    good = snapshot_payload.get("Good")
    if isinstance(good, str):
        good = good.lower() in ("true", "1", "yes")
    ts = _parse_timestamp(snapshot_payload.get("Timestamp"))
    units_abbr = snapshot_payload.get("UnitsAbbreviation") or units or ""
    return Snapshot(
        attribute_id=attribute_id,
        value=value,
        value_good=good,
        units=str(units_abbr) if units_abbr else None,
        source_timestamp=ts,
        collected_at=datetime.now(timezone.utc),
    )


def extract_interpolated(payload: Mapping[str, Any], attribute_id: str) -> list:
    """Parse a PI /streams/{webId}/interpolated response into TimeseriesPoint list."""
    from src.domain.models import TimeseriesPoint

    points: list[TimeseriesPoint] = []
    for item in payload.get("Items", []) or []:
        raw = item.get("Value")
        value = _coerce_float(raw)
        good = item.get("Good")
        if isinstance(good, str):
            good = good.lower() in ("true", "1", "yes")
        ts = _parse_timestamp(item.get("Timestamp"))
        if ts is None:
            continue
        points.append(TimeseriesPoint(
            attribute_id=attribute_id,
            timestamp=ts,
            value=value,
            value_good=good,
        ))
    return points


def extract_recorded(payload: Mapping[str, Any], attribute_id: str) -> list:
    """Parse a PI /streams/{webId}/recorded response into TimeseriesPoint list.

    Same structure as interpolated: Items[] with Timestamp, Value, Good.
    """
    from src.domain.models import TimeseriesPoint

    points: list[TimeseriesPoint] = []
    for item in payload.get("Items", []) or []:
        raw = item.get("Value")
        value = _coerce_float(raw)
        good = item.get("Good")
        if isinstance(good, str):
            good = good.lower() in ("true", "1", "yes")
        ts = _parse_timestamp(item.get("Timestamp"))
        if ts is None:
            continue
        points.append(TimeseriesPoint(
            attribute_id=attribute_id,
            timestamp=ts,
            value=value,
            value_good=good,
        ))
    return points
