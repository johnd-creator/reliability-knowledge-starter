"""Technical status is derived from stored metadata without constructing a PI client."""
import unittest
from datetime import datetime,timezone,timedelta
from unittest.mock import Mock,patch
from src.config import DbConfig
from src.repositories.database import Database,Base
from src.repositories.models import AttributeRegistryOrm,SnapshotOrm,CollectRunOrm
from src.repositories.store import CollectorStore
from src.api.app import create_app

class IntegrationObservationTest(unittest.TestCase):
    def setUp(self):
        self.db=Database(DbConfig(dsn="sqlite+pysqlite:///:memory:"));Base.metadata.create_all(self.db.engine)
        self.store=CollectorStore(self.db);self.now=datetime(2026,10,7,12,tzinfo=timezone.utc)
    def tearDown(self):self.db.engine.dispose()
    def test_empty_inventory_does_not_claim_success(self):
        result=self.store.integration_observation()
        self.assertEqual(result["registry_active"],0);self.assertIsNone(result["last_successful_activity"])
    def test_success_partial_quality_epoch_and_inactive_exclusion(self):
        with self.db.session() as s:
            s.add_all([AttributeRegistryOrm(attribute_id="ACTIVE",is_active=True),AttributeRegistryOrm(attribute_id="INACTIVE",is_active=False)])
            s.add_all([SnapshotOrm(attribute_id="ACTIVE",source_timestamp=datetime(1970,1,1,tzinfo=timezone.utc),collected_at=self.now,value_good=False,value_questionable=True,source_value="PRIVATE"),SnapshotOrm(attribute_id="INACTIVE",value_good=True)])
            s.add_all([CollectRunOrm(scope="snapshot",started_at=self.now-timedelta(minutes=1),finished_at=self.now,attributes_seen=1,rows_collected=1,errors=0,aborted=False),CollectRunOrm(scope="snapshot",started_at=self.now,finished_at=self.now+timedelta(seconds=10),attributes_seen=1,rows_collected=0,errors=1,aborted=False)])
            s.commit()
        result=self.store.integration_observation()
        self.assertEqual(result["registry_total"],2);self.assertEqual(result["registry_active"],1);self.assertEqual(result["snapshots"],1)
        self.assertEqual(result["errors"],1);self.assertEqual(result["last_successful_activity"],self.now.isoformat())
        self.assertEqual(result["bad_quality_signals"],1);self.assertTrue(result["oldest_source_timestamp"].startswith("1970"))
        self.assertNotIn("PRIVATE",str(result))
        self.assertEqual(result["future_source_timestamps"],0)
    def test_fixed_api_is_get_and_stored_only(self):
        route=next(r for r in create_app().routes if r.path=="/integration-observation")
        self.assertEqual(route.methods,{"GET"})
        store=Mock();store.integration_observation.return_value={"availability":"AVAILABLE"}
        with patch("src.adapters.pi.client.PiClient") as client:
            self.assertEqual(route.endpoint(store),{"availability":"AVAILABLE"});client.assert_not_called()

    def test_future_source_time_count_is_explicit(self):
        with self.db.session() as s:
            s.add(AttributeRegistryOrm(attribute_id="FUTURE",is_active=True))
            s.add(SnapshotOrm(attribute_id="FUTURE",source_timestamp=datetime.now(timezone.utc)+timedelta(days=1),value_good=True))
            s.commit()
        self.assertEqual(self.store.integration_observation()["future_source_timestamps"],1)
