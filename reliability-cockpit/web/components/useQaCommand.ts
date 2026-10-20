'use client';
import { idText, errorLabel } from "../lib/id-copy";
import {useRef,useState,type RefObject} from 'react';
import {engineeringRequest,EngineeringHttpError} from '../lib/engineering-http';
import type {QaSession} from '../lib/product-records';
// A retry of the same failed intent retains its idempotency ID. No browser storage.
type IntentRef=RefObject<{key:string;id:string}|null>;
export function useQaCommand(session:QaSession,onExpired:()=>void,intent?:IntentRef|((path:string,method:string)=>IntentRef)) {
 const localPending=useRef<{key:string;id:string}|null>(null),locked=useRef(false);
 const [busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
 async function run<T>(path:string,method:string,body:Record<string,unknown>):Promise<T|null>{
  if(locked.current)return null;locked.current=true;setBusy(true);setError('');setNotice('');
  const pending=typeof intent==='function'?intent(path,method):intent??localPending;
  const key=JSON.stringify([path,method,body]);if(pending.current?.key!==key)pending.current={key,id:crypto.randomUUID()};
  const requestId=pending.current.id;
  try {const result=await engineeringRequest(path,method,{...body,request_id:requestId},session.csrf_token) as T;if(pending.current?.id!==requestId)return null;pending.current=null;setNotice(idText("Saved in SYNTHETIC QA. No operational action authorized."));return result;}
  catch(e){if(pending.current?.id!==requestId)return null;if(e instanceof EngineeringHttpError){if(e.status===401)onExpired();setError(e.status===409?`${errorLabel(e.code)} ${idText("Input retained; reload revision before retrying.")}`:errorLabel(e.code));}else setError(idText("Request unavailable. Retry preserves the same request ID."));return null;}
  finally{locked.current=false;setBusy(false);}
 }
 return {run,busy,error,notice};
}
