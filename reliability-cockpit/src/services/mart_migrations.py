"""Deliberate canonical governance DDL in an existing Collector-owned Mart.

No base initialization, source calls, seeds or legacy DATABASE_URL fallback.
Status is read-only; apply is one bounded, leased transaction for 002/003.
"""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from src.repositories.mart_models import AssetAfMappingMart

FILES = ("002_asset_af_mapping.sql", "003_asset_af_mapping_provenance.sql")
ROOT = Path(os.getenv("RELIABILITY_MART_MIGRATIONS_ROOT", str(Path(__file__).resolve().parents[2] / "migrations")))
LEDGER = "nadi_mart_schema_migration"
BASE_TABLES = (
    "equipment", "work_order", "sync_cursor", "collect_run", "asset_master",
    "maintenance_event", "fmea_assessment", "rcfa_analysis",
    "asset_health_assessment", "overhaul_event", "reliability_asset_registry",
    "mart_projection_state", "equipment_status_history", "item", "labor", "person", "service_request",
)
READ_TABLES = ("asset_master", "maintenance_event", "fmea_assessment", "rcfa_analysis",
               "asset_health_assessment", "overhaul_event", "reliability_asset_registry",
               "mart_projection_state", "asset_af_mapping")
READER_ROLE = "nadi_mart_reader"
LEASE_KEY = 73002002


class MartMigrationError(RuntimeError):
    """Safe operator diagnostic without DSNs, source records or SQL parameters."""


def admin_engine():
    dsn = os.getenv("RELIABILITY_MART_ADMIN_DATABASE_URL")
    if not dsn:
        raise MartMigrationError("RELIABILITY_MART_ADMIN_DATABASE_URL is required; no reader/legacy fallback")
    return create_engine(dsn, pool_pre_ping=True, echo=False)


def _expected_database():
    value = os.getenv("RELIABILITY_MART_EXPECT_DATABASE")
    if not value:
        raise MartMigrationError("RELIABILITY_MART_EXPECT_DATABASE must explicitly name the existing owner database")
    return value


def _preflight(c, expected_database):
    if c.dialect.name != "postgresql":
        raise MartMigrationError("governance deployment requires PostgreSQL")
    actual = c.scalar(text("SELECT current_database()"))
    if actual != expected_database:
        raise MartMigrationError("wrong database: expected existing Mart owner")
    inspector = inspect(c)
    names = set(inspector.get_table_names(schema="public"))
    if not set(BASE_TABLES) <= names:
        raise MartMigrationError("existing Collector/Mart anchors are missing; refusing initialization")
    for table, key in (("asset_master", "canonical_id"), ("reliability_asset_registry", "asset_ref"),
                       ("sync_cursor", "scope"), ("mart_projection_state", "projection_key")):
        if inspector.get_pk_constraint(table, schema="public")["constrained_columns"] != [key]:
            raise MartMigrationError("incompatible existing Mart identity")
    c.exec_driver_sql("SET LOCAL search_path = public, pg_catalog")
    return names


def _files(directory):
    entries = []
    for name in FILES:
        p = directory / name
        if not p.is_file():
            raise MartMigrationError("canonical governance SQL is not packaged")
        raw = p.read_bytes()
        entries.append((name, hashlib.sha256(raw).hexdigest(), raw.decode("utf-8")))
    return entries


def _validate_mapping(c, provenance):
    inspector = inspect(c)
    actual = {v["name"]: v for v in inspector.get_columns("asset_af_mapping", schema="public")}
    expected = AssetAfMappingMart.__table__
    provenance_columns = {"verified_by", "verification_note", "evidence_ref", "retired_by", "retirement_note"}
    for col in expected.columns:
        if not provenance and col.name in provenance_columns:
            continue
        a = actual.get(col.name)
        if a is None or a["nullable"] != col.nullable or str(a["type"].compile(dialect=c.dialect)).upper() != str(col.type.compile(dialect=c.dialect)).upper():
            raise MartMigrationError("mapping schema columns differ from merged lifecycle model")
    constraints = {v["name"]: v for v in inspector.get_check_constraints("asset_af_mapping", schema="public")}
    required = {"ck_asset_af_mapping_status", "ck_asset_af_mapping_role", "ck_asset_af_mapping_evidence"}
    if provenance:
        required |= {"ck_asset_af_mapping_verified_provenance", "ck_asset_af_mapping_proposed_provenance", "ck_asset_af_mapping_retired_provenance"}
    if not required <= constraints.keys():
        raise MartMigrationError("mapping lifecycle constraints missing")
    if inspector.get_pk_constraint("asset_af_mapping", schema="public")["constrained_columns"] != ["id"]:
        raise MartMigrationError("mapping primary key differs")
    fks = inspector.get_foreign_keys("asset_af_mapping", schema="public")
    if not any(f["constrained_columns"] == ["canonical_asset_id"] and f["referred_table"] == "asset_master"
               and f["referred_columns"] == ["canonical_id"] and f["options"].get("ondelete") == "RESTRICT" for f in fks):
        raise MartMigrationError("mapping canonical Asset FK differs")
    indexes = {i["name"]: i for i in inspector.get_indexes("asset_af_mapping", schema="public")}
    for name, columns in (("ix_asset_af_mapping_asset_status", ["canonical_asset_id", "mapping_status"]),
                          ("ix_asset_af_mapping_af_element", ["af_element_ref"]),
                          ("uq_asset_af_mapping_active_exact", ["canonical_asset_id", "af_element_ref", "mapping_role"])):
        if name not in indexes or indexes[name]["column_names"] != columns:
            raise MartMigrationError("mapping identity indexes differ")
    unique = indexes["uq_asset_af_mapping_active_exact"]
    predicate = str(unique.get("dialect_options", {}).get("postgresql_where", ""))
    if not unique["unique"] or "PROPOSED" not in predicate or "VERIFIED" not in predicate or "RETIRED" in predicate:
        raise MartMigrationError("mapping active-exact uniqueness differs")
    if c.scalar(text("SELECT count(*) FROM pg_constraint WHERE conrelid='public.asset_af_mapping'::regclass AND NOT convalidated")):
        raise MartMigrationError("mapping constraints are not validated")


def _status(c, names, entries):
    applied = []
    if LEDGER in names:
        applied = list(c.execute(text(f"SELECT filename,sha256 FROM {LEDGER} ORDER BY filename")))
    if [r.filename for r in applied] != list(FILES[:len(applied)]):
        raise MartMigrationError("unknown/out-of-order governance migration ledger")
    for row, entry in zip(applied, entries):
        if row.sha256 != entry[1]:
            raise MartMigrationError("governance migration checksum drift")
    if "asset_af_mapping" in names:
        if not applied:
            raise MartMigrationError("untracked governance schema: explicit reconciliation required")
        _validate_mapping(c, len(applied) == 2)
    elif applied:
        raise MartMigrationError("ledger present but mapping schema missing")
    return [{"filename": name, "sha256": digest, "status": "APPLIED" if i < len(applied) else "PENDING"}
            for i, (name, digest, _) in enumerate(entries)]


def _counts(c):
    return {t: c.scalar(text(f'SELECT count(*) FROM public."{t}"')) for t in BASE_TABLES}


def _fingerprints(c):
    # Aggregate only: payload stays inside PostgreSQL. Includes recovery-floor,
    # cursor and projection evidence without writing/resetting any of them.
    result = {}
    for table in BASE_TABLES:
        statement = "SELECT md5(coalesce(string_agg(md5(row_to_json(t)::text), '' ORDER BY md5(row_to_json(t)::text)), '')) FROM public.\"" + table + "\" t"
        result[table] = c.scalar(text(statement))
    return result


def run_migrations(engine, *, expected_database, apply=False, require_ready=False, directory=ROOT):
    entries = _files(directory)
    started = time.monotonic()
    try:
        with engine.begin() as c:
            if not apply:
                c.exec_driver_sql("SET TRANSACTION READ ONLY")
            c.exec_driver_sql("SET LOCAL lock_timeout = '5s'")
            c.exec_driver_sql("SET LOCAL statement_timeout = '30s'")
            names = _preflight(c, expected_database)
            if apply and not c.scalar(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": LEASE_KEY}):
                raise MartMigrationError("another governance administration owns the lease")
            status = _status(c, names, entries)
            pending = [s["filename"] for s in status if s["status"] == "PENDING"]
            before = after = None
            fingerprints_before = fingerprints_after = None
            if apply and pending:
                # Short, bounded local DDL: prevent concurrent facts changing the
                # preservation comparison; no worker stop/cursor reset required.
                c.exec_driver_sql("LOCK TABLE " + ",".join('public."'+t+'"' for t in BASE_TABLES) + " IN SHARE MODE")
                before = _counts(c)
                fingerprints_before = _fingerprints(c)
                c.exec_driver_sql(f"CREATE TABLE IF NOT EXISTS {LEDGER} (filename text PRIMARY KEY, sha256 varchar(64) NOT NULL, applied_at timestamptz NOT NULL DEFAULT clock_timestamp())")
                for name, digest, sql in entries:
                    if name in pending:
                        c.exec_driver_sql(sql)
                        c.execute(text(f"INSERT INTO {LEDGER} (filename,sha256) VALUES (:name,:sha)"), {"name": name, "sha": digest})
                _validate_mapping(c, True)
                after = _counts(c)
                fingerprints_after = _fingerprints(c)
                if before != after or fingerprints_before != fingerprints_after:
                    raise MartMigrationError("factual population changed inside governance transaction")
                status = _status(c, set(inspect(c).get_table_names(schema="public")), entries)
            ready = all(s["status"] == "APPLIED" for s in status)
            if require_ready and not ready:
                raise MartMigrationError("Mart governance pending: deliberately migrate before starting reader/projector")
            return {"ready": ready, "applied": pending if apply else [], "migrations": status,
                    "before": before, "after": after, "fingerprints_before": fingerprints_before,
                    "fingerprints_after": fingerprints_after, "duration_seconds": round(time.monotonic()-started, 3)}
    except SQLAlchemyError as error:
        raise MartMigrationError("governance database operation failed; transaction rolled back ("+type(error).__name__+")") from None


def reader_role(engine, *, expected_database, apply=False, password=None):
    """Deliberately provision only named Mart SELECT grants; no owner changes.

    Password stays private, supplied by the operator environment; no DSN/SQL
    parameter is logged or returned. Existing unexpected privileges fail closed.
    """
    from psycopg import sql, Error as PsycopgError
    try:
        with engine.begin() as c:
            if not apply:
                c.exec_driver_sql("SET TRANSACTION READ ONLY")
            c.exec_driver_sql("SET LOCAL lock_timeout = '5s'")
            c.exec_driver_sql("SET LOCAL statement_timeout = '30s'")
            names = _preflight(c, expected_database)
            status = _status(c, names, _files(ROOT))
            if not all(s["status"] == "APPLIED" for s in status):
                raise MartMigrationError("governance must be ready before reader grants")
            row = c.execute(text("SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname=:role"), {"role": READER_ROLE}).first()
            if row:
                if any(row) or c.scalar(text("SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=:role)"), {"role": READER_ROLE}):
                    raise MartMigrationError("existing reader has privileged role attributes/memberships")
                if c.scalar(text("SELECT count(*) FROM pg_database WHERE datdba=(SELECT oid FROM pg_roles WHERE rolname=:role)"), {"role": READER_ROLE}):
                    raise MartMigrationError("reader cannot own a database")
                if c.scalar(text("SELECT count(*) FROM pg_class WHERE relowner=(SELECT oid FROM pg_roles WHERE rolname=:role)"), {"role": READER_ROLE}):
                    raise MartMigrationError("reader cannot own relations")
                for table in sorted(names):
                    if any(c.scalar(text("SELECT has_table_privilege(:role,:table,:priv)"), {"role": READER_ROLE,"table": "public."+table,"priv": priv}) for priv in ("INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER")):
                        raise MartMigrationError("existing reader has Mart/Collector write privileges")
            if apply:
                if not c.scalar(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": LEASE_KEY}):
                    raise MartMigrationError("another governance administration owns the lease")
                if not row:
                    if not password or len(password) < 24:
                        raise MartMigrationError("new reader requires a private password of at least 24 characters")
                    raw = c.connection.driver_connection
                    with raw.cursor() as cursor:
                        cursor.execute(sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD {}").format(sql.Identifier(READER_ROLE), sql.Literal(password)))
                c.exec_driver_sql(f"ALTER ROLE {READER_ROLE} SET default_transaction_read_only = on")
                with c.connection.driver_connection.cursor() as cursor:
                    cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(sql.Identifier(expected_database), sql.Identifier(READER_ROLE)))
                c.exec_driver_sql(f"GRANT USAGE ON SCHEMA public TO {READER_ROLE}")
                c.exec_driver_sql("GRANT SELECT ON " + ",".join('public."'+t+'"' for t in READ_TABLES) + f" TO {READER_ROLE}")
            return {"role": READER_ROLE, "exists": bool(row) or apply, "applied": apply, "select_tables": list(READ_TABLES)}
    except (SQLAlchemyError, PsycopgError) as error:
        raise MartMigrationError("reader provision failed; transaction rolled back ("+type(error).__name__+")") from None


def environment_migrations(**kwargs):
    engine = admin_engine()
    try:
        return run_migrations(engine, expected_database=_expected_database(), **kwargs)
    finally:
        engine.dispose()
