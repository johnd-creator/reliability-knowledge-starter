"""Candidate presentation -> unchanged server DTO compatibility; no workbook/DB/network access."""
import json
import unittest
from pathlib import Path
from pydantic import ValidationError
from src.domain.manual_inspection import InspectionDraft

PROFILES=json.loads((Path(__file__).resolve().parents[1]/'docs/evidence/nadi-pdm-workbook-01/candidate-dictionary.json').read_text())['profiles']+json.loads((Path(__file__).resolve().parents[1]/'docs/evidence/nadi-pdm-workbook-02/candidate-dictionary.json').read_text())['profiles']

def draft(profile):
    return {'canonical_asset_id':'asset:SYNTHETIC:WORKBOOK','method':profile['methodTerm'],
            'method_version':'SYNTHETIC-inspector-version','inspector_ref':'synthetic-author',
            'inspected_at':'2026-10-09T09:00:00+07:00',
            'measurements':[{'quantity':'SYNTHETIC-inspector-quantity' if f.get('sourcePointLabel') else f['label'],'unit':f['unit'] or None,'value':value,
                             'point_ref':None,'measured_at':None,
                             'quality':'INSPECTOR_REPORTED','provenance':'HUMAN_ENTERED_MEASUREMENT'}
                            for f,value in zip(profile['fields'],([0,None,'SYNTHETIC original text']*34))]}

class WorkbookContractTest(unittest.TestCase):
    def test_all_candidate_fields_preserve_server_scalar_and_unit_contract(self):
        for p in PROFILES:
            with self.subTest(profile=p['id']):
                data=draft(p);parsed=InspectionDraft.model_validate(data).model_dump(mode='json')
                self.assertEqual(parsed['measurements'],data['measurements'])
                self.assertEqual(parsed['inspected_at'],data['inspected_at'])
                self.assertEqual(parsed['method_extension'],{})
    def test_template_identity_cannot_enter_unapproved_contract_properties(self):
        data=draft(PROFILES[0]);data['template_id']=PROFILES[0]['id']
        with self.assertRaises(ValidationError):InspectionDraft.model_validate(data)
    def test_workbook_context_is_not_a_canonical_asset(self):
        data=draft(PROFILES[0]);del data['canonical_asset_id']
        with self.assertRaises(ValidationError):InspectionDraft.model_validate(data)
    def test_unknown_time_stays_null_not_midnight(self):
        data=draft(PROFILES[0]);data['inspected_at']=None
        parsed=InspectionDraft.model_validate(data)
        self.assertIsNone(parsed.inspected_at)
        self.assertTrue(all(x.measured_at is None for x in parsed.measurements))
