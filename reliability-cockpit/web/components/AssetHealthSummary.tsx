"use client";
import Link from "next/link";
import type { AssetView, ContextView } from "../lib/api";
import { formatDate } from "../lib/format";
import { EmptyState, SectionCard, StatCard, StatusBadge, TableFrame } from "./ui";

export default function AssetHealthSummary({asset, context, maintenanceCount, assessmentCount, onMaintenance}: {asset:AssetView; context:ContextView|null; maintenanceCount:number|null; assessmentCount:number|null; onMaintenance:()=>void}) {
 return <div className="asset-health-workspace">
  <section aria-label="Health Summary" className="stat-grid asset-summary-grid">
   <StatCard label="Health score" value="NOT ASSESSED" detail="Engineering rules and evidence approval pending" />
   <StatCard label="Criticality" value="UNKNOWN" detail="No approved classification in this contract" />
   <StatCard label="Last failure" value="UNKNOWN" detail="Maintenance activity is not failure identity" />
   <StatCard label="Maintenance records" value={maintenanceCount ?? "UNKNOWN"} detail="All related Mart events; not open WO or failure count" tone="accent" />
   <StatCard label="Assessment records" value={assessmentCount ?? "UNKNOWN"} detail="Record availability, not condition" />
  </section>
  <div className="asset-reference-grid">
   <SectionCard><div className="section-heading"><h2>Technical Details</h2><span className="dataset-badge compact">Governed asset DTO</span></div>
    <dl className="asset-facts">{[["Canonical identity",asset.canonical_id],["Source asset",asset.source_asset_number],["Description",asset.description],["Location",asset.location_ref],["Asset type",asset.asset_type],["Plant",asset.plant],["Unit",asset.unit],["Scope",`${asset.site_code} / ${asset.organization_code}`],["Source record updated",formatDate(asset.source_updated_at)]].map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value ?? "UNKNOWN"}</dd></div>)}</dl>
    <p className="section-note">Operating condition, manufacturer, rating and serial number are UNKNOWN where absent from the governed contract. Source status does not establish operating condition.</p>
   </SectionCard>
   <SectionCard><div className="section-heading"><h2>PdM Condition Summary</h2><Link className="text-link" href="/pdm">Open PdM Center →</Link></div>
    <TableFrame minWidth={430} label="Candidate method evidence availability"><table><thead><tr><th>Candidate method</th><th>Assessment / coverage</th></tr></thead><tbody>{["Vibration","IR Thermography","MCSA","Tribology"].map(method=><tr key={method}><td>{method}</td><td>NOT ASSESSED<small className="table-subtext">Operational manual measurement contract unavailable</small></td></tr>)}</tbody></table></TableFrame>
    <p className="section-note">Candidate definitions await engineer validation. Governed PI source evidence below stays separate from portable PdM.</p>
   </SectionCard>
   <SectionCard><div className="section-heading"><h2>Maintenance / Work Order History</h2><button type="button" className="text-link-button" onClick={onMaintenance}>View all records →</button></div>
    {!context ? <EmptyState title="Maintenance context UNAVAILABLE" detail="Asset identity remains available; retry or use the Maintenance tab." /> : context.maintenance.length === 0 ? <EmptyState title="No related maintenance records returned." detail="This does not prove no failures occurred." /> : <TableFrame minWidth={580} label="Related maintenance chronology"><table><thead><tr><th>Existing WO reference</th><th>Source status</th><th>Activity time</th></tr></thead><tbody>{context.maintenance.map(row=><tr key={row.canonical_id}><td>{row.work_order_id ?? "NOT LINKED"}<small className="table-subtext">{row.event_type ?? "UNKNOWN"}</small></td><td><StatusBadge value={row.status ?? "UNKNOWN"} mode="raw-neutral" /></td><td>{formatDate(row.actual_start ?? row.source_changed_at)}<small className="table-subtext">Actual start, otherwise source changed time</small></td></tr>)}</tbody></table></TableFrame>}
    <p className="section-note">Recent context only; complete asset-scoped chronology is paginated in the existing tabs. No inferred monthly totals, failure counts or open/closed classification.</p>
   </SectionCard>
   <SectionCard><div className="section-heading"><h2>Recommendations / Actions</h2><Link className="text-link" href="/recommendations">Open Recommendations →</Link></div>
    <EmptyState title="Operational recommendation linkage UNAVAILABLE" detail="The current NADI-owned application HTTP contract is isolated Engineering QA. Synthetic records are not joined to this factual asset." />
    <p className="section-note">Recommendations remain NADI-owned. Existing Maximo WOs are informational read-only references.</p>
   </SectionCard>
  </div>
 </div>;
}
