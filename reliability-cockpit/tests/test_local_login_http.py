"""Actual HTTPS sockets + local password login + disposable application PostgreSQL."""
import os, secrets, socket, threading, time, unittest
import uvicorn
from sqlalchemy import select, text
import test_bundle_d_http as legacy
from src.api.engineering_qa import create_qa_app
from src.domain.engineering import Role
from src.services.local_authentication import LocalIdentityProvider, ACCOUNT, EVENT


@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable PostgreSQL required")
class LocalLoginHttpTest(unittest.TestCase):
    def setUp(self):
        self.fx = legacy.RealHttpQaTest(methodName="test_records_survive_connection_reopen_and_conflict")
        self.fx.setUp()
        self.fx.client.close();self.fx.server.should_exit=True;self.fx.thread.join(10);self.fx.sock.close()
        self.password = secrets.token_urlsafe(24)
        provider = LocalIdentityProvider(self.fx.store,clock=lambda:self.fx.now)
        admin_id = provider.bootstrap(username="fixture-admin",password=self.password,
            assets={self.fx.asset},operator_ref="fixture-operator")
        self.admin=provider.current_grant(admin_id)
        self.users={name:provider.create_account(self.admin,username="fixture-"+name,password=self.password,
            roles={role},assets={self.fx.asset},require_change=False)
            for name,role in (("author",Role.AUTHOR),("reviewer",Role.REVIEWER))}
        self.fx.provider = provider;self.fx.authority.provider=provider
        # Existing directory lambda resolves self.provider; immutable audit IDs now local UUIDs.
        self.provider = provider
        app=create_qa_app(authority=self.fx.authority,cases=self.fx.cases,inspections=self.fx.inspections,
            recommendations=self.fx.recommendations,context=self.fx.context,environment="development")
        from pathlib import Path
        tls=Path(self.fx.tls.name)
        self.fx.sock=socket.socket();self.fx.sock.bind(("127.0.0.1",0));port=self.fx.sock.getsockname()[1]
        self.fx.server=uvicorn.Server(uvicorn.Config(app,host="127.0.0.1",port=port,
            ssl_keyfile=str(tls/"key.pem"),ssl_certfile=str(tls/"cert.pem"),log_level="critical"))
        self.fx.thread=threading.Thread(target=lambda:self.fx.server.run(sockets=[self.fx.sock]),daemon=True);self.fx.thread.start()
        for _ in range(200):
            if self.fx.server.started:break
            time.sleep(.01)
        if not self.fx.server.started:raise RuntimeError("local fixture startup failed")
        self.fx.client=legacy.SocketClient("https://127.0.0.1:"+str(port));self.client=self.fx.client
        self.fx.credentials={}
        for actor in ("author","reviewer"):
            reply=self.login(actor)
            self.assertEqual(reply.status_code,200)
            self.fx.credentials[actor]=(self.client.cookies.get(self.fx.authority.COOKIE),reply.json()["csrf_token"])
            self.client.cookies.clear()

    def tearDown(self):
        self.fx.tearDown()

    def login(self, actor="author", **extra):
        self.client.cookies.clear()
        return self.client.request("POST","/v1/engineering/auth/login",json={"username":"fixture-"+actor,
            "password":self.password,**extra},headers={"Origin":"https://nadi.example.invalid"})

    def inspection(self):
        return self.fx.call("POST","inspections",{"request_id":"local-inspection","draft":{
            "canonical_asset_id":self.fx.asset,"method":"VIBRATION","method_version":"proposal-1",
            "inspector_ref":self.users["author"],"inspected_at":self.fx.now.isoformat(),
            "measurements":[{"quantity":"velocity","value":None,"unit":"mm/s"}],
            "observations":["Fixture human observation"],"interpretations":["Unverified hypothesis"]}},expected=201)

    def test_actual_password_login_complete_engineering_workflow_logout(self):
        row=self.inspection();row=self.fx.step("inspections",row,"submit")
        row=self.fx.step("inspections",row,"begin_review",{"reason":"Independent review"},"reviewer")
        row=self.fx.step("inspections",row,"review",{"decision":"APPROVED","reason":"Human evidence reviewed"},"reviewer")
        case=self.fx.approved_case(row)
        rec=self.fx.call("POST","recommendations",{"request_id":"local-recommendation","draft":{
            "canonical_asset_id":self.fx.asset,"case_ref":case["case_id"],"rationale":"Reviewed finding",
            "proposed_action":"Local follow-up only","evidence_selections":[{"kind":"MANUAL_INSPECTION","record_id":row["record_id"]}]}},expected=201)
        rec=self.fx.step("recommendations",rec,"submit")
        rec=self.fx.step("recommendations",rec,"review",{"decision":"APPROVED","reason":"Independent proposal review"},"reviewer")
        self.fx.step("recommendations",rec,"followup",{"status":"PLANNED","reason":"NADI local follow-up"})
        context=self.fx.call("GET","asset-context/"+self.fx.asset)
        self.assertEqual(context["recommendations"]["total"],1)
        self.assertEqual(context["assessment"],"NOT_ASSESSED")
        for actor in ("author","reviewer"):
            token,csrf=self.fx.credentials[actor];self.client.cookies.set(self.fx.authority.COOKIE,token)
            response=self.client.request("POST","/v1/engineering/session/logout",json={},
                headers={"Origin":"https://nadi.example.invalid","X-CSRF-Token":csrf})
            self.assertEqual(response.status_code,200)
            self.client.cookies.set(self.fx.authority.COOKIE,token)
            self.assertEqual(self.client.request("GET","/v1/engineering/cases").status_code,401)

    def test_generic_failure_no_plaintext_echo_cookie_flags_or_browser_roles(self):
        replies=[self.login(password=secrets.token_urlsafe(24)), self.login(username="absent-user")]
        self.assertEqual([r.status_code for r in replies],[401,401])
        self.assertEqual(replies[0].json(),replies[1].json())
        self.assertNotIn(self.password,str([r.json() for r in replies]))
        response=self.login(roles=["ADMIN"],asset_ids=["asset:FOREIGN"])
        self.assertEqual(response.status_code,422)
        self.assertNotIn(self.password,response.text)
        response=self.login();self.assertEqual(response.status_code,200)
        cookie=response.headers["Set-Cookie"]
        for flag in ("Secure","HttpOnly","SameSite=strict","Path=/"):
            self.assertIn(flag,cookie)
        self.assertEqual(response.headers["Cache-Control"],"no-store")
        self.assertEqual(self.client.request("POST","/v1/engineering/session",json={"proof":"fixture-author"},
            headers={"Origin":"https://nadi.example.invalid"}).status_code,401)

    def test_csrf_origin_cross_asset_and_source_mutation_rejected(self):
        token,csrf=self.fx.credentials["author"];self.client.cookies.set(self.fx.authority.COOKIE,token)
        for headers in ({"Origin":"https://evil.example.invalid"},{"Origin":"https://nadi.example.invalid"}):
            self.assertEqual(self.client.request("POST","/v1/engineering/session/logout",json={},headers=headers).status_code,403)
        self.assertEqual(self.client.request("POST","/v1/engineering/auth/login",json={"username":"fixture-author","password":self.password},headers={"Origin":"https://evil.example.invalid"}).status_code,403)
        self.fx.call("GET","asset-context/asset:FOREIGN",expected=404)
        for path in ("/maximo/workorders","/v1/engineering/maximo/workorders","/v1/engineering/pi/write"):
            self.assertEqual(self.client.request("POST",path,json={}).status_code,404)
        # Combined AUTHOR+REVIEWER still cannot review their own record.
        self.provider.change_account(self.admin,self.users["author"],roles={Role.AUTHOR,Role.REVIEWER})
        response=self.login();self.fx.credentials["author"]=(self.client.cookies.get(self.fx.authority.COOKIE),response.json()["csrf_token"])
        row=self.inspection();row=self.fx.step("inspections",row,"submit")
        self.fx.step("inspections",row,"begin_review",{"reason":"self approval attempt"},expected=403)

    def test_password_reset_disabled_user_and_validation_errors_safe(self):
        user=self.users["author"];token,csrf=self.fx.credentials["author"]
        temporary=secrets.token_urlsafe(24)
        self.provider.change_account(self.admin,user,password=temporary)
        self.client.cookies.set(self.fx.authority.COOKIE,token)
        self.assertEqual(self.client.request("GET","/v1/engineering/session").status_code,401)
        self.assertEqual(self.login(password=temporary).status_code,403)
        response=self.login(password=temporary,new_password=secrets.token_urlsafe(24));self.assertEqual(response.status_code,200)
        self.provider.change_account(self.admin,user,active=False)
        self.assertEqual(self.client.request("GET","/v1/engineering/session").status_code,401)
        response=self.login(password={"nested":self.password});self.assertEqual(response.status_code,422)
        self.assertNotIn(self.password,response.text)
