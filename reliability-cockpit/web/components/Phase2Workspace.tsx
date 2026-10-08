"use client";
import Link from "next/link";
import {useEffect,useState} from "react";
import {PageHeader,SectionCard,StatusBadge,EmptyState} from "./ui";
import {methods,enteredValue,localRecord,submitLocal,type LocalInspection,type Method} from "../lib/manual-pdm";
import {parseHypotheses} from "../lib/engineering";
const asset="asset:SYNTHETIC:FEEDER-A";
const screens=["PdM Center","Asset Health 360","Recommendations","Action Board"] as const;
type Screen=typeof screens[number];
type Proposal={id:string;action:string;rationale:string;case_ref:string;target:string|null;status:"DRAFT";scope:"NOT_A_MAINTENANCE_AUTHORIZATION"};
export default function Phase2Workspace(){
  const [screen,setScreen]=useState<Screen>("PdM Center");const [records,setRecords]=useState<LocalInspection[]>([]);
  const [proposals,setProposals]=useState<Proposal[]>([]);const [method,setMethod]=useState<Method>("VIBRATION");
  const [quantity,setQuantity]=useState("");const [value,setValue]=useState("");const [unit,setUnit]=useState("");
  const [kind,setKind]=useState<"NUMERIC"|"TEXT"|"BOOLEAN"|"UNKNOWN">("UNKNOWN");
  const [at,setAt]=useState("");const [context,setContext]=useState("");const [observations,setObservations]=useState("");
  const [interpretations,setInterpretations]=useState("");const [action,setAction]=useState("");const [rationale,setRationale]=useState("");
  const [target,setTarget]=useState("");const [search,setSearch]=useState("");const [status,setStatus]=useState("");
  const [feedback,setFeedback]=useState("");const [dirty,setDirty]=useState(false);
  useEffect(()=>{function warn(event:BeforeUnloadEvent){if(dirty){event.preventDefault();event.returnValue="";}}window.addEventListener("beforeunload",warn);return()=>window.removeEventListener("beforeunload",warn);},[dirty]);
  function changeScreen(next:Screen){if(dirty&&!window.confirm("Discard unsaved form input? Saved synthetic records remain in memory."))return;setDirty(false);setScreen(next);setFeedback("");}
  function edit(change:()=>void){change();setDirty(true);}
  function saveInspection(){try{
    const input={canonical_asset_id:asset,method,method_version:"engineer-proposal-1",inspector_ref:"synthetic-inspector",
      inspected_at:at||null,quantity,value:enteredValue(value,kind),unit:unit||null,operating_context:context,
      observations:parseHypotheses(observations),interpretations:parseHypotheses(interpretations)};
    const record=localRecord(input,new Date().toISOString(),"inspection:synthetic:"+crypto.randomUUID());
    setRecords(old=>[record,...old]);setDirty(false);setFeedback("Synthetic draft saved locally. NOT ASSESSED; no backend write.");
  }catch(error){setFeedback(error instanceof Error?error.message:"Invalid inspection input.");}}
  function submit(record:LocalInspection){try{const next=submitLocal(record,record.revision,new Date().toISOString());setRecords(old=>old.map(x=>x.id===next.id?next:x));setFeedback("Synthetic review queued. No approval or source action.");}catch(error){setFeedback(error instanceof Error?error.message:"Conflict.");}}
  function saveProposal(){if(!action.trim()||!rationale.trim()||Array.from(action).length>6000||Array.from(rationale).length>6000){setFeedback("Enter nonblank proposed action and rationale, at most 6,000 characters each.");return;}
    setProposals(old=>[{id:"recommendation:synthetic:"+crypto.randomUUID(),action,rationale,case_ref:"case:synthetic-flow-a",target:target||null,status:"DRAFT",scope:"NOT_A_MAINTENANCE_AUTHORIZATION"},...old]);setDirty(false);setFeedback("Synthetic proposal saved locally. It does not authorize maintenance or create a Maximo WO.");}
  const visible=records.filter(x=>(!status||x.status===status)&&(!search||`${x.id} ${x.input.method} ${x.input.canonical_asset_id}`.toLowerCase().includes(search.toLowerCase())));
  return <>
    <PageHeader eyebrow="PHASE 2 / DEVELOPMENT LAB" title={screen} description="Engineering evidence and human proposals, with explicit provenance." actions={<Link className="engineering-primary" href="/engineering" onClick={event=>{if(dirty&&!window.confirm("Leave unsaved form input?"))event.preventDefault();}}>Engineering Workspace ↗</Link>}/>
    <div className="scope-banner engineering-demo" role="note"><strong>SYNTHETIC LOCAL DEMO</strong><span>Browser-memory fixtures. No authentication, operational data, source requests or backend writes.</span></div>
    <nav className="phase2-tabs" aria-label="Phase 2 workspaces">{screens.map(name=><button type="button" key={name} aria-current={screen===name?"page":undefined} onClick={()=>changeScreen(name)}>{name}</button>)}</nav>
    <SectionCard className="phase2-context"><div><p className="eyebrow">SYNTHETIC ASSET CONTEXT</p><h2>Feeder A — training fixture</h2><code>{asset}</code></div><div><StatusBadge value="NOT ASSESSED" mode="raw-neutral"/><p>Asset identity here is synthetic. No operational health assessment.</p></div></SectionCard>
    <p className="engineering-feedback" role="status" aria-live="polite">{feedback||"Engineering field approval and trusted operational identity remain pending."}</p>
    {screen==="PdM Center"&&<div className="phase2-grid"><SectionCard><h2>Manual inspection entry</h2><p className="phase2-muted">Human-entered measurement. Method fields are proposals; no acceptance limit is applied.</p>
      <form className="engineering-editor" onSubmit={event=>{event.preventDefault();saveInspection();}}>
        <label>Inspection method<select value={method} onChange={e=>edit(()=>setMethod(e.target.value as Method))}>{methods.map(m=><option key={m}>{m}</option>)}</select></label>
        <label>Quantity<input value={quantity} maxLength={120} onChange={e=>edit(()=>setQuantity(e.target.value))}/></label>
        <div className="phase2-form-row"><label>Value type<select value={kind} onChange={e=>edit(()=>setKind(e.target.value as typeof kind))}>{["UNKNOWN","NUMERIC","TEXT","BOOLEAN"].map(x=><option key={x}>{x}</option>)}</select></label><label>Original unit<input value={unit} maxLength={40} onChange={e=>edit(()=>setUnit(e.target.value))}/></label></div>
        <label>Original measurement value<input disabled={kind==="UNKNOWN"} value={value} onChange={e=>edit(()=>setValue(e.target.value))}/></label>
        <label>Inspection timestamp with timezone<input placeholder="2026-10-09T08:00:00+07:00" value={at} onChange={e=>edit(()=>setAt(e.target.value))}/></label>
        <label>Operating context<textarea rows={2} maxLength={6000} value={context} onChange={e=>edit(()=>setContext(e.target.value))}/></label>
        <label>HUMAN OBSERVATION — one entry per line<textarea rows={2} value={observations} onChange={e=>edit(()=>setObservations(e.target.value))}/></label>
        <label>HUMAN HYPOTHESIS — not source fact<textarea rows={2} value={interpretations} onChange={e=>edit(()=>setInterpretations(e.target.value))}/></label>
        <p>Attachments: metadata contract prepared; secure upload is not enabled.</p><button className="engineering-primary" type="submit">Save local inspection</button>
      </form></SectionCard><SectionCard><h2>Inspection register</h2><div className="engineering-toolbar"><label>Filter record / asset<input value={search} onChange={e=>setSearch(e.target.value)}/></label><label>Review status<select value={status} onChange={e=>setStatus(e.target.value)}><option value="">All</option><option>DRAFT</option><option>IN_REVIEW</option></select></label></div>
      {visible.length===0?<EmptyState title="No synthetic inspection records."/>:visible.map(r=><article className="phase2-record" key={r.id}><h3>{r.input.method}</h3><code>{r.id}</code><p>HUMAN MEASUREMENT: {r.input.value===null?"UNKNOWN":String(r.input.value)} {r.input.unit??"unit UNKNOWN"}</p><p>Source quality UNKNOWN · freshness UNKNOWN · assessment NOT ASSESSED</p><StatusBadge value={r.status} mode="raw-neutral"/><p>Revision {r.revision} · inspector {r.input.inspector_ref}</p><button type="button" className="engineering-primary" disabled={r.status!=="DRAFT"} onClick={()=>submit(r)}>Submit local review</button><details><summary>Revision history</summary>{r.history.map(h=><p key={h.revision}>r{h.revision} · {h.action} · {h.actor} · {h.at}</p>)}</details></article>)}
    </SectionCard></div>}
    {screen==="Asset Health 360"&&<div className="phase2-grid"><SectionCard><h2>Evidence, not a health score</h2><p>Overall assessment: <strong>NOT ASSESSED</strong></p><p>Maintenance context: existing-WO references are informational. No production records are loaded in this lab.</p><p>PI condition evidence: UNKNOWN / NOT LOADED. Source quality does not prove freshness or equipment health.</p><Link href="/engineering">View linked synthetic investigation ↗</Link></SectionCard><SectionCard><h2>Method evidence coverage</h2>{methods.map(m=><div className="phase2-record" key={m}><strong>{m}</strong><p>{records.some(r=>r.input.method===m)?"Synthetic human measurement available":"UNKNOWN — no inspection submitted"}</p><StatusBadge value="NOT ASSESSED" mode="raw-neutral"/></div>)}</SectionCard></div>}
    {screen==="Recommendations"&&<div className="phase2-grid"><SectionCard><h2>Draft engineering proposal</h2><form className="engineering-editor" onSubmit={e=>{e.preventDefault();saveProposal();}}><label>Linked synthetic case<input value="case:synthetic-flow-a" readOnly/></label><label>Proposed action<textarea rows={3} maxLength={6000} value={action} onChange={e=>edit(()=>setAction(e.target.value))}/></label><label>Human engineering rationale<textarea rows={3} maxLength={6000} value={rationale} onChange={e=>edit(()=>setRationale(e.target.value))}/></label><label>Proposed target date<input type="date" value={target} onChange={e=>edit(()=>setTarget(e.target.value))}/></label><p>PIC/team directory pending. Existing Maximo WO linking is a backend contract; no source action is exposed.</p><button className="engineering-primary" type="submit">Save local proposal</button></form></SectionCard><SectionCard><h2>Proposal register</h2>{proposals.length===0?<EmptyState title="No synthetic recommendations."/>:proposals.map(p=><article className="phase2-record" key={p.id}><h3>{p.action}</h3><p>HUMAN RATIONALE: {p.rationale}</p><StatusBadge value={p.status} mode="raw-neutral"/><p>{p.scope}</p><p>Target date {p.target??"UNKNOWN"} · responsible team UNKNOWN</p><code>{p.case_ref}</code></article>)}</SectionCard></div>}
    {screen==="Action Board"&&<div className="phase2-grid"><SectionCard><h2>Independent review queue</h2><p>{records.filter(r=>r.status==="IN_REVIEW").length} synthetic inspection records awaiting review.</p>{records.filter(r=>r.status==="IN_REVIEW").map(r=><article className="phase2-record" key={r.id}><strong>{r.input.method}</strong><p>HUMAN OBSERVATION / HYPOTHESIS · r{r.revision}</p><p>Reviewer assignment UNKNOWN. Trusted independent review is not activated.</p><code>{r.id}</code></article>)}<p>No browser-controlled reviewer authority is accepted.</p></SectionCard><SectionCard><h2>Follow-up boundary</h2><p>Local recommendation drafts: {proposals.length} (synthetic).</p><p>REVIEW DECISION: PENDING. Proposed actions are not approved maintenance actions.</p><p>No Maximo WO create, update, approval or closure operation exists in this workspace.</p><EmptyState title="Operational action workflow not activated."/></SectionCard></div>}
  </>;
}
