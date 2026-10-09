// Browser-memory presentation simulation ONLY. No sessions, authority or API writes.
import {validateInspection, type InspectionInput} from "./manual-pdm";
import {validateHypotheses} from "./engineering";
export type Stage="DRAFT"|"SUBMITTED"|"UNDER_REVIEW"|"APPROVED"|"RETURNED"|"REJECTED";
export type Event={revision:number;action:string;at:string;actor:string;reason:string};
export type Inspection={id:string;asset:string;input:InspectionInput;status:Stage;revision:number;
  reviewer:string|null;history:Event[];attachment:{filename:string;status:"METADATA_ONLY_NOT_UPLOADED"}|null};
export type ReviewedStage="DRAFT"|"IN_REVIEW"|"APPROVED"|"REJECTED";
export type Finding={id:string;asset:string;inspection:string;inspectionRevision:number;hypotheses:string[];
  status:ReviewedStage;revision:number;history:Event[]};
export type Proposal={id:string;asset:string;caseId:string;caseRevision:number;status:ReviewedStage;revision:number;
  action:string;priority:"LOW"|"NORMAL"|"HIGH";pic:string;target:string|null;wo:string|null;
  followup:"PROPOSED"|"PLANNED"|"IN_PROGRESS"|"COMPLETED"|"VERIFIED";history:Event[]};
const inspector="demo-inspector", reviewer="demo-reviewer";
const event=(revision:number,action:string,at:string,actor:string,reason:string):Event=>({revision,action,at,actor,reason});
function guard(record:{revision:number},expected:number){if(record.revision!==expected)throw Error("REVISION_CONFLICT: reload; unsaved input retained.");}
function independent(actor:string){if(actor!==reviewer)throw Error("INDEPENDENT_REVIEWER_REQUIRED (synthetic simulation).");}
export function inspectionDraft(input:InspectionInput,id:string,now:string,filename=""):Inspection {
  validateInspection(input);
  if(!input.inspected_at||Date.parse(input.inspected_at)>Date.parse(now))throw Error("Inspection requires a non-future timestamp with timezone.");
  if(filename&&(!/^[A-Za-z0-9_. -]{1,180}$/.test(filename)||filename.includes("..")))throw Error("Safe filename only; file storage disabled.");
  return {id,asset:input.canonical_asset_id,input:structuredClone(input),status:"DRAFT",revision:1,reviewer:null,
    attachment:filename?{filename,status:"METADATA_ONLY_NOT_UPLOADED"}:null,history:[event(1,"CREATE",now,inspector,"Synthetic draft")]};
}
export function inspectionEdit(row:Inspection,expected:number,input:InspectionInput,now:string,filename=""):Inspection {
  guard(row,expected);
  if(row.status!=="DRAFT"||input.canonical_asset_id!==row.asset)throw Error("IMMUTABLE_APPROVED_OR_ASSET_IDENTITY");
  const draft=inspectionDraft(input,row.id,now,filename),revision=row.revision+1;
  return {...row,input:draft.input,attachment:draft.attachment,revision,
    history:[...row.history,event(revision,"UPDATE",now,inspector,"Synthetic draft correction")]};
}
export function inspectionAction(row:Inspection,expected:number,action:"SUBMIT"|"BEGIN_REVIEW"|"APPROVED"|"RETURNED"|"REJECTED"|"REVISE",now:string,actor=inspector,reason=""):Inspection {
  guard(row,expected);let status:Stage=row.status,assigned=row.reviewer;
  if(action==="SUBMIT"){if(row.status!=="DRAFT"||actor!==inspector)throw Error("INVALID_TRANSITION");validateInspection(row.input);status="SUBMITTED";}
  else if(action==="BEGIN_REVIEW"){independent(actor);if(row.status!=="SUBMITTED")throw Error("INVALID_TRANSITION");status="UNDER_REVIEW";assigned=actor;}
  else if(action==="REVISE"){if(!["RETURNED","REJECTED"].includes(row.status)||actor!==inspector)throw Error("INVALID_TRANSITION");status="DRAFT";assigned=null;}
  else {independent(actor);if(row.status!=="UNDER_REVIEW"||assigned!==actor||!reason.trim())throw Error("INVALID_REVIEW");status=action;}
  const revision=row.revision+1;return {...row,status,reviewer:assigned,revision,history:[...row.history,event(revision,action,now,actor,reason)]};
}
export function findingDraft(row:Inspection,hypotheses:string[],id:string,now:string):Finding {
  if(row.status!=="APPROVED")throw Error("APPROVED_INSPECTION_REQUIRED");validateHypotheses(hypotheses);
  return {id,asset:row.asset,inspection:row.id,inspectionRevision:row.revision,hypotheses:[...hypotheses],status:"DRAFT",revision:1,history:[event(1,"CREATE",now,inspector,"Frozen reviewed human evidence")]};
}
export function findingAction(row:Finding,inspection:Inspection,expected:number,action:"SUBMIT"|"APPROVED"|"REJECTED",now:string,actor=inspector,reason="Synthetic fixture decision"):Finding {
  guard(row,expected);validateHypotheses(row.hypotheses);
  if(inspection.asset!==row.asset||inspection.id!==row.inspection||inspection.revision!==row.inspectionRevision||inspection.status!=="APPROVED")throw Error("EVIDENCE_VERSION_CHANGED");
  if(action==="SUBMIT"){if(row.status!=="DRAFT"||actor!==inspector)throw Error("INVALID_TRANSITION");}
  else{independent(actor);if(row.status!=="IN_REVIEW")throw Error("INVALID_TRANSITION");}
  const revision=row.revision+1;return {...row,status:action==="SUBMIT"?"IN_REVIEW":action,revision,history:[...row.history,event(revision,action,now,actor,reason)]};
}
export function proposalDraft(row:Finding,id:string,now:string,fields:Pick<Proposal,"action"|"priority"|"pic"|"target"|"wo">):Proposal {
  if(row.status!=="APPROVED")throw Error("REVIEWED_CASE_REQUIRED");
  if(!fields.action.trim()||Array.from(fields.action).length>6000||!fields.pic.trim()||fields.pic.length>160)throw Error("Enter bounded action and internal PIC.");
  if(!["LOW","NORMAL","HIGH"].includes(fields.priority)||fields.target!==null&&!/^\d{4}-\d{2}-\d{2}$/.test(fields.target))throw Error("INVALID_PROPOSAL");
  if(fields.target!==null&&new Date(fields.target+"T00:00:00Z").toISOString().slice(0,10)!==fields.target)throw Error("INVALID_TARGET_DATE");
  if(fields.wo!==null&&fields.wo!=="maintenance:SYNTHETIC:WO-A")throw Error("EXISTING_WO_REFERENCE_REQUIRED");
  if(fields.wo&&row.asset!=="asset:SYNTHETIC:A")throw Error("CROSS_ASSET_REFERENCE");
  return {...fields,id,asset:row.asset,caseId:row.id,caseRevision:row.revision,status:"DRAFT",revision:1,followup:"PROPOSED",history:[event(1,"CREATE",now,inspector,"NADI proposal only; no maintenance authorization")]};
}
export function proposalAction(row:Proposal,finding:Finding,expected:number,action:"SUBMIT"|"APPROVED"|"REJECTED"|"PLANNED"|"IN_PROGRESS"|"COMPLETED"|"VERIFIED",now:string,actor=inspector,closure:Inspection|null=null,reason="Synthetic fixture decision"):Proposal {
  guard(row,expected);
  if(finding.asset!==row.asset||finding.id!==row.caseId||finding.revision!==row.caseRevision||finding.status!=="APPROVED")throw Error("REVIEWED_CASE_CHANGED");
  let status=row.status,followup=row.followup;
  if(action==="SUBMIT"){if(status!=="DRAFT"||actor!==inspector)throw Error("INVALID_TRANSITION");status="IN_REVIEW";}
  else if(action==="APPROVED"||action==="REJECTED"){independent(actor);if(status!=="IN_REVIEW")throw Error("INVALID_TRANSITION");status=action;}
  else if(action==="VERIFIED"){independent(actor);if(status!=="APPROVED"||followup!=="COMPLETED"||!closure||closure.status!=="APPROVED"||closure.asset!==row.asset)throw Error("COMPLETION_EVIDENCE_REQUIRED");followup=action;}
  else {if(actor!==inspector||status!=="APPROVED"||({PROPOSED:"PLANNED",PLANNED:"IN_PROGRESS",IN_PROGRESS:"COMPLETED"} as Record<string,string>)[followup]!==action)throw Error("INVALID_TRANSITION");followup=action;}
  const revision=row.revision+1;return {...row,status,followup,revision,history:[...row.history,event(revision,action,now,actor,action==="VERIFIED"?`${reason}; local follow-up reviewed with ${closure?.id} r${closure?.revision}; no WO closure`:reason)]};
}
export function actionBoard(rows:Proposal[],now:string){return {awaiting_review:rows.filter(x=>x.status==="IN_REVIEW"),
  overdue:rows.filter(x=>x.status==="APPROVED"&&!['COMPLETED','VERIFIED'].includes(x.followup)&&x.target!==null&&x.target<now.slice(0,10)),
  awaiting_verification:rows.filter(x=>x.status==="APPROVED"&&x.followup==="COMPLETED")};}
