"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type MaintenanceInvestigationView } from "../../../lib/api";
import { formatDate, formatNumber } from "../../../lib/format";
import { DataMaturity, EmptyState, ErrorState, LoadingState, PageHeader, Pagination, SectionCard, StatCard, TableFrame } from "../../../components/ui";

const WINDOWS = [30, 90, 180] as const;
const MIN_EVENTS = [2, 3, 5] as const;
type WindowDays = (typeof WINDOWS)[number];
type MinEvents = (typeof MIN_EVENTS)[number];
type SortMode = "event_count_desc" | "latest_activity_desc" | "latest_gap_asc";

export default function MaintenanceInvestigationPage() {
  const [windowDays, setWindowDays] = useState<WindowDays>(90);
  const [minEvents, setMinEvents] = useState<MinEvents>(2);
  const [sort, setSort] = useState<SortMode>("event_count_desc");
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState<MaintenanceInvestigationView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    reliabilityApi.maintenanceInvestigation(windowDays, minEvents, offset, 25, sort).then((next) => {
      if (!cancelled) { setData(next); setError(null); }
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable");
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [windowDays, minEvents, offset, sort]);

  function changeWindow(value: WindowDays) { setWindowDays(value); setOffset(0); }
  function changeMinEvents(value: MinEvents) { setMinEvents(value); setOffset(0); }
  function changeSort(value: SortMode) { setSort(value); setOffset(0); }

  return <>
    <PageHeader
      eyebrow="Maintenance / Investigation"
      title="Maintenance Investigation"
      description="Menelusuri pola aktivitas Maintenance berulang pada Registered Reliability Assets tanpa mengasumsikan kegagalan atau risiko."
      actions={<div className="overview-actions"><span className="scope-chip">BSR / IP</span><Link className="button" href="/maintenance">Back to Maintenance</Link></div>}
    />
    <div className="scope-banner trust-strip"><DataMaturity state="CURRENT LOCAL PROJECTION" detail="Maintenance data are projected locally from Collector into the Mart." /><span>Registry-scoped Maintenance</span><span className="muted-label">{data?.evidence.work_type_source ?? "Source Work Type → canonical fallback → UNKNOWN"}</span></div>
    <SectionCard className="neutral-note"><strong>Repeat Activity means more than one Maintenance Event on the same Asset within the selected period. It does not by itself mean repeat failure.</strong></SectionCard>
    <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">Investigation window</p><strong>Bounded activity sequence</strong></div><span className="muted-label">Activity date uses actual start when available, otherwise source change time.</span></div><div className="filter-grid compact-filter"><label>Current data window<select value={windowDays} onChange={(event) => changeWindow(Number(event.target.value) as WindowDays)}><option value={30}>30 days</option><option value={90}>90 days</option><option value={180}>180 days</option></select></label><label>Minimum events<select value={minEvents} onChange={(event) => changeMinEvents(Number(event.target.value) as MinEvents)}><option value={2}>2+ events</option><option value={3}>3+ events</option><option value={5}>5+ events</option></select></label><label>Sort<select value={sort} onChange={(event) => changeSort(event.target.value as SortMode)}><option value="event_count_desc">Event count, high to low</option><option value="latest_activity_desc">Latest activity, newest</option><option value="latest_gap_asc">Latest gap, shortest</option></select></label></div></SectionCard>
    {loading && <LoadingState label="Reading bounded Maintenance Investigation aggregates…" />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && data && <>
      <section className="stat-grid investigation-stat-grid"><StatCard label={`Maintenance Events ${windowDays}d`} value={formatNumber(data.summary.maintenance_events)} detail="Registry-scoped · DERIVED_SAFE" tone="accent" /><StatCard label="Assets with Activity" value={formatNumber(data.summary.assets_with_activity)} detail="Distinct registered Assets · DERIVED_SAFE" /><StatCard label="Assets with 2+ Events" value={formatNumber(data.summary.assets_with_2plus_events)} detail="Repeat Activity candidate · DERIVED_SAFE" /><StatCard label="Repeat Activity Events" value={formatNumber(data.summary.repeat_activity_events)} detail="Events beyond the first · DERIVED_SAFE" /></section>
      <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">{minEvents}+ events · {windowDays}d</p><h2>Repeated Maintenance Activity</h2></div><span className="muted-label">{data.meta.total.toLocaleString("id-ID")} Assets in result · server-side</span></div>{data.assets.length === 0 ? <EmptyState title="No Assets meet this activity threshold in the selected window." detail="This is an empty activity result, not a reliability conclusion." /> : <TableFrame minWidth={1220}><table><thead><tr><th>Asset</th><th>Description</th><th>Maintenance Events</th><th>Repeat Activity Events</th><th>Latest Activity</th><th>Previous Activity</th><th>Latest Gap</th><th>Latest Work Type</th><th>Dominant Work Type</th></tr></thead><tbody>{data.assets.map((asset) => <tr key={asset.asset_ref}><td><Link className="asset-row-link" href={`/assets/${encodeURIComponent(asset.asset_ref)}`}>{asset.source_asset_number}</Link></td><td className="wide-cell">{asset.description ?? "—"}</td><td><strong>{formatNumber(asset.event_count)}</strong></td><td>{formatNumber(asset.repeat_activity_events)}</td><td>{formatDate(asset.latest_activity)}</td><td>{formatDate(asset.previous_activity)}</td><td>{asset.latest_gap_days == null ? "—" : `${asset.latest_gap_days.toFixed(1)} days`}</td><td>{asset.latest_work_type ?? "UNKNOWN"}</td><td>{asset.dominant_work_type ?? "UNKNOWN"}</td></tr>)}</tbody></table></TableFrame>}<Pagination meta={data.meta} onChange={setOffset} /></SectionCard>
      <p className="section-note">{data.evidence.activity_date} Intervals are descriptive only. Repeated activity can include planned, inspection, administrative, or cancelled source events; raw source statuses remain unchanged.</p>
    </>}
  </>;
}
