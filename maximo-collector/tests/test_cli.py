"""CLI diagnostics and per-resource failure isolation tests."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.cli import _safe_error_metadata, cmd_diagnose, cmd_sync, parse_args


class DiagnoseSelectTest(unittest.TestCase):
    def test_master_data_diagnose_forwards_minimal_select(self):
        instances = []

        class FakeClient:
            def __init__(self, *_args, **_kwargs):
                self.calls = []
                instances.append(self)

            def iterate(self, object_structure, **kwargs):
                self.calls.append((object_structure, kwargs))
                yield {field: "present" for field in kwargs["select"]}

        with patch("src.adapters.maximo.oslc_client.OslcClient", FakeClient):
            result = cmd_diagnose(SimpleNamespace())

        self.assertEqual(result, 0)
        self.assertEqual(len(instances), 1)
        calls = instances[0].calls
        self.assertEqual(calls[0][0], "mxperson")
        self.assertEqual(calls[0][1]["select"], ["personid", "displayname", "firstname", "status", "statusdate", "locationorg"])
        self.assertEqual(calls[1][1]["select"], ["itemnum", "description", "status", "site"])
        self.assertEqual(calls[2][1]["select"], ["laborcode", "personid", "status", "worksite"])


class SyncIsolationTest(unittest.TestCase):
    def test_failed_resource_does_not_block_next_resource(self):
        class FakeService:
            def __init__(self):
                self.calls = []

            def sync(self, config):
                self.calls.append(config)
                if config == "mxwodetail":
                    raise RuntimeError("upstream failure")
                return SimpleNamespace(
                    mode="full", object_structure=config, rows_seen=1,
                    upserted=1, skipped=0, errors=0, watermark=None,
                )

        service = FakeService()
        with (
            patch("src.cli.get_database", return_value=object()),
            patch("src.cli.CollectorStore", return_value=object()),
            patch("src.cli._sync_service", return_value=(service, object())),
            patch("src.api.app.sync_config_for", side_effect=lambda name: name),
        ):
            result = cmd_sync(SimpleNamespace(objects=["mxwodetail", "mxperson"]))

        self.assertEqual(result, 1)
        self.assertEqual(service.calls, ["mxwodetail", "mxperson"])


class SafeErrorMetadataTest(unittest.TestCase):
    def test_timeout_is_classified_without_error_text(self):
        error = TimeoutError("https://example.invalid/path?marker=hidden")
        metadata = _safe_error_metadata(error)
        self.assertEqual(metadata["error_category"], "READ_TIMEOUT")
        self.assertNotIn("hidden", str(metadata))


class ControlledLoadCliTest(unittest.TestCase):
    def test_only_initial_controlled_profile_is_available(self):
        args = parse_args(["mart-load", "--profile", "initial-controlled", "--dry-run"])
        self.assertTrue(args.dry_run)
        with self.assertRaises(SystemExit):
            parse_args(["mart-load", "--unlimited"])

    def test_http_error_metadata_keeps_only_sanitized_fields(self):
        response = SimpleNamespace(
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
            content=b'{"oslc:Error":{"oslc:message":"BMXAA5000E bad hidden"}}',
            json=lambda: {"oslc:Error": {"oslc:message": "BMXAA5000E bad 'hidden'"}},
        )
        error = RuntimeError("raw https://example.invalid/path")
        error.response = response
        metadata = _safe_error_metadata(error)
        self.assertEqual(metadata["error_category"], "UPSTREAM_MAXIMO_500")
        self.assertEqual(metadata["http_status"], 500)
        self.assertEqual(metadata["content_type"], "application/json")
        self.assertNotIn("hidden", str(metadata))


if __name__ == "__main__":
    unittest.main()
