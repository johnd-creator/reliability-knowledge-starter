import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pi_input import FEATURES, Settings, CollectorReader, InputError, build_features, convert

class FeaturesTest(unittest.TestCase):
    def setUp(self):
        self.now=datetime.now(timezone.utc)
        self.mapping={'features':{f:{'attribute_id':str(i),'status':'verified','evidence_ref':'test fixture','source_unit':'MW','training_unit':'MW','source_unit_confirmed':True} for i,f in enumerate(FEATURES)}}
        self.registry={str(i):{'web_id':'web'+str(i),'unit':'MW'} for i in range(13)}
        self.attrs=[{'attribute_id':i,'web_id':r['web_id'],'unit_of_measure':'MW'} for i,r in self.registry.items()]
        self.snaps=[{'attribute_id':str(i),'value':float(i),'value_good':True,'value_questionable':False,'value_substituted':False,'source_timestamp':self.now.isoformat(),'units':'MW'} for i in range(13)]
    def batch(self):return build_features(self.mapping,self.attrs,self.snaps,Settings(),self.registry,self.now)
    def test_order_and_complete(self):self.assertEqual(self.batch().values,list(map(float,range(13))))
    def test_missing_mapping(self):
        self.mapping['features']['PS']['status']='unknown';self.assertIsNone(self.batch().values)
    def test_missing_snapshot(self):
        self.snaps.pop();self.assertIsNone(self.batch().values)
    def test_registry_identity_mismatch(self):
        self.attrs[0]['web_id']='other';self.assertIsNone(self.batch().values)
    def test_bad_and_unknown_quality(self):
        for field in ['value_good','value_questionable','value_substituted']:
            with self.subTest(field=field):
                original=self.snaps[0].pop(field);self.assertIsNone(self.batch().values);self.snaps[0][field]=original
        self.snaps[0]['value_substituted']=True;self.assertIsNone(self.batch().values)
    def test_non_numeric(self):
        for value in [None,True,float('nan'),float('inf'),'12']:
            self.snaps[0]['value']=value;self.assertIsNone(self.batch().values)
    def test_stale_future_naive_timestamp(self):
        for stamp in [(self.now-timedelta(hours=1)).isoformat(),(self.now+timedelta(minutes=1)).isoformat(),self.now.replace(tzinfo=None).isoformat(),'invalid',None]:
            self.snaps[0]['source_timestamp']=stamp;self.assertIsNone(self.batch().values)
    def test_skew(self):
        self.snaps[0]['source_timestamp']=(self.now-timedelta(seconds=400)).isoformat();self.assertIsNone(self.batch().values)
    def test_wrong_units(self):
        self.snaps[0]['units']='kPa';self.assertIsNone(self.batch().values)
    def test_pressure_conversion(self):self.assertAlmostEqual(convert(15000,'kPa','MPa'),15)
    def test_unknown_conversion(self):
        with self.assertRaises(InputError):convert(10,'','MPa')
        with self.assertRaises(InputError):convert(10,'MW','t/h')
    def test_api_failure_no_fallback(self):
        with patch('pi_input.build_opener',side_effect=OSError('private detail')):
            with self.assertRaisesRegex(InputError,'OSError') as err:CollectorReader(Settings()).read()
            self.assertNotIn('private detail',str(err.exception))

if __name__=='__main__':unittest.main()
