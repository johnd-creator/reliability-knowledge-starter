/** Local-development boundary only. PostgreSQL SessionAuthority remains the authority.
 * Never import this module into client components or cache a verified principal. */
import {readBounded} from './bounded-http';
export const SESSION_COOKIE='__Host-nadi_session';
export const LOCAL_ORIGIN='https://localhost:3000';
export type LocalSession={subject:string;roles:string[];asset_ids:string[];username?:string};
export type SessionResult={state:'authenticated';session:LocalSession}|{state:'anonymous'|'unavailable'};
export function localGuardEnabled(env:NodeJS.ProcessEnv=process.env):boolean {
 // Explicit approved laptop launch identity; production/other deployments cannot opt in by cookie.
 return env.NODE_ENV==='development'&&env.NADI_PRIMARY_FRONTEND==='true'&&env.NADI_LIVE_DEV==='true'&&env.NADI_ENGINEERING_QA_ENABLED==='true'&&env.NADI_QA_BACKEND_URL==='http://127.0.0.1:13036';
}
export function sessionCookie(headers:Headers):string|null {
 const parts=(headers.get('cookie')??'').split(';').map(v=>v.trim()).filter(v=>v.startsWith(SESSION_COOKIE+'='));
 if(parts.length!==1)return null;
 const token=parts[0].slice(SESSION_COOKIE.length+1);
 return /^[A-Za-z0-9_-]{40,128}$/.test(token)?SESSION_COOKIE+'='+token:null;
}
export async function verifyLocalSession(headers:Headers,requestFetch:typeof fetch=fetch):Promise<SessionResult>{
 const cookie=sessionCookie(headers);if(!cookie)return {state:'anonymous'};
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),3000);
 try{
  const response=await requestFetch('http://127.0.0.1:13036/v1/engineering/session',{method:'GET',headers:{cookie},cache:'no-store',redirect:'error',signal:controller.signal});
  if([401,403].includes(response.status))return {state:'anonymous'};
  if(response.status!==200)return {state:'unavailable'};
  const value=JSON.parse(new TextDecoder().decode(await readBounded(response.body,256*1024,controller.signal)));
  if(!value||typeof value.subject!=='string'||!/^local:[A-Za-z0-9-]{1,150}$/.test(value.subject)||!Array.isArray(value.roles)||!value.roles.length||!value.roles.every((r:unknown)=>typeof r==='string'&&['ADMIN','AUTHOR','REVIEWER'].includes(r))||!Array.isArray(value.asset_ids)||value.asset_ids.length>1000||!value.asset_ids.every((id:unknown)=>typeof id==='string'&&/^[A-Za-z0-9_.:-]{1,200}$/.test(id)))return {state:'unavailable'};
  // CSRF is intentionally not exposed through this server-side read verifier.
  return {state:'authenticated',session:{subject:value.subject,roles:value.roles,asset_ids:value.asset_ids,...(typeof value.username==='string'&&/^[a-z0-9][a-z0-9_.@-]{1,63}$/.test(value.username)?{username:value.username}:{})}};
 }catch{return {state:'unavailable'};}finally{clearTimeout(timer);}
}
export const PRIVATE_HEADERS={'Cache-Control':'private, no-store, max-age=0','Pragma':'no-cache','X-Content-Type-Options':'nosniff'};
