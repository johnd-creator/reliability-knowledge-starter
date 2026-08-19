"use client";

import { useEffect, useState, useCallback } from "react";
import { collectorApi, StatsView, CollectRunView, timeAgo } from "@/lib/api";

const DEFAULT_SYNC_OBJECTS = ["mxwodetail", "mxapisr", "mxperson", "mxitem", "mxapilabor"];
const ALL_SYNC_OBJECTS = ["mxapiasset", "mxwodetail", "mxapisr", "mxperson", "mxitem", "mxapilabor"];

export function CollectStatusBar({ onRefresh }: { onRefresh: () => void }) {
  const [stats, setStats] = useState<StatsView | null>(null);
  const [lastRun, setLastRun] = useState<CollectRunView | null>(null);
  const [syncingObject, setSyncingObject] = useState<string | null>(null);
  const [syncProgress, setSyncProgress] = useState<{ current: number; total: number; object: string } | null>(null);
  const [resultMsg, setResultMsg] = useState<{ text: string; type: "ok" | "err" } | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const [st, runs] = await Promise.all([
        collectorApi.stats(),
        collectorApi.runs(1),
      ]);
      setStats(st);
      if (runs.length > 0) {
        setLastRun(runs[0]);
      }
    } catch {
      // ignore transient network error
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const timer = setInterval(() => {
      fetchStatus();
    }, 15000);
    return () => clearInterval(timer);
  }, [fetchStatus]);

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([fetchStatus(), onRefresh()]);
    } finally {
      setTimeout(() => setIsRefreshing(false), 400);
    }
  };

  const handleSyncBatch = async (objects: string[], label: string) => {
    setResultMsg(null);
    let totalUpserted = 0;
    let totalSeen = 0;
    let hasError = false;

    for (let i = 0; i < objects.length; i++) {
      const obj = objects[i];
      setSyncingObject(obj);
      setSyncProgress({ current: i + 1, total: objects.length, object: obj });
      try {
        const res = await collectorApi.sync(obj);
        totalUpserted += res.upserted;
        totalSeen += res.rows_seen;
        if (res.errors > 0) {
          hasError = true;
          setResultMsg({
            text: `Sync ${obj} selesai dengan ${res.errors} error dan ${res.skipped} row dilewati.`,
            type: "err",
          });
        }
      } catch (e) {
        hasError = true;
        setResultMsg({
          text: `Gagal sync ${obj}: ${e instanceof Error ? e.message : String(e)}`,
          type: "err",
        });
        break;
      }
    }

    setSyncingObject(null);
    setSyncProgress(null);
    await Promise.all([fetchStatus(), onRefresh()]);

    if (!hasError) {
      setResultMsg({
        text: `✓ ${label} selesai: +${totalUpserted.toLocaleString()} baris ter-update (${totalSeen.toLocaleString()} diperiksa).`,
        type: "ok",
      });
      setTimeout(() => setResultMsg(null), 8000);
    }
  };

  const isRunning = syncingObject !== null;

  return (
    <div style={{ marginBottom: 24 }}>
      <div className="ops-grid">
        {/* Collector State Box */}
        <div className={`countdown-box ${isRunning ? "countdown-running" : "countdown-ok"}`}>
          <span className={`dot ${isRunning ? "dot-cyan dot-pulse" : "dot-green"}`} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 700, display: "flex", alignItems: "center", gap: 8 }}>
              {isRunning ? (
                <>
                  <span style={{ color: "var(--cyan)" }}>Collector Sedang Berjalan</span>
                  {syncProgress && (
                    <span className="count-pill" style={{ color: "var(--cyan)", borderColor: "var(--cyan)" }}>
                      {syncProgress.current}/{syncProgress.total} · {syncProgress.object}
                    </span>
                  )}
                </>
              ) : (
                <>
                  <span style={{ color: "#fff" }}>Collector Standby · Siap</span>
                  <span className="count-pill">BSR Store</span>
                </>
              )}
            </div>

            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: 4 }}>
              {isRunning ? (
                <span>Menarik data delta OSLC Maximo secara read-only (GET)...</span>
              ) : lastRun ? (
                <span>
                  Sinkronisasi terakhir: <b>{lastRun.object_structure}</b> ({timeAgo(lastRun.finished_at || lastRun.started_at)}) · +{lastRun.upserted} records
                </span>
              ) : (
                <span>Belum ada siklus sinkronisasi tercatat.</span>
              )}
            </div>
          </div>

          <button
            type="button"
            onClick={handleManualRefresh}
            className="btn btn-ghost"
            style={{ padding: "6px 12px", fontSize: "0.8rem", flexShrink: 0 }}
            title="Refresh Data & Status"
          >
            {isRefreshing ? "⏳" : "🔄 Refresh"}
          </button>
        </div>

        {/* Action Controls Box */}
        <div className="ops-actions-box">
          <div style={{ minWidth: 0 }}>
            <span style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "var(--cyan)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
              SYNC CONTROLS (READ-ONLY GET)
            </span>
            <small style={{ color: "var(--text-muted)", fontSize: "11px" }}>
              Picu sinkronisasi manual ke Maximo BSR tanpa merubah data di server Maximo.
            </small>
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              type="button"
              className="btn btn-primary"
              disabled={isRunning}
              onClick={() => handleSyncBatch(DEFAULT_SYNC_OBJECTS, "Sync Operasional")}
              title="Sync WO, SR, Person, Item, Labor"
            >
              {isRunning && !syncingObject?.includes("asset") ? "Sedang Sync..." : "⚡ Sync Operasional"}
            </button>

            <button
              type="button"
              className="btn btn-ghost"
              disabled={isRunning}
              onClick={() => handleSyncBatch(ALL_SYNC_OBJECTS, "Sync Lengkap Termasuk Asset")}
              title="Sync semua termasuk Equipment (MXAPIASSET)"
            >
              Sync Semua (Termasuk Asset)
            </button>
          </div>
        </div>
      </div>

      {resultMsg && (
        <div className={`collect-result ${resultMsg.type}`} style={{ marginTop: 8 }}>
          <span>{resultMsg.text}</span>
          <button
            type="button"
            onClick={() => setResultMsg(null)}
            className="btn btn-ghost"
            style={{ marginLeft: "auto", padding: "2px 8px", fontSize: "0.75rem" }}
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
