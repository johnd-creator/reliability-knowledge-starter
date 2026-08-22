"""Cached JSON Schema validation for canonical collector records."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator


class ContractValidationError(ValueError):
    """A canonical record does not satisfy its committed contract schema."""


_SCHEMAS = {
    "asset_master": "asset-master.schema.json",
    "maintenance_event": "maintenance-event.schema.json",
    "fmea_assessment": "fmea-assessment.schema.json",
    "rcfa_analysis": "rcfa-analysis.schema.json",
    "asset_health_assessment": "asset-health-assessment.schema.json",
    "overhaul_event": "overhaul-event.schema.json",
}


def contracts_root() -> Path:
    configured = os.getenv("RELIABILITY_CONTRACTS_ROOT")
    if configured:
        return Path(configured).resolve()
    # src/contracts/validator.py -> repository root is parents[3].
    return Path(__file__).resolve().parents[3] / "reliability-data-contracts"


@lru_cache(maxsize=None)
def _validator(entity: str) -> Draft202012Validator:
    try:
        filename = _SCHEMAS[entity]
    except KeyError as exc:
        raise ContractValidationError(f"unsupported canonical entity: {entity}") from exc
    path = contracts_root() / "schemas" / filename
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ContractValidationError(f"canonical schema unavailable for {entity}") from exc
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_record(entity: str, record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a shallow-copied canonical record.

    Validators are cached so production collection does not re-read or
    recompile a schema for every row. Error text contains only schema paths,
    never the full source payload.
    """
    errors = sorted(_validator(entity).iter_errors(record), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        path = ".".join(str(part) for part in first.path) or "<record>"
        raise ContractValidationError(f"{entity}.{path}: {first.message}")
    return dict(record)
