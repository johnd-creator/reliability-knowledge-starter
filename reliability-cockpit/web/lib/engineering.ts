// Presentation subset of engineering-case.schema.json; not an authorization source.
export type CaseStatus = "DRAFT" | "IN_REVIEW" | "APPROVED" | "REJECTED";
export type Priority = "LOW" | "NORMAL" | "HIGH";
export type Category = "INVESTIGATION" | "MAINTENANCE" | "CONDITION";
export type EvidenceReference = {
  reference_id: string; record_id: string; canonical_asset_id: string;
  kind: string; source: string; mode: "LIVE_REFERENCE" | "FROZEN_SNAPSHOT";
  stable_version: string; source_timestamp: string | null; observed_at: string;
  linked_at: string; linked_by: string; identity_status: "VERIFIED";
  signal_approval: "APPROVED" | "NOT_APPLICABLE";
  freshness: "CURRENT" | "STALE" | "UNKNOWN"; freshness_policy_ref: string | null;
  unit: string | null; quality_good: boolean | null; quality_questionable: boolean | null;
  quality_substituted: boolean | null; quality_annotated: boolean | null;
  snapshot: {label: string; summary: string | null; availability: string; condition: {
    semantic_name: string; value: number | string | boolean | null | {name: string | null; code: number | null; is_system: boolean | null};
    value_type: string; unit: string | null; source_timestamp: string | null;
    collected_at: string; evidence_status: string;
    sources: {pi: {mapping_status: "VERIFIED"; af_element_ref: string}};
  } | null} | null;
};
export type CaseDocument = {
  contract_version: "1.0"; case_id: string; title: string; problem_statement: string;
  canonical_asset_id: string; category: Category; priority: Priority; status: CaseStatus;
  assigned_engineer: string | null; created_at: string; updated_at: string;
  created_by: string; contributors: string[]; revision: number; provenance: "HUMAN_ENGINEERING_RECORD";
  investigation: {observed_symptoms: string[]; operating_context: string; hypotheses: string[];
    observations: string[]; open_questions: string[]; proposed_next_checks: string[]};
  notes: {note_id: string; text: string; actor: string; created_at: string}[];
  evidence: EvidenceReference[];
  review: {reviewer: string; decision: "APPROVED" | "REJECTED"; rationale: string; decided_at: string} | null;
};
export type CaseEvent = {case_id: string; revision: number; previous_revision: number;
  actor: string; action: string; occurred_at: string; changed_fields: string[]; reason: string | null};
export function engineeringMode(environment: Record<string,string | undefined>): "OFF" | "BLOCKED" | "DEMO" {
  if (environment.NADI_ENGINEERING_WORKSPACE_ENABLED !== "true") return "OFF";
  return environment.NODE_ENV === "development" && environment.NADI_ENGINEERING_DEMO_ENABLED === "true" ? "DEMO" : "BLOCKED";
}
export function evidenceValue(reference: EvidenceReference): string {
  const condition = reference.snapshot?.condition;
  if (!condition || condition.value === null) return "Unknown";
  return typeof condition.value === "object" ? condition.value.name ?? "Unknown digital state" : String(condition.value);
}
export function demoTransition(current: CaseDocument, expected: number, actor: string,
  action: "SAVE" | "NOTE" | "LINK" | "SUBMIT" | "APPROVED" | "REJECTED" | "REVISE" | "REOPEN",
  now: string, data?: Partial<CaseDocument>, reason?: string): {document: CaseDocument; event: CaseEvent} {
  if (current.revision !== expected) throw new Error("REVISION_CONFLICT");
  const reviewer = actor === "reviewer-fixture";
  if (["APPROVED","REJECTED","REOPEN"].includes(action)) {
    if (!reviewer || current.contributors.includes(actor) || actor === current.created_by || actor === current.assigned_engineer)
      throw new Error("INDEPENDENT_REVIEWER_REQUIRED");
  } else if (reviewer || ![current.created_by, current.assigned_engineer].includes(actor)) throw new Error("FORBIDDEN");
  let next = {...current, updated_at: now, revision: expected+1};
  if (["SAVE","NOTE","LINK","SUBMIT"].includes(action) && current.status !== "DRAFT") throw new Error("INVALID_TRANSITION");
  if (action === "SAVE") {
    if (!data?.title?.trim() || !data.problem_statement?.trim() || data.title.length>200 || data.problem_statement.length>12000)
      throw new Error("INVALID_DRAFT");
    next={...next,title:data.title,problem_statement:data.problem_statement,priority:data.priority ?? current.priority,investigation:data.investigation ?? current.investigation};
  } else if (action === "NOTE") {
    if (!reason?.trim() || reason.length>12000 || current.notes.length>=100) throw new Error("INVALID_NOTE");
    next.notes=[...current.notes,{note_id:`note:demo-${next.revision}`,text:reason,actor,created_at:now}];
  } else if (action === "LINK") {
    const ref=data?.evidence?.[0];
    if (!ref || ref.canonical_asset_id!==current.canonical_asset_id || current.evidence.length>=30) throw new Error("INVALID_EVIDENCE");
    if (current.evidence.some(item=>item.kind===ref.kind && item.record_id===ref.record_id)) throw new Error("DUPLICATE_EVIDENCE");
    next.evidence=[...current.evidence,{...ref,linked_by:actor,linked_at:now}];
  } else if (action === "SUBMIT") next.status="IN_REVIEW";
  else if (action === "APPROVED" || action === "REJECTED") {
    if (current.status!=="IN_REVIEW" || !reason?.trim()) throw new Error("INVALID_REVIEW");
    next.status=action; next.review={reviewer:actor,decision:action,rationale:reason,decided_at:now};
  } else {
    if (current.status!==(action==="REOPEN"?"APPROVED":"REJECTED") || !reason?.trim()) throw new Error("INVALID_TRANSITION");
    next.status="DRAFT";next.review=null;
  }
  if (!reviewer) next.contributors=Array.from(new Set([...current.contributors,actor]));
  return {document:next,event:{case_id:current.case_id,revision:next.revision,previous_revision:expected,
    actor,action:action==="SAVE"?"UPDATE":["APPROVED","REJECTED"].includes(action)?"REVIEW":action,
    occurred_at:now,changed_fields:Object.keys(next).filter(key=>JSON.stringify(next[key as keyof CaseDocument])!==JSON.stringify(current[key as keyof CaseDocument])),reason:reason??null}};
}
