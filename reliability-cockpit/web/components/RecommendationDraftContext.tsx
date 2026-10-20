'use client';
import {createContext,useCallback,useContext,useEffect,useMemo,useRef,useState,type ReactNode,type RefObject} from 'react';
import {QA_SESSION_EVENT,type QaSessionEvent} from '../lib/qa-session-events';
import {recommendationSessionKey,recoverableRecommendation,sameRecommendationDraft,type RecommendationDraftValues,type RecommendationRecovery} from '../lib/recommendation-draft';

type IntentRef=RefObject<{key:string;id:string}|null>;
type Cache={intent:IntentRef;intentFor:(key:string)=>IntentRef;recovery:RecommendationRecovery|null;busy:boolean;keep:(value:RecommendationRecovery)=>void;clear:()=>void;clearSaved:(subject:string,record:string,draft:RecommendationDraftValues)=>void;discard:()=>boolean;begin:()=>number|null;end:(token:number)=>void};
const Context=createContext<Cache|null>(null);
// Layout-owned memory only: never persist human record content in browser storage.
export function RecommendationDraftProvider({children}:{children:ReactNode}){
 const intent=useRef<{key:string;id:string}|null>(null),current=useRef<RecommendationRecovery|null>(null),sessionKey=useRef<string|null>(null),pending=useRef<number|null>(null),sequence=useRef(0);
 const [recovery,setRecovery]=useState<RecommendationRecovery|null>(null),[busy,setBusy]=useState(false);
 const slots=useRef(new Map<string,IntentRef>());
 const intentFor=useCallback((key:string)=>{let slot=slots.current.get(key);if(!slot){slot=slots.current.size===0?intent:{current:null};slots.current.set(key,slot);}return slot;},[]);
 const keep=useCallback((value:RecommendationRecovery)=>{current.current=value;setRecovery(value);},[]);
 const clear=useCallback(()=>{current.current=null;setRecovery(null);for(const slot of slots.current.values())slot.current=null;slots.current.clear();intent.current=null;},[]);
 const clearSaved=useCallback((subject:string,record:string,draft:RecommendationDraftValues)=>{const saved=current.current;if(saved?.subject===subject&&saved.base.record_id===record&&sameRecommendationDraft(saved.draft,draft)){current.current=null;setRecovery(null);}},[]);
 const begin=useCallback(()=>{if(pending.current!==null)return null;const token=++sequence.current;pending.current=token;setBusy(true);return token;},[]);
 const end=useCallback((token:number)=>{if(pending.current===token){pending.current=null;setBusy(false);}},[]);
 const discard=useCallback(()=>{if(pending.current!==null)return false;if(current.current&&!window.confirm('Buang perubahan Recommendation yang belum disimpan?'))return false;clear();return true;},[clear]);
 useEffect(()=>{
  const identity=(event:Event)=>{
   const detail=(event as CustomEvent<QaSessionEvent>).detail;
   if(!detail)return;
   if(['expired','denied','disabled','signed-out'].includes(detail.state)){clear();sessionKey.current=null;pending.current=null;setBusy(false);return;}
   if(detail.state!=='ready'||!detail.session)return; // Loading/outage is not revocation.
   const key=recommendationSessionKey(detail.session);
   if((sessionKey.current!==null&&sessionKey.current!==key)||(current.current&&!recoverableRecommendation(current.current,detail.session))){clear();pending.current=null;setBusy(false);}
   sessionKey.current=key;
  };
  window.addEventListener(QA_SESSION_EVENT,identity);
  return()=>window.removeEventListener(QA_SESSION_EVENT,identity);
 },[clear]);
 const value=useMemo(()=>({intent,intentFor,recovery,busy,keep,clear,clearSaved,discard,begin,end}),[intentFor,recovery,busy,keep,clear,clearSaved,discard,begin,end]);
 return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useRecommendationDraft(){return useContext(Context);}
