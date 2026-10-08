"""Manual pilot coordinator: trusted local handoff, private journal, no PI client.

No HTTP entrypoint, approval mutation, timer or retry. Source credentials belong
only to an operator-owned Collector launcher, never this process.
"""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from src.domain.condition_evidence import EvidenceBatch, FreshnessPolicy

PILOT_ASSET = "asset:MAXIMO:MXASSET:BSR:IP:CS10HFB01AF001-001"
MAX_BYTES = 262144

class RefreshError(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

def private_read(path, limit=MAX_BYTES):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as f:
        info = os.fstat(f.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise RefreshError('PRIVATE_ARTIFACT_REQUIRED')
        data = f.read(limit+1)
        if len(data) > limit:
            raise RefreshError('ARTIFACT_TOO_LARGE')
        return data

def private_write(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())

def aware_clock(clock):
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise RefreshError('INVALID_CLOCK')
    return value.astimezone(timezone.utc)

def validate_chronology(batch, now):
    if batch.collector_last_success_at is not None and batch.collector_last_success_at > now:
        raise RefreshError('FUTURE_COLLECTOR_SUCCESS')
    for result in batch.results:
        if result.evidence is None:
            continue
        e = result.evidence
        if e.collected_at > now:
            raise RefreshError('FUTURE_COLLECTION')
        if e.source_timestamp is not None:
            if e.source_timestamp > now:
                raise RefreshError('FUTURE_SOURCE')
            if e.source_timestamp > e.collected_at:
                raise RefreshError('CLOCK_CONTRADICTION')
            if e.source_timestamp <= datetime(1970, 1, 1, tzinfo=timezone.utc):
                raise RefreshError('EPOCH_SOURCE_TIMESTAMP')

@dataclass(frozen=True)
class SourceHandoff:
    batch: EvidenceBatch
    source_gets: int

class CollectorLauncherSource:
    """Pinned executable local launcher with sanitized env and inherited host lock.

    Launcher must exec the Collector CLI locally, not daemonize or dispatch to a
    remote/Docker daemon. It loads only Collector-owned source config itself.
    """
    def __init__(self, launcher, sha256, *, timeout_seconds=600):
        self.launcher = Path(launcher)
        if not self.launcher.is_absolute() or self.launcher.is_symlink():
            raise RefreshError('TRUSTED_LAUNCHER_REQUIRED')
        info = self.launcher.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022 or not info.st_mode & 0o100:
            raise RefreshError('TRUSTED_LAUNCHER_REQUIRED')
        self.sha256 = sha256
        if hashlib.sha256(self.launcher.read_bytes()).hexdigest() != sha256:
            raise RefreshError('LAUNCHER_CHECKSUM_MISMATCH')
        self.timeout_seconds = timeout_seconds

    def collect(self, plan, directory, lock_fd):
        if hashlib.sha256(self.launcher.read_bytes()).hexdigest() != self.sha256:
            raise RefreshError('LAUNCHER_CHECKSUM_MISMATCH')
        output, report = directory/'handoff.json', directory/'receipt.json'
        command = [str(self.launcher), 'condition-evidence', '--plan-file', str(directory/'plan.json'),
                   '--execute', '--output', str(output), '--max-source-gets', '5', '--report-file', str(report)]
        # Never forward admin DSNs, PI/Maximo secrets, PYTHONPATH, proxies or .netrc.
        env = {'PATH': '/usr/bin:/bin', 'PI_CONFIG_MODE': 'managed'}
        with subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              start_new_session=True, pass_fds=(lock_fd,)) as process:
            try:
                code = process.wait(timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise RefreshError('SOURCE_TIMEOUT') from None
        if code != 0:
            raise RefreshError('SOURCE_PROCESS_FAILED')
        receipt = json.loads(private_read(report))
        if (set(receipt) != {'contract_version','source_gets','max_source_gets','handoff_sha256'}
            or receipt['contract_version'] != '1.0' or type(receipt['source_gets']) is not int
            or not 0 <= receipt['source_gets'] <= 5 or type(receipt['max_source_gets']) is not int
            or receipt['max_source_gets'] != 5):
            raise RefreshError('SOURCE_RECEIPT_INVALID')
        raw = private_read(output)
        if hashlib.sha256(raw).hexdigest() != receipt['handoff_sha256']:
            raise RefreshError('HANDOFF_CHECKSUM_MISMATCH')
        batch = EvidenceBatch.model_validate_json(raw)
        if batch.plan != plan:
            raise RefreshError('HANDOFF_PLAN_MISMATCH')
        return SourceHandoff(batch, receipt['source_gets'])

class ConditionRefreshRunner:
    def __init__(self, store, directory, baseline_file, baseline_sha256, *, source=None, policy=None, clock=None, lock_directory=None):
        self.store, self.source = store, source
        self.directory = Path(directory).absolute()
        self.policy = policy if policy is not None else FreshnessPolicy.from_environment()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        raw = private_read(baseline_file)
        if hashlib.sha256(raw).hexdigest() != baseline_sha256:
            raise RefreshError('BASELINE_CHECKSUM_MISMATCH')
        self.baseline = EvidenceBatch.model_validate_json(raw)
        plan = self.baseline.plan
        if plan.canonical_asset_id != PILOT_ASSET or len(plan.signals) != 1 or plan.signals[0].semantic_name != 'coal_flow':
            raise RefreshError('PILOT_SCOPE_MISMATCH')
        # One fixed lock scope per operator host, even with different journals.
        self.lock_directory = Path(lock_directory) if lock_directory else Path.home()/'.local/state/nadi-coal-flow-refresh'
        self.lock_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        lock_info = self.lock_directory.lstat()
        if not stat.S_ISDIR(lock_info.st_mode) or lock_info.st_uid != os.getuid() or lock_info.st_mode & 0o077:
            raise RefreshError('PRIVATE_LOCK_DIRECTORY_REQUIRED')
        if (len(self.baseline.results) != 1 or self.baseline.results[0].evidence is None
            or self.baseline.results[0].evidence.value_type != 'NUMERIC'
            or self.baseline.results[0].evidence.unit != 'Ton/h'
            or self.baseline.results[0].evidence.evidence_status != 'EVIDENCE_AVAILABLE'):
            raise RefreshError('ACCEPTED_BASELINE_REQUIRED')
        self.directory.mkdir(mode=0o700, parents=False, exist_ok=True)
        info = self.directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise RefreshError('PRIVATE_DIRECTORY_REQUIRED')

    @contextmanager
    def lock(self):
        fd = os.open(self.lock_directory/'refresh.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise RefreshError('PRIVATE_LOCK_REQUIRED')
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RefreshError('REFRESH_LOCK_BUSY') from None
            yield fd
        finally:
            os.close(fd)

    def journal(self):
        path = self.directory/'journal.jsonl'
        if not path.exists():
            return []
        raw = private_read(path, 1048576)
        records = [json.loads(line) for line in raw.splitlines()]
        if any(type(r) is not dict or not {'attempt_id','event','at'} <= r.keys() for r in records):
            raise RefreshError('JOURNAL_INVALID')
        times = [datetime.fromisoformat(r['at']) for r in records]
        if any(t.tzinfo is None for t in times) or times != sorted(times):
            raise RefreshError('JOURNAL_CLOCK_CONTRADICTION')
        return records

    def append(self, attempt_id, event, **fields):
        now = aware_clock(self.clock)
        previous = self.journal()
        if previous and now < datetime.fromisoformat(previous[-1]['at']):
            raise RefreshError('JOURNAL_CLOCK_CONTRADICTION')
        fd = os.open(self.directory/'journal.jsonl', os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as f:
            info = os.fstat(f.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise RefreshError('PRIVATE_JOURNAL_REQUIRED')
            f.write(json.dumps({'attempt_id':attempt_id,'event':event,'at':now.isoformat(),**fields},sort_keys=True)+'\n')
            f.flush(); os.fsync(f.fileno())

    def pending_writes(self):
        """A durable intent without a receipt is an uncertain commit, not a retry."""
        records = self.journal()
        completed = {r.get('reconciles_attempt', r['attempt_id']) for r in records
                     if r['event'] in {'ACCEPTED', 'REPLAYED', 'IGNORED_OLDER_BATCH', 'RECONCILED'}}
        return [r for r in records if r['event'] == 'WRITER_STARTED' and r['attempt_id'] not in completed]

    def summary(self):
        records = self.journal()
        def last(event):
            return next((r['at'] for r in reversed(records) if r['event']==event),None)
        return {'last_attempt_at':last('STARTED'),'last_acquisition_success_at':last('ACQUIRED'),
                'last_evidence_success_at':last('ACCEPTED'),'last_failure_at':last('FAILED'),
                'last_replay_at':last('REPLAYED'),
                'uncertain_writer_attempts': [r['attempt_id'] for r in self.pending_writes()]}

    def run(self, attempt_id, *, execute=False, authorization_ref=None, replay_file=None):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',attempt_id):
            raise RefreshError('INVALID_ATTEMPT_ID')
        if execute and (not authorization_ref or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9:_./-]{0,199}',authorization_ref)):
            raise RefreshError('EXECUTION_AUTHORIZATION_REQUIRED')
        with self.store.refresh_lease(PILOT_ASSET), self.lock() as fd:
            if any(r['attempt_id']==attempt_id for r in self.journal()):
                raise RefreshError('DUPLICATE_ATTEMPT')
            pending = self.pending_writes()
            if pending and not replay_file:
                raise RefreshError('WRITER_OUTCOME_UNKNOWN')
            folder = self.directory/attempt_id
            folder.mkdir(mode=0o700)
            self.append(attempt_id,'STARTED',mode='REPLAY' if replay_file else 'REFRESH',authorization_ref=authorization_ref)
            phase, gets = 'PLAN', None
            try:
                plan = self.store.plan(PILOT_ASSET)
                if plan != self.baseline.plan:
                    raise RefreshError('IDENTITY_OR_APPROVAL_CHANGED')
                private_write(folder/'plan.json',plan.model_dump_json(indent=2))
                if not execute:
                    self.append(attempt_id,'DRY_RUN',source_gets=0)
                    return {'status':'DRY_RUN','source_gets':0,'written':0}
                phase = 'HANDOFF'
                if replay_file:
                    batch = EvidenceBatch.model_validate_json(private_read(replay_file)); gets = 0
                else:
                    if self.source is None:
                        raise RefreshError('COLLECTOR_LAUNCHER_REQUIRED')
                    handoff = self.source.collect(plan,folder,fd)
                    batch = EvidenceBatch.model_validate(handoff.batch.model_dump(mode='json'))
                    gets = handoff.source_gets
                    if type(gets) is not int or not 0 <= gets <= 5:
                        raise RefreshError('SOURCE_BUDGET_VIOLATION')
                if batch.plan != plan or len(batch.results)!=1:
                    raise RefreshError('HANDOFF_PLAN_MISMATCH')
                batch_hash = hashlib.sha256(batch.model_dump_json().encode()).hexdigest()
                if pending and any(r['handoff_sha256'] != batch_hash for r in pending):
                    raise RefreshError('RECONCILIATION_HANDOFF_MISMATCH')
                result = batch.results[0]; e = result.evidence
                if e is None:
                    raise RefreshError('SOURCE_UNAVAILABLE')
                if not replay_file:
                    self.append(attempt_id,'ACQUIRED',source_gets=gets)
                validate_chronology(batch,aware_clock(self.clock))
                if e.evidence_status!='EVIDENCE_AVAILABLE':
                    raise RefreshError('QUALITY_OR_VALUE_NOT_ACCEPTED')
                reference = self.baseline.results[0].evidence
                if reference is None or e.value_type not in {'NUMERIC','NULL'} or e.unit != reference.unit:
                    raise RefreshError('SIGNAL_TYPE_OR_UNIT_CHANGED')
                if not replay_file:
                    if self.policy.state('SOURCE',e.source_timestamp,aware_clock(self.clock),component='PI_CONDITION_PROJECTION')=='SOURCE_STALE':
                        raise RefreshError('SOURCE_STALE')
                # Journal and Mart cannot share a transaction. Persist intent first;
                # a lost commit receipt blocks further acquisition pending strict replay.
                self.append(attempt_id, 'WRITER_STARTED', handoff_sha256=batch_hash, source_gets=gets)
                phase = 'WRITER'
                # Canonical transaction re-resolves and locks governance again.
                result = self.store.project(batch,now=aware_clock(self.clock),replay_only=bool(replay_file))
                if result['written'] == 0:
                    event = 'IGNORED_OLDER_BATCH' if result['status']=='IGNORED_OLDER_BATCH' else 'REPLAYED'
                    self.append(attempt_id,event,source_gets=gets,written=0)
                    for intent in pending:
                        self.append(attempt_id, 'RECONCILED', reconciles_attempt=intent['attempt_id'],
                                    source_gets=0, written=0)
                    return {'status':event,'source_gets':gets,'written':0}
                self.append(attempt_id,'ACCEPTED',source_gets=gets,written=result['written'],
                            collector_success_known=batch.collector_last_success_at is not None,
                            source_freshness=self.policy.state('SOURCE',e.source_timestamp,aware_clock(self.clock),component='PI_CONDITION_PROJECTION'))
                return {'status':'ACCEPTED','source_gets':gets,'written':result['written']}
            except Exception as error:
                reason = error.reason if isinstance(error,RefreshError) else 'WRITER_FAILED' if phase=='WRITER' else 'REFRESH_FAILED'
                try:
                    self.append(attempt_id,'FAILED',phase=phase,reason=reason,source_gets=gets)
                except Exception:
                    # Existing durable intent still records an unknown writer outcome.
                    # Never expose raw filesystem/DB errors or retry the source.
                    reason = 'WRITER_OUTCOME_UNKNOWN' if phase == 'WRITER' else 'JOURNAL_FAILED'
                raise RefreshError(reason) from None
