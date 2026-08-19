"use client";

export interface AttributeView {
  attribute_id: string;
  site: string | null;
  unit: string | null;
  equipment: string | null;
  parameter: string | null;
  business_name: string | null;
  position: string | null;
  unit_of_measure: string | null;
}

export interface SnapshotView {
  attribute_id: string;
  value: number | null;
  value_good: boolean | null;
  units: string | null;
  source_timestamp: string | null;
  collected_at: string | null;
}

export interface HeatmapDay {
  date: string;
  count: number;
}

export interface HeatmapResponse {
  attribute_id: string;
  days: HeatmapDay[];
  max_count: number;
  total_points: number;
}

export interface ActivityDay {
  date: string;
  runs: number;
  hours_covered: number;
}

export interface ActivityResponse {
  days: ActivityDay[];
  target_hours_per_day: number;
}

export interface StatsView {
  registered_attributes: number;
  total_timeseries_points: number;
  snapshots_collected_today: number;
  last_snapshot_cursor: string | null;
  last_backfill_cursor: string | null;
}

export interface CollectResponse {
  status: string;
  message: string;
  stats: Record<string, number> | null;
}

export interface ScheduleView {
  interval_seconds: number;
  state: "running" | "scheduled" | "idle";
  last_run_at: string | null;
  next_run_at: string | null;
  active: boolean;
}

export function timeAgo(iso: string | null | undefined): string | null {
  if (!iso) return null;
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return null;
  // epoch-ish timestamps (1970-01-01) are PI digital-state placeholders,
  // not real measurement times
  if (then < 946684800000) return null; // before 2000-01-01
  const diff = Math.max(0, Date.now() - then);
  const s = Math.floor(diff / 1000);
  if (s < 10) return "baru saja";
  if (s < 60) return `${s} dtk lalu`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} mnt lalu`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} jam lalu`;
  const d = Math.floor(h / 24);
  return `${d} hari lalu`;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api/collector${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`collector API ${path}: HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`/api/collector${path}`, { method: "POST", cache: "no-store" });
  if (!res.ok) throw new Error(`collector API ${path}: HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export const collectorApi = {
  listAttributes: (equipment?: string) =>
    get<AttributeView[]>(`/attributes${equipment ? `?equipment=${encodeURIComponent(equipment)}` : ""}`),
  listSnapshots: (limit = 500) => get<SnapshotView[]>(`/snapshots?limit=${limit}`),
  getSnapshot: (id: string) => get<SnapshotView>(`/snapshots/${encodeURIComponent(id)}`),
  getHeatmap: (id: string, days = 365) =>
    get<HeatmapResponse>(`/heatmap/${encodeURIComponent(id)}?days=${days}`),
  getActivity: (days = 365) => get<ActivityResponse>(`/activity?days=${days}`),
  getStats: () => get<StatsView>("/stats"),
  getSchedule: () => get<ScheduleView>("/schedule"),
  collectSnapshots: () => post<CollectResponse>("/collect/snapshots"),
  collectBackfill: (start: string, end: string, interval: string) =>
    post<CollectResponse>(`/collect/backfill?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&interval=${encodeURIComponent(interval)}`),
};
