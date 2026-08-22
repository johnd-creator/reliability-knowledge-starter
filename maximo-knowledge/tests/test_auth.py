import http.cookiejar
import unittest
from urllib.parse import parse_qs

from scripts.discover import Config, DiscoveryError, ReadOnlyClient


class FakeResponse:
    def __init__(self, status=200, headers=None, body=b"{}", url=""):
        self.status = status
        self.headers = headers or {"Content-Type": "application/json"}
        self._body = body
        self.url = url

    def read(self, limit):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeOpener:
    def __init__(self, client, responses, *, set_cookie_on_post=True):
        self.client = client
        self.responses = list(responses)
        self.calls = []
        self.set_cookie_on_post = set_cookie_on_post

    def open(self, request, timeout):
        self.calls.append(request)
        if request.get_method() == "POST" and self.set_cookie_on_post:
            self.client.cookie_jar.set_cookie(
                http.cookiejar.Cookie(
                    version=0,
                    name="JSESSIONID",
                    value="memory-only",
                    port=None,
                    port_specified=False,
                    domain="example.invalid",
                    domain_specified=False,
                    domain_initial_dot=False,
                    path="/",
                    path_specified=True,
                    secure=False,
                    expires=None,
                    discard=True,
                    comment=None,
                    comment_url=None,
                    rest={},
                    rfc2109=False,
                )
            )
        return self.responses.pop(0)


def config(auth_mode="form"):
    return Config(
        "http://example.invalid/maximo",
        "/oslc/oas",
        auth_mode,
        "bearer-test-token",
        "user-secret",
        "pass-secret",
        0,
        0,
        10000,
    )


class AuthParityTests(unittest.TestCase):
    def test_form_auth_posts_only_to_exact_login_endpoint(self):
        client = ReadOnlyClient(config())
        client.opener = FakeOpener(client, [FakeResponse(url="http://example.invalid/maximo/home")])

        client.request("POST", "/j_security_check")

        request = client.opener.calls[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, "http://example.invalid/maximo/j_security_check")
        self.assertEqual(
            parse_qs(request.data.decode("utf-8")),
            {"j_username": ["user-secret"], "j_password": ["pass-secret"]},
        )

    def test_business_post_and_arbitrary_login_url_are_blocked_before_network(self):
        client = ReadOnlyClient(config())
        opener = FakeOpener(client, [])
        client.opener = opener

        with self.assertRaises(DiscoveryError):
            client.request("POST", "/oslc/os/mxasset")
        with self.assertRaises(DiscoveryError):
            client.request("POST", "https://evil.invalid/j_security_check")
        self.assertEqual(opener.calls, [])

    def test_successful_login_keeps_cookie_in_memory_and_get_has_no_login_body(self):
        client = ReadOnlyClient(config())
        client.opener = FakeOpener(
            client,
            [
                FakeResponse(url="http://example.invalid/maximo/home"),
                FakeResponse(body=b'{"openapi":"3.0.0"}', url="http://example.invalid/maximo/oslc/oas"),
            ],
        )

        client.request("GET", "/oslc/oas")

        self.assertTrue(client.logged_in)
        self.assertEqual([request.get_method() for request in client.opener.calls], ["POST", "GET"])
        self.assertIsNone(client.opener.calls[1].data)
        self.assertTrue(any(cookie.name == "JSESSIONID" for cookie in client.cookie_jar))

    def test_login_failure_does_not_loop(self):
        client = ReadOnlyClient(config())
        opener = FakeOpener(client, [FakeResponse(body=b"login.jsp")], set_cookie_on_post=False)
        client.opener = opener

        with self.assertRaisesRegex(DiscoveryError, "AUTHENTICATION FAILED"):
            client.authenticate()
        with self.assertRaisesRegex(DiscoveryError, "login limit"):
            client.authenticate()
        self.assertEqual(len(opener.calls), 1)

    def test_expiry_allows_one_relogin_only(self):
        client = ReadOnlyClient(config())
        opener = FakeOpener(
            client,
            [
                FakeResponse(url="http://example.invalid/maximo/home"),
                FakeResponse(status=302, headers={"Location": "/maximo/login.jsp", "Content-Type": "text/html"}),
                FakeResponse(url="http://example.invalid/maximo/home"),
                FakeResponse(body=b'{"ok":true}', url="http://example.invalid/maximo/oslc/oas"),
            ],
        )
        client.opener = opener

        status, _, body = client.request("GET", "/oslc/oas")

        self.assertEqual((status, body), (200, b'{"ok":true}'))
        self.assertEqual([request.get_method() for request in opener.calls], ["POST", "GET", "POST", "GET"])
        self.assertEqual(client._reauth_attempts, 1)

    def test_auth_logs_contain_no_credentials_or_cookie_names(self):
        client = ReadOnlyClient(config())
        client.opener = FakeOpener(client, [FakeResponse(url="http://example.invalid/maximo/home")])

        with self.assertLogs("scripts.discover", level="INFO") as captured:
            client.authenticate()
        output = "\n".join(captured.output)
        for secret in ("user-secret", "pass-secret", "JSESSIONID", "memory-only"):
            self.assertNotIn(secret, output)

    def test_existing_auth_modes_remain_supported(self):
        for mode in ("none", "bearer", "token", "basic"):
            client = ReadOnlyClient(config(mode))
            opener = FakeOpener(client, [FakeResponse(body=b"ok")])
            client.opener = opener
            status, _, body = client.request("GET", "/oslc/oas")
            self.assertEqual((status, body), (200, b"ok"))
            self.assertEqual([request.get_method() for request in opener.calls], ["GET"])


if __name__ == "__main__":
    unittest.main()
