"""Validate every committed discovery object against its JSON Schema.

Ensures the hand-curated knowledge records in discovery/objects/*.json conform
to schemas/object.schema.json, so downstream consumers (reliability-data-contracts,
reliability-cockpit) can rely on a stable shape.
"""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
OBJECTS_DIR = REPO_ROOT / "discovery" / "objects"
SCHEMA_PATH = REPO_ROOT / "schemas" / "object.schema.json"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class SchemaValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = _load_json(SCHEMA_PATH)
        cls.validator = Draft202012Validator(cls.schema)

    def test_schema_itself_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(self.schema)

    def test_every_committed_object_validates(self):
        files = sorted(OBJECTS_DIR.glob("*.json"))
        self.assertGreater(len(files), 0, "expected at least one object record")
        for path in files:
            with self.subTest(object=path.name):
                record = _load_json(path)
                errors = sorted(self.validator.iter_errors(record), key=lambda e: e.path)
                if errors:
                    detail = "; ".join(f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}" for e in errors)
                    self.fail(f"{path.name} does not conform to object.schema.json — {detail}")

    def test_verified_records_carry_verified_at(self):
        for path in sorted(OBJECTS_DIR.glob("*.json")):
            record = _load_json(path)
            if record.get("status") == "verified":
                with self.subTest(object=path.name):
                    self.assertIsNotNone(
                        record.get("verified_at"),
                        f"{path.name} is verified but has no verified_at timestamp",
                    )

    def test_forbidden_records_have_null_verified_at(self):
        for path in sorted(OBJECTS_DIR.glob("*.json")):
            record = _load_json(path)
            if record.get("status") == "forbidden":
                with self.subTest(object=path.name):
                    self.assertIsNone(
                        record.get("verified_at"),
                        f"{path.name} is forbidden and must not carry a verified_at timestamp",
                    )


if __name__ == "__main__":
    unittest.main()
