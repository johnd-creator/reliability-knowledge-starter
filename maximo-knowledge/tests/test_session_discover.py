import unittest

from scripts.discover import DiscoveryError
from scripts.session_discover import BrowserSessionClient


class FakeResponse:
    status = 200
    headers = {"Content-Type": "application/json"}

    def body(self):
        return b'{"openapi":"3.0.0","paths":{}}'


class FakeRequestContext:
    def __init__(self):
        self.calls = []

    def fetch(self, url, **kwargs):
        method = kwargs.pop("method")
        self.calls.append((method, url, kwargs))
        return FakeResponse()


class BrowserSessionTests(unittest.TestCase):
    def test_browser_adapter_only_sends_allowed_method(self):
        context = FakeRequestContext()
        client = BrowserSessionClient(context, "http://example.invalid/maximo", 1000, 0)
        status, headers, body = client.request("GET", "/oslc/oas")
        self.assertEqual(status, 200)
        self.assertIn(b"openapi", body)
        self.assertEqual(context.calls[0][0:2], ("GET", "http://example.invalid/maximo/oslc/oas"))

    def test_browser_adapter_rejects_mutation(self):
        context = FakeRequestContext()
        client = BrowserSessionClient(context, "http://example.invalid/maximo", 1000, 0)
        with self.assertRaises(DiscoveryError):
            client.request("POST", "/j_security_check")
        self.assertEqual(context.calls, [])


if __name__ == "__main__":
    unittest.main()
