import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),temp=mkdtempSync(join(tmpdir(),'nadi-ph2-ui-'));
let count=0;const check=(name,fn)=>{fn();count++;console.log('PASS '+name);};
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','components/CaseForm.tsx','lib/case-form.ts','--outDir',temp,'--rootDir','.','--module','commonjs','--target','ES2022','--jsx','react-jsx','--esModuleInterop','--skipLibCheck','--resolveJsonModule','--moduleResolution','node'],{stdio:'pipe'});
 process.env.NODE_PATH=join(process.cwd(),'node_modules');require('node:module').Module._initPaths();
 const {emptyDraft}=require(join(temp,'lib/case-records.js'));
 const {validateCaseForm,independentCaseReviewer}=require(join(temp,'lib/case-form.js'));
 const draft={...emptyDraft('asset:SYNTHETIC:PH2'),title:'Synthetic test',problem_statement:'Human observation'};
 check('empty optional lists remain valid',()=>validateCaseForm(draft));
 check('blank title or problem denied without normalizing',()=>{for(const patch of [{title:' '},{problem_statement:'\u0085'}])assert.throws(()=>validateCaseForm({...draft,...patch}));});
 check('all investigation lists enforce canonical cardinality',()=>{for(const field of Object.keys(draft.investigation).filter(x=>x!=='operating_context'))assert.throws(()=>validateCaseForm({...draft,investigation:{...draft.investigation,[field]:Array(21).fill('x')}}));});
 check('blank list item is rejected rather than silently removed',()=>assert.throws(()=>validateCaseForm({...draft,investigation:{...draft.investigation,observations:['x','']}})));
 check('unicode count matches contract and preserves original content',()=>{const next={...draft,investigation:{...draft.investigation,hypotheses:['🛠'.repeat(2000),'  original  ']}};validateCaseForm(next);assert.equal(next.investigation.hypotheses[1],'  original  ');assert.throws(()=>validateCaseForm({...draft,investigation:{...draft.investigation,hypotheses:['🛠'.repeat(2001)]}}));});
 const row={...draft,created_by:'author',assigned_engineer:'assignee',contributors:['previous-contributor']};
 check('review affordance excludes author assignee and prior contributors',()=>{for(const subject of ['author','assignee','previous-contributor'])assert.equal(independentCaseReviewer(row,subject),false);assert.equal(independentCaseReviewer(row,'reviewer'),true);});
 const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),Form=require(join(temp,'components/CaseForm.js')).default;
 const html=renderToStaticMarkup(React.createElement(Form,{initial:draft,assets:[draft.canonical_asset_id],busy:true,onSave:async()=>{},onCancel(){}}));
 check('form has three labeled groups and busy fields',()=>{assert.equal((html.match(/<fieldset disabled=""/g)||[]).length,3);for(const name of ['Identitas','Masalah','Catatan investigasi'])assert.ok(html.includes(name));});
 check('all investigation inputs retain explicit labels',()=>{for(const key of ['title','problem','context','observations','hypotheses'])assert.ok(html.includes('for="case-'+key+'"'));});
 console.log('Phase 2 UI behavior checks passed: '+count);
}finally{rmSync(temp,{recursive:true,force:true});}
