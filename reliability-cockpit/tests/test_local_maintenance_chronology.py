import unittest
from datetime import timedelta
from sqlalchemy import update
from src.repositories.mart_models import MaintenanceEventMart
from src.domain.engineering import EngineeringError
import test_maximo_intelligence as mx

class ChronologyTest(unittest.TestCase):
    def setUp(self):
        self.fixture=mx.MaintenanceIntelligenceTest(); self.fixture.setUp()
        with self.fixture.engine.begin() as c:
            for i in range(3):
                c.execute(update(MaintenanceEventMart).where(MaintenanceEventMart.canonical_id==f'maintenance:synthetic-{i}').values(actual_start=mx.NOW-timedelta(days=3-i),actual_finish=mx.NOW-timedelta(days=2-i),failure_code='SOURCE-CODE',sources={'maximo':{'problemcode':'UNPROJECTED','credential':'never expose'}}))
    def tearDown(self): self.fixture.tearDown()
    def test_descending_chronology_and_stable_paging(self):
        f=self.fixture
        first=f.service.work_orders(f.actor,mx.ASSET,sort='chronology_desc',limit=2)
        last=f.service.work_orders(f.actor,mx.ASSET,sort='chronology_desc',offset=2,limit=2)
        self.assertEqual([x.canonical_record_id for x in first['items']+last['items']], [f'maintenance:synthetic-{i}' for i in (2,1,0)])
        self.assertTrue(first['has_more']);self.assertFalse(last['has_more'])
    def test_source_failure_code_is_not_cause_or_jobplan(self):
        f=self.fixture;r=f.service.work_orders(f.actor,mx.ASSET)['items'][0]
        self.assertEqual(r.failure_code,'SOURCE-CODE');self.assertIsNone(r.problem_code)
        self.assertIsNone(r.cause_code);self.assertIsNone(r.remedy_code)
        self.assertIsNone(r.job_plan_ref);self.assertIsNone(r.preventive_maintenance_ref)
        self.assertEqual(r.chronology_basis,'ACTUAL_START')
        self.assertEqual(r.freshness,'UNKNOWN');self.assertEqual(r.quality,'UNKNOWN')
        self.assertNotIn('credential',r.model_dump_json())
    def test_missing_execution_date_falls_back_explicitly(self):
        f=self.fixture
        with f.engine.begin() as c:
            c.execute(update(MaintenanceEventMart).values(actual_start=None,actual_finish=None))
        r=f.service.work_orders(f.actor,mx.ASSET)['items'][0]
        self.assertEqual(r.chronology_basis,'SOURCE_CHANGE');self.assertEqual(r.chronology_timestamp,mx.NOW)
    def test_unknown_dates_and_ties_are_deterministic(self):
        f=self.fixture
        with f.engine.begin() as c:
            c.execute(update(MaintenanceEventMart).values(actual_start=None,source_changed_at=None))
        rows=f.service.work_orders(f.actor,mx.ASSET,sort='chronology_desc')['items']
        self.assertEqual([r.canonical_record_id for r in rows],sorted(r.canonical_record_id for r in rows))
        self.assertTrue(all(r.chronology_timestamp is None and r.chronology_basis=='UNKNOWN' for r in rows))
    def test_sort_is_allowlisted_not_interpolated_sql(self):
        with self.assertRaises(EngineeringError):
            self.fixture.service.work_orders(self.fixture.actor,mx.ASSET,sort='changedate; DROP TABLE x')
