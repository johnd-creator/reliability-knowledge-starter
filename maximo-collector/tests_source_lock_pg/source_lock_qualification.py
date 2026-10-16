"""FIX-01 actual restricted credentials, private Unix-only PG fixtures ONLY."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import hashlib,json,time,unittest,uuid
from unittest.mock import patch
import psycopg
from sqlalchemy import text,event,select,update,delete,func
from sqlalchemy.exc import DBAPIError
from src.config import DbConfig
from src.repositories.database import Database
from src.repositories import models,mart_models,projection_models as pm,deferred_models as dm,replay_models as rm
from src.repositories.projection_store import CaptureError,FencedOut,Ticket,encode
from src.repositories.replay_store import ReplayStore
from src.repositories.source_lock import SourceLockBoundary
from src.services.projection_replay import ProjectionReplay
from qualification_writer import B5Fixture

URL=ROOT=WORK=None
SCENARIOS={};METRICS=[]

class RestrictedFixture(B5Fixture):
    def __init__(self,name,install=True,sql_install=False):
        super().__init__(URL,ROOT,'lock_'+hashlib.sha256(name.encode()).hexdigest()[:16])
        if sql_install:
            # A separate real SQL schema, never ALTER the ORM schema into compliance.
            self.db.engine.dispose();self.schema='lock_sql_'+uuid.uuid4().hex[:12]
            admin=Database(DbConfig(URL.render_as_string(hide_password=False)))
            with admin.engine.connect() as c:
                raw=c.connection.driver_connection;raw.execute('CREATE SCHEMA '+self.schema)
                raw.execute('SET search_path TO '+self.schema);raw.commit()
                for n in ('001_init.sql','002_reliability_mart.sql','003_reliability_registry_projection.sql','004_projection_capture_candidate.sql','005_deferred_obligation_candidate.sql','006_bounded_replay_candidate.sql'):
                    raw.execute((ROOT/'migrations'/n).read_text());raw.commit()
            admin.engine.dispose()
            self.db=self.connection('nadi_lock_fixture')
            with self.db.engine.begin() as c:c.execute(text("INSERT INTO sync_cursor(scope,watermark,rows_seen) VALUES ('FIX01_SYNTHETIC','2000-01-01',7)"))
            self.cursor=self.cursors()
        self.app=self.connection('nadi_lock_projector');self.writer=self.connection('nadi_lock_source')
        with self.db.engine.begin() as c:
            c.execute(text('REVOKE ALL ON SCHEMA '+self.schema+' FROM PUBLIC'))
            c.execute(text('GRANT USAGE ON SCHEMA '+self.schema+' TO nadi_lock_projector,nadi_lock_source,nadi_lock_reader'))
            c.execute(text('GRANT SELECT(id,name,description,status,equipment_class,unit,location_id,parent_id,source_changed_at,sources) ON equipment TO nadi_lock_projector'))
            c.execute(text('GRANT SELECT(id,equipment_id,status,work_type,reported_at,scheduled_start,scheduled_finish,source_changed_at,downtime_hours,actual_labor_hours) ON work_order TO nadi_lock_projector'))
            c.execute(text('GRANT SELECT,INSERT,UPDATE,DELETE ON equipment,work_order TO nadi_lock_source'))
            for name in (*pm.metadata.tables,*dm.metadata.tables,*rm.metadata.tables,'asset_master','maintenance_event'):
                c.execute(text('GRANT SELECT,INSERT,UPDATE ON '+name+' TO nadi_lock_projector'))
        if install:self.install()
        self.store=self.fresh(helper=install)

    def connection(self,role):
        db=Database(DbConfig(URL.set(username=role).render_as_string(hide_password=False)))
        schema=self.schema
        @event.listens_for(db.engine,'connect')
        def scope(conn,_):conn.execute('SET search_path TO '+schema);conn.commit()
        return db

    def install(self):
        with self.db.engine.connect() as c:
            raw=c.connection.driver_connection
            raw.execute("SELECT pg_catalog.set_config('nadi.lock_projector_role','nadi_lock_projector',false)");raw.commit()
            raw.execute((ROOT/'migrations/007_restricted_source_lock_candidate.sql').read_text());raw.commit()

    def fresh(self,helper=True):
        return ReplayStore(self.app,enabled=True,exclusive_writer=True,controlled_transitions=True,replay_enabled=True,
                           **({'source_lock_schema':self.schema} if helper else {}))

    def debt_claim(self):
        self.wo('BSR-HISTORIC','MISSING')
        t=self.store.capture('maintenance_event');self.store.process(t)
        self.store.register(t,self.current());self.store.release(t)
        self.asset('MISSING')
        t=self.store.claim_due('maintenance_event');self.store.capture_claim(t);self.store.reserve_attempt(t)
        return t

    def due_again(self):
        with self.db.session() as s,s.begin():
            d=s.execute(select(pm.lease).where(pm.lease.c.domain=='maintenance_event')).mappings().one()
            s.execute(update(pm.lease).where(pm.lease.c.domain=='maintenance_event').values(lease_until=func.clock_timestamp()+timedelta(seconds=60)))
            q=dict(s.execute(select(rm.queue)).mappings().one())
            self.store._change(s,Ticket(d['latest_run'],d['domain'],d['owner'],d['fence']),q,q['phase'],q['reason'],due_at=func.clock_timestamp()-timedelta(seconds=1))
            s.execute(update(pm.lease).where(pm.lease.c.domain=='maintenance_event').values(lease_until=func.clock_timestamp()-timedelta(seconds=1)))

    def finish(self):
        assert self.cursors()==self.cursor
        with self.db.engine.begin() as c:
            for table in (*pm.metadata.tables.values(),*dm.metadata.tables.values(),*rm.metadata.tables.values()):
                cols=','.join(col.name for col in table.c if col.name!='payload')
                c.execute(text(f'GRANT SELECT ({cols}) ON {table.name} TO nadi_lock_reader'))
            c.execute(text('GRANT SELECT ON asset_master,maintenance_event TO nadi_lock_reader'))
        return dict(schema=self.schema,policy_digest=self.store.policy_digest)

    def close(self):
        for name in ('db','app','writer'):
            db=getattr(self,name,None)
            if db is not None:db.engine.dispose()

class RestrictedSourceLockTest(unittest.TestCase):
    def setUp(self):
        self.f=RestrictedFixture.__new__(RestrictedFixture);self.addCleanup(self.f.close)
        self.f.__init__(self._testMethodName)
    def tearDown(self):self.assertEqual(self.f.cursors(),self.f.cursor)
    def sql(self,query,params=None,role='app'):
        db=getattr(self.f,role)
        with db.engine.begin() as c:return c.execute(text(query),params or {})
    def no_false_resolution(self):
        self.assertFalse(any(v['state']=='RESOLVED' for v in self.f.rows(dm.version)))
        self.assertFalse(any(q['phase']=='DONE' for q in self.f.rows(rm.queue)))
    def refused_preflight(self):
        with self.assertRaises(CaptureError):self.f.fresh()
    def helper(self,domain='maintenance_event',key='BSR-HISTORIC',equipment='MISSING',db=None):
        db=db or self.f.app;qualified=self.f.db.engine.dialect.identifier_preparer.quote_identifier(self.f.schema)+'.nadi_lock_source_exact'
        with db.engine.begin() as c:return c.execute(text(f'SELECT {qualified}(CAST(:d AS text),CAST(:s AS text),CAST(:e AS text))'),{'d':domain,'s':key,'e':equipment})

    def test_root_cause_select_and_direct_share_failure(self):
        f=self.f;self.assertEqual(self.sql('SELECT count(*) FROM work_order').scalar(),0)
        for query in ('SELECT id FROM work_order FOR SHARE','SELECT id FROM equipment FOR SHARE'):
            with self.assertRaises(DBAPIError):self.sql(query)
        t=f.debt_claim();legacy=f.fresh(helper=False)
        with self.assertRaises(DBAPIError):legacy.process(t,max_items=1)
        self.assertEqual(f.rows(pm.target),[]);self.no_false_resolution()
        f.store.process(t,max_items=1);self.assertEqual(f.store.resolve_claim(t)['state'],'DONE');f.store.release(t)
        METRICS.append(dict(case='root_cause',server=self.sql('SELECT version()').scalar().split(' on ')[0],direct_share='DENIED',restricted_replay='PASS'))

    def test_projector_source_mutation_and_admin_denied(self):
        for query in ('UPDATE work_order SET status=status','UPDATE equipment SET id=id','DELETE FROM work_order',
                      'TRUNCATE equipment','ALTER TABLE equipment DISABLE TRIGGER ALL','CREATE TABLE forbidden(x int)',
                      'CREATE TEMP TABLE forbidden(x int)','SET ROLE nadi_capture_lock_owner'):
            with self.subTest(query=query),self.assertRaises(DBAPIError):self.sql(query)
        self.assertFalse(self.sql("SELECT has_any_column_privilege(current_user,'equipment','UPDATE')").scalar())
        self.assertFalse(self.sql("SELECT has_any_column_privilege(current_user,'work_order','UPDATE')").scalar())

    def test_helper_replacement_owner_and_privileges_denied(self):
        q=self.f.schema+'.nadi_lock_source_exact(text,text,text)'
        for query in (f'ALTER FUNCTION {q} OWNER TO nadi_lock_projector',f'ALTER FUNCTION {q} SET search_path=public',
                      f'CREATE OR REPLACE FUNCTION {self.f.schema}.nadi_lock_source_exact(text,text,text) RETURNS void LANGUAGE sql AS $$SELECT NULL$$'):
            with self.assertRaises(DBAPIError):self.sql(query)
        self.sql('GRANT EXECUTE ON FUNCTION '+q+' TO nadi_lock_source')  # warning/no-op, not authority.
        with self.f.app.session() as s:SourceLockBoundary(self.f.app,self.f.schema).verify(s)

    def test_public_and_unrelated_role_cannot_execute(self):
        self.f.asset('MISSING');self.f.wo('BSR-HISTORIC','MISSING')
        with self.assertRaises(DBAPIError):self.helper(db=self.f.writer)
        self.assertFalse(self.sql("SELECT has_function_privilege('nadi_lock_source',:q,'EXECUTE')",{'q':self.f.schema+'.nadi_lock_source_exact(text,text,text)'}).scalar())

    def test_malformed_oversized_and_cross_scope_refused(self):
        f=self.f;f.asset('MISSING');f.wo('BSR-HISTORIC','MISSING');f.wo('OTHER','MISSING')
        for args in ((None,'BSR-HISTORIC','MISSING'),('wrong','BSR-HISTORIC','MISSING'),('maintenance_event','x'*61,'MISSING'),
                     ('maintenance_event',"BSR';SELECT",'MISSING'),('maintenance_event','OTHER','MISSING'),('maintenance_event','BSR-HISTORIC','WRONG'),
                     ('maintenance_event','BSR-HISTORIC',None),('asset_master','MISSING','EXTRA'),('asset_master','ABSENT',None)):
            with self.subTest(args=args),self.assertRaises(DBAPIError):self.helper(*args)
        self.sql("UPDATE equipment SET sources='{}'::jsonb",role='writer')
        with self.assertRaises(DBAPIError):self.helper()

    def test_changed_source_before_lock_refused(self):
        t=self.f.debt_claim();self.sql("UPDATE work_order SET status='COMP'",role='writer')
        with self.assertRaises(FencedOut):self.f.store.process(t,max_items=1)
        self.assertEqual(self.f.rows(pm.target),[]);self.no_false_resolution()

    def test_dependency_deleted_before_lock_refused(self):
        t=self.f.debt_claim();self.sql('DELETE FROM equipment',role='writer')
        with self.assertRaises(CaptureError):self.f.store.process(t,max_items=1)
        self.assertEqual(self.f.rows(pm.target),[]);self.no_false_resolution()

    def test_dependency_identity_changed_after_capture_refused(self):
        t=self.f.debt_claim();self.f.asset('OTHER');self.sql("UPDATE work_order SET equipment_id='OTHER'",role='writer')
        with self.assertRaises(CaptureError):self.f.store.process(t,max_items=1)
        self.assertEqual(self.f.rows(pm.target),[]);self.no_false_resolution()

    def wait_lock(self,pid,timeout=1.0):
        until=time.monotonic()+timeout
        while time.monotonic()<until:
            row=self.sql('SELECT wait_event_type FROM pg_stat_activity WHERE pid=:p',{'p':pid},role='db').scalar()
            if row=='Lock':return
            time.sleep(.01)
        self.fail('expected bounded actual PostgreSQL lock wait')

    def concurrent_update(self,table):
        f=self.f;t=f.debt_claim();started=Event();holder={};seen=[]
        def write():
            with f.writer.engine.begin() as c:
                c.execute(text("SET LOCAL lock_timeout='3000ms'"));holder['pid']=c.scalar(text('SELECT pg_backend_pid()'));started.set()
                c.execute(text("UPDATE "+table+" SET "+('status' if table=='work_order' else 'description')+"='AFTER_COMMIT'"))
        with ThreadPoolExecutor(1) as pool:
            future=None
            def hook(s):
                nonlocal future
                seen.append(s.scalar(text('SELECT pg_backend_pid()')));future=pool.submit(write)
                self.assertTrue(started.wait(1));self.wait_lock(holder['pid']);self.assertFalse(future.done())
            f.store.process(t,max_items=1,before_commit=hook)
            future.result(timeout=5)
        self.assertEqual(len(f.rows(pm.target)),1)
        with f.app.session() as s:self.assertNotEqual(s.scalar(text('SELECT pg_backend_pid()')),holder['pid'])
        self.assertEqual(len(seen),1)
        return t

    def test_work_order_writer_waits_until_atomic_commit(self):self.concurrent_update('work_order')
    def test_equipment_writer_waits_until_atomic_commit(self):self.concurrent_update('equipment')

    def test_source_update_after_commit_detected_by_next_capture(self):
        t=self.concurrent_update('work_order');f=self.f
        self.assertEqual(f.store.resolve_claim(t)['state'],'DONE')
        # The row is still valid evidence at its commit instant; the next
        # source generation differs and cannot be silently certified resolved.
        f.store.release(t)
        newer=f.store.capture('maintenance_event')
        row=next(i for i in f.rows(pm.item) if i['run_id']==newer.run_id)
        self.assertEqual(row['payload']['status'],'AFTER_COMMIT')
        self.assertEqual(f.store.process(newer)['status'],'PARTIAL')
        f.store.release(newer)
        current=next(v for v in f.rows(dm.version) if v['id']==f.current())
        self.assertEqual(current['state'],'OPEN')

    def test_helper_and_receipt_use_same_connection_transaction(self):
        f=self.f;t=f.debt_claim();seen=[]
        def record(conn,cursor,statement,params,context,many):
            if 'nadi_lock_source_exact(' in statement or statement.startswith(('INSERT INTO','UPDATE mart_capture_item')):
                seen.append((conn.connection.driver_connection.info.backend_pid,id(conn.get_transaction())))
        event.listen(f.app.engine,'before_cursor_execute',record)
        try:f.store.process(t,max_items=1)
        finally:event.remove(f.app.engine,'before_cursor_execute',record)
        self.assertGreaterEqual(len(seen),3);self.assertEqual(len(set(seen)),1)

    def test_opposite_order_contention_bounded(self):
        f=self.f;t=f.debt_claim();pid={}
        def trace(conn,cursor,statement,*args):
            if 'nadi_lock_source_exact(' in statement:pid['app']=conn.connection.driver_connection.info.backend_pid
        event.listen(f.app.engine,'before_cursor_execute',trace)
        try:
            with f.writer.engine.connect() as c:
                tx=c.begin();c.execute(text("SET LOCAL lock_timeout='1500ms'"))
                c.execute(text('UPDATE equipment SET description=description'))
                with ThreadPoolExecutor(1) as pool:
                    future=pool.submit(f.store.process,t,max_items=1)
                    until=time.monotonic()+1
                    while 'app' not in pid and time.monotonic()<until:time.sleep(.005)
                    self.assertIn('app',pid);self.wait_lock(pid['app'])
                    try:
                        c.execute(text("UPDATE work_order SET status='OPPOSITE'"));tx.commit()
                    except DBAPIError:tx.rollback()
                    try:future.result(timeout=4)
                    except (CaptureError,DBAPIError):self.assertEqual(f.rows(pm.target),[])
                    else:self.assertEqual(self.sql('SELECT status FROM work_order').scalar(),'CAN')
            self.no_false_resolution()
        finally:event.remove(f.app.engine,'before_cursor_execute',trace)

    def test_reread_fingerprint_after_helper_lock_refuses_tamper(self):
        f=self.f;t=f.debt_claim();original=f.store._source
        def mismatched(session,domain,key,**kw):
            payload=original(session,domain,key,**kw);return dict(payload,status='DIFFERENT')
        with patch.object(f.store,'_source',side_effect=mismatched):
            with self.assertRaises(FencedOut):f.store.process(t,max_items=1)
        self.assertEqual(f.rows(pm.target),[]);self.no_false_resolution()

    def test_source_scope_changed_before_lock_refused(self):
        t=self.f.debt_claim()
        self.sql("UPDATE equipment SET sources=CAST(:value AS jsonb)",{'value':json.dumps({'maximo':{'siteid':'OTHER','orgid':'IP'}})},role='writer')
        with self.assertRaises(CaptureError):self.f.store.process(t,max_items=1)
        self.assertEqual(self.f.rows(pm.target),[])

    def test_lock_timeout_refuses_without_target(self):
        f=self.f;t=f.debt_claim();start=time.monotonic()
        with f.writer.engine.connect() as c,c.begin():
            c.execute(text('UPDATE work_order SET status=status'))
            with ThreadPoolExecutor(1) as pool:
                with self.assertRaises(CaptureError):pool.submit(f.store.process,t,max_items=1).result(timeout=4)
        self.assertLess(time.monotonic()-start,4);self.assertEqual(f.rows(pm.target),[]);self.no_false_resolution()

    def test_lease_expires_while_waiting(self):
        f=self.f;t=f.debt_claim()
        self.sql("UPDATE mart_capture_domain SET lease_until=clock_timestamp()+interval '250 milliseconds' WHERE domain='maintenance_event'",role='db')
        with f.writer.engine.connect() as c:
            tx=c.begin();c.execute(text('UPDATE work_order SET status=status'))
            with ThreadPoolExecutor(1) as pool:
                future=pool.submit(f.store.process,t,max_items=1)
                time.sleep(.4);tx.commit()
                with self.assertRaises(FencedOut):future.result(timeout=4)
        self.assertEqual(f.rows(pm.target),[]);self.no_false_resolution()

    def test_connection_loss_before_commit_rolls_back(self):
        f=self.f;f.wo('BSR-HISTORIC','MISSING');t=f.store.capture('maintenance_event');f.store.process(t);f.store.register(t,f.current());f.store.release(t);f.asset('MISSING')
        def disconnect(s):s.connection().connection.driver_connection.close()
        with self.assertRaises(CaptureError):ProjectionReplay(f.store,enabled=True).run('maintenance_event',before_commit=disconnect)
        self.assertEqual(f.rows(pm.target),[]);self.no_false_resolution()

    def test_lost_ack_after_commit_resumes_exact_receipt(self):
        f=self.f;f.wo('BSR-HISTORIC','MISSING');t=f.store.capture('maintenance_event');f.store.process(t);f.store.register(t,f.current());f.store.release(t);f.asset('MISSING')
        def lost():raise RuntimeError('synthetic lost ack')
        with self.assertRaises(RuntimeError):ProjectionReplay(f.store,enabled=True).run('maintenance_event',after_commit=lost)
        before=f.rows(pm.target);self.assertEqual(f.rows(rm.queue)[0]['phase'],'PROJECTED');f.due_again()
        self.assertEqual(ProjectionReplay(f.store,enabled=True).run('maintenance_event')[0]['state'],'DONE')
        self.assertEqual(f.rows(pm.target),before);self.assertEqual(f.rows(rm.queue)[0]['attempts'],1)

    def test_helper_changed_body_refused(self):
        self.sql('CREATE OR REPLACE FUNCTION '+self.f.schema+".nadi_lock_source_exact(p_domain text,p_source_id text,p_equipment_id text) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$BEGIN RETURN; END$$",role='db')
        self.refused_preflight()
    def test_helper_body_drift_refused(self):
        self.sql("ALTER FUNCTION "+self.f.schema+".nadi_lock_source_exact(text,text,text) SET search_path=public",role='db');self.refused_preflight()
    def test_helper_owner_drift_refused(self):
        self.sql('ALTER FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text,text,text) OWNER TO nadi_lock_fixture',role='db');self.refused_preflight()
    def test_helper_acl_drift_refused(self):
        self.sql('GRANT EXECUTE ON FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text,text,text) TO PUBLIC',role='db');self.refused_preflight()
    def test_helper_missing_refused(self):
        self.sql('DROP FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text,text,text)',role='db');self.refused_preflight()
    def test_helper_execute_denied_refused(self):
        self.sql('REVOKE EXECUTE ON FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text,text,text) FROM nadi_lock_projector',role='db');self.refused_preflight()
    def test_helper_membership_cannot_be_granted_by_projector(self):
        with self.assertRaises(DBAPIError):self.sql('GRANT nadi_capture_lock_owner TO nadi_lock_projector')
        with self.assertRaises(DBAPIError):self.sql('SET ROLE nadi_capture_lock_owner')
        self.f.fresh()
    def test_projector_inbound_membership_refused(self):
        self.sql('GRANT nadi_lock_projector TO nadi_lock_source',role='db')
        try:self.refused_preflight()
        finally:self.sql('REVOKE nadi_lock_projector FROM nadi_lock_source',role='db')
    def test_helper_login_or_rls_drift_refused(self):
        self.sql('ALTER ROLE nadi_capture_lock_owner LOGIN',role='db')
        try:self.refused_preflight()
        finally:self.sql('ALTER ROLE nadi_capture_lock_owner NOLOGIN',role='db')
        self.sql('ALTER TABLE work_order ENABLE ROW LEVEL SECURITY',role='db');self.refused_preflight()
    def test_projector_no_source_update_across_fixture_schemas(self):
        count=self.sql("SELECT count(*) FROM pg_catalog.pg_class WHERE relname IN ('equipment','work_order') AND pg_catalog.has_any_column_privilege(current_user,oid,'UPDATE')").scalar()
        self.assertEqual(count,0)
    def test_helper_source_privilege_drift_refused(self):
        self.sql('GRANT UPDATE(status) ON work_order TO nadi_capture_lock_owner',role='db');self.refused_preflight()

    def test_security_mode_and_overload_refused(self):
        self.sql('ALTER FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text,text,text) SECURITY INVOKER',role='db');self.refused_preflight()
        self.sql('ALTER FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text,text,text) SECURITY DEFINER',role='db')
        self.sql('CREATE FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text) RETURNS void LANGUAGE sql AS $$SELECT NULL$$',role='db');self.refused_preflight()
    def test_source_ownership_drift_refused(self):
        self.sql('ALTER TABLE equipment OWNER TO nadi_capture_lock_owner',role='db');self.refused_preflight()
    def test_running_store_drift_refuses_without_fallback(self):
        t=self.f.debt_claim();self.sql('DROP FUNCTION '+self.f.schema+'.nadi_lock_source_exact(text,text,text)',role='db')
        with self.assertRaises(CaptureError):self.f.store.process(t,max_items=1)
        self.assertEqual(self.f.rows(pm.target),[]);self.no_false_resolution()
    def test_force_rls_and_schema_create_drift_refused(self):
        self.sql('ALTER TABLE work_order ENABLE ROW LEVEL SECURITY',role='db')
        self.sql('ALTER TABLE work_order FORCE ROW LEVEL SECURITY',role='db');self.refused_preflight()
        self.sql('ALTER TABLE work_order DISABLE ROW LEVEL SECURITY',role='db')
        self.sql('ALTER TABLE work_order NO FORCE ROW LEVEL SECURITY',role='db')
        self.sql('GRANT CREATE ON SCHEMA '+self.f.schema+' TO nadi_capture_lock_owner',role='db');self.refused_preflight()

    def test_duplicate_migration_refused(self):
        with self.assertRaises(psycopg.errors.DuplicateFunction):self.f.install()
        self.f.fresh()

    def test_untrusted_search_path_and_temp_objects(self):
        f=self.f;f.asset('MISSING');f.wo('BSR-HISTORIC','MISSING')
        with f.db.engine.connect() as c:
            raw=c.connection.driver_connection
            raw.execute('CREATE TEMP TABLE work_order(id text,equipment_id text)');raw.execute('CREATE TEMP TABLE equipment(id text,sources jsonb)')
            raw.execute("SET search_path=pg_temp,public");raw.execute('SET ROLE nadi_lock_projector')
            raw.execute('SELECT '+f.schema+".nadi_lock_source_exact('maintenance_event','BSR-HISTORIC','MISSING')")
            raw.rollback()
        with f.app.session() as s:
            s.execute(text('SET LOCAL search_path=pg_catalog,pg_temp'))
            with self.assertRaises(CaptureError):SourceLockBoundary(f.app,f.schema).verify(s)

    def test_out_of_order_007_refused(self):
        db=Database(DbConfig(URL.render_as_string(hide_password=False)));self.addCleanup(db.engine.dispose)
        schema='empty_lock_'+uuid.uuid4().hex[:10]
        with db.engine.connect() as c:
            raw=c.connection.driver_connection;raw.execute('CREATE SCHEMA '+schema)
            raw.execute('SET search_path TO '+schema)
            raw.execute("SELECT set_config('nadi.lock_projector_role','nadi_lock_projector',false)");raw.commit()
            with self.assertRaises(psycopg.errors.RaiseException):raw.execute((ROOT/'migrations/007_restricted_source_lock_candidate.sql').read_text())
            raw.rollback()

    def test_helper_returns_no_payload_and_asset_recovery(self):
        f=self.f;f.asset('A',unknown=True)
        t=f.store.capture('asset_master');f.store.process(t);f.store.register(t,f.current());f.store.release(t)
        self.sql("UPDATE equipment SET sources=CAST(:v AS jsonb)",{'v':json.dumps({'maximo':{'assetnum':'A','siteid':'BSR','orgid':'IP'}})},role='writer')
        value=self.helper('asset_master','A',None).scalar();self.assertIn(value,(None,''))
        self.assertEqual(ProjectionReplay(f.store,enabled=True).run('asset_master')[0]['state'],'DONE')
        self.assertTrue(any(v['state']=='RESOLVED' for v in f.rows(dm.version)))

    def test_restricted_e2e_and_later_full_coverage(self):
        for sql_install in (False,True):
            f=self.f if not sql_install else RestrictedFixture('sql_full',sql_install=True)
            if sql_install:self.addCleanup(f.close)
            f.asset('READY');f.wo('BSR-READY','READY');f.wo('BSR-HISTORIC','MISSING')
            t=f.store.capture('maintenance_event');f.store.process(t);old=f.store.inspect(t.run_id)
            f.store.register(t,f.current());f.store.release(t)
            with f.writer.engine.begin() as c:c.execute(text("UPDATE work_order SET source_changed_at='2026-01-01' WHERE id='BSR-READY'"))
            for _ in range(2):f.capture('maintenance_event')
            f.asset('MISSING');f.capture('asset_master')
            self.assertEqual(len(f.store.due('maintenance_event',limit=1)),1)
            out=ProjectionReplay(f.store,enabled=True).run('maintenance_event');self.assertEqual(out[0]['state'],'DONE')
            self.assertEqual(f.store.inspect(t.run_id),old)
            recovery=next(r for r in f.rows(pm.item) if r['run_id']==out[0]['run_id'])
            self.assertEqual(recovery['payload']['source_changed_at'],'2000-01-01T00:00:00+00:00')
            self.assertEqual(f.store.inspect(out[0]['run_id'])['scope']['capture_mode'],'RECOVERY_BY_ID')
            full=f.capture('maintenance_event');self.assertEqual(f.store.inspect(full.run_id)['status'],'COMPLETE')
            for table in ('equipment','work_order'):
                with self.assertRaises(DBAPIError):
                    with f.app.engine.begin() as c:c.execute(text('DELETE FROM '+table))
            SCENARIOS['sql' if sql_install else 'orm']=f.finish()


def qualify(url,root,work):
    global URL,ROOT,WORK
    URL,ROOT,WORK=url,root,work
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(RestrictedSourceLockTest);count=suite.countTestCases()
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    # Final actor-global proof catches accidental test-fixture grants too.
    projector=Database(DbConfig(url.set(username='nadi_lock_projector').render_as_string(hide_password=False)))
    try:
        with projector.engine.connect() as connection:
            writes=connection.scalar(text("SELECT count(*) FROM pg_catalog.pg_class WHERE relname IN ('equipment','work_order') AND (pg_catalog.has_any_column_privilege(current_user,oid,'INSERT,UPDATE,REFERENCES') OR pg_catalog.has_table_privilege(current_user,oid,'INSERT,DELETE,TRUNCATE,REFERENCES,TRIGGER'))"))
        assert writes==0,'projector source write privilege detected'
    finally:projector.engine.dispose()
    METRICS.append(dict(case='final_projector_source_privileges',source_write_tables=0))
    output=dict(tests=result.testsRun,discovered=count,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
                metrics=METRICS,conclusion='PASS' if result.wasSuccessful() and result.testsRun==count and not result.skipped else 'FAIL')
    (work/'prepare-result.json').write_text(json.dumps(output,indent=2)+'\n')
    if output['conclusion']!='PASS':raise RuntimeError('restricted source lock qualification failed')
    return SCENARIOS
