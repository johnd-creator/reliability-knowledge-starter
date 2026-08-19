"""Unit tests for PiClient safety + payload parsing — no network required."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.adapters.pi import client as pi_client
from src.adapters.pi.client import PiClient, PiClientError, PiApiConfig


class GoneErrorTest(unittest.TestCase):
    def test_410_raises_gone_error(self):
        class Fake410Response:
            status_code = 410
            content = b"{}"

            def json(self):
                return {"Errors": ["PI Point not found '\\\\PI1\\X.Y'."]}

        class FakeSession:
            def request(self, method, url, **kwargs):
                return Fake410Response()

        cfg = PiApiConfig(base_url="https://example/piwebapi", rate_limit_seconds=0)
        c = PiClient(cfg, session=FakeSession())
        with self.assertRaises(PiClientError) as ctx:
            c.get_json("/streams/abc/value")
        self.assertIn("410", str(ctx.exception))
        self.assertIn("PI Point not found", str(ctx.exception))


class ReadOnlyEnforcementTest(unittest.TestCase):
    def test_only_get_head_options_allowed(self):
        for ok in ("GET", "HEAD", "OPTIONS", "get", "Head"):
            self.assertIn(ok.upper(), pi_client.READ_ONLY_METHODS)

    def test_blocked_methods_raise(self):
        cfg = PiApiConfig(base_url="https://example/piwebapi", rate_limit_seconds=0)
        c = PiClient(cfg)
        for bad in ("POST", "PUT", "PATCH", "DELETE"):
            with self.assertRaises(PiClientError):
                c.request(bad, "/")


class SnapshotParseTest(unittest.TestCase):
    def test_numeric_value_parsed(self):
        payload = {
            "Timestamp": "2026-08-14T04:30:00Z",
            "Value": 77.81,
            "UnitsAbbreviation": "deg C",
            "Good": True,
            "IsSubstituted": None,
        }
        snap = pi_client.extract_snapshot(payload, "test-attr", units="degC")
        self.assertEqual(snap.attribute_id, "test-attr")
        self.assertAlmostEqual(snap.value, 77.81)
        self.assertTrue(snap.value_good)
        self.assertEqual(snap.units, "deg C")
        self.assertIsNotNone(snap.source_timestamp)

    def test_none_value_becomes_none(self):
        payload = {"Timestamp": "2026-08-14T04:30:00Z", "Value": None, "Good": False}
        snap = pi_client.extract_snapshot(payload, "test-attr")
        self.assertIsNone(snap.value)
        self.assertFalse(snap.value_good)

    def test_string_good_coerced(self):
        payload = {"Timestamp": "2026-08-14T04:30:00Z", "Value": 50.0, "Good": "true"}
        snap = pi_client.extract_snapshot(payload, "test-attr")
        self.assertTrue(snap.value_good)


class InterpolatedParseTest(unittest.TestCase):
    def test_items_parsed(self):
        payload = {
            "Items": [
                {"Timestamp": "2026-08-14T03:00:00Z", "Value": 77.1, "Good": True},
                {"Timestamp": "2026-08-14T04:00:00Z", "Value": 77.5, "Good": True},
                {"Timestamp": "2026-08-14T05:00:00Z", "Value": None, "Good": False},
            ]
        }
        points = pi_client.extract_interpolated(payload, "test-attr")
        self.assertEqual(len(points), 3)
        self.assertAlmostEqual(points[0].value, 77.1)
        self.assertIsNone(points[2].value)

    def test_empty_items(self):
        points = pi_client.extract_interpolated({"Items": []}, "test-attr")
        self.assertEqual(len(points), 0)

    def test_missing_timestamp_skipped(self):
        payload = {"Items": [{"Value": 50.0, "Good": True}]}
        points = pi_client.extract_interpolated(payload, "test-attr")
        self.assertEqual(len(points), 0)


class AuthConfigTest(unittest.TestCase):
    def test_basic_auth_kwargs(self):
        cfg = PiApiConfig(base_url="https://x", username="user", password="pw")
        self.assertEqual(cfg.auth_kwargs(), {"auth": ("user", "pw")})

    def test_bearer_auth_kwargs(self):
        cfg = PiApiConfig(base_url="https://x", token="abc")
        self.assertEqual(cfg.auth_kwargs(), {"headers": {"Authorization": "Bearer abc"}})

    def test_no_auth_empty(self):
        cfg = PiApiConfig(base_url="https://x")
        self.assertEqual(cfg.auth_kwargs(), {})


if __name__ == "__main__":
    unittest.main()
