"use client";

import {idText, errorLabel, statusLabel} from "../../lib/id-copy";
import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type OverhaulFilters, type OverhaulOverviewView, type OverhaulView, type Page } from "../../lib/api";
import { displayValue, formatDate, formatNumber } from "../../lib/format";
import { DataMaturity, EmptyState, ErrorState, Identifier, LoadingState, PageHeader, Pagination, SectionCard, StatCard, TableFrame } from "../../components/ui";

const LIMIT = 50;

function SourceStatus({ value }: { value: string | null | undefined }) {
  return <span className="status-badge neutral">{value ?? statusLabel("UNKNOWN")}</span>;
}

function Distribution({ items }: { items: { value: string; count: { value: number } }[] }) {
  const max = Math.max(...items.map((item) => item.count.value), 1);
  return <SectionCard className="overhaul-distribution-card"><div className="section-heading"><div><p className="eyebrow">{idText("Raw source values")}</p><h2>{idText("Status distribution")}</h2></div><span className="muted-label">{idText("Business semantics unverified")}</span></div><div className="overhaul-distribution-grid">{items.map((item) => <div className="overhaul-distribution-item" key={item.value}><div><span className="status-badge neutral">{item.value}</span><strong>{formatNumber(item.count.value)}</strong></div><div className="overhaul-distribution-track"><span style={{ width: `${Math.max((item.count.value / max) * 100, 2)}%` }} /></div></div>)}</div></SectionCard>;
}

function WorkOrderCell({ row }: { row: OverhaulView }) {
  if (row.work_order_resolution === "SOURCE_WORK_ORDER_MISSING") {
    return <span className="muted-label">{idText("Work Order not provided")}</span>;
  }
  return <><strong>{row.source_work_order_number ?? idText("Work Order identified")}</strong><small className="table-subtext">{row.work_order_resolution === "SOURCE_LINK_VERIFIED_AND_MART_RESOLVED" ? idText("Local Mart context resolved") : idText("Identified; local Mart reference not available")}</small></>;
}

function AssetCell({ row }: { row: OverhaulView }) {
  if (row.asset_resolution === "ASSET_RESOLVED_REGISTERED" && row.asset_ref) {
    return <><Link className="asset-row-link" href={`/assets/${encodeURIComponent(row.asset_ref)}`}>{row.source_asset_number ?? idText("Registered Asset")}</Link><small className="table-subtext">{row.asset_description ?? ""}</small></>;
  }
  if (row.asset_resolution === "ASSET_RESOLVED_TECHNICAL_CONTEXT") {
    return <><strong>{row.source_asset_number ?? idText("Technical context")}</strong><small className="table-subtext">{idText("Technical context · not a Registered Reliability Asset")}</small></>;
  }
  return <span className="muted-label">{idText("Asset not resolved through current Work Order context")}</span>;
}

export default function OverhaulsPage() {
  const [overview, setOverview] = useState<OverhaulOverviewView | null>(null);
  const [page, setPage] = useState<Page<OverhaulView> | null>(null);
  const [filters, setFilters] = useState<OverhaulFilters>({ limit: LIMIT });
  const [draft, setDraft] = useState({ source_number: "", lifecycle_status: "", source_work_order_number: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([reliabilityApi.overhaulOverview(), reliabilityApi.overhauls({ ...filters, limit: LIMIT })]).then(([nextOverview, nextPage]) => {
      if (!cancelled) { setOverview(nextOverview); setPage(nextPage); setError(null); }
    }).catch((reason: unknown) => {
      if (!cancelled) setError(reason instanceof Error ? errorLabel(reason) : idText("Reliability Mart unavailable"));
    }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters]);

  function applyFilters() {
    setFilters({ source_number: draft.source_number || undefined, lifecycle_status: draft.lifecycle_status || undefined, source_work_order_number: draft.source_work_order_number || undefined, limit: LIMIT, offset: 0 });
  }

  return <>
    <PageHeader eyebrow={idText("Controlled Mart population")} title="Overhaul" description={idText("Overhaul execution records available in the current Reliability Mart population. Dates and progress remain factual source evidence, not performance KPIs.")} actions={<span className="scope-chip">BSR / IP</span>} />
    <div className="scope-banner trust-strip"><DataMaturity state="CONTROLLED MART POPULATION" detail={idText("The current Overhaul population is controlled, not a completeness claim.")} /><DataMaturity state="WORK ORDER RELATIONSHIP VERIFIED" /><DataMaturity state="ASSET DERIVED THROUGH WORK ORDER" /><span className="muted-label">{idText("Mart resolution is measured separately")}</span></div>
    <SectionCard className="neutral-note"><strong>{idText("Asset links appear only when the existing Work Order path resolves to a Registered Reliability Asset. An identified Work Order without local Mart context remains visible and is not treated as invalid.")}</strong></SectionCard>
    {loading && <LoadingState label={idText("Reading Overhaul execution aggregates…")} />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && overview && page && <>
      <section className="stat-grid overhaul-stat-grid"><StatCard label={idText("Overhaul Records")} value={formatNumber(overview.summary.overhaul_records)} detail={idText("Current controlled Mart population · VERIFIED")} tone="accent" /><StatCard label={idText("Records with Work Order")} value={formatNumber(overview.summary.records_with_work_order)} detail={idText("Source relationship present · VERIFIED")} /><StatCard label={idText("Work Orders Resolved Locally")} value={formatNumber(overview.summary.work_orders_resolved_in_mart)} detail={idText("Reference found in local Mart")} /><StatCard label={idText("Registered Assets Resolved")} value={formatNumber(overview.summary.registered_assets_resolved)} detail={idText("Asset path resolved through Work Order")} /></section>
      <div className="overhaul-workspace-grid"><Distribution items={overview.status_distribution} /><SectionCard className="overhaul-boundary-card"><div className="section-heading"><div><p className="eyebrow">{idText("Execution evidence")}</p><h2>{idText("Date and progress availability")}</h2></div><span className="muted-label">{idText("No performance interpretation")}</span></div><div className="overhaul-facts"><div><span>{idText("Planned duration records")}</span><strong>{formatNumber(overview.date_availability.planned_duration_available)}</strong></div><div><span>{idText("Actual duration records")}</span><strong>{formatNumber(overview.date_availability.actual_duration_available)}</strong></div><div><span>{idText("Source Progress present")}</span><strong>{formatNumber(overview.summary.records_with_progress)}</strong></div><div><span>{idText("Inspection number present")}</span><strong>{formatNumber(overview.summary.inspection_number_present)}</strong></div></div><p className="section-note">{idText("Planned and actual duration are timestamp intervals only. Source Progress is shown without a percentage or completion meaning.")}</p></SectionCard></div>
      <SectionCard className="filter-card"><div className="filter-heading"><div><p className="eyebrow">{idText("Overhaul filters")}</p><strong>{idText("Find an Overhaul record")}</strong></div><span className="muted-label">{idText("Server-side · human-facing identifiers")}</span></div><div className="filter-grid compact-filter"><label>{idText("Overhaul number")}<input value={draft.source_number} onChange={(event) => setDraft({ ...draft, source_number: event.target.value })} placeholder={idText("Source Overhaul number")} /></label><label>{idText("Lifecycle status")}<input value={draft.lifecycle_status} onChange={(event) => setDraft({ ...draft, lifecycle_status: event.target.value })} placeholder={idText("Raw source status")} /></label><label>{idText("Work Order number")}<input value={draft.source_work_order_number} onChange={(event) => setDraft({ ...draft, source_work_order_number: event.target.value })} placeholder={idText("Source Work Order number")} /></label><button className="button primary" onClick={applyFilters}>{idText("Apply filters")}</button></div></SectionCard>
      <SectionCard className="data-section"><div className="section-heading"><div><p className="eyebrow">{idText("Reliability Mart / Overhaul")}</p><h2>{page.meta.total.toLocaleString("id-ID")}  {idText("Overhaul records")}</h2></div><span className="dataset-badge compact">{idText("Relationship-aware")}</span></div>{page.items.length === 0 ? <EmptyState title={idText("No Overhaul records match the current filters.")} detail={idText("An empty result is not a completion or performance conclusion.")} /> : <TableFrame minWidth={1450}><table><thead><tr><th>{idText("Overhaul number")}</th><th>{idText("Source status")}</th><th>Work Order</th><th>{idText("Asset")}</th><th>{idText("Planned Start")}</th><th>{idText("Planned Finish")}</th><th>{idText("Actual Start")}</th><th>{idText("Actual Finish")}</th><th>{idText("Source Progress")}</th></tr></thead><tbody>{page.items.map((row) => <tr key={row.canonical_id}><td><strong>{row.source_number ?? "—"}</strong><small className="table-subtext"><Identifier value={row.source_record_id} /></small></td><td><SourceStatus value={row.lifecycle_status} /></td><td><WorkOrderCell row={row} /></td><td><AssetCell row={row} /></td><td>{formatDate(row.planned_start_at)}</td><td>{formatDate(row.planned_finish_at)}</td><td>{formatDate(row.actual_start_at)}</td><td>{formatDate(row.actual_finish_at)}</td><td>{displayValue(row.progress)}<small className="table-subtext">{idText("Raw source value")}</small></td></tr>)}</tbody></table></TableFrame>}<Pagination meta={page.meta} onChange={(offset) => setFilters((current) => ({ ...current, offset }))} /></SectionCard>
      <p className="section-note">{idText("Lifecycle status remains raw source status. Planned/actual dates are source timestamps; no schedule variance, delay, completion, or performance score is calculated.")}</p>
    </>}
  </>;
}
