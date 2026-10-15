import type { FreshnessDimension, IntegrationStatus } from "../lib/api";
import { integrationComponents, evidenceTime, schemaReadiness } from "../lib/integration";
import { statusLabel } from "../lib/id-copy";
import { EmptyState, StatusBadge } from "./ui";

export function EvidenceTime({ value }: { value: string | null | undefined }) {
  const stamp = evidenceTime(value);
  return stamp ? <time dateTime={stamp}>{stamp.replace("T", " ").replace(".000Z", " UTC").replace("Z", " UTC")}</time> : <span>Belum diketahui (UNKNOWN)</span>;
}
function Dimension({ label, value }: { label: string; value?: FreshnessDimension }) {
  return <div className="integration-dimension"><dt>{label}</dt><dd><StatusBadge mode="raw-neutral" value={value?.state || "UNKNOWN"} /><small>Waktu bukti: <EvidenceTime value={value?.observed_at} /></small><small>Batas usia kebijakan: {value?.max_age_seconds != null && Number.isFinite(value.max_age_seconds) && value.max_age_seconds > 0 ? `${value.max_age_seconds} detik` : "Belum diketahui / tidak dikonfigurasi (UNKNOWN)"}</small></dd></div>;
}
export default function IntegrationComponentCards({ data }: { data: IntegrationStatus }) {
  const components = data.components ?? [];
  return <>
    <p className="section-note">Observasi DTO integrasi: <EvidenceTime value={data.observed_at} />. Status ditampilkan sesuai API; tidak dihitung ulang oleh tampilan.</p>
    {components.length === 0 ? <EmptyState title="Belum ada bukti komponen." detail="Komponen yang tidak dilaporkan tetap UNKNOWN, bukan otomatis tidak terhubung." /> : <div className="integration-component-grid">{components.map(component => <article className="integration-component" key={component.component} aria-label={integrationComponents[component.component]?.title ?? component.component}>
      <div className="integration-component-heading"><div><h3>{integrationComponents[component.component]?.title ?? component.component}</h3><span className="integration-code">{component.component}</span></div><StatusBadge mode="raw-neutral" value={component.state || "UNKNOWN"} /></div>
      <p className="section-note">{integrationComponents[component.component]?.context ?? "Komponen dilaporkan oleh DTO integrasi; batas interpretasinya memerlukan review."}</p>
      <dl className="integration-dimensions"><div className="integration-dimension"><dt>Ketersediaan komponen</dt><dd><StatusBadge mode="raw-neutral" value={component.availability || "UNKNOWN"} /></dd></div>
        <Dimension label="Freshness pengumpulan" value={component.collection_freshness} />
        <Dimension label="Freshness sumber" value={component.source_freshness} />
        <Dimension label="Freshness proyeksi" value={component.projection_freshness} />
        <div className="integration-dimension"><dt>Kesiapan identitas / mapping</dt><dd><StatusBadge mode="raw-neutral" value={component.mapping_readiness || "UNKNOWN"} /></dd></div>
        <div className="integration-dimension"><dt>Kualitas data</dt><dd><StatusBadge mode="raw-neutral" value={component.quality || "UNKNOWN"} /></dd></div>
      </dl>
      <p className="section-note">Aktivitas sukses terakhir: <EvidenceTime value={component.last_successful_activity} />. Sukses historis tidak membuktikan konektivitas saat ini.</p>
      <details className="integration-reasons"><summary>Alasan dan batas bukti ({component.degraded_reasons?.length ?? 0})</summary>{component.degraded_reasons?.length ? <ul>{component.degraded_reasons.map(reason => <li key={reason}>{statusLabel(reason)}</li>)}</ul> : <p>Tidak ada alasan yang dilaporkan; bukan bukti kesiapan operasional.</p>}</details>
    </article>)}</div>}
    <dl className="integration-schema"><div><dt>Schema governance</dt><dd>{schemaReadiness(data.governance_schema_ready)}</dd></div><div><dt>Schema bukti kondisi</dt><dd>{schemaReadiness(data.condition_schema_ready)}</dd></div></dl>
    <p className="section-note">Kesiapan schema di atas hanya kompatibilitas read model, bukan pemeriksaan migration ledger atau persetujuan migrasi.</p>
  </>;
}
