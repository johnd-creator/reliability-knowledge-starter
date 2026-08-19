"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { cockpitApi, type WorkOrderView } from "../../lib/api";

export default function WorkOrdersPage() {
  const [workOrders, setWorkOrders] = useState<WorkOrderView[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cockpitApi
      .listWorkOrders(undefined, 500)
      .then(setWorkOrders)
      .catch((err) => setError(String(err)));
  }, []);

  return (
    <main>
      <section className="card">
        <h2>Work Orders (all equipment)</h2>
        {error && <div className="error">{error}</div>}
        {!error && workOrders === null && <div className="empty">Loading…</div>}
        {workOrders && workOrders.length === 0 && (
          <div className="empty">Belum ada data. Jalankan <code>cockpit sync</code> terlebih dahulu.</div>
        )}
        {workOrders && workOrders.length > 0 && (
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
              {workOrders.map((wo) => (
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
      </section>
    </main>
  );
}
