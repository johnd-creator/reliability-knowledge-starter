"""CollectorStore: persist contract-shaped domain models into Postgres."""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.domain import models as domain
from src.repositories import models as orm
from src.repositories.database import Database


def _json_safe(value: Any) -> Any:
    """Convert nested datetimes/dataclasses to values accepted by JSONB."""
    if isinstance(value, datetime):
        return value.isoformat()
    if dataclasses.is_dataclass(value):
        return _json_safe(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _parameter_row(parameter: domain.ParameterSpec) -> dict:
    """ParameterSpec -> column dict; modbus config flattens into sources.cems."""
    row: dict[str, Any] = {}
    for f in dataclasses.fields(parameter):
        value = getattr(parameter, f.name)
        if f.name == "modbus":
            row["sources"] = _json_safe({"cems": {"modbus": value}})
            continue
        row[f.name] = _json_safe(value)
    return row


def _reading_row(reading: domain.Reading) -> dict:
    return {
        "parameter_code": reading.parameter_code,
        "stack_id": reading.stack_id,
        "value_raw": reading.value_raw,
        "value_normalized": reading.value_normalized,
        "value_correction": reading.value_correction,
        "value_final": reading.value_final,
        "transformation_status": reading.transformation_status,
        "observed_at": reading.observed_at,
        "created_at": datetime.now(timezone.utc),
    }


class CollectorStore:
    def __init__(self, db: Database):
        self._db = db

    # -- registry --------------------------------------------------------------
    def upsert_stacks(self, stacks: list[domain.Stack]) -> None:
        if not stacks:
            return
        with self._db.session() as session:
            for stack in stacks:
                row = dataclasses.asdict(stack)
                stmt = pg_insert(orm.StackOrm).values(**row)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["stack_id"],
                    set_={c: getattr(stmt.excluded, c) for c in row if c != "stack_id"},
                )
                session.execute(stmt)
            session.commit()

    def upsert_parameters(self, parameters: list[domain.ParameterSpec]) -> None:
        if not parameters:
            return
        rows = [_parameter_row(p) for p in parameters]
        with self._db.session() as session:
            stmt = pg_insert(orm.ParameterOrm).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["code", "stack_id"],
                set_={c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("code", "stack_id")},
            )
            session.execute(stmt)
            session.commit()

    def get_stack(self, stack_id: str) -> domain.Stack | None:
        with self._db.session() as session:
            row = session.get(orm.StackOrm, stack_id)
            if row is None:
                return None
            return domain.Stack(
                stack_id=row.stack_id,
                code=row.code,
                name=row.name,
                status=row.status,
                description=row.description,
                maintenance_from=row.maintenance_from,
                maintenance_to=row.maintenance_to,
            )

    def active_parameters(self, stack_id: str | None = None) -> list[domain.ParameterSpec]:
        with self._db.session() as session:
            stmt = select(orm.ParameterOrm).where(orm.ParameterOrm.collect_enabled.is_(True))
            if stack_id:
                stmt = stmt.where(orm.ParameterOrm.stack_id == stack_id)
            stmt = stmt.order_by(orm.ParameterOrm.code)
            rows = list(session.execute(stmt).scalars())
            return [self._spec_from_orm(row) for row in rows]

    @staticmethod
    def _spec_from_orm(row: orm.ParameterOrm) -> domain.ParameterSpec:
        sources = row.sources or {}
        cems = sources.get("cems") or {}
        modbus_raw = cems.get("modbus") or {}
        modbus = domain.ModbusReadConfig(
            register=int(modbus_raw.get("register", 0)),
            register_type=modbus_raw.get("register_type", "holding"),
            data_type=modbus_raw.get("data_type", "float32"),
            word_order=modbus_raw.get("word_order", "big"),
            byte_order=modbus_raw.get("byte_order", "big"),
            address_base=modbus_raw.get("address_base"),
            zero_based=bool(modbus_raw.get("zero_based", False)),
        )
        return domain.ParameterSpec(
            code=row.code,
            stack_id=row.stack_id,
            name=row.name,
            unit=row.unit,
            status=row.status,
            collect_enabled=row.collect_enabled,
            threshold=row.threshold,
            normalization_enabled=row.normalization_enabled,
            maintenance_override_enabled=row.maintenance_override_enabled,
            o2_reference=row.o2_reference,
            adjust_factor=row.adjust_factor,
            adjust_constant=row.adjust_constant,
            modbus=modbus,
        )

    # -- readings ---------------------------------------------------------------
    def insert_readings(self, readings: list[domain.Reading]) -> int:
        if not readings:
            return 0
        rows = [_reading_row(r) for r in readings]
        with self._db.session() as session:
            session.add_all([orm.ReadingOrm(**row) for row in rows])
            session.commit()
        return len(rows)

    def latest_readings(self, stack_id: str | None = None) -> list[Any]:
        """Latest reading per (parameter_code, stack_id)."""
        with self._db.session() as session:
            stmt = (
                select(orm.ReadingOrm)
                .distinct(orm.ReadingOrm.parameter_code, orm.ReadingOrm.stack_id)
                .order_by(
                    orm.ReadingOrm.parameter_code,
                    orm.ReadingOrm.stack_id,
                    desc(orm.ReadingOrm.observed_at),
                )
            )
            if stack_id:
                stmt = stmt.where(orm.ReadingOrm.stack_id == stack_id)
            return list(session.execute(stmt).scalars())

    def list_readings(
        self,
        *,
        parameter_code: str | None = None,
        stack_id: str | None = None,
        status: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> list[Any]:
        with self._db.session() as session:
            stmt = select(orm.ReadingOrm)
            if parameter_code:
                stmt = stmt.where(orm.ReadingOrm.parameter_code == parameter_code)
            if stack_id:
                stmt = stmt.where(orm.ReadingOrm.stack_id == stack_id)
            if status:
                stmt = stmt.where(orm.ReadingOrm.transformation_status == status)
            if since is not None:
                stmt = stmt.where(orm.ReadingOrm.observed_at >= since)
            if until is not None:
                stmt = stmt.where(orm.ReadingOrm.observed_at < until)
            stmt = stmt.order_by(orm.ReadingOrm.observed_at.desc(), orm.ReadingOrm.id.desc())
            stmt = stmt.offset(offset).limit(limit)
            return list(session.execute(stmt).scalars())

    def count_readings(
        self,
        *,
        parameter_code: str | None = None,
        stack_id: str | None = None,
        status: str | None = None,
    ) -> int:
        with self._db.session() as session:
            stmt = select(func.count()).select_from(orm.ReadingOrm)
            if parameter_code:
                stmt = stmt.where(orm.ReadingOrm.parameter_code == parameter_code)
            if stack_id:
                stmt = stmt.where(orm.ReadingOrm.stack_id == stack_id)
            if status:
                stmt = stmt.where(orm.ReadingOrm.transformation_status == status)
            return session.execute(stmt).scalar() or 0

    # -- aggregation --------------------------------------------------------------
    def window_aggregate(
        self,
        window_start: datetime,
        window_end: datetime,
        *,
        stack_id: str | None = None,
    ) -> list[domain.AggregatedReading]:
        """Aggregate value_final over one window; empty values count as 0 samples."""
        value_final = orm.ReadingOrm.value_final
        with self._db.session() as session:
            stmt = (
                select(
                    orm.ReadingOrm.parameter_code,
                    orm.ReadingOrm.stack_id,
                    func.avg(value_final),
                    func.min(value_final),
                    func.max(value_final),
                    func.count(value_final),
                )
                .where(
                    orm.ReadingOrm.observed_at >= window_start,
                    orm.ReadingOrm.observed_at < window_end,
                )
                .group_by(orm.ReadingOrm.parameter_code, orm.ReadingOrm.stack_id)
            )
            if stack_id:
                stmt = stmt.where(orm.ReadingOrm.stack_id == stack_id)
            rows = session.execute(stmt).all()
            return [
                domain.AggregatedReading(
                    parameter_code=code,
                    stack_id=stack,
                    window_start=window_start,
                    avg_value=float(avg) if count else 0.0,
                    min_value=float(mn) if count else 0.0,
                    max_value=float(mx) if count else 0.0,
                    sample_count=int(count),
                )
                for code, stack, avg, mn, mx, count in rows
            ]

    def upsert_5min(self, aggregates: list[domain.AggregatedReading]) -> int:
        if not aggregates:
            return 0
        rows = [dataclasses.asdict(a) for a in aggregates]
        with self._db.session() as session:
            stmt = pg_insert(orm.Reading5MinOrm).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["parameter_code", "stack_id", "window_start"],
                set_={
                    "avg_value": stmt.excluded.avg_value,
                    "min_value": stmt.excluded.min_value,
                    "max_value": stmt.excluded.max_value,
                    "sample_count": stmt.excluded.sample_count,
                },
            )
            session.execute(stmt)
            session.commit()
        return len(rows)

    def list_5min(
        self,
        *,
        parameter_code: str | None = None,
        stack_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> list[Any]:
        with self._db.session() as session:
            stmt = select(orm.Reading5MinOrm)
            if parameter_code:
                stmt = stmt.where(orm.Reading5MinOrm.parameter_code == parameter_code)
            if stack_id:
                stmt = stmt.where(orm.Reading5MinOrm.stack_id == stack_id)
            if since is not None:
                stmt = stmt.where(orm.Reading5MinOrm.window_start >= since)
            if until is not None:
                stmt = stmt.where(orm.Reading5MinOrm.window_start < until)
            stmt = stmt.order_by(orm.Reading5MinOrm.window_start.desc())
            stmt = stmt.offset(offset).limit(limit)
            return list(session.execute(stmt).scalars())

    # -- registry listing (API) ------------------------------------------------
    def list_parameters(self, stack_id: str | None = None) -> list[Any]:
        with self._db.session() as session:
            stmt = select(orm.ParameterOrm).order_by(orm.ParameterOrm.stack_id, orm.ParameterOrm.code)
            if stack_id:
                stmt = stmt.where(orm.ParameterOrm.stack_id == stack_id)
            return list(session.execute(stmt).scalars())

    def list_stacks(self) -> list[Any]:
        with self._db.session() as session:
            stmt = select(orm.StackOrm).order_by(orm.StackOrm.stack_id)
            return list(session.execute(stmt).scalars())

    def count(self, orm_cls: type) -> int:
        with self._db.session() as session:
            return session.execute(select(func.count()).select_from(orm_cls)).scalar() or 0

    def list_runs(self, limit: int = 20) -> list[Any]:
        with self._db.session() as session:
            stmt = (
                select(orm.CollectRunOrm)
                .order_by(orm.CollectRunOrm.started_at.desc(), orm.CollectRunOrm.id.desc())
                .limit(limit)
            )
            return list(session.execute(stmt).scalars())

    def latest_run(self) -> Any | None:
        rows = self.list_runs(1)
        return rows[0] if rows else None

    # -- cursor / run log --------------------------------------------------------
    def get_cursor(self, scope: str) -> datetime | None:
        with self._db.session() as session:
            row = session.get(orm.SyncCursorOrm, scope)
            return row.watermark if row else None

    def set_cursor(self, scope: str, watermark: datetime | None, rows_seen: int) -> None:
        with self._db.session() as session:
            row = session.get(orm.SyncCursorOrm, scope)
            if row is None:
                row = orm.SyncCursorOrm(scope=scope)
            row.watermark = watermark
            row.rows_seen = rows_seen
            row.updated_at = datetime.now(timezone.utc)
            session.add(row)
            session.commit()

    def record_run(self, run) -> None:
        """Persist one completed run (CollectStats / AggregateStats) for observability."""
        with self._db.session() as session:
            session.add(
                orm.CollectRunOrm(
                    run_type=run.run_type,
                    mode=run.mode,
                    rows_seen=run.rows_seen,
                    upserted=run.upserted,
                    skipped=run.skipped,
                    errors=run.errors,
                    watermark=run.watermark,
                    started_at=run.started_at,
                    finished_at=run.finished_at,
                )
            )
            session.commit()
