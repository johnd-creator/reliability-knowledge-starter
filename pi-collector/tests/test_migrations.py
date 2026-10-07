"""Check PI migration filenames offline; no database or migration runner."""

from pathlib import Path
import unittest


def unique_numeric_prefixes(names):
    """Reject collisions even when filenames have different zero padding."""
    prefixes = {}
    for name in sorted(names):
        prefix = int(name.split("_", 1)[0])
        if prefix in prefixes:
            raise ValueError(f"Duplicate migration prefix {prefix:03d}: {prefixes[prefix]} and {name}")
        prefixes[prefix] = name
    return prefixes


class MigrationSequenceTest(unittest.TestCase):
    def test_repository_migration_prefixes_are_unique_and_ordered(self):
        directory = Path(__file__).resolve().parents[1] / "migrations"
        prefixes = unique_numeric_prefixes(path.name for path in directory.glob("*.sql"))
        expected = ["001_init.sql", "002_collect_runs.sql", "003_backfill_progress.sql",
                    "004_signal_quality_fields.sql"]
        # Additional future migrations are allowed; existing numbers stay unique.
        self.assertEqual([prefixes[number] for number in sorted(prefixes)][:4], expected)

    def test_duplicate_numeric_prefixes_are_rejected(self):
        for names in (("002_collect_runs.sql", "002_signal_quality_fields.sql"),
                      ("004_signal_quality_fields.sql", "4_another_change.sql")):
            with self.subTest(names=names):
                with self.assertRaisesRegex(ValueError, "Duplicate migration prefix"):
                    unique_numeric_prefixes(names)


if __name__ == "__main__":
    unittest.main()
