import type {QaSession,Recommendation} from './product-records';

export type RecommendationDraftValues=Pick<Recommendation,'rationale'|'proposed_action'|'responsible_person_ref'|'responsible_team_ref'|'target_date'>;
export type RecommendationRecovery={subject:string;sessionKey:string;base:Recommendation;draft:RecommendationDraftValues};
export function recommendationDraft(row:Recommendation):RecommendationDraftValues {
 return {rationale:row.rationale,proposed_action:row.proposed_action,responsible_person_ref:row.responsible_person_ref,responsible_team_ref:row.responsible_team_ref,target_date:row.target_date};
}
export function sameRecommendationDraft(left:RecommendationDraftValues,right:RecommendationDraftValues):boolean {
 return left.rationale===right.rationale&&left.proposed_action===right.proposed_action&&left.responsible_person_ref===right.responsible_person_ref&&left.responsible_team_ref===right.responsible_team_ref&&left.target_date===right.target_date;
}
export function recoverableRecommendation(recovery:RecommendationRecovery,session:QaSession):boolean {
 return recovery.sessionKey===recommendationSessionKey(session)&&recovery.subject===session.subject&&recovery.base.created_by===session.subject&&session.roles.includes('AUTHOR')&&session.asset_ids.includes(recovery.base.canonical_asset_id);
}
export function recommendationSessionKey(session:QaSession):string {
 return JSON.stringify([session.subject,[...new Set(session.roles)].sort(),[...new Set(session.asset_ids)].sort()]);
}
