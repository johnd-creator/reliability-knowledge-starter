"""Real HTTPS + disposable PostgreSQL advisory acceptance. No persistent QA DSN."""
import os, unittest
import test_bundle_d_http as legacy
from src.repositories.qa_advisory_schema import change_qa_advisory_schema
from src.domain.engineering import Principal, Role

@unittest.skipUnless(os.getenv('NADI_APPLICATION_TEST_DSN'), 'disposable PostgreSQL required')
class AdvisoryHttpTest(unittest.TestCase):
    def setUp(self):
        self.fx=legacy.RealHttpQaTest(methodName='test_records_survive_connection_reopen_and_conflict')
        original_engine=self.fx.application_engine
        def ready_engine():
            engine=original_engine()
            if engine.url.database != 'nadi_application_test':raise RuntimeError('disposable CI database only')
            change_qa_advisory_schema(engine,expected_database='nadi_application_test',acknowledgement='isolated-advisory-qa-only')
            return engine
        self.fx.application_engine=ready_engine
        self.fx.setUp()
    def tearDown(self):self.fx.tearDown()
    def published(self):
        f=self.fx
        inspection=f.create_inspection();inspection=f.step('inspections',inspection,'submit')
        inspection=f.step('inspections',inspection,'begin_review',{'reason':'Independent review'},'reviewer')
        inspection=f.step('inspections',inspection,'review',{'decision':'APPROVED','reason':'QA evidence checked'},'reviewer')
        case=f.approved_case(inspection)
        rec=f.call('POST','recommendations',{'request_id':'rec','draft':{'canonical_asset_id':f.asset,'case_ref':case['case_id'],'rationale':'Synthetic reviewed rationale','proposed_action':'Local follow-up only','evidence_selections':[{'kind':'MANUAL_INSPECTION','record_id':inspection['record_id']}]}},expected=201)
        rec=f.step('recommendations',rec,'submit');rec=f.step('recommendations',rec,'review',{'decision':'APPROVED','reason':'Reviewed proposal'},'reviewer')
        row=f.call('POST','advisories',{'request_id':'adv','draft':{'canonical_asset_id':f.asset,'recommendation_ref':rec['record_id'],'summary':'Synthetic QA advisory','finding':'Reviewed observation, no diagnosis inferred','evidence_caveat':'Synthetic evidence only','audiences':['OPERATIONS_QA','MAINTENANCE_QA']}},expected=201)
        row=f.step('advisories',row,'submit')
        f.step('advisories',row,'review',{'decision':'APPROVED','reason':'self'},expected=403)
        row=f.step('advisories',row,'review',{'decision':'APPROVED','reason':'Independent QA statement review'},'reviewer')
        f.step('advisories',row,'publish',{'reason':'self'},expected=403)
        return f.step('advisories',row,'publish',{'reason':'In-app QA only'},'reviewer')
    def test_real_https_receipt_csrf_origin_withdraw_and_audit(self):
        f=self.fx;row=self.published();path='inbox/'+row['record_id']+'/acknowledge'
        token,csrf=f.credentials['author'];f.client.cookies.clear();f.client.cookies.set(f.authority.COOKIE,token)
        payload={'request_id':'ack','expected_revision':row['revision']}
        for headers in ({'Origin':'https://evil.example.invalid','X-CSRF-Token':csrf},{'Origin':'https://nadi.example.invalid'}):
            self.assertEqual(f.client.request('POST','/v1/engineering/'+path,json=payload,headers=headers).status_code,403)
        ack=f.call('POST',path,payload);self.assertEqual(ack['status'],'ACKNOWLEDGED');self.assertEqual(ack,f.call('POST',path,payload))
        item=f.call('GET','inbox/'+row['record_id']);self.assertEqual(item['acknowledgement']['actor'],'author');self.assertEqual(item['viewed_status'],'NOT_RECORDED')
        row=f.step('advisories',row,'withdraw',{'reason':'Withdraw QA statement'},'reviewer')
        item=f.call('GET','inbox/'+row['record_id']);self.assertEqual(item['availability'],'WITHDRAWN')
        self.assertEqual(item['snapshot'],row['publication']['snapshot'])
        f.call('POST',path,payload,expected=409)
        self.assertEqual([e['action'] for e in f.call('GET','advisories/'+row['record_id']+'/history')],['CREATE','SUBMIT','REVIEW','PUBLISH','WITHDRAW'])
    def test_revoked_asset_and_identity_fail_closed_for_inbox(self):
        f=self.fx;row=self.published()
        grant=f.provider.grants['author']
        f.provider.grants['author']=grant.model_copy(update={'version':grant.version+1,'principal':Principal(principal_id='author',roles={Role.AUTHOR},asset_ids={'asset:FOREIGN'})})
        f.call('GET','inbox/'+row['record_id'],expected=401)
        f.call('GET','advisories/'+row['record_id']+'/history',expected=401)

@unittest.skipUnless(os.getenv('NADI_APPLICATION_TEST_DSN'), 'disposable PostgreSQL required')
class AdvisorySchemaGateTest(unittest.TestCase):
    def test_original_schema_keeps_advisory_routes_disabled(self):
        f=legacy.RealHttpQaTest(methodName='test_records_survive_connection_reopen_and_conflict')
        f.setUp()
        try:
            f.client.cookies.clear()
            self.assertEqual(f.client.request('GET','/v1/engineering/advisory-capability').status_code,401)
            self.assertEqual(f.call('GET','advisory-capability')['persistence'],'BLOCKED_SCHEMA_PREREQUISITE')
            f.call('GET','inbox',expected=404)
            f.call('POST','advisories',{},expected=404)
            self.assertEqual(f.call('GET','cases')['total'],0)
        finally:f.tearDown()
