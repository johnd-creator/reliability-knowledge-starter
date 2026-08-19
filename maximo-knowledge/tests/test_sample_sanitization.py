"""Regression guard: administrative / personal identifiers and internal
hostnames must never re-enter committed discovery samples.

Catches the issues fixed in hardening/sample-sanitization:
  * `changeby` / `plusgopenomuid` personal identifiers left as real values
  * internal app-server hostname `mx761app1.*` leaking into tracked JSON
"""

from __future__ import annotations

import glob
import json
import unittest
from pathlib import Path

DISCOVERY_DIR = Path(__file__).resolve().parent.parent / "discovery"
INTERNAL_HOSTNAME = "mx761app1"
PERSONAL_FIELDS = {
    "changeby",
    "plusgopenomuid",
    "reportedby",
    "reportedbyname",
    "supervisor",
    "lead",
    "affectedperson",
    "affectedphone",
    "reportedphone",
    "primaryphone",
    "primaryemail",
}


class SampleSanitizationTest(unittest.TestCase):
    def test_no_internal_hostname_in_tracked_object_samples(self) -> None:
        for path in sorted(glob.glob(str(DISCOVERY_DIR / "objects" / "*.json"))):
            text = Path(path).read_text(encoding="utf-8")
            self.assertNotIn(
                INTERNAL_HOSTNAME,
                text,
                f"internal app-server hostname '{INTERNAL_HOSTNAME}' leaked into {path}",
            )

    def test_personal_fields_in_samples_are_redacted(self) -> None:
        for path in sorted(glob.glob(str(DISCOVERY_DIR / "objects" / "*.json"))):
            record = json.loads(Path(path).read_text(encoding="utf-8"))
            sample = record.get("sample")
            if not isinstance(sample, dict):
                continue
            for field in PERSONAL_FIELDS & sample.keys():
                value = sample[field]
                self.assertIn(
                    value,
                    (None, "", []),
                    f"personal field '{field}' in {path} sample must be redacted, got {value!r}",
                )

    def test_large_oas_not_tracked(self) -> None:
        """maximo_oas.json is auto-fetched and may contain hostnames; keep it
        gitignored and out of the repository."""
        import subprocess

        tracked = subprocess.check_output(
            ["git", "ls-files", "discovery/oslc/maximo_oas.json"], cwd=DISCOVERY_DIR.parent, text=True
        ).strip()
        self.assertEqual(tracked, "", "discovery/oslc/maximo_oas.json must be gitignored, not tracked")


if __name__ == "__main__":
    unittest.main()