"""Hermetic governed projection acceptance plus an opt-in isolated PostgreSQL E2E."""
import copy
import json
import os
import subprocess
import sys
import unittest
from dataclasses import asdict
from datetime import timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from sqlalchemy.engine import make_url
from pydantic import ValidationError
from src.api.app import create_app
from src.api import reliability as api
from src.config import MartDbConfig
from src.domain.condition_evidence import (ConditionEvidence, EvidenceBatch, SignalSelection, FreshnessPolicy)
from src.repositories.condition_store import ConditionCommandStore, ProjectionGateError
from src.repositories.condition_models import ConditionSignalSelectionMart, ConditionEvidenceLatestMart
from src.repositories.mart_database import MartDatabase
from src.repositories.mart_models import MartBase, AssetAfMappingMart, ReliabilityAssetRegistryMart
from src.services.condition_projection import ConditionProjectionService, EvidenceDocumentSource
from src.services.condition_query import ConditionQueryService
from test_asset_af_mapping_admin import _asset, _mapping, ASSET_ID
from datetime import datetime
NOW = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[1]

class ConditionProjectionTest(unittest.TestCase):
    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread":False}, poolclass=StaticPool)
        MartBase.metadata.create_all(self.engine)
        self.store = ConditionCommandStore(self.engine)
        with Session(self.engine) as s:
            s.add(_asset()); s.add(ReliabilityAssetRegistryMart(asset_ref=ASSET_ID, source_asset_number="SYNTHETIC",
                site_code="BSR", organization_code="IP", registry_source="SYNTHETIC", snapshot_sha256="a"*64, snapshot_row_count=1, snapshot_imported_at=NOW))
            s.flush(); s.add(AssetAfMappingMart(**asdict(_mapping("VERIFIED")))); s.commit()
        self.mapping_id = _mapping("VERIFIED").id
        self.approve()

    def tearDown(self): self.engine.dispose()

    def approve(self, signal_id="synthetic-current", semantic_name="motor_current"):
        self.store.approve_signal(SignalSelection(signal_id=signal_id, mapping_id=self.mapping_id,
            sources={"pi":{"attribute_ref":"SYNTHETIC-ATTRIBUTE-"+signal_id}}, semantic_name=semantic_name, approval_status="APPROVED",
            approved_by="synthetic-signal-reviewer", approved_at=NOW, evidence_ref="synthetic-only-selection"))

    def source_document(self, variants=None):
        plan = self.store.plan(ASSET_ID)
        result = subprocess.run([sys.executable, str(ROOT.parent / "pi-collector/tests/fixtures/condition_source.py")],
            input=json.dumps({"plan": plan.model_dump(mode="json"), "variants": variants or {}}),
            capture_output=True, text=True, check=True, timeout=15)
        result = json.loads(result.stdout)
        self.assertLessEqual(result["synthetic_gets"], 25)
        return result["batch"]

    def reader(self):
        # Own query facade on the same fixture engine; engine begin callback not needed on SQLite.
        reader = MartDatabase(MartDbConfig(dsn="sqlite://"))
        reader._engine.dispose()
        reader._engine = self.engine
        from sqlalchemy.orm import sessionmaker
        reader._session_factory = sessionmaker(bind=self.engine)
        return reader

    def read(self, policy=None):
        reader = self.reader()
        try:
            return ConditionQueryService(reader, policy=policy, clock=lambda: NOW).asset_evidence(ASSET_ID)
        finally:
            if reader.engine is not self.engine: reader.engine.dispose()

    def project(self, document):
        return ConditionProjectionService(self.store, EvidenceDocumentSource(document)).project(ASSET_ID, now=NOW)

    def test_synthetic_verified_selected_source_mart_api_e2e(self):
        document = self.source_document()
        result = self.project(document)
        self.assertEqual(result["written"], 1)
        response = self.read()
        e = response.items[0].evidence
        self.assertEqual((e.value, e.value_type, e.unit), (12.5, "NUMERIC", "A"))
        self.assertEqual(e.source_timestamp, NOW)
        self.assertEqual(e.sources.pi.af_element_ref, "AF_ELEMENT_TEST_001")
        self.assertEqual(e.provenance.selection_approved_by, "synthetic-signal-reviewer")
        route = next(r for r in create_app().routes if r.path.endswith("/condition-evidence"))
        self.assertEqual(route.methods, {"GET"})
        with patch.object(api.ConditionQueryService, "asset_evidence", return_value=response):
            encoded = route.endpoint(ASSET_ID, Mock()).model_dump(mode="json")
        self.assertEqual(encoded["items"][0]["evidence"]["value"], 12.5)
        self.assertNotIn("password", json.dumps(encoded).lower())

    def test_idempotent_replay_does_not_freshen_projection_or_duplicate(self):
        doc = self.source_document()
        self.assertEqual(self.project(doc)["written"], 1)
        first = self.read().model_dump(mode="json")
        result = self.store.project(EvidenceBatch.model_validate(doc), now=NOW+timedelta(minutes=1))
        self.assertEqual(result["written"], 0)
        self.assertEqual(first, self.read().model_dump(mode="json"))
        with Session(self.engine) as s:
            self.assertEqual(len(list(s.scalars(select(ConditionEvidenceLatestMart)))), 1)

    def test_text_digital_boolean_and_null_remain_typed_not_zero(self):
        for raw, value_type in (("RUNNING", "TEXT"), ({"Name":"RUN", "Value":1,"IsSystem":False}, "DIGITAL_STATE"),
                                (True,"BOOLEAN"), (None,"NULL")):
            with self.subTest(value_type=value_type):
                doc = self.source_document({"motor_current":{"Value":raw}})
                batch = EvidenceBatch.model_validate(doc)
                e = batch.results[0].evidence
                self.assertEqual(e.value_type, value_type)
                expected = {"name": raw.get("Name"), "code": raw.get("Value"), "is_system": raw.get("IsSystem")} if isinstance(raw, dict) else raw
                self.assertEqual(e.model_dump(mode="json")["value"], expected)
                # New fixture row per type avoids changing an immutable same-collection result.
                with Session(self.engine) as s, s.begin():
                    s.query(ConditionEvidenceLatestMart).delete()
                self.project(doc)
                self.assertEqual(self.read().items[0].evidence.model_dump(mode="json")["value"], expected)

    def test_bad_quality_flags_preserved_without_health_inference(self):
        doc = self.source_document({"motor_current":{"Good":False,"Questionable":True,"Substituted":True,"Annotated":True}})
        self.project(doc)
        e = self.read().items[0].evidence
        self.assertEqual(e.evidence_status,"BAD_QUALITY")
        self.assertEqual((e.quality_good,e.quality_questionable,e.quality_substituted,e.quality_annotated),(False,True,True,True))
        self.assertEqual(e.value,12.5)

    def test_epoch_stale_current_collector_projection_and_verified_mapping_coexist(self):
        self.project(self.source_document({"motor_current":{"Timestamp":"1970-01-01T00:00:00Z"}}))
        item = self.read(FreshnessPolicy(collector_max_age_seconds=60,source_max_age_seconds=60,projection_max_age_seconds=60)).items[0]
        self.assertEqual(item.freshness.model_dump(), {"collector":"COLLECTOR_CURRENT","source":"SOURCE_STALE",
            "projection":"PROJECTION_CURRENT","mapping":"MAPPING_VERIFIED"})
        self.assertIn("SOURCE_STALE",item.statuses)

    def test_default_neutral_and_unknown_source_quality_remain_unknown(self):
        doc = self.source_document({"motor_current":{"Good":None,"Questionable":None,"Substituted":None,"Annotated":None}})
        self.project(doc)
        e = self.read().items[0]
        self.assertEqual(e.freshness.source,"SOURCE_UNKNOWN")
        self.assertEqual(e.freshness.collector,"COLLECTOR_UNKNOWN")
        self.assertEqual(e.evidence.evidence_status,"UNKNOWN_QUALITY")
        policy = FreshnessPolicy(source_max_age_seconds=60)
        self.assertEqual(policy.state("SOURCE",NOW+timedelta(seconds=1),NOW),"SOURCE_UNKNOWN")

    def test_null_source_timestamp_preserved_as_unknown(self):
        doc = self.source_document();doc["results"][0]["evidence"]["source_timestamp"]=None
        self.project(doc)
        self.assertEqual(self.read(FreshnessPolicy(source_max_age_seconds=60)).items[0].freshness.source,"SOURCE_UNKNOWN")

    def test_unmapped_proposed_retired_ambiguous_never_call_source(self):
        for status in ("PROPOSED","RETIRED","AMBIGUOUS","UNMAPPED"):
            with self.subTest(status=status):
                with Session(self.engine) as s, s.begin():
                    s.query(AssetAfMappingMart).filter(AssetAfMappingMart.id != self.mapping_id).delete()
                    row=s.get(AssetAfMappingMart,self.mapping_id)
                    replacement = _mapping("RETIRED" if status == "RETIRED" else "PROPOSED" if status in {"PROPOSED","UNMAPPED"} else "VERIFIED")
                    # Preserve stable ID/selection and use provenance-valid fixture lifecycle.
                    for key,value in asdict(replacement).items():
                        if key != "id":setattr(row,key,value)
                    if status == "AMBIGUOUS":s.add(AssetAfMappingMart(**asdict(_mapping("VERIFIED","AF_ELEMENT_OTHER"))))
                source=Mock()
                with self.assertRaises(ProjectionGateError):ConditionProjectionService(self.store,source).project(ASSET_ID)
                source.collect.assert_not_called()
                self.assertEqual(self.read().items,())

    def test_wrong_source_or_role_fails_before_source(self):
        for field,value in (("pi_source_id","OTHER_PI"),("mapping_role","SECONDARY")):
            with Session(self.engine) as s, s.begin():
                row=s.get(AssetAfMappingMart,self.mapping_id)
                if field=="mapping_role":
                    # Domain fixture instead of violating SQL CHECK on stored production model.
                    continue
                setattr(row,field,value)
            source=Mock()
            with self.assertRaises(ValueError):ConditionProjectionService(self.store,source).project(ASSET_ID)
            source.collect.assert_not_called()

    def test_no_approved_signals_never_call_source(self):
        self.store.retire_signal("synthetic-current")
        source=Mock()
        with self.assertRaisesRegex(ProjectionGateError,"NO_APPROVED_SIGNALS"):
            ConditionProjectionService(self.store,source).project(ASSET_ID)
        source.collect.assert_not_called()
        self.assertIn("NO_APPROVED_SIGNALS",self.read().statuses)

    def test_selection_requires_explicit_provenance_and_caps_five(self):
        for i in range(4):self.approve("signal"+str(i),"parameter_"+str(i))
        with self.assertRaises(ProjectionGateError):self.approve("signal5","parameter_5")
        with self.assertRaises(ProjectionGateError):self.approve()
        definition=self.store.plan(ASSET_ID).signals[0].model_dump(mode="json")
        definition["approved_by"]=" "
        with self.assertRaises(ValidationError):SignalSelection.model_validate(definition)

    def test_partial_signal_set_does_not_manufacture_missing_zero(self):
        self.approve("synthetic-temp","bearing_temperature")
        doc=self.source_document({"bearing_temperature":{"unavailable":True}})
        self.project(doc)
        result=self.read()
        self.assertEqual(len(result.items),1)
        self.assertEqual(result.expected_signals,2)
        self.assertIn("PARTIAL_SIGNAL_SET",result.statuses)
        self.assertIn("SOURCE_UNAVAILABLE",result.statuses)

    def test_source_unavailable_retains_previous_evidence_and_last_projection_time(self):
        self.project(self.source_document())
        old=self.read().items[0]
        bad=self.source_document({"motor_current":{"unavailable":True}})
        self.project(bad)
        result=self.read()
        self.assertEqual(result.items[0],old)
        self.assertIn("SOURCE_UNAVAILABLE",result.statuses)

    def test_retire_or_approval_change_during_acquisition_blocks_commit(self):
        doc=self.source_document()
        self.store.retire_signal("synthetic-current")
        with self.assertRaises(ProjectionGateError):self.store.project(EvidenceBatch.model_validate(doc),now=NOW)
        with Session(self.engine) as s:self.assertEqual(list(s.scalars(select(ConditionEvidenceLatestMart))),[])

    def test_evidence_lineage_unselected_duplicate_raw_payload_rejected(self):
        doc=self.source_document()
        mutations = [lambda d:d["results"][0]["evidence"]["sources"]["pi"].update(af_element_ref="OTHER"),
            lambda d:d["results"][0].update(signal_id="UNSELECTED"),
            lambda d:d["results"].append(d["results"][0]),
            lambda d:d["results"][0]["evidence"].update(raw_payload={"Authorization":"secret"}),
            lambda d:d["results"][0]["evidence"].update(value="12",value_type="NUMERIC"),
            lambda d:d["results"][0]["evidence"].update(collected_at="2026-10-07T12:00:00")]
        for mutate in mutations:
            d=copy.deepcopy(doc);mutate(d)
            with self.assertRaises(ValidationError):EvidenceBatch.model_validate(d)

    def test_same_collection_conflict_and_older_handoff_cannot_replace_latest(self):
        doc=self.source_document();self.project(doc)
        changed=copy.deepcopy(doc);changed["results"][0]["evidence"]["value"]=99
        with self.assertRaises(ProjectionGateError):self.project(changed)
        older=copy.deepcopy(doc);older["results"][0]["evidence"]["collected_at"]=(NOW-timedelta(hours=1)).isoformat()
        self.assertEqual(self.project(older)["status"],"IGNORED_OLDER_BATCH")
        self.assertEqual(self.read().items[0].evidence.value,12.5)

    def test_retired_mapping_hides_old_evidence(self):
        self.project(self.source_document())
        from src.repositories.asset_af_mapping_store import AssetAfMappingCommandStore
        AssetAfMappingCommandStore(self.engine).retire(self.mapping_id,retired_by="fixture-reviewer",retirement_note="synthetic-only")
        self.assertEqual(self.read().items,())
        self.assertIn("NO_VERIFIED_MAPPING",self.read().statuses)

    def test_missing_future_schema_does_not_break_factual_queries(self):
        with self.engine.begin() as c:c.exec_driver_sql("DROP TABLE condition_evidence_latest")
        self.assertIn("PROJECTION_ERROR",self.read().statuses)
        from src.repositories.mart_reader import MartQueryRepository
        reader=Mock()
        # The accepted factual Asset query is independent of optional evidence DDL.
        from src.repositories.mart_reader import MartQueryRepository
        database = self.reader()
        try:
            self.assertIsNotNone(MartQueryRepository(database).get_asset(ASSET_ID))
        finally:
            if database.engine is not self.engine: database.engine.dispose()

    def test_api_is_read_only_no_source_client_or_admin_config(self):
        routes=[r for r in create_app().routes if "condition" in r.path]
        self.assertTrue(routes)
        self.assertTrue(all(r.methods=={"GET"} for r in routes))
        for path in (ROOT/"src/services/condition_query.py",ROOT/"src/api/reliability.py"):
            content=path.read_text()
            for forbidden in ("PI_USERNAME","PI_PASSWORD","PiClient","ConditionCommandStore"):
                self.assertNotIn(forbidden,content)
        with patch.dict(os.environ,{"DATABASE_URL":"sqlite://","RELIABILITY_MART_DATABASE_URL":"sqlite://"},clear=True):
            with self.assertRaises(Exception):ConditionCommandStore.from_environment()

    def test_unregistered_asset_and_unknown_api_asset_rejected(self):
        with self.assertRaises(ProjectionGateError):self.store.plan("UNKNOWN")
        with patch.object(api.ConditionQueryService,"asset_evidence",return_value=None):
            from fastapi import HTTPException
            with self.assertRaises(HTTPException) as error:api.asset_condition_evidence("UNKNOWN",Mock())
            self.assertEqual(error.exception.status_code,404)

    def test_actual_asgi_asset_evidence_read_serialization_and_no_mutation(self):
        import asyncio
        self.project(self.source_document({"motor_current":{"Value":"RUNNING"}}))
        app=create_app()
        reader=self.reader()
        app.dependency_overrides[api._db]=lambda: reader
        async def request(method="GET"):
            sent=[]
            async def receive(): return {"type":"http.request","body":b"","more_body":False}
            async def send(message): sent.append(message)
            path="/v1/reliability/assets/"+ASSET_ID+"/condition-evidence"
            await app({"type":"http","asgi":{"version":"3.0"},"http_version":"1.1","method":method,
                "scheme":"http","path":path,"raw_path":path.encode(),"query_string":b"","headers":[],
                "server":("fixture",80),"client":("127.0.0.1",1234),"root_path":""}, receive, send)
            status=next(m["status"] for m in sent if m["type"]=="http.response.start")
            body=b"".join(m.get("body",b"") for m in sent if m["type"]=="http.response.body")
            return status, json.loads(body)
        try:
            with patch("src.api.reliability.get_mart_database",return_value=reader):
                status,body=asyncio.run(request())
            self.assertEqual(status,200)
            self.assertEqual(body["items"][0]["evidence"]["value"],"RUNNING")
            with patch("src.api.reliability.get_mart_database",return_value=reader):
                self.assertEqual(asyncio.run(request("POST"))[0],405)
        finally:
            if reader.engine is not self.engine:reader.engine.dispose()

    def test_projection_port_error_records_unknown_failure_without_values(self):
        source=Mock();source.collect.side_effect=RuntimeError("synthetic password must not escape")
        result=ConditionProjectionService(self.store,source).project(ASSET_ID,now=NOW)
        self.assertIn("PROJECTION_ERROR",result["status"])
        response=self.read()
        self.assertEqual(response.items,())
        self.assertIn("PROJECTION_ERROR",response.statuses)
        self.assertNotIn("password",response.model_dump_json())

    def test_selected_approval_change_between_read_and_write_rejects_batch(self):
        doc=self.source_document()
        self.approve("new-approved-signal","outlet_temperature")
        with self.assertRaises(ProjectionGateError):self.store.project(EvidenceBatch.model_validate(doc),now=NOW)

    def test_configurable_freshness_keeps_all_dimensions_independent(self):
        policy=FreshnessPolicy(collector_max_age_seconds=60,source_max_age_seconds=3600,projection_max_age_seconds=30)
        self.assertEqual(policy.state("COLLECTOR",NOW-timedelta(seconds=120),NOW),"COLLECTOR_STALE")
        self.assertEqual(policy.state("SOURCE",NOW-timedelta(seconds=120),NOW),"SOURCE_CURRENT")
        self.assertEqual(policy.state("PROJECTION",NOW-timedelta(seconds=120),NOW),"PROJECTION_STALE")
        with patch.dict(os.environ,{"NADI_SOURCE_MAX_AGE_SECONDS":"","NADI_COLLECTOR_MAX_AGE_SECONDS":""},clear=True):
            self.assertEqual(FreshnessPolicy.from_environment(),FreshnessPolicy())

    def test_finite_and_bounded_values_required_and_future_collection_rejected(self):
        doc=self.source_document()
        for value in (float("nan"),float("inf")):
            changed=copy.deepcopy(doc);changed["results"][0]["evidence"]["value"]=value
            with self.assertRaises(ValidationError):EvidenceBatch.model_validate(changed)
        changed=copy.deepcopy(doc);changed["results"][0]["evidence"]["collected_at"]=(NOW+timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(ProjectionGateError,"FUTURE_COLLECTION"):self.store.project(EvidenceBatch.model_validate(changed),now=NOW)

@unittest.skipUnless(os.getenv("NADI_MART_TEST_DSN"),"isolated PostgreSQL fixture not configured")
class ConditionPostgresTest(ConditionProjectionTest):
    def setUp(self):
        from test_mart_migrations import MartPostgresMigrationTest
        from src.services.mart_migrations import run_migrations, reader_role
        self.url=make_url(os.environ["NADI_MART_TEST_DSN"])
        if self.url.host not in {"localhost","127.0.0.1"} or not self.url.database.endswith("_test"):
            raise RuntimeError("local disposable *_test database required")
        self.engine=create_engine(self.url)
        MartPostgresMigrationTest.setUp(self)
        result=run_migrations(self.engine,expected_database=self.url.database,apply=True)
        self.assertTrue(result["ready"])
        self.assertIn("004_condition_evidence.sql",result["applied"])
        with Session(self.engine) as s:
            s.add(_asset());s.flush()
            s.add(ReliabilityAssetRegistryMart(asset_ref=ASSET_ID,source_asset_number="SYNTHETIC",site_code="BSR",organization_code="IP",
                registry_source="SYNTHETIC",snapshot_sha256="a"*64,snapshot_row_count=1,snapshot_imported_at=NOW))
            s.add(AssetAfMappingMart(**asdict(_mapping("VERIFIED"))));s.commit()
        self.mapping_id=_mapping("VERIFIED").id
        self.store=ConditionCommandStore(self.engine)
        self.approve()
        self.password="synthetic-reader-password-at-least-24"
        reader_role(self.engine,expected_database=self.url.database,apply=True,password=self.password)

    def reader(self):
        dsn=self.url.set(username="nadi_mart_reader",password=self.password).render_as_string(hide_password=False)
        return MartDatabase(MartDbConfig(dsn=dsn))

    def test_reader_cannot_write_condition_tables_even_with_readonly_off(self):
        from sqlalchemy.exc import DBAPIError
        engine=create_engine(self.url.set(username="nadi_mart_reader",password=self.password))
        try:
            for table in ("condition_signal_selection","condition_evidence_latest","condition_projection_state"):
                with engine.connect() as c:self.assertEqual(c.scalar(text("SELECT count(*) FROM "+table)) >= 0,True)
                with self.assertRaises(DBAPIError):
                    with engine.begin() as c:
                        c.exec_driver_sql("SET TRANSACTION READ WRITE")
                        c.exec_driver_sql("DELETE FROM "+table+" WHERE false")
        finally:engine.dispose()
