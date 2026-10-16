"""Cross-component evidence produced by actual restricted-role replay."""
import unittest
from sqlalchemy import event
from src.config import MartDbConfig
from src.repositories.mart_database import MartDatabase
from src.repositories.projection_coverage import ProjectionCoverageReader
import fixture_context as fixture

class RestrictedCoverageTest(unittest.TestCase):
    def read(self,name):
        db=MartDatabase(MartDbConfig(dsn=fixture.reader_url.render_as_string(hide_password=False)))
        self.addCleanup(db.engine.dispose)
        @event.listens_for(db.engine,'connect')
        def path(conn,_):conn.execute('SET search_path TO '+fixture.scenarios[name]['schema']);conn.commit()
        return ProjectionCoverageReader(db,enabled=True,expected_database='nadi_lock_disposable').read()
    def test_restricted_orm_replay_reconciles(self):self.verify('orm')
    def test_restricted_sql_replay_reconciles(self):self.verify('sql')
    def verify(self,name):
        result=self.read(name);self.assertEqual(result.capability,'VERIFIED',result)
        self.assertTrue(all(d.proof_complete and d.last_complete_verified for d in result.domains),result)
        debt=next(d.debt for d in result.domains if d.domain=='maintenance_event')
        self.assertEqual(debt['outstanding'],0);self.assertEqual(debt['resolved'],1);self.assertEqual(debt['superseded'],1)
