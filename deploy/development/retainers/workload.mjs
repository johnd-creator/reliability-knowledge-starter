// Count-matched disposable browser workload. No operational origin or business write.
import fs from 'node:fs';import {pathToFileURL} from 'node:url';
const [port,web,out]=process.argv.slice(2),base='http://127.0.0.1:'+port;
const {chromium}=await import(pathToFileURL(process.env.NADI_PLAYWRIGHT_MODULE).href);
const browser=await chromium.launch({headless:true}),context=await browser.newContext(),page=await context.newPage();
await context.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());
const copy=JSON.parse(fs.readFileSync(web+'/lib/id-messages.json')),counts={navigation:0,status:0,hmr:0,session:0},errors=[];
page.on('pageerror',e=>errors.push(e.message));
const routes=['/','/assets','/assets/asset%3ADEMO-001','/asset-health','/pdm','/recommendations?record=recommendation:DEMO-001','/action-board','/engineering/local','/engineering/cases?record=case:DEMO-001','/engineering/advisories?record=advisory:DEMO-001','/engineering/inbox?record=advisory:DEMO-001','/maintenance','/maintenance/investigation','/work-orders','/data-quality','/fmea','/rcfa','/overhauls','/engineering','/panduan/istilah','/','/assets','/engineering/local','/'];
const component=web+'/components/DevelopmentStatus.tsx',original=fs.readFileSync(component);
const progress=()=>fs.writeFileSync(out+'/browser-progress.json',JSON.stringify({at:Date.now(),counts,errors}));
try{
 await page.goto(base+'/login',{waitUntil:'networkidle'});await page.getByLabel(copy.Username,{exact:true}).fill('DEMO_NOT_AN_ACCOUNT');await page.getByLabel(copy.Password,{exact:true}).fill('DEMO_NOT_A_CREDENTIAL');await page.getByRole('button',{name:copy['Sign in'],exact:true}).click();await page.waitForURL(/\/engineering\/local/);await page.waitForLoadState('load');
 for(let step=1;step<=6;step++){
  await page.goto(base+routes[step-1],{waitUntil:'load'});await page.getByRole('main').waitFor();counts.navigation++;
  if(step%3===0){await new Promise(r=>setTimeout(r,2000));const marker='DEV MATCH '+step;fs.writeFileSync(component,original.toString().replace('<span>DEV</span>','<span>'+marker+'</span>'));await page.getByRole('button',{name:/Status development:/}).filter({hasText:marker}).waitFor({timeout:45000});await new Promise(r=>setTimeout(r,2000));fs.writeFileSync(component,original);await page.waitForFunction(()=>document.querySelector('.dev-status-trigger span:nth-child(2)')?.textContent==='DEV');counts.hmr++;}
  if(step%6===0){const code=await page.evaluate(async()=> (await fetch('/api/engineering-qa/session',{cache:'no-store'})).status);if(code!==200)throw Error('Fixture session');counts.session++;}
  for(let poll=0;poll<3;poll++){const code=await page.evaluate(async()=> (await fetch('/api/development/status',{cache:'no-store'})).status);if(code!==200)throw Error('Fixture status');counts.status++;progress();await new Promise(r=>setTimeout(r,5000));}
  if(step===6){
   await browser.close(); // Release disposable browser before blocking private capture in ALL matched controls.
   await new Promise(r=>setTimeout(r,2000));
   fs.writeFileSync(out+`/checkpoint-${step}.ready`,JSON.stringify({counts,step}));
   while(!fs.existsSync(out+`/capture-${step}.json`))await new Promise(r=>setTimeout(r,500));
   if(JSON.parse(fs.readFileSync(out+`/capture-${step}.json`)).refused)throw Error('Capture refused');
  }
 }
 if(errors.length)throw Error('Browser exceptions');fs.writeFileSync(out+'/browser-result.json',JSON.stringify({completed:true,counts,errors}));
}catch(e){fs.writeFileSync(out+'/browser-result.json',JSON.stringify({completed:false,counts,errors,reason:e.message}));throw e;}
finally{fs.writeFileSync(component,original);await browser.close();}
