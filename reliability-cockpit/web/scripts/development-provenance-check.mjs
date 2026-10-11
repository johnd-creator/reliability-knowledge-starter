import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync,mkdirSync,writeFileSync,chmodSync,symlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const require=createRequire(import.meta.url),temp=mkdtempSync(join(tmpdir(),'nadi-provenance-'));
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','lib/development-provenance.ts','--outDir',temp,'--module','commonjs','--target','ES2022','--esModuleInterop','--skipLibCheck']);
 const {approvalDigest,approvedPair,readApproval}=require(join(temp,'development-provenance.js'));
 const front='a'.repeat(40),back='b'.repeat(40);
 const approval={version:1,frontend_sha:front,backend_sha:back,frontend_root:'/fixture/front',backend_root:'/fixture/backend',compatibility_digest:'c'.repeat(64),launcher_source_sha:'d'.repeat(40),launcher_sha256:'d'.repeat(64),backup_sha256:'e'.repeat(64),approved_at:'2026-10-11T00:00:00Z'};
 const e={approval,approval_id:approvalDigest(approval)};
 assert.ok(approvedPair(e,front,front,back,false,back,false));
 for(const args of [[null,front,front,back,false,back,false],[e,front,'f'.repeat(40),back,false,back,false],[e,front,front,'f'.repeat(40),false,back,false],[e,front,front,back,true,back,false],[e,front,front,back,false,back,true],[e,front,front,back,false,'f'.repeat(40),false],[e,front,front,back,null,back,false]])assert.equal(approvedPair(...args),false);
 assert.equal(approvedPair({...e,approval_id:'f'.repeat(64)},front,front,back,false,back,false),false);
 assert.equal(approvedPair({...e,approval:{...approval,backend_sha:front}},front,front,back,false,back,false),false);
 const base=join(temp,'managed'),root=join(base,'frontend'),state=join(base,'state'),web=join(root,'reliability-cockpit','web');
 mkdirSync(web,{recursive:true});mkdirSync(state);
 const a={...approval,frontend_root:root,backend_root:join(base,'backend')},approved={approval:a,approval_id:approvalDigest(a)},path=join(state,'frontend-approval-aaaa.json');
 writeFileSync(path,JSON.stringify(approved),{mode:0o600});
 assert.deepEqual(await readApproval(path,web),approved);
 chmodSync(path,0o644);assert.equal(await readApproval(path,web),null);chmodSync(path,0o600);
 const link=join(state,'frontend-approval-bbbb.json');symlinkSync(path,link);assert.equal(await readApproval(link,web),null);
 assert.equal(await readApproval(path,join(base,'other','reliability-cockpit','web')),null);
 writeFileSync(path,JSON.stringify({...approved,approval_id:'f'.repeat(64)}));assert.equal(await readApproval(path,web),null);
 console.log('Development provenance checks PASS: approved exact pair, missing/forged/stale/dirty/unknown identities refused');
}finally{rmSync(temp,{recursive:true,force:true});}
