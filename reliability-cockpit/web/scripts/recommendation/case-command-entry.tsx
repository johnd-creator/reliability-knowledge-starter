// Focused browser fixture for the real Case provider + command hook, no server.
import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {CaseDraftProvider,useCaseDraft} from '../../components/CaseDraftContext';
import {useCaseCommand} from '../../components/useCaseCommand';
import {notifyQaSession,type QaSessionEvent} from '../../lib/qa-session-events';
import {emptyDraft} from '../../lib/case-records';
import type {QaSession} from '../../lib/product-records';
const initial:QaSession={subject:'author',roles:['AUTHOR'],asset_ids:['asset:qa'],csrf_token:'synthetic-only'};
function Editor({session,onResult}:{session:QaSession;onResult:(value:unknown)=>void}){
 const cache=useCaseDraft(),command=useCaseCommand(session,()=>{Object.assign(window,{caseExpiredCalls:((window as unknown as {caseExpiredCalls?:number}).caseExpiredCalls??0)+1});});
 async function run(kind:string){const captured=cache?.recovery;const result=await command.run('cases/case%3Afixture/'+kind,'POST',{expected_revision:3,text:'Unchanged synthetic intent'});if(result&&kind==='save'&&captured)cache?.clearSaved(captured.subject,captured.draft,captured.base?.case_id);onResult(result);}
 return <section><button id="case-note" disabled={command.busy} onClick={()=>run('notes')}>NOTE</button><button id="case-linked" disabled={command.busy} onClick={()=>run('linked-recommendation')}>Linked Recommendation</button><button id="case-save" disabled={command.busy} onClick={()=>run('save')}>Save captured draft</button><output id="case-error">{command.error}</output></section>;
}
function Fixture(){
 const cache=useCaseDraft(),[session,setSession]=useState(initial),[mounted,setMounted]=useState(true),[results,setResults]=useState<unknown[]>([]),[primed,setPrimed]=useState(false);
 useEffect(()=>{const timer=setTimeout(()=>{notifyQaSession({state:'ready',session:initial});setPrimed(true);},0);return()=>clearTimeout(timer);},[]);
 useEffect(()=>{
  Object.assign(window,{caseFixture:{
   mount:setMounted,
   ready:(patch:Partial<QaSession>)=>{const next={...session,...patch};setSession(next);notifyQaSession({state:'ready',session:next});},
   revoke:(state:'expired'|'denied'|'disabled')=>notifyQaSession({state} as QaSessionEvent),
   keep:(title:string)=>cache?.keep({subject:session.subject,draft:{...emptyDraft('asset:qa'),title,problem_statement:'synthetic statement'}}),
  }});
 },[cache,session]);
 return <main><output id="case-primed">{String(primed)}</output><output id="case-subject">{session.subject}</output><output id="case-cache">{JSON.stringify({recovery:cache?.recovery,intent:cache?.intent.current,busy:cache?.busy})}</output><output id="case-results">{JSON.stringify(results)}</output>{mounted&&<Editor key={JSON.stringify([session.subject,session.roles,session.asset_ids])} session={session} onResult={result=>setResults(old=>[...old,result])}/>}</main>;
}
createRoot(document.getElementById('root')!).render(<CaseDraftProvider><Fixture/></CaseDraftProvider>);
