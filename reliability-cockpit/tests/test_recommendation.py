"""Synthetic recommendations remain application proposals, never WO commands."""
import unittest
from datetime import timedelta
from unittest.mock import patch
from pydantic import ValidationError
from src.domain.engineering import EvidenceReference, EvidenceSnapshot, EvidenceKind, Principal, Role, EngineeringError
from src.domain.recommendation import RecommendationDraft
from src.domain.maintenance_context import ExistingWorkOrderReference, MaintenanceSources, MaximoWorkOrderIdentity
from src.services.recommendation import RecommendationService
from src.services.application_evidence import ApplicationEvidenceCatalog
import test_manual_inspection as inspection
from test_manual_inspection import ASSET, NOW, FixtureCatalog
from src.api.human_records import build_recommendation_router
from fastapi import FastAPI
from fastapi.testclient import TestClient

class Catalog(FixtureCatalog):
    def resolve(self,asset,kind,record,mode,actor,now):
        if kind!=EvidenceKind.ASSET or record!=ASSET:raise EngineeringError("EVIDENCE_NOT_FOUND",404)
        return EvidenceReference(reference_id="evidence:synthetic",record_id=record,canonical_asset_id=asset,kind=kind,
          source="CANONICAL_MART",mode=mode,stable_version="synthetic-1",observed_at=NOW,linked_at=now,linked_by=actor,
          identity_status="VERIFIED",signal_approval="NOT_APPLICABLE",snapshot=EvidenceSnapshot(label="Synthetic asset",availability="AVAILABLE") if mode=="FROZEN_SNAPSHOT" else None)
class Maintenance:
    def resolve_work_order(self,actor,asset,record):
        if record!="maintenance:SYNTHETIC:ONE":raise EngineeringError("EVIDENCE_NOT_FOUND",404)
        return ExistingWorkOrderReference(canonical_asset_id=asset,canonical_record_id=record,
          record_status="COMP",sources=MaintenanceSources(maximo=MaximoWorkOrderIdentity(source_record_ref="SYNTHETIC-WO")))

class RecommendationTest(unittest.TestCase):
    # Reuse fixture setup and helpers, not inspection-specific assertions.
    setUpBase=inspection.InspectionTest.setUp
    tearDown=inspection.InspectionTest.tearDown
    create=inspection.InspectionTest.create
    change=inspection.InspectionTest.change
    code=inspection.InspectionTest.code
    def setUp(self):
        self.setUpBase();self.catalog=Catalog();self.maintenance=Maintenance()
        self.service=RecommendationService(self.repo,self.catalog,self.maintenance,
          lambda ref:self.author if ref=="author" else None,lambda ref,asset:ref=="team:synthetic" and asset==ASSET,
          enabled=True,clock=lambda:self.now)
        self.draft=dict(canonical_asset_id=ASSET,case_ref="case:SYNTHETIC:ONE",rationale="Human interpretation requires follow-up",
          proposed_action="Propose an inspection; no execution authorization",priority="NORMAL",responsible_person_ref="author",
          responsible_team_ref="team:synthetic",target_date="2026-10-20",existing_work_order_ref="maintenance:SYNTHETIC:ONE",
          evidence_selections=[dict(kind="ASSET",record_id=ASSET)])
    def approved(self):
        row=self.change(self.create(),"SUBMIT",{})
        return self.change(row,"REVIEW",{"decision":"APPROVED","reason":"Reviewed proposal only"},self.reviewer)
    def test_exact_factual_refs_and_no_maintenance_authorization(self):
        row=self.create();self.assertEqual(row.existing_work_order.record_status,"COMP")
        self.assertEqual(row.supporting_evidence[0].linked_by,"author")
        self.assertEqual(row.action_authorization,"NOT_A_MAINTENANCE_AUTHORIZATION")
        self.assertEqual(row.follow_up_scope,"NADI_LOCAL_FOLLOW_UP_ONLY")
    def test_review_then_followup_with_immutable_source_snapshot(self):
        row=self.approved();before=row.existing_work_order.model_dump()
        for status in ("PLANNED","IN_PROGRESS","COMPLETED"):
            row=self.change(row,"FOLLOWUP",{"status":status,"reason":"Local tracking"},request=status)
        self.assertEqual(row.existing_work_order.model_dump(),before)
        self.assertEqual(row.follow_up_status,"COMPLETED")
        self.assertEqual(len(self.service.history(self.author,row.record_id)),6)
    def test_unreviewed_followup_denied(self):
        row=self.create();self.code("INVALID_TRANSITION",lambda:self.change(row,"FOLLOWUP",{"status":"PLANNED","reason":"x"}))
    def test_invalid_followup_and_terminal_mutation_denied(self):
        row=self.approved();self.code("INVALID_TRANSITION",lambda:self.change(row,"FOLLOWUP",{"status":"COMPLETED","reason":"skip"}))
        row=self.change(row,"FOLLOWUP",{"status":"CANCELLED","reason":"Withdrawn"},request="cancel")
        self.code("INVALID_TRANSITION",lambda:self.change(row,"FOLLOWUP",{"status":"PLANNED","reason":"x"},request="restart"))
        with self.assertRaises(ValidationError):self.change(row,"REOPEN",{"reason":"rewrite"},self.reviewer)
    def test_pic_cannot_independently_review(self):
        pic=self.reviewer;self.service.directory=lambda ref:pic
        self.draft["responsible_person_ref"]="reviewer"
        row=self.change(self.create(),"SUBMIT",{})
        self.code("INDEPENDENT_REVIEWER_REQUIRED",lambda:self.change(row,"REVIEW",{"decision":"APPROVED","reason":"x"},pic))
    def test_unresolved_case_wo_person_team_rejected(self):
        for field,value,code in (("case_ref","case:other","CASE_NOT_ACCESSIBLE"),("existing_work_order_ref","maintenance:other","EVIDENCE_NOT_FOUND"),
          ("responsible_person_ref","forged","INVALID_RESPONSIBLE_PERSON"),("responsible_team_ref","forged","INVALID_RESPONSIBLE_TEAM")):
            original=self.draft[field];self.draft[field]=value;self.code(code,self.create);self.draft[field]=original
    def test_client_factual_snapshot_and_maximo_command_rejected(self):
        for field,value in (("supporting_evidence",[]),("existing_work_order",{}),("maximo_action","CREATE"),("follow_up_status","COMPLETED")):
            with self.assertRaises(ValidationError):RecommendationDraft(**{**self.draft,field:value})
    def test_catalog_mismatch_or_false_provenance_rejected(self):
        ref=self.catalog.resolve(ASSET,EvidenceKind.ASSET,ASSET,"FROZEN_SNAPSHOT","author",NOW)
        for update,code in (({"canonical_asset_id":"asset:SYNTHETIC:B"},"EVIDENCE_IDENTITY_INVALID"),({"linked_by":"forged"},"EVIDENCE_PROVENANCE_INVALID")):
            with patch.object(self.catalog,"resolve",return_value=ref.model_copy(update=update)):
                self.code(code,self.create)
    def test_duplicate_evidence_and_blank_proposal_rejected(self):
        for extra in ({"rationale":" "},{"proposed_action":"x"*6001},{"evidence_selections":self.draft["evidence_selections"]*2}):
            with self.assertRaises(ValidationError):RecommendationDraft(**{**self.draft,**extra})
    def test_scoped_reads_replay_and_conflicts(self):
        row=self.create();self.assertEqual(self.create(),row)
        self.assertEqual(self.service.list(self.foreign)["total"],0)
        self.code("NOT_FOUND",lambda:self.service.history(self.foreign,row.record_id))
        self.change(row,"UPDATE",{**self.draft,"rationale":"new rationale"})
        self.code("REVISION_CONFLICT",lambda:self.change(row,"UPDATE",self.draft,request="stale"))
    def test_api_disabled_without_trusted_dependency(self):
        self.assertFalse(build_recommendation_router(self.service,enabled=True).routes)
        app=FastAPI();app.include_router(build_recommendation_router(self.service,enabled=True,trusted_principal_dependency=lambda:self.author))
        with TestClient(app) as c:
            r=c.post("/v1/engineering/recommendations",json={"request_id":"api","draft":self.draft})
            self.assertEqual(r.status_code,201,r.text);self.assertEqual(r.json()["existing_work_order"]["informational_only"],True)
    def test_application_case_adapter_checks_asset(self):
        class Cases:
            def get(self,actor,ref):return type("Case",(),{"canonical_asset_id":"asset:OTHER"})()
        wrapper=ApplicationEvidenceCatalog(self.catalog,Cases())
        self.code("CASE_ASSET_MISMATCH",lambda:wrapper.validate_case(self.author,ASSET,"case:exact"))
