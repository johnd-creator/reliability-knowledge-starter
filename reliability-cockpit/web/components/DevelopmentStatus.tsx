"use client";
import { idText, statusLabel } from "../lib/id-copy";
import Link from "next/link";
import {useEffect,useState} from "react";
type Status={branch:string;sha:string;dirty:boolean|null;backend:string;database:string;database_identity:string;factual_backend:string;engineering:boolean;stale:boolean;backend_sha:string;compatibility:string;compatibility_approval:string|null;launcher_sha256:string|null;launcher_source_sha:string|null};
export default function DevelopmentStatus(){
 const [status,setStatus]=useState<Status|null>(null);
 useEffect(()=>{let active=true;const read=async()=>{try{const reply=await fetch("/api/development/status",{cache:"no-store"});if(!reply.ok)throw new Error();const data=await reply.json();if(active)setStatus(data);}catch{if(active)setStatus(null);}};read();const timer=setInterval(read,5000);return()=>{active=false;clearInterval(timer);};},[]);
 return <aside className="nadi-development-status" aria-label={idText("Development environment status")} style={{padding:"12px 20px",background:"#102f43",color:"#eaf8fa",overflowWrap:"anywhere",fontSize:12}}>
 <strong>{idText("DEVELOPMENT · LIVE PREVIEW")}</strong>{" · "}{status?.branch??statusLabel("UNKNOWN")}<br/>
 {idText("Source SHA:")} <code>{status?.sha??statusLabel("UNKNOWN")}</code>{" · "}{idText("Changes:")} {statusLabel(status?.dirty===null||!status?statusLabel("UNKNOWN"):status.dirty?"UNCOMMITTED":"CLEAN")}<br/>
 <span>SHA backend QA: <code>{status?.backend_sha??statusLabel("UNKNOWN")}</code></span><br/>
 {status?.compatibility==="VERIFIED_SOURCE_EQUIVALENT"&&<p>Sumber frontend dan backend berbeda. Kompatibilitas source/kontrak terverifikasi: <code>{status.compatibility_approval}</code><br/>Source launcher: <code>{status.launcher_source_sha}</code><br/>SHA256 launcher: <code>{status.launcher_sha256}</code></p>}
 {idText("Factual backend:")} {statusLabel(status?.factual_backend??statusLabel("UNKNOWN"))}{" · "}{idText("Engineering backend:")} {statusLabel(status?.backend??statusLabel("UNKNOWN"))}<br/>
 {idText("Application DB:")} {status?.database_identity??statusLabel("UNKNOWN")} ({statusLabel(status?.database??statusLabel("UNKNOWN"))}){" · "}{idText("Engineering:")} {!status?statusLabel("UNKNOWN"):status.engineering?idText("ENABLED (fixture only)"):statusLabel("UNAVAILABLE")}
 {status?.stale&&<p role="alert">{idText("Preview release mismatch / UNKNOWN. Stop and reconcile the worktree; do not switch branches while running.")}</p>}
 <p style={{margin:"6px 0"}}>{idText("Factual pages: existing local read-only API. Engineering: SYNTHETIC fixtures; no operational writes.")}</p>
 <nav aria-label={idText("Development preview navigation")} style={{display:"flex",gap:16,flexWrap:"wrap"}}>
 <Link href="/login">{idText("Local login")}</Link><Link href="/engineering/local">{idText("Persisted Engineering Workspace")}</Link><Link href="/engineering">{idText("Synthetic demo screens")}</Link>
 </nav></aside>;
}
