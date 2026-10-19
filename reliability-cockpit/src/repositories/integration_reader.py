"""Read-only aggregate inventory of the existing canonical Mart.

Schema readiness here means query compatibility under the actual reader role.
It is not a replacement for the writer's canonical migration/checksum preflight.
"""
from collections import defaultdict
from datetime import timezone
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from src.domain.condition_evidence import PiLineage, EvidenceSources, ProjectionPlan
from src.repositories.mart_models import AssetMasterMart, ReliabilityAssetRegistryMart, AssetAfMappingMart
from src.repositories.condition_models import ConditionSignalSelectionMart, ConditionEvidenceLatestMart, ConditionProjectionStateMart
from src.services.asset_af_mapping import mapping_from_row, resolve_asset_af_mapping
from src.repositories.condition_integrity import stored_selection, stored_evidence, stored_projection_state

class IntegrationMartReader:
    def __init__(self,database): self.database=database

    def inventory(self,asset_id=None):
        result={"available":False,"governance_ready":None,"condition_ready":None,"coverage":{},
                "mapping_readiness":"UNKNOWN","source_times":[],"projection_times":[],"qualities":[],
                "projection_statuses":set(),"mart_success":None,"mart_degraded":False}
        try:
            with self.database.read_session() as s:
                ids=list(s.scalars(select(ReliabilityAssetRegistryMart.asset_ref).join(AssetMasterMart,
                    ReliabilityAssetRegistryMart.asset_ref==AssetMasterMart.canonical_id).where(
                    ReliabilityAssetRegistryMart.site_code=="BSR",ReliabilityAssetRegistryMart.organization_code=="IP",
                    AssetMasterMart.site_code=="BSR",AssetMasterMart.organization_code=="IP",
                    *([AssetMasterMart.canonical_id==asset_id] if asset_id else []))))
                result["available"]=True
                result["coverage"]["registered_assets"]=len(ids)
                result["asset_exists"] = bool(ids)
            try:
                with self.database.read_session() as s:
                    states=list(s.execute(text("SELECT projection_key, last_status, last_success_at FROM mart_projection_state WHERE projection_key IN ('asset_master','maintenance_event')")))
                # Both factual projections need recorded success. No business changedate fallback.
                result["mart_success_times"]=[r.last_success_at for r in states] if len(states)==2 else [None]
                result["mart_degraded"]=any(r.last_status!="SUCCEEDED" for r in states)
                result["mart_success"]=min((r.last_success_at for r in states if r.last_success_at),default=None) if len(states)>=2 and all(r.last_success_at for r in states) else None
                if any(isinstance(value,str) for value in result["mart_success_times"]):
                    from datetime import datetime
                    result["mart_success_times"]=[datetime.fromisoformat(value.replace("Z","+00:00")) if isinstance(value,str) else value for value in result["mart_success_times"]]
                if isinstance(result["mart_success"],str):
                    from datetime import datetime
                    result["mart_success"]=datetime.fromisoformat(result["mart_success"].replace("Z","+00:00"))
            except SQLAlchemyError: result["mart_degraded"]=True
            grouped=defaultdict(list)
            with self.database.read_session() as s:
                # Select all model columns: detects incomplete governance schema/grants.
                for row in s.scalars(select(AssetAfMappingMart).where(AssetAfMappingMart.canonical_asset_id.in_(ids))):
                    grouped[row.canonical_asset_id].append(mapping_from_row(row))
            result["governance_ready"]=True
            usable={}; ambiguous=0
            for identity in ids:
                resolution=resolve_asset_af_mapping(identity,grouped[identity])
                if resolution.mapping_state=="AMBIGUOUS": ambiguous+=1
                if resolution.selected:
                    m=resolution.selected
                    try:
                        lineage=PiLineage(pi_source_id=m.pi_source_id,af_server_ref=m.af_server_ref,
                            af_database_ref=m.af_database_ref,af_element_ref=m.af_element_ref,
                            mapping_role=m.mapping_role,mapping_status=m.mapping_status)
                    except ValueError: continue
                    usable[m.id]=(identity,lineage)
            c=result["coverage"];c.update(verified_mapping_assets=len(usable),ambiguous_mapping_assets=ambiguous)
            result["mapping_readiness"]="AMBIGUOUS" if ambiguous else "UNMAPPED" if not usable else "VERIFIED" if len(usable)==len(ids) else "PARTIAL"
            approved={};count_by_mapping=defaultdict(int);signals_by_mapping=defaultdict(list)
            with self.database.read_session() as s:
                # Probe all three relations, even if no mapping exists. Empty != missing schema.
                for model in (ConditionSignalSelectionMart,ConditionEvidenceLatestMart,ConditionProjectionStateMart):
                    s.execute(select(model).limit(0))
                for row in s.scalars(select(ConditionSignalSelectionMart).where(
                    ConditionSignalSelectionMart.mapping_id.in_(usable),ConditionSignalSelectionMart.approval_status=="APPROVED")):
                    definition=stored_selection(row, row.mapping_id)
                    approved[row.signal_id]=definition;count_by_mapping[row.mapping_id]+=1
                    signals_by_mapping[row.mapping_id].append(definition)
                for mapping_id, signals in signals_by_mapping.items():
                    identity,lineage=usable[mapping_id]
                    ProjectionPlan(canonical_asset_id=identity, mapping_id=mapping_id,
                        sources=EvidenceSources(pi=lineage), signals=tuple(signals))
                projected_assets=set(); projected_signals=0; evidence_by_mapping=defaultdict(list)
                for row in s.scalars(select(ConditionEvidenceLatestMart).where(ConditionEvidenceLatestMart.signal_id.in_(approved))):
                    definition=approved[row.signal_id];identity,lineage=usable[definition.mapping_id]
                    e=stored_evidence(row, identity, definition.mapping_id, definition, lineage)
                    evidence_by_mapping[definition.mapping_id].append(row)
                    projected_assets.add(identity);projected_signals+=1
                    result["source_times"].append(e.source_timestamp)
                    result["projection_times"].append(row.projected_at)
                    result["qualities"].append(e.evidence_status)
                states={row.canonical_asset_id:row for row in s.scalars(select(ConditionProjectionStateMart).where(ConditionProjectionStateMart.canonical_asset_id.in_(ids)))}
                for mapping_id,(identity,_) in usable.items():
                    if not count_by_mapping.get(mapping_id): continue
                    state=stored_projection_state(states.get(identity), mapping_id, evidence_by_mapping[mapping_id])
                    if state is not None:
                        result["projection_statuses"].update(state["statuses"])
                    elif identity in projected_assets or identity in states:
                        # Evidence may survive a partial restore while its attestation
                        # is missing or bound to another mapping. Retain its counts and
                        # original source time, but never infer a complete/current run.
                        result["projection_statuses"].add("PROJECTION_ERROR")
                        result["projection_times"].append(None)
            result["condition_ready"]=True
            c.update(approved_signal_assets=len(count_by_mapping),approved_signals=len(approved),projected_assets=len(projected_assets),projected_signals=projected_signals)
        except (SQLAlchemyError,ValueError,KeyError,TypeError):
            if result["governance_ready"] is None and result["available"]: result["governance_ready"]=False
            elif result["governance_ready"]: result["condition_ready"]=False
            # Unknown counts remain null, never pretend a missing schema has zero evidence.
        return result
