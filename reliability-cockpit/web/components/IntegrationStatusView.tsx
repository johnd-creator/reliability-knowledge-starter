import type { IntegrationStatus } from "@/lib/api";

const label = (value: string) => value.replaceAll("_", " ");
const date = (value: string | null) => value ? new Date(value).toLocaleString() : "UNKNOWN";

export default function IntegrationStatusView({ data }: { data: IntegrationStatus }) {
  const coverage = data.coverage;
  return <div>
    <p className="section-note">Local evidence as of {date(data.observed_at)}. Collection, source, projection and identity are independent. No policy means UNKNOWN; evidence is not equipment health.</p>
    <div className="trust-population-grid">
      {([ ["Registered assets", coverage.registered_assets], ["Verified mapping assets", coverage.verified_mapping_assets],
        ["Approved signal assets", coverage.approved_signal_assets], ["Projected condition assets", coverage.projected_assets] ] as const).map(([name,count]) =>
        <article className="trust-population-card" key={name}><span>{name}</span><strong>{count ?? "UNKNOWN"}</strong></article>)}
    </div>
    <div className="table-scroll"><table><thead><tr><th>Component</th><th>State / availability</th><th>Collection</th><th>Source</th><th>Projection</th><th>Identity / quality</th><th>Evidence</th></tr></thead>
      <tbody>{data.components.map(component => <tr key={component.component}>
        <td>{label(component.component)}</td><td>{component.state}<br />{component.availability}</td>
        {([component.collection_freshness, component.source_freshness, component.projection_freshness]).map((dimension,i) => <td key={i}>{dimension.state}<br /><small>{date(dimension.observed_at)}</small></td>)}
        <td>{component.mapping_readiness}<br />{component.quality}</td>
        <td><small>Last success: {date(component.last_successful_activity)}</small><br />{component.degraded_reasons.map(label).join(" · ") || "No recorded degradation"}</td>
      </tr>)}</tbody></table></div>
    <p className="section-note">Technical PI inventory: {coverage.technical_registry_active ?? "UNKNOWN"} active / {coverage.technical_registry_total ?? "UNKNOWN"} total, {coverage.technical_snapshots ?? "UNKNOWN"} stored snapshots. Technical attributes are not governed Asset signals.</p>
  </div>;
}
