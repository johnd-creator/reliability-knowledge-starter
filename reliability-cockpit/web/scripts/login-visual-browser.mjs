// No listener or retained credentials: actual presentation, intercepted synthetic session.
import assert from 'node:assert/strict';
import {readFileSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {browserBundle} from './localization-browser-build.mjs';
const {chromium}=await import(pathToFileURL(process.env.NADI_PLAYWRIGHT_MODULE).href);
const out=resolve(process.env.NADI_BROWSER_OUTPUT??'/tmp/nadi-login-visual-evidence');mkdirSync(out,{recursive:true});
const b=await browserBundle('scripts/login-visual-entry.tsx');b.css+='\n'+readFileSync('app/login-refresh.css','utf8');
const browser=await chromium.launch({headless:true}),ctx=await browser.newContext({viewport:{width:1440,height:1000}}),p=await ctx.newPage(),base='https://login-visual.synthetic.invalid',checks=[],errors=[];let logoutCalls=0;let failLogout=true;
const check=(label,value)=>{assert(value,label);checks.push(label);console.log('PASS '+label)};
p.on('pageerror',e=>errors.push(e.message));
await ctx.addInitScript(()=>localStorage.setItem('nadi-theme','light'));
await ctx.route('**/*',async route=>{const r=route.request(),u=new URL(r.url());assert.equal(u.origin,base,'No external egress');
 if(u.pathname==='/candidate.js')return route.fulfill({contentType:'application/javascript',body:b.js});
 if(u.pathname==='/candidate.css')return route.fulfill({contentType:'text/css',body:b.css});
 if(u.pathname==='/login/logo_nadi-white-cyan.png'||u.pathname==='/logo_nadi.png'||u.pathname==='/login/power-plant-night.png')return route.fulfill({contentType:'image/png',body:readFileSync('public'+u.pathname)});
 if(r.isNavigationRequest())return route.fulfill({contentType:'text/html',body:'<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/candidate.css"></head><body><div id="root"></div><script src="/candidate.js"></script></body></html>'});
 if(u.pathname==='/api/engineering-qa/session')return route.fulfill({json:{subject:'local:SYNTHETIC-VISUAL',username:'QA_VISUAL_ONLY',roles:['ADMIN'],asset_ids:['asset:SYNTHETIC'],csrf_token:'SYNTHETIC_CSRF_ONLY'}});
 if(u.pathname==='/api/engineering-qa/session/logout'){assert.equal(r.method(),'POST');assert.equal(r.headers()['x-csrf-token'],'SYNTHETIC_CSRF_ONLY');logoutCalls++;await new Promise(r=>setTimeout(r,700));if(failLogout)return route.fulfill({status:503,json:{}});return route.fulfill({json:{status:'REVOKED'}});}
 return route.fulfill({status:404,json:{}});
});
try{
 for(const width of [1440,768,390]){
  await p.setViewportSize({width,height:1000});await p.goto(base+'/login',{waitUntil:'networkidle'});
  check('login fullscreen no application navigation '+width,await p.locator('.nadi-topbar,.nadi-sidebar,.session-account').count()===0);
  check('exact tagline '+width,await p.getByRole('heading',{name:'Data Andal Keputusan Terarah'}).isVisible());
  check('logo has no opaque panel '+width,await p.locator('.login-logo-surface').evaluate(el=>getComputedStyle(el).backgroundColor==='rgba(0, 0, 0, 0)'));
  check('illustration loaded '+width,await p.evaluate(async()=>{const i=new Image();i.src='/login/power-plant-night.png';await i.decode();return i.naturalWidth>1000;}));
  const username=p.locator('input[name="username"]'),password=p.locator('input[name="password"]'),eye=p.getByRole('button',{name:'Tampilkan kata sandi',exact:true});
  const ub=await username.boundingBox(),pb=await password.boundingBox(),eb=await eye.boundingBox();
  check('equal full-width inputs and inset eye '+width,Math.abs(ub.width-pb.width)<1&&Math.abs(ub.height-pb.height)<1&&eb.x>=pb.x&&eb.x+eb.width<=pb.x+pb.width);
  check('icon only and selected cyan logo '+width,(await eye.innerText()).trim()===''&&await p.locator('.login-logo-surface img').getAttribute('src')==='/login/logo_nadi-white-cyan.png'&&await p.locator('.login-logo-surface img').evaluate(el=>getComputedStyle(el).filter==='none'));
  await password.fill('SYNTHETIC_VISIBILITY_ONLY');await eye.click();check('eye shows unchanged password '+width,await password.getAttribute('type')==='text'&&await password.inputValue()==='SYNTHETIC_VISIBILITY_ONLY');await p.getByRole('button',{name:'Sembunyikan kata sandi',exact:true}).click();check('eye hides password '+width,await password.getAttribute('type')==='password');await password.fill('');
  check('login no overflow '+width,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await p.screenshot({path:out+'/login-light-'+width+'.png',fullPage:true});await p.getByRole('button',{name:'Ganti ke tema gelap'}).click();await p.screenshot({path:out+'/login-dark-'+width+'.png',fullPage:true});
  await p.goto(base+'/workspace',{waitUntil:'networkidle'});const trigger=p.getByRole('button',{name:'Keluar dari NADI',exact:true});await trigger.waitFor();
  check('one existing navbar only '+width,await p.locator('.nadi-topbar').count()===1&&await p.locator('.session-account').count()===0);
  const positions=await p.evaluate(()=>{const a=document.querySelector('.theme-toggle').getBoundingClientRect(),b=document.querySelector('.logout-trigger').getBoundingClientRect();return Math.abs((a.y+a.height/2)-(b.y+b.height/2))<2;});check('theme and logout aligned '+width,positions);
  check('workspace no overflow '+width,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await trigger.click();await p.getByRole('dialog',{name:'Keluar dari NADI?'}).waitFor();check('cancel focused '+width,await p.getByRole('button',{name:'Batal',exact:true}).evaluate(el=>el===document.activeElement));
  await p.screenshot({path:out+'/logout-confirm-'+width+'.png',fullPage:true});await p.getByRole('button',{name:'Batal',exact:true}).click();check('cancel never revokes session '+width,logoutCalls===0);
  await trigger.click();await p.keyboard.press('Escape');check('Escape closes without logout '+width,await p.locator('dialog[open]').count()===0&&logoutCalls===0);
 }
 await p.getByRole('button',{name:'Keluar dari NADI',exact:true}).click();await p.getByRole('button',{name:'Ya, keluar',exact:true}).click();
 await p.locator('dialog[aria-busy="true"]').waitFor();check('pending spinner remains in dialog; old checking page absent',await p.locator('dialog[open] .spinner').count()>0&&await p.locator('main.state-card,.nadi-topbar').count()===0);await p.keyboard.press('Escape');check('pending cannot dismiss or submit twice',await p.locator('dialog[open]').count()===1&&await p.getByRole('button',{name:'Sedang keluar…',exact:true}).isDisabled());await p.getByRole('alert').waitFor();check('failure stays in popup and protected workspace remains hidden',await p.locator('dialog[open]').count()===1&&await p.locator('.nadi-topbar,main.state-card').count()===0);await p.keyboard.press('Escape');check('unconfirmed revocation cannot dismiss failure',await p.locator('dialog[open]').count()===1);failLogout=false;await p.getByRole('button',{name:'Coba keluar lagi',exact:true}).click();await p.waitForURL(base+'/login');check('explicit retry uses existing CSRF logout then direct login',logoutCalls===2);check('no browser exceptions',errors.length===0);
 writeFileSync(out+'/results.json',JSON.stringify({status:'PASS',checks,errors,logoutCalls,synthetic:true,official_runtime_access:false},null,2));console.log('Visual browser PASS '+checks.length);
}finally{await browser.close();rmSync(b.temp,{recursive:true,force:true});}
