"""Restored evidence must fail closed: SQLite plus opt-in disposable PostgreSQL."""
import copy
import json
import os
from pathlib import Path
import unittest
from datetime import timedelta, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.condition_evidence import FreshnessPolicy, EvidenceBatch
from src.repositories.condition_models import ConditionEvidenceLatestMart, ConditionProjectionStateMart, ConditionSignalSelectionMart
from src.services.condition_query import ConditionQueryService
from src.services.phase1_readiness import phase1_readiness
from src.domain.phase1_readiness import GateId
import test_condition_evidence as fixture
import test_integration_status as integration_fixture

class Phase1ReadIntegrityTest(unittest.TestCase):
    setUp = fixture.ConditionProjectionTest.setUp
    tearDown = fixture.ConditionProjectionTest.tearDown
    approve = fixture.ConditionProjectionTest.approve
    reader = fixture.ConditionProjectionTest.reader
    source_document = fixture.ConditionProjectionTest.source_document
    project = fixture.ConditionProjectionTest.project
    service = integration_fixture.IntegrationStatusTest.service

    def read(self):
        return ConditionQueryService(self.reader(), policy=FreshnessPolicy(collector_max_age_seconds=60,
            source_max_age_seconds=60, projection_max_age_seconds=60), clock=lambda:fixture.NOW).asset_evidence(fixture.ASSET_ID)

    def gate(self, status):
        return next(g for g in phase1_readiness(status).gates if g.gate == GateId.CONDITION_PROJECTION)

    def test_missing_projection_state_cannot_report_complete_pilot(self):
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            s.delete(s.get(ConditionProjectionStateMart, fixture.ASSET_ID))
        status = self.service().status()
        self.assertTrue(status.condition_schema_ready)
        self.assertNotEqual(self.gate(status).verdict, 'PASS')
        row = self.read()
        self.assertEqual(len(row.items), 1, 'retain original evidence while disclosing missing state')
        self.assertEqual(row.items[0].freshness.projection, 'PROJECTION_UNKNOWN')
        self.assertIn('PROJECTION_ERROR', row.statuses)

    def test_projection_state_for_another_mapping_cannot_attest_current_evidence(self):
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            row=s.get(ConditionProjectionStateMart, fixture.ASSET_ID)
            row.state={**row.state, 'mapping_id':'SYNTHETIC-OTHER-MAPPING'}
        self.assertNotEqual(self.gate(self.service().status()).verdict, 'PASS')
        self.assertEqual(self.read().items[0].freshness.projection, 'PROJECTION_UNKNOWN')

    def test_evidence_json_signal_id_must_match_its_storage_row(self):
        self.approve('synthetic-temp','bearing_temperature')
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            current=s.get(ConditionEvidenceLatestMart,'synthetic-current')
            other=s.get(ConditionEvidenceLatestMart,'synthetic-temp')
            current.evidence=copy.deepcopy(other.evidence)
        result=self.read()
        self.assertEqual(result.items, ())
        self.assertIn('PROJECTION_ERROR', result.statuses)

    def test_selection_json_signal_id_must_match_its_storage_row(self):
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            row=s.get(ConditionSignalSelectionMart,'synthetic-current')
            row.definition={**row.definition, 'signal_id':'SYNTHETIC-OTHER-SIGNAL'}
        result=self.read()
        self.assertEqual(result.items, ())
        self.assertIn('PROJECTION_ERROR', result.statuses)

    def test_unknown_projection_dimensions_explain_unset_policy(self):
        self.project(self.source_document())
        status=self.service(policy=False).status()
        component=next(c for c in status.components if c.component=='PI_CONDITION_PROJECTION')
        self.assertEqual(component.state,'UNKNOWN')
        self.assertIn('UNKNOWN_FRESHNESS_POLICY',component.degraded_reasons)

    def test_configured_missing_collection_timestamp_explains_unknown(self):
        service=self.service()
        service.observations.maximo.return_value=service.observations.maximo.return_value.model_copy(update={'last_successful_activity':None})
        component=next(c for c in service.status().components if c.component=='MAXIMO')
        self.assertEqual(component.collection_freshness.state,'UNKNOWN')
        self.assertIn('UNKNOWN_TIMESTAMP',component.degraded_reasons)

    def test_collected_timestamp_column_must_match_original_document(self):
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            row=s.get(ConditionEvidenceLatestMart,'synthetic-current')
            row.collected_at=fixture.NOW+timedelta(seconds=1)
        self.assertEqual(self.read().items, ())
        status=self.service().status()
        self.assertIsNone(status.coverage.projected_signals)
        self.assertNotEqual(self.gate(status).verdict,'PASS')

    def test_malformed_projection_statuses_cannot_attest_current_evidence(self):
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            row=s.get(ConditionProjectionStateMart,fixture.ASSET_ID)
            row.state={**row.state,'statuses':'PROJECTED'}
        self.assertNotEqual(self.gate(self.service().status()).verdict,'PASS')
        self.assertIn('PROJECTION_ERROR',self.read().statuses)

    def _duplicate_selection(self, field):
        self.approve('synthetic-temp', 'bearing_temperature')
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            first=s.get(ConditionSignalSelectionMart, 'synthetic-current')
            other=s.get(ConditionSignalSelectionMart, 'synthetic-temp')
            evidence=s.get(ConditionEvidenceLatestMart, 'synthetic-temp')
            definition=copy.deepcopy(other.definition)
            document=copy.deepcopy(evidence.evidence)
            if field == 'attribute_ref':
                value=first.definition['sources']['pi']['attribute_ref']
                definition['sources']['pi']['attribute_ref']=value
                document['sources']['pi']['attribute_ref']=value
            else:
                definition['semantic_name']=first.definition['semantic_name']
                document['semantic_name']=first.definition['semantic_name']
            other.definition=definition
            evidence.evidence=document
        status=self.service().status()
        self.assertFalse(status.condition_schema_ready)
        self.assertNotEqual(self.gate(status).verdict, 'PASS')
        self.assertEqual(self.read().items, ())
        self.assertIn('PROJECTION_ERROR', self.read().statuses)

    def test_duplicate_attribute_set_rejected_by_detail_and_aggregate(self):
        self._duplicate_selection('attribute_ref')

    def test_duplicate_semantic_set_rejected_by_detail_and_aggregate(self):
        self._duplicate_selection('semantic_name')

    def test_same_mapping_older_attempt_cannot_attest_newer_evidence(self):
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            row=s.get(ConditionProjectionStateMart, fixture.ASSET_ID)
            row.attempted_at=fixture.NOW-timedelta(seconds=1)
        self.assertNotEqual(self.gate(self.service().status()).verdict, 'PASS')
        result=self.read()
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].freshness.projection, 'PROJECTION_UNKNOWN')
        self.assertIn('PROJECTION_ERROR', result.statuses)
        self.assertIsNone(result.latest_attempt_at)

    def test_valid_original_evidence_and_attempt_are_not_mutated_by_reads(self):
        self.project(self.source_document())
        def snapshot():
            with Session(self.engine) as s:
                evidence=s.get(ConditionEvidenceLatestMart,'synthetic-current')
                state=s.get(ConditionProjectionStateMart,fixture.ASSET_ID)
                return copy.deepcopy((evidence.evidence,evidence.collected_at,evidence.projected_at,state.state,state.attempted_at))
        before=snapshot()
        self.assertEqual(self.gate(self.service().status()).verdict,'PASS')
        row=self.read()
        self.assertEqual(row.items[0].evidence.value,12.5)
        self.assertEqual(row.items[0].freshness.projection,'PROJECTION_CURRENT')
        self.assertEqual(snapshot(),before)

    def test_failed_factual_projection_cannot_pass_on_recent_last_success(self):
        service=self.service()
        with self.engine.begin() as c:
            c.execute(text("UPDATE mart_projection_state SET last_status='FAILED' WHERE projection_key='maintenance_event'"))
        status=service.status()
        gate=next(g for g in phase1_readiness(status).gates if g.gate==GateId.MART)
        self.assertEqual((gate.verdict,gate.reason),('PARTIAL','LOCAL_EVIDENCE_DEGRADED'))

    def test_non_utc_collection_preserves_original_time_and_same_storage_instant(self):
        document=self.source_document()
        original=fixture.NOW.astimezone(timezone(timedelta(hours=7))).isoformat()
        document['results'][0]['evidence']['collected_at']=original
        self.project(document)
        result=self.read()
        self.assertEqual(len(result.items),1)
        self.assertEqual(result.items[0].evidence.collected_at.isoformat(),original)
        self.assertEqual(self.gate(self.service().status()).verdict,'PASS')
        before=result.model_dump(mode='json')
        self.assertEqual(self.store.project(EvidenceBatch.model_validate(document),now=fixture.NOW+timedelta(minutes=5))['written'],0)
        self.assertEqual(self.read().model_dump(mode='json'),before)

    def test_unknown_and_missing_attestation_statuses_validate_public_contract(self):
        from jsonschema import Draft202012Validator, FormatChecker
        schema=json.loads((Path(__file__).parents[2]/'reliability-data-contracts/schemas/integration-status.schema.json').read_text())
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            s.delete(s.get(ConditionProjectionStateMart,fixture.ASSET_ID))
        for service in (self.service(),self.service(policy=False)):
            document=service.status().model_dump(mode='json')
            Draft202012Validator(schema,format_checker=FormatChecker()).validate(document)
            self.assertNotEqual(self.gate(service.status()).verdict,'PASS')

@unittest.skipUnless(os.getenv('NADI_MART_TEST_DSN'), 'isolated PostgreSQL fixture not configured')
class Phase1PostgresReadIntegrityTest(Phase1ReadIntegrityTest):
    reader = fixture.ConditionPostgresTest.reader

    def setUp(self):
        fixture.ConditionPostgresTest.setUp(self)
        with self.engine.begin() as c:
            c.exec_driver_sql('ALTER TABLE mart_projection_state ADD COLUMN last_status text')
            c.exec_driver_sql('ALTER TABLE mart_projection_state ADD COLUMN last_success_at timestamptz')
