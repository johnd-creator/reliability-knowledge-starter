// Independent test composition matching the real workspace layout after its fix.
// Diagnostic output is test-only; no operational endpoint or session is used.
import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import EngineeringDraftProviders from '../../components/EngineeringDraftProviders';
import {PdmDraftProvider} from '../../components/PdmDraftContext';
import AuthenticatedWorkspace from '../../components/AuthenticatedWorkspace';
import PdmCenter from '../../components/PdmCenter';
import {usePdmDraft} from '../../components/PdmDraftContext';
import type {LocalSession} from '../../lib/local-session';
const identity=(window as unknown as {fixtureIdentity:LocalSession}).fixtureIdentity;
const debug:{kind:string;url?:string;status?:number}[]=[];
Object.assign(window,{fixtureFetchDebug:debug});
const originalFetch=window.fetch.bind(window);
window.fetch=(...args)=>{const url=String(args[0]);debug.push({kind:'request',url});const pending=originalFetch(...args);pending.then(r=>debug.push({kind:'response',url,status:r.status}),()=>debug.push({kind:'fetch-error',url}));return pending;};
window.addEventListener('focus',()=>debug.push({kind:'focus'}));
function Diagnostics(){const cache=usePdmDraft();return <output id="pdm-fixture-diagnostics">{JSON.stringify({recovery:cache?.recovery,busy:cache?.busy,completed:cache?.completed,intent:cache?.intent.current})}</output>;}
function WorkspaceFixture(){const [epoch,setEpoch]=useState(0);useEffect(()=>{Object.assign(window,{fixtureRemountPdm:(url:string)=>{window.history.replaceState({},'',url);setEpoch(x=>x+1);}});},[]);return <PdmCenter key={epoch} qaEnabled/>;}
createRoot(document.getElementById('root')!).render(<PdmDraftProvider><Diagnostics/><AuthenticatedWorkspace identity={identity}><EngineeringDraftProviders><WorkspaceFixture/></EngineeringDraftProviders></AuthenticatedWorkspace></PdmDraftProvider>);
