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
  const [excludeClosedCancelled, setExcludeClosedCancelled] = useState(true);
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [classFilter, setClassFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [downtimeFilter, setDowntimeFilter] = useState("ALL");
  const [timeWindowFilter, setTimeWindowFilter] = useState("ALL");
  const [quickFilter, setQuickFilter] = useState("ALL");

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
  }, [
    search,
    statusFilter,
    excludeClosedCancelled,
    typeFilter,
    classFilter,
    priorityFilter,
    downtimeFilter,
    timeWindowFilter,
    quickFilter,
    pageSize,
  ]);

  // Derived Options
  const statusOptions = useMemo(() => {
    const excluded = new Set(["CLOSE", "CAN"]);
    return Array.from(new Set(list.map((e) => e.status).filter(Boolean) as string[]))
      .filter((status) => !excludeClosedCancelled || !excluded.has(status.toUpperCase()))
      .sort();
  }, [list, excludeClosedCancelled]);

  const typeOptions = useMemo(() => {
    return Array.from(new Set(list.map((e) => e.work_type).filter(Boolean) as string[])).sort();
  }, [list]);

  const classOptions = useMemo(() => {
    return Array.from(new Set(list.map((e) => e.work_class).filter(Boolean) as string[])).sort();
  }, [list]);

  const priorityOptions = useMemo(() => {
    return Array.from(new Set(list.map((e) => e.priority).filter(Boolean) as string[])).sort();
  }, [list]);

  // Filtered & Sorted
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const now = Date.now();

    const result = list.filter((item) => {
      const matchStatus = statusFilter === "ALL" || item.status === statusFilter;
      const matchExcluded =
        !excludeClosedCancelled || !["CLOSE", "CAN"].includes((item.status || "").toUpperCase());
      const matchType = typeFilter === "ALL" || item.work_type === typeFilter;
      const matchClass = classFilter === "ALL" || item.work_class === classFilter;
      const matchPriority = priorityFilter === "ALL" || item.priority === priorityFilter;

      let matchDowntime = true;
      if (downtimeFilter === "HAS_DOWNTIME") {
        matchDowntime = (item.downtime_hours != null && item.downtime_hours > 0);
      } else if (downtimeFilter === "HAS_LABOR") {
        matchDowntime = (item.actual_labor_hours != null && item.actual_labor_hours > 0);
      } else if (downtimeFilter === "HAS_COST") {
        matchDowntime =
          (item.actual_labor_cost != null && item.actual_labor_cost > 0) ||
          (item.actual_material_cost != null && item.actual_material_cost > 0);
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
      if (quickFilter === "EMERGENCY") {
        matchQuick = ["EM", "CM", "BD", "CORR"].includes((item.work_type || "").toUpperCase());
      } else if (quickFilter === "PREVENTIVE") {
        matchQuick = (item.work_type || "").toUpperCase() === "PM";
      } else if (quickFilter === "ACTIVE") {
        matchQuick = ["APPR", "INPRG", "WSCH", "WMATL"].includes((item.status || "").toUpperCase());
      } else if (quickFilter === "COMPLETED") {
        matchQuick = ["COMP", "CLOSE", "CLOSED", "COMPLETE"].includes((item.status || "").toUpperCase());
      } else if (quickFilter === "DOWNTIME") {
        matchQuick = (item.downtime_hours != null && item.downtime_hours > 0);
      }

      const matchSearch =
        !q ||
        [
          item.id,
          item.equipment_id,
          item.location_id,
          item.description,
          item.work_type,
          item.work_class,
          item.status,
          item.reported_by,
          item.supervisor,
          item.lead,
          item.failure_code,
        ].some((v) => v?.toLowerCase().includes(q));

      return (
        matchStatus &&
        matchExcluded &&
        matchType &&
        matchClass &&
        matchPriority &&
        matchDowntime &&
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
    excludeClosedCancelled,
    typeFilter,
    classFilter,
    priorityFilter,
    downtimeFilter,
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

  const toggleSort = (field: keyof WorkOrderView) => {
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
    !excludeClosedCancelled ||
    typeFilter !== "ALL" ||
    classFilter !== "ALL" ||
    priorityFilter !== "ALL" ||
    downtimeFilter !== "ALL" ||
    timeWindowFilter !== "ALL" ||
    quickFilter !== "ALL";

  const handleResetFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
    setExcludeClosedCancelled(true);
    setTypeFilter("ALL");
    setClassFilter("ALL");
    setPriorityFilter("ALL");
    setDowntimeFilter("ALL");
    setTimeWindowFilter("ALL");
    setQuickFilter("ALL");
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
            Daftar lengkap perintah kerja pemeliharaan korektif dan preventif yang disinkronkan dari Maximo BSR dengan filter multi-dimensi.
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
            className={`quick-chip ${quickFilter === "EMERGENCY" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "EMERGENCY" ? "ALL" : "EMERGENCY")}
          >
            🔴 Emergency / Corrective
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "PREVENTIVE" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "PREVENTIVE" ? "ALL" : "PREVENTIVE")}
          >
            🛠️ Preventive (PM)
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "ACTIVE" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "ACTIVE" ? "ALL" : "ACTIVE")}
          >
            ⏳ Sedang Berjalan (INPRG/APPR)
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "COMPLETED" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "COMPLETED" ? "ALL" : "COMPLETED")}
          >
            ✔️ Selesai (COMP/CLOSE)
          </button>
          <button
            type="button"
            className={`quick-chip ${quickFilter === "DOWNTIME" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "DOWNTIME" ? "ALL" : "DOWNTIME")}
          >
            ⏱️ Ada Downtime
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
                  Status: {s}
                </option>
              ))}
            </select>

            <label className="select-filter" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
              <input
                type="checkbox"
                checked={excludeClosedCancelled}
                onChange={(event) => setExcludeClosedCancelled(event.target.checked)}
              />
              Exclude CLOSE/CAN
            </label>

            <select
              className="select-filter"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="ALL">Semua Work Type ({typeOptions.length})</option>
              {typeOptions.map((t) => (
                <option key={t} value={t}>
                  Type: {t}
                </option>
              ))}
            </select>

            {classOptions.length > 0 && (
              <select
                className="select-filter"
                value={classFilter}
                onChange={(e) => setClassFilter(e.target.value)}
              >
                <option value="ALL">Semua Work Class ({classOptions.length})</option>
                {classOptions.map((c) => (
                  <option key={c} value={c}>
                    Class: {c}
                  </option>
                ))}
              </select>
            )}

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
              value={downtimeFilter}
              onChange={(e) => setDowntimeFilter(e.target.value)}
            >
              <option value="ALL">Semua Durasi & Biaya</option>
              <option value="HAS_DOWNTIME">Ada Downtime ({">"}0 jam)</option>
              <option value="HAS_LABOR">Ada Jam Kerja ({">"}0 jam)</option>
              <option value="HAS_COST">Memiliki Biaya Material/Labor</option>
            </select>

            <select
              className="select-filter"
              value={timeWindowFilter}
              onChange={(e) => setTimeWindowFilter(e.target.value)}
            >
              <option value="ALL">Semua Rentang Waktu</option>
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
                  <th className="sortable" onClick={() => toggleSort("priority")}>
                    Pri {sortBy === "priority" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th>Deskripsi Pekerjaan</th>
                  <th className="sortable" onClick={() => toggleSort("downtime_hours")}>
                    Downtime {sortBy === "downtime_hours" && (sortOrder === "asc" ? "↑" : "↓")}
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
                      {row.priority ? (
                        <span className="count-pill">{row.priority}</span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      <div style={{ maxWidth: 280 }}>{row.description || "—"}</div>
                    </td>
                    <td>
                      {row.downtime_hours != null && row.downtime_hours > 0 ? (
                        <span className="mono" style={{ color: "var(--amber)", fontWeight: 600 }}>
                          {row.downtime_hours} jam
                        </span>
                      ) : (
                        <span style={{ color: "var(--text-dim)" }}>0</span>
                      )}
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
              <div className="empty">Tidak ada data work orders yang sesuai dengan kriteria filter.</div>
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
