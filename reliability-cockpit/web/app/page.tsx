"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type AssetHealthView, type FmeaView, type IntegrityView, type MaintenanceEventView, type Page } from "../lib/api";
import { formatDate, formatNumber } from "../lib/format";
import { EmptyState, ErrorState, Identifier, LoadingState, PageHeader, SectionCard, StatCard, StatusBadge, TableFrame } from "../components/ui";

interface OverviewData {
  assets: number;
  maintenance: number;
  fmea: number;
  rcfa: number;
  health: number;
  overhauls: number;
  integrity: IntegrityView;
  recentMaintenance: Page<MaintenanceEventView>;
  recentFmea: Page<FmeaView>;
  recentHealth: Page<AssetHealthView>;
}

export default function HomePage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      reliabilityApi.registry(),
      reliabilityApi.maintenance({ limit: 5 }),
      reliabilityApi.fmea({ limit: 5 }),
      reliabilityApi.rcfa({ limit: 1 }),
      reliabilityApi.assetHealth({ limit: 5 }),
      reliabilityApi.overhauls({ limit: 1 }),
      reliabilityApi.integrity(),
    ]).then(([registry, maintenance, fmea, rcfa, health, overhauls, integrity]) => {
      if (cancelled) return;
      setData({ assets: registry.registered_asset_count, maintenance: maintenance.meta.total, fmea: fmea.meta.total, rcfa: rcfa.meta.total, health: health.meta.total, overhauls: overhauls.meta.total, integrity, recentMaintenance: maintenance, recentFmea: fmea, recentHealth: health });
      setError(null);
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable");
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return (
    <>
      <PageHeader eyebrow="Reliability information" title="NADI Overview" description="Membaca denyut kesehatan aset pembangkit dari Reliability Mart yang terkontrol." actions={<span className="dataset-badge"><span className="pulse-dot" /> Controlled Initial Dataset</span>} />
      <div className="scope-banner"><span className="scope-chip">BSR / IP</span><span>Current operating scope</span><span className="banner-divider" />Data Mart dibaca secara read-only; angka ini bukan klaim populasi historis lengkap.</div>
      {loading && <LoadingState />}
      {!loading && error && <ErrorState message={error} />}
      {!loading && !error && data && <>
        <section className="stat-grid overview-stat-grid">
          <StatCard label="Registered Reliability Assets" value={formatNumber(data.assets)} detail="Current List of Assets projection" tone="accent" />
          <StatCard label="Maintenance events" value={formatNumber(data.maintenance)} detail="Local Collector projection; registry-scoped" />
          <StatCard label="FMEA assessments" value={formatNumber(data.fmea)} detail="Canonical reliability records" />
          <StatCard label="RCFA analyses" value={formatNumber(data.rcfa)} detail="Canonical reliability records" />
          <StatCard label="Asset health" value={formatNumber(data.health)} detail="Current controlled dataset" />
          <StatCard label="Overhauls" value={formatNumber(data.overhauls)} detail="Available in Reliability Mart" tone="muted" />
        </section>

        <div className="overview-grid">
          <SectionCard>
            <div className="section-heading"><div><p className="eyebrow">Reference health</p><h2>Relationship integrity</h2></div><a href="/data-quality" className="text-link">Open data quality →</a></div>
            <div className="integrity-cards">
              <div><span>Asset references</span><strong>{data.integrity.asset_refs_resolved} <small>/ {data.integrity.asset_refs_total} resolved</small></strong><em>{data.integrity.asset_refs_unresolved} unresolved</em></div>
              <div><span>Work Order references</span><strong>{data.integrity.workorder_refs_resolved} <small>/ {data.integrity.workorder_refs_total} resolved</small></strong><em>{data.integrity.workorder_refs_unresolved} unresolved</em></div>
            </div>
            <p className="section-note">Unresolved references can point outside the current controlled initial dataset; they are not automatically source-data errors.</p>
          </SectionCard>
          <SectionCard className="controlled-card">
            <p className="eyebrow">How to read this view</p><h2>Controlled dataset</h2>
            <p>Asset and Maintenance views are projected from the local Maximo Collector. FMEA, RCFA, Asset Health, and Overhaul remain within their current controlled Mart population.</p>
            <div className="controlled-line"><span className="pulse-dot" /><strong>Factual Mart information first</strong></div>
            <p className="section-note">Reliability analytics such as MTBF, MTTR, and health scores are intentionally not presented here yet.</p>
          </SectionCard>
        </div>

        <div className="overview-grid recent-grid">
          <SectionCard><div className="section-heading"><div><p className="eyebrow">Latest records</p><h2>Maintenance</h2></div><a href="/maintenance" className="text-link">View all →</a></div><TableFrame minWidth={680}><table><thead><tr><th>Work order</th><th>Event</th><th>Status</th><th>Start / changed</th></tr></thead><tbody>{data.recentMaintenance.items.map((row) => <tr key={row.canonical_id}><td><Identifier value={row.work_order_id ?? row.id} /></td><td>{row.event_type ?? "—"}</td><td><StatusBadge value={row.status} /></td><td>{formatDate(row.actual_start ?? row.source_changed_at)}</td></tr>)}</tbody></table></TableFrame>{data.recentMaintenance.items.length === 0 && <EmptyState />}</SectionCard>
          <SectionCard><div className="section-heading"><div><p className="eyebrow">Latest records</p><h2>FMEA & asset health</h2></div><span className="muted-label">Canonical views</span></div><div className="mini-record-list">{data.recentFmea.items.slice(0, 3).map((row) => <div className="mini-record" key={row.canonical_id}><span className="record-type">FMEA</span><div><strong>{row.source_number ?? row.source_record_id ?? "Assessment"}</strong><small>{row.description ?? "No description"}</small></div><StatusBadge value={row.lifecycle_status} /></div>)}{data.recentHealth.items.slice(0, 2).map((row) => <div className="mini-record" key={row.canonical_id}><span className="record-type health">Asset Health</span><div><strong>{row.source_record_id ?? "Assessment"}</strong><small>{row.function_description ?? row.description ?? "No description"}</small></div><StatusBadge value={row.lifecycle_status} /></div>)}{data.recentFmea.items.length === 0 && data.recentHealth.items.length === 0 && <EmptyState />}</div></SectionCard>
        </div>
      </>}
    </>
  );
}
