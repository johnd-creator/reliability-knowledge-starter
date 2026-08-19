"""Unit tests for the PI discovery CLI — no network, no PI access required.

Covers the safety guarantees and the offline documented-catalog generation.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import scripts.discover_pi as dpi

REPO_ROOT = Path(__file__).resolve().parent.parent


class ReadOnlyEnforcementTest(unittest.TestCase):
    def test_only_get_head_options_allowed(self):
        for ok in ("GET", "HEAD", "OPTIONS", "get", "Head"):
            self.assertIn(ok.upper(), dpi.READ_ONLY_METHODS)

    def test_blocked_methods_raise(self):
        cfg = dpi.Config(base_url="https://example/piwebapi", rate_limit_seconds=0)
        for bad in ("POST", "PUT", "PATCH", "DELETE"):
            with self.assertRaises(dpi.DiscoveryError):
                dpi._request(bad, cfg.base_url + "/", cfg, auth_headers=None)


class SanitizeTest(unittest.TestCase):
    def test_credentials_stripped(self):
        out = dpi.sanitize({"Token": "abc", "Authorization": "Bearer x", "Name": "PUMP", "set-cookie": "y"})
        self.assertNotIn("Token", out)
        self.assertNotIn("Authorization", out)
        self.assertNotIn("set-cookie", out)
        self.assertEqual(out["Name"], "PUMP")

    def test_nested_lists_and_dicts(self):
        out = dpi.sanitize({"Links": [{"href": "/x", "password": "p"}]})
        self.assertEqual(out["Links"][0]["href"], "/x")
        self.assertNotIn("password", out["Links"][0])


class DocumentedCatalogTest(unittest.TestCase):
    """The documented catalog is a GENERATOR: running it must never clobber
    the repo's verified discovery data. Write to a temp dir, not the repo."""

    def _write_catalog_to(self, repo_root: Path) -> Path:
        import argparse

        rc = dpi.cmd_documented(argparse.Namespace(), repo_root)
        self.assertEqual(rc, 0)
        return repo_root / "discovery" / "endpoints.json"

    def test_documented_command_writes_catalog(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            catalog = json.loads(self._write_catalog_to(Path(td)).read_text(encoding="utf-8"))
        self.assertEqual(catalog["system"], "pi")
        self.assertFalse(catalog["instance_verified"])
        names = {r["resource"] for r in catalog["resources"]}
        self.assertIn("dataservers", names)
        self.assertIn("points", names)
        self.assertIn("stream-value", names)
        for r in catalog["resources"]:
            self.assertEqual(r["status"], "documented", f"{r['resource']} must start documented")
            self.assertEqual(r["method"], "GET")

    def test_documented_records_units_guidance(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            catalog = json.loads(self._write_catalog_to(Path(td)).read_text(encoding="utf-8"))
        attr = next(r for r in catalog["resources"] if r["resource"] == "attributes")
        self.assertIn("DefaultUnitsName", attr["important_fields"])
        pts = next(r for r in catalog["resources"] if r["resource"] == "points")
        self.assertIn("Units", pts["important_fields"])

    def test_documented_does_not_touch_repo_catalog(self):
        """Guard: the repo's endpoints.json must survive a catalog generation."""
        before = (REPO_ROOT / "discovery" / "endpoints.json").read_text(encoding="utf-8")
        import argparse
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            dpi.cmd_documented(argparse.Namespace(), Path(td))
        after = (REPO_ROOT / "discovery" / "endpoints.json").read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_probe_requires_execute(self):
        rc = dpi.main(["--probe-system"])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()