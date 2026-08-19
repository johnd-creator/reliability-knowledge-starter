"use client";

import { useEffect, useState } from "react";
import { collectorApi, ActivityResponse } from "@/lib/api";

interface DayCell {
  date: string;
  runs: number;
  hours: number;
  level: number;
}

const RANGE_OPTIONS = [
  { label: "1 Bulan", months: 1 },
  { label: "2 Bulan", months: 2 },
  { label: "3 Bulan", months: 3 },
];

function buildWeeks(data: ActivityResponse, months: number) {
  const dayMap = new Map(data.days.map((d) => [d.date, d]));
  const target = data.target_hours_per_day || 24;
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), 1);
  start.setMonth(start.getMonth() - (months - 1));
  start.setDate(start.getDate() - start.getDay());

  const weeks: DayCell[][] = [];
  const monthsLabels: { label: string; year: number; weekIndex: number }[] = [];
  const cursor = new Date(start);
  let weekIndex = 0;
  let lastMonth = -1;

  while (cursor <= today) {
    const week: DayCell[] = [];
    for (let dow = 0; dow < 7; dow++) {
      const dateStr = cursor.toISOString().slice(0, 10);
      if (cursor > today) {
        week.push({ date: dateStr, runs: 0, hours: 0, level: 0 });
      } else {
        const entry = dayMap.get(dateStr);
        const runs = entry?.runs ?? 0;
        const hours = entry?.hours_covered ?? 0;
        const ratio = hours / target;
        let level = 0;
        if (hours > 0) {
          if (ratio >= 0.999) level = 4;
          else if (ratio >= 0.75) level = 3;
          else if (ratio >= 0.5) level = 2;
          else level = 1;
        }
        week.push({ date: dateStr, runs, hours, level });
      }
      if (dow === 0) {
        const m = cursor.getMonth();
        if (m !== lastMonth) {
          const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
          monthsLabels.push({ label: monthNames[m], year: cursor.getFullYear(), weekIndex });
          lastMonth = m;
        }
      }
      cursor.setDate(cursor.getDate() + 1);
    }
    weeks.push(week);
    weekIndex++;
  }
  return { weeks, monthsLabels };
}

function tooltip(day: DayCell) {
  const date = new Date(day.date + "T00:00:00").toLocaleDateString("id-ID", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
  if (day.hours === 0 && day.runs === 0) return `${date}: Belum ada data / aktivitas`;
  const source = day.runs > 0 ? `${day.runs} collector run` : "Terisi via backfill";
  const parts = [`${date}: ${day.hours}/24 jam tercakup (${source})`];
  if (day.hours === 24) parts.push("✓ Full 24h Coverage");
  return parts.join(" • ");
}

export function ActivityHeatmap() {
  const [data, setData] = useState<ActivityResponse | null>(null);
  const [months, setMonths] = useState(2);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    collectorApi
      .getActivity(months * 31 + 7)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [months]);

  if (error) return <div className="collect-result err">✗ {error}</div>;
  if (!data) return <p className="muted" style={{ padding: "16px 0" }}>Memuat riwayat aktivitas collector...</p>;
  if (data.days.length === 0) {
    return (
      <div style={{ padding: "16px 0" }} className="muted">
        Belum ada riwayat aktivitas collector. Menjalankan <code>picollector run</code> atau{" "}
        <code>collect-snapshots</code> akan mengisi matriks ini.
      </div>
    );
  }

  const { weeks, monthsLabels } = buildWeeks(data, months);
  const activeDays = data.days.filter((d) => d.hours_covered > 0).length;
  const fullDays = data.days.filter((d) => d.hours_covered >= 24).length;
  const totalDays = data.days.length || 1;
  const coveragePercent = Math.min(100, Math.round((activeDays / totalDays) * 100));

  return (
    <div>
      <div style={{ display: "flex", gap: 16, marginBottom: 12, flexWrap: "wrap", alignItems: "center" }}>
        <div className="range-toggle">
          {RANGE_OPTIONS.map((opt) => (
            <button
              key={opt.months}
              type="button"
              className={`range-btn ${months === opt.months ? "active" : ""}`}
              onClick={() => setMonths(opt.months)}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <span className="badge badge-good">
            <strong>{activeDays}</strong> Hari Aktif ({coveragePercent}%)
          </span>
          <span className="badge badge-param">
            <strong>{fullDays}</strong> Hari Penuh (24h)
          </span>
        </div>
      </div>

      <div style={{ position: "relative", height: 18, marginBottom: 6 }}>
        {monthsLabels.map((m, i) => (
          <span
            key={`${m.label}-${m.year}-${i}`}
            className="sub-muted mono"
            style={{
              position: "absolute",
              left: 10 + m.weekIndex * 16,
              fontSize: "0.72rem",
              fontWeight: 600,
            }}
          >
            {m.label}
          </span>
        ))}
      </div>

      <div className="heatmap-container">
        <div className="heatmap-grid">
          {weeks.map((week, wi) => (
            <div key={wi} className="heatmap-week">
              {week.map((day, di) => (
                <div
                  key={di}
                  className={`heatmap-cell l${day.level}`}
                  title={tooltip(day)}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="heatmap-legend">
        <span className="sub-muted">Kosong</span>
        <div className="heatmap-cell l0" />
        <div className="heatmap-cell l1" />
        <div className="heatmap-cell l2" />
        <div className="heatmap-cell l3" />
        <div className="heatmap-cell l4" />
        <span className="sub-muted">24 Jam Penuh</span>
      </div>
    </div>
  );
}
