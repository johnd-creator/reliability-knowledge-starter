"use client";

import {useEffect, useState} from "react";
import {PageHeader, SectionCard, StatusBadge, EmptyState, Pagination} from "./ui";
import {CaseDocument, CaseEvent, CaseStatus, Priority, demoTransition, evidenceValue} from "../lib/engineering";
import synthetic from "../fixtures/engineering-workspace.json";

const initial = synthetic.cases as CaseDocument[];
const statuses: CaseStatus[] = ["DRAFT","IN_REVIEW","APPROVED","REJECTED"];
function timestamp(value: string | null) { return value ? new Date(value).toLocaleString("id-ID") : "Unknown"; }
function quality(value: boolean | null) { return value === null ? "Unknown" : String(value); }

export default function EngineeringWorkspace({initialCaseId}: {initialCaseId?:string}) {
  const [cases,setCases]=useState<CaseDocument[]>(initial);
  const [history,setHistory]=useState<CaseEvent[]>(synthetic.history as CaseEvent[]);
  const [selected,setSelected]=useState(initialCaseId ?? initial[0].case_id);
  const [filter,setFilter]=useState<string>("");
  const [search,setSearch]=useState("");const [offset,setOffset]=useState(0);
  const [actor,setActor]=useState("engineer-fixture");
  const [title,setTitle]=useState("");const [problem,setProblem]=useState("");
  const [priority,setPriority]=useState<Priority>("NORMAL");const [hypothesis,setHypothesis]=useState("");
  const [note,setNote]=useState("");const [rationale,setRationale]=useState("");
  const [dirty,setDirty]=useState(false);const [feedback,setFeedback]=useState("");
  const [loadedRevision,setLoadedRevision]=useState(1);
  const current=cases.find(item=>item.case_id===selected);
  const hasUnsaved=dirty||Boolean(note.trim())||Boolean(rationale.trim());
  useEffect(()=>{
    if (current) {setTitle(current.title);setProblem(current.problem_statement);setPriority(current.priority);
      setHypothesis(current.investigation.hypotheses.join("\n"));setLoadedRevision(current.revision);}
    setDirty(false);setNote("");setRationale("");
  },[selected]); // Keep the editor revision pinned; changes require an explicit reload.
  useEffect(()=>{
    function warn(event: BeforeUnloadEvent) { if(hasUnsaved) {event.preventDefault();event.returnValue="";} }
    window.addEventListener("beforeunload",warn);return ()=>window.removeEventListener("beforeunload",warn);
  },[hasUnsaved]);
  const filtered=cases.filter(item=>(!filter || item.status===filter) && `${item.title} ${item.canonical_asset_id}`.toLowerCase().includes(search.toLowerCase()));
  const page=filtered.slice(offset,offset+3);
  const reviewer=actor==="reviewer-fixture";
  const editable=current?.status==="DRAFT" && !reviewer;
  function choose(id:string) {if(hasUnsaved&&!window.confirm("Discard unsaved synthetic changes?"))return;setSelected(id);setFeedback("");}
  function change(action: Parameters<typeof demoTransition>[3]) {
    if(!current)return;
    if(action!=="NOTE" && note.trim()) {setFeedback("Save or clear the unsaved note first.");return;}
    try {
      const data=action==="SAVE"?{title,problem_statement:problem,priority,
        investigation:{...current.investigation,hypotheses:hypothesis.split("\n").filter(Boolean)}}:
        action==="LINK"?{evidence:[synthetic.available_evidence as CaseDocument["evidence"][number]]}:undefined;
      const result=demoTransition(current,loadedRevision,actor,action,new Date().toISOString(),data,action==="NOTE"?note:rationale);
      setCases(items=>items.map(item=>item.case_id===current.case_id?result.document:item));
      setHistory(items=>[...items,result.event]);setLoadedRevision(result.document.revision);setDirty(false);
      setNote("");setRationale("");setFeedback(`Synthetic ${action.toLowerCase()} saved · revision ${result.document.revision}. No server write.`);
    } catch(error) {setFeedback(error instanceof Error?error.message:"DEMO_ERROR");}
  }
  function createDraft() {
    if(hasUnsaved&&!window.confirm("Discard unsaved synthetic changes?"))return;
    const now=new Date().toISOString();const next:CaseDocument={...initial[0],case_id:`case:synthetic-${cases.length+1}`,
      title:"New synthetic investigation",problem_statement:"Describe the investigation question.",status:"DRAFT",revision:1,
      created_at:now,updated_at:now,notes:[],evidence:[],review:null,investigation:{observed_symptoms:[],operating_context:"",hypotheses:[],observations:[],open_questions:[],proposed_next_checks:[]}};
    setCases(items=>[next,...items]);setHistory(items=>[...items,{case_id:next.case_id,revision:1,previous_revision:0,actor,action:"CREATE",occurred_at:now,changed_fields:["title","problem_statement"],reason:null}]);
    setSelected(next.case_id);setFilter("");setOffset(0);setFeedback("Local synthetic draft created. Reload discards demo changes.");
  }
  return <>
    <PageHeader eyebrow="PHASE 2 / DEVELOPMENT ONLY" title="Engineering Workspace" description="Investigasi engineer dengan fakta terpisah dari hipotesis dan keputusan manusia." actions={<button className="engineering-primary" disabled={reviewer} onClick={createDraft}>New synthetic case</button>}/>
    <div className="scope-banner engineering-demo" role="note"><strong>SYNTHETIC LOCAL DEMO</strong><span>No operational records, authenticated users or backend writes. Changes exist only in browser memory.</span></div>
    <div className="engineering-toolbar">
      <label>Search case / asset<input value={search} onChange={event=>{setSearch(event.target.value);setOffset(0);}} placeholder="Search synthetic cases"/></label>
      <label>Status<select value={filter} onChange={event=>{setFilter(event.target.value);setOffset(0);}}><option value="">All statuses</option>{statuses.map(status=><option key={status}>{status}</option>)}</select></label>
      <label>Simulated actor — not authentication<select value={actor} onChange={event=>setActor(event.target.value)}><option value="engineer-fixture">Synthetic author</option><option value="reviewer-fixture">Synthetic independent reviewer</option></select></label>
    </div>
    <div className="engineering-grid">
      <SectionCard><h2>Investigation cases</h2>{page.length===0?<EmptyState title="No matching synthetic cases."/>:<ul className="engineering-cases">{page.map(item=><li key={item.case_id}><button className={selected===item.case_id?"engineering-case selected":"engineering-case"} onClick={()=>choose(item.case_id)} aria-pressed={selected===item.case_id}><strong>{item.title}</strong><code>{item.canonical_asset_id}</code><div><StatusBadge value={item.status} mode="raw-neutral"/><span>{item.priority} · r{item.revision}</span></div><small>{item.assigned_engineer??item.created_by} · {timestamp(item.updated_at)}</small></button></li>)}</ul>}
        <Pagination meta={{offset,limit:3,total:filtered.length,has_more:offset+3<filtered.length}} onChange={setOffset}/>
      </SectionCard>
      <div>{!current?<EmptyState title="Select an investigation case."/>:<>
        <SectionCard><div className="engineering-heading"><div><p className="eyebrow">HUMAN ENGINEERING RECORD</p><h2>{current.title}</h2></div><StatusBadge value={current.status} mode="raw-neutral"/></div>
          <code className="engineering-asset">{current.canonical_asset_id}</code>
          <p className="engineering-meta">Revision {current.revision} · created by {current.created_by} · {timestamp(current.created_at)}</p>
          <form onSubmit={event=>{event.preventDefault();change("SAVE");}} className="engineering-editor">
            <label>Case title<input maxLength={200} required disabled={!editable} value={title} onChange={event=>{setTitle(event.target.value);setDirty(true);}}/></label>
            <label>Problem statement<textarea maxLength={12000} required rows={4} disabled={!editable} value={problem} onChange={event=>{setProblem(event.target.value);setDirty(true);}}/></label>
            <label>Human priority<select disabled={!editable} value={priority} onChange={event=>{setPriority(event.target.value as Priority);setDirty(true);}}>{["LOW","NORMAL","HIGH"].map(value=><option key={value}>{value}</option>)}</select></label>
            <label>Hypotheses — human judgment, not confirmed facts<textarea maxLength={4000} rows={3} disabled={!editable} value={hypothesis} onChange={event=>{setHypothesis(event.target.value);setDirty(true);}}/></label>
            <div className="engineering-actions"><button className="engineering-primary" disabled={!editable||!dirty} type="submit">Save synthetic draft</button><button type="button" disabled={!editable||dirty} onClick={()=>change("SUBMIT")}>Submit for synthetic review</button>{dirty&&<span>Unsaved changes</span>}</div>
          </form>
          <details className="engineering-context"><summary>Human observations and investigation context</summary><dl><dt>Operating context</dt><dd>{current.investigation.operating_context||"Not recorded"}</dd><dt>Observed symptoms</dt><dd>{current.investigation.observed_symptoms.join("; ")||"Not recorded"}</dd><dt>Engineer observations</dt><dd>{current.investigation.observations.join("; ")||"Not recorded"}</dd><dt>Open questions</dt><dd>{current.investigation.open_questions.join("; ")||"Not recorded"}</dd><dt>Proposed next checks</dt><dd>{current.investigation.proposed_next_checks.join("; ")||"Not recorded"}</dd></dl></details>
          <div role="status" aria-live="polite" className="engineering-feedback">{feedback}</div>
        </SectionCard>
        <SectionCard><p className="eyebrow">CANONICAL FACTS / FROZEN SNAPSHOTS</p><h2>Evidence panel</h2><p>Good describes signal quality. Equipment condition is not inferred. UNKNOWN freshness remains unknown.</p>
          {current.evidence.length===0?<EmptyState title="No accepted evidence linked." detail="A hypothesis does not establish evidence."/>:current.evidence.map(reference=><article className="engineering-evidence" key={reference.reference_id}><h3>{reference.snapshot?.label??reference.kind}</h3><div className="engineering-evidence-value">{evidenceValue(reference)} <small>{reference.unit??"Unit unknown"}</small></div><dl><dt>Source / mode</dt><dd>{reference.source} / {reference.mode}</dd><dt>Source timestamp</dt><dd>{timestamp(reference.source_timestamp)}</dd><dt>Observed / linked</dt><dd>{timestamp(reference.observed_at)} / {timestamp(reference.linked_at)}</dd><dt>Freshness / policy</dt><dd>{reference.freshness} / {reference.freshness_policy_ref??"UNSET"}</dd><dt>Mapping / signal</dt><dd>{reference.identity_status} / {reference.signal_approval}</dd><dt>Quality</dt><dd>Good {quality(reference.quality_good)} · Questionable {quality(reference.quality_questionable)} · Substituted {quality(reference.quality_substituted)} · Annotated {quality(reference.quality_annotated)}</dd><dt>Record / version</dt><dd><code>{reference.record_id} / {reference.stable_version}</code></dd><dt>Linked by</dt><dd>{reference.linked_by}</dd></dl></article>)}
          <button disabled={!editable||dirty} onClick={()=>change("LINK")}>Link bounded synthetic condition snapshot</button>
        </SectionCard>
        <SectionCard><h2>Investigation notes</h2>{current.notes.length===0?<p>No engineer notes.</p>:current.notes.map(item=><article className="engineering-note" key={item.note_id}><small>{item.actor} · {timestamp(item.created_at)}</small><p>{item.text}</p></article>)}<label>New note — plain text<textarea maxLength={12000} rows={3} value={note} disabled={!editable} onChange={event=>setNote(event.target.value)}/></label><button disabled={!editable||!note.trim()||dirty} onClick={()=>change("NOTE")}>Add synthetic note</button></SectionCard>
        <SectionCard><h2>Review decision</h2><p>An independent reviewer decides. Field completeness never approves a case.</p>{current.review&&<div className="engineering-note"><strong>{current.review.decision} · {current.review.reviewer}</strong><p>{current.review.rationale}</p></div>}<label>Review / revision rationale<textarea maxLength={6000} value={rationale} onChange={event=>setRationale(event.target.value)} rows={3}/></label><div className="engineering-actions"><button disabled={!reviewer||current.status!=="IN_REVIEW"||!rationale.trim()} onClick={()=>change("APPROVED")}>Approve synthetic case</button><button disabled={!reviewer||current.status!=="IN_REVIEW"||!rationale.trim()} onClick={()=>change("REJECTED")}>Reject synthetic case</button><button disabled={reviewer||current.status!=="REJECTED"||!rationale.trim()} onClick={()=>change("REVISE")}>Revise rejected case</button><button disabled={!reviewer||current.status!=="APPROVED"||!rationale.trim()} onClick={()=>change("REOPEN")}>Reopen approved case</button></div></SectionCard>
        <SectionCard><h2>Revision timeline</h2><ol className="engineering-timeline">{history.filter(item=>item.case_id===current.case_id).map(item=><li key={item.revision}><strong>r{item.revision} · {item.action}</strong><span>{item.actor} · {timestamp(item.occurred_at)}</span><small>Previous r{item.previous_revision} · {item.changed_fields.join(", ")}</small>{item.reason&&<p>{item.reason}</p>}</li>)}</ol></SectionCard>
      </>}</div>
    </div>
  </>;
}
