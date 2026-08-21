"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type MaintenanceEventView, type MaintenanceFilters, type Page } from "../../lib/api";
import { formatDate, formatNumber } from "../../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatusBadge, TableFrame } from "../../components/ui";

const LIMIT = 50;

export default function MaintenancePage() {
  const [page, setPage] = useState<Page<MaintenanceEventView> | null>(null);
  const [filters, setFilters] = useState<MaintenanceFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ status: "", event_type: "", work_order_id: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.maintenance(filters).then((next) => { if (!cancelled) { setPage(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);

  function applyFilters() { setFilters({ status: draft.status || undefined, event_type: draft.event_type || undefined, work_order_id: draft.work_order_id || undefined, limit: LIMIT, offset: 0 }); }
  return <>
    <PageHeader eyebrow="Canonical reliability view" title="Maintenance" description="Maintenance events yang tersimpan di Reliability Mart, dengan waktu dan beban kerja apa adanya dari kontrak canonical." actions={<span className="scope-chip">BSR / IP</span>} />
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Event filters</p><strong>Search the maintenance event page</strong></div><span className="muted-label">Server-side · 50 rows</span></div><div className="filter-grid"><label>Status<input value={draft.status} onChange={(event) => setDraft({ ...draft, status: event.target.value })} placeholder="e.g. COMPLETE" /></label><label>Event / work type<input value={draft.event_type} onChange={(event) => setDraft({ ...draft, event_type: event.target.value })} placeholder="e.g. PM" /></label><label>Work Order<input value={draft.work_order_id} onChange={(event) => setDraft({ ...draft, work_order_id: event.target.value })} placeholder="Reference" /></label><button className="button primary" onClick={applyFilters}>Apply filters</button></div></SectionCard>
    <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">Reliability Mart / Maintenance</p><h2>{page?.meta.total.toLocaleString("id-ID") ?? "—"} maintenance events</h2></div>{page && <span className="dataset-badge compact">Canonical Contract v1</span>}</div>
      {loading && <LoadingState />}{!loading && error && <ErrorState message={error} />}{!loading && !error && page && page.items.length === 0 && <EmptyState />}{!loading && !error && page && page.items.length > 0 && <><TableFrame minWidth={1100}><table><thead><tr><th>Work Order</th><th>Asset</th><th>Event / work type</th><th>Status</th><th>Actual start</th><th>Actual finish</th><th>Downtime</th><th>Labor hours</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><Identifier value={row.work_order_id ?? row.id} /></td><td><Identifier value={row.equipment_id} /></td><td>{row.event_type ?? "—"}</td><td><StatusBadge value={row.status} /></td><td>{formatDate(row.actual_start)}</td><td>{formatDate(row.actual_finish)}</td><td>{formatNumber(row.downtime_hours)} h</td><td>{formatNumber(row.labor_hours)} h</td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></>}</SectionCard>
  </>;
}
