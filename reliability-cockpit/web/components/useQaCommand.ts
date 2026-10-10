'use client';
import {useRef,useState} from 'react';
import {engineeringRequest,EngineeringHttpError} from '../lib/engineering-http';
import type {QaSession} from '../lib/product-records';
// A retry of the same failed intent retains its idempotency ID. No browser storage.
export function useQaCommand(session:QaSession,onExpired:()=>void) {
 const pending=useRef<{key:string;id:string}|null>(null),locked=useRef(false);
 const [busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
 async function run<T>(path:string,method:string,body:Record<string,unknown>):Promise<T|null>{
  if(locked.current)return null;locked.current=true;setBusy(true);setError('');setNotice('');
  const key=JSON.stringify([path,method,body]);if(pending.current?.key!==key)pending.current={key,id:crypto.randomUUID()};
  try {const result=await engineeringRequest(path,method,{...body,request_id:pending.current.id},session.csrf_token) as T;pending.current=null;setNotice('Saved in SYNTHETIC QA. No operational action authorized.');return result;}
  catch(e){if(e instanceof EngineeringHttpError){if(e.status===401)onExpired();setError(e.status===409?`${e.code}: your input is preserved. Read the latest revision, compare changes, then retry intentionally.`:e.code);}else setError('Request unavailable. Retry preserves the same request ID.');return null;}
  finally{locked.current=false;setBusy(false);}
 }
 return {run,busy,error,notice};
}
