"""Read-only SQLAlchemy boundary for the MX-009R Reliability Mart."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import event, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.elements import TextClause

from src.config import MartDbConfig


class MartDatabaseConfigError(RuntimeError):
    """Reliability Mart DSN is not configured or cannot be used safely."""


class ReadOnlySession:
    """Small query-only facade over SQLAlchemy Session.

    The facade intentionally does not expose ``add``, ``delete``, ``merge``,
    ``flush`` or ``commit``. PostgreSQL transactions are also marked read-only
    by ``MartDatabase`` as a second defense.
    """

    def __init__(self, session: Session):
        self._session = session

    def _execute(self, statement, *args, **kwargs):  # type: ignore[no-untyped-def]
        if getattr(statement, "is_insert", False) or getattr(statement, "is_update", False) or getattr(statement, "is_delete", False):
            raise RuntimeError("Reliability Mart query session blocks DML")
        if isinstance(statement, TextClause):
            sql = str(statement).lstrip().upper()
            if not sql.startswith(("SELECT", "EXPLAIN")):
                raise RuntimeError("Reliability Mart query session blocks non-read SQL")
        return self._session.execute(statement, *args, **kwargs)

    def execute(self, statement, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._execute(statement, *args, **kwargs)

    def scalar(self, statement, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._execute(statement, *args, **kwargs).scalar()

    def scalars(self, statement, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._execute(statement, *args, **kwargs).scalars()

    def get(self, model, identity):  # type: ignore[no-untyped-def]
        return self._session.get(model, identity)


class MartDatabase:
    """Dedicated Mart engine with no application write API."""

    def __init__(self, config: MartDbConfig):
        if not config.dsn:
            raise MartDatabaseConfigError("RELIABILITY_MART_DATABASE_URL is not configured")
        from sqlalchemy import create_engine

        self._engine = create_engine(config.dsn, echo=config.echo, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self._engine, autoflush=False, expire_on_commit=False)
        statement_timeout_ms = config.statement_timeout_ms

        @event.listens_for(self._engine, "begin")
        def _mark_transaction_read_only(connection):  # type: ignore[no-untyped-def]
            if connection.dialect.name == "postgresql":
                connection.exec_driver_sql("SET TRANSACTION READ ONLY")
                connection.exec_driver_sql(f"SET LOCAL statement_timeout = {statement_timeout_ms}")

    @property
    def engine(self):
        return self._engine

    @contextmanager
    def read_session(self) -> Iterator[ReadOnlySession]:
        session = self._session_factory()
        readonly = ReadOnlySession(session)
        try:
            yield readonly
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def healthcheck(self) -> bool:
        with self.read_session() as session:
            return session.scalar(select(1)) == 1


mart_db: MartDatabase | None = None


def get_mart_database() -> MartDatabase:
    global mart_db
    if mart_db is None:
        mart_db = MartDatabase(MartDbConfig.from_environment())
    return mart_db
