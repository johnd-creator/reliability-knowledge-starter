import assert from 'node:assert/strict';
import ts from 'typescript';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(import.meta.url);
const nextUrl=pathToFileURL(require.resolve('next/server')).href;
const {NextRequest}=await import(nextUrl);
const compile=s=>ts.transpileModule(s,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
const url=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const bounded=url(compile(readFileSync('lib/bounded-http.ts','utf8')));
const routeSource=compile(readFileSync('app/api/engineering-qa/[...path]/route.ts','utf8')).replaceAll('next/server',nextUrl).replaceAll('../../../../lib/bounded-http',bounded);
const route=await import(url(routeSource));
const previousFetch=globalThis.fetch;const saved={...process.env};
const context={params:Promise.resolve({path:['inspections']})};
const request=(body,extra={})=>new NextRequest('https://qa.example.invalid/api/engineering-qa/inspections',{method:'POST',body,duplex:'half',headers:{'content-type':'application/json',origin:'https://qa.example.invalid','x-csrf-token':'fixture','x-actor':'forged','authorization':'forged','x-forwarded-host':'forged'},...extra});
let count=0;
async function check(name,fn){await fn();count++;console.log('PASS '+name);}
try {
 process.env.NODE_ENV='development';process.env.NADI_ENGINEERING_QA_ENABLED='true';process.env.NADI_QA_BACKEND_URL='http://127.0.0.1:13036';
 await check('bounded actual Next proxy preserves payload and filters identity headers',async()=>{
  globalThis.fetch=async(target,options)=>{assert.equal(options.headers.has('authorization'),false);assert.equal(options.headers.has('x-actor'),false);assert.equal(options.headers.has('x-forwarded-host'),false);assert.equal(options.redirect,'error');assert.ok(options.signal);assert.equal(new TextDecoder().decode(options.body),'{}');return new Response('{"unit":"Ton/h","value":0,"quality":"UNKNOWN"}',{headers:{'content-type':'application/json','set-cookie':'__Host-nadi_session=fixture; Secure; HttpOnly; Path=/'}});};
  const response=await route.POST(request('{}'),context);assert.equal(response.status,200);assert.equal((await response.json()).unit,'Ton/h');assert.match(response.headers.get('set-cookie'),/Secure/);
 });
 await check('oversized chunked request never calls backend',async()=>{globalThis.fetch=async()=>{throw Error('must not fetch');};const stream=new ReadableStream({start(c){c.enqueue(new Uint8Array(1024*1024+1));c.close();}});const response=await route.POST(request(stream),context);assert.equal(response.status,413);});
 await check('oversized upstream is sanitized502',async()=>{globalThis.fetch=async()=>new Response(new Uint8Array(2*1024*1024+1));const response=await route.POST(request('{}'),context);assert.equal(response.status,502);assert.deepEqual(await response.json(),{detail:{code:'QA_BODY_LIMIT_EXCEEDED'}});});
 await check('exact byte limit accepts payload',async()=>{globalThis.fetch=async()=>new Response('ok');const response=await route.POST(request('x'.repeat(1024*1024)),context);assert.equal(response.status,200);});
 await check('declared length cap precedes reading',async()=>{const response=await route.POST(request('{}',{headers:{'content-length':String(1024*1024+1)}}),context);assert.equal(response.status,413);});
 await check('production stays disabled',async()=>{process.env.NODE_ENV='production';const response=await route.POST(request('{}'),context);assert.equal(response.status,404);process.env.NODE_ENV='development';});
 await check('unsafe non-loopback target denied',async()=>{process.env.NADI_QA_BACKEND_URL='https://source.example.invalid';const response=await route.POST(request('{}'),context);assert.equal(response.status,503);process.env.NADI_QA_BACKEND_URL='http://127.0.0.1:13036';});
 await check('upstream error never leaks URL/body/secrets',async()=>{globalThis.fetch=async()=>{throw Error('secret-token https://internal.invalid/raw');};const response=await route.POST(request('{}'),context);assert.deepEqual(await response.json(),{detail:{code:'QA_BACKEND_UNAVAILABLE'}});});
 await check('path traversal denied',async()=>{const response=await route.POST(request('{}'),{params:Promise.resolve({path:['..']})});assert.equal(response.status,400);});
} finally {globalThis.fetch=previousFetch;for(const key of Object.keys(process.env))if(!(key in saved))delete process.env[key];Object.assign(process.env,saved);}
console.log('Bounded proxy checks passed: '+count);
