"use client";
import {useCallback,useEffect,useRef,useState,type ReactNode} from 'react';
import {engineeringRequest} from '../lib/engineering-http';
import {loginHref} from '../lib/login-navigation';
import {WorkspaceAccountContext} from './WorkspaceAccount';
import type {LocalSession} from '../lib/local-session';
/** Presentation/expired-session cleanup, never an authorization substitute. */
export default function AuthenticatedWorkspace({identity,children}:{identity:LocalSession;children:ReactNode}){
 const [state,setState]=useState<'ready'|'checking'|'unavailable'>('ready'),[error,setError]=useState('');
 const [confirmLogout,setConfirmLogout]=useState(false),[logoutPhase,setLogoutPhase]=useState<'idle'|'pending'|'failed'>('idle');
 const logoutActive=useRef(false),logoutInFlight=useRef(false),retrySession=useRef<()=>void>(()=>{});
 const dialogRef=useRef<HTMLDialogElement>(null),cancelRef=useRef<HTMLButtonElement>(null);
 useEffect(()=>{if(confirmLogout&&!dialogRef.current?.open){dialogRef.current?.showModal();cancelRef.current?.focus();}},[confirmLogout]);
 const requestLogout=()=>setConfirmLogout(true);
 const toLogin=useCallback(()=>{setState('checking');window.location.replace(loginHref(window.location.pathname+window.location.search,true));},[]);
 useEffect(()=>{
  let active=true,inflight=false;
  async function check(block=false){
   if(logoutActive.current||inflight)return;inflight=true;if(block)setState('checking');
   try{
    const response=await fetch('/api/engineering-qa/session',{cache:'no-store',redirect:'error',signal:AbortSignal.timeout(5000)});
    if(!active||logoutActive.current)return;
    if(response.status===401||response.status===403){toLogin();return;}
    if(!response.ok){setState('unavailable');return;}
    const who=await response.json();
    if(who.username!==identity.username||who.subject!==identity.subject||JSON.stringify(who.roles)!==JSON.stringify(identity.roles)||JSON.stringify(who.asset_ids)!==JSON.stringify(identity.asset_ids)){window.location.reload();return;}
    setState('ready');
   }catch{if(active&&!logoutActive.current)setState('unavailable');}finally{inflight=false;}
  }
  const recheck=()=>{void check(true);};retrySession.current=recheck;
  const focus=()=>{if(logoutActive.current)return;dialogRef.current?.close();setConfirmLogout(false);void check(true);};
  const visibility=()=>{if(document.visibilityState==='visible')focus();};
  const pageShow=(event:PageTransitionEvent)=>{if(event.persisted){setState('checking');window.location.reload();}};
  const pageHide=()=>{if(!logoutActive.current)setState('checking');};
  window.addEventListener('pagehide',pageHide);
  window.addEventListener('focus',focus);document.addEventListener('visibilitychange',visibility);window.addEventListener('pageshow',pageShow);
  const timer=setInterval(()=>{if(document.visibilityState==='visible')void check();},30000);
  return()=>{active=false;if(retrySession.current===recheck)retrySession.current=()=>{};clearInterval(timer);window.removeEventListener('pagehide',pageHide);window.removeEventListener('focus',focus);document.removeEventListener('visibilitychange',visibility);window.removeEventListener('pageshow',pageShow);};
 },[identity,toLogin]);
 async function logout(){
  if(logoutInFlight.current)return;
  logoutInFlight.current=true;logoutActive.current=true;setLogoutPhase('pending');setError('');
  try{const who=await engineeringRequest('session') as {csrf_token:string};await engineeringRequest('session/logout','POST',{},who.csrf_token);window.location.replace('/login');}
  catch{logoutInFlight.current=false;setLogoutPhase('failed');setState('unavailable');setError('Keluar belum dapat dikonfirmasi. Akses ditutup; coba lagi.');}
 }
 const pending=logoutPhase==='pending',locked=logoutPhase!=='idle';
 const confirmation=<dialog className="logout-dialog" ref={dialogRef} aria-labelledby="logout-title" aria-describedby="logout-description" aria-busy={pending} onCancel={event=>{if(locked)event.preventDefault();}} onClose={()=>{if(locked){dialogRef.current?.showModal();return;}setConfirmLogout(false);}}><div className="logout-dialog-icon" aria-hidden="true">{pending?<span className="spinner"/>:'↗'}</div><h2 id="logout-title">{pending?'Sedang keluar…':logoutPhase==='failed'?'Belum dapat keluar':'Keluar dari NADI?'}</h2><p id="logout-description" role={pending?'status':undefined}>{pending?'Mohon tunggu. Anda akan diarahkan ke halaman masuk.':'Anda akan kembali ke halaman masuk. Pastikan isian yang ingin disimpan sudah tersimpan.'}</p>{error&&<p role="alert">{error}</p>}<div className="logout-dialog-actions">{!locked&&<button ref={cancelRef} className="button" type="button" onClick={()=>dialogRef.current?.close()}>Batal</button>}<button className="button primary" type="button" disabled={pending} onClick={()=>{void logout();}}>{pending?<><span className="spinner" aria-hidden="true"/> Sedang keluar…</>:logoutPhase==='failed'?'Coba keluar lagi':'Ya, keluar'}</button></div></dialog>;
 return <WorkspaceAccountContext.Provider value={{identity,requestLogout}}>{!locked&&(state==='ready'?children:<main className="state-card" role="status"><h1>{state==='checking'?'Memeriksa sesi…':'Otoritas sesi tidak tersedia'}</h1><p>Tampilan terlindungi ditutup sampai sesi dapat diverifikasi.</p><button className="button" onClick={()=>retrySession.current()}>Periksa kembali</button><button className="button" onClick={requestLogout}>Keluar</button></main>)}{confirmation}</WorkspaceAccountContext.Provider>;
}
