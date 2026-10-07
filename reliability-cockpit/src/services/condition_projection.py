"""Trusted local orchestration port; no PI client/config/credentials in NADI."""
from typing import Protocol
from src.domain.condition_evidence import EvidenceBatch, ProjectionPlan, SignalResult
from src.repositories.condition_store import ConditionCommandStore

class GovernedEvidenceSource(Protocol):
    def collect(self, plan: ProjectionPlan) -> EvidenceBatch: ...

class EvidenceDocumentSource:
    """Operator handoff emitted by the collector-owned governed adapter.

    Private controlled files only, never an HTTP request body or public API.
    Writer re-resolves governance after handoff and compares the whole plan.
    """
    def __init__(self, document: dict):
        self.batch = EvidenceBatch.model_validate(document)

    def collect(self, plan):
        if self.batch.plan != plan:
            raise ValueError("collector document differs from current approved plan")
        return self.batch

class ConditionProjectionService:
    def __init__(self, store: ConditionCommandStore, source: GovernedEvidenceSource):
        self.store, self.source = store, source

    def project(self, asset_id, *, now=None):
        plan = self.store.plan(asset_id)  # No source operation before identity/approval gate.
        try:
            batch = self.source.collect(plan)
        except Exception:
            batch = EvidenceBatch(plan=plan, results=tuple(SignalResult(signal_id=s.signal_id, status="PROJECTION_ERROR") for s in plan.signals))
        return self.store.project(batch, now=now)  # Atomic governance recheck + latest upsert.
