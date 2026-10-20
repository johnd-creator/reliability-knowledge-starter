'use client';
import type {QaSession} from '../lib/product-records';
import {useQaCommand} from './useQaCommand';
import {useCaseDraft} from './CaseDraftContext';

// The lock survives a focus refresh that unmounts the editor during an HTTP write.
export function useCaseCommand(session:QaSession,onExpired:()=>void){
 const cache=useCaseDraft(),command=useQaCommand(session,onExpired,cache?(path,method)=>cache.intentFor(JSON.stringify([session.subject,method,path])):undefined);
 async function run<T>(path:string,method:string,body:Record<string,unknown>):Promise<T|null>{
  const token=cache?.begin();if(cache&&token===null)return null;
  try{return await command.run<T>(path,method,body);}finally{if(token!==undefined&&token!==null)cache?.end(token);}
 }
 return {...command,run,busy:command.busy||!!cache?.busy};
}
