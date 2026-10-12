import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,symlinkSync,rmSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
const require=createRequire(import.meta.url),temp=mkdtempSync(join(tmpdir(),'nadi-dev-status-'));let count=0;
const check=(name,fn)=>{fn();count++;console.log('PASS '+name);};
const navigation=require.resolve('next/navigation'),previous=require.cache[navigation];
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','components/DevelopmentStatus.tsx','app/(workspace)/layout.tsx','--outDir',temp,'--rootDir','.','--module','commonjs','--target','ES2022','--jsx','react-jsx','--esModuleInterop','--skipLibCheck','--resolveJsonModule','--moduleResolution','node'],{stdio:'pipe'});
 symlinkSync(resolve('node_modules'),join(temp,'node_modules'));
 require.cache[navigation]={id:navigation,filename:navigation,loaded:true,exports:{usePathname:()=>'/'}};
 const {developmentTone}=require(join(temp,'components/DevelopmentStatus.js'));
 const snapshot={branch:'DEMO',sha:'a'.repeat(40),launched_sha:'a'.repeat(40),backend_sha:'b'.repeat(40),dirty:false,stale:false,compatibility:'VERIFIED_SOURCE_EQUIVALENT',compatibility_approval:'c'.repeat(64),backend:'AVAILABLE',factual_backend:'AVAILABLE'};
 check('approved split-source pair is verified',()=>assert.equal(developmentTone(snapshot),'verified'));
 check('same-source contract is verified',()=>assert.equal(developmentTone({...snapshot,backend_sha:snapshot.sha,compatibility:'SAME_SOURCE',compatibility_approval:null}),'verified'));
 check('dirty uncommitted source remains warning',()=>assert.equal(developmentTone({...snapshot,dirty:true}),'warning'));
 check('stale release remains warning',()=>assert.equal(developmentTone({...snapshot,stale:true}),'warning'));
 check('unapproved mismatch remains warning',()=>assert.equal(developmentTone({...snapshot,compatibility:'UNVERIFIED'}),'warning'));
 check('approval and loaded source identity cannot be missing',()=>{for(const patch of [{compatibility_approval:null},{launched_sha:'d'.repeat(40)},{sha:'UNKNOWN'},{backend_sha:'UNKNOWN'},{dirty:null},{compatibility:'UNKNOWN'}])assert.equal(developmentTone({...snapshot,...patch}),'warning');});
 check('service failure remains warning even with approved release',()=>{for(const patch of [{backend:'UNAVAILABLE'},{factual_backend:'UNAVAILABLE'}])assert.equal(developmentTone({...snapshot,...patch}),'warning');});
 check('unretrievable endpoint is distinct unavailable',()=>assert.equal(developmentTone(null),'unavailable'));
 const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),Layout=require(join(temp,'app/(workspace)/layout.js')).default;
 const env={NODE_ENV:process.env.NODE_ENV,NADI_LIVE_DEV:process.env.NADI_LIVE_DEV};
 try{
  for(const [mode,flag,expected]of [['production','true',false],['development','false',false],['development','true',true]]){
   process.env.NODE_ENV=mode;process.env.NADI_LIVE_DEV=flag;
   const markup=renderToStaticMarkup(React.createElement(Layout,null,React.createElement('h1',null,'Dashboard')));
   check('explicit dev gate '+mode+'/'+flag,()=>{assert.equal(markup.includes('dev-status-trigger'),expected);assert.doesNotMatch(markup,/nadi-development-status/);assert.match(markup,/<h1>Dashboard<\/h1>/);});
  }
 }finally{for(const[k,v]of Object.entries(env)){if(v===undefined)delete process.env[k];else process.env[k]=v;}}
 check('status endpoint and approval rules are not UI presentation',()=>{const layout=readFileSync('app/(workspace)/layout.tsx','utf8');assert.match(layout,/developmentStatus=/);assert.doesNotMatch(layout,/DevelopmentStatus \/>\}\{children\}/);});
 console.log('Development status checks PASS '+count);
}finally{if(previous)require.cache[navigation]=previous;else delete require.cache[navigation];rmSync(temp,{recursive:true,force:true});}
