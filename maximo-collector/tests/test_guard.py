"""Safety guard tests: the ONLY POST in this codebase is the login handshake."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.adapters.maximo.auth import MaximoAuth
from src.adapters.maximo.oslc_client import (
    OslcClient,
    OslcError,
    OslcPaginationLimitError,
    OslcPaginationLoopError,
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

    def test_page_size_override_is_bounded(self):
        with self.assertRaises(OslcError):
            list(self.client.iterate("mxasset", page_size=0))
        with self.assertRaises(OslcError):
            list(self.client.iterate("mxasset", page_size=self.config.page_size + 1))

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

    def test_business_request_budget_blocks_request_101(self):
        class Session:
            def request(self, method, url, **kwargs):
                return SimpleNamespace(status_code=200, content=b"{}")

        session = Session()
        client = OslcClient(
            self.config,
            MaximoAuth(self.config, session=session),
            session=session,
            request_budget=1,
        )
        client.get("/oslc/os/mxasset")
        with self.assertRaises(OslcError):
            client.get("/oslc/os/mxasset")
        self.assertEqual(client.request_telemetry["business_requests"], 1)
        self.assertEqual(client.request_telemetry["status_counts"], {"200": 1})

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


class PaginationCompletionTest(unittest.TestCase):
    class Response:
        status_code = 200
        content = b"{}"
        headers = {"Content-Type": "application/json"}
        text = ""

        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

        def raise_for_status(self):
            return None

    class Auth:
        session = object()
        last_request_at = 0.0

        def ensure_logged_in(self):
            return None

    def _client(self, responses):
        config = MaximoConfig(rate_limit_seconds=0, base_url="http://maximo.example/maximo")
        client = OslcClient.__new__(OslcClient)
        client._config = config
        client._auth = self.Auth()
        client._session = client._auth.session
        client._last_request = 0.0
        queue = iter(responses)
        client.get = lambda _url: next(queue)
        return client

    def test_natural_final_page_is_complete_at_cap_boundary(self):
        client = self._client([
            self.Response({"_member": [{"wonum": "BSR-1"}]}),
        ])
        rows = list(client.iterate("mxwodetail", page_size=1, max_pages=1, identity_field="wonum"))
        self.assertEqual(len(rows), 1)

    def test_cap_with_next_page_raises_typed_error(self):
        client = self._client([
            self.Response({
                "_member": [{"wonum": "BSR-1"}],
                "oslc:responseInfo": {"oslc:nextPage": "?p=2"},
            }),
            self.Response({
                "_member": [{"wonum": "BSR-2"}],
                "oslc:responseInfo": {"oslc:nextPage": "?p=3"},
            }),
        ])
        with self.assertRaises(OslcPaginationLimitError) as raised:
            list(client.iterate("mxwodetail", page_size=1, max_pages=2, identity_field="wonum"))
        self.assertEqual(raised.exception.pages, 2)
        self.assertTrue(raised.exception.next_page_fingerprint)

    def test_repeated_next_page_raises_loop_error(self):
        client = self._client([
            self.Response({
                "_member": [{"wonum": "BSR-1"}],
                "oslc:responseInfo": {"oslc:nextPage": "?p=2"},
            }),
            self.Response({
                "_member": [{"wonum": "BSR-2"}],
                "oslc:responseInfo": {"oslc:nextPage": "?p=2"},
            }),
        ])
        with self.assertRaises(OslcPaginationLoopError):
            list(client.iterate("mxwodetail", page_size=1, max_pages=10, identity_field="wonum"))


if __name__ == "__main__":
    unittest.main()
