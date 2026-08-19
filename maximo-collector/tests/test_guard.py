"""Safety guard tests: the ONLY POST in this codebase is the login handshake."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.adapters.maximo.auth import MaximoAuth
from src.adapters.maximo.oslc_client import (
    OslcClient,
    OslcError,
    _next_page_url,
    _normalize_next_page_url,
    _normalize_member,
    _add_detail_select,
    _default_scope_clause,
)
from src.config import MaximoConfig


class ReadOnlyGuardTest(unittest.TestCase):
    def setUp(self):
        self.config = MaximoConfig(rate_limit_seconds=0)
        self.client = OslcClient(self.config, MaximoAuth(self.config))

    def test_post_to_oslc_blocked(self):
        for bad in ("POST", "PUT", "PATCH", "DELETE"):
            with self.assertRaises(OslcError):
                self.client.request(bad, "/oslc/os/mxasset")

    def test_lowercase_blocked_too(self):
        with self.assertRaises(OslcError):
            self.client.request("post", "/oslc/os/mxasset")

    def test_read_only_methods_allowed_by_guard(self):
        # guard raises only for non-read methods; method set is exact
        from src.adapters.maximo.oslc_client import READ_ONLY_METHODS
        self.assertEqual(READ_ONLY_METHODS, frozenset({"GET", "HEAD", "OPTIONS"}))

    def test_login_post_only_via_auth_module(self):
        # the login POST lives in auth.py only — OslcClient has no POST path
        import inspect
        from src.adapters.maximo import oslc_client as mod
        source = inspect.getsource(mod)
        self.assertNotIn(".post(", source)

    def test_custom_query_cannot_escape_bsr_scope(self):
        with self.assertRaises(OslcError):
            list(self.client.iterate("mxasset", where='siteid="OTHER"'))

    def test_object_specific_scopes_are_allowed(self):
        self.assertEqual(_default_scope_clause("mxwodetail", "BSR", "IP"), 'siteid="BSR"')
        self.assertEqual(_default_scope_clause("mxapisr", "BSR", "IP"), 'siteid="BSR"')
        self.assertEqual(_default_scope_clause("mxperson", "BSR", "IP"), 'locationorg="IP"')
        self.assertEqual(_default_scope_clause("mxitem", "BSR", "IP"), 'site="BSR"')
        self.assertEqual(_default_scope_clause("mxapilabor", "BSR", "IP"), 'worksite="BSR"')

    def test_unknown_scope_is_blocked(self):
        with self.assertRaises(OslcError):
            list(self.client.iterate("mxperson", where='orgid="IP"', required_scope='orgid="IP"'))

    def test_oslc_requests_negotiate_json(self):
        calls = []

        class Session:
            def __init__(self):
                self.cookies = []
                self.headers = {}

            def request(self, method, url, **kwargs):
                calls.append((method, url, kwargs))
                return SimpleNamespace(content=b"{}")

        session = Session()
        client = OslcClient(self.config, MaximoAuth(self.config, session=session), session=session)
        client.get("/oslc/os/mxasset")
        self.assertEqual(calls[0][2]["headers"], {"Accept": "application/json"})

    def test_auth_and_oslc_share_session(self):
        auth = MaximoAuth(self.config)
        client = OslcClient(self.config, auth)
        self.assertIs(client._session, auth.session)

    def test_next_page_rdf_resource_is_unwrapped(self):
        self.assertEqual(
            _next_page_url({"oslc:responseInfo": {"oslc:nextPage": {"rdf:resource": "next"}}}),
            "next",
        )

    def test_spi_business_fields_are_normalized(self):
        normalized = _normalize_member({"spi:assetnum": "A-1", "spi:description": "Pump"})
        self.assertEqual(normalized, {"assetnum": "A-1", "description": "Pump"})

    def test_asset_detail_select_is_added(self):
        url = _add_detail_select("http://maximo.example/maximo/oslc/os/mxapiasset/1")
        self.assertIn("oslc.select=", url)
        self.assertIn("assetnum", url)

    def test_next_page_internal_host_uses_configured_origin(self):
        with self.assertRaises(OslcError):
            _normalize_next_page_url(
                "http://mx761app1.example/maximo/oslc/os/mxapiasset?pageno=2",
                "http://maximo.example/maximo",
            )


if __name__ == "__main__":
    unittest.main()
