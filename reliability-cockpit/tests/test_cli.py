"""CLI regression tests for local Cockpit web-access commands."""

from __future__ import annotations

import argparse
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.cli import cmd_sync, parse_args
from src.services.sync import SyncStats


class CliSyncOutputTest(unittest.TestCase):
    def test_sync_prints_resource_name_from_cockpit_stats(self):
        class FakeService:
            def __init__(self, client, store):
                self.calls = []

            def sync(self, resource):
                self.calls.append(resource)
                return SyncStats(resource=resource, rows_seen=1, upserted=1)

        class FakeClient:
            def __init__(self, base_url, timeout_seconds):
                self.base_url = base_url
                self.timeout_seconds = timeout_seconds

        class FakeConfig:
            maximo_api_base = "http://127.0.0.1:8002"
            timeout_seconds = 60

        output = StringIO()
        with (
            patch("src.cli.CollectorConfig.from_environment", return_value=FakeConfig()),
            patch("src.adapters.collector_client.CollectorClient", FakeClient),
            patch("src.cli.CockpitStore"),
            patch("src.cli.get_database"),
            patch("src.cli.SyncService", FakeService),
            redirect_stdout(output),
        ):
            result = cmd_sync(argparse.Namespace(objects=["equipment"]))

        self.assertEqual(result, 0)
        self.assertIn("equipment", output.getvalue())
        self.assertIn("seen=1", output.getvalue())


class MappingCommandParserTest(unittest.TestCase):
    def test_mapping_import_parser_is_internal_and_dry_run_aware(self):
        args = parse_args(["mapping", "import", "--file", "candidate.csv", "--dry-run"])
        self.assertEqual(args.command, "mapping")
        self.assertEqual(args.mapping_command, "import")
        self.assertEqual(args.file, "candidate.csv")
        self.assertTrue(args.dry_run)

    def test_mapping_verify_and_retire_require_explicit_actors(self):
        verify = parse_args(
            [
                "mapping",
                "verify",
                "--mapping-id",
                "mapping-1",
                "--verified-by",
                "human-operator",
                "--evidence-ref",
                "review-1",
            ]
        )
        retire = parse_args(
            [
                "mapping",
                "retire",
                "--mapping-id",
                "mapping-1",
                "--retired-by",
                "human-operator",
                "--reason",
                "superseded",
            ]
        )
        self.assertEqual(verify.verified_by, "human-operator")
        self.assertEqual(verify.evidence_ref, "review-1")
        self.assertEqual(retire.retired_by, "human-operator")
        self.assertEqual(retire.reason, "superseded")


if __name__ == "__main__":
    unittest.main()
