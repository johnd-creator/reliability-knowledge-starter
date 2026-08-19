"use client";

import { useState } from "react";
import { collectorApi, CollectResponse } from "@/lib/api";

export function CollectBar({ onComplete }: { onComplete?: () => void }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [result, setResult] = useState<CollectResponse | null>(null);
  const [backfillStart, setBackfillStart] = useState("*-7d");
  const [backfillInterval, setBackfillInterval] = useState("1h");

  async function doSnapshots() {
    setBusy("snapshot");
    setResult(null);
    try {
      const res = await collectorApi.collectSnapshots();
      setResult(res);
      if (onComplete) onComplete();
    } catch (e) {
      setResult({ status: "error", message: String(e), stats: null });
    } finally {
      setBusy(null);
    }
  }

  async function doBackfill() {
    setBusy("backfill");
    setResult(null);
    try {
      const res = await collectorApi.collectBackfill(backfillStart, "*", backfillInterval);
      setResult(res);
      if (onComplete) onComplete();
    } catch (e) {
      setResult({ status: "error", message: String(e), stats: null });
    } finally {
      setBusy(null);
    }
  }

  const presets = [
    { label: "24 Jam", start: "*-1d", interval: "15m" },
    { label: "7 Hari", start: "*-7d", interval: "1h" },
    { label: "30 Hari", start: "*-30d", interval: "2h" },
  ];

  return (
    <div className="card" style={{ marginBottom: 0 }}>
      <h2>⚡ Manual Data Collection & Backfill</h2>
      <p className="sub-muted" style={{ marginBottom: 14 }}>
        Ambil snapshot live seketika atau jalankan backfill interpolasi historis.
      </p>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        <button
          className="btn btn-emerald"
          onClick={doSnapshots}
          disabled={busy !== null}
        >
          {busy === "snapshot" ? "⏳ Mengambil Snapshot..." : "📸 Ambil Live Snapshots"}
        </button>

        <div style={{ height: 24, width: 1, background: "var(--border)" }} />

        <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
          <span className="muted" style={{ fontSize: "0.8rem", fontWeight: 600 }}>Backfill Start:</span>
          <input
            className="input-control mono"
            style={{ width: 100, paddingLeft: 10 }}
            value={backfillStart}
            onChange={(e) => setBackfillStart(e.target.value)}
            placeholder="*-7d"
          />
          <span className="muted" style={{ fontSize: "0.8rem", fontWeight: 600 }}>Intv:</span>
          <input
            className="input-control mono"
            style={{ width: 70, paddingLeft: 10 }}
            value={backfillInterval}
            onChange={(e) => setBackfillInterval(e.target.value)}
            placeholder="1h"
          />

          <button
            className="btn btn-primary"
            onClick={doBackfill}
            disabled={busy !== null}
          >
            {busy === "backfill" ? "⏳ Running Backfill..." : "🚀 Run Backfill"}
          </button>
        </div>

        <div style={{ display: "flex", gap: 4, alignItems: "center", marginLeft: "auto" }}>
          <span className="sub-muted">Presets:</span>
          {presets.map((p) => (
            <button
              key={p.label}
              type="button"
              className="btn btn-ghost"
              style={{ padding: "3px 8px", fontSize: "0.75rem" }}
              onClick={() => {
                setBackfillStart(p.start);
                setBackfillInterval(p.interval);
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {result && (
        <div className={`collect-result ${result.status === "ok" ? "ok" : "err"}`}>
          <span>{result.status === "ok" ? "✓" : "✗"}</span>
          <span>{result.message}</span>
        </div>
      )}
    </div>
  );
}
