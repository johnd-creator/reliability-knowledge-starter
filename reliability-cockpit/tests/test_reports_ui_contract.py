"""Reports fixtures use existing factual DTOs. No database or network access."""
import json
import unittest
from pathlib import Path
from pydantic import ValidationError
from src.api.reliability import DataTrustView, DecisionOverviewView

class ReportsUiContractTest(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((Path(__file__).parents[1] / 'web/fixtures/reports-ui.json').read_text())

    def test_coverage_reuses_data_trust_population_boundaries(self):
        data = DataTrustView.model_validate(self.fixture['coverage'])
        self.assertEqual(data.population.registered_reliability_assets, 12)
        self.assertEqual(data.population.technical_asset_context, 120)
        self.assertEqual(data.scope.sync_freshness, 'NOT_AVAILABLE')
        self.assertNotIn('as_of', data.model_fields)
        self.assertIsNone(data.domains[0].scoped_record_count)

    def test_all_supported_overview_windows_use_existing_dto(self):
        for days in (7, 30, 90):
            data = DecisionOverviewView.model_validate(self.fixture['maintenance'][str(days)])
            self.assertEqual(data.window_days, days)
            self.assertEqual((data.as_of - data.window_start).days, days)
            self.assertEqual(data.summary.registered_assets.evidence_class, 'DERIVED_SAFE')
            self.assertEqual(len(data.maintenance_activity), 12)
            self.assertEqual(data.maintenance_activity[0].event_count.value, 0)

    def test_bucket_scope_is_not_the_selected_report_window(self):
        short = DecisionOverviewView.model_validate(self.fixture['maintenance']['7'])
        long = DecisionOverviewView.model_validate(self.fixture['maintenance']['90'])
        self.assertEqual(short.maintenance_activity, long.maintenance_activity)
        self.assertLess(short.maintenance_activity[0].period_start, short.window_start)
        self.assertGreater(short.maintenance_activity[-1].period_end, short.as_of)
        self.assertEqual(short.summary.maintenance_activity_7d.value, 0)
        self.assertEqual(short.activity_concentration, [])

    def test_backend_still_rejects_unapproved_period(self):
        row = dict(self.fixture['maintenance']['30'], window_days=14)
        with self.assertRaises(ValidationError):
            DecisionOverviewView.model_validate(row)
