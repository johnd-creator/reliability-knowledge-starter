import unittest
from unittest.mock import patch
from pydantic import ValidationError
from sqlalchemy import select
from src.domain.engineering import EvidenceKind, EvidenceReference, EngineeringError, Role
from src.domain.manual_inspection import ManualInspection
from src.repositories.human_records import RevisionRow
from src.services.reviewed_inspection_evidence import ReviewedInspectionCatalog
import test_manual_inspection as manual

class InspectionWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.f=manual.InspectionTest();self.f.setUp()
        self.catalog=ReviewedInspectionCatalog(self.f.catalog,self.f.service,lambda ref:self.f.author if ref=='author' else None)
    def tearDown(self):self.f.tearDown()
    def submitted(self):return self.f.change(self.f.create(),'SUBMIT',{})
    def under_review(self):return self.f.change(self.submitted(),'BEGIN_REVIEW',{'reason':'Review record'},self.f.reviewer)
    def approved(self):return self.f.change(self.under_review(),'REVIEW',{'decision':'APPROVED','reason':'Human evidence only'},self.f.reviewer)
    def resolve(self,row):return self.catalog.resolve(manual.ASSET,EvidenceKind.MANUAL_INSPECTION,row.record_id,'FROZEN_SNAPSHOT','author',self.f.now)
    def test_full_explicit_workflow(self):
        row=self.f.create();self.assertEqual(row.status,'DRAFT')
        row=self.f.change(row,'SUBMIT',{});self.assertEqual(row.status,'SUBMITTED')
        row=self.f.change(row,'BEGIN_REVIEW',{'reason':'Independent review'},self.f.reviewer)
        self.assertEqual(row.status,'UNDER_REVIEW');self.assertEqual(row.review_started_by,'reviewer')
        row=self.f.change(row,'REVIEW',{'decision':'APPROVED','reason':'Record reviewed'},self.f.reviewer)
        self.assertEqual(row.contract_version,'1.1');self.assertEqual(row.assessment,'NOT_ASSESSED')
        self.assertEqual([h['snapshot']['status'] for h in self.f.service.history(self.f.author,row.record_id)],['DRAFT','SUBMITTED','UNDER_REVIEW','APPROVED'])
    def test_review_cannot_skip_under_review(self):
        row=self.submitted()
        with self.assertRaises(EngineeringError):
            self.f.service.command(self.f.reviewer,'REVIEW',{'decision':'APPROVED','reason':'Cannot skip'},'skip',record_id=row.record_id,expected_revision=row.revision)
    def test_returned_record_can_be_corrected_and_resubmitted(self):
        row=self.f.change(self.under_review(),'REVIEW',{'decision':'RETURNED','reason':'Clarify observation'},self.f.reviewer)
        self.assertEqual(row.status,'RETURNED')
        row=self.f.change(row,'REVISE',{'reason':'Correction'})
        self.assertIsNone(row.review_started_by);self.assertIsNone(row.review_started_at)
        row=self.f.change(row,'UPDATE',{**self.f.draft,'observations':['Clarified observation']})
        row=self.f.change(row,'SUBMIT',{},request='resubmit');self.assertEqual(row.status,'SUBMITTED')
    def test_own_start_review_and_other_reviewers_denied(self):
        row=self.submitted();owner=self.f.author.model_copy(update={'roles':frozenset({Role.AUTHOR,Role.REVIEWER})})
        with self.assertRaises(EngineeringError):
            self.f.change(row,'BEGIN_REVIEW',{'reason':'Self review'},owner)
        row=self.f.change(row,'BEGIN_REVIEW',{'reason':'Start'},self.f.reviewer)
        other=self.f.reviewer.model_copy(update={'principal_id':'other-reviewer'})
        with self.assertRaises(EngineeringError):
            self.f.change(row,'REVIEW',{'decision':'APPROVED','reason':'Take over'},other)
    def test_empty_inspection_cannot_be_submitted(self):
        self.f.draft={**self.f.draft,'observations':[],'interpretations':[],'measurements':[]}
        with self.assertRaises(EngineeringError):self.submitted()
    def test_unreviewed_and_returned_not_usable_evidence(self):
        row=self.f.create()
        with self.assertRaises(EngineeringError):self.resolve(row)
        row=self.f.change(row,'SUBMIT',{})
        row=self.f.change(row,'BEGIN_REVIEW',{'reason':'Start'},self.f.reviewer)
        row=self.f.change(row,'REVIEW',{'decision':'RETURNED','reason':'Clarify'},self.f.reviewer)
        with self.assertRaises(EngineeringError):self.resolve(row)
    def test_frozen_review_retains_measurement_units_times_and_revision(self):
        row=self.approved();ref=self.resolve(row);human=ref.snapshot.reviewed_inspection
        self.assertEqual(human.measurements,row.measurements)
        self.assertEqual(ref.identity_status,'REGISTERED');self.assertEqual(ref.freshness,'UNKNOWN')
        self.assertEqual(human.inspected_at,row.inspected_at);self.assertEqual(human.revision,row.revision)
        self.assertEqual(human.interpretation,'REVIEWED_HUMAN_EVIDENCE')
        before=ref.model_dump_json()
        self.f.change(row,'REOPEN',{'reason':'New observation'},self.f.reviewer)
        self.assertEqual(ref.model_dump_json(),before)
    def test_live_or_revoked_directory_lookup_rejected(self):
        row=self.approved()
        with self.assertRaises(EngineeringError):
            self.catalog.resolve(manual.ASSET,EvidenceKind.MANUAL_INSPECTION,row.record_id,'LIVE_REFERENCE','author',self.f.now)
        with patch.object(self.catalog,'directory',return_value=None):
            with self.assertRaises(EngineeringError):self.resolve(row)
    def test_tampered_human_lineage_and_source_verification_rejected(self):
        ref=self.resolve(self.approved()).model_dump(mode='json')
        with self.assertRaises(ValidationError):EvidenceReference.model_validate({**ref,'identity_status':'VERIFIED'})
        human=ref['snapshot']['reviewed_inspection'];human['record_id']='inspection:other'
        with self.assertRaises(ValidationError):EvidenceReference.model_validate(ref)
    def test_legacy_approved_record_remains_readable(self):
        row=self.approved().model_dump(mode='json')
        row.update(contract_version='1.0',review_started_by=None,review_started_at=None)
        self.assertEqual(ManualInspection.model_validate(row).status,'APPROVED')
    def test_stale_start_review_and_duplicate_replay_do_not_rewrite(self):
        row=self.submitted()
        reviewed=self.f.change(row,'BEGIN_REVIEW',{'reason':'Start'},self.f.reviewer,request='start')
        replay=self.f.service.command(self.f.reviewer,'BEGIN_REVIEW',{'reason':'Start'},'start',record_id=row.record_id,expected_revision=row.revision)
        self.assertEqual(replay,reviewed)
        with self.assertRaises(EngineeringError):
            self.f.change(row,'BEGIN_REVIEW',{'reason':'Other'},self.f.reviewer,request='stale')
        self.assertEqual(len(self.f.service.history(self.f.author,row.record_id)),3)
