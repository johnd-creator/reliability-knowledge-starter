"""Bounded internal persistence for the NADI mapping registry.

This is deliberately separate from ``MartDatabase``. The public Mart query
facade remains SELECT-only; this command store can write only the NADI-owned
mapping table for a future administrative workflow.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from src.domain.asset_af_mapping import (
    MAPPING_EVIDENCE_METHODS,
    MAPPING_ROLES,
    MAPPING_STATUSES,
    AssetAfMapping,
)
from src.repositories.mart_models import (
    AssetAfMappingMart,
    AssetMasterMart,
    ReliabilityAssetRegistryMart,
)


class MappingValidationError(ValueError):
    """The proposed mapping is not a valid governed registry command."""


class MappingConflictError(RuntimeError):
    """The mapping conflicts with an active exact registry row."""


class AssetAfMappingCommandStore:
    """Internal command boundary restricted to the mapping registry table."""

    def __init__(self, engine):  # type: ignore[no-untyped-def]
        self._session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def create(self, mapping: AssetAfMapping) -> AssetAfMapping:
        self._validate(mapping)
        with self._session_factory() as session:
            self._require_registered_asset(session, mapping.canonical_asset_id)
            row = AssetAfMappingMart(**asdict(mapping))
            session.add(row)
            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise MappingConflictError("active exact Asset to AF mapping already exists") from error
            return mapping

    def retire(self, mapping_id: str, *, retired_at: datetime | None = None) -> bool:
        when = retired_at or datetime.now(timezone.utc)
        with self._session_factory() as session:
            row = session.get(AssetAfMappingMart, mapping_id)
            if row is None or row.mapping_status == "RETIRED":
                return False
            row.mapping_status = "RETIRED"
            row.retired_at = when
            row.updated_at = when
            session.commit()
            return True

    @staticmethod
    def _require_registered_asset(session: Session, canonical_asset_id: str) -> None:
        statement = (
            select(AssetMasterMart.canonical_id)
            .join(ReliabilityAssetRegistryMart, ReliabilityAssetRegistryMart.asset_ref == AssetMasterMart.canonical_id)
            .where(
                AssetMasterMart.canonical_id == canonical_asset_id,
                AssetMasterMart.site_code == "BSR",
                AssetMasterMart.organization_code == "IP",
                ReliabilityAssetRegistryMart.site_code == "BSR",
                ReliabilityAssetRegistryMart.organization_code == "IP",
            )
        )
        if session.scalar(statement) is None:
            raise MappingValidationError("canonical Asset is not a registered BSR/IP Asset")

    @staticmethod
    def _validate(mapping: AssetAfMapping) -> None:
        if mapping.mapping_status not in MAPPING_STATUSES:
            raise MappingValidationError("unsupported mapping status")
        if mapping.evidence_method not in MAPPING_EVIDENCE_METHODS:
            raise MappingValidationError("unsupported mapping evidence method")
        if mapping.mapping_role not in MAPPING_ROLES:
            raise MappingValidationError("unsupported mapping role")
        if mapping.mapping_status == "VERIFIED" and mapping.verified_at is None:
            raise MappingValidationError("VERIFIED mappings require verified_at")
        if mapping.mapping_status == "PROPOSED" and mapping.verified_at is not None:
            raise MappingValidationError("PROPOSED mappings cannot have verified_at")
        if mapping.mapping_status == "RETIRED" and mapping.retired_at is None:
            raise MappingValidationError("RETIRED mappings require retired_at")
