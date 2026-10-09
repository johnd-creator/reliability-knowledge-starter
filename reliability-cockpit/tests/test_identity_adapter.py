import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.services.identity_adapter import EnterpriseIdentityAdapter
from src.api.application_session import build_session_router
from src.domain.engineering import EngineeringError
from test_application_identity import IdentityTest
class AdapterTest(unittest.TestCase):
    tearDown = IdentityTest.tearDown
    def setUp(self):
        IdentityTest.setUp(self)
        class Verifier:
            def subject(self,proof):
                if proof!='verified-once':raise EngineeringError('AUTHENTICATION_REQUIRED',401)
                return 'author'
        self.adapter=EnterpriseIdentityAdapter(Verifier(),self.provider);self.authority.provider=self.adapter
        app=FastAPI();app.include_router(build_session_router(self.authority,enabled=True))
        self.client.close();self.client=TestClient(app,base_url='https://nadi.example.invalid')
    def test_adapter_rejects_forged_assertion(self):
        with self.assertRaises(EngineeringError):self.adapter.verify_assertion('author')
    def test_bootstrap_cookie_logout(self):
        response=self.client.post('/v1/engineering/session',json={'proof':'verified-once'},headers={'origin':'https://nadi.example.invalid'})
        self.assertEqual(response.status_code,200)
        for flag in ['Secure','HttpOnly','SameSite=strict']:self.assertIn(flag,response.headers['set-cookie'])
        self.assertEqual(self.client.get('/v1/engineering/session').json()['roles'],['AUTHOR'])
        out=self.client.post('/v1/engineering/session/logout',json={},headers={'origin':'https://nadi.example.invalid','x-csrf-token':response.json()['csrf_token']})
        self.assertEqual(out.status_code,200);self.assertEqual(self.client.get('/v1/engineering/session').status_code,401)
    def test_wrong_origin_and_browser_roles(self):
        self.assertEqual(self.client.post('/v1/engineering/session',json={'proof':'verified-once','roles':['ADMIN']},headers={'origin':'https://nadi.example.invalid'}).status_code,422)
        self.assertEqual(self.client.post('/v1/engineering/session',json={'proof':'verified-once'},headers={'origin':'https://evil.example.invalid'}).status_code,403)
