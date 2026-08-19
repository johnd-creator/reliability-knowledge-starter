"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { collectorApi, AttributeView, SnapshotView, HeatmapResponse, timeAgo, ScheduleView } from "@/lib/api";
import { Heatmap } from "../Heatmap";

export default function AttributeDetailPage({ params }: { params: Promise<{ attributeId: string }> }) {
  const [attributeId, setAttributeId] = useState<string>("");
  const [attr, setAttr] = useState<AttributeView | null>(null);
  const [snapshot, setSnapshot] = useState<SnapshotView | null>(null);
  const [heatmap, setHeatmap] = useState<HeatmapResponse | null>(null);
  const [schedule, setSchedule] = useState<ScheduleView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [, setTick] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    params.then((p) => setAttributeId(decodeURIComponent(p.attributeId)));
  }, [params]);

  const load = useCallback(async () => {
    if (!attributeId) return;
    try {
      const [attrs, snap] = await Promise.all([
        collectorApi.listAttributes(),
        collectorApi.getSnapshot(attributeId),
      ]);
      const found = attrs.find((a) => a.attribute_id === attributeId);
      setAttr(found || null);
      setSnapshot(snap);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, [attributeId]);

  useEffect(() => {
    if (!attributeId) return;
    setLoading(true);
    load();
    collectorApi.getHeatmap(attributeId, 365).then(setHeatmap).catch(() => setHeatmap(null));
  }, [attributeId, load]);

  // Auto-refresh snapshot when schedule updates
  useEffect(() => {
    let cancelled = false;
    const pollSchedule = async () => {
      try {
        const s = await collectorApi.getSchedule();
        if (!cancelled) setSchedule(s);
      } catch {
        /* schedule unknown */
      }
    };
    pollSchedule();
    const poll = setInterval(pollSchedule, 15_000);
    const ticker = setInterval(() => setTick((n) => n + 1), 30_000);
    return () => {
      cancelled = true;
      clearInterval(poll);
      clearInterval(ticker);
    };
  }, []);

  useEffect(() => {
    if (!schedule) return;
    if (schedule.state === "running") {
      const t = setInterval(load, 20_000);
      return () => clearInterval(t);
    }
    if (schedule.state !== "scheduled") return;
    const next = schedule.next_run_at ? new Date(schedule.next_run_at).getTime() : null;
    if (!next) return;
    const ms = Math.max(0, next - Date.now()) + 5_000;
    const t = setTimeout(load, ms);
    return () => clearTimeout(t);
  }, [schedule, load]);

  const handleCopy = () => {
    navigator.clipboard.writeText(attributeId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div style={{ padding: "64px 0", textAlign: "center" }}>
        <div className="dot dot-green dot-pulse" style={{ width: 16, height: 16, margin: "0 auto 16px" }} />
        <p className="muted">Memuat detail atribut telemetri...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="collect-result err" style={{ padding: 16, fontSize: "1rem" }}>
        <span>✗ Error:</span>
        <span className="mono">{error}</span>
      </div>
    );
  }

  return (
    <div>
      {/* Breadcrumb Navigation */}
      <div style={{ marginBottom: 20 }}>
        <Link href="/" className="btn btn-ghost" style={{ padding: "6px 12px", fontSize: "0.85rem" }}>
          ← Kembali ke Semua Atribut
        </Link>
      </div>

      {/* Hero Telemetry Banner */}
      <div className="detail-hero">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
          <div>
            <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
              {attr?.equipment && <span className="badge badge-equipment">{attr.equipment}</span>}
              {attr?.parameter && <span className="badge badge-param">{attr.parameter}</span>}
              {attr?.position && <span className="badge badge-null">Pos: {attr.position}</span>}
            </div>
            <h1 style={{ fontSize: "1.85rem", marginBottom: 6 }}>
              {attr?.business_name || attributeId}
            </h1>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className="sub-muted mono">{attributeId}</span>
              <button
                type="button"
                onClick={handleCopy}
                className="btn btn-ghost"
                style={{ padding: "2px 6px", fontSize: "0.72rem" }}
              >
                {copied ? "✓ Copied!" : "📋 Salin ID"}
              </button>
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            {snapshot ? (
              <span className={`badge ${snapshot.value_good ? "badge-good" : "badge-bad"}`} style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
                <span className={`dot ${snapshot.value_good ? "dot-green" : "dot-red"}`} style={{ width: 8, height: 8 }} />
                {snapshot.value_good ? "Signal Quality: GOOD" : "Signal Quality: BAD / UNCERTAIN"}
              </span>
            ) : (
              <span className="badge badge-null">No Snapshot Yet</span>
            )}
          </div>
        </div>

        {/* Big Snapshot Display */}
        {snapshot && (
          <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid rgba(255, 255, 255, 0.08)" }}>
            <div className="sub-muted" style={{ fontWeight: 700, letterSpacing: "0.05em", textTransform: "uppercase" }}>
              Live Snapshot Value
            </div>
            <div className="snapshot-display">
              <span className="snapshot-large-val mono">
                {snapshot.value != null ? snapshot.value.toFixed(2) : "—"}
              </span>
              {(snapshot.units || attr?.unit_of_measure) && (
                <span className="snapshot-uom mono">
                  {snapshot.units || attr?.unit_of_measure}
                </span>
              )}
            </div>

            <div style={{ display: "flex", gap: 24, flexWrap: "wrap", fontSize: "0.85rem" }}>
              <div className="muted">
                <span className="sub-muted">Waktu Pengukuran PI: </span>
                <strong className="mono" style={{ color: "#fff" }}>
                  {snapshot.source_timestamp
                    ? `${new Date(snapshot.source_timestamp).toLocaleString("id-ID")} (${timeAgo(snapshot.source_timestamp)})`
                    : "—"}
                </strong>
              </div>
              {snapshot.collected_at && (
                <div className="muted">
                  <span className="sub-muted">Terakhir Diunduh Collector: </span>
                  <span className="mono">
                    {new Date(snapshot.collected_at).toLocaleTimeString("id-ID")}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Metadata Specification Grid */}
      <div className="card">
        <h2>
          <span>📋</span> Spesifikasi & Pemetaan AF (PI Asset Framework)
        </h2>
        <div className="meta-grid">
          <div className="meta-item">
            <div className="meta-item-label">Equipment</div>
            <div className="meta-item-val">{attr?.equipment || "—"}</div>
          </div>
          <div className="meta-item">
            <div className="meta-item-label">Parameter</div>
            <div className="meta-item-val">{attr?.parameter || "—"}</div>
          </div>
          <div className="meta-item">
            <div className="meta-item-label">Position / Measurement Point</div>
            <div className="meta-item-val">{attr?.position || "—"}</div>
          </div>
          <div className="meta-item">
            <div className="meta-item-label">Unit of Measure (UoM)</div>
            <div className="meta-item-val mono">{attr?.unit_of_measure || "—"}</div>
          </div>
          <div className="meta-item">
            <div className="meta-item-label">Plant Site</div>
            <div className="meta-item-val">{attr?.site || "BSR"}</div>
          </div>
          <div className="meta-item">
            <div className="meta-item-label">Plant Unit</div>
            <div className="meta-item-val">{attr?.unit || "BSR1"}</div>
          </div>
        </div>
      </div>

      {/* Data Coverage (Historian) */}
      <div className="card">
        <h2>
          <span>📈</span> Cakupan Data Historian (TimescaleDB Hypertable)
        </h2>
        <p className="muted" style={{ marginBottom: 16 }}>
          Riwayat ketersediaan titik data 365 hari terakhir. Setiap sel merepresentasikan 1 hari.
        </p>
        <Heatmap data={heatmap} />
      </div>
    </div>
  );
}
