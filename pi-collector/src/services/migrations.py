"""Deliberate local PostgreSQL migrations; no PI config/client or source access."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from sqlalchemy import inspect, text

LOCK_KEY = 714025014
LEDGER = "pi_schema_migration"


class MigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Migration:
    number: int
    name: str
    checksum: str
    sql: str


def discover(directory):
    migrations = []
    numbers = set()
    for path in Path(directory).glob("*.sql"):
        match = re.fullmatch(r"(\d+)_[a-z0-9_]+\.sql", path.name)
        if not match:
            raise MigrationError("Invalid migration filename")
        number = int(match[1])
        if number in numbers:
            raise MigrationError(f"Duplicate migration prefix {number}")
        numbers.add(number)
        raw = path.read_bytes()
        sql = re.sub(r"(?m)^--.*$", "", raw.decode()).strip()
        if sql.startswith("BEGIN;") and sql.endswith("COMMIT;"):
            sql = sql[len("BEGIN;"):-len("COMMIT;")].strip()
        if re.search(r"(?im)^\s*(?:BEGIN|COMMIT|ROLLBACK);", sql):
            raise MigrationError("Migration must use runner transaction")
        migrations.append(Migration(number, path.name, sha256(raw).hexdigest(), sql))
    if not migrations:
        raise MigrationError("No migration files found")
    return sorted(migrations, key=lambda migration: migration.number)


def _history(connection):
    if not inspect(connection).has_table(LEDGER, schema="public"):
        return {}
    return {row.number: row for row in connection.execute(text(
        "SELECT number, name, checksum FROM public.pi_schema_migration ORDER BY number"
    ))}


def _plan(connection, migrations):
    history = _history(connection)
    catalog = {m.number: m for m in migrations}
    for number, row in history.items():
        if number not in catalog or (row.name, row.checksum) != (catalog[number].name, catalog[number].checksum):
            raise MigrationError(f"Applied migration identity drift at {number}")
    if history and set(history) != {m.number for m in migrations[:len(history)]}:
        raise MigrationError("Applied migration history is not an ordered prefix")
    return [{"number": m.number, "name": m.name, "checksum": m.checksum,
             "status": "APPLIED" if m.number in history else "PENDING"} for m in migrations]


def quality_preflight(connection):
    expected = {"source_value": ("json", None), "value_type": ("character varying", 40),
                "value_questionable": ("boolean", None), "value_substituted": ("boolean", None),
                "value_annotated": ("boolean", None)}
    for table in ("pi_snapshot", "pi_timeseries"):
        if not inspect(connection).has_table(table, schema="public"):
            raise MigrationError("Required PI table is missing")
        fields = dict(expected)
        if table == "pi_timeseries":
            fields["units"] = ("character varying", 40)
        rows = {r.column_name: r for r in connection.execute(text(
            "SELECT column_name,data_type,character_maximum_length,is_nullable,column_default "
            "FROM information_schema.columns WHERE table_schema='public' AND table_name=:table"
        ), {"table": table})}
        for field, (kind, length) in fields.items():
            if field not in rows:
                continue
            row = rows[field]
            if (row.data_type, row.character_maximum_length) != (kind, length) or row.is_nullable != "YES" or row.column_default is not None:
                raise MigrationError(f"Incompatible quality column {table}.{field}")


def migrate(engine, directory, *, apply=False):
    migrations = discover(directory)
    if engine.dialect.name != "postgresql" or engine.dialect.driver != "psycopg":
        raise MigrationError("PI migrations require PostgreSQL/TimescaleDB with psycopg")
    with engine.connect() as connection:
        if not apply:
            return _plan(connection, migrations)
        # Existing-store only: init-db owns initial schema creation. Refuse an
        # empty/misdirected database instead of silently creating PI tables.
        required = ("pi_attribute_registry", "pi_snapshot", "pi_timeseries",
                    "pi_collect_cursor", "pi_collect_run", "pi_backfill_progress")
        if any(not inspect(connection).has_table(table, schema="public") for table in required):
            raise MigrationError("Existing PI store preflight failed: required table missing")
        connection.commit()
        # A dedicated session lease serializes migrations and the managed worker.
        if not connection.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": LOCK_KEY}):
            raise MigrationError("PI worker or migration already owns the lease")
        connection.commit()
        try:
            plan = _plan(connection, migrations)
            connection.commit()
            for migration, state in zip(migrations, plan):
                if state["status"] == "APPLIED":
                    continue
                with connection.begin():
                    connection.execute(text("SET LOCAL search_path = public, pg_catalog"))
                    connection.execute(text("SET LOCAL lock_timeout = '5s'"))
                    connection.execute(text("SET LOCAL statement_timeout = '30s'"))
                    if migration.name == "004_signal_quality_fields.sql":
                        quality_preflight(connection)
                    connection.execute(text("CREATE TABLE IF NOT EXISTS public.pi_schema_migration ("
                        "number INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE,checksum VARCHAR(64) NOT NULL,"
                        "applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"))
                    # Psycopg simple protocol supports the reviewed DO block in 001.
                    with connection.connection.driver_connection.cursor() as cursor:
                        cursor.execute(migration.sql, prepare=False)
                    if migration.number == 1:
                        if not connection.scalar(text("SELECT EXISTS(SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_schema='public' AND hypertable_name='pi_timeseries')")):
                            raise MigrationError("Expected TimescaleDB hypertable is absent")
                    connection.execute(text("INSERT INTO public.pi_schema_migration(number,name,checksum) VALUES(:number,:name,:checksum)"),
                                       {"number": migration.number, "name": migration.name, "checksum": migration.checksum})
            return _plan(connection, migrations)
        except Exception as error:
            connection.rollback()
            if isinstance(error, MigrationError):
                raise
            raise MigrationError("Local migration failed; current file rolled back") from None
        finally:
            connection.rollback()
            connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": LOCK_KEY})
            connection.commit()
