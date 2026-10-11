import { idText, statusLabel } from "../lib/id-copy";
import { TableFrame } from "./ui";
import type { IntegrationStatus } from "@/lib/api";

const label = (value: string) => statusLabel(value);
const date = (value: string | null) => value ? new Date(value).toLocaleString("id-ID") : "UNKNOWN";

export default function IntegrationStatusView({ data }: { data: IntegrationStatus }) {
  const coverage = data.coverage;
  return <div>
    <p className="section-note">{idText("Local evidence as of")} {date(data.observed_at)}{idText(". Collection, source, projection and identity are independent. No policy means UNKNOWN; evidence is not equipment health.")}</p>
    <div className="trust-population-grid">
      {([ [idText("Registered assets"), coverage.registered_assets], [idText("Verified mapping assets"), coverage.verified_mapping_assets],
        [idText("Approved signal assets"), coverage.approved_signal_assets], [idText("Projected condition assets"), coverage.projected_assets] ] as const).map(([name,count]) =>
        <article className="trust-population-card" key={name}><span>{name}</span><strong>{count ?? "UNKNOWN"}</strong></article>)}
    </div>
    <TableFrame minWidth={800} label={idText("Integration evidence matrix")}><table><thead><tr><th>{idText("Component")}</th><th>{idText("State / availability")}</th><th>{idText("Collection")}</th><th>{idText("Source")}</th><th>{idText("Projection")}</th><th>{idText("Identity / quality")}</th><th>{idText("Evidence")}</th></tr></thead>
      <tbody>{data.components.map(component => <tr key={component.component}>
        <td>{label(component.component)}</td><td>{statusLabel(component.state)}<br />{statusLabel(component.availability)}</td>
        {([component.collection_freshness, component.source_freshness, component.projection_freshness]).map((dimension,i) => <td key={i}>{statusLabel(dimension.state)}<br /><small>{date(dimension.observed_at)}</small></td>)}
        <td>{statusLabel(component.mapping_readiness)}<br />{statusLabel(component.quality)}</td>
        <td><small>{idText("Last success:")} {date(component.last_successful_activity)}</small><br />{component.degraded_reasons.map(label).join(" · ") || idText("No recorded degradation")}</td>
      </tr>)}</tbody></table></TableFrame>
    <p className="section-note">{idText("Technical PI inventory:")} {coverage.technical_registry_active ?? statusLabel("UNKNOWN")}  {idText("active /")} {coverage.technical_registry_total ?? statusLabel("UNKNOWN")} total, {coverage.technical_snapshots ?? statusLabel("UNKNOWN")}  {idText("stored snapshots. Technical attributes are not governed Asset signals.")}</p>
  </div>;
}
