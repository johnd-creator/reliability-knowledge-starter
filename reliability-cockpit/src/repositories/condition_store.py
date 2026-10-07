"""Operator-only selected evidence writer; query API uses MartDatabase instead."""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.domain.condition_evidence import (EvidenceBatch, EvidenceSources, PiLineage, ProjectionPlan, SignalSelection, MAX_SIGNALS)
from src.repositories.condition_models import ConditionSignalSelectionMart, ConditionEvidenceLatestMart, ConditionProjectionStateMart
from src.repositories.mart_models import AssetAfMappingMart, ReliabilityAssetRegistryMart, AssetMasterMart
from src.services.asset_af_mapping import mapping_from_row, resolve_asset_af_mapping

class ProjectionGateError(ValueError):
    def __init__(self, status):
        self.status = status
        super().__init__(status)

class ConditionCommandStore:
    def __init__(self, engine):
        self.engine = engine

    @classmethod
    def from_environment(cls):
        from src.services.mart_migrations import admin_engine, run_migrations, _expected_database
        engine = admin_engine()
        try:
            run_migrations(engine, expected_database=_expected_database(), require_ready=True)
            return cls(engine)
        except Exception:
            engine.dispose()
            raise

    @staticmethod
    def _mapping(session, asset_id, *, lock=False):
        registered = session.scalar(select(ReliabilityAssetRegistryMart).join(AssetMasterMart, AssetMasterMart.canonical_id == ReliabilityAssetRegistryMart.asset_ref).where(
            ReliabilityAssetRegistryMart.asset_ref == asset_id, ReliabilityAssetRegistryMart.site_code == "BSR",
            ReliabilityAssetRegistryMart.organization_code == "IP", AssetMasterMart.site_code == "BSR", AssetMasterMart.organization_code == "IP"))
        if registered is None:
            raise ProjectionGateError("ASSET_NOT_REGISTERED")
        query = select(AssetAfMappingMart).where(AssetAfMappingMart.canonical_asset_id == asset_id).order_by(AssetAfMappingMart.id)
        if lock:
            # Serializes projection/approval with retire/verify on the same mapping rows.
            query = query.with_for_update()
        rows = list(session.scalars(query))
        resolution = resolve_asset_af_mapping(asset_id, [mapping_from_row(r) for r in rows])
        mapping = resolution.selected
        if mapping is None:
            raise ProjectionGateError("NO_VERIFIED_MAPPING")
        lineage = PiLineage(pi_source_id=mapping.pi_source_id, af_server_ref=mapping.af_server_ref,
            af_database_ref=mapping.af_database_ref, af_element_ref=mapping.af_element_ref,
            mapping_role=mapping.mapping_role, mapping_status=mapping.mapping_status)
        return mapping, EvidenceSources(pi=lineage)

    def approve_signal(self, definition: SignalSelection):
        """Explicit local approval, never registry inference; immutable definition IDs."""
        definition = SignalSelection.model_validate(definition.model_dump(mode="json"))
        if definition.approval_status != "APPROVED":
            raise ProjectionGateError("NO_APPROVED_SIGNALS")
        with Session(self.engine) as session, session.begin():
            row = session.get(AssetAfMappingMart, definition.mapping_id)
            if row is None:
                raise ProjectionGateError("NO_VERIFIED_MAPPING")
            mapping, _ = self._mapping(session, row.canonical_asset_id, lock=True)
            if mapping.id != definition.mapping_id:
                raise ProjectionGateError("NO_VERIFIED_MAPPING")
            current = list(session.scalars(select(ConditionSignalSelectionMart).where(
                ConditionSignalSelectionMart.mapping_id == mapping.id, ConditionSignalSelectionMart.approval_status == "APPROVED").with_for_update()))
            if len(current) >= MAX_SIGNALS or any(
                SignalSelection.model_validate(r.definition).attribute_ref == definition.attribute_ref or
                SignalSelection.model_validate(r.definition).semantic_name == definition.semantic_name for r in current):
                raise ProjectionGateError("SIGNAL_SELECTION_CONFLICT")
            if session.get(ConditionSignalSelectionMart, definition.signal_id):
                raise ProjectionGateError("SIGNAL_SELECTION_CONFLICT")
            session.add(ConditionSignalSelectionMart(signal_id=definition.signal_id, mapping_id=definition.mapping_id,
                approval_status="APPROVED", definition=definition.model_dump(mode="json")))

    def retire_signal(self, signal_id):
        with Session(self.engine) as session, session.begin():
            row = session.get(ConditionSignalSelectionMart, signal_id)
            if row is None:
                raise ProjectionGateError("NO_APPROVED_SIGNALS")
            mapping = session.get(AssetAfMappingMart, row.mapping_id)
            # Lock mapping before selection: same lock order as projection/approval.
            session.scalars(select(AssetAfMappingMart).where(AssetAfMappingMart.canonical_asset_id == mapping.canonical_asset_id).with_for_update()).all()
            session.refresh(row, with_for_update=True)
            definition = SignalSelection.model_validate(row.definition)
            row.approval_status = "RETIRED"
            row.definition = definition.model_copy(update={"approval_status": "RETIRED"}).model_dump(mode="json")

    def _plan(self, session, asset_id, *, lock=False):
        mapping, lineage = self._mapping(session, asset_id, lock=lock)
        query = select(ConditionSignalSelectionMart).where(ConditionSignalSelectionMart.mapping_id == mapping.id,
            ConditionSignalSelectionMart.approval_status == "APPROVED").order_by(ConditionSignalSelectionMart.signal_id).limit(MAX_SIGNALS + 1)
        if lock:
            query = query.with_for_update()
        signals = tuple(SignalSelection.model_validate(r.definition) for r in session.scalars(query))
        if not signals:
            raise ProjectionGateError("NO_APPROVED_SIGNALS")
        return ProjectionPlan(canonical_asset_id=asset_id, mapping_id=mapping.id, sources=lineage, signals=signals)

    def plan(self, asset_id):
        with Session(self.engine) as session:
            return self._plan(session, asset_id)

    def project(self, batch: EvidenceBatch, *, now=None):
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("aware projection clock required")
        with Session(self.engine) as session, session.begin():
            current = self._plan(session, batch.plan.canonical_asset_id, lock=True)
            if current != batch.plan:
                raise ProjectionGateError("GOVERNANCE_CHANGED")
            # Revalidate even callers using model_construct; never trust transport assertions.
            batch = EvidenceBatch.model_validate(batch.model_dump(mode="json"))
            if any(r.evidence and r.evidence.collected_at > now for r in batch.results):
                raise ProjectionGateError("FUTURE_COLLECTION")
            state_row = session.get(ConditionProjectionStateMart, current.canonical_asset_id, with_for_update=True)
            # Older handoffs must not move attempt/currentness backwards.
            attempt_at = max((r.evidence.collected_at for r in batch.results if r.evidence), default=now)
            if state_row:
                previous = state_row.attempted_at
                if previous.tzinfo is None:
                    previous = previous.replace(tzinfo=timezone.utc)
                if attempt_at < previous:
                    return {"status": "IGNORED_OLDER_BATCH", "written": 0}
            written = 0
            for result in batch.results:
                if result.evidence is None:
                    continue
                e = result.evidence
                row = session.get(ConditionEvidenceLatestMart, e.signal_id)
                payload = e.model_dump(mode="json")
                if row is not None:
                    previous = row.collected_at
                    if previous.tzinfo is None:
                        previous = previous.replace(tzinfo=timezone.utc)
                    if e.collected_at < previous:
                        continue
                    if e.collected_at == previous:
                        if row.evidence != payload:
                            raise ProjectionGateError("CONFLICTING_SAME_COLLECTION")
                        continue
                    row.evidence, row.collected_at, row.projected_at = payload, e.collected_at, now
                else:
                    session.add(ConditionEvidenceLatestMart(signal_id=e.signal_id, canonical_asset_id=e.canonical_asset_id,
                        mapping_id=e.mapping_id, evidence=payload, collected_at=e.collected_at, projected_at=now))
                written += 1
            successful = sum(r.evidence is not None for r in batch.results)
            statuses = sorted({r.status for r in batch.results if r.status != "COLLECTED"})
            if successful < len(current.signals):
                statuses.append("PARTIAL_SIGNAL_SET" if successful else "SOURCE_UNAVAILABLE")
            status = statuses or ["PROJECTED"]
            state = {"mapping_id": current.mapping_id, "statuses": sorted(set(status)),
                "expected_signals": len(current.signals), "collected_signals": successful,
                "collector_last_success_at": batch.collector_last_success_at.isoformat() if batch.collector_last_success_at else None}
            if state_row is None:
                session.add(ConditionProjectionStateMart(canonical_asset_id=current.canonical_asset_id, attempted_at=attempt_at, state=state))
            elif state_row.state != state or state_row.attempted_at.replace(tzinfo=timezone.utc) != attempt_at:
                state_row.state, state_row.attempted_at = state, attempt_at
            return {"status": status, "written": written}
