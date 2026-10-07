"""Clean Compose/runtime contract checks; no private env/source access."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.cli import parse_args
from src.config import MartDbConfig, load_env

ROOT = Path(__file__).resolve().parents[2]


class RuntimeConfigTest(unittest.TestCase):
    def test_no_legacy_mart_fallback(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://legacy.invalid/cockpit"}, clear=True):
            self.assertIsNone(MartDbConfig.from_environment().dsn)

    def test_managed_skips_both_dotenv_paths(self):
        with patch.dict(os.environ, {"COCKPIT_CONFIG_MODE": "managed"}, clear=True), patch("src.config._load_dotenv") as loader:
            load_env()
            loader.assert_not_called()

    def test_standalone_preserves_local_dotenv(self):
        with patch.dict(os.environ, {}, clear=True), patch("src.config._load_dotenv") as loader:
            load_env()
            self.assertEqual(loader.call_count, 2)

    def test_migration_and_role_default_are_non_destructive(self):
        self.assertFalse(parse_args(["mart-migrate"]).apply)
        self.assertFalse(parse_args(["mart-reader"]).apply)
        self.assertTrue(parse_args(["mart-migrate", "--require-ready"]).require_ready)
        self.assertTrue(parse_args(["mart-migrate", "--apply"]).apply)


@unittest.skipUnless(os.getenv("NADI_COMPOSE_TESTS"), "enable clean Docker Compose config checks explicitly")
class ComposeRuntimeTest(unittest.TestCase):
    def config(self, name, missing_reader=False):
        with tempfile.TemporaryDirectory() as directory:
            clean = Path(directory)
            (clean / name).write_bytes((ROOT / name).read_bytes())
            sample = (ROOT / ".env.platform.example").read_text()
            if missing_reader:
                sample = "\n".join(line for line in sample.splitlines() if not line.startswith("RELIABILITY_MART_DATABASE_URL="))
            (clean / ".env.platform").write_text(sample)
            result = subprocess.run(["docker", "compose", "--env-file", ".env.platform", "-f", name,
                "--profile", "mart-maintenance", "config", "--format", "json"], cwd=clean,
                env={"PATH": os.environ["PATH"], "HOME": directory, "COMPOSE_DISABLE_ENV_FILE": "1"}, capture_output=True, text=True)
            if missing_reader:
                self.assertNotEqual(result.returncode, 0)
                return None
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)["services"]

    def test_managed_explicit_reader_admin_isolation_and_existing_databases(self):
        s = self.config("compose.yaml")
        api = s["cockpit-api"]["environment"]
        self.assertIn("nadi_mart_reader:", api["RELIABILITY_MART_DATABASE_URL"])
        self.assertIn("@maximo-db/maximo_collector", api["RELIABILITY_MART_DATABASE_URL"])
        self.assertIn("@cockpit-db/cockpit", api["DATABASE_URL"])
        self.assertNotIn("RELIABILITY_MART_ADMIN_DATABASE_URL", api)
        self.assertNotIn("RELIABILITY_MART_READER_PASSWORD", api)
        self.assertEqual({k for k in s if k.endswith("-db")}, {"maximo-db", "pi-db", "cems-db", "cockpit-db"})
        self.assertNotIn("RELIABILITY_MART_DATABASE_URL", s["cockpit-init"]["environment"])

    def test_projector_waits_for_ready_schema_without_source_acquisition(self):
        s = self.config("compose.yaml")
        self.assertEqual(s["mart-projector"]["depends_on"]["mart-ready"]["condition"], "service_completed_successfully")
        self.assertEqual(s["cockpit-api"]["depends_on"]["mart-ready"]["condition"], "service_completed_successfully")
        self.assertEqual(s["mart-ready"]["command"], ["cockpit", "mart-migrate", "--require-ready"])
        self.assertEqual(set(s["mart-ready"]["depends_on"]), {"maximo-db"})
        self.assertNotIn("--apply", s["mart-ready"]["command"])
        self.assertIn("--incremental", s["mart-projector"]["command"][-1])
        self.assertEqual(s["mart-projector"]["environment"]["RELIABILITY_CONTRACTS_ROOT"], "/contracts")
        self.assertEqual(s["mart-migrate"]["profiles"], ["mart-maintenance"])

    def test_no_source_credentials_in_mart_or_cockpit(self):
        s = self.config("compose.yaml")
        secrets = {"MAXIMO_USERNAME", "MAXIMO_PASSWORD", "MAXIMO_READ_ONLY_TOKEN", "PI_USERNAME", "PI_PASSWORD", "PI_TOKEN"}
        for name in ["cockpit-api", "cockpit-init", "cockpit-worker", "mart-migrate", "mart-ready", "mart-reader", "mart-projector"]:
            self.assertFalse(secrets & s[name]["environment"].keys(), name)

    def test_external_explicit_existing_mart_without_projector_or_mart_initialization(self):
        s = self.config("compose.external.yaml")
        self.assertEqual(set(s), {"cockpit-db", "cockpit-init", "cockpit-api", "cockpit-worker", "cockpit-web"})
        self.assertIn("RELIABILITY_MART_DATABASE_URL", s["cockpit-api"]["environment"])
        self.assertNotIn("RELIABILITY_MART_ADMIN_DATABASE_URL", s["cockpit-api"]["environment"])
        self.assertNotIn("RELIABILITY_MART_DATABASE_URL", s["cockpit-init"]["environment"])
        self.assertIn("host.docker.internal=host-gateway", s["cockpit-api"]["extra_hosts"])

    def test_both_modes_require_reader_dsn(self):
        self.config("compose.yaml", missing_reader=True)
        self.config("compose.external.yaml", missing_reader=True)
