"use client";

import { idText, errorLabel } from "../../lib/id-copy";
import IntegrationStatusPanel from "@/components/IntegrationStatusPanel";
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
    reliabilityApi.dataTrust().then((next) => { if (!cancelled) { setData(next); setError(null); } }).catch((reason: unknown) => { if (!cancelled) setError(reason instanceof Error ? errorLabel(reason) : idText("Reliability Mart unavailable")); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return <>
    <PageHeader eyebrow={idText("NADI / Trust & governance")} title={idText("Data Trust Center")} description="Melihat cakupan data, kematangan populasi, integritas relasi, dan batas interpretasi yang digunakan NADI." actions={<span className="scope-chip">BSR / IP · MAXIMO</span>} />
    <div className="scope-banner trust-strip"><DataMaturity state="FACTUAL EVIDENCE" detail={idText("Trust dimensions are shown separately.")} /><DataMaturity state="MIXED DATA MATURITY" /><DataMaturity state="NO TRUST SCORE" /><span className="muted-label">{idText("Latest record evidence is not sync freshness")}</span></div>
    <IntegrationStatusPanel />
    {loading && <LoadingState label={idText("Reading NADI Data Trust evidence…")} />}
    {!loading && error && <ErrorState message={error} />}
    {!loading && !error && data && <>
      <SectionCard className="trust-explanation"><p className="eyebrow">{idText("How to interpret")}</p><h2>{idText("Trust should be explained, not compressed into a score.")}</h2><p>{data.scope.interpretation}</p><p className="section-note">{idText("A capability marked blocked is intentionally withheld because its business semantics or required source evidence are not yet verified. It does not mean the source system is defective.")}</p></SectionCard>

      <SectionCard className="trust-population-section"><div className="section-heading"><div><p className="eyebrow">{idText("Population boundary")}</p><h2>{idText("Business Asset scope versus technical context")}</h2></div><span className="muted-label">{idText("Source system:")} {data.scope.source_system}</span></div><div className="trust-population-grid">
        <PopulationCard label={idText("Registered Reliability Assets")} value={data.population.registered_reliability_assets} detail={`${formatNumber(data.population.registry_resolved)} terselesaikan · ${formatNumber(data.population.registry_unresolved)} belum terselesaikan`} maturity="BUSINESS REGISTRY" href="/assets" />
        <PopulationCard label={idText("Technical Asset Context")} value={data.population.technical_asset_context} detail={idText("Broader technical Asset context")} maturity="TECHNICAL CONTEXT" />
        <PopulationCard label={idText("Maintenance Events")} value={data.population.maintenance_total} detail={`${formatNumber(data.population.registry_maintenance)} dalam lingkup Registry`} maturity="LOCAL COLLECTOR PROJECTION" href="/maintenance" />
        <PopulationCard label="FMEA" value={data.population.fmea} detail={idText("Current bounded record population")} maturity="CONTROLLED MART POPULATION" href="/fmea" />
        <PopulationCard label={idText("Asset Health")} value={data.population.asset_health} detail={idText("Assessment records")} maturity="CONTROLLED MART POPULATION" href="/asset-health" />
        <PopulationCard label="RCFA" value={data.population.rcfa} detail={idText("Global analysis records")} maturity="CONTROLLED MART POPULATION" href="/rcfa" />
        <PopulationCard label="Overhaul" value={data.population.overhaul} detail={idText("Execution evidence records")} maturity="CONTROLLED MART POPULATION" href="/overhauls" />
      </div><p className="section-note">{idText("The Registry is NADI&apos;s business Asset boundary. The broader technical Asset context (")}<code>asset_master</code>{idText(") is retained for evidence and is not presented as the Reliability Asset population.")}</p></SectionCard>

      <SectionCard className="trust-legend"><div className="section-heading"><div><p className="eyebrow">{idText("Data maturity legend")}</p><h2>{idText("How to read population labels")}</h2></div></div><div className="trust-legend-grid"><div><DataMaturity state="BUSINESS REGISTRY" /><p>{idText("Authoritative current business Asset projection used as NADI&apos;s product boundary.")}</p></div><div><DataMaturity state="LOCAL COLLECTOR PROJECTION" /><p>{idText("Broad local operational source projected without a source-system reread.")}</p></div><div><DataMaturity state="CONTROLLED MART POPULATION" /><p>{idText("Verified bounded dataset; not asserted as complete history.")}</p></div><div><DataMaturity state="TECHNICAL CONTEXT" /><p>{idText("Broader technical Equipment population outside normal business Asset scope.")}</p></div></div></SectionCard>

      <section className="trust-domain-grid"><div className="section-heading trust-domain-heading"><div><p className="eyebrow">{idText("Domain maturity")}</p><h2>{idText("What NADI currently has")}</h2></div><span className="muted-label">{idText("Source-record evidence by domain")}</span></div>{data.domains.map((domain) => <article className="trust-domain-card" key={domain.domain}><div className="section-heading"><div><p className="eyebrow">{domain.source_object}</p><h3>{domainLinks[domain.domain] ? <Link href={domainLinks[domain.domain] as string}>{domain.domain.replaceAll("_", " ")}</Link> : domain.domain.replaceAll("_", " ")}</h3></div><EvidenceBadge value={domain.evidence_class} /></div><div className="trust-domain-value"><strong>{formatNumber(domain.record_count)}</strong>{domain.scoped_record_count != null && <small>{formatNumber(domain.scoped_record_count)}  {idText("Registry-scoped")}</small>}</div>{domain.registered_assets_represented != null && <p className="trust-domain-meta">{formatNumber(domain.registered_assets_represented)}  {idText("Registered Assets represented in current population")}</p>}<DataMaturity state={domain.population_type.replaceAll("_", " ")} /><p className="trust-domain-meta">{domain.relationship_state}</p><p className="trust-domain-meta">{idText("Latest available evidence:")} <strong>{formatDate(domain.latest_record_date)}</strong><br />{idText("Date basis:")} {domain.date_basis}</p><p className="trust-domain-limit">{domain.known_limitation}</p></article>)}</section>

      <SectionCard className="trust-matrix-card"><div className="section-heading"><div><p className="eyebrow">{idText("Relationship readiness")}</p><h2>{idText("Relationships NADI can verify")}</h2></div><span className="muted-label">{idText("No traffic-light score")}</span></div><TableFrame minWidth={1050}><table className="trust-table"><thead><tr><th>{idText("Relationship")}</th><th>{idText("Evidence")}</th><th>{idText("Resolved")}</th><th>{idText("Unresolved")}</th><th>{idText("Technical context")}</th><th>{idText("Interpretation")}</th></tr></thead><tbody>{data.relationships.map((row) => <tr key={row.relationship}><td><strong>{row.relationship}</strong></td><td><span className="evidence-badge">{row.evidence.replaceAll("_", " ")}</span></td><td>{row.resolved_count == null ? "—" : formatNumber(row.resolved_count)}</td><td>{row.unresolved_count == null ? "—" : formatNumber(row.unresolved_count)}</td><td>{row.technical_context_count == null ? "—" : formatNumber(row.technical_context_count)}</td><td className="wide-cell">{row.interpretation}</td></tr>)}</tbody></table></TableFrame></SectionCard>

      <SectionCard className="trust-matrix-card"><div className="section-heading"><div><p className="eyebrow">{idText("Analytics readiness")}</p><h2>{idText("What NADI can safely say")}</h2></div><span className="muted-label">{idText("Evidence class · current status · reason")}</span></div><TableFrame minWidth={1050}><table className="trust-table"><thead><tr><th>{idText("Capability")}</th><th>{idText("Evidence class")}</th><th>Status</th><th>{idText("Reason")}</th></tr></thead><tbody>{data.semantic_readiness.map((row) => <tr key={row.capability}><td><strong>{row.capability}</strong></td><td><EvidenceBadge value={row.evidence_class} /></td><td><ReadinessBadge status={row.status} /></td><td className="wide-cell">{row.reason}</td></tr>)}</tbody></table></TableFrame></SectionCard>

      <SectionCard className="trust-integrity-card"><div className="section-heading"><div><p className="eyebrow">{idText("Existing integrity evidence")}</p><h2>{idText("Reference integrity remains available")}</h2></div><Link className="text-link" href="/">{idText("Back to Executive Overview →")}</Link></div><div className="integrity-cards"><div><span>{idText("Registry")}</span><strong>{formatNumber(data.integrity.registered_assets_resolved)} <small>/ {formatNumber(data.integrity.registered_assets_total)}  {idText("resolved")}</small></strong><em>{formatNumber(data.integrity.registered_assets_unresolved)}  {idText("unresolved")}</em></div><div><span>{idText("Asset references")}</span><strong>{formatNumber(data.integrity.asset_refs_resolved)} <small>/ {formatNumber(data.integrity.asset_refs_total)}  {idText("resolved")}</small></strong><em>{formatNumber(data.integrity.asset_refs_unresolved)}  {idText("unresolved")}</em></div><div><span>{idText("Work Order references")}</span><strong>{formatNumber(data.integrity.workorder_refs_resolved)} <small>/ {formatNumber(data.integrity.workorder_refs_total)}  {idText("resolved")}</small></strong><em>{formatNumber(data.integrity.workorder_refs_unresolved)}  {idText("unresolved")}</em></div><div><span>{idText("Technical context")}</span><strong>{formatNumber(data.integrity.technical_asset_context_total)}</strong><em>{idText("asset_master context · factual")}</em></div></div></SectionCard>

      <div className="overview-grid trust-bottom-grid"><SectionCard><div className="section-heading"><div><p className="eyebrow">{idText("Current product boundary")}</p><h2>{idText("Available now")}</h2></div></div><ul className="trust-list"><li>{idText("Asset Reliability and Registry-scoped Maintenance activity")}</li><li>{idText("Repeat Activity investigation")}</li><li>{idText("FMEA header assessment records")}</li><li>{idText("Asset Health assessment records")}</li><li>{idText("Global RCFA records")}</li><li>{idText("Overhaul execution evidence")}</li></ul><p className="section-note">{idText("These are evidence surfaces, not a claim that every domain has complete historical coverage.")}</p></SectionCard><SectionCard><div className="section-heading"><div><p className="eyebrow">{idText("Future verification backlog")}</p><h2>{idText("Requires source or business verification")}</h2></div></div><ul className="trust-list"><li>{idText("FMEA item semantics and failure-mode details")}</li><li>{idText("RCFA Asset, Work Order, root-cause, and action relationships")}</li><li>{idText("Asset Health Wellness, ACR, MPI, and condition semantics")}</li><li>{idText("Overhaul status, progress, inspection, and date boundaries")}</li><li>{idText("Maintenance failure-code semantics and repeat-failure identity")}</li><li>{idText("PI/DCS model for future PdM")}</li></ul><p className="section-note">{idText("PI/DCS/CEMS are not represented as connected live systems in this Trust Center.")}</p></SectionCard></div>

      <SectionCard className="trust-limitations"><div className="section-heading"><div><p className="eyebrow">{idText("Data boundaries")}</p><h2>{idText("Read the evidence in context")}</h2></div></div><ul className="trust-list">{data.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></SectionCard>
    </>}
  </>;
}
