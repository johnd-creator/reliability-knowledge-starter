"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type Page, type RcfaFilters, type RcfaView } from "../../lib/api";
import { formatDate } from "../../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatusBadge, TableFrame } from "../../components/ui";

const LIMIT = 50;

export default function RcfaPage() {
  const [page, setPage] = useState<Page<RcfaView> | null>(null);
  const [filters, setFilters] = useState<RcfaFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ lifecycle_status: "", category: "", source_number: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.rcfa(filters).then((next) => { if (!cancelled) { setPage(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);
  return <>
    <PageHeader eyebrow="Canonical reliability view" title="RCFA" description="Root Cause Failure Analysis berdiri sebagai dataset sendiri sampai relasinya ke asset terbukti di Contract v1." actions={<span className="scope-chip">BSR / IP</span>} />
    <div className="neutral-note"><span className="status-badge neutral">Relationship unresolved</span><span>RCFA → Asset belum dipetakan. NADI tidak menebak hubungan melalui deskripsi, tanggal, atau nomor.</span></div>
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Analysis filters</p><strong>Find an RCFA record</strong></div><span className="muted-label">No asset filter by design</span></div><div className="filter-grid"><label>Lifecycle status<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder="e.g. OPEN" /></label><label>Category<input value={draft.category} onChange={(event) => setDraft({ ...draft, category: event.target.value })} placeholder="Category" /></label><label>RCFA number<input value={draft.source_number} onChange={(event) => setDraft({ ...draft, source_number: event.target.value })} placeholder="Reference" /></label><button className="button primary" onClick={() => setFilters({ lifecycle_status: draft.lifecycle_status || undefined, category: draft.category || undefined, source_number: draft.source_number || undefined, limit: LIMIT, offset: 0 })}>Apply filters</button></div></SectionCard>
    <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / rcfa_analysis</p><h2>{page?.meta.total.toLocaleString("id-ID") ?? "—"} analyses</h2></div>{page && <span className="dataset-badge compact">Relationship-safe</span>}</div>
      {loading && <LoadingState />}{!loading && error && <ErrorState message={error} />}{!loading && !error && page && page.items.length === 0 && <EmptyState />}{!loading && !error && page && page.items.length > 0 && <><TableFrame minWidth={1050}><table><thead><tr><th>RCFA number</th><th>Revision</th><th>Status</th><th>Category</th><th>Created</th><th>Requested</th><th>Relationship</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? <Identifier value={row.source_record_id} />}</strong><small className="table-subtext"><Identifier value={row.source_record_id} /></small></td><td>{row.revision ?? "—"}</td><td><StatusBadge value={row.lifecycle_status} /></td><td>{row.category ?? "—"}</td><td>{formatDate(row.source_created_at)}</td><td>{formatDate(row.requested_at)}</td><td><span className="relationship-note">Asset relationship not mapped</span></td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></>}</SectionCard>
  </>;
}
