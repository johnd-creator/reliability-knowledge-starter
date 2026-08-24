"""Bounded internal persistence for the NADI mapping registry.

This is deliberately separate from ``MartDatabase``. The public Mart query
facade remains SELECT-only; this command store is the only write boundary for
the NADI-owned mapping table.
"""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from src.config import MartDbConfig
from src.domain.asset_af_mapping import (
    MAPPING_EVIDENCE_METHODS,
    MAPPING_ROLES,
    MAPPING_STATUSES,
    SUPPORTED_PI_SOURCE_IDS,
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
    """The mapping conflicts with an active exact registry row or transition."""


class MappingBatchValidationError(MappingValidationError):
    """A complete proposal batch failed validation before any write."""

    def __init__(self, issues: dict[int, str]):
        self.issues = dict(issues)
        summary = ", ".join(f"row {index + 1}: {reason}" for index, reason in self.issues.items())
        super().__init__(summary or "mapping proposal batch is invalid")


class AssetAfMappingCommandStore:
    """Internal command boundary restricted to the mapping registry table."""

    def __init__(self, engine):  # type: ignore[no-untyped-def]
        self._engine = engine
        self._session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    @classmethod
    def from_environment(cls) -> "AssetAfMappingCommandStore":
        """Build the write-only mapping command boundary from the Mart DSN."""

        config = MartDbConfig.from_environment()
        if not config.dsn:
            raise MappingValidationError("RELIABILITY_MART_DATABASE_URL is not configured")
        return cls(create_engine(config.dsn, echo=config.echo, pool_pre_ping=True))

    def close(self) -> None:
        """Release the command store engine owned by a CLI invocation."""

        self._engine.dispose()

    def create(self, mapping: AssetAfMapping) -> AssetAfMapping:
        """Persist an explicitly constructed, provenance-valid registry row.

        CSV administration never calls this method with a VERIFIED row; normal
        import uses :meth:`create_proposed_batch`, and verification uses the
        explicit :meth:`verify` transition.
        """

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

    def validate_proposed_batch(self, mappings: Sequence[AssetAfMapping]) -> dict[int, str]:
        """Validate proposal rows without writing anything to the database."""

        issues: dict[int, str] = {}
        seen: dict[tuple[str, str, str], int] = {}
        with self._session_factory() as session:
            for index, mapping in enumerate(mappings):
                reason = self._proposal_shape_reason(mapping)
                if reason is not None:
                    issues[index] = reason
                    continue

                key = self._exact_key(mapping)
                if key in seen:
                    issues[index] = "DUPLICATE_INPUT"
                    continue
                seen[key] = index

                asset_exists = session.scalar(
                    select(AssetMasterMart.canonical_id).where(
                        AssetMasterMart.canonical_id == mapping.canonical_asset_id,
                    )
                )
                if asset_exists is None:
                    issues[index] = "UNKNOWN_ASSET"
                    continue

                if not self._is_registered_asset(session, mapping.canonical_asset_id):
                    issues[index] = "NON_REGISTERED_ASSET"
                    continue

                conflict = session.scalar(
                    select(AssetAfMappingMart.id).where(
                        AssetAfMappingMart.canonical_asset_id == mapping.canonical_asset_id,
                        AssetAfMappingMart.af_element_ref == mapping.af_element_ref,
                        AssetAfMappingMart.mapping_role == mapping.mapping_role,
                        AssetAfMappingMart.mapping_status.in_(("PROPOSED", "VERIFIED")),
                    )
                )
                if conflict is not None:
                    issues[index] = "ACTIVE_MAPPING_CONFLICT"
        return issues

    def create_proposed_batch(self, mappings: Sequence[AssetAfMapping]) -> tuple[AssetAfMapping, ...]:
        """Atomically persist validated PROPOSED rows and nothing else."""

        mappings = tuple(mappings)
        issues = self.validate_proposed_batch(mappings)
        if issues:
            raise MappingBatchValidationError(issues)

        with self._session_factory() as session:
            rows: list[AssetAfMappingMart] = []
            stored: list[AssetAfMapping] = []
            for mapping in mappings:
                self._validate(mapping)
                self._require_registered_asset(session, mapping.canonical_asset_id)
                persisted = self._allocate_available_id(session, mapping)
                stored.append(persisted)
                rows.append(AssetAfMappingMart(**asdict(persisted)))
            session.add_all(rows)
            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise MappingConflictError("active exact Asset to AF mapping already exists") from error
            return tuple(stored)

    def verify(
        self,
        mapping_id: str,
        *,
        verified_by: str,
        verification_note: str | None = None,
        evidence_ref: str | None = None,
        verified_at: datetime | None = None,
    ) -> AssetAfMapping:
        """Move one PROPOSED mapping to VERIFIED with explicit human evidence."""

        actor = self._required_text(verified_by, "verified_by")
        note = self._optional_text(verification_note)
        reference = self._optional_text(evidence_ref)
        if note is None and reference is None:
            raise MappingValidationError("verification_note or evidence_ref is required")

        when = verified_at or datetime.now(timezone.utc)
        with self._session_factory() as session:
            row = session.get(AssetAfMappingMart, mapping_id)
            if row is None:
                raise MappingValidationError("mapping not found")
            if row.mapping_status == "RETIRED":
                raise MappingConflictError("RETIRED mappings cannot be reactivated")
            if row.mapping_status == "VERIFIED":
                raise MappingConflictError("VERIFIED mappings cannot be silently re-verified")
            if row.mapping_status != "PROPOSED":
                raise MappingValidationError("only PROPOSED mappings can be verified")
            row.mapping_status = "VERIFIED"
            row.verified_at = when
            row.verified_by = actor
            row.verification_note = note
            row.evidence_ref = reference
            row.updated_at = when
            session.commit()
            return self._mapping_from_row(row)

    def retire(
        self,
        mapping_id: str,
        *,
        retired_by: str,
        retirement_note: str,
        retired_at: datetime | None = None,
    ) -> bool:
        """Retire an active proposal or verified mapping with a reason."""

        actor = self._required_text(retired_by, "retired_by")
        reason = self._required_text(retirement_note, "retirement_note")
        when = retired_at or datetime.now(timezone.utc)
        with self._session_factory() as session:
            row = session.get(AssetAfMappingMart, mapping_id)
            if row is None or row.mapping_status == "RETIRED":
                return False
            row.mapping_status = "RETIRED"
            row.retired_at = when
            row.retired_by = actor
            row.retirement_note = reason
            row.updated_at = when
            session.commit()
            return True

    @staticmethod
    def _exact_key(mapping: AssetAfMapping) -> tuple[str, str, str]:
        return mapping.canonical_asset_id, mapping.af_element_ref, mapping.mapping_role

    @staticmethod
    def _required_text(value: str | None, field_name: str) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not normalized:
            raise MappingValidationError(f"{field_name} is required")
        return normalized

    @staticmethod
    def _optional_text(value: str | None) -> str | None:
        normalized = value.strip() if isinstance(value, str) else ""
        return normalized or None

    @classmethod
    def _proposal_shape_reason(cls, mapping: AssetAfMapping) -> str | None:
        try:
            cls._validate(mapping)
        except MappingValidationError as error:
            message = str(error)
            if "status" in message:
                return "INVALID_STATUS"
            if "role" in message:
                return "INVALID_ROLE"
            if "evidence method" in message:
                return "INVALID_EVIDENCE_METHOD"
            if "PI source" in message:
                return "UNSUPPORTED_PI_SOURCE"
            if "AF reference" in message:
                return "MISSING_REQUIRED_FIELD"
            if "PROPOSED" in message:
                return "PROPOSED_VERIFICATION_FORBIDDEN"
            return "INVALID_MAPPING"
        return None

    @classmethod
    def _validate(cls, mapping: AssetAfMapping) -> None:
        if mapping.mapping_status not in MAPPING_STATUSES:
            raise MappingValidationError("unsupported mapping status")
        if mapping.mapping_role not in MAPPING_ROLES:
            raise MappingValidationError("unsupported mapping role")
        if mapping.evidence_method not in MAPPING_EVIDENCE_METHODS:
            raise MappingValidationError("unsupported mapping evidence method")
        if mapping.pi_source_id not in SUPPORTED_PI_SOURCE_IDS:
            raise MappingValidationError("unsupported PI source")
        if not all(
            cls._optional_text(value)
            for value in (mapping.canonical_asset_id, mapping.af_server_ref, mapping.af_database_ref, mapping.af_element_ref)
        ):
            raise MappingValidationError("AF reference and canonical Asset fields are required")

        if mapping.mapping_status == "VERIFIED":
            if mapping.verified_at is None or cls._optional_text(mapping.verified_by) is None:
                raise MappingValidationError("VERIFIED mappings require verified_at and verified_by")
            if cls._optional_text(mapping.verification_note) is None and cls._optional_text(mapping.evidence_ref) is None:
                raise MappingValidationError("VERIFIED mappings require verification_note or evidence_ref")
        elif mapping.mapping_status == "PROPOSED":
            if mapping.verified_at is not None or mapping.verified_by is not None:
                raise MappingValidationError("PROPOSED mappings cannot have verification identity")
        elif mapping.mapping_status == "RETIRED":
            if mapping.retired_at is None or cls._optional_text(mapping.retired_by) is None or cls._optional_text(mapping.retirement_note) is None:
                raise MappingValidationError("RETIRED mappings require retirement provenance")

    @classmethod
    def _is_registered_asset(cls, session: Session, canonical_asset_id: str) -> bool:
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
        return session.scalar(statement) is not None

    @classmethod
    def _require_registered_asset(cls, session: Session, canonical_asset_id: str) -> None:
        if not cls._is_registered_asset(session, canonical_asset_id):
            raise MappingValidationError("canonical Asset is not a registered BSR/IP Asset")

    @staticmethod
    def _allocate_available_id(session: Session, mapping: AssetAfMapping) -> AssetAfMapping:
        """Keep deterministic import IDs while allowing retired history."""

        if session.get(AssetAfMappingMart, mapping.id) is None:
            return mapping
        suffix = 2
        while session.get(AssetAfMappingMart, f"{mapping.id}-v{suffix}") is not None:
            suffix += 1
        return replace(mapping, id=f"{mapping.id}-v{suffix}")

    @staticmethod
    def _mapping_from_row(row: AssetAfMappingMart) -> AssetAfMapping:
        return AssetAfMapping(
            id=row.id,
            canonical_asset_id=row.canonical_asset_id,
            pi_source_id=row.pi_source_id,
            af_server_ref=row.af_server_ref,
            af_database_ref=row.af_database_ref,
            af_element_ref=row.af_element_ref,
            mapping_role=row.mapping_role,  # type: ignore[arg-type]
            mapping_status=row.mapping_status,  # type: ignore[arg-type]
            evidence_method=row.evidence_method,  # type: ignore[arg-type]
            created_at=row.created_at,
            updated_at=row.updated_at,
            verified_at=row.verified_at,
            verified_by=row.verified_by,
            verification_note=row.verification_note,
            evidence_ref=row.evidence_ref,
            retired_at=row.retired_at,
            retired_by=row.retired_by,
            retirement_note=row.retirement_note,
            source_assetnum_snapshot=row.source_assetnum_snapshot,
            source_siteid_snapshot=row.source_siteid_snapshot,
            source_orgid_snapshot=row.source_orgid_snapshot,
            af_path_snapshot=row.af_path_snapshot,
            af_element_name_snapshot=row.af_element_name_snapshot,
        )
