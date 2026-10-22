import json, tempfile, unittest
from pathlib import Path
from datetime import date
from hashlib import sha256
from openpyxl import Workbook
from src.services.pdm_complete_plan import write_complete_plan, verify_plan, CompleteReader, scalar, canonical


class CompletePlanTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.root.chmod(0o700)
        self.book=self.root/'source.xlsx';w=Workbook();s=w.active;s.title='Source equipment label'
        for address,value in {'A1':'Tanggal','B1':'V','B2':'mm/s','A3':'2020-01-02','B3':0,'C3':5,'D3':'Unclassified note','A4':'uncertain date','A5':'2020-01-03','B5':'=1+1'}.items():s[address]=value
        w.save(self.book)
        self.source={'id':'WB-X','sha256':sha256(self.book.read_bytes()).hexdigest()}
        field={'id':'value','source_label':'V','unit':'mm/s','header_cells':['B1'],'unit_cells':['B2'],'value_region':'B3:B5','row_role':'INPUT'}
        self.profile={'id':'p','version':'1','source_ref':'WB-X','sheet_index':0,'method':'VIBRATION','fields':[field,dict(field,id='alias'),dict(field,id='reference',value_region='C3:C5',row_role='REFERENCE')],'clocks':[{'role':'DATE','source_label':'Tanggal','header_cells':['A1']}]}
        self.catalog=self.root/'catalog.ts';self.catalog.write_text('export const captureSources='+json.dumps([self.source])+';\nexport const captureProfiles='+json.dumps([self.profile])+';')
    def tearDown(self):self.tmp.cleanup()
    def plan(self):return write_complete_plan([{'source_ref':'WB-X','path':str(self.book)}],self.catalog,self.root/'plan',as_of=date(2026,1,1))
    def test_every_physical_cell_has_category_and_navigable_field(self):
        m=self.plan();self.assertEqual(m['counts']['cells'],10)
        cells=[json.loads(l) for l in (self.root/'plan/cells.jsonl').read_text().splitlines()]
        events=[json.loads(l) for l in (self.root/'plan/events.jsonl').read_text().splitlines()]
        covered={f['cell'] for e in events for f in e['document']['fields']}
        self.assertTrue({c['cell'] for c in cells}<=covered)
        self.assertEqual(sum(m['coverage'][0]['terminal_cells'].values()),10)
        self.assertEqual(m['coverage'][0]['overlapping_value_claim_cells'],2)
        self.assertEqual(sum(c['cell']=='B3' for c in cells),1)
        self.assertEqual(next(c for c in cells if c['cell']=='B3')['document']['raw_value'],0)
        self.assertEqual(verify_plan(self.root/'plan')['plan_id'],m['plan_id'])
    def test_formula_with_no_cached_value_is_kept_raw_with_expression(self):
        self.plan();cells=[json.loads(l) for l in (self.root/'plan/cells.jsonl').read_text().splitlines()]
        formula=next(c for c in cells if c['cell']=='B5')['document']
        self.assertIsNone(formula['raw_value']);self.assertTrue(formula['formula_present']);self.assertEqual(formula['formula_xml']['expression'],'1+1')
        self.assertEqual(formula['cache_status'],'NO_STORED_FORMULA_RESULT')
        events=[json.loads(l) for l in (self.root/'plan/events.jsonl').read_text().splitlines()]
        self.assertTrue(any(any(f['cell']=='B5' for f in e['document']['fields']) and e['document']['classification']=='RAW_UNRESOLVED' for e in events))
    def test_alias_collision_not_promoted_and_unknown_region_retained(self):
        self.plan();events=[json.loads(l) for l in (self.root/'plan/events.jsonl').read_text().splitlines()]
        item=next(e for e in events if e['profile_id']=='p' and e['position']==3)
        self.assertIn('OVERLAPPING_FIELD_CLAIMS',item['document']['reasons']);self.assertEqual(item['document']['classification'],'RAW_UNRESOLVED')
        self.assertTrue(any(f['cell']=='D3' and f['role']=='UNCLASSIFIED' for e in events for f in e['document']['fields']))
    def test_modified_stream_is_rejected(self):
        self.plan();p=self.root/'plan/cells.jsonl';p.write_text(p.read_text()+'{}\n')
        with self.assertRaisesRegex(ValueError,'CONTENT_CHANGED'):verify_plan(self.root/'plan')
    def test_nonfinite_is_preserved_as_typed_raw_not_zero_or_null(self):
        self.assertEqual(json.loads(canonical(scalar(float('nan')))),{'nonfinite_float':'nan'})
        self.assertEqual(scalar(0),0);self.assertIsNone(scalar(None))
    def test_original_bytes_unchanged_and_repeat_uses_new_directory(self):
        before=self.book.read_bytes();self.plan();self.assertEqual(self.book.read_bytes(),before)
        with self.assertRaisesRegex(ValueError,'NEW_COMPLETE'):self.plan()

    def test_authenticated_anonymous_plan_survives_original_stream_replacement(self):
        from src.services.pdm_complete_import import frozen_plan, chunks
        manifest=self.plan()
        with frozen_plan(self.root/'plan',manifest['plan_id']) as frozen:
            before=list(chunks(frozen))
            (self.root/'plan/cells.jsonl').write_text('{}\n')
            self.assertEqual(list(chunks(frozen)),before)
        with self.assertRaisesRegex(ValueError,'CONTENT_CHANGED'):
            with frozen_plan(self.root/'plan',manifest['plan_id']):self.fail('Must not yield unapproved bytes')
    def test_plan_stream_race_during_freeze_is_refused_before_writer(self):
        from unittest.mock import patch
        import src.services.pdm_complete_import as importer
        manifest=self.plan();original=importer.verify_plan
        def changed(directory):
            approved=original(directory);(self.root/'plan/cells.jsonl').write_text('{}\n');return approved
        with patch.object(importer,'verify_plan',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'CONTENT_CHANGED'):
                with importer.frozen_plan(self.root/'plan',manifest['plan_id']):self.fail('No database writer may start')


if __name__=='__main__':unittest.main()
