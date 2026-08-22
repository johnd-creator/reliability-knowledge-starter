"""CLI regression tests for local Cockpit web-access commands."""

from __future__ import annotations

import argparse
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.cli import cmd_sync
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


if __name__ == "__main__":
    unittest.main()
