import type { AssetConditionEvidence } from "@/lib/api";
function label(value: string) { return value.toLowerCase().replaceAll("_", " "); }
function date(value: string | null) { return value ? new Date(value).toLocaleString() : "Unknown"; }
function valueLabel(value: AssetConditionEvidence["items"][number]["evidence"]["value"]) {
  if (value == null) return "Unknown";
  if (typeof value === "object") return value.name ?? "Unknown digital state";
  return String(value);
}
export default function ConditionEvidenceView({data}: {data: AssetConditionEvidence}) {
  return <>
      <p className="section-note">{label(data.mapping_readiness)} · {data.statuses.map(label).join(" · ")}</p>
      {data.items.length === 0 ? <p>No governed condition evidence available. Verified equipment identity and approved signals are required. Equipment condition remains unknown.</p> :
        <div className="asset-record-list">{data.items.map(({ evidence, freshness, projected_at, statuses }) => <article className="asset-record" key={evidence.signal_id}>
          <div><strong>{label(evidence.semantic_name)}: {valueLabel(evidence.value)} {evidence.unit ?? ""}</strong>
            <small>{statuses.map(label).join(" · ")} · {evidence.value_type}</small>
            <small>Source timestamp: {date(evidence.source_timestamp)} · Collected: {date(evidence.collected_at)} · Projected: {date(projected_at)}</small>
            <small>Collector: {label(freshness.collector)} · Source: {label(freshness.source)} · Projection: {label(freshness.projection)}</small>
            <small>Good: {String(evidence.quality_good ?? "unknown")} · Questionable: {String(evidence.quality_questionable ?? "unknown")} · Substituted: {String(evidence.quality_substituted ?? "unknown")} · Annotated: {String(evidence.quality_annotated ?? "unknown")}</small>
          </div>
        </article>)}</div>}
      <p className="section-note">Latest successful collector cycle: {date(data.collector_last_success_at)}. Signal evidence does not determine equipment health.</p>
  </>;
}
