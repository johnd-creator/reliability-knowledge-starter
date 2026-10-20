'use client';
import {createContext,useCallback,useContext,useEffect,useMemo,useState,useRef,type RefObject,type ReactNode} from 'react';
import type {Entry} from '../lib/pdm-input';
import type {Inspection} from '../lib/product-records';
import {QA_SESSION_EVENT,type QaSessionEvent} from '../lib/qa-session-events';
type Recovery={subject:string;entry:Entry;base?:Inspection};
type IntentRef=RefObject<{key:string;id:string}|null>;
type Cache={completed:Inspection|null;complete:(row:Inspection)=>void;consumeCompletion:()=>void;intent:IntentRef;intentFor:(key:string)=>IntentRef;recovery:Recovery|null;busy:boolean;begin:()=>number|null;end:(token:number)=>void;keep:(value:Recovery)=>void;clear:()=>void;clearSaved:(subject:string,entry:Entry,baseId?:string)=>void;discard:()=>boolean};
const Context=createContext<Cache|null>(null);
// In-memory, per-workspace recovery. Never store inspection content or identity in browser storage.
export function PdmDraftProvider({children}:{children:ReactNode}){
 const intent=useRef<{key:string;id:string}|null>(null),current=useRef<Recovery|null>(null),pending=useRef<number|null>(null),sequence=useRef(0),sessionKey=useRef<string|null>(null);
 const [recovery,setRecovery]=useState<Recovery|null>(null),[busy,setBusy]=useState(false),[completed,setCompleted]=useState<Inspection|null>(null);
 const slots=useRef(new Map<string,IntentRef>());
 const intentFor=useCallback((key:string)=>{let slot=slots.current.get(key);if(!slot){slot=slots.current.size===0?intent:{current:null};slots.current.set(key,slot);}return slot;},[]);
 const keep=useCallback((value:Recovery)=>{current.current=value;setRecovery(value);},[]);
 const clear=useCallback(()=>{current.current=null;setRecovery(null);setCompleted(null);for(const slot of slots.current.values())slot.current=null;slots.current.clear();intent.current=null;},[]);
 const clearSaved=useCallback((subject:string,entry:Entry,baseId?:string)=>{const saved=current.current;if(saved?.subject===subject&&saved.base?.record_id===baseId&&JSON.stringify(saved.entry)===JSON.stringify(entry)){current.current=null;setRecovery(null);}},[]);
 const complete=useCallback((row:Inspection)=>setCompleted(row),[]),consumeCompletion=useCallback(()=>setCompleted(null),[]);
 const begin=useCallback(()=>{if(pending.current!==null)return null;const token=++sequence.current;pending.current=token;setBusy(true);return token;},[]);
 const end=useCallback((token:number)=>{if(pending.current===token){pending.current=null;setBusy(false);}},[]);
 useEffect(()=>{
  const verify=(event:Event)=>{
   const detail=(event as CustomEvent<QaSessionEvent>).detail;
   if(detail.state!=='ready'){clear();sessionKey.current=null;pending.current=null;setBusy(false);return;}
   const who=detail.session;
   const key=JSON.stringify([who.subject,[...who.roles].sort(),[...who.asset_ids].sort()]);
   const saved=current.current;
   if((sessionKey.current!==null&&sessionKey.current!==key)||(saved&&(who.subject!==saved.subject||!who.roles.includes('AUTHOR')||!who.asset_ids.includes(saved.entry.asset)))){clear();pending.current=null;setBusy(false);}
   sessionKey.current=key;
  };
  window.addEventListener(QA_SESSION_EVENT,verify);return()=>window.removeEventListener(QA_SESSION_EVENT,verify);
 },[clear]);
 const discard=useCallback(()=>{if(pending.current!==null)return false;if(current.current&&!window.confirm('Buang isian inspeksi yang belum disimpan?'))return false;clear();return true;},[clear]);
 const value=useMemo(()=>({completed,complete,consumeCompletion,recovery,busy,begin,end,keep,clear,clearSaved,discard,intent,intentFor}),[completed,complete,consumeCompletion,recovery,busy,begin,end,keep,clear,clearSaved,discard,intentFor]);
 return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function usePdmDraft(){return useContext(Context);}
