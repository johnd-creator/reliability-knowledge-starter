"""Genuine B1/B2/B3 writers → distinct SELECT-only Cockpit reader role."""
from dataclasses import asdict
from datetime import datetime,timedelta,timezone
import json,unittest
from sqlalchemy import create_engine,event,text
from sqlalchemy.exc import DBAPIError
from src.config import MartDbConfig
from src.repositories.mart_database import MartDatabase
from src.repositories.projection_coverage import (ProjectionCoverageReader,CoverageLimits,BoundedRead,
    catalog_signature,CATALOG_SIGNATURE,DEFAULT_REPLAY_DIGEST)
from src.services.projection_coverage import ProjectionCoverageService
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.integration_status import IntegrationStatus,Component
import fixture_context as fixture

class CoveragePostgreSQLTest(unittest.TestCase):
    def db(self,name='complete',owner=False):
        self.assertIsNotNone(fixture.identity,'private runner required; never skip')
        url=fixture.owner_url if owner else fixture.reader_url
        db=MartDatabase(MartDbConfig(dsn=url.render_as_string(hide_password=False),statement_timeout_ms=2000))
        schema=fixture.scenarios[name]['schema']
        @event.listens_for(db.engine,'connect')
        def path(conn,record): conn.execute('SET search_path TO '+schema);conn.commit()
        self.addCleanup(db.engine.dispose)
        return db

    def reader(self,name='complete',**kw):
        return ProjectionCoverageReader(self.db(name),enabled=True,expected_database='nadi_b4_disposable',**kw)

    def report(self,name='complete',**kw): return self.reader(name,**kw).read()
    def domain(self,name='complete',domain='maintenance_event',**kw):
        return next(d for d in self.report(name,**kw).domains if d.domain==domain)

    def status(self):
        now=datetime.now(timezone.utc)
        return IntegrationStatus(observed_at=now,components=tuple(
            __import__('src.domain.integration_status',fromlist=['IntegrationComponentStatus']).IntegrationComponentStatus(
                component=c,state='CURRENT',availability='AVAILABLE',
                collection_freshness={'state':'CURRENT','observed_at':now,'max_age_seconds':660},
                projection_freshness={'state':'CURRENT','observed_at':now,'max_age_seconds':660})
            for c in (Component.MAXIMO,Component.RELIABILITY_MART,Component.PI_COLLECTOR,Component.PI_CONDITION_PROJECTION)))

    def adapted(self,name='complete'):
        result=ProjectionCoverageService(self.reader(name),enabled=True,policy=FreshnessPolicy(
            maximo_wo_max_age_seconds=660,mart_factual_projection_max_age_seconds=660,pi_collector_max_age_seconds=1800)).reconcile(self.status())
        return next(c for c in result.status.components if c.component==Component.RELIABILITY_MART),result

    def test_00_capability_pin(self):
        with self.db().read_snapshot() as s:
            actual=catalog_signature(BoundedRead(s,CoverageLimits()))
        self.assertEqual(actual,CATALOG_SIGNATURE,'ACTUAL_CATALOG='+actual)
        self.assertEqual(fixture.scenarios['complete']['policy_digest'],DEFAULT_REPLAY_DIGEST,
                         'ACTUAL_POLICY='+fixture.scenarios['complete']['policy_digest'])

    def test_complete_receipts_both_domains(self):
        report=self.report()
        self.assertEqual(report.capability,'VERIFIED')
        self.assertTrue(all(d.reconciliation=='VERIFIED' and d.last_complete_verified for d in report.domains),asdict(report))
        d=self.domain();self.assertEqual(d.manifest['captured'],d.manifest['acknowledged'])
        self.assertEqual(d.debt['outstanding'],0)
        self.assertEqual(self.adapted()[0].state,'CURRENT')

    def test_one_deferred_item_prevents_current(self):
        d=self.domain('partial');self.assertEqual(d.debt['outstanding'],1)
        self.assertEqual(d.manifest['deferred'],1);self.assertEqual(d.reconciliation,'INCOMPLETE')
        self.assertNotEqual(self.adapted('partial')[0].state,'CURRENT')

    def test_repeated_attempt_one_family(self):
        d=self.domain('repeated')
        self.assertEqual(d.debt['open'],1);self.assertEqual(d.debt['outstanding'],1)
        self.assertEqual(d.replay['PENDING'],1)

    def test_superseded_version_not_double_counted(self):
        d=self.domain('superseded')
        self.assertEqual(d.debt['outstanding'],1);self.assertEqual(d.debt['superseded'],1)
        self.assertEqual(d.replay['stale_claims'],1)

    def test_replayed_debt_resolved_old_partial_remains_partial(self):
        d=self.domain('replayed')
        self.assertEqual(d.debt['resolved'],1);self.assertEqual(d.debt['outstanding'],0)
        self.assertEqual(d.replay['DONE'],1);self.assertEqual(d.latest.capture_mode,'RECOVERY_BY_ID')
        self.assertEqual(d.latest.state,'PARTIAL');self.assertIsNone(d.last_complete)
        self.assertNotEqual(self.adapted('replayed')[0].state,'CURRENT')

    def test_unlinked_b1_debt_retained(self):
        d=self.domain('unlinked');self.assertEqual(d.debt['unlinked'],1)
        self.assertNotEqual(d.reconciliation,'VERIFIED')

    def test_missing_schema_not_zero(self):
        report=self.report('missing');self.assertNotEqual(report.capability,'VERIFIED')
        self.assertTrue(all(d.debt is None for d in report.domains))

    def test_index_drift_blocked(self):
        self.assertEqual(self.report('index_drift').capability,'BLOCKED')
        self.assertEqual(self.adapted('index_drift')[0].state,'BLOCKED')

    def test_guard_drift_blocked(self): self.assertEqual(self.report('guard_drift').capability,'BLOCKED')

    def test_projected_is_not_resolved(self):
        d=self.domain('projected');self.assertEqual(d.replay['PROJECTED'],1)
        self.assertEqual(d.debt['outstanding'],1);self.assertEqual(d.debt['resolved'],0)

    def test_expired_claim_explicit(self):
        d=self.domain('claimed');self.assertEqual(d.replay['CLAIMED'],1)
        self.assertEqual(d.replay['expired_claims'],1)

    def test_expired_writing_explicit(self):
        d=self.domain('writing');self.assertEqual(d.replay['WRITING'],1)
        self.assertEqual(d.replay['expired_claims'],1);self.assertEqual(d.manifest['unprocessed'],1)

    def test_retry_waiting_not_false_success(self):
        d=self.domain('retry');self.assertEqual(d.replay['FAILED'],1)
        self.assertEqual(d.debt['outstanding'],1)

    def test_poison_queue_visible(self):
        d=self.domain('poison');self.assertEqual(d.replay['BLOCKED'],1)
        self.assertEqual(self.adapted('poison')[0].state,'BLOCKED')

    def test_source_absence_not_resolution(self):
        d=self.domain('absent');self.assertEqual(d.replay['BLOCKED'],1)
        self.assertEqual(d.debt['outstanding'],1);self.assertEqual(d.debt['resolved'],0)

    def test_stale_claim_needs_reconciliation(self):
        d=self.domain('stale_claim');self.assertEqual(d.replay['stale_claims'],1)
        self.assertNotEqual(d.reconciliation,'VERIFIED')

    def test_latest_failed_does_not_erase_previous_complete(self):
        d=self.domain('latest_failed')
        self.assertEqual(d.latest.state,'FAILED');self.assertTrue(d.last_complete_verified)
        self.assertNotEqual(d.latest.run_id,d.last_complete.run_id)
        self.assertNotEqual(self.adapted('latest_failed')[0].state,'CURRENT')

    def test_latest_partial_does_not_refresh_old_complete(self):
        d=self.domain('old_complete_partial')
        self.assertGreater(d.latest.started_at,d.last_complete.completed_at)
        mart,_=self.adapted('old_complete_partial')
        self.assertEqual(mart.projection_freshness.state,'STALE');self.assertNotEqual(mart.state,'CURRENT')

    def test_mixed_domains_remain_independent(self):
        report=self.report('mixed');by={d.domain:d for d in report.domains}
        self.assertEqual(by['asset_master'].reconciliation,'VERIFIED')
        self.assertEqual(by['asset_master'].debt['outstanding'],0)
        self.assertEqual(by['maintenance_event'].debt['outstanding'],1)

    def test_legacy_success_without_candidate_receipts_unknown(self):
        report=self.report('legacy')
        self.assertTrue(all(d.reconciliation=='UNKNOWN' and d.manifest is None for d in report.domains))
        self.assertEqual(self.adapted('legacy')[0].state,'UNKNOWN')

    def test_owner_role_refused(self):
        report=ProjectionCoverageReader(self.db(owner=True),enabled=True,expected_database='nadi_b4_disposable').read()
        self.assertEqual(report.capability,'BLOCKED')
        self.assertEqual(report.domains[0].reasons,('READER_ROLE_UNVERIFIED',))

    def test_reader_has_no_write_ddl_or_raw_source_permissions(self):
        schema=fixture.scenarios['complete']['schema']
        engine=create_engine(fixture.reader_url)
        self.addCleanup(engine.dispose)
        for sql in ("INSERT INTO asset_master(canonical_id) VALUES ('forbidden')",'CREATE TABLE forbidden(id int)','CREATE TEMP TABLE forbidden_temp(id int)',
                    'SELECT payload FROM mart_capture_item','SELECT * FROM work_order','SELECT * FROM sync_cursor'):
            with self.subTest(sql=sql),self.assertRaises(DBAPIError):
                with engine.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ WRITE')
                    c.exec_driver_sql('SET LOCAL search_path TO '+schema)
                    c.exec_driver_sql(sql)

    def test_snapshot_is_consistent_read_only_no_commit_facade(self):
        with self.db().read_snapshot() as s:
            self.assertEqual(s.scalar(text("SELECT current_setting('transaction_isolation')")),'repeatable read')
            self.assertEqual(s.scalar(text("SELECT current_setting('transaction_read_only')")),'on')
            self.assertFalse(hasattr(s,'commit'));self.assertFalse(hasattr(s,'flush'))
            with self.assertRaises(RuntimeError): s.execute(text('DELETE FROM mart_capture_run'))

    def test_wrong_database_identity_refused(self):
        report=ProjectionCoverageReader(self.db(),enabled=True,expected_database='wrong').read()
        self.assertNotEqual(report.capability,'VERIFIED');self.assertIsNone(report.domains[0].debt)

    def test_large_population_limit_is_unknown_not_zero(self):
        report=self.report('large',limits=CoverageLimits(rows=3))
        self.assertNotEqual(report.capability,'VERIFIED');self.assertTrue(all(d.debt is None for d in report.domains))

    def test_target_digest_drift_refuses_current(self):
        report=self.report('target_drift');self.assertNotEqual(report.capability,'VERIFIED')
        self.assertNotEqual(self.adapted('target_drift')[0].state,'CURRENT')

    def test_unknown_scope_not_approved_exclusion(self):
        d=self.domain('scope_unknown',domain='asset_master')
        self.assertEqual(d.manifest['excluded'],0);self.assertEqual(d.debt['open'],1)

    def test_public_shape_pi_and_registry_coverage_unchanged(self):
        result=ProjectionCoverageService(self.reader('partial'),enabled=True).reconcile(self.status())
        original=self.status()
        self.assertEqual(set(result.status.model_dump()),set(original.model_dump()))
        by={c.component:c for c in result.status.components}
        self.assertEqual(by[Component.PI_COLLECTOR].model_dump(exclude={'collection_freshness','projection_freshness'}),
            next(c for c in original.components if c.component==Component.PI_COLLECTOR).model_dump(exclude={'collection_freshness','projection_freshness'}))
        self.assertEqual(result.status.coverage,original.coverage)

    def test_no_sensitive_or_source_identity_output(self):
        raw=json.dumps(asdict(self.report('replayed')),default=str)
        for private in ('BSR001','family_id','obligation_id','source_id','payload','owner','policy_digest'):
            self.assertNotIn(private,raw)

    def test_policy_mismatch_blocks_candidate(self):
        d=self.domain('partial',replay_digest='0'*64)
        self.assertEqual(d.replay['policy_mismatch'],1);self.assertEqual(d.reconciliation,'BLOCKED')

    def test_expired_evidence_policy_is_blocked(self):
        report=self.report(policy_expires_at=datetime(2000,1,1,tzinfo=timezone.utc))
        self.assertEqual(report.capability,'BLOCKED');self.assertIsNone(report.domains[0].debt)

    def test_source_collection_not_refreshed_by_read(self):
        reader=self.reader();before=reader.read();after=reader.read()
        self.assertEqual([d.last_complete for d in before.domains],[d.last_complete for d in after.domains])
        self.assertTrue(all(d.source_freshness=='NOT_EVALUATED' for d in after.domains))

    def test_incompatible_debt_policy_cannot_be_filtered_to_zero(self):
        report=self.report('wrong_policy')
        self.assertEqual(report.capability,'BLOCKED')
        self.assertTrue(all(d.debt is None for d in report.domains))
        self.assertEqual(self.adapted('wrong_policy')[0].state,'BLOCKED')

    def test_query_budget_fails_closed(self):
        report=self.report(limits=CoverageLimits(queries=16))
        self.assertNotEqual(report.capability,'VERIFIED')
        self.assertTrue(all(d.manifest is None for d in report.domains))

    def test_column_level_writer_grant_refused(self):
        report=self.report('column_grant')
        self.assertEqual(report.capability,'BLOCKED')
        self.assertEqual(report.domains[0].reasons,('READER_ROLE_UNVERIFIED',))

    def test_unlinked_repeated_history_is_one_unknown_identity(self):
        d=self.domain('unlinked_repeated')
        self.assertEqual(d.debt['unlinked'],1)
        self.assertEqual(d.debt['outstanding'],0)
        self.assertEqual(d.reconciliation,'INCOMPLETE')

    def test_missing_canonical_target_primary_key_refused(self):
        report=self.report('target_key_drift')
        self.assertEqual(report.capability,'BLOCKED')
        self.assertTrue(all(d.manifest is None for d in report.domains))
