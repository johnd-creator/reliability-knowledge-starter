"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { cockpitApi, type EquipmentView } from "../lib/api";

export default function HomePage() {
  const [equipment, setEquipment] = useState<EquipmentView[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cockpitApi
      .listEquipment(200)
      .then(setEquipment)
      .catch((err) => setError(String(err)));
  }, []);

  return (
    <main>
      <section className="card">
        <h2>Equipment (objects synced from Maximo site BSR)</h2>
        {error && <div className="error">{error}</div>}
        {!error && equipment === null && <div className="empty">Loading…</div>}
        {equipment && equipment.length === 0 && (
          <div className="empty">Belum ada data. Jalankan <code>cockpit sync</code> terlebih dahulu.</div>
        )}
        {equipment && equipment.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Unit</th>
                <th>Class</th>
                <th>Status</th>
                <th>Downtime (h)</th>
              </tr>
            </thead>
            <tbody>
              {equipment.map((e) => (
                <tr key={e.id}>
                  <td>
                    <Link href={`/equipment/${encodeURIComponent(e.id)}`}>{e.id}</Link>
                  </td>
                  <td>{e.name ?? "—"}</td>
                  <td>{e.unit ?? "—"}</td>
                  <td>
                    <span className="badge">{e.equipment_class ?? "—"}</span>
                  </td>
                  <td>{e.status_description ?? e.status ?? "—"}</td>
                  <td>{e.downtime_total_hours ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
