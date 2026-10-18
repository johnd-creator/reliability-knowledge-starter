"use client";
import {useCallback,useEffect,useState,type ReactNode} from 'react';
import {engineeringRequest} from '../lib/engineering-http';
import {loginHref} from '../lib/login-navigation';
import type {LocalSession} from '../lib/local-session';
/** Presentation/expired-session cleanup, never an authorization substitute. */
export default function AuthenticatedWorkspace({identity,children}:{identity:LocalSession;children:ReactNode}){
 const [state,setState]=useState<'ready'|'checking'|'unavailable'>('ready'),[error,setError]=useState('');
 const toLogin=useCallback(()=>{setState('checking');window.location.replace(loginHref(window.location.pathname+window.location.search,true));},[]);
 useEffect(()=>{
  let active=true,inflight=false;
  async function check(block=false){
   if(inflight)return;inflight=true;if(block)setState('checking');
   try{
    const response=await fetch('/api/engineering-qa/session',{cache:'no-store',redirect:'error',signal:AbortSignal.timeout(5000)});
    if(!active)return;
    if(response.status===401||response.status===403){toLogin();return;}
    if(!response.ok){setState('unavailable');return;}
    const who=await response.json();
    if(who.username!==identity.username||who.subject!==identity.subject||JSON.stringify(who.roles)!==JSON.stringify(identity.roles)||JSON.stringify(who.asset_ids)!==JSON.stringify(identity.asset_ids)){window.location.reload();return;}
    setState('ready');
   }catch{if(active)setState('unavailable');}finally{inflight=false;}
  }
  const focus=()=>{void check(true);};
  const visibility=()=>{if(document.visibilityState==='visible')focus();};
  const pageShow=(event:PageTransitionEvent)=>{if(event.persisted){setState('checking');window.location.reload();}};
  const pageHide=()=>{setState('checking');};
  window.addEventListener('pagehide',pageHide);
  window.addEventListener('focus',focus);document.addEventListener('visibilitychange',visibility);window.addEventListener('pageshow',pageShow);
  const timer=setInterval(()=>{if(document.visibilityState==='visible')void check();},30000);
  return()=>{active=false;clearInterval(timer);window.removeEventListener('pagehide',pageHide);window.removeEventListener('focus',focus);document.removeEventListener('visibilitychange',visibility);window.removeEventListener('pageshow',pageShow);};
 },[identity,toLogin]);
 async function logout(){
  setState('checking');setError('');
  try{const who=await engineeringRequest('session') as {csrf_token:string};await engineeringRequest('session/logout','POST',{},who.csrf_token);window.location.replace('/login');}
  catch{setState('unavailable');setError('Keluar belum dapat dikonfirmasi. Akses ditutup; coba lagi.');}
 }
 if(state!=='ready')return <main className="state-card" role="status"><h1>{state==='checking'?'Memeriksa sesi…':'Otoritas sesi tidak tersedia'}</h1><p>{error||'Tampilan terlindungi ditutup sampai sesi dapat diverifikasi.'}</p><button className="button" onClick={()=>window.location.reload()}>Periksa kembali</button><button className="button" onClick={logout}>Keluar</button></main>;
 return <><div className="session-account" aria-label="Akun terautentikasi"><span title={"ID audit: "+identity.subject}>Nama pengguna: {identity.username??identity.subject}</span><span>Peran: {identity.roles.join(', ')}</span><button className="button" onClick={logout}>Keluar</button></div>{children}</>;
}
