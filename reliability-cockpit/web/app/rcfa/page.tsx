"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type Page, type RcfaFilters, type RcfaOverviewView, type RcfaView } from "../../lib/api";
import { formatDate, formatNumber } from "../../lib/format";
import { DataMaturity, EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatCard, TableFrame } from "../../components/ui";

const LIMIT = 50;

function SourceStatus({ value }: { value: string | null | undefined }) {
  return <span className="status-badge neutral">{value ?? "UNKNOWN"}</span>;
}

function Distribution({ title, items }: { title: string; items: { value: string; count: { value: number } }[] }) {
  const max = Math.max(...items.map((item) => item.count.value), 1);
  return <SectionCard className="rcfa-distribution-card"><div className="section-heading"><div><p className="eyebrow">Raw source values</p><h2>{title}</h2></div><span className="muted-label">Business semantics unverified</span></div><div className="rcfa-distribution-grid">{items.map((item) => <div className="rcfa-distribution-item" key={item.value}><div><span className="status-badge neutral">{item.value}</span><strong>{formatNumber(item.count.value)}</strong></div><div className="rcfa-distribution-track"><span style={{ width: `${Math.max((item.count.value / max) * 100, 2)}%` }} /></div></div>)}</div></SectionCard>;
}

export default function RcfaPage() {
  const [overview, setOverview] = useState<RcfaOverviewView | null>(null);
  const [page, setPage] = useState<Page<RcfaView> | null>(null);
  const [filters, setFilters] = useState<RcfaFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ lifecycle_status: "", category: "", source_number: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([reliabilityApi.rcfaOverview(), reliabilityApi.rcfa({ ...filters, limit: LIMIT })]).then(([nextOverview, nextPage]) => {
      if (!cancelled) { setOverview(nextOverview); setPage(nextPage); setError(null); }
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable");
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);

  function applyFilters() {
    setFilters({ lifecycle_status: draft.lifecycle_status || undefined, category: draft.category || undefined, source_number: draft.source_number || undefined, limit: LIMIT, offset: 0 });
  }

  return <>
    <PageHeader eyebrow="Controlled Mart population" title="RCFA" description="Root Cause Failure Analysis records available in the current Reliability Mart population. RCFA remains a global analysis dataset while its relationships are unresolved." actions={<span className="scope-chip">BSR / IP</span>} />
    <div className="scope-banner trust-strip"><DataMaturity state="CONTROLLED MART POPULATION" detail="Current RCFA records are a controlled Mart population." /><DataMaturity state="GLOBAL ANALYSIS RECORDS" /><DataMaturity state="ASSET RELATIONSHIP UNRESOLVED" /><span className="muted-label">No Asset or Work Order join</span></div>
    <SectionCard className="neutral-note"><strong>RCFA records are global analysis evidence. Asset, Work Order, and Failure Event relationships remain unresolved; no root-cause detail or completion meaning is inferred.</strong></SectionCard>
    {loading && <LoadingState label="Reading RCFA analysis aggregates…" />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && overview && page && <>
      <section className="stat-grid rcfa-stat-grid"><StatCard label="RCFA Records" value={formatNumber(overview.summary.rcfa_records)} detail="Current controlled Mart population · VERIFIED" tone="accent" /><StatCard label="Records with Category" value={formatNumber(overview.summary.records_with_category)} detail="Raw source value present · VERIFIED" /><StatCard label="Records with Revision" value={formatNumber(overview.summary.records_with_revision)} detail="Raw source value present · VERIFIED" /><StatCard label="Records with Request Date" value={formatNumber(overview.summary.records_with_requested_at)} detail="Requested date present · VERIFIED" /></section>
      <div className="rcfa-distribution-grid-wide"><Distribution title="Status distribution" items={overview.status_distribution} /><Distribution title="Category distribution" items={overview.category_distribution} /></div>
      <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Global RCFA filters</p><strong>Find an RCFA record</strong></div><span className="muted-label">No Asset filter by design · Server-side</span></div><div className="filter-grid rcfa-filter-grid"><label>Lifecycle status<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder="Raw source status" /></label><label>Category<input value={draft.category} onChange={(event) => setDraft({ ...draft, category: event.target.value })} placeholder="Raw category" /></label><label>RCFA number<input value={draft.source_number} onChange={(event) => setDraft({ ...draft, source_number: event.target.value })} placeholder="RCFA number" /></label><button className="button primary" onClick={applyFilters}>Apply filters</button></div></SectionCard>
      <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / Global RCFA</p><h2>{page.meta.total.toLocaleString("id-ID")} RCFA records</h2></div><span className="dataset-badge compact">Relationship-safe</span></div>{page.items.length === 0 ? <EmptyState title="No RCFA records match the current filters." detail="No RCFA record is not a conclusion about failure or completion." /> : <TableFrame minWidth={1200}><table><thead><tr><th>RCFA number</th><th>Revision</th><th>Source status</th><th>Category</th><th>Requested date</th><th>Created date</th><th>RCFA record date</th><th>Age</th><th>Relationship</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? "—"}</strong><small className="table-subtext"><Identifier value={row.source_record_id} /></small></td><td>{row.revision ?? "—"}</td><td><SourceStatus value={row.lifecycle_status} /></td><td>{row.category ?? "—"}</td><td>{formatDate(row.requested_at)}</td><td>{formatDate(row.source_created_at)}</td><td>{formatDate(row.rcfa_record_date)}</td><td>{row.rcfa_age_days == null ? "Date unavailable" : `${row.rcfa_age_days.toFixed(0)} days`}<small className="table-subtext">Record recency only</small></td><td><span className="relationship-note">Asset relationship unresolved</span></td></tr>)}</tbody></table></TableFrame>}<Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></SectionCard>
      <p className="section-note">RCFA record date uses {overview.record_recency.date_basis}. It is not a failure date, analysis completion date, investigation start date, or SLA measure. No Asset links are generated.</p>
    </>}
  </>;
}
