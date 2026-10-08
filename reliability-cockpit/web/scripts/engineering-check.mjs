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
  const {engineeringMode,demoTransition,evidenceValue}=require(join(output,"engineering.js"));
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
  const view=readFileSync("components/EngineeringWorkspace.tsx","utf8");
  test("notes rendered as text",()=>{assert.ok(view.includes("{item.text}"));assert.ok(!view.includes("dangerouslySetInnerHTML"));});
  test("no operational request",()=>assert.ok(!view.includes("fetch(")));
  test("explicit synthetic banner",()=>assert.ok(view.includes("SYNTHETIC LOCAL DEMO")));
  test("revision conflict pinned",()=>assert.ok(view.includes("demoTransition(current,loadedRevision")));
  test("unknown and quality caveat",()=>assert.ok(view.includes("UNKNOWN freshness remains unknown")));
  console.log(`Engineering frontend checks passed: ${count}`);
} finally {rmSync(output,{recursive:true,force:true});}
