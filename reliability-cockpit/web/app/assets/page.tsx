"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type AssetFilters, type AssetView, type Page } from "../../lib/api";
import { formatDate } from "../../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatusBadge, StatCard, TableFrame, InputControl, Button } from "../../components/ui";

const LIMIT = 50;

export default function AssetsPage() {
  const [page, setPage] = useState<Page<AssetView> | null>(null);
  const [filters, setFilters] = useState<AssetFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ status: "", unit: "", asset_type: "" });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [refresh, setRefresh] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.assets(filters).then((next) => { if (!cancelled) { setPage(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters, refresh]);

  const visible = page?.items.filter(asset => [asset.canonical_id, asset.source_asset_number, asset.description, asset.location_ref].some(value => value?.toLowerCase().includes(search.trim().toLowerCase()))) ?? [];

  function applyFilters() { setFilters({ status: draft.status || undefined, unit: draft.unit || undefined, asset_type: draft.asset_type || undefined, limit: LIMIT, offset: 0 }); }
  function changePage(offset: number) { setFilters((current) => ({ ...current, offset })); }

  return <>
    <PageHeader eyebrow="Registered Asset projection" title="Asset Register" description="Registered Reliability Assets dari snapshot List of Assets, diperkaya konteks teknis lokal tanpa mengunduh seluruh records." actions={<span className="scope-chip">BSR / IP</span>} />
    <section className="stat-grid"><StatCard label="Registered assets" value={!loading && !error && page ? page.meta.total : "UNKNOWN"} detail="Server-filtered Registry population" /><StatCard label="Health score" value="NOT ASSESSED" detail="No approved numerical assessment" /><StatCard label="Evidence scope" value="BSR / IP" detail="Technical equipment remains separate" /></section>
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Asset filters</p><strong>Find a registered asset</strong></div><span className="muted-label">Server filters · 50 rows; search this page only</span></div><div className="filter-grid"><InputControl id="asset-page-search" label="Search this page" value={search} onChange={e => setSearch(e.target.value)} placeholder="Identity, description or location" /><label>Status<input value={draft.status} onChange={(event) => setDraft({ ...draft, status: event.target.value })} placeholder="e.g. ACTIVE" /></label><label>Unit<input value={draft.unit} onChange={(event) => setDraft({ ...draft, unit: event.target.value })} placeholder="e.g. Unit 1" /></label><label>Asset type<input value={draft.asset_type} onChange={(event) => setDraft({ ...draft, asset_type: event.target.value })} placeholder="e.g. PRODUCTION" /></label><Button variant="primary" onClick={applyFilters}>Apply filters</Button><Button onClick={() => {setDraft({status:"",unit:"",asset_type:""});setSearch("");setFilters({limit:LIMIT});}}>Clear filters</Button></div></SectionCard>
    <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / Registered Assets</p><h2>{!loading && !error && page ? page.meta.total.toLocaleString("id-ID") : "UNKNOWN"} registered assets</h2></div>{page && <span className="dataset-badge compact">Current registry projection</span>}</div>
      {loading && <LoadingState />}{!loading && error && <ErrorState message="Asset Register unavailable" onRetry={() => setRefresh(value => value + 1)} />}{!loading && !error && page && visible.length === 0 && <EmptyState title="No registered assets match these page filters." detail="Page search covers only the loaded server page; no condition conclusion follows." />}{!loading && !error && page && visible.length > 0 && <><TableFrame minWidth={1120}><table><thead><tr><th>Asset</th><th>Description</th><th>Source Status</th><th>Location</th><th>Type</th><th>Plant</th><th>Unit</th><th>Source record updated</th><th>Assessment</th><th>Open</th></tr></thead><tbody>{visible.map((asset) => <tr key={asset.canonical_id}><td><strong><Link className="asset-row-link" href={`/assets/${encodeURIComponent(asset.canonical_id)}`}>{asset.source_asset_number ?? <Identifier value={asset.canonical_id} />}</Link></strong><small className="table-subtext"><Identifier value={asset.canonical_id} /></small></td><td className="wide-cell">{asset.description ?? "—"}</td><td><StatusBadge value={asset.status} mode="raw-neutral" /></td><td>{asset.location_ref ?? "—"}</td><td>{asset.asset_type ?? "—"}</td><td>{asset.plant ?? "—"}</td><td>{asset.unit ?? "—"}</td><td>{formatDate(asset.source_updated_at)}<small className="table-subtext">Record timestamp, not freshness</small></td><td>NOT ASSESSED<small className="table-subtext">See asset evidence</small></td><td><Link className="table-action" href={`/assets/${encodeURIComponent(asset.canonical_id)}`}>View Asset →</Link></td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={changePage} /></>}</SectionCard>
  </>;
}
