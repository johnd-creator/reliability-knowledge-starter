"use client";
import {useCallback,useEffect,useRef,useState} from "react";
import {engineeringRequest,EngineeringHttpError} from "../lib/engineering-http";
import type {QaPage,QaSession} from "../lib/product-records";
import {notifyQaSession} from '../lib/qa-session-events';
export type QaState="blocked-schema"|"disabled"|"loading"|"signed-out"|"expired"|"denied"|"error"|"ready";
export function useQaRecords<T>(resource:"inspections"|"recommendations"|"cases"|"advisories"|"inbox",enabled:boolean,offset:number,query="") {
 const [state,setState]=useState<QaState>(enabled?"loading":"disabled"),[page,setPage]=useState<QaPage<T>|null>(null),[session,setSession]=useState<QaSession|null>(null),[refresh,setRefresh]=useState(0);
 const authenticated=useRef(false),generation=useRef(0);
 const reload=useCallback(()=>setRefresh(n=>n+1),[]);
 const invalidate=useCallback(()=>{generation.current++;setPage(null);setSession(null);setState('expired');notifyQaSession({state:'expired'});},[]);
 useEffect(()=>{
  if(!enabled)return;
  let active=true;const epoch=++generation.current;
  setPage(null);setSession(null);setState("loading");
  (async()=>{
   try {
    const who=await engineeringRequest("session") as QaSession;
    if(!active||epoch!==generation.current)return;
    authenticated.current=true;notifyQaSession({state:'ready',session:who});
    if(resource==='advisories'||resource==='inbox'){
     const capability=await engineeringRequest('advisory-capability') as {persistence:string};
     if(capability.persistence!=='READY'){if(active&&epoch===generation.current){setSession(who);setState('blocked-schema');}return;}
    }
    const pageSize=resource==='inspections'?1:25;
    const next=await engineeringRequest(`${resource}?offset=${offset}&limit=${pageSize}${query}`) as QaPage<T>;
    if(!Array.isArray(next.items)||!Number.isInteger(next.total)||next.total<0)throw new Error("INVALID_RESPONSE");
    if(active&&epoch===generation.current){setSession(who);setPage(next);setState("ready");}
   }catch(error){if(active&&epoch===generation.current){setPage(null);setSession(null);const next=error instanceof EngineeringHttpError&&error.status===401?(authenticated.current||error.code==='IDENTITY_REVOKED'?"expired":"signed-out"):error instanceof EngineeringHttpError&&[403,404].includes(error.status)?"denied":"error";setState(next);if(next==='expired'||next==='signed-out')notifyQaSession({state:'expired'});else if(next==='denied')notifyQaSession({state:'denied'});}}
  })();
  const focus=()=>reload();window.addEventListener("focus",focus);
  return()=>{active=false;window.removeEventListener("focus",focus);};
 },[enabled,resource,offset,query,refresh,reload]);
 return {state,page,session,reload,invalidate};
}
