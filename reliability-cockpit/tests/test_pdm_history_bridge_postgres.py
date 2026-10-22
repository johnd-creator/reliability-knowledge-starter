"""Portable PG16/source qualification using synthetic data and exact Git objects.

Never contacts installed state, source collectors, live database or actual services.
"""
import importlib.util
import json
import os
import secrets
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.engine import make_url
from src.repositories.application_migrations import ApplicationMigrator
from src.repositories.application_boundary import ApplicationStore
from src.repositories.pdm_source_history import Source, Profile, Cell, Event
from src.services.local_authentication import LocalIdentityProvider
from src.services.pdm_source_history import digest
from src.services.pdm_history_recovery import history, business
from src.services.pdm_complete_demo import assert_history_privileges
from src.domain.engineering import EngineeringError
from qa.live_server import PersistentFixture, ASSET_ID
import test_condition_evidence as condition

REPO=Path(__file__).resolve().parents[2]
PACKAGE=REPO/'deploy/development/pdm_history_111'
spec=importlib.util.spec_from_file_location('pinned_history_bridge',PACKAGE/'controller/pdm_007_bridge.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)

@unittest.skipUnless(os.getenv('NADI_HISTORY_BRIDGE_TEST_DSN'),'separate empty bridge PostgreSQL required')
class HistoryBridgePostgresTest(unittest.TestCase):
 def test_exact_source_startup_schema_history_and_later_revision(self):
  url=make_url(os.environ['NADI_HISTORY_BRIDGE_TEST_DSN'])
  if (url.host!='127.0.0.1' or url.port in {None,5432,15443} or url.query or
      not (url.database or '').startswith('pdm_history_complete_bridge_') or not url.database.endswith('_test')):
   raise RuntimeError('EMPTY_ISOLATED_BRIDGE_DATABASE_REQUIRED')
  engine=create_engine(url,hide_parameters=True)
  if inspect(engine).get_table_names():raise RuntimeError('EMPTY_ISOLATED_BRIDGE_DATABASE_REQUIRED')
  with tempfile.TemporaryDirectory(prefix='pdm-bridge-ci-',dir=REPO.parent) as tmp:
   root=Path(tmp);oldroot=root/'pr110';newroot=root/'pr111';created=[]
   def git(*args):return subprocess.check_output(['git',*map(str,args)],cwd=REPO,text=True,timeout=30).strip()
   try:
    for sha,path in [(bridge.FROM_SHA,oldroot),(bridge.TO_SHA,newroot)]:
     git('worktree','add','--detach',path,sha);created.append(path)
    oldspec=importlib.util.spec_from_file_location('original_pr110_migration',oldroot/'reliability-cockpit/src/repositories/application_migrations.py')
    old=importlib.util.module_from_spec(oldspec);oldspec.loader.exec_module(old)
    old.ApplicationMigrator(engine,expected_database=url.database,isolated=True).apply()
    from src.repositories.qa_advisory_schema import change_qa_advisory_schema
    change_qa_advisory_schema(engine,expected_database=url.database,acknowledgement='isolated-advisory-qa-only')
    store=ApplicationStore(engine,expected_database=url.database,isolated=True);provider=LocalIdentityProvider(store)
    password=secrets.token_urlsafe(24)
    admin=provider.bootstrap(username='fixture-admin',password=password,assets={ASSET_ID,'asset:SYNTHETIC:FOREIGN'},operator_ref='SYNTHETIC_BRIDGE_TEST')
    users={'admin':{'user_id':admin}}
    for name,role,asset in [('engineer','AUTHOR',ASSET_ID),('reviewer','REVIEWER',ASSET_ID),('outsider','AUTHOR','asset:SYNTHETIC:FOREIGN')]:
     users[name]={'user_id':provider.create_account(provider.current_grant(admin),username='fixture-'+name,password=password,roles={role},assets={asset},require_change=False)}
    accounts=root/'accounts.json';accounts.write_text(json.dumps(users));accounts.chmod(0o600)
    config=root/'qualification.json';cfg={'accounts_file':str(accounts),'password':password,'old_source_root':str(oldroot),'expected_source_groups':1};config.write_text(json.dumps(cfg));config.chmod(0o600)
    def probe(source,mode='normal'):
     cockpit=source/'reliability-cockpit'
     env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',NADI_HISTORY_BRIDGE_CONFIG=str(config),PYTHONPATH=os.pathsep.join(map(str,[cockpit,cockpit/'tests',cockpit/'tests/qa',PACKAGE/'controller'])))
     result=subprocess.run([sys.executable,str(REPO/'reliability-cockpit/tests/qa/pdm_history_bridge_probe.py'),str(source),mode],cwd=cockpit,env=env,text=True,capture_output=True,timeout=60)
     if result.returncode:raise AssertionError('Synthetic bridge bootstrap failed: '+result.stderr)
     return json.loads(result.stdout)
    self.assertEqual(bridge.states(engine,oldroot)[-1]['status'],'PENDING')
    self.assertEqual(probe(oldroot)['startup'],'PASS')
    self.assertEqual(probe(newroot,'candidate-pending-denied')['outcome'],'REFUSED')
    self.assertEqual(probe(newroot,'compatibility-pending-denied')['outcome'],'REFUSED')
    ApplicationMigrator(engine,expected_database=url.database,isolated=True).apply()
    self.assertEqual(bridge.states(engine,oldroot),bridge.states(engine,newroot))
    with self.assertRaisesRegex(EngineeringError,'UNKNOWN_APPLICATION_MIGRATION'):
     old.ApplicationMigrator(engine,expected_database=url.database,isolated=True).status()
    self.assertEqual(probe(newroot,'startup-config-mismatch-denied')['outcome'],'REFUSED')
    # Rejections operate on this empty history fixture and reverse each synthetic
    # fault explicitly; no live rollback, purge or blanket reset exists here.
    faults=[
     ("UPDATE nadi_application_migration SET checksum='bad' WHERE name='007_pdm_source_history.sql'", "UPDATE nadi_application_migration SET checksum='"+bridge.MIGRATION_CHECKSUMS['007_pdm_source_history.sql']+"' WHERE name='007_pdm_source_history.sql'"),
     ('ALTER TABLE nadi_history_cell ALTER COLUMN coordinate TYPE varchar(21)','ALTER TABLE nadi_history_cell ALTER COLUMN coordinate TYPE varchar(20)'),
     ('ALTER TABLE nadi_history_batch ALTER COLUMN cursor SET DEFAULT 0','ALTER TABLE nadi_history_batch ALTER COLUMN cursor DROP DEFAULT'),
     ('ALTER TABLE nadi_history_cell ENABLE ROW LEVEL SECURITY','ALTER TABLE nadi_history_cell DISABLE ROW LEVEL SECURITY'),
     ('DROP INDEX nadi_history_owner_page','CREATE INDEX nadi_history_owner_page ON nadi_history_event(owner_id,access_asset_id,event_key)'),
     ("INSERT INTO nadi_application_migration(name,checksum) VALUES('008_unapproved.sql','bad')","DELETE FROM nadi_application_migration WHERE name='008_unapproved.sql'"),
    ]
    for do,undo in faults:
     with engine.begin() as c:c.exec_driver_sql(do)
     try:
      with self.assertRaises(RuntimeError):bridge.states(engine,oldroot)
     finally:
      with engine.begin() as c:c.exec_driver_sql(undo)
    self.assertEqual(bridge.states(engine,oldroot),bridge.states(engine,newroot))
    # Exact new-table rights; no blanket grant_writer or existing account changes.
    role='pdm_bridge_history_writer_ci'
    from src.repositories.pdm_source_history import TABLES
    with engine.begin() as c:
     c.exec_driver_sql('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS')
     c.exec_driver_sql('GRANT USAGE ON SCHEMA public TO '+role)
     for name in TABLES:c.exec_driver_sql('GRANT SELECT,INSERT ON TABLE '+name+' TO '+role)
     c.exec_driver_sql('GRANT UPDATE ON TABLE nadi_history_batch TO '+role)
     c.exec_driver_sql('SET LOCAL ROLE '+role);assert_history_privileges(c)
    with engine.begin() as c:c.exec_driver_sql('GRANT DELETE ON TABLE nadi_history_alias TO '+role)
    with engine.begin() as c:
     c.exec_driver_sql('SET LOCAL ROLE '+role)
     with self.assertRaisesRegex(EngineeringError,'EXACT_HISTORY_WRITER_PRIVILEGES_REQUIRED'):assert_history_privileges(c)
    with engine.begin() as c:
     for name in TABLES:c.exec_driver_sql('REVOKE ALL ON TABLE '+name+' FROM '+role)
     c.exec_driver_sql('REVOKE USAGE ON SCHEMA public FROM '+role);c.exec_driver_sql('DROP ROLE '+role)
    fixture=PersistentFixture.__new__(PersistentFixture);fixture.engine=engine;fixture.store=store;fixture.pi=condition.ConditionProjectionTest();fixture.pi.setUp();fixture.pi.project(fixture.pi.source_document({'synthetic-current':{'Timestamp':'1970-01-01T00:00:00Z'}}));fixture.asset=ASSET_ID;fixture.mart=fixture.pi.reader();fixture.wire(provider)
    try:
     subject=users['engineer']['user_id'];actor=provider.current_grant(subject).principal
     payload={'canonical_asset_id':ASSET_ID,'method':'VIBRATION','method_version':'SYNTHETIC-CI','inspector_ref':subject}
     record=fixture.inspections.command(actor,'CREATE',payload,'synthetic-bridge-create')
     profile={'id':'p','version':'1','fields':[{'id':'f','source_label':'Velocity','unit':'mm/s','header_cells':['B1'],'unit_cells':['B2']}],'clocks':[]};source='a'*64;ph=digest(profile)
     with engine.begin() as c:
      c.execute(Source.insert().values(source_sha=source,document={'source_ref':'WB-SYNTHETIC','sheets':[{'label':'SYNTHETIC','shape':[3,2]}]}));c.execute(Profile.insert().values(profile_hash=ph,document=profile));c.execute(Cell.insert().values(source_sha=source,sheet_index=0,coordinate='B3',terminal_role='INPUT',claims=['INPUT'],document={'raw_value':0,'source_type':'n'}))
      c.execute(Event.insert().values(event_key='b'*64,owner_id=subject,access_asset_id=ASSET_ID,source_sha=source,source_ref='WB-SYNTHETIC',sheet_index=0,profile_id='p',profile_hash=ph,axis='ROW',position=3,classification_hash='c'*64,kind='MEASUREMENT_SOURCE',classification='RAW_UNRESOLVED',document={'kind':'MEASUREMENT_SOURCE','classification':'RAW_UNRESOLVED','reasons':['SYNTHETIC_UNVERIFIED'],'fields':[{'field_id':'f','cell':'B3','role':'INPUT'}],'clocks':[],'clock_cells':[],'source_asset_label':'SYNTHETIC','mapping':'UNVERIFIED_SOURCE_LABEL_ONLY'}))
      before_history={n:digest(v) for n,v in history(c).items()}
     first=probe(oldroot)['compatibility'];self.assertEqual(first,probe(newroot)['compatibility']);self.assertEqual(first,probe(newroot,'compatibility-only'))
     payload['observations']=['SYNTHETIC later user revision']
     changed=fixture.inspections.command(actor,'UPDATE',payload,'synthetic-bridge-revision',record_id=record.record_id,expected_revision=1);self.assertEqual(changed.revision,2)
     later=probe(oldroot)['compatibility'];self.assertEqual(later,probe(newroot)['compatibility']);self.assertNotEqual(first['records'],later['records'])
     with engine.connect() as c:self.assertEqual({n:digest(v) for n,v in history(c).items()},before_history)
    finally:fixture.pi.tearDown()
   finally:
    engine.dispose()
    for path in reversed(created):git('worktree','remove',path)

if __name__=='__main__':unittest.main(verbosity=2)
