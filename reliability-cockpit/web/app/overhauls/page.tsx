"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type OverhaulFilters, type OverhaulView, type Page } from "../../lib/api";
import { displayValue, formatDate } from "../../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatusBadge, TableFrame } from "../../components/ui";

const LIMIT = 50;

export default function OverhaulsPage() {
  const [page, setPage] = useState<Page<OverhaulView> | null>(null);
  const [filters, setFilters] = useState<OverhaulFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ lifecycle_status: "", workorder_ref: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.overhauls(filters).then((next) => { if (!cancelled) { setPage(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);
  return <>
    <PageHeader eyebrow="Canonical reliability view" title="Overhaul" description="Overhaul yang tersimpan pada Mart, termasuk status relasi asset bila tersedia." actions={<span className="scope-chip">BSR / IP</span>} />
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Overhaul filters</p><strong>Find an overhaul record</strong></div><span className="muted-label">Current controlled load may contain one record</span></div><div className="filter-grid compact-filter"><label>Status<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder="Lifecycle status" /></label><label>Work Order reference<input value={draft.workorder_ref} onChange={(event) => setDraft({ ...draft, workorder_ref: event.target.value })} placeholder="Reference" /></label><button className="button primary" onClick={() => setFilters({ lifecycle_status: draft.lifecycle_status || undefined, workorder_ref: draft.workorder_ref || undefined, limit: LIMIT, offset: 0 })}>Apply filters</button></div></SectionCard>
    <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / Overhaul</p><h2>{page?.meta.total.toLocaleString("id-ID") ?? "—"} overhauls</h2></div>{page && <span className="dataset-badge compact">Contract v1</span>}</div>
      {loading && <LoadingState />}{!loading && error && <ErrorState message={error} />}{!loading && !error && page && page.items.length === 0 && <EmptyState />}{!loading && !error && page && page.items.length > 0 && <><TableFrame minWidth={1100}><table><thead><tr><th>Overhaul number</th><th>Status</th><th>Work Order</th><th>Asset</th><th>Planned dates</th><th>Actual dates</th><th>Progress</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? <Identifier value={row.source_record_id} />}</strong><small className="table-subtext"><Identifier value={row.source_record_id} /></small></td><td><StatusBadge value={row.lifecycle_status} /></td><td><Identifier value={row.workorder_ref} /></td><td>{row.asset_ref ? <Identifier value={row.asset_ref} /> : <span className="muted-label">Asset unresolved</span>}</td><td>{formatDate(row.planned_start_at)}<br />{formatDate(row.planned_finish_at)}</td><td>{formatDate(row.actual_start_at)}<br />{formatDate(row.actual_finish_at)}</td><td>{displayValue(row.progress)}</td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></>}</SectionCard>
  </>;
}
