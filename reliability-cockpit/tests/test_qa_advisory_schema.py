"""Disposable PostgreSQL constraint acceptance; persistent fixture never used."""
import os, unittest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from src.repositories.application_migrations import ApplicationMigrator
from src.repositories.qa_advisory_schema import change_qa_advisory_schema
from src.domain.engineering import EngineeringError

@unittest.skipUnless(os.getenv('NADI_APPLICATION_TEST_DSN'), 'disposable PostgreSQL required')
class QaAdvisorySchemaTest(unittest.TestCase):
    def setUp(self):
        url=make_url(os.environ['NADI_APPLICATION_TEST_DSN'])
        if url.host not in {'localhost','127.0.0.1'} or url.database != 'nadi_application_test':
            raise RuntimeError('dedicated disposable CI database required; persistent fixture forbidden')
        self.engine=create_engine(url)
        with self.engine.begin() as c:
            c.exec_driver_sql('DROP SCHEMA public CASCADE; CREATE SCHEMA public')
        ApplicationMigrator(self.engine,expected_database=url.database,isolated=True).apply()
    def tearDown(self):self.engine.dispose()
    def change(self,**kwargs):return change_qa_advisory_schema(self.engine,expected_database='nadi_application_test',acknowledgement='isolated-advisory-qa-only',**kwargs)
    def test_expand_preserve_idempotent_restore_and_fail_closed(self):
        with self.engine.begin() as c:
            c.exec_driver_sql("INSERT INTO nadi_human_record VALUES('RECOMMENDATION','fixture',1,'{}')")
        self.assertEqual(self.change(),'READY');self.assertEqual(self.change(),'ALREADY_READY')
        with self.engine.begin() as c:
            self.assertEqual(c.scalar(text('SELECT count(*) FROM nadi_human_record')),1)
            c.exec_driver_sql("INSERT INTO nadi_human_record VALUES('ADVISORY','new-fixture',1,'{}')")
        with self.assertRaises(EngineeringError):self.change(rollback=True)
        # Removal confined to this disposable test's own row, never persistent QA.
        with self.engine.begin() as c:c.exec_driver_sql("DELETE FROM nadi_human_record WHERE record_id='new-fixture'")
        self.assertEqual(self.change(rollback=True),'RESTORED')
        self.assertEqual(self.change(rollback=True),'ALREADY_RESTORED')
        with self.assertRaises(EngineeringError):change_qa_advisory_schema(self.engine,expected_database='wrong_test',acknowledgement='isolated-advisory-qa-only')
        with self.assertRaises(EngineeringError):change_qa_advisory_schema(self.engine,expected_database='nadi_application_test',acknowledgement='no')
