// Every request is intercepted: synthetic components, no server/live QA or source access.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {browserBundle} from './localization-browser-build.mjs';
const {chromium}=await import(process.env.NADI_PLAYWRIGHT_MODULE?pathToFileURL(process.env.NADI_PLAYWRIGHT_MODULE).href:'playwright');
const base='https://pdm.synthetic.invalid',out=resolve(process.env.NADI_BROWSER_OUTPUT??'/tmp/nadi-pdm-input-evidence');mkdirSync(out,{recursive:true});
const bundle=await browserBundle(),browser=await chromium.launch({headless:true}),checks=[],errors=[],commands=[];
const check=(label,result)=>{assert.ok(result,label);checks.push(label);console.log('PASS '+label);};
const ctx=await browser.newContext({viewport:{width:1440,height:1086}}),p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
const asset='asset:SYNTHETIC:A',time='2026-10-09T01:00:00Z';let subject='synthetic-author',role='AUTHOR',failSave=true,denied=0;const inspections=[],cases=[],receipts=new Map();
const pageOf=(items,url)=>{const offset=Number(url.searchParams.get('offset')??0),limit=Number(url.searchParams.get('limit')??25);return {items:items.slice(offset,offset+limit),total:items.length,offset,limit,has_more:offset+limit<items.length};};
await ctx.route('**/*',async route=>{
 const r=route.request(),u=new URL(r.url()),path=u.pathname,method=r.method();
 if(u.origin!==base)return route.abort('blockedbyclient');
 if(path==='/candidate.js')return route.fulfill({contentType:'application/javascript',body:bundle.js});
 if(path==='/candidate.css')return route.fulfill({contentType:'text/css',body:bundle.css});
 if(path==='/logo_nadi.png')return route.fulfill({contentType:'image/png',body:readFileSync('public/logo_nadi.png')});
 if(r.isNavigationRequest())return route.fulfill({contentType:'text/html',body:'<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/candidate.css"></head><body><div id="root"></div><script src="/candidate.js"></script></body></html>'});
 if(!path.startsWith('/api/engineering-qa/'))return route.fulfill({status:404,body:''});
 const [resource,idRaw,action]=path.slice('/api/engineering-qa/'.length).split('/'),id=decodeURIComponent(idRaw??'');
 const fail=(status,code)=>route.fulfill({status,json:{detail:{code}}});
 if(resource==='session'){if(denied)return fail(denied,'AUTHENTICATION_REQUIRED');return route.fulfill({json:{subject,roles:[role],asset_ids:[asset],csrf_token:'SYNTHETIC_NON_SESSION'}});}
 if(denied)return fail(denied,'FORBIDDEN');
 if(resource==='asset-context')return route.fulfill({json:{canonical_asset_id:asset,identity_availability:'AVAILABLE',identity:{description:'DEMO — equipment sintetis',location_ref:'SYNTHETIC AREA'}}});
 if(resource==='inspections'&&id==='measurement-history'){
  let events=inspections.flatMap(row=>row.measurements.map((measurement,measurement_index)=>({...row,measurement,measurement_index})));
  for(const [param,key] of [['point','point_ref'],['quantity','quantity']])if(u.searchParams.get(param))events=events.filter(e=>e.measurement[key]===u.searchParams.get(param));
  return route.fulfill({json:pageOf(events,u)});
 }
 const rows=resource==='inspections'?inspections:cases;let row=rows.find(x=>(x.record_id??x.case_id)===id);
 if(method==='GET'){
  if(action==='history')return route.fulfill({json:[{revision:1,actor:'synthetic-author',action:'CREATE',occurred_at:time,reason:'SYNTHETIC'}]});
  if(id)return row?route.fulfill({json:row}):fail(404,'NOT_FOUND');
  let result=rows;
  if(u.searchParams.get('status'))result=result.filter(x=>x.status===u.searchParams.get('status'));
  if(u.searchParams.get('method'))result=result.filter(x=>x.method===u.searchParams.get('method'));
  if(u.searchParams.get('search'))result=result.filter(x=>x.observations?.join(' ').includes(u.searchParams.get('search')));
  return route.fulfill({json:pageOf(result,u)});
 }
 const body=r.postDataJSON();commands.push({resource,id,action,body});
 check('CSRF unchanged '+commands.length,r.headers()['x-csrf-token']==='SYNTHETIC_NON_SESSION');
 if(failSave&&resource==='inspections'&&!id){failSave=false;return fail(503,'QA_BACKEND_UNAVAILABLE');}
 if(receipts.has(body.request_id))return route.fulfill({json:receipts.get(body.request_id)});
 if(row&&body.expected_revision!==row.revision)return fail(409,'REVISION_CONFLICT');
 if(!id){row={...body.draft,[resource==='cases'?'case_id':'record_id']:resource==='cases'?'case:SYNTHETIC-INPUT':'inspection:SYNTHETIC-INPUT',created_by:subject,status:'DRAFT',revision:1,created_at:time,updated_at:time,review:null,contributors:[subject],review_started_by:null,field_approval:'ENGINEER_FIELDS_PENDING',assessment:'NOT_ASSESSED',provenance:'NADI_MANUAL_INSPECTION',attachments:body.draft.attachments??[],case_refs:[],method_extension:body.draft.method_extension??{}};rows.push(row);}
 else if(method==='PUT')Object.assign(row,{...body.draft,revision:row.revision+1});
 else if(action==='submit'){row.status='SUBMITTED';row.revision++;}
 else if(action==='begin_review'){if(subject===row.created_by)return fail(403,'INDEPENDENT_REVIEWER_REQUIRED');row.status='UNDER_REVIEW';row.review_started_by=subject;row.revision++;}
 else if(action==='review'){row.status=body.decision;row.review={decision:body.decision,reviewer:subject,decided_at:time,rationale:body.reason};row.revision++;}
 else if(action==='revise'){row.status='DRAFT';row.review=null;row.review_started_by=null;row.revision++;}
 else if(action==='evidence'){check('handoff binds exact approved inspection revision',body.expected_inspection_revision===inspections[0].revision);row.evidence=[{record_id:inspections[0].record_id,stable_version:'SYNTHETIC-SHA',kind:'MANUAL_INSPECTION'}];row.revision++;}
 receipts.set(body.request_id,structuredClone(row));return route.fulfill({json:row});
});
const button=name=>p.getByRole('button',{name,exact:true});const go=async()=>{await p.goto(base+'/pdm',{waitUntil:'networkidle'});await button('Input Pengukuran').waitFor();};
async function evidence(name){for(const width of [1440,768,390]){await p.setViewportSize({width,height:1086});check('no page overflow '+name+' '+width,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:out+'/'+name+'-'+width+'.png',fullPage:true});}}
try{
 await go();await button('Input Pengukuran').click();await p.getByLabel('Konteks input kandidat').selectOption('AREA_FAN');check('template awaits validation',await p.getByText(/Menunggu Validasi Engineer\. Pemilihan konteks/).isVisible());
 await p.getByLabel('Versi metode / prosedur').fill('candidate-1');await p.getByLabel('Waktu inspeksi asli').fill('2026-10-09T08:00:00+07:00');await p.getByLabel('Referensi instrumen').fill('instrument:SYNTHETIC');await p.getByLabel('Referensi prosedur').fill('procedure:SYNTHETIC');await p.getByLabel('Orientasi').fill('orientation:SYNTHETIC');await p.getByLabel('Konteks operasi',{exact:true}).fill('SYNTHETIC steady regime');
 for(let i=1;i<=3;i++){if(i>1)await button('Tambah baris').click();await p.getByLabel('Titik '+i,{exact:true}).fill('point:SYNTHETIC');await p.getByLabel('Parameter '+i,{exact:true}).fill(i===3?'synthetic_state':'synthetic_quantity');await p.getByLabel('Tipe nilai '+i,{exact:true}).selectOption(i===3?'UNKNOWN':'NUMERIC');if(i<3)await p.getByLabel('Nilai asli '+i,{exact:true}).fill(i===1?'0':'4.2');await p.getByLabel('Unit asli '+i,{exact:true}).fill(i===3?'':'unit-A');await p.getByLabel('Waktu measurement '+i,{exact:true}).fill(i===1?time:i===2?'2026-10-09T02:51:00Z':'');}
 await p.getByLabel('Observasi (satu per baris)').fill('SYNTHETIC reported observation');await p.getByLabel('Interpretasi / Hipotesis').fill('SYNTHETIC unconfirmed hypothesis');await p.getByLabel('Parameter 1',{exact:true}).focus();await p.keyboard.press('Tab');check('keyboard advances measurement fields',await p.getByLabel('Tipe nilai 1',{exact:true}).evaluate(el=>el===document.activeElement));
 await p.evaluate(()=>window.dispatchEvent(new Event('focus')));await p.getByLabel('Nilai asli 1',{exact:true}).waitFor();check('trusted-session refresh retains same-identity unsaved rows',await p.getByLabel('Nilai asli 1',{exact:true}).inputValue()==='0');check('candidate context survives authorized refresh',await p.getByLabel('Konteks input kandidat').inputValue()==='AREA_FAN');check('native controls have touch height',await p.getByLabel('Tipe nilai 1',{exact:true}).evaluate(el=>el.getBoundingClientRect().height>=44));await evidence('measurement-input');await p.setViewportSize({width:1440,height:1086});await button('Simpan draf inspeksi').click();await p.getByRole('alert').waitFor();check('failed save retains native rows',await p.getByLabel('Nilai asli 1',{exact:true}).inputValue()==='0');await button('Simpan draf inspeksi').click();await p.getByRole('heading',{name:'Workflow inspeksi berotorisasi',exact:true}).waitFor();check('retry uses same request ID',commands[0].body.request_id===commands[1].body.request_id);check('zero and null preserved',inspections[0].measurements[0].value===0&&inspections[0].measurements[2].value===null);await evidence('inspection-detail');
 await button('Riwayat & Tren').click();await p.getByRole('region',{name:'Riwayat measurement asli'}).waitFor();await p.getByLabel('Plot sampel pada halaman ini').selectOption(inspections[0].record_id);check('null/incompatible context not plotted',await p.getByText('Tren sebanding belum tersedia',{exact:true}).isVisible());await p.getByLabel('Parameter exact').fill('synthetic_quantity');await button('Terapkan filter measurement').click();await p.getByRole('region',{name:'Riwayat measurement asli'}).waitFor();await p.getByLabel('Plot sampel pada halaman ini').selectOption(inspections[0].record_id);await p.getByRole('img',{name:/Sampel measurement asli/}).waitFor();check('scatter has two actual samples without interpolation',await p.locator('.pdm-raw-plot circle').count()===2&&await p.locator('.pdm-raw-plot polyline').count()===0);await evidence('measurement-history');
 await button('Register Inspeksi').click();await button(inspections[0].record_id).click();await button('Ajukan inspeksi').click();await p.getByLabel('Alasan review / revisi').waitFor();check('author has no self-review control',await button('Mulai review independen').count()===0);
 role='REVIEWER';subject='synthetic-reviewer';await p.goto(base+'/pdm?record='+encodeURIComponent(inspections[0].record_id),{waitUntil:'networkidle'});await p.getByLabel('Alasan review / revisi').fill('SYNTHETIC independent review');await button('Mulai review independen').click();await button('Setujui rekam inspeksi').waitFor();await p.getByLabel('Alasan review / revisi').fill('SYNTHETIC record review only');await button('Setujui rekam inspeksi').click();check('review does not classify condition',inspections[0].status==='APPROVED'&&inspections[0].assessment==='NOT_ASSESSED');
 role='AUTHOR';subject='synthetic-author';await p.goto(base+'/pdm?record='+encodeURIComponent(inspections[0].record_id),{waitUntil:'networkidle'});await button('Mulai Engineering Case').click();await p.getByLabel('Judul kasus',{exact:true}).fill('SYNTHETIC investigation');await p.getByLabel('Pernyataan masalah',{exact:true}).fill('SYNTHETIC observation requires independent review');await button('Simpan kasus').click();await p.getByText('Evidence versi exact telah ditautkan.',{exact:false}).waitFor();check('Case existing workflow receives exact evidence',cases.length===1&&cases[0].evidence[0].record_id===inspections[0].record_id);await evidence('engineering-handoff');
 denied=403;await p.goto(base+'/pdm',{waitUntil:'networkidle'});check('denied session exposes no records',await p.getByRole('heading',{name:'Register inspeksi / temuan',exact:true}).count()===0);denied=0;await go();await p.evaluate(()=>document.documentElement.dataset.theme='dark');await evidence('register-dark');check('no uncaught browser errors',errors.length===0);
 writeFileSync(out+'/results.json',JSON.stringify({status:'PASS',checks,errors,synthetic_fixtures:true,official_runtime_access:false,commands:commands.map(c=>({resource:c.resource,action:c.action}))},null,2));
}finally{await ctx.close();await browser.close();}
