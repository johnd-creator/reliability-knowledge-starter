// Presentation contract for browser-memory fixtures, never an authority source.
import {validateHypotheses, type CaseStatus} from "./engineering";
export const methods=["VIBRATION","IR_THERMOGRAPHY","MCSA","TRIBOLOGY","DGA","OTHER"] as const;
export type Method=typeof methods[number];
export type InspectionInput={canonical_asset_id:string;method:Method;method_version:string;inspector_ref:string;
  inspected_at:string|null;quantity:string;value:number|string|boolean|null;unit:string|null;operating_context:string;
  observations:string[];interpretations:string[]};
export type LocalInspection={id:string;input:InspectionInput;status:CaseStatus;assessment:"NOT_ASSESSED";
  revision:number;history:{revision:number;action:string;at:string;actor:string}[]};
export function validateInspection(input:InspectionInput):void {
  if(!/^[A-Za-z0-9_.:-]{1,200}$/.test(input.canonical_asset_id))throw Error("Exact synthetic asset identity required.");
  if(!methods.includes(input.method))throw Error("Select an inspection method.");
  for(const [label,value,max] of [["Method version",input.method_version,80],["Inspector",input.inspector_ref,160],["Quantity",input.quantity,120]] as const)
    if(!value.trim()||Array.from(value).length>max)throw Error(`${label}: enter bounded nonblank text.`);
  if(typeof input.value==="number"&&!Number.isFinite(input.value))throw Error("Measurement must be finite or unknown.");
  if(typeof input.value==="string"&&Array.from(input.value).length>2000)throw Error("Measurement text exceeds 2,000 characters.");
  if(input.unit!==null&&Array.from(input.unit).length>40)throw Error("Unit exceeds 40 characters.");
  if(Array.from(input.operating_context).length>6000)throw Error("Operating context exceeds 6,000 characters.");
  if(input.inspected_at!==null&&(!/(Z|[+-]\d\d:\d\d)$/.test(input.inspected_at)||!Number.isFinite(Date.parse(input.inspected_at))))throw Error("Inspection time requires an explicit timezone.");
  validateHypotheses(input.observations);validateHypotheses(input.interpretations);
}
export function enteredValue(text:string,kind:"NUMERIC"|"TEXT"|"BOOLEAN"|"UNKNOWN"):number|string|boolean|null {
  if(kind==="UNKNOWN")return null;
  if(kind==="TEXT")return text;
  if(kind==="BOOLEAN") {if(text==="true")return true;if(text==="false")return false;throw Error("Boolean requires true or false.");}
  if(!text.trim()||!Number.isFinite(Number(text)))throw Error("Enter a finite numeric measurement or choose UNKNOWN.");
  return Number(text);
}
export function localRecord(input:InspectionInput,now:string,id:string):LocalInspection {
  validateInspection(input);
  if(input.inspected_at&&Date.parse(input.inspected_at)>Date.parse(now))throw Error("Inspection time cannot be in the future.");
  return {id,input:structuredClone(input),status:"DRAFT",assessment:"NOT_ASSESSED",revision:1,
    history:[{revision:1,action:"LOCAL_DRAFT",at:now,actor:"synthetic-inspector"}]};
}
export function submitLocal(record:LocalInspection,expected:number,now:string):LocalInspection {
  if(record.revision!==expected)throw Error("REVISION_CONFLICT: reload; your unsaved input is retained.");
  if(record.status!=="DRAFT")throw Error("Record is no longer editable.");
  validateInspection(record.input);
  return {...record,status:"IN_REVIEW",revision:record.revision+1,
    history:[...record.history,{revision:record.revision+1,action:"LOCAL_SUBMIT",at:now,actor:"synthetic-inspector"}]};
}
