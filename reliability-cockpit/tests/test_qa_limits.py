import asyncio, unittest
from src.api.qa_limits import QaIngressLimits


class QaLimitsTest(unittest.IsolatedAsyncioTestCase):
    async def call(self, chunks, headers=()):
        self.invoked = False
        async def app(scope, receive, send):
            self.invoked = True
            self.received = await receive()
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})
        middleware = QaIngressLimits(app, max_bytes=4, deadline_seconds=1)
        events = iter(chunks)
        async def receive():
            return next(events)
        results = []
        async def send(event):
            results.append(event)
        await middleware({"type": "http", "headers": headers}, receive, send)
        return results

    async def test_chunked_exact_cap_and_overflow(self):
        ok = await self.call([{"type":"http.request","body":b"ab","more_body":True},
                              {"type":"http.request","body":b"cd"}])
        self.assertEqual(ok[0]["status"],200)
        self.assertEqual(self.received["body"],b"abcd")
        bad = await self.call([{"type":"http.request","body":b"abcde"}])
        self.assertEqual(bad[0]["status"],413)
        self.assertFalse(self.invoked)

    async def test_invalid_or_declared_oversized_body_never_invokes_application(self):
        for headers, expected in [([(b"content-length",b"5")],413),
                                  ([(b"content-length",b"-1")],400),
                                  ([(b"content-length",b"1"),(b"content-length",b"1")],400)]:
            response=await self.call([],headers)
            self.assertEqual(response[0]["status"],expected)
            self.assertFalse(self.invoked)

    async def test_disconnect_never_authorizes(self):
        response=await self.call([{"type":"http.disconnect"}])
        self.assertEqual(response,[])
        self.assertFalse(self.invoked)

    async def test_timeout_sanitized_no_application_invocation(self):
        async def app(*args):
            raise AssertionError("must not invoke")
        async def receive():
            await asyncio.sleep(2)
        results=[]
        async def send(event):
            results.append(event)
        await QaIngressLimits(app,max_bytes=4,deadline_seconds=1)(
            {"type":"http","headers":[]},receive,send)
        self.assertEqual(results[0]["status"],408)
        self.assertIn(b"REQUEST_TIMEOUT",results[1]["body"])
