"use client";
import { idText, statusLabel } from "../lib/id-copy";
import Link from "next/link";
import type { AssetView, ContextView } from "../lib/api";
import { formatDate } from "../lib/format";
import { EmptyState, HelpDetails, SectionCard, StatCard, StatusBadge, TableFrame } from "./ui";

export default function AssetHealthSummary({asset, context, maintenanceCount, assessmentCount, onMaintenance}: {asset:AssetView; context:ContextView|null; maintenanceCount:number|null; assessmentCount:number|null; onMaintenance:()=>void}) {
 return <div className="asset-health-workspace">
  <section aria-label={idText("Health Summary")} className="stat-grid asset-summary-grid">
   <StatCard label={idText("Health score")} value="NOT ASSESSED" detail={idText("Engineering rules and evidence approval pending")} />
   <StatCard label="Criticality" value="UNKNOWN" detail={idText("No approved classification in this contract")} />
   <StatCard label={idText("Last failure")} value="UNKNOWN" detail={idText("Maintenance activity is not failure identity")} />
   <StatCard label={idText("Maintenance records")} value={maintenanceCount ?? "UNKNOWN"} detail={idText("All related Mart events; not open WO or failure count")} tone="accent" />
   <StatCard label={idText("Assessment records")} value={assessmentCount ?? "UNKNOWN"} detail={idText("Record availability, not condition")} />
  </section>
  <div className="asset-reference-grid">
   <SectionCard><div className="section-heading"><h2>{idText("Technical Details")}</h2><span className="dataset-badge compact">{idText("Governed asset DTO")}</span></div>
    <dl className="asset-facts">{[[idText("Canonical identity"),asset.canonical_id],[idText("Source asset"),asset.source_asset_number],[idText("Description"),asset.description],[idText("Location"),asset.location_ref],[idText("Asset type"),asset.asset_type],[idText("Plant"),asset.plant],[idText("Unit"),asset.unit],["Scope",`${asset.site_code} / ${asset.organization_code}`],[idText("Source record updated"),formatDate(asset.source_updated_at)]].map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value ?? "UNKNOWN"}</dd></div>)}</dl>
    <HelpDetails title="Batas informasi teknis"><p>{idText("Operating condition, manufacturer, rating and serial number are UNKNOWN where absent from the governed contract. Source status does not establish operating condition.")}</p></HelpDetails>
   </SectionCard>
   <SectionCard><div className="section-heading"><h2>{idText("PdM Condition Summary")}</h2><Link className="text-link" href="/pdm">{idText("Open PdM Center →")}</Link></div>
    <TableFrame minWidth={430} label={idText("Candidate method evidence availability")}><table><thead><tr><th>{idText("Candidate method")}</th><th>{idText("Assessment / coverage")}</th></tr></thead><tbody>{["Vibration","IR Thermography","MCSA","Tribology"].map(method=><tr key={method}><td>{method}</td><td>{statusLabel("NOT ASSESSED")}<small className="table-subtext">{idText("Operational manual measurement contract unavailable")}</small></td></tr>)}</tbody></table></TableFrame>
    <p className="section-note">{idText("Candidate definitions await engineer validation. Governed PI source evidence below stays separate from portable PdM.")}</p>
   </SectionCard>
   <SectionCard><div className="section-heading"><h2>{idText("Maintenance / Work Order History")}</h2><button type="button" className="button tertiary" onClick={onMaintenance}>{idText("View all records →")}</button></div>
    {!context ? <EmptyState title={idText("Maintenance context UNAVAILABLE")} detail={idText("Asset identity remains available; retry or use the Maintenance tab.")} /> : context.maintenance.length === 0 ? <EmptyState title={idText("No related maintenance records returned.")} detail={idText("This does not prove no failures occurred.")} /> : <TableFrame minWidth={580} label={idText("Related maintenance chronology")}><table><thead><tr><th>{idText("Existing WO reference")}</th><th>{idText("Source status")}</th><th>{idText("Activity time")}</th></tr></thead><tbody>{context.maintenance.map(row=><tr key={row.canonical_id}><td>{row.work_order_id ?? "NOT LINKED"}<small className="table-subtext">{row.event_type ?? "UNKNOWN"}</small></td><td><StatusBadge value={row.status ?? "UNKNOWN"} mode="raw-neutral" /></td><td>{formatDate(row.actual_start ?? row.source_changed_at)}<small className="table-subtext">{idText("Actual start, otherwise source changed time")}</small></td></tr>)}</tbody></table></TableFrame>}
    <p className="section-note">{idText("Recent context only; complete asset-scoped chronology is paginated in the existing tabs. No inferred monthly totals, failure counts or open/closed classification.")}</p>
   </SectionCard>
   <SectionCard><div className="section-heading"><h2>{idText("Recommendations / Actions")}</h2><Link className="text-link" href="/recommendations">{idText("Open Recommendations →")}</Link></div>
    <EmptyState title={idText("Operational recommendation linkage UNAVAILABLE")} detail={idText("The current NADI-owned application HTTP contract is isolated Engineering QA. Synthetic records are not joined to this factual asset.")} />
    <p className="section-note">{idText("Recommendations remain NADI-owned. Existing Maximo WOs are informational read-only references.")}</p>
   </SectionCard>
  </div>
 </div>;
}
