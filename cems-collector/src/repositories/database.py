"""SQLAlchemy engine/session factory for the collector local DB."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import DbConfig

LOG = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, config: DbConfig):
        self._engine = create_engine(config.dsn, echo=config.echo, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self._engine, autoflush=False, expire_on_commit=False)

    @property
    def engine(self):
        return self._engine

    def create_all(self) -> None:
        from src.repositories import models  # noqa: F401  (register tables)

        Base.metadata.create_all(self._engine)
        LOG.info("cems-collector local tables created (Postgres)")

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db: Database | None = None


def get_database() -> Database:
    global db
    if db is None:
        db = Database(DbConfig.from_environment())
    return db
