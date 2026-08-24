"""Input boundary for NADI-governed PI AF targets.

This module deliberately has no database or Cockpit dependency. An orchestration
layer supplies a mapping selected from the Reliability Mart; the PI collector
only validates the already-resolved governance state before reading PI.
"""

from __future__ import annotations

from dataclasses import dataclass


class GovernedTargetError(ValueError):
    """Raised when a target is not an active governed Asset-to-AF identity."""


@dataclass(frozen=True)
class GovernedAfTarget:
    canonical_asset_id: str
    pi_source_id: str
    af_server_ref: str
    af_database_ref: str
    af_element_ref: str
    mapping_role: str
    mapping_status: str


def validate_governed_af_target(target: GovernedAfTarget) -> GovernedAfTarget:
    """Accept only a verified primary CENTRAL_PI mapping.

    PROPOSED, RETIRED, UNMAPPED, MAPPED, and AMBIGUOUS are intentionally not
    usable source lineage states. No winner is selected for ambiguity.
    """
    for field_name in (
        "canonical_asset_id",
        "pi_source_id",
        "af_server_ref",
        "af_database_ref",
        "af_element_ref",
        "mapping_role",
        "mapping_status",
    ):
        if not getattr(target, field_name).strip():
            raise GovernedTargetError(f"governed target requires {field_name}")
    if target.mapping_status != "VERIFIED":
        raise GovernedTargetError("governed target must be VERIFIED")
    if target.mapping_role != "PRIMARY_EQUIPMENT":
        raise GovernedTargetError("governed target must be PRIMARY_EQUIPMENT")
    if target.pi_source_id != "CENTRAL_PI":
        raise GovernedTargetError("governed target must use CENTRAL_PI")
    return target
