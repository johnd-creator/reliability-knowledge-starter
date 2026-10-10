"use client";
import {useCallback,useEffect,useState} from "react";
import {engineeringRequest,EngineeringHttpError} from "../lib/engineering-http";
import type {QaPage,QaSession} from "../lib/product-records";
export type QaState="disabled"|"loading"|"signed-out"|"denied"|"error"|"ready";
export function useQaRecords<T>(resource:"inspections"|"recommendations"|"cases"|"advisories"|"inbox",enabled:boolean,offset:number,query="") {
 const [state,setState]=useState<QaState>(enabled?"loading":"disabled"),[page,setPage]=useState<QaPage<T>|null>(null),[session,setSession]=useState<QaSession|null>(null),[refresh,setRefresh]=useState(0);
 const reload=useCallback(()=>setRefresh(n=>n+1),[]);
 useEffect(()=>{
  if(!enabled)return;
  let active=true;
  setPage(null);setSession(null);setState("loading");
  (async()=>{
   try {
    const who=await engineeringRequest("session") as QaSession;
    const next=await engineeringRequest(`${resource}?offset=${offset}&limit=25${query}`) as QaPage<T>;
    if(!Array.isArray(next.items)||!Number.isInteger(next.total)||next.total<0)throw new Error("INVALID_RESPONSE");
    if(active){setSession(who);setPage(next);setState("ready");}
   }catch(error){if(active){setPage(null);setSession(null);setState(error instanceof EngineeringHttpError&&error.status===401?"signed-out":error instanceof EngineeringHttpError&&[403,404].includes(error.status)?"denied":"error");}}
  })();
  const focus=()=>reload();window.addEventListener("focus",focus);
  return()=>{active=false;window.removeEventListener("focus",focus);};
 },[enabled,resource,offset,query,refresh,reload]);
 return {state,page,session,reload};
}
