'use client';
import type {Inspection,QaSession} from '../lib/product-records';
import {useQaCommand} from './useQaCommand';
import {usePdmDraft} from './PdmDraftContext';

// The lock survives a focus refresh that unmounts the editor during an HTTP write.
export function usePdmCommand(session:QaSession,onExpired:()=>void){
 const cache=usePdmDraft(),command=useQaCommand(session,onExpired,cache?(path,method)=>cache.intentFor(JSON.stringify([session.subject,method,path])):undefined);
 async function run<T>(path:string,method:string,body:Record<string,unknown>):Promise<T|null>{
  const token=cache?.begin();if(cache&&token===null)return null;
  try{const result=await command.run<T>(path,method,body);if(result&&body.draft&&((method==='POST'&&path==='inspections')||(method==='PUT'&&/^inspections\/[^/]+$/.test(path))))cache?.complete(result as unknown as Inspection);return result;}finally{if(token!==undefined&&token!==null)cache?.end(token);}
 }
 return {...command,run,busy:command.busy||!!cache?.busy};
}
