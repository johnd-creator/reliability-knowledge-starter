"""Opt-in conservative adapter. No route, environment activation or source client.

The caller supplies an existing IntegrationStatus and its independently governed
FreshnessPolicy. Rich candidate evidence stays internal; existing public shape,
PI state, mapping/Registry coverage and operational defaults are unchanged.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.integration_status import (Component,TrustState,Availability,FreshnessDimension,
    DegradedReason as Reason,IntegrationStatus)
from src.domain.projection_coverage import CoverageSnapshot,DOMAINS

@dataclass(frozen=True)
class CandidateCoverageResult:
    evidence: CoverageSnapshot
    status: IntegrationStatus
    legacy_activity_at: datetime | None = None

class ProjectionCoverageService:
    def __init__(self,reader=None,*,enabled=False,policy=None,clock=None):
        self.reader=reader; self.enabled=enabled is True
        self.policy=policy if policy is not None else FreshnessPolicy()
        self.clock=clock or (lambda:datetime.now(timezone.utc))

    def reconcile(self,status):
        now=self.clock()
        mart=next((c for c in status.components if c.component==Component.RELIABILITY_MART),None)
        legacy=mart.last_successful_activity if mart else None
        if not self.enabled:
            return CandidateCoverageResult(CoverageSnapshot.unknown(now,'DISABLED','DISABLED'),status,legacy)
        evidence=self.reader.read() if self.reader is not None else CoverageSnapshot.unknown(now,'MART_NOT_CONFIGURED','NOT_CONFIGURED')
        if mart is None: return CandidateCoverageResult(evidence,status,legacy)
        domains=evidence.domains
        times=[d.last_complete.completed_at if d.last_complete and d.last_complete_verified else None for d in domains]
        states=[self.policy.state('PROJECTION',t,now,component=Component.RELIABILITY_MART).split('_',1)[1] for t in times]
        freshness=TrustState.STALE if 'STALE' in states else TrustState.CURRENT if states and all(s=='CURRENT' for s in states) else TrustState.UNKNOWN
        observed=min((t for t in times if t is not None),default=None)
        dimension=FreshnessDimension(state=freshness,observed_at=observed,
            max_age_seconds=self.policy.threshold('PROJECTION',Component.RELIABILITY_MART))
        source=next((c for c in status.components if c.component==Component.MAXIMO),None)
        source_ready=(source is not None and source.availability==Availability.AVAILABLE and
                      source.state==TrustState.CURRENT and source.collection_freshness.state==TrustState.CURRENT and
                      self.policy.state('COLLECTOR',source.collection_freshness.observed_at,now,component=Component.MAXIMO)=='COLLECTOR_CURRENT')
        reasons=set(mart.degraded_reasons)
        if len(domains)!=len(DOMAINS) or {d.domain for d in domains}!=set(DOMAINS):
            state=TrustState.UNKNOWN; reasons.add(Reason.UNKNOWN_TIMESTAMP)
        elif evidence.capability=='BLOCKED' or any(d.reconciliation=='BLOCKED' for d in domains):
            state=TrustState.BLOCKED; reasons.add(Reason.PROJECTION_ERROR)
        elif evidence.capability!='VERIFIED' or any(d.reconciliation=='UNKNOWN' for d in domains):
            state=TrustState.UNKNOWN; reasons.add(Reason.UNKNOWN_TIMESTAMP)
        elif any(d.reconciliation!='VERIFIED' for d in domains):
            state=TrustState.DEGRADED; reasons.add(Reason.PROJECTION_ERROR)
        elif not all(d.proof_complete for d in domains):
            state=TrustState.UNKNOWN; reasons.add(Reason.UNKNOWN_TIMESTAMP)
        elif freshness==TrustState.STALE:
            state=TrustState.STALE; reasons.add(Reason.PROJECTION_STALE)
        elif freshness!=TrustState.CURRENT or not source_ready:
            state=TrustState.UNKNOWN; reasons.add(Reason.UNKNOWN_TIMESTAMP)
        else:
            state=TrustState.CURRENT
        # Candidate evidence may downgrade, never waive existing independent gates.
        if mart.state==TrustState.BLOCKED: state=TrustState.BLOCKED
        elif mart.availability==Availability.NOT_CONFIGURED: state=TrustState.NOT_CONFIGURED
        elif mart.availability!=Availability.AVAILABLE: state=TrustState.DEGRADED
        elif state==TrustState.CURRENT and mart.state!=TrustState.CURRENT: state=mart.state
        replacement=mart.model_copy(update=dict(state=state,projection_freshness=dimension,
            last_successful_activity=observed,degraded_reasons=tuple(sorted(reasons))))
        output=status.model_copy(update={'components':tuple(replacement if c.component==Component.RELIABILITY_MART else c for c in status.components)})
        return CandidateCoverageResult(evidence,output,legacy)
