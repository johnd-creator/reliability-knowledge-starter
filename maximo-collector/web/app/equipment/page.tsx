"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { collectorApi, EquipmentView, timeAgo } from "@/lib/api";

export default function EquipmentPage() {
  const [equipmentList, setEquipmentList] = useState<EquipmentView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [unitFilter, setUnitFilter] = useState("ALL");
  const [classFilter, setClassFilter] = useState("ALL");
  const [runningFilter, setRunningFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [quickFilter, setQuickFilter] = useState<string>("ALL");

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortBy, setSortBy] = useState<keyof EquipmentView>("id");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await collectorApi.equipment(10000);
      setEquipmentList(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    setCurrentPage(1);
  }, [search, statusFilter, unitFilter, classFilter, runningFilter, priorityFilter, quickFilter, pageSize]);

  // Options derived from live data
  const statusOptions = useMemo(() => {
    return Array.from(new Set(equipmentList.map((e) => e.status).filter(Boolean) as string[])).sort();
  }, [equipmentList]);

  const unitOptions = useMemo(() => {
    return Array.from(new Set(equipmentList.map((e) => e.unit).filter(Boolean) as string[])).sort();
  }, [equipmentList]);

  const classOptions = useMemo(() => {
    return Array.from(new Set(equipmentList.map((e) => e.equipment_class).filter(Boolean) as string[])).sort();
  }, [equipmentList]);

  const priorityOptions = useMemo(() => {
    const list = equipmentList.map((e) => e.priority).filter((p) => p != null) as number[];
    return Array.from(new Set(list)).sort((a, b) => a - b);
  }, [equipmentList]);

  // Filtered & Sorted
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = equipmentList.filter((e) => {
      const matchStatus = statusFilter === "ALL" || e.status === statusFilter;
      const matchUnit = unitFilter === "ALL" || e.unit === unitFilter;
      const matchClass = classFilter === "ALL" || e.equipment_class === classFilter;
      const matchRunning =
        runningFilter === "ALL" ||
        (runningFilter === "RUNNING" && (e.is_running === true || e.status?.toLowerCase() === "operating")) ||
        (runningFilter === "STOPPED" && (e.is_running === false || e.status?.toLowerCase() !== "operating"));
      const matchPriority = priorityFilter === "ALL" || (e.priority != null && String(e.priority) === priorityFilter);

      let matchQuick = true;
      if (quickFilter === "RUNNING") {
        matchQuick = e.is_running === true || e.status?.toLowerCase() === "operating";
      } else if (quickFilter === "HIGH_PRIORITY") {
        matchQuick = e.priority != null && e.priority <= 2;
      } else if (quickFilter === "WITH_VENDOR") {
        matchQuick = Boolean(e.manufacturer || e.vendor);
      } else if (quickFilter === "HAS_LOCATION") {
        matchQuick = Boolean(e.location_id);
      }

      const matchSearch =
        !q ||
        [e.id, e.name, e.location_id, e.unit, e.equipment_class, e.status, e.manufacturer, e.vendor].some((v) =>
          v?.toLowerCase().includes(q)
        );

      return matchStatus && matchUnit && matchClass && matchRunning && matchPriority && matchQuick && matchSearch;
    });

    list.sort((a, b) => {
      const valA = a[sortBy] ?? "";
      const valB = b[sortBy] ?? "";
      if (typeof valA === "string") {
        const cmp = (valA as string).localeCompare(String(valB));
        return sortOrder === "asc" ? cmp : -cmp;
      }
      const cmp = valA > valB ? 1 : -1;
      return sortOrder === "asc" ? cmp : -cmp;
    });

    return list;
  }, [
    equipmentList,
    search,
    statusFilter,
    unitFilter,
    classFilter,
    runningFilter,
    priorityFilter,
    quickFilter,
    sortBy,
    sortOrder,
  ]);

  // Pagination Math
  const totalRows = filtered.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  const pageSafe = Math.min(Math.max(1, currentPage), totalPages);
  const startIdx = (pageSafe - 1) * pageSize;
  const paginated = filtered.slice(startIdx, startIdx + pageSize);

  const toggleSort = (field: keyof EquipmentView) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const isFiltered =
    Boolean(search) ||
    statusFilter !== "ALL" ||
    unitFilter !== "ALL" ||
    classFilter !== "ALL" ||
    runningFilter !== "ALL" ||
    priorityFilter !== "ALL" ||
    quickFilter !== "ALL";

  const handleResetFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
    setUnitFilter("ALL");
    setClassFilter("ALL");
    setRunningFilter("ALL");
    setPriorityFilter("ALL");
    setQuickFilter("ALL");
  };

  return (
    <div>
      {/* Header Breadcrumb */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <Link href="/" className="back-link" style={{ margin: 0 }}>
          ← Kembali ke Dashboard
        </Link>
        <span className="count-pill">Total: {equipmentList.length.toLocaleString()} Equipment Terdaftar</span>
      </div>

      <section className="hero" style={{ marginBottom: 24 }}>
        <div>
          <p className="eyebrow">EQUIPMENT MASTER / MXAPIASSET</p>
          <h1>Equipment Explorer</h1>
          <p className="lede">
            Daftar lengkap aset dan peralatan pabrik BSR yang disinkronkan dari Maximo ke dalam penyimpanan lokal Postgres dengan filter multi-dimensi.
          </p>
        </div>
      </section>

      {error && (
        <div className="alert">
          <div>
            <strong>Gagal memuat: </strong> {error}
          </div>
          <button onClick={load}>Coba Lagi</button>
        </div>
      )}

      {/* Main Panel */}
      <div className="panel">
        {/* Quick Filter Chips */}
        <div className="quick-chips-wrapper">
          <span style={{ fontSize: "11px", color: "var(--text-dim)", fontWeight: 700, textTransform: "uppercase", marginRight: 4 }}>
            Quick Filter:
          </span>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "ALL" ? "active" : ""}`}
            onClick={() => setQuickFilter("ALL")}
          >
            Semua
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "RUNNING" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "RUNNING" ? "ALL" : "RUNNING")}
          >
            ⚡ Running / Operating
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "HIGH_PRIORITY" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "HIGH_PRIORITY" ? "ALL" : "HIGH_PRIORITY")}
          >
            ★ Prioritas Tinggi (P1/P2)
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "WITH_VENDOR" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "WITH_VENDOR" ? "ALL" : "WITH_VENDOR")}
          >
            🏷️ Ada Pabrikan / Vendor
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "HAS_LOCATION" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "HAS_LOCATION" ? "ALL" : "HAS_LOCATION")}
          >
            📍 Terdata Lokasi
          </button>
        </div>

        {/* Multi-Filter Bar */}
        <div className="table-tools-bar">
          <div className="table-filters">
            <input
              className="search-input"
              style={{ width: 260 }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Cari ID, deskripsi, lokasi, vendor..."
            />

            <select
              className="select-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">Semua Status ({statusOptions.length})</option>
              {statusOptions.map((s) => (
                <option key={s} value={s}>
                  Status: {s}
                </option>
              ))}
            </select>

            <select
              className="select-filter"
              value={unitFilter}
              onChange={(e) => setUnitFilter(e.target.value)}
            >
              <option value="ALL">Semua Unit ({unitOptions.length})</option>
              {unitOptions.map((u) => (
                <option key={u} value={u}>
                  Unit: {u}
                </option>
              ))}
            </select>

            {classOptions.length > 0 && (
              <select
                className="select-filter"
                value={classFilter}
                onChange={(e) => setClassFilter(e.target.value)}
              >
                <option value="ALL">Semua Class ({classOptions.length})</option>
                {classOptions.map((c) => (
                  <option key={c} value={c}>
                    Class: {c}
                  </option>
                ))}
              </select>
            )}

            <select
              className="select-filter"
              value={runningFilter}
              onChange={(e) => setRunningFilter(e.target.value)}
            >
              <option value="ALL">Semua Operating State</option>
              <option value="RUNNING">Operating / Running (✓)</option>
              <option value="STOPPED">Stopped / Other (—)</option>
            </select>

            {priorityOptions.length > 0 && (
              <select
                className="select-filter"
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
              >
                <option value="ALL">Semua Prioritas</option>
                {priorityOptions.map((p) => (
                  <option key={p} value={String(p)}>
                    Prioritas {p}
                  </option>
                ))}
              </select>
            )}

            {isFiltered && (
              <button
                type="button"
                className="btn btn-ghost"
                onClick={handleResetFilters}
              >
                ✕ Reset Filter
              </button>
            )}
          </div>

          <div className="page-size-selector">
            <span>Per halaman:</span>
            <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="empty">Memuat data equipment...</div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th className="sortable" onClick={() => toggleSort("id")}>
                    Asset ID {sortBy === "id" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("name")}>
                    Nama & Deskripsi {sortBy === "name" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("unit")}>
                    Unit / Class {sortBy === "unit" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("location_id")}>
                    Location {sortBy === "location_id" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("status")}>
                    Status {sortBy === "status" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("priority")}>
                    Pri {sortBy === "priority" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th>Manufacturer / Vendor</th>
                  <th className="sortable" onClick={() => toggleSort("source_changed_at")}>
                    Changed Date {sortBy === "source_changed_at" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th style={{ textAlign: "right" }}>Aksi</th>
                </tr>
              </thead>
              <tbody>
                {paginated.map((row) => (
                  <tr key={row.id}>
                    <td>
                      <Link href={`/equipment/${encodeURIComponent(row.id)}`} className="asset-link">
                        <b>{row.id}</b>
                      </Link>
                    </td>
                    <td>
                      <div style={{ maxWidth: 300, fontWeight: 600 }}>{row.name || "No description"}</div>
                    </td>
                    <td>
                      <span>{row.unit || "—"}</span>
                      {row.equipment_class && (
                        <small style={{ display: "block", color: "var(--text-muted)", fontSize: "11px" }}>
                          {row.equipment_class}
                        </small>
                      )}
                    </td>
                    <td className="mono">{row.location_id || "—"}</td>
                    <td>
                      <span className={`status ${row.status?.toLowerCase() === "operating" ? "good" : ""}`}>
                        {row.status || "—"}
                      </span>
                    </td>
                    <td>
                      {row.priority != null ? (
                        <span className="count-pill">P{row.priority}</span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>{row.manufacturer || row.vendor || "—"}</td>
                    <td className="mono" style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                      {timeAgo(row.source_changed_at)}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <Link
                        href={`/equipment/${encodeURIComponent(row.id)}`}
                        className="btn btn-ghost"
                        style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                      >
                        Detail ↗
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {paginated.length === 0 && (
              <div className="empty">Tidak ada data equipment yang sesuai dengan kriteria filter.</div>
            )}
          </div>
        )}

        {/* Pagination Controls */}
        <div className="pagination-bar">
          <div className="pagination-info">
            Menampilkan <strong>{totalRows === 0 ? 0 : startIdx + 1}</strong> –{" "}
            <strong>{Math.min(startIdx + pageSize, totalRows)}</strong> dari{" "}
            <strong>{totalRows.toLocaleString()}</strong> equipment
          </div>

          <div className="pagination-controls">
            <button
              type="button"
              className="page-btn"
              disabled={pageSafe <= 1}
              onClick={() => setCurrentPage(1)}
              title="Awal"
            >
              «
            </button>
            <button
              type="button"
              className="page-btn"
              disabled={pageSafe <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              title="Sebelumnya"
            >
              ‹
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(
                (p) =>
                  p === 1 ||
                  p === totalPages ||
                  (p >= pageSafe - 2 && p <= pageSafe + 2)
              )
              .map((p, idx, arr) => {
                const prev = arr[idx - 1];
                return (
                  <span key={p} style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                    {prev && p - prev > 1 && <span style={{ color: "var(--text-dim)", padding: "0 4px" }}>…</span>}
                    <button
                      type="button"
                      className={`page-btn ${pageSafe === p ? "active" : ""}`}
                      onClick={() => setCurrentPage(p)}
                    >
                      {p}
                    </button>
                  </span>
                );
              })}

            <button
              type="button"
              className="page-btn"
              disabled={pageSafe >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              title="Berikutnya"
            >
              ›
            </button>
            <button
              type="button"
              className="page-btn"
              disabled={pageSafe >= totalPages}
              onClick={() => setCurrentPage(totalPages)}
              title="Akhir"
            >
              »
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
