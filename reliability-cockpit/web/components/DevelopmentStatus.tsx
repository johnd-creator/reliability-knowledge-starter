'use client';
import {idText,statusLabel} from '../lib/id-copy';
import Link from 'next/link';
import {useEffect,useRef,useState} from 'react';
import {developmentWarnings,type DevelopmentStatusValue} from '../lib/development-status-view';
export default function DevelopmentStatus(){
 const [status,setStatus]=useState<DevelopmentStatusValue|null>(null);
 useEffect(()=>{let active=true;const read=async()=>{try{const reply=await fetch('/api/development/status',{cache:'no-store'});if(!reply.ok)throw new Error();const data=await reply.json();if(active)setStatus(data);}catch{if(active)setStatus(null);}};read();const timer=setInterval(read,5000);return()=>{active=false;clearInterval(timer);};},[]);
 return <DevelopmentStatusPanel status={status}/>;
}
export function DevelopmentStatusPanel({status}:{status:DevelopmentStatusValue|null}){
 const warnings=developmentWarnings(status);
 const details=useRef<HTMLDetailsElement|null>(null);
 useEffect(()=>{const close=(event:KeyboardEvent)=>{const panel=details.current;if(event.key==='Escape'&&panel?.open&&panel.contains(document.activeElement)){panel.open=false;panel.querySelector('summary')?.focus();}};document.addEventListener('keydown',close);return()=>document.removeEventListener('keydown',close);},[]);
 return <aside className="nadi-development-status nadi-development-compact" aria-label={idText('Development environment status')}>
  <div className="dev-status-row"><strong>DEV · Lokal</strong><span>{status?.branch??'UNKNOWN'}</span><code title={status?.sha}>{status?.sha?.slice(0,8)??'UNKNOWN'}</code><span>{status?.dirty===true?'Draf lokal':status?.dirty===false?'Bersih':'Perubahan UNKNOWN'}</span><span className="dev-service-summary">{status?.backend==='AVAILABLE'&&status?.factual_backend==='AVAILABLE'?'Kedua API tersedia':'Perlu pemeriksaan API'}</span>
  <details className="dev-status-details" ref={details}><summary>Detail teknis</summary><div className="dev-status-panel"><h2>Identitas development</h2><dl>
   <div><dt>Source SHA frontend</dt><dd><code>{status?.sha??'UNKNOWN'}</code></dd></div><div><dt>SHA saat startup</dt><dd><code>{status?.launched_sha??'UNKNOWN'}</code></dd></div><div><dt>SHA backend QA</dt><dd><code>{status?.backend_sha??'UNKNOWN'}</code></dd></div><div><dt>Branch / perubahan</dt><dd>{status?.branch??'UNKNOWN'} · {statusLabel(!status||typeof status.dirty!=='boolean'?'UNKNOWN':status.dirty?'UNCOMMITTED':'CLEAN')}</dd></div>
   <div><dt>Integritas / kompatibilitas</dt><dd>{!status?'UNKNOWN':status.stale?'STALE':status.compatibility} · {status?.compatibility??'UNKNOWN'}</dd></div><div><dt>Persetujuan pasangan source</dt><dd><code>{status?.compatibility_approval??'Tidak berlaku / tidak tersedia'}</code></dd></div>
   <div><dt>Backend faktual</dt><dd>{statusLabel(status?.factual_backend??'UNKNOWN')}</dd></div><div><dt>Backend Engineering</dt><dd>{statusLabel(status?.backend??'UNKNOWN')}</dd></div><div><dt>Database aplikasi QA</dt><dd>{status?.database_identity??'UNKNOWN'} · {statusLabel(status?.database??'UNKNOWN')}</dd></div><div><dt>Engineering</dt><dd>{!status?'UNKNOWN':status.engineering?'Aktif hanya untuk fixture sintetis':'Tidak tersedia'}</dd></div>
   <div><dt>Source launcher</dt><dd><code>{status?.launcher_source_sha??'Tidak tersedia pada DTO / tidak berlaku'}</code></dd></div><div><dt>SHA256 launcher</dt><dd><code>{status?.launcher_sha256??'Tidak tersedia pada DTO / tidak berlaku'}</code></dd></div>
  </dl><p>{idText('Factual pages: existing local read-only API. Engineering: SYNTHETIC fixtures; no operational writes.')}</p><nav aria-label={idText('Development preview navigation')}><Link href="/login">{idText('Local login')}</Link><Link href="/engineering/local">{idText('Persisted Engineering Workspace')}</Link><Link href="/engineering">{idText('Synthetic demo screens')}</Link></nav></div></details></div>
  {warnings.length>0&&<div className="dev-status-warnings" role="alert">{warnings.map(w=><p key={w}>{w}</p>)}</div>}
 </aside>;
}
