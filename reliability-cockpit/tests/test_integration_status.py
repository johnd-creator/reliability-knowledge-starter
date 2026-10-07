"""Local-evidence trust regression; all identities/source replies are synthetic."""
import json
import unittest
from datetime import timedelta
from unittest.mock import Mock, patch
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.api.app import create_app
from src.api import reliability as api
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.integration_status import CollectorObservation, Component, TrustState, DegradedReason, Availability
from src.services.integration_status import IntegrationStatusService
from src.repositories.mart_models import AssetAfMappingMart
import test_condition_evidence as fixture
from test_condition_evidence import NOW, ASSET_ID
from test_asset_af_mapping_admin import _mapping
from dataclasses import asdict

class IntegrationStatusTest(unittest.TestCase):
    setUp=fixture.ConditionProjectionTest.setUp
    tearDown=fixture.ConditionProjectionTest.tearDown
    approve=fixture.ConditionProjectionTest.approve
    reader=fixture.ConditionProjectionTest.reader
    source_document=fixture.ConditionProjectionTest.source_document
    project=fixture.ConditionProjectionTest.project

    def service(self,policy=True,now=NOW):
        observations=Mock()
        observations.maximo.return_value=CollectorObservation(availability="AVAILABLE",last_successful_activity=NOW,errors=0,cursor_present=True)
        observations.pi.return_value=CollectorObservation(availability="AVAILABLE",last_successful_activity=NOW,errors=0,
            registry_total=490,registry_active=433,snapshots=433,oldest_source_timestamp=NOW,unknown_source_timestamps=0,bad_quality_signals=0,unknown_quality_signals=0)
        with self.engine.begin() as c:
            c.exec_driver_sql("CREATE TABLE IF NOT EXISTS mart_projection_state (projection_key text PRIMARY KEY,last_status text,last_success_at text)")
            c.exec_driver_sql("DELETE FROM mart_projection_state")
            for key in ("asset_master","maintenance_event"):
                c.execute(text("INSERT INTO mart_projection_state (projection_key,last_status,last_success_at) VALUES (:key,'SUCCEEDED',:time)"),{"key":key,"time":NOW.isoformat()})
        return IntegrationStatusService(self.reader(),observations=observations,
            policy=FreshnessPolicy(collector_max_age_seconds=60,source_max_age_seconds=60,projection_max_age_seconds=60) if policy else FreshnessPolicy(),clock=lambda:now)

    def component(self,result,name):return next(c for c in result.components if c.component==name)

    def test_verified_approved_projected_coverage_and_api_serialization(self):
        self.project(self.source_document());result=self.service().status()
        self.assertTrue(result.governance_schema_ready);self.assertTrue(result.condition_schema_ready)
        self.assertEqual(result.coverage.verified_mapping_assets,1)
        self.assertEqual(result.coverage.approved_signal_assets,1);self.assertEqual(result.coverage.projected_assets,1)
        self.assertTrue(all(c.state==TrustState.CURRENT for c in result.components))
        with patch.object(api,"_integration_service",return_value=self.service()):
            encoded=api.integration_status().model_dump(mode="json")
            self.assertEqual(encoded["coverage"]["projected_assets"],1)
        self.assertFalse(any(x in json.dumps(encoded).lower() for x in ("password","token","authorization","12.5")))
        routes=[r for r in create_app().routes if r.path.endswith("integration-status")]
        self.assertEqual(len(routes),2);self.assertTrue(all(r.methods=={"GET"} for r in routes))

    def test_proposed_and_retired_show_no_usable_mapping(self):
        for status in ("PROPOSED","RETIRED"):
            with Session(self.engine) as s,s.begin():
                row=s.get(AssetAfMappingMart,self.mapping_id)
                for key,value in asdict(_mapping(status)).items():
                    if key!="id":setattr(row,key,value)
            result=self.service().status();mapping=self.component(result,Component.ASSET_AF_MAPPING)
            self.assertEqual(mapping.state,TrustState.BLOCKED)
            self.assertIn(DegradedReason.HUMAN_CROSSWALK_REQUIRED,mapping.degraded_reasons)
            self.assertEqual(result.coverage.verified_mapping_assets,0);self.assertEqual(result.coverage.projected_assets,0)

    def test_ambiguous_has_no_winner(self):
        with Session(self.engine) as s,s.begin():s.add(AssetAfMappingMart(**asdict(_mapping("VERIFIED","OTHER_ELEMENT"))))
        result=self.service().status();self.assertEqual(result.coverage.verified_mapping_assets,0)
        self.assertEqual(result.coverage.ambiguous_mapping_assets,1)
        self.assertEqual(self.component(result,Component.ASSET_AF_MAPPING).mapping_readiness,"AMBIGUOUS")

    def test_collector_current_source_stale_and_projection_current_coexist(self):
        self.project(self.source_document({"motor_current":{"Timestamp":"1970-01-01T00:00:00Z"}}))
        service=self.service();service.observations.pi.return_value=service.observations.pi.return_value.model_copy(update={"oldest_source_timestamp":NOW-timedelta(days=1)})
        result=service.status();pi=self.component(result,Component.PI_COLLECTOR);projection=self.component(result,Component.PI_CONDITION_PROJECTION)
        self.assertEqual(pi.collection_freshness.state,"CURRENT");self.assertEqual(pi.source_freshness.state,"STALE")
        self.assertEqual(projection.source_freshness.state,"STALE");self.assertEqual(projection.projection_freshness.state,"CURRENT")
        self.assertEqual(projection.mapping_readiness,"VERIFIED")

    def test_projection_stale_is_not_refreshed_by_query(self):
        self.project(self.source_document());result=self.service(now=NOW+timedelta(seconds=61)).status()
        self.assertEqual(self.component(result,Component.PI_CONDITION_PROJECTION).projection_freshness.state,"STALE")

    def test_missing_condition_schema_is_unknown_count_not_zero(self):
        with self.engine.begin() as c:c.exec_driver_sql("DROP TABLE condition_evidence_latest")
        result=self.service().status();self.assertFalse(result.condition_schema_ready)
        self.assertIsNone(result.coverage.projected_assets)
        self.assertIn(DegradedReason.CONDITION_SCHEMA_NOT_READY,self.component(result,Component.PI_CONDITION_PROJECTION).degraded_reasons)

    def test_mart_unavailable_and_not_configured(self):
        service=self.service();service.database=Mock()
        service.database.read_session.side_effect=__import__("sqlalchemy").exc.OperationalError("synthetic",{},Exception())
        result=service.status();self.assertEqual(self.component(result,Component.RELIABILITY_MART).availability,"UNAVAILABLE")
        service.database=None;self.assertEqual(self.component(service.status(),Component.RELIABILITY_MART).state,"NOT_CONFIGURED")

    def test_neutral_policy_remains_unknown(self):
        self.project(self.source_document());result=self.service(policy=False).status()
        pi=self.component(result,Component.PI_COLLECTOR)
        self.assertEqual(pi.collection_freshness.state,"UNKNOWN");self.assertEqual(pi.source_freshness.state,"UNKNOWN")
        self.assertNotEqual(self.component(result,Component.PI_CONDITION_PROJECTION).state,"CURRENT")

    def test_partial_signal_set_and_bad_quality(self):
        self.approve("synthetic-temp","bearing_temperature")
        self.project(self.source_document({"motor_current":{"Good":False},"bearing_temperature":{"unavailable":True}}))
        result=self.service().status();projection=self.component(result,Component.PI_CONDITION_PROJECTION)
        self.assertEqual(result.coverage.approved_signals,2);self.assertEqual(result.coverage.projected_signals,1)
        self.assertEqual(projection.quality,"BAD");self.assertEqual(projection.state,"DEGRADED")
        self.assertIn(DegradedReason.PARTIAL_SIGNAL_SET,projection.degraded_reasons)

    def test_retired_signal_or_mapping_does_not_inflate_coverage(self):
        self.project(self.source_document());self.store.retire_signal("synthetic-current")
        result=self.service().status();self.assertEqual(result.coverage.projected_assets,0);self.assertEqual(result.coverage.approved_signals,0)

    def test_asset_scoped_status_does_not_count_other_assets(self):
        self.project(self.source_document());service=self.service()
        self.assertEqual(service.status(ASSET_ID).coverage.registered_assets,1)
        self.assertEqual(service.status("UNKNOWN").coverage.registered_assets,0)
