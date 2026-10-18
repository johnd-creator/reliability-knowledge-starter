'use client';
import {createContext,useCallback,useContext,useMemo,useState,useRef,type RefObject,type ReactNode} from 'react';
import type {CaseDraft,CaseRecord} from '../lib/case-records';
type Recovery={subject:string;draft:CaseDraft;base?:CaseRecord};
type Cache={intent:RefObject<{key:string;id:string}|null>;recovery:Recovery|null;keep:(value:Recovery)=>void;clear:()=>void;discard:()=>boolean};
const Context=createContext<Cache|null>(null);
// In-memory, per-workspace recovery. Never store case content or identity in browser storage.
export function CaseDraftProvider({children}:{children:ReactNode}){
 const intent=useRef<{key:string;id:string}|null>(null);
 const [recovery,keep]=useState<Recovery|null>(null);
 const clear=useCallback(()=>{keep(null);intent.current=null;},[]);
 const discard=useCallback(()=>{if(recovery&&!window.confirm('Buang isian Case yang belum disimpan?'))return false;clear();return true;},[recovery,clear]);
 const value=useMemo(()=>({recovery,keep,clear,discard,intent}),[recovery,clear,discard]);
 return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useCaseDraft(){return useContext(Context);}
