"""Bounded local canonical evidence adapter. Never imports a source client."""
from datetime import datetime, timezone
from hashlib import sha256
import math
from uuid import uuid4
import json
from sqlalchemy import select
from src.domain.engineering import EvidenceKind, EvidenceReference, EvidenceSnapshot, EngineeringError
from src.repositories.mart_reader import MartQueryRepository
from src.repositories.mart_models import MaintenanceEventMart, FmeaAssessmentMart
from src.services.condition_query import ConditionQueryService


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value is not None and value.tzinfo is None else value


# Digest contract v2: canonical facts and source identity only. Never serialize
# raw sources, personal reported_by/lead fields, arbitrary provenance, or local
# ingestion/projector timestamps. Historical v1 references remain readable;
# their versions differ and must be deliberately reselected before new actions.
FACT_FIELDS = {
    EvidenceKind.ASSET: ("canonical_id", "contract_version", "source_asset_number",
        "description", "status", "location_ref", "parent_asset_ref", "site_code",
        "organization_code", "asset_type", "plant", "unit", "criticality", "source_updated_at"),
    EvidenceKind.MAINTENANCE: ("canonical_id", "contract_version", "id", "equipment_id",
        "work_order_id", "event_type", "status", "actual_start", "actual_finish",
        "duration_hours", "labor_hours", "downtime_hours", "failure_code",
        "source_changed_at", "site_code", "organization_code"),
    EvidenceKind.FMEA: ("canonical_id", "contract_version", "source_record_id", "source_number",
        "revision", "lifecycle_status", "description", "asset_ref", "failure_code_ref",
        "site_code", "organization_code", "source_updated_at", "status_changed_at"),
}
PROVENANCE_FIELDS = ("source_system", "source_application", "source_object", "source_record_id",
    "source_number", "source_site", "source_organization", "source_created_at", "source_updated_at")


def factual_version(asset_id, kind, record_id, row):
    """Hash canonical facts without imposing new business-string size limits.

    Text becomes a typed, fixed-size field digest before building the manifest.
    UTF-8 chunks bound temporary encoding memory even for unbounded contract
    descriptions. This is content identity, not source approval.
    """
    def scalar(value):
        if isinstance(value, datetime):
            return dict(type="datetime", value=aware(value).astimezone(timezone.utc).isoformat())
        if isinstance(value, str):
            digest, utf8_bytes = sha256(), 0
            for start in range(0, len(value), 2048):
                encoded = value[start:start + 2048].encode("utf-8")
                digest.update(encoded)
                utf8_bytes += len(encoded)
            return dict(type="string", codepoints=len(value), utf8_bytes=utf8_bytes,
                sha256=digest.hexdigest())
        if value is None or type(value) in (str, int, float, bool):
            if isinstance(value, float) and not math.isfinite(value):
                raise EngineeringError("EVIDENCE_CONTENT_INVALID", 422)
            return dict(type=type(value).__name__, value=value)
        raise EngineeringError("EVIDENCE_CONTENT_INVALID", 422)
    provenance = row.provenance or {}
    if not isinstance(provenance, dict):
        raise EngineeringError("EVIDENCE_CONTENT_INVALID", 422)
    fields = FACT_FIELDS[EvidenceKind.MAINTENANCE if kind == EvidenceKind.WORK_ORDER else kind]
    document = dict(contract="nadi-canonical-evidence-v2", canonical_asset_id=asset_id,
        kind=kind, record_id=record_id, facts={name: scalar(getattr(row, name)) for name in fields},
        provenance={name: scalar(provenance.get(name)) for name in PROVENANCE_FIELDS})
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return "mart-facts-v2:" + sha256(encoded).hexdigest()


class LocalEvidenceCatalog:
    def __init__(self, mart_database, *, policy=None, clock=None):
        self.database = mart_database
        self.repository = MartQueryRepository(mart_database)
        self.conditions = ConditionQueryService(mart_database, policy=policy, clock=clock)

    def registered(self, asset_id):
        return self.repository.get_asset(asset_id) is not None

    def resolve(self, asset_id, kind, record_id, mode, linked_by, linked_at):
        asset = self.repository.get_asset(asset_id)
        if asset is None:
            raise EngineeringError("ASSET_NOT_REGISTERED", 422)
        source, approval = "CANONICAL_MART", "NOT_APPLICABLE"
        unit = good = questionable = substituted = annotated = timestamp = None
        freshness = "UNKNOWN"
        policy_ref = None
        factual_row = None
        if kind == EvidenceKind.ASSET:
            if record_id != asset_id:
                raise EngineeringError("EVIDENCE_NOT_FOUND", 404)
            timestamp = aware(asset.source_updated_at)
            snapshot = EvidenceSnapshot(label="Registered canonical asset", availability="AVAILABLE")
            factual_row = asset
        elif kind in {EvidenceKind.MAINTENANCE, EvidenceKind.WORK_ORDER, EvidenceKind.FMEA}:
            if kind == EvidenceKind.FMEA:
                query = select(FmeaAssessmentMart).where(FmeaAssessmentMart.canonical_id == record_id,
                    FmeaAssessmentMart.asset_ref == asset_id)
            else:
                identity = MaintenanceEventMart.work_order_id if kind == EvidenceKind.WORK_ORDER else MaintenanceEventMart.canonical_id
                query = select(MaintenanceEventMart).where(identity == record_id, MaintenanceEventMart.equipment_id == asset_id)
            with self.database.read_session() as session:
                rows = list(session.scalars(query.limit(2)))
            if not rows:
                raise EngineeringError("EVIDENCE_NOT_FOUND", 404)
            if len(rows) != 1:
                raise EngineeringError("EVIDENCE_AMBIGUOUS", 422)
            row = rows[0]
            factual_row = row
            if row.site_code != "BSR" or row.organization_code != "IP":
                raise EngineeringError("EVIDENCE_NOT_FOUND", 404)
            timestamp = aware(row.source_updated_at if kind == EvidenceKind.FMEA else row.source_changed_at)
            snapshot = EvidenceSnapshot(label="Canonical "+kind.value.lower()+" record",
                summary="Controlled local population; original record semantics retained.", availability="AVAILABLE")
        elif kind == EvidenceKind.CONDITION:
            result = self.conditions.asset_evidence(asset_id)
            if result is None or result.mapping_readiness != "MAPPING_VERIFIED":
                raise EngineeringError("NO_VERIFIED_MAPPING", 422)
            items = [item for item in result.items if item.evidence.signal_id == record_id]
            if len(items) != 1:
                raise EngineeringError("NO_APPROVED_EVIDENCE", 422)
            item = items[0]; e = item.evidence
            source, approval, timestamp, unit = "NADI_CONDITION", "APPROVED", e.source_timestamp, e.unit
            good, questionable, substituted, annotated = e.quality_good, e.quality_questionable, e.quality_substituted, e.quality_annotated
            freshness = item.freshness.source.removeprefix("SOURCE_")
            threshold = self.conditions.policy.threshold("SOURCE", "PI_CONDITION_PROJECTION")
            policy_ref = "SOURCE_MAX_AGE_SECONDS:"+str(threshold) if threshold is not None else None
            snapshot = EvidenceSnapshot(label=e.semantic_name, condition=e, availability="PARTIAL" if "PARTIAL_SIGNAL_SET" in result.statuses else "AVAILABLE")
        elif kind == EvidenceKind.RCFA:
            # Current Mart explicitly reports RCFA Asset relation UNRESOLVED.
            raise EngineeringError("RELATIONSHIP_UNRESOLVED", 422)
        else:
            # Data Trust aggregate includes local Collector observations. A frozen
            # reviewed aggregate provider is needed; no implicit HTTP query here.
            raise EngineeringError("EVIDENCE_PROVIDER_NOT_CONFIGURED", 422)
        version = (factual_version(asset_id, kind, record_id, factual_row) if factual_row is not None else
            sha256(json.dumps(dict(snapshot=snapshot.model_dump(mode="json"),
                timestamp=timestamp.isoformat() if timestamp else None), sort_keys=True).encode()).hexdigest())
        return EvidenceReference(reference_id="ref:"+str(uuid4()), record_id=record_id,
            canonical_asset_id=asset_id, kind=kind, source=source, mode=mode, stable_version=version,
            source_timestamp=timestamp, observed_at=linked_at, linked_at=linked_at, linked_by=linked_by,
            identity_status="VERIFIED", signal_approval=approval, freshness=freshness, freshness_policy_ref=policy_ref,
            unit=unit, quality_good=good, quality_questionable=questionable, quality_substituted=substituted,
            quality_annotated=annotated, snapshot=snapshot if mode == "FROZEN_SNAPSHOT" else None)
