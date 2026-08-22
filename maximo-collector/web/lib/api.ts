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
  first_name?: string | null;
  description?: string | null;
  status?: string | null;
  location_org?: string | null;
  item_type?: string | null;
  issue_unit?: string | null;
  order_unit?: string | null;
  person_id?: string | null;
  work_site?: string | null;
  is_assigned?: boolean | null;
  status_description?: string | null;
}

export interface ListFilters {
  q?: string;
  status?: string;
  work_type?: string;
  equipment_id?: string;
  location_id?: string;
  unit?: string;
  equipment_class?: string;
  manufacturer?: string;
  vendor?: string;
  priority?: string;
  item_type?: string;
  issue_unit?: string;
  order_unit?: string;
  location_org?: string;
  work_site?: string;
  person_id?: string;
  changed_since?: string;
  changed_until?: string;
  offset?: number;
  limit?: number;
  sort?: string;
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

export interface ExplorerResourceView {
  resource_key: string;
  source_system: string;
  source_application: string | null;
  source_object: string;
  label: string;
  module: string;
  scope: { site: string; organization: string };
  selected_fields: string[];
  canonical_target: string;
  contract_version: string;
  records: number;
  last_sync: string | null;
  status: "READY" | "CONFIGURED_EMPTY";
  primary_fields: string[];
  deferred: boolean;
}

export interface ExplorerDeferredView {
  source_object: string;
  label: string;
  reason: string;
}

export interface ExplorerCatalogView {
  resources: ExplorerResourceView[];
  deferred: ExplorerDeferredView[];
  integrity?: ExplorerIntegrityView;
}

export interface ExplorerIntegrityView {
  asset_reference_total: number;
  asset_reference_resolved: number;
  asset_reference_unresolved: number;
  workorder_reference_total: number;
  workorder_reference_resolved: number;
  workorder_reference_unresolved: number;
}

export interface ExplorerPage<T> {
  items: T[];
  meta: { total: number; offset: number; limit: number; has_more: boolean };
}

export interface ExplorerSourceRecord {
  canonical_id: string;
  contract_version: string;
  source_data: Record<string, unknown>;
  source_updated_at: string | null;
}

export interface ExplorerMappingRow {
  source_field: string | null;
  canonical_field: string;
  transformation: string;
  nullable: boolean;
  evidence: string;
  notes: string | null;
}

export interface ExplorerRecordDetail {
  resource: ExplorerResourceView;
  canonical_id: string;
  source_data: Record<string, unknown>;
  canonical: Record<string, unknown>;
  provenance: Record<string, unknown>;
  relationship_evidence: Record<string, unknown>;
  mapping: ExplorerMappingRow[];
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`/api/collector${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Collector API ${path}: HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

function query(filters: ListFilters = {}): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  const encoded = params.toString();
  return encoded ? `?${encoded}` : "";
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
  equipment: (limit = 5000, filters: Omit<ListFilters, "limit"> = {}) => get<EquipmentView[]>(`/equipment${query({ ...filters, limit })}`),
  workOrders: (limit = 5000, filters: Omit<ListFilters, "limit"> = {}) => get<WorkOrderView[]>(`/work-orders${query({ ...filters, limit })}`),
  serviceRequests: (limit = 5000, filters: Omit<ListFilters, "limit"> = {}) => get<ServiceRequestView[]>(`/service-requests${query({ ...filters, limit })}`),
  persons: (limit = 5000, filters: Omit<ListFilters, "limit"> = {}) => get<GenericView[]>(`/persons${query({ ...filters, limit })}`),
  items: (limit = 5000, filters: Omit<ListFilters, "limit"> = {}) => get<GenericView[]>(`/items${query({ ...filters, limit })}`),
  labor: (limit = 5000, filters: Omit<ListFilters, "limit"> = {}) => get<GenericView[]>(`/labor${query({ ...filters, limit })}`),
  sync: (object: string) => post<{ object_structure: string; rows_seen: number; upserted: number; skipped: number; errors: number }>(`/sync/${object}`),
  explorerResources: () => get<ExplorerCatalogView>("/data-explorer/resources"),
  explorerIntegrity: () => get<ExplorerIntegrityView>("/data-explorer/integrity"),
  explorerResource: (resource: string) => get<ExplorerResourceView>(`/data-explorer/resources/${encodeURIComponent(resource)}`),
  explorerSourceRecords: (resource: string, filters: { q?: string; offset?: number; limit?: number; sort?: string } = {}) =>
    get<{ resource: ExplorerResourceView } & ExplorerPage<ExplorerSourceRecord>>(`/data-explorer/resources/${encodeURIComponent(resource)}/records${query(filters)}`),
  explorerSourceRecord: (resource: string, canonicalId: string) => get<ExplorerRecordDetail>(`/data-explorer/resources/${encodeURIComponent(resource)}/records/${encodeURIComponent(canonicalId)}`),
  explorerMartRecords: (entity: string, filters: { q?: string; offset?: number; limit?: number; sort?: string } = {}) =>
    get<{ entity: string } & ExplorerPage<Record<string, unknown>>>(`/data-explorer/mart/${encodeURIComponent(entity)}${query(filters)}`),
  explorerMartRecord: (entity: string, canonicalId: string) => get<ExplorerRecordDetail>(`/data-explorer/mart/${encodeURIComponent(entity)}/${encodeURIComponent(canonicalId)}`),
  explorerMapping: (resource: string) => get<{ source_object: string; canonical_entity: string; contract_version: string; fields: ExplorerMappingRow[] }>(`/data-explorer/mappings/${encodeURIComponent(resource)}`),
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
