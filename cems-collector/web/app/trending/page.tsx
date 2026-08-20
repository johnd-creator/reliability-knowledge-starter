"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { collectorApi, Reading5MinView, ParameterView, fmt, compareParameterCodes } from "@/lib/api";

function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2) return <span style={{ color: "var(--text-muted)" }}>—</span>;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const points = values
    .map((v, i) => {
      const x = (i / (values.length - 1)) * 100;
      const y = 28 - ((v - min) / span) * 24;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg viewBox="0 0 100 30" preserveAspectRatio="none" style={{ width: 120, height: 30 }}>
      <polyline points={points} fill="none" stroke="var(--cyan, #00cfe8)" strokeWidth="1.5" />
    </svg>
  );
}

export default function TrendingPage() {
  const [rows, setRows] = useState<Reading5MinView[]>([]);
  const [parameters, setParameters] = useState<ParameterView[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [aggregates, params] = await Promise.all([
        collectorApi.readings5min({ limit: 1000 }),
        collectorApi.parameters(),
      ]);
      setRows(aggregates);
      setParameters(params);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const codes = useMemo(
    () => Array.from(new Set(rows.map((r) => r.parameter_code))).sort(compareParameterCodes),
    [rows]
  );

  const filtered = selected ? rows.filter((r) => r.parameter_code === selected) : rows;
  const unitByCode = new Map(parameters.map((p) => [p.code, p.unit]));
  const seriesByCode = useMemo(() => {
    const map = new Map<string, Reading5MinView[]>();
    for (const row of filtered) {
      const list = map.get(row.parameter_code) ?? [];
      list.push(row);
      map.set(row.parameter_code, list);
    }
    for (const list of map.values()) {
      list.sort((a, b) => a.window_start.localeCompare(b.window_start));
    }
    return map;
  }, [filtered]);

  return (
    <>
      <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Tren 5-Menit</h2>

      {error && (
        <div className="collect-result err" style={{ marginBottom: 16 }}>
          Gagal memuat: {error}
        </div>
      )}

      <div style={{ marginBottom: 16, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <label style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Parameter:</label>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          style={{ padding: "6px 10px", borderRadius: 8, background: "var(--card, #1e2330)", color: "inherit", border: "1px solid var(--border, #333a48)" }}
        >
          <option value="">Semua ({codes.length})</option>
          {codes.map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </select>
        <button type="button" className="btn btn-ghost" style={{ padding: "6px 12px" }} onClick={refresh}>
          🔄 Muat ulang
        </button>
      </div>

      {rows.length === 0 && !error ? (
        <p style={{ color: "var(--text-muted)" }}>
          Belum ada agregat. Jalankan <code>cemscollector aggregate</code> (atau tombol di dashboard).
        </p>
      ) : (
        Array.from(seriesByCode.entries())
          .sort(([a], [b]) => compareParameterCodes(a, b))
          .map(([code, series]) => (
          <div key={code} style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <h3 style={{ fontSize: "0.95rem" }}>
                {code} <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>({unitByCode.get(code) ?? "?"})</span>
              </h3>
              <Sparkline values={series.map((s) => s.avg_value)} />
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ color: "var(--text-muted)", textAlign: "left" }}>
                  <th style={{ padding: "6px 8px" }}>Jendela</th>
                  <th style={{ padding: "6px 8px" }}>Avg</th>
                  <th style={{ padding: "6px 8px" }}>Min</th>
                  <th style={{ padding: "6px 8px" }}>Max</th>
                  <th style={{ padding: "6px 8px" }}>Sampel</th>
                </tr>
              </thead>
              <tbody>
                {series
                  .slice()
                  .reverse()
                  .map((row) => (
                    <tr key={`${row.parameter_code}-${row.window_start}`} style={{ borderTop: "1px solid var(--border, #2a3040)" }}>
                      <td style={{ padding: "6px 8px" }}>{row.window_start.replace("T", " ").slice(0, 16)}</td>
                      <td style={{ padding: "6px 8px" }}>{fmt(row.avg_value, 3)}</td>
                      <td style={{ padding: "6px 8px" }}>{fmt(row.min_value, 3)}</td>
                      <td style={{ padding: "6px 8px" }}>{fmt(row.max_value, 3)}</td>
                      <td style={{ padding: "6px 8px" }}>{row.sample_count}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        ))
      )}
    </>
  );
}
