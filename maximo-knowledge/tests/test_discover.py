import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.discover import (
    Config,
    DiscoveryError,
    ReadOnlyClient,
    READ_ONLY_METHODS,
    business_fields,
    describe_object_structure,
    discover_oslc,
    discover_oas,
    enumerate_object_structures,
    is_internal_field,
    minimal_object_query,
    object_structure_record,
    operation_entries,
    oslc_members,
    oslc_pagination_info,
    parse_document,
    parse_object_structure_catalog,
    response_structure,
    sanitize,
    select_entries,
    validate_endpoint_record,
    validate_object_structure_record,
)


OAS = {
    "openapi": "3.0.0",
    "info": {"title": "Maximo", "version": "1"},
    "paths": {
        "/oslc/os/asset": {
            "get": {
                "tags": ["asset"],
                "parameters": [{"name": "oslc.pageSize", "in": "query", "schema": {"type": "integer"}}],
                "responses": {"200": {"content": {"application/json": {"schema": {"type": "object", "properties": {"assetnum": {"type": "string"}, "email": {"type": "string"}}}}}}},
            },
            "post": {"tags": ["asset"], "responses": {"201": {}}},
        },
        "/oslc/os/workorder/{wonum}": {
            "get": {
                "tags": ["workorder"],
                "parameters": [{"name": "wonum", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"schema": {"type": "object", "properties": {"wonum": {"type": "string"}}}}},
            }
        },
    },
}


class DiscoverTests(unittest.TestCase):
    def test_only_read_methods_are_extracted(self):
        entries = operation_entries(OAS)
        self.assertEqual({entry["method"] for entry in entries}, {"GET"})
        self.assertEqual(READ_ONLY_METHODS, {"GET", "HEAD", "OPTIONS"})

    def test_scope_and_resource_filtering(self):
        entries = operation_entries(OAS)
        self.assertEqual({entry["resource"] for entry in select_entries(entries, "reliability-core", [])}, {"asset", "workorder"})
        self.assertEqual(len(select_entries(entries, None, ["asset"])), 1)

    def test_sanitizer_removes_sensitive_and_personal_data(self):
        value = sanitize({"assetnum": "A-1", "password": "secret", "owner_email": "a@example.com", "children": [{"token": "x"}]})
        self.assertEqual(value, {"assetnum": "A-1", "children": [{}]})
        self.assertEqual(response_structure(value)["assetnum"], "str")

    def test_invalid_oas_is_rejected(self):
        with self.assertRaises(DiscoveryError):
            parse_document(b'{"paths": {}}')

    def test_local_oas_can_be_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oas.json"
            path.write_text(json.dumps(OAS), encoding="utf-8")
            parsed = parse_document(path.read_bytes())
            self.assertEqual(parsed["openapi"], "3.0.0")

    def test_local_discovery_writes_catalogs_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            selected = discover_oas(OAS, Path(directory), "reliability-core", [])
            self.assertEqual(len(selected), 2)
            catalog = json.loads((Path(directory) / "discovery/endpoints.json").read_text())
            self.assertEqual(catalog["resources"][0]["status"], "documented")
            self.assertTrue((Path(directory) / "discovery/capabilities.json").exists())

    def test_client_blocks_mutating_method(self):
        config = Config("http://example.invalid/maximo", "/oslc/oas", "none", "", "", "", 1, 0, 100)
        with self.assertRaises(DiscoveryError):
            ReadOnlyClient(config).request("POST", "/j_security_check")

    def test_client_uses_get_against_local_mock_only(self):
        requests_seen = []

        class Response:
            status = 200
            headers = {"Content-Type": "application/json"}

            def read(self, limit):
                return b'{"openapi":"3.0.0","paths":{}}'

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        class Opener:
            def open(self, request, timeout):
                requests_seen.append((request.get_method(), request.full_url, request.headers.get("Authorization")))
                return Response()

        config = Config("http://example.invalid/maximo", "/oslc/oas", "bearer", "test-token", "", "", 1, 0, 10000)
        client = ReadOnlyClient(config)
        client.opener = Opener()
        status, _, body = client.request("GET", "/oslc/oas")
        self.assertEqual(status, 200)
        self.assertIn(b"openapi", body)
        self.assertEqual(requests_seen, [("GET", "http://example.invalid/maximo/oslc/oas", "Bearer test-token")])

    def test_endpoint_validation_requires_verified_timestamp(self):
        with self.assertRaises(DiscoveryError):
            validate_endpoint_record({"resource": "asset", "endpoint": "/asset", "method": "GET", "status": "verified"})


class FakeClient:
    """A no-network stand-in for ReadOnlyClient used by OSLC discovery."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def request(self, method, path):
        method = method.upper()
        self.calls.append((method, path))
        key = (method, path)
        if key not in self.routes:
            raise DiscoveryError(f"unexpected request {method} {path}")
        status, headers, body = self.routes[key]
        return status, headers, body


class OslcDiscoveryTests(unittest.TestCase):
    def test_member_extraction_supports_common_shapes(self):
        self.assertEqual(len(oslc_members({"_member": [{"a": 1}]})), 1)
        self.assertEqual(len(oslc_members({"member": [{"b": 2}]})), 1)
        self.assertEqual(len(oslc_members([{"c": 3}])), 1)
        self.assertEqual(oslc_members({"oslc:responseInfo": {}}), [])
        self.assertEqual(oslc_members({"_member": {"d": 4}}), [{"d": 4}])

    def test_business_fields_skip_internal_namespaces(self):
        self.assertEqual(
            business_fields({"assetnum": "A1", "_rowstamp": "1", "oslc:x": 1, "rdf:y": 2}),
            ["assetnum"],
        )
        self.assertEqual(business_fields([{"wonum": "W1", "_id": 1}]), ["wonum"])

    def test_internal_field_detection(self):
        self.assertTrue(is_internal_field("_rowstamp"))
        self.assertTrue(is_internal_field("oslc:name"))
        self.assertTrue(is_internal_field(""))
        self.assertFalse(is_internal_field("assetnum"))

    def test_pagination_info_reads_responseinfo(self):
        info = oslc_pagination_info(
            {"oslc:responseInfo": {"oslc:totalCount": 42, "oslc:nextPage": "u"}, "oslc:prevPage": None}
        )
        self.assertEqual(info, {"total_count": 42, "next_page": True, "prev_page": False})

    def test_catalog_parser_extracts_names_preserving_order(self):
        payload = {"_member": [{"oslc:name": "MXASSET"}, {"name": "MXWODETAIL"}, {"oslc:label": "MXASSET"}]}
        self.assertEqual(parse_object_structure_catalog(payload), ["MXASSET", "MXWODETAIL"])

    def test_catalog_parser_handles_service_provider_shape(self):
        # OSLC Service Provider Catalog: members under oslc:serviceProvider, names in dcterms:title
        payload = {
            "oslc:responseInfo": {"oslc:totalCount": 2},
            "oslc:serviceProvider": [
                {"dcterms:title": "MXASSET"},
                {"dcterms:title": "MXWODETAIL"},
            ],
        }
        self.assertEqual(parse_object_structure_catalog(payload), ["MXASSET", "MXWODETAIL"])

    def test_enumerate_falls_back_to_seed_when_catalog_empty(self):
        client = FakeClient({("GET", "/oslc/os"): (200, {}, b'{"oslc:responseInfo":{}}')})
        result = enumerate_object_structures(client, "/oslc/os")
        self.assertEqual(result["source"], "seed-fallback")
        self.assertTrue(result["object_structures"])
        self.assertTrue(all(i["status"] == "documented" for i in result["object_structures"]))
        self.assertIn("catalog returned no member names", result["notes"][0])

    def test_enumerate_falls_back_to_seed_on_http_error(self):
        client = FakeClient({("GET", "/oslc/os"): (401, {}, b'')})
        result = enumerate_object_structures(client, "/oslc/os")
        self.assertEqual(result["source"], "seed-fallback")
        self.assertTrue(result["object_structures"])
        self.assertIn("HTTP 401", result["notes"][0])

    def test_enumerate_falls_back_when_request_raises(self):
        class BrokenClient:
            def request(self, method, path):
                raise DiscoveryError("boom")

        result = enumerate_object_structures(BrokenClient(), "/oslc/os")
        self.assertEqual(result["source"], "seed-fallback")
        self.assertIn("catalog GET failed", result["notes"][0])

    def test_enumerate_uses_live_catalog_and_marks_verified(self):
        body = b'{"_member":[{"oslc:name":"MXASSET"},{"oslc:name":"MXWODETAIL"},{"oslc:name":"CUSTOMOS"}]}'
        client = FakeClient({("GET", "/oslc/os"): (200, {}, body)})
        result = enumerate_object_structures(client, "/oslc/os")
        self.assertEqual(result["source"], "oslc-catalog")
        names = [i["name"] for i in result["object_structures"]]
        self.assertEqual(names, ["MXASSET", "MXWODETAIL", "CUSTOMOS"])
        statuses = [i["status"] for i in result["object_structures"]]
        self.assertTrue(all(s == "verified" for s in statuses))
        self.assertEqual(result["object_structures"][2]["resource"], "customos")

    def test_describe_builds_verified_record_with_fields_and_sample(self):
        body = b'{"oslc:responseInfo":{"oslc:totalCount":7,"oslc:nextPage":"u"},"_member":[{"assetnum":"A1","description":"pump","_rowstamp":"9"}]}'
        path = minimal_object_query("MXASSET")
        client = FakeClient({("GET", path): (200, {}, body)})
        record = describe_object_structure(client, "MXASSET", "asset")
        self.assertEqual(record["status"], "verified")
        self.assertEqual(record["access"], "http_200")
        self.assertIn("assetnum", record["important_fields"])
        self.assertIn("assetnum", record["field_candidates"])
        self.assertEqual(record["sample"]["assetnum"], "A1")
        self.assertEqual(record["pagination"]["total_count"], 7)
        self.assertEqual(record["endpoint"], path)
        self.assertIsNone(record["primary_key"])

    def test_describe_marks_forbidden_on_403(self):
        path = minimal_object_query("MXASSET")
        client = FakeClient({("GET", path): (403, {}, b'')})
        record = describe_object_structure(client, "MXASSET", "asset")
        self.assertEqual(record["status"], "forbidden")
        self.assertEqual(record["access"], "http_403")
        self.assertIsNone(record["verified_at"])

    def test_describe_stays_documented_on_unknown_status(self):
        path = minimal_object_query("MXASSET")
        client = FakeClient({("GET", path): (500, {}, b'oops')})
        record = describe_object_structure(client, "MXASSET", "asset")
        self.assertEqual(record["status"], "documented")
        self.assertEqual(record["access"], "http_500")

    def test_describe_redacts_sample_fields(self):
        body = b'{"_member":[{"assetnum":"A1","password":"secret","owner_email":"a@example.com"}]}'
        path = minimal_object_query("MXASSET")
        client = FakeClient({("GET", path): (200, {}, body)})
        record = describe_object_structure(client, "MXASSET", "asset")
        self.assertNotIn("password", record["sample"])
        self.assertNotIn("owner_email", record["sample"])
        self.assertIn("assetnum", record["important_fields"])

    def test_validate_object_record_rejects_sensitive_keys(self):
        record = object_structure_record("MXASSET", "asset", status="documented")
        record["token"] = "x"
        with self.assertRaises(DiscoveryError):
            validate_object_structure_record(record)

    def test_validate_object_record_requires_verified_at(self):
        record = object_structure_record("MXASSET", "asset", status="verified")
        with self.assertRaises(DiscoveryError):
            validate_object_structure_record(record)

    def test_discover_oslc_writes_catalogs_and_per_object_files(self):
        catalog_body = b'{"_member":[{"oslc:name":"MXASSET"}]}'
        os_body = b'{"_member":[{"assetnum":"A1","description":"pump"}]}'
        client = FakeClient(
            {
                ("GET", "/oslc/"): (200, {}, catalog_body),
                ("GET", minimal_object_query("MXASSET")): (200, {}, os_body),
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            discovered = discover_oslc(client, Path(directory), None, [])
            self.assertEqual(len(discovered), 1)
            catalog = json.loads((Path(directory) / "discovery/object-structures.json").read_text())
            self.assertEqual(catalog["source"], "oslc-catalog")
            self.assertEqual(catalog["object_structures"][0]["name"], "MXASSET")
            obj = json.loads((Path(directory) / "discovery/objects/mxasset.json").read_text())
            self.assertEqual(obj["status"], "verified")
            self.assertIn("assetnum", obj["important_fields"])

    def test_discover_oslc_respects_scope_filter(self):
        catalog_body = b'{"_member":[{"oslc:name":"MXASSET"},{"oslc:name":"MXJOBPLAN"}]}'
        asset_body = b'{"_member":[{"assetnum":"A1"}]}'
        jobplan_body = b'{"_member":[{"jpnum":"J1"}]}'
        client = FakeClient(
            {
                ("GET", "/oslc/"): (200, {}, catalog_body),
                ("GET", minimal_object_query("MXASSET")): (200, {}, asset_body),
                ("GET", minimal_object_query("MXJOBPLAN")): (200, {}, jobplan_body),
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            discovered = discover_oslc(client, Path(directory), "reliability-core", [])
            self.assertEqual({d["resource"] for d in discovered}, {"asset"})


class CliGuardTests(unittest.TestCase):
    def setUp(self):
        # Prevent the real .env from leaking credentials into the test process.
        self._overrides = {
            "MAXIMO_BASE_URL": "http://example.invalid/maximo",
            "MAXIMO_AUTH_MODE": "none",
            "MAXIMO_TOKEN": "",
            "MAXIMO_USERNAME": "",
            "MAXIMO_PASSWORD": "",
        }
        self._saved = {key: os.environ.get(key) for key in self._overrides}
        os.environ.update(self._overrides)

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_enumerate_requires_execute_flag(self):
        from scripts.discover import main

        with self.assertRaises(DiscoveryError):
            main(["--enumerate-oslc"])


if __name__ == "__main__":
    unittest.main()
