"use client";

import { useEffect, useState, useCallback } from "react";
import { collectorApi, StatsView, CollectRunView, timeAgo } from "@/lib/api";

export function CollectStatusBar({ onRefresh }: { onRefresh: () => void }) {
  const [stats, setStats] = useState<StatsView | null>(null);
  const [lastRun, setLastRun] = useState<CollectRunView | null>(null);
  const [running, setRunning] = useState<"collect" | "aggregate" | null>(null);
  const [resultMsg, setResultMsg] = useState<{ text: string; type: "ok" | "err" } | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const [st, runs] = await Promise.all([collectorApi.stats(), collectorApi.runs(1)]);
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

  const handleTrigger = async (kind: "collect" | "aggregate", label: string) => {
    setResultMsg(null);
    setRunning(kind);
    try {
      const res =
        kind === "collect" ? await collectorApi.collectOnce() : await collectorApi.aggregate();
      const text =
        kind === "collect"
          ? `✓ ${label} selesai: ${res.rows_seen} parameter dibaca, ${res.upserted} baris disimpan` +
            (res.errors > 0 ? `, ${res.errors} gagal dibaca` : "") +
            (res.skipped > 0 ? `, ${res.skipped} gagal ditransformasi` : "") +
            "."
          : `✓ ${label} selesai: ${res.rows_seen} seri, ${res.upserted} baris 5-menit` +
            (res.skipped > 0 ? " (jendela sudah diproses — dilewati)" : "") +
            ".";
      setResultMsg({ text, type: res.errors > 0 ? "err" : "ok" });
    } catch (e) {
      setResultMsg({
        text: `Gagal ${label}: ${e instanceof Error ? e.message : String(e)}`,
        type: "err",
      });
    } finally {
      setRunning(null);
      await Promise.all([fetchStatus(), onRefresh()]);
    }
  };

  const isRunning = running !== null;

  return (
    <div style={{ marginBottom: 24 }}>
      <div className="ops-grid">
        <div className={`countdown-box ${isRunning ? "countdown-running" : "countdown-ok"}`}>
          <span className={`dot ${isRunning ? "dot-cyan dot-pulse" : "dot-green"}`} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 700, display: "flex", alignItems: "center", gap: 8 }}>
              {isRunning ? (
                <span style={{ color: "var(--cyan)" }}>
                  {running === "collect" ? "Siklus Koleksi Berjalan…" : "Agregasi Berjalan…"}
                </span>
              ) : (
                <>
                  <span style={{ color: "#fff" }}>Collector Standby · Siap</span>
                  <span className="count-pill">
                    {stats ? `${stats.resources.reading_realtime.toLocaleString()} readings` : "…"}
                  </span>
                </>
              )}
            </div>

            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: 4 }}>
              {lastRun ? (
                <span>
                  Run terakhir: <b>{lastRun.run_type}</b> ({timeAgo(lastRun.finished_at || lastRun.started_at)}) ·{" "}
                  {lastRun.upserted} baris
                </span>
              ) : (
                <span>Belum ada siklus koleksi tercatat. Jalankan `cemscollector collect` untuk polling kontinu.</span>
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

        <div className="ops-actions-box">
          <div style={{ minWidth: 0 }}>
            <span
              style={{
                display: "block",
                fontSize: "11px",
                fontWeight: 700,
                color: "var(--cyan)",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              COLLECT CONTROLS (READ-ONLY MODBUS)
            </span>
            <small style={{ color: "var(--text-muted)", fontSize: "11px" }}>
              Picu satu siklus koleksi / agregasi lokal. PLC hanya pernah dibaca (FC03/FC04).
            </small>
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              type="button"
              className="btn btn-primary"
              disabled={isRunning}
              onClick={() => handleTrigger("collect", "Koleksi sekali")}
              title="Baca semua parameter satu siklus"
            >
              {running === "collect" ? "Mengumpulkan…" : "⚡ Koleksi Sekali"}
            </button>

            <button
              type="button"
              className="btn btn-ghost"
              disabled={isRunning}
              onClick={() => handleTrigger("aggregate", "Agregasi 5-menit")}
              title="Agregasi jendela 5-menit terakhir"
            >
              {running === "aggregate" ? "Mengagregasi…" : "Agregasi 5-Menit"}
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
