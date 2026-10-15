import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
const temp=mkdtempSync(join(tmpdir(),'nadi-workbook-'));let checks=0;
const test=(label,fn)=>{fn();checks++;console.log('PASS '+label);};
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','lib/pdm-workbook.ts','--outDir',temp,'--target','ES2022','--module','commonjs','--skipLibCheck'],{stdio:'pipe'});
 const require=createRequire(import.meta.url),{workbookProfiles,workbookRows}=require(join(temp,'pdm-workbook.js')),{newEntry,buildDraft,fromInspection}=require(join(temp,'pdm-input.js'));
 test('published dictionary stays aligned with presentation registry',()=>assert.deepEqual(JSON.parse(readFileSync(new URL('../../docs/evidence/nadi-pdm-workbook-01/candidate-dictionary.json',import.meta.url),'utf8')).profiles,workbookProfiles.slice(0,3)));
 let key=100;
 test('three versioned pending profiles and exact header lineage',()=>{assert.deepEqual(workbookProfiles.slice(0,3).map(p=>p.context),['AREA_FAN','AREA_MILL','LOGSHEET_6KV']);for(const p of workbookProfiles.slice(0,3)){assert.equal(p.approval,'PENDING_ENGINEER_VALIDATION');assert.equal(p.version,'candidate-0.1.0');for(const f of p.fields){assert.equal(f.classification,'DIRECT');assert.ok(f.headerCells.length&&f.unitCell&&f.valueRange);}}});
 test('context does not select or approve a method',()=>{const e=newEntry('asset:SYNTHETIC');for(const p of workbookProfiles.slice(0,3))assert.throws(()=>workbookRows(p.id,e.method,()=>String(++key)));assert.equal(e.method,'VIBRATION');});
 test('unknown profile fails closed',()=>assert.throws(()=>workbookRows('unreviewed','TRIBOLOGY',()=>String(++key))));
 test('raw unit tokens stay distinct without conversion',()=>{const [fan,mill,log]=workbookProfiles;assert.deepEqual(fan.fields.map(f=>f.unit),['Cst','mgKOH/g','ppm']);assert.deepEqual(mill.fields.map(f=>f.unit),['%','mg KOH/g','ppm']);assert.deepEqual(log.fields.map(f=>f.unit),['%','Ω','dB']);assert.ok(!log.fields.some(f=>['A','V','RMS'].includes(f.unit)));});
 for(const p of workbookProfiles){
  const rows=workbookRows(p.id,p.methodTerm,()=> 'row-'+ ++key);
  test(p.id+' has no invented values points or times',()=>{assert.equal(rows.length,p.fields.length);for(const row of rows){assert.equal(row.kind,'UNKNOWN');assert.equal(row.value,'');assert.equal(row.point,'');assert.equal(row.time,'');}assert.deepEqual(rows.map(r=>r.quantity),p.fields.map(f=>f.label));});
  const e={...newEntry('asset:SYNTHETIC'),inputContext:p.context,method:p.methodTerm,version:'SYNTHETIC-user-version',time:'2026-10-09T09:00:00+07:00',rows};
  rows[0]={...rows[0],kind:'NUMERIC',value:'0',time:'2026-10-09T09:01:00+07:00'};
  const draft=buildDraft(e,'synthetic-author',[e.asset],undefined,Date.parse('2026-10-10T00:00:00Z'));
  test(p.id+' preserves zero null units and timezone',()=>{assert.equal(draft.measurements[0].value,0);if(rows.length>1){assert.equal(draft.measurements[1].value,null);assert.equal(draft.measurements[1].measured_at,null);}assert.equal(draft.measurements[0].unit,p.fields[0].unit||null);assert.equal(draft.measurements[0].measured_at,rows[0].time);assert.equal(draft.inspected_at,e.time);});
  test(p.id+' has no hidden template metadata or approval',()=>{assert.deepEqual(draft.method_extension,{});for(const key of ['template_id','inputContext','source_ref','approval','assessment','source_cells'])assert.equal(key in draft,false);assert.ok(p.unresolved.length);});
  test(p.id+' edit roundtrip retains values and extension',()=>{const record={...draft,revision:3,record_id:'inspection:SYNTHETIC',status:'DRAFT',method_extension:{legacy_note:'SYNTHETIC'},attachments:[],case_refs:[]};const next=buildDraft(fromInspection(record),'synthetic-author',[e.asset],record);assert.deepEqual(next.measurements,draft.measurements);assert.deepEqual(next.method_extension,record.method_extension);});
 }
 test('row instances and keys independent',()=>{const p=workbookProfiles[0],a=workbookRows(p.id,p.methodTerm,()=>String(++key)),b=workbookRows(p.id,p.methodTerm,()=>String(++key));a[0].unit='edited';assert.notEqual(a[0].key,b[0].key);assert.equal(b[0].unit,'Cst');assert.equal(p.fields[0].unit,'Cst');});

 test('new dictionary and all 42 fields stay aligned',()=>assert.deepEqual(JSON.parse(readFileSync(new URL('../../docs/evidence/nadi-pdm-workbook-02/candidate-dictionary.json',import.meta.url),'utf8')).profiles,workbookProfiles.slice(3)));
 test('new families require exact method without hidden conversion',()=>{for(const p of workbookProfiles.slice(3)){assert.equal(p.approval,'PENDING_ENGINEER_VALIDATION');assert.throws(()=>workbookRows(p.id,p.methodTerm==='OTHER'?'IR_THERMOGRAPHY':'MCSA',()=>String(++key)));}});
 test('RMS spelling and incomplete BC axes remain distinct',()=>{const rms=workbookProfiles.find(p=>p.id==='boiler-three-point-rms'),bc=workbookProfiles.find(p=>p.id==='bc-irregular-axis');assert.ok(rms.fields.every(f=>f.unit==='mm/s-rms'));assert.ok(bc.fields.some(f=>f.label==='6A'));assert.ok(!bc.fields.some(f=>f.label==='6H'));});
 test('CEP does not infer IRT or temperature units from baseline',()=>{for(const p of workbookProfiles.filter(p=>p.context==='CEP_CBM')){assert.equal(p.methodTerm,'OTHER');for(const f of p.fields.filter(f=>f.classification==='AMBIGUOUS')){assert.equal(f.unit,'');assert.equal(f.unitCell,'');}}});
 test('source axes are display-only; canonical point and orientation stay unbound',()=>{for(const p of workbookProfiles.filter(p=>p.methodTerm==='VIBRATION')){const rows=workbookRows(p.id,p.methodTerm,()=>String(++key));assert.ok(rows.every(r=>r.point===''&&r.time===''));assert.ok(p.fields.every(f=>f.sourcePointLabel===f.label));}});
 test('date-only does not invent midnight',()=>{const p=workbookProfiles[3];assert.throws(()=>buildDraft({...newEntry('asset:SYNTHETIC'),method:p.methodTerm,version:'SYNTHETIC',time:'2026-10-09',rows:workbookRows(p.id,p.methodTerm,()=>String(++key))},'synthetic-author',['asset:SYNTHETIC']));});
 console.log('Workbook candidate safety checks: '+checks);
}finally{rmSync(temp,{recursive:true,force:true});}
