"""Bounded development ingress. No production routes, source calls or header trust."""
import asyncio
import json


class QaIngressLimits:
    def __init__(self, app, *, max_bytes, deadline_seconds):
        if type(max_bytes) is not int or not 1 <= max_bytes <= 20*1024*1024:
            raise ValueError("explicit request byte cap required")
        if type(deadline_seconds) is not int or not 1 <= deadline_seconds <= 30:
            raise ValueError("explicit bounded ingress deadline required")
        self.app, self.limit, self.deadline = app, max_bytes, deadline_seconds

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        async def fail(status, code):
            data = json.dumps({"detail": {"code": code}}).encode()
            await send({"type": "http.response.start", "status": status, "headers": [
                (b"content-type", b"application/json"), (b"cache-control", b"no-store"),
                (b"x-content-type-options", b"nosniff")]})
            await send({"type": "http.response.body", "body": data})
        lengths = [v for k, v in scope.get("headers", ()) if k.lower() == b"content-length"]
        if len(lengths) > 1 or any(not v.isdigit() for v in lengths):
            return await fail(400, "REQUEST_LENGTH_INVALID")
        if lengths and int(lengths[0]) > self.limit:
            return await fail(413, "REQUEST_TOO_LARGE")
        body = bytearray()
        try:
            async with asyncio.timeout(self.deadline):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    if message["type"] != "http.request":
                        return await fail(400, "REQUEST_CONTRACT_INVALID")
                    chunk = message.get("body", b"")
                    if len(body) + len(chunk) > self.limit:
                        return await fail(413, "REQUEST_TOO_LARGE")
                    body.extend(chunk)
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            return await fail(408, "REQUEST_TIMEOUT")
        sent = False
        async def replay():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()
        return await self.app(scope, replay, send)
