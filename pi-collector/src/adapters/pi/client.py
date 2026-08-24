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
from urllib.parse import parse_qs, quote, urlparse

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
    # PI digital states and text are source values, not numeric measurements.
    # Only JSON numeric values may cross the numeric domain boundary.
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
    return None


def _infer_value_type(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, (int, float)):
        return "NUMERIC"
    if isinstance(value, Mapping):
        return "DIGITAL_STATE"
    return "TEXT"


def _origin(url: str) -> tuple[str, str, int]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("invalid PI URL")
    if parsed.username or parsed.password:
        raise ValueError("PI URL must not contain credentials")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("invalid PI URL port") from error
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    return parsed.scheme.lower(), parsed.hostname.lower(), port


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
        base_url = self._config.base_url
        if not base_url:
            raise PiClientError("PI Web API base URL is required for source operations")
        if (self._config.username is None) != (self._config.password is None):
            raise PiClientError("PI Basic auth requires both PI_USERNAME and PI_PASSWORD")
        try:
            base_origin = _origin(base_url)
        except ValueError as error:
            raise PiClientError("PI Web API base URL is invalid") from error
        if path.startswith(("http://", "https://")):
            try:
                same_origin = _origin(path) == base_origin
            except ValueError as error:
                raise PiClientError("PI absolute link rejected: invalid origin") from error
            if not same_origin:
                raise PiClientError("PI absolute link rejected: foreign origin")
            url = path
        else:
            url = base_url.rstrip("/") + (path if path.startswith("/") else f"/{path}")
        delay = self._config.rate_limit_seconds - (time.monotonic() - self._last_request)
        if delay > 0:
            time.sleep(delay)
        extra = self._config.auth_kwargs()
        try:
            resp = self._session.request(
                method, url, params=params, timeout=self._config.timeout_seconds,
                verify=self._config.verify_tls, allow_redirects=False, **extra,
            )
        except requests.exceptions.Timeout as error:
            raise PiClientError("PI request timed out") from error
        except requests.exceptions.SSLError as error:
            raise PiClientError("PI TLS verification failed") from error
        except requests.exceptions.RequestException as error:
            raise PiClientError("PI transport failure") from error
        self._last_request = time.monotonic()
        if len(resp.content) > self._config.max_response_bytes:
            raise PiClientError(
                f"PI {method} returned oversized body "
                f"({len(resp.content)} > {self._config.max_response_bytes} bytes)"
            )
        return resp

    def get_json(self, path: str, *, params: dict | None = None) -> dict:
        resp = self.request("GET", path, params=params)
        if resp.status_code == 401:
            raise PiClientError("PI returned HTTP 401; authentication failed")
        if resp.status_code == 410:
            raise PiGoneError("PI returned HTTP 410 Gone for PI resource")
        if resp.status_code >= 400:
            raise PiClientError(f"PI returned HTTP {resp.status_code} for PI resource")
        try:
            payload = resp.json()
        except (TypeError, ValueError) as error:
            raise PiClientError("PI returned invalid JSON") from error
        if not isinstance(payload, dict):
            raise PiClientError("PI returned an unexpected JSON shape")
        return payload

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

    # -- AF metadata and bounded source operations -----------------------
    def get_af_element(self, element_web_id: str) -> dict:
        """GET AF Element metadata without traversing child elements."""
        return self.get_json(f"/elements/{_quote(element_web_id)}")

    def list_af_attributes(self, element_web_id: str, *, max_count: int = 100) -> list[dict]:
        """List at most 100 direct attributes for one AF Element."""
        bounded_count = max(1, min(max_count, 100))
        payload = self.get_json(
            f"/elements/{_quote(element_web_id)}/attributes",
            params={"maxCount": str(bounded_count)},
        )
        items = payload.get("Items")
        if not isinstance(items, list):
            raise PiClientError("AF attribute response missing Items")
        if len(items) > bounded_count:
            raise PiClientError("AF attribute response exceeded bounded limit")
        if any(not isinstance(item, dict) for item in items):
            raise PiClientError("AF attribute response contained an invalid item")
        return items

    def get_af_attribute(self, attribute_web_id: str) -> dict:
        """GET one AF Attribute metadata document."""
        return self.get_json(f"/attributes/{_quote(attribute_web_id)}")

    @staticmethod
    def _related_link(metadata: Mapping[str, Any], relation: str) -> str:
        links = metadata.get("Links")
        link = links.get(relation) if isinstance(links, Mapping) else None
        if not isinstance(link, str) or not link:
            raise PiClientError(f"AF attribute metadata missing {relation} link")
        return link

    def get_af_attribute_value(self, metadata: Mapping[str, Any]) -> dict:
        """Read the current value through the AF Attribute's Value link."""
        return self.get_json(self._related_link(metadata, "Value"))

    def get_af_attribute_recorded(
        self,
        metadata: Mapping[str, Any],
        *,
        start_time: str,
        end_time: str,
        max_count: int = 20,
    ) -> dict:
        """Read bounded recorded data through the AF Attribute's link.

        The governed source boundary caps a single operation at 20 samples;
        larger extraction belongs to the existing technical collector modes.
        """
        bounded_count = max(1, min(max_count, 20))
        return self.get_json(
            self._related_link(metadata, "RecordedData"),
            params={
                "startTime": start_time,
                "endTime": end_time,
                "maxCount": str(bounded_count),
            },
        )

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
            items = payload.get("Items")
            if not isinstance(items, list):
                raise PiClientError("PI recorded response missing Items")
            if len(items) < max_count:
                return  # final page — under the cap means no more data
            # Prefer server-provided Next link when present
            next_url = (payload.get("Links") or {}).get("Next")
            if next_url:
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
        try:
            if url.startswith(("http://", "https://")):
                self._resolve_absolute_link(url)
            qs = parse_qs(urlparse(url).query)
            values = qs.get("startTime")
            return values[0] if values else None
        except PiClientError:
            raise
        except (TypeError, ValueError):
            return None

    def _resolve_absolute_link(self, url: str) -> str:
        """Validate a PI response link before it can be requested."""
        base_url = self._config.base_url
        if not base_url:
            raise PiClientError("PI Web API base URL is required for source operations")
        try:
            if _origin(url) != _origin(base_url):
                raise PiClientError("PI absolute link rejected: foreign origin")
        except ValueError as error:
            raise PiClientError("PI absolute link rejected: invalid origin") from error
        return url


# -- payload parsing helpers ---------------------------------------------------
def extract_snapshot(snapshot_payload: Mapping[str, Any], attribute_id: str, units: str | None = None):
    """Parse a PI /streams/{webId}/value response into a Snapshot domain object."""
    from src.domain.models import Snapshot

    if "Value" not in snapshot_payload:
        raise PiClientError("PI snapshot response missing Value")
    raw_value = snapshot_payload.get("Value")
    # PI digital states may return dicts; coerce numeric values only
    value = _coerce_float(raw_value)
    good = _coerce_bool(snapshot_payload.get("Good"))
    ts = _parse_timestamp(snapshot_payload.get("Timestamp"))
    units_abbr = snapshot_payload.get("UnitsAbbreviation") or snapshot_payload.get("Units") or units or ""
    return Snapshot(
        attribute_id=attribute_id,
        value=value,
        value_good=good,
        units=str(units_abbr) if units_abbr else None,
        source_timestamp=ts,
        collected_at=datetime.now(timezone.utc),
        value_type=str(snapshot_payload.get("ValueType") or _infer_value_type(raw_value)),
        value_questionable=_coerce_bool(
            snapshot_payload.get("Questionable", snapshot_payload.get("IsQuestionable"))
        ),
        value_substituted=_coerce_bool(
            snapshot_payload.get("Substituted", snapshot_payload.get("IsSubstituted"))
        ),
        value_annotated=_coerce_bool(
            snapshot_payload.get("Annotated", snapshot_payload.get("IsAnnotated"))
        ),
    )


def _history_items(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    items = payload.get("Items")
    if not isinstance(items, list):
        raise PiClientError("PI history response missing Items")
    if any(not isinstance(item, Mapping) for item in items):
        raise PiClientError("PI history response contained an invalid item")
    return items


def extract_interpolated(payload: Mapping[str, Any], attribute_id: str) -> list:
    """Parse a PI /streams/{webId}/interpolated response into TimeseriesPoint list."""
    from src.domain.models import TimeseriesPoint

    points: list[TimeseriesPoint] = []
    default_units = payload.get("UnitsAbbreviation") or payload.get("Units")
    for item in _history_items(payload):
        raw = item.get("Value")
        value = _coerce_float(raw)
        good = _coerce_bool(item.get("Good"))
        ts = _parse_timestamp(item.get("Timestamp"))
        if ts is None:
            continue
        points.append(TimeseriesPoint(
            attribute_id=attribute_id,
            timestamp=ts,
            value=value,
            value_good=good,
            units=str(item.get("UnitsAbbreviation") or item.get("Units") or default_units)
            if item.get("UnitsAbbreviation") or item.get("Units") or default_units else None,
            value_type=str(item.get("ValueType") or _infer_value_type(raw)),
            value_questionable=_coerce_bool(
                item.get("Questionable", item.get("IsQuestionable"))
            ),
            value_substituted=_coerce_bool(
                item.get("Substituted", item.get("IsSubstituted"))
            ),
            value_annotated=_coerce_bool(
                item.get("Annotated", item.get("IsAnnotated"))
            ),
        ))
    return points


def extract_recorded(payload: Mapping[str, Any], attribute_id: str) -> list:
    """Parse a PI /streams/{webId}/recorded response into TimeseriesPoint list.

    Same structure as interpolated: Items[] with Timestamp, Value, Good.
    """
    from src.domain.models import TimeseriesPoint

    points: list[TimeseriesPoint] = []
    default_units = payload.get("UnitsAbbreviation") or payload.get("Units")
    for item in _history_items(payload):
        raw = item.get("Value")
        value = _coerce_float(raw)
        good = _coerce_bool(item.get("Good"))
        ts = _parse_timestamp(item.get("Timestamp"))
        if ts is None:
            continue
        points.append(TimeseriesPoint(
            attribute_id=attribute_id,
            timestamp=ts,
            value=value,
            value_good=good,
            units=str(item.get("UnitsAbbreviation") or item.get("Units") or default_units)
            if item.get("UnitsAbbreviation") or item.get("Units") or default_units else None,
            value_type=str(item.get("ValueType") or _infer_value_type(raw)),
            value_questionable=_coerce_bool(
                item.get("Questionable", item.get("IsQuestionable"))
            ),
            value_substituted=_coerce_bool(
                item.get("Substituted", item.get("IsSubstituted"))
            ),
            value_annotated=_coerce_bool(
                item.get("Annotated", item.get("IsAnnotated"))
            ),
        ))
    return points
