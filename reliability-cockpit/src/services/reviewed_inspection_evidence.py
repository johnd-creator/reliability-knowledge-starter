"""Operator-injected current directory and local application reads; no source calls."""
from hashlib import sha256
from uuid import uuid4
from sqlalchemy import select
from src.repositories.human_records import RecordRow
from src.domain.engineering import (Principal, EvidenceKind, EvidenceReference,
    EvidenceSnapshot, EngineeringError)
from src.domain.reviewed_inspection import ReviewedInspectionEvidence

class ReviewedInspectionCatalog:
    def __init__(self, canonical_catalog, inspections, directory):
        self.canonical, self.inspections, self.directory = canonical_catalog, inspections, directory
    def registered(self, asset): return self.canonical.registered(asset)
    def resolve(self, asset, kind, record, mode, actor_id, linked_at):
        if kind != EvidenceKind.MANUAL_INSPECTION:
            return self.canonical.resolve(asset, kind, record, mode, actor_id, linked_at)
        if mode != 'FROZEN_SNAPSHOT':
            raise EngineeringError('REVIEWED_SNAPSHOT_REQUIRED',422)
        actor = self.directory(actor_id)
        if not isinstance(actor,Principal) or actor.principal_id != actor_id or not actor.roles or asset not in actor.asset_ids:
            raise EngineeringError('AUTHENTICATION_REQUIRED',401)
        row=self.inspections.get(actor,record)
        if row.canonical_asset_id != asset or row.status != 'APPROVED' or row.review is None:
            raise EngineeringError('NO_APPROVED_INSPECTION',422)
        version=sha256(row.model_dump_json().encode()).hexdigest()
        human=ReviewedInspectionEvidence(canonical_asset_id=asset,record_id=record,
            revision=row.revision,stable_version=version,inspector_ref=row.inspector_ref,
            inspected_at=row.inspected_at,method=row.method,method_version=row.method_version,
            measurements=row.measurements,observations=row.observations,interpretations=row.interpretations,
            reviewer=row.review.reviewer,reviewed_at=row.review.decided_at)
        return EvidenceReference(reference_id='ref:'+str(uuid4()),record_id=record,
            canonical_asset_id=asset,kind=kind,source='NADI_REVIEWED_INSPECTION',
            mode=mode,stable_version=version,source_timestamp=row.inspected_at,
            observed_at=row.updated_at,linked_at=linked_at,linked_by=actor_id,
            identity_status='REGISTERED',signal_approval='NOT_APPLICABLE',
            snapshot=EvidenceSnapshot(label='Reviewed human inspection',availability='AVAILABLE',reviewed_inspection=human))

    def guard_evidence(self, connection, actor, asset, refs):
        if connection.engine is not self.inspections.repo.engine:
            raise EngineeringError("APPLICATION_STORE_IDENTITY_MISMATCH", 503)
        for ref in sorted(refs, key=lambda x: (x.kind, x.record_id)):
            if ref.kind != EvidenceKind.MANUAL_INSPECTION:
                continue
            raw = connection.scalar(select(RecordRow.document).where(
                RecordRow.kind == "INSPECTION", RecordRow.record_id == ref.record_id).with_for_update())
            row = self.inspections.visible(actor, raw)
            if row.canonical_asset_id != asset or row.status != "APPROVED" or sha256(row.model_dump_json().encode()).hexdigest() != ref.stable_version:
                raise EngineeringError("EVIDENCE_VERSION_CHANGED", 409)
