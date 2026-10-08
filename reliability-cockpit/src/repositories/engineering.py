"""Explicit application-only repository. No environment lookup or schema creation."""
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, select, update
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from src.domain.engineering import EngineeringCase, CaseEvent, EngineeringError


class EngineeringBase(DeclarativeBase):
    pass


class CaseRow(EngineeringBase):
    __tablename__ = "engineering_case"
    case_id = Column(String(100), primary_key=True)
    revision = Column(Integer, nullable=False)
    document = Column(JSON, nullable=False)


class EventRow(EngineeringBase):
    __tablename__ = "engineering_case_event"
    case_id = Column(String(100), ForeignKey("engineering_case.case_id"), primary_key=True)
    revision = Column(Integer, primary_key=True)
    event = Column(JSON, nullable=False)
    snapshot = Column(JSON, nullable=False)


class ReceiptRow(EngineeringBase):
    __tablename__ = "engineering_case_receipt"
    actor = Column(String(160), primary_key=True)
    request_id = Column(String(100), primary_key=True)
    fingerprint = Column(String(64), nullable=False)
    case_id = Column(String(100), ForeignKey("engineering_case.case_id"), nullable=False)
    revision = Column(Integer, nullable=False)
    result = Column(JSON, nullable=False)


class CaseRepository:
    def __init__(self, engine):
        self.engine = engine

    def transact(self, operation):
        try:
            with self.engine.begin() as connection:
                return operation(connection)
        except SQLAlchemyError:
            # Never return database details, DSNs or driver exceptions to clients.
            raise EngineeringError("PERSISTENCE_UNAVAILABLE", 503) from None

    def get(self, c, case_id):
        raw = c.execute(select(CaseRow.document).where(CaseRow.case_id == case_id)).scalar_one_or_none()
        return EngineeringCase.model_validate(raw) if raw is not None else None

    def receipt(self, c, actor, request_id, fingerprint):
        row = c.execute(select(ReceiptRow.fingerprint, ReceiptRow.result).where(
            ReceiptRow.actor == actor, ReceiptRow.request_id == request_id)).first()
        if row is None:
            return None
        if row.fingerprint != fingerprint:
            raise EngineeringError("IDEMPOTENCY_CONFLICT")
        return EngineeringCase.model_validate(row.result)

    def save(self, c, case, event, expected_revision, actor, request_id, fingerprint):
        raw = case.model_dump(mode="json")
        if expected_revision == 0:
            c.execute(CaseRow.__table__.insert().values(case_id=case.case_id, revision=case.revision, document=raw))
        else:
            changed = c.execute(update(CaseRow).where(CaseRow.case_id == case.case_id,
                CaseRow.revision == expected_revision).values(revision=case.revision, document=raw))
            if changed.rowcount != 1:
                raise EngineeringError("REVISION_CONFLICT")
        c.execute(EventRow.__table__.insert().values(case_id=case.case_id, revision=case.revision,
            event=event.model_dump(mode="json"), snapshot=raw))
        c.execute(ReceiptRow.__table__.insert().values(actor=actor, request_id=request_id,
            fingerprint=fingerprint, case_id=case.case_id, revision=case.revision, result=raw))

    def list(self, c):
        # Bounded SQL asset/owner filtering is applied by the service query below.
        return select(CaseRow.document)

    def history(self, c, case_id, offset, limit):
        rows = c.execute(select(EventRow.event).where(EventRow.case_id == case_id)
            .order_by(EventRow.revision).offset(offset).limit(limit)).scalars()
        return [CaseEvent.model_validate(row) for row in rows]
