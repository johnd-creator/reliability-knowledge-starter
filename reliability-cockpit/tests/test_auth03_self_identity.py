"""Self identity only. All destructive fixture setup is disposable PostgreSQL gated."""
import os,unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from src.api.application_session import build_session_router
from src.services.local_authentication import ACCOUNT
import test_local_authentication as fixture
@unittest.skipUnless(os.getenv('NADI_APPLICATION_TEST_DSN'),'disposable PostgreSQL required')
class SelfIdentityTest(unittest.TestCase):
 def setUp(self):
  self.fx=fixture.LocalAuthTest(methodName='test_forced_change_cannot_get_session_then_changes_version');self.fx.setUp();self.user=self.fx.user()
  token=self.fx.token();app=FastAPI();app.include_router(build_session_router(self.fx.authority,enabled=True,resume_csrf=True));self.client=TestClient(app,base_url='https://nadi.example.invalid');self.client.cookies.set(self.fx.authority.COOKIE,token)
 def tearDown(self):self.client.close();self.fx.tearDown()
 def test_self_username_is_current_directory_identity_not_client_claim(self):
  r=self.client.get('/v1/engineering/session?username=fixture-admin&subject=other',headers={'X-Username':'fixture-admin','X-Roles':'ADMIN'})
  self.assertEqual(r.status_code,200);v=r.json();self.assertEqual(v['username'],'fixture-engineer');self.assertEqual(v['subject'],self.user);self.assertEqual(v['roles'],['AUTHOR']);self.assertEqual(set(v),{'subject','username','roles','asset_ids','csrf_token'})
 def test_self_query_never_mutates_account(self):
  with self.fx.engine.connect() as c:before=dict(c.execute(select(ACCOUNT).where(ACCOUNT.c.user_id==self.user)).mappings().one())
  self.assertEqual(self.client.get('/v1/engineering/session').status_code,200)
  with self.fx.engine.connect() as c:after=dict(c.execute(select(ACCOUNT).where(ACCOUNT.c.user_id==self.user)).mappings().one())
  self.assertEqual(before,after)
 def test_missing_display_name_does_not_replace_canonical_subject(self):
  with patch.object(self.fx.provider,'self_username',return_value=None):
   r=self.client.get('/v1/engineering/session');self.assertEqual(r.status_code,200);self.assertIsNone(r.json()['username']);self.assertEqual(r.json()['subject'],self.user)
 def test_revoked_identity_cannot_read_username(self):
  self.fx.provider.change_account(self.fx.admin,self.user,active=False)
  r=self.client.get('/v1/engineering/session');self.assertEqual(r.status_code,401);self.assertNotIn('username',r.json())
