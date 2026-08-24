"""Governed Maximo Asset to PI AF mapping domain values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


MappingStatus = Literal["PROPOSED", "VERIFIED", "RETIRED"]
MappingEvidenceMethod = Literal[
    "NATIVE_IDENTIFIER",
    "GOVERNED_LOOKUP",
    "MANUAL_VERIFICATION",
    "MIGRATED_VERIFIED",
]
MappingRole = Literal["PRIMARY_EQUIPMENT"]


@dataclass(frozen=True, slots=True)
class AssetAfMapping:
    """A NADI-owned cross-source identity assertion.

    This object contains references only. It never contains PI credentials,
    authorization material, or process values.
    """

    id: str
    canonical_asset_id: str
    pi_source_id: str
    af_server_ref: str
    af_database_ref: str
    af_element_ref: str
    mapping_role: MappingRole
    mapping_status: MappingStatus
    evidence_method: MappingEvidenceMethod
    created_at: datetime
    updated_at: datetime
    verified_at: datetime | None = None
    verified_by: str | None = None
    verification_note: str | None = None
    evidence_ref: str | None = None
    retired_at: datetime | None = None
    retired_by: str | None = None
    retirement_note: str | None = None
    source_assetnum_snapshot: str | None = None
    source_siteid_snapshot: str | None = None
    source_orgid_snapshot: str | None = None
    af_path_snapshot: str | None = None
    af_element_name_snapshot: str | None = None


MAPPING_STATUSES = frozenset({"PROPOSED", "VERIFIED", "RETIRED"})
MAPPING_EVIDENCE_METHODS = frozenset(
    {"NATIVE_IDENTIFIER", "GOVERNED_LOOKUP", "MANUAL_VERIFICATION", "MIGRATED_VERIFIED"}
)
MAPPING_ROLES = frozenset({"PRIMARY_EQUIPMENT"})
# Administrative input is allowlisted to the governed PI source alias already
# used by the foundation's synthetic fixtures. This is not a live PI lookup.
SUPPORTED_PI_SOURCE_IDS = frozenset({"CENTRAL_PI"})
