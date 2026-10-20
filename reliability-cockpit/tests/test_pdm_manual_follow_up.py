"""Manual analysis + explicitly unverified reported SR references, no source writes."""
import copy,json,os,unittest
from hashlib import sha256
from pathlib import Path
from pydantic import ValidationError
from jsonschema import Draft202012Validator,FormatChecker
from src.domain.manual_inspection import InspectionDraft,ManualInspection
import test_bundle_c_integration as fixture
from test_pdm_input_capture import capture,legacy_document
from test_pdm_work_origin import DEPT,PM

ANALYSIS=dict(notes="  Synthetic engineer reasoning\nOriginal zero remains zero  ",recommended_follow_up="Synthetic human follow-up\nNo automatic diagnosis",provenance="HUMAN_ENTERED_ENGINEER_NOTES")
SR=dict(sr_number="  00012/SYNTHETIC  ",follow_up_note="Synthetic SR follow-up\nStatus not checked",system="MAXIMO",verification="REPORTED_UNVERIFIED")

class FollowUpContractTest(unittest.TestCase):
    def test_all_legacy_versions_exact_json_witnesses(self):
        expected={"1.0":"d338769072a913247618962fdac9f0354bb47b71f12140462e5533f414fa23f3","1.1":"006463493f56f271f5c8c27d9ee88a2e844fd8a1b14e25607e8bebbf2e50021c","1.2":"6c0f6ce97a03e7bb6a49c331389b37c5eecd6e0f697d71aa6a6aa1bf04926394","1.3":"8131aad0af352e895063b4338ec03d0f480a8966fd0138eec82fa8205a764e43"}
        for version,h in expected.items():
            data={**legacy_document(version),**({"input_capture":capture()} if version=="1.2" else {}),**({"work_origin":DEPT} if version=="1.3" else {})}
            row=ManualInspection.model_validate(data)
            self.assertEqual(sha256(row.model_dump_json().encode()).hexdigest(),h)
            self.assertNotIn("engineering_analysis",row.model_dump());self.assertNotIn("sr_references",row.model_dump())

    def test_manual_exact_text_and_unverified_sr_types_preserved(self):
        row=ManualInspection.model_validate({**legacy_document("1.4"),"engineering_analysis":ANALYSIS,"sr_references":[SR]})
        self.assertEqual(row.engineering_analysis.model_dump(mode="json"),ANALYSIS)
        self.assertEqual(row.sr_references[0].model_dump(mode="json"),SR)
        self.assertEqual(row.field_approval,"ENGINEER_FIELDS_PENDING");self.assertEqual(row.assessment,"NOT_ASSESSED")

    def test_bounded_strict_manual_notes_and_no_authority_fields(self):
        for extra in ({"notes":" "},{"notes":False},{"notes":"x"*6001},{"notes":""},{"recommended_follow_up":" "},{"recommended_follow_up":"x"*6001},{"provenance":"AUTO_DIAGNOSIS"},{"reviewer":"invented"},{"diagnosis_approved":True},{"recorded_by":"spoofed"}):
            with self.subTest(extra=extra),self.assertRaises(ValidationError):
                InspectionDraft.model_validate({**legacy_draft(),"engineering_analysis":{**ANALYSIS,**extra}})
        with self.assertRaises(ValidationError):InspectionDraft.model_validate({**legacy_draft(),"engineering_analysis":{"recommended_follow_up":"Ungrounded follow-up"}})

    def test_sr_is_informational_fixed_unverified_and_has_strict_bounds(self):
        for extra in ({"sr_number":""},{"sr_number":" "},{"sr_number":123},{"sr_number":"x"*101},{"verification":"VERIFIED"},{"system":"OTHER"},{"asset_id":"guessed"},{"url":"https://arbitrary.invalid"},{"status":"APPROVED"},{"follow_up_note":" "},{"follow_up_note":"x"*2001}):
            with self.subTest(extra=extra),self.assertRaises(ValidationError):
                InspectionDraft.model_validate({**legacy_draft(),"sr_references":[{**SR,**extra}]})
        for refs in ([SR,SR],[{**SR,"sr_number":str(i)} for i in range(11)]):
            with self.assertRaises(ValidationError):InspectionDraft.model_validate({**legacy_draft(),"sr_references":refs})

    def test_version_matrix_origin_and_capture_are_orthogonal_to_new_context(self):
        for origin in (None,DEPT,PM):
            for provisional in (False,True):
                for fields in ({"engineering_analysis":ANALYSIS},{"sr_references":[SR]},{"engineering_analysis":ANALYSIS,"sr_references":[SR]}):
                    data={**legacy_document("1.4"),**({"work_origin":origin} if origin else {}),**({"input_capture":capture()} if provisional else {}),**fields}
                    ManualInspection.model_validate(data)
                    for v in ("1.0","1.1","1.2","1.3"):
                        with self.assertRaises(ValidationError):ManualInspection.model_validate({**data,"contract_version":v})
        with self.assertRaises(ValidationError):ManualInspection.model_validate(legacy_document("1.4"))

    def test_published_schema_matches_and_denies_false_sr_verification(self):
        schema=json.loads((Path(__file__).resolve().parents[2]/'reliability-data-contracts/schemas/manual-inspection.schema.json').read_text())
        for k,v in ManualInspection.model_json_schema().items():self.assertEqual(schema[k],v)
        valid=ManualInspection.model_validate({**legacy_document("1.4"),"engineering_analysis":ANALYSIS,"sr_references":[SR]}).model_dump(mode='json')
        validator=Draft202012Validator(schema,format_checker=FormatChecker());validator.validate(valid)
        valid['sr_references'][0]['verification']='VERIFIED';self.assertTrue(list(validator.iter_errors(valid)))


def legacy_draft():return dict(canonical_asset_id='asset:SYNTHETIC:CAPTURE',method='OTHER',method_version='synthetic-1',inspector_ref='author')

class FollowUpWorkflowTest(unittest.TestCase):
    application_engine=fixture.BundleCIntegrationTest.application_engine
    setUp=fixture.BundleCIntegrationTest.setUp
    tearDown=fixture.BundleCIntegrationTest.tearDown
    call=fixture.BundleCIntegrationTest.call
    step=fixture.BundleCIntegrationTest.step
    def draft(self,origin=DEPT,provisional=False):
        return dict(canonical_asset_id=self.asset,method='OTHER',method_version='synthetic-package-1',inspector_ref='author',
            **({'work_origin':copy.deepcopy(origin)} if origin else {}),engineering_analysis=copy.deepcopy(ANALYSIS),sr_references=[copy.deepcopy(SR)],
            **({'input_capture':capture()} if provisional else {'measurements':[dict(quantity='Synthetic raw',value=0)],'observations':['Synthetic original finding'],'interpretations':['Synthetic unverified hypothesis']}))
    def create(self,draft=None,key='package-create'):
        return self.call('POST','inspections',dict(request_id=key,draft=draft or self.draft()),expected=201)

    def test_save_replay_readback_revision_history_and_no_recommendation_created(self):
        draft=self.draft();row=self.create(draft);self.assertEqual(row['contract_version'],'1.4')
        self.assertEqual(self.create(draft),row);self.assertEqual(self.call('GET','inspections/'+row['record_id']),row)
        revised=self.draft(PM);revised['engineering_analysis']['notes']='Synthetic corrected analysis';revised['sr_references']=[{**SR,'sr_number':'Synthetic SR2'}]
        changed=self.call('PUT','inspections/'+row['record_id'],dict(request_id='package-update',expected_revision=1,draft=revised))
        self.call('PUT','inspections/'+row['record_id'],dict(request_id='package-stale',expected_revision=1,draft=draft),expected=409)
        history=self.call('GET','inspections/'+row['record_id']+'/history')
        self.assertEqual(history[0]['snapshot']['engineering_analysis'],ANALYSIS);self.assertEqual(history[0]['snapshot']['sr_references'],[SR])
        self.assertEqual(history[1]['snapshot']['engineering_analysis']['notes'],'Synthetic corrected analysis')
        self.assertEqual(history[1]['snapshot']['work_origin'],PM)
        self.assertEqual(changed['measurements'][0]['value'],0)
        self.assertEqual(self.call('GET','recommendations')['items'],[])

    def test_individual_and_combined_clears_replace_old_context_and_keep_history(self):
        for i,keys in enumerate((("engineering_analysis",),("sr_references",),("work_origin",),("engineering_analysis","sr_references","work_origin"))):
            row=self.create(key="clear-create-"+str(i));draft=self.draft()
            for key in keys:draft.pop(key)
            changed=self.call('PUT','inspections/'+row['record_id'],dict(request_id='clear-edit-'+str(i),expected_revision=1,draft=draft))
            for key in ('engineering_analysis','sr_references','work_origin'):
                if key in keys:self.assertNotIn(key,changed)
                else:self.assertEqual(changed[key],row[key])
            self.assertEqual(changed['contract_version'],'1.1' if len(keys)==3 else '1.4')
            self.assertEqual(self.call('GET','inspections/'+row['record_id']),changed)
            self.assertEqual(self.call('GET','inspections/'+row['record_id']+'/history')[0]['snapshot'],row)

    def test_review_and_revise_do_not_verify_sr_or_certify_engineering_notes(self):
        row=self.create();row=self.step('inspections',row,'submit')
        self.step('inspections',row,'begin_review',dict(reason='Self review denied'),expected=403)
        row=self.step('inspections',row,'begin_review',dict(reason='Review record only'),'reviewer')
        row=self.step('inspections',row,'review',dict(decision='RETURNED',reason='Clarify context'),'reviewer')
        row=self.step('inspections',row,'revise',dict(reason='Manual correction'))
        self.assertEqual(row['engineering_analysis'],ANALYSIS);self.assertEqual(row['sr_references'],[SR])
        row=self.step('inspections',row,'submit');row=self.step('inspections',row,'begin_review',dict(reason='Independent record review'),'reviewer')
        row=self.step('inspections',row,'review',dict(decision='APPROVED',reason='Record only'),'reviewer')
        self.assertEqual(row['sr_references'][0]['verification'],'REPORTED_UNVERIFIED')
        self.assertEqual(row['field_approval'],'ENGINEER_FIELDS_PENDING');self.assertEqual(row['assessment'],'NOT_ASSESSED')
        self.assertEqual(row['approval_scope'],'NADI_RECORD_REVIEW_ONLY')

    def test_capture_notes_do_not_make_provisional_input_case_evidence(self):
        row=self.create(self.draft(PM,True));row=self.step('inspections',row,'submit')
        row=self.step('inspections',row,'begin_review',dict(reason='Manual source review'),'reviewer')
        row=self.step('inspections',row,'review',dict(decision='APPROVED',reason='Record only'),'reviewer')
        case=self.call('POST','cases',dict(request_id='package-case',draft=dict(canonical_asset_id=self.asset,title='Synthetic case',problem_statement='Human question')),expected=201)
        failure=self.step('cases',case,'evidence',dict(kind='MANUAL_INSPECTION',record_id=row['record_id'],mode='FROZEN_SNAPSHOT',expected_inspection_revision=row['revision']),expected=409)
        self.assertEqual(failure['detail']['code'],'PROVISIONAL_INPUT_NOT_CASE_EVIDENCE')
        self.assertEqual(self.call('GET','inspections/measurement-history')['items'],[])

    def test_existing_record_can_add_remove_context_without_fabricating_legacy_snapshots(self):
        draft=self.draft();draft.pop('engineering_analysis');draft.pop('sr_references')
        row=self.create(draft);self.assertEqual(row['contract_version'],'1.3')
        added=self.call('PUT','inspections/'+row['record_id'],dict(request_id='add-context',expected_revision=1,draft=self.draft()))
        removed=self.call('PUT','inspections/'+row['record_id'],dict(request_id='remove-context',expected_revision=added['revision'],draft=draft))
        self.assertNotIn('engineering_analysis',removed);self.assertNotIn('sr_references',removed)
        history=self.call('GET','inspections/'+row['record_id']+'/history')
        self.assertNotIn('engineering_analysis',history[0]['snapshot']);self.assertEqual(history[1]['snapshot']['sr_references'],[SR])

@unittest.skipUnless(os.getenv('NADI_APPLICATION_TEST_DSN'),'disposable QA PostgreSQL fixture not configured')
class FollowUpPostgresWorkflowTest(FollowUpWorkflowTest):
    application_engine=fixture.BundleCPostgresIntegrationTest.application_engine

@unittest.skipUnless(os.getenv('NADI_APPLICATION_TEST_DSN'),'disposable QA PostgreSQL fixture not configured')
class FollowUpQaValidationPostgresTest(unittest.TestCase):
    application_engine=fixture.BundleCPostgresIntegrationTest.application_engine
    tearDown=fixture.BundleCIntegrationTest.tearDown
    call=fixture.BundleCIntegrationTest.call
    draft=FollowUpWorkflowTest.draft
    create=FollowUpWorkflowTest.create
    def setUp(self):
        fixture.BundleCIntegrationTest.setUp(self)
        from fastapi.testclient import TestClient
        from src.api.engineering_qa import create_qa_app
        app=create_qa_app(authority=self.authority,cases=self.cases,inspections=self.inspections,recommendations=self.recommendations,context=self.context,environment='development')
        self.client.close();self.client=TestClient(app,base_url='https://nadi.example.invalid')
    def test_invalid_http_sanitized_no_mutation_or_lease_loss(self):
        bad=[{'engineering_analysis':{'notes':'PRIVATE-SYNTHETIC','provenance':'AUTO'}},{'sr_references':[{**SR,'verification':'VERIFIED'}]},
            {'sr_references':[{**SR,'status':'APPROVED'}]},{'sr_references':[SR]*2},{'engineering_analysis':{'notes':' '}}]
        for extra in bad:
            failure=self.call('POST','inspections',dict(request_id='invalid-package',draft={**self.draft(),**extra}),expected=422)
            self.assertEqual(failure,{'detail':{'code':'INVALID_REQUEST'}});self.assertNotIn('PRIVATE-SYNTHETIC',json.dumps(failure))
        self.assertEqual(self.call('GET','inspections')['items'],[]);self.assertEqual(self.create()['revision'],1)
    def test_csrf_reviewer_foreign_asset_attribution_and_revocation_are_enforced(self):
        row=self.create();path='inspections/'+row['record_id']
        self.call('PUT',path,dict(request_id='reviewer-analysis',expected_revision=1,draft=self.draft()),actor='reviewer',expected=403)
        self.call('PUT',path,dict(request_id='csrf-analysis',expected_revision=1,draft=self.draft()),headers={'X-CSRF-Token':'invalid'},expected=403)
        draft=self.draft();draft['inspector_ref']='reviewer';self.call('PUT',path,dict(request_id='spoofed-analysis',expected_revision=1,draft=draft),expected=422)
        self.assertEqual(self.call('GET',path),row)
        grant=self.provider.grants['author'];self.provider.grants['author']=grant.model_copy(update={'principal':grant.principal.model_copy(update={'asset_ids':frozenset({'asset:SYNTHETIC:FOREIGN'})})})
        self.call('GET',path,expected=404);self.provider.grants['author']=grant
        self.authority.revoke(self.directory('author'),self.credentials['author'][0]);self.call('GET',path,expected=401)
