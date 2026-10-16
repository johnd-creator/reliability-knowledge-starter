"""Generic cursor recovery with deterministic fakes: no network or DB."""
from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace
import re
import unittest
from src.adapters.maximo.oslc_client import OslcError, OslcPaginationLimitError, oslc_timestamp
from src.api.app import sync_config_for
from src.services.sync import ObjectSyncConfig, SyncService

C0,T1,T2 = [datetime(2026,8,d,tzinfo=timezone.utc) for d in (10,11,12)]
def row(identity,stamp):
    return dict(id=identity,changedate=stamp.isoformat(),statusdate=stamp.isoformat(),eq11='CS01',wonum='BSR-'+identity)

class Store:
    def __init__(self,cursor=C0):
        self.cursor,self.rows,self.runs,self.writes=cursor,{},[],[]
        self.fail,self.status_fail,self.history=set(),set(),{}
    def get_cursor(self,scope):return self.cursor
    def set_cursor(self,scope,stamp,count):
        self.cursor=stamp;self.writes.append((scope,stamp,count))
    def is_unchanged(self,kind,identity,column,stamp):
        return identity in self.rows and self.rows[identity].stamp==stamp
    def upsert_for(self,kind,entity):
        if entity.id in self.fail:raise RuntimeError('PRIVATE_SYNTHETIC_PAYLOAD')
        outcome='updated' if entity.id in self.rows else 'inserted'
        self.rows[entity.id]=entity
        return outcome
    def upsert_many_for(self,kind,entities):
        if any(e.id in self.fail for e in entities):raise RuntimeError('PRIVATE_SYNTHETIC_PAYLOAD')
        for e in entities:self.upsert_for(kind,e)
    def record_equipment_status(self,entity):
        if entity.id in self.status_fail:raise RuntimeError('PRIVATE_SYNTHETIC_PAYLOAD')
        self.history[entity.id]=entity.stamp
    def record_run(self,stats):self.runs.append(stats)

class Client:
    def __init__(self,rows,error=None):self.rows,self.error,self.calls=rows,error,[]
    def iterate(self,structure,**kw):
        self.calls.append(kw)
        match=re.search(r'(?:changedate|statusdate) >= "([^"]+)"',kw['where'])
        floor=oslc_timestamp(match[1]) if match else None
        for raw in self.rows:
            if floor is None or oslc_timestamp(raw['changedate'])>=floor:yield dict(raw)
        if self.error:raise self.error

class CursorRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.bad={'A'}
        def mapper(raw):
            if raw['id'] in self.bad:raise ValueError('PRIVATE_SYNTHETIC_PAYLOAD')
            return SimpleNamespace(id=raw['id'],stamp=oslc_timestamp(raw['changedate']))
        self.cfg=ObjectSyncConfig('mxapisr','service_request',mapper)
        self.source=[row('A',T1),row('B',T2)]
    def run_fake(self,store,cfg=None,client=None):
        return SyncService(client or Client(self.source),store).sync(cfg or self.cfg)
    def test_older_mapping_failure_recovers_unchanged_timestamp_after_restart(self):
        store=Store();first=self.run_fake(store)
        self.assertEqual(store.cursor,C0)
        self.assertFalse(first.complete);self.assertEqual(first.mode,'partial')
        self.assertEqual(set(store.rows),{'B'})
        self.bad.clear()  # local mapping repair only, source A stays T1
        self.assertTrue(self.run_fake(store).complete)  # fresh service/client
        self.assertEqual(store.rows['A'].stamp,T1)
        self.assertEqual(store.cursor,T2);self.assertEqual(len(store.rows),2)
    def test_first_full_failure_creates_no_cursor(self):
        store=Store(None)
        self.assertFalse(self.run_fake(store).complete)
        self.assertIsNone(store.cursor);self.assertEqual(store.writes,[])
        self.bad.clear();self.assertTrue(self.run_fake(store).complete)
        self.assertEqual(set(store.rows),{'A','B'})
    def test_repeated_failure_retains_cursor_and_idempotent_rows(self):
        store=Store()
        for _ in range(3):
            self.assertFalse(self.run_fake(store).complete)
            self.assertEqual(store.cursor,C0);self.assertEqual(set(store.rows),{'B'})
        self.assertEqual(store.writes,[]);self.assertEqual(len(store.runs),3)
    def test_tied_timestamp_and_inclusive_checkpoint_replay(self):
        self.source=[row('A',T2),row('B',T2)];store=Store()
        self.assertFalse(self.run_fake(store).complete)
        self.bad.clear();self.assertTrue(self.run_fake(store).complete)
        client=Client([row('C',T2)])
        self.assertTrue(self.run_fake(store,client=client).complete)
        self.assertEqual(set(store.rows),{'A','B','C'})
        self.assertIn('changedate >= ',client.calls[0]['where'])
    def test_descending_order_still_holds_cursor(self):
        self.source.reverse();store=Store()
        self.assertFalse(self.run_fake(store).complete);self.assertEqual(store.cursor,C0)
    def test_permissive_legacy_flag_cannot_opt_out(self):
        store=Store()
        self.assertFalse(self.run_fake(store,replace(self.cfg,cursor_requires_zero_errors=False)).complete)
        self.assertEqual(store.cursor,C0)
    def test_success_advances_empty_run_preserves_cursor(self):
        self.bad.clear();store=Store();result=self.run_fake(store)
        self.assertTrue(result.complete);self.assertEqual(result.inserted,2)
        self.assertEqual(result.upserted,2);self.assertEqual(store.cursor,T2)
        self.assertTrue(self.run_fake(store,client=Client([])).complete)
        self.assertEqual(store.cursor,T2)
    def test_row_persistence_failure_then_recovery(self):
        self.bad.clear();store=Store();store.fail.add('A')
        self.assertFalse(self.run_fake(store).complete)
        self.assertEqual(store.cursor,C0);self.assertEqual(set(store.rows),{'B'})
        store.fail.clear();self.assertTrue(self.run_fake(store).complete)
        self.assertEqual(set(store.rows),{'A','B'})
    def test_terminal_batch_failure_recorded_then_recovered(self):
        self.bad.clear();store=Store();store.fail.add('A')
        cfg=replace(self.cfg,entity_name='person',batch_size=100)
        result=self.run_fake(store,cfg)
        self.assertFalse(result.complete);self.assertEqual(store.cursor,C0)
        self.assertEqual(len(store.runs),1);self.assertEqual(result.errors,1)
        store.fail.clear();self.assertTrue(self.run_fake(store,cfg).complete)
        self.assertEqual(set(store.rows),{'A','B'})
    def test_failed_batch_does_not_poison_later_batches(self):
        self.bad.clear();self.source += [row('C',T2),row('D',T2)]
        store=Store();store.fail.add('A')
        result=self.run_fake(store,replace(self.cfg,entity_name='item',batch_size=2))
        self.assertFalse(result.complete);self.assertEqual(set(store.rows),{'C','D'})
        self.assertEqual(store.cursor,C0);self.assertEqual(result.errors,1)
    def test_network_and_page_failure_hold_cursor_and_retry(self):
        self.bad.clear()
        errors=[OslcError('PRIVATE_SYNTHETIC_PAYLOAD'),OslcPaginationLimitError('mxapisr',pages=1,max_pages=1,next_page_fingerprint='synthetic')]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                store=Store();result=self.run_fake(store,client=Client(self.source,error))
                self.assertFalse(result.complete);self.assertEqual(store.cursor,C0)
                self.assertEqual(result.pagination_error,type(error).__name__)
                self.assertTrue(self.run_fake(store).complete)
    def test_network_and_terminal_persistence_failure_both_recorded(self):
        self.bad.clear();store=Store();store.fail.add('A')
        result=self.run_fake(store,replace(self.cfg,batch_size=100),Client(self.source,OslcError('synthetic')))
        self.assertFalse(result.complete);self.assertEqual(store.cursor,C0)
        self.assertEqual(result.errors,2);self.assertEqual(len(store.runs),1)
    def test_expected_required_scope_exclusion_not_error(self):
        self.bad={'OUTSIDE'};store=Store()
        client=Client([dict(row('OUTSIDE',T2),eq11='CS02'),row('B',T1)])
        result=self.run_fake(store,replace(self.cfg,required_values=(('eq11','CS01'),)),client)
        self.assertTrue(result.complete);self.assertEqual(result.errors,0)
        self.assertEqual(result.skipped,1);self.assertEqual(store.cursor,T1)
    def test_expected_prefix_exclusion_not_error(self):
        self.bad.clear();store=Store()
        client=Client([dict(row('OUTSIDE',T2),wonum='OTHER'),row('B',T1)])
        result=self.run_fake(store,replace(self.cfg,prefix_field='wonum',allowed_prefixes=('BSR',)),client)
        self.assertTrue(result.complete);self.assertEqual(result.errors,0)
        self.assertEqual(store.cursor,T1)
        self.assertIn('wonum in ["BSR%"]',client.calls[0]['where'])
    def test_nonwatermarked_failure_partial_never_creates_cursor(self):
        store=Store(None);cfg=replace(self.cfg,watermark_field=None,compare_column=None,entity_name='labor')
        self.assertFalse(self.run_fake(store,cfg).complete);self.assertEqual(store.writes,[])
        self.bad.clear();self.assertTrue(self.run_fake(store,cfg).complete)
        self.assertIsNone(store.cursor)
    def test_equipment_status_failure_recovered_after_primary_upsert(self):
        self.bad.clear();store=Store();store.status_fail.add('A')
        cfg=replace(self.cfg,entity_name='equipment')
        self.assertFalse(self.run_fake(store,cfg).complete);self.assertEqual(store.cursor,C0)
        store.status_fail.clear();self.assertTrue(self.run_fake(store,cfg).complete)
        self.assertEqual(store.history['A'],T1)
    def test_error_logging_sanitizes_exception_message(self):
        with self.assertLogs('src.services.sync',level='WARNING') as logs:self.run_fake(Store())
        self.assertNotIn('PRIVATE_SYNTHETIC_PAYLOAD',str(logs.output))
        self.assertIn('ValueError',str(logs.output))
    def test_object_defaults_keep_specialized_and_nonwatermarked_paths(self):
        for name in ['mxapiasset','mxasset','mxapisr','mxperson','mxitem']:
            cfg=sync_config_for(name)
            self.assertTrue(cfg.cursor_requires_zero_errors,name)
            self.assertFalse(cfg.recent_work_orders);self.assertIsNotNone(cfg.watermark_field)
        self.assertTrue(sync_config_for('mxwodetail').recent_work_orders)
        self.assertIsNone(sync_config_for('mxapilabor').watermark_field)

    def test_every_generic_object_replays_failure_with_original_query_bounds(self):
        for name in ['mxapiasset','mxasset','mxapisr','mxperson','mxitem']:
            with self.subTest(object=name):
                self.bad={'A'}
                cfg=replace(sync_config_for(name),mapper=self.cfg.mapper)
                store,client=Store(),Client(self.source)
                self.assertFalse(self.run_fake(store,cfg,client).complete)
                self.assertEqual(store.cursor,C0)
                self.assertEqual(client.calls[0]['required_scope'],cfg.scope_clause)
                self.assertEqual(client.calls[0]['max_pages'],cfg.max_pages)
                self.assertEqual(client.calls[0]['page_size'],cfg.page_size)
                self.assertIn(cfg.watermark_field+' >= ',client.calls[0]['where'])
                self.bad.clear()
                self.assertTrue(self.run_fake(store,cfg).complete)
                self.assertEqual(set(store.rows),{'A','B'})
                self.assertEqual(store.rows['A'].stamp,T1)

    def test_comparison_failure_keeps_recovery_floor(self):
        self.bad.clear();store=Store()
        original=store.is_unchanged
        def broken(kind,identity,column,stamp):
            if identity=='A':raise RuntimeError('PRIVATE_SYNTHETIC_PAYLOAD')
            return original(kind,identity,column,stamp)
        store.is_unchanged=broken
        self.assertFalse(self.run_fake(store).complete)
        self.assertEqual(store.cursor,C0)
        store.is_unchanged=original
        self.assertTrue(self.run_fake(store).complete)
        self.assertEqual(set(store.rows),{'A','B'})

    def test_failed_batch_is_attempted_once_and_logs_no_payload(self):
        self.bad.clear();store=Store();store.fail.add('A')
        attempts=[];original=store.upsert_many_for
        def counted(kind,entities):
            attempts.append([e.id for e in entities])
            return original(kind,entities)
        store.upsert_many_for=counted
        with self.assertLogs('src.services.sync',level='WARNING') as logs:
            result=self.run_fake(store,replace(self.cfg,batch_size=100))
        self.assertFalse(result.complete)
        self.assertEqual(attempts,[['A','B']])
        self.assertEqual(result.upserted,0)
        self.assertEqual(result.skipped,2)
        self.assertNotIn('PRIVATE_SYNTHETIC_PAYLOAD',str(logs.output))
