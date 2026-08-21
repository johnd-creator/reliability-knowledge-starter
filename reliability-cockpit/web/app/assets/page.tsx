"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type AssetFilters, type AssetView, type Page } from "../../lib/api";
import { formatDate } from "../../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatusBadge, TableFrame } from "../../components/ui";

const LIMIT = 50;

export default function AssetsPage() {
  const [page, setPage] = useState<Page<AssetView> | null>(null);
  const [filters, setFilters] = useState<AssetFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ status: "", unit: "", asset_type: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.assets(filters).then((next) => { if (!cancelled) { setPage(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);

  function applyFilters() { setFilters({ status: draft.status || undefined, unit: draft.unit || undefined, asset_type: draft.asset_type || undefined, limit: LIMIT, offset: 0 }); }
  function changePage(offset: number) { setFilters((current) => ({ ...current, offset })); }

  return <>
    <PageHeader eyebrow="Canonical reliability view" title="Asset Reliability" description="Asset master terkurasi dari Reliability Mart. Gunakan filter untuk menemukan aset tanpa mengunduh seluruh dataset." actions={<span className="scope-chip">BSR / IP</span>} />
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Asset filters</p><strong>Refine the current Mart page</strong></div><span className="muted-label">Server-side · 50 rows</span></div><div className="filter-grid"><label>Status<input value={draft.status} onChange={(event) => setDraft({ ...draft, status: event.target.value })} placeholder="e.g. ACTIVE" /></label><label>Unit<input value={draft.unit} onChange={(event) => setDraft({ ...draft, unit: event.target.value })} placeholder="e.g. Unit 1" /></label><label>Asset type<input value={draft.asset_type} onChange={(event) => setDraft({ ...draft, asset_type: event.target.value })} placeholder="e.g. PRODUCTION" /></label><button className="button primary" onClick={applyFilters}>Apply filters</button></div></SectionCard>
    <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / asset_master</p><h2>{page?.meta.total.toLocaleString("id-ID") ?? "—"} assets</h2></div>{page && <span className="dataset-badge compact">Canonical Contract v1</span>}</div>
      {loading && <LoadingState />}{!loading && error && <ErrorState message={error} />}{!loading && !error && page && page.items.length === 0 && <EmptyState />}{!loading && !error && page && page.items.length > 0 && <><TableFrame minWidth={1050}><table><thead><tr><th>Asset</th><th>Description</th><th>Status</th><th>Location</th><th>Type</th><th>Plant</th><th>Unit</th><th>Last updated</th></tr></thead><tbody>{page.items.map((asset) => <tr key={asset.canonical_id}><td><strong>{asset.source_asset_number ?? <Identifier value={asset.canonical_id} />}</strong><small className="table-subtext"><Identifier value={asset.canonical_id} /></small></td><td className="wide-cell">{asset.description ?? "—"}</td><td><StatusBadge value={asset.status} /></td><td>{asset.location_ref ?? "—"}</td><td>{asset.asset_type ?? "—"}</td><td>{asset.plant ?? "—"}</td><td>{asset.unit ?? "—"}</td><td>{formatDate(asset.source_updated_at)}</td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={changePage} /></>}</SectionCard>
  </>;
}
