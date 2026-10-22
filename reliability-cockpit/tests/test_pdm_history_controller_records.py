import importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[2]/'deploy/development/pdm_history_111/controller/local_fixture.py';s=importlib.util.spec_from_file_location('fixture_records_test',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
from src.domain.manual_inspection import ManualInspection
class Connection:
 def __init__(self,rows):self.rows=rows;self.sql=[]
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def execution_options(self,**kw):assert kw=={'stream_results':True};return self
 def execute(self,stmt):
  text=str(stmt);self.sql.append(text)
  if text.startswith('SET '):return []
  return iter(self.rows if 'FROM nadi_human_record ORDER' in text else [])
class Engine:
 def __init__(self,rows):self.c=Connection(rows)
 def connect(self):return self.c
class RecordsTest(unittest.TestCase):
 def doc(self):return ManualInspection(canonical_asset_id='asset:SYNTHETIC:A',method='VIBRATION',method_version='synthetic-1',inspector_ref='synthetic-author',record_id='inspection:SYNTHETIC',created_by='synthetic-author',created_at='2026-10-20T00:00:00Z',updated_at='2026-10-20T00:00:00Z',revision=1).model_dump(mode='json')
 def test_native_document_roundtrip_and_readonly_sql(self):
  e=Engine([('INSPECTION',self.doc())]);r=m.records_readiness(e);self.assertEqual(r['counts']['human'],1);self.assertEqual(r['raw_sha256'],r['normalized_sha256']);self.assertEqual(e.c.sql[0],'SET TRANSACTION READ ONLY');self.assertTrue(all(q.startswith(('SELECT','SET TRANSACTION READ ONLY')) for q in e.c.sql))
 def test_private_invalid_content_not_in_error(self):
  for row in [('INSPECTION',{'private':'NEVER_PRINT_PRIVATE_CONTENT'}),('UNKNOWN_KIND',self.doc())]:
   with self.assertRaisesRegex(RuntimeError,'^EXISTING_RECORD_NOT_READABLE$'):m.records_readiness(Engine([row]))
 def test_bounded_row_scan(self):
  with self.assertRaisesRegex(RuntimeError,'COMPATIBILITY_RECORD_SCAN_LIMIT'):m.records_readiness(Engine([('INSPECTION',self.doc())]*10001))
 def test_corrupted_native_type_not_coerced(self):
  d=self.doc();d['revision']='1'
  with self.assertRaisesRegex(RuntimeError,'EXISTING_RECORD_NOT_READABLE'):m.records_readiness(Engine([('INSPECTION',d)]))
if __name__=='__main__':unittest.main(verbosity=2)
