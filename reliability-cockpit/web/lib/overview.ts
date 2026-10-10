import type { EvidenceValue, IntegrityView } from "./api";
import { formatDate, formatNumber } from "./format";

export function factualMetric(metric: EvidenceValue | null | undefined): string {
  if (!metric || metric.value == null || !Number.isFinite(metric.value)) return "UNKNOWN";
  if (metric.evidence_class === "BUSINESS_SEMANTICS_REQUIRED") return "NOT ASSESSED";
  if (metric.evidence_class === "DEFERRED") return "UNAVAILABLE";
  if (!["VERIFIED", "DERIVED_SAFE"].includes(metric.evidence_class)) return "UNKNOWN";
  return formatNumber(metric.value);
}
export function overviewDate(value: string | null | undefined): string {
  return value && Number.isFinite(Date.parse(value)) ? formatDate(value) : "UNKNOWN";
}
export function attentionItems(integrity: Pick<IntegrityView, "registered_assets_unresolved" | "asset_refs_unresolved" | "workorder_refs_unresolved">) {
  return [
    { label: "Registry references", count: integrity.registered_assets_unresolved, href: "/data-quality" },
    { label: "Asset references", count: integrity.asset_refs_unresolved, href: "/data-quality" },
    { label: "Work Order references", count: integrity.workorder_refs_unresolved, href: "/data-quality" },
  ];
}
