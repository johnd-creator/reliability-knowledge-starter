"""Regression checks for the platform Reliability Mart runtime wiring."""

from pathlib import Path
import os
import re
import unittest
from unittest.mock import patch

from src.config import MartDbConfig


ROOT = Path(__file__).resolve().parents[2]


def _service_block(compose: str, service: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(service)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        compose,
    )
    if match is None:
        raise AssertionError(f"service not found: {service}")
    return match.group(1)


class RuntimeWiringTest(unittest.TestCase):
    def test_platform_example_declares_separate_mart_dsn_placeholder(self):
        example = (ROOT / ".env.platform.example").read_text(encoding="utf-8")
        self.assertIn("RELIABILITY_MART_DATABASE_URL=\n", example)
        self.assertNotIn("mxcollector:", example)
        self.assertNotIn("postgresql://", example)

    def test_managed_cockpit_api_receives_internal_mart_dsn(self):
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        block = _service_block(compose, "cockpit-api")
        self.assertIn("RELIABILITY_MART_DATABASE_URL:", block)
        self.assertIn("@maximo-db/maximo_collector", block)
        self.assertNotIn("@localhost:", block)
        self.assertIn("maximo-init: {condition: service_completed_successfully}", block)

    def test_external_cockpit_api_requires_reachable_mart_dsn(self):
        compose = (ROOT / "compose.external.yaml").read_text(encoding="utf-8")
        block = _service_block(compose, "cockpit-api")
        self.assertIn("RELIABILITY_MART_DATABASE_URL:", block)
        self.assertIn("set in .env.platform", block)
        self.assertIn("host.docker.internal:host-gateway", block)
        self.assertNotIn("@localhost:", block)

    def test_missing_mart_dsn_does_not_fallback_to_legacy_database_url(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://legacy-cockpit/cockpit",
                "RELIABILITY_MART_DATABASE_URL": "",
            },
            clear=False,
        ):
            self.assertIsNone(MartDbConfig.from_environment().dsn)


if __name__ == "__main__":
    unittest.main()
