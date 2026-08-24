"""Controlled CSV administration for governed Asset to PI AF proposals."""

from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.domain.asset_af_mapping import AssetAfMapping
from src.repositories.asset_af_mapping_store import AssetAfMappingCommandStore


MAX_IMPORT_ROWS = 500
MAX_IMPORT_BYTES = 2 * 1024 * 1024
MAX_IMPORT_CELL_LENGTH = 2_000

REQUIRED_COLUMNS = (
    "canonical_asset_id",
    "pi_source_id",
    "af_server_ref",
    "af_database_ref",
    "af_element_ref",
    "mapping_role",
    "evidence_method",
)
OPTIONAL_COLUMNS = (
    "evidence_ref",
    "verification_note",
    "source_assetnum_snapshot",
    "source_siteid_snapshot",
    "source_orgid_snapshot",
    "af_path_snapshot",
    "af_element_name_snapshot",
)
ALLOWED_COLUMNS = frozenset((*REQUIRED_COLUMNS, *OPTIONAL_COLUMNS))


class ImportFormatError(ValueError):
    """The CSV envelope cannot be safely interpreted as an import batch."""


@dataclass(frozen=True, slots=True)
class ImportRowResult:
    row_number: int
    status: str
    reason_code: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "row_number": self.row_number,
            "status": self.status,
            "reason_code": self.reason_code,
        }


@dataclass(frozen=True, slots=True)
class ImportResult:
    rows_seen: int
    valid: int
    accepted: int
    rejected: int
    duplicates: int
    unknown_assets: int
    conflicts: int
    dry_run: bool
    row_results: tuple[ImportRowResult, ...]

    @property
    def invalid(self) -> int:
        return self.rejected

    def as_dict(self) -> dict[str, object]:
        return {
            "rows_seen": self.rows_seen,
            "valid": self.valid,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "duplicates": self.duplicates,
            "unknown_assets": self.unknown_assets,
            "conflicts": self.conflicts,
            "dry_run": self.dry_run,
            "row_results": [row.as_dict() for row in self.row_results],
        }


@dataclass(frozen=True, slots=True)
class _ParsedRow:
    row_number: int
    mapping: AssetAfMapping | None
    reason_code: str | None = None


def deterministic_proposal_id(
    canonical_asset_id: str,
    pi_source_id: str,
    af_server_ref: str,
    af_database_ref: str,
    af_element_ref: str,
    mapping_role: str,
) -> str:
    """Create a stable candidate ID from the explicit two-sided identity."""

    identity = "\x1f".join(
        (canonical_asset_id, pi_source_id, af_server_ref, af_database_ref, af_element_ref, mapping_role)
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
    return f"nadi-map-{digest}"


def parse_import_csv(path: Path) -> tuple[_ParsedRow, ...]:
    """Parse and syntactically validate an untrusted proposal CSV."""

    if path.stat().st_size > MAX_IMPORT_BYTES:
        raise ImportFormatError(f"IMPORT_TOO_LARGE: file exceeds {MAX_IMPORT_BYTES} bytes")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        content = stream.read()

    reader = csv.DictReader(io.StringIO(content, newline=""))
    headers = reader.fieldnames
    if not headers:
        raise ImportFormatError("MISSING_HEADER")
    if len(headers) != len(set(headers)):
        raise ImportFormatError("DUPLICATE_HEADERS")
    missing = sorted(set(REQUIRED_COLUMNS) - set(headers))
    unexpected = sorted(set(headers) - ALLOWED_COLUMNS)
    if missing:
        raise ImportFormatError(f"MISSING_REQUIRED_COLUMNS: {','.join(missing)}")
    if unexpected:
        raise ImportFormatError("UNEXPECTED_COLUMNS")

    rows: list[_ParsedRow] = []
    for row_number, raw in enumerate(reader, start=2):
        if len(rows) >= MAX_IMPORT_ROWS:
            raise ImportFormatError(f"IMPORT_TOO_LARGE: maximum {MAX_IMPORT_ROWS} rows")
        if None in raw:
            rows.append(_ParsedRow(row_number, None, "UNEXPECTED_COLUMNS"))
            continue

        values = {key: (raw.get(key) or "") for key in headers}
        formula_field = next(
            (key for key, value in values.items() if value.lstrip().startswith(("=", "+", "-", "@"))),
            None,
        )
        if formula_field is not None:
            rows.append(_ParsedRow(row_number, None, "FORMULA_VALUE"))
            continue
        if any(len(value) > MAX_IMPORT_CELL_LENGTH for value in values.values()):
            rows.append(_ParsedRow(row_number, None, "OVERSIZED_CELL"))
            continue

        normalized = {key: value.strip() or None for key, value in values.items()}
        missing_field = next((field for field in REQUIRED_COLUMNS if normalized.get(field) is None), None)
        if missing_field is not None:
            rows.append(_ParsedRow(row_number, None, "MISSING_REQUIRED_FIELD"))
            continue

        now = datetime.now(timezone.utc)
        role = normalized["mapping_role"]
        evidence_method = normalized["evidence_method"]
        mapping = AssetAfMapping(
            id=deterministic_proposal_id(
                normalized["canonical_asset_id"],
                normalized["pi_source_id"],
                normalized["af_server_ref"],
                normalized["af_database_ref"],
                normalized["af_element_ref"],
                role,
            ),
            canonical_asset_id=normalized["canonical_asset_id"],
            pi_source_id=normalized["pi_source_id"],
            af_server_ref=normalized["af_server_ref"],
            af_database_ref=normalized["af_database_ref"],
            af_element_ref=normalized["af_element_ref"],
            mapping_role=role,  # type: ignore[arg-type]
            mapping_status="PROPOSED",
            evidence_method=evidence_method,  # type: ignore[arg-type]
            created_at=now,
            updated_at=now,
            evidence_ref=normalized.get("evidence_ref"),
            verification_note=normalized.get("verification_note"),
            source_assetnum_snapshot=normalized.get("source_assetnum_snapshot"),
            source_siteid_snapshot=normalized.get("source_siteid_snapshot"),
            source_orgid_snapshot=normalized.get("source_orgid_snapshot"),
            af_path_snapshot=normalized.get("af_path_snapshot"),
            af_element_name_snapshot=normalized.get("af_element_name_snapshot"),
        )
        rows.append(_ParsedRow(row_number, mapping))
    return tuple(rows)


class AssetAfMappingAdminService:
    """Validate, dry-run, and atomically import candidate proposals."""

    def __init__(self, store: AssetAfMappingCommandStore):
        self.store = store

    def import_csv(self, path: Path, *, dry_run: bool) -> ImportResult:
        parsed = parse_import_csv(path)
        candidates = [row.mapping for row in parsed if row.mapping is not None]
        database_issues = self.store.validate_proposed_batch(candidates)

        candidate_index = 0
        row_results: list[ImportRowResult] = []
        valid_mappings: list[AssetAfMapping] = []
        for row in parsed:
            reason = row.reason_code
            if reason is None and row.mapping is not None:
                reason = database_issues.get(candidate_index)
                candidate_index += 1
            if reason is None and row.mapping is not None:
                valid_mappings.append(row.mapping)
                row_results.append(ImportRowResult(row.row_number, "VALID"))
            else:
                row_results.append(ImportRowResult(row.row_number, "REJECTED", reason))

        rejected = sum(result.status == "REJECTED" for result in row_results)
        accepted = 0
        if rejected == 0:
            if dry_run:
                accepted = len(valid_mappings)
            else:
                self.store.create_proposed_batch(valid_mappings)
                accepted = len(valid_mappings)
                row_results = [ImportRowResult(result.row_number, "IMPORTED") for result in row_results]

        reasons = [result.reason_code for result in row_results if result.reason_code is not None]
        return ImportResult(
            rows_seen=len(parsed),
            valid=len(valid_mappings),
            accepted=accepted,
            rejected=rejected,
            duplicates=reasons.count("DUPLICATE_INPUT"),
            unknown_assets=sum(reason in {"UNKNOWN_ASSET", "NON_REGISTERED_ASSET"} for reason in reasons),
            conflicts=reasons.count("ACTIVE_MAPPING_CONFLICT"),
            dry_run=dry_run,
            row_results=tuple(row_results),
        )
