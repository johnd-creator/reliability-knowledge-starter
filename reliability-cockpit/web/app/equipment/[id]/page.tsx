"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { cockpitApi, KPI_METRICS, type EquipmentView, type ReliabilityKpiView, type WorkOrderPage } from "../../../lib/api";

export default function EquipmentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [equipment, setEquipment] = useState<EquipmentView | null>(null);
  const [kpis, setKpis] = useState<Record<string, ReliabilityKpiView | null>>({});
  const [workOrders, setWorkOrders] = useState<WorkOrderPage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setEquipment(null);
    setKpis({});
    setWorkOrders(null);
    setError(null);
    Promise.all([
      cockpitApi.getEquipment(id).then(setEquipment).catch(() => null),
      cockpitApi.listWorkOrders(id, 0, 200).then(setWorkOrders).catch(() => null),
      Promise.all(
        KPI_METRICS.map((m) =>
          cockpitApi.getKpi(id, m).then((k) => [m, k] as const).catch(() => [m, null] as const),
        ),
      ).then((entries) => setKpis(Object.fromEntries(entries))),
    ]).catch((err) => setError(String(err)));
  }, [id]);

  if (error) {
    return (
      <main>
        <div className="error">{error}</div>
      </main>
    );
  }

  if (equipment === null) {
    return (
      <main>
        <div className="empty">Loading…</div>
      </main>
    );
  }

  if (!equipment) {
    return (
      <main>
        <div className="empty">
          Equipment not found. <Link href="/">Back to equipment list</Link>
        </div>
      </main>
    );
  }

  return (
    <main>
      <p>
        <Link href="/">← All equipment</Link>
      </p>
      <section className="card">
        <h2>{equipment.id}</h2>
        <dl className="kv">
          <dt>Name</dt>
          <dd>{equipment.name ?? "—"}</dd>
          <dt>Unit</dt>
          <dd>{equipment.unit ?? "—"}</dd>
          <dt>Class</dt>
          <dd>
            <span className="badge">{equipment.equipment_class ?? "—"}</span>
          </dd>
          <dt>Status</dt>
          <dd>{equipment.status_description ?? equipment.status ?? "—"}</dd>
          <dt>Running</dt>
          <dd>{equipment.is_running === null ? "—" : equipment.is_running ? "Yes" : "No"}</dd>
          <dt>Total downtime</dt>
          <dd>{equipment.downtime_total_hours != null ? `${equipment.downtime_total_hours} h` : "—"}</dd>
        </dl>
      </section>

      <section className="card">
        <h2>Reliability KPIs</h2>
        <div className="kpi-grid">
          {KPI_METRICS.map((metric) => {
            const kpi = kpis[metric];
            return (
              <div key={metric} className="kpi-card">
                <div className="kpi-label">{metric}</div>
                <div className="kpi-value">
                  {kpi?.value != null ? kpi.value.toFixed(kpi.unit === "percent" ? 1 : 0) : "—"}
                </div>
                <div className="kpi-unit">{kpi?.unit ?? ""}</div>
              </div>
            );
          })}
        </div>
        {Object.values(kpis).every((k) => k === null) && (
          <div className="empty">
            Belum ada KPI. Jalankan <code>cockpit kpi</code> untuk menghitung.
          </div>
        )}
      </section>

      <section className="card">
        <h2>Work Orders ({workOrders?.total ?? 0})</h2>
        {workOrders === null && <div className="empty">Loading…</div>}
        {workOrders && workOrders.items.length === 0 && <div className="empty">No work orders for this equipment.</div>}
        {workOrders && workOrders.items.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Description</th>
                <th>Reported</th>
                <th>Downtime (h)</th>
                <th>Failure</th>
              </tr>
            </thead>
            <tbody>
              {workOrders.items.map((wo) => (
                <tr key={wo.id}>
                  <td>{wo.id}</td>
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
