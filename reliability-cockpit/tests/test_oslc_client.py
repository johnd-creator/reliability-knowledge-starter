"""Unit tests for OSLC client member extraction, pagination, and size cap.

The verified Maximo response shape comes from maximo-knowledge/CONTEXT.md:
records live under ``_member`` and the next-page link under
``oslc:responseInfo.oslc:nextPage``.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from src.adapters.maximo.oslc_client import (
    OslcClient,
    OslcError,
    _extract_members,
    _next_page_url,
)


class MemberExtractionTest(unittest.TestCase):
    def test_primary_member_shape(self):
        payload = {"oslc:responseInfo": {"oslc:totalCount": 1}, "_member": [{"assetnum": "A1"}]}
        self.assertEqual(_extract_members(payload), [{"assetnum": "A1"}])

    def test_generic_member_shape(self):
        self.assertEqual(_extract_members({"member": [{"a": 1}]}), [{"a": 1}])

    def test_bare_list(self):
        self.assertEqual(_extract_members([{"a": 1}, {"b": 2}]), [{"a": 1}, {"b": 2}])

    def test_empty_payload(self):
        self.assertEqual(_extract_members({"oslc:responseInfo": {}}), [])

    def test_single_member_dict_is_wrapped(self):
        self.assertEqual(_extract_members({"_member": {"d": 4}}), [{"d": 4}])


class NextPageTest(unittest.TestCase):
    def test_nested_under_response_info(self):
        payload = {"oslc:responseInfo": {"oslc:nextPage": "http://x/oslc/os/mxasset?p=2"}, "_member": []}
        self.assertEqual(_next_page_url(payload), "http://x/oslc/os/mxasset?p=2")

    def test_top_level_fallback(self):
        self.assertEqual(_next_page_url({"nextPage": "http://x?p=2"}), "http://x?p=2")

    def test_no_next_page(self):
        self.assertIsNone(_next_page_url({"oslc:responseInfo": {"oslc:totalCount": 0}, "_member": []}))


class SizeCapTest(unittest.TestCase):
    def _client(self, max_bytes=10):
        client = OslcClient.__new__(OslcClient)
        client._config = MagicMock()
        client._config.rate_limit_seconds = 0
        client._config.timeout_seconds = 5
        client._config.max_response_bytes = max_bytes
        client._last_request = 0.0
        client._cookie = None
        return client

    def test_oversized_success_response_raises(self):
        client = self._client(max_bytes=8)
        resp = MagicMock()
        resp.content = b"x" * 16
        resp.status_code = 200
        client._session = MagicMock()
        client._session.request.return_value = resp
        with self.assertRaises(OslcError):
            client.request("GET", "/oslc/os/mxasset")

    def test_within_cap_returns_response(self):
        client = self._client(max_bytes=100)
        resp = MagicMock()
        resp.content = b"small"
        resp.status_code = 200
        client._session = MagicMock()
        client._session.request.return_value = resp
        self.assertIs(client.request("GET", "/oslc/os/mxasset"), resp)


if __name__ == "__main__":
    unittest.main()
