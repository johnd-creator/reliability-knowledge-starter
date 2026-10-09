"""Synthetic source→context→inspection→review→case→recommendation acceptance.

HTTP is in-process TestClient only. Both stores are disposable fixtures. No source requests.
"""
import json, unittest, os
from threading import Event
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.engine import make_url
from datetime import timedelta
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError
from src.domain.engineering import EngineeringError, Principal, Role
from src.domain.condition_evidence import FreshnessPolicy
from src.repositories.application_boundary import ApplicationStore
from src.repositories.human_records import HumanRecordBase, HumanRecordRepository
from src.repositories.engineering import EngineeringBase, CaseRepository
from src.repositories.mart_models import MaintenanceEventMart
from src.services.application_identity import IdentityBase, SessionAuthority
from src.services.engineering_evidence import LocalEvidenceCatalog
from src.services.engineering import CaseService
from src.services.human_records import InspectionService
from src.services.reviewed_inspection_evidence import ReviewedInspectionCatalog
from src.services.application_evidence import ApplicationEvidenceCatalog
from src.services.recommendation import RecommendationService
from src.services.maximo_intelligence import LocalMaintenanceIntelligence
from src.services.asset_context import AssetContextService
from src.api.asset_context import build_asset_context_router
from src.api.engineering import build_router
from src.api.human_records import build_inspection_router, build_recommendation_router
import test_condition_evidence as condition
import test_application_identity as identity
from pathlib import Path


class BundleCIntegrationTest(unittest.TestCase):
    def application_engine(self):
        return create_engine("sqlite://",poolclass=StaticPool,connect_args={"check_same_thread":False})
    def setUp(self):
        self.pi = condition.ConditionProjectionTest(); self.pi.setUp()
        self.pi.project(self.pi.source_document({"synthetic-current": {"source_timestamp": "1970-01-01T00:00:00Z"}}))
        self.asset = condition.ASSET_ID; self.now = identity.NOW
        with self.pi.engine.begin() as c:
            c.execute(MaintenanceEventMart.__table__.insert().values(canonical_id="maintenance:SYNTHETIC:C",
                contract_version="1.0", id="WO-C", equipment_id=self.asset, work_order_id="WO-C", status="COMP", event_type="PM",
                source_changed_at=self.now, site_code="BSR", organization_code="IP", sources={},
                provenance={"ingested_at": self.now.isoformat()}, mart_created_at=self.now, mart_updated_at=self.now))
        self.mart=self.pi.reader()
        self.engine=self.application_engine()
        for metadata in (HumanRecordBase.metadata,EngineeringBase.metadata,IdentityBase.metadata):metadata.create_all(self.engine)
        self.store=ApplicationStore(self.engine,expected_database=self.engine.url.database if self.engine.dialect.name=="postgresql" else "bundle_c_test",isolated=True)
        self.provider=identity.FixtureProvider()
        for name,grant in list(self.provider.grants.items()):
            self.provider.grants[name]=grant.model_copy(update={"principal":grant.principal.model_copy(update={"asset_ids":frozenset({self.asset})})})
        self.directory=lambda subject: self.provider.current_grant(subject).principal if self.provider.current_grant(subject) else None
        self.authority=SessionAuthority(self.store,self.provider,origins={"https://nadi.example.invalid"},idle_seconds=300,absolute_seconds=3600,clock=lambda:self.now)
        self.local=LocalEvidenceCatalog(self.mart,clock=lambda:self.now)
        self.inspections=InspectionService(HumanRecordRepository(self.store),self.local,enabled=True,clock=lambda:self.now)
        self.catalog=ReviewedInspectionCatalog(self.local,self.inspections,self.directory)
        self.cases=CaseService(CaseRepository(self.engine),self.catalog,self.directory,enabled=True,clock=lambda:self.now)
        self.inspections.catalog=ApplicationEvidenceCatalog(self.catalog,self.cases)
        self.recommendations=RecommendationService(HumanRecordRepository(self.store),ApplicationEvidenceCatalog(self.catalog,self.cases),
            LocalMaintenanceIntelligence(self.mart),self.directory,lambda team,asset:team=="team:demo" and asset==self.asset,enabled=True,clock=lambda:self.now)
        self.context=AssetContextService(self.mart,cases=self.cases,inspections=self.inspections,recommendations=self.recommendations,enabled=True,clock=lambda:self.now)
        app=FastAPI(); dep=self.authority.dependency()
        for router in (build_router(self.cases,enabled=True,trusted_principal_dependency=dep),
                       build_inspection_router(self.inspections,enabled=True,trusted_principal_dependency=dep),
                       build_recommendation_router(self.recommendations,enabled=True,trusted_principal_dependency=dep),
                       build_asset_context_router(self.context,enabled=True,trusted_principal_dependency=dep)):app.include_router(router)
        self.client=TestClient(app,base_url="https://nadi.example.invalid");self.credentials={name:self.authority.establish(name) for name in ("author","reviewer")}

    def tearDown(self):
        self.client.close(); self.engine.dispose(); self.pi.tearDown()

    def call(self,method,path,body=None,actor="author",expected=200,headers=None):
        token,csrf=self.credentials[actor];self.client.cookies.set(self.authority.COOKIE,token)
        self.now+=timedelta(seconds=1)
        h={"Origin":"https://nadi.example.invalid","X-CSRF-Token":csrf,"Content-Type":"application/json",**(headers or {})}
        response=self.client.request(method,"/v1/engineering/"+path,json=body,headers=h)
        self.assertEqual(response.status_code,expected,response.text);return response.json()

    def create_inspection(self):
        return self.call("POST","inspections",{"request_id":"inspection-create","draft":{
            "canonical_asset_id":self.asset,"method":"VIBRATION","method_version":"proposal-1","inspector_ref":"author",
            "inspected_at":identity.NOW.isoformat(),"measurements":[{"quantity":"velocity","value":None,"unit":"mm/s","measured_at":identity.NOW.isoformat()},
                {"quantity":"observed_state","value":"trace","unit":None}],"observations":["Human reported observation"],"interpretations":["Unverified hypothesis"]}},expected=201)

    def step(self,resource,row,action,fields=None,actor="author",expected=200):
        record=row.get("record_id",row.get("case_id"));return self.call("POST",resource+"/"+record+"/"+action,
            {"request_id":resource+"-"+action+"-"+str(row["revision"]),"expected_revision":row["revision"],**(fields or {})},actor,expected)

    def approved_inspection(self):
        row=self.create_inspection();row=self.step("inspections",row,"submit")
        row=self.step("inspections",row,"begin_review",{"reason":"Independent review start"},"reviewer")
        return self.step("inspections",row,"review",{"decision":"APPROVED","reason":"Human record reviewed, no health claim"},"reviewer")

    def approved_case(self,inspection):
        row=self.call("POST","cases",{"request_id":"case-create","draft":{"canonical_asset_id":self.asset,
            "title":"Investigate synthetic finding","problem_statement":"Human interpretation requires a controlled check",
            "investigation":{"hypotheses":["Human hypothesis"]}}},expected=201)
        row=self.step("cases",row,"evidence",{"kind":"MANUAL_INSPECTION","record_id":inspection["record_id"],"mode":"FROZEN_SNAPSHOT"})
        row=self.step("cases",row,"submit")
        return self.step("cases",row,"review",{"decision":"APPROVED","reason":"Independent finding review"},"reviewer")

    def test_complete_trusted_http_workflow_preserves_lineage(self):
        with self.pi.engine.connect() as c:before=list(c.execute(select(MaintenanceEventMart.__table__)).mappings())
        initial=self.call("GET","asset-context/"+self.asset)
        self.assertEqual(initial["condition"]["mapping_readiness"],"MAPPING_VERIFIED")
        self.assertEqual(initial["condition"]["items"][0]["evidence"]["value"],12.5)
        inspection=self.approved_inspection();case=self.approved_case(inspection)
        human=case["evidence"][0]["snapshot"]["reviewed_inspection"]
        self.assertEqual((human["measurements"][0]["value"],human["measurements"][0]["unit"]),(None,"mm/s"))
        self.assertEqual(human["measurements"][1]["value"],"trace")
        self.assertEqual(human["reviewer"],"reviewer")
        row=self.call("POST","recommendations",{"request_id":"recommendation-create","draft":{
            "canonical_asset_id":self.asset,"case_ref":case["case_id"],"rationale":"Reviewed human finding",
            "proposed_action":"Propose bounded local follow-up","responsible_team_ref":"team:demo","responsible_person_ref":"author",
            "existing_work_order_ref":"maintenance:SYNTHETIC:C","evidence_selections":[{"kind":"MANUAL_INSPECTION","record_id":inspection["record_id"]}]}},expected=201)
        row=self.step("recommendations",row,"submit");row=self.step("recommendations",row,"review",{"decision":"APPROVED","reason":"Proposal reviewed"},"reviewer")
        for status in ("PLANNED","IN_PROGRESS","COMPLETED"):row=self.step("recommendations",row,"followup",{"status":status,"reason":"Local human report"})
        final=self.step("recommendations",row,"verify_completion",{"reason":"Local record reviewed; no Maximo closure",
            "evidence_selections":[{"kind":"MANUAL_INSPECTION","record_id":inspection["record_id"]}]},"reviewer")
        self.assertEqual(final["follow_up_status"],"VERIFIED")
        self.assertEqual(final["existing_work_order"]["record_status"],"COMP")
        result=self.call("GET","asset-context/"+self.asset)
        for name in ("cases","inspections","recommendations"):self.assertEqual(result[name]["total"],1)
        self.assertEqual(len(result["reviewed_inspections"]),1)
        self.assertEqual(result["assessment"],"NOT_ASSESSED")
        schema=json.loads((Path(__file__).resolve().parents[2]/"reliability-data-contracts/schemas/asset-context.schema.json").read_text())
        Draft202012Validator(schema,format_checker=FormatChecker()).validate(result)
        self.assertNotIn("secret",json.dumps(result).lower())
        with self.pi.engine.connect() as c:self.assertEqual(list(c.execute(select(MaintenanceEventMart.__table__)).mappings()),before)

    def test_spoofed_authority_self_review_revocation_csrf_denied(self):
        row=self.create_inspection();row=self.step("inspections",row,"submit")
        self.call("POST","inspections/"+row["record_id"]+"/begin_review",{"request_id":"spoof","expected_revision":row["revision"],"reason":"x"},headers={"X-Actor":"reviewer","X-Role":"REVIEWER"},expected=403)
        self.call("POST","inspections/"+row["record_id"]+"/begin_review",{"request_id":"origin","expected_revision":row["revision"],"reason":"x"},actor="reviewer",headers={"Origin":"https://evil.example.invalid"},expected=403)
        self.authority.revoke(self.directory("author"),self.credentials["author"][0])
        self.call("GET","asset-context/"+self.asset,expected=401)
        self.assertEqual(self.inspections.get(self.directory("author"),row["record_id"]).revision,2)

    def test_cross_asset_context_denied_before_local_queries(self):
        with patch.object(self.context.assets,"get_asset",side_effect=AssertionError("must not query")):
            self.call("GET","asset-context/asset:SYNTHETIC:OTHER",expected=404)

    def test_invalid_local_provider_is_not_exposed(self):
        row=self.approved_inspection();foreign={**row,"canonical_asset_id":"asset:FOREIGN"}
        with patch.object(self.inspections,"list",return_value={"items":[foreign],"total":1,"has_more":False}):
            result=self.call("GET","asset-context/"+self.asset)
        self.assertEqual(result["inspections"]["availability"],"INVALID_RECORD")
        self.assertNotIn("asset:FOREIGN",json.dumps(result));self.assertEqual(result["reviewed_inspections"],[])

    def test_unknown_source_freshness_is_separate_from_quality(self):
        result=self.call("GET","asset-context/"+self.asset)
        item=result["condition"]["items"][0]
        self.assertTrue(item["evidence"]["quality_good"])
        self.assertEqual(item["freshness"]["source"],"SOURCE_UNKNOWN")
        self.context.conditions.policy=FreshnessPolicy(source_max_age_seconds=60)
        stale=self.call("GET","asset-context/"+self.asset)["condition"]["items"][0]
        self.assertEqual(stale["freshness"]["source"],"SOURCE_STALE")
        self.assertTrue(stale["evidence"]["quality_good"])

    def test_mart_failure_keeps_unknown_not_empty_healthy(self):
        failure=OperationalError("private query",{},Exception("private details"))
        with patch.object(self.context.assets,"get_asset",side_effect=failure),patch.object(self.context.maintenance,"work_orders",side_effect=failure),patch.object(self.context.conditions,"asset_evidence",side_effect=failure):
            result=self.call("GET","asset-context/"+self.asset)
        self.assertEqual(result["identity_availability"],"UNAVAILABLE")
        self.assertIsNone(result["maintenance"]["total"])
        self.assertNotIn("private details",json.dumps(result))

    def test_new_paths_have_no_source_admin_or_operational_activation(self):
        root=Path(__file__).resolve().parents[1]
        for filename in ("src/services/asset_context.py", "src/services/reviewed_inspection_evidence.py",
                         "src/services/application_evidence.py", "src/services/recommendation.py", "src/api/asset_context.py"):
            content=(root/filename).read_text()
            for forbidden in ("PiClient", "OslcClient", "requests.", "httpx.", "PI_PASSWORD", "MAXIMO_READ_ONLY_TOKEN",
                              "RELIABILITY_MART_ADMIN_DATABASE_URL", "get_database(", "os.environ", "subprocess"):
                self.assertNotIn(forbidden, content, filename)
        from src.api.app import create_app
        routes=create_app().routes
        self.assertFalse(any(getattr(r,"path","").startswith("/v1/engineering") for r in routes))

    def test_unreviewed_inspection_cannot_become_case_evidence(self):
        row=self.create_inspection()
        with self.assertRaises(EngineeringError):self.catalog.resolve(self.asset,"MANUAL_INSPECTION",row["record_id"],"FROZEN_SNAPSHOT","author",self.now)



@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable application PostgreSQL fixture not configured")
class BundleCPostgresIntegrationTest(BundleCIntegrationTest):
    def application_engine(self):
        url = make_url(os.environ["NADI_APPLICATION_TEST_DSN"])
        if url.host not in {"127.0.0.1", "localhost"} or not url.database.endswith("_test"):
            raise RuntimeError("disposable local *_test only")
        engine = create_engine(url)
        root = Path(__file__).resolve().parents[1]
        with engine.begin() as c:
            c.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public")
            for name in ("002_engineering_workspace.sql", "003_application_identity.sql", "004_human_records.sql"):
                c.exec_driver_sql((root / "application-migrations" / name).read_text())
        return engine

    def test_case_revision_is_locked_through_recommendation_submission(self):
        inspection=self.approved_inspection(); case=self.approved_case(inspection)
        row=self.call("POST","recommendations",{"request_id":"concurrency-recommendation","draft":{
            "canonical_asset_id":self.asset,"case_ref":case["case_id"],"rationale":"Reviewed finding",
            "proposed_action":"Local proposal","evidence_selections":[{"kind":"MANUAL_INSPECTION","record_id":inspection["record_id"]}]}},expected=201)
        locked,release,finished=Event(),Event(),Event()
        original=self.recommendations.catalog.guard_case
        def guard(*args):
            result=original(*args);locked.set();release.wait(10);return result
        self.recommendations.catalog.guard_case=guard
        def submit():
            return self.recommendations.command(self.directory("author"),"SUBMIT",{},"locked-submit",record_id=row["record_id"],expected_revision=1)
        def reopen():
            result=self.cases.command(self.directory("reviewer"),"REOPEN",{"reason":"New investigation"},"reopen-after-submit",case_id=case["case_id"],expected_revision=case["revision"])
            finished.set();return result
        with ThreadPoolExecutor(max_workers=2) as pool:
            first=pool.submit(submit);self.assertTrue(locked.wait(10))
            second=pool.submit(reopen);self.assertFalse(finished.wait(.15));release.set()
            submitted=first.result(10);second.result(10)
        self.recommendations.catalog.guard_case=original
        self.assertEqual(submitted.reviewed_case.revision,case["revision"])
        with self.assertRaises(EngineeringError) as error:
            self.recommendations.command(self.directory("reviewer"),"REVIEW",{"decision":"APPROVED","reason":"x"},"stale-case-review",record_id=row["record_id"],expected_revision=submitted.revision)
        self.assertEqual(error.exception.code,"REVIEWED_CASE_REQUIRED")
        self.assertEqual(len(self.recommendations.history(self.directory("author"),row["record_id"])),2)
