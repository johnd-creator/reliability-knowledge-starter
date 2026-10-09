"""Explicit existing application-store identity. Never fall back to Mart/DSNs."""
from sqlalchemy import inspect, text
from src.domain.engineering import EngineeringError


class ApplicationStore:
    def __init__(self, engine, *, expected_database: str, isolated=False):
        if not expected_database or engine.dialect.name not in {"sqlite", "postgresql"}:
            raise EngineeringError("APPLICATION_STORE_IDENTITY_REQUIRED", 503)
        if engine.dialect.name == "sqlite" and not isolated:
            raise EngineeringError("ISOLATED_STORE_ONLY", 503)
        with engine.connect() as connection:
            tables = set(inspect(connection).get_table_names())
            if {"asset_master", "reliability_asset_registry", "asset_af_mapping"} & tables:
                raise EngineeringError("MART_WRITER_FORBIDDEN", 503)
            if engine.dialect.name == "postgresql":
                actual = connection.scalar(text("SELECT current_database()"))
                if actual != expected_database or (isolated and not actual.endswith("_test")):
                    raise EngineeringError("APPLICATION_STORE_IDENTITY_MISMATCH", 503)
            if not isolated and not {"equipment", "work_order", "sync_cursor"} <= tables:
                raise EngineeringError("APPLICATION_SCHEMA_ANCHORS_REQUIRED", 503)
        self.engine = engine
