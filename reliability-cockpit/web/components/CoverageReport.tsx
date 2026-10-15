import Link from "next/link";
import type { DataTrustView } from "../lib/api";
import { evidenceCount } from "../lib/integration";
import { reportCandidates } from "../lib/reports";
import { EvidenceTime } from "./IntegrationComponentCards";
import { ReportIntegrity, ReportProvenance } from "./ReportEvidence";
import { EmptyState, SectionCard, StatCard, StatusBadge, TableFrame } from "./ui";

const domains = { ASSET: ["Aset terdaftar", "/assets"], MAINTENANCE: ["Pemeliharaan", "/maintenance"], FMEA: ["FMEA", "/fmea"], ASSET_HEALTH: ["Rekam penilaian aset", "/asset-health"], RCFA: ["RCFA", "/rcfa"], OVERHAUL: ["Overhaul", "/overhauls"] } as const;
export default function CoverageReport({ data }: { data: DataTrustView }) {
  const p = data.population;
  return <>
    <ReportProvenance candidate={reportCandidates[0]} scope={`${data.scope.site_code} / ${data.scope.organization_code} · ${data.scope.source_system} · ${data.scope.registered_asset_boundary}`} period="Tidak ada filter periode pada DataTrustView; seluruh populasi yang dikembalikan API." dateBasis="Tanggal rekam berbeda per domain; bukan timestamp observasi independen atau freshness sinkronisasi" />
    <SectionCard><div className="section-heading"><h3>Populasi yang berbeda, tidak dijumlahkan</h3></div><p className="section-note">Angka langsung dari population DTO; evidence class per field tidak disediakan. Klasifikasi domain dilaporkan terpisah di tabel berikutnya. Populasi terbatas bukan bukti kelengkapan historis.</p><div className="report-metrics">{[
      ["Registry bisnis", p?.registered_reliability_assets, "BUSINESS REGISTRY · berbeda dari konteks teknis"],
      ["Konteks aset teknis", p?.technical_asset_context, "TECHNICAL CONTEXT · bukan anggota Registry otomatis"],
      ["Aktivitas maintenance tersimpan", p?.maintenance_total, `Populasi lokal; dalam Registry: ${evidenceCount(p?.registry_maintenance)}`],
      ["Rekam FMEA", p?.fmea, "Populasi terkelola, bukan skor risiko"],
      ["Rekam penilaian aset", p?.asset_health, "Assessment records, bukan health score"],
      ["Rekam RCFA", p?.rcfa, "Populasi global; relasi aset tidak diasumsikan"],
      ["Rekam Overhaul", p?.overhaul, "Bukan KPI penyelesaian atau performa"],
    ].map(([label,value,detail]) => <StatCard key={String(label)} label={String(label)} value={evidenceCount(value as number | undefined)} detail={String(detail)} />)}</div></SectionCard>
    <SectionCard><div className="section-heading"><h3>Bukti domain dan basis tanggal</h3></div><p className="section-note">Tanggal rekam sumber bukan freshness pengumpulan/sinkronisasi. Nol tetap nol; null tetap UNKNOWN.</p>{data.domains?.length ? <TableFrame minWidth={850} label="Domain cakupan laporan"><table><thead><tr><th scope="col">Domain / provenance</th><th scope="col">Populasi / scope</th><th scope="col">Jumlah</th><th scope="col">Klasifikasi bukti</th><th scope="col">Tanggal rekam / basis</th><th scope="col">Batas interpretasi</th></tr></thead><tbody>{data.domains.map(domain => <tr key={domain.domain}><th scope="row"><Link href={domains[domain.domain][1]} className="text-link">{domains[domain.domain][0]} →</Link><small>{domain.source_system} · {domain.source_object}</small></th><td>{domain.population_type}<small>{domain.business_scope}</small></td><td>{evidenceCount(domain.record_count)}<small>Dalam scope: {evidenceCount(domain.scoped_record_count)}</small></td><td><StatusBadge mode="raw-neutral" value={domain.evidence_class || "UNKNOWN"} /></td><td><EvidenceTime value={domain.latest_record_date} /><small>{domain.date_basis || "UNKNOWN"}</small></td><td>{domain.relationship_state || "UNKNOWN"}<small>{domain.known_limitation || "UNKNOWN"}</small></td></tr>)}</tbody></table></TableFrame> : <EmptyState title="Belum ada baris domain." detail="Tidak ada baris tidak menyatakan populasi nol atau sistem sehat." />}</SectionCard>
    <SectionCard><div className="section-heading"><h3>Integritas referensi dan batas bukti</h3></div><ReportIntegrity data={data.integrity} /><details className="report-provenance"><summary>Relasi, provenance dan keterbatasan</summary>{data.relationships?.length ? <ul>{data.relationships.map(row => <li key={row.relationship}><strong>{row.relationship}</strong> · {row.evidence}; resolved {evidenceCount(row.resolved_count)}, unresolved {evidenceCount(row.unresolved_count)}, technical {evidenceCount(row.technical_context_count)}. {row.interpretation}</li>)}</ul> : <p>Relasi belum dilaporkan (UNKNOWN).</p>}<p>{data.scope.interpretation}</p><ul>{data.limitations?.map(value => <li key={value}>{value}</li>)}</ul></details><p>Assessment bukan health score, Work Order bukan bukti kegagalan, dan relasi belum terselesaikan tidak dibuat otomatis.</p></SectionCard>
  </>;
}
