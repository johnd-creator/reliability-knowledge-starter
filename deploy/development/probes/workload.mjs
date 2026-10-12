// Real Next browser workload against disposable fixture servers only.
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [port,web,out,mode,seconds]=process.argv.slice(2);
const {chromium}=await import(pathToFileURL(process.env.NADI_PLAYWRIGHT_MODULE).href);
const base='http://127.0.0.1:'+port, browser=await chromium.launch({headless:true});
const copy=JSON.parse(fs.readFileSync(web+'/lib/id-messages.json'));
const context=await browser.newContext({viewport:{width:1440,height:1086}}),page=await context.newPage();
const counts={requests:0,status:0,navigations:0,hmr:0,session:0},errors=[];
const record=row=>fs.appendFileSync(out+'/workload.jsonl',JSON.stringify({at:Date.now(),...row})+'\n',{mode:0o600});
await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort('blockedbyclient'));
page.on('request',req=>{counts.requests++;if(req.url().includes('/api/development/status'))counts.status++;});
page.on('pageerror',e=>{errors.push(e.message);record({error:e.message});});
page.on('requestfailed',req=>record({request_failure:new URL(req.url()).pathname,error:req.failure()?.errorText}));
const routes=['/','/assets','/assets/'+encodeURIComponent('asset:DEMO-001'),'/asset-health','/pdm','/recommendations?record=recommendation:DEMO-001','/action-board','/engineering/local','/engineering/cases?record=case:DEMO-001','/engineering/advisories?record=advisory:DEMO-001','/engineering/inbox?record=advisory:DEMO-001','/maintenance','/maintenance/investigation','/work-orders','/data-quality','/fmea','/rcfa','/overhauls','/engineering','/panduan/istilah','/login'];
const component=web+'/components/DevelopmentStatus.tsx',original=fs.readFileSync(component);
let lastHmr=-1;
try {
  // Login has no DEV polling; wait for hydration before entering controlled fields.
  await page.goto(base+'/login',{waitUntil:'networkidle',timeout:60000});
  await page.getByLabel(copy.Username,{exact:true}).fill('DEMO_NOT_AN_ACCOUNT');
  await page.getByLabel(copy.Password,{exact:true}).fill('DEMO_NOT_A_CREDENTIAL');
  await page.getByRole('button',{name:copy['Sign in'],exact:true}).click();
  await page.waitForURL(/\/engineering\/local/,{timeout:60000});
  record({login:'DISPOSABLE_FIXTURE_SUCCESS',https:false});
  await page.goto(base+'/',{waitUntil:'domcontentloaded',timeout:60000});
  const start=Date.now();
  while((Date.now()-start)/1000<Number(seconds)) {
    const elapsed=(Date.now()-start)/1000;
    if(mode!=='poll-only') {
      const route=routes[counts.navigations%routes.length];
      const response=await page.goto(base+route,{waitUntil:'load',timeout:60000});
      await page.getByRole('main').waitFor({timeout:30000});
      counts.navigations++;record({route,code:response.status(),elapsed,counts});
    }
    if(mode==='nav-hmr'&&Math.floor(elapsed/60)>lastHmr) {
      lastHmr=Math.floor(elapsed/60);
      if(page.url().endsWith('/login'))await page.goto(base+'/',{waitUntil:'domcontentloaded'});
      const text='DEV PROBE '+lastHmr;
      fs.writeFileSync(component,original.toString().replace('<span>DEV</span>','<span>'+text+'</span>'));
      await page.getByRole('button',{name:/Status development:/}).filter({hasText:text}).waitFor({timeout:45000});
      // Allow the full-reload fallback/hot-update transaction to settle before
      // the reverse edit; otherwise rapid restore can race the in-flight reload.
      await new Promise(resolve=>setTimeout(resolve,2000));
      fs.writeFileSync(component,original);
      await page.waitForFunction(()=>document.querySelector('.dev-status-trigger span:nth-child(2)')?.textContent==='DEV',null,{timeout:45000});
      counts.hmr++;record({hmr:counts.hmr,elapsed});
    }
    if(counts.navigations%10===0||mode==='poll-only') {
      const code=await page.evaluate(async()=>{const r=await fetch('/api/engineering-qa/session',{cache:'no-store'});return r.status;});
      counts.session++;if(code!==200)throw Error('Disposable session lost: '+code);
    }
    fs.writeFileSync(out+'/browser-progress.json',JSON.stringify({at:Date.now(),elapsed,counts,errors}));
    await new Promise(resolve=>setTimeout(resolve,Number(process.env.NADI_PROBE_NAV_DELAY_MS??15000)));
  }
  for(const width of [1440,768,390]) {
    await page.setViewportSize({width,height:1086});await page.goto(base+'/',{waitUntil:'load'});
    await page.waitForFunction(()=>{const button=document.querySelector('.dev-status-trigger');return button&&button.getAttribute('aria-label')!=='Status development: Memeriksa status';});
    await page.getByRole('button',{name:/Status development:/}).click();
    await page.getByRole('region',{name:'Detail status development'}).waitFor();
    await page.screenshot({path:out+'/fixture-only-'+width+'.png',fullPage:true});
  }
  if(errors.length)throw Error('Disposable fixture browser exceptions: '+errors.length);
  fs.writeFileSync(out+'/browser-result.json',JSON.stringify({completed:true,counts,errors,scope:'DISPOSABLE HTTP FIXTURE; not live or security acceptance'}));
} catch(e) {
  record({dev_dom:await page.locator('.dev-status-trigger').evaluateAll(nodes=>nodes.map(n=>n.outerHTML)).catch(()=>[])});
  record({failure:e.message,counts,errors});fs.writeFileSync(out+'/browser-result.json',JSON.stringify({completed:false,failure:e.message,counts,errors}));throw e;
} finally {fs.writeFileSync(component,original);await browser.close();}
