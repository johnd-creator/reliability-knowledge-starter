import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
const temp=mkdtempSync(join(tmpdir(),'nadi-pdm-date-'));let checks=0;
const test=(name,fn)=>{fn();checks++;console.log('PASS '+name);};
try {
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','lib/pdm-date.ts','lib/pdm-input.ts','--outDir',temp,'--target','ES2022','--module','commonjs','--skipLibCheck']);
 const require=createRequire(import.meta.url),{pdmDate,pdmClockDate,formatRecordedInstant}=require(join(temp,'pdm-date.js'));
 test('Indonesian calendar dates retain date-only precision and leap years',()=>{
  assert.equal(pdmDate('2019-01-03','DATE'),'3 Januari 2019');
  assert.equal(pdmDate('2000-02-29','DATE'),'29 Februari 2000');
  assert.equal(pdmDate('0004-02-29','DATE'),'29 Februari 0004');
  for(const date of ['1900-02-29','2019-02-29','2026-04-31','2026-00-01','0000-01-01','2026-1-03','03/01/2019'])assert.match(pdmDate(date,'DATE'),/tidak valid/);
 });
 test('reported offset and date survive midnight and non-Indonesian offsets',()=>{
  for(const [value,label] of [['2026-10-21T00:15+07:00','21 Oktober 2026, 00.15 WIB'],['2026-10-21T14:30+08:00','21 Oktober 2026, 14.30 WITA'],['2026-10-21T14:30+09:00','21 Oktober 2026, 14.30 WIT'],['2026-10-20T23:59:59Z','20 Oktober 2026, 23.59.59 UTC'],['2026-10-21T14:30-05:30','21 Oktober 2026, 14.30 UTC-05:30'],['2026-10-21T14:30-00:00','21 Oktober 2026, 14.30 zona waktu belum diketahui']])assert.equal(pdmDate(value),label);
 });
 test('application instants consistently convert to WIB including a genuine day change',()=>{
  assert.equal(formatRecordedInstant('2026-10-20T23:30:00Z'),'21 Oktober 2026, 06.30.00 WIB');
  assert.equal(formatRecordedInstant('2026-10-21T00:15:00+09:00'),'20 Oktober 2026, 22.15.00 WIB');
  assert.equal(formatRecordedInstant('2026-10-21T14:30+07:00'),'21 Oktober 2026, 14.30 WIB');
  assert.equal(formatRecordedInstant('2019-01-03'),'3 Januari 2019');
  assert.equal(formatRecordedInstant('2026-10-21T00:15-00:00'),'21 Oktober 2026, 00.15 zona waktu belum diketahui');
  assert.equal(formatRecordedInstant('2026-10-21T00:15:01.123456Z'),'21 Oktober 2026, 07.15.01,123456 WIB');
 });
 test('proleptic WIB stays fixed UTC+07 before 1964 and does not invent a midnight crossing',()=>{
  for(const year of ['1900','1948','1960'])assert.equal(formatRecordedInstant(year+'-01-01T00:00:00Z'),'1 Januari '+year+', 07.00.00 WIB');
  assert.equal(formatRecordedInstant('1960-01-01T16:45:00Z'),'1 Januari 1960, 23.45.00 WIB');
  assert.equal(formatRecordedInstant('1948-01-01T16:30:00Z'),'1 Januari 1948, 23.30.00 WIB');
  assert.equal(formatRecordedInstant('1960-01-01T17:00:00Z'),'2 Januari 1960, 00.00.00 WIB');
  assert.equal(pdmDate('1960-01-01T16:45:00+07:30','DATETIME'),'1 Januari 1960, 16.45.00 UTC+07:30');
  assert.equal(pdmDate('1960-01-01','DATE'),'1 Januari 1960');
 });
 test('local datetime and time-only never gain a timezone or date',()=>{
  assert.equal(pdmDate('2019-01-03T14:30','LOCAL_DATETIME'),'3 Januari 2019, 14.30 zona waktu belum diketahui');
  assert.equal(pdmDate('14:30:01.123456','TIME'),'14.30.01,123456 · tanggal dan zona waktu belum diketahui');
  assert.equal(pdmDate('2019-01-03T14:30:00.123+07:00'),'3 Januari 2019, 14.30.00,123 WIB');
  assert.match(pdmDate('2019-01-03T14:30+07:00','LOCAL_DATETIME'),/tidak sesuai presisi/);
  assert.match(pdmDate('2019-01-03T14:30','DATETIME'),/tidak sesuai presisi/);
 });
 test('null unknown invalid mixed and raw values have honest Indonesian labels',()=>{
  for(const value of [null,undefined,'','UNKNOWN'])assert.equal(pdmDate(value),'Belum diketahui');
  for(const value of [true,0,123,{},[], '2026-10-21T24:00Z','2026-10-21T14:60Z','2026-10-21T14:30+25:00','2019-02-29T14:30Z','2019-01-03T14:30Z extra','2019-01-03 / 2020-02-04'])assert.match(pdmDate(value),/tidak valid/);
  assert.equal(pdmDate(null,'RAW'),'Teks / serial belum ditafsirkan');
  assert.equal(pdmDate('2019-01-03','UNKNOWN'),'Belum diketahui');
 });
 test('conflicting raw claims are neither parsed nor rewritten',()=>{
  const c={role:'SAMPLE',precision:'DATE',value:'2019-01-03',raw_value:'SHEET CLAIM: 2020-02-04 / serial 43865',source_label:'tanggal'};
  const before=structuredClone(c);assert.equal(pdmClockDate(c),'3 Januari 2019');assert.deepEqual(c,before);
  assert.equal(pdmClockDate({...c,precision:'RAW',value:null}),'Teks / serial belum ditafsirkan');
 });
 test('formatting is independent of browser/server timezone and locale',()=>{
  const code=`const {pdmDate,formatRecordedInstant}=require(${JSON.stringify(join(temp,'pdm-date.js'))});process.stdout.write(pdmDate('2019-01-03')+'|'+pdmDate('2026-10-21T00:15:00+07:00')+'|'+formatRecordedInstant('2026-10-20T23:30Z'));`;
  for(const TZ of ['UTC','America/Los_Angeles','Asia/Jakarta','Pacific/Kiritimati'])assert.equal(execFileSync(process.execPath,['-e',code],{env:{...process.env,TZ,LANG:'en_US.UTF-8'},encoding:'utf8'}),'3 Januari 2019|21 Oktober 2026, 00.15.00 WIB|21 Oktober 2026, 06.30 WIB');
 });
 test('readable presentation preserves draft timestamps and conflicting source claims',()=>{
  const {newEntry,buildDraft,fromInspection}=require(join(temp,'pdm-input.js'));
  const e={...newEntry('asset:SYNTHETIC'),version:'synthetic',time:'2019-01-03T00:15:00+07:00',rows:[{key:'row-1',point:'P',quantity:'Q',kind:'NUMERIC',value:'0',unit:'mm/s',time:'2019-01-03T00:16:00+07:00'}]};
  const draft=buildDraft(e,'synthetic',['asset:SYNTHETIC']);pdmDate(draft.inspected_at);pdmDate(draft.measurements[0].measured_at);
  const next=buildDraft(fromInspection(draft),'synthetic',['asset:SYNTHETIC'],draft);
  assert.equal(next.inspected_at,e.time);assert.equal(next.measurements[0].measured_at,e.rows[0].time);assert.deepEqual(next.measurements,draft.measurements);
 });
 console.log('PdM date checks: '+checks);
} finally {rmSync(temp,{recursive:true,force:true});}
