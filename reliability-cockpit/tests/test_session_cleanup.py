"""Source-free task cancellation and bounded thread-affine lease regression."""
import asyncio
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException
from src.services.application_identity import SessionAuthority
from src.domain.engineering import EngineeringError

class Lease:
    def __init__(self, *, fail=False):
        self.entering=threading.Event(); self.enter_gate=threading.Event()
        self.exiting=threading.Event(); self.exit_gate=threading.Event()
        self.enter_thread=None; self.exit_thread=None; self.error=None; self.fail=fail
    def __enter__(self):
        self.enter_thread=threading.get_ident();self.entering.set()
        assert self.enter_gate.wait(2), "fixture entry timed out"
        if self.fail: raise EngineeringError("IDENTITY_PROVIDER_UNAVAILABLE",503)
        return "fixture"
    def __exit__(self,*error):
        self.exit_thread=threading.get_ident();self.error=error;self.exiting.set()
        assert self.exit_gate.wait(2), "fixture exit timed out"

class SessionCleanupTest(unittest.IsolatedAsyncioTestCase):
    async def wait(self,event):
        for _ in range(1000):
            if event.is_set():return
            await asyncio.sleep(.001)
        self.fail("fixture event not reached")
    def setup_lease(self,fail=False):
        authority=object.__new__(SessionAuthority)
        authority._lease_slots=threading.BoundedSemaphore(1)
        lease=Lease(fail=fail);authority.lease=lambda *a,**k:lease
        request=SimpleNamespace(cookies={},method="GET",headers={})
        return authority,lease,request
    async def test_cancel_during_entry_releases_same_thread_and_loop_stays_live(self):
        authority,lease,request=self.setup_lease()
        gen=authority.dependency()(request);task=asyncio.create_task(gen.__anext__())
        await self.wait(lease.entering);task.cancel()
        # The event loop must continue while entry is blocked on its worker.
        await asyncio.sleep(.01);self.assertFalse(task.done())
        lease.exit_gate.set();lease.enter_gate.set()
        with self.assertRaises(asyncio.CancelledError):await task
        self.assertTrue(lease.exiting.is_set());self.assertEqual(lease.enter_thread,lease.exit_thread)
        self.assertIs(lease.error[0],asyncio.CancelledError)
        self.assertTrue(authority._lease_slots.acquire(False));authority._lease_slots.release()
    async def test_repeated_cancel_during_exit_cannot_interrupt_release(self):
        authority,lease,request=self.setup_lease();lease.enter_gate.set()
        gen=authority.dependency()(request);self.assertEqual(await gen.__anext__(),"fixture")
        close=asyncio.create_task(gen.aclose());await self.wait(lease.exiting)
        close.cancel();await asyncio.sleep(.01);close.cancel();await asyncio.sleep(.01)
        self.assertFalse(close.done());lease.exit_gate.set()
        with self.assertRaises(asyncio.CancelledError):await close
        self.assertEqual(lease.enter_thread,lease.exit_thread)
        self.assertTrue(authority._lease_slots.acquire(False));authority._lease_slots.release()
    async def test_capacity_rejects_without_spawning_another_worker(self):
        authority,lease,request=self.setup_lease();lease.enter_gate.set();lease.exit_gate.set()
        gen=authority.dependency()(request);await gen.__anext__()
        other=authority.dependency()(request)
        with self.assertRaises(HTTPException) as error:await other.__anext__()
        self.assertEqual(error.exception.detail,{"code":"SESSION_CAPACITY_EXCEEDED"})
        await gen.aclose();self.assertTrue(authority._lease_slots.acquire(False));authority._lease_slots.release()
    async def test_failed_entry_releases_capacity_without_exit(self):
        authority,lease,request=self.setup_lease(fail=True);lease.enter_gate.set()
        gen=authority.dependency()(request)
        with self.assertRaises(HTTPException) as error:await gen.__anext__()
        self.assertEqual(error.exception.status_code,503);self.assertFalse(lease.exiting.is_set())
        self.assertTrue(authority._lease_slots.acquire(False));authority._lease_slots.release()
    async def test_normal_exit_and_body_exception_preserve_context(self):
        authority,lease,request=self.setup_lease();lease.enter_gate.set();lease.exit_gate.set()
        gen=authority.dependency()(request);await gen.__anext__()
        with self.assertRaises(ValueError):await gen.athrow(ValueError("fixture failure"))
        self.assertIs(lease.error[0],ValueError);self.assertEqual(lease.enter_thread,lease.exit_thread)

class ProviderFailureTest(unittest.TestCase):
    def test_provider_outage_during_lease_is_sanitized_and_denies_request(self):
        from test_application_identity import IdentityTest
        fixture=IdentityTest();fixture.setUp()
        try:
            fixture.cookie()
            with patch.object(fixture.provider,"current_grant",side_effect=RuntimeError("private provider detail")):
                response=fixture.client.get("/read")
            self.assertEqual(response.status_code,503)
            self.assertEqual(response.json(),{"detail":{"code":"IDENTITY_PROVIDER_UNAVAILABLE"}})
            self.assertNotIn("private",response.text)
            self.assertEqual(fixture.client.get("/read").status_code,200)
        finally:fixture.tearDown()

@unittest.skipUnless(__import__("os").getenv("NADI_APPLICATION_TEST_DSN"), "disposable PostgreSQL required")
class SessionPostgresTest(unittest.TestCase):
    def setUp(self):
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.engine import make_url
        from src.repositories.application_boundary import ApplicationStore
        from src.services.application_identity import IdentityBase
        from test_application_identity import FixtureProvider,NOW
        url=make_url(os.environ["NADI_APPLICATION_TEST_DSN"])
        if url.host not in {"localhost","127.0.0.1"} or not url.database.endswith("_test"):
            raise RuntimeError("disposable loopback store only")
        self.engine=create_engine(url,pool_size=5,max_overflow=0,pool_timeout=.1,
            connect_args={"options":"-c statement_timeout=2000 -c lock_timeout=2000"})
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE TABLE fixture_write(id integer PRIMARY KEY)")
        IdentityBase.metadata.create_all(self.engine)
        self.provider=FixtureProvider()
        self.authority=SessionAuthority(ApplicationStore(self.engine,expected_database=url.database,isolated=True),self.provider,
            origins={"https://nadi.example.invalid"},idle_seconds=300,absolute_seconds=3600,clock=lambda:NOW,lease_capacity=2)
        self.token,_=self.authority.establish("author")
    def tearDown(self):self.engine.dispose()
    def test_same_session_serialization_and_revoke_racing_write(self):
        from concurrent.futures import ThreadPoolExecutor
        from sqlalchemy import text
        entered,release,revoked=threading.Event(),threading.Event(),threading.Event()
        def writer():
            with self.authority.lease(self.token):
                entered.set();assert release.wait(2)
                with self.engine.begin() as c:c.exec_driver_sql("INSERT INTO fixture_write VALUES(1)")
        def revoke():
            self.authority.revoke(self.provider.grants["author"].principal,self.token);revoked.set()
        with ThreadPoolExecutor(max_workers=2) as workers:
            first=workers.submit(writer);self.assertTrue(entered.wait(2))
            second=workers.submit(revoke);self.assertFalse(revoked.wait(.05));release.set()
            first.result(2);second.result(2)
        with self.assertRaises(EngineeringError):
            with self.authority.lease(self.token):self.fail("revoked write allowed")
        with self.engine.connect() as c:self.assertEqual(c.scalar(text("SELECT count(*) FROM fixture_write")),1)
        self.assertEqual(self.engine.pool.checkedout(),0)
    def test_concurrent_same_session_leases_serialize(self):
        from concurrent.futures import ThreadPoolExecutor
        first_entered,release,second_entered=threading.Event(),threading.Event(),threading.Event()
        def first():
            with self.authority.lease(self.token):first_entered.set();assert release.wait(2)
        def second():
            with self.authority.lease(self.token):second_entered.set()
        with ThreadPoolExecutor(max_workers=2) as workers:
            a=workers.submit(first);self.assertTrue(first_entered.wait(2));b=workers.submit(second)
            self.assertFalse(second_entered.wait(.05));release.set();a.result(2);b.result(2)
        self.assertEqual(self.engine.pool.checkedout(),0)
    def test_cancel_entry_rolls_back_database_lease_and_provider_guard(self):
        from contextlib import contextmanager
        original=self.provider.guard;started,release=threading.Event(),threading.Event()
        @contextmanager
        def blocked(*args):
            started.set();assert release.wait(2)
            with original(*args):yield
        async def exercise():
            self.provider.guard=blocked
            request=SimpleNamespace(cookies={self.authority.COOKIE:self.token},method="GET",headers={})
            gen=self.authority.dependency()(request);task=asyncio.create_task(gen.__anext__())
            for _ in range(1000):
                if started.is_set():break
                await asyncio.sleep(.001)
            self.assertTrue(started.is_set());task.cancel();await asyncio.sleep(.01);release.set()
            with self.assertRaises(asyncio.CancelledError):await task
        try:asyncio.run(exercise())
        finally:release.set();self.provider.guard=original
        self.assertEqual(self.engine.pool.checkedout(),0)
        with self.authority.lease(self.token):pass
        self.assertEqual(self.engine.pool.checkedout(),0)
    def test_pool_timeout_is_sanitized_and_capacity_recovers(self):
        held=[self.engine.connect() for _ in range(5)]
        async def exercise():
            request=SimpleNamespace(cookies={self.authority.COOKIE:self.token},method="GET",headers={})
            gen=self.authority.dependency()(request)
            with self.assertRaises(HTTPException) as error:await gen.__anext__()
            self.assertEqual(error.exception.detail,{"code":"IDENTITY_STORE_UNAVAILABLE"})
        try:asyncio.run(exercise())
        finally:
            for c in held:c.close()
        self.assertEqual(self.engine.pool.checkedout(),0)
        with self.authority.lease(self.token):pass
