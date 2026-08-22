"use client";

/** Typed clients for the legacy Cockpit store and canonical Reliability Mart. */

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

export interface WorkOrderPage { items: WorkOrderView[]; total: number; offset: number; limit: number; has_more: boolean; }
export interface ReliabilityKpiView { id: string; equipment_id: string | null; metric: string | null; value: number | null; unit: string | null; period_start: string | null; period_end: string | null; }
export interface PageMeta { total: number; offset: number; limit: number; has_more: boolean; }
export interface Page<T> { items: T[]; meta: PageMeta; }

export interface AssetView {
  canonical_id: string; contract_version: string; source_asset_number: string | null; description: string | null; status: string | null;
  location_ref: string | null; parent_asset_ref: string | null; site_code: string; organization_code: string; asset_type: string | null;
  plant: string | null; unit: string | null; source_updated_at: string | null;
}
export interface MaintenanceEventView {
  canonical_id: string; contract_version: string; id: string; equipment_id: string; work_order_id: string | null; event_type: string | null;
  status: string | null; actual_start: string | null; actual_finish: string | null; duration_hours: number | null; labor_hours: number | null;
  downtime_hours: number | null; failure_code: string | null; source_changed_at: string | null; site_code: string; organization_code: string;
}
export interface FmeaView {
  canonical_id: string; contract_version: string; source_record_id: string | null; source_number: string | null; revision: string | null;
  lifecycle_status: string | null; description: string | null; asset_ref: string | null; failure_code_ref: string | null;
  site_code: string; organization_code: string; source_updated_at: string | null; status_changed_at: string | null;
}
export interface RcfaView {
  canonical_id: string; contract_version: string; source_record_id: string | null; source_number: string | null; revision: string | null;
  lifecycle_status: string | null; category: string | null; asset_ref: string | null; location_ref: string | null; workorder_ref: string | null;
  failure_event_ref: string | null; site_code: string; organization_code: string; source_created_at: string | null; requested_at: string | null;
  relationship_status: "UNRESOLVED";
}
export interface AssetHealthView {
  canonical_id: string; contract_version: string; source_record_id: string | null; revision: string | null; lifecycle_status: string | null;
  description: string | null; function_description: string | null; asset_ref: string | null; site_code: string; organization_code: string;
  source_created_at: string | null; source_updated_at: string | null; status_changed_at: string | null;
  source_asset_number: string | null; asset_description: string | null; assessment_record_date: string | null; assessment_age_days: number | null;
}
export interface OverhaulView {
  canonical_id: string; contract_version: string; source_record_id: string | null; source_number: string | null; lifecycle_status: string | null;
  workorder_ref: string | null; asset_ref: string | null; site_code: string; organization_code: string; planned_start_at: string | null;
  planned_finish_at: string | null; actual_start_at: string | null; actual_finish_at: string | null; progress: unknown | null;
  unresolved_attributes_present: boolean;
}
export interface TimelineView {
  event_id: string;
  event_type: "MAINTENANCE" | "FMEA" | "ASSET_HEALTH" | "OVERHAUL";
  event_at: string | null;
  summary: string | null;
  status: string | null;
  canonical_ref: string;
}
export interface ContextView {
  asset: AssetView;
  maintenance: MaintenanceEventView[];
  fmea: FmeaView[];
  health: AssetHealthView[];
  overhauls: OverhaulView[];
  rcfa_relationship_status: "UNRESOLVED";
  relationship_health: IntegrityView;
}
export interface IntegrityView {
  asset_refs_total: number; asset_refs_resolved: number; asset_refs_unresolved: number;
  workorder_refs_total: number; workorder_refs_resolved: number; workorder_refs_unresolved: number;
  technical_asset_context_total: number; registered_assets_total: number; registered_assets_resolved: number;
  registered_assets_unresolved: number; maintenance_registered_total: number;
}
export interface RegistryView { registered_asset_count: number; snapshot_sha256: string | null; snapshot_row_count: number | null; snapshot_imported_at: string | null; source: string; }

export type EvidenceClass = "VERIFIED" | "DERIVED_SAFE" | "BUSINESS_SEMANTICS_REQUIRED" | "DATA_NOT_AVAILABLE" | "DEFERRED";
export interface EvidenceValue { value: number; evidence_class: EvidenceClass; }
export interface AssetHealthOverviewView {
  scope: { site_code: "BSR"; organization_code: "IP"; registry_scope: string; population: "CONTROLLED_MART_POPULATION"; interpretation: "ASSESSMENT_RECORDS_NOT_HEALTH_SCORE" };
  summary: {
    assessment_records: number; records_with_asset_ref: number; records_without_asset_ref: number; asset_master_resolved: number;
    registry_resolved: number; technical_non_registry_records: number; unresolved_asset_refs: number; registered_assets_represented: number;
    assets_with_multiple_records: number; maximum_records_per_asset: number;
  };
  status_distribution: { value: string; count: EvidenceValue }[];
  record_recency: { oldest_record_at: string | null; latest_record_at: string | null; as_of: string; latest_assessment_age_days: number | null; date_basis: string };
  evidence: {
    assessment_records: EvidenceClass; registered_assets_represented: EvidenceClass; assets_with_multiple_records: EvidenceClass;
    latest_assessment_record: EvidenceClass; assessment_age: EvidenceClass; lifecycle_status: EvidenceClass; health_score: EvidenceClass;
    wellness_score: EvidenceClass; condition_classification: EvidenceClass;
  };
}
export interface DecisionOverviewView {
  scope: { site_code: "BSR"; organization_code: "IP"; registry_scope: string; maintenance_source: string; date_basis: string };
  data_maturity: { asset_maintenance: string; controlled_domains: string; rcfa_relationship: string; technical_context: string };
  window_days: 7 | 30 | 90;
  window_start: string;
  as_of: string;
  summary: {
    registered_assets: EvidenceValue;
    maintenance_activity_7d: EvidenceValue;
    maintenance_activity_30d: EvidenceValue;
    maintenance_activity_90d: EvidenceValue;
    assets_active_7d: EvidenceValue;
    assets_active_30d: EvidenceValue;
    assets_active_90d: EvidenceValue;
  };
  maintenance_activity: { period_start: string; period_end: string; event_count: EvidenceValue }[];
  status_distribution: { value: string; count: EvidenceValue }[];
  work_type_distribution: { value: string; count: EvidenceValue }[];
  activity_concentration: { asset_ref: string; source_asset_number: string; description: string | null; event_count: EvidenceValue; latest_activity: string | null }[];
  record_availability: {
    fmea_records: EvidenceValue;
    fmea_assets_represented: EvidenceValue;
    asset_health_records: EvidenceValue;
    asset_health_assets_represented: EvidenceValue;
    rcfa_records: EvidenceValue;
    overhaul_records: EvidenceValue;
  };
  integrity: IntegrityView;
}

export interface MaintenanceInvestigationView {
  scope: { site_code: "BSR"; organization_code: "IP"; registry_scope: string; date_basis: string; interpretation: "ACTIVITY_NOT_FAILURE" };
  window: { days: 30 | 90 | 180; start: string; as_of: string };
  summary: {
    registered_assets: number;
    maintenance_events: number;
    assets_with_activity: number;
    assets_with_2plus_events: number;
    assets_with_3plus_events: number;
    repeat_activity_events: number;
  };
  assets: {
    asset_ref: string;
    source_asset_number: string;
    description: string | null;
    event_count: number;
    repeat_activity_events: number;
    latest_activity: string | null;
    previous_activity: string | null;
    latest_gap_days: number | null;
    minimum_gap_days: number | null;
    latest_work_type: string | null;
    dominant_work_type: string | null;
  }[];
  meta: PageMeta;
  evidence: {
    repeat_activity: "DERIVED_SAFE";
    work_type_source: string;
    activity_date: string;
    repeat_failure: "BUSINESS_SEMANTICS_REQUIRED";
  };
}

export interface AssetFilters { status?: string; unit?: string; asset_type?: string; offset?: number; limit?: number; sort?: "updated_desc" | "updated_asc" | "status"; }
export interface MaintenanceFilters { asset_ref?: string; work_order_id?: string; status?: string; event_type?: string; date_from?: string; date_to?: string; offset?: number; limit?: number; sort?: "date_desc" | "date_asc" | "status"; }
export interface FmeaFilters { asset_ref?: string; lifecycle_status?: string; source_number?: string; updated_from?: string; updated_to?: string; offset?: number; limit?: number; sort?: "updated_desc" | "updated_asc" | "status"; }
export interface RcfaFilters { lifecycle_status?: string; category?: string; source_number?: string; created_from?: string; created_to?: string; offset?: number; limit?: number; sort?: "created_desc" | "created_asc" | "status"; }
export interface HealthFilters { asset_ref?: string; asset_number?: string; description?: string; lifecycle_status?: string; updated_from?: string; updated_to?: string; offset?: number; limit?: number; sort?: "updated_desc" | "updated_asc" | "status"; }
export interface OverhaulFilters { asset_ref?: string; workorder_ref?: string; lifecycle_status?: string; planned_from?: string; planned_to?: string; actual_from?: string; actual_to?: string; offset?: number; limit?: number; sort?: "date_desc" | "date_asc" | "status"; }
export interface AssetDetailPageFilters { offset?: number; limit?: number; }

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) { super(message); this.name = "ApiError"; }
}

function query(filters: object): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if ((typeof value === "string" && value !== "") || typeof value === "number") params.set(key, String(value));
  }
  const encoded = params.toString();
  return encoded ? `?${encoded}` : "";
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`/api/cockpit${path}`, { cache: "no-store" });
  if (!response.ok) {
    if (response.status === 503) throw new ApiError("Reliability Mart unavailable", response.status);
    throw new ApiError(`Reliability API ${path}: HTTP ${response.status}`, response.status);
  }
  return response.json() as Promise<T>;
}

export const KPI_METRICS = ["MTBF", "MTTR", "AVAILABILITY", "PM_COMPLIANCE"] as const;
export const cockpitApi = {
  listEquipment: (limit = 200) => get<EquipmentView[]>(`/equipment?limit=${limit}`),
  getEquipment: (equipmentId: string) => get<EquipmentView>(`/equipment/${encodeURIComponent(equipmentId)}`),
  listWorkOrders: (equipmentId?: string, offset = 0, limit = 50, status?: string) => get<WorkOrderPage>(`/work-orders${query({ equipment_id: equipmentId, status, offset, limit })}`),
  listWorkOrderStatuses: () => get<string[]>("/work-orders/statuses"),
  getKpi: (equipmentId: string, metric: string) => get<ReliabilityKpiView>(`/kpis/${encodeURIComponent(equipmentId)}/${encodeURIComponent(metric)}`),
  health: () => get<{ status: string }>("/health"),
};

export const reliabilityApi = {
  decisionOverview: (windowDays: 7 | 30 | 90 = 30) => get<DecisionOverviewView>(`/v1/reliability/decision-overview?window_days=${windowDays}`),
  assetHealthOverview: () => get<AssetHealthOverviewView>("/v1/reliability/asset-health/overview"),
  maintenanceInvestigation: (windowDays: 30 | 90 | 180 = 90, minEvents: 2 | 3 | 5 = 2, offset = 0, limit = 25, sort: "event_count_desc" | "latest_activity_desc" | "latest_gap_asc" = "event_count_desc") => get<MaintenanceInvestigationView>(`/v1/reliability/maintenance-investigation${query({ window_days: windowDays, min_events: minEvents, offset, limit, sort })}`),
  assets: (filters: AssetFilters = {}) => get<Page<AssetView>>(`/v1/reliability/assets${query(filters)}`),
  registry: () => get<RegistryView>("/v1/reliability/registry"),
  asset: (canonicalId: string) => get<AssetView>(`/v1/reliability/assets/${encodeURIComponent(canonicalId)}`),
  assetContext: (canonicalId: string) => get<ContextView>(`/v1/reliability/assets/${encodeURIComponent(canonicalId)}/context`),
  assetTimeline: (canonicalId: string, filters: AssetDetailPageFilters = {}) => get<Page<TimelineView>>(`/v1/reliability/assets/${encodeURIComponent(canonicalId)}/timeline${query(filters)}`),
  assetFmea: (canonicalId: string, filters: AssetDetailPageFilters = {}) => get<Page<FmeaView>>(`/v1/reliability/assets/${encodeURIComponent(canonicalId)}/fmea${query(filters)}`),
  assetHealthAssessments: (canonicalId: string, filters: AssetDetailPageFilters = {}) => get<Page<AssetHealthView>>(`/v1/reliability/assets/${encodeURIComponent(canonicalId)}/health-assessments${query(filters)}`),
  latestAssetHealth: (canonicalId: string) => get<AssetHealthView>(`/v1/reliability/assets/${encodeURIComponent(canonicalId)}/health/latest`),
  maintenance: (filters: MaintenanceFilters = {}) => get<Page<MaintenanceEventView>>(`/v1/reliability/maintenance-events${query(filters)}`),
  fmea: (filters: FmeaFilters = {}) => get<Page<FmeaView>>(`/v1/reliability/fmea${query(filters)}`),
  rcfa: (filters: RcfaFilters = {}) => get<Page<RcfaView>>(`/v1/reliability/rcfa${query(filters)}`),
  assetHealth: (filters: HealthFilters = {}) => get<Page<AssetHealthView>>(`/v1/reliability/asset-health${query(filters)}`),
  overhauls: (filters: OverhaulFilters = {}) => get<Page<OverhaulView>>(`/v1/reliability/overhauls${query(filters)}`),
  integrity: () => get<IntegrityView>("/v1/reliability/integrity"),
};
