"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { collectorApi, type EquipmentView, timeAgo } from "@/lib/api";

export default function EquipmentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const decodedId = decodeURIComponent(id);
  const [row, setRow] = useState<EquipmentView | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setLoading(true);
    collectorApi
      .equipment(10000)
      .then((rows) => {
        setRow(rows.find((item) => item.id === decodedId) || null);
      })
      .catch(() => setRow(null))
      .finally(() => setLoading(false));
  }, [decodedId]);

  const handleCopy = () => {
    if (row?.id) {
      navigator.clipboard.writeText(row.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return <div className="empty page-empty">Memuat data spesifikasi equipment...</div>;
  }

  if (!row) {
    return (
      <div className="empty page-empty">
        <p>Equipment <strong>{decodedId}</strong> tidak ditemukan di local store.</p>
        <div style={{ marginTop: 16 }}>
          <Link href="/equipment" className="btn btn-primary">
            ← Kembali ke Daftar Equipment
          </Link>
        </div>
      </div>
    );
  }

  const extra = row.sources?.maximo?.extra || {};

  return (
    <>
      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 20 }}>
        <Link href="/equipment" className="back-link" style={{ margin: 0 }}>
          ← Kembali ke Equipment Explorer
        </Link>
        <span style={{ color: "var(--text-dim)" }}>/</span>
        <Link href="/" className="back-link" style={{ margin: 0 }}>
          Dashboard
        </Link>
      </div>

      <section className="detail-hero">
        <div>
          <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
            <p className="eyebrow" style={{ margin: 0 }}>
              EQUIPMENT / MXAPIASSET
            </p>
            {row.unit && <span className="count-pill">Unit: {row.unit}</span>}
            {row.equipment_class && <span className="count-pill">Class: {row.equipment_class}</span>}
          </div>
          <h1>{row.id}</h1>
          <p className="lede">{row.name || "No description provided"}</p>
        </div>

        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={handleCopy}
            title="Salin Asset ID ke clipboard"
          >
            {copied ? "✓ Copied!" : "📋 Copy ID"}
          </button>
          <span className={`status ${row.status?.toLowerCase() === "operating" ? "good" : ""}`} style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
            {row.status || "UNKNOWN"}
          </span>
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <p className="eyebrow">VENDOR-NEUTRAL CONTRACT FIELDS</p>
          <h2>Equipment Profile</h2>
          <dl className="facts">
            <div>
              <dt>Asset Tag / ID</dt>
              <dd className="mono">{row.id}</dd>
            </div>
            <div>
              <dt>Location ID</dt>
              <dd className="mono">{row.location_id || "—"}</dd>
            </div>
            <div>
              <dt>Plant Unit</dt>
              <dd>{row.unit || "—"}</dd>
            </div>
            <div>
              <dt>Equipment Class</dt>
              <dd>{row.equipment_class || "—"}</dd>
            </div>
            <div>
              <dt>Manufacturer</dt>
              <dd>{row.manufacturer || "—"}</dd>
            </div>
            <div>
              <dt>Vendor</dt>
              <dd>{row.vendor || "—"}</dd>
            </div>
            <div>
              <dt>Operating State</dt>
              <dd>{row.is_running === null ? "—" : row.is_running ? "Running" : "Stopped"}</dd>
            </div>
            <div>
              <dt>Priority</dt>
              <dd>{row.priority ?? "—"}</dd>
            </div>
            <div>
              <dt>Source Changed Date</dt>
              <dd className="mono">
                {row.source_changed_at ? new Date(row.source_changed_at).toLocaleString("id-ID") : "—"}
                {row.source_changed_at && <small style={{ display: "block", color: "var(--text-dim)" }}>({timeAgo(row.source_changed_at)})</small>}
              </dd>
            </div>
          </dl>
        </div>

        <div className="panel">
          <p className="eyebrow">VERIFIED SOURCE EXTENSIONS</p>
          <h2>Maximo Extra Fields</h2>
          <p className="panel-note">
            Field skalar tambahan dari pemetaan terverifikasi <code>MXAPIASSET</code>. Field ini tetap dikarantina di bawah <code>sources.maximo.extra</code>.
          </p>

          <div className="extra-grid">
            {Object.entries(extra).map(([key, value]) => (
              <div className="extra-item" key={key}>
                <code>{key}</code>
                <strong>{String(value)}</strong>
              </div>
            ))}
          </div>

          {Object.keys(extra).length === 0 && (
            <div className="empty">Tidak ada field ekstra tambahan untuk record ini.</div>
          )}
        </div>
      </section>
    </>
  );
}
