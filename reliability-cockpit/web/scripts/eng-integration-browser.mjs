// Real HTTPS QA authentication at the product boundary; no response fixtures.
// Existing operator-owned accounts only. No source calls or record mutations.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.env.NADI_PLAYWRIGHT_MODULE).href);
const base='https://localhost:3000',out=resolve(process.env.NADI_BROWSER_OUTPUT??'/tmp/nadi-integration-browser');
mkdirSync(out,{recursive:true});
const accounts=JSON.parse(readFileSync(process.env.NADI_QA_ACCOUNT_FILE,'utf8'));
const checks=[],errors=[];const browser=await chromium.launch({headless:true});
function check(name,ok){assert.ok(ok,name);checks.push(name);console.log('PASS '+name);}
try{
 for(const [route,title,ready,who,resource]of[
  ['/engineering/cases','Engineering Cases','Case register','engineer','cases'],
  ['/engineering/advisories','Engineering Advisories','Advisory register','engineer','advisories'],
  ['/engineering/inbox','Advisory Inbox','Authorized advisory inbox','reviewer','inbox'],
 ]){
  const context=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:390,height:1000}});
  try{
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
   const response=await page.goto(base+route,{waitUntil:'networkidle'});
   check('public shell renders '+route,response.status()===200);
   await page.getByRole('heading',{name:title,exact:true}).waitFor();
   await page.getByRole('form',{name:'NADI sign-in',exact:true}).waitFor();
   check('anonymous records denied '+resource,(await context.request.get(base+'/api/engineering-qa/'+resource)).status()===401);
   check('signed-out data hidden '+route,await page.getByRole('heading',{name:ready,exact:true}).count()===0);
   await page.getByLabel('Username',{exact:true}).fill(accounts[who].username);
   await page.getByLabel('Password',{exact:true}).fill(accounts[who].password);
   await page.getByRole('button',{name:'Sign in',exact:true}).click();
   await page.getByRole('heading',{name:ready,exact:true}).waitFor();
   check('inline login retains intended route '+route,new URL(page.url()).pathname===route);
   check('credentials removed after login '+route,await page.getByRole('form',{name:'NADI sign-in',exact:true}).count()===0);
   check('Secure HttpOnly Strict session '+route,(await context.cookies()).some(c=>c.secure&&c.httpOnly&&c.sameSite==='Strict'));
   check('authenticated records available '+resource,(await context.request.get(base+'/api/engineering-qa/'+resource)).status()===200);
   if(who==='reviewer')check('reviewer cannot draft an advisory',await page.getByRole('button',{name:'New advisory',exact:true}).count()===0);
   await page.reload({waitUntil:'networkidle'});await page.getByRole('heading',{name:ready,exact:true}).waitFor();
   check('reload retains product and session '+route,new URL(page.url()).pathname===route);
   check('mobile content contained '+route,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  }finally{await context.close();}
 }
 check('no page errors',errors.length===0);
 writeFileSync(out+'/integration-browser-report.json',JSON.stringify({status:'PASS',checks,actual_qa_authentication:true,response_fixtures:false},null,2));
 console.log('Integration browser checks passed: '+checks.length);
}finally{await browser.close();}
