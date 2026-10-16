"""B4 source-free preparation ONLY in runner-verified disposable PostgreSQL.

Executed in its own interpreter to avoid sharing the two components' src package.
Never imported by the Cockpit reader, startup, scheduler or operational CLI.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid
from unittest.mock import patch
from sqlalchemy import event, select, update, delete, text
from src.config import DbConfig
from src.repositories.database import Database
from src.repositories import models, projection_models as pm, deferred_models as dm
from src.repositories.projection_store import ProjectionStore, Budget, BudgetExceeded, CaptureError
from src.repositories.replay_store import ReplayStore, ReplayPolicy
from src.services.projection_replay import ProjectionReplay

SCENARIOS=('legacy','complete','partial','repeated','superseded','replayed','projected','claimed','writing',
           'poison','retry','absent','stale_claim','latest_failed','old_complete_partial','unlinked','unlinked_repeated',
           'scope_unknown','wrong_policy','column_grant','large','missing','index_drift','guard_drift','target_drift','target_key_drift','mixed')

class Fixture:
    def __init__(self,url,root,name):
        self.schema='b4_'+name+'_'+uuid.uuid4().hex[:12]
        self.db=Database(DbConfig(url.render_as_string(hide_password=False)))
        with self.db.engine.begin() as c: c.execute(text('CREATE SCHEMA '+self.schema))
        @event.listens_for(self.db.engine,'connect')
        def path(conn,record):
            conn.execute('SET search_path TO '+self.schema); conn.commit()
        self.db.engine.dispose()
        self.db.create_all()
        with self.db.engine.connect() as c:
            for filename in ('004_projection_capture_candidate.sql','005_deferred_obligation_candidate.sql','006_bounded_replay_candidate.sql'):
                c.connection.driver_connection.execute((root/'migrations'/filename).read_text())
                c.connection.driver_connection.commit()
        self.store=ReplayStore(self.db,enabled=True,exclusive_writer=True,controlled_transitions=True,replay_enabled=True)
        with self.db.session() as s,s.begin():
            s.add(models.SyncCursorOrm(scope='B4_SYNTHETIC',watermark=datetime(2000,1,1,tzinfo=timezone.utc),rows_seen=7))
        self.cursor=self.cursors()

    def cursors(self):
        with self.db.session() as s: return [tuple(r) for r in s.execute(select(models.SyncCursorOrm.__table__))]

    def asset(self,key='A',unknown=False):
        with self.db.session() as s,s.begin():
            s.add(models.EquipmentOrm(id=key,description='SYNTHETIC',unit='CS01',
                sources={'maximo':{'assetnum':key,**({} if unknown else {'siteid':'BSR','orgid':'IP'})}}))

    def wo(self,key='BSR001',eq='A'):
        with self.db.session() as s,s.begin():
            s.add(models.WorkOrderOrm(id=key,equipment_id=eq,status='CAN',work_type='PM',
                                      source_changed_at=datetime(2000,1,1,tzinfo=timezone.utc)))

    def capture(self,domain,store=None):
        store=store or self.store; t=store.capture(domain); store.process(t); store.release(t)
        return t

    def current(self):
        with self.db.session() as s: return s.scalar(select(dm.family.c.current_id))

    def debt(self,register=True):
        self.wo(); t=self.store.capture('maintenance_event'); self.store.process(t)
        if register: self.store.register(t,self.current())
        self.store.release(t)
        self.capture('asset_master')
        return t

    def expired(self):
        with self.db.session() as s,s.begin(): s.execute(update(pm.lease).values(lease_until=datetime(2000,1,1,tzinfo=timezone.utc)))

    def complete(self):
        self.asset(); self.wo(); self.capture('asset_master'); self.capture('maintenance_event')

    def finish(self):
        assert self.cursors()==self.cursor,'synthetic source cursor changed'
        with self.db.engine.begin() as c:
            c.execute(text('GRANT USAGE ON SCHEMA '+self.schema+' TO nadi_b4_reader'))
            for name in pm.metadata.tables.keys()|dm.metadata.tables.keys():
                if name=='mart_capture_item':
                    columns=','.join(col.name for col in pm.item.c if col.name!='payload')
                    c.execute(text(f'GRANT SELECT ({columns}) ON mart_capture_item TO nadi_b4_reader'))
                else: c.execute(text('GRANT SELECT ON '+name+' TO nadi_b4_reader'))
            for name in ('mart_replay_queue','mart_replay_event','asset_master','maintenance_event'):
                c.execute(text('GRANT SELECT ON '+name+' TO nadi_b4_reader'))
        result={'schema':self.schema,'policy_digest':self.store.policy_digest}
        self.db.engine.dispose()
        return result


def prepare(url,root):
    result={}
    for name in SCENARIOS:
        f=Fixture(url,root,name)
        if name=='legacy':
            with f.db.session() as s,s.begin():
                s.execute(text("INSERT INTO mart_projection_state (projection_key,last_status,last_success_at,rows_seen,rows_written,updated_at) VALUES ('asset_master','SUCCEEDED',now(),0,0,now()),('maintenance_event','SUCCEEDED',now(),0,0,now())"))
        elif name in ('complete','column_grant','target_key_drift','latest_failed','old_complete_partial','target_drift','missing','index_drift','guard_drift','mixed'):
            f.complete()
            if name in ('old_complete_partial','mixed'):
                if name=='old_complete_partial':
                    with f.db.session() as s,s.begin():
                        rid=s.scalar(select(pm.lease.c.last_complete_run).where(pm.lease.c.domain=='maintenance_event'))
                        old=datetime.now(timezone.utc)-timedelta(hours=1)
                        s.execute(update(pm.run).where(pm.run.c.id==rid).values(completed_at=old))
                        s.execute(update(pm.lease).where(pm.lease.c.domain=='maintenance_event').values(last_complete_at=old))
                f.wo('BSR002','MISSING'); f.capture('maintenance_event')
            elif name=='latest_failed':
                f.wo('BSR002','MISSING')
                store=ReplayStore(f.db,enabled=True,exclusive_writer=True,controlled_transitions=True,replay_enabled=True,budget=Budget(rows=1))
                try: store.capture('maintenance_event')
                except BudgetExceeded: pass
                else: raise AssertionError('expected bounded failed capture')
            elif name=='target_drift':
                with f.db.session() as s,s.begin(): s.execute(text("UPDATE maintenance_event SET status='SYNTHETIC_DRIFT'"))
        elif name=='scope_unknown':
            f.asset(unknown=True); f.capture('asset_master'); f.capture('maintenance_event')
        elif name in ('unlinked','unlinked_repeated'):
            f.wo(); base=ProjectionStore(f.db,enabled=True,exclusive_writer=True)
            f.capture('maintenance_event',base)
            if name=='unlinked_repeated': f.capture('maintenance_event',base)
            f.capture('asset_master',base)
        elif name=='large':
            f.asset()
            for i in range(6): f.wo('BSR'+str(i))
            f.capture('asset_master'); f.capture('maintenance_event')
        else:
            f.debt()
            if name=='repeated': f.capture('maintenance_event')
            if name=='superseded':
                with f.db.session() as s,s.begin(): s.execute(update(models.WorkOrderOrm).values(equipment_id='MISSING2'))
                f.capture('maintenance_event')
            if name in ('replayed','projected','claimed','writing','retry','poison','stale_claim'):
                f.asset()
                if name=='poison':
                    # Policy adjustment is explicit synthetic enrollment, never an operational cap increase.
                    # Use default policy and three separately due actual failures.
                    for i in range(3):
                        with patch.object(f.store.writer,'persist_in_session',side_effect=RuntimeError('synthetic')):
                            try: ProjectionReplay(f.store,enabled=True).run('maintenance_event')
                            except CaptureError: pass
                        if i<2:
                            with f.db.session() as s,s.begin():
                                q=dict(s.execute(select(__import__('src.repositories.replay_models',fromlist=['queue']).queue)).mappings().one())
                                from src.repositories.projection_store import Ticket
                                rm=__import__('src.repositories.replay_models',fromlist=['queue'])
                                d=s.execute(select(pm.lease).where(pm.lease.c.domain=='maintenance_event')).mappings().one()
                                s.execute(update(pm.lease).where(pm.lease.c.domain=='maintenance_event').values(lease_until=datetime.now(timezone.utc)+timedelta(seconds=60)))
                                f.store._change(s,Ticket(q['run_id'],'maintenance_event',d['owner'],d['fence']),q,q['phase'],q['reason'],due_at=datetime(2000,1,1,tzinfo=timezone.utc))
                            f.expired()
                elif name=='retry':
                    with patch.object(f.store.writer,'persist_in_session',side_effect=RuntimeError('synthetic')):
                        try: ProjectionReplay(f.store,enabled=True).run('maintenance_event')
                        except CaptureError: pass
                elif name in ('claimed','writing','stale_claim'):
                    t=f.store.claim_due('maintenance_event')
                    if name!='claimed': f.store.capture_claim(t); f.store.reserve_attempt(t)
                    f.expired()
                    if name=='stale_claim': f.capture('maintenance_event')
                else:
                    def lost(): raise RuntimeError('synthetic ack loss')
                    try: ProjectionReplay(f.store,enabled=True).run('maintenance_event',after_commit=lost if name=='projected' else None)
                    except RuntimeError:
                        if name!='projected': raise
            if name=='absent':
                with f.db.session() as s,s.begin(): s.execute(delete(models.WorkOrderOrm))
                ProjectionReplay(f.store,enabled=True).run('maintenance_event')
        result[name]=f.finish()
        if name=='column_grant':
            db=Database(DbConfig(url.render_as_string(hide_password=False)))
            with db.engine.begin() as c:
                c.execute(text('GRANT INSERT(canonical_id) ON '+f.schema+'.asset_master TO nadi_b4_reader'))
            db.engine.dispose()
        if name=='wrong_policy':
            db=Database(DbConfig(url.render_as_string(hide_password=False)))
            with db.engine.begin() as c:
                c.execute(text('SET LOCAL search_path TO '+f.schema))
                c.execute(text('ALTER TABLE mart_deferred_family DISABLE TRIGGER deferred_family_guard'))
                c.execute(text("UPDATE mart_deferred_family SET policy_epoch='UNREVIEWED'"))
                c.execute(text('ALTER TABLE mart_deferred_family ENABLE TRIGGER deferred_family_guard'))
            db.engine.dispose()
        if name in ('missing','index_drift','guard_drift','target_key_drift'):
            # Post-grant fixture-only drift; preserve all operational systems.
            db=Database(DbConfig(url.render_as_string(hide_password=False)))
            with db.engine.begin() as c:
                c.execute(text('SET LOCAL search_path TO '+f.schema))
                c.execute(text({'missing':'DROP TABLE mart_replay_event','index_drift':'DROP INDEX replay_due',
                    'guard_drift':'ALTER TABLE mart_replay_queue DISABLE TRIGGER replay_queue_guard',
                    'target_key_drift':'ALTER TABLE maintenance_event DROP CONSTRAINT maintenance_event_pkey'}[name]))
            db.engine.dispose()
    return result
