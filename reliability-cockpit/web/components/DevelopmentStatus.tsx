"use client";
import { idText, statusLabel } from "../lib/id-copy";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";

export type DevelopmentSnapshot = {
 branch:string; sha:string; launched_sha:string; dirty:boolean|null; backend:string;
 database:string; database_identity:string; factual_backend:string; engineering:boolean;
 stale:boolean; backend_sha:string; compatibility:string; compatibility_approval:string|null;
 worker_pid?:number;parent_pid?:number;worker_generation?:number|null;worker_integrity?:string;
 launcher_sha256:string|null; launcher_source_sha:string|null;
};
export function developmentTone(status:DevelopmentSnapshot|null):"verified"|"warning"|"unavailable" {
 if(!status)return "unavailable";
 const sha=(value:string)=>/^[a-f0-9]{40}$/.test(value);
 const pair=status.compatibility==="SAME_SOURCE"?status.sha===status.backend_sha:
  status.compatibility==="VERIFIED_SOURCE_EQUIVALENT"&&!!status.compatibility_approval&&/^[a-f0-9]{64}$/.test(status.compatibility_approval);
 return status.dirty===false&&status.stale===false&&sha(status.sha)&&sha(status.backend_sha)&&status.launched_sha===status.sha&&pair&&
  status.backend==="AVAILABLE"&&status.factual_backend==="AVAILABLE"?"verified":"warning";
}

/** Compact disclosure of the existing endpoint; never changes release approval or auth. */
export default function DevelopmentStatus(){
 const [status,setStatus]=useState<DevelopmentSnapshot|null>(null),[loading,setLoading]=useState(true),[open,setOpen]=useState(false);
 const container=useRef<HTMLDivElement>(null),trigger=useRef<HTMLButtonElement>(null),panel=useRef<HTMLDivElement>(null);
 const id=useId(),pathname=usePathname();
 useEffect(()=>{setOpen(false);},[pathname]);
 useEffect(()=>{
  let active=true,reading=false;let pending:AbortController|null=null;
  const read=async()=>{
   if(reading)return;reading=true;pending=new AbortController();const timeout=setTimeout(()=>pending?.abort(),10000);
   try{
    const reply=await fetch("/api/development/status",{cache:"no-store",signal:pending.signal});if(!reply.ok)throw new Error();
    const data=await reply.json();
    if(!data||typeof data.branch!=="string"||typeof data.sha!=="string"||typeof data.backend_sha!=="string"||typeof data.stale!=="boolean"||![true,false,null].includes(data.dirty))throw new Error();
    if(active)setStatus(data);
   }catch{if(active)setStatus(null);}
   finally{clearTimeout(timeout);reading=false;if(active)setLoading(false);}
  };
  void read();const timer=setInterval(read,5000);
  return()=>{active=false;pending?.abort();clearInterval(timer);};
 },[]);
 useEffect(()=>{
  if(!open)return;
  panel.current?.focus();
  const outside=(event:Event)=>{if(event.target instanceof Node&&!container.current?.contains(event.target))setOpen(false);};
  const escape=(event:KeyboardEvent)=>{if(event.key==="Escape"){event.preventDefault();setOpen(false);trigger.current?.focus();}};
  document.addEventListener("pointerdown",outside);document.addEventListener("focusin",outside);document.addEventListener("keydown",escape);
  return()=>{document.removeEventListener("pointerdown",outside);document.removeEventListener("focusin",outside);document.removeEventListener("keydown",escape);};
 },[open]);
 const tone=loading?"checking":developmentTone(status);
 const label=loading?"Memeriksa status":tone==="verified"?"Layanan dan integritas terverifikasi":tone==="warning"?"Peringatan development":"Status tidak tersedia";
 const value=(text:string|undefined|null)=>text??statusLabel("UNKNOWN");
 return <div className={`dev-status dev-status--${tone}`} ref={container}>
  <button ref={trigger} type="button" className="dev-status-trigger" aria-label={`Status development: ${label}`} aria-expanded={open} aria-controls={id} onClick={()=>setOpen(!open)} title={label}>
   <span className="dev-status-dot" aria-hidden="true"/><span>DEV</span><span aria-hidden="true">{tone==="warning"?"!":tone==="unavailable"?"?":""} {open?"▴":"▾"}</span>
  </button>
  {open&&<div ref={panel} id={id} className="dev-status-panel" role="region" aria-label="Detail status development" tabIndex={-1}>
   <div className="dev-status-heading"><strong>Status development</strong><button type="button" className="icon-button" aria-label="Tutup detail status development" onClick={()=>{setOpen(false);trigger.current?.focus();}}>×</button></div>
   <p className="dev-status-summary" role="status">{label}</p>
   {!loading&&!status&&<p>Endpoint status tidak dapat dibaca. Integritas dan ketersediaan layanan belum dapat diverifikasi.</p>}
   {status&&<>
    {status.dirty===true&&<p className="dev-status-warning">Ada perubahan belum di-commit (UNCOMMITTED). Periksa diff; jangan mereset atau berpindah source pada worktree aktif.</p>}
    {status.stale&&<p className="dev-status-warning">Integritas preview belum terverifikasi (UNKNOWN / release mismatch). SHA proses, source, dirty state dan approval kompatibilitas perlu diperiksa.</p>}
    <dl>
     {status.worker_integrity&&<><dt>Integritas worker Next</dt><dd>{status.worker_integrity}</dd><dt>PID parent / worker · generasi resmi</dt><dd>{status.parent_pid} / {status.worker_pid} · {value(status.worker_generation?.toString())}</dd></>}
     <dt>Branch</dt><dd>{status.branch}</dd>
     <dt>SHA frontend</dt><dd><code>{status.sha}</code></dd>
     <dt>SHA saat proses diluncurkan</dt><dd><code>{value(status.launched_sha)}</code></dd>
     <dt>{idText("Changes:")}</dt><dd>{statusLabel(status.dirty===null?"UNKNOWN":status.dirty?"UNCOMMITTED":"CLEAN")}</dd>
     <dt>SHA backend QA</dt><dd><code>{status.backend_sha}</code></dd>
     <dt>Kompatibilitas release</dt><dd><code>{status.compatibility}</code>{status.compatibility==="VERIFIED_SOURCE_EQUIVALENT"&&<p>SHA frontend/backend berbeda; pasangan source/kontrak ini disetujui secara eksplisit.</p>}</dd>
     {status.compatibility_approval&&<><dt>Approval kompatibilitas</dt><dd><code>{status.compatibility_approval}</code></dd></>}
     <dt>{idText("Factual backend:")}</dt><dd>{statusLabel(value(status.factual_backend))}</dd>
     <dt>{idText("Engineering backend:")}</dt><dd>{statusLabel(value(status.backend))}</dd>
     <dt>{idText("Application DB:")}</dt><dd>{value(status.database_identity)} · {statusLabel(value(status.database))}</dd>
     <dt>{idText("Engineering:")}</dt><dd>{status.engineering?idText("ENABLED (fixture only)"):statusLabel("UNAVAILABLE")}</dd>
     {status.launcher_source_sha&&<><dt>Source launcher</dt><dd><code>{status.launcher_source_sha}</code></dd><dt>SHA256 launcher</dt><dd><code>{value(status.launcher_sha256)}</code></dd></>}
    </dl>
   </>}
   <p className="dev-status-boundary">{idText("Factual pages: existing local read-only API. Engineering: SYNTHETIC fixtures; no operational writes.")}</p>
   <nav aria-label={idText("Development preview navigation")}><Link href="/login">{idText("Local login")}</Link><Link href="/engineering/local">{idText("Persisted Engineering Workspace")}</Link><Link href="/engineering">{idText("Synthetic demo screens")}</Link></nav>
  </div>}
 </div>;
}
