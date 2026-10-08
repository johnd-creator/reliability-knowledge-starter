"""Independent policies; every example threshold is synthetic, never activated."""
import os
import unittest
from datetime import timedelta
from unittest.mock import patch
from pydantic import ValidationError
from src.domain.condition_evidence import FreshnessPolicy
from src.services.phase1_readiness import phase1_readiness
from src.domain.phase1_readiness import GateId
import test_integration_status as fixture
from test_condition_evidence import NOW

COMPONENTS = [('MAXIMO','COLLECTOR','maximo_wo'),('RELIABILITY_MART','PROJECTION','mart_factual_projection'),
              ('PI_COLLECTOR','COLLECTOR','pi_collector'),('PI_CONDITION_PROJECTION','SOURCE','condition_source'),
              ('PI_CONDITION_PROJECTION','PROJECTION','condition_projection')]

class ComponentPolicyTest(unittest.TestCase):
    def test_each_threshold_affects_only_its_component(self):
        for component,dimension,field in COMPONENTS:
            policy=FreshnessPolicy(**{field+'_max_age_seconds':60})
            for other,dim,key in COMPONENTS:
                self.assertEqual(policy.state(dim,NOW,NOW,component=other),dim+('_CURRENT' if field==key else '_UNKNOWN'))
            self.assertEqual(policy.state('SOURCE',NOW,NOW,component='PI_COLLECTOR'),'SOURCE_UNKNOWN')

    def test_future_times_never_make_any_component_current(self):
        for component, dimension, field in COMPONENTS:
            policy = FreshnessPolicy(**{field+'_max_age_seconds': 60})
            self.assertEqual(policy.state(dimension, NOW+timedelta(seconds=1), NOW, component=component), dimension+'_UNKNOWN')
            self.assertEqual(policy.state(dimension, None, NOW, component=component), dimension+'_UNKNOWN')

    def test_explicit_legacy_compatibility(self):
        policy=FreshnessPolicy(collector_max_age_seconds=60,source_max_age_seconds=70,projection_max_age_seconds=80)
        for component,dimension,field in COMPONENTS:
            self.assertEqual(policy.state(dimension,NOW,NOW,component=component),dimension+'_CURRENT')
        self.assertEqual(policy.threshold('SOURCE','PI_COLLECTOR'),70)

    def test_mixing_even_equal_legacy_and_component_values_is_rejected(self):
        with self.assertRaises(ValidationError):FreshnessPolicy(collector_max_age_seconds=60,pi_collector_max_age_seconds=60)
        with patch.dict(os.environ,{'NADI_COLLECTOR_MAX_AGE_SECONDS':'60','NADI_PI_COLLECTOR_MAX_AGE_SECONDS':'1800'},clear=True):
            with self.assertRaises(ValidationError):FreshnessPolicy.from_environment()

    def test_blank_and_invalid_environment(self):
        env={'NADI_'+key.upper()+'_MAX_AGE_SECONDS':'' for _,_,key in COMPONENTS}
        with patch.dict(os.environ,env,clear=True):self.assertEqual(FreshnessPolicy.from_environment(),FreshnessPolicy())
        for value in (' ', 'nan','inf','0','-1','garbage'):
            with patch.dict(os.environ,{'NADI_MAXIMO_WO_MAX_AGE_SECONDS':value},clear=True):
                with self.assertRaises(ValidationError):FreshnessPolicy.from_environment()
        with self.assertRaises(ValidationError):FreshnessPolicy(maximo_wo_max_age_seconds=True)

class ComponentRuntimeTest(unittest.TestCase):
    setUp=fixture.IntegrationStatusTest.setUp
    tearDown=fixture.IntegrationStatusTest.tearDown
    approve=fixture.IntegrationStatusTest.approve
    reader=fixture.IntegrationStatusTest.reader
    source_document=fixture.IntegrationStatusTest.source_document
    project=fixture.IntegrationStatusTest.project
    service=fixture.IntegrationStatusTest.service

    def test_proposed_monitoring_values_never_enable_condition_freshness(self):
        self.project(self.source_document());service=self.service()
        service.policy=FreshnessPolicy(maximo_wo_max_age_seconds=660,mart_factual_projection_max_age_seconds=660,pi_collector_max_age_seconds=1800)
        status=service.status();components={c.component:c for c in status.components}
        self.assertEqual(components['MAXIMO'].collection_freshness.max_age_seconds,660)
        self.assertEqual(components['PI_COLLECTOR'].collection_freshness.max_age_seconds,1800)
        self.assertEqual(components['RELIABILITY_MART'].projection_freshness.max_age_seconds,660)
        projection=components['PI_CONDITION_PROJECTION']
        self.assertEqual(projection.source_freshness.state,'UNKNOWN')
        self.assertEqual(projection.projection_freshness.state,'UNKNOWN')
        gate=next(g for g in phase1_readiness(status).gates if g.gate==GateId.CONDITION_PROJECTION)
        self.assertEqual(gate.verdict,'UNKNOWN')

    def test_source_current_quality_bad_still_cannot_pass(self):
        self.project(self.source_document({'motor_current':{'Good':False}}));service=self.service()
        service.policy=FreshnessPolicy(condition_source_max_age_seconds=60,condition_projection_max_age_seconds=60)
        gate=next(g for g in phase1_readiness(service.status()).gates if g.gate==GateId.CONDITION_PROJECTION)
        self.assertEqual((gate.verdict,gate.reason),('PARTIAL','QUALITY_NOT_ACCEPTED'))
