"""B5 checkpoint evidence from genuine B1-B3 pipeline; SELECT-only B4 reader."""
from datetime import datetime,timezone
import time,unittest
from test_projection_coverage_pg import CoveragePostgreSQLTest as Helpers
from src.repositories.projection_coverage import ProjectionCoverageReader,CoverageLimits
from src.services.projection_coverage import ProjectionCoverageService
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.integration_status import Component
import fixture_context as fixture

class IntegratedCoverageTest(unittest.TestCase):
    db=Helpers.db
    status=Helpers.status
    def reader(self,name,**kw):return ProjectionCoverageReader(self.db(name),enabled=True,expected_database='nadi_b5_disposable',**kw)
    def report(self,name):return self.reader(name).read()
    def domain(self,name):return next(d for d in self.report(name).domains if d.domain=='maintenance_event')
    def test_partial_generation_historical_debt_remains(self):
        d=self.domain('partial');self.assertEqual(d.debt['outstanding'],1)
        self.assertEqual(d.debt['unlinked'],0);self.assertEqual(d.replay['PENDING'],1)
        self.assertEqual(d.reconciliation,'INCOMPLETE');self.assertIsNone(d.last_complete)
    def test_exact_id_recovery_is_not_population_complete(self):
        d=self.domain('targeted');self.assertEqual(d.debt['outstanding'],0)
        self.assertEqual(d.debt['resolved'],1);self.assertEqual(d.debt['superseded'],1)
        self.assertEqual(d.replay['DONE'],1);self.assertEqual(d.latest.capture_mode,'RECOVERY_BY_ID')
        self.assertEqual(d.reconciliation,'INCOMPLETE')
    def test_later_full_generation_complete_both_domains(self):
        snapshot=self.report('final');self.assertEqual(snapshot.capability,'VERIFIED')
        self.assertTrue(all(d.proof_complete and d.last_complete_verified and d.reconciliation=='VERIFIED' for d in snapshot.domains),snapshot)
        policy=FreshnessPolicy(maximo_wo_max_age_seconds=660,mart_factual_projection_max_age_seconds=660,pi_collector_max_age_seconds=1800)
        out=ProjectionCoverageService(self.reader('final'),enabled=True,policy=policy).reconcile(self.status())
        self.assertEqual(next(c for c in out.status.components if c.component==Component.RELIABILITY_MART).state,'CURRENT')
    def test_empty_full_generation_truthful_zero(self):
        s=self.report('empty');self.assertTrue(all(d.reconciliation=='VERIFIED' and d.manifest['captured']==0 for d in s.domains),s)
    def test_actual_sql_migrations_writer_reader_compatible(self):
        from pathlib import Path
        import json
        from src.repositories.projection_coverage import BoundedRead,catalog_signature
        class Record(BoundedRead):
            def __init__(self,*args):super().__init__(*args);self.results=[]
            def rows(self,*args,**kw):
                result=super().rows(*args,**kw);self.results.append(result);return result
        catalogs={}
        for name in ('final','sql_install'):
            with self.db(name).read_snapshot() as session:
                record=Record(session,CoverageLimits());digest=catalog_signature(record)
                catalogs[name]={'digest':digest,'groups':record.results[:5]}
        (Path(fixture.identity['directory'])/'catalog-comparison.json').write_text(json.dumps(catalogs,indent=2))
        print('B5_CATALOG_HASHES', {k:v['digest'] for k,v in catalogs.items()})
        print('B5_CATALOG_DIFFERENCES', [i for i in range(5) if catalogs['final']['groups'][i]!=catalogs['sql_install']['groups'][i]])
        s=self.report('sql_install');self.assertEqual(s.capability,'VERIFIED',s)
        self.assertTrue(all(d.proof_complete for d in s.domains),s)
    def test_sql_catalog_index_drift_remains_blocked(self):
        from sqlalchemy import create_engine,text
        engine=create_engine(fixture.owner_url)
        try:
            with engine.begin() as c:
                c.execute(text('SET LOCAL search_path TO '+fixture.scenarios['sql_install']['schema']))
                c.execute(text('DROP INDEX ix_asset_master_scope'))
            self.assertEqual(self.report('sql_install').capability,'BLOCKED')
        finally:
            with engine.begin() as c:
                c.execute(text('SET LOCAL search_path TO '+fixture.scenarios['sql_install']['schema']))
                c.execute(text('CREATE INDEX ix_asset_master_scope ON asset_master(site_code,organization_code)'))
            engine.dispose()
    def test_bounded_proof_exhaustion_unknown(self):
        s=self.reader('final',limits=CoverageLimits(rows=1)).read()
        self.assertNotEqual(s.capability,'VERIFIED');self.assertTrue(all(d.manifest is None for d in s.domains))
    def test_reader_measured_query_budget(self):
        from sqlalchemy import event
        db=self.db('final');queries=[]
        def record(*a):queries.append(a[2])
        event.listen(db.engine,'before_cursor_execute',record);start=time.monotonic()
        s=ProjectionCoverageReader(db,enabled=True,expected_database='nadi_b5_disposable').read()
        elapsed=time.monotonic()-start;self.assertEqual(s.capability,'VERIFIED')
        self.assertLessEqual(len(queries),128);self.assertLess(elapsed,5)
        print('B5_READER_METRIC',{'queries':len(queries),'seconds':elapsed})
