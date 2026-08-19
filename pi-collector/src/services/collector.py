"""Collection engine: snapshot + interpolated/recorded history from PI Web API.

Read-only against PI. Safety layers:
  * Rate limiting + size cap (PiClient)
  * Circuit breaker: max requests per session, max consecutive errors
  * Time-window chunking: long ranges split into N-day windows
  * Off-hours gate: heavy backfill only during configured off-hours
  * Resume capability: per-attribute cursor tracking
  * Pause between attributes: extra cooldown to protect PI server
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from src.adapters.pi.client import (
    PiClient,
    PiClientError,
    PiGoneError,
    extract_interpolated,
    extract_recorded,
    extract_snapshot,
)
from src.config import CollectSafetyConfig
from src.domain.models import AttributeRegistration
from src.repositories.store import CollectorStore

LOG = logging.getLogger(__name__)


class CircuitBreakerError(RuntimeError):
    """Raised when the circuit breaker trips (too many requests or errors)."""


@dataclass
class CollectStats:
    scope: str
    attributes_seen: int = 0
    rows_collected: int = 0
    errors: int = 0
    requests_made: int = 0
    chunks_processed: int = 0
    aborted: bool = False
    abort_reason: str = ""
    deactivated_attributes: list = field(default_factory=list)
    attributes_skipped: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None

    def summary(self) -> str:
        status = f"ABORTED ({self.abort_reason})" if self.aborted else "complete"
        extra = f", {len(self.deactivated_attributes)} deactivated" if self.deactivated_attributes else ""
        skipped = f", {self.attributes_skipped} skipped (already downloaded)" if self.attributes_skipped else ""
        return (
            f"{self.scope}: {self.rows_collected} rows, {self.requests_made} requests, "
            f"{self.errors} errors, {self.attributes_seen} attributes"
            f"{skipped}{extra} - {status}"
        )


def _chunk_time_range(start: datetime, end: datetime, chunk_days: int) -> list[tuple[datetime, datetime]]:
    """Split [start, end] into N-day chunks. Returns list of (chunk_start, chunk_end)."""
    chunks: list[tuple[datetime, datetime]] = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=chunk_days), end)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end
    return chunks


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _interval_to_timedelta(interval: str) -> timedelta | None:
    """Parse a PI interpolation interval ("30s", "5m", "1h", "1d", "1w")."""
    interval = interval.strip()
    units = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    for unit, kwarg in units.items():
        if interval.endswith(unit):
            try:
                return timedelta(**{kwarg: int(interval[:-1])})
            except ValueError:
                return None
    return None


class CollectorService:
    """Collects PI time-series data into the collector Postgres store."""

    def __init__(
        self,
        client: PiClient,
        store: CollectorStore,
        safety: CollectSafetyConfig | None = None,
    ):
        self._client = client
        self._store = store
        self._safety = safety or CollectSafetyConfig()

    def _check_circuit_breaker(self, stats: CollectStats, consecutive_errors: int) -> bool:
        """Return True if circuit breaker has tripped (should abort)."""
        if stats.requests_made >= self._safety.max_requests_per_session:
            stats.aborted = True
            stats.abort_reason = (
                f"max_requests_per_session reached ({self._safety.max_requests_per_session})"
            )
            return True
        if consecutive_errors >= self._safety.max_consecutive_errors:
            stats.aborted = True
            stats.abort_reason = (
                f"max_consecutive_errors reached ({self._safety.max_consecutive_errors})"
            )
            return True
        return False

    def collect_snapshots(self, attributes: list[AttributeRegistration] | None = None) -> CollectStats:
        """Fetch current snapshot value for every active (or given) attribute.

        Attributes whose PI Point is gone (HTTP 410) are deactivated in the
        registry so they are excluded from future runs — the reference is
        permanently broken (verified 2026-08-14: AF keeps the attribute but the
        underlying PI Point was deleted from the data archive).
        """
        if attributes is None:
            attributes = self._store.list_active_attributes()
        stats = CollectStats(scope="snapshot")
        deactivated: list[str] = []
        LOG.info("snapshot collection: %d attributes", len(attributes))

        for attr in attributes:
            stats.attributes_seen += 1
            try:
                payload = self._client.get_snapshot(attr.web_id)  # type: ignore[arg-type]
                snap = extract_snapshot(payload, attr.attribute_id, units=attr.unit_of_measure)
                self._store.upsert_snapshot(snap)
                stats.rows_collected += 1
                stats.requests_made += 1
            except PiGoneError as error:
                stats.errors += 1
                deactivated.append(attr.attribute_id)
                self._store.deactivate_attribute(attr.attribute_id)
                LOG.warning(
                    "snapshot 410 GONE for %s (%s) — deactivated in registry: %s",
                    attr.attribute_id, attr.business_name, error,
                )
            except (PiClientError, Exception) as error:  # noqa: BLE001
                stats.errors += 1
                LOG.warning("snapshot failed for %s (%s): %s", attr.attribute_id, attr.business_name, error)

        stats.finished_at = datetime.now(timezone.utc)
        self._store.set_cursor("snapshot", stats.rows_collected)
        self._store.record_run(stats)
        if deactivated:
            stats.deactivated_attributes = deactivated
        LOG.info("snapshot collection done: %d OK, %d errors, %d deactivated, %d total",
                 stats.rows_collected, stats.errors, len(deactivated), stats.attributes_seen)
        return stats

    def backfill(
        self,
        start_time: str,
        end_time: str,
        *,
        interval: str = "1h",
        attributes: list[AttributeRegistration] | None = None,
        attribute_id: str | None = None,
        skip_downloaded: bool = True,
    ) -> CollectStats:
        """Fetch interpolated history for active attributes within a time range.

        Skip-downloaded: when enabled (default), the per-attribute start is
        clamped to its (attribute_id, interval) watermark in
        pi_backfill_progress minus one interval of margin (the upsert dedups
        the overlap, and the boundary value gets refreshed). An attribute
        whose watermark already covers the end time is skipped entirely —
        zero PI requests. Use skip_downloaded=False to force a full re-download
        (e.g. to fill interior gaps or repair bad data).
        """
        if attributes is None:
            attributes = self._store.list_active_attributes()
        if attribute_id:
            attributes = [a for a in attributes if a.attribute_id == attribute_id]
        stats = CollectStats(scope=f"backfill:{interval}")
        LOG.info("backfill %s..%s @ %s: %d attributes (skip_downloaded=%s)",
                 start_time, end_time, interval, len(attributes), skip_downloaded)

        start_dt = self._parse_pi_time(start_time)
        end_dt = self._parse_pi_time(end_time)
        if start_dt is None or end_dt is None:
            stats.aborted = True
            stats.abort_reason = (
                f"could not parse time range: start={start_time}, end={end_time}"
            )
            stats.finished_at = datetime.now(timezone.utc)
            self._store.record_run(stats)
            return stats

        step = _interval_to_timedelta(interval)
        watermarks: dict = {}
        if skip_downloaded and step is not None:
            watermarks = self._store.get_backfill_progress(interval)

        consecutive_errors = 0
        for attr in attributes:
            if self._check_circuit_breaker(stats, consecutive_errors):
                break
            stats.attributes_seen += 1

            effective_start = start_dt
            watermark = watermarks.get(attr.attribute_id)
            if watermark is not None and step is not None:
                # one interval of margin: refresh the boundary value
                effective_start = max(start_dt, watermark - step)
            if effective_start >= end_dt:
                stats.attributes_skipped += 1
                LOG.info("backfill skip %s: watermark %s covers %s..%s",
                         attr.business_name, watermark, start_time, end_time)
                continue

            try:
                payload = self._client.get_interpolated(
                    attr.web_id,  # type: ignore[arg-type]
                    start_time=_iso(effective_start),
                    end_time=_iso(end_dt),
                    interval=interval,
                )
                stats.requests_made += 1
                points = extract_interpolated(payload, attr.attribute_id)
                inserted = self._store.bulk_insert_timeseries(points)
                stats.rows_collected += inserted
                consecutive_errors = 0
                if points and skip_downloaded:
                    last_ts = max(p.timestamp for p in points)
                    self._store.record_backfill_progress(
                        attr.attribute_id, interval, last_ts
                    )
                LOG.info("backfill %s: %d points (%s)", attr.business_name, inserted, attr.unit_of_measure or "")
            except (PiClientError, Exception) as error:  # noqa: BLE001
                stats.errors += 1
                consecutive_errors += 1
                LOG.warning("backfill failed for %s (%s): %s", attr.attribute_id, attr.business_name, error)

        stats.finished_at = datetime.now(timezone.utc)
        self._store.set_cursor(stats.scope, stats.rows_collected)
        self._store.record_run(stats)
        LOG.info("backfill done: %s", stats.summary())
        return stats

    def backfill_recorded(
        self,
        start_time: str,
        end_time: str,
        *,
        attributes: list[AttributeRegistration] | None = None,
        attribute_id: str | None = None,
        max_count_per_page: int = 5000,
        enforce_off_hours: bool = True,
        skip_downloaded: bool = True,
    ) -> CollectStats:
        """Download ALL raw recorded values for active attributes within a time range.

        This is the heaviest operation. Safety mechanisms:

        1. **Off-hours gate**: if ``enforce_off_hours`` and outside the configured
           off-hours window, the run aborts immediately with a clear message.
           Override with ``enforce_off_hours=False`` (not recommended for production).

        2. **Time-window chunking**: the full range is split into N-day chunks
           (default 7) so each PI request covers a bounded period. This keeps
           individual responses small and resumable.

        3. **Circuit breaker**: after ``max_requests_per_session`` API calls or
           ``max_consecutive_errors`` failures in a row, the run aborts. Partial
           progress is already committed to the DB — re-running resumes from
           where it left off (upsert by attribute_id + timestamp).

        4. **Pause between attributes**: extra cooldown (default 2s) between each
           attribute to give the PI server breathing room.

        5. **Pagination**: within each chunk, PI's ``Links.Next`` is followed until
           all pages are consumed. Bounded by ``max_pages`` (1000) per chunk.

        Args:
            start_time: PI time expression or ISO-8601 (e.g. "2024-01-01T00:00:00Z")
            end_time: PI time expression or ISO-8601 (e.g. "*" for now)
            attribute_id: optional single attribute_id to limit scope
            max_count_per_page: PI maxCount per request (default 5000)
            enforce_off_hours: if True, abort outside off-hours window
        """
        # --- off-hours gate ---
        if enforce_off_hours and not self._safety.is_off_hours():
            stats = CollectStats(scope="backfill_recorded", aborted=True)
            now = datetime.now()
            stats.abort_reason = (
                f"outside off-hours window "
                f"({self._safety.off_hours_start:02d}:00-{self._safety.off_hours_end:02d}:00, "
                f"weekend={self._safety.off_hours_weekend}); current time {now.strftime('%H:%M %A')}. "
                f"Re-run during off-hours or use --force to override."
            )
            LOG.warning("backfill_recorded ABORTED: %s", stats.abort_reason)
            stats.finished_at = datetime.now(timezone.utc)
            self._store.record_run(stats)
            return stats

        # --- parse time range into chunks ---
        start_dt = self._parse_pi_time(start_time)
        end_dt = self._parse_pi_time(end_time)
        if start_dt is None or end_dt is None:
            stats = CollectStats(scope="backfill_recorded", aborted=True)
            stats.abort_reason = f"could not parse time range: start={start_time}, end={end_time}"
            stats.finished_at = datetime.now(timezone.utc)
            self._store.record_run(stats)
            return stats

        chunks = _chunk_time_range(start_dt, end_dt, self._safety.chunk_days)
        LOG.info(
            "backfill_recorded %s..%s: %d chunks of %d days, off_hours=%s, skip_downloaded=%s",
            _iso(start_dt), _iso(end_dt), len(chunks), self._safety.chunk_days,
            self._safety.is_off_hours(), skip_downloaded,
        )

        if attributes is None:
            attributes = self._store.list_active_attributes()
        if attribute_id:
            attributes = [a for a in attributes if a.attribute_id == attribute_id]

        recorded_watermarks: dict = {}
        if skip_downloaded:
            recorded_watermarks = self._store.get_backfill_progress("recorded")

        stats = CollectStats(scope="backfill_recorded")
        consecutive_errors = 0

        for attr in attributes:
            if self._check_circuit_breaker(stats, consecutive_errors):
                LOG.warning("backfill_recorded circuit breaker tripped: %s", stats.abort_reason)
                break

            stats.attributes_seen += 1

            # skip-downloaded: clamp this attribute's range to its watermark
            attr_start = start_dt
            watermark = recorded_watermarks.get(attr.attribute_id)
            if skip_downloaded and watermark is not None:
                attr_start = max(start_dt, watermark)
            if attr_start >= end_dt:
                stats.attributes_skipped += 1
                LOG.info(
                    "backfill_recorded [%d/%d] skip %s: watermark %s covers range",
                    stats.attributes_seen, len(attributes), attr.business_name, watermark,
                )
                continue

            attr_chunks = [c for c in chunks if c[1] > attr_start]
            LOG.info(
                "backfill_recorded [%d/%d] %s: %d chunks",
                stats.attributes_seen, len(attributes), attr.business_name, len(attr_chunks),
            )
            attr_points: list = []
            for chunk_start, chunk_end in attr_chunks:
                if self._check_circuit_breaker(stats, consecutive_errors):
                    break
                effective_chunk_start = max(chunk_start, attr_start)
                try:
                    for page in self._client.iter_recorded(
                        attr.web_id,  # type: ignore[arg-type]
                        start_time=_iso(effective_chunk_start),
                        end_time=_iso(chunk_end),
                        max_count=max_count_per_page,
                    ):
                        stats.requests_made += 1
                        points = extract_recorded(page, attr.attribute_id)
                        attr_points.extend(points)
                        stats.chunks_processed += 1
                    consecutive_errors = 0
                except (PiClientError, Exception) as error:  # noqa: BLE001
                    stats.errors += 1
                    consecutive_errors += 1
                    LOG.warning(
                        "backfill_recorded chunk failed for %s (%s..%s): %s",
                        attr.business_name, _iso(chunk_start), _iso(chunk_end), error,
                    )
                    if self._check_circuit_breaker(stats, consecutive_errors):
                        break

            if attr_points:
                inserted = self._store.bulk_insert_timeseries(attr_points)
                stats.rows_collected += inserted
                if skip_downloaded:
                    last_ts = max(p.timestamp for p in attr_points)
                    self._store.record_backfill_progress(
                        attr.attribute_id, "recorded", last_ts
                    )
                LOG.info(
                    "backfill_recorded %s: %d points total across %d chunks",
                    attr.business_name, inserted, len(attr_chunks),
                )

            # pause between attributes
            if self._safety.pause_between_attributes_seconds > 0:
                time.sleep(self._safety.pause_between_attributes_seconds)

        stats.finished_at = datetime.now(timezone.utc)
        self._store.set_cursor("backfill_recorded", stats.rows_collected)
        self._store.record_run(stats)
        LOG.info("backfill_recorded done: %s", stats.summary())
        return stats

    def _parse_pi_time(self, expr: str) -> datetime | None:
        """Parse a PI time expression into a datetime.

        Supports:
          * ISO-8601: "2024-01-01T00:00:00Z"
          * "*" → now
          * "*-Nd" / "*-Nh" / "*-Nm" → now minus N days/hours/minutes
        """
        expr = expr.strip()
        if expr == "*":
            return datetime.now(timezone.utc)
        if expr.startswith("*-"):
            now = datetime.now(timezone.utc)
            rest = expr[2:]
            for unit, kwarg in [("d", "days"), ("h", "hours"), ("m", "minutes"), ("w", "weeks")]:
                if rest.endswith(unit):
                    try:
                        n = int(rest[:-1])
                        return now - timedelta(**{kwarg: n})
                    except ValueError:
                        break
        try:
            return datetime.fromisoformat(expr.replace("Z", "+00:00"))
        except ValueError:
            return None
