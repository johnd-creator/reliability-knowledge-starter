"""F-03 preparation only: real local projector, private disposable SQLite files.

No input DSN, roles, grants, source clients or operational backup/restore.
This does not qualify PostgreSQL locking, helper/global metadata or activation.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from src.config import DbConfig
from src.repositories.database import Database
from src.repositories import models, mart_models
from src.services.local_mart_projector import CollectorMartProjector

NOW = datetime(2026, 10, 19, 8, 0, tzinfo=timezone.utc)

class F03LocalRehearsalTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='nadi-f03-sqlite-', dir=os.environ.get('NADI_REHEARSAL_ROOT'))
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.source_path=self.root/'collector.sqlite'
        self.mart_path=self.root/'mart.sqlite'
        self.source=Database(DbConfig('sqlite+pysqlite:///'+str(self.source_path)))
        self.mart=Database(DbConfig('sqlite+pysqlite:///'+str(self.mart_path)))
        self.addCleanup(self.source.engine.dispose)
        self.addCleanup(self.mart.engine.dispose)
        self.source.create_all();self.mart.create_all()
        with self.source.session() as s:
            s.add(models.SyncCursorOrm(scope='mxwodetail',watermark=NOW,rows_seen=7,updated_at=NOW))
            s.add(models.CollectRunOrm(object_structure='mxwodetail-recovery-floor',mode='recovery-floor',watermark=NOW,started_at=NOW))
            s.commit()

    def asset(self, identity, stamp=NOW):
        with self.source.session() as s:
            s.add(models.EquipmentOrm(id=identity,unit='CS01',source_changed_at=stamp,
                sources={'maximo':{'assetnum':identity,'siteid':'BSR','orgid':'IP','eq11':'CS01','changedate':stamp.isoformat()}}))
            s.commit()

    def work_order(self, identity, asset, stamp=NOW):
        with self.source.session() as s:
            s.add(models.WorkOrderOrm(id=identity,equipment_id=asset,status='CAN',work_type='PM',source_changed_at=stamp))
            s.commit()

    @staticmethod
    def snapshot(path):
        with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as c:
            names=[x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            out={}
            for name in names:
                rows=c.execute('SELECT * FROM "'+name.replace('"','""')+'"').fetchall()
                encoded=sorted(json.dumps(row,default=str,separators=(',',':')) for row in rows)
                out[name]={'rows':len(rows),'sha256':hashlib.sha256('\n'.join(encoded).encode()).hexdigest()}
            return out

    def clone_private(self, source, name, expected_digest=None):
        # Test controller accepts only files it created under its own temporary
        # root. Existing destinations and corrupt archives are never overwritten.
        if source.parent.resolve()!=self.root or source.is_symlink():
            raise ValueError('owned disposable fixture required')
        if expected_digest and hashlib.sha256(source.read_bytes()).hexdigest()!=expected_digest:
            raise ValueError('archive digest mismatch')
        with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as c:
            if c.execute('PRAGMA quick_check').fetchone()!=('ok',):
                raise ValueError('invalid archive')
        target=self.root/name
        if target.parent.resolve()!=self.root:
            raise ValueError('new disposable destination required')
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
        with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src,sqlite3.connect(target) as dst:
            src.backup(dst)
        return target

    def test_interruption_records_failure_without_advancing_success_or_source_cursor(self):
        self.asset('A')
        CollectorMartProjector(self.source,self.mart,batch_size=1).project('asset_master')
        before=CollectorMartProjector(self.source,self.mart)._state('asset_master')
        self.asset('B',NOW+timedelta(minutes=1));self.asset('C',NOW+timedelta(minutes=2))
        source_before=self.snapshot(self.source_path)
        projector=CollectorMartProjector(self.source,self.mart,batch_size=1)
        persist=projector.writer.persist_collection
        calls=0
        def interrupted(collection):
            nonlocal calls
            calls+=1
            if calls==3:raise RuntimeError('SYNTHETIC_INTERRUPTION')
            return persist(collection)
        with patch.object(projector.writer,'persist_collection',side_effect=interrupted):
            with self.assertRaisesRegex(RuntimeError,'SYNTHETIC_INTERRUPTION'):
                projector.project('asset_master',incremental=True)
        failed=projector._state('asset_master')
        self.assertEqual(failed.last_status,'FAILED')
        self.assertEqual((failed.watermark,failed.last_success_at),(before.watermark,before.last_success_at))
        with self.mart.session() as s:self.assertEqual(s.query(mart_models.AssetMasterMartOrm).count(),2)
        restarted=CollectorMartProjector(self.source,self.mart,batch_size=1)
        self.assertTrue(restarted.project('asset_master',incremental=True).completed)
        self.assertEqual(restarted._state('asset_master').last_status,'SUCCEEDED')
        with self.mart.session() as s:self.assertEqual(s.query(mart_models.AssetMasterMartOrm).count(),3)
        stable=self.snapshot(self.mart_path)['asset_master']
        restarted.project('asset_master',incremental=True)
        self.assertEqual(self.snapshot(self.mart_path)['asset_master'],stable)
        self.assertEqual(self.snapshot(self.source_path),source_before)

    def test_first_failure_has_no_invented_success_or_watermark(self):
        self.asset('A')
        projector=CollectorMartProjector(self.source,self.mart)
        with patch.object(projector.writer,'persist_collection',side_effect=RuntimeError('SYNTHETIC_FIRST_FAILURE')):
            with self.assertRaises(RuntimeError):projector.project('asset_master')
        state=projector._state('asset_master')
        self.assertIsNotNone(state)
        self.assertEqual(state.last_status,'FAILED')
        self.assertIsNone(state.last_success_at)
        self.assertIsNone(state.watermark)
        recovered=CollectorMartProjector(self.source,self.mart).project('asset_master',incremental=True)
        self.assertEqual(recovered.mode,'full')
        self.assertTrue(recovered.completed)

    def test_private_separate_restore_roundtrips_all_fixture_tables_and_cursors(self):
        self.asset('A');self.work_order('BSR-1','A')
        CollectorMartProjector(self.source,self.mart,batch_size=1).project_all()
        for name,path in [('collector',self.source_path),('mart',self.mart_path)]:
            before=self.snapshot(path)
            archive=self.clone_private(path,name+'-backup.sqlite')
            digest=hashlib.sha256(archive.read_bytes()).hexdigest()
            restored=self.clone_private(archive,name+'-restored.sqlite',digest)
            self.assertNotEqual(restored,path)
            self.assertEqual(archive.stat().st_mode&0o777,0o600)
            self.assertEqual(restored.stat().st_mode&0o777,0o600)
            self.assertEqual(self.snapshot(restored),before)
            self.assertEqual(self.snapshot(path),before)
        self.assertEqual(self.snapshot(self.source_path)['sync_cursor']['rows'],1)
        self.assertEqual(self.snapshot(self.source_path)['collect_run']['rows'],1)

    def test_existing_restore_target_and_corrupt_backup_are_refused(self):
        existing=self.root/'preserve.sqlite';existing.write_bytes(b'SYNTHETIC_RETAIN')
        before=existing.read_bytes()
        with self.assertRaises(FileExistsError):self.clone_private(self.source_path,existing.name)
        self.assertEqual(existing.read_bytes(),before)
        archive=self.clone_private(self.source_path,'backup.sqlite')
        digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        archive.write_bytes(b'SYNTHETIC_CORRUPTION')
        with self.assertRaisesRegex(ValueError,'digest mismatch'):
            self.clone_private(archive,'must-not-exist.sqlite',digest)
        self.assertFalse((self.root/'must-not-exist.sqlite').exists())

    def test_missing_dependency_requires_full_reconciliation_on_legacy_projector(self):
        # This bounded witness preserves the known F-03 limitation: a later asset
        # does not itself replay arbitrarily old WO dependencies incrementally.
        self.work_order('BSR-OLD','LATE',NOW-timedelta(days=2))
        self.work_order('BSR-NEW','LATE',NOW)
        projector=CollectorMartProjector(self.source,self.mart,batch_size=1)
        first=projector.project('maintenance_event')
        self.assertEqual(first.skipped_missing_equipment,2)
        self.asset('LATE');projector.project('asset_master')
        projector.project('maintenance_event',incremental=True)
        with self.mart.session() as s:self.assertEqual(s.query(mart_models.MaintenanceEventMartOrm).count(),1)
        source_before=self.snapshot(self.source_path)
        self.assertTrue(projector.project('maintenance_event',incremental=False).completed)
        with self.mart.session() as s:self.assertEqual(s.query(mart_models.MaintenanceEventMartOrm).count(),2)
        self.assertEqual(self.snapshot(self.source_path),source_before)

    def test_failure_journal_error_does_not_mask_original_projection_error(self):
        self.asset('A')
        projector=CollectorMartProjector(self.source,self.mart)
        with patch.object(projector.writer,'persist_collection',side_effect=RuntimeError('SYNTHETIC_ORIGINAL')), patch.object(projector,'_save_failure',side_effect=RuntimeError('SYNTHETIC_JOURNAL_UNAVAILABLE')):
            with self.assertLogs('src.services.local_mart_projector',level='ERROR') as log:
                with self.assertRaisesRegex(RuntimeError,'SYNTHETIC_ORIGINAL'):
                    projector.project('asset_master')
        self.assertNotIn('SYNTHETIC_ORIGINAL',' '.join(log.output))
        self.assertNotIn('SYNTHETIC_JOURNAL_UNAVAILABLE',' '.join(log.output))
