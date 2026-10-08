"""Cross-component synthetic acceptance on SQLite and isolated canonical PostgreSQL.

No operational DSN/source calls. Reuse actual collector-owned guarded handoff.
Optional rendered React contract test requires Node dependencies locally.
"""
import asyncio
import copy
import json
import os
import subprocess
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
from sqlalchemy import text,select
from sqlalchemy.orm import Session
from src.api.app import create_app
from src.api import reliability as api
from src.domain.condition_evidence import EvidenceBatch,ConditionEvidence,ProjectionPlan,SignalSelection
from src.domain.integration_status import IntegrationStatus,CollectorObservation
from src.repositories.condition_store import ProjectionGateError
from src.services.condition_query import ConditionQueryService
from src.services.mart_migrations import run_migrations,FILES,LEDGER
import test_condition_evidence as fixture
import test_integration_status as integration_fixture
from test_condition_evidence import NOW,ASSET_ID,ROOT

async def asgi_request(app,path,method="GET"):
    sent=[]
    async def receive(): return {"type":"http.request","body":b"","more_body":False}
    async def send(message):sent.append(message)
    await app({"type":"http","asgi":{"version":"3.0"},"method":method,"path":path,"raw_path":path.encode(),"root_path":"","query_string":b"","headers":[],"scheme":"http","server":("fixture",80),"client":("fixture",1),"http_version":"1.1"},receive,send)
    status=next(x["status"] for x in sent if x["type"]=="http.response.start")
    body=b"".join(x.get("body",b"") for x in sent if x["type"]=="http.response.body")
    return status,json.loads(body) if body else None

class AcceptanceCases:
    approve=fixture.ConditionProjectionTest.approve
    source_document=fixture.ConditionProjectionTest.source_document
    project=fixture.ConditionProjectionTest.project
    read=fixture.ConditionProjectionTest.read
    component=integration_fixture.IntegrationStatusTest.component
    def service(self):
        service=integration_fixture.IntegrationStatusTest.service(self)
        self.addCleanup(lambda: service.database.engine.dispose() if service.database.engine is not self.engine else None)
        return service

    def test_real_asgi_condition_asset_and_platform_status_share_contract(self):
        self.project(self.source_document());service=self.service();app=create_app()
        with patch.object(api,"get_mart_database",return_value=service.database),patch.object(api,"_integration_service",return_value=service):
            code,condition=asyncio.run(asgi_request(app,"/v1/reliability/assets/"+ASSET_ID+"/condition-evidence"))
            self.assertEqual(code,200);self.assertEqual(condition["items"][0]["evidence"]["value"],12.5)
            for path in ("/v1/reliability/integration-status","/v1/reliability/assets/"+ASSET_ID+"/integration-status"):
                code,status=asyncio.run(asgi_request(app,path));self.assertEqual(code,200)
                self.assertEqual(status["coverage"]["projected_assets"],1);IntegrationStatus.model_validate(status)
                self.assertTrue(all(c["state"]=="CURRENT" for c in status["components"]))
                code,_=asyncio.run(asgi_request(app,path,"POST"));self.assertEqual(code,405)

    def test_full_attribute_reference_survives_selection_handoff_mart_and_http(self):
        from jsonschema import Draft202012Validator, FormatChecker
        self.store.retire_signal("synthetic-current")
        previous = None
        for length in (203, 512):
            with self.subTest(length=length):
                if previous:
                    self.store.retire_signal(previous)
                reference = "F1Ab" + "x" * (length - 4)  # Synthetic, never a source identity.
                identity = "synthetic-long-" + str(length)
                definition = SignalSelection(signal_id=identity, mapping_id=self.mapping_id,
                    sources={"pi": {"attribute_ref": reference}}, semantic_name="coal_flow",
                    approval_status="APPROVED", approved_by="synthetic-reviewer", approved_at=NOW,
                    evidence_ref="synthetic-long-reference-acceptance")
                self.store.approve_signal(definition)
                with self.assertRaisesRegex(ProjectionGateError, "SIGNAL_SELECTION_CONFLICT"):
                    self.store.approve_signal(definition)
                self.assertEqual(len(self.store.plan(ASSET_ID).signals), 1)
                document = self.source_document()
                EvidenceBatch.model_validate(document)
                for name, data in (("condition-evidence-batch", document),
                    ("condition-projection-plan", document["plan"]),
                    ("condition-signal-selection", document["plan"]["signals"][0]),
                    ("condition-evidence", document["results"][0]["evidence"])):
                    schema = json.loads((ROOT.parent / "reliability-data-contracts/schemas" / (name + ".schema.json")).read_text())
                    Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
                self.assertEqual(self.project(document)["written"], 1)
                first = self.read().model_dump(mode="json")
                self.assertEqual(first["items"][0]["evidence"]["sources"]["pi"]["attribute_ref"], reference)
                self.assertEqual(self.project(document)["written"], 0)
                self.assertEqual(self.read().model_dump(mode="json"), first)
                service = self.service()
                with patch.object(api, "get_mart_database", return_value=service.database):
                    code, payload = asyncio.run(asgi_request(create_app(), "/v1/reliability/assets/" + ASSET_ID + "/condition-evidence"))
                self.assertEqual(code, 200)
                self.assertEqual(payload["items"][0]["evidence"]["sources"]["pi"]["attribute_ref"], reference)
                previous = identity

    def test_oversized_attribute_reference_rejected_by_models_and_all_contracts(self):
        from jsonschema import Draft202012Validator, FormatChecker
        document = self.source_document()
        oversized = "F1Ab" + "x" * 509
        document["plan"]["signals"][0]["sources"]["pi"]["attribute_ref"] = oversized
        document["results"][0]["evidence"]["sources"]["pi"]["attribute_ref"] = oversized
        for name, model, data in (("condition-evidence-batch", EvidenceBatch, document),
            ("condition-projection-plan", ProjectionPlan, document["plan"]),
            ("condition-signal-selection", SignalSelection, document["plan"]["signals"][0]),
            ("condition-evidence", ConditionEvidence, document["results"][0]["evidence"])):
            with self.subTest(contract=name):
                with self.assertRaises(ValueError):
                    model.model_validate(data)
                schema = json.loads((ROOT.parent / "reliability-data-contracts/schemas" / (name + ".schema.json")).read_text())
                self.assertTrue(list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data)))

    def test_all_typed_values_and_bad_quality_cross_handoff_storage_query_status(self):
        for identity,semantic in (("text","running_status"),("digital","digital_status"),("boolean","interlock_status"),("null","outlet_temperature")):
            self.approve(identity,semantic)
        variants={"motor_current":{"Good":False,"Questionable":True,"Substituted":True,"Annotated":True},
            "running_status":{"Value":"RUNNING"},"digital_status":{"Value":{"Name":"RUN","Value":0,"IsSystem":False}},
            "interlock_status":{"Value":False},"outlet_temperature":{"Value":None}}
        self.project(self.source_document(variants));result=self.read()
        values={x.evidence.value_type:x.evidence for x in result.items}
        self.assertEqual(set(values),{"NUMERIC","TEXT","DIGITAL_STATE","BOOLEAN","NULL"})
        self.assertIsNone(values["NULL"].value);self.assertIs(values["BOOLEAN"].value,False)
        self.assertEqual(values["DIGITAL_STATE"].value.code,0);self.assertIs(values["DIGITAL_STATE"].value.is_system,False)
        self.assertEqual(values["NUMERIC"].evidence_status,"BAD_QUALITY")
        status=self.service().status();self.assertEqual(status.coverage.projected_signals,5)
        self.assertEqual(self.component(status,"PI_CONDITION_PROJECTION").quality,"BAD")

    def test_schema_and_models_accept_actual_collector_handoff_and_typed_variants(self):
        from jsonschema import Draft202012Validator,FormatChecker
        def schema(name):return json.loads((ROOT.parent/"reliability-data-contracts/schemas"/(name+".schema.json")).read_text())
        for variant in ({},{"Value":"RUNNING"},{"Value":None},{"Value":False},{"Value":{"Name":"OFF","Value":0,"IsSystem":False}},{"Good":False}):
            doc=self.source_document({"motor_current":variant});batch=EvidenceBatch.model_validate(doc)
            Draft202012Validator(schema("condition-evidence-batch"),format_checker=FormatChecker()).validate(doc)
            for name,model,data in (("condition-projection-plan",ProjectionPlan,doc["plan"]),
                ("condition-signal-selection",SignalSelection,doc["plan"]["signals"][0]),
                ("condition-evidence",ConditionEvidence,doc["results"][0]["evidence"])):
                Draft202012Validator(schema(name),format_checker=FormatChecker()).validate(data);model.model_validate(data)
            self.assertEqual(batch.results[0].evidence.value_type,doc["results"][0]["evidence"]["value_type"])
        result=self.service().status().model_dump(mode="json")
        Draft202012Validator(schema("integration-status"),format_checker=FormatChecker()).validate(result)
        # Exported status schemas must exactly track their Python contract definitions.
        for name,model in (("integration-status",IntegrationStatus),("collector-observation",CollectorObservation)):
            exported=schema(name);exported.pop("$id");exported.pop("$schema")
            self.assertEqual(exported,model.model_json_schema())

    def test_domain_and_schema_reject_bad_value_type_naive_time_and_raw_payload(self):
        from jsonschema import Draft202012Validator,FormatChecker
        schema=json.loads((ROOT.parent/"reliability-data-contracts/schemas/condition-evidence.schema.json").read_text())
        for field,value in (("value","12.5"),("source_timestamp","2026-10-07T12:00:00"),("source_timestamp",0),("raw_payload",{"secret":"unsafe"})):
            document=self.source_document()["results"][0]["evidence"];document[field]=value
            self.assertTrue(list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(document)))
            with self.assertRaises(ValueError):ConditionEvidence.model_validate(document)

    def test_no_direct_source_client_or_public_arbitrary_plan_proxy(self):
        for name in ("src/services/condition_projection.py","src/services/integration_status.py","src/api/reliability.py","src/repositories/integration_reader.py"):
            content=(ROOT/name).read_text()
            for forbidden in ("PiClient", "PI_USERNAME", "PI_PASSWORD", "PiApiConfig"):
                self.assertNotIn(forbidden,content)
        for route in create_app().routes:
            if "condition" in route.path or "integration-status" in route.path:
                self.assertEqual(route.methods,{"GET"})
                self.assertNotIn("attribute",route.path);self.assertNotIn("plan",route.path)

    def test_replay_conflict_older_batch_and_governance_change_across_handoff(self):
        document=self.source_document();self.assertEqual(self.project(document)["written"],1)
        self.assertEqual(self.project(document)["written"],0)
        changed=copy.deepcopy(document);changed["results"][0]["evidence"]["value"]=42
        with self.assertRaisesRegex(ProjectionGateError,"CONFLICTING_SAME_COLLECTION"):self.project(changed)
        older=copy.deepcopy(document);older["results"][0]["evidence"]["collected_at"]=(NOW-timedelta(minutes=1)).isoformat()
        self.assertEqual(self.project(older)["status"],"IGNORED_OLDER_BATCH")
        self.store.retire_signal("synthetic-current")
        with self.assertRaises(ProjectionGateError):self.project(document)
        self.assertEqual(self.service().status().coverage.projected_assets,0)

    def test_source_unavailable_does_not_reclassify_old_value_as_healthy(self):
        self.project(self.source_document());before=self.read().items[0].projected_at
        self.project(self.source_document({"motor_current":{"unavailable":True}}))
        status=self.service().status();projection=self.component(status,"PI_CONDITION_PROJECTION")
        self.assertIn("SOURCE_UNAVAILABLE",projection.degraded_reasons);self.assertEqual(projection.state,"DEGRADED")
        self.assertEqual(self.read().items[0].projected_at,before)

class ProjectionAcceptanceTest(AcceptanceCases,unittest.TestCase):
    setUp=fixture.ConditionProjectionTest.setUp
    tearDown=fixture.ConditionProjectionTest.tearDown
    reader=fixture.ConditionProjectionTest.reader

    @unittest.skipUnless((ROOT/"web/node_modules/typescript").exists(),"local UI dependencies not installed")
    def test_api_documents_render_actual_asset_evidence_and_trust_views(self):
        self.project(self.source_document({"motor_current":{"Value":None}}));service=self.service()
        condition=ConditionQueryService(service.database,policy=service.policy,clock=lambda:NOW).asset_evidence(ASSET_ID)
        document={"integration":service.status().model_dump(mode="json"),"condition":condition.model_dump(mode="json")}
        result=subprocess.run(["node","scripts/evidence-acceptance.mjs"],cwd=ROOT/"web",input=json.dumps(document),capture_output=True,text=True,check=True)
        rendered=json.loads(result.stdout)
        self.assertIn("Unknown",rendered["evidence"]);self.assertIn("UNKNOWN",rendered["trust"])
        self.assertNotIn("motor current: 0",rendered["evidence"])
        for page in ("app/assets/[...canonicalId]/page.tsx","app/data-quality/page.tsx"):
            self.assertIn("IntegrationStatusPanel",(ROOT/"web"/page).read_text())
        self.assertIn("ConditionEvidencePanel",(ROOT/"web/app/assets/[...canonicalId]/page.tsx").read_text())

@unittest.skipUnless(os.getenv("NADI_MART_TEST_DSN"),"isolated PostgreSQL fixture not configured")
class ProjectionPostgresAcceptanceTest(AcceptanceCases,unittest.TestCase):
    reader=fixture.ConditionPostgresTest.reader
    tearDown=fixture.ConditionProjectionTest.tearDown
    def setUp(self):
        fixture.ConditionPostgresTest.setUp(self)
        # Canonical projector metadata belongs to the accepted owning collector.
        # The migration fixture originally contains only the watermark anchor.
        with self.engine.begin() as c:
            c.exec_driver_sql("ALTER TABLE mart_projection_state ADD COLUMN last_status text")
            c.exec_driver_sql("ALTER TABLE mart_projection_state ADD COLUMN last_success_at timestamptz")
    def test_canonical_migration_order_idempotency_reader_and_writer_separation(self):
        with self.engine.connect() as c:
            names=list(c.scalars(text("SELECT filename FROM "+LEDGER+" ORDER BY filename")))
            self.assertEqual(names,list(FILES));self.assertEqual(c.scalar(text("SELECT count(*) FROM sync_cursor")),1)
        self.assertEqual(run_migrations(self.engine,expected_database=self.url.database,apply=True)["applied"],[])
        fixture.ConditionPostgresTest.test_reader_cannot_write_condition_tables_even_with_readonly_off(self)
        self.project(self.source_document());self.assertEqual(self.service().status().coverage.projected_assets,1)
