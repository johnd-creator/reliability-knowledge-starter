"""Hermetic Streamlit flow tests using the shipped model and fake collector data."""
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from streamlit.testing.v1 import AppTest
from pi_input import ROOT, FEATURES

class UiTest(unittest.TestCase):
    def test_manual_and_valid_pi_then_stale(self):
        row=pd.read_excel(ROOT/'Data_DCS_NK.xlsx').iloc[0]
        now=datetime.now(timezone.utc)
        mapping={'version':1,'features':{f:{'attribute_id':str(i),'status':'verified','evidence_ref':'synthetic test fixture','source_unit':'fixture','training_unit':'fixture','source_unit_confirmed':True} for i,f in enumerate(FEATURES)}}
        registry={str(i):{'web_id':'fixture'+str(i),'unit':'fixture'} for i in range(13)}
        attrs=[{'attribute_id':i,'web_id':e['web_id'],'unit_of_measure':'fixture','business_name':FEATURES[int(i)]} for i,e in registry.items()]
        snaps=[{'attribute_id':str(i),'value':float(row[f]),'value_good':True,'value_questionable':False,'value_substituted':False,'units':'fixture','source_timestamp':now.isoformat()} for i,f in enumerate(FEATURES)]
        def get(_reader,path):return snaps if path.startswith('/snapshots') else attrs
        with patch('pi_panel.load_mapping',return_value=mapping),patch('pi_panel.verified_registry',return_value=registry),patch('pi_input.CollectorReader.get',get):
            at=AppTest.from_file(str(ROOT/'nk_web_app.py')).run(timeout=30)
            self.assertFalse(at.exception)
            at.sidebar.button[0].click().run(timeout=30)
            self.assertFalse(at.exception)
            self.assertTrue(any(m.label=='Nilai Kalor (NK) Prediksi' for m in at.metric))
            at.radio[0].set_value('PI Collector').run(timeout=30)
            self.assertFalse(at.exception)
            self.assertTrue(any(m.label=='Nilai Kalor (NK) Prediksi' for m in at.metric))
            self.assertTrue(at.session_state['pi_prediction_history'])
            snaps[0]['source_timestamp']=(now-timedelta(hours=2)).isoformat()
            at.run(timeout=30)
            self.assertFalse(at.exception)
            self.assertFalse(any(m.label=='Nilai Kalor (NK) Prediksi' for m in at.metric))
            self.assertTrue(at.warning)
            at.radio[0].set_value('Manual').run(timeout=30)
            self.assertFalse(at.exception)
            self.assertFalse(any(m.label=='Nilai Kalor (NK) Prediksi' for m in at.metric))

if __name__=='__main__':unittest.main()
