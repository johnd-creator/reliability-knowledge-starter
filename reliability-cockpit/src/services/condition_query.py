"""SELECT-only evidence reads; no source clients or mutation dependencies."""
from datetime import datetime, timezone
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from src.domain.condition_evidence import (ConditionEvidence, EvidenceModel, EvidenceSources, FreshnessPolicy, PiLineage,
                                         ProjectionPlan, MAX_SIGNALS)
from src.repositories.condition_models import ConditionSignalSelectionMart, ConditionEvidenceLatestMart, ConditionProjectionStateMart
from src.repositories.mart_reader import MartQueryRepository
from src.repositories.condition_integrity import stored_selection, stored_evidence, stored_projection_state, utc_timestamp
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
                    signals=tuple(stored_selection(r, mapping.id) for r in selections))
                rows = list(session.scalars(select(ConditionEvidenceLatestMart).where(
                    ConditionEvidenceLatestMart.mapping_id == mapping.id, ConditionEvidenceLatestMart.canonical_asset_id == asset_id,
                    ConditionEvidenceLatestMart.signal_id.in_([s.signal_id for s in plan.signals])).order_by(ConditionEvidenceLatestMart.signal_id).limit(MAX_SIGNALS)))
                attempt = session.get(ConditionProjectionStateMart, asset_id)
                state = stored_projection_state(attempt, mapping.id, rows) or {}
                last_success = datetime.fromisoformat(state["collector_last_success_at"]) if state.get("collector_last_success_at") else None
                statuses = set(state.get("statuses", ["PROJECTION_NOT_RUN"]))
                if not state and (rows or attempt is not None):
                    statuses.add("PROJECTION_ERROR")
                items = []
                selected = {s.signal_id: s for s in plan.signals}
                now = self.clock()
                for row in rows:
                    signal = selected[row.signal_id]
                    e = stored_evidence(row, asset_id, mapping.id, signal, lineage.pi)
                    source_state = self.policy.state("SOURCE", e.source_timestamp, now, component="PI_CONDITION_PROJECTION")
                    item_statuses = {e.evidence_status}
                    if source_state == "SOURCE_STALE":
                        item_statuses.add("SOURCE_STALE")
                    statuses |= item_statuses
                    projected_at = utc_timestamp(row.projected_at)
                    items.append(ConditionEvidenceItem(evidence=e, projected_at=projected_at,
                        freshness=EvidenceFreshness(collector=self.policy.state("COLLECTOR", last_success, now, component="PI_COLLECTOR"),
                            source=source_state, projection=self.policy.state("PROJECTION", projected_at, now, component="PI_CONDITION_PROJECTION") if state else "PROJECTION_UNKNOWN", mapping="MAPPING_VERIFIED"),
                        statuses=tuple(sorted(item_statuses))))
                if len(items) < len(plan.signals):
                    statuses.add("PARTIAL_SIGNAL_SET")
                return AssetConditionEvidence(canonical_asset_id=asset_id, mapping_readiness="MAPPING_VERIFIED",
                    statuses=tuple(sorted(statuses)), expected_signals=len(plan.signals), items=tuple(items),
                    latest_attempt_at=(utc_timestamp(attempt.attempted_at) if attempt and state else None), collector_last_success_at=last_success)
        except (SQLAlchemyError, ValueError, KeyError, TypeError):
            # Pending additive schema, invalid rows or query failure remain unknown.
            # Other factual routes still read their accepted unchanged tables.
            return AssetConditionEvidence(canonical_asset_id=asset_id, mapping_readiness="MAPPING_UNKNOWN", statuses=("PROJECTION_ERROR",))
