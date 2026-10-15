"""Product fixtures validate against existing DTOs. No databases, HTTP or source clients."""
import json
import unittest
from pathlib import Path
from src.api.reliability import DataTrustView
from src.domain.integration_status import IntegrationStatus

class IntegrationUiContractTest(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((Path(__file__).parents[1] / 'web/fixtures/integration-ui.json').read_text())

    def test_existing_integration_dto_and_independent_clocks(self):
        result = IntegrationStatus.model_validate(self.fixture['integration'])
        components = {c.component: c for c in result.components}
        self.assertEqual(len(components), 5)
        self.assertEqual(components['MAXIMO'].collection_freshness.state, 'CURRENT')
        self.assertEqual(components['MAXIMO'].source_freshness.state, 'UNKNOWN')
        self.assertEqual(components['PI_COLLECTOR'].source_freshness.state, 'STALE')
        self.assertEqual(components['RELIABILITY_MART'].projection_freshness.state, 'CURRENT')
        self.assertIsNone(result.coverage.projected_assets)
        self.assertEqual(result.coverage.approved_signal_assets, 0)

    def test_existing_data_trust_dto_preserves_population_and_unknowns(self):
        result = DataTrustView.model_validate(self.fixture['trust'])
        self.assertEqual(result.population.registered_reliability_assets, 12)
        self.assertEqual(result.population.technical_asset_context, 120)
        self.assertEqual(result.scope.sync_freshness, 'NOT_AVAILABLE')
        self.assertIsNone(result.domains[0].scoped_record_count)
        self.assertEqual(result.relationships[0].evidence, 'UNRESOLVED')

    def test_missing_integration_dimensions_use_existing_unknown_defaults(self):
        result = IntegrationStatus.model_validate({'observed_at':'2026-10-15T00:00:00Z', 'components':[{'component':'MAXIMO', 'state':'UNKNOWN', 'availability':'UNKNOWN'}]})
        self.assertIsNone(result.coverage.registered_assets)
        self.assertEqual(result.components[0].collection_freshness.state, 'UNKNOWN')
        self.assertIsNone(result.components[0].collection_freshness.max_age_seconds)
