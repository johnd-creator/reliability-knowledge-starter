import json,os,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from sqlalchemy import create_engine,text,select
from src.repositories.application_boundary import ApplicationStore
from src.services.local_authentication import LocalIdentityProvider,ACCOUNT
from src.repositories.application_migrations import ApplicationMigrator
from src.services.pdm_history_pilot import HistoryPilot,budget,validate_disposable_target
from src.services.pdm_history_staging import canonical,fingerprint
from src.domain.manual_inspection import InspectionDraft
from test_pdm_history_staging import events,FakeReader
from test_condition_evidence import ConditionProjectionTest,ASSET_ID
from qa.live_server import PersistentFixture

DSN=os.environ.get('NADI_HISTORY_PILOT_TEST_DSN')
AUTHOR=ADMIN=None
class HistoryPilotTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  global AUTHOR,ADMIN
  if not DSN:raise unittest.SkipTest('Explicit disposable history copy required')
  cls.engine=create_engine(DSN,hide_parameters=True);cls.database=cls.engine.url.database
  validate_disposable_target(cls.engine,cls.database)
  ApplicationMigrator(cls.engine,expected_database=cls.database,isolated=True).apply()
  cls.fixture=PersistentFixture.__new__(PersistentFixture);cls.fixture.engine=cls.engine;cls.fixture.store=ApplicationStore(cls.engine,expected_database=cls.database,isolated=True)
  cls.fixture.pi=ConditionProjectionTest();cls.fixture.pi.setUp();cls.fixture.asset=ASSET_ID;cls.fixture.mart=cls.fixture.pi.reader();cls.provider=LocalIdentityProvider(cls.fixture.store)
  with cls.engine.connect() as c:admins=[r for r in c.execute(select(ACCOUNT.c.user_id,ACCOUNT.c.roles)).mappings() if 'ADMIN' in r['roles']]
  password='Disposable-history-fixture-'+uuid.uuid4().hex
  ADMIN=admins[0]['user_id'] if admins else cls.provider.bootstrap(username='history-test-admin',password=password,assets={ASSET_ID},operator_ref='ISOLATED_HISTORY_TEST')
  AUTHOR=cls.provider.create_account(cls.provider.current_grant(ADMIN),username='history-test-'+uuid.uuid4().hex,password=password,roles={'AUTHOR'},assets={ASSET_ID},require_change=False)
  cls.fixture.wire(cls.provider);cls.service=cls.fixture.inspections
 @classmethod
 def tearDownClass(cls):
  if hasattr(cls,'engine'):cls.fixture.pi.tearDown();cls.engine.dispose()
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.pilot=HistoryPilot(self.service,self.provider,database=self.database)
 def tearDown(self):self.temp.cleanup()
 def plan(self,count=2):
  reader=FakeReader();reader.sha=uuid.uuid4().hex*2;rows=events(reader,reviewed_hashes=[reader.sha])[:count];directory=self.root/'plan';directory.mkdir();stream=directory/'events.jsonl';stream.write_text(''.join(canonical(r)+'\n' for r in rows));m={'events_sha256':__import__('hashlib').sha256(stream.read_bytes()).hexdigest(),'as_of':'2026-10-21'};m['plan_id']=fingerprint(m);(directory/'manifest.json').write_text(canonical(m));return directory,rows
 def stats(self):
  with self.engine.connect() as c:return tuple(c.scalar(text('SELECT count(*) FROM '+t)) for t in ['nadi_human_record','nadi_human_record_revision','nadi_human_record_receipt'])
 def test_bounded_commit_audit_and_idempotent_replay(self):
  d,rows=self.plan();before=self.stats();r=self.pilot.run(d,AUTHOR,self.root/'journal.json');self.assertEqual(r['created'],2);self.assertEqual(self.stats(),tuple(x+2 for x in before));again=self.pilot.run(d,AUTHOR,self.root/'journal.json');self.assertEqual((again['created'],again['replayed']),(0,2));self.assertEqual(self.stats(),tuple(x+2 for x in before))
  actor=self.provider.current_grant(AUTHOR).principal
  for item in r['records']:
   record=self.service.get(actor,item['record_id']);history=self.service.history(actor,item['record_id']);self.assertEqual(record.status,'DRAFT');self.assertEqual(record.created_by,AUTHOR);self.assertEqual(len(history),1);self.assertEqual(history[0]['action'],'CREATE');self.assertEqual(record.input_capture.rows[0].raw_value,rows[0]['draft']['input_capture']['rows'][0]['raw_value'] if item==r['records'][0] else 2)
 def test_resume_after_commit_before_journal_lost_ack(self):
  d,_=self.plan();before=self.stats()
  with self.assertRaisesRegex(RuntimeError,'LOST_ACK'):self.pilot.run(d,AUTHOR,self.root/'journal.json',limit=1,after_commit=lambda:(_ for _ in ()).throw(RuntimeError('LOST_ACK')))
  self.assertFalse((self.root/'journal.json').exists());r=self.pilot.run(d,AUTHOR,self.root/'journal.json',limit=1);self.assertEqual((r['created'],r['replayed']),(1,1));self.assertEqual(self.stats(),tuple(x+2 for x in before))
 def test_admin_cannot_import(self):
  d,_=self.plan();before=self.stats()
  with self.assertRaisesRegex(Exception,'FORBIDDEN'):self.pilot.run(d,ADMIN,self.root/'journal.json')
  self.assertEqual(before,self.stats())
 def test_no_live_database_adapter(self):
  for name in ['nadi_local_dev_01_test','nadi_live_dev_test','maximo_collector','pdm_history_pilot_fake']:
   with self.assertRaisesRegex(ValueError,'DISPOSABLE_HISTORY_COPY_ONLY'):HistoryPilot(self.service,self.provider,database=name)
 def test_existing_partial_preserved_without_overwrite_even_missing_index(self):
  d,rows=self.plan(1);draft=dict(rows[0]['draft'],inspector_ref=AUTHOR);draft['input_capture']=dict(draft['input_capture'],rows=draft['input_capture']['rows'][:1]);actor=self.provider.current_grant(AUTHOR).principal;old=self.service.command(actor,'CREATE',draft,'partial-'+uuid.uuid4().hex);before=self.stats()
  with self.assertRaisesRegex(Exception,'EXISTING_SOURCE_EVENT_PRESERVED'):self.pilot.run(d,AUTHOR,self.root/'journal.json')
  self.assertEqual(before,self.stats());self.assertEqual(self.service.get(actor,old.record_id).revision,1)
 def test_budget_failure_rolls_back_chunk(self):
  d,_=self.plan();before=self.stats()
  with self.engine.connect() as c:document_count=budget(c)['documents']
  with patch('src.services.pdm_history_pilot.DOCUMENT_BUDGET',document_count+5):
   with self.assertRaisesRegex(Exception,'BUDGET_EXCEEDED'):self.pilot.run(d,AUTHOR,self.root/'journal.json')
  self.assertEqual(before,self.stats())
 def test_limit_and_plan_tamper_before_write(self):
  d,_=self.plan();before=self.stats()
  with self.assertRaisesRegex(ValueError,'BOUNDED_PILOT_LIMIT'):self.pilot.run(d,AUTHOR,self.root/'journal.json',limit=26)
  (d/'events.jsonl').write_text('{}\n')
  with self.assertRaisesRegex(ValueError,'CONTENT_CHANGED'):self.pilot.run(d,AUTHOR,self.root/'journal.json')
  self.assertEqual(before,self.stats())
 def test_removed_optional_origin_is_a_payload_conflict_not_replay(self):
  d,rows=self.plan(1);actor=self.provider.current_grant(AUTHOR).principal
  payload=InspectionDraft.model_validate(dict(rows[0]['draft'],inspector_ref=AUTHOR,work_origin={'source':'PDM_PM_52_WEEK','reported_asset_label':'Synthetic source label'})).model_dump(mode='json')
  self.service.command(actor,'CREATE',payload,rows[0]['request_id']);before=self.stats()
  with self.assertRaisesRegex(Exception,'IDEMPOTENCY_CONFLICT'):self.pilot.run(d,AUTHOR,self.root/'journal.json')
  self.assertEqual(before,self.stats())
 def test_historical_partial_remains_reserved_after_source_coordinates_change(self):
  d,rows=self.plan(1);actor=self.provider.current_grant(AUTHOR).principal
  draft=InspectionDraft.model_validate(dict(rows[0]['draft'],inspector_ref=AUTHOR)).model_dump(mode='json');draft['input_capture']['rows']=draft['input_capture']['rows'][:1]
  old=self.service.command(actor,'CREATE',draft,'manual-partial-'+uuid.uuid4().hex)
  changed=json.loads(json.dumps(draft));changed['input_capture']['rows'][0]['value_region']='B4'
  current=self.service.command(actor,'UPDATE',changed,'manual-edit-'+uuid.uuid4().hex,record_id=old.record_id,expected_revision=1)
  self.assertEqual(current.revision,2);before=self.stats()
  with self.assertRaisesRegex(Exception,'EXISTING_SOURCE_EVENT_PRESERVED'):self.pilot.run(d,AUTHOR,self.root/'journal.json')
  self.assertEqual(before,self.stats());self.assertEqual(len(self.service.history(actor,old.record_id)),2)
 def test_replay_after_later_user_edit_preserves_latest_revision(self):
  d,rows=self.plan(1);actor=self.provider.current_grant(AUTHOR).principal;created=self.pilot.run(d,AUTHOR,self.root/'journal.json');rid=created['records'][0]['record_id']
  payload=InspectionDraft.model_validate(dict(rows[0]['draft'],inspector_ref=AUTHOR,observations=['Synthetic later user edit'])).model_dump(mode='json')
  self.service.command(actor,'UPDATE',payload,'later-edit-'+uuid.uuid4().hex,record_id=rid,expected_revision=1);before=self.stats()
  replay=self.pilot.run(d,AUTHOR,self.root/'journal.json');self.assertEqual((replay['created'],replay['replayed']),(0,1));self.assertEqual(before,self.stats());self.assertEqual(self.service.get(actor,rid).revision,2)
 def test_post_write_byte_budget_rolls_back_all_records(self):
  d,_=self.plan();before=self.stats()
  with self.engine.connect() as c:current=budget(c)['bytes']
  with patch('src.services.pdm_history_pilot.BYTE_BUDGET',current+1):
   with self.assertRaisesRegex(Exception,'BUDGET_EXCEEDED'):self.pilot.run(d,AUTHOR,self.root/'journal.json')
  self.assertEqual(before,self.stats())
 def test_revoked_or_unavailable_author_never_writes(self):
  d,_=self.plan();before=self.stats()
  with patch.object(self.provider,'current_grant',return_value=None):
   with self.assertRaisesRegex(Exception,'FORBIDDEN'):self.pilot.run(d,AUTHOR,self.root/'journal.json')
  self.assertEqual(before,self.stats())
