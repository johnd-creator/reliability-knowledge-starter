import type { DecisionOverviewView, EvidenceValue } from "./api";
import { factualMetric } from "./overview";

export const reportPeriods = [7, 30, 90] as const;
export type ReportPeriod = (typeof reportPeriods)[number];
export const reportCandidates = [
  { id: "coverage", definition: "NADI-RPT-COVERAGE-CANDIDATE", version: "0.1", name: "Data Coverage Report", title: "Cakupan Data", description: "Populasi Registry, konteks teknis dan batas bukti domain.", contract: "DataTrustView", api: "/v1/reliability/data-trust" },
  { id: "maintenance", definition: "NADI-RPT-MAINTENANCE-CANDIDATE", version: "0.1", name: "Maintenance Activity Report", title: "Aktivitas Pemeliharaan", description: "Aktivitas aset terdaftar dengan periode API 7, 30 atau 90 hari.", contract: "DecisionOverviewView", api: "/v1/reliability/decision-overview" },
] as const;
export type ReportCandidate = (typeof reportCandidates)[number];
export function reportMetric(value: EvidenceValue | null | undefined): string {
  if (value?.value != null && value.value < 0) return "UNKNOWN";
  return factualMetric(value);
}
export function chartCount(value: EvidenceValue | null | undefined): number | null {
  return value && ["VERIFIED", "DERIVED_SAFE"].includes(value.evidence_class) && typeof value.value === "number" && Number.isFinite(value.value) && value.value >= 0 ? value.value : null;
}
export function selectedMaintenance(data: DecisionOverviewView, days: ReportPeriod) {
  return { activity: data.summary?.[`maintenance_activity_${days}d`], assets: data.summary?.[`assets_active_${days}d`] };
}
export class ReportPeriodMismatch extends Error {}
export function requireReportPeriod(data: DecisionOverviewView, requested: ReportPeriod): DecisionOverviewView {
  if (!reportPeriods.includes(requested) || data?.window_days !== requested) throw new ReportPeriodMismatch();
  return data;
}
