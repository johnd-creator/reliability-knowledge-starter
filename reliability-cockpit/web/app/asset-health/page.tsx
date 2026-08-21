"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type AssetHealthView, type HealthFilters, type Page } from "../../lib/api";
import { formatDate } from "../../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatusBadge, TableFrame } from "../../components/ui";

const LIMIT = 50;

export default function AssetHealthPage() {
  const [page, setPage] = useState<Page<AssetHealthView> | null>(null);
  const [filters, setFilters] = useState<HealthFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ lifecycle_status: "", asset_ref: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.assetHealth(filters).then((next) => { if (!cancelled) { setPage(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);
  return <>
    <PageHeader eyebrow="Canonical reliability view" title="Asset Health" description="Assessment kesehatan aset yang tersedia. NADI menampilkan status dan deskripsi, bukan skor kesehatan buatan." actions={<span className="scope-chip">BSR / IP</span>} />
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Assessment filters</p><strong>Find an asset health record</strong></div><span className="muted-label">No numerical health score</span></div><div className="filter-grid compact-filter"><label>Status<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder="Lifecycle status" /></label><label>Asset reference<input value={draft.asset_ref} onChange={(event) => setDraft({ ...draft, asset_ref: event.target.value })} placeholder="Canonical reference" /></label><button className="button primary" onClick={() => setFilters({ lifecycle_status: draft.lifecycle_status || undefined, asset_ref: draft.asset_ref || undefined, limit: LIMIT, offset: 0 })}>Apply filters</button></div></SectionCard>
    <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / asset_health_assessment</p><h2>{page?.meta.total.toLocaleString("id-ID") ?? "—"} assessments</h2></div>{page && <span className="dataset-badge compact">Factual records</span>}</div>
      {loading && <LoadingState />}{!loading && error && <ErrorState message={error} />}{!loading && !error && page && page.items.length === 0 && <EmptyState />}{!loading && !error && page && page.items.length > 0 && <><TableFrame minWidth={1050}><table><thead><tr><th>Record</th><th>Asset</th><th>Status</th><th>Revision</th><th>Description</th><th>Function</th><th>Updated</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><Identifier value={row.source_record_id ?? row.canonical_id} /></td><td><Identifier value={row.asset_ref} /></td><td><StatusBadge value={row.lifecycle_status} /></td><td>{row.revision ?? "—"}</td><td className="wide-cell">{row.description ?? "—"}</td><td className="wide-cell">{row.function_description ?? "—"}</td><td>{formatDate(row.source_updated_at ?? row.status_changed_at)}</td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></>}</SectionCard>
  </>;
}
