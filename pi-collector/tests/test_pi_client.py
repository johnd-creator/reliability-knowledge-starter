"""Unit tests for PiClient safety + payload parsing — no network required."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch
import os

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
        self.assertNotIn("PI Point not found", str(ctx.exception))


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

    def test_quality_and_digital_state_are_preserved(self):
        payload = {
            "Timestamp": "2026-08-14T04:30:00Z",
            "Value": {"Name": "Off", "Value": 0},
            "ValueType": "DigitalState",
            "UnitsAbbreviation": "state",
            "Good": False,
            "Questionable": True,
            "Substituted": False,
            "Annotated": True,
        }
        snap = pi_client.extract_snapshot(payload, "digital-attr")
        self.assertIsNone(snap.value)
        self.assertEqual(snap.value_type, "DigitalState")
        self.assertEqual(snap.units, "state")
        self.assertFalse(snap.value_good)
        self.assertTrue(snap.value_questionable)
        self.assertFalse(snap.value_substituted)
        self.assertTrue(snap.value_annotated)

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

    def test_quality_units_and_type_are_preserved(self):
        points = pi_client.extract_interpolated({
            "UnitsAbbreviation": "bar",
            "Items": [{
                "Timestamp": "2026-08-14T04:00:00Z",
                "Value": 4.2,
                "ValueType": "Double",
                "Good": True,
                "Questionable": False,
                "Substituted": True,
                "Annotated": False,
            }],
        }, "test-attr")
        point = points[0]
        self.assertEqual(point.units, "bar")
        self.assertEqual(point.value_type, "Double")
        self.assertTrue(point.value_good)
        self.assertFalse(point.value_questionable)
        self.assertTrue(point.value_substituted)
        self.assertFalse(point.value_annotated)

    def test_missing_items_is_an_explicit_shape_error(self):
        with self.assertRaises(PiClientError):
            pi_client.extract_interpolated({}, "test-attr")

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

    def test_partial_basic_credentials_are_rejected(self):
        with self.assertRaisesRegex(PiClientError, "both PI_USERNAME and PI_PASSWORD"):
            PiClient(
                PiApiConfig(base_url="https://x", username="operator", rate_limit_seconds=0)
            ).request("GET", "/")

    def test_runtime_base_url_is_required_and_tls_defaults_on(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = PiApiConfig.from_environment()
        self.assertIsNone(cfg.base_url)
        self.assertTrue(cfg.verify_tls)


class OriginGuardTest(unittest.TestCase):
    class Response:
        status_code = 200
        content = b"{}"

        def json(self):
            return {}

    class Session:
        def __init__(self):
            self.calls = []

        def request(self, method, url, **kwargs):
            self.calls.append((method, url, kwargs))
            return OriginGuardTest.Response()

    def test_same_origin_absolute_url_is_allowed_with_runtime_auth_and_tls(self):
        session = self.Session()
        cfg = PiApiConfig(
            base_url="https://pi.example.test/piwebapi",
            username="operator",
            password="runtime-only",
            rate_limit_seconds=0,
        )
        PiClient(cfg, session=session).request(
            "GET", "https://pi.example.test/other-resource"
        )
        method, url, kwargs = session.calls[0]
        self.assertEqual(method, "GET")
        self.assertEqual(url, "https://pi.example.test/other-resource")
        self.assertEqual(kwargs["auth"], ("operator", "runtime-only"))
        self.assertTrue(kwargs["verify"])

    def test_foreign_absolute_url_is_rejected_before_request(self):
        session = self.Session()
        cfg = PiApiConfig(base_url="https://pi.example.test/piwebapi", rate_limit_seconds=0)
        with self.assertRaisesRegex(PiClientError, "foreign origin"):
            PiClient(cfg, session=session).request("GET", "https://evil.example.test/value")
        self.assertEqual(session.calls, [])

    def test_missing_base_url_fails_before_request(self):
        session = self.Session()
        with self.assertRaisesRegex(PiClientError, "base URL is required"):
            PiClient(PiApiConfig(rate_limit_seconds=0), session=session).request("GET", "/")
        self.assertEqual(session.calls, [])

    def test_response_cap_and_invalid_json_are_controlled_errors(self):
        class OversizedResponse:
            status_code = 200
            content = b"12345"

            def json(self):
                return {}

        class InvalidJsonResponse:
            status_code = 200
            content = b"not-json"

            def json(self):
                raise ValueError("invalid")

        class Session:
            def __init__(self, response):
                self.response = response

            def request(self, method, url, **kwargs):
                return self.response

        oversized = PiClient(
            PiApiConfig(base_url="https://pi.example.test", max_response_bytes=4, rate_limit_seconds=0),
            session=Session(OversizedResponse()),
        )
        with self.assertRaisesRegex(PiClientError, "oversized body"):
            oversized.request("GET", "/value")

        invalid = PiClient(
            PiApiConfig(base_url="https://pi.example.test", rate_limit_seconds=0),
            session=Session(InvalidJsonResponse()),
        )
        with self.assertRaisesRegex(PiClientError, "invalid JSON"):
            invalid.get_json("/value")

    def test_foreign_pagination_link_is_rejected(self):
        class FullPageResponse:
            status_code = 200
            content = b"{}"

            def json(self):
                return {
                    "Items": [{"Timestamp": str(i), "Value": 1.0} for i in range(2)],
                    "Links": {"Next": "https://evil.example.test/recorded?startTime=next"},
                }

        class Session:
            def request(self, method, url, **kwargs):
                return FullPageResponse()

        client = PiClient(
            PiApiConfig(base_url="https://pi.example.test/piwebapi", rate_limit_seconds=0),
            session=Session(),
        )
        with self.assertRaisesRegex(PiClientError, "foreign origin"):
            list(client.iter_recorded("A", start_time="start", end_time="end", max_count=2))


class AfOperationTest(unittest.TestCase):
    class Response:
        status_code = 200
        content = b"{}"

        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    class Session:
        def __init__(self, payloads):
            self.payloads = iter(payloads)
            self.calls = []

        def request(self, method, url, **kwargs):
            self.calls.append((method, url, kwargs))
            return AfOperationTest.Response(next(self.payloads))

    def test_af_chain_uses_links_and_bounds_operations(self):
        metadata = {
            "WebId": "A",
            "DefaultUnitsName": "degC",
            "Links": {
                "Value": "https://pi.example.test/piwebapi/streams/S/value",
                "RecordedData": "https://pi.example.test/piwebapi/streams/S/recorded",
            },
        }
        session = self.Session([
            {"Name": "Element", "WebId": "E"},
            {"Items": [{"Name": "Attr", "WebId": "A"}]},
            metadata,
            {"Value": 12.5, "Timestamp": "2026-08-14T04:00:00Z", "Good": True},
            {"Items": [{"Value": 12.5, "Timestamp": "2026-08-14T04:00:00Z", "Good": True}]},
        ])
        client = PiClient(
            PiApiConfig(base_url="https://pi.example.test/piwebapi", rate_limit_seconds=0),
            session=session,
        )
        self.assertEqual(client.get_af_element("E")["WebId"], "E")
        self.assertEqual(len(client.list_af_attributes("E", max_count=1000)), 1)
        self.assertEqual(client.get_af_attribute("A")["WebId"], "A")
        self.assertEqual(client.get_af_attribute_value(metadata)["Value"], 12.5)
        self.assertEqual(len(client.get_af_attribute_recorded(
            metadata, start_time="start", end_time="end", max_count=1000
        )["Items"]), 1)
        self.assertEqual(session.calls[1][2]["params"]["maxCount"], "100")
        self.assertEqual(session.calls[4][2]["params"]["maxCount"], "20")


if __name__ == "__main__":
    unittest.main()
