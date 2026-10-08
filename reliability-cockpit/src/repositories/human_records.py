"""Application-only CAS and append-only revisions, atomic receipts; no init."""

from sqlalchemy import (
    Column,
    String,
    Integer,
    JSON,
    ForeignKeyConstraint,
    select,
    update,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.domain.engineering import EngineeringError


class HumanRecordBase(DeclarativeBase):
    pass


class RecordRow(HumanRecordBase):
    __tablename__ = "nadi_human_record"
    kind = Column(String(40), primary_key=True)
    record_id = Column(String(100), primary_key=True)
    revision = Column(Integer, nullable=False)
    document = Column(JSON, nullable=False)


class RevisionRow(HumanRecordBase):
    __tablename__ = "nadi_human_record_revision"
    kind = Column(String(40), primary_key=True)
    record_id = Column(String(100), primary_key=True)
    revision = Column(Integer, primary_key=True)
    actor = Column(String(160), nullable=False)
    action = Column(String(40), nullable=False)
    occurred_at = Column(String(40), nullable=False)
    reason = Column(String(6000), nullable=True)
    snapshot = Column(JSON, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["kind", "record_id"],
            ["nadi_human_record.kind", "nadi_human_record.record_id"],
        ),
    )


class HumanReceiptRow(HumanRecordBase):
    __tablename__ = "nadi_human_record_receipt"
    actor = Column(String(160), primary_key=True)
    request_id = Column(String(100), primary_key=True)
    fingerprint = Column(String(64), nullable=False)
    kind = Column(String(40), nullable=False)
    record_id = Column(String(100), nullable=False)
    revision = Column(Integer, nullable=False)
    result = Column(JSON, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["kind", "record_id"],
            ["nadi_human_record.kind", "nadi_human_record.record_id"],
        ),
    )


class HumanRecordRepository:
    def __init__(self, store):
        self.engine = store.engine

    def transact(self, operation):
        try:
            with self.engine.begin() as c:
                return operation(c)
        except IntegrityError:
            raise EngineeringError("REQUEST_CONFLICT", 409) from None
        except SQLAlchemyError:
            raise EngineeringError("PERSISTENCE_UNAVAILABLE", 503) from None

    def get(self, c, kind, record_id):
        return c.scalar(
            select(RecordRow.document).where(
                RecordRow.kind == kind, RecordRow.record_id == record_id
            )
        )

    def receipt(self, c, actor, request_id, fingerprint):
        row = c.execute(
            select(HumanReceiptRow.fingerprint, HumanReceiptRow.result).where(
                HumanReceiptRow.actor == actor, HumanReceiptRow.request_id == request_id
            )
        ).first()
        if row:
            if row.fingerprint != fingerprint:
                raise EngineeringError("IDEMPOTENCY_CONFLICT", 409)
            return row.result

    def save(
        self, c, kind, record, previous, actor, action, reason, request_id, fingerprint
    ):
        raw = record.model_dump(mode="json")
        if previous == 0:
            c.execute(
                RecordRow.__table__.insert().values(
                    kind=kind, record_id=record.record_id, revision=1, document=raw
                )
            )
        else:
            result = c.execute(
                update(RecordRow)
                .where(
                    RecordRow.kind == kind,
                    RecordRow.record_id == record.record_id,
                    RecordRow.revision == previous,
                )
                .values(revision=record.revision, document=raw)
            )
            if result.rowcount != 1:
                raise EngineeringError("REVISION_CONFLICT", 409)
        c.execute(
            RevisionRow.__table__.insert().values(
                kind=kind,
                record_id=record.record_id,
                revision=record.revision,
                actor=actor,
                action=action,
                occurred_at=record.updated_at.isoformat(),
                reason=reason,
                snapshot=raw,
            )
        )
        c.execute(
            HumanReceiptRow.__table__.insert().values(
                actor=actor,
                request_id=request_id,
                fingerprint=fingerprint,
                kind=kind,
                record_id=record.record_id,
                revision=record.revision,
                result=raw,
            )
        )
