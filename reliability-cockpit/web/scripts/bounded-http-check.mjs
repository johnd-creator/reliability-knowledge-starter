import assert from 'node:assert/strict';
import ts from 'typescript';
import {readFileSync} from 'node:fs';
const output=ts.transpileModule(readFileSync('lib/bounded-http.ts','utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
const {readBounded}=await import('data:text/javascript;base64,'+Buffer.from(output).toString('base64'));
const make=chunks=>new ReadableStream({start(c){for(const chunk of chunks)c.enqueue(new Uint8Array(chunk));c.close();}});
let n=0;
async function check(label,fn){await fn();n++;console.log('PASS '+label);}
await check('exact cap byte preservation',async()=>assert.deepEqual([...await readBounded(make([[0,255],[1,2]]),4,new AbortController().signal)],[0,255,1,2]));
await check('one byte overflow rejected',async()=>assert.rejects(readBounded(make([[1,2],[3]]),2,new AbortController().signal),/BODY_TOO_LARGE/));
await check('large first chunk rejected',async()=>assert.rejects(readBounded(make([Array(10000).fill(1)]),3,new AbortController().signal),/BODY_TOO_LARGE/));
await check('null body preserved',async()=>assert.equal((await readBounded(null,1,new AbortController().signal)).length,0));
await check('blocked body deadline enforced',async()=>{const controller=new AbortController();const body=new ReadableStream({pull(){return new Promise(()=>{});}});setTimeout(()=>controller.abort(),20);await assert.rejects(readBounded(body,10,controller.signal),/DEADLINE_EXCEEDED/);});
await check('aborted operation denied',async()=>{const c=new AbortController();c.abort();await assert.rejects(readBounded(make([[1]]),1,c.signal),/DEADLINE_EXCEEDED/);});
await check('invalid caps rejected',async()=>assert.rejects(readBounded(make([[1]]),0,new AbortController().signal),/INVALID_BODY_LIMIT/));
await check('upstream overflow same safe contract',async()=>assert.rejects(readBounded(make([[1],[2],[3]]),2,new AbortController().signal),/BODY_TOO_LARGE/));
console.log('Bounded HTTP checks passed: '+n);
