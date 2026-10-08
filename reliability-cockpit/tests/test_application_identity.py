"""Trusted fixture identity, shared local sessions and security-negative acceptance."""
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from threading import RLock
from unittest.mock import patch
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.pool import StaticPool
from src.domain.engineering import Principal, Role, EngineeringError
from src.repositories.application_boundary import ApplicationStore
from src.services.application_identity import SessionAuthority, IdentityBase, SessionRow, SecurityRow, IdentityGrant

NOW=datetime(2026,10,9,tzinfo=timezone.utc)
ASSET="asset:SYNTHETIC:A"
class FixtureProvider:
    def __init__(self):
        self.lock=RLock()
        self.grants={name:IdentityGrant(principal=Principal(principal_id=name,roles=roles,asset_ids={ASSET}),version=1,valid_until=NOW+timedelta(hours=2))
          for name,roles in (("author",{Role.AUTHOR}),("reviewer",{Role.REVIEWER}),("admin",{Role.ADMIN}))}
    def verify_assertion(self,assertion):
        if assertion not in self.grants:raise EngineeringError("AUTHENTICATION_REQUIRED",401)
        return self.grants[assertion]
    def current_grant(self,subject):return self.grants.get(subject)
    @contextmanager
    def guard(self,subject,version):
        with self.lock:
            grant=self.current_grant(subject)
            if not grant or grant.version!=version:raise EngineeringError("IDENTITY_REVOKED",401)
            yield

class IdentityTest(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine("sqlite://",poolclass=StaticPool,connect_args={"check_same_thread":False})
        IdentityBase.metadata.create_all(self.engine)
        self.provider=FixtureProvider();self.now=NOW
        self.store=ApplicationStore(self.engine,expected_database="fixture_test",isolated=True)
        self.authority=SessionAuthority(self.store,self.provider,origins={"https://nadi.example.invalid"},idle_seconds=300,absolute_seconds=3600,clock=lambda:self.now)
        self.token,self.csrf=self.authority.establish("author")
        app=FastAPI();dependency=self.authority.dependency()
        @app.get("/read")
        def read(actor=Depends(dependency)):return {"subject":actor.principal_id,"roles":sorted(actor.roles),"assets":sorted(actor.asset_ids)}
        @app.post("/write")
        def write(actor=Depends(dependency)):return {"actor":actor.principal_id}
        self.client=TestClient(app,base_url="https://nadi.example.invalid")
    def tearDown(self):self.client.close();self.engine.dispose()
    def headers(self,**extra):return {"origin":"https://nadi.example.invalid","x-csrf-token":self.csrf,"content-type":"application/json",**extra}
    def cookie(self):self.client.cookies.set(self.authority.COOKIE,self.token)
    def code(self,code,operation):
        with self.assertRaises(EngineeringError) as c:operation()
        self.assertEqual(c.exception.code,code)
    def test_cookie_secure_and_opaque(self):
        from starlette.responses import Response
        response=Response();self.authority.set_cookie(response,self.token)
        cookie=response.headers["set-cookie"]
        for value in ("Secure","HttpOnly","SameSite=strict","Path=/"):self.assertIn(value,cookie)
        self.assertEqual(response.headers["cache-control"],"no-store")
        with self.engine.connect() as c:
            row=c.execute(select(SessionRow.__table__)).mappings().first()
            self.assertNotIn(self.token,str(row));self.assertNotIn(self.csrf,str(row))
    def test_missing_and_forged_identity_denied(self):
        for token in (None,"forged", "x"*43):
            if token:self.client.cookies.set(self.authority.COOKIE,token)
            self.assertEqual(self.client.get("/read",headers={"X-Actor":"admin","X-Role":"ADMIN"}).status_code,401)
            self.client.cookies.clear()
    def test_trusted_principal_ignores_browser_authority(self):
        self.cookie();r=self.client.get("/read",headers={"X-Actor":"admin","X-Asset":ASSET,"X-Role":"ADMIN"})
        self.assertEqual(r.json()["subject"],"author");self.assertEqual(r.json()["roles"],["AUTHOR"])
    def test_correct_origin_csrf_allowed(self):
        self.cookie();self.assertEqual(self.client.post("/write",headers=self.headers(),json={}).json(),{"actor":"author"})
    def test_missing_untrusted_origin_denied(self):
        self.cookie()
        for origin in (None,"null","https://evil.example.invalid","https://nadi.example.invalid.evil.invalid"):
            headers=self.headers();headers.pop("origin") if origin is None else headers.update(origin=origin)
            self.assertEqual(self.client.post("/write",headers=headers,json={}).status_code,403)
    def test_csrf_missing_forged_and_cross_session_denied(self):
        self.cookie();_,other=self.authority.establish("reviewer")
        for token in (None,"x"*43,other):
            headers=self.headers();headers.pop("x-csrf-token") if token is None else headers.update({"x-csrf-token":token})
            self.assertEqual(self.client.post("/write",headers=headers,json={}).status_code,403)
    def test_content_type_denied(self):
        self.cookie();self.assertEqual(self.client.post("/write",headers=self.headers(**{"content-type":"text/plain"}),content="x").status_code,415)
    def test_idle_expiry_denied(self):
        self.now+=timedelta(seconds=301);self.cookie();self.assertEqual(self.client.get("/read").status_code,401)
    def test_absolute_expiry_denied_even_when_active(self):
        for minute in range(1,13):
            self.now=NOW+timedelta(seconds=minute*299)
            with self.authority.lease(self.token):pass
        self.now=NOW+timedelta(seconds=3601);self.cookie();self.assertEqual(self.client.get("/read").status_code,401)
    def test_revocation_shared_across_authorities(self):
        actor=self.provider.grants["author"].principal
        self.authority.revoke(actor,self.token)
        other=SessionAuthority(self.store,self.provider,origins={"https://nadi.example.invalid"},idle_seconds=300,absolute_seconds=3600,clock=lambda:self.now)
        with self.assertRaises(EngineeringError):
            with other.lease(self.token):self.fail("revoked session permitted")
    def test_directory_revocation_and_version_change_denied(self):
        self.provider.grants["author"]=self.provider.grants["author"].model_copy(update={"version":2})
        self.cookie();self.assertEqual(self.client.get("/read").status_code,401)
        del self.provider.grants["author"]
        self.assertEqual(self.client.get("/read").status_code,401)
    def test_admin_scoped_and_not_author_or_reviewer(self):
        admin=self.provider.grants["admin"].principal
        self.assertNotIn(Role.REVIEWER,admin.roles);self.assertNotIn(Role.AUTHOR,admin.roles)
        self.authority.revoke(admin,self.token)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(self.token):pass
    def test_admin_outside_target_scope_denied(self):
        grant=self.provider.grants["admin"]
        actor=grant.principal.model_copy(update={"asset_ids":frozenset({"asset:SYNTHETIC:OTHER"})})
        self.provider.grants["admin"]=grant.model_copy(update={"principal":actor})
        self.code("FORBIDDEN",lambda:self.authority.revoke(actor,self.token))
    def test_activity_has_no_secrets_or_raw_records(self):
        with self.authority.lease(self.token):pass
        with self.engine.connect() as c:
            data=str(c.execute(select(SecurityRow.__table__)).mappings().all())
            self.assertNotIn(self.token,data);self.assertNotIn(self.csrf,data);self.assertNotIn("cookie",data)
    def test_denial_audit_sanitized_without_claiming_actor(self):
        self.client.get("/read",headers={"X-Actor":"forged-secret"})
        with self.engine.connect() as c:
            rows=c.execute(select(SecurityRow.__table__).where(SecurityRow.action=="ACCESS_DENIED")).mappings().all()
            self.assertTrue(rows);self.assertIsNone(rows[0]["subject"])
            self.assertNotIn("forged-secret",str(rows))

    def test_provider_error_sanitized(self):
        with patch.object(self.provider,"verify_assertion",side_effect=RuntimeError("secret source URL")):
            self.code("AUTHENTICATION_UNAVAILABLE",lambda:self.authority.establish("x"))
    def test_session_fixation_not_reused(self):
        other,_=self.authority.establish("author");self.assertNotEqual(other,self.token)
    def test_wrong_database_anchors_fail_closed(self):
        with self.engine.begin() as c:c.exec_driver_sql("CREATE TABLE asset_af_mapping (id integer)")
        self.code("MART_WRITER_FORBIDDEN",lambda:ApplicationStore(self.engine,expected_database="fixture_test",isolated=True))
    def test_nonisolated_sqlite_rejected(self):
        self.code("ISOLATED_STORE_ONLY",lambda:ApplicationStore(self.engine,expected_database="fixture_test"))
