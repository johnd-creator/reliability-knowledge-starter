"""B5 qualification only; runner injects independently verified disposable URL.

No runtime imports this module. Existing candidate implementations are unmodified.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,time,resource,unittest,uuid
from unittest.mock import patch
import psycopg
from sqlalchemy import select,update,text,delete,event,func
from sqlalchemy.exc import DBAPIError
from src.config import DbConfig
from src.repositories.database import Database
from src.repositories import models,mart_models,projection_models as pm,deferred_models as dm,replay_models as rm
from src.repositories.projection_store import Budget,BudgetExceeded,CaptureError,FencedOut,ProjectionStore,Ticket
from src.repositories.replay_store import ReplayStore
from src.services.projection_replay import ProjectionReplay
from coverage_writer import Fixture

URL=ROOT=WORK=None
METRICS=[]
SCENARIOS={}

class B5Fixture(Fixture):
    def rows(self,table):
        with self.db.session() as s:return [dict(r) for r in s.execute(select(table)).mappings()]

    def finish(self):
        assert self.cursors()==self.cursor
        with self.db.engine.begin() as c:
            c.execute(text('GRANT USAGE ON SCHEMA '+self.schema+' TO nadi_b5_reader'))
            for table in (*pm.metadata.tables.values(),*dm.metadata.tables.values(),*rm.metadata.tables.values()):
                columns=','.join(col.name for col in table.c if col.name!='payload')
                c.execute(text(f'GRANT SELECT ({columns}) ON {table.name} TO nadi_b5_reader'))
            for table in ('asset_master','maintenance_event'):
                c.execute(text('GRANT SELECT ON '+table+' TO nadi_b5_reader'))
        result=dict(schema=self.schema,policy_digest=self.store.policy_digest)
        self.db.engine.dispose();return result


def fixture(name):return B5Fixture(URL,ROOT,'b5_'+name)

def pipeline(stage):
    f=fixture(stage);f.asset('READY');f.wo('BSR-READY','READY');f.wo('BSR-HISTORIC','MISSING')
    t=f.store.capture('maintenance_event');f.store.process(t)
    original=f.rows(pm.item);old=f.store.inspect(t.run_id)
    missing=next(v for v in f.rows(dm.version) if v['reason']=='MISSING_LOCAL_EQUIPMENT')
    f.store.register(t,missing['id']);f.store.release(t);f.capture('asset_master')
    # Later synthetic source generation advances another WO, never the old debt
    # and never the source synchronization cursor.
    with f.db.session() as session,session.begin():
        session.execute(update(models.WorkOrderOrm).where(models.WorkOrderOrm.id=='BSR-READY').values(
            source_changed_at=datetime(2026,1,1,tzinfo=timezone.utc)))
    for _ in range(2):f.capture('maintenance_event')
    assert f.store.inspect(t.run_id)==old and f.rows(pm.item)[:len(original)]==original
    assert f.rows(rm.queue)[0]['phase']=='PENDING'
    assert len(f.rows(dm.family))==1
    if stage!='partial':
        f.asset('MISSING');f.capture('asset_master')
        due=f.store.due('maintenance_event',limit=1);assert len(due)==1
        out=ProjectionReplay(f.store,enabled=True).run('maintenance_event');assert out[0]['state']=='DONE'
        run=f.store.inspect(out[0]['run_id']);assert run['scope']['capture_mode']=='RECOVERY_BY_ID' and run['item_count']==1
        receipt=next(r for r in f.rows(pm.item) if r['run_id']==run['id'])
        assert receipt['source_id']=='BSR-HISTORIC' and receipt['payload']['source_changed_at']=='2000-01-01T00:00:00+00:00'
        assert f.store.inspect(t.run_id)==old
        assert next(v for v in f.rows(dm.version) if v['id']==missing['id'])['state']=='SUPERSEDED_BY_NEW_VERSION'
        assert any(v['state']=='RESOLVED' for v in f.rows(dm.version))
        assert f.rows(rm.queue)[0]['phase']=='DONE'
        assert not next(d for d in f.rows(pm.lease) if d['domain']=='maintenance_event')['last_complete_run']
    if stage=='final':
        full=f.capture('maintenance_event');assert f.store.inspect(full.run_id)['status']=='COMPLETE'
        assert f.store.inspect(t.run_id)==old
    return f

class IntegratedWriterTest(unittest.TestCase):
    def setUp(self):
        self.f=fixture(self._testMethodName);self.addCleanup(self.f.db.engine.dispose)
    def tearDown(self):self.assertEqual(self.f.cursors(),self.f.cursor)

    def test_pipeline_partial_targeted_and_final(self):
        for stage in ('partial','targeted','final'):
            f=pipeline(stage);SCENARIOS[stage]=f.finish()
        self.assertTrue({'partial','targeted','final'}<=SCENARIOS.keys())

    def test_empty_manifest(self):
        f=self.f;f.capture('asset_master');f.capture('maintenance_event')
        self.assertTrue(all(r['item_count']==0 and r['status']=='COMPLETE' for r in f.rows(pm.run)))
        SCENARIOS['empty']=f.finish()

    def test_default_disabled_and_wrong_engine(self):
        with self.assertRaises(CaptureError):ReplayStore(self.f.db)
        with self.assertRaises(CaptureError):ProjectionStore(self.f.db,enabled=True)

    def test_crash_before_commit_atomicity(self):
        f=self.f;f.debt();f.asset();before=f.rows(dm.version)
        def crash(s):raise RuntimeError('synthetic pre-commit crash')
        with self.assertRaises(CaptureError):ProjectionReplay(f.store,enabled=True).run('maintenance_event',before_commit=crash)
        self.assertEqual(f.rows(pm.target),[]);self.assertEqual(before,f.rows(dm.version))
        self.assertEqual(f.rows(rm.queue)[0]['phase'],'FAILED')

    def test_lost_reply_recovery_is_idempotent(self):
        f=self.f;f.debt();f.asset()
        def lost():raise RuntimeError('synthetic lost reply')
        with self.assertRaises(RuntimeError):ProjectionReplay(f.store,enabled=True).run('maintenance_event',after_commit=lost)
        target=f.rows(pm.target);self.assertEqual(f.rows(rm.queue)[0]['phase'],'PROJECTED')
        self.make_due();self.assertEqual(ProjectionReplay(f.store,enabled=True).run('maintenance_event')[0]['state'],'DONE')
        self.assertEqual(f.rows(pm.target),target);self.assertEqual(f.rows(rm.queue)[0]['attempts'],1)

    def make_due(self):
        f=self.f
        with f.db.session() as s,s.begin():
            d=s.execute(select(pm.lease).where(pm.lease.c.domain=='maintenance_event')).mappings().one()
            s.execute(update(pm.lease).where(pm.lease.c.domain=='maintenance_event').values(lease_until=func.clock_timestamp()+timedelta(seconds=60)))
            q=dict(s.execute(select(rm.queue)).mappings().one())
            f.store._change(s,Ticket(d['latest_run'],d['domain'],d['owner'],d['fence']),q,q['phase'],q['reason'],due_at=func.clock_timestamp()-timedelta(seconds=1))
            s.execute(update(pm.lease).where(pm.lease.c.domain=='maintenance_event').values(lease_until=func.clock_timestamp()-timedelta(seconds=1)))

    def test_source_absence_retains_debt(self):
        f=self.f;f.debt()
        with f.db.session() as s,s.begin():s.execute(delete(models.WorkOrderOrm))
        out=ProjectionReplay(f.store,enabled=True).run('maintenance_event')
        self.assertEqual(out[0]['reason'],'SOURCE_ABSENT');self.assertEqual(f.rows(dm.version)[0]['state'],'OPEN')

    def test_unknown_scope_and_invalid_mapping(self):
        f=self.f;f.asset(unknown=True);f.capture('asset_master')
        self.assertEqual(f.rows(dm.version)[0]['scope_proof'],'UNKNOWN')
        with f.db.session() as s,s.begin():s.execute(update(models.EquipmentOrm).values(sources={'maximo':{'assetnum':'A','siteid':'BSR','orgid':'IP','changedate':'bad'}}))
        f.capture('asset_master');self.assertTrue(any(v['state']=='BLOCKED_NEEDS_REVIEW' for v in f.rows(dm.version)))

    def test_poison_exhaustion_never_drops_debt(self):
        f=self.f;f.debt();f.asset()
        for i in range(3):
            with patch.object(f.store.writer,'persist_in_session',side_effect=RuntimeError('synthetic')):
                with self.assertRaises(CaptureError):ProjectionReplay(f.store,enabled=True).run('maintenance_event')
            if i<2:self.make_due()
        self.assertEqual(f.rows(rm.queue)[0]['phase'],'BLOCKED');self.assertEqual(f.rows(pm.target),[])
        self.assertNotEqual(f.rows(dm.version)[0]['state'],'RESOLVED')

    def test_expired_claim_rejects_commit(self):
        f=self.f;f.debt();f.asset();t=f.store.claim_due('maintenance_event');f.store.capture_claim(t);f.store.reserve_attempt(t);f.expired()
        with self.assertRaises(FencedOut):f.store.process(t,max_items=1)
        self.assertEqual(f.rows(pm.target),[])

    def test_legacy_target_conflict_detected_not_prevented(self):
        f=self.f;f.complete()
        with f.db.session() as s,s.begin():s.execute(update(mart_models.MaintenanceEventMartOrm).values(status='LEGACY-CONFLICT'))
        t=f.store.capture('maintenance_event')
        with self.assertRaises(FencedOut):f.store.process(t)
        self.assertEqual(f.store.inspect(t.run_id)['continuation'],0)

    def test_lock_contention_bounded(self):
        f=self.f;f.asset();t=f.store.capture('asset_master');start=time.monotonic()
        with f.db.engine.connect() as c,c.begin():
            c.execute(text("SELECT * FROM mart_capture_domain WHERE domain='asset_master' FOR UPDATE"))
            with ThreadPoolExecutor(1) as pool:
                with self.assertRaises(DBAPIError):pool.submit(f.store.process,t).result(timeout=4)
        elapsed=time.monotonic()-start;self.assertLess(elapsed,4)
        METRICS.append(dict(case='lock_contention',seconds=elapsed));self.assertEqual(f.rows(pm.target),[])

    def test_concurrent_source_change_snapshot_consistency(self):
        f=self.f;f.asset();f.wo()
        def change(_):
            with f.db.session() as s,s.begin():s.execute(update(models.WorkOrderOrm).values(status='COMP'))
        t=f.store.capture('maintenance_event',after_page=change)
        self.assertEqual(f.rows(pm.item)[0]['payload']['status'],'CAN')
        self.assertEqual(f.rows(models.WorkOrderOrm.__table__)[0]['status'],'COMP')
        f.store.release(t)

    def test_clean_sql_install_order_repeat_and_reader_signature(self):
        schema='b5_sql_'+uuid.uuid4().hex[:10]
        clean=Database(DbConfig(URL.render_as_string(hide_password=False)))
        self.addCleanup(clean.engine.dispose)
        with clean.engine.connect() as c:
            raw=c.connection.driver_connection
            raw.execute('CREATE SCHEMA '+schema);raw.execute('SET search_path TO '+schema);raw.commit()
            for name in ('001_init.sql','002_reliability_mart.sql','003_reliability_registry_projection.sql','004_projection_capture_candidate.sql','005_deferred_obligation_candidate.sql','006_bounded_replay_candidate.sql'):
                raw.execute((ROOT/'migrations'/name).read_text());raw.commit()
            before=raw.execute("SELECT count(*) FROM pg_tables WHERE schemaname=%s",(schema,)).fetchone()[0];raw.commit()
            for name in ('004_projection_capture_candidate.sql','005_deferred_obligation_candidate.sql','006_bounded_replay_candidate.sql'):
                with self.assertRaises(psycopg.errors.DuplicateTable):raw.execute((ROOT/'migrations'/name).read_text())
                raw.rollback()
                self.assertEqual(raw.execute("SELECT count(*) FROM pg_tables WHERE schemaname=%s",(schema,)).fetchone()[0],before);raw.commit()
        clean.engine.dispose()
        @event.listens_for(clean.engine,'connect')
        def path(conn,_):conn.execute('SET search_path TO '+schema);conn.commit()
        store=ReplayStore(clean,enabled=True,exclusive_writer=True,controlled_transitions=True,replay_enabled=True)
        for domain in ('asset_master','maintenance_event'):
            t=store.capture(domain);store.process(t);store.release(t)
        f=object.__new__(B5Fixture);f.db=clean;f.schema=schema;f.store=store;f.cursor=f.cursors()
        SCENARIOS['sql_install']=f.finish()
        METRICS.append(dict(case='migration_install',schema=schema,tables=before))

    def test_distinct_projector_source_grants_and_guards(self):
        f=self.f;f.asset();f.wo()
        with f.db.engine.begin() as c:
            c.execute(text('GRANT USAGE ON SCHEMA '+f.schema+' TO nadi_b5_projector,nadi_b5_source'))
            for table in ('equipment','work_order'):c.execute(text('GRANT SELECT ON '+table+' TO nadi_b5_projector,nadi_b5_source'))
            for name in (*pm.metadata.tables,*dm.metadata.tables,*rm.metadata.tables,'asset_master','maintenance_event'):
                c.execute(text('GRANT SELECT,INSERT,UPDATE ON '+name+' TO nadi_b5_projector'))
            c.execute(text('REVOKE ALL ON SCHEMA '+f.schema+' FROM PUBLIC'))
        db=Database(DbConfig(URL.set(username='nadi_b5_projector').render_as_string(hide_password=False)))
        @event.listens_for(db.engine,'connect')
        def path(conn,_):conn.execute('SET search_path TO '+f.schema);conn.commit()
        self.addCleanup(db.engine.dispose)
        store=ReplayStore(db,enabled=True,exclusive_writer=True,controlled_transitions=True,replay_enabled=True)
        t=store.capture('asset_master');store.process(t);store.release(t)
        for sql in ('CREATE TABLE forbidden(x int)','ALTER TABLE mart_capture_run DISABLE TRIGGER ALL',
                    'DELETE FROM mart_capture_item','TRUNCATE mart_capture_item',
                    "UPDATE sync_cursor SET rows_seen=0", "UPDATE equipment SET description='forbidden'"):
            with self.subTest(sql=sql),self.assertRaises(DBAPIError):
                with db.engine.begin() as c:c.execute(text(sql))
        with self.assertRaises(DBAPIError):
            with db.engine.begin() as c:c.execute(text("UPDATE mart_capture_item SET source_id='forged'"))
        # PostgreSQL FOR SHARE needs UPDATE on at least one column: document this
        # permission-design gap rather than silently granting source writes.
        with self.assertRaises(DBAPIError):
            with db.engine.begin() as c:c.execute(text('SELECT id FROM work_order FOR SHARE'))
        f.wo('BSR-MISSING','UNKNOWN')
        t=store.capture('maintenance_event');store.process(t)
        with db.session() as session:version=session.scalar(select(dm.family.c.current_id))
        store.register(t,version);store.release(t);f.asset('UNKNOWN')
        with self.assertRaises(CaptureError):ProjectionReplay(store,enabled=True).run('maintenance_event')
        with db.session() as session:self.assertEqual(session.scalar(select(rm.queue.c.phase)),'FAILED')
        METRICS.append(dict(case='projector_grants',full_capture='PASS',read_only_source_row_lock='REFUSED',
                            operational_gate='source-row-lock permission design required; no source UPDATE granted'))

    def test_distinct_source_reader_and_migration_owner(self):
        f=self.f;f.asset()
        schema='b5_owner_'+uuid.uuid4().hex[:10]
        with f.db.engine.begin() as c:
            c.execute(text('CREATE SCHEMA '+schema+' AUTHORIZATION nadi_b5_migrator'))
            c.execute(text('GRANT USAGE ON SCHEMA '+f.schema+' TO nadi_b5_source'))
            c.execute(text('GRANT SELECT ON equipment,work_order TO nadi_b5_source'))
        for user in ('nadi_b5_source','nadi_b5_migrator'):
            db=Database(DbConfig(URL.set(username=user).render_as_string(hide_password=False)))
            self.addCleanup(db.engine.dispose)
            name=f.schema if user=='nadi_b5_source' else schema
            def on_connect(conn,_,name=name):conn.execute('SET search_path TO '+name);conn.commit()
            event.listen(db.engine,'connect',on_connect)
            if user=='nadi_b5_source':
                with db.engine.connect() as c:self.assertEqual(c.scalar(text('SELECT count(*) FROM equipment')),1)
                for sql in ('UPDATE equipment SET id=id','CREATE TABLE forbidden(x int)','SELECT * FROM '+f.schema+'.mart_capture_run'):
                    with self.assertRaises(DBAPIError):
                        with db.engine.begin() as c:c.execute(text(sql))
            else:
                with db.engine.connect() as c:
                    raw=c.connection.driver_connection
                    for filename in ('001_init.sql','002_reliability_mart.sql','003_reliability_registry_projection.sql','004_projection_capture_candidate.sql','005_deferred_obligation_candidate.sql','006_bounded_replay_candidate.sql'):
                        raw.execute((ROOT/'migrations'/filename).read_text());raw.commit()
                    self.assertEqual(raw.execute("SELECT count(*) FROM pg_tables WHERE schemaname=%s AND tableowner='nadi_b5_migrator'",(schema,)).fetchone()[0],28)
                with self.assertRaises(DBAPIError):
                    with db.engine.begin() as c:c.execute(text('CREATE DATABASE forbidden'))

    def test_migration_out_of_order_refused(self):
        schema='b5_bad_order_'+uuid.uuid4().hex[:10]
        clean=Database(DbConfig(URL.render_as_string(hide_password=False)))
        self.addCleanup(clean.engine.dispose)
        with clean.engine.connect() as c:
            raw=c.connection.driver_connection;raw.execute('CREATE SCHEMA '+schema);raw.execute('SET search_path TO '+schema);raw.commit()
            with self.assertRaises(psycopg.errors.UndefinedTable):raw.execute((ROOT/'migrations/005_deferred_obligation_candidate.sql').read_text())
            raw.rollback()

    def test_deferred_cardinality_index_latency_and_fairness(self):
        f=self.f
        with f.db.engine.begin() as c:
            c.execute(text("INSERT INTO work_order(id,equipment_id,status) SELECT 'BSR'||lpad(i::text,5,'0'),'MISSING','CAN' FROM generate_series(1,100) i"))
        t=f.store.capture('maintenance_event');start=time.monotonic();f.store.process(t,max_items=500)
        receipt_seconds=time.monotonic()-start
        for v in f.rows(dm.version):f.store.register(t,v['id'])
        f.store.release(t);self.assertEqual(len(f.rows(dm.family)),100)
        start=time.monotonic();due=f.store.due('maintenance_event',limit=20);latency=time.monotonic()-start
        self.assertEqual(len(due),20)
        from sqlalchemy.dialects import postgresql
        query=str(f.store._due_query('maintenance_event',20).compile(dialect=postgresql.dialect(),compile_kwargs={'literal_binds':True}))
        with f.db.engine.begin() as c:
            c.execute(text('SET LOCAL enable_seqscan=off'))
            plan='\n'.join(c.scalars(text('EXPLAIN '+query)))
        self.assertIn('replay_due',plan)
        ProjectionReplay(f.store,enabled=True).run('maintenance_event')
        self.assertNotEqual(f.store.due('maintenance_event',limit=1)[0]['family_id'],due[0]['family_id'])
        METRICS.append(dict(case='deferred_ledger',families=100,receipt_seconds=receipt_seconds,
            receipts_per_second=100/receipt_seconds,due_selection_seconds=latency,index='replay_due',fairness='first probed family rotates behind next due family'))

    def test_performance_capture_budgets(self):
        for size,rows,seconds,bytes_ in ((10000,10000,15,16*1024*1024),(10001,10000,15,16*1024*1024),(100000,100000,60,64*1024*1024)):
            f=fixture('perf_'+str(size));start=time.monotonic()
            with f.db.engine.begin() as c:
                c.execute(text("INSERT INTO work_order(id,status,source_changed_at) SELECT 'BSR'||lpad(i::text,7,'0'),'CAN','2000-01-01'::timestamptz FROM generate_series(1,:n) i"),{'n':size})
                wal=c.scalar(text('SELECT pg_current_wal_insert_lsn()::text'))
            store=ReplayStore(f.db,enabled=True,exclusive_writer=True,controlled_transitions=True,replay_enabled=True,
                              budget=Budget(rows=rows,seconds=seconds,bytes=bytes_,page=100))
            capture=time.monotonic();outcome='SEALED';ticket=None
            try:ticket=store.capture('maintenance_event')
            except BudgetExceeded:outcome='BUDGET_REFUSED'
            elapsed=time.monotonic()-capture
            with f.db.engine.begin() as c:
                wal_bytes=int(c.scalar(text('SELECT pg_wal_lsn_diff(pg_current_wal_insert_lsn(),CAST(:start AS pg_lsn))'),{'start':wal}))
                relation=int(c.scalar(text("SELECT pg_total_relation_size('mart_capture_item')")))
                count=c.scalar(select(func.count()).select_from(pm.item))
            if size==10001:self.assertEqual(outcome,'BUDGET_REFUSED');self.assertEqual(count,0)
            if ticket:
                self.assertEqual(store.inspect(ticket.run_id)['item_count'],size)
                store.release(ticket)
            self.assertEqual(f.cursors(),f.cursor)
            METRICS.append(dict(case='capture_capacity',requested=size,row_budget=rows,seconds_budget=seconds,
                outcome=outcome,captured=count,capture_seconds=elapsed,total_seconds=time.monotonic()-start,
                wal_bytes=wal_bytes,relation_and_index_bytes=relation,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
            f.db.engine.dispose()
        with self.assertRaises(ValueError):Budget(rows=100001)


def qualify(url,root,work):
    global URL,ROOT,WORK
    URL,ROOT,WORK=url,root,work
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(IntegratedWriterTest)
    count=suite.countTestCases();result=unittest.TextTestRunner(verbosity=2).run(suite)
    data=dict(tests=result.testsRun,discovered=count,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
              metrics=METRICS,conclusion='PASS' if result.wasSuccessful() and result.testsRun==count and not result.skipped else 'FAIL')
    (work/'prepare-result.json').write_text(json.dumps(data,indent=2)+'\n')
    if data['conclusion']!='PASS':raise RuntimeError('integrated writer qualification failed')
    return SCENARIOS
