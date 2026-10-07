"""Pure gate evaluator; no source access, DDL, mapping promotion or service control."""
from src.domain.integration_status import Component,IntegrationStatus,TrustState,Availability
from src.domain.phase1_readiness import GateId as Id,GateReason as Reason,Verdict,ReadinessGate,Phase1Readiness


def phase1_readiness(status:IntegrationStatus,*,evidence_origin="LOCAL_RUNTIME"):
    status=IntegrationStatus.model_validate(status.model_dump(mode="json"))
    components={component.component:component for component in status.components};gates=[]
    def gate(identity,verdict,reason):
        result=ReadinessGate(gate=identity,verdict=verdict,reason=reason);gates.append(result);return result
    for identity,component,dimension in ((Id.MAXIMO,Component.MAXIMO,"collection_freshness"),
        (Id.MART,Component.RELIABILITY_MART,"projection_freshness"),(Id.PI_COLLECTOR,Component.PI_COLLECTOR,"collection_freshness")):
        observation=components.get(component)
        if observation is None or observation.availability!=Availability.AVAILABLE:
            gate(identity,Verdict.UNKNOWN,Reason.LOCAL_EVIDENCE_UNAVAILABLE);continue
        freshness=getattr(observation,dimension)
        # A stale technical PI source timestamp does not invalidate the collector
        # activity gate. Source quality/freshness is independently checked below.
        collector_errors=set(observation.degraded_reasons)&{"COLLECTOR_ERRORS","CURSOR_MISSING","NO_SUCCESSFUL_ACTIVITY","PROJECTION_ERROR"}
        if component==Component.PI_COLLECTOR and (not status.coverage.technical_registry_active or status.coverage.technical_snapshots is None or status.coverage.technical_snapshots<status.coverage.technical_registry_active):
            gate(identity,Verdict.PARTIAL,Reason.PARTIAL_SIGNAL_SET);continue
        if collector_errors:gate(identity,Verdict.PARTIAL,Reason.LOCAL_EVIDENCE_DEGRADED)
        elif freshness.state==TrustState.STALE:gate(identity,Verdict.PARTIAL,Reason.LOCAL_EVIDENCE_STALE)
        elif freshness.state==TrustState.CURRENT:gate(identity,Verdict.PASS,Reason.LOCAL_EVIDENCE_CURRENT)
        else:gate(identity,Verdict.UNKNOWN,Reason.UNKNOWN_FRESHNESS_POLICY if freshness.max_age_seconds is None else Reason.UNKNOWN_TIMESTAMP)
    for identity,ready,reason in ((Id.GOVERNANCE,status.governance_schema_ready,Reason.GOVERNANCE_SCHEMA_NOT_READY),
        (Id.CONDITION_SCHEMA,status.condition_schema_ready,Reason.CONDITION_SCHEMA_NOT_READY)):
        gate(identity,Verdict.PASS if ready is True else Verdict.BLOCKED if ready is False else Verdict.UNKNOWN,
             Reason.READER_SCHEMA_COMPATIBLE if ready else reason)
    coverage=status.coverage
    # Initial governed pilot readiness requires at least one usable identity, not
    # unreviewed full-registry mapping. Any ambiguity in this scope blocks it.
    if coverage.ambiguous_mapping_assets:
        mapping=gate(Id.MAPPING,Verdict.BLOCKED,Reason.AMBIGUOUS_MAPPING)
    elif coverage.verified_mapping_assets is None:
        mapping=gate(Id.MAPPING,Verdict.UNKNOWN,Reason.UNKNOWN_MAPPING_READINESS)
    elif coverage.verified_mapping_assets==0:
        mapping=gate(Id.MAPPING,Verdict.BLOCKED,Reason.HUMAN_CROSSWALK_REQUIRED)
    else:mapping=gate(Id.MAPPING,Verdict.PASS,Reason.VERIFIED_PILOT_AVAILABLE)
    if mapping.verdict!=Verdict.PASS:
        signals=gate(Id.SIGNAL_SELECTION,mapping.verdict,mapping.reason)
    elif status.condition_schema_ready is not True:
        signals=gate(Id.SIGNAL_SELECTION,Verdict.BLOCKED,Reason.CONDITION_SCHEMA_NOT_READY)
    elif not coverage.approved_signals or not coverage.approved_signal_assets:
        signals=gate(Id.SIGNAL_SELECTION,Verdict.BLOCKED,Reason.NO_APPROVED_SIGNALS)
    else:signals=gate(Id.SIGNAL_SELECTION,Verdict.PASS,Reason.APPROVED_PILOT_SIGNALS_AVAILABLE)
    projection=components.get(Component.PI_CONDITION_PROJECTION)
    if mapping.verdict!=Verdict.PASS:gate(Id.CONDITION_PROJECTION,mapping.verdict,mapping.reason)
    elif signals.verdict!=Verdict.PASS:gate(Id.CONDITION_PROJECTION,signals.verdict,signals.reason)
    elif projection is None or projection.availability!=Availability.AVAILABLE:
        gate(Id.CONDITION_PROJECTION,Verdict.UNKNOWN,Reason.LOCAL_EVIDENCE_UNAVAILABLE)
    elif not coverage.projected_assets or not coverage.projected_signals:
        gate(Id.CONDITION_PROJECTION,Verdict.BLOCKED,Reason.PROJECTION_NOT_AVAILABLE)
    elif coverage.projected_signals<coverage.approved_signals or coverage.projected_assets<coverage.approved_signal_assets:
        gate(Id.CONDITION_PROJECTION,Verdict.PARTIAL,Reason.PARTIAL_SIGNAL_SET)
    elif projection.source_freshness.state==TrustState.STALE:
        gate(Id.CONDITION_PROJECTION,Verdict.PARTIAL,Reason.SOURCE_STALE)
    elif projection.projection_freshness.state==TrustState.STALE:
        gate(Id.CONDITION_PROJECTION,Verdict.PARTIAL,Reason.PROJECTION_STALE)
    elif projection.source_freshness.state!=TrustState.CURRENT or projection.projection_freshness.state!=TrustState.CURRENT:
        gate(Id.CONDITION_PROJECTION,Verdict.UNKNOWN,Reason.UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS)
    elif projection.quality!="GOOD":gate(Id.CONDITION_PROJECTION,Verdict.PARTIAL,Reason.QUALITY_NOT_ACCEPTED)
    elif projection.state!=TrustState.CURRENT:gate(Id.CONDITION_PROJECTION,Verdict.PARTIAL,Reason.PROJECTION_DEGRADED)
    else:gate(Id.CONDITION_PROJECTION,Verdict.PASS,Reason.COMPLETE_PILOT_PROJECTION)
    valid=set(components)==set(Component) and len(components)==len(status.components)
    gate(Id.INTEGRATION_STATUS,Verdict.PASS if valid else Verdict.UNKNOWN,Reason.STATUS_CONTRACT_VALID if valid else Reason.STATUS_CONTRACT_INVALID)
    verdict=Verdict.BLOCKED if any(g.verdict==Verdict.BLOCKED for g in gates) else Verdict.UNKNOWN if any(g.verdict==Verdict.UNKNOWN for g in gates) else Verdict.PARTIAL if any(g.verdict==Verdict.PARTIAL for g in gates) else Verdict.PASS
    return Phase1Readiness(observed_at=status.observed_at,evidence_origin=evidence_origin,verdict=verdict,gates=tuple(gates),coverage=coverage)
