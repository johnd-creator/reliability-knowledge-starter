"use client";

import { useCallback, useEffect, useState } from "react";
import { CollectStatusBar } from "./CollectStatusBar";
import { collectorApi, ReadingView, ParameterView, StatsView, timeAgo, fmt, compareParameterCodes } from "@/lib/api";

function statusColor(reading: ReadingView, parameter: ParameterView | undefined): string {
  if (reading.transformation_status !== "ok") return "var(--danger, #ea5455)";
  if (parameter?.threshold && reading.value_final !== null) {
    if (reading.value_final >= parameter.threshold) return "var(--danger, #ea5455)";
    if (reading.value_final >= parameter.threshold * 0.8) return "var(--warning, #ff9f43)";
  }
  return "var(--success, #28c76f)";
}

export default function DashboardPage() {
  const [latest, setLatest] = useState<ReadingView[]>([]);
  const [parameters, setParameters] = useState<ParameterView[]>([]);
  const [stats, setStats] = useState<StatsView | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [readings, params, st] = await Promise.all([
        collectorApi.latest(),
        collectorApi.parameters(),
        collectorApi.stats(),
      ]);
      setLatest(readings);
      setParameters(params);
      setStats(st);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 10000);
    return () => clearInterval(timer);
  }, [refresh]);

  const paramByCode = new Map(parameters.map((p) => [p.code, p]));
  const lastObserved = latest
    .map((r) => r.observed_at)
    .sort()
    .reverse()[0];

  return (
    <>
      <CollectStatusBar onRefresh={refresh} />

      {error && (
        <div className="collect-result err" style={{ marginBottom: 16 }}>
          Gagal memuat data: {error} — pastikan `cemscollector serve` berjalan di :8003.
        </div>
      )}

      <div className="stats-row" style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <div className="stat-card" style={{ flex: 1, minWidth: 160 }}>
          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Stack
          </div>
          <div style={{ fontSize: "1.15rem", fontWeight: 700 }}>{stats?.stack_id ?? "—"}</div>
        </div>
        <div className="stat-card" style={{ flex: 1, minWidth: 160 }}>
          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Parameter aktif
          </div>
          <div style={{ fontSize: "1.15rem", fontWeight: 700 }}>
            {stats ? `${stats.resources.parameters}` : "—"}
          </div>
        </div>
        <div className="stat-card" style={{ flex: 1, minWidth: 160 }}>
          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Baris realtime
          </div>
          <div style={{ fontSize: "1.15rem", fontWeight: 700 }}>
            {stats ? stats.resources.reading_realtime.toLocaleString() : "—"}
          </div>
        </div>
        <div className="stat-card" style={{ flex: 1, minWidth: 160 }}>
          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Pembacaan terakhir
          </div>
          <div style={{ fontSize: "1.15rem", fontWeight: 700 }}>{lastObserved ? timeAgo(lastObserved) : "—"}</div>
        </div>
      </div>

      <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Nilai Terkini per Parameter</h2>
      {latest.length === 0 && !error ? (
        <p style={{ color: "var(--text-muted)" }}>
          Belum ada pembacaan. Jalankan <code>cemscollector collect</code> atau tombol “Koleksi Sekali”.
        </p>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(5, minmax(0, 1fr))",
            gap: 12,
          }}
        >
          {latest
            .slice()
            .sort((a, b) => compareParameterCodes(a.parameter_code, b.parameter_code))
            .map((reading) => {
              const parameter = paramByCode.get(reading.parameter_code);
              const color = statusColor(reading, parameter);
              return (
                <div
                  key={`${reading.stack_id}-${reading.parameter_code}`}
                  className="stat-card"
                  style={{ borderLeft: `3px solid ${color}` }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "baseline",
                      gap: 8,
                    }}
                  >
                    <strong style={{ fontSize: "0.95rem" }}>{reading.parameter_code}</strong>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                      {parameter?.unit ?? ""}
                    </span>
                  </div>
                  <div style={{ fontSize: "1.7rem", fontWeight: 800, color, marginTop: 2 }}>
                    {fmt(reading.value_final, reading.parameter_code === "Hg" ? 5 : 3)}
                  </div>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginTop: 4 }}>
                    raw {fmt(reading.value_raw, 2)} · norm {fmt(reading.value_normalized, 3)}
                    {parameter?.threshold !== null && parameter?.threshold !== undefined
                      ? ` · batas ${parameter.threshold}`
                      : ""}
                  </div>
                  {reading.transformation_status !== "ok" && (
                    <div style={{ fontSize: "0.72rem", color: color, marginTop: 2 }}>
                      transformasi gagal
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      )}
    </>
  );
}
