"""Hermetic tests for controlled Asset to PI AF mapping administration."""

from __future__ import annotations

import csv
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.app import create_app
from src.config import MartDbConfig
from src.domain.asset_af_mapping import AssetAfMapping
from src.repositories.asset_af_mapping_store import (
    AssetAfMappingCommandStore,
    MappingConflictError,
    MappingValidationError,
)
from src.repositories.mart_database import MartDatabase
from src.repositories.mart_models import (
    AssetAfMappingMart,
    AssetMasterMart,
    MartBase,
    ReliabilityAssetRegistryMart,
)
from src.services.asset_af_mapping_admin import (
    AssetAfMappingAdminService,
    ImportFormatError,
    REQUIRED_COLUMNS,
)
from src.services.reliability import ReliabilityQueryService
from src.repositories.mart_reader import MartQueryRepository


NOW = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
ASSET_ID = "NADI-ASSET-001"


def _asset(asset_id: str = ASSET_ID, *, site: str = "BSR", organization: str = "IP") -> AssetMasterMart:
    return AssetMasterMart(
        canonical_id=asset_id,
        contract_version="1.0",
        source_asset_number=f"SYNTHETIC-{asset_id}",
        description="Synthetic asset fixture",
        status="OPERATING",
        site_code=site,
        organization_code=organization,
        provenance={"source_system": "MAXIMO"},
        relationship_evidence={},
        sources={"maximo": {"assetnum": f"SYNTHETIC-{asset_id}"}},
        mart_created_at=NOW,
        mart_updated_at=NOW,
    )


def _mapping(status: str = "PROPOSED", element_ref: str = "AF_ELEMENT_TEST_001") -> AssetAfMapping:
    return AssetAfMapping(
        id=f"mapping-{status.lower()}-{element_ref.lower()}",
        canonical_asset_id=ASSET_ID,
        pi_source_id="CENTRAL_PI",
        af_server_ref="AF_SERVER_TEST",
        af_database_ref="AF_DATABASE_TEST",
        af_element_ref=element_ref,
        mapping_role="PRIMARY_EQUIPMENT",
        mapping_status=status,  # type: ignore[arg-type]
        evidence_method="MANUAL_VERIFICATION",
        created_at=NOW,
        updated_at=NOW,
        verified_at=NOW if status == "VERIFIED" else None,
        verified_by="synthetic-operator" if status == "VERIFIED" else None,
        verification_note="Synthetic verification" if status == "VERIFIED" else None,
        evidence_ref="synthetic-evidence" if status == "VERIFIED" else None,
        retired_at=NOW if status == "RETIRED" else None,
        retired_by="synthetic-operator" if status == "RETIRED" else None,
        retirement_note="Synthetic retirement" if status == "RETIRED" else None,
    )


class AssetAfMappingAdminTest(unittest.TestCase):
    def setUp(self) -> None:
        self.database = MartDatabase(MartDbConfig(dsn="sqlite+pysqlite:///:memory:"))
        MartBase.metadata.create_all(self.database.engine)
        with Session(self.database.engine) as session:
            session.add(_asset())
            session.add(_asset("NADI-ASSET-UNREGISTERED"))
            session.add(
                ReliabilityAssetRegistryMart(
                    asset_ref=ASSET_ID,
                    source_asset_number="SYNTHETIC-NADI-ASSET-001",
                    site_code="BSR",
                    organization_code="IP",
                    registry_source="SYNTHETIC_FIXTURE",
                    snapshot_sha256="a" * 64,
                    snapshot_row_count=1,
                    snapshot_imported_at=NOW,
                )
            )
            session.commit()
        self.store = AssetAfMappingCommandStore(self.database.engine)
        self.admin = AssetAfMappingAdminService(self.store)
        self.service = ReliabilityQueryService(MartQueryRepository(self.database))

    def tearDown(self) -> None:
        self.database.engine.dispose()

    @staticmethod
    def _write_csv(directory: str, rows: list[dict[str, str]], headers: list[str] | None = None) -> Path:
        path = Path(directory) / "mapping.csv"
        fieldnames = headers or list(REQUIRED_COLUMNS) + ["evidence_ref", "verification_note"]
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        return path

    @staticmethod
    def _row(**overrides: str) -> dict[str, str]:
        row = {
            "canonical_asset_id": ASSET_ID,
            "pi_source_id": "CENTRAL_PI",
            "af_server_ref": "AF_SERVER_TEST",
            "af_database_ref": "AF_DATABASE_TEST",
            "af_element_ref": "AF_ELEMENT_TEST_001",
            "mapping_role": "PRIMARY_EQUIPMENT",
            "evidence_method": "MANUAL_VERIFICATION",
            "evidence_ref": "synthetic-candidate-ref",
            "verification_note": "Synthetic candidate context",
        }
        row.update(overrides)
        return row

    def _count_rows(self) -> int:
        with Session(self.database.engine) as session:
            return len(session.scalars(select(AssetAfMappingMart)).all())

    def test_verified_integrity_requires_actor_time_and_evidence(self):
        with self.assertRaises(MappingValidationError):
            self.store.create(replace(_mapping("VERIFIED"), verified_by=None))
        with self.assertRaises(MappingValidationError):
            self.store.create(replace(_mapping("VERIFIED"), verified_at=None))
        with self.assertRaises(MappingValidationError):
            self.store.create(replace(_mapping("VERIFIED"), verification_note=None, evidence_ref=None))

    def test_proposed_rejects_verification_identity_and_retired_requires_provenance(self):
        with self.assertRaises(MappingValidationError):
            self.store.create(replace(_mapping(), verified_by="operator"))
        with self.assertRaises(MappingValidationError):
            self.store.create(replace(_mapping("RETIRED"), retired_by=None))
        with self.assertRaises(MappingValidationError):
            self.store.create(replace(_mapping("RETIRED"), retirement_note=None))

    def test_valid_dry_run_writes_zero_and_import_creates_proposed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_csv(directory, [self._row()])
            dry_run = self.admin.import_csv(path, dry_run=True)
            self.assertEqual((dry_run.rows_seen, dry_run.valid, dry_run.accepted, dry_run.rejected), (1, 1, 1, 0))
            self.assertEqual(self._count_rows(), 0)

            imported = self.admin.import_csv(path, dry_run=False)
            self.assertEqual(imported.accepted, 1)
            self.assertEqual(self._count_rows(), 1)
            stored = self.service.repository.list_asset_af_mappings(ASSET_ID)[0]
            self.assertEqual(stored.mapping_status, "PROPOSED")
            self.assertIsNone(stored.verified_by)

    def test_unknown_and_nonregistered_assets_are_rejected_atomically(self):
        rows = [
            self._row(af_element_ref="AF_ELEMENT_UNKNOWN_ASSET", canonical_asset_id="NADI-ASSET-UNKNOWN"),
            self._row(af_element_ref="AF_ELEMENT_UNREGISTERED", canonical_asset_id="NADI-ASSET-UNREGISTERED"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            result = self.admin.import_csv(self._write_csv(directory, rows), dry_run=False)
        self.assertEqual(result.rejected, 2)
        self.assertEqual(result.unknown_assets, 2)
        self.assertEqual(result.accepted, 0)
        self.assertEqual(self._count_rows(), 0)

    def test_duplicate_input_and_active_conflict_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            duplicate_path = self._write_csv(directory, [self._row(), self._row()])
            duplicate = self.admin.import_csv(duplicate_path, dry_run=False)
            self.assertEqual(duplicate.duplicates, 1)
            self.assertEqual(duplicate.accepted, 0)
            self.assertEqual(self._count_rows(), 0)

            self.store.create(_mapping())
            conflict = self.admin.import_csv(self._write_csv(directory, [self._row()]), dry_run=True)
            self.assertEqual(conflict.conflicts, 1)
            self.assertEqual(conflict.accepted, 0)

    def test_invalid_role_evidence_and_blank_af_reference_are_rejected(self):
        rows = [
            self._row(af_element_ref="AF_ELEMENT_BAD_ROLE", mapping_role="SECONDARY"),
            self._row(af_element_ref="AF_ELEMENT_BAD_METHOD", evidence_method="FUZZY"),
            self._row(af_element_ref="", af_database_ref=""),
        ]
        with tempfile.TemporaryDirectory() as directory:
            result = self.admin.import_csv(self._write_csv(directory, rows), dry_run=True)
        reasons = [row.reason_code for row in result.row_results]
        self.assertEqual(reasons, ["INVALID_ROLE", "INVALID_EVIDENCE_METHOD", "MISSING_REQUIRED_FIELD"])

    def test_csv_security_limits_and_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            formula = self.admin.import_csv(
                self._write_csv(directory, [self._row(af_element_ref="=HYPERLINK(\"x\")")]),
                dry_run=True,
            )
            self.assertEqual(formula.row_results[0].reason_code, "FORMULA_VALUE")

            with self.assertRaises(ImportFormatError):
                self.admin.import_csv(
                    self._write_csv(directory, [self._row()], headers=list(REQUIRED_COLUMNS) + ["mapping_status"]),
                    dry_run=True,
                )

            oversized = self._row(verification_note="x" * 2001)
            result = self.admin.import_csv(self._write_csv(directory, [oversized]), dry_run=True)
            self.assertEqual(result.row_results[0].reason_code, "OVERSIZED_CELL")

            too_many_rows = [self._row(af_element_ref=f"AF_ELEMENT_{index:03d}") for index in range(501)]
            with self.assertRaises(ImportFormatError):
                self.admin.import_csv(self._write_csv(directory, too_many_rows), dry_run=True)

    def test_batch_insert_failure_rolls_back_all_rows(self):
        first = _mapping(element_ref="AF_ELEMENT_ROLLBACK_001")
        second = replace(_mapping(element_ref="AF_ELEMENT_ROLLBACK_002"), id=first.id)
        with self.assertRaises(MappingConflictError):
            self.store.create_proposed_batch((first, second))
        self.assertEqual(self._count_rows(), 0)

    def test_verify_retire_and_reverification_transitions(self):
        with tempfile.TemporaryDirectory() as directory:
            self.admin.import_csv(self._write_csv(directory, [self._row()]), dry_run=False)
        proposal = self.service.repository.list_asset_af_mappings(ASSET_ID)[0]

        with self.assertRaises(MappingValidationError):
            self.store.verify(proposal.id, verified_by="operator")
        verified = self.store.verify(
            proposal.id,
            verified_by="human-operator",
            evidence_ref="controlled-review-001",
        )
        self.assertEqual(verified.mapping_status, "VERIFIED")
        self.assertEqual(verified.verified_by, "human-operator")
        self.assertEqual(verified.evidence_ref, "controlled-review-001")
        self.assertEqual(self.service.asset_af_mapping(ASSET_ID).mapping_state, "MAPPED")

        with self.assertRaises(MappingConflictError):
            self.store.verify(proposal.id, verified_by="second-operator", verification_note="overwrite")
        self.assertTrue(self.store.retire(proposal.id, retired_by="human-operator", retirement_note="superseded"))
        self.assertEqual(self.service.asset_af_mapping(ASSET_ID).mapping_state, "UNMAPPED")
        self.assertFalse(self.store.retire(proposal.id, retired_by="human-operator", retirement_note="again"))
        with self.assertRaises(MappingConflictError):
            self.store.verify(proposal.id, verified_by="human-operator", evidence_ref="reactivation")

    def test_reimport_of_active_proposal_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_csv(directory, [self._row()])
            self.assertEqual(self.admin.import_csv(path, dry_run=False).accepted, 1)
            second = self.admin.import_csv(path, dry_run=False)
        self.assertEqual(second.accepted, 0)
        self.assertEqual(second.conflicts, 1)
        self.assertEqual(self._count_rows(), 1)

    def test_public_mapping_routes_remain_get_only(self):
        routes = [route for route in create_app().routes if route.path.endswith("/pi-mapping")]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].methods, {"GET"})


if __name__ == "__main__":
    unittest.main()
