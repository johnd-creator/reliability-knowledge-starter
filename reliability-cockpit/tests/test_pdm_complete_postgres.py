"""Public importer qualification, opt-in to an empty disposable database only.

No DROP/reset, operational login, source I/O, schema preparation on startup or
live-target adapter. Fixture accounts exist only inside this throwaway database.
"""
import os,json,tempfile,unittest,uuid
from pathlib import Path
from datetime import date
from unittest.mock import patch
from hashlib import sha256
from openpyxl import Workbook
from sqlalchemy import create_engine,inspect,select,func
from src.repositories.application_boundary import ApplicationStore
from src.repositories.application_migrations import ApplicationMigrator
from src.repositories.pdm_source_history import TABLES,Batch,Receipt,Cell,Event,Alias
from src.services.local_authentication import LocalIdentityProvider
from src.services.pdm_complete_plan import write_complete_plan,CompleteReader
from src.services.pdm_history_staging import iter_events
from src.services.pdm_complete_import import CompleteHistoryImporter,target,snapshot
from src.services.pdm_history_recovery import write_snapshot,validate_snapshot,business
from src.services.pdm_source_history import SourceHistoryService,digest
from src.domain.engineering import EngineeringError
import qa.live_server as qa
ASSET_ID=qa.ASSET_ID


@unittest.skipUnless(os.getenv('NADI_COMPLETE_HISTORY_TEST_DSN'),'empty disposable complete-history PostgreSQL required')
class CompleteHistoryPostgresTest(unittest.TestCase):
    def test_public_run_resume_replay_recovery_and_source_binding(self):
        engine=create_engine(os.environ['NADI_COMPLETE_HISTORY_TEST_DSN'],hide_parameters=True)
        target(engine)
        if inspect(engine).get_table_names():raise RuntimeError('EMPTY_COMPLETE_HISTORY_TEST_DATABASE_REQUIRED')
        ApplicationMigrator(engine,expected_database=engine.url.database,isolated=True).apply()
        store=ApplicationStore(engine,expected_database=engine.url.database,isolated=True);provider=LocalIdentityProvider(store)
        password='Disposable-complete-'+uuid.uuid4().hex
        admin=provider.bootstrap(username='history-admin',password=password,assets={ASSET_ID},operator_ref='SYNTHETIC_TEST_ONLY')
        subject=provider.create_account(provider.current_grant(admin),username='history-author',password=password,roles={'AUTHOR'},assets={ASSET_ID},require_change=False)
        fixture=qa.PersistentFixture.__new__(qa.PersistentFixture);fixture.engine=engine;fixture.store=store;fixture.asset=ASSET_ID;fixture.pi=qa.ConditionProjectionTest();fixture.pi.setUp();fixture.mart=fixture.pi.reader();fixture.wire(provider)
        try:
            with tempfile.TemporaryDirectory(prefix='complete-history-test-') as tmp:
                root=Path(tmp);root.chmod(0o700);book=root/'synthetic.xlsx';w=Workbook();sheet=w.active
                for key,value in {'A1':'Tanggal','B1':'V','B2':'mm/s','A3':'2020-01-02','B3':0,'C3':'Unclassified note','A4':'unknown date','B4':'=1+1'}.items():sheet[key]=value
                w.save(book);original=book.read_bytes();source={'id':'WB-SYNTHETIC','sha256':sha256(original).hexdigest()}
                profile={'id':'p','version':'SYNTHETIC','source_ref':source['id'],'sheet_index':0,'method':'VIBRATION','fields':[{'id':'f','source_label':'V','unit':'mm/s','header_cells':['B1'],'unit_cells':['B2'],'value_region':'B3:B4','row_role':'INPUT'}],'clocks':[{'role':'DATE','source_label':'Tanggal','header_cells':['A1']}]}
                catalog=root/'catalog.ts';catalog.write_text('export const captureSources='+json.dumps([source])+';\nexport const captureProfiles='+json.dumps([profile])+';')
                plan=root/'plan';manifest=write_complete_plan([{'source_ref':source['id'],'path':str(book)}],catalog,plan,as_of=date(2026,1,1))
                # Existing human sample, created by the normal service before import.
                reader=CompleteReader(book)
                try: payload=next(iter_events(reader,source,profile,date(2026,1,1)))['draft']
                finally:reader.close()
                payload['inspector_ref']=subject
                actor=provider.current_grant(subject).principal
                record=fixture.inspections.command(actor,'CREATE',payload,'synthetic-existing-sample')
                record_id=record.record_id
                importer=CompleteHistoryImporter(fixture.inspections,provider)
                with provider.guard(subject,provider.current_grant(subject).version):backup=write_snapshot(engine,root/'before.json')
                args=dict(access_asset_id=ASSET_ID,expected_plan_id=manifest['plan_id'],source_paths={source['sha256']:str(book)},recovery_snapshot=backup['path'],expected_snapshot_sha256=backup['sha256'])
                def lost(seq,result):
                    if result['aliases_added']:raise RuntimeError('SYNTHETIC_LOST_ACK')
                with self.assertRaisesRegex(RuntimeError,'SYNTHETIC_LOST_ACK'):importer.run(plan,subject,after_commit=lost,**args)
                result=importer.run(plan,subject,**args);self.assertTrue(result['complete']);self.assertGreaterEqual(result['replayed_chunks'],1)
                with engine.connect() as c:
                    before={name:digest(rows) for name,rows in snapshot(c).items()};self.assertEqual(c.scalar(select(func.count()).select_from(Cell)),manifest['counts']['cells']);self.assertEqual(c.scalar(select(func.count()).select_from(Event)),manifest['counts']['events'])
                replay=importer.run(plan,subject,**args);self.assertEqual(replay['committed_chunks'],0)
                with engine.connect() as c:self.assertEqual({name:digest(rows) for name,rows in snapshot(c).items()},before)
                service=SourceHistoryService(fixture.inspections,enabled=True);actor=provider.current_grant(subject).principal
                self.assertEqual(service.listing(actor)['total'],manifest['counts']['events'])
                with provider.guard(subject,provider.current_grant(subject).version):complete=write_snapshot(engine,root/'complete.json')
                with engine.begin() as c:self.assertEqual(validate_snapshot(c,complete['path'],complete['sha256'])['history'].keys(),TABLES.keys())
                with engine.connect() as c:
                    alias=dict(c.execute(select(Alias)).mappings().one())
                    self.assertEqual((alias['record_id'],alias['revision']),(record_id,1))
                    receipt=c.execute(select(Receipt)).mappings().all()
                    self.assertEqual(sum(len(r['document']['alias_proofs']) for r in receipt),1)
                # Later legitimate user edit, fresh preimage: replay must retain source rev1.
                payload['observations']=['SYNTHETIC legitimate later user revision']
                payload['input_capture']['rows'][0]['raw_value']=15
                revised=fixture.inspections.command(actor,'UPDATE',payload,'synthetic-later-user-edit',record_id=record_id,expected_revision=1)
                self.assertEqual(revised.revision,2)
                with provider.guard(subject,provider.current_grant(subject).version):fresh=write_snapshot(engine,root/'after-user-edit.json')
                args=dict(args,recovery_snapshot=fresh['path'],expected_snapshot_sha256=fresh['sha256'])
                with engine.connect() as c:before={name:digest(rows) for name,rows in snapshot(c).items()};business_before=business(c)
                again=importer.run(plan,subject,**args);self.assertEqual(again['committed_chunks'],0)
                with engine.connect() as c:
                    self.assertEqual(business(c),business_before)
                    self.assertEqual(dict(c.execute(select(Alias)).mappings().one()),alias)
                current=fixture.inspections.get(actor,record_id);self.assertEqual(current.revision,2)
                self.assertEqual(current.input_capture.rows[0].raw_value,15)
                self.assertEqual(len(fixture.inspections.history(actor,record_id)),2)
                detail=service.detail(actor,alias['event_key'])
                self.assertEqual((detail['aliases'][0]['source_revision'],detail['aliases'][0]['current_revision']),(1,2))
                # Wrong source bytes fail before a new fact/receipt, never silently change lineage.
                bad=root/'changed.xlsx';bad.write_bytes(original+b'SYNTHETIC_CHANGED')
                with self.assertRaisesRegex(EngineeringError,'ORIGINAL_WORKBOOK_CHANGED'):importer.run(plan,subject,**dict(args,source_paths={source['sha256']:str(bad)}))
                provider.change_account(provider.current_grant(admin),subject,roles={'REVIEWER'})
                with self.assertRaisesRegex(EngineeringError,'FORBIDDEN'):importer.run(plan,subject,**args)
                with engine.connect() as c:self.assertEqual({name:digest(rows) for name,rows in snapshot(c).items()},before)
                self.assertEqual(book.read_bytes(),original)
        finally:
            fixture.pi.tearDown();engine.dispose()

if __name__=='__main__':unittest.main()
