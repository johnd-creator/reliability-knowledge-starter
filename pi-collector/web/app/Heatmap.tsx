"use client";

import { HeatmapResponse } from "@/lib/api";

function buildWeeks(days: HeatmapResponse["days"], maxCount: number) {
  const dayMap = new Map(days.map((d) => [d.date, d.count]));
  const today = new Date();
  const start = new Date(today);
  start.setDate(start.getDate() - 364);
  start.setDate(start.getDate() - start.getDay());

  const weeks: { date: string; count: number; level: number }[][] = [];
  const months: { label: string; weekIndex: number }[] = [];
  const cursor = new Date(start);
  let weekIndex = 0;
  let lastMonth = -1;

  while (cursor <= today) {
    const week: { date: string; count: number; level: number }[] = [];
    for (let dow = 0; dow < 7; dow++) {
      const dateStr = cursor.toISOString().slice(0, 10);
      if (cursor > today) {
        week.push({ date: dateStr, count: 0, level: 0 });
      } else {
        const count = dayMap.get(dateStr) || 0;
        let level = 0;
        if (count > 0 && maxCount > 0) {
          const ratio = count / maxCount;
          if (ratio <= 0.25) level = 1;
          else if (ratio <= 0.5) level = 2;
          else if (ratio <= 0.75) level = 3;
          else level = 4;
        }
        week.push({ date: dateStr, count, level });
      }
      if (dow === 0) {
        const m = cursor.getMonth();
        if (m !== lastMonth) {
          const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
          months.push({ label: monthNames[m], weekIndex });
          lastMonth = m;
        }
      }
      cursor.setDate(cursor.getDate() + 1);
    }
    weeks.push(week);
    weekIndex++;
  }
  return { weeks, months };
}

export function Heatmap({ data }: { data: HeatmapResponse | null }) {
  if (!data || data.days.length === 0) {
    return (
      <p className="muted" style={{ padding: "16px 0" }}>
        Belum ada time-series data untuk atribut ini. Jalankan backfill untuk mengunduh riwayat.
      </p>
    );
  }

  const { weeks, months } = buildWeeks(data.days, data.max_count);
  const monthLabels = [];
  let lastWeekIdx = -1;
  for (const m of months) {
    if (m.weekIndex > lastWeekIdx + 1 || lastWeekIdx === -1) {
      monthLabels.push(
        <span
          key={m.label}
          className="sub-muted mono"
          style={{ position: "absolute", left: 10 + m.weekIndex * 16, fontSize: "0.72rem", fontWeight: 600 }}
        >
          {m.label}
        </span>
      );
      lastWeekIdx = m.weekIndex;
    }
  }

  const activeDays = data.days.filter((d) => d.count > 0).length;

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 12, alignItems: "center", flexWrap: "wrap" }}>
        <span className="badge badge-good">
          <strong>{data.total_points.toLocaleString()}</strong> Data Points
        </span>
        <span className="badge badge-param">
          <strong>{activeDays}</strong> Hari dengan Data
        </span>
        <span className="sub-muted mono" style={{ marginLeft: "auto" }}>
          Peak: {data.max_count.toLocaleString()} pts/hari
        </span>
      </div>

      <div style={{ position: "relative", height: 18, marginBottom: 6 }}>
        {monthLabels}
      </div>

      <div className="heatmap-container">
        <div className="heatmap-grid">
          {weeks.map((week, wi) => (
            <div key={wi} className="heatmap-week">
              {week.map((day, di) => (
                <div
                  key={di}
                  className={`heatmap-cell l${day.level}`}
                  title={`${day.date}: ${day.count.toLocaleString()} data points`}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="heatmap-legend">
        <span className="sub-muted">Sedikit</span>
        <div className="heatmap-cell l0" />
        <div className="heatmap-cell l1" />
        <div className="heatmap-cell l2" />
        <div className="heatmap-cell l3" />
        <div className="heatmap-cell l4" />
        <span className="sub-muted">Banyak (Kerapatan Tinggi)</span>
      </div>
    </div>
  );
}
