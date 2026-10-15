"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, reliabilityApi, type DataTrustView } from "../lib/api";
import { evidenceCount } from "../lib/integration";
import { statusLabel } from "../lib/id-copy";
import { Breadcrumbs, Button, EmptyState, LoadingState, PageHeader, SectionCard, StatCard, StatusBadge, TableFrame } from "./ui";
import IntegrationComponentCards, { EvidenceTime } from "./IntegrationComponentCards";

// Each read settles independently. No polling, operational refresh or source command.
function useEvidence<T>(read: () => Promise<T>) {
  const [state, setState] = useState<{ loading: boolean; data: T | null; error: string | null }>({ loading: true, data: null, error: null });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setState({ loading: true, data: null, error: null });
    read().then(data => { if (active) setState({ loading: false, data, error: null }); })
      .catch((error: unknown) => { if (active) setState({ loading: false, data: null, error: error instanceof ApiError && [401, 403].includes(error.status) ? "Akses bukti ditolak. Gunakan akses deployment yang berwenang; tidak ada bypass otorisasi." : "API bukti lokal tidak tersedia. Status tidak dapat diverifikasi (UNKNOWN)." }); });
    return () => { active = false; };
  }, [read, attempt]);
  return { ...state, retry: () => setAttempt(value => value + 1) };
}
function EvidenceError({ title, message, retry }: { title: string; message: string; retry: () => void }) {
  return <div className="state-card error-state" role="alert"><h3>{title}</h3><p>{message}</p><Button onClick={retry}>Baca ulang bukti lokal</Button></div>;
}
const domainNames: Record<DataTrustView["domains"][number]["domain"], string> = { ASSET: "Aset", MAINTENANCE: "Pemeliharaan", FMEA: "FMEA", ASSET_HEALTH: "Rekam penilaian aset", RCFA: "RCFA", OVERHAUL: "Overhaul" };
const technicalLinks = [
  ["/data-quality", "Data Trust Center", "Rincian populasi, provenance dan batas semantik."],
  ["/maintenance", "Pemeliharaan", "Aktivitas maintenance dalam lingkup Registry."],
  ["/work-orders", "Work Orders", "Rujukan Work Order lokal, read-only."],
  ["/fmea", "FMEA", "Rekam assessment; bukan skor risiko otomatis."],
  ["/rcfa", "RCFA", "Rekam global dan hubungan yang belum terselesaikan."],
  ["/overhauls", "Overhaul", "Bukti pelaksanaan dan resolusi relasi existing."],
] as const;

export default function SystemIntegrationCenter() {
  const integration = useEvidence(reliabilityApi.integrationStatus);
  const trust = useEvidence(reliabilityApi.dataTrust);
  const coverage = integration.data?.coverage;
  return <div className="integration-workspace">
    <Breadcrumbs items={[{ label: "NADI", href: "/" }, { label: "Integrasi Sistem" }]} />
    <PageHeader eyebrow="NADI / Bukti integrasi" title="Pusat Integrasi Sistem" description="Telusuri bukti integrasi yang tersimpan, cakupan identitas dan kesiapan data untuk tampilan NADI." actions={<a className="button secondary" href="#integration-navigation">Buka domain teknis ↓</a>} />
    <div className="scope-banner"><span className="dataset-badge">DEVELOPMENT · READ-ONLY</span><span>Kandidat produk; bukan penerimaan operasional. Tidak ada kontrol collector atau perubahan kebijakan.</span></div>
    <section aria-label="Ringkasan cakupan" className="integration-summary">
      <StatCard label="Aset bisnis terdaftar" value={evidenceCount(coverage?.registered_assets)} detail="Registry · DTO integrasi" />
      <StatCard label="Aset dengan mapping terverifikasi" value={evidenceCount(coverage?.verified_mapping_assets)} detail="Identitas governed · bukan skor kondisi" />
      <StatCard label="Konteks aset teknis" value={evidenceCount(trust.data?.population.technical_asset_context)} detail="Data Trust · populasi lebih luas, terpisah" />
      <StatCard label="Aset dengan bukti kondisi terproyeksi" value={evidenceCount(coverage?.projected_assets)} detail="Bukti tersedia · bukan penilaian kesehatan" />
    </section>
    <SectionCard><div className="section-heading"><div><p className="eyebrow">01 / Bukti per komponen</p><h2>Availability dan freshness tetap terpisah</h2></div></div>
      <p>Ketersediaan, pengumpulan, waktu sumber, proyeksi, identitas dan kualitas adalah dimensi independen. Kebijakan atau waktu yang tidak tersedia tetap UNKNOWN. Tanggal rekam sumber bukan freshness collector.</p>
      {integration.loading ? <LoadingState label="Membaca bukti integrasi lokal…" /> : integration.error ? <EvidenceError title="Bukti integrasi tidak tersedia" message={integration.error} retry={integration.retry} /> : integration.data ? <IntegrationComponentCards data={integration.data} /> : <EmptyState title="Bukti integrasi belum tersedia." />}
      <p className="section-note">Komponen yang tidak ada dalam respons tidak dapat diverifikasi. CEMS belum memiliki DTO status pada kontrak ini; tidak diberi status terhubung, sehat, atau terputus. Bukti koleksi CEMS juga bukan validasi pelaporan emisi.</p>
    </SectionCard>
    <SectionCard><div className="section-heading"><div><p className="eyebrow">02 / Arsitektur logis</p><h2>Dari sumber menuju tampilan produk</h2></div></div>
      <ol className="integration-pipeline" aria-label="Hubungan data logis">{[
        ["Sistem sumber", "Maximo / PI / CEMS: batas sumber masing-masing tetap berlaku."],
        ["Collector lokal", "Riwayat akuisisi dan snapshot yang sudah tersimpan."],
        ["Proyeksi / Reliability Mart", "Store milik komponen; Mart berada di database Maximo Collector."],
        ["Tampilan NADI", "Populasi Registry dan bukti governed sesuai kontrak."],
      ].map(([title, detail], index) => <li key={title}><span className="integration-step">0{index + 1}</span><h3>{title}</h3><p>{detail}</p></li>)}</ol>
      <p className="section-note">Diagram menjelaskan hubungan arsitektur, bukan bukti bahwa semua jalur sedang aktif. Status aktual hanya mengikuti DTO. Tidak ada permintaan langsung ke sistem sumber dari halaman ini.</p>
    </SectionCard>
    <SectionCard><div className="section-heading"><div><p className="eyebrow">03 / Cakupan dan kepercayaan</p><h2>Registry bisnis ≠ inventaris teknis</h2></div><Link className="text-link" href="/data-quality">Rincian Data Trust →</Link></div>
      <p className="section-note">PI teknis: {evidenceCount(coverage?.technical_registry_active)} atribut aktif / {evidenceCount(coverage?.technical_registry_total)} total · {evidenceCount(coverage?.technical_snapshots)} snapshot tersimpan. Atribut teknis bukan otomatis sinyal kondisi aset yang disetujui.</p>
      <p className="section-note">Mapping ambigu: {evidenceCount(coverage?.ambiguous_mapping_assets)} aset · aset dengan sinyal disetujui: {evidenceCount(coverage?.approved_signal_assets)} · sinyal disetujui / terproyeksi: {evidenceCount(coverage?.approved_signals)} / {evidenceCount(coverage?.projected_signals)}.</p>
      {trust.loading ? <LoadingState label="Membaca ringkasan Data Trust…" /> : trust.error ? <EvidenceError title="Data Trust tidak tersedia" message={trust.error} retry={trust.retry} /> : trust.data ? <>
        <p>Lingkup: {trust.data.scope.site_code} / {trust.data.scope.organization_code} · sumber {trust.data.scope.source_system}. Registry Data Trust: {evidenceCount(trust.data.population.registered_reliability_assets)}; terselesaikan {evidenceCount(trust.data.population.registry_resolved)}, belum terselesaikan {evidenceCount(trust.data.population.registry_unresolved)}. Angka DTO dibaca terpisah dan tidak dijumlahkan.</p>
        <p className="section-note">Data Trust tidak menyediakan timestamp observasi mandiri. Tanggal rekam di bawah bukan waktu observasi, sinkronisasi, atau penilaian freshness.</p>
        {trust.data.domains.length ? <TableFrame minWidth={760} label="Cakupan domain Data Trust"><table><thead><tr><th scope="col">Domain / sumber</th><th scope="col">Populasi / jumlah</th><th scope="col">Dalam scope</th><th scope="col">Tanggal rekam / basis</th><th scope="col">Relasi / batas</th></tr></thead><tbody>{trust.data.domains.map(domain => <tr key={domain.domain}><th scope="row">{domainNames[domain.domain] ?? domain.domain}<small className="integration-source">{domain.source_system} · {domain.source_object}</small></th><td>{domain.population_type}<br />{evidenceCount(domain.record_count)} <StatusBadge mode="raw-neutral" value={domain.evidence_class} /></td><td>{evidenceCount(domain.scoped_record_count)}<small className="integration-source">{domain.business_scope}</small></td><td><EvidenceTime value={domain.latest_record_date} /><small className="integration-source">{domain.date_basis}</small></td><td>{statusLabel(domain.relationship_state)}<small className="integration-source">{domain.known_limitation}</small></td></tr>)}</tbody></table></TableFrame> : <EmptyState title="Populasi domain belum dilaporkan." detail="Tidak ada baris bukan bukti populasi nol atau sumber terputus." />}
        <details className="integration-reasons"><summary>Relasi dan provenance Data Trust</summary>{trust.data.relationships.length ? <ul>{trust.data.relationships.map(row => <li key={row.relationship}><strong>{row.relationship}</strong> — {statusLabel(row.evidence)}; terselesaikan {evidenceCount(row.resolved_count)}, belum terselesaikan {evidenceCount(row.unresolved_count)}, konteks teknis {evidenceCount(row.technical_context_count)}. {row.interpretation}</li>)}</ul> : <p>Belum ada bukti relasi.</p>}{trust.data.limitations.map(item => <p key={item}>{item}</p>)}</details>
      </> : <EmptyState title="Data Trust belum tersedia." />}
    </SectionCard>
    <SectionCard><div id="integration-navigation" className="section-heading"><div><p className="eyebrow">04 / Jelajahi bukti</p><h2>Domain teknis existing</h2></div></div><nav className="integration-links" aria-label="Navigasi domain teknis">{technicalLinks.map(([href, title, detail]) => <Link href={href} key={href}><strong>{title} <span aria-hidden="true">↗</span></strong><span>{detail}</span></Link>)}</nav></SectionCard>
    <p className="section-note">Tidak ada health score, diagnosis, keputusan engineer, aktivasi integrasi, atau perubahan expiry. Kebijakan yang kedaluwarsa tidak menjadi disetujui kembali karena halaman dibuka.</p>
  </div>;
}
