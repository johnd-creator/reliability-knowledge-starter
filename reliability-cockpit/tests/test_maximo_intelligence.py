"""Local factual reference acceptance; no source requests."""
import unittest
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from sqlalchemy import create_engine
from src.config import MartDbConfig
from src.repositories.mart_database import MartDatabase
from src.repositories.mart_models import MartBase,AssetMasterMart,ReliabilityAssetRegistryMart,MaintenanceEventMart
from src.domain.engineering import Principal,Role,EngineeringError
from src.services.maximo_intelligence import LocalMaintenanceIntelligence
NOW=datetime(2026,10,9,tzinfo=timezone.utc);ASSET="asset:SYNTHETIC:A"
class MaintenanceIntelligenceTest(unittest.TestCase):
 def setUp(self):
  self.temp=TemporaryDirectory();dsn="sqlite:///"+self.temp.name+"/fixture.db";self.engine=create_engine(dsn)
  MartBase.metadata.create_all(self.engine)
  with self.engine.begin() as c:
   c.execute(AssetMasterMart.__table__.insert().values(canonical_id=ASSET,contract_version="1.0",site_code="BSR",organization_code="IP",mart_created_at=NOW,mart_updated_at=NOW,provenance={},relationship_evidence={}))
   c.execute(ReliabilityAssetRegistryMart.__table__.insert().values(asset_ref=ASSET,source_asset_number="SYNTHETIC-A",site_code="BSR",organization_code="IP",registry_source="synthetic",snapshot_sha256="x"*64,snapshot_row_count=1,snapshot_imported_at=NOW))
   for i in range(3):
    c.execute(MaintenanceEventMart.__table__.insert().values(canonical_id=f"maintenance:synthetic-{i}",contract_version="1.0",id=f"synthetic-{i}",equipment_id=ASSET,work_order_id=f"SYNTHETIC-WO-{i}",status="WDONE",event_type="PM",source_changed_at=NOW,site_code="BSR",organization_code="IP",sources={"maximo":{"secret":"must not escape"}},provenance={"ingested_at":NOW.isoformat()},mart_created_at=NOW,mart_updated_at=NOW))
  self.db=MartDatabase(MartDbConfig(dsn));self.service=LocalMaintenanceIntelligence(self.db)
  self.actor=Principal(principal_id="fixture-author",roles={Role.AUTHOR},asset_ids={ASSET})
 def tearDown(self):self.db.engine.dispose();self.engine.dispose();self.temp.cleanup()
 def test_bounded_pagination_and_original_status(self):
  page=self.service.work_orders(self.actor,ASSET,limit=2)
  self.assertEqual(len(page["items"]),2);self.assertTrue(page["has_more"])
  self.assertEqual(page["items"][0].record_status,"WDONE")
  self.assertEqual(page["items"][0].freshness,"UNKNOWN")
 def test_exact_identity_provenance_and_no_raw_payload(self):
  row=self.service.resolve_work_order(self.actor,ASSET,"maintenance:synthetic-0")
  self.assertEqual(row.sources.maximo.source_record_ref,"SYNTHETIC-WO-0")
  self.assertTrue(row.informational_only);self.assertEqual(row.source_changed_at,NOW)
  self.assertEqual(row.collected_at,NOW);self.assertNotIn("secret",row.model_dump_json())
 def test_foreign_scope_and_unregistered_rejected(self):
  for actor,asset in ((None,ASSET),(self.actor,"asset:SYNTHETIC:OTHER")):
   with self.assertRaises(EngineeringError):self.service.work_orders(actor,asset)
 def test_no_fuzzy_number_or_cross_asset_resolution(self):
  with self.assertRaises(EngineeringError):self.service.resolve_work_order(self.actor,ASSET,"SYNTHETIC-WO-0")
 def test_invalid_pagination(self):
  for args in ({"limit":101},{"offset":-1},{"limit":True}):
   with self.assertRaises(EngineeringError):self.service.work_orders(self.actor,ASSET,**args)
 def test_query_wrapper_blocks_mutations(self):
  from sqlalchemy import update
  with self.db.read_session() as s:
   with self.assertRaises(RuntimeError):s.execute(update(MaintenanceEventMart).values(status="CLOSED"))
