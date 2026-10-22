"""Qualification importer: disposable owning-store copies only, never live/demo.

One session advisory lock serializes history writers, while the current grant
guard is reacquired for every bounded transaction. No writer endpoint or DDL.
"""
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from hashlib import sha256
import stat
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json, os, re
from sqlalchemy import select, text, tuple_, update, func, inspect
from src.domain.engineering import Role, EngineeringError
from src.repositories.pdm_source_history import Source, Profile, Cell, Event, Alias, Batch, Receipt, TABLES, KEYS
from src.repositories.human_records import RevisionRow
from src.services.local_authentication import LocalIdentityProvider
from src.services.pdm_source_history import canonical, digest
from src.services.pdm_complete_plan import verify_plan, STREAMS
from src.services.pdm_history_staging import capture_event_key, event_key
from openpyxl.utils.cell import range_boundaries, coordinate_to_tuple

MAX_ROWS = 240000
MAX_BYTES = 96*1024*1024
LOCK_ID = 793245117
CHUNKS = {'sources': 1, 'profiles': 1, 'cells': 500, 'events': 25}


def target(engine):
    url = engine.url
    if (engine.dialect.name != 'postgresql' or url.query or url.host != '127.0.0.1' or
        url.port in {None, 5432, 15443} or not (url.database or '').startswith('pdm_history_complete_') or not url.database.endswith('_test')):
        raise EngineeringError('DISPOSABLE_COMPLETE_HISTORY_ONLY', 403)
    with engine.connect() as c:
        if c.scalar(text('SELECT current_database()')) != url.database:
            raise EngineeringError('COMPLETE_HISTORY_TARGET_CHANGED', 409)


def snapshot(c):
    return {name: [dict(r) for r in c.execute(select(table).order_by(*(table.c[k] for k in KEYS[name]))).mappings()] for name, table in TABLES.items()}


def budget(c):
    count = size = 0
    for table in TABLES.values():
        count += c.scalar(select(func.count()).select_from(table))
        for column in table.c:
            if column.type.__class__.__name__ == 'JSON':
                size += c.scalar(text('SELECT coalesce(sum(octet_length('+column.name+'::text)),0) FROM '+table.name))
    if count > MAX_ROWS or size > MAX_BYTES: raise EngineeringError('COMPLETE_HISTORY_STORAGE_BOUND', 409)
    return {'rows': count, 'json_bytes': size}


@contextmanager
def frozen_plan(directory, expected_plan_id):
    """Pin authenticated bytes before any DB mutation; never reopen source paths.

    Anonymous read-only descriptors survive replacement/mutation of the original
    plan. Closing the last descriptor destroys the private spool automatically.
    """
    manifest = verify_plan(directory)
    if manifest['plan_id'] != expected_plan_id:
        raise EngineeringError('EXACT_COMPLETE_PLAN_REQUIRED', 409)
    handles = {}
    with TemporaryDirectory(prefix='nadi-complete-plan-') as private:
        try:
            for name in STREAMS:
                fd = os.open(Path(directory)/(name+'.jsonl'), os.O_RDONLY | os.O_NOFOLLOW)
                path = Path(private)/name
                try:
                    info = os.fstat(fd)
                    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size > 128*1024*1024:
                        raise ValueError('PRIVATE_BOUNDED_PLAN_FILE_REQUIRED')
                    h = sha256(); copied = 0
                    with os.fdopen(fd, 'rb', closefd=False) as source, path.open('xb') as dest:
                        for block in iter(lambda: source.read(1024*1024), b''):
                            copied += len(block)
                            if copied > 128*1024*1024: raise ValueError('COMPLETE_PLAN_CONTENT_CHANGED')
                            h.update(block); dest.write(block)
                        dest.flush(); os.fsync(dest.fileno())
                    if copied != info.st_size or h.hexdigest() != manifest['stream_sha256'][name]:
                        raise ValueError('COMPLETE_PLAN_CONTENT_CHANGED')
                    path.chmod(0o400)
                    handles[name] = path.open('r', encoding='utf-8')
                    path.unlink()  # No writable name remains after authentication.
                finally:
                    os.close(fd)
            yield {'manifest': manifest, 'streams': handles}
        finally:
            for handle in handles.values(): handle.close()


def plan_lines(plan, name):
    stream = plan['streams'][name]; stream.seek(0)
    for line in stream:
        if len(line.encode()) > 128*1024: raise ValueError('COMPLETE_PLAN_ITEM_BOUND')
        yield json.loads(line)


def chunks(plan):
    sequence = 0
    for stage in STREAMS:
        pending = []
        for item in plan_lines(plan, stage):
            pending.append(item)
            if len(pending) == CHUNKS[stage]:
                yield sequence, stage, pending; sequence += 1; pending = []
        if pending:
            yield sequence, stage, pending; sequence += 1


def put(c, table, rows, *, require_existing=False):
    if not rows: return 0
    names = KEYS[table.name]
    wanted = {tuple(r[k] for k in names): r for r in rows}
    if len(wanted) != len(rows): raise EngineeringError('DUPLICATE_COMPLETE_CHUNK_KEY', 409)
    condition = tuple_(*(table.c[k] for k in names)).in_(list(wanted))
    existing = {tuple(r[k] for k in names): dict(r) for r in c.execute(select(table).where(condition)).mappings()}
    for key, row in existing.items():
        if canonical(row) != canonical(wanted[key]): raise EngineeringError('IMMUTABLE_HISTORY_CONFLICT', 409)
    new = [r for key, r in wanted.items() if key not in existing]
    if require_existing and new: raise EngineeringError('HISTORY_COMMITTED_ROWS_MISSING', 409)
    if new: c.execute(table.insert(), new)
    return len(new)


RECEIPT_SCHEMA = 'NADI_COMPLETE_HISTORY_CHUNK_RECEIPT_V2'


def checked_alias_proofs(links, allowed):
    """Bound and validate the exact immutable alias rows recorded at commit."""
    keys = {'event_key','record_id','revision','capture_hash','relation'}
    if not isinstance(links,list): raise EngineeringError('HISTORY_RECEIPT_ALIAS_PROOF_INVALID',409)
    for row in links:
        if (not isinstance(row,dict) or set(row)!=keys or not isinstance(row['event_key'],str) or row['event_key'] not in allowed or
            not isinstance(row['record_id'],str) or not 1<=len(row['record_id'])<=100 or
            type(row['revision']) is not int or not 1<=row['revision']<=2147483647 or
            not isinstance(row['capture_hash'],str) or not re.fullmatch('[0-9a-f]{64}',row['capture_hash']) or
            not isinstance(row['relation'],str) or row['relation'] not in {'SOURCE_COMPLETE','SOURCE_PARTIAL','SOURCE_CONFLICT'}):
            raise EngineeringError('HISTORY_RECEIPT_ALIAS_PROOF_INVALID',409)
    if len(canonical(links).encode())>128*1024: raise EngineeringError('HISTORY_ALIAS_CHUNK_BOUND',409)
    return links


class CompleteHistoryImporter:
    def __init__(self, inspections, provider):
        self.inspections, self.provider, self.engine = inspections, provider, inspections.repo.engine
        target(self.engine)
        if not isinstance(provider, LocalIdentityProvider) or provider.engine is not self.engine:
            raise EngineeringError('COMPLETE_OWNING_PROVIDER_REQUIRED', 403)
        with self.engine.connect() as c:
            if not set(TABLES) <= set(inspect(c).get_table_names()): raise EngineeringError('HISTORY_SCHEMA_PREREQUISITE', 503)

    def grant(self, subject, asset):
        grant = self.provider.current_grant(subject)
        if not grant or Role.AUTHOR not in grant.principal.roles or asset not in grant.principal.asset_ids:
            raise EngineeringError('FORBIDDEN', 403)
        self.inspections.gate(grant.principal)
        if not self.inspections.catalog.registered(asset): raise EngineeringError('NOT_FOUND', 404)
        return grant

    def aliases(self, c, profiles, actor):
        """Immutable revision anchors; never updates/replaces human records."""
        result = defaultdict(list)
        for row in c.execute(select(RevisionRow).where(RevisionRow.kind == 'INSPECTION')).mappings():
            capture = row['snapshot'].get('input_capture')
            if not capture: continue
            try: self.inspections.visible(actor, self.inspections.repo.get(c, 'INSPECTION', row['record_id']))
            except EngineeringError: continue
            profile = profiles.get((capture['source_ref'], capture['profile_id']))
            if not profile: raise EngineeringError('EXISTING_CAPTURE_PROFILE_UNRESOLVED', 409)
            directions = set()
            for value in capture['rows']:
                f = next((f for f in profile['fields'] if f['id'] == value['source_field_id']), None)
                if not f or not f.get('value_region'): raise EngineeringError('EXISTING_CAPTURE_COORDINATE_UNRESOLVED', 409)
                a,b,d,e = range_boundaries(f['value_region'])
                if a == d: directions.add('ROW')
                elif b == e: directions.add('COL')
            if len(directions) != 1: raise EngineeringError('EXISTING_CAPTURE_AXIS_UNRESOLVED', 409)
            key = capture_event_key(dict(capture, source_event_axis=next(iter(directions))))
            result[key].append({'record_id': row['record_id'], 'revision': row['revision'], 'capture': capture})
        return result

    def _rows(self, stage, items, subject, asset):
        if stage == 'sources': return Source, [{'source_sha': x['sha256'], 'document': x} for x in items]
        if stage == 'profiles':
            if any(digest(x['document']) != x['profile_hash'] for x in items): raise EngineeringError('PROFILE_PROOF_CHANGED', 409)
            return Profile, items
        if stage == 'cells': return Cell, [{'source_sha': x['source_sha256'], 'sheet_index': x['sheet_index'], 'coordinate': x['cell'], 'terminal_role': x['terminal_role'], 'claims': x['claims'], 'document': x['document']} for x in items]
        rows = []
        for item in items:
            if item['event_key'] != event_key(item['source_sha256'], item['sheet_index'], item['profile_id'], item['axis'], item['position']):
                raise EngineeringError('OCCURRENCE_IDENTITY_CHANGED', 409)
            rows.append({'event_key': item['event_key'], 'owner_id': subject, 'access_asset_id': asset, 'source_sha': item['source_sha256'],
                         **{k: item[k] for k in ('source_ref','sheet_index','profile_id','profile_hash','axis','position','classification_hash','document')},
                         'kind': item['document']['kind'], 'classification': item['document']['classification']})
        return Event, rows

    def _chunk(self, c, batch_id, sequence, stage, items, subject, asset, aliases):
        allowed = {item['event_key'] for item in items} if stage=='events' else set()
        receipt = c.execute(select(Receipt).where(Receipt.c.batch_id == batch_id, Receipt.c.sequence == sequence)).mappings().first()
        if receipt:
            if receipt['document'].get('schema')!=RECEIPT_SCHEMA:
                raise EngineeringError('HISTORY_RECEIPT_ALIAS_PROOF_INVALID',409)
            links=checked_alias_proofs(receipt['document'].get('alias_proofs'),allowed)
            fingerprint=digest([batch_id,sequence,stage,items,links])
            if receipt['fingerprint'] != fingerprint or receipt['actor'] != subject: raise EngineeringError('HISTORY_RECEIPT_CONFLICT', 409)
            table, rows = self._rows(stage, items, subject, asset)
            put(c, table, rows, require_existing=True)
            put(c, Alias, links, require_existing=True)
            return dict(receipt['document'], replayed=True)
        batch = c.execute(select(Batch).where(Batch.c.batch_id == batch_id).with_for_update()).mappings().one()
        if (batch['cursor'], batch['owner_id'], batch['access_asset_id'], batch['state']) != (sequence, subject, asset, 'IMPORTING'):
            raise EngineeringError('HISTORY_CURSOR_CONFLICT', 409)
        table, rows = self._rows(stage, items, subject, asset)
        inserted = put(c, table, rows); links = []
        if stage == 'events':
            for item in items:
                for anchor in aliases.get(item['event_key'], []):
                    capture = anchor['capture']; original = {r['value_region']: (r['raw_value'], r['unit']) for r in capture['rows']}
                    profile = c.scalar(select(Profile.c.document).where(Profile.c.profile_hash == item['profile_hash']))
                    metadata = {f['id']: f for f in profile['fields']}; fields = {r['cell']: metadata.get(r['field_id'], {}).get('unit') for r in item['document']['fields'] if r['role'] == 'INPUT'}
                    values = {r['coordinate']: r['document'].get('raw_value') for r in c.execute(select(Cell).where(Cell.c.source_sha == item['source_sha256'], Cell.c.sheet_index == item['sheet_index'], Cell.c.coordinate.in_(original))).mappings()}
                    # The complete physical census omits only blank/non-formula cells.
                    # A catalog-referenced absent cell therefore matches captured null,
                    # while numeric zero and Boolean false remain distinct typed JSON.
                    match = all(coordinate in fields and canonical(values.get(coordinate)) == canonical(value) and canonical(fields[coordinate]) == canonical(unit) for coordinate, (value, unit) in original.items())
                    relation = 'SOURCE_CONFLICT' if not match else 'SOURCE_COMPLETE' if set(original) == set(fields) else 'SOURCE_PARTIAL'
                    links.append({'event_key': item['event_key'], 'record_id': anchor['record_id'], 'revision': anchor['revision'], 'capture_hash': digest(capture), 'relation': relation})
        checked_alias_proofs(links,allowed)
        linked = put(c, Alias, links)
        fingerprint=digest([batch_id,sequence,stage,items,links])
        result = {'schema':RECEIPT_SCHEMA,'stage': stage, 'items': len(items), 'inserted': inserted,
                  'aliases_added': linked,'alias_proofs':links,'replayed': False}
        c.execute(Receipt.insert().values(batch_id=batch_id, sequence=sequence, actor=subject,
                  occurred_at=datetime.now(timezone.utc).isoformat(), fingerprint=fingerprint, document=result))
        c.execute(update(Batch).where(Batch.c.batch_id == batch_id, Batch.c.cursor == sequence).values(cursor=sequence+1))
        return result

    def run(self, directory, subject, *, access_asset_id, expected_plan_id, source_paths, recovery_snapshot, expected_snapshot_sha256, max_chunks=None, after_commit=None):
        with frozen_plan(directory, expected_plan_id) as plan:
            return self._run(plan, subject, access_asset_id=access_asset_id, expected_plan_id=expected_plan_id,
                             source_paths=source_paths, recovery_snapshot=recovery_snapshot,
                             expected_snapshot_sha256=expected_snapshot_sha256, max_chunks=max_chunks, after_commit=after_commit)

    def _run(self, plan, subject, *, access_asset_id, expected_plan_id, source_paths, recovery_snapshot, expected_snapshot_sha256, max_chunks, after_commit):
        target(self.engine); manifest = plan['manifest']
        if max_chunks is not None and (type(max_chunks) is not int or not 1 <= max_chunks <= 10000): raise ValueError('BOUNDED_CHUNKS_REQUIRED')
        source_meta = list(plan_lines(plan, 'sources'))
        if set(source_paths) != {s['sha256'] for s in source_meta}: raise EngineeringError('SOURCE_FILE_BINDING_REQUIRED', 409)
        def verify_sources():
            from hashlib import sha256
            if any(Path(source_paths[s['sha256']]).is_symlink() or Path(source_paths[s['sha256']]).suffix.lower() not in {'.xls','.xlsx'} or not 0<Path(source_paths[s['sha256']]).stat().st_size<=32*1024*1024 or sha256(Path(source_paths[s['sha256']]).read_bytes()).hexdigest() != s['sha256'] for s in source_meta):
                raise EngineeringError('ORIGINAL_WORKBOOK_CHANGED', 409)
        verify_sources()
        profiles = {(p['document']['source_ref'],p['document']['id']): p['document'] for p in plan_lines(plan, 'profiles')}
        batch_id = digest([expected_plan_id, subject, access_asset_id])
        with self.engine.connect() as lock:
            if not lock.scalar(text('SELECT pg_try_advisory_lock(:id)'), {'id': LOCK_ID}): raise EngineeringError('HISTORY_IMPORT_BUSY', 409)
            try:
                grant = self.grant(subject, access_asset_id)
                with self.provider.guard(subject, grant.version), self.engine.begin() as c:
                    from src.services.pdm_history_recovery import validate_snapshot
                    recovery = validate_snapshot(c, recovery_snapshot, expected_snapshot_sha256)
                    if c.scalar(select(func.count()).select_from(Event).where(Event.c.source_sha.in_([s['sha256'] for s in source_meta]), (Event.c.owner_id != subject) | (Event.c.access_asset_id != access_asset_id))): raise EngineeringError('SOURCE_CUSTODY_CONFLICT',409)
                    baseline_batches={r['batch_id'] for r in recovery['history']['nadi_history_batch']}
                    actual_batches=set(c.scalars(select(Batch.c.batch_id)))
                    if actual_batches-baseline_batches-{batch_id}: raise EngineeringError('HISTORY_NEW_BATCH_REQUIRES_FRESH_BACKUP',409)
                    put(c, Batch, [{'batch_id': batch_id, 'owner_id': subject, 'access_asset_id': access_asset_id, 'manifest': manifest, 'cursor': 0, 'state': 'IMPORTING'}]) if not c.scalar(select(Batch.c.batch_id).where(Batch.c.batch_id == batch_id)) else None
                    batch = c.execute(select(Batch).where(Batch.c.batch_id == batch_id)).mappings().one()
                    if batch['manifest'] != manifest or batch['owner_id'] != subject or batch['access_asset_id'] != access_asset_id: raise EngineeringError('BATCH_BINDING_CHANGED', 409)
                    initial = budget(c); anchors = self.aliases(c, profiles, grant.principal)
                # Conservative upper bound for the whole remaining append-only plan.
                remaining_bytes = remaining_rows = remaining_chunks = 0
                for seq, stage, items in chunks(plan):
                    if seq >= batch['cursor']:
                        remaining_rows += len(items); remaining_chunks += 1
                        remaining_bytes += len(canonical(items).encode())
                if initial['rows']+remaining_rows+remaining_chunks+sum(map(len,anchors.values())) > MAX_ROWS or initial['json_bytes']+remaining_bytes+remaining_chunks*2048+sum(map(len,anchors.values()))*1024 > MAX_BYTES:
                    raise EngineeringError('COMPLETE_HISTORY_STORAGE_BOUND', 409)
                completed = replayed = 0; last = None
                for sequence, stage, items in chunks(plan):
                    grant = self.grant(subject, access_asset_id)
                    with self.provider.guard(subject, grant.version), self.engine.begin() as c:
                        age=c.scalar(text('SELECT clock_timestamp()'))-datetime.fromisoformat(recovery['created_at'])
                        if not 0<=age.total_seconds()<=900: raise EngineeringError('FRESH_HISTORY_BACKUP_REQUIRED',409)
                        c.execute(text("SET LOCAL lock_timeout='5s'")); c.execute(text("SET LOCAL statement_timeout='30s'"))
                        result = self._chunk(c, batch_id, sequence, stage, items, subject, access_asset_id, anchors)
                    last = sequence
                    if result['replayed']: replayed += 1
                    else:
                        completed += 1
                        if after_commit: after_commit(sequence, result)  # Lost ACK: authoritative receipt/cursor remains.
                    if max_chunks and completed >= max_chunks: break
                verify_sources()
                total_chunks = sum(1 for _ in chunks(plan))
                grant = self.grant(subject, access_asset_id)
                with self.provider.guard(subject, grant.version), self.engine.begin() as c:
                    state = c.execute(select(Batch).where(Batch.c.batch_id == batch_id).with_for_update()).mappings().one()
                    if state['cursor'] == total_chunks:
                        c.execute(update(Batch).where(Batch.c.batch_id == batch_id).values(state='COMPLETE'))
                    final = budget(c)
                return {'batch_id': batch_id, 'committed_chunks': completed, 'replayed_chunks': replayed,
                        'cursor': state['cursor'], 'total_chunks': total_chunks, 'complete': state['cursor'] == total_chunks,
                        'budget': final, 'scope': 'DISPOSABLE_SOURCE_HISTORY_ONLY_NO_CANONICAL_PROMOTION'}
            finally:
                lock.execute(text('SELECT pg_advisory_unlock(:id)'), {'id': LOCK_ID})
