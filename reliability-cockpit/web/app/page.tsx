"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type DecisionOverviewView, type EvidenceValue } from "../lib/api";
import { formatDate, formatNumber } from "../lib/format";
import { DataMaturity, EmptyState, ErrorState, LoadingState, PageHeader, SectionCard, StatCard, TableFrame } from "../components/ui";

const WINDOWS = [7, 30, 90] as const;
type WindowDays = (typeof WINDOWS)[number];

function metric(value: EvidenceValue): string {
  return formatNumber(value.value);
}

function Distribution({ title, rows }: { title: string; rows: DecisionOverviewView["status_distribution"] }) {
  const maximum = Math.max(...rows.map((row) => row.count.value), 0);
  if (rows.length === 0) return <EmptyState title={`No ${title.toLowerCase()} in this window.`} />;
  return <div className="distribution-list">{rows.map((row) => <div className="distribution-row" key={row.value}><div className="distribution-label"><span>{row.value}</span><strong>{formatNumber(row.count.value)}</strong></div><div className="distribution-track" aria-hidden="true"><span style={{ width: `${maximum ? (row.count.value / maximum) * 100 : 0}%` }} /></div></div>)}</div>;
}

function TrendChart({ rows }: { rows: DecisionOverviewView["maintenance_activity"] }) {
  const maximum = Math.max(...rows.map((row) => row.event_count.value), 0);
  if (rows.length === 0) return <EmptyState title="No maintenance activity trend available." />;
  return <div className="trend-chart" role="img" aria-label="Weekly maintenance activity counts for the last 12 weeks">{rows.map((row) => <div className="trend-column" key={row.period_start} title={`${formatDate(row.period_start)}: ${row.event_count.value} events`}><strong>{formatNumber(row.event_count.value)}</strong><div className="trend-track"><span style={{ height: `${maximum ? Math.max((row.event_count.value / maximum) * 100, row.event_count.value ? 7 : 0) : 0}%` }} /></div><small>{new Date(row.period_start).toLocaleDateString("id-ID", { day: "2-digit", month: "short" })}</small></div>)}</div>;
}

export default function HomePage() {
  const [windowDays, setWindowDays] = useState<WindowDays>(30);
  const [data, setData] = useState<DecisionOverviewView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.decisionOverview(windowDays).then((next) => {
      if (cancelled) return;
      setData(next);
      setError(null);
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable");
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [windowDays]);

  return <>
    <PageHeader eyebrow="NADI / Decision layer" title="NADI Executive Overview" description="Factual view of current Reliability data for the BSR / IP operating scope." actions={<div className="overview-actions"><span className="dataset-badge"><span className="pulse-dot" /> MIXED DATA MATURITY</span><label className="window-select">Current data window<select value={windowDays} onChange={(event) => setWindowDays(Number(event.target.value) as WindowDays)} aria-label="Maintenance activity window">{WINDOWS.map((days) => <option key={days} value={days}>{days} days</option>)}</select></label></div>} />
    <div className="scope-banner trust-strip"><span className="scope-chip">BSR / IP</span><span>{data ? `${metric(data.summary.registered_assets)} Registered Reliability Assets` : "Registered Reliability Assets"}</span><DataMaturity state="CURRENT LOCAL PROJECTION" detail="Asset and maintenance data are projected locally from Collector into the Mart." /><DataMaturity state="CONTROLLED MART POPULATION" detail="FMEA, Asset Health, RCFA, and Overhaul remain current controlled populations." /></div>
    {loading && <LoadingState label="Reading Executive Overview aggregates…" />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && data && <>
      <section className="stat-grid overview-stat-grid">
        <StatCard label="Registered Reliability Assets" value={metric(data.summary.registered_assets)} detail="Registry count · VERIFIED" tone="accent" />
        <StatCard label="Maintenance Activity 7d" value={metric(data.summary.maintenance_activity_7d)} detail="Registry-scoped · DERIVED_SAFE" />
        <StatCard label="Maintenance Activity 30d" value={metric(data.summary.maintenance_activity_30d)} detail="Registry-scoped · DERIVED_SAFE" />
        <StatCard label="Assets with Activity 30d" value={metric(data.summary.assets_active_30d)} detail="Distinct registered Asset refs · DERIVED_SAFE" />
        <StatCard label="Maintenance Activity 90d" value={metric(data.summary.maintenance_activity_90d)} detail="Registry-scoped · DERIVED_SAFE" />
      </section>

      <div className="overview-grid overview-grid-wide">
        <SectionCard><div className="section-heading"><div><p className="eyebrow">Last 12 weeks</p><h2>Maintenance Activity Trend</h2></div><span className="muted-label">Weekly event count · DERIVED_SAFE</span></div><TrendChart rows={data.maintenance_activity} /><p className="section-note">Activity date uses actual start when available, otherwise source change time. This is an activity series, not a condition or risk score.</p></SectionCard>
        <SectionCard className="maturity-card"><div className="section-heading"><div><p className="eyebrow">Trust strip</p><h2>Data maturity</h2></div><Link href="/data-quality" className="text-link">Data Trust →</Link></div><div className="maturity-list"><div><DataMaturity state={data.data_maturity.asset_maintenance} /><p>Asset and Maintenance</p></div><div><DataMaturity state={data.data_maturity.controlled_domains} /><p>FMEA · Asset Health · RCFA · Overhaul</p></div><div><DataMaturity state={data.data_maturity.rcfa_relationship} /><p>RCFA Asset relationship is not used for Asset representation.</p></div></div></SectionCard>
      </div>

      <SectionCard className="data-section activity-concentration"><div className="section-heading"><div><p className="eyebrow">Activity concentration · {windowDays}d</p><h2>Highest Maintenance Activity</h2></div><div className="overview-actions"><span className="muted-label">Investigation signal only</span><Link className="text-link" href="/maintenance/investigation">Investigate repeats →</Link></div></div><p className="section-note concentration-note">High activity is an investigation signal, not a condition or risk score.</p>{data.activity_concentration.length === 0 ? <EmptyState title="No maintenance activity in this window." /> : <TableFrame minWidth={650}><table><thead><tr><th>Asset</th><th>Description</th><th>Maintenance events</th><th>Latest activity</th></tr></thead><tbody>{data.activity_concentration.map((row) => <tr key={row.asset_ref}><td><Link className="asset-row-link" href={`/assets/${encodeURIComponent(row.asset_ref)}`}>{row.source_asset_number}</Link></td><td>{row.description ?? "—"}</td><td><strong>{formatNumber(row.event_count.value)}</strong></td><td>{formatDate(row.latest_activity)}</td></tr>)}</tbody></table></TableFrame>}</SectionCard>

      <div className="overview-grid distribution-grid"><SectionCard><div className="section-heading"><div><p className="eyebrow">Source Status</p><h2>Status distribution</h2></div><span className="muted-label">Raw source values · DERIVED_SAFE</span></div><Distribution title="source statuses" rows={data.status_distribution} /></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Work Type</p><h2>Work-type distribution</h2></div><span className="muted-label">Raw source values · DERIVED_SAFE</span></div><Distribution title="work types" rows={data.work_type_distribution} /></SectionCard></div>

      <div className="overview-grid overview-grid-wide"><SectionCard><div className="section-heading"><div><p className="eyebrow">Controlled record evidence</p><h2>Available Reliability Records</h2></div><span className="muted-label">Factual counts · VERIFIED / DERIVED_SAFE</span></div><div className="record-availability-grid"><div><strong>{formatNumber(data.record_availability.fmea_records.value)}</strong><span>FMEA records · VERIFIED</span><small>{formatNumber(data.record_availability.fmea_assets_represented.value)} registered Assets represented · DERIVED_SAFE</small></div><div><strong>{formatNumber(data.record_availability.asset_health_records.value)}</strong><span>Asset Health records · VERIFIED</span><small>{formatNumber(data.record_availability.asset_health_assets_represented.value)} registered Assets represented · DERIVED_SAFE</small></div><div><strong>{formatNumber(data.record_availability.rcfa_records.value)}</strong><span>RCFA records · VERIFIED</span><small>Global count · Asset relationship unresolved</small></div><div><strong>{formatNumber(data.record_availability.overhaul_records.value)}</strong><span>Overhaul records · VERIFIED</span><small>Global count · unresolved Asset refs retained</small></div></div><p className="section-note">Asset representation means a record points to a registered Asset in the current controlled population; it is not a completion rate.</p></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Data Trust</p><h2>Relationship integrity</h2></div><Link href="/data-quality" className="text-link">Open Data Trust Center →</Link></div><div className="integrity-cards"><div><span>Registry</span><strong>{data.integrity.registered_assets_resolved} <small>/ {data.integrity.registered_assets_total} resolved</small></strong><em>{data.integrity.registered_assets_unresolved} unresolved</em></div><div><span>Asset refs</span><strong>{data.integrity.asset_refs_resolved} <small>/ {data.integrity.asset_refs_total} resolved</small></strong><em>{data.integrity.asset_refs_unresolved} unresolved</em></div><div><span>Work Order refs</span><strong>{data.integrity.workorder_refs_resolved} <small>/ {data.integrity.workorder_refs_total} resolved</small></strong><em>{data.integrity.workorder_refs_unresolved} unresolved</em></div><div><span>Technical context</span><strong>{formatNumber(data.integrity.technical_asset_context_total)}</strong><em>secondary context · VERIFIED</em></div></div></SectionCard></div>
    </>}
  </>;
}
