"""AggregationService: 5-minute rolling buckets over value_final.

Port of the DAZ AggregateSensorData job, minus the KLHK push. Idempotent:
each (parameter_code, stack_id, window_start) row is upserted, and a
sync_cursor watermark prevents reprocessing completed windows. Unlike the
DAZ job, every parameter present in the readings is aggregated — the
KLHK seven-code list is not hardcoded here.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from src.config import CemsConfig
from src.repositories.store import CollectorStore

LOG = logging.getLogger(__name__)


def floor_to_interval(moment: datetime, minutes: int) -> datetime:
    """Floor a timestamp to the boundary of a fixed minute interval."""
    midnight = moment.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed_minutes = int((moment - midnight).total_seconds() // 60)
    bucket = (elapsed_minutes // minutes) * minutes
    return midnight + timedelta(minutes=bucket)


@dataclass
class AggregateStats:
    run_type: str = "aggregate"
    mode: str = "window"
    rows_seen: int = 0
    upserted: int = 0
    skipped: int = 0
    errors: int = 0
    watermark: datetime | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class AggregationService:
    def __init__(self, store: CollectorStore, config: CemsConfig):
        self._store = store
        self._config = config
        self._interval = timedelta(minutes=config.aggregation_interval_minutes)
        self._scope = f"aggregation:{config.aggregation_interval_minutes}m"

    def aggregate(self, now: datetime | None = None, force: bool = False) -> AggregateStats:
        """Aggregate the most recently completed window (cursor-guarded)."""
        moment = now or datetime.now(timezone.utc)
        window_end = floor_to_interval(moment, self._config.aggregation_interval_minutes)
        window_start = window_end - self._interval
        return self._aggregate_window(window_start, window_end, force=force)

    def backfill(
        self,
        start: datetime,
        end: datetime,
        force: bool = True,
    ) -> list[AggregateStats]:
        """Re-aggregate a range of windows (oldest first)."""
        results: list[AggregateStats] = []
        window_start = floor_to_interval(start, self._config.aggregation_interval_minutes)
        window_end = floor_to_interval(end, self._config.aggregation_interval_minutes)
        while window_start < window_end:
            results.append(
                self._aggregate_window(window_start, window_start + self._interval, force=force)
            )
            window_start += self._interval
        return results

    def _aggregate_window(
        self,
        window_start: datetime,
        window_end: datetime,
        force: bool = False,
    ) -> AggregateStats:
        stats = AggregateStats(mode=f"{self._config.aggregation_interval_minutes}m")
        try:
            cursor = self._store.get_cursor(self._scope)
            if not force and cursor is not None and window_end <= cursor:
                stats.skipped = 1
                stats.watermark = cursor
                LOG.info(
                    "window %s already aggregated (cursor=%s) — skipped",
                    window_start.isoformat(), cursor.isoformat(),
                )
                return stats
            aggregates = self._store.window_aggregate(
                window_start, window_end, stack_id=self._config.stack_id
            )
            stats.rows_seen = len(aggregates)
            stats.upserted = self._store.upsert_5min(aggregates)
            stats.watermark = window_end
            self._store.set_cursor(self._scope, window_end, stats.rows_seen)
            LOG.info(
                "aggregated %s..%s: %s windows rows upserted",
                window_start.isoformat(), window_end.isoformat(), stats.upserted,
            )
            return stats
        finally:
            stats.finished_at = datetime.now(timezone.utc)
            self._store.record_run(stats)
