"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { collectorApi, ServiceRequestView, timeAgo } from "@/lib/api";

export default function ServiceRequestsPage() {
  const [list, setList] = useState<ServiceRequestView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [laborFilter, setLaborFilter] = useState("ALL");
  const [timeWindowFilter, setTimeWindowFilter] = useState("ALL");
  const [quickFilter, setQuickFilter] = useState("ALL");

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [sortBy, setSortBy] = useState<keyof ServiceRequestView>("id");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await collectorApi.serviceRequests(10000);
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
  }, [
    search,
    statusFilter,
    typeFilter,
    priorityFilter,
    riskFilter,
    laborFilter,
    timeWindowFilter,
    quickFilter,
    pageSize,
  ]);

  // Options
  const statusOptions = useMemo(() => {
    return Array.from(new Set(list.map((e) => e.status).filter(Boolean) as string[])).sort();
  }, [list]);

  const typeOptions = useMemo(() => {
    return Array.from(new Set(list.map((e) => e.work_type).filter(Boolean) as string[])).sort();
  }, [list]);

  const priorityOptions = useMemo(() => {
    const set = new Set<string>();
    for (const item of list) {
      if (item.reported_priority) set.add(item.reported_priority);
      if (item.internal_priority) set.add(item.internal_priority);
    }
    return Array.from(set).sort();
  }, [list]);

  // Filtered & Sorted
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const now = Date.now();

    const result = list.filter((item) => {
      const matchStatus = statusFilter === "ALL" || item.status === statusFilter;
      const matchType = typeFilter === "ALL" || item.work_type === typeFilter;
      const matchPriority =
        priorityFilter === "ALL" ||
        item.reported_priority === priorityFilter ||
        item.internal_priority === priorityFilter;

      let matchRisk = true;
      if (riskFilter === "ANY_RISK") {
        matchRisk = Boolean(item.risk_area_process || item.risk_area_human || item.risk_area_environment || item.risk_area_reputation);
      } else if (riskFilter === "PROCESS") {
        matchRisk = Boolean(item.risk_area_process);
      } else if (riskFilter === "HUMAN") {
        matchRisk = Boolean(item.risk_area_human);
      } else if (riskFilter === "ENV") {
        matchRisk = Boolean(item.risk_area_environment);
      } else if (riskFilter === "REPUTATION") {
        matchRisk = Boolean(item.risk_area_reputation);
      }

      let matchLabor = true;
      if (laborFilter === "HAS_HOURS") {
        matchLabor = item.actual_labor_hours != null && item.actual_labor_hours > 0;
      } else if (laborFilter === "HAS_COST") {
        matchLabor = item.actual_labor_cost != null && item.actual_labor_cost > 0;
      }

      let matchWindow = true;
      if (timeWindowFilter !== "ALL" && item.source_changed_at) {
        const itemTime = new Date(item.source_changed_at).getTime();
        const diffDays = (now - itemTime) / (1000 * 60 * 60 * 24);
        if (timeWindowFilter === "7D") matchWindow = diffDays <= 7;
        else if (timeWindowFilter === "30D") matchWindow = diffDays <= 30;
        else if (timeWindowFilter === "90D") matchWindow = diffDays <= 90;
      }

      let matchQuick = true;
      if (quickFilter === "HIGH_PRIORITY") {
        matchQuick = ["1", "2", "P1", "P2", "HIGH", "EMERGENCY"].includes((item.reported_priority || item.internal_priority || "").toUpperCase());
      } else if (quickFilter === "HAS_RISK") {
        matchQuick = Boolean(item.risk_area_process || item.risk_area_human || item.risk_area_environment);
      } else if (quickFilter === "OPEN") {
        matchQuick = ["NEW", "QUEUED", "INPRG", "ASSIGNED", "WAPPR"].includes((item.status || "").toUpperCase());
      } else if (quickFilter === "RESOLVED") {
        matchQuick = ["RESOLVED", "CLOSED", "CLOSE", "COMPLETE"].includes((item.status || "").toUpperCase());
      } else if (quickFilter === "HAS_LABOR") {
        matchQuick = (item.actual_labor_hours != null && item.actual_labor_hours > 0) || (item.actual_labor_cost != null && item.actual_labor_cost > 0);
      }

      const matchSearch =
        !q ||
        [
          item.id,
          item.equipment_id,
          item.location_id,
          item.description,
          item.reported_by,
          item.reported_by_name,
          item.status,
          item.risk_area_process,
          item.risk_area_human,
          item.risk_area_environment,
        ].some((v) => v?.toLowerCase().includes(q));

      return (
        matchStatus &&
        matchType &&
        matchPriority &&
        matchRisk &&
        matchLabor &&
        matchWindow &&
        matchQuick &&
        matchSearch
      );
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
  }, [
    list,
    search,
    statusFilter,
    typeFilter,
    priorityFilter,
    riskFilter,
    laborFilter,
    timeWindowFilter,
    quickFilter,
    sortBy,
    sortOrder,
  ]);

  // Pagination
  const totalRows = filtered.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  const pageSafe = Math.min(Math.max(1, currentPage), totalPages);
  const startIdx = (pageSafe - 1) * pageSize;
  const paginated = filtered.slice(startIdx, startIdx + pageSize);

  const toggleSort = (field: keyof ServiceRequestView) => {
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
    typeFilter !== "ALL" ||
    priorityFilter !== "ALL" ||
    riskFilter !== "ALL" ||
    laborFilter !== "ALL" ||
    timeWindowFilter !== "ALL" ||
    quickFilter !== "ALL";

  const handleResetFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
    setTypeFilter("ALL");
    setPriorityFilter("ALL");
    setRiskFilter("ALL");
    setLaborFilter("ALL");
    setTimeWindowFilter("ALL");
    setQuickFilter("ALL");
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <Link href="/" className="back-link" style={{ margin: 0 }}>
          ← Kembali ke Dashboard
        </Link>
        <span className="count-pill">Total: {list.length.toLocaleString()} Service Requests Terdaftar</span>
      </div>

      <section className="hero" style={{ marginBottom: 24 }}>
        <div>
          <p className="eyebrow">SERVICE REQUESTS / MXAPISR</p>
          <h1>Service Requests Explorer</h1>
          <p className="lede">
            Daftar laporan tiket gangguan dan permintaan layanan yang disinkronkan dari Maximo BSR dengan filter multi-dimensi.
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
            className={`quick-chip ${quickFilter === "HIGH_PRIORITY" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "HIGH_PRIORITY" ? "ALL" : "HIGH_PRIORITY")}
          >
            🚨 Prioritas Tinggi (P1/P2)
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "HAS_RISK" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "HAS_RISK" ? "ALL" : "HAS_RISK")}
          >
            ⚠️ Area Risiko Teridentifikasi
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "OPEN" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "OPEN" ? "ALL" : "OPEN")}
          >
            🟢 Open / Dalam Proses
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "RESOLVED" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "RESOLVED" ? "ALL" : "RESOLVED")}
          >
            ✔️ Selesai (Resolved/Closed)
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "HAS_LABOR" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "HAS_LABOR" ? "ALL" : "HAS_LABOR")}
          >
            💼 Ada Jam/Biaya Labor
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
              placeholder="Cari SR #, asset, pelapor, deskripsi..."
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
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="ALL">Semua Work Type ({typeOptions.length})</option>
              {typeOptions.map((type) => (
                <option key={type} value={type}>
                  Type: {type}
                </option>
              ))}
            </select>

            {priorityOptions.length > 0 && (
              <select
                className="select-filter"
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
              >
                <option value="ALL">Semua Prioritas</option>
                {priorityOptions.map((p) => (
                  <option key={p} value={p}>
                    Priority: {p}
                  </option>
                ))}
              </select>
            )}

            <select
              className="select-filter"
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
            >
              <option value="ALL">Semua Kategori Risiko</option>
              <option value="ANY_RISK">Memiliki Catatan Risiko</option>
              <option value="PROCESS">Risiko Operasi / Proses</option>
              <option value="HUMAN">Risiko Keselamatan Kerja</option>
              <option value="ENV">Risiko Lingkungan</option>
            </select>

            <select
              className="select-filter"
              value={laborFilter}
              onChange={(e) => setLaborFilter(e.target.value)}
            >
              <option value="ALL">Semua Pengerjaan</option>
              <option value="HAS_HOURS">Ada Jam Kerja ({">"}0 jam)</option>
              <option value="HAS_COST">Ada Biaya Labor</option>
            </select>

            <select
              className="select-filter"
              value={timeWindowFilter}
              onChange={(e) => setTimeWindowFilter(e.target.value)}
            >
              <option value="ALL">Semua Waktu</option>
              <option value="7D">7 Hari Terakhir</option>
              <option value="30D">30 Hari Terakhir</option>
              <option value="90D">90 Hari Terakhir</option>
            </select>

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

        {loading ? (
          <div className="empty">Memuat data service requests...</div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th className="sortable" onClick={() => toggleSort("id")}>
                    SR # {sortBy === "id" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("equipment_id")}>
                    Equipment {sortBy === "equipment_id" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("status")}>
                    Status {sortBy === "status" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="sortable" onClick={() => toggleSort("reported_priority")}>
                    Pri {sortBy === "reported_priority" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th>Deskripsi Permintaan</th>
                  <th className="sortable" onClick={() => toggleSort("reported_by")}>
                    Pelapor {sortBy === "reported_by" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
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
                      <Link href={`/service-requests/${encodeURIComponent(row.id)}`} className="asset-link">
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
                      <span className="status">{row.status || "—"}</span>
                    </td>
                    <td>
                      {row.reported_priority ? (
                        <span className="count-pill">P{row.reported_priority}</span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      <div style={{ maxWidth: 280 }}>{row.description || "—"}</div>
                    </td>
                    <td>
                      <small style={{ color: "var(--text)", fontWeight: 600 }}>{row.reported_by_name || row.reported_by || "—"}</small>
                    </td>
                    <td className="mono" style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                      {timeAgo(row.source_changed_at)}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <Link
                        href={`/service-requests/${encodeURIComponent(row.id)}`}
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
              <div className="empty">Tidak ada data service requests yang sesuai kriteria filter.</div>
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
