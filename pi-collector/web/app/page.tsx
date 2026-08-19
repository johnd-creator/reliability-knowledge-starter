"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import Link from "next/link";
import { collectorApi, AttributeView, SnapshotView, StatsView, timeAgo } from "@/lib/api";
import { CollectBar } from "./CollectBar";
import { ActivityHeatmap } from "./ActivityHeatmap";
import { NextRunCountdown } from "./NextRunCountdown";

export default function HomePage() {
  const [attributes, setAttributes] = useState<AttributeView[]>([]);
  const [snapshots, setSnapshots] = useState<Map<string, SnapshotView>>(new Map());
  const [stats, setStats] = useState<StatsView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEquipmentTab, setSelectedEquipmentTab] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterParameter, setFilterParameter] = useState("");
  const [filterQuality, setFilterQuality] = useState("ALL");
  const [sortBy, setSortBy] = useState<"name" | "parameter" | "value" | "time">("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [tickNow, setTickNow] = useState(Date.now());

  const load = useCallback(async () => {
    try {
      const [attrs, snaps, st] = await Promise.all([
        collectorApi.listAttributes(),
        collectorApi.listSnapshots(500),
        collectorApi.getStats(),
      ]);
      setAttributes(attrs);
      setSnapshots(new Map(snaps.map((s) => [s.attribute_id, s])));
      setStats(st);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Keep relative times ("2 mnt lalu") fresh
  useEffect(() => {
    const t = setInterval(() => setTickNow(Date.now()), 30_000);
    return () => clearInterval(t);
  }, []);

  const equipmentOptions = useMemo(
    () => ([...new Set(attributes.map((a) => a.equipment).filter(Boolean))] as string[]).sort(),
    [attributes],
  );

  const parameterOptions = useMemo(
    () => ([...new Set(attributes.map((a) => a.parameter).filter(Boolean))] as string[]).sort(),
    [attributes],
  );

  const equipmentCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const a of attributes) {
      const eq = a.equipment || "(unknown)";
      counts[eq] = (counts[eq] || 0) + 1;
    }
    return counts;
  }, [attributes]);

  const filtered = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    return attributes.filter((a) => {
      const snap = snapshots.get(a.attribute_id);
      const matchTab = selectedEquipmentTab === "ALL" || a.equipment === selectedEquipmentTab;
      const matchParam = !filterParameter || a.parameter === filterParameter;
      const matchQuality =
        filterQuality === "ALL" ||
        (filterQuality === "GOOD" && snap?.value_good === true) ||
        (filterQuality === "BAD" && snap?.value_good === false) ||
        (filterQuality === "NULL" && (!snap || snap.value == null));
      const matchSearch =
        !q ||
        (a.business_name && a.business_name.toLowerCase().includes(q)) ||
        (a.attribute_id && a.attribute_id.toLowerCase().includes(q)) ||
        (a.position && a.position.toLowerCase().includes(q)) ||
        (a.parameter && a.parameter.toLowerCase().includes(q));
      return matchTab && matchParam && matchQuality && matchSearch;
    });
  }, [attributes, snapshots, selectedEquipmentTab, filterParameter, filterQuality, searchQuery]);

  // Group by equipment & sort within each group
  const grouped = useMemo(() => {
    const g: Record<string, AttributeView[]> = {};
    for (const a of filtered) {
      const key = a.equipment || "(unknown)";
      if (!g[key]) g[key] = [];
      g[key].push(a);
    }

    // Sort items within each group
    for (const key in g) {
      g[key].sort((a, b) => {
        const snapA = snapshots.get(a.attribute_id);
        const snapB = snapshots.get(b.attribute_id);
        let cmp = 0;
        if (sortBy === "name") {
          cmp = (a.business_name || "").localeCompare(b.business_name || "");
        } else if (sortBy === "parameter") {
          cmp = (a.parameter || "").localeCompare(b.parameter || "");
        } else if (sortBy === "value") {
          const valA = snapA?.value ?? -Infinity;
          const valB = snapB?.value ?? -Infinity;
          cmp = valA - valB;
        } else if (sortBy === "time") {
          const tA = snapA?.source_timestamp ? new Date(snapA.source_timestamp).getTime() : 0;
          const tB = snapB?.source_timestamp ? new Date(snapB.source_timestamp).getTime() : 0;
          cmp = tA - tB;
        }
        return sortOrder === "asc" ? cmp : -cmp;
      });
    }

    return g;
  }, [filtered, snapshots, sortBy, sortOrder]);

  const toggleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const goodCount = useMemo(() => {
    let count = 0;
    snapshots.forEach((s) => {
      if (s.value_good) count++;
    });
    return count;
  }, [snapshots]);

  const isFiltered =
    searchQuery !== "" ||
    filterParameter !== "" ||
    filterQuality !== "ALL" ||
    selectedEquipmentTab !== "ALL";

  if (loading) {
    return (
      <div style={{ padding: "64px 0", textAlign: "center" }}>
        <div className="dot dot-green dot-pulse" style={{ width: 16, height: 16, margin: "0 auto 16px" }} />
        <p className="muted">Memuat data collector & live telemetri BSR1...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="collect-result err" style={{ padding: 16, fontSize: "1rem" }}>
        <span>✗ Gagal memuat data:</span>
        <span className="mono">{error}</span>
      </div>
    );
  }

  return (
    <div>
      {/* Top Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1>PI Telemetry & Historian Explorer</h1>
          <p className="muted">
            Monitoring telemetri terverifikasi, continuous daemon status, & TimescaleDB hypertable coverage
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <span className="badge badge-good">
            <span className="dot dot-green" style={{ width: 6, height: 6 }} />
            {goodCount} Signal Good
          </span>
          <span className="badge badge-param">BSR1 Plant Scope</span>
        </div>
      </div>

      {/* Stats KPI Grid */}
      <div className="stats-grid">
        <div className="stat-box">
          <div className="label">
            <span>Attributes Terdaftar</span>
            <span>📑</span>
          </div>
          <div className="value">{stats?.registered_attributes ?? attributes.length}</div>
          <div className="subtext">150 tag terverifikasi BSR1</div>
        </div>

        <div className="stat-box" title="Jumlah nilai snapshot yang ditulis collector sejak tengah malam lokal — naik tiap siklus">
          <div className="label">
            <span>Snapshot Hari Ini</span>
            <span>🔄</span>
          </div>
          <div className="value mono">{stats?.snapshots_collected_today?.toLocaleString() ?? "0"}</div>
          <div className="subtext">+{stats?.registered_attributes ?? 0} per siklus collector</div>
        </div>

        <div className="stat-box" title="Baris arsip historian (pi_timeseries) — hanya bertambah saat backfill dijalankan; snapshot rutin tidak menambah arsip">
          <div className="label">
            <span>Total Points Archived</span>
            <span>📈</span>
          </div>
          <div className="value mono">{stats?.total_timeseries_points?.toLocaleString() ?? "0"}</div>
          <div className="subtext">via backfill saja • TimescaleDB</div>
        </div>

        <div className="stat-box">
          <div className="label">
            <span>Snapshot Terakhir</span>
            <span>⚡</span>
          </div>
          <div className="value mono" style={{ fontSize: "1.15rem" }}>
            {stats?.last_snapshot_cursor ? (
              <>
                <div>{new Date(stats.last_snapshot_cursor).toLocaleTimeString("id-ID")}</div>
                <div className="subtext" data-now={tickNow}>
                  {timeAgo(stats.last_snapshot_cursor)}
                </div>
              </>
            ) : (
              "—"
            )}
          </div>
        </div>

        <div className="stat-box">
          <div className="label">
            <span>Backfill Cursor</span>
            <span>🕒</span>
          </div>
          <div className="value mono" style={{ fontSize: "1.15rem" }}>
            {stats?.last_backfill_cursor ? (
              <>
                <div>{new Date(stats.last_backfill_cursor).toLocaleDateString("id-ID")}</div>
                <div className="subtext">{new Date(stats.last_backfill_cursor).toLocaleTimeString("id-ID")}</div>
              </>
            ) : (
              "—"
            )}
          </div>
        </div>
      </div>

      {/* Operations Grid: Countdown + Collect Actions */}
      <div className="ops-grid">
        <NextRunCountdown onRefresh={load} />
        <CollectBar onComplete={load} />
      </div>

      {/* Activity Heatmap Card */}
      <div className="card">
        <h2>
          <span>📅</span> Aktivitas & Kerapatan Data Collector
        </h2>
        <p className="muted" style={{ marginBottom: 16 }}>
          Matriks cakupan data harian — kotak hijau pekat menunjukkan 24 jam penuh data terkumpul secara kontinu atau melalui backfill.
        </p>
        <ActivityHeatmap />
      </div>

      {/* Equipment Tabs */}
      <div className="tabs-wrapper">
        <div className="tabs-header">
          <button
            type="button"
            className={`tab-btn ${selectedEquipmentTab === "ALL" ? "active" : ""}`}
            onClick={() => setSelectedEquipmentTab("ALL")}
          >
            Semua Equipment
            <span className="tab-badge">{attributes.length}</span>
          </button>
          {equipmentOptions.map((eq) => (
            <button
              key={eq}
              type="button"
              className={`tab-btn ${selectedEquipmentTab === eq ? "active" : ""}`}
              onClick={() => setSelectedEquipmentTab(eq)}
            >
              {eq}
              <span className="tab-badge">{equipmentCounts[eq] ?? 0}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="toolbar-card">
        <div className="filter-bar">
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="input-control"
              placeholder="Cari nama tag, posisi, parameter, atau ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <select
            className="select-control"
            value={filterParameter}
            onChange={(e) => setFilterParameter(e.target.value)}
          >
            <option value="">Semua Parameter ({parameterOptions.length})</option>
            {parameterOptions.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>

          <select
            className="select-control"
            value={filterQuality}
            onChange={(e) => setFilterQuality(e.target.value)}
          >
            <option value="ALL">Semua Sinyal Kualitas</option>
            <option value="GOOD">Good Signal Only (✓)</option>
            <option value="BAD">Bad Signal Only (✗)</option>
            <option value="NULL">No Data / Null</option>
          </select>

          {isFiltered && (
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => {
                setSelectedEquipmentTab("ALL");
                setSearchQuery("");
                setFilterParameter("");
                setFilterQuality("ALL");
              }}
            >
              ✕ Reset Filter
            </button>
          )}

          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 12 }}>
            <span className="sub-muted">
              Menampilkan <strong>{filtered.length}</strong> dari {attributes.length} atribut
            </span>
          </div>
        </div>
      </div>

      {/* Equipment Grouped Tables */}
      {filtered.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px 24px", color: "var(--fg-secondary)" }}>
          <div style={{ fontSize: "2rem", marginBottom: 12 }}>🔍</div>
          <div style={{ fontWeight: 600, fontSize: "1.1rem", marginBottom: 6 }}>Tidak ada atribut yang cocok</div>
          <div className="sub-muted">Coba ubah kata kunci pencarian atau reset filter di atas.</div>
        </div>
      ) : (
        Object.entries(grouped).sort().map(([equipment, attrs]) => (
          <div key={equipment} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h2>
                <span className="badge badge-equipment" style={{ fontSize: "0.85rem", padding: "4px 10px" }}>
                  {equipment}
                </span>
                <span className="sub-muted">({attrs.length} atribut telemetri)</span>
              </h2>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th style={{ cursor: "pointer" }} onClick={() => toggleSort("name")}>
                      Attribute & Business Name {sortBy === "name" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th style={{ cursor: "pointer" }} onClick={() => toggleSort("parameter")}>
                      Parameter {sortBy === "parameter" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th>Position</th>
                    <th>Unit</th>
                    <th style={{ cursor: "pointer" }} onClick={() => toggleSort("value")}>
                      Live Snapshot {sortBy === "value" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th style={{ cursor: "pointer" }} onClick={() => toggleSort("time")}>
                      Timestamp Data {sortBy === "time" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                    <th>Kualitas</th>
                    <th style={{ textAlign: "right" }}>Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {attrs.map((a) => {
                    const snap = snapshots.get(a.attribute_id);
                    return (
                      <tr key={a.attribute_id}>
                        <td>
                          <div>
                            <Link href={`/${encodeURIComponent(a.attribute_id)}`} className="attr-link">
                              {a.business_name || a.attribute_id}
                            </Link>
                            <div className="sub-muted mono" style={{ fontSize: "0.72rem", marginTop: 2 }}>
                              {a.attribute_id}
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className="badge badge-param">{a.parameter}</span>
                        </td>
                        <td className="muted">{a.position || "—"}</td>
                        <td className="muted mono">{a.unit_of_measure || "—"}</td>
                        <td>
                          <span className="mono" style={{ fontWeight: 700, fontSize: "0.95rem", color: "#fff" }}>
                            {snap?.value != null ? snap.value.toFixed(2) : "—"}
                          </span>
                        </td>
                        <td
                          title={[
                            snap?.source_timestamp
                              ? `Source PI Time: ${new Date(snap.source_timestamp).toLocaleString("id-ID")}`
                              : null,
                            snap?.collected_at
                              ? `Collected Time: ${new Date(snap.collected_at).toLocaleString("id-ID")}`
                              : null,
                          ]
                            .filter(Boolean)
                            .join("\n") || undefined}
                        >
                          {snap?.source_timestamp ? (
                            <div>
                              <div style={{ fontSize: "0.825rem" }} className="mono">
                                {timeAgo(snap.source_timestamp)}
                              </div>
                              <div className="sub-muted" style={{ fontSize: "0.72rem" }}>
                                {new Date(snap.source_timestamp).toLocaleTimeString("id-ID")}
                              </div>
                            </div>
                          ) : (
                            <span className="sub-muted">—</span>
                          )}
                        </td>
                        <td>
                          {snap ? (
                            <span className={`badge ${snap.value_good ? "badge-good" : "badge-bad"}`}>
                              <span
                                className={`dot ${snap.value_good ? "dot-green" : "dot-red"}`}
                                style={{ width: 6, height: 6 }}
                              />
                              {snap.value_good ? "Good" : "Bad"}
                            </span>
                          ) : (
                            <span className="badge badge-null">—</span>
                          )}
                        </td>
                        <td style={{ textAlign: "right" }}>
                          <Link
                            href={`/${encodeURIComponent(a.attribute_id)}`}
                            className="btn btn-ghost"
                            style={{ padding: "4px 8px", fontSize: "0.75rem" }}
                          >
                            Detail ↗
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
