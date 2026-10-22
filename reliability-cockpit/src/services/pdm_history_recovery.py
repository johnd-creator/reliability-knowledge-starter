"""Private, scoped history recovery evidence; no restore/delete endpoint.

Includes the seven new history tables and six existing business document tables.
Excludes accounts, sessions, attachments and all collector/factual stores.
"""
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256
import os, stat, json
from sqlalchemy import select, text, inspect, MetaData, Table, tuple_
from src.repositories.pdm_source_history import TABLES, KEYS
from src.services.pdm_source_history import canonical, digest
from src.domain.engineering import EngineeringError

BUSINESS = ('nadi_human_record', 'nadi_human_record_revision', 'nadi_human_record_receipt',
            'engineering_case', 'engineering_case_event', 'engineering_case_receipt')
MAX_SNAPSHOT_BYTES = 128*1024*1024


def private_bytes(path):
    path = Path(path).absolute(); parent = path.parent.stat()
    if path.resolve() != path or parent.st_uid != os.getuid() or parent.st_mode & 0o077:
        raise EngineeringError('PRIVATE_HISTORY_RECOVERY_REQUIRED', 403)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_uid != os.getuid() or st.st_mode & 0o077 or st.st_size > MAX_SNAPSHOT_BYTES:
            raise EngineeringError('PRIVATE_HISTORY_RECOVERY_REQUIRED', 403)
        with os.fdopen(fd, 'rb', closefd=False) as stream: data = stream.read(MAX_SNAPSHOT_BYTES+1)
        if len(data) != st.st_size: raise EngineeringError('HISTORY_RECOVERY_FILE_CHANGED', 409)
        return data
    finally: os.close(fd)


def identity(c):
    database, oid, started = c.execute(text('SELECT current_database(),(SELECT oid::text FROM pg_database WHERE datname=current_database()),pg_postmaster_start_time()::text')).one()
    return {'database': database, 'oid': oid, 'server_started_at': started}


def schema(c):
    inspector = inspect(c); result = {}
    for name in (*TABLES, *BUSINESS):
        columns = inspector.get_columns(name, schema='public')
        relation = c.execute(text('SELECT oid::text,relkind,relpersistence,relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=to_regclass(:name)'), {'name': 'public.'+name}).one()
        if relation[1:] != ('r','p',False,False) or c.scalar(text('SELECT count(*) FROM pg_trigger WHERE tgrelid=to_regclass(:name) AND NOT tgisinternal'), {'name':'public.'+name}):
            raise EngineeringError('UNREVIEWED_HISTORY_RELATION', 409)
        result[name] = {'oid': relation[0], 'columns': [(x['name'],str(x['type']),x['nullable']) for x in columns],
                        'pk': inspector.get_pk_constraint(name, schema='public')['constrained_columns'],
                        'foreign_keys': inspector.get_foreign_keys(name, schema='public')}
    return json.loads(canonical(result))


def business(c):
    result = {}; metadata = MetaData()
    for name in BUSINESS:
        table = Table(name, metadata, autoload_with=c, schema='public')
        rows = [dict(r) for r in c.execute(select(table)).mappings()]
        result[name] = sorted(rows, key=canonical)
    return result


def history(c):
    return {n: [dict(r) for r in c.execute(select(t).order_by(*(t.c[k] for k in KEYS[n]))).mappings()] for n,t in TABLES.items()}


def write_snapshot(engine, path):
    """Caller must establish disposable target, grant and exclusive import lock."""
    path = Path(path).absolute()
    if path.exists() or path.parent.resolve() != path.parent or path.parent.stat().st_mode & 0o077:
        raise EngineeringError('NEW_PRIVATE_HISTORY_SNAPSHOT_REQUIRED', 409)
    with engine.begin() as c:
        c.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        value = {'schema':'NADI_COMPLETE_HISTORY_RECOVERY_V1', 'created_at':c.scalar(text('SELECT clock_timestamp()')).isoformat(),
                 'target':identity(c), 'migration_ledger':[dict(r) for r in c.execute(text('SELECT name,checksum FROM nadi_application_migration ORDER BY name')).mappings()], 'table_schema':schema(c), 'business':business(c), 'history':history(c)}
    value['content_hash'] = digest(value)
    data = (canonical(value)+'\n').encode()
    if len(data) > MAX_SNAPSHOT_BYTES: raise EngineeringError('HISTORY_RECOVERY_BOUND', 413)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
    if private_bytes(path) != data: raise EngineeringError('HISTORY_SNAPSHOT_READBACK_FAILED', 409)
    return {'path':str(path), 'sha256':sha256(data).hexdigest(), 'created_at':value['created_at'],
            'scope':'SEVEN_HISTORY_AND_SIX_BUSINESS_TABLES_NO_AUTH_SESSIONS', 'bytes':len(data)}


def validate_snapshot(c, path, expected_sha):
    data = private_bytes(path)
    if sha256(data).hexdigest() != expected_sha: raise EngineeringError('HISTORY_BACKUP_BYTES_CHANGED', 409)
    value = json.loads(data); content_hash = value.pop('content_hash')
    if value.get('schema') != 'NADI_COMPLETE_HISTORY_RECOVERY_V1' or digest(value) != content_hash or set(value.get('history',{})) != set(TABLES) or set(value.get('business',{})) != set(BUSINESS):
        raise EngineeringError('HISTORY_BACKUP_CONTENT_INVALID', 409)
    now = c.scalar(text('SELECT clock_timestamp()'))
    if not 0 <= (now-datetime.fromisoformat(value['created_at'])).total_seconds() <= 900:
        raise EngineeringError('FRESH_HISTORY_BACKUP_REQUIRED', 409)
    if value.get('migration_ledger') != [dict(r) for r in c.execute(text('SELECT name,checksum FROM nadi_application_migration ORDER BY name')).mappings()]: raise EngineeringError('HISTORY_MIGRATION_LEDGER_CHANGED',409)
    if value['target'] != identity(c) or value['table_schema'] != schema(c): raise EngineeringError('HISTORY_BACKUP_TARGET_CHANGED', 409)
    if value['business'] != business(c): raise EngineeringError('BUSINESS_CHANGED_REQUIRES_FRESH_BACKUP', 409)
    # Snapshot rows must remain byte-equivalent; never restore over later writes.
    for name, rows in value['history'].items():
        table = TABLES[name]
        for start in range(0, len(rows), 500):
            chosen = rows[start:start+500]; keys = KEYS[name]
            actual_rows = {tuple(r[k] for k in keys):dict(r) for r in c.execute(select(table).where(tuple_(*(table.c[k] for k in keys)).in_([tuple(r[k] for k in keys) for r in chosen]))).mappings()}
            for row in chosen:
                actual = actual_rows.get(tuple(row[k] for k in keys))
                if actual is None or canonical(actual) != canonical(row):
                    # Batch cursor/state is the deliberate mutable exception, bound by receipts.
                    if name != 'nadi_history_batch' or actual is None or any(actual[k] != row[k] for k in row if k not in {'cursor','state'}):
                        raise EngineeringError('HISTORY_BACKUP_PREIMAGE_CHANGED', 409)
    return value
