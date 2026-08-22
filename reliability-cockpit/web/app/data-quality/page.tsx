"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { reliabilityApi, type DataTrustView, type EvidenceClass } from "../../lib/api";
import { formatDate, formatNumber } from "../../lib/format";
import { DataMaturity, ErrorState, LoadingState, PageHeader, SectionCard, TableFrame } from "../../components/ui";

const domainLinks: Partial<Record<DataTrustView["domains"][number]["domain"], string>> = {
  ASSET: "/assets", MAINTENANCE: "/maintenance", FMEA: "/fmea", ASSET_HEALTH: "/asset-health", RCFA: "/rcfa", OVERHAUL: "/overhauls",
};

const evidenceLabels: Record<EvidenceClass, string> = {
  VERIFIED: "VERIFIED", DERIVED_SAFE: "DERIVED SAFE", BUSINESS_SEMANTICS_REQUIRED: "SEMANTICS REQUIRED", DATA_NOT_AVAILABLE: "NOT AVAILABLE", DEFERRED: "DEFERRED",
};

function EvidenceBadge({ value }: { value: EvidenceClass }) { return <span className="evidence-badge">{evidenceLabels[value]}</span>; }
function ReadinessBadge({ status }: { status: DataTrustView["semantic_readiness"][number]["status"] }) { return <span className={`readiness-badge readiness-${status.toLowerCase()}`}>{status.replaceAll("_", " ")}</span>; }

function PopulationCard({ label, value, detail, maturity, href }: { label: string; value: number; detail: string; maturity: string; href?: string }) {
  const content = <><span>{label}</span><strong>{formatNumber(value)}</strong><small>{maturity}</small><em>{detail}</em></>;
  return href ? <Link className="trust-population-card" href={href}>{content}</Link> : <article className="trust-population-card">{content}</article>;
}

export default function DataQualityPage() {
  const [data, setData] = useState<DataTrustView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    reliabilityApi.dataTrust().then((next) => { if (!cancelled) { setData(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable"); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return <>
    <PageHeader eyebrow="NADI / Trust & governance" title="Data Trust Center" description="Melihat cakupan data, kematangan populasi, integritas relasi, dan batas interpretasi yang digunakan NADI." actions={<span className="scope-chip">BSR / IP · MAXIMO</span>} />
    <div className="scope-banner trust-strip"><DataMaturity state="FACTUAL EVIDENCE" detail="Trust dimensions are shown separately." /><DataMaturity state="MIXED DATA MATURITY" /><DataMaturity state="NO TRUST SCORE" /><span className="muted-label">Latest record evidence is not sync freshness</span></div>
    {loading && <LoadingState label="Reading NADI Data Trust evidence…" />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && data && <>
      <SectionCard className="trust-explanation"><p className="eyebrow">How to interpret</p><h2>Trust should be explained, not compressed into a score.</h2><p>{data.scope.interpretation}</p><p className="section-note">A capability marked blocked is intentionally withheld because its business semantics or required source evidence are not yet verified. It does not mean the source system is defective.</p></SectionCard>

      <SectionCard className="trust-population-section"><div className="section-heading"><div><p className="eyebrow">Population boundary</p><h2>Business Asset scope versus technical context</h2></div><span className="muted-label">Source system: {data.scope.source_system}</span></div><div className="trust-population-grid">
        <PopulationCard label="Registered Reliability Assets" value={data.population.registered_reliability_assets} detail={`${formatNumber(data.population.registry_resolved)} resolved · ${formatNumber(data.population.registry_unresolved)} unresolved`} maturity="BUSINESS REGISTRY" href="/assets" />
        <PopulationCard label="Technical Asset Context" value={data.population.technical_asset_context} detail="Broader asset_master population" maturity="TECHNICAL CONTEXT" />
        <PopulationCard label="Maintenance Events" value={data.population.maintenance_total} detail={`${formatNumber(data.population.registry_maintenance)} Registry-scoped`} maturity="LOCAL COLLECTOR PROJECTION" href="/maintenance" />
        <PopulationCard label="FMEA" value={data.population.fmea} detail="Current bounded record population" maturity="CONTROLLED MART POPULATION" href="/fmea" />
        <PopulationCard label="Asset Health" value={data.population.asset_health} detail="Assessment records" maturity="CONTROLLED MART POPULATION" href="/asset-health" />
        <PopulationCard label="RCFA" value={data.population.rcfa} detail="Global analysis records" maturity="CONTROLLED MART POPULATION" href="/rcfa" />
        <PopulationCard label="Overhaul" value={data.population.overhaul} detail="Execution evidence records" maturity="CONTROLLED MART POPULATION" href="/overhauls" />
      </div><p className="section-note">The Registry is NADI&apos;s business Asset boundary. <code>asset_master</code> is retained as technical context and is not presented as the Reliability Asset population.</p></SectionCard>

      <SectionCard className="trust-legend"><div className="section-heading"><div><p className="eyebrow">Data maturity legend</p><h2>How to read population labels</h2></div></div><div className="trust-legend-grid"><div><DataMaturity state="BUSINESS REGISTRY" /><p>Authoritative current business Asset projection used as NADI&apos;s product boundary.</p></div><div><DataMaturity state="LOCAL COLLECTOR PROJECTION" /><p>Broad local operational source projected without a source-system reread.</p></div><div><DataMaturity state="CONTROLLED MART POPULATION" /><p>Verified bounded dataset; not asserted as complete history.</p></div><div><DataMaturity state="TECHNICAL CONTEXT" /><p>Broader technical Equipment population outside normal business Asset scope.</p></div></div></SectionCard>

      <section className="trust-domain-grid"><div className="section-heading trust-domain-heading"><div><p className="eyebrow">Domain maturity</p><h2>What NADI currently has</h2></div><span className="muted-label">Source-record evidence by domain</span></div>{data.domains.map((domain) => <article className="trust-domain-card" key={domain.domain}><div className="section-heading"><div><p className="eyebrow">{domain.source_object}</p><h3>{domainLinks[domain.domain] ? <Link href={domainLinks[domain.domain] as string}>{domain.domain.replaceAll("_", " ")}</Link> : domain.domain.replaceAll("_", " ")}</h3></div><EvidenceBadge value={domain.evidence_class} /></div><div className="trust-domain-value"><strong>{formatNumber(domain.record_count)}</strong>{domain.scoped_record_count != null && <small>{formatNumber(domain.scoped_record_count)} Registry-scoped</small>}</div>{domain.registered_assets_represented != null && <p className="trust-domain-meta">{formatNumber(domain.registered_assets_represented)} Registered Assets represented in current population</p>}<DataMaturity state={domain.population_type.replaceAll("_", " ")} /><p className="trust-domain-meta">{domain.relationship_state}</p><p className="trust-domain-meta">Latest available evidence: <strong>{formatDate(domain.latest_record_date)}</strong><br />Date basis: {domain.date_basis}</p><p className="trust-domain-limit">{domain.known_limitation}</p></article>)}</section>

      <SectionCard className="trust-matrix-card"><div className="section-heading"><div><p className="eyebrow">Relationship readiness</p><h2>Relationships NADI can verify</h2></div><span className="muted-label">No traffic-light score</span></div><TableFrame minWidth={1050}><table className="trust-table"><thead><tr><th>Relationship</th><th>Evidence</th><th>Resolved</th><th>Unresolved</th><th>Technical context</th><th>Interpretation</th></tr></thead><tbody>{data.relationships.map((row) => <tr key={row.relationship}><td><strong>{row.relationship}</strong></td><td><span className="evidence-badge">{row.evidence.replaceAll("_", " ")}</span></td><td>{row.resolved_count == null ? "—" : formatNumber(row.resolved_count)}</td><td>{row.unresolved_count == null ? "—" : formatNumber(row.unresolved_count)}</td><td>{row.technical_context_count == null ? "—" : formatNumber(row.technical_context_count)}</td><td className="wide-cell">{row.interpretation}</td></tr>)}</tbody></table></TableFrame></SectionCard>

      <SectionCard className="trust-matrix-card"><div className="section-heading"><div><p className="eyebrow">Analytics readiness</p><h2>What NADI can safely say</h2></div><span className="muted-label">Evidence class · current status · reason</span></div><TableFrame minWidth={1050}><table className="trust-table"><thead><tr><th>Capability</th><th>Evidence class</th><th>Status</th><th>Reason</th></tr></thead><tbody>{data.semantic_readiness.map((row) => <tr key={row.capability}><td><strong>{row.capability}</strong></td><td><EvidenceBadge value={row.evidence_class} /></td><td><ReadinessBadge status={row.status} /></td><td className="wide-cell">{row.reason}</td></tr>)}</tbody></table></TableFrame></SectionCard>

      <SectionCard className="trust-integrity-card"><div className="section-heading"><div><p className="eyebrow">Existing integrity evidence</p><h2>Reference integrity remains available</h2></div><Link className="text-link" href="/">Back to Executive Overview →</Link></div><div className="integrity-cards"><div><span>Registry</span><strong>{formatNumber(data.integrity.registered_assets_resolved)} <small>/ {formatNumber(data.integrity.registered_assets_total)} resolved</small></strong><em>{formatNumber(data.integrity.registered_assets_unresolved)} unresolved</em></div><div><span>Asset references</span><strong>{formatNumber(data.integrity.asset_refs_resolved)} <small>/ {formatNumber(data.integrity.asset_refs_total)} resolved</small></strong><em>{formatNumber(data.integrity.asset_refs_unresolved)} unresolved</em></div><div><span>Work Order references</span><strong>{formatNumber(data.integrity.workorder_refs_resolved)} <small>/ {formatNumber(data.integrity.workorder_refs_total)} resolved</small></strong><em>{formatNumber(data.integrity.workorder_refs_unresolved)} unresolved</em></div><div><span>Technical context</span><strong>{formatNumber(data.integrity.technical_asset_context_total)}</strong><em>asset_master context · factual</em></div></div></SectionCard>

      <div className="overview-grid trust-bottom-grid"><SectionCard><div className="section-heading"><div><p className="eyebrow">Current product boundary</p><h2>Available now</h2></div></div><ul className="trust-list"><li>Asset Reliability and Registry-scoped Maintenance activity</li><li>Repeat Activity investigation</li><li>FMEA header assessment records</li><li>Asset Health assessment records</li><li>Global RCFA records</li><li>Overhaul execution evidence</li></ul><p className="section-note">These are evidence surfaces, not a claim that every domain has complete historical coverage.</p></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">Future verification backlog</p><h2>Requires source or business verification</h2></div></div><ul className="trust-list"><li>FMEA item semantics and failure-mode details</li><li>RCFA Asset, Work Order, root-cause, and action relationships</li><li>Asset Health Wellness, ACR, MPI, and condition semantics</li><li>Overhaul status, progress, inspection, and date boundaries</li><li>Maintenance failure-code semantics and repeat-failure identity</li><li>PI/DCS model for future PdM</li></ul><p className="section-note">PI/DCS/CEMS are not represented as connected live systems in this Trust Center.</p></SectionCard></div>

      <SectionCard className="trust-limitations"><div className="section-heading"><div><p className="eyebrow">Data boundaries</p><h2>Read the evidence in context</h2></div></div><ul className="trust-list">{data.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></SectionCard>
    </>}
  </>;
}
