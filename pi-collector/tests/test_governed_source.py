"""Hermetic tests for the NADI governed PI source boundary."""

from __future__ import annotations

import unittest

from src.domain.governed import (
    GovernedAfTarget,
    GovernedTargetError,
    validate_governed_af_target,
)
from src.services.governed_source import GovernedSourceBoundary


def target(**changes) -> GovernedAfTarget:
    values = {
        "canonical_asset_id": "NADI-ASSET-TEST-001",
        "pi_source_id": "CENTRAL_PI",
        "af_server_ref": "AF_SERVER_TEST",
        "af_database_ref": "AF_DATABASE_TEST",
        "af_element_ref": "AF_ELEMENT_TEST",
        "mapping_role": "PRIMARY_EQUIPMENT",
        "mapping_status": "VERIFIED",
    }
    values.update(changes)
    return GovernedAfTarget(**values)


class GovernedTargetValidationTest(unittest.TestCase):
    def test_verified_primary_central_pi_is_accepted(self):
        self.assertEqual(validate_governed_af_target(target()).mapping_status, "VERIFIED")

    def test_unusable_states_and_wrong_identity_are_rejected(self):
        for status in ("PROPOSED", "RETIRED", "UNMAPPED", "MAPPED", "AMBIGUOUS"):
            with self.subTest(status=status):
                with self.assertRaises(GovernedTargetError):
                    validate_governed_af_target(target(mapping_status=status))
        with self.assertRaises(GovernedTargetError):
            validate_governed_af_target(target(mapping_role="SECONDARY"))
        with self.assertRaises(GovernedTargetError):
            validate_governed_af_target(target(pi_source_id="OTHER_PI"))

    def test_required_references_are_explicit(self):
        for field_name in (
            "canonical_asset_id",
            "af_server_ref",
            "af_database_ref",
            "af_element_ref",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(GovernedTargetError):
                    validate_governed_af_target(target(**{field_name: "  "}))


if __name__ == "__main__":
    unittest.main()
