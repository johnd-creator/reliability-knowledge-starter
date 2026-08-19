"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { collectorApi, type WorkOrderView, timeAgo } from "@/lib/api";

export default function WorkOrderDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const decodedId = decodeURIComponent(id);
  const [row, setRow] = useState<WorkOrderView | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setLoading(true);
    collectorApi
      .workOrders(10000)
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
    return <div className="empty page-empty">Memuat detail Work Order...</div>;
  }

  if (!row) {
    return (
      <div className="empty page-empty">
        <p>Work Order <strong>{decodedId}</strong> tidak ditemukan di local store.</p>
        <div style={{ marginTop: 16 }}>
          <Link href="/work-orders" className="btn btn-primary">
            ← Kembali ke Work Orders
          </Link>
        </div>
      </div>
    );
  }

  const extra = row.sources?.maximo?.extra || {};

  return (
    <>
      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 20 }}>
        <Link href="/work-orders" className="back-link" style={{ margin: 0 }}>
          ← Kembali ke Work Orders
        </Link>
        <span style={{ color: "var(--text-dim)" }}>/</span>
        <Link href="/" className="back-link" style={{ margin: 0 }}>
          Dashboard
        </Link>
        <span style={{ color: "var(--text-dim)" }}>/</span>
        <span className="count-pill">Work Order #{row.id}</span>
      </div>

      <section className="detail-hero">
        <div>
          <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap", alignItems: "center" }}>
            <p className="eyebrow" style={{ margin: 0 }}>
              WORK ORDER / MXWODETAIL
            </p>
            {row.work_type && <span className="count-pill">Type: {row.work_type}</span>}
            {row.work_class && <span className="count-pill">Class: {row.work_class}</span>}
            {row.priority && <span className="count-pill">Priority: {row.priority}</span>}
          </div>
          <h1>{row.id}</h1>
          <p className="lede">{row.description || "No description provided"}</p>
        </div>

        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={handleCopy}
            title="Salin WO ID ke clipboard"
          >
            {copied ? "✓ Copied!" : "📋 Copy WO #"}
          </button>
          <span className="status" style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
            {row.status || "UNKNOWN"}
          </span>
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <p className="eyebrow">VENDOR-NEUTRAL CONTRACT FIELDS</p>
          <h2>Work Order Profile</h2>
          <dl className="facts">
            <div>
              <dt>Work Order ID</dt>
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
              <dt>Work Type / Class</dt>
              <dd>{row.work_type ? `${row.work_type} (${row.work_class || "WO"})` : "—"}</dd>
            </div>
            <div>
              <dt>Reported By</dt>
              <dd>{row.reported_by || "—"}</dd>
            </div>
            <div>
              <dt>Supervisor / Lead</dt>
              <dd>{row.supervisor || row.lead || "—"}</dd>
            </div>
            <div>
              <dt>Reported Date</dt>
              <dd className="mono">
                {row.reported_at ? new Date(row.reported_at).toLocaleString("id-ID") : "—"}
              </dd>
            </div>
            <div>
              <dt>Scheduled Window</dt>
              <dd className="mono" style={{ fontSize: "0.78rem" }}>
                {row.scheduled_start ? new Date(row.scheduled_start).toLocaleDateString("id-ID") : "—"} s/d{" "}
                {row.scheduled_finish ? new Date(row.scheduled_finish).toLocaleDateString("id-ID") : "—"}
              </dd>
            </div>
            <div>
              <dt>Estimated Duration / Downtime</dt>
              <dd>
                {row.estimated_duration_hours != null ? `${row.estimated_duration_hours} jam` : "—"} /{" "}
                {row.downtime_hours != null ? `${row.downtime_hours} jam down` : "—"}
              </dd>
            </div>
            <div>
              <dt>Actual Labor Hours</dt>
              <dd>{row.actual_labor_hours != null ? `${row.actual_labor_hours} jam` : "—"}</dd>
            </div>
            <div>
              <dt>Labor Cost (Est / Act)</dt>
              <dd className="mono">
                {row.estimated_labor_cost?.toLocaleString("id-ID") ?? "—"} /{" "}
                {row.actual_labor_cost?.toLocaleString("id-ID") ?? "—"}
              </dd>
            </div>
            <div>
              <dt>Material Cost (Est / Act)</dt>
              <dd className="mono">
                {row.estimated_material_cost?.toLocaleString("id-ID") ?? "—"} /{" "}
                {row.actual_material_cost?.toLocaleString("id-ID") ?? "—"}
              </dd>
            </div>
            <div>
              <dt>Failure Code</dt>
              <dd className="mono">{row.failure_code || "—"}</dd>
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
            Field skalar tambahan dari pemetaan terverifikasi <code>MXWODETAIL</code>. Field ini tetap dikarantina di bawah <code>sources.maximo.extra</code>.
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
