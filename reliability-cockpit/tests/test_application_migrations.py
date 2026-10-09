import os,unittest
from pathlib import Path
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from src.repositories.application_migrations import ApplicationMigrator
from src.domain.engineering import EngineeringError
@unittest.skipUnless(os.getenv('NADI_APPLICATION_TEST_DSN'),'disposable PostgreSQL required')
class ApplicationMigrationTest(unittest.TestCase):
 def setUp(self):
  url=make_url(os.environ['NADI_APPLICATION_TEST_DSN'])
  if url.host not in {'localhost','127.0.0.1'} or not url.database.endswith('_test'):raise RuntimeError('isolated fixture only')
  self.engine=create_engine(url)
  with self.engine.begin() as c:
   c.exec_driver_sql('DROP SCHEMA public CASCADE; CREATE SCHEMA public')
   c.exec_driver_sql('CREATE TABLE legacy_fixture(id integer PRIMARY KEY); INSERT INTO legacy_fixture VALUES(1)')
  self.runner=ApplicationMigrator(self.engine,expected_database=url.database,isolated=True)
 def tearDown(self):self.engine.dispose()
 def test_order_idempotency_preservation_and_grants(self):
  self.assertEqual([s['status'] for s in self.runner.status()],['PENDING']*3)
  self.assertEqual([s['status'] for s in self.runner.apply()],['APPLIED']*3)
  self.assertEqual(self.runner.apply(),self.runner.status())
  with self.engine.begin() as c:
   self.assertEqual(c.scalar(text('SELECT count(*) FROM legacy_fixture')),1)
   c.exec_driver_sql('DO $$ BEGIN IF NOT EXISTS(SELECT FROM pg_roles WHERE rolname=\'nadi_d_writer_test\') THEN CREATE ROLE nadi_d_writer_test NOLOGIN; END IF; END $$')
  self.runner.grant_writer('nadi_d_writer_test')
  with self.engine.begin() as c:
   for right in ['UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']:
    self.assertFalse(c.scalar(text("SELECT has_table_privilege('nadi_d_writer_test','engineering_case_event',:right)"),{'right':right}))
   self.assertTrue(c.scalar(text("SELECT has_table_privilege('nadi_d_writer_test','engineering_case','UPDATE')")))
 def test_untracked_and_checksum_drift_fail_closed(self):
  self.runner.apply()
  with self.engine.begin() as c:c.exec_driver_sql("UPDATE nadi_application_migration SET checksum='invalid'")
  with self.assertRaises(EngineeringError):self.runner.apply()
 def test_wrong_database_and_mart_denied(self):
  with self.assertRaises(EngineeringError):ApplicationMigrator(self.engine,expected_database='wrong_test',isolated=True)
  with self.engine.begin() as c:c.exec_driver_sql('CREATE TABLE asset_master(id integer)')
  with self.assertRaises(EngineeringError):ApplicationMigrator(self.engine,expected_database=self.engine.url.database,isolated=True)
