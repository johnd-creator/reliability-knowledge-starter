"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type AssetHealthOverviewView, type AssetHealthView, type HealthFilters, type Page } from "../../lib/api";
import { formatDate, formatNumber } from "../../lib/format";
import { DataMaturity, EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatCard, TableFrame } from "../../components/ui";

const LIMIT = 50;

function SourceStatus({ value }: { value: string | null | undefined }) {
  return <span className="status-badge neutral">{value ?? "UNKNOWN"}</span>;
}

export default function AssetHealthPage() {
  const [overview, setOverview] = useState<AssetHealthOverviewView | null>(null);
  const [page, setPage] = useState<Page<AssetHealthView> | null>(null);
  const [filters, setFilters] = useState<HealthFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ asset_number: "", description: "", lifecycle_status: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([reliabilityApi.assetHealthOverview(), reliabilityApi.assetHealth({ ...filters, limit: LIMIT })]).then(([nextOverview, nextPage]) => {
      if (!cancelled) { setOverview(nextOverview); setPage(nextPage); setError(null); }
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable");
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);

  function applyFilters() {
    setFilters({ asset_number: draft.asset_number || undefined, description: draft.description || undefined, lifecycle_status: draft.lifecycle_status || undefined, limit: LIMIT, offset: 0 });
  }

  const maxStatusCount = overview ? Math.max(...overview.status_distribution.map((item) => item.count.value), 1) : 1;
  return <>
    <PageHeader eyebrow="Controlled Mart population" title="Asset Health" description="Assessment records for Registered Reliability Assets. No numerical health score is inferred." actions={<span className="scope-chip">BSR / IP</span>} />
    <div className="scope-banner trust-strip"><DataMaturity state="CONTROLLED MART POPULATION" detail="Current Asset Health records are a controlled Mart population." /><DataMaturity state="ASSESSMENT RECORDS" /><DataMaturity state="NO VERIFIED HEALTH SCORE" /><span className="muted-label">Registry-scoped normal view</span></div>
    <SectionCard className="neutral-note"><strong>Assessment recency indicates when the latest assessment record was updated; it does not indicate Asset condition.</strong></SectionCard>
    {loading && <LoadingState label="Reading Asset Health assessment aggregates…" />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && overview && page && <>
      <section className="stat-grid asset-health-stat-grid"><StatCard label="Assessment Records" value={formatNumber(overview.summary.assessment_records)} detail="Current controlled Mart population · VERIFIED" tone="accent" /><StatCard label="Registered Assets Represented" value={formatNumber(overview.summary.registered_assets_represented)} detail="Representation in current population · DERIVED_SAFE" /><StatCard label="Assets with Multiple Records" value={formatNumber(overview.summary.assets_with_multiple_records)} detail="Observed record count · DERIVED_SAFE" /><StatCard label="Latest Assessment Record" value={formatDate(overview.record_recency.latest_record_at)} detail="Record date, not condition date · DERIVED_SAFE" /></section>
      <SectionCard className="health-status-card"><div className="section-heading"><div><p className="eyebrow">Source lifecycle status</p><h2>Status distribution</h2></div><span className="muted-label">Raw source values · VERIFIED</span></div><div className="health-status-grid">{overview.status_distribution.map((item) => <div className="health-status-item" key={item.value}><div><SourceStatus value={item.value} /><strong>{formatNumber(item.count.value)}</strong></div><div className="health-status-track"><span style={{ width: `${Math.max((item.count.value / maxStatusCount) * 100, 2)}%` }} /></div></div>)}</div></SectionCard>
      <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Assessment filters</p><strong>Find a Registered Asset assessment</strong></div><span className="muted-label">Server-side · 50 rows</span></div><div className="filter-grid"><label>Asset number<input value={draft.asset_number} onChange={(event) => setDraft({ ...draft, asset_number: event.target.value })} placeholder="Source Asset number" /></label><label>Asset description<input value={draft.description} onChange={(event) => setDraft({ ...draft, description: event.target.value })} placeholder="Description contains" /></label><label>Source status<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder="e.g. VER-OK" /></label><button className="button primary" onClick={applyFilters}>Apply filters</button></div></SectionCard>
      <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Registered Reliability Assets / Asset Health</p><h2>{page.meta.total.toLocaleString("id-ID")} assessment records</h2></div><span className="dataset-badge compact">Controlled population</span></div>{page.items.length === 0 ? <EmptyState title="No Asset Health records match the current filters." detail="No assessment is not a health conclusion." /> : <TableFrame minWidth={1450}><table><thead><tr><th>Asset</th><th>Asset description</th><th>Assessment status</th><th>Revision</th><th>Assessment description</th><th>Function</th><th>Assessment record date</th><th>Age</th><th>Source record</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td>{row.asset_ref ? <Link className="asset-row-link" href={`/assets/${encodeURIComponent(row.asset_ref)}`}>{row.source_asset_number ?? "Registered Asset"}</Link> : "—"}</td><td className="wide-cell">{row.asset_description ?? "—"}</td><td><SourceStatus value={row.lifecycle_status} /></td><td>{row.revision ?? "—"}</td><td className="wide-cell">{row.description ?? "—"}</td><td className="wide-cell">{row.function_description ?? "—"}</td><td>{formatDate(row.assessment_record_date)}</td><td>{row.assessment_age_days == null ? "Date unavailable" : `${row.assessment_age_days.toFixed(0)} days`}<small className="table-subtext">Record recency only</small></td><td><Identifier value={row.source_record_id} /></td></tr>)}</tbody></table></TableFrame>}<Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></SectionCard>
      <p className="section-note">Assessment record date uses {overview.record_recency.date_basis}. It is not a condition measurement date. Current population: {overview.summary.registry_resolved} records resolve to Registered Assets; technical/non-Registry records remain outside this normal view.</p>
    </>}
  </>;
}
