import Link from "next/link";
import type { DecisionOverviewView, EvidenceValue, IntegrityView } from "../lib/api";
import { chartCount, reportMetric, type ReportCandidate } from "../lib/reports";
import { evidenceCount } from "../lib/integration";
import { EvidenceTime } from "./IntegrationComponentCards";
import { EmptyState, StatCard, StatusBadge, TableFrame } from "./ui";

export function ReportMetric({ label, value, detail }: { label: string; value?: EvidenceValue | null; detail: string }) {
  return <StatCard label={label} value={reportMetric(value)} detail={`${detail} · ${value?.evidence_class || "UNKNOWN"}`} />;
}
export function ReportProvenance({ candidate, scope, period, asOf, dateBasis }: { candidate: ReportCandidate; scope: string; period: string; asOf?: string; dateBasis: string }) {
  return <details className="report-provenance" open><summary>Provenance dan definisi kandidat</summary><dl>
    <div><dt>Identitas / versi definisi</dt><dd>{candidate.definition} / {candidate.version} · kandidat, belum disahkan</dd></div>
    <div><dt>Kontrak / API sumber</dt><dd>{candidate.contract} · GET {candidate.api}</dd></div>
    <div><dt>Lingkup dikembalikan API</dt><dd>{scope}</dd></div><div><dt>Periode</dt><dd>{period}</dd></div>
    <div><dt>As-of authoritative DTO</dt><dd>{asOf ? <EvidenceTime value={asOf} /> : "Tidak disediakan DTO (UNKNOWN)"}</dd></div>
    <div><dt>Basis waktu / evidence</dt><dd>{dateBasis}. Klasifikasi bukti ditampilkan per metrik/domain, tanpa skor gabungan.</dd></div>
  </dl><p className="section-note">Waktu fetch browser bukan as-of sumber. Kedua endpoint bukan satu snapshot atomik. Preview ini bukan laporan operasional yang disetujui; completeness historis tidak dibuktikan.</p></details>;
}
export function ReportIntegrity({ data }: { data?: IntegrityView }) {
  return <><p className="section-note">Konteks integritas populasi Mart yang dikembalikan DTO; bukan hitungan kejadian dalam periode pilihan. DTO ini tidak memberi evidence class per field integrity.</p><TableFrame minWidth={540} label="Konteks integritas laporan"><table><thead><tr><th scope="col">Referensi</th><th scope="col">Total</th><th scope="col">Terselesaikan</th><th scope="col">Belum terselesaikan</th></tr></thead><tbody>{[
    ["Registry bisnis", data?.registered_assets_total, data?.registered_assets_resolved, data?.registered_assets_unresolved],
    ["Referensi aset", data?.asset_refs_total, data?.asset_refs_resolved, data?.asset_refs_unresolved],
    ["Referensi Work Order", data?.workorder_refs_total, data?.workorder_refs_resolved, data?.workorder_refs_unresolved],
  ].map(([label, total, resolved, unresolved]) => <tr key={String(label)}><th scope="row">{label}</th><td>{evidenceCount(total as number | undefined)}</td><td>{evidenceCount(resolved as number | undefined)}</td><td>{evidenceCount(unresolved as number | undefined)}</td></tr>)}</tbody></table></TableFrame><Link href="/data-quality" className="text-link">Telusuri Data Trust →</Link></>;
}
export function ReportActivity({ rows }: { rows: DecisionOverviewView["maintenance_activity"] }) {
  if (!rows?.length) return <EmptyState title="Kronologi belum tersedia." detail="Tidak ada bucket bukan bukti tidak ada aktivitas atau kondisi peralatan normal." />;
  const max = Math.max(0, ...rows.map(row => chartCount(row.event_count) ?? 0));
  return <figure className="report-activity"><figcaption>Kronologi bucket API · aktivitas, bukan kegagalan</figcaption><p className="section-note">Kronologi memiliki rentang bucket sendiri (API existing: 12 minggu), terpisah dari periode ringkasan pilihan. Bucket tidak dipotong, diisi atau diinterpolasi; batas bucket terakhir dapat melewati as-of, bukan klaim satu minggu selesai.</p>
    <div className="report-chart-scroll" role="region" tabIndex={0} aria-label="Grafik aktivitas dengan rentang bucket asli"><div className="report-bars" style={{ gridTemplateColumns: `repeat(${rows.length}, minmax(48px, 1fr))` }}>{rows.map((row, index) => {
      const count = chartCount(row.event_count);
      return <div key={`${row.period_start}-${index}`} className="report-bar"><strong>{reportMetric(row.event_count)}</strong><div className="report-bar-track" aria-hidden="true">{count !== null && <span style={{ height: `${max > 0 ? count / max * 100 : 0}%` }} />}</div><small>Bucket {index + 1}</small></div>;
    })}</div></div>
    <TableFrame minWidth={650} label="Tabel ekuivalen grafik aktivitas"><table><thead><tr><th scope="col">Bucket</th><th scope="col">Mulai asli</th><th scope="col">Akhir asli</th><th scope="col">Aktivitas</th><th scope="col">Evidence class</th></tr></thead><tbody>{rows.map((row,index) => <tr key={`${row.period_start}-${index}`}><th scope="row">{index + 1}</th><td><EvidenceTime value={row.period_start} /></td><td><EvidenceTime value={row.period_end} /></td><td>{reportMetric(row.event_count)}</td><td><StatusBadge mode="raw-neutral" value={row.event_count?.evidence_class || "UNKNOWN"} /></td></tr>)}</tbody></table></TableFrame>
  </figure>;
}
export function ReportDistribution({ label, rows }: { label: string; rows: DecisionOverviewView["status_distribution"] }) {
  if (!rows?.length) return <EmptyState title={`${label} belum tersedia.`} detail="Tidak ada baris bukan klasifikasi kondisi normal." />;
  return <TableFrame minWidth={360} label={label}><table><thead><tr><th scope="col">Nilai sumber</th><th scope="col">Jumlah aktivitas</th><th scope="col">Evidence class</th></tr></thead><tbody>{rows.map((row,index) => <tr key={`${row.value}-${index}`}><th scope="row">{row.value || "UNKNOWN"}</th><td>{reportMetric(row.count)}</td><td><StatusBadge mode="raw-neutral" value={row.count?.evidence_class || "UNKNOWN"} /></td></tr>)}</tbody></table></TableFrame>;
}
