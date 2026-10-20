import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),temp=mkdtempSync(join(tmpdir(),'nadi-frozen-case-'));
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','components/FrozenCaseEvidence.tsx','--outDir',temp,'--rootDir','.','--module','commonjs','--target','ES2022','--jsx','react-jsx','--esModuleInterop','--skipLibCheck','--resolveJsonModule','--moduleResolution','node'],{stdio:'pipe'});
 process.env.NODE_PATH=join(process.cwd(),'node_modules');require('node:module').Module._initPaths();
 const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),View=require(join(temp,'components/FrozenCaseEvidence.js')).default;
 const evidence={mode:'FROZEN_SNAPSHOT',source:'NADI_CONDITION',unit:'A',freshness:'STALE',freshness_policy_ref:'source-age:120',quality_good:false,quality_questionable:true,quality_substituted:false,quality_annotated:null,identity_status:'VERIFIED',signal_approval:'APPROVED',observed_at:'2026-10-09T00:00:00Z',linked_at:'2026-10-09T01:00:00Z',linked_by:'author',snapshot:{condition:{value:0,unit:'A',semantic_name:'fixture current',value_type:'NUMERIC',source_timestamp:'2026-10-08T00:00:00Z',collected_at:'2026-10-08T00:01:00Z',evidence_status:'EVIDENCE_AVAILABLE'}}};
 const render=patch=>renderToStaticMarkup(React.createElement(View,{evidence:{...evidence,...patch}}));
 const html=render({});assert.ok(html.includes('<strong>0</strong>'));for(const text of ['STALE','source-age:120','false / true / false / UNKNOWN','2026-10-08T00:01:00Z','VERIFIED / APPROVED','author'])assert.ok(html.includes(text),text);
 console.log('PASS zero value, frozen unit/time, exact quality flags, freshness policy and provenance');
 const nil=render({unit:null,freshness:'UNKNOWN',freshness_policy_ref:null,snapshot:{condition:{...evidence.snapshot.condition,value:null,unit:null}}});assert.ok(nil.includes('<strong>UNKNOWN</strong>'));assert.ok(nil.includes('UNKNOWN'));console.log('PASS null value/unit and unknown policy remain UNKNOWN');
 const digital=render({snapshot:{condition:{...evidence.snapshot.condition,value:{name:'<script>bad()</script>',code:0,is_system:false},value_type:'DIGITAL'}}});assert.ok(digital.includes('&lt;script&gt;'));assert.ok(!digital.includes('<script>'));assert.ok(digital.includes('code 0'));assert.ok(digital.includes('system false'));console.log('PASS original digital code/false preserved and content escaped');
 const live=render({mode:'LIVE_REFERENCE'});assert.ok(!live.includes('<strong>0</strong>'));assert.ok(live.includes('nilai terkini tidak diambil otomatis'));console.log('PASS live reference cannot masquerade as a frozen measurement');
}finally{rmSync(temp,{recursive:true,force:true});}
