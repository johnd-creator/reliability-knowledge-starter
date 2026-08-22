"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type FmeaFilters, type FmeaOverviewView, type FmeaView, type Page } from "../../lib/api";
import { formatDate, formatNumber } from "../../lib/format";
import { DataMaturity, EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatCard, TableFrame } from "../../components/ui";

const LIMIT = 50;

function SourceStatus({ value }: { value: string | null | undefined }) {
  return <span className="status-badge neutral">{value ?? "UNKNOWN"}</span>;
}

function Distribution({ title, items }: { title: string; items: { value: string; count: { value: number } }[] }) {
  const max = Math.max(...items.map((item) => item.count.value), 1);
  return <SectionCard className="fmea-distribution-card"><div className="section-heading"><div><p className="eyebrow">Raw source values</p><h2>{title}</h2></div><span className="muted-label">No business status mapping</span></div><div className="fmea-distribution-grid">{items.map((item) => <div className="fmea-distribution-item" key={item.value}><div><SourceStatus value={item.value} /><strong>{formatNumber(item.count.value)}</strong></div><div className="fmea-distribution-track"><span style={{ width: `${Math.max((item.count.value / max) * 100, 2)}%` }} /></div></div>)}</div></SectionCard>;
}

export default function FmeaPage() {
  const [overview, setOverview] = useState<FmeaOverviewView | null>(null);
  const [page, setPage] = useState<Page<FmeaView> | null>(null);
  const [filters, setFilters] = useState<FmeaFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ lifecycle_status: "", source_number: "", asset_number: "", source_failure_code: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([reliabilityApi.fmeaOverview(), reliabilityApi.fmea({ ...filters, limit: LIMIT })]).then(([nextOverview, nextPage]) => {
      if (!cancelled) { setOverview(nextOverview); setPage(nextPage); setError(null); }
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable");
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);

  function applyFilters() {
    setFilters({ asset_number: draft.asset_number || undefined, lifecycle_status: draft.lifecycle_status || undefined, source_number: draft.source_number || undefined, source_failure_code: draft.source_failure_code || undefined, limit: LIMIT, offset: 0 });
  }

  return <>
    <PageHeader eyebrow="Controlled Mart population" title="FMEA" description="FMEA records available for Registered Reliability Assets. Item-level failure-mode details remain outside the current controlled population." actions={<span className="scope-chip">BSR / IP</span>} />
    <div className="scope-banner trust-strip"><DataMaturity state="CONTROLLED MART POPULATION" detail="Current FMEA records are a controlled Mart population." /><DataMaturity state="ASSET RELATIONSHIP VERIFIED" /><DataMaturity state="FMEA ITEM DETAILS DEFERRED" /><span className="muted-label">Registry-scoped normal view</span></div>
    <SectionCard className="neutral-note"><strong>FMEA records are evidence. Failure-mode item details, severity, occurrence, detectability, and RPN are not available in the current controlled population.</strong></SectionCard>
    {loading && <LoadingState label="Reading FMEA assessment aggregates…" />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && overview && page && <>
      <section className="stat-grid fmea-stat-grid"><StatCard label="FMEA Records" value={formatNumber(overview.summary.fmea_records)} detail="Current controlled Mart population · VERIFIED" tone="accent" /><StatCard label="Registered Assets Represented" value={formatNumber(overview.summary.registered_assets_represented)} detail="Representation in current population · DERIVED_SAFE" /><StatCard label="Assets with Multiple FMEA Records" value={formatNumber(overview.summary.assets_with_multiple_records)} detail="Record multiplicity only · DERIVED_SAFE" /><StatCard label="Records with Failure Code" value={formatNumber(overview.summary.records_with_failure_code)} detail="Raw source value present · VERIFIED" /></section>
      <div className="fmea-distribution-grid-wide"><Distribution title="Status distribution" items={overview.status_distribution} /><Distribution title="Revision distribution" items={overview.revision_distribution} /></div>
      <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">FMEA filters</p><strong>Find a Registered Asset FMEA record</strong></div><span className="muted-label">Server-side · 50 rows</span></div><div className="filter-grid fmea-filter-grid"><label>Asset number<input value={draft.asset_number} onChange={(event) => setDraft({ ...draft, asset_number: event.target.value })} placeholder="Source Asset number" /></label><label>FMEA number<input value={draft.source_number} onChange={(event) => setDraft({ ...draft, source_number: event.target.value })} placeholder="FMEA number" /></label><label>Source status<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder="e.g. MONITORED" /></label><label>Source Failure Code<input value={draft.source_failure_code} onChange={(event) => setDraft({ ...draft, source_failure_code: event.target.value })} placeholder="Raw source code" /></label><button className="button primary" onClick={applyFilters}>Apply filters</button></div></SectionCard>
      <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Registered Reliability Assets / FMEA</p><h2>{page.meta.total.toLocaleString("id-ID")} Registry-scoped FMEA records</h2></div><span className="dataset-badge compact">Factual records</span></div>{page.items.length === 0 ? <EmptyState title="No FMEA records match the current filters." detail="No FMEA record is not a risk conclusion." /> : <TableFrame minWidth={1450}><table><thead><tr><th>FMEA number</th><th>Asset</th><th>Asset description</th><th>Revision</th><th>Source status</th><th>Description</th><th>Failure Code</th><th>FMEA record date</th><th>Age</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? "—"}</strong><small className="table-subtext"><Identifier value={row.source_record_id} /></small></td><td>{row.asset_ref ? <Link className="asset-row-link" href={`/assets/${encodeURIComponent(row.asset_ref)}`}>{row.source_asset_number ?? "Registered Asset"}</Link> : "—"}</td><td className="wide-cell">{row.asset_description ?? "—"}</td><td>{row.revision ?? "—"}</td><td><SourceStatus value={row.lifecycle_status} /></td><td className="wide-cell">{row.description ?? "—"}</td><td>{row.source_failure_code ?? "—"}<small className="table-subtext">Source value</small></td><td>{formatDate(row.fmea_record_date)}</td><td>{row.fmea_age_days == null ? "Date unavailable" : `${row.fmea_age_days.toFixed(0)} days`}<small className="table-subtext">Record recency only</small></td></tr>)}</tbody></table></TableFrame>}<Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></SectionCard>
      <p className="section-note">FMEA record date uses {overview.record_recency.date_basis}. It is not an approval date, failure date, or risk review deadline. FMEA item details remain deferred.</p>
    </>}
  </>;
}
