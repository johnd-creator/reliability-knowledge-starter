"""Disabled application proposal workflow; exclusively local informational reads."""

from src.domain.engineering import (
    Principal,
    Role,
    CaseStatus,
    EvidenceReference,
    EngineeringError,
)
from src.domain.recommendation import (
    RecommendationDraft,
    Recommendation,
    FollowUpStatus,
)
from src.services.human_records import ReviewedRecordService


class RecommendationService(ReviewedRecordService):
    def __init__(self, repo, catalog, maintenance, directory, team_directory, **kwargs):
        super().__init__(
            repo,
            catalog,
            kind="RECOMMENDATION",
            draft_model=RecommendationDraft,
            record_model=Recommendation,
            **kwargs
        )
        self.maintenance, self.directory, self.team_directory = (
            maintenance,
            directory,
            team_directory,
        )

    def draft_data(self, actor, draft):
        self.catalog.validate_case(actor, draft.canonical_asset_id, draft.case_ref)
        if draft.responsible_person_ref:
            person = self.directory(draft.responsible_person_ref)
            if (
                not isinstance(person, Principal)
                or not person.roles
                or draft.canonical_asset_id not in person.asset_ids
            ):
                raise EngineeringError("INVALID_RESPONSIBLE_PERSON", 422)
        if draft.responsible_team_ref and not self.team_directory(
            draft.responsible_team_ref, draft.canonical_asset_id
        ):
            raise EngineeringError("INVALID_RESPONSIBLE_TEAM", 422)
        now = self.clock()
        evidence = []
        for selected in draft.evidence_selections:
            ref = self.catalog.resolve(
                draft.canonical_asset_id,
                selected.kind,
                selected.record_id,
                selected.mode,
                actor.principal_id,
                now,
            )
            if not isinstance(ref, EvidenceReference):
                raise EngineeringError("EVIDENCE_IDENTITY_INVALID", 422)
            ref = EvidenceReference.model_validate(ref.model_dump(mode="json"))
            if (ref.canonical_asset_id, ref.kind, ref.record_id, ref.mode) != (
                draft.canonical_asset_id,
                selected.kind,
                selected.record_id,
                selected.mode,
            ):
                raise EngineeringError("EVIDENCE_IDENTITY_INVALID", 422)
            if (ref.linked_by, ref.linked_at) != (actor.principal_id, now):
                raise EngineeringError("EVIDENCE_PROVENANCE_INVALID", 422)
            evidence.append(ref)
        data = draft.model_dump(mode="json")
        data["supporting_evidence"] = [ref.model_dump(mode="json") for ref in evidence]
        data["existing_work_order"] = (
            self.maintenance.resolve_work_order(
                actor, draft.canonical_asset_id, draft.existing_work_order_ref
            ).model_dump(mode="json")
            if draft.existing_work_order_ref
            else None
        )
        return data

    def extra_transition(self, actor, action, payload, current, data):
        if (
            action != "FOLLOWUP"
            or set(payload) != {"status", "reason"}
            or current.status != CaseStatus.APPROVED
        ):
            raise EngineeringError("INVALID_TRANSITION", 409)
        reason = payload["reason"]
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 6000:
            raise EngineeringError("INVALID_CONTRACT", 422)
        status = FollowUpStatus(payload["status"])
        transitions = {
            FollowUpStatus.PROPOSED: {FollowUpStatus.PLANNED, FollowUpStatus.CANCELLED},
            FollowUpStatus.PLANNED: {
                FollowUpStatus.IN_PROGRESS,
                FollowUpStatus.CANCELLED,
            },
            FollowUpStatus.IN_PROGRESS: {
                FollowUpStatus.COMPLETED,
                FollowUpStatus.CANCELLED,
            },
        }
        if status not in transitions.get(current.follow_up_status, set()):
            raise EngineeringError("INVALID_TRANSITION", 409)
        data["follow_up_status"] = status
