"""SELECT-only evidence reads; no source clients or mutation dependencies."""
from datetime import datetime, timezone
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from src.domain.condition_evidence import (ConditionEvidence, EvidenceModel, EvidenceSources, FreshnessPolicy, PiLineage,
                                         ProjectionPlan, SignalSelection, MAX_SIGNALS)
from src.repositories.condition_models import ConditionSignalSelectionMart, ConditionEvidenceLatestMart, ConditionProjectionStateMart
from src.repositories.mart_reader import MartQueryRepository
from src.services.asset_af_mapping import mapping_from_row, resolve_asset_af_mapping

class EvidenceFreshness(EvidenceModel):
    collector: str
    source: str
    projection: str
    mapping: str

class ConditionEvidenceItem(EvidenceModel):
    evidence: ConditionEvidence
    projected_at: datetime
    freshness: EvidenceFreshness
    statuses: tuple[str, ...]

class AssetConditionEvidence(EvidenceModel):
    canonical_asset_id: str
    mapping_readiness: str
    statuses: tuple[str, ...]
    expected_signals: int = 0
    latest_attempt_at: datetime | None = None
    collector_last_success_at: datetime | None = None
    items: tuple[ConditionEvidenceItem, ...] = Field(default=(), max_length=MAX_SIGNALS)

class ConditionQueryService:
    def __init__(self, database, *, policy=None, clock=None):
        self.database = database
        self.repository = MartQueryRepository(database)
        self.policy = policy or FreshnessPolicy.from_environment()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def asset_evidence(self, asset_id):
        if self.repository.get_asset(asset_id) is None:
            return None
        try:
            resolution = resolve_asset_af_mapping(asset_id, [mapping_from_row(r) for r in self.repository.list_asset_af_mappings(asset_id)])
            mapping = resolution.selected
            if mapping is None:
                readiness = "MAPPING_AMBIGUOUS" if resolution.mapping_state == "AMBIGUOUS" else "MAPPING_UNVERIFIED"
                return AssetConditionEvidence(canonical_asset_id=asset_id, mapping_readiness=readiness, statuses=("NO_VERIFIED_MAPPING",))
            lineage = EvidenceSources(pi=PiLineage(pi_source_id=mapping.pi_source_id,
                af_server_ref=mapping.af_server_ref, af_database_ref=mapping.af_database_ref, af_element_ref=mapping.af_element_ref,
                mapping_status=mapping.mapping_status, mapping_role=mapping.mapping_role))
            with self.database.read_session() as session:
                selections = list(session.scalars(select(ConditionSignalSelectionMart).where(
                    ConditionSignalSelectionMart.mapping_id == mapping.id,
                    ConditionSignalSelectionMart.approval_status == "APPROVED").order_by(ConditionSignalSelectionMart.signal_id).limit(MAX_SIGNALS + 1)))
                if not selections:
                    return AssetConditionEvidence(canonical_asset_id=asset_id, mapping_readiness="MAPPING_VERIFIED", statuses=("NO_APPROVED_SIGNALS",))
                plan = ProjectionPlan(canonical_asset_id=asset_id, mapping_id=mapping.id, sources=lineage,
                    signals=tuple(SignalSelection.model_validate(r.definition) for r in selections))
                rows = list(session.scalars(select(ConditionEvidenceLatestMart).where(
                    ConditionEvidenceLatestMart.mapping_id == mapping.id, ConditionEvidenceLatestMart.canonical_asset_id == asset_id,
                    ConditionEvidenceLatestMart.signal_id.in_([s.signal_id for s in plan.signals])).order_by(ConditionEvidenceLatestMart.signal_id).limit(MAX_SIGNALS)))
                attempt = session.get(ConditionProjectionStateMart, asset_id)
                state = attempt.state if attempt and attempt.state.get("mapping_id") == mapping.id else {}
                last_success = datetime.fromisoformat(state["collector_last_success_at"]) if state.get("collector_last_success_at") else None
                statuses = set(state.get("statuses", ["PROJECTION_NOT_RUN"]))
                items = []
                selected = {s.signal_id: s for s in plan.signals}
                now = self.clock()
                for row in rows:
                    e = ConditionEvidence.model_validate(row.evidence)
                    signal = selected[e.signal_id]
                    if (e.sources.pi.model_dump(exclude={"attribute_ref", "attribute_name"}) != lineage.pi.model_dump() or e.mapping_id != mapping.id or e.canonical_asset_id != asset_id
                        or e.attribute_ref != signal.attribute_ref or e.semantic_name != signal.semantic_name
                        or e.provenance.selection_evidence_ref != signal.evidence_ref
                        or e.provenance.selection_approved_by != signal.approved_by
                        or e.provenance.selection_approved_at != signal.approved_at):
                        raise ValueError("stored evidence differs from active selection")
                    source_state = self.policy.state("SOURCE", e.source_timestamp, now)
                    item_statuses = {e.evidence_status}
                    if source_state == "SOURCE_STALE":
                        item_statuses.add("SOURCE_STALE")
                    statuses |= item_statuses
                    projected_at = row.projected_at
                    if projected_at.tzinfo is None:
                        projected_at = projected_at.replace(tzinfo=timezone.utc)
                    items.append(ConditionEvidenceItem(evidence=e, projected_at=projected_at,
                        freshness=EvidenceFreshness(collector=self.policy.state("COLLECTOR", last_success, now),
                            source=source_state, projection=self.policy.state("PROJECTION", projected_at, now), mapping="MAPPING_VERIFIED"),
                        statuses=tuple(sorted(item_statuses))))
                if len(items) < len(plan.signals):
                    statuses.add("PARTIAL_SIGNAL_SET")
                return AssetConditionEvidence(canonical_asset_id=asset_id, mapping_readiness="MAPPING_VERIFIED",
                    statuses=tuple(sorted(statuses)), expected_signals=len(plan.signals), items=tuple(items),
                    latest_attempt_at=(attempt.attempted_at.replace(tzinfo=timezone.utc) if attempt and state else None), collector_last_success_at=last_success)
        except (SQLAlchemyError, ValueError, KeyError, TypeError):
            # Pending additive schema, invalid rows or query failure remain unknown.
            # Other factual routes still read their accepted unchanged tables.
            return AssetConditionEvidence(canonical_asset_id=asset_id, mapping_readiness="MAPPING_UNKNOWN", statuses=("PROJECTION_ERROR",))
