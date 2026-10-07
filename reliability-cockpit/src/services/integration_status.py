"""Independent trust dimensions derived exclusively from accepted local evidence."""
import os
from datetime import datetime, timezone
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.integration_status import (Component, TrustState, Availability, MappingReadiness, Quality,
    DegradedReason as Reason, FreshnessDimension, CoverageSummary, IntegrationComponentStatus, IntegrationStatus)
from src.repositories.integration_reader import IntegrationMartReader
from src.adapters.integration_observations import LocalCollectorObservations

class IntegrationStatusService:
    def __init__(self,database=None,*,observations=None,policy=None,clock=None):
        self.database=database
        self._owns_observations=observations is None
        self.observations=observations or LocalCollectorObservations(os.getenv("MAXIMO_COLLECTOR_API_BASE"),os.getenv("PI_COLLECTOR_API_BASE"))
        self.policy=policy or FreshnessPolicy.from_environment()
        self.clock=clock or (lambda:datetime.now(timezone.utc))

    def freshness(self,dimension,times):
        now=self.clock();threshold=getattr(self.policy,dimension.lower()+"_max_age_seconds")
        times=[t.replace(tzinfo=timezone.utc) if t is not None and t.tzinfo is None else t for t in times]
        states=[self.policy.state(dimension,t,now).split("_",1)[1] for t in times]
        state=TrustState.STALE if "STALE" in states else TrustState.CURRENT if states and all(s=="CURRENT" for s in states) else TrustState.UNKNOWN
        return FreshnessDimension(state=state,observed_at=min((t for t in times if t),default=None),max_age_seconds=threshold)

    @staticmethod
    def _state(reasons,freshness,availability):
        if availability==Availability.NOT_CONFIGURED:return TrustState.NOT_CONFIGURED
        if availability==Availability.UNAVAILABLE:return TrustState.DEGRADED
        if reasons & {Reason.HUMAN_CROSSWALK_REQUIRED,Reason.AMBIGUOUS_MAPPING,Reason.NO_APPROVED_SIGNALS,Reason.CONDITION_SCHEMA_NOT_READY,Reason.GOVERNANCE_SCHEMA_NOT_READY}:return TrustState.BLOCKED
        if any(f.state==TrustState.STALE for f in freshness):return TrustState.STALE
        if reasons & {Reason.BAD_QUALITY,Reason.PARTIAL_SIGNAL_SET,Reason.SOURCE_UNAVAILABLE,Reason.PROJECTION_ERROR,Reason.COLLECTOR_ERRORS,Reason.PARTIAL_MAPPING_COVERAGE}:return TrustState.DEGRADED
        if reasons or availability!=Availability.AVAILABLE:return TrustState.UNKNOWN
        return TrustState.CURRENT if freshness and all(f.state==TrustState.CURRENT for f in freshness) else TrustState.UNKNOWN

    def status(self,asset_id=None):
        try:
            mx,pi=self.observations.maximo(),self.observations.pi()
        finally:
            if self._owns_observations: self.observations.close()
        inventory=IntegrationMartReader(self.database).inventory(asset_id) if self.database else {"available":False,"coverage":{},"governance_ready":None,"condition_ready":None,"mapping_readiness":"UNKNOWN"}
        components=[]
        c=dict(inventory["coverage"]);c.update(technical_registry_total=pi.registry_total,technical_registry_active=pi.registry_active,technical_snapshots=pi.snapshots)
        for component,observation in ((Component.MAXIMO,mx),(Component.PI_COLLECTOR,pi)):
            collection=self.freshness("COLLECTOR",[observation.last_successful_activity]);reasons=set()
            if observation.availability!=Availability.AVAILABLE:reasons.add(Reason.COLLECTOR_UNAVAILABLE if observation.availability==Availability.UNAVAILABLE else Reason.COLLECTOR_OBSERVATION_UNAVAILABLE)
            if observation.last_successful_activity is None:reasons.add(Reason.NO_SUCCESSFUL_ACTIVITY)
            if observation.errors:reasons.add(Reason.COLLECTOR_ERRORS)
            if component==Component.MAXIMO and observation.cursor_present is not True:reasons.add(Reason.CURSOR_MISSING)
            if collection.state==TrustState.STALE:reasons.add(Reason.COLLECTION_STALE)
            source=FreshnessDimension();quality=Quality.UNKNOWN
            if component==Component.PI_COLLECTOR:
                times=[observation.oldest_source_timestamp]
                if observation.unknown_source_timestamps is None or observation.unknown_source_timestamps or observation.future_source_timestamps is None or observation.future_source_timestamps or observation.snapshots!=observation.registry_active:times.append(None)
                source=self.freshness("SOURCE",times)
                if source.state==TrustState.STALE:reasons.add(Reason.SOURCE_STALE)
                quality=Quality.BAD if observation.bad_quality_signals else Quality.UNKNOWN if observation.unknown_quality_signals is None or observation.unknown_quality_signals or not observation.snapshots else Quality.GOOD
                if quality==Quality.BAD:reasons.add(Reason.BAD_QUALITY)
                if quality==Quality.UNKNOWN:reasons.add(Reason.UNKNOWN_QUALITY)
                if observation.snapshots!=observation.registry_active:reasons.add(Reason.PARTIAL_SIGNAL_SET)
            components.append(IntegrationComponentStatus(component=component,availability=observation.availability,
                state=self._state(reasons,[collection],observation.availability),collection_freshness=collection,source_freshness=source,quality=quality,
                last_successful_activity=observation.last_successful_activity,degraded_reasons=tuple(sorted(reasons))))
        availability=Availability.AVAILABLE if inventory["available"] else Availability.UNAVAILABLE if self.database else Availability.NOT_CONFIGURED
        martfresh=self.freshness("PROJECTION",inventory.get("mart_success_times",[inventory.get("mart_success")]));reasons=set()
        if availability!=Availability.AVAILABLE:reasons.add(Reason.MART_UNAVAILABLE if self.database else Reason.MART_NOT_CONFIGURED)
        if inventory.get("mart_degraded"):reasons.add(Reason.PROJECTION_ERROR)
        if martfresh.state==TrustState.STALE:reasons.add(Reason.PROJECTION_STALE)
        components.append(IntegrationComponentStatus(component=Component.RELIABILITY_MART,availability=availability,
            state=self._state(reasons,[martfresh],availability),projection_freshness=martfresh,last_successful_activity=martfresh.observed_at,degraded_reasons=tuple(sorted(reasons))))
        readiness=MappingReadiness(inventory["mapping_readiness"]);reasons=set()
        if inventory["governance_ready"] is not True:reasons.add(Reason.GOVERNANCE_SCHEMA_NOT_READY)
        if readiness==MappingReadiness.UNMAPPED:reasons.add(Reason.HUMAN_CROSSWALK_REQUIRED)
        if readiness==MappingReadiness.AMBIGUOUS:reasons.add(Reason.AMBIGUOUS_MAPPING)
        if readiness==MappingReadiness.PARTIAL:reasons.add(Reason.PARTIAL_MAPPING_COVERAGE)
        components.append(IntegrationComponentStatus(component=Component.ASSET_AF_MAPPING,availability=availability,
            state=TrustState.CURRENT if readiness==MappingReadiness.VERIFIED and not reasons else self._state(reasons,[],availability),mapping_readiness=readiness,degraded_reasons=tuple(sorted(reasons))))
        projection=self.freshness("PROJECTION",inventory.get("projection_times",[]));source=self.freshness("SOURCE",inventory.get("source_times",[]));reasons=set()
        if inventory["condition_ready"] is not True:reasons.add(Reason.CONDITION_SCHEMA_NOT_READY)
        if readiness==MappingReadiness.UNMAPPED:reasons.add(Reason.HUMAN_CROSSWALK_REQUIRED)
        if readiness==MappingReadiness.AMBIGUOUS:reasons.add(Reason.AMBIGUOUS_MAPPING)
        if not c.get("approved_signals"):reasons.add(Reason.NO_APPROVED_SIGNALS)
        if not c.get("projected_signals"):reasons.add(Reason.NO_PROJECTED_EVIDENCE)
        if c.get("approved_signals") and c.get("projected_signals",0)<c["approved_signals"]:reasons.add(Reason.PARTIAL_SIGNAL_SET)
        for status in inventory.get("projection_statuses",set()):
            if status in {"SOURCE_UNAVAILABLE","PROJECTION_ERROR","PARTIAL_SIGNAL_SET"}:reasons.add(Reason(status))
        if source.state==TrustState.STALE:reasons.add(Reason.SOURCE_STALE)
        if projection.state==TrustState.STALE:reasons.add(Reason.PROJECTION_STALE)
        qualities=inventory.get("qualities",[])
        quality=Quality.BAD if "BAD_QUALITY" in qualities else Quality.UNKNOWN if not qualities or any(q!="EVIDENCE_AVAILABLE" for q in qualities) else Quality.GOOD
        if quality==Quality.BAD:reasons.add(Reason.BAD_QUALITY)
        if quality==Quality.UNKNOWN:reasons.add(Reason.UNKNOWN_QUALITY)
        components.append(IntegrationComponentStatus(component=Component.PI_CONDITION_PROJECTION,availability=availability,
            state=self._state(reasons,[projection,source],availability),source_freshness=source,projection_freshness=projection,
            mapping_readiness=readiness,quality=quality,last_successful_activity=projection.observed_at,degraded_reasons=tuple(sorted(reasons))))
        return IntegrationStatus(observed_at=self.clock(),canonical_asset_id=asset_id,governance_schema_ready=inventory["governance_ready"],
            condition_schema_ready=inventory["condition_ready"],coverage=CoverageSummary(**c),components=tuple(components))
