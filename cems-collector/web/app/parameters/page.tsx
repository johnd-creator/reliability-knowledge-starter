"use client";

import { useCallback, useEffect, useState } from "react";
import { collectorApi, ParameterView, StackView, fmt, compareParameterCodes } from "@/lib/api";

export default function ParametersPage() {
  const [parameters, setParameters] = useState<ParameterView[]>([]);
  const [stacks, setStacks] = useState<StackView[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [params, stackRows] = await Promise.all([collectorApi.parameters(), collectorApi.stacks()]);
      setParameters(params);
      setStacks(stackRows);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <>
      <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Registry Parameter</h2>

      {error && (
        <div className="collect-result err" style={{ marginBottom: 16 }}>
          Gagal memuat: {error}
        </div>
      )}

      {stacks.map((stack) => (
        <p key={stack.stack_id} style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          <b>{stack.code}</b> — {stack.name} (stack {stack.stack_id}, status {stack.status})
        </p>
      ))}

      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
        <thead>
          <tr style={{ color: "var(--text-muted)", textAlign: "left" }}>
            <th style={{ padding: "6px 8px" }}>Kode</th>
            <th style={{ padding: "6px 8px" }}>Nama</th>
            <th style={{ padding: "6px 8px" }}>Satuan</th>
            <th style={{ padding: "6px 8px" }}>Batas</th>
            <th style={{ padding: "6px 8px" }}>Register</th>
            <th style={{ padding: "6px 8px" }}>Tipe</th>
            <th style={{ padding: "6px 8px" }}>Status</th>
            <th style={{ padding: "6px 8px" }}>Koleksi</th>
          </tr>
        </thead>
        <tbody>
          {parameters
            .slice()
            .sort((a, b) => compareParameterCodes(a.code, b.code))
            .map((p) => {
            const modbus = p.sources?.cems?.modbus as
              | { register?: number; register_type?: string; data_type?: string }
              | undefined;
            return (
              <tr key={`${p.stack_id}-${p.code}`} style={{ borderTop: "1px solid var(--border, #2a3040)" }}>
                <td style={{ padding: "6px 8px", fontWeight: 700 }}>{p.code}</td>
                <td style={{ padding: "6px 8px" }}>{p.name}</td>
                <td style={{ padding: "6px 8px" }}>{p.unit}</td>
                <td style={{ padding: "6px 8px" }}>{p.threshold !== null ? fmt(p.threshold, 2) : "—"}</td>
                <td style={{ padding: "6px 8px" }}>{modbus?.register ?? "—"}</td>
                <td style={{ padding: "6px 8px" }}>
                  {modbus?.register_type ?? "—"} / {modbus?.data_type ?? "—"}
                </td>
                <td style={{ padding: "6px 8px" }}>{p.status}</td>
                <td style={{ padding: "6px 8px" }}>{p.collect_enabled ? "aktif" : "nonaktif"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}
