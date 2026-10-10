"use client";

import Link from "next/link";
import { ErrorState, LoadingState, TableFrame } from "../../../components/ui";
import { use, useEffect, useState } from "react";
import { cockpitApi, KPI_METRICS, type EquipmentView, type ReliabilityKpiView, type WorkOrderPage } from "../../../lib/api";

export default function EquipmentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [equipment, setEquipment] = useState<EquipmentView | null>(null);
  const [kpis, setKpis] = useState<Record<string, ReliabilityKpiView | null>>({});
  const [workOrders, setWorkOrders] = useState<WorkOrderPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setEquipment(null);
    setKpis({});
    setWorkOrders(null);
    setError(null);
    cockpitApi.getEquipment(id).then(nextEquipment => {
      if (!active) return;
      setEquipment(nextEquipment);
    }).catch(() => { if (active) setError("Equipment data unavailable"); })
      .finally(() => { if (active) setLoading(false); });
    cockpitApi.listWorkOrders(id, 0, 200).then(nextWorkOrders => {
      if (active) setWorkOrders(nextWorkOrders);
    }).catch(() => undefined);
    Promise.all(KPI_METRICS.map(metric =>
      cockpitApi.getKpi(id, metric).then(value => [metric, value] as const).catch(() => [metric, null] as const),
    )).then(entries => { if (active) setKpis(Object.fromEntries(entries)); });
    return () => { active = false; };
  }, [id]);

  if (error) {
    return (
      <section className="legacy-content" aria-label="Equipment context">
        <ErrorState message={error} />
      </section>
    );
  }

  if (loading) {
    return (
      <section className="legacy-content" aria-label="Equipment context">
        <LoadingState label="Reading equipment context…" />
      </section>
    );
  }

  if (!equipment) {
    return (
      <section className="legacy-content" aria-label="Equipment context">
        <div className="empty">
          Equipment not found. <Link href="/">Back to overview</Link>
        </div>
      </section>
    );
  }

  return (
    <section className="legacy-content" aria-label="Equipment context">
      <p>
        <Link href="/">← Executive Overview</Link>
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
        <h2>Work Orders ({workOrders?.total ?? "UNKNOWN"})</h2>
        {workOrders === null && <LoadingState label="Reading equipment context…" />}
        {workOrders && workOrders.items.length === 0 && <div className="empty">No work orders for this equipment.</div>}
        {workOrders && workOrders.items.length > 0 && (
          <TableFrame label="Equipment context data"><table>
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
          </table></TableFrame>
        )}
      </section>
    </section>
  );
}
