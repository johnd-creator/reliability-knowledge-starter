"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type FmeaFilters, type FmeaView, type Page } from "../../lib/api";
import { formatDate } from "../../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatusBadge, TableFrame } from "../../components/ui";

const LIMIT = 50;

export default function FmeaPage() {
  const [page, setPage] = useState<Page<FmeaView> | null>(null);
  const [filters, setFilters] = useState<FmeaFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ lifecycle_status: "", source_number: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.fmea(filters).then((next) => { if (!cancelled) { setPage(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);
  return <>
    <PageHeader eyebrow="Canonical reliability view" title="FMEA" description="Failure Mode and Effects Analysis yang tersedia dalam dataset Reliability Mart saat ini." actions={<span className="scope-chip">BSR / IP</span>} />
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Assessment filters</p><strong>Find a FMEA record</strong></div><span className="muted-label">IPFMEA detail items remain deferred</span></div><div className="filter-grid compact-filter"><label>Lifecycle status<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder="e.g. ACTIVE" /></label><label>FMEA number<input value={draft.source_number} onChange={(event) => setDraft({ ...draft, source_number: event.target.value })} placeholder="Reference" /></label><button className="button primary" onClick={() => setFilters({ lifecycle_status: draft.lifecycle_status || undefined, source_number: draft.source_number || undefined, limit: LIMIT, offset: 0 })}>Apply filters</button></div></SectionCard>
    <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / fmea_assessment</p><h2>{page?.meta.total.toLocaleString("id-ID") ?? "—"} assessments</h2></div>{page && <span className="dataset-badge compact">Factual records</span>}</div>
      {loading && <LoadingState />}{!loading && error && <ErrorState message={error} />}{!loading && !error && page && page.items.length === 0 && <EmptyState />}{!loading && !error && page && page.items.length > 0 && <><TableFrame minWidth={1000}><table><thead><tr><th>FMEA number</th><th>Revision</th><th>Status</th><th>Description</th><th>Asset reference</th><th>Failure code</th><th>Updated</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? <Identifier value={row.source_record_id} />}</strong><small className="table-subtext"><Identifier value={row.source_record_id} /></small></td><td>{row.revision ?? "—"}</td><td><StatusBadge value={row.lifecycle_status} /></td><td className="wide-cell">{row.description ?? "—"}</td><td><Identifier value={row.asset_ref} /></td><td>{row.failure_code_ref ?? "—"}</td><td>{formatDate(row.source_updated_at ?? row.status_changed_at)}</td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></>}</SectionCard>
    </>
  ;
}
