"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { collectorApi, type ServiceRequestView, timeAgo } from "@/lib/api";

export default function ServiceRequestDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const decodedId = decodeURIComponent(id);
  const [row, setRow] = useState<ServiceRequestView | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setLoading(true);
    collectorApi
      .serviceRequests(10000)
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
    return <div className="empty page-empty">Memuat detail Service Request...</div>;
  }

  if (!row) {
    return (
      <div className="empty page-empty">
        <p>Service Request <strong>{decodedId}</strong> tidak ditemukan di local store.</p>
        <div style={{ marginTop: 16 }}>
          <Link href="/service-requests" className="btn btn-primary">
            ← Kembali ke Service Requests
          </Link>
        </div>
      </div>
    );
  }

  const extra = row.sources?.maximo?.extra || {};

  return (
    <>
      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 20 }}>
        <Link href="/service-requests" className="back-link" style={{ margin: 0 }}>
          ← Kembali ke Service Requests
        </Link>
        <span style={{ color: "var(--text-dim)" }}>/</span>
        <Link href="/" className="back-link" style={{ margin: 0 }}>
          Dashboard
        </Link>
        <span style={{ color: "var(--text-dim)" }}>/</span>
        <span className="count-pill">Service Request #{row.id}</span>
      </div>

      <section className="detail-hero">
        <div>
          <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap", alignItems: "center" }}>
            <p className="eyebrow" style={{ margin: 0 }}>
              SERVICE REQUEST / MXAPISR
            </p>
            {row.work_type && <span className="count-pill">Type: {row.work_type}</span>}
            {row.reported_priority && <span className="count-pill">Priority: {row.reported_priority}</span>}
          </div>
          <h1>{row.id}</h1>
          <p className="lede">{row.description || "No description provided"}</p>
        </div>

        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={handleCopy}
            title="Salin SR ID ke clipboard"
          >
            {copied ? "✓ Copied!" : "📋 Copy SR #"}
          </button>
          <span className="status" style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
            {row.status || "UNKNOWN"}
          </span>
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <p className="eyebrow">VENDOR-NEUTRAL CONTRACT FIELDS</p>
          <h2>Service Request Profile</h2>
          <dl className="facts">
            <div>
              <dt>Service Request ID</dt>
              <dd className="mono">{row.id}</dd>
            </div>
            <div>
              <dt>Equipment ID</dt>
              <dd>
                {row.equipment_id ? (
                  <Link href={`/equipment/${encodeURIComponent(row.equipment_id)}`} className="asset-link">
                    <b>{row.equipment_id} ↗</b>
                  </Link>
                ) : (
                  "—"
                )}
              </dd>
            </div>
            <div>
              <dt>Location ID</dt>
              <dd className="mono">{row.location_id || "—"}</dd>
            </div>
            <div>
              <dt>Reported By</dt>
              <dd>{row.reported_by_name ? `${row.reported_by_name} (${row.reported_by})` : row.reported_by || "—"}</dd>
            </div>
            <div>
              <dt>Reported Date</dt>
              <dd className="mono">
                {row.reported_at ? new Date(row.reported_at).toLocaleString("id-ID") : "—"}
              </dd>
            </div>
            <div>
              <dt>Affected Date</dt>
              <dd className="mono">
                {row.affected_at ? new Date(row.affected_at).toLocaleString("id-ID") : "—"}
              </dd>
            </div>
            <div>
              <dt>Actual Window</dt>
              <dd className="mono" style={{ fontSize: "0.78rem" }}>
                {row.actual_start ? new Date(row.actual_start).toLocaleDateString("id-ID") : "—"} s/d{" "}
                {row.actual_finish ? new Date(row.actual_finish).toLocaleDateString("id-ID") : "—"}
              </dd>
            </div>
            <div>
              <dt>Target Window</dt>
              <dd className="mono" style={{ fontSize: "0.78rem" }}>
                {row.target_start ? new Date(row.target_start).toLocaleDateString("id-ID") : "—"} s/d{" "}
                {row.target_finish ? new Date(row.target_finish).toLocaleDateString("id-ID") : "—"}
              </dd>
            </div>
            <div>
              <dt>Priorities (Rep / Int)</dt>
              <dd>{row.reported_priority || "—"} / {row.internal_priority || "—"}</dd>
            </div>
            <div>
              <dt>Labor Effort (Hours / Cost)</dt>
              <dd>
                {row.actual_labor_hours != null ? `${row.actual_labor_hours} jam` : "—"} /{" "}
                {row.actual_labor_cost != null ? `Rp ${row.actual_labor_cost.toLocaleString("id-ID")}` : "—"}
              </dd>
            </div>
            <div>
              <dt>Risk Areas</dt>
              <dd style={{ fontSize: "0.8rem" }}>
                {row.risk_area_process ? `Process: ${row.risk_area_process} • ` : ""}
                {row.risk_area_human ? `Human: ${row.risk_area_human} • ` : ""}
                {row.risk_area_environment ? `Env: ${row.risk_area_environment}` : "None noted"}
              </dd>
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
            Field skalar tambahan dari pemetaan terverifikasi <code>MXAPISR</code>. Field ini tetap dikarantina di bawah <code>sources.maximo.extra</code>.
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
