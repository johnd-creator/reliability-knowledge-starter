"use client";
import Link from "next/link";
import type {Inspection} from "../lib/product-records";
import {originalValue,qaRecordLink} from "../lib/product-records";
import {SectionCard,StatusBadge,TableFrame,EmptyState} from "./ui";
export default function InspectionDetail({row}:{row:Inspection}) {
 return <SectionCard className="product-record-detail"><div className="section-heading"><h2>Inspection {row.record_id}</h2><StatusBadge mode="raw-neutral" value={row.status}/></div>
  <p className="section-note">SYNTHETIC QA · {row.canonical_asset_id} · Revision {row.revision} · {row.method} / {row.method_version}</p>
  <dl className="asset-facts"><div><dt>Inspected at (original timestamp)</dt><dd>{row.inspected_at??"UNKNOWN"}</dd></div><div><dt>Operating context</dt><dd>{row.operating_context??"UNKNOWN"}</dd></div><div><dt>Inspector reference</dt><dd>{row.inspector_ref}</dd></div><div><dt>Field approval / assessment</dt><dd>{row.field_approval} / {row.assessment}</dd></div></dl>
  <h3>Original measurements</h3>{row.measurements.length?<TableFrame minWidth={860} label="Original episodic measurement values"><table><thead><tr><th>Quantity</th><th>Original value</th><th>Unit</th><th>Actual measured at</th><th>Point</th><th>Quality / provenance</th></tr></thead><tbody>{row.measurements.map((m,i)=><tr key={i}><td>{m.quantity}</td><td>{originalValue(m.value)}</td><td>{m.unit??"UNKNOWN"}</td><td>{m.measured_at??"UNKNOWN"}</td><td>{m.point_ref??"UNKNOWN"}</td><td>{m.quality}<small className="table-subtext">{m.provenance}</small></td></tr>)}</tbody></table></TableFrame>:<EmptyState title="No measurements recorded."/>}
  <div className="product-context-grid"><div><h3>Observations</h3>{row.observations.length?<ul>{row.observations.map((x,i)=><li key={i}>{x}</li>)}</ul>:<p>UNKNOWN — no observation recorded.</p>}</div><div><h3>Engineering interpretation</h3>{row.interpretations.length?<ul>{row.interpretations.map((x,i)=><li key={i}>{x}</li>)}</ul>:<p>NOT ASSESSED — no interpretation recorded.</p>}</div><div><h3>Independent review</h3>{row.review?<p>{row.review.decision} · {row.review.reviewer} · {row.review.decided_at}<br/>{row.review.rationale}</p>:<p>Review decision NOT AVAILABLE.</p>}</div></div>
  <h3>Evidence / attachment references</h3>{row.attachments.length?<ul>{row.attachments.map(a=><li key={a.attachment_ref}>{a.filename} · {a.content_type} · {a.size_bytes} bytes · {a.status}<small className="table-subtext">{a.attachment_ref} · SHA256 {a.sha256??"UNKNOWN"}</small></li>)}</ul>:<p>No attachment metadata. Upload/download custody is not activated.</p>}
  <p className="section-note">Attachment references are metadata only; no arbitrary URL is opened.</p>
  <div className="page-actions"><Link className="button secondary" href={qaRecordLink("inspections",row.record_id)}>Authorized inspection workflow →</Link>{row.case_refs.map(id=><Link key={id} className="text-link" href={qaRecordLink("cases",id)}>Case {id} →</Link>)}</div>
 </SectionCard>;
}
