"""Explicit reversible QA constraint expansion. Never a startup/operational migration."""
import re
from sqlalchemy import text
from src.domain.engineering import EngineeringError
from src.repositories.application_boundary import ApplicationStore


def change_qa_advisory_schema(engine, *, expected_database, acknowledgement, rollback=False):
    url = engine.url
    if acknowledgement != 'isolated-advisory-qa-only' or url.get_backend_name() != 'postgresql' or url.host not in {'127.0.0.1', 'localhost'} or not (url.database or '').endswith('_test'):
        raise EngineeringError('ISOLATED_QA_ACK_REQUIRED', 503)
    ApplicationStore(engine, expected_database=expected_database, isolated=True)
    with engine.begin() as c:
        c.execute(text('SELECT pg_advisory_xact_lock(793245102)'))
        constraints = dict(c.execute(text("SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='nadi_human_record'::regclass AND contype='c'")).all())
        old = 'nadi_human_record_kind_check'
        new = 'nadi_qa_advisory_kind_check'
        if rollback:
            if old in constraints and new not in constraints:
                return 'ALREADY_RESTORED'
            if new not in constraints or old in constraints:
                raise EngineeringError('QA_SCHEMA_DRIFT', 503)
            if c.scalar(text("SELECT count(*) FROM nadi_human_record WHERE kind IN ('ADVISORY','ADVISORY_ACK')")):
                raise EngineeringError('QA_RECORDS_REQUIRE_PRESERVATION', 409)
            c.exec_driver_sql("ALTER TABLE nadi_human_record DROP CONSTRAINT nadi_qa_advisory_kind_check, ADD CONSTRAINT nadi_human_record_kind_check CHECK(kind IN ('INSPECTION','RECOMMENDATION'))")
            return 'RESTORED'
        if new in constraints and old not in constraints and re.findall(r"'([^']*)'", constraints[new]) == ['INSPECTION','RECOMMENDATION','ADVISORY','ADVISORY_ACK']:
            return 'ALREADY_READY'
        if old not in constraints or new in constraints or re.findall(r"'([^']*)'", constraints[old]) != ['INSPECTION','RECOMMENDATION']:
            raise EngineeringError('QA_SCHEMA_DRIFT', 503)
        c.exec_driver_sql("ALTER TABLE nadi_human_record DROP CONSTRAINT nadi_human_record_kind_check, ADD CONSTRAINT nadi_qa_advisory_kind_check CHECK(kind IN ('INSPECTION','RECOMMENDATION','ADVISORY','ADVISORY_ACK'))")
        return 'READY'


def qa_advisory_schema_ready(engine):
    """Read-only capability probe; never changes a constraint."""
    with engine.connect() as c:
        definitions = c.execute(text("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='nadi_human_record'::regclass AND conname='nadi_qa_advisory_kind_check' AND contype='c'")).scalars().all()
        return len(definitions) == 1 and re.findall(r"'([^']*)'", definitions[0]) == ['INSPECTION','RECOMMENDATION','ADVISORY','ADVISORY_ACK']
