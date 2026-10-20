import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
const temp=mkdtempSync(join(tmpdir(),'nadi-pdm-follow-up-'));let checks=0;
const test=(name,fn)=>{fn();checks++;console.log('PASS '+name);};
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','lib/pdm-input.ts','--outDir',temp,'--target','ES2022','--module','commonjs','--skipLibCheck'],{stdio:'pipe'});
 const {buildDraft,newEntry,fromInspection}=createRequire(import.meta.url)(join(temp,'pdm-input.js'));
 const e={...newEntry('asset:SYNTHETIC:A'),version:'synthetic-1',rows:[],observation:'Synthetic original finding',analysisNotes:'  Synthetic analysis\nZero is original  ',analysisFollowUp:'Manual follow-up\nNo automated decision',srReferences:[{key:'1',number:'  00012/SYNTHETIC  ',note:'Manual SR note\nNot verified'}]};
 const draft=buildDraft(e,'author',[e.asset]);
 test('manual notes and SR exact text preserve whitespace/leading zero/newline',()=>{assert.equal(draft.engineering_analysis.notes,e.analysisNotes);assert.equal(draft.sr_references[0].sr_number,e.srReferences[0].number);assert.equal(draft.sr_references[0].follow_up_note,e.srReferences[0].note);assert.equal(draft.canonical_asset_id,e.asset);});
 test('provenance and SR verification fixed without auto Recommendation',()=>{assert.equal(draft.engineering_analysis.provenance,'HUMAN_ENTERED_ENGINEER_NOTES');assert.equal(draft.sr_references[0].verification,'REPORTED_UNVERIFIED');assert.equal(draft.sr_references[0].system,'MAXIMO');assert.equal(draft.recommendation,undefined);});
 test('measurements findings hypotheses remain separate and unchanged',()=>{assert.deepEqual(draft.measurements,[]);assert.deepEqual(draft.observations,['Synthetic original finding']);assert.deepEqual(draft.interpretations,[]);});
 test('revision readback retains analysis and SR strings exactly',()=>{const row={...draft,record_id:'inspection:SYNTHETIC',revision:3};const next=buildDraft(fromInspection(row),'author',[e.asset],row);assert.deepEqual(next.engineering_analysis,draft.engineering_analysis);assert.deepEqual(next.sr_references,draft.sr_references);});
 test('legacy absence never invents manual analysis/SR',()=>{const legacy={...draft};delete legacy.engineering_analysis;delete legacy.sr_references;const next=buildDraft(fromInspection(legacy),'author',[e.asset],legacy);assert.equal(next.engineering_analysis,undefined);assert.equal(next.sr_references,undefined);});
 test('analysis required when follow-up present; notes bounded nonblank',()=>{for(const change of [{analysisNotes:''},{analysisNotes:' '},{analysisNotes:'x'.repeat(6001)},{analysisFollowUp:' '},{analysisFollowUp:'x'.repeat(6001)}])assert.throws(()=>buildDraft({...e,...change},'author',[e.asset]));});
 test('SR nonblank exact unique numbers, bounded list/text',()=>{for(const refs of [[{key:'1',number:'',note:''}],[{key:'1',number:' ',note:''}],[{key:'1',number:'x'.repeat(101),note:''}],[{...e.srReferences[0],note:' '}],[{...e.srReferences[0],note:'x'.repeat(2001)}],[...e.srReferences,...e.srReferences],Array.from({length:11},(_,i)=>({key:String(i),number:String(i),note:''}))])assert.throws(()=>buildDraft({...e,srReferences:refs},'author',[e.asset]));});
 test('explicit clearing removes new context only; unknown fields remain preserved',()=>{const row={...draft,method_extension:{legacy:0}};const next=buildDraft({...fromInspection(row),analysisNotes:'',analysisFollowUp:'',srReferences:[]},'author',[e.asset],row);assert.equal(next.engineering_analysis,undefined);assert.equal(next.sr_references,undefined);assert.equal(next.method_extension.legacy,0);});
 test('foreign asset is still denied with manual context',()=>assert.throws(()=>buildDraft(e,'author',['asset:SYNTHETIC:FOREIGN'])));
 console.log('PdM manual follow-up checks: '+checks);
}finally{rmSync(temp,{recursive:true,force:true});}
