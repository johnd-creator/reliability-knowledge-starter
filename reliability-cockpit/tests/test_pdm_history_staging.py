import copy,json,tempfile,unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from src.services.pdm_history_staging import event_key,iter_events,source_clock,write_plan,verified_events,fingerprint,capture_event_key

class FakeReader:
    sha='a'*64;names=['DEMO SHEET'];path=Path('demo.xlsx')
    def __init__(self,values=None):self.values=values or {}
    def shape(self,i):return 4,3
    def cell(self,i,cell):
        raw={'A1':'Tanggal','B2':'1V (mm/s)','C2':'1H (mm/s)','A3':'2020-01-03','B3':0,'C3':None,'A4':'2020-01-04','B4':2,'C4':3}.get(cell)
        result={'cell':cell,'raw_value':raw,'date_interpretation':None,'source_type':'n' if isinstance(raw,(int,float)) else 's','formula_present':False,'formula_sha256':None,'cache_status':'LITERAL','number_format':'General','xml_value':None}
        result.update(self.values.get(cell,{}));return result
    def close(self):pass

def sample_profile():
    return {'id':'demo-s001','sheet_index':0,'method':'VIBRATION','version':'demo-1','clocks':[{'source_label':'Tanggal','header_cells':['A1']}],'fields':[{'id':'axis-'+c,'source_label':c.replace('B','1V').replace('C','1H')+' (mm/s)','unit':'mm/s','header_cells':[c+'2'],'unit_cells':[c+'2'],'row_role':'INPUT','value_region':c+'3:'+c+'4','source_point':c,'source_axis':'V' if c=='B' else 'H'} for c in ['B','C']]}
BOOK={'id':'DEMO','sha256':'a'*64}
def events(reader=None,profile=None,**kw):return list(iter_events(reader or FakeReader(),BOOK,profile or sample_profile(),date(2026,10,21),**kw))

class HistoryStageTest(unittest.TestCase):
    def test_zero_null_date_and_provisional_boundary(self):
        row=events()[0];self.assertEqual(row['status'],'ACCEPTED');capture=row['draft']['input_capture'];self.assertEqual([x['raw_value'] for x in capture['rows']],[0,None]);self.assertEqual(capture['clocks'][0]['value'],'2020-01-03');self.assertEqual(row['draft']['measurements'],[]);self.assertIsNone(row['draft']['inspected_at'])
    def test_unknown_unit_preserved_and_held(self):
        p=sample_profile();p['fields'][0]['unit']=None;r=events(profile=p)[0];self.assertEqual(r['status'],'UNRESOLVED');self.assertIn('UNIT_UNKNOWN',r['reasons']);self.assertIsNone(r['draft']['input_capture']['rows'][0]['unit'])
    def test_header_mismatch_held(self):self.assertIn('HEADER_MISMATCH',events(FakeReader({'B2':{'raw_value':'Other'}}))[0]['reasons'])
    def test_cached_formula_never_recalculated_or_literal(self):
        r=events(FakeReader({'B3':{'raw_value':4,'formula_present':True,'cache_status':'STORED_FORMULA_RESULT_NOT_RECALCULATED'}}))[0];self.assertEqual(r['status'],'UNRESOLVED');self.assertEqual(r['draft']['input_capture']['rows'][0]['value_origin'],'SOURCE_FORMULA_RESULT')
    def test_uncached_formula_held_with_other_value(self):
        r=events(FakeReader({'B3':{'raw_value':None,'formula_present':True,'cache_status':'NO_STORED_FORMULA_RESULT'},'C3':{'raw_value':2}}))[0];self.assertIn('FORMULA_CACHE_REVIEW_REQUIRED',r['reasons'])
    def test_changed_source_hash_requires_explicit_review(self):
        reader=FakeReader();reader.sha='b'*64;self.assertIn('SOURCE_HASH_CHANGED_REVIEW_REQUIRED',events(reader)[0]['reasons']);self.assertEqual(events(reader,reviewed_hashes=['b'*64])[0]['status'],'ACCEPTED')
    def test_numeric_date_not_silently_interpreted(self):
        reader=FakeReader({'A3':{'raw_value':20200103}});self.assertIn('SOURCE_DATE_UNRESOLVED',events(reader)[0]['reasons']);rules={'demo-s001':{'source_sha256':'a'*64,'sheet_index':0,'axis':'ROW','locator':'A','encoding':'YYYYMMDD','rationale':'Explicit synthetic source test'}};self.assertEqual(events(reader,date_rules=rules)[0]['status'],'ACCEPTED');rules['demo-s001']['source_sha256']='b'*64;self.assertIn('DATE_RULE_IDENTITY_MISMATCH',events(reader,date_rules=rules)[0]['reasons'])
    def test_future_source_date_held(self):self.assertIn('FUTURE_SOURCE_DATE_REVIEW_REQUIRED',events(FakeReader({'A3':{'raw_value':'2030-01-01'}}))[0]['reasons'])
    def test_excel_error_rejected(self):self.assertEqual(events(FakeReader({'B3':{'raw_value':'#REF!','source_type':'e'}}))[0]['status'],'REJECTED')
    def test_empty_not_zero(self):self.assertEqual(events(FakeReader({'B3':{'raw_value':None},'C3':{'raw_value':None}}))[0]['status'],'REJECTED')
    def test_partial_event_is_skipped_independent_of_field_subset(self):
        source=events()[1];old={'event_key':source['event_key'],'record_id':'inspection:existing','rows':source['draft']['input_capture']['rows'][:1]};result=events(existing=[old])[1];self.assertEqual(result['status'],'EXISTING_PARTIAL');self.assertEqual(result['event_key'],source['event_key']);self.assertEqual(result['existing_record_id'],'inspection:existing')
    def test_existing_value_conflict_never_overwritten(self):
        e=events()[1];old={'event_key':e['event_key'],'record_id':'inspection:existing','rows':copy.deepcopy(e['draft']['input_capture']['rows'])};old['rows'][0]['raw_value']=999;self.assertIn('EXISTING_SAMPLE_CONFLICT',events(existing=[old])[1]['reasons'])
    def test_single_cell_partial_requires_axis(self):
        c=events()[1]['draft']['input_capture'];c['rows']=c['rows'][:1]
        with self.assertRaisesRegex(ValueError,'SINGLE_CELL_AXIS'):capture_event_key(c)
        c['source_event_axis']='ROW';self.assertEqual(capture_event_key(c),events()[1]['event_key'])
    def test_complete_plan_content_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            d=Path(root);stream=d/'events.jsonl';stream.write_text('{}\n');m={'events_sha256':__import__('hashlib').sha256(stream.read_bytes()).hexdigest()};m['plan_id']=fingerprint(m);(d/'manifest.json').write_text(json.dumps(m));self.assertEqual(list(verified_events(d)),[{}]);stream.write_text('{"status":"ACCEPTED"}\n')
            with self.assertRaisesRegex(ValueError,'CONTENT_CHANGED'):list(verified_events(d))

    def test_secondary_unresolved_date_cannot_hide_behind_valid_date(self):
        p=sample_profile();p['clocks'].append({'role':'DATE','source_label':'Other source date','header_cells':['D1']})
        for raw in [20300104,'ambiguous date']:
            event=events(FakeReader({'D3':{'raw_value':raw}}),p)[0]
            self.assertEqual(event['status'],'UNRESOLVED');self.assertIn('SOURCE_DATE_COMPONENT_UNRESOLVED',event['reasons'])
    def test_date_plus_literal_time_preserves_date_without_inventing_timestamp(self):
        p=sample_profile();p['clocks'].append({'role':'TIME','source_label':'Time','header_cells':['D1']})
        event=events(FakeReader({'D3':{'raw_value':0.5}}),p)[0]
        self.assertEqual(event['status'],'ACCEPTED');self.assertEqual(event['draft']['input_capture']['clocks'][1]['raw_value'],0.5)
        self.assertEqual(event['draft']['input_capture']['clocks'][1]['precision'],'RAW');self.assertIsNone(event['draft']['inspected_at'])
    def test_secondary_date_or_time_formula_and_clock_errors_are_held(self):
        for kind in ['DATE','TIME']:
            p=sample_profile();p['clocks'].append({'role':kind,'source_label':'Other clock','header_cells':['D1']})
            e=events(FakeReader({'D3':{'raw_value':'2030-01-04','formula_present':True}}),p)[0]
            self.assertEqual(e['status'],'UNRESOLVED');self.assertIn('FORMULA_CACHE_REVIEW_REQUIRED',e['reasons'])
            e=events(FakeReader({'D3':{'raw_value':'#REF!','source_type':'e'}}),p)[0]
            self.assertIn('SOURCE_CLOCK_ERROR_REVIEW_REQUIRED',e['reasons']);self.assertEqual(e['status'],'UNRESOLVED')
    def test_explicit_date_rule_does_not_discard_other_source_clock(self):
        p=sample_profile();p['clocks'].append({'role':'DATE','source_label':'Other date','header_cells':['D1']})
        rules={p['id']:{'source_sha256':'a'*64,'sheet_index':0,'axis':'ROW','locator':'A','encoding':'YYYYMMDD','rationale':'Synthetic explicit date rule'}}
        e=events(FakeReader({'A3':{'raw_value':20200103},'D3':{'raw_value':20300104}}),p,date_rules=rules)[0]
        self.assertEqual(e['status'],'UNRESOLVED');self.assertEqual(len(e['clock_proof']),2)
    def test_unit_expression_is_exact_in_separate_unit_cell(self):
        p=sample_profile();f=p['fields'][0];f.update(source_label='1V',unit_cells=['D1'])
        for unit in ['mm/s²','mm/s-rms','xmm/s','MM/S','mm/s2','mm/s / extra']:
            e=events(FakeReader({'B2':{'raw_value':'1V'},'D1':{'raw_value':'Vibration ('+unit+')'}}),p)[0]
            self.assertEqual(e['status'],'UNRESOLVED',unit);self.assertIn('UNIT_HEADER_MISMATCH',e['reasons'])
        for text in ['mm/s','Vibration (mm/s)','Vibration [mm/s]']:
            self.assertEqual(events(FakeReader({'B2':{'raw_value':'1V'},'D1':{'raw_value':text}}),p)[0]['status'],'ACCEPTED')
    def test_formula_header_and_unit_evidence_require_review(self):
        self.assertIn('FORMULA_CACHE_REVIEW_REQUIRED',events(FakeReader({'B2':{'formula_present':True}}))[0]['reasons'])

if __name__=='__main__':unittest.main()
