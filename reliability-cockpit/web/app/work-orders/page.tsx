"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { cockpitApi, type WorkOrderPage } from "../../lib/api";

export default function WorkOrdersPage() {
  const [page, setPage] = useState<WorkOrderPage | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    cockpitApi
      .listWorkOrders(undefined, (pageNumber - 1) * pageSize, pageSize)
      .then((result) => {
        if (active) setPage(result);
      })
      .catch((err) => {
        if (active) setError(String(err));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [pageNumber, pageSize]);

  const total = page?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = Math.min(pageNumber, totalPages);
  const start = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const end = Math.min(currentPage * pageSize, total);

  const changePageSize = (value: number) => {
    setPageSize(value);
    setPageNumber(1);
  };

  return (
    <main>
      <section className="card">
        <h2>Work Orders (all equipment)</h2>
        {error && <div className="error">{error}</div>}
        {loading && <div className="empty">Loading…</div>}
        {!loading && !error && total === 0 && (
          <div className="empty">Belum ada data. Jalankan <code>cockpit sync</code> terlebih dahulu.</div>
        )}
        {!loading && !error && page && page.items.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Equipment</th>
                <th>Type</th>
                <th>Status</th>
                <th>Description</th>
                <th>Reported</th>
                <th>Downtime (h)</th>
                <th>Failure</th>
              </tr>
            </thead>
            <tbody>
              {page.items.map((wo) => (
                <tr key={wo.id}>
                  <td>{wo.id}</td>
                  <td>
                    {wo.equipment_id ? (
                      <Link href={`/equipment/${encodeURIComponent(wo.equipment_id)}`}>{wo.equipment_id}</Link>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    <span className="badge">{wo.work_type ?? "—"}</span>
                  </td>
                  <td>{wo.status ?? "—"}</td>
                  <td className="desc">{wo.description ?? "—"}</td>
                  <td>{wo.reported_at?.slice(0, 10) ?? "—"}</td>
                  <td>{wo.downtime_hours ?? "—"}</td>
                  <td>{wo.failure_code ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && !error && total > 0 && (
          <div className="pagination-bar" aria-label="Work order pagination">
            <div>
              Menampilkan <strong>{start.toLocaleString()}</strong>–<strong>{end.toLocaleString()}</strong> dari{" "}
              <strong>{total.toLocaleString()}</strong> Work Order
            </div>
            <div className="pagination-controls">
              <label>
                Per halaman{" "}
                <select value={pageSize} onChange={(event) => changePageSize(Number(event.target.value))}>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </label>
              <button type="button" disabled={currentPage <= 1} onClick={() => setPageNumber(1)}>
                Awal
              </button>
              <button type="button" disabled={currentPage <= 1} onClick={() => setPageNumber((value) => value - 1)}>
                Sebelumnya
              </button>
              <span>Halaman {currentPage} / {totalPages}</span>
              <button type="button" disabled={currentPage >= totalPages} onClick={() => setPageNumber((value) => value + 1)}>
                Berikutnya
              </button>
              <button type="button" disabled={currentPage >= totalPages} onClick={() => setPageNumber(totalPages)}>
                Akhir
              </button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
