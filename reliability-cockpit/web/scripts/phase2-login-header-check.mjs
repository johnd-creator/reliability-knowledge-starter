import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync,symlinkSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),temp=mkdtempSync(join(tmpdir(),'nadi-login-header-'));let count=0;
const check=(name,fn)=>{fn();count++;console.log('PASS '+name);};
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','components/DevelopmentStatus.tsx','components/QaProductBoundary.tsx','lib/login-navigation.ts','--outDir',temp,'--rootDir','.','--module','commonjs','--target','ES2022','--jsx','react-jsx','--esModuleInterop','--skipLibCheck','--resolveJsonModule','--moduleResolution','node'],{stdio:'pipe'});symlinkSync(resolve('node_modules'),join(temp,'node_modules'));
 const {safeReturnDestination,loginHref}=require(join(temp,'lib/login-navigation.js'));
 check('exact QA destinations and version-bound record links survive',()=>{for(const path of ['/pdm','/engineering/cases?record=case:abc','/engineering/local?resource=inspections&record=inspection:abc','/recommendations'])assert.equal(safeReturnDestination(path),path);});
 check('external scheme protocol-relative backslash and encoded tricks rejected',()=>{for(const path of ['https://evil.test','//evil.test','/\\evil.test','javascript:alert(1)','/pdm\n','/%2f%2fevil.test','/pdm/../engineering/cases','/pdm?record=%252f%252fevil','/pdm?record=x&record=y','/pdm?next=https://evil.test','/login','/api/engineering-qa/session',null,['/pdm']])assert.equal(safeReturnDestination(path),'/engineering/local',String(path));});
 check('return link is encoded and expiry is explicit',()=>{const url=new URL(loginHref('/pdm?record=inspection:abc',true),'https://localhost:3000');assert.equal(url.pathname,'/login');assert.equal(url.searchParams.get('returnTo'),'/pdm?record=inspection:abc');assert.equal(url.searchParams.get('expired'),'1');});
 const {developmentWarnings}=require(join(temp,'lib/development-status-view.js'));
 const good={sha:'a'.repeat(40),backend_sha:'a'.repeat(40),branch:'DETACHED',dirty:true,backend:'AVAILABLE',factual_backend:'AVAILABLE',database:'DISPOSABLE_TEST',database_identity:'synthetic_test',engineering:true,stale:false,compatibility:'SAME_SOURCE'};
 check('dirty reviewed development is explicit without a fake integrity failure',()=>assert.deepEqual(developmentWarnings(good),[]));
 check('stale mismatch unknown and unavailable remain actionable',()=>{for(const patch of [{stale:true},{sha:'UNKNOWN'},{backend_sha:'b'.repeat(40),compatibility:'UNVERIFIED'},{backend:'UNAVAILABLE'},{factual_backend:'UNAVAILABLE'},{dirty:null},{database_identity:'UNKNOWN'}])assert(developmentWarnings({...good,...patch}).length);assert(developmentWarnings(null).length);});
 const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),Panel=require(join(temp,'components/DevelopmentStatus.js')).DevelopmentStatusPanel,Boundary=require(join(temp,'components/QaProductBoundary.js')).default;
 const render=(Component,props)=>renderToStaticMarkup(React.createElement(Component,props));
 check('full technical provenance retained behind disclosure',()=>{const html=render(Panel,{status:good});for(const text of ['Detail teknis',good.sha,'SHA backend QA','synthetic_test','Draf lokal'])assert(html.includes(text));assert(!html.includes(' open=""'));});
 check('critical warning renders outside collapsed technical details',()=>{const html=render(Panel,{status:{...good,stale:true}});assert(html.indexOf('role="alert"')>html.indexOf('</details>'));assert(html.includes('STALE / mismatch'));});
 check('every QA boundary state is distinct and never embeds credentials',()=>{const states=['ready','loading','signed-out','expired','denied','error','blocked-schema','disabled'];for(const state of states){const html=render(Boundary,{state,reload(){}});assert(!html.includes('type="password"'));assert(!html.includes('name="username"'));if(['signed-out','expired'].includes(state))assert(html.includes('/login?returnTo='));}assert.notEqual(render(Boundary,{state:'signed-out',reload(){}}),render(Boundary,{state:'expired',reload(){}}));});
 check('diagnostic workspace no longer mounts local credentials inline',()=>{const s=readFileSync('components/EngineeringQa.tsx','utf8');assert(!s.includes('<LocalLogin'));assert(s.includes('QaSignInRequired'));assert(s.includes("engineeringRequest('session/logout','POST'"));});
 console.log('Login/header regression checks passed: '+count);
}finally{rmSync(temp,{recursive:true,force:true});}
