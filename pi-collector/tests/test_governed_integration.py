"""End-to-end offline source-boundary tests. All source requests are synthetic."""
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
import requests

from src.adapters.pi.client import PiClient, PiClientError, extract_snapshot, extract_recorded
from src.config import PiApiConfig
from src.domain.governed import GovernedTargetError
from src.services.governed_source import GovernedSourceBoundary
from test_governed_source import target

ROOT = "https://pi.example.test/piwebapi"
START = "2026-10-07T00:00:00Z"
END = "2026-10-07T01:00:00Z"
E, D, S, A = "AF_ELEMENT_TEST", "AF_DATABASE_TEST", "AF_SERVER_TEST", "A"


def sample(value=12.5):
    return {"Value": value, "Timestamp": START, "UnitsAbbreviation": "bar", "Good": True,
            "Questionable": False, "Substituted": True, "Annotated": False}


def fixtures():
    attribute = {"WebId": A, "DefaultUnitsName": "bar", "Links": {
        "Element": ROOT + "/elements/" + E,
        "Value": ROOT + "/streams/A/value", "RecordedData": ROOT + "/streams/A/recorded"}}
    return {
        "/elements/" + E: {"WebId": E, "Links": {"Database": ROOT + "/assetdatabases/" + D}},
        "/assetdatabases/" + D: {"WebId": D, "Links": {"AssetServer": ROOT + "/assetservers/" + S}},
        "/elements/" + E + "/attributes": {"Items": [attribute]},
        "/attributes/A": attribute,
        "/streams/A/value": sample(),
        "/streams/A/recorded": {"Items": [sample()]},
    }


class Session:
    def __init__(self, data=None, status=200):
        self.data = data if data is not None else fixtures()
        self.status = status
        self.calls = []
        self.responses = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = requests.Response()
        response.status_code = self.status
        response.url = url
        payload = self.data[url.removeprefix(ROOT)]
        response._content = json.dumps(payload).encode()
        response._content_consumed = True
        self.responses.append(response)
        return response


class GovernedIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.sleep = patch("src.adapters.pi.client.time.sleep").start()
        self.addCleanup(patch.stopall)
        self.session = Session()
        self.client = PiClient(PiApiConfig(base_url=ROOT, username="test-user", password="test-only"), self.session)
        self.boundary = GovernedSourceBoundary(self.client)

    def test_all_operations_preserve_lineage_value_quality_and_limits(self):
        self.assertEqual(self.boundary.get_element(target())["WebId"], E)
        self.assertEqual(self.boundary.list_attributes(target(), max_count=1000)[0]["WebId"], A)
        self.assertEqual(self.boundary.get_attribute(target(), A)["WebId"], A)
        snap = self.boundary.get_snapshot(target(), A)
        self.assertEqual((snap.value, snap.source_value, snap.units), (12.5, 12.5, "bar"))
        self.assertEqual((snap.value_good, snap.value_questionable, snap.value_substituted, snap.value_annotated), (True, False, True, False))
        points = self.boundary.get_recorded(target(), A, start_time=START, end_time=END, max_count=1000)
        self.assertEqual(points[0].source_value, 12.5)
        self.assertEqual(self.session.calls[-1][2]["params"]["maxCount"], "20")
        self.assertTrue(all(call[0] == "GET" and call[2]["verify"] and not call[2]["allow_redirects"] for call in self.session.calls))
        self.assertTrue(self.sleep.called)

    def test_every_operation_rejects_unusable_states_before_source(self):
        operations = [lambda t: self.boundary.get_element(t), lambda t: self.boundary.list_attributes(t),
                      lambda t: self.boundary.get_attribute(t, A), lambda t: self.boundary.get_snapshot(t, A),
                      lambda t: self.boundary.get_recorded(t, A, start_time=START, end_time=END)]
        for state in ("PROPOSED", "RETIRED", "UNMAPPED", "AMBIGUOUS", "MAPPED"):
            for operation in operations:
                with self.subTest(state=state, operation=operation):
                    with self.assertRaises(GovernedTargetError):
                        operation(target(mapping_status=state))
        self.assertEqual(self.session.calls, [])

    def test_missing_null_nonstring_identifiers_fail_closed(self):
        for field in ("canonical_asset_id", "af_server_ref", "af_database_ref", "af_element_ref", "pi_source_id", "mapping_role", "mapping_status"):
            for value in (None, 0, "", " ", " spaced "):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(GovernedTargetError):
                        self.boundary.get_element(target(**{field: value}))
        self.assertEqual(self.session.calls, [])

    def test_wrong_database_and_server_cannot_reach_signal(self):
        for field in ("af_database_ref", "af_server_ref"):
            with self.subTest(field=field):
                self.session.calls.clear()
                with self.assertRaisesRegex(PiClientError, "relationship"):
                    self.boundary.get_snapshot(target(**{field: "WRONG"}), A)
                self.assertFalse(any("/streams/" in call[1] for call in self.session.calls))

    def test_unrelated_attribute_is_not_requested(self):
        with self.assertRaisesRegex(PiClientError, "outside bounded"):
            self.boundary.get_snapshot(target(), "OUTSIDER")
        self.assertFalse(any("OUTSIDER" in call[1] for call in self.session.calls))

    def test_changed_attribute_identity_or_parent_fails_before_value(self):
        for changes in ({"WebId": "WRONG"}, {"Links": {"Element": ROOT + "/elements/WRONG"}}):
            data = fixtures()
            data["/attributes/A"] = {**data["/attributes/A"], **changes}
            session = Session(data)
            boundary = GovernedSourceBoundary(PiClient(PiApiConfig(base_url=ROOT), session))
            with self.assertRaises(PiClientError):
                boundary.get_snapshot(target(), A)
            self.assertFalse(any("/streams/" in call[1] for call in session.calls))

    def test_foreign_value_link_never_receives_credentials(self):
        self.session.data["/attributes/A"]["Links"]["Value"] = "https://foreign.test/stream"
        with self.assertRaisesRegex(PiClientError, "foreign origin"):
            self.boundary.get_snapshot(target(), A)
        self.assertTrue(all(call[1].startswith(ROOT) for call in self.session.calls))

    def test_recorded_link_cannot_override_bounded_parameters(self):
        self.session.data["/attributes/A"]["Links"]["RecordedData"] += "?maxCount=100000"
        with self.assertRaisesRegex(PiClientError, "bounded parameters"):
            self.boundary.get_recorded(target(), A, start_time=START, end_time=END)
        self.assertFalse(any("/streams/" in call[1] for call in self.session.calls))

    def test_attribute_list_missing_duplicate_or_oversized_is_rejected(self):
        for items in ([{}], [{"WebId": A}, {"WebId": A}], [{}] * 101):
            with self.subTest(items=len(items)):
                self.session.data["/elements/" + E + "/attributes"] = {"Items": items}
                with self.assertRaises(PiClientError):
                    self.boundary.list_attributes(target())

    def test_invalid_history_parameters_fail_before_request(self):
        for start, end, count in (("*-7d", END, 20), (START, "*", 20), (END, START, 20),
                                  (START, "2026-10-09T00:00:00Z", 20), (START, END, 0), (START, END, True)):
            with self.subTest(start=start, end=end, count=count):
                with self.assertRaises(PiClientError):
                    self.boundary.get_recorded(target(), A, start_time=start, end_time=end, max_count=count)
        self.assertEqual(self.session.calls, [])

    def test_recorded_limit_and_timestamp_errors_are_not_hidden(self):
        for items in ([sample()] * 21, [{"Value": 1}], [{**sample(), "Timestamp": "2026-10-06T00:00:00Z"}], [{**sample(), "Timestamp": "invalid"}]):
            with self.subTest(items=len(items)):
                self.session.data["/streams/A/recorded"] = {"Items": items}
                with self.assertRaises(PiClientError):
                    self.boundary.get_recorded(target(), A, start_time=START, end_time=END)

    def test_governed_snapshot_requires_aware_timestamp(self):
        for timestamp in (None, "wrong", "2026-10-07T00:00:00"):
            self.session.data["/streams/A/value"] = {**sample(), "Timestamp": timestamp}
            with self.assertRaises(PiClientError):
                self.boundary.get_snapshot(target(), A)

    def test_recorded_falls_back_to_af_units(self):
        self.session.data["/streams/A/recorded"] = {"Items": [{"Value": 1, "Timestamp": START}]}
        self.assertEqual(self.boundary.get_recorded(target(), A, start_time=START, end_time=END)[0].units, "bar")


class SourceSafetyTest(unittest.TestCase):
    def setUp(self):
        patch("src.adapters.pi.client.time.sleep").start()
        self.addCleanup(patch.stopall)

    def test_unsafe_links_and_bases_fail_without_request(self):
        for base, link in ((None, "/value"), (123, "/value"), ("ftp://pi.test", "/value"),
                           ("https://u:p@pi.test", "/value"), (ROOT + "?q=x", "/value"),
                           (ROOT, "//foreign.test/value"), (ROOT, "https://foreign.test/value"),
                           (ROOT, "http://pi.example.test/piwebapi/value"),
                           (ROOT, "https://pi.example.test:444/piwebapi/value"),
                           (ROOT, "https://pi.example.test/outside"), (ROOT, "/../outside"),
                           (ROOT, "/%2e%2e/outside"), (ROOT, "/%0a/value"), (ROOT, "https://u:p@pi.example.test/piwebapi/value")):
            session = Session()
            with self.subTest(base=base, link=link):
                with self.assertRaises(PiClientError):
                    PiClient(PiApiConfig(base_url=base), session).get_json(link)
                self.assertEqual(session.calls, [])

    def test_redirects_errors_and_json_shapes_fail_safely(self):
        for status in (302, 401, 403, 410, 500):
            session = Session({"/value": {"Errors": ["DO NOT EXPOSE"]}}, status=status)
            with self.subTest(status=status):
                with self.assertRaises(PiClientError) as context:
                    PiClient(PiApiConfig(base_url=ROOT), session).get_json("/value")
                self.assertNotIn("DO NOT EXPOSE", str(context.exception))
                self.assertFalse(session.calls[0][2]["allow_redirects"])
        with self.assertRaises(PiClientError):
            PiClient(PiApiConfig(base_url=ROOT), Session({"/value": []})).get_json("/value")

    def test_streamed_response_cap_stops_download_and_closes(self):
        class Response:
            status_code = 200
            closed = False
            seen = 0
            def iter_content(self, chunk_size):
                for chunk in (b"123", b"456", b"789"):
                    self.seen += 1
                    yield chunk
            def close(self): self.closed = True
        response = Response()
        session = Session()
        session.request = lambda *args, **kwargs: response
        with self.assertRaisesRegex(PiClientError, "oversized body"):
            PiClient(PiApiConfig(base_url=ROOT, max_response_bytes=4), session).request("GET", "/value")
        self.assertTrue(response.closed)
        self.assertEqual(response.seen, 2)

    def test_request_rate_floor_and_failure_backoff(self):
        session = Session({"/value": {}})
        client = PiClient(PiApiConfig(base_url=ROOT, rate_limit_seconds=0), session)
        with patch("src.adapters.pi.client.time.monotonic", return_value=100), patch("src.adapters.pi.client.time.sleep") as sleep:
            client.get_json("/value")
            client.get_json("/value")
        sleep.assert_called_once_with(1.0)

    def test_api_root_relative_link_and_explicit_default_port_are_accepted(self):
        client = PiClient(PiApiConfig(base_url=ROOT), Session({"/value": {}}))
        self.assertEqual(client.resolve_source_link("/piwebapi/streams/A/value"), ROOT + "/streams/A/value")
        self.assertEqual(client.resolve_source_link("https://pi.example.test:443/piwebapi/value"), "https://pi.example.test:443/piwebapi/value")

    def test_tls_transport_and_timeout_errors_are_sanitized(self):
        for error in (requests.exceptions.SSLError("SECRET"), requests.exceptions.Timeout("SECRET"), requests.exceptions.ConnectionError("SECRET")):
            session = Session()
            session.request = lambda *args, **kwargs: (_ for _ in ()).throw(error)
            with self.assertRaises(PiClientError) as context:
                PiClient(PiApiConfig(base_url=ROOT), session).get_json("/value")
            self.assertNotIn("SECRET", str(context.exception))


class SourceValueTest(unittest.TestCase):
    def test_all_source_types_are_preserved_without_zero_coercion(self):
        for value, kind in ((None, "NULL"), (False, "BOOLEAN"), (True, "BOOLEAN"), ("0", "TEXT"),
                            ("OFF", "TEXT"), ({"Name": "Stopped", "Value": 0, "IsSystem": False}, "DIGITAL_STATE")):
            with self.subTest(kind=kind, value=value):
                snapshot = extract_snapshot(sample(value), A)
                self.assertIsNone(snapshot.value)
                self.assertEqual(snapshot.source_value, value)
                self.assertEqual(snapshot.value_type, kind)
                point = extract_recorded({"Items": [sample(value)]}, A)[0]
                self.assertEqual(point.source_value, value)
                self.assertIsNone(point.value)

    def test_bad_quality_is_preserved_and_unknown_flags_are_null(self):
        snapshot = extract_snapshot({**sample(), "Good": False, "Questionable": True, "Substituted": None, "Annotated": "unknown"}, A)
        self.assertFalse(snapshot.value_good)
        self.assertTrue(snapshot.value_questionable)
        self.assertIsNone(snapshot.value_substituted)
        self.assertIsNone(snapshot.value_annotated)

    def test_malformed_units_or_type_are_rejected(self):
        for field, value in (("UnitsAbbreviation", ["bar"]), ("Units", 9), ("Units", "x" * 41), ("ValueType", {"Type": "Double"}), ("ValueType", "x" * 41)):
            with self.subTest(field=field):
                payload = {"Value": 1, "Timestamp": START, field: value}
                with self.assertRaises(PiClientError): extract_snapshot(payload, A)
                with self.assertRaises(PiClientError): extract_recorded({"Items": [payload]}, A)

    def test_malformed_values_and_payloads_raise_controlled_errors(self):
        for value in (float("nan"), float("inf"), [], {}, {"Name": "X", "Value": False, "IsSystem": True}):
            with self.subTest(value=value):
                with self.assertRaises(PiClientError): extract_snapshot(sample(value), A)
        for payload in (None, [], {}):
            with self.assertRaises(PiClientError): extract_snapshot(payload, A)
        for payload in (None, [], {}, {"Items": None}, {"Items": [1]}, {"Items": [{"Timestamp": START}]}):
            with self.assertRaises(PiClientError): extract_recorded(payload, A)


if __name__ == "__main__":
    unittest.main()
