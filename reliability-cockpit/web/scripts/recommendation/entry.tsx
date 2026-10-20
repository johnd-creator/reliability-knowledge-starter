// Browser regression entry: real components and memory provider; no listening service.
import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import RecommendationActions from '../../components/RecommendationActions';
import {RecommendationDraftProvider,useRecommendationDraft} from '../../components/RecommendationDraftContext';
import {notifyQaSession} from '../../lib/qa-session-events';
import {recommendationSessionKey} from '../../lib/recommendation-draft';
import type {Recommendation,QaSession} from '../../lib/product-records';
const initial:Recommendation={record_id:'recommendation:fixture',canonical_asset_id:'asset:qa',revision:7,status:'DRAFT',created_at:'2026-10-20T00:00:00Z',updated_at:'2026-10-20T00:00:00Z',created_by:'author',review:null,case_ref:'case:fixture',rationale:'Original rationale',proposed_action:'Original action',priority:'HUMAN',responsible_team_ref:null,responsible_person_ref:null,target_date:null,follow_up_status:'PROPOSED',existing_work_order_ref:null,reviewed_case:null,completion_verification:null,supporting_evidence:[],provenance:'SYNTHETIC_QA'};
const identity:QaSession={subject:'author',roles:['AUTHOR'],asset_ids:['asset:qa'],csrf_token:'synthetic-only'};
function Fixture(){
 const [row,setRow]=useState(initial),[session,setSession]=useState(identity),[mounted,setMounted]=useState(true),cache=useRecommendationDraft();
 useEffect(()=>{notifyQaSession({state:'ready',session});},[session]);
 useEffect(()=>{
  Object.assign(window,{recommendationFixture:{mount:setMounted,row:(patch:Partial<Recommendation>)=>setRow(old=>({...old,...patch})),session:(patch:Partial<QaSession>)=>setSession(old=>({...old,...patch})),expire:()=>notifyQaSession({state:'expired'}),transient:()=>window.dispatchEvent(new Event('focus'))}});
 },[]);
 return <main><output data-testid="recovery">{cache?.recovery?JSON.stringify(cache.recovery):'EMPTY'}</output><output data-testid="busy">{String(cache?.busy)}</output><a href="/other">Leave module</a>{mounted&&<RecommendationActions key={row.record_id+':'+row.revision+':'+recommendationSessionKey(session)} row={row} session={session} onChanged={()=>{setMounted(false);fetch('/api/engineering-qa/recommendations/recommendation%3Afixture').then(response=>response.json()).then(setRow).finally(()=>setMounted(true));}} onExpired={()=>notifyQaSession({state:'expired'})}/>}</main>;
}
createRoot(document.getElementById('root')!).render(<RecommendationDraftProvider><Fixture/></RecommendationDraftProvider>);
