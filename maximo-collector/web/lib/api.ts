"use client";

export type SourceMap = Record<string, unknown>;

export interface EquipmentView {
  id: string;
  name: string | null;
  location_id: string | null;
  equipment_class: string | null;
  unit: string | null;
  status: string | null;
  status_description: string | null;
  is_running: boolean | null;
  priority: number | null;
  manufacturer: string | null;
  vendor: string | null;
  source_changed_at: string | null;
  sources: { maximo?: { extra?: SourceMap } } | null;
}

export interface WorkOrderView {
  id: string;
  equipment_id: string | null;
  location_id: string | null;
  status: string | null;
  status_description: string | null;
  work_type: string | null;
  work_class: string | null;
  description: string | null;
  reported_at: string | null;
  source_changed_at: string | null;
  status_changed_at: string | null;
  scheduled_start: string | null;
  scheduled_finish: string | null;
  target_completion: string | null;
  estimated_duration_hours: number | null;
  downtime_hours: number | null;
  priority: string | null;
  priority_description: string | null;
  reported_by: string | null;
  supervisor: string | null;
  lead: string | null;
  failure_code: string | null;
  is_task: boolean | null;
  parent_wo: string | null;
  has_children: boolean | null;
  estimated_labor_cost: number | null;
  estimated_material_cost: number | null;
  actual_labor_cost: number | null;
  actual_material_cost: number | null;
  actual_labor_hours: number | null;
  sources: { maximo?: { extra?: SourceMap } } | null;
}

export interface ServiceRequestView {
  id: string;
  description: string | null;
  status: string | null;
  status_description: string | null;
  work_type: string | null;
  equipment_id: string | null;
  location_id: string | null;
  reported_by: string | null;
  reported_by_name: string | null;
  reported_at: string | null;
  source_changed_at: string | null;
  affected_at: string | null;
  actual_start: string | null;
  actual_finish: string | null;
  target_start: string | null;
  target_finish: string | null;
  internal_priority: string | null;
  reported_priority: string | null;
  actual_labor_hours: number | null;
  actual_labor_cost: number | null;
  risk_area_environment: string | null;
  risk_area_process: string | null;
  risk_area_human: string | null;
  risk_area_reputation: string | null;
  class: string | null;
  status_changed_at: string | null;
  sources: { maximo?: { extra?: SourceMap } } | null;
}

export interface GenericView {
  id: string;
  display_name?: string | null;
  description?: string | null;
  status?: string | null;
}

export interface SyncStatus {
  watermark: string | null;
  rows: number;
}

export interface CollectRunView {
  id: number;
  object_structure: string;
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
  site: string;
  org: string;
  read_only: boolean;
  resources: Record<string, number>;
  last_run: CollectRunView | null;
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`/api/collector${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Collector API ${path}: HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

async function post<T>(path: string): Promise<T> {
  const response = await fetch(`/api/collector${path}`, { method: "POST", cache: "no-store" });
  if (!response.ok) throw new Error(`Collector API ${path}: HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

export const collectorApi = {
  stats: () => get<StatsView>("/stats"),
  status: () => get<Record<string, SyncStatus>>("/sync/status"),
  runs: (limit = 20) => get<CollectRunView[]>(`/collect-runs?limit=${limit}`),
  equipment: (limit = 5000) => get<EquipmentView[]>(`/equipment?limit=${limit}`),
  workOrders: (limit = 5000) => get<WorkOrderView[]>(`/work-orders?limit=${limit}`),
  serviceRequests: (limit = 5000) => get<ServiceRequestView[]>(`/service-requests?limit=${limit}`),
  persons: (limit = 5000) => get<GenericView[]>(`/persons?limit=${limit}`),
  items: (limit = 5000) => get<GenericView[]>(`/items?limit=${limit}`),
  labor: (limit = 5000) => get<GenericView[]>(`/labor?limit=${limit}`),
  sync: (object: string) => post<{ object_structure: string; rows_seen: number; upserted: number; skipped: number }>(`/sync/${object}`),
};

export function timeAgo(value: string | null | undefined): string {
  if (!value) return "—";
  const elapsed = Math.max(0, Date.now() - new Date(value).getTime());
  const minutes = Math.floor(elapsed / 60000);
  if (minutes < 1) return "baru saja";
  if (minutes < 60) return `${minutes} mnt lalu`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} jam lalu`;
  return `${Math.floor(hours / 24)} hari lalu`;
}
