import { idText, statusLabel } from "../lib/id-copy";
import type { AssetConditionEvidence } from "@/lib/api";
function label(value: string) { return statusLabel(value); }
function date(value: string | null) { return value ? new Date(value).toLocaleString("id-ID") : idText("Unknown"); }
function valueLabel(value: AssetConditionEvidence["items"][number]["evidence"]["value"]) {
  if (value == null) return idText("Unknown");
  if (typeof value === "object") return value.name ?? idText("Unknown digital state");
  return String(value);
}
export default function ConditionEvidenceView({data}: {data: AssetConditionEvidence}) {
  return <>
      <p className="section-note">{label(data.mapping_readiness)} · {data.statuses.map(label).join(" · ")}</p>
      {data.items.length === 0 ? <p>{idText("No governed condition evidence available. Verified equipment identity and approved signals are required. Equipment condition remains unknown.")}</p> :
        <div className="asset-record-list">{data.items.map(({ evidence, freshness, projected_at, statuses }) => <article className="asset-record" key={evidence.signal_id}>
          <div><strong>{label(evidence.semantic_name)}: {valueLabel(evidence.value)} {evidence.unit ?? ""}</strong>
            <small>{statuses.map(label).join(" · ")} · {evidence.value_type}</small>
            <small>{idText("Source timestamp:")} {date(evidence.source_timestamp)}  {idText("· Collected:")} {date(evidence.collected_at)}  {idText("· Projected:")} {date(projected_at)}</small>
            <small>{idText("Collector:")} {label(freshness.collector)}  {idText("· Source:")} {label(freshness.source)}  {idText("· Projection:")} {label(freshness.projection)}</small>
            <small>{idText("Good:")}{String(evidence.quality_good ?? idText("Unknown"))}  {idText("· Questionable:")} {String(evidence.quality_questionable ?? idText("Unknown"))}  {idText("· Substituted:")} {String(evidence.quality_substituted ?? idText("Unknown"))}  {idText("· Annotated:")} {String(evidence.quality_annotated ?? idText("Unknown"))}</small>
          </div>
        </article>)}</div>}
      <p className="section-note">{idText("Latest successful collector cycle:")} {date(data.collector_last_success_at)}{idText(". Signal evidence does not determine equipment health.")}</p>
  </>;
}
