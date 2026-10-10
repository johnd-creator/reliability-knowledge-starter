"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type DecisionOverviewView } from "../lib/api";
import { formatNumber } from "../lib/format";
import { attentionItems, factualMetric as metric, overviewDate } from "../lib/overview";
import { Breadcrumbs, Button, DataMaturity, EmptyState, ErrorState, LoadingState, PageHeader, SectionCard, StatCard, TableFrame } from "./ui";
import { NavIcon } from "./AppNavigation";

const WINDOWS = [7, 30, 90] as const;
type WindowDays = (typeof WINDOWS)[number];
const factualCount = (value: number | null | undefined) => value != null && Number.isFinite(value) ? formatNumber(value) : "UNKNOWN";

export function Distribution({ title, rows }: { title: string; rows: DecisionOverviewView["status_distribution"] }) {
  const maximum = Math.max(...rows.filter(row => ["VERIFIED", "DERIVED_SAFE"].includes(row.count.evidence_class) && Number.isFinite(row.count.value)).map(row => row.count.value), 0);
  if (!rows.length) return <EmptyState title={`No ${title.toLowerCase()} in this window.`} />;
  return <div className="distribution-list">{rows.map(row => <div className="distribution-row" key={row.value}><div className="distribution-label"><span>{row.value || "UNKNOWN"}</span><strong>{metric(row.count)}</strong></div><div className="distribution-track" aria-hidden="true"><span style={{ width: `${maximum && ["VERIFIED", "DERIVED_SAFE"].includes(row.count.evidence_class) && Number.isFinite(row.count.value) ? (row.count.value / maximum) * 100 : 0}%` }} /></div></div>)}</div>;
}

export function ActivityChart({ rows }: { rows: DecisionOverviewView["maintenance_activity"] }) {
  const supported = rows.filter(row => ["VERIFIED", "DERIVED_SAFE"].includes(row.event_count.evidence_class) && Number.isFinite(row.event_count.value));
  const maximum = Math.max(...supported.map(row => row.event_count.value), 0);
  if (!rows.length) return <EmptyState title="No maintenance activity trend available." detail="An empty activity series does not establish equipment condition." />;
  return <figure className="activity-figure"><figcaption>Registered-asset maintenance events per week · counts, not failures or condition scores</figcaption><div className="chart-scroll" role="region" aria-label="Weekly maintenance activity chart, scroll for all periods" tabIndex={0}><div className="trend-chart">{rows.map(row => <div className="trend-column" key={row.period_start} title={`${overviewDate(row.period_start)}: ${metric(row.event_count)} events`}><strong>{metric(row.event_count)}</strong><div className="trend-track" aria-hidden="true"><span style={{ height: `${maximum && supported.includes(row) ? (row.event_count.value / maximum) * 100 : 0}%` }} /></div><small>{Number.isFinite(Date.parse(row.period_start)) ? new Date(row.period_start).toLocaleDateString("id-ID", {day:"2-digit", month:"short"}) : "UNKNOWN"}</small></div>)}</div></div><p className="chart-scroll-hint">Scroll horizontally for all {rows.length} periods; exact counts are available below.</p><details className="chart-values"><summary>View exact periods and counts</summary><TableFrame minWidth={550} label="Weekly maintenance counts"><table><thead><tr><th>Period start</th><th>Period end</th><th>Events</th><th>Evidence</th></tr></thead><tbody>{rows.map(row => <tr key={row.period_start}><td>{overviewDate(row.period_start)}</td><td>{overviewDate(row.period_end)}</td><td>{metric(row.event_count)}</td><td>{row.event_count.evidence_class}</td></tr>)}</tbody></table></TableFrame></details></figure>;
}

export default function ExecutiveOverview() {
  const [windowDays, setWindowDays] = useState<WindowDays>(30);
  const [data, setData] = useState<DecisionOverviewView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allActivity, setAllActivity] = useState(false);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setAllActivity(false);
    setError(null);
    reliabilityApi.decisionOverview(windowDays).then(next => {
      if (!cancelled) { setData(next); setError(null); }
    }).catch(() => {
      if (!cancelled) { setData(null); setError("Reliability Mart unavailable"); }
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [windowDays, retry]);
  const current = !loading && !error ? data : null;
  return <>
    <Breadcrumbs items={[{label:"NADI"}, {label:"Executive Overview"}]} />
    <PageHeader eyebrow="Factual reliability workspace" title="Executive Overview" description="Registered assets and maintenance evidence for the BSR / IP operating scope." />
    <section className="overview-filter-bar" aria-label="Executive Overview context"><div><span className="filter-caption">Operating scope</span><strong>BSR / IP</strong></div><div><span className="filter-caption">Population</span><Link href="/assets">Registered Reliability Assets →</Link></div><label className="window-select">Maintenance activity window<select value={windowDays} onChange={event => setWindowDays(Number(event.target.value) as WindowDays)}>{WINDOWS.map(days => <option key={days} value={days}>{days} days</option>)}</select></label><div className="overview-query-time"><span className="filter-caption">Query as of · not source freshness</span><time dateTime={current?.as_of}>{overviewDate(current?.as_of)}</time></div></section>
    <div className="scope-banner trust-strip"><span className="dataset-badge">MIXED DATA MATURITY</span><DataMaturity state={current?.data_maturity.asset_maintenance ?? "UNKNOWN"} /><DataMaturity state={current?.data_maturity.controlled_domains ?? "UNKNOWN"} /><span>Equipment condition: NOT ASSESSED by this dashboard</span></div>
    {loading && <LoadingState label="Reading Executive Overview aggregates…" />}
    {!loading && error && <ErrorState message={error} onRetry={() => setRetry(value => value + 1)} />}
    {!loading && !error && data && <>
      <section className="stat-grid overview-stat-grid" aria-label="Factual KPI overview">
        <StatCard label="Registered Reliability Assets" value={metric(data.summary.registered_assets)} detail={`Registry count · ${data.summary.registered_assets.evidence_class}`} tone="accent" />
        <StatCard label="Maintenance Activity 7d" value={metric(data.summary.maintenance_activity_7d)} detail={`Registry-scoped · ${data.summary.maintenance_activity_7d.evidence_class}`} />
        <StatCard label="Maintenance Activity 30d" value={metric(data.summary.maintenance_activity_30d)} detail={`Registry-scoped · ${data.summary.maintenance_activity_30d.evidence_class}`} />
        <StatCard label="Assets with Activity 30d" value={metric(data.summary.assets_active_30d)} detail={`Distinct registered Asset refs · ${data.summary.assets_active_30d.evidence_class}`} />
        <StatCard label="Maintenance Activity 90d" value={metric(data.summary.maintenance_activity_90d)} detail={`Registry-scoped · ${data.summary.maintenance_activity_90d.evidence_class}`} />
        <StatCard label="Asset Health Records" value={metric(data.record_availability.asset_health_records)} detail={`Controlled records, not scores · ${data.record_availability.asset_health_records.evidence_class}`} />
      </section>
      <div className="executive-summary-grid">
        <SectionCard><div className="section-heading"><h2>Reliability evidence</h2><NavIcon name="assets" /></div><div className="assessment-boundary"><span>Portfolio health / risk</span><strong>NOT ASSESSED</strong><p>Record availability does not establish an asset health score or risk classification.</p></div><div className="evidence-summary-list"><Link href="/fmea"><span>FMEA records</span><strong>{metric(data.record_availability.fmea_records)}</strong></Link><Link href="/asset-health"><span>Assessment records</span><strong>{metric(data.record_availability.asset_health_records)}</strong></Link><Link href="/assets"><span>Registered assets</span><strong>{metric(data.summary.registered_assets)}</strong></Link></div><p className="section-note">Controlled record populations; inspect the evidence and identity before interpretation.</p></SectionCard>
        <SectionCard><div className="section-heading"><div><p className="eyebrow">Activity concentration · {windowDays}d</p><h2>Highest Maintenance Activity</h2></div></div><p className="section-note concentration-note">Investigation signal only; not a condition or risk score.</p>{data.activity_concentration.length === 0 ? <EmptyState title="No maintenance activity in this window." /> : <TableFrame minWidth={560} label="Registered assets with highest maintenance activity"><table><thead><tr><th>Asset</th><th>Description</th><th>Events</th><th>Latest activity</th></tr></thead><tbody>{(allActivity ? data.activity_concentration : data.activity_concentration.slice(0, 5)).map(row => <tr key={row.asset_ref}><td><Link className="asset-row-link" href={`/assets/${encodeURIComponent(row.asset_ref)}`}>{row.source_asset_number}</Link></td><td>{row.description ?? "UNKNOWN"}</td><td><strong>{metric(row.event_count)}</strong></td><td>{overviewDate(row.latest_activity)}</td></tr>)}</tbody></table></TableFrame>}{data.activity_concentration.length > 5 && <Button className="activity-expand" aria-expanded={allActivity} onClick={() => setAllActivity(value => !value)}>{allActivity ? "Show top 5 assets" : `Show all ${data.activity_concentration.length} assets`}</Button>}<Link className="text-link panel-drilldown" href="/maintenance/investigation">Investigate repeats →</Link></SectionCard>
        <SectionCard><div className="section-heading"><h2>Management attention</h2><NavIcon name="integration" /></div><p className="section-note concentration-note">Relationship evidence requiring review; no inferred equipment priorities.</p><div className="attention-list">{attentionItems(data.integrity).map(item => <Link key={item.label} href={item.href}><span className="attention-symbol" aria-hidden="true">i</span><div><strong>{item.label}</strong><span>{factualCount(item.count)} unresolved in current Mart</span></div></Link>)}</div><Link className="text-link panel-drilldown" href="/data-quality">Review Data Trust →</Link></SectionCard>
      </div>
      <SectionCard className="executive-history"><div className="section-heading"><div><p className="eyebrow">Last 12 weeks</p><h2>Maintenance Activity Trend</h2></div><span className="muted-label">Weekly event count · DERIVED_SAFE</span></div><ActivityChart rows={data.maintenance_activity} /><p className="section-note">Activity date uses actual start when available, otherwise source change time. Scope: {data.scope.site_code} / {data.scope.organization_code} · {data.scope.registry_scope}. Date basis: {data.scope.date_basis}. No interpolation or prediction.</p></SectionCard>
      <div className="overview-grid distribution-grid"><SectionCard><div className="section-heading"><div><p className="eyebrow">Source Status · {windowDays}d</p><h2>Status distribution</h2></div><span className="muted-label">Raw source values · DERIVED_SAFE</span></div><Distribution title="source statuses" rows={data.status_distribution} /></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Work Type · {windowDays}d</p><h2>Work-type distribution</h2></div><span className="muted-label">Raw source values · DERIVED_SAFE</span></div><Distribution title="work types" rows={data.work_type_distribution} /></SectionCard></div>
      <div className="overview-grid overview-grid-wide"><SectionCard><div className="section-heading"><div><p className="eyebrow">Controlled record evidence</p><h2>Available Reliability Records</h2></div><span className="muted-label">Factual counts · VERIFIED / DERIVED_SAFE</span></div><div className="record-availability-grid"><div><strong>{metric(data.record_availability.fmea_records)}</strong><span>FMEA records · VERIFIED</span><small>{metric(data.record_availability.fmea_assets_represented)} registered Assets represented · DERIVED_SAFE</small></div><div><strong>{metric(data.record_availability.asset_health_records)}</strong><span>Asset Health records · VERIFIED</span><small>{metric(data.record_availability.asset_health_assets_represented)} registered Assets represented · DERIVED_SAFE</small></div><div><strong>{metric(data.record_availability.rcfa_records)}</strong><span>RCFA records · VERIFIED</span><small>Global count · Asset relationship unresolved</small></div><div><strong>{metric(data.record_availability.overhaul_records)}</strong><span>Overhaul records · VERIFIED</span><small>Global count · unresolved Asset refs retained</small></div></div><p className="section-note">Asset representation means a record points to a registered Asset in the current controlled population; it is not a completion rate.</p></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Data Trust</p><h2>Relationship integrity</h2></div><Link href="/data-quality" className="text-link">Open Data Trust Center →</Link></div><div className="integrity-cards"><div><span>Registry</span><strong>{data.integrity.registered_assets_resolved} <small>/ {data.integrity.registered_assets_total} resolved</small></strong><em>{data.integrity.registered_assets_unresolved} unresolved</em></div><div><span>Asset refs</span><strong>{data.integrity.asset_refs_resolved} <small>/ {data.integrity.asset_refs_total} resolved</small></strong><em>{data.integrity.asset_refs_unresolved} unresolved</em></div><div><span>Work Order refs</span><strong>{data.integrity.workorder_refs_resolved} <small>/ {data.integrity.workorder_refs_total} resolved</small></strong><em>{data.integrity.workorder_refs_unresolved} unresolved</em></div><div><span>Technical context</span><strong>{factualCount(data.integrity.technical_asset_context_total)}</strong><em>secondary context · VERIFIED</em></div></div></SectionCard></div>
      <SectionCard className="executive-maturity"><div className="section-heading"><h2>Data maturity and source context</h2><Link className="text-link" href="/data-quality">Data Trust →</Link></div><div className="content-grid"><div><DataMaturity state={data.data_maturity.asset_maintenance} /><p>Asset and Maintenance · {data.scope.maintenance_source}</p></div><div><DataMaturity state={data.data_maturity.controlled_domains} /><p>FMEA · Asset Health · RCFA · Overhaul</p></div><div><DataMaturity state={data.data_maturity.rcfa_relationship} /><p>RCFA Asset relationship is not used for Asset representation.</p></div><div><DataMaturity state={data.data_maturity.technical_context} /><p>Technical equipment remains a separate population.</p></div></div></SectionCard>
    </>}
  </>;
}
