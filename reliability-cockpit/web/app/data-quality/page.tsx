"use client";

import { useEffect, useState } from "react";
import { reliabilityApi, type IntegrityView } from "../../lib/api";
import { formatNumber } from "../../lib/format";
import { ErrorState, LoadingState, PageHeader, SectionCard, StatCard } from "../../components/ui";

export default function DataQualityPage() {
  const [integrity, setIntegrity] = useState<IntegrityView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    reliabilityApi.integrity().then((next) => { setIntegrity(next); setError(null); }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Reliability Mart unavailable")).finally(() => setLoading(false));
  }, []);
  return <>
    <PageHeader eyebrow="Trust & reference health" title="Data Quality" description="Memeriksa apakah hubungan canonical dapat diselesaikan di dalam dataset Mart yang tersedia." actions={<span className="scope-chip">BSR / IP</span>} />
    <div className="scope-banner"><span className="dataset-badge compact">Controlled Initial Dataset</span><span>Unresolved references dapat terjadi karena target berada di luar bounded MX-011R sample.</span></div>
    {loading && <LoadingState />}{!loading && error && <ErrorState message={error} />}{!loading && !error && integrity && <>
      <section className="stat-grid quality-stat-grid"><StatCard label="Asset references" value={`${formatNumber(integrity.asset_refs_resolved)} / ${formatNumber(integrity.asset_refs_total)}`} detail={`${formatNumber(integrity.asset_refs_unresolved)} unresolved`} tone="accent" /><StatCard label="Work Order references" value={`${formatNumber(integrity.workorder_refs_resolved)} / ${formatNumber(integrity.workorder_refs_total)}`} detail={`${formatNumber(integrity.workorder_refs_unresolved)} unresolved`} /></section>
      <SectionCard className="quality-explanation"><p className="eyebrow">How to interpret</p><h2>Reference health, not a source-system score</h2><p>Angka ini menunjukkan apakah referensi antar-record canonical menemukan target dalam Mart saat ini. Karena MX-011R adalah controlled initial load dan sebagian koleksi dibatasi, unresolved tidak otomatis berarti data Maximo salah atau rusak.</p><div className="quality-legend"><div><span className="legend-dot resolved" /><strong>Resolved</strong><small>Target ditemukan di dataset Mart</small></div><div><span className="legend-dot unresolved" /><strong>Unresolved</strong><small>Target belum ada di bounded dataset saat ini</small></div></div></SectionCard>
    </>}
  </>;
}
