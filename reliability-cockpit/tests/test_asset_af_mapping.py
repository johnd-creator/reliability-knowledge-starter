"""Hermetic tests for the governed Asset to PI AF mapping registry."""

from __future__ import annotations

import unittest
from dataclasses import fields
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.api import reliability as reliability_api
from src.api.app import create_app
from src.config import MartDbConfig
from src.domain.asset_af_mapping import AssetAfMapping
from src.repositories.asset_af_mapping_store import (
    AssetAfMappingCommandStore,
    MappingConflictError,
    MappingValidationError,
)
from src.repositories.mart_database import MartDatabase
from src.repositories.mart_models import AssetAfMappingMart, AssetMasterMart, MartBase, ReliabilityAssetRegistryMart
from src.repositories.mart_reader import MartQueryRepository
from src.services.reliability import ReliabilityQueryService


NOW = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
ASSET_ID = "NADI-ASSET-001"


def _asset() -> AssetMasterMart:
    return AssetMasterMart(
        canonical_id=ASSET_ID,
        contract_version="1.0",
        source_asset_number="SYNTHETIC-ASSET-001",
        description="Synthetic asset fixture",
        status="OPERATING",
        site_code="BSR",
        organization_code="IP",
        provenance={"source_system": "MAXIMO", "source_site": "BSR", "source_organization": "IP"},
        relationship_evidence={},
        sources={"maximo": {"assetnum": "SYNTHETIC-ASSET-001"}},
        mart_created_at=NOW,
        mart_updated_at=NOW,
    )


def _mapping(status: str, element_ref: str = "AF_ELEMENT_TEST_001") -> AssetAfMapping:
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
        retired_at=NOW if status == "RETIRED" else None,
        source_assetnum_snapshot="SYNTHETIC-ASSET-001",
        source_siteid_snapshot="BSR",
        source_orgid_snapshot="IP",
    )


class AssetAfMappingRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.database = MartDatabase(MartDbConfig(dsn="sqlite+pysqlite:///:memory:"))
        MartBase.metadata.create_all(self.database.engine)
        with Session(self.database.engine) as session:
            session.add(_asset())
            session.add(
                ReliabilityAssetRegistryMart(
                    asset_ref=ASSET_ID,
                    source_asset_number="SYNTHETIC-ASSET-001",
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
        self.service = ReliabilityQueryService(MartQueryRepository(self.database))

    def test_valid_mapping_references_registered_canonical_asset(self):
        mapping = _mapping("VERIFIED")
        self.store.create(mapping)
        rows = self.service.repository.list_asset_af_mappings(ASSET_ID)
        self.assertEqual([row.canonical_asset_id for row in rows], [ASSET_ID])

    def test_invalid_or_unregistered_asset_is_rejected(self):
        mapping = _mapping("PROPOSED")
        invalid = mapping.__class__(**{**{field.name: getattr(mapping, field.name) for field in fields(mapping)}, "canonical_asset_id": "NADI-ASSET-UNKNOWN"})
        with self.assertRaises(MappingValidationError):
            self.store.create(invalid)

    def test_duplicate_active_exact_mapping_is_rejected(self):
        self.store.create(_mapping("PROPOSED"))
        with self.assertRaises(MappingConflictError):
            self.store.create(_mapping("PROPOSED"))

    def test_retired_history_does_not_block_a_new_active_proposal(self):
        self.store.create(_mapping("RETIRED"))
        self.store.create(_mapping("PROPOSED"))
        self.assertEqual(len(self.service.repository.list_asset_af_mappings()), 2)

    def test_proposed_mapping_is_not_ready(self):
        self.store.create(_mapping("PROPOSED"))
        resolution = self.service.asset_af_mapping(ASSET_ID)
        self.assertEqual(resolution.mapping_state, "UNMAPPED")
        self.assertIsNone(resolution.selected)

    def test_retired_mapping_is_not_active(self):
        self.store.create(_mapping("RETIRED"))
        resolution = self.service.asset_af_mapping(ASSET_ID)
        self.assertEqual(resolution.mapping_state, "UNMAPPED")
        self.assertEqual(resolution.candidates[0].mapping_status, "RETIRED")

    def test_one_verified_primary_mapping_is_mapped(self):
        self.store.create(_mapping("VERIFIED"))
        resolution = self.service.asset_af_mapping(ASSET_ID)
        self.assertEqual(resolution.mapping_state, "MAPPED")
        self.assertEqual(resolution.selected.af_element_ref, "AF_ELEMENT_TEST_001")

    def test_multiple_verified_primary_mappings_are_ambiguous(self):
        self.store.create(_mapping("VERIFIED", "AF_ELEMENT_TEST_001"))
        self.store.create(_mapping("VERIFIED", "AF_ELEMENT_TEST_002"))
        resolution = self.service.asset_af_mapping(ASSET_ID)
        self.assertEqual(resolution.mapping_state, "AMBIGUOUS")
        self.assertIsNone(resolution.selected)
        self.assertEqual(len(resolution.candidates), 2)

    def test_api_exposes_state_without_source_write_or_fuzzy_fallback(self):
        response = reliability_api.asset_af_mapping(ASSET_ID, service=self.service)
        self.assertEqual(response.mapping_state, "UNMAPPED")
        self.assertIsNone(response.pi_af)
        self.assertIn("/v1/reliability/assets/{canonical_id}/pi-mapping", create_app().openapi()["paths"])

    def test_api_returns_mapped_af_reference_only_after_verification(self):
        self.store.create(_mapping("VERIFIED"))
        response = reliability_api.asset_af_mapping(ASSET_ID, service=self.service)
        self.assertEqual(response.mapping_state, "MAPPED")
        self.assertEqual(response.pi_af.af_server_ref, "AF_SERVER_TEST")
        self.assertEqual(response.pi_af.af_element_ref, "AF_ELEMENT_TEST_001")

    def test_registry_has_no_credential_or_live_value_fields(self):
        names = set(AssetAfMappingMart.__table__.columns.keys())
        forbidden = {"password", "token", "cookie", "authorization", "live_value", "process_value"}
        self.assertTrue(names.isdisjoint(forbidden))
        self.assertNotIn("PI_PASSWORD", {field.name.upper() for field in fields(_mapping("PROPOSED"))})
