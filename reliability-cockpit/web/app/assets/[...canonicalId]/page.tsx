"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import {
  ApiError,
  reliabilityApi,
  type AssetHealthView,
  type AssetView,
  type ContextView,
  type FmeaView,
  type MaintenanceEventView,
  type OverhaulView,
  type Page,
  type TimelineView,
} from "../../../lib/api";
import { displayValue, formatDate, formatNumber } from "../../../lib/format";
import {
  EmptyState,
  ErrorState,
  Identifier,
  LoadingState,
  PageHeader,
  Pagination,
  SectionCard,
  StatCard,
  StatusBadge,
  TableFrame,
} from "../../../components/ui";

type Tab = "overview" | "timeline" | "maintenance" | "fmea" | "health" | "overhaul";

function SourceStatus({ value }: { value: string | null | undefined }) {
  return <span className="status-badge neutral">{value ?? "UNKNOWN"}</span>;
}

const tabs: Array<{ id: Tab; label: string }> = [
  { id: "overview", label: "Overview" },
  { id: "timeline", label: "Timeline" },
  { id: "maintenance", label: "Maintenance" },
  { id: "fmea", label: "FMEA" },
  { id: "health", label: "Asset Health" },
  { id: "overhaul", label: "Overhaul" },
];

interface AssetCounts {
  maintenance: number;
  fmea: number;
  health: number;
  overhaul: number;
}

function routeAssetId(parts: string[]): string {
  const raw = parts.join("/");
  try {
    return decodeURIComponent(raw);
  } catch {
    return raw;
  }
}

function isTab(value: string | null): value is Tab {
  return tabs.some((tab) => tab.id === value);
}

function errorMessage(reason: unknown): string {
  return reason instanceof Error ? reason.message : "Reliability Mart unavailable";
}

function CopyCanonicalId({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  }
  return <button className="copy-button" type="button" onClick={copy}>{copied ? "Copied" : "Copy"}</button>;
}

function AssetFacts({ asset }: { asset: AssetView }) {
  return <dl className="asset-facts">
    <div><dt>Status</dt><dd><StatusBadge value={asset.status} /></dd></div>
    <div><dt>Location</dt><dd>{asset.location_ref ?? "—"}</dd></div>
    <div><dt>Asset type</dt><dd>{asset.asset_type ?? "—"}</dd></div>
    <div><dt>Plant</dt><dd>{asset.plant ?? "—"}</dd></div>
    <div><dt>Unit</dt><dd>{asset.unit ?? "—"}</dd></div>
    <div><dt>Last source update</dt><dd>{formatDate(asset.source_updated_at)}</dd></div>
    <div><dt>Scope</dt><dd>{asset.site_code} / {asset.organization_code}</dd></div>
  </dl>;
}

function RecentMaintenance({ rows }: { rows: MaintenanceEventView[] }) {
  if (rows.length === 0) return <EmptyState title="No recent maintenance in this dataset." />;
  return <TableFrame minWidth={560}><table><thead><tr><th>Work order</th><th>Event</th><th>Status</th><th>Date</th></tr></thead><tbody>{rows.map((row) => <tr key={row.canonical_id}><td><Identifier value={row.work_order_id ?? row.id} /></td><td>{row.event_type ?? "—"}</td><td><StatusBadge value={row.status} /></td><td>{formatDate(row.actual_start ?? row.source_changed_at)}</td></tr>)}</tbody></table></TableFrame>;
}

function RecentFmea({ rows }: { rows: FmeaView[] }) {
  if (rows.length === 0) return <EmptyState title="No recent FMEA assessment in this dataset." />;
  return <div className="asset-record-list">{rows.map((row) => <div className="asset-record" key={row.canonical_id}><div><strong>{row.source_number ?? "FMEA record"}</strong><small>{row.fmea_record_date ? `FMEA record date ${formatDate(row.fmea_record_date)}` : row.description ?? "Date unavailable"}</small></div><span className="status-badge neutral">{row.lifecycle_status ?? "UNKNOWN"}</span></div>)}</div>;
}

function RecentHealth({ rows }: { rows: AssetHealthView[] }) {
  if (rows.length === 0) return <EmptyState title="No recent Asset Health assessment in this dataset." />;
  return <div className="asset-record-list">{rows.map((row) => <div className="asset-record" key={row.canonical_id}><div><strong>{row.source_record_id ?? "Asset Health assessment"}</strong><small>{row.assessment_record_date ? `Assessment record date ${formatDate(row.assessment_record_date)}` : row.function_description ?? row.description ?? "Date unavailable"}</small></div><span className="status-badge neutral">{row.lifecycle_status ?? "UNKNOWN"}</span></div>)}</div>;
}

function RecentOverhaul({ rows }: { rows: OverhaulView[] }) {
  if (rows.length === 0) return <EmptyState title="No recent Overhaul resolved to this Asset." />;
  return <div className="asset-record-list">{rows.map((row) => <div className="asset-record" key={row.canonical_id}><div><strong>{row.source_number ?? row.source_record_id ?? "Overhaul"}</strong><small>{formatDate(row.actual_start_at ?? row.planned_start_at)} · {row.source_work_order_number ?? "No Work Order number"}</small></div><SourceStatus value={row.lifecycle_status} /></div>)}</div>;
}

function TimelinePanel({ page, onChange }: { page: Page<TimelineView>; onChange: (offset: number) => void }) {
  if (page.items.length === 0) return <EmptyState title="No timeline events resolved to this Asset." detail="Timeline includes Maintenance, FMEA, Asset Health, and Overhaul records only." />;
  return <>
    <div className="timeline-list">{page.items.map((event) => <article className={`timeline-item timeline-${event.event_type.toLowerCase()}`} key={`${event.event_id}-${event.event_type}`}><span className="timeline-marker" /><div className="timeline-content"><div className="timeline-meta"><span className="timeline-type">{event.event_type.replace("_", " ")}</span><span>{event.event_at ? formatDate(event.event_at) : "Date unavailable"}</span></div><strong>{event.summary ?? "Reliability event"}</strong><StatusBadge value={event.status} /><small><Identifier value={event.canonical_ref} /></small></div></article>)}</div>
    <Pagination meta={page.meta} onChange={onChange} />
  </>;
}

function MaintenancePanel({ page, onChange }: { page: Page<MaintenanceEventView>; onChange: (offset: number) => void }) {
  if (page.items.length === 0) return <EmptyState title="No Maintenance events for this Asset." />;
  return <><TableFrame minWidth={1050}><table><thead><tr><th>Work Order</th><th>Event / Work type</th><th>Status</th><th>Actual start</th><th>Actual finish</th><th>Duration</th><th>Downtime</th><th>Labor hours</th><th>Failure code</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.work_order_id ?? "—"}</strong></td><td>{row.event_type ?? "—"}</td><td><StatusBadge value={row.status} /></td><td>{formatDate(row.actual_start)}</td><td>{formatDate(row.actual_finish)}</td><td>{row.duration_hours == null ? "—" : `${row.duration_hours} h`}</td><td>{row.downtime_hours == null ? "—" : `${row.downtime_hours} h`}</td><td>{row.labor_hours == null ? "—" : `${row.labor_hours} h`}</td><td>{row.failure_code ?? "—"}</td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={onChange} /></>;
}

function FmeaPanel({ page, onChange }: { page: Page<FmeaView>; onChange: (offset: number) => void }) {
  if (page.items.length === 0) return <EmptyState title="No FMEA assessments for this Asset." />;
  return <><TableFrame minWidth={1050}><table><thead><tr><th>FMEA number</th><th>Revision</th><th>Source status</th><th>Description</th><th>Failure Code</th><th>FMEA record date</th><th>Age</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? "—"}</strong><small className="table-subtext">{row.source_record_id ?? "Source record unavailable"}</small></td><td>{row.revision ?? "—"}</td><td><span className="status-badge neutral">{row.lifecycle_status ?? "UNKNOWN"}</span></td><td className="wide-cell">{row.description ?? "—"}</td><td>{row.source_failure_code ?? "—"}<small className="table-subtext">Source value</small></td><td>{formatDate(row.fmea_record_date)}</td><td>{row.fmea_age_days == null ? "Date unavailable" : `${row.fmea_age_days.toFixed(0)} days`}<small className="table-subtext">Record recency only</small></td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={onChange} /></>;
}

function HealthPanel({ page, onChange }: { page: Page<AssetHealthView>; onChange: (offset: number) => void }) {
  if (page.items.length === 0) return <EmptyState title="No Asset Health assessments for this Asset." />;
  return <><TableFrame minWidth={1050}><table><thead><tr><th>Record</th><th>Status</th><th>Revision</th><th>Description</th><th>Function</th><th>Assessment record date</th><th>Age</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_record_id ?? "—"}</strong></td><td><span className="status-badge neutral">{row.lifecycle_status ?? "UNKNOWN"}</span></td><td>{row.revision ?? "—"}</td><td className="wide-cell">{row.description ?? "—"}</td><td className="wide-cell">{row.function_description ?? "—"}</td><td>{formatDate(row.assessment_record_date)}</td><td>{row.assessment_age_days == null ? "Date unavailable" : `${row.assessment_age_days.toFixed(0)} days`}<small className="table-subtext">Record recency only</small></td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={onChange} /></>;
}

function OverhaulPanel({ page, onChange }: { page: Page<OverhaulView>; onChange: (offset: number) => void }) {
  if (page.items.length === 0) return <EmptyState title="No Overhaul records resolved to this Asset." detail="Overhauls without a proven Asset relationship remain visible only on the global Overhaul view." />;
  return <><TableFrame minWidth={920}><table><thead><tr><th>Overhaul number</th><th>Source status</th><th>Work Order</th><th>Planned dates</th><th>Actual dates</th><th>Source Progress</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? row.source_record_id ?? "—"}</strong></td><td><SourceStatus value={row.lifecycle_status} /></td><td>{row.source_work_order_number ?? "Work Order identified"}</td><td>{formatDate(row.planned_start_at)}<br />{formatDate(row.planned_finish_at)}</td><td>{formatDate(row.actual_start_at)}<br />{formatDate(row.actual_finish_at)}</td><td>{displayValue(row.progress)}</td></tr>)}</tbody></table></TableFrame><Pagination meta={page.meta} onChange={onChange} /></>;
}

export default function AssetDetailPage({ params }: { params: Promise<{ canonicalId: string[] }> }) {
  const { canonicalId: parts } = use(params);
  const canonicalId = routeAssetId(parts);
  const [asset, setAsset] = useState<AssetView | null>(null);
  const [context, setContext] = useState<ContextView | null>(null);
  const [counts, setCounts] = useState<AssetCounts | null>(null);
  const [latestHealth, setLatestHealth] = useState<AssetHealthView | null>(null);
  const [detailLoading, setDetailLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("overview");
  const [tabOffset, setTabOffset] = useState(0);
  const [tabLoading, setTabLoading] = useState(false);
  const [tabError, setTabError] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<Page<TimelineView> | null>(null);
  const [maintenance, setMaintenance] = useState<Page<MaintenanceEventView> | null>(null);
  const [fmea, setFmea] = useState<Page<FmeaView> | null>(null);
  const [health, setHealth] = useState<Page<AssetHealthView> | null>(null);
  const [overhaul, setOverhaul] = useState<Page<OverhaulView> | null>(null);

  useEffect(() => {
    const readTab = () => {
      const requested = new URLSearchParams(window.location.search).get("tab");
      setTab(isTab(requested) ? requested : "overview");
    };
    readTab();
    window.addEventListener("popstate", readTab);
    return () => window.removeEventListener("popstate", readTab);
  }, [canonicalId]);

  useEffect(() => {
    let cancelled = false;
    setAsset(null);
    setContext(null);
    setCounts(null);
    setLatestHealth(null);
    setNotFound(false);
    setDetailError(null);
    setDetailLoading(true);
    async function loadOverview() {
      try {
        const currentAsset = await reliabilityApi.asset(canonicalId);
        if (cancelled) return;
        setAsset(currentAsset);
        const [nextContext, maintenanceCount, fmeaCount, healthCount, overhaulCount, nextLatestHealth] = await Promise.all([
          reliabilityApi.assetContext(canonicalId),
          reliabilityApi.maintenance({ asset_ref: canonicalId, limit: 1 }),
          reliabilityApi.fmea({ asset_ref: canonicalId, limit: 1 }),
          reliabilityApi.assetHealth({ asset_ref: canonicalId, limit: 1 }),
          reliabilityApi.overhauls({ asset_ref: canonicalId, limit: 1 }),
          reliabilityApi.latestAssetHealth(canonicalId).catch((reason: unknown) => {
            if (reason instanceof ApiError && reason.status === 404) return null;
            throw reason;
          }),
        ]);
        if (cancelled) return;
        setContext(nextContext);
        setCounts({ maintenance: maintenanceCount.meta.total, fmea: fmeaCount.meta.total, health: healthCount.meta.total, overhaul: overhaulCount.meta.total });
        setLatestHealth(nextLatestHealth);
      } catch (reason: unknown) {
        if (cancelled) return;
        if (reason instanceof ApiError && reason.status === 404) setNotFound(true);
        else setDetailError(errorMessage(reason));
      } finally {
        if (!cancelled) setDetailLoading(false);
      }
    }
    loadOverview();
    return () => { cancelled = true; };
  }, [canonicalId]);

  useEffect(() => {
    if (!asset || tab === "overview") return;
    let cancelled = false;
    setTabLoading(true);
    setTabError(null);
    const page = { offset: tabOffset, limit: 50 };
    const load = tab === "timeline"
      ? reliabilityApi.assetTimeline(canonicalId, page).then((next) => { if (!cancelled) setTimeline(next); })
      : tab === "maintenance"
        ? reliabilityApi.maintenance({ asset_ref: canonicalId, ...page }).then((next) => { if (!cancelled) setMaintenance(next); })
        : tab === "fmea"
          ? reliabilityApi.assetFmea(canonicalId, page).then((next) => { if (!cancelled) setFmea(next); })
          : tab === "health"
            ? reliabilityApi.assetHealthAssessments(canonicalId, page).then((next) => { if (!cancelled) setHealth(next); })
            : reliabilityApi.overhauls({ asset_ref: canonicalId, ...page }).then((next) => { if (!cancelled) setOverhaul(next); });
    load.catch((reason: unknown) => { if (!cancelled) setTabError(errorMessage(reason)); }).finally(() => { if (!cancelled) setTabLoading(false); });
    return () => { cancelled = true; };
  }, [asset, canonicalId, tab, tabOffset]);

  function selectTab(next: Tab) {
    setTab(next);
    setTabOffset(0);
    const suffix = next === "overview" ? "" : `?tab=${next}`;
    window.history.pushState({}, "", `${window.location.pathname}${suffix}`);
  }

  function changeTabPage(offset: number) {
    setTabOffset(offset);
  }

  if (detailLoading) return <><PageHeader eyebrow="Asset Reliability" title="Asset Detail" description="Memuat identitas dan konteks Reliability Mart…" actions={<Link className="text-link" href="/assets">← Back to Asset Reliability</Link>} /><LoadingState /></>;
  if (notFound) return <><PageHeader eyebrow="Asset Reliability" title="Asset not found" description="Aset yang diminta tidak ditemukan pada Reliability Mart saat ini." actions={<Link className="text-link" href="/assets">← Back to Asset Reliability</Link>} /><ErrorState message="Asset not found" /></>;
  if (detailError || !asset) return <><PageHeader eyebrow="Asset Reliability" title="Asset Detail" description="Detail Asset tidak dapat dimuat." actions={<Link className="text-link" href="/assets">← Back to Asset Reliability</Link>} /><ErrorState message={detailError ?? "Reliability Mart unavailable"} /></>;

  return <>
    <PageHeader eyebrow="Asset Reliability / Asset Detail" title={asset.source_asset_number ?? "Asset Detail"} description={asset.description ?? "Canonical Asset reliability workspace"} actions={<Link className="text-link" href="/assets">← Back to Asset Reliability</Link>} />
    <SectionCard className="asset-identity-card"><div className="asset-identity-main"><div><p className="eyebrow">Current asset identity</p><h2>{asset.source_asset_number ?? <Identifier value={asset.canonical_id} />}</h2><p className="asset-description">{asset.description ?? "No description available"}</p></div><StatusBadge value={asset.status} /></div><AssetFacts asset={asset} /><div className="canonical-identity"><span><small>Canonical identity</small><Identifier value={asset.canonical_id} /></span><CopyCanonicalId value={asset.canonical_id} /></div></SectionCard>
    <nav className="asset-tabs" aria-label="Asset workspace tabs">{tabs.map((item) => <button key={item.id} type="button" className={tab === item.id ? "asset-tab active" : "asset-tab"} onClick={() => selectTab(item.id)}>{item.label}</button>)}</nav>

    {tab === "overview" && context && counts && <>
      <section className="stat-grid asset-stat-grid"><StatCard label="Maintenance Events" value={formatNumber(counts.maintenance)} detail="Asset-scoped Mart total" tone="accent" /><StatCard label="FMEA Assessments" value={formatNumber(counts.fmea)} detail="Asset-scoped Mart total" /><StatCard label="Asset Health" value={formatNumber(counts.health)} detail="Asset-scoped Mart total" /><StatCard label="Overhauls" value={formatNumber(counts.overhaul)} detail="Resolved Asset relationship" tone="muted" /></section>
      <div className="asset-overview-grid"><SectionCard><div className="section-heading"><div><p className="eyebrow">Recent context</p><h2>Recent Maintenance</h2></div><button className="text-link-button" onClick={() => selectTab("maintenance")}>View all →</button></div><RecentMaintenance rows={context.maintenance} /></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Recent context</p><h2>Recent FMEA</h2></div><button className="text-link-button" onClick={() => selectTab("fmea")}>View all →</button></div><RecentFmea rows={context.fmea} /></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Recent context</p><h2>Recent Asset Health</h2></div><button className="text-link-button" onClick={() => selectTab("health")}>View all →</button></div><RecentHealth rows={context.health} /></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Recent context</p><h2>Recent Overhaul</h2></div><button className="text-link-button" onClick={() => selectTab("overhaul")}>View all →</button></div><RecentOverhaul rows={context.overhauls} /></SectionCard></div>
      <div className="asset-bottom-grid"><SectionCard><div className="section-heading"><div><p className="eyebrow">Latest available evidence</p><h2>Latest Asset Health</h2></div></div>{latestHealth ? <div className="latest-health"><span className="status-badge neutral">{latestHealth.lifecycle_status ?? "UNKNOWN"}</span><strong>{latestHealth.source_record_id ?? "Asset Health assessment"}</strong><p>{latestHealth.description ?? latestHealth.function_description ?? "No description available"}</p><small>Revision {latestHealth.revision ?? "—"} · Assessment record date {formatDate(latestHealth.assessment_record_date ?? latestHealth.source_updated_at ?? latestHealth.status_changed_at)} · {latestHealth.assessment_age_days == null ? "Age unavailable" : `${latestHealth.assessment_age_days.toFixed(0)} days since record`}</small></div> : <EmptyState title="No asset-health assessment available in the current Mart dataset." />}</SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Relationship boundary</p><h2>Reference health</h2></div></div><div className="neutral-note"><span className="state-symbol">i</span>RCFA relationship is not mapped in Contract v1.</div><p className="section-note">Dataset Reference Health: {context.relationship_health.asset_refs_resolved} of {context.relationship_health.asset_refs_total} asset references resolved. This is a Mart-level aggregate, not an Asset health score.</p></SectionCard></div>
    </>}

    {tab !== "overview" && <SectionCard className="data-section asset-tab-panel"><div className="section-heading"><div><p className="eyebrow">Asset-scoped reliability records</p><h2>{tabs.find((item) => item.id === tab)?.label}</h2></div><span className="dataset-badge compact">Current controlled dataset</span></div>{tabLoading && <LoadingState />}{!tabLoading && tabError && <ErrorState message={tabError} />}{!tabLoading && !tabError && tab === "timeline" && timeline && <TimelinePanel page={timeline} onChange={changeTabPage} />}{!tabLoading && !tabError && tab === "maintenance" && maintenance && <MaintenancePanel page={maintenance} onChange={changeTabPage} />}{!tabLoading && !tabError && tab === "fmea" && fmea && <FmeaPanel page={fmea} onChange={changeTabPage} />}{!tabLoading && !tabError && tab === "health" && health && <HealthPanel page={health} onChange={changeTabPage} />}{!tabLoading && !tabError && tab === "overhaul" && overhaul && <OverhaulPanel page={overhaul} onChange={changeTabPage} />}</SectionCard>}
  </>;
}
