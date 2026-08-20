"use client";

/** Minimal client for the Reliability Cockpit API (server-side proxy via rewrite). */

export interface EquipmentView {
  id: string;
  name: string | null;
  location_id: string | null;
  equipment_class: string | null;
  unit: string | null;
  status: string | null;
  status_description: string | null;
  is_running: boolean | null;
  parent_id: string | null;
  ancestor_id: string | null;
  downtime_total_hours: number | null;
}

export interface WorkOrderView {
  id: string;
  equipment_id: string | null;
  status: string | null;
  work_type: string | null;
  description: string | null;
  reported_at: string | null;
  downtime_hours: number | null;
  failure_code: string | null;
}

export interface WorkOrderPage {
  items: WorkOrderView[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

export interface ReliabilityKpiView {
  id: string;
  equipment_id: string | null;
  metric: string | null;
  value: number | null;
  unit: string | null;
  period_start: string | null;
  period_end: string | null;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api/cockpit${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`cockpit API ${path}: HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export const KPI_METRICS = ["MTBF", "MTTR", "AVAILABILITY", "PM_COMPLIANCE"] as const;

export const cockpitApi = {
  listEquipment: (limit = 200) => get<EquipmentView[]>(`/equipment?limit=${limit}`),
  getEquipment: (equipmentId: string) =>
    get<EquipmentView>(`/equipment/${encodeURIComponent(equipmentId)}`),
  listWorkOrders: (equipmentId?: string, offset = 0, limit = 50, status?: string) => {
    const params = new URLSearchParams();
    if (equipmentId) params.set("equipment_id", equipmentId);
    if (status) params.set("status", status);
    params.set("offset", String(offset));
    params.set("limit", String(limit));
    return get<WorkOrderPage>(`/work-orders?${params.toString()}`);
  },
  listWorkOrderStatuses: () => get<string[]>("/work-orders/statuses"),
  getKpi: (equipmentId: string, metric: string) =>
    get<ReliabilityKpiView>(`/kpis/${encodeURIComponent(equipmentId)}/${encodeURIComponent(metric)}`),
  health: () => get<{ status: string }>("/health"),
};
