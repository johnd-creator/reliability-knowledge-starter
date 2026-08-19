"""Programmatic login tests (FakeSession — no network)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import requests

from src.adapters.maximo.auth import MaximoAuth, MaximoAuthError
from src.config import MaximoConfig


def _resp(status=200, text="", content_type="text/html", headers=None):
    r = MagicMock(spec=requests.Response)
    r.status_code = status
    r.text = text
    r.content = text.encode("utf-8")
    r.headers = headers or {"Content-Type": content_type}
    r.url = "http://maximo.test/maximo/"
    return r


class FakeSession:
    """Mimics requests.Session: cookies.clear() works and each POST sets a
    fresh JSESSIONID (server behavior) unless set_cookie_on_post is False."""

    def __init__(self):
        self.cookies: list = []
        self.headers: dict[str, str] = {}
        self.post_responses: list = []
        self.posts: list[dict] = []
        self.set_cookie_on_post = True

    def post(self, url, **kwargs):
        self.posts.append({"url": url, **kwargs})
        if self.set_cookie_on_post:
            # server sets a fresh session cookie on the login response
            self.cookies.append(_cookie("JSESSIONID"))
        return self.post_responses.pop(0)


def _cookie(name):
    c = MagicMock()
    c.name = name
    return c


class LoginTest(unittest.TestCase):
    def _auth(self, session=None, **config_kwargs):
        kwargs = dict(rate_limit_seconds=0, username="bsr\\reader", password="secret")
        kwargs.update(config_kwargs)
        config = MaximoConfig(**kwargs)
        return MaximoAuth(config, session or FakeSession())

    def test_login_success_sets_cookie_in_memory(self):
        session = FakeSession()
        session.cookies.append(_cookie("JSESSIONID"))
        session.post_responses = [_resp(302, content_type="text/html")]
        auth = self._auth(session)
        auth.ensure_logged_in()
        self.assertTrue(auth.logged_in)
        # posted once, to the exact login path, url-encoded form
        self.assertEqual(len(session.posts), 1)
        self.assertIn("/j_security_check", session.posts[0]["url"])
        self.assertEqual(session.posts[0]["data"]["j_username"], "bsr\\reader")
        self.assertEqual(session.posts[0]["data"]["j_password"], "secret")

    def test_login_idempotent_within_session(self):
        session = FakeSession()
        session.cookies.append(_cookie("JSESSIONID"))
        session.post_responses = [_resp(200, content_type="text/html")]
        auth = self._auth(session)
        auth.ensure_logged_in()
        auth.ensure_logged_in()
        self.assertEqual(len(session.posts), 1)  # no second login

    def test_bad_credentials_raise_clear_error(self):
        session = FakeSession()
        session.cookies.append(_cookie("JSESSIONID"))
        # server re-serves the login form -> credentials rejected
        session.post_responses = [
            _resp(200, text="<html><form action='j_security_check'>login</form></html>")
        ]
        auth = self._auth(session)
        with self.assertRaises(MaximoAuthError) as ctx:
            auth.ensure_logged_in()
        self.assertIn("rejected", str(ctx.exception))
        # no retry loop — exactly one POST
        self.assertEqual(len(session.posts), 1)

    def test_login_error_redirect_is_rejected(self):
        session = FakeSession()
        session.post_responses = [
            _resp(302, content_type="", headers={"Location": "/maximo/webclient/login/loginerror.jsp"})
        ]
        auth = self._auth(session)
        with self.assertRaises(MaximoAuthError) as ctx:
            auth.ensure_logged_in()
        self.assertIn("rejected", str(ctx.exception))

    def test_no_cookie_means_login_failed(self):
        session = FakeSession()
        session.set_cookie_on_post = False  # server did not set a session cookie
        session.post_responses = [_resp(200, content_type="text/html")]
        auth = self._auth(session)
        with self.assertRaises(MaximoAuthError):
            auth.ensure_logged_in()

    def test_missing_credentials_raise_config_error(self):
        auth = self._auth(username=None, password=None)
        with self.assertRaises(MaximoAuthError):
            auth.ensure_logged_in()

    def test_token_mode_skips_login(self):
        session = FakeSession()
        auth = self._auth(session, auth_mode="token", token="abc123")
        auth.ensure_logged_in()
        self.assertTrue(auth.logged_in)
        self.assertEqual(session.headers.get("Authorization"), "Bearer abc123")
        self.assertEqual(len(session.posts), 0)

    def test_login_response_size_cap(self):
        session = FakeSession()
        session.post_responses = [_resp(text="x" * 32)]
        auth = self._auth(session, max_response_bytes=8)
        with self.assertRaises(MaximoAuthError) as ctx:
            auth.ensure_logged_in()
        self.assertIn("1 MiB safety cap", str(ctx.exception))

    def test_handle_expiry_forces_one_relogin(self):
        session = FakeSession()
        session.cookies.append(_cookie("LtpaToken2"))
        session.post_responses = [_resp(200, content_type="text/html")]
        auth = self._auth(session)
        auth.ensure_logged_in()
        session.post_responses = [_resp(200, content_type="text/html")]
        auth.handle_expiry()
        self.assertTrue(auth.logged_in)
        self.assertEqual(len(session.posts), 2)


class ExpiryDetectionTest(unittest.TestCase):
    def test_401_403_look_expired(self):
        self.assertTrue(MaximoAuth.looks_expired(_resp(401)))
        self.assertTrue(MaximoAuth.looks_expired(_resp(403)))

    def test_redirect_to_login_looks_expired(self):
        r = _resp(302, headers={"Content-Type": "text/html", "Location": "/maximo/webclient/login/login.jsp"})
        self.assertTrue(MaximoAuth.looks_expired(r))

    def test_json_200_not_expired(self):
        r = _resp(200, content_type="application/json", text='{"_member": []}')
        self.assertFalse(MaximoAuth.looks_expired(r))


if __name__ == "__main__":
    unittest.main()
