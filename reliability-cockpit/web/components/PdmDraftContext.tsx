'use client';
import {createContext,useCallback,useContext,useState,type ReactNode} from 'react';
import type {Entry} from '../lib/pdm-input';
import type {Inspection} from '../lib/product-records';
// In-memory unsaved input only. Never persisted or restored for another identity.
interface Recovery {subject:string;entry:Entry;base?:Inspection;}
const Context=createContext<{recovery:Recovery|null;keep:(value:Recovery)=>void;clear:()=>void}|null>(null);
export function PdmDraftProvider({children}:{children:ReactNode}){
 const [recovery,setRecovery]=useState<Recovery|null>(null);
 const clear=useCallback(()=>setRecovery(null),[]),keep=useCallback((value:Recovery)=>setRecovery(value),[]);
 return <Context.Provider value={{recovery,keep,clear}}>{children}</Context.Provider>;
}
export function usePdmDraft(){return useContext(Context);}
