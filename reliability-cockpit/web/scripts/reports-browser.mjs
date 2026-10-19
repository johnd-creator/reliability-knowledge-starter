// Actual report components, fully intercepted synthetic network. No listening application or DB.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,rmSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {browserBundle} from './localization-browser-build.mjs';
const {chromium}=await import(process.env.NADI_PLAYWRIGHT_MODULE?pathToFileURL(process.env.NADI_PLAYWRIGHT_MODULE).href:'playwright');
const {default:AxeBuilder}=await import(process.env.NADI_AXE_MODULE?pathToFileURL(process.env.NADI_AXE_MODULE).href:'@axe-core/playwright');
const fixture=JSON.parse(readFileSync('fixtures/reports-ui.json','utf8'));
const out=resolve(process.env.NADI_REPORTS_OUTPUT??'/tmp/nadi-reports-ui-evidence');mkdirSync(out,{recursive:true});
const bundle=await browserBundle('scripts/reports-entry.tsx'),browser=await chromium.launch({headless:true});
const checks=[],requests=[],errors=[],violations=[],accessibility=[],pending=[];
const ctx=await browser.newContext({viewport:{width:1440,height:1080},serviceWorkers:'block'}),p=await ctx.newPage();
const base='https://reports.synthetic.invalid';let mode='normal';
const check=(name,result)=>{assert.ok(result,name);checks.push(name);console.log('PASS '+name);};
p.on('pageerror',error=>errors.push(error.message));
await ctx.route('**/*',async route=>{
 const r=route.request(),u=new URL(r.url());
 if(u.origin!==base){violations.push({path:u.pathname,method:r.method()});return route.abort('blockedbyclient');}
 if(u.pathname==='/candidate.js')return route.fulfill({contentType:'application/javascript',body:bundle.js});
 if(u.pathname==='/candidate.css')return route.fulfill({contentType:'text/css',body:bundle.css});
 if(['/logo_nadi.png','/login/logo_nadi-white-cyan.png','/login/power-plant-night.png'].includes(u.pathname))return route.fulfill({contentType:'image/png',body:readFileSync('public'+u.pathname)});
 if(r.isNavigationRequest())return route.fulfill({contentType:'text/html',body:'<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DEMO / QA SYNTHETIC — Reports</title><link rel="stylesheet" href="/candidate.css"></head><body><div id="root"></div><script src="/candidate.js"></script></body></html>'});
 const coverage=u.pathname==='/api/cockpit/v1/reliability/data-trust',maintenance=u.pathname==='/api/cockpit/v1/reliability/decision-overview',days=u.searchParams.get('window_days');
 requests.push({mode,path:u.pathname,query:u.search,method:r.method()});
 if(r.method()!=='GET'||(!coverage&&!maintenance)||(coverage&&u.search)||(maintenance&&(!['7','30','90'].includes(days)||u.searchParams.size!==1))){violations.push({path:u.pathname,method:r.method()});return route.abort('blockedbyclient');}
 if(mode==='denied-401'||mode==='denied-403')return route.fulfill({status:Number(mode.slice(-3)),json:{detail:'PRIVATE_SYNTHETIC_SERVER_SECRET_MUST_NOT_RENDER'}});
 if(mode==='unavailable')return route.fulfill({status:503,json:{detail:'PRIVATE_SYNTHETIC_SERVER_SECRET_MUST_NOT_RENDER'}});
 let data=structuredClone(coverage?fixture.coverage:fixture.maintenance[days]);
 if(mode==='unknown'){
  if(coverage){for(const key of Object.keys(data.population))data.population[key]=null;data.domains[0].latest_record_date=null;data.integrity.asset_refs_unresolved=null;}
  else {data.summary[`maintenance_activity_${days}d`]={value:98765,evidence_class:'BUSINESS_SEMANTICS_REQUIRED'};data.summary[`assets_active_${days}d`]={value:null,evidence_class:'VERIFIED'};data.maintenance_activity[1].event_count={value:87654,evidence_class:'DEFERRED'};data.status_distribution=[{value:'SYNTHETIC',count:{value:76543,evidence_class:'DATA_NOT_AVAILABLE'}}];data.as_of=null;}
 }
 if(mode==='empty'){
  if(coverage){for(const key of Object.keys(data.population))data.population[key]=0;data.domains=[];data.relationships=[];}
  else {data.maintenance_activity=[];data.status_distribution=[];data.work_type_distribution=[];data.activity_concentration=[];data.summary[`maintenance_activity_${days}d`]={value:0,evidence_class:'DERIVED_SAFE'};data.summary[`assets_active_${days}d`]={value:0,evidence_class:'VERIFIED'};}
 }
 if(mode==='mismatch'&&maintenance)data=structuredClone(fixture.maintenance['7']);
 if((mode==='hold-7'&&maintenance&&days==='7')||(mode==='hold-coverage'&&coverage)){pending.push({route,data});return;}
 return route.fulfill({json:data});
});
const catalog=name=>p.getByRole('button',{name:new RegExp('^'+name)});
const period=()=>p.getByLabel('Periode aktivitas',{exact:true});
async function loadedCoverage(){await p.getByRole('heading',{name:'Populasi yang berbeda, tidak dijumlahkan',exact:true}).waitFor();}
async function loadedMaintenance(days){await p.getByRole('heading',{name:`Ringkasan aktivitas · ${days} hari`,exact:true}).waitFor();}
async function go(next='normal'){mode=next;await p.goto(base+'/reports',{waitUntil:next.startsWith('hold')?'domcontentloaded':'networkidle'});if(!next.startsWith('hold')&&!['unavailable','denied-401','denied-403'].includes(next))await loadedCoverage();}
async function selectMaintenance(days=30){await catalog('Aktivitas Pemeliharaan').click();if(days!==30)await period().selectOption(String(days));await loadedMaintenance(days);}
async function waitPending(){for(let i=0;i<100&&!pending.length;i++)await new Promise(r=>setTimeout(r,20));assert.ok(pending.length,'held request observed');}
async function release(){for(const item of pending.splice(0))await item.route.fulfill({json:item.data});await p.waitForTimeout(100);}
async function screenshots(name){
 for(const width of [1440,1920,768,390]){
  await p.setViewportSize({width,height:1080});
  for(const theme of ['light','dark']){
   await p.evaluate(theme=>{document.documentElement.dataset.theme=theme;localStorage.setItem('nadi-theme',theme);scrollTo(0,0);},theme);
   check(`${name} no page overflow ${width} ${theme}`,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const table=p.getByRole('region',{name:name==='coverage'?'Domain cakupan laporan':'Tabel ekuivalen grafik aktivitas'});await table.focus();
   check(`${name} table keyboard focus ${width} ${theme}`,await table.evaluate(n=>document.activeElement===n&&parseFloat(getComputedStyle(n).outlineWidth)>=3));
   if(width===390){await p.keyboard.press('ArrowRight');await p.waitForFunction(node=>node.scrollLeft>0,await table.elementHandle(),{timeout:1500});check(`${name} table scroll contained ${theme}`,await table.evaluate(n=>n.scrollLeft>0));await table.evaluate(n=>n.scrollLeft=0);}
   const audit=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
   accessibility.push({name,width,theme,violations:audit.violations.map(v=>({id:v.id,impact:v.impact,targets:v.nodes.map(n=>n.target)})),incomplete:audit.incomplete.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});
   check(`${name} axe A/AA ${width} ${theme}`,audit.violations.length===0);
   await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:resolve(out,`${name}-${theme}-${width}.png`),fullPage:true});
  }
 }
}
try{
 await go();
 check('Reports nav becomes real candidate route',await p.locator('nav a[href="/reports"][aria-current="page"]').count()===1);
 check('two candidate catalog buttons and labels',await p.locator('.report-template').count()===2&&await p.getByText('DEVELOPMENT CANDIDATE — NOT OPERATIONALLY APPROVED',{exact:true}).count()>=3);
 check('Coverage requests no arbitrary period and no maintenance DTO',requests.length===1&&requests[0].path.endsWith('/data-trust')&&!requests[0].query);
 check('Coverage has no time period control',await period().count()===0&&await p.getByText('Data Coverage tidak mendukung filter periode.',{exact:false}).isVisible());
 check('Registry and technical populations remain distinct',await p.locator('.report-metrics .stat-card').filter({hasText:'Registry bisnis'}).locator('strong').innerText()==='12'&&await p.locator('.report-metrics .stat-card').filter({hasText:'Konteks aset teknis'}).locator('strong').innerText()==='120');
 check('Data Trust no invented as-of',await p.getByText('Tidak disediakan DTO (UNKNOWN)',{exact:true}).isVisible()&&await p.getByText('bukan timestamp observasi independen',{exact:false}).isVisible());
 for(const href of ['/data-quality','/assets','/maintenance','/fmea','/asset-health','/rcfa','/overhauls','/system-integration'])check('source link preserved '+href,await p.locator(`main a[href="${href}"]`).count()>0);
 await screenshots('coverage');
 await p.setViewportSize({width:1440,height:1080});await p.evaluate(()=>scrollTo(0,0));
 await catalog('Aktivitas Pemeliharaan').focus();await p.keyboard.press('Space');await loadedMaintenance(30);
 check('catalog keyboard selection and focus',await catalog('Aktivitas Pemeliharaan').getAttribute('aria-pressed')==='true'&&await catalog('Aktivitas Pemeliharaan').evaluate(n=>document.activeElement===n));
 check('period options exactly supported',JSON.stringify(await period().locator('option').evaluateAll(xs=>xs.map(x=>x.value)))===JSON.stringify(['7','30','90']));
 check('30-day maintenance metric exact',await p.locator('.report-metrics .stat-card').filter({hasText:'Aktivitas maintenance 30 hari'}).locator('strong').innerText()==='23');
 check('DTO window and as-of preserved',await p.locator('time[datetime="2026-09-15T12:00:00.000Z"]').count()===1&&await p.locator('time[datetime="2026-10-15T12:00:00.000Z"]').count()>=2);
 check('chronology independently labeled and exact last bucket',await p.getByText('Kronologi memiliki rentang bucket sendiri',{exact:false}).isVisible()&&await p.locator('time[datetime="2026-10-19T00:00:00.000Z"]').count()>0);
 check('chart and table have equivalent original rows',await p.locator('.report-bar').count()===12&&await p.getByRole('region',{name:'Tabel ekuivalen grafik aktivitas'}).locator('tbody tr').count()===12);
 check('no unsupported new KPI numbers',await p.getByText('Tidak tersedia: MTBF, MTTR, Availability, PM Compliance',{exact:false}).isVisible());
 await screenshots('maintenance');
 await p.setViewportSize({width:1440,height:1080});
 await period().selectOption('7');await loadedMaintenance(7);
 check('7-day actual zero is not UNKNOWN',await p.locator('.report-metrics .stat-card').filter({hasText:'Aktivitas maintenance 7 hari'}).locator('strong').innerText()==='0');
 await period().selectOption('90');await loadedMaintenance(90);
 check('90-day requested API metric',await p.locator('.report-metrics .stat-card').filter({hasText:'Aktivitas maintenance 90 hari'}).locator('strong').innerText()==='54'&&requests.some(r=>r.query==='?window_days=90'));
 mode='hold-7';await period().selectOption('7');await waitPending();
 check('period-specific loading clears prior report numbers',await p.getByRole('status').getByText('Memuat preview Aktivitas Pemeliharaan 7 hari…',{exact:true}).isVisible()&&await p.locator('.report-metrics').count()===0);
 mode='normal';await period().selectOption('90');await loadedMaintenance(90);await release();
 check('late 7-day response cannot replace 90-day report',await p.getByRole('heading',{name:'Ringkasan aktivitas · 90 hari',exact:true}).isVisible()&&await period().inputValue()==='90');
 mode='hold-coverage';await catalog('Cakupan Data').click();await waitPending();
 check('coverage-specific loading clears maintenance preview',await p.getByRole('status').getByText('Memuat preview Cakupan Data…',{exact:true}).isVisible()&&await p.getByRole('heading',{name:/Ringkasan aktivitas/}).count()===0);
 mode='normal';await catalog('Aktivitas Pemeliharaan').click();await loadedMaintenance(90);await release();
 check('late Coverage cannot replace Maintenance',await p.getByRole('heading',{name:'Ringkasan aktivitas · 90 hari',exact:true}).isVisible()&&await p.getByRole('heading',{name:'Populasi yang berbeda, tidak dijumlahkan',exact:true}).count()===0);
 await go('unknown');check('null Coverage counts remain UNKNOWN',await p.locator('.report-metrics .stat-card strong').allTextContents().then(xs=>xs.every(x=>x.includes('UNKNOWN'))));
 await selectMaintenance(30);const text=await p.locator('main').innerText();
 check('gated metrics never expose unsupported numeric values',!['98765','87654','76543'].some(x=>text.includes(x))&&text.includes('NOT ASSESSED'));
 check('null authoritative as-of never replaced by current time',await p.getByText('As-of authoritative DTO',{exact:true}).locator('..').getByText('Tidak disediakan DTO (UNKNOWN)',{exact:true}).isVisible());
 await go('empty');check('empty Coverage has explicit domains and actual zero',await p.getByText('Belum ada baris domain.',{exact:true}).isVisible()&&await p.locator('.report-metrics .stat-card strong').allTextContents().then(xs=>xs.every(x=>x==='0')));
 await selectMaintenance();check('empty Maintenance chart is explicit',await p.getByText('Kronologi belum tersedia.',{exact:true}).isVisible()&&await p.getByText('Konsentrasi aktivitas belum tersedia pada rentang ini.',{exact:true}).isVisible());
 await go('mismatch');await catalog('Aktivitas Pemeliharaan').click();await p.getByRole('alert').waitFor();
 check('mismatched response refused before numbers render',await p.getByText('Periode respons tidak sesuai permintaan.',{exact:false}).isVisible()&&await p.locator('.report-metrics').count()===0);
 for(const fail of ['unavailable','denied-403']){
  await go(fail);await p.getByRole('alert').waitFor();
  check(fail+' Coverage explicit safe error',await p.getByRole('alert').count()===1&&!((await p.locator('body').innerText()).includes('PRIVATE_SYNTHETIC')));
  await catalog('Aktivitas Pemeliharaan').click();await p.getByRole('alert').waitFor();
  check(fail+' Maintenance no data or raw errors',await p.locator('.report-metrics').count()===0&&!((await p.locator('body').innerText()).includes('PRIVATE_SYNTHETIC')));
 }
 mode='normal';await p.getByRole('button',{name:'Baca ulang laporan kandidat',exact:true}).click();await loadedMaintenance(30);check('deliberate GET retry recovers',await p.getByRole('heading',{name:'Ringkasan aktivitas · 30 hari',exact:true}).isVisible());
 await p.setViewportSize({width:390,height:1080});await p.getByRole('button',{name:'Buka navigasi',exact:true}).click();
 check('mobile drawer preserves reports access',await p.getByRole('dialog').isVisible()&&await p.locator('nav a[href="/reports"]').isVisible());await p.keyboard.press('Escape');check('Escape returns to preview',await p.getByRole('dialog').count()===0);
 check('no export, downloads or print controls',await p.locator('[download],input[type="file"]').count()===0&&await p.getByRole('button',{name:/^(Ekspor|Unduh|Kirim|Cetak)/}).count()===0);
 check('only two read-only allowlisted DTOs, no egress',violations.length===0&&requests.every(r=>r.method==='GET'));
 await go('denied-401');await p.waitForURL(base+'/login?expired=1');await p.getByRole('heading',{name:'Masuk ke NADI',exact:true}).waitFor();check('401 clears report and returns to standalone expired login',await p.locator('.report-metrics,.nadi-shell').count()===0&&!((await p.locator('body').innerText()).includes('PRIVATE_SYNTHETIC')));
 check('no browser exceptions',errors.length===0);
 writeFileSync(resolve(out,'browser-results.json'),JSON.stringify({status:'PASS',passed:checks.length,total:checks.length,checks,requests,errors,violations,accessibility,scope:'DEMO / QA SYNTHETIC actual components; no application listener/runtime/DB'},null,2));
 console.log(`Reports browser checks passed: ${checks.length}`);
}catch(error){writeFileSync(resolve(out,'browser-results.json'),JSON.stringify({status:'FAIL',passed:checks.length,checks,requests,errors,violations,accessibility,failure:String(error)},null,2));throw error;}
finally{await browser.close();rmSync(bundle.temp,{recursive:true,force:true});}
