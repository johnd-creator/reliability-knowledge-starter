"""Readiness logic for governed Asset to PI AF mappings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.domain.asset_af_mapping import AssetAfMapping
from src.repositories.mart_models import AssetAfMappingMart


MappingState = Literal["UNMAPPED", "MAPPED", "AMBIGUOUS"]


@dataclass(frozen=True, slots=True)
class AssetAfMappingResolution:
    asset_id: str
    mapping_state: MappingState
    selected: AssetAfMapping | None
    candidates: tuple[AssetAfMapping, ...]


def mapping_from_row(row: AssetAfMappingMart) -> AssetAfMapping:
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


def resolve_asset_af_mapping(asset_id: str, mappings: list[AssetAfMapping]) -> AssetAfMappingResolution:
    """Resolve only verified primary mappings; never choose an ambiguous row."""

    candidates = tuple(mappings)
    verified = tuple(
        mapping
        for mapping in candidates
        if mapping.mapping_status == "VERIFIED" and mapping.mapping_role == "PRIMARY_EQUIPMENT"
    )
    if len(verified) == 0:
        return AssetAfMappingResolution(asset_id, "UNMAPPED", None, candidates)
    if len(verified) > 1:
        return AssetAfMappingResolution(asset_id, "AMBIGUOUS", None, candidates)
    return AssetAfMappingResolution(asset_id, "MAPPED", verified[0], candidates)
