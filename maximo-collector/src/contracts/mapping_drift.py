"""Assertions that keep explicit collector mappers aligned with MX-007R."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


class MappingDriftError(ValueError):
    """The committed canonical mapping no longer matches required semantics."""


def _mapping_path() -> Path:
    return Path(__file__).resolve().parents[3] / "reliability-data-contracts" / "mappings" / "maximo-nadi-reliability.json"


@lru_cache(maxsize=1)
def assert_mapping_contract() -> bool:
    payload = json.loads(_mapping_path().read_text(encoding="utf-8"))
    rows = payload.get("mappings", [])
    keys = {(row.get("source_object"), row.get("source_field"), row.get("canonical_field"), row.get("evidence")) for row in rows}
    required = {
        ("IPFMEA", "fmeaid", "source_record_id", "DIRECT_VERIFIED"),
        ("IPFMEA", "assetnum", "asset_ref", "DIRECT_VERIFIED"),
        ("IPRCFA", "rcfaid", "source_record_id", "DIRECT_VERIFIED"),
        ("IPRCFA", None, "asset_ref", "UNRESOLVED"),
        ("IPBHM", "bhmid", "source_record_id", "DIRECT_VERIFIED"),
        ("IPBHM", "assetnum", "asset_ref", "DIRECT_VERIFIED"),
        ("IP_DOM_OH", "domid", "source_record_id", "DIRECT_VERIFIED"),
        ("IP_DOM_OH", "wonum", "workorder_ref", "DIRECT_VERIFIED"),
        ("IP_DOM_OH", None, "asset_ref", "DERIVED_VERIFIED_PATH"),
    }
    missing = required - keys
    if missing:
        raise MappingDriftError(f"canonical mapping drift detected: {sorted(missing)!r}")
    return True
