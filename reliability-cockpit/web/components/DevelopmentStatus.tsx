"use client";
import Link from "next/link";
import {useEffect,useState} from "react";
type Status={branch:string;sha:string;dirty:boolean|null;backend:string;database:string;database_identity:string;factual_backend:string;engineering:boolean;stale:boolean};
export default function DevelopmentStatus(){
 const [status,setStatus]=useState<Status|null>(null);
 useEffect(()=>{let active=true;const read=async()=>{try{const reply=await fetch("/api/development/status",{cache:"no-store"});if(!reply.ok)throw new Error();const data=await reply.json();if(active)setStatus(data);}catch{if(active)setStatus(null);}};read();const timer=setInterval(read,5000);return()=>{active=false;clearInterval(timer);};},[]);
 return <aside className="nadi-development-status" aria-label="Development environment status" style={{padding:"12px 20px",background:"#102f43",color:"#eaf8fa",overflowWrap:"anywhere",fontSize:12}}>
 <strong>DEVELOPMENT · LIVE PREVIEW</strong>{" · "}{status?.branch??"UNKNOWN"}<br/>
 Source SHA: <code>{status?.sha??"UNKNOWN"}</code>{" · "}Changes: {status?.dirty===null||!status?"UNKNOWN":status.dirty?"UNCOMMITTED":"CLEAN"}<br/>
 Factual backend: {status?.factual_backend??"UNKNOWN"}{" · "}Engineering backend: {status?.backend??"UNKNOWN"}<br/>
 Application DB: {status?.database_identity??"UNKNOWN"} ({status?.database??"UNKNOWN"}){" · "}Engineering: {!status?"UNKNOWN":status.engineering?"ENABLED (fixture only)":"UNAVAILABLE"}
 {status?.stale&&<p role="alert">Preview release mismatch / UNKNOWN. Stop and reconcile the worktree; do not switch branches while running.</p>}
 <p style={{margin:"6px 0"}}>Factual pages: existing local read-only API. Engineering: SYNTHETIC fixtures; no operational writes.</p>
 <nav aria-label="Development preview navigation" style={{display:"flex",gap:16,flexWrap:"wrap"}}>
 <Link href="/login">Local login</Link><Link href="/engineering/local">Persisted Engineering Workspace</Link><Link href="/engineering">Synthetic demo screens</Link>
 </nav></aside>;
}
