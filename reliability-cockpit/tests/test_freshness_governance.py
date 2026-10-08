"""Synthetic policy regression; fixture numbers are never production SLAs."""
import copy
import os
import unittest
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session
from pydantic import ValidationError
from src.domain.condition_evidence import EvidenceBatch, FreshnessPolicy
from src.domain.phase1_readiness import GateId
from src.repositories.condition_models import ConditionEvidenceLatestMart, ConditionProjectionStateMart
from src.services.condition_query import ConditionQueryService
from src.services.phase1_readiness import phase1_readiness
import test_condition_evidence as fixture
import test_integration_status as integration_fixture

NOW = fixture.NOW
POLICY = FreshnessPolicy(collector_max_age_seconds=60, source_max_age_seconds=60,
                         projection_max_age_seconds=60)

class FreshnessTimestampTest(unittest.TestCase):
    def test_current_boundary_and_stale(self):
        for age, expected in ((0, 'CURRENT'), (60, 'CURRENT'), (61, 'STALE')):
            self.assertEqual(POLICY.state('SOURCE', NOW-timedelta(seconds=age), NOW), 'SOURCE_'+expected)

    def test_blank_policy_and_missing_timestamp_remain_unknown(self):
        self.assertEqual(FreshnessPolicy().state('SOURCE', NOW, NOW), 'SOURCE_UNKNOWN')
        self.assertEqual(POLICY.state('COLLECTOR', None, NOW), 'COLLECTOR_UNKNOWN')

    def test_epoch_is_stale_with_policy_unknown_without_policy(self):
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(POLICY.state('SOURCE', epoch, NOW), 'SOURCE_STALE')
        self.assertEqual(FreshnessPolicy().state('SOURCE', epoch, NOW), 'SOURCE_UNKNOWN')

    def test_future_is_unknown_even_with_threshold(self):
        self.assertEqual(POLICY.state('SOURCE', NOW+timedelta(seconds=1), NOW), 'SOURCE_UNKNOWN')

    def test_equivalent_offset_is_same_instant(self):
        self.assertEqual(POLICY.state('SOURCE', NOW.astimezone(timezone(timedelta(hours=7))), NOW), 'SOURCE_CURRENT')

class FreshnessGovernanceTest(unittest.TestCase):
    setUp = fixture.ConditionProjectionTest.setUp
    tearDown = fixture.ConditionProjectionTest.tearDown
    approve = fixture.ConditionProjectionTest.approve
    reader = fixture.ConditionProjectionTest.reader
    source_document = fixture.ConditionProjectionTest.source_document
    project = fixture.ConditionProjectionTest.project
    service = integration_fixture.IntegrationStatusTest.service

    def read(self):
        return ConditionQueryService(self.reader(), policy=POLICY, clock=lambda: NOW).asset_evidence(fixture.ASSET_ID)

    def gate(self, status):
        return next(g for g in phase1_readiness(status).gates if g.gate == GateId.CONDITION_PROJECTION)

    def test_missing_collector_success_never_falls_back_to_recent_collection(self):
        doc = self.source_document(); doc['collector_last_success_at'] = None
        self.project(doc); result = self.read()
        self.assertIsNone(result.collector_last_success_at)
        self.assertEqual(result.items[0].freshness.collector, 'COLLECTOR_UNKNOWN')
        self.assertEqual(result.items[0].freshness.source, 'SOURCE_CURRENT')
        self.assertEqual(result.items[0].freshness.projection, 'PROJECTION_CURRENT')
        status = self.service().status()
        pi = next(c for c in status.components if c.component == 'PI_COLLECTOR')
        self.assertEqual(pi.collection_freshness.state, 'CURRENT')
        self.assertIsNone(self.read().collector_last_success_at)

    def test_invalid_and_unzoned_timestamps_rejected_before_projection(self):
        doc = self.source_document()
        for value in ('not-a-time', '2026-10-07T12:00:00', 0):
            bad = copy.deepcopy(doc); bad['results'][0]['evidence']['source_timestamp'] = value
            with self.assertRaises(ValidationError): EvidenceBatch.model_validate(bad)
        self.assertEqual(self.read().items, ())

    def test_good_but_stale_cannot_pass(self):
        self.project(self.source_document({'motor_current': {'Timestamp': '1970-01-01T00:00:00Z'}}))
        item = self.read().items[0]
        self.assertTrue(item.evidence.quality_good)
        self.assertEqual(item.freshness.source, 'SOURCE_STALE')
        gate = self.gate(self.service().status())
        self.assertEqual((gate.verdict, gate.reason), ('PARTIAL', 'SOURCE_STALE'))

    def test_bad_quality_but_fresh_cannot_pass(self):
        self.project(self.source_document({'motor_current': {'Good': False}}))
        item = self.read().items[0]
        self.assertEqual(item.freshness.source, 'SOURCE_CURRENT')
        self.assertEqual(item.evidence.evidence_status, 'BAD_QUALITY')
        self.assertEqual(self.gate(self.service().status()).reason, 'QUALITY_NOT_ACCEPTED')

    def test_future_source_cannot_pass(self):
        self.project(self.source_document({'motor_current': {'Timestamp': (NOW+timedelta(seconds=1)).isoformat()}}))
        self.assertEqual(self.read().items[0].freshness.source, 'SOURCE_UNKNOWN')
        self.assertEqual(self.gate(self.service().status()).verdict, 'UNKNOWN')

    def test_older_projection_not_freshened_by_newer_source_or_collector(self):
        self.project(self.source_document())
        with Session(self.engine) as s, s.begin():
            s.get(ConditionEvidenceLatestMart, 'synthetic-current').projected_at = NOW-timedelta(seconds=61)
        item = self.read().items[0]
        self.assertLess(item.projected_at, item.evidence.source_timestamp)
        self.assertEqual(item.freshness.source, 'SOURCE_CURRENT')
        self.assertEqual(item.freshness.projection, 'PROJECTION_STALE')
        self.assertEqual(self.gate(self.service().status()).reason, 'PROJECTION_STALE')

    def test_identical_replay_preserves_payload_projection_and_attempt_times(self):
        doc = self.source_document(); self.project(doc)
        def snapshot():
            with Session(self.engine) as s:
                return (s.get(ConditionEvidenceLatestMart, 'synthetic-current').projected_at,
                        s.get(ConditionProjectionStateMart, fixture.ASSET_ID).attempted_at,
                        copy.deepcopy(s.get(ConditionProjectionStateMart, fixture.ASSET_ID).state))
        before = snapshot(); evidence = self.read().items[0]
        self.assertEqual(self.store.project(EvidenceBatch.model_validate(doc), now=NOW+timedelta(minutes=5))['written'], 0)
        self.assertEqual(before, snapshot()); self.assertEqual(evidence, self.read().items[0])

    def test_failed_refresh_preserves_evidence_but_degrades_readiness(self):
        self.project(self.source_document()); accepted = self.read().items[0]
        doc = self.source_document({'motor_current': {'unavailable': True}})
        result = self.store.project(EvidenceBatch.model_validate(doc), now=NOW+timedelta(seconds=10))
        self.assertEqual(result['written'], 0)
        self.assertEqual(self.read().items[0], accepted)
        self.assertIn('SOURCE_UNAVAILABLE', self.read().statuses)
        gate = self.gate(self.service().status())
        self.assertEqual((gate.verdict, gate.reason), ('PARTIAL', 'PROJECTION_DEGRADED'))
        with Session(self.engine) as s:
            attempted = s.get(ConditionProjectionStateMart, fixture.ASSET_ID).attempted_at
            if attempted.tzinfo is None:
                attempted = attempted.replace(tzinfo=timezone.utc)
            self.assertEqual(attempted, NOW+timedelta(seconds=10))

    def test_configured_thresholds_do_not_override_missing_times(self):
        self.project(self.source_document()); service = self.service()
        for name in ('maximo', 'pi'):
            observation = getattr(service.observations, name)
            observation.return_value = observation.return_value.model_copy(update={'last_successful_activity': None})
        gates = {g.gate: g for g in phase1_readiness(service.status()).gates}
        self.assertNotEqual(gates[GateId.MAXIMO].verdict, 'PASS')
        self.assertNotEqual(gates[GateId.PI_COLLECTOR].verdict, 'PASS')


@unittest.skipUnless(os.getenv("NADI_MART_TEST_DSN"), "isolated PostgreSQL fixture not configured")
class FreshnessGovernancePostgresTest(FreshnessGovernanceTest):
    """Same contracts against canonical migrations and SELECT-only query role."""
    reader = fixture.ConditionPostgresTest.reader

    def setUp(self):
        fixture.ConditionPostgresTest.setUp(self)
        # Migration tests use minimal owner anchors. Integration status also
        # consumes these projector-owned columns in the real runtime schema.
        # Extend only this disposable fixture, never the operational Mart.
        with self.engine.begin() as connection:
            connection.exec_driver_sql("ALTER TABLE mart_projection_state ADD COLUMN last_status text")
            connection.exec_driver_sql("ALTER TABLE mart_projection_state ADD COLUMN last_success_at timestamptz")
