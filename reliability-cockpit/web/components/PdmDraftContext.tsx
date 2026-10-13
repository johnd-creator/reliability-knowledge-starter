'use client';
import {createContext,useCallback,useContext,useState,useRef,type RefObject,type ReactNode} from 'react';
import type {Entry} from '../lib/pdm-input';
import type {Inspection} from '../lib/product-records';
// In-memory unsaved input only. Never persisted or restored for another identity.
interface Recovery {subject:string;entry:Entry;base?:Inspection;}
const Context=createContext<{recovery:Recovery|null;keep:(value:Recovery)=>void;clear:()=>void;intent:RefObject<{key:string;id:string}|null>}|null>(null);
export function PdmDraftProvider({children}:{children:ReactNode}){
 const intent=useRef<{key:string;id:string}|null>(null);
 const [recovery,setRecovery]=useState<Recovery|null>(null);
 const clear=useCallback(()=>{setRecovery(null);intent.current=null;},[]),keep=useCallback((value:Recovery)=>setRecovery(value),[]);
 return <Context.Provider value={{recovery,keep,clear,intent}}>{children}</Context.Provider>;
}
export function usePdmDraft(){return useContext(Context);}
