/** Typed client for the cems-collector FastAPI (read-only + local triggers). */

/** Canonical display order (mirrors the production DAS layout, 5 per row). */
export const PARAMETER_ORDER: readonly string[] = [
  "SO2", "NOx", "NO", "NO2", "CO",
  "CO2", "O2", "PM", "Hg", "Flow",
  "Laju_alir", "Temp", "Humidity", "Pressure", "Opacity",
];

const _ORDER_INDEX: Record<string, number> = Object.fromEntries(
  PARAMETER_ORDER.map((code, i) => [code, i])
);

/** Sort comparator: canonical order first, unknown codes alphabetically at the end. */
export function compareParameterCodes(a: string, b: string): number {
  const ia = _ORDER_INDEX[a];
  const ib = _ORDER_INDEX[b];
  if (ia !== undefined && ib !== undefined) return ia - ib;
  if (ia !== undefined) return -1;
  if (ib !== undefined) return 1;
  return a.localeCompare(b);
}

export type SourceMap = Record<string, unknown>;

export interface ReadingView {
  id: number;
  parameter_code: string;
  stack_id: string;
  value_raw: number | null;
  value_normalized: number | null;
  value_correction: number | null;
  value_final: number | null;
  transformation_status: string;
  observed_at: string;
  created_at: string | null;
  sources?: { cems?: { read?: SourceMap; raw_registers?: number[] } } | null;
}

export interface Reading5MinView {
  id: number;
  parameter_code: string;
  stack_id: string;
  avg_value: number;
  min_value: number;
  max_value: number;
  sample_count: number;
  window_start: string;
}

export interface ParameterView {
  code: string;
  stack_id: string;
  name: string;
  unit: string;
  status: string;
  collect_enabled: boolean;
  threshold: number | null;
  normalization_enabled: boolean;
  o2_reference: number | null;
  adjust_factor: number;
  adjust_constant: number;
  sources?: { cems?: { modbus?: SourceMap } } | null;
}

export interface StackView {
  stack_id: string;
  code: string;
  name: string;
  status: string;
  description: string | null;
}

export interface CollectRunView {
  id: number;
  run_type: string;
  mode: string;
  rows_seen: number;
  upserted: number;
  skipped: number;
  errors: number;
  watermark: string | null;
  started_at: string;
  finished_at: string | null;
}

export interface StatsView {
  stack_id: string;
  read_only: boolean;
  resources: {
    stacks: number;
    parameters: number;
    reading_realtime: number;
    reading_5min: number;
  };
  last_run: CollectRunView | null;
}

export interface TriggerResult {
  run_type: string;
  rows_seen: number;
  upserted: number;
  errors: number;
  skipped: number;
  watermark: string | null;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api/collector${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} (${path})`);
  }
  return (await res.json()) as T;
}

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`/api/collector${path}`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} (${path})`);
  }
  return (await res.json()) as T;
}

export const collectorApi = {
  stats: () => get<StatsView>("/stats"),
  stacks: () => get<StackView[]>("/stacks"),
  parameters: () => get<ParameterView[]>("/parameters"),
  latest: () => get<ReadingView[]>("/latest"),
  readings: (params?: { parameter?: string; status?: string; since?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.parameter) qs.set("parameter", params.parameter);
    if (params?.status) qs.set("status", params.status);
    if (params?.since) qs.set("since", params.since);
    qs.set("limit", String(params?.limit ?? 1000));
    return get<ReadingView[]>(`/readings?${qs.toString()}`);
  },
  readings5min: (params?: { parameter?: string; since?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.parameter) qs.set("parameter", params.parameter);
    if (params?.since) qs.set("since", params.since);
    qs.set("limit", String(params?.limit ?? 1000));
    return get<Reading5MinView[]>(`/readings/5min?${qs.toString()}`);
  },
  runs: (limit = 20) => get<CollectRunView[]>(`/collect-runs?limit=${limit}`),
  collectOnce: () => post<TriggerResult>("/collect/once"),
  aggregate: () => post<TriggerResult>("/aggregate"),
};

export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return "—";
  const ms = Date.now() - new Date(iso).getTime();
  const s = Math.floor(ms / 1000);
  if (s < 60) return `${s} dtk lalu`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} mnt lalu`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} jam lalu`;
  return `${Math.floor(h / 24)} hari lalu`;
}

export function fmt(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toFixed(digits);
}
