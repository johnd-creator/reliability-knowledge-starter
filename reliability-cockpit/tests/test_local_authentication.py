"""No public seed credentials. All secrets are generated only inside disposable fixtures."""
import json
import os
import secrets
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from src.domain.engineering import EngineeringError, Principal, Role
from src.repositories.application_boundary import ApplicationStore
from src.repositories.application_migrations import ApplicationMigrator
from src.services.application_identity import SessionAuthority, SessionRow
from src.services.local_authentication import LocalIdentityProvider, PasswordPolicy, ACCOUNT, EVENT


@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable PostgreSQL required")
class LocalAuthTest(unittest.TestCase):
    def setUp(self):
        url = make_url(os.environ["NADI_APPLICATION_TEST_DSN"])
        if url.host not in {"127.0.0.1","localhost"} or not url.database.endswith("_test"):
            raise RuntimeError("isolated fixture only")
        self.engine = create_engine(url, hide_parameters=True)
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public")
        self.runner = ApplicationMigrator(self.engine,expected_database=url.database,isolated=True)
        self.runner.apply()
        self.now = datetime(2026,10,9,tzinfo=timezone.utc)
        self.store = ApplicationStore(self.engine,expected_database=url.database,isolated=True)
        self.provider = LocalIdentityProvider(self.store,clock=lambda:self.now)
        self.secret = secrets.token_urlsafe(24)
        self.admin_id = self.provider.bootstrap(username="fixture-admin",password=self.secret,
            assets={"asset:SYNTHETIC:A","asset:SYNTHETIC:B"},operator_ref="fixture-operator")
        self.admin = self.provider.current_grant(self.admin_id)
        self.authority = SessionAuthority(self.store,self.provider,origins={"https://nadi.example.invalid"},
            idle_seconds=300,absolute_seconds=3600,clock=lambda:self.now)

    def tearDown(self):
        self.engine.dispose()

    def user(self, *, username="fixture-engineer", roles=None, assets=None, require_change=False):
        return self.provider.create_account(self.admin,username=username,password=self.secret,
            roles=roles or {Role.AUTHOR},assets=assets or {"asset:SYNTHETIC:A"},require_change=require_change)

    def token(self, username="fixture-engineer"):
        return self.authority.establish_verified(self.provider.authenticate(username,self.secret))[0]

    def test_argon2id_immutable_identity_normalized_unique_and_safe_audit(self):
        user = self.user(username=" Fixture-Engineer ")
        with self.engine.connect() as c:
            row = c.execute(select(ACCOUNT).where(ACCOUNT.c.user_id==user)).mappings().one()
            self.assertTrue(row["password_hash"].startswith("$argon2id$"))
            self.assertNotEqual(row["password_hash"],self.secret)
            events = list(c.execute(select(EVENT)).mappings())
        self.assertNotIn(self.secret,str(events))
        with self.assertRaises(EngineeringError) as error:self.user(username="fixture-ENGINEER")
        self.assertEqual(error.exception.code,"ACCOUNT_CONFLICT")
        self.assertEqual(self.provider.authenticate("FIXTURE-ENGINEER",self.secret).principal.principal_id,user)

    def test_invalid_unknown_disabled_locked_generic_and_no_grant(self):
        user=self.user()
        for name in ("absent-account","bad name","fixture-engineer"):
            with self.assertRaises(EngineeringError) as e:self.provider.authenticate(name,secrets.token_urlsafe(24))
            self.assertEqual((e.exception.code,e.exception.status),("INVALID_CREDENTIALS",401))
        self.provider.change_account(self.admin,user,active=False)
        with self.assertRaises(EngineeringError) as e:self.provider.authenticate("fixture-engineer",self.secret)
        self.assertEqual(e.exception.code,"INVALID_CREDENTIALS")
        self.assertIsNone(self.provider.current_grant(user))

    def test_password_input_bounds_no_coercion_and_minimum_policy(self):
        for password in ("short",True,123," "*30,"x"*257):
            with self.assertRaises(EngineeringError):self.provider.create_account(self.admin,username="bounded",password=password,roles={Role.AUTHOR},assets=set())
        for minimum in (True,0,11,129):
            with self.assertRaises(ValueError):PasswordPolicy(minimum_length=minimum)
        for password in (None,True,"x"*257):
            with self.assertRaises(EngineeringError) as e:self.provider.authenticate("fixture-admin",password)
            self.assertEqual(e.exception.code,"INVALID_CREDENTIALS")

    def test_forced_change_cannot_get_session_then_changes_version(self):
        user=self.user(require_change=True)
        with self.assertRaises(EngineeringError) as e:self.provider.authenticate("fixture-engineer",self.secret)
        self.assertEqual(e.exception.code,"PASSWORD_CHANGE_REQUIRED")
        self.assertIsNone(self.provider.current_grant(user))
        grant=self.provider.authenticate("fixture-engineer",self.secret,new_password=secrets.token_urlsafe(24))
        self.assertEqual(grant.version,2)
        self.authority.establish_verified(grant)

    def test_account_lockout_and_shared_bounded_global_rate_limit(self):
        self.user()
        for _ in range(self.provider.policy.account_failures):
            with self.assertRaises(EngineeringError):self.provider.authenticate("fixture-engineer",secrets.token_urlsafe(24))
        with self.assertRaises(EngineeringError):self.provider.authenticate("fixture-engineer",self.secret)
        self.now+=timedelta(seconds=301)
        self.provider.authenticate("fixture-engineer",self.secret)
        other=LocalIdentityProvider(self.store,policy=PasswordPolicy(attempts_per_window=1),clock=lambda:self.now)
        with self.assertRaises(EngineeringError) as e:other.authenticate("unknown-account",self.secret)
        self.assertEqual(e.exception.status,429)
        with self.engine.connect() as c:self.assertEqual(c.scalar(text("SELECT count(*) FROM nadi_local_login_budget")),1)

    def test_disable_reactivate_does_not_resurrect_sessions(self):
        user=self.user();token=self.token()
        self.provider.change_account(self.admin,user,active=False)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass
        self.provider.change_account(self.admin,user,active=True)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass
        with self.authority.lease(self.token()) as actor:self.assertEqual(actor.principal_id,user)

    def test_reset_and_grant_changes_revoke_old_sessions(self):
        user=self.user();token=self.token()
        replacement=secrets.token_urlsafe(24)
        self.provider.change_account(self.admin,user,password=replacement)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass
        with self.assertRaises(EngineeringError):self.provider.authenticate("fixture-engineer",self.secret)
        grant=self.provider.authenticate("fixture-engineer",replacement,new_password=secrets.token_urlsafe(24))
        token=self.authority.establish_verified(grant)[0]
        self.provider.change_account(self.admin,user,roles={Role.REVIEWER},assets={"asset:SYNTHETIC:B"})
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass

    def test_role_assignment_scope_escalation_and_last_admin_denied(self):
        user=self.user();actor=self.provider.current_grant(user).principal
        with self.assertRaises(EngineeringError):self.provider.create_account(actor,username="escalate",password=self.secret,roles={Role.ADMIN},assets=set())
        with self.assertRaises(EngineeringError):self.provider.create_account(self.admin,username="foreign",password=self.secret,roles={Role.AUTHOR},assets={"asset:FOREIGN"})
        with self.assertRaises(EngineeringError):self.provider.change_account(self.admin,self.admin_id,active=False)
        with self.assertRaises(EngineeringError):self.provider.bootstrap(username="another-admin",password=self.secret,assets=set(),operator_ref="fixture")

    def test_opaque_proof_rejected_even_if_known_username(self):
        with self.assertRaises(EngineeringError):self.authority.establish("fixture-admin")

    def test_session_forgery_expiry_csrf_and_logout(self):
        self.user();grant=self.provider.authenticate("fixture-engineer",self.secret)
        token,csrf=self.authority.establish_verified(grant)
        for candidate in ("x"*43,token):
            with self.assertRaises(EngineeringError):
                with self.authority.lease(candidate,method="POST",origin="https://nadi.example.invalid",csrf="bad",content_type="application/json"):pass
        self.authority.revoke(grant.principal,token)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass
        token=self.token();self.now+=timedelta(seconds=301)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass

    def test_concurrent_normalized_creation_is_single_account(self):
        def create():
            try:return self.user(username="race-account")
            except EngineeringError:return None
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:create(),range(2)))
        self.assertEqual(sum(r is not None for r in results),1)
        with self.engine.connect() as c:self.assertEqual(c.scalar(select(text("count(*)")).select_from(ACCOUNT).where(ACCOUNT.c.username=="race-account")),1)

    def test_reset_serializes_with_inflight_authorized_command(self):
        from threading import Event
        user=self.user();token=self.token();entered=Event();release=Event()
        def command():
            with self.authority.lease(token):entered.set();release.wait(5)
        with ThreadPoolExecutor(max_workers=2) as pool:
            running=pool.submit(command);self.assertTrue(entered.wait(5))
            resetting=pool.submit(self.provider.change_account,self.admin,user,password=secrets.token_urlsafe(24))
            self.assertFalse(resetting.done());release.set();running.result(5);resetting.result(5)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass

    def test_old_verified_login_grant_rejected_after_password_race(self):
        user=self.user();grant=self.provider.authenticate("fixture-engineer",self.secret)
        self.provider.change_account(self.admin,user,password=secrets.token_urlsafe(24))
        with self.assertRaises(EngineeringError):self.authority.establish_verified(grant)
        with self.engine.connect() as c:self.assertEqual(c.scalar(select(text("count(*)")).select_from(SessionRow)),0)

    def test_cli_private_input_no_default_or_automatic_provisioning(self):
        from src.qa.users import secret
        with patch("sys.stdin.isatty",return_value=False):
            with self.assertRaises(EngineeringError):secret("test")
        self.assertEqual([s["status"] for s in self.runner.apply()],["APPLIED"]*5)
        with self.assertRaises(EngineeringError):ApplicationMigrator(self.engine,expected_database="wrong_test",isolated=True)

    def test_old_administrative_grant_cannot_mutate_after_revocation(self):
        user=self.user()
        self.provider.change_account(self.admin,self.admin_id,revoke=True)
        with self.assertRaises(EngineeringError):self.provider.change_account(self.admin,user,roles={Role.ADMIN})

    def test_security_audit_is_bounded_scoped_and_contains_no_credentials(self):
        self.user();self.provider.authenticate("fixture-engineer",self.secret)
        events=self.provider.security_events(self.admin,limit=1)
        self.assertEqual(len(events),1)
        self.assertNotIn(self.secret,str(events))
        self.assertFalse({"password","password_hash","token","csrf_token"}&set(events[0]))
        with self.assertRaises(EngineeringError):self.provider.security_events(self.admin,limit=1000)

    def test_revoke_all_roles_denies_grant_and_prior_session(self):
        user=self.user();token=self.token()
        self.provider.change_account(self.admin,user,roles=set())
        self.assertIsNone(self.provider.current_grant(user))
        with self.assertRaises(EngineeringError):
            with self.authority.lease(token):pass

    def test_security_history_runtime_cannot_update_or_delete(self):
        role="nadi_local_audit_fixture"
        with self.engine.begin() as c:
            c.exec_driver_sql("DO $$ BEGIN IF NOT EXISTS(SELECT FROM pg_roles WHERE rolname='nadi_local_audit_fixture') THEN CREATE ROLE nadi_local_audit_fixture NOLOGIN; END IF; END $$")
        self.runner.grant_writer(role)
        for sql in ("UPDATE nadi_local_security_event SET outcome='changed'", "DELETE FROM nadi_local_security_event", "TRUNCATE nadi_local_security_event"):
            with self.assertRaises(Exception) as error:
                with self.engine.begin() as c:
                    c.exec_driver_sql("SET LOCAL ROLE nadi_local_audit_fixture")
                    c.exec_driver_sql(sql)
            self.assertEqual(error.exception.orig.sqlstate,"42501")

    def test_operator_cli_authenticated_admin_create_and_no_secret_output(self):
        import io
        from contextlib import redirect_stdout
        from src.qa.users import main
        output=io.StringIO();temporary=secrets.token_urlsafe(24)
        with patch.dict(os.environ,{"NADI_APPLICATION_ADMIN_DSN":self.engine.url.render_as_string(hide_password=False)}), \
                patch("sys.stdin.isatty",return_value=True), \
                patch("getpass.getpass",side_effect=[self.secret,temporary,temporary]), redirect_stdout(output):
            result=main(["create","--expected-database",self.engine.url.database,"--operator-ref","fixture-operator",
                "--acknowledge-private-administration","--admin-username","fixture-admin","--username","cli-engineer",
                "--roles","AUTHOR","--assets","asset:SYNTHETIC:A"])
        self.assertEqual(result,0)
        self.assertNotIn(self.secret,output.getvalue());self.assertNotIn(temporary,output.getvalue())
        with self.engine.connect() as c:
            self.assertTrue(c.scalar(select(ACCOUNT.c.password_change_required).where(ACCOUNT.c.username=="cli-engineer")))
