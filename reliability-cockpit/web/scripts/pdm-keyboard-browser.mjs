// Shares the PdM browser harness: actual components, intercepted synthetic data,
// no application server and no persistent QA access.
import {writeFileSync,mkdirSync} from 'node:fs';
export async function pdmKeyboardChecks({p,button,go,check,out}){
 const folder=out+'/keyboard';mkdirSync(folder,{recursive:true});const observations=[];
 async function visible(label,expected){
  await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const observation=await p.evaluate(()=>{
   const el=document.activeElement,region=document.querySelector('.pdm-grid-scroll');
   const rect=el.getBoundingClientRect(),bounds=region.getBoundingClientRect(),style=getComputedStyle(el);
   const ring=Math.max(0,parseFloat(style.outlineWidth)+parseFloat(style.outlineOffset));
   const left=bounds.left+region.clientLeft,right=left+region.clientWidth,top=bounds.top+region.clientTop,bottom=top+region.clientHeight;
   return {active:el.getAttribute('aria-label')??el.closest('label')?.textContent,focusVisible:el.matches(':focus-visible'),outlineWidth:parseFloat(style.outlineWidth),outlineStyle:style.outlineStyle,ring,control:[rect.left,rect.right,rect.top,rect.bottom],container:[left,right,top,bottom],scrollLeft:region.scrollLeft,scrollWidth:region.scrollWidth,clientWidth:region.clientWidth,
    contained:rect.left-ring>=left-.25&&rect.right+ring<=right+.25&&rect.top-ring>=top-.25&&rect.bottom+ring<=bottom+.25,
    viewportVisible:rect.top-ring>=0&&rect.bottom+ring<=innerHeight,pageOverflow:document.documentElement.scrollWidth>innerWidth};
  });
  observations.push({label,...observation});
  check(label+' active and complete outline contained',observation.active===expected&&observation.focusVisible&&observation.outlineWidth>=2&&observation.outlineStyle!=='none'&&observation.contained&&observation.viewportVisible&&!observation.pageOverflow);
 }
 for(const [context,profile,method,count] of [
  ['AREA_FAN',null,'TRIBOLOGY',3],['VIBRATION_BOILER','boiler-three-point-rms','VIBRATION',9],
  ['VIBRATION_BC','bc-irregular-axis','VIBRATION',11],['VIBRATION_TURBINE','turbine-four-point','VIBRATION',12]]){
  await go();await button('Input Pengukuran').click();await p.getByLabel('Konteks input kandidat').selectOption(context);
  if(profile)await p.getByLabel('Keluarga template kandidat').selectOption(profile);
  await p.getByLabel('Metode',{exact:true}).selectOption(method);await button('Gunakan baris kandidat').click();
  await p.getByLabel('Tipe nilai 1',{exact:true}).selectOption('NUMERIC');await p.getByLabel('Nilai asli 1',{exact:true}).fill('0');
  const values=()=>p.locator('.pdm-measurement-row input,.pdm-measurement-row select').evaluateAll(els=>els.map(el=>el.value));
  const original=await values();
  for(const width of [1440,1920,1280,1152])for(const theme of ['light','dark']){
   await p.setViewportSize({width,height:960});
   const toggle=p.getByRole('button',{name:theme==='dark'?'Ganti ke tema gelap':'Ganti ke tema terang',exact:true});if(await toggle.count())await toggle.click();
   const mode=width===1152?'125-percent-effective-width-proxy':width;
   for(const row of [1,count]){
    const label=`keyboard ${count} rows ${mode} ${theme} row ${row}`;
    await p.getByLabel('Waktu measurement '+row,{exact:true}).focus();await p.locator('.pdm-grid-scroll').evaluate(el=>el.scrollLeft=0);
    await p.keyboard.press('Tab');await visible(label+' Tab','Hapus measurement '+row);
    if(count===12&&row===12&&theme==='light'&&[1440,1920,1280].includes(width))await p.screenshot({path:folder+'/after-'+width+'.png'});
    const next=row===count?p.getByLabel('Observasi (satu per baris)',{exact:true}):p.getByLabel('Titik '+(row+1),{exact:true});
    await p.keyboard.press('Tab');check(label+' forward order',await next.evaluate(el=>el===document.activeElement));
    await p.locator('.pdm-grid-scroll').evaluate(el=>el.scrollLeft=0);await p.keyboard.press('Shift+Tab');await visible(label+' Shift+Tab','Hapus measurement '+row);
    await p.keyboard.press('Shift+Tab');await visible(label+' reverse to time','Waktu measurement '+row);
    await p.keyboard.press('Tab');await visible(label+' return Tab','Hapus measurement '+row);
    await p.getByLabel('Parameter '+row,{exact:true}).focus();await p.keyboard.press('Shift+Tab');await visible(label+' left field','Titik '+row);
   }
  }
  check('keyboard preserves all native values '+count,JSON.stringify(original)===JSON.stringify(await values()));
  await p.setViewportSize({width:1440,height:960});
  await button('Tambah baris').click();check('pointer add row '+count,await p.locator('.pdm-measurement-row').count()===count+1);
  await button('Hapus measurement '+(count+1)).click();check('pointer remove row '+count,await p.locator('.pdm-measurement-row').count()===count&&await p.getByLabel('Nilai asli 1',{exact:true}).inputValue()==='0');
  p.once('dialog',d=>d.dismiss());await button('Batal input').click();check('cancelled discard retains dirty draft '+count,await p.getByLabel('Nilai asli 1',{exact:true}).inputValue()==='0');
  await p.evaluate(()=>window.dispatchEvent(new Event('focus')));await p.getByLabel('Nilai asli 1',{exact:true}).waitFor();check('same-session refresh retains dirty draft '+count,await p.getByLabel('Nilai asli 1',{exact:true}).inputValue()==='0');
  p.once('dialog',d=>d.accept());await button('Batal input').click();
 }
 await p.setViewportSize({width:1440,height:1086});await p.evaluate(()=>{document.documentElement.dataset.theme='light';localStorage.setItem('nadi-theme','light');});
 writeFileSync(folder+'/results.json',JSON.stringify({status:'PASS',synthetic_fixtures:true,official_runtime_access:false,zoom:'Actual browser chrome zoom unavailable in headless harness. 1152 CSS pixels is an additional 1440/1.25 effective-width proxy, not actual browser zoom.',observations},null,2));
}
