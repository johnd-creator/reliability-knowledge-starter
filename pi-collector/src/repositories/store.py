"""CockpitStore: persist domain models <-> ORM rows in Postgres.

Stores only the collector's OWN normalized time-series data.
Never writes to PI production.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.domain.models import AttributeRegistration, Snapshot, TimeseriesPoint
from src.repositories.database import Database
from src.repositories import models as orm


# Local timezone used to bucket daily collector activity. Overnight runs
# (22:00-06:00 WIB) would land on the wrong UTC date; bucket by wall-clock
# day the operator actually saw.
ACTIVITY_TZ = ZoneInfo("Asia/Jakarta")


def accumulate_run_coverage(
    runs: list[tuple[datetime, datetime | None]], tz=ACTIVITY_TZ, data_buckets=()
) -> list[dict]:
    """Aggregate runs + collected data into per-day coverage for the activity graph.

    An hour of a local day is COVERED when either:
      * the collector process was running during it (runs: started_at..finished_at),
        e.g. a snapshot daemon — a single 8-minute session covers 1 hour; or
      * at least one time-series data point exists in it (data_buckets: naive
        local hour-truncated datetimes). This is what makes BACKFILL count: a
        backfill run today that fills hourly history for a past day lights
        that past day up.

    Full green (24 hours) therefore means "every hour of that day has
    collected data or a running collector".

    Returns ``[{"date": "YYYY-MM-DD", "runs": int, "hours_covered": int}]``
    sorted by date.
    """
    from datetime import timedelta

    runs_per_day: dict[str, int] = {}
    covered: dict[str, set[int]] = {}
    for started_at, finished_at in runs:
        end = finished_at or started_at
        start_local = started_at.astimezone(tz)
        end_local = end.astimezone(tz)
        day_key = start_local.date().isoformat()
        runs_per_day[day_key] = runs_per_day.get(day_key, 0) + 1
        # mark every local hour bucket the run touched (cap for safety)
        bucket = start_local.replace(minute=0, second=0, microsecond=0)
        final_bucket = end_local.replace(minute=0, second=0, microsecond=0)
        for _ in range(168):  # max one-week span per run
            cur_day = bucket.date().isoformat()
            covered.setdefault(cur_day, set()).add(bucket.hour)
            if bucket >= final_bucket:
                break
            bucket += timedelta(hours=1)

    # hours covered by collected data (e.g. backfilled history)
    for data_bucket in data_buckets:
        day_key = data_bucket.date().isoformat()
        covered.setdefault(day_key, set()).add(data_bucket.hour)

    return [
        {
            "date": day,
            "runs": runs_per_day.get(day, 0),
            "hours_covered": len(covered.get(day, ())),
        }
        for day in sorted(set(runs_per_day) | set(covered))
    ]


class CollectorStore:
    def __init__(self, db: Database):
        self._db = db

    # -- registry ---------------------------------------------------------
    def upsert_registration(self, reg: AttributeRegistration) -> None:
        with self._db.session() as session:
            row = session.get(orm.AttributeRegistryOrm, reg.attribute_id)
            if row is None:
                row = orm.AttributeRegistryOrm(attribute_id=reg.attribute_id)
            row.site = reg.site
            row.unit = reg.unit
            row.equipment = reg.equipment
            row.parameter = reg.parameter
            row.business_name = reg.business_name
            row.position = reg.position
            row.unit_of_measure = reg.unit_of_measure
            row.web_id = reg.web_id
            row.af_path = reg.af_path
            row.is_active = True
            row.registered_at = datetime.now(timezone.utc)
            session.add(row)
            session.commit()

    def list_active_attributes(self) -> list[AttributeRegistration]:
        with self._db.session() as session:
            rows = (
                session.execute(
                    select(orm.AttributeRegistryOrm).where(orm.AttributeRegistryOrm.is_active == True)  # noqa: E712
                )
                .scalars()
                .all()
            )
            return [
                AttributeRegistration(
                    attribute_id=r.attribute_id,
                    site=r.site,
                    unit=r.unit,
                    equipment=r.equipment,
                    parameter=r.parameter,
                    business_name=r.business_name,
                    position=r.position,
                    unit_of_measure=r.unit_of_measure,
                    web_id=r.web_id,
                    af_path=r.af_path,
                )
                for r in rows
            ]

    def list_attribute_ids_by_equipment(self, equipment: str) -> list[str]:
        with self._db.session() as session:
            rows = (
                session.execute(
                    select(orm.AttributeRegistryOrm.attribute_id).where(
                        orm.AttributeRegistryOrm.equipment == equipment
                    )
                )
                .scalars()
                .all()
            )
            return list(rows)

    def deactivate_attribute(self, attribute_id: str) -> None:
        """Mark an attribute inactive (e.g. its PI Point was deleted — 410 Gone)."""
        with self._db.session() as session:
            row = session.get(orm.AttributeRegistryOrm, attribute_id)
            if row is not None and row.is_active:
                row.is_active = False
                session.add(row)
                session.commit()

    def prune_not_in(self, active_ids: list[str]) -> int:
        """Deactivate registry rows whose attribute_id is NOT in the given list.

        Used after load-registry to sync the collector registry with the
        pi-knowledge mapping (entries removed or marked broken upstream).
        Returns the number of rows deactivated.
        """
        keep = set(active_ids)
        deactivated = 0
        with self._db.session() as session:
            rows = (
                session.execute(
                    select(orm.AttributeRegistryOrm).where(orm.AttributeRegistryOrm.is_active == True)  # noqa: E712
                )
                .scalars()
                .all()
            )
            for row in rows:
                if row.attribute_id not in keep:
                    row.is_active = False
                    deactivated += 1
            if deactivated:
                session.commit()
        return deactivated

    # -- snapshots --------------------------------------------------------
    def upsert_snapshot(self, snap: Snapshot) -> None:
        with self._db.session() as session:
            row = session.get(orm.SnapshotOrm, snap.attribute_id)
            if row is None:
                row = orm.SnapshotOrm(attribute_id=snap.attribute_id)
            row.value = snap.value
            row.value_good = snap.value_good
            row.units = snap.units
            row.value_type = snap.value_type
            row.value_questionable = snap.value_questionable
            row.value_substituted = snap.value_substituted
            row.value_annotated = snap.value_annotated
            row.source_timestamp = snap.source_timestamp
            row.collected_at = snap.collected_at or datetime.now(timezone.utc)
            session.add(row)
            session.commit()

    def get_snapshot(self, attribute_id: str) -> Snapshot | None:
        with self._db.session() as session:
            row = session.get(orm.SnapshotOrm, attribute_id)
            if row is None:
                return None
            return Snapshot(
                attribute_id=row.attribute_id,
                value=row.value,
                value_good=row.value_good,
                units=row.units,
                source_timestamp=row.source_timestamp,
                collected_at=row.collected_at,
                value_type=row.value_type,
                value_questionable=row.value_questionable,
                value_substituted=row.value_substituted,
                value_annotated=row.value_annotated,
            )

    def list_snapshots(self, equipment: str | None = None, limit: int = 500) -> list[Snapshot]:
        with self._db.session() as session:
            stmt = select(orm.SnapshotOrm)
            if equipment:
                stmt = stmt.join(
                    orm.AttributeRegistryOrm,
                    orm.SnapshotOrm.attribute_id == orm.AttributeRegistryOrm.attribute_id,
                ).where(orm.AttributeRegistryOrm.equipment == equipment)
            stmt = stmt.limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [
                Snapshot(
                    attribute_id=r.attribute_id,
                    value=r.value,
                    value_good=r.value_good,
                    units=r.units,
                    source_timestamp=r.source_timestamp,
                    collected_at=r.collected_at,
                    value_type=r.value_type,
                    value_questionable=r.value_questionable,
                    value_substituted=r.value_substituted,
                    value_annotated=r.value_annotated,
                )
                for r in rows
            ]

    # -- timeseries -------------------------------------------------------
    def bulk_insert_timeseries(self, points: list[TimeseriesPoint], *, batch_size: int = 1000) -> int:
        """Bulk upsert time-series points using Postgres ON CONFLICT.

        Points are deduplicated by (attribute_id, timestamp) first — cursor
        pagination repeats boundary items across pages, and PI archives can
        hold multiple events at the same timestamp. Without dedup, Postgres
        rejects the batch ("cannot affect row a second time").

        Rows are inserted in batches to stay under Postgres's 65535 bind-parameter
        limit (each row binds 5 columns; 1000 rows = 5000 params).
        """
        if not points:
            return 0
        deduped: dict[tuple[str, datetime], TimeseriesPoint] = {}
        for p in points:
            deduped[(p.attribute_id, p.timestamp)] = p  # last occurrence wins
        now = datetime.now(timezone.utc)
        rows = [
            {
                "attribute_id": p.attribute_id,
                "timestamp": p.timestamp,
                "value": p.value,
                "value_good": p.value_good,
                "units": p.units,
                "value_type": p.value_type,
                "value_questionable": p.value_questionable,
                "value_substituted": p.value_substituted,
                "value_annotated": p.value_annotated,
                "collected_at": now,
            }
            for p in deduped.values()
        ]
        inserted = 0
        with self._db.engine.begin() as conn:
            for offset in range(0, len(rows), batch_size):
                batch = rows[offset : offset + batch_size]
                stmt = pg_insert(orm.TimeseriesOrm).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["attribute_id", "timestamp"],
                    set_={
                        "value": stmt.excluded.value,
                        "value_good": stmt.excluded.value_good,
                        "units": stmt.excluded.units,
                        "value_type": stmt.excluded.value_type,
                        "value_questionable": stmt.excluded.value_questionable,
                        "value_substituted": stmt.excluded.value_substituted,
                        "value_annotated": stmt.excluded.value_annotated,
                        "collected_at": stmt.excluded.collected_at,
                    },
                )
                conn.execute(stmt)
                inserted += len(batch)
        return inserted

    def query_timeseries(
        self,
        attribute_id: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 10000,
    ) -> list[TimeseriesPoint]:
        with self._db.session() as session:
            stmt = select(orm.TimeseriesOrm).where(orm.TimeseriesOrm.attribute_id == attribute_id)
            if start:
                stmt = stmt.where(orm.TimeseriesOrm.timestamp >= start)
            if end:
                stmt = stmt.where(orm.TimeseriesOrm.timestamp <= end)
            stmt = stmt.order_by(orm.TimeseriesOrm.timestamp.asc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [
                TimeseriesPoint(
                    attribute_id=r.attribute_id,
                    timestamp=r.timestamp,
                    value=r.value,
                    value_good=r.value_good,
                    units=r.units,
                    value_type=r.value_type,
                    value_questionable=r.value_questionable,
                    value_substituted=r.value_substituted,
                    value_annotated=r.value_annotated,
                )
                for r in rows
            ]

    def timeseries_count(self, attribute_id: str | None = None) -> int:
        with self._db.session() as session:
            stmt = select(func.count()).select_from(orm.TimeseriesOrm)
            if attribute_id:
                stmt = stmt.where(orm.TimeseriesOrm.attribute_id == attribute_id)
            return session.execute(stmt).scalar() or 0

    def heatmap(self, attribute_id: str, *, days: int = 365) -> list[dict]:
        """Return daily data-point counts for the last N days (GitHub-style heatmap).

        Returns a list of {"date": "YYYY-MM-DD", "count": int} dicts.
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        with self._db.session() as session:
            stmt = (
                select(
                    func.date_trunc("day", orm.TimeseriesOrm.timestamp).label("day"),
                    func.count().label("count"),
                )
                .where(
                    orm.TimeseriesOrm.attribute_id == attribute_id,
                    orm.TimeseriesOrm.timestamp >= cutoff,
                )
                .group_by("day")
                .order_by("day")
            )
            rows = session.execute(stmt).all()
            return [{"date": r.day.date().isoformat(), "count": r.count} for r in rows]

    def last_snapshot_cycle(self) -> tuple[datetime | None, float | None]:
        """Return (finished_at, duration_seconds) of the latest snapshot run.

        Powers the /schedule endpoint: a snapshot cycle takes minutes
        (rate-limited at 1 req/s), so the real daemon period is
        duration + interval — not the bare interval.
        """
        with self._db.session() as session:
            row = session.execute(
                select(
                    orm.CollectRunOrm.finished_at,
                    orm.CollectRunOrm.started_at,
                )
                .where(orm.CollectRunOrm.scope == "snapshot")
                .order_by(orm.CollectRunOrm.id.desc())
                .limit(1)
            ).first()
            if row is None or row.finished_at is None:
                return None, None
            duration = (row.finished_at - row.started_at).total_seconds()
            return row.finished_at, duration

    def latest_snapshot_activity(self) -> datetime | None:
        """Most recent pi_snapshot.collected_at — non-None while a cycle is writing."""
        with self._db.session() as session:
            return session.execute(
                select(func.max(orm.SnapshotOrm.collected_at))
            ).scalar()

    def snapshot_writes_today(self) -> int:
        """Snapshot values written since local midnight (ACTIVITY_TZ).

        pi_snapshot is an UPSERT table (433 rows overwritten each cycle), so
        history cannot be derived from its current state. The honest source
        is pi_collect_run: sum of rows_collected over snapshot runs that
        finished today — grows by ~433 on every cycle.
        """
        from datetime import time as _time

        now_local = datetime.now(ACTIVITY_TZ)
        local_midnight = datetime.combine(
            now_local.date(), _time.min, tzinfo=ACTIVITY_TZ
        )
        with self._db.session() as session:
            return (
                session.execute(
                    select(func.coalesce(func.sum(orm.CollectRunOrm.rows_collected), 0)).where(
                        orm.CollectRunOrm.scope == "snapshot",
                        orm.CollectRunOrm.finished_at
                        >= local_midnight.astimezone(timezone.utc),
                    )
                ).scalar()
                or 0
            )

    def last_backfill_at(self) -> datetime | None:
        """When any backfill run last finished (pi_collect_run, any backfill scope)."""
        with self._db.session() as session:
            return session.execute(
                select(func.max(orm.CollectRunOrm.finished_at)).where(
                    orm.CollectRunOrm.scope.like("backfill%")
                )
            ).scalar()

    def collector_activity(self, *, days: int = 365) -> list[dict]:
        """Return per-day collector coverage for a GitHub-style activity graph.

        An hour counts as covered when the collector was running during it
        (pi_collect_run) OR at least one time-series point exists in it
        (pi_timeseries.timestamp). This way a backfill that fills hourly
        history for past days lights those days up. See
        accumulate_run_coverage.
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        tz_name = getattr(ACTIVITY_TZ, "key", str(ACTIVITY_TZ))
        with self._db.session() as session:
            run_rows = session.execute(
                select(
                    orm.CollectRunOrm.started_at,
                    orm.CollectRunOrm.finished_at,
                ).where(orm.CollectRunOrm.started_at >= cutoff)
            ).all()
            # local-hour buckets (naive wall-clock) that hold at least one point
            data_hour = func.date_trunc(
                "hour", orm.TimeseriesOrm.timestamp.op("AT TIME ZONE")(tz_name)
            ).label("bucket")
            data_rows = session.execute(
                select(data_hour)
                .where(orm.TimeseriesOrm.timestamp >= cutoff)
                .group_by(data_hour)
            ).all()
        return accumulate_run_coverage(
            list(run_rows), data_buckets=[r[0] for r in data_rows]
        )

    def record_run(self, stats) -> None:
        """Persist one completed collector run (CollectStats) for the activity graph."""
        with self._db.session() as session:
            session.add(
                orm.CollectRunOrm(
                    scope=stats.scope,
                    started_at=stats.started_at,
                    finished_at=stats.finished_at or datetime.now(timezone.utc),
                    attributes_seen=stats.attributes_seen,
                    rows_collected=stats.rows_collected,
                    errors=stats.errors,
                    requests_made=stats.requests_made,
                    aborted=stats.aborted,
                    abort_reason=stats.abort_reason or None,
                )
            )
            session.commit()

    # -- backfill progress (skip already-downloaded ranges) ------------------
    def get_backfill_progress(self, interval: str) -> dict[str, datetime]:
        """Return {attribute_id: last_timestamp} watermarks for an interval scope."""
        with self._db.session() as session:
            rows = session.execute(
                select(
                    orm.BackfillProgressOrm.attribute_id,
                    orm.BackfillProgressOrm.last_timestamp,
                ).where(orm.BackfillProgressOrm.interval == interval)
            ).all()
            return {attribute_id: last_ts for attribute_id, last_ts in rows}

    def record_backfill_progress(
        self, attribute_id: str, interval: str, last_timestamp: datetime
    ) -> None:
        """Upsert the download watermark for (attribute_id, interval)."""
        with self._db.session() as session:
            row = session.get(
                orm.BackfillProgressOrm, (attribute_id, interval)
            )
            if row is None:
                row = orm.BackfillProgressOrm(
                    attribute_id=attribute_id, interval=interval
                )
            row.last_timestamp = last_timestamp
            row.updated_at = datetime.now(timezone.utc)
            session.add(row)
            session.commit()

    # -- cursor -----------------------------------------------------------
    def set_cursor(self, scope: str, rows_seen: int) -> None:
        with self._db.session() as session:
            row = session.get(orm.CollectCursorOrm, scope)
            if row is None:
                row = orm.CollectCursorOrm(scope=scope)
            row.last_collected_at = datetime.now(timezone.utc)
            row.rows_seen = rows_seen
            row.updated_at = datetime.now(timezone.utc)
            session.add(row)
            session.commit()

    def get_cursor(self, scope: str) -> datetime | None:
        with self._db.session() as session:
            row = session.get(orm.CollectCursorOrm, scope)
            return row.last_collected_at if row else None
