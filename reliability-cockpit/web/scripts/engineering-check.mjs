import assert from "node:assert/strict";
import {readFileSync, mkdtempSync, rmSync} from "node:fs";
import {join} from "node:path";
import {tmpdir} from "node:os";
import {execFileSync} from "node:child_process";
import {createRequire} from "node:module";

const output=mkdtempSync(join(tmpdir(),"nadi-engineering-types-"));
let count=0;
function test(name,operation){operation();count++;console.log(`PASS ${name}`);}
try {
  execFileSync(process.execPath,["node_modules/typescript/bin/tsc","lib/engineering.ts","--outDir",output,"--target","ES2022","--module","commonjs","--skipLibCheck"],{stdio:"pipe"});
  const require=createRequire(import.meta.url);
  const {engineeringMode,demoTransition,evidenceValue,parseHypotheses}=require(join(output,"engineering.js"));
  const fixture=JSON.parse(readFileSync("fixtures/engineering-workspace.json","utf8"));
  const case0=fixture.cases[0];const now="2026-10-08T13:00:00Z";
  test("default flag off",()=>assert.equal(engineeringMode({}),"OFF"));
  test("production cannot run demo",()=>assert.equal(engineeringMode({NADI_ENGINEERING_WORKSPACE_ENABLED:"true",NADI_ENGINEERING_DEMO_ENABLED:"true",NODE_ENV:"production"}),"BLOCKED"));
  test("explicit development demo",()=>assert.equal(engineeringMode({NADI_ENGINEERING_WORKSPACE_ENABLED:"true",NADI_ENGINEERING_DEMO_ENABLED:"true",NODE_ENV:"development"}),"DEMO"));
  test("source unit/value preserved",()=>assert.equal(evidenceValue(case0.evidence[0]),"42.25"));
  test("null is unknown never zero",()=>assert.equal(evidenceValue({...case0.evidence[0],snapshot:{...case0.evidence[0].snapshot,condition:{...case0.evidence[0].snapshot.condition,value:null}}}),"Unknown"));
  test("numeric zero preserved",()=>assert.equal(evidenceValue({...case0.evidence[0],snapshot:{...case0.evidence[0].snapshot,condition:{...case0.evidence[0].snapshot.condition,value:0}}}),"0"));
  test("stale revision denied",()=>assert.throws(()=>demoTransition(case0,99,"engineer-fixture","SUBMIT",now),/REVISION_CONFLICT/));
  test("self approval denied",()=>assert.throws(()=>demoTransition({...case0,status:"IN_REVIEW"},1,"engineer-fixture","APPROVED",now,undefined,"x"),/INDEPENDENT_REVIEWER_REQUIRED/));
  test("previous contributor denied",()=>assert.throws(()=>demoTransition({...case0,status:"IN_REVIEW",contributors:["reviewer-fixture"]},1,"reviewer-fixture","APPROVED",now,undefined,"x"),/INDEPENDENT_REVIEWER_REQUIRED/));
  const submitted=demoTransition(case0,1,"engineer-fixture","SUBMIT",now).document;
  test("submit doesn't approve",()=>assert.equal(submitted.status,"IN_REVIEW"));
  const approved=demoTransition(submitted,2,"reviewer-fixture","APPROVED",now,undefined,"Synthetic rationale");
  test("independent review attributable",()=>assert.equal(approved.document.review.reviewer,"reviewer-fixture"));
  test("review audit previous revision",()=>assert.equal(approved.event.previous_revision,2));
  test("cannot edit approved case",()=>assert.throws(()=>demoTransition(approved.document,3,"engineer-fixture","NOTE",now,undefined,"x"),/INVALID_TRANSITION/));
  test("reopen retains history/clears decision",()=>assert.equal(demoTransition(approved.document,3,"reviewer-fixture","REOPEN",now,undefined,"New question").document.review,null));
  test("duplicate evidence denied",()=>assert.throws(()=>demoTransition(case0,1,"engineer-fixture","LINK",now,{evidence:[case0.evidence[0]]}),/DUPLICATE_EVIDENCE/));
  test("cross asset evidence denied",()=>assert.throws(()=>demoTransition({...case0,evidence:[]},1,"engineer-fixture","LINK",now,{evidence:[{...case0.evidence[0],canonical_asset_id:"asset:OTHER"}]}),/INVALID_EVIDENCE/));
  const saveHypotheses=items=>demoTransition(case0,case0.revision,"engineer-fixture","SAVE",now,
    {title:case0.title,problem_statement:case0.problem_statement,investigation:{...case0.investigation,hypotheses:items}});
  test("optional empty hypotheses allowed",()=>assert.deepEqual(saveHypotheses([]).document.investigation.hypotheses,[]));
  test("20 hypotheses of 2000 characters allowed",()=>assert.equal(saveHypotheses(Array(20).fill("x".repeat(2000))).document.investigation.hypotheses.length,20));
  test("Unicode codepoint boundary preserved",()=>assert.equal(saveHypotheses(["🛠".repeat(2000)]).document.investigation.hypotheses[0],"🛠".repeat(2000)));
  test("21 hypotheses rejected",()=>assert.throws(()=>saveHypotheses(Array(21).fill("x")),/at most 20/));
  test("overlong hypotheses rejected",()=>{for(const item of ["x".repeat(2001),"🛠".repeat(2001)])assert.throws(()=>saveHypotheses([item]),/2,000 characters/);});
  test("empty and Unicode whitespace rejected",()=>{for(const item of [""," ","\t\r\n","\u001c","\u0085","\u00a0","\u3000"])assert.throws(()=>saveHypotheses([item]),/nonblank/);});
  test("strict string hypotheses",()=>{for(const item of [null,1,true,{},[]])assert.throws(()=>saveHypotheses([item]),/nonblank/);});
  test("nonblank content is not trimmed",()=>{for(const item of ["  hypothesis  ","\ufeff"])assert.equal(saveHypotheses([item]).document.investigation.hypotheses[0],item);});
  test("empty editor becomes optional empty list",()=>assert.deepEqual(parseHypotheses(""),[]));
  test("blank editor entries retained and rejected",()=>{for(const text of ["a\n\nb","a\n","   "])assert.throws(()=>saveHypotheses(parseHypotheses(text)),/nonblank/);});
  test("CRLF editor entries parsed exactly",()=>assert.deepEqual(parseHypotheses("a\r\nb"),["a","b"]));
  test("failed save preserves case and revision",()=>{const before=JSON.stringify(case0);assert.throws(()=>saveHypotheses([" "]),/nonblank/);assert.equal(JSON.stringify(case0),before);});
  test("invalid hypotheses cannot be submitted",()=>{
    for(const items of [Array(21).fill("x"),["x".repeat(2001)],[" "]])
      assert.throws(()=>demoTransition({...case0,investigation:{...case0.investigation,hypotheses:items}},case0.revision,"engineer-fixture","SUBMIT",now),/Hypothes/);
  });
  test("submit preserves valid hypothesis boundary",()=>{
    const saved=saveHypotheses(Array(20).fill("x".repeat(2000))).document;
    assert.equal(demoTransition(saved,saved.revision,"engineer-fixture","SUBMIT",now).document.status,"IN_REVIEW");
  });
  const schema=JSON.parse(readFileSync("../../reliability-data-contracts/schemas/engineering-case.schema.json","utf8"));
  test("frontend limits match canonical hypothesis schema",()=>{
    const constraint=schema.$defs.Investigation.properties.hypotheses;
    assert.equal(constraint.maxItems,20);assert.equal(constraint.items.minLength,1);assert.equal(constraint.items.maxLength,2000);
    const nonblank=new RegExp(constraint.items.pattern,"u");
    for(const item of [""," ","\u001c","\u0085","\u00a0","\u3000","\ufeff"," x "]){
      let accepted=true;try{saveHypotheses([item]);}catch{accepted=false;}
      assert.equal(accepted,nonblank.test(item));
    }
  });
  const view=readFileSync("components/EngineeringWorkspace.tsx","utf8");
  test("editor preserves unsaved protection on rejection",()=>{
    assert.ok(view.includes("hypotheses:parseHypotheses(hypothesis)"));
    assert.ok(view.includes('window.addEventListener("beforeunload",warn)'));
    assert.ok(view.includes('hasUnsaved&&!window.confirm'));
    const failure=view.slice(view.indexOf("} catch(error)"),view.indexOf("function createDraft"));
    assert.ok(failure.includes("setFeedback"));assert.ok(!failure.includes("setDirty(false)"));assert.ok(!failure.includes("setHypothesis"));
  });
  test("notes rendered as text",()=>{assert.ok(view.includes("{item.text}"));assert.ok(!view.includes("dangerouslySetInnerHTML"));});
  test("no operational request",()=>assert.ok(!view.includes("fetch(")));
  test("explicit synthetic banner",()=>assert.ok(view.includes("SYNTHETIC LOCAL DEMO")));
  test("revision conflict pinned",()=>assert.ok(view.includes("demoTransition(current,loadedRevision")));
  test("unknown and quality caveat",()=>assert.ok(view.includes("UNKNOWN freshness remains unknown")));
  console.log(`Engineering frontend checks passed: ${count}`);
} finally {rmSync(output,{recursive:true,force:true});}
