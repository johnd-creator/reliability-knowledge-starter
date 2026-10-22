"""Synthetic owning-store/API/transaction regressions; no live resources."""
import copy, json, unittest
from pathlib import Path
from unittest.mock import patch
from sqlalchemy import select, func, create_engine
from src.repositories.pdm_source_history import metadata, Source, Profile, Cell, Event, Alias, Batch, Receipt, TABLES
from src.services.pdm_source_history import SourceHistoryService, digest
from src.services.pdm_complete_import import CompleteHistoryImporter, target, put
from src.services.pdm_history_staging import event_key
from src.api.pdm_source_history import build_source_history_router
from src.domain.engineering import Principal,Role,EngineeringError
import test_bundle_c_integration as bundle


class SourceHistoryTest(unittest.TestCase):
    def setUp(self):
        self.fixture=bundle.BundleCIntegrationTest();self.fixture.setUp();self.engine=self.fixture.engine
        metadata.create_all(self.engine);self.service=SourceHistoryService(self.fixture.inspections,enabled=True)
        self.fixture.client.app.include_router(build_source_history_router(self.service,trusted_principal_dependency=self.fixture.authority.dependency()))
        self.actor=self.fixture.provider.current_grant('author').principal
        self.source='a'*64;self.profile={'id':'p','version':'1','fields':[{'id':'f','source_label':'Velocity','unit':'mm/s','header_cells':['B1'],'unit_cells':['B2']}],'clocks':[]}
        self.ph=digest(self.profile);self.key=event_key(self.source,0,'p','ROW',3)
        self.doc={'kind':'MEASUREMENT_SOURCE','classification':'RAW_UNRESOLVED','reasons':['UNIT_UNKNOWN'],'fields':[{'field_id':'f','cell':'B3','role':'INPUT'}],'clocks':[],'clock_cells':[],'source_asset_label':'Synthetic source label','mapping':'UNVERIFIED_SOURCE_LABEL_ONLY'}
        self.row={'event_key':self.key,'owner_id':'author','access_asset_id':self.fixture.asset,'source_sha':self.source,'source_ref':'WB-X','sheet_index':0,'profile_id':'p','profile_hash':self.ph,'axis':'ROW','position':3,'classification_hash':'c'*64,'kind':'MEASUREMENT_SOURCE','classification':'RAW_UNRESOLVED','document':self.doc}
        with self.engine.begin() as c:
            c.execute(Source.insert().values(source_sha=self.source,document={'source_ref':'WB-X','sheets':[{'label':'Synthetic equipment','shape':[5,3]}]}))
            c.execute(Profile.insert().values(profile_hash=self.ph,document=self.profile))
            c.execute(Cell.insert().values(source_sha=self.source,sheet_index=0,coordinate='B3',terminal_role='INPUT',claims=['INPUT'],document={'raw_value':0,'source_type':'n'}))
            c.execute(Event.insert(),self.row)
    def tearDown(self):self.fixture.tearDown()
    def test_exact_source_zero_not_blank_and_readonly_http(self):
        page=self.fixture.call('GET','source-history');self.assertEqual(page['total'],1);self.assertFalse(page['canonical_eligible'])
        detail=self.fixture.call('GET','source-history/'+self.key);self.assertEqual(detail['fields'][0]['value']['raw_value'],0);self.assertFalse(detail['editable'])
        self.fixture.call('POST','source-history/'+self.key,{},expected=405)
        self.fixture.call('PUT','source-history/'+self.key,{},expected=405)
    def test_hidden_owner_asset_counts_and_proof_do_not_leak(self):
        for actor in [Principal(principal_id='other',roles={Role.AUTHOR},asset_ids={self.fixture.asset}),Principal(principal_id='author',roles={Role.AUTHOR},asset_ids={'foreign'})]:
            self.assertEqual(self.service.listing(actor)['total'],0)
            with self.assertRaisesRegex(EngineeringError,'NOT_FOUND'):self.service.detail(actor,self.key)
            self.assertEqual(self.service.batches(actor)['items'],[])
        # Full unclassified source is not automatically shared with reviewers/admins.
        for actor in [self.fixture.provider.current_grant('reviewer').principal,Principal(principal_id='other-admin',roles={Role.ADMIN},asset_ids={self.fixture.asset})]:
            with self.assertRaisesRegex(EngineeringError,'HISTORY_AUTHOR_SCOPE_REQUIRED'):self.service.listing(actor)
    def test_revoked_session_is_denied_by_existing_authority(self):
        self.fixture.call('GET','source-history')
        self.fixture.provider.grants.pop('author')
        self.fixture.call('GET','source-history',expected=401)
    def test_missing_schema_disabled_and_bad_filters(self):
        off=SourceHistoryService(self.fixture.inspections,enabled=False)
        with self.assertRaisesRegex(EngineeringError,'FEATURE_DISABLED'):off.listing(self.actor)
        with patch.object(self.service,'ready',return_value=False):
            with self.assertRaisesRegex(EngineeringError,'SCHEMA_PREREQUISITE'):self.service.listing(self.actor)
        for args in [{'limit':101},{'after':'wrong'},{'sheet_index':-1}]:
            with self.assertRaises(EngineeringError):self.service.listing(self.actor,**args)
    def test_forged_alias_snapshot_fingerprint_is_rejected(self):
        record=self.fixture.create_inspection()
        with self.engine.begin() as c:c.execute(Alias.insert().values(event_key=self.key,record_id=record['record_id'],revision=1,capture_hash='f'*64,relation='SOURCE_COMPLETE'))
        with self.assertRaisesRegex(EngineeringError,'ALIAS_PROOF_CHANGED'):self.service.detail(self.actor,self.key)
    def test_keyset_can_reach_beyond_legacy_offset_limit(self):
        rows=[]
        for i in range(10005):
            r=copy.deepcopy(self.row);r['event_key']=format(i,'064x');r['position']=i+10;rows.append(r)
        with self.engine.begin() as c:c.execute(Event.insert(),rows)
        after=format(10000,'064x');page=self.service.listing(self.actor,after=after,limit=100)
        self.assertEqual(page['total'],10006);self.assertEqual(len(page['items']),5)
        self.assertEqual(page['items'][0]['event_key'],format(10001,'064x'))
    def test_global_occurrence_uniqueness_does_not_include_custodian(self):
        with self.engine.begin() as c:
            with self.assertRaisesRegex(EngineeringError,'IMMUTABLE_HISTORY_CONFLICT'):put(c,Event,[dict(self.row,owner_id='different')])
        self.assertEqual(self.service.listing(self.actor)['total'],1)

    def test_long_raw_clocks_do_not_break_listing_and_remain_in_detail(self):
        clocks=[{'role':'DATE','precision':'RAW','value':None,'raw_value':'x'*30000} for _ in range(3)]
        rows=[]
        for i in range(25):
            row=copy.deepcopy(self.row);row['event_key']=format(i,'064x');row['document']['clocks']=clocks;row['document']['clock_cells']=['A3'];rows.append(row)
        with self.engine.begin() as c:
            c.execute(Event.insert(),rows)
            c.execute(Cell.insert().values(source_sha=self.source,sheet_index=0,coordinate='A3',terminal_role='CONTEXT',claims=[],document={'raw_value':'x'*30000}))
        page=self.service.listing(self.actor)
        self.assertLess(len(json.dumps(page).encode()),900*1024);self.assertTrue(page['items'][0]['raw_clock_values_in_detail'])
        self.assertEqual(self.service.detail(self.actor,format(0,'064x'))['clock_evidence'][0]['raw_value'],'x'*30000)
    def test_large_shared_proof_detail_pages_are_all_navigable(self):
        profile=copy.deepcopy(self.profile);profile['fields']=[dict(profile['fields'][0],id='f'+str(i),header_cells=['A1'],unit_cells=['A1']) for i in range(25)]
        doc=copy.deepcopy(self.doc);doc['fields']=[{'field_id':'f'+str(i),'cell':'B3','role':'INPUT'} for i in range(25)]
        with self.engine.begin() as c:
            c.execute(Profile.update().values(document=profile));c.execute(Event.update().values(document=doc))
            c.execute(Cell.insert().values(source_sha=self.source,sheet_index=0,coordinate='A1',terminal_role='CONTEXT',claims=[],document={'raw_value':'x'*30000}))
        offset=0;seen=[]
        while True:
            page=self.service.detail(self.actor,self.key,offset=offset)
            self.assertLess(len(json.dumps(page).encode()),1024*1024);seen.extend(f['field_id'] for f in page['fields'])
            if not page['has_more']:break
            self.assertEqual(page['next_offset'],offset+len(page['fields']));offset=page['next_offset']
        self.assertEqual(seen,['f'+str(i) for i in range(25)])
    def test_byte_bounded_listing_keyset_does_not_skip_large_summaries(self):
        rows=[]
        for i in range(30):
            row=copy.deepcopy(self.row);row['event_key']=format(i,'064x');row['document']['source_asset_label']='x'*60000;rows.append(row)
        with self.engine.begin() as c:c.execute(Event.insert(),rows)
        first=self.service.listing(self.actor,limit=25)
        self.assertTrue(first['has_more']);self.assertLess(len(first['items']),25)
        second=self.service.listing(self.actor,limit=25,after=first['next_after'])
        self.assertEqual(second['items'][0]['event_key'],format(len(first['items']),'064x'))


class CompleteChunkTest(unittest.TestCase):
    def setUp(self):
        SourceHistoryTest.setUp(self);self.importer=object.__new__(CompleteHistoryImporter);self.importer.engine=self.engine;self.importer.inspections=self.fixture.inspections
        self.batch='b'*64
        with self.engine.begin() as c:c.execute(Batch.insert().values(batch_id=self.batch,owner_id='author',access_asset_id=self.fixture.asset,manifest={},cursor=0,state='IMPORTING'))
    def tearDown(self):SourceHistoryTest.tearDown(self)
    def counts(self):
        with self.engine.connect() as c:return {n:c.scalar(select(func.count()).select_from(t)) for n,t in TABLES.items()}
    def chunk(self,items):
        with self.engine.begin() as c:return self.importer._chunk(c,self.batch,0,'profiles',items,'author',self.fixture.asset,{})
    def test_chunk_receipt_recovers_lost_ack_without_duplicate(self):
        profile={'id':'second','version':'2','fields':[]};item={'profile_hash':digest(profile),'document':profile}
        result=self.chunk([item]);self.assertEqual(result['inserted'],1);before=self.counts()
        # No journal/ack file: immutable receipt is sufficient.
        result=self.chunk([item]);self.assertTrue(result['replayed']);self.assertEqual(before,self.counts())
    def test_changed_payload_or_missing_committed_rows_is_not_repaired(self):
        profile={'id':'second','version':'2','fields':[]};item={'profile_hash':digest(profile),'document':profile};self.chunk([item])
        with self.assertRaisesRegex(EngineeringError,'RECEIPT_CONFLICT'):self.chunk([dict(item,document={'id':'different'})])
        with self.engine.begin() as c:c.execute(Profile.delete().where(Profile.c.profile_hash==item['profile_hash']))
        with self.assertRaisesRegex(EngineeringError,'COMMITTED_ROWS_MISSING'):self.chunk([item])
    def test_failure_after_facts_rolls_back_fact_receipt_and_cursor(self):
        profile={'id':'second','version':'2','fields':[]};item={'profile_hash':digest(profile),'document':profile};before=self.counts()
        import src.services.pdm_complete_import as module
        original=module.put
        def fail(c,table,rows,**kwargs):
            result=original(c,table,rows,**kwargs)
            if table is Profile:raise RuntimeError('SYNTHETIC_AFTER_FACTS')
            return result
        with patch.object(module,'put',side_effect=fail):
            with self.assertRaisesRegex(RuntimeError,'AFTER_FACTS'):self.chunk([item])
        self.assertEqual(before,self.counts())
        with self.engine.connect() as c:self.assertEqual(c.scalar(select(Batch.c.cursor).where(Batch.c.batch_id==self.batch)),0)
    def test_alias_comparison_preserves_numeric_versus_boolean_types(self):
        for number,boolean in [(0,False),(1,True)]:
            with self.subTest(number=number):
                with self.engine.begin() as c:
                    c.execute(Cell.update().values(document={'raw_value':number,'source_type':'n'}))
                    c.execute(Alias.delete());c.execute(Receipt.delete());c.execute(Batch.update().values(cursor=0))
                    item={'event_key':self.key,'source_sha256':self.source,**{k:self.row[k] for k in ('source_ref','sheet_index','profile_id','profile_hash','axis','position','classification_hash','document')}}
                    anchors={self.key:[{'record_id':'synthetic-revision','revision':1,'capture':{'rows':[{'value_region':'B3','raw_value':boolean,'unit':'mm/s'}]}}]}
                    self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
                    self.assertEqual(c.scalar(select(Alias.c.relation)),'SOURCE_CONFLICT')

    def test_absent_physical_blank_matches_null_but_never_zero(self):
        for value,expected in [(None,'SOURCE_COMPLETE'),(0,'SOURCE_CONFLICT')]:
            with self.subTest(value=value),self.engine.begin() as c:
                c.execute(Cell.delete());c.execute(Alias.delete());c.execute(Receipt.delete());c.execute(Batch.update().values(cursor=0))
                item={'event_key':self.key,'source_sha256':self.source,**{k:self.row[k] for k in ('source_ref','sheet_index','profile_id','profile_hash','axis','position','classification_hash','document')}}
                anchors={self.key:[{'record_id':'synthetic-revision','revision':1,'capture':{'rows':[{'value_region':'B3','raw_value':value,'unit':'mm/s'}]}}]}
                self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
                self.assertEqual(c.scalar(select(Alias.c.relation)),expected)

    def test_missing_committed_alias_is_not_silently_repaired_or_reported_complete(self):
        item={'event_key':self.key,'source_sha256':self.source,**{k:self.row[k] for k in ('source_ref','sheet_index','profile_id','profile_hash','axis','position','classification_hash','document')}}
        anchors={self.key:[{'record_id':'synthetic-revision','revision':1,'capture':{'rows':[{'value_region':'B3','raw_value':0,'unit':'mm/s'}]}}]}
        with self.engine.begin() as c:self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
        with self.engine.begin() as c:c.execute(Alias.delete())
        with self.assertRaisesRegex(EngineeringError,'COMMITTED_ROWS_MISSING'),self.engine.begin() as c:
            self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
        with self.engine.connect() as c:self.assertEqual(c.scalar(select(func.count()).select_from(Alias)),0)

    def alias_event(self):
        item={'event_key':self.key,'source_sha256':self.source,**{k:self.row[k] for k in ('source_ref','sheet_index','profile_id','profile_hash','axis','position','classification_hash','document')}}
        anchors={self.key:[{'record_id':'synthetic-revision','revision':1,'capture':{'rows':[{'value_region':'B3','raw_value':0,'unit':'mm/s'}]}}]}
        return item,anchors
    def commit_alias_event(self):
        item,anchors=self.alias_event()
        with self.engine.begin() as c:return self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
    def test_receipt_exact_alias_evidence_replay_ignores_later_revision_candidates(self):
        item,anchors=self.alias_event();committed=self.commit_alias_event();before=self.counts()
        self.assertEqual(len(committed['alias_proofs']),1)
        self.assertEqual(committed['alias_proofs'][0]['revision'],1)
        # New/current human revisions are not the immutable historical commit evidence.
        later=copy.deepcopy(anchors);later[self.key][0]['revision']=2;later[self.key][0]['capture']['rows'][0]['raw_value']=15
        with self.engine.begin() as c:
            replay=self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,later)
            self.assertEqual(c.scalar(select(Alias.c.revision)),1)
        self.assertTrue(replay['replayed']);self.assertEqual(replay['alias_proofs'],committed['alias_proofs']);self.assertEqual(self.counts(),before)
    def test_changed_committed_alias_is_rejected_without_repair(self):
        item,anchors=self.alias_event();self.commit_alias_event()
        with self.engine.begin() as c:c.execute(Alias.update().values(capture_hash='e'*64))
        before=self.counts()
        with self.assertRaisesRegex(EngineeringError,'IMMUTABLE_HISTORY_CONFLICT'),self.engine.begin() as c:
            self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
        with self.engine.connect() as c:self.assertEqual(c.scalar(select(Alias.c.capture_hash)),'e'*64)
        self.assertEqual(before,self.counts())
    def test_changed_receipt_alias_evidence_is_fingerprint_bound(self):
        item,anchors=self.alias_event();self.commit_alias_event()
        with self.engine.begin() as c:
            doc=copy.deepcopy(c.scalar(select(Receipt.c.document)));doc['alias_proofs'][0]['relation']='SOURCE_CONFLICT'
            c.execute(Receipt.update().values(document=doc))
        with self.assertRaisesRegex(EngineeringError,'RECEIPT_CONFLICT'),self.engine.begin() as c:
            self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
    def test_legacy_or_malformed_receipt_evidence_fails_closed(self):
        item,anchors=self.alias_event();self.commit_alias_event()
        with self.engine.connect() as c:original=copy.deepcopy(c.scalar(select(Receipt.c.document)))
        for change in [{'alias_proofs':None},{'schema':'legacy'},{'alias_proofs':[{'event_key':[]}]},{'alias_proofs':[{**original['alias_proofs'][0],'revision':True}]}]:
            with self.subTest(change=change):
                with self.engine.begin() as c:c.execute(Receipt.update().values(document={**original,**change}))
                with self.assertRaisesRegex(EngineeringError,'ALIAS_PROOF_INVALID'),self.engine.begin() as c:
                    self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,anchors)
    def test_alias_evidence_bound_rolls_back_whole_event_chunk(self):
        item,anchors=self.alias_event();before=self.counts()
        many={self.key:[{**anchors[self.key][0],'record_id':'synthetic-'+str(i)+'x'*80} for i in range(500)]}
        with self.assertRaisesRegex(EngineeringError,'HISTORY_ALIAS_CHUNK_BOUND'),self.engine.begin() as c:
            self.importer._chunk(c,self.batch,0,'events',[item],'author',self.fixture.asset,many)
        self.assertEqual(before,self.counts())

    def test_live_and_query_override_targets_refused_before_connect(self):
        for url in ['postgresql+psycopg://x@127.0.0.1:15443/nadi_local_dev_01_test','postgresql+psycopg://x@127.0.0.1:15956/maximo_collector','postgresql+psycopg://x@127.0.0.1:15956/pdm_history_complete_x_test?host=example.invalid']:
            engine=create_engine(url)
            try:
                with patch.object(engine,'connect',side_effect=AssertionError('must not connect')):
                    with self.assertRaisesRegex(EngineeringError,'DISPOSABLE_COMPLETE_HISTORY_ONLY'):target(engine)
            finally:engine.dispose()


if __name__=='__main__':unittest.main()
