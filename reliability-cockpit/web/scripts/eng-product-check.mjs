import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),React=require('react'),{renderToStaticMarkup}=require('react-dom/server');
const temp=mkdtempSync(join(tmpdir(),'nadi-eng-ui-'));let count=0;
function check(label,fn){fn();count++;console.log('PASS '+label);}
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','components/CaseForm.tsx','lib/case-records.ts','--outDir',temp,'--rootDir','.','--module','commonjs','--target','ES2022','--jsx','react-jsx','--esModuleInterop','--skipLibCheck'],{stdio:'pipe'});
 process.env.NODE_PATH=join(process.cwd(),'node_modules');require('node:module').Module._initPaths();
 const {emptyDraft,caseDraft}=require(join(temp,'lib/case-records.js'));
 const Form=require(join(temp,'components/CaseForm.js')).default;
 const draft=emptyDraft('asset:SYNTHETIC:A');
 const html=renderToStaticMarkup(React.createElement(Form,{initial:draft,assets:['asset:SYNTHETIC:A'],busy:false,onSave:async()=>{},onCancel(){}}));
 check('all structured investigation fields have labels',()=>{for(const x of ['title','problem','context','observed_symptoms','hypotheses','observations','open_questions','proposed_next_checks'])assert.ok(html.includes('for="case-'+x+'"'));});
 check('case DTO excludes server-owned status identity and revision',()=>assert.deepEqual(Object.keys(caseDraft({...draft,status:'APPROVED',revision:5,created_by:'other'})).sort(),Object.keys(draft).sort()));
 check('blank investigation remains optional not synthetic evidence',()=>assert.deepEqual(draft.investigation.hypotheses,[]));
 const attack=renderToStaticMarkup(React.createElement(Form,{initial:{...draft,title:'<script>attack()</script>'},assets:['asset:SYNTHETIC:A'],busy:true,onSave:async()=>{},onCancel(){}}));
 check('form escapes text and blocks submission while busy',()=>{assert.ok(attack.includes('&lt;script&gt;'));assert.ok(attack.includes('disabled=""'));});
 check('all new routes require development plus QA opt-in',()=>{for(const x of ['cases','advisories','inbox'])assert.ok(readFileSync('app/engineering/'+x+'/page.tsx','utf8').includes("process.env.NODE_ENV==='development'&&process.env.NADI_ENGINEERING_QA_ENABLED==='true'"));});
 check('failed intent retains idempotency ID and has no browser storage',()=>{const s=readFileSync('components/useQaCommand.ts','utf8');assert.ok(s.includes('pending.current?.key!==key'));assert.ok(s.includes('request_id:pending.current.id'));assert.ok(!/localStorage|sessionStorage/.test(s));assert.ok(s.includes('e.status===409'));});
 check('advisory recipient has no external channel or attachment download',()=>{const s=readFileSync('components/AdvisoryWorkspace.tsx','utf8');assert.ok(s.includes('Acknowledge receipt only'));assert.ok(!/mailto:|tel:|whatsapp|dangerouslySetInnerHTML|download=/.test(s));assert.ok(s.includes("item.availability!=='IN_APP_QA_AVAILABLE'"));});
 check('full provenance hashes are not ellipsized in product workspaces',()=>{const css=readFileSync('app/globals.css','utf8');assert.ok(css.includes('white-space:normal;overflow:visible;text-overflow:clip;overflow-wrap:anywhere'));});
 console.log('Engineering product UI checks passed: '+count);
}finally{rmSync(temp,{recursive:true,force:true});}
