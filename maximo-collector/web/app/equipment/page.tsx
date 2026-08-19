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
  }, [search, statusFilter, unitFilter, pageSize]);

  // Options
  const statusOptions = useMemo(() => {
    return Array.from(new Set(equipmentList.map((e) => e.status).filter(Boolean) as string[])).sort();
  }, [equipmentList]);

  const unitOptions = useMemo(() => {
    return Array.from(new Set(equipmentList.map((e) => e.unit).filter(Boolean) as string[])).sort();
  }, [equipmentList]);

  // Filtered & Sorted
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = equipmentList.filter((e) => {
      const matchStatus = statusFilter === "ALL" || e.status === statusFilter;
      const matchUnit = unitFilter === "ALL" || e.unit === unitFilter;
      const matchSearch =
        !q ||
        [e.id, e.name, e.location_id, e.unit, e.equipment_class, e.status, e.manufacturer, e.vendor].some((v) =>
          v?.toLowerCase().includes(q)
        );
      return matchStatus && matchUnit && matchSearch;
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
  }, [equipmentList, search, statusFilter, unitFilter, sortBy, sortOrder]);

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
          <h1>Equipment Explorer & Paginasi</h1>
          <p className="lede">
            Daftar lengkap asset dan peralatan BSR yang disinkronkan dari Maximo ke dalam penyimpanan lokal Postgres.
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
        <div className="table-tools-bar">
          <div className="table-filters">
            <input
              className="search-input"
              style={{ width: 280 }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Cari asset ID, deskripsi, lokasi, unit..."
            />

            <select
              className="select-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">Semua Status ({statusOptions.length})</option>
              {statusOptions.map((s) => (
                <option key={s} value={s}>
                  {s}
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
                  {u}
                </option>
              ))}
            </select>

            {(search || statusFilter !== "ALL" || unitFilter !== "ALL") && (
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => {
                  setSearch("");
                  setStatusFilter("ALL");
                  setUnitFilter("ALL");
                }}
              >
                ✕ Reset Filter
              </button>
            )}
          </div>

          <div className="page-size-selector">
            <span>Baris per halaman:</span>
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
                      <div style={{ maxWidth: 320, fontWeight: 600 }}>{row.name || "No description"}</div>
                    </td>
                    <td>
                      <span>{row.unit || "—"}</span>
                      <small>{row.equipment_class || "—"}</small>
                    </td>
                    <td className="mono">{row.location_id || "—"}</td>
                    <td>
                      <span className={`status ${row.status?.toLowerCase() === "operating" ? "good" : ""}`}>
                        {row.status || "—"}
                      </span>
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
              <div className="empty">Tidak ada data equipment yang sesuai dengan filter.</div>
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
