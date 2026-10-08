"""Synthetic manual runner acceptance; real sources are never contacted."""
import copy, hashlib, json, os, sys, tempfile, unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from src.cli import parse_args
from src.domain.condition_evidence import EvidenceBatch, FreshnessPolicy
from src.repositories.condition_models import ConditionEvidenceLatestMart, ConditionProjectionStateMart, ConditionSignalSelectionMart
from src.repositories.condition_store import ConditionCommandStore, ProjectionGateError
from src.repositories.mart_models import AssetAfMappingMart
from src.services.condition_query import ConditionQueryService
from src.services.condition_refresh import ConditionRefreshRunner, CollectorLauncherSource, RefreshError, SourceHandoff, private_write
import test_condition_evidence as fixture
NOW, ASSET = fixture.NOW, fixture.ASSET_ID

class RefreshTest(unittest.TestCase):
    approve=fixture.ConditionProjectionTest.approve
    reader=fixture.ConditionProjectionTest.reader
    source_document=fixture.ConditionProjectionTest.source_document
    project=fixture.ConditionProjectionTest.project
    def setUp(self):
        fixture.ConditionProjectionTest.setUp(self)
        self.patch=patch('src.services.condition_refresh.PILOT_ASSET',ASSET);self.patch.start()
        with Session(self.engine) as s,s.begin():
            row=s.get(ConditionSignalSelectionMart,'synthetic-current');row.definition={**row.definition,'semantic_name':'coal_flow'}
        self.baseline=self.source_document({'coal_flow':{'UnitsAbbreviation':'Ton/h'}});self.project(self.baseline)
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.file=self.root/'baseline.json';private_write(self.file,json.dumps(self.baseline));self.sha=hashlib.sha256(self.file.read_bytes()).hexdigest()
        self.now=NOW+timedelta(seconds=20);self.document=copy.deepcopy(self.baseline);self.document['collector_last_success_at']=None
        e=self.document['results'][0]['evidence'];e.update(collected_at=(NOW+timedelta(seconds=10)).isoformat(),source_timestamp=(NOW+timedelta(seconds=5)).isoformat(),value=13.5)
        self.source=Mock()
        def collect(plan,directory,fd):
            private_write(directory/'handoff.json',json.dumps(self.document))
            return SourceHandoff(EvidenceBatch.model_validate(self.document),5)
        self.source.collect.side_effect=collect
    def tearDown(self):self.patch.stop();self.tmp.cleanup();self.engine.dispose()
    def runner(self,source=None,policy=None,directory=None):
        return ConditionRefreshRunner(self.store,directory or self.root/'journal',self.file,self.sha,source=source or self.source,
            policy=policy or FreshnessPolicy(),clock=lambda:self.now,lock_directory=self.root/'locks')
    def execute(self,r=None,attempt='run-1',**kw):return (r or self.runner()).run(attempt,execute=True,authorization_ref='SYNTHETIC-ONLY',**kw)
    def snapshot(self):
        with Session(self.engine) as s:
            e=s.get(ConditionEvidenceLatestMart,'synthetic-current');p=s.get(ConditionProjectionStateMart,ASSET)
            return copy.deepcopy((e.evidence,e.collected_at,e.projected_at,p.state,p.attempted_at))
    def test_dry_run_and_separate_authorization(self):
        old=self.snapshot();r=self.runner();self.assertEqual(r.run('dry')['status'],'DRY_RUN');self.source.collect.assert_not_called()
        self.assertEqual(old,self.snapshot())
        with self.assertRaisesRegex(RefreshError,'EXECUTION_AUTHORIZATION_REQUIRED'):r.run('unapproved',execute=True)
        args=parse_args(['condition','refresh','--state-directory','/tmp/private','--baseline-file','/tmp/b','--baseline-sha256','a'*64,'--attempt-id','dry'])
        self.assertFalse(args.execute)
    def test_single_numeric_unknown_collector_preserved(self):
        result=self.execute();self.assertEqual((result['source_gets'],result['written']),(5,1))
        view=ConditionQueryService(self.reader(),policy=FreshnessPolicy(pi_collector_max_age_seconds=60),clock=lambda:self.now).asset_evidence(ASSET)
        self.assertEqual((view.items[0].evidence.value,view.items[0].evidence.unit),(13.5,'Ton/h'))
        self.assertIsNone(view.collector_last_success_at);self.assertEqual(view.items[0].freshness.collector,'COLLECTOR_UNKNOWN')
    def test_unavailable_bad_and_null_preserve_exact_accepted_rows(self):
        for mode in ['unavailable','bad','null']:
            old=self.snapshot();self.document=copy.deepcopy(self.baseline)
            e=self.document['results'][0]['evidence']
            if mode=='unavailable':self.document['results'][0]={'signal_id':'synthetic-current','status':'SOURCE_UNAVAILABLE','evidence':None}
            elif mode=='bad':e.update(quality_good=False,evidence_status='BAD_QUALITY')
            else:e.update(value=None,value_type='NULL',evidence_status='UNKNOWN_VALUE')
            r=self.runner()
            with self.assertRaises(RefreshError):self.execute(r,attempt=mode)
            self.assertEqual(old,self.snapshot());self.assertIsNotNone(r.summary()['last_failure_at']);self.assertIsNone(r.summary()['last_evidence_success_at'])
            saved=json.loads((self.root/'journal'/mode/'handoff.json').read_text())
            self.assertEqual(saved,self.document)
            self.assertEqual(r.summary()['last_acquisition_success_at'] is not None, mode != 'unavailable')
    def test_epoch_future_and_chronology_rejected(self):
        for attempt,timestamp,reason in [('epoch','1970-01-01T00:00:00Z','EPOCH_SOURCE_TIMESTAMP'),
          ('future',(NOW+timedelta(seconds=21)).isoformat(),'FUTURE_SOURCE'),('clock',(NOW+timedelta(seconds=11)).isoformat(),'CLOCK_CONTRADICTION')]:
            old=self.snapshot();self.document['results'][0]['evidence']['source_timestamp']=timestamp
            with self.assertRaisesRegex(RefreshError,reason):self.execute(attempt=attempt)
            self.assertEqual(old,self.snapshot())
    def test_stale_source_and_future_collection_rejected(self):
        old=self.snapshot();self.document['results'][0]['evidence']['source_timestamp']=(NOW-timedelta(seconds=61)).isoformat()
        with self.assertRaisesRegex(RefreshError,'SOURCE_STALE'):self.execute(self.runner(policy=FreshnessPolicy(condition_source_max_age_seconds=60)),attempt='stale')
        self.assertEqual(old,self.snapshot())
        self.document['results'][0]['evidence']['collected_at']=(self.now+timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(RefreshError,'FUTURE_COLLECTION'):self.execute(attempt='future-collection')
        self.assertEqual(old,self.snapshot())
    def test_retired_and_conflicting_identity_stop_before_source(self):
        from src.repositories.asset_af_mapping_store import AssetAfMappingCommandStore
        AssetAfMappingCommandStore(self.engine).retire(self.mapping_id,retired_by='synthetic-reviewer',retirement_note='synthetic-only')
        with self.assertRaises(RefreshError):self.execute(attempt='retired')
        self.source.collect.assert_not_called()
        with Session(self.engine) as s,s.begin():
            row=s.get(AssetAfMappingMart,self.mapping_id);row.mapping_status='VERIFIED';row.retired_at=None;row.retired_by=None;row.retirement_note=None
            row=s.get(ConditionSignalSelectionMart,'synthetic-current');d=copy.deepcopy(row.definition);d['sources']['pi']['attribute_ref']='DIFFERENT-SYNTHETIC';row.definition=d
        with self.assertRaisesRegex(RefreshError,'IDENTITY_OR_APPROVAL_CHANGED'):self.execute(attempt='conflict')
        self.source.collect.assert_not_called()
    def test_duplicate_attempt_and_shared_lock(self):
        r=self.runner();self.execute(r)
        with self.assertRaisesRegex(RefreshError,'DUPLICATE_ATTEMPT'):self.execute(r)
        other=self.runner(directory=self.root/'other')
        with r.lock():
            with self.assertRaisesRegex(RefreshError,'REFRESH_LOCK_BUSY'):self.execute(other)
        self.assertEqual(self.source.collect.call_count,1)
    def test_writer_failure_keeps_rows_private_journal_no_secrets(self):
        old=self.snapshot();r=self.runner()
        with patch.object(self.store,'project',side_effect=RuntimeError('password=secret PI_URL secret')):
            with self.assertRaisesRegex(RefreshError,'WRITER_FAILED'):self.execute(r)
        self.assertEqual(old,self.snapshot());text=(self.root/'journal/journal.jsonl').read_text()
        self.assertNotIn('secret',text);self.assertNotIn('13.5',text)
        self.assertEqual((self.root/'journal/journal.jsonl').stat().st_mode & 0o777,0o600)
    def test_replay_no_new_success_or_freshness(self):
        r=self.runner();self.execute(r);old=self.snapshot();summary=r.summary();self.now+=timedelta(seconds=100)
        result=self.execute(r,attempt='replay',replay_file=self.root/'journal/run-1/handoff.json')
        self.assertEqual(result,{'status':'REPLAYED','source_gets':0,'written':0});self.assertEqual(old,self.snapshot())
        self.assertEqual(self.source.collect.call_count,1);self.assertEqual(summary['last_evidence_success_at'],r.summary()['last_evidence_success_at'])
        view=ConditionQueryService(self.reader(),policy=FreshnessPolicy(condition_projection_max_age_seconds=60),clock=lambda:self.now).asset_evidence(ASSET)
        self.assertEqual(view.items[0].freshness.projection,'PROJECTION_STALE')
    def test_changed_replay_and_projection_chronology_rejected(self):
        old=self.snapshot();bad=copy.deepcopy(self.baseline);bad['results'][0]['evidence']['value']=999
        path=self.root/'bad.json';private_write(path,json.dumps(bad))
        with self.assertRaises(RefreshError):self.execute(attempt='bad-replay',replay_file=path)
        self.assertEqual(old,self.snapshot())
        with Session(self.engine) as s,s.begin():s.get(ConditionEvidenceLatestMart,'synthetic-current').projected_at=NOW-timedelta(seconds=1)
        altered=self.snapshot()
        with self.assertRaises(RefreshError):self.execute(attempt='clock-replay',replay_file=self.file)
        self.assertEqual(altered,self.snapshot())
    def test_lost_commit_receipt_blocks_new_acquisition_until_strict_replay(self):
        r = self.runner()
        append = r.append
        def lose_receipt(attempt, event, **fields):
            if event == 'ACCEPTED':
                raise OSError('synthetic disk failure')
            return append(attempt, event, **fields)
        with patch.object(r, 'append', side_effect=lose_receipt):
            with self.assertRaises(RefreshError):
                self.execute(r)
        accepted = self.snapshot()
        self.assertEqual(r.summary()['uncertain_writer_attempts'], ['run-1'])
        with self.assertRaisesRegex(RefreshError, 'WRITER_OUTCOME_UNKNOWN'):
            self.execute(r, attempt='must-not-retry')
        self.assertEqual(self.source.collect.call_count, 1)
        self.assertEqual(self.execute(r, attempt='reconcile', replay_file=self.root/'journal/run-1/handoff.json')['status'], 'REPLAYED')
        self.assertEqual(accepted, self.snapshot())
        self.assertIsNone(r.summary()['last_evidence_success_at'])
        self.assertEqual(r.summary()['uncertain_writer_attempts'], [])

    def test_over_budget_receipt_cannot_reach_writer(self):
        old = self.snapshot()
        self.source.collect.side_effect = lambda *args: SourceHandoff(EvidenceBatch.model_validate(self.document), 6)
        with self.assertRaisesRegex(RefreshError, 'SOURCE_BUDGET_VIOLATION'):
            self.execute()
        self.assertEqual(old, self.snapshot())

    def test_future_collector_completion_rejected_without_relabeling(self):
        old = self.snapshot()
        self.document['collector_last_success_at'] = (self.now + timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(RefreshError, 'FUTURE_COLLECTOR_SUCCESS'):
            self.execute()
        self.assertEqual(old, self.snapshot())

    def test_governance_changed_during_source_is_rejected(self):
        old = self.snapshot()
        collect = self.source.collect.side_effect
        def retire_during_read(plan, directory, fd):
            handoff = collect(plan, directory, fd)
            self.store.retire_signal('synthetic-current')
            return handoff
        self.source.collect.side_effect = retire_during_read
        with self.assertRaisesRegex(RefreshError, 'WRITER_FAILED'):
            self.execute()
        self.assertEqual(old, self.snapshot())

    def test_local_launcher_receipt_env_and_checksum(self):
        private_write(self.root/'seed.json',json.dumps(self.document));launcher=self.root/'launcher'
        launcher.write_text('#!' + sys.executable + '''
import sys,json,hashlib,os
from pathlib import Path
args=sys.argv;p=Path(args[args.index('--plan-file')+1]).parent
raw=(p.parent.parent/'seed.json').read_bytes()
output=Path(args[args.index('--output')+1]);output.write_bytes(raw);output.chmod(0o600)
report=Path(args[args.index('--report-file')+1]);report.write_text(json.dumps({'contract_version':'1.0','source_gets':5,'max_source_gets':5,'handoff_sha256':hashlib.sha256(raw).hexdigest()}));report.chmod(0o600)
(p/'environment.json').write_text(json.dumps(dict(os.environ)))
''');launcher.chmod(0o700)
        source=CollectorLauncherSource(launcher,hashlib.sha256(launcher.read_bytes()).hexdigest());r=self.runner(source=source)
        with patch.dict(os.environ,{'PI_PASSWORD':'secret','RELIABILITY_MART_ADMIN_DATABASE_URL':'secret'}):self.execute(r)
        env=json.loads((self.root/'journal/run-1/environment.json').read_text())
        self.assertNotIn('PI_PASSWORD',env);self.assertNotIn('RELIABILITY_MART_ADMIN_DATABASE_URL',env)
        launcher.write_text('changed')
        with self.assertRaisesRegex(RefreshError,'LAUNCHER_CHECKSUM_MISMATCH'):self.execute(r,attempt='changed-launcher')

@unittest.skipUnless(os.getenv('NADI_MART_TEST_DSN'),'isolated PostgreSQL not configured')
class RefreshPostgresTest(RefreshTest):
    reader=fixture.ConditionPostgresTest.reader
    def setUp(self):
        with patch.object(fixture.ConditionProjectionTest,'setUp',fixture.ConditionPostgresTest.setUp):super().setUp()
    def test_cross_connection_asset_lease(self):
        with self.store.refresh_lease(ASSET):
            with self.assertRaisesRegex(ProjectionGateError,'REFRESH_LEASE_BUSY'):
                with ConditionCommandStore(self.engine).refresh_lease(ASSET):pass
