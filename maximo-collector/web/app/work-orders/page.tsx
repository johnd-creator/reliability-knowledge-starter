"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { collectorApi, WorkOrderView, timeAgo } from "@/lib/api";

export default function WorkOrdersPage() {
  const [list, setList] = useState<WorkOrderView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortBy, setSortBy] = useState<keyof WorkOrderView>("id");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await collectorApi.workOrders(10000);
      setList(data);
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
  }, [search, statusFilter, typeFilter, pageSize]);

  // Options
  const statusOptions = useMemo(() => {
    return Array.from(new Set(list.map((e) => e.status).filter(Boolean) as string[])).sort();
  }, [list]);

  const typeOptions = useMemo(() => {
    return Array.from(new Set(list.map((e) => e.work_type).filter(Boolean) as string[])).sort();
  }, [list]);

  // Filtered & Sorted
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const result = list.filter((item) => {
      const matchStatus = statusFilter === "ALL" || item.status === statusFilter;
      const matchType = typeFilter === "ALL" || item.work_type === typeFilter;
      const matchSearch =
        !q ||
        [item.id, item.equipment_id, item.location_id, item.description, item.work_type, item.status, item.reported_by].some(
          (v) => v?.toLowerCase().includes(q)
        );
      return matchStatus && matchType && matchSearch;
    });

    result.sort((a, b) => {
      const valA = a[sortBy] ?? "";
      const valB = b[sortBy] ?? "";
      if (typeof valA === "string") {
        const cmp = (valA as string).localeCompare(String(valB));
        return sortOrder === "asc" ? cmp : -cmp;
      }
      const cmp = valA > valB ? 1 : -1;
      return sortOrder === "asc" ? cmp : -cmp;
    });

    return result;
  }, [list, search, statusFilter, typeFilter, sortBy, sortOrder]);

  // Pagination
  const totalRows = filtered.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  const pageSafe = Math.min(Math.max(1, currentPage), totalPages);
  const startIdx = (pageSafe - 1) * pageSize;
  const paginated = filtered.slice(startIdx, startIdx + pageSize);

  const toggleSort = (field: keyof WorkOrderView) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <Link href="/" className="back-link" style={{ margin: 0 }}>
          ← Kembali ke Dashboard
        </Link>
        <span className="count-pill">Total: {list.length.toLocaleString()} Work Orders Terdaftar</span>
      </div>

      <section className="hero" style={{ marginBottom: 24 }}>
        <div>
          <p className="eyebrow">WORK ORDERS / MXWODETAIL</p>
          <h1>Work Orders Explorer</h1>
          <p className="lede">
            Daftar lengkap perintah kerja pemeliharaan korektif dan preventif yang disinkronkan dari Maximo BSR.
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

      <div className="panel">
        <div className="table-tools-bar">
          <div className="table-filters">
            <input
              className="search-input"
              style={{ width: 280 }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Cari WO #, asset, deskripsi, pelapor..."
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
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="ALL">Semua Work Type ({typeOptions.length})</option>
              {typeOptions.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>

            {(search || statusFilter !== "ALL" || typeFilter !== "ALL") && (
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => {
                  setSearch("");
                  setStatusFilter("ALL");
                  setTypeFilter("ALL");
                }}
              >
                ✕ Reset
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

        {loading ? (
          <div className="empty">Memuat data work orders...</div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th className="sortable" onClick={() => toggleSort("id")}>
                    WO # {sortBy === "id" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("equipment_id")}>
                    Equipment {sortBy === "equipment_id" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("work_type")}>
                    Work Type {sortBy === "work_type" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("status")}>
                    Status {sortBy === "status" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th>Deskripsi Pekerjaan</th>
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
                      <Link href={`/work-orders/${encodeURIComponent(row.id)}`} className="asset-link">
                        <b>{row.id}</b>
                      </Link>
                    </td>
                    <td>
                      {row.equipment_id ? (
                        <Link href={`/equipment/${encodeURIComponent(row.equipment_id)}`} className="asset-link">
                          <b>{row.equipment_id} ↗</b>
                        </Link>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      <span className="count-pill">{row.work_type || "—"}</span>
                    </td>
                    <td>
                      <span className="status">{row.status || "—"}</span>
                    </td>
                    <td>
                      <div style={{ maxWidth: 320 }}>{row.description || "—"}</div>
                    </td>
                    <td className="mono" style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                      {timeAgo(row.source_changed_at)}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <Link
                        href={`/work-orders/${encodeURIComponent(row.id)}`}
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
              <div className="empty">Tidak ada data work orders yang sesuai filter.</div>
            )}
          </div>
        )}

        <div className="pagination-bar">
          <div className="pagination-info">
            Menampilkan <strong>{totalRows === 0 ? 0 : startIdx + 1}</strong> –{" "}
            <strong>{Math.min(startIdx + pageSize, totalRows)}</strong> dari{" "}
            <strong>{totalRows.toLocaleString()}</strong> data
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
