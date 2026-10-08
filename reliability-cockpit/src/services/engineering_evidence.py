"""Bounded local canonical evidence adapter. Never imports a source client."""
from datetime import timezone
from hashlib import sha256
from uuid import uuid4
import json
from sqlalchemy import select
from src.domain.engineering import EvidenceKind, EvidenceReference, EvidenceSnapshot, EngineeringError
from src.repositories.mart_reader import MartQueryRepository
from src.repositories.mart_models import MaintenanceEventMart, FmeaAssessmentMart
from src.services.condition_query import ConditionQueryService


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value is not None and value.tzinfo is None else value


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
        if kind == EvidenceKind.ASSET:
            if record_id != asset_id:
                raise EngineeringError("EVIDENCE_NOT_FOUND", 404)
            timestamp = aware(asset.source_updated_at)
            snapshot = EvidenceSnapshot(label="Registered canonical asset", availability="AVAILABLE")
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
        version = sha256(json.dumps(dict(snapshot=snapshot.model_dump(mode="json"),
            timestamp=timestamp.isoformat() if timestamp else None), sort_keys=True).encode()).hexdigest()
        return EvidenceReference(reference_id="ref:"+str(uuid4()), record_id=record_id,
            canonical_asset_id=asset_id, kind=kind, source=source, mode=mode, stable_version=version,
            source_timestamp=timestamp, observed_at=linked_at, linked_at=linked_at, linked_by=linked_by,
            identity_status="VERIFIED", signal_approval=approval, freshness=freshness, freshness_policy_ref=policy_ref,
            unit=unit, quality_good=good, quality_questionable=questionable, quality_substituted=substituted,
            quality_annotated=annotated, snapshot=snapshot if mode == "FROZEN_SNAPSHOT" else None)
