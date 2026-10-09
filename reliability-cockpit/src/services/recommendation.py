"""Disabled application proposal workflow; exclusively local informational reads."""

from hashlib import sha256
from src.domain.engineering import (
    Principal,
    Role,
    CaseStatus,
    EvidenceReference,
    EngineeringError,
    EngineeringCase,
)
from src.domain.recommendation import (
    RecommendationDraft,
    Recommendation,
    FollowUpStatus,
    ReviewedCaseLink,
    CompletionVerification,
    EvidenceSelection,
)
from src.services.human_records import ReviewedRecordService


class RecommendationService(ReviewedRecordService):
    extra_reviewer_actions = {"VERIFY_COMPLETION"}

    def case_link(self, actor, current):
        case = self.catalog.validate_case(actor, current.canonical_asset_id, current.case_ref)
        if not isinstance(case, EngineeringCase) or case.status != CaseStatus.APPROVED or not case.review:
            raise EngineeringError("REVIEWED_CASE_REQUIRED", 409)
        case = EngineeringCase.model_validate(case.model_dump(mode="json"))
        if case.canonical_asset_id != current.canonical_asset_id or case.case_id != current.case_ref:
            raise EngineeringError("CASE_ASSET_MISMATCH", 422)
        return ReviewedCaseLink(case_id=case.case_id, revision=case.revision,
            stable_version=sha256(case.model_dump_json().encode()).hexdigest(),
            reviewer=case.review.reviewer, reviewed_at=case.review.decided_at)

    def validate_submission(self, actor, current):
        if not current.supporting_evidence:
            raise EngineeringError("SUPPORTING_EVIDENCE_REQUIRED", 422)
        self.check_evidence(actor, current, current.supporting_evidence)
        return {"reviewed_case": self.case_link(actor, current)}

    def validate_review(self, actor, current):
        if not current.reviewed_case or self.case_link(actor, current) != current.reviewed_case:
            raise EngineeringError("REVIEWED_CASE_CHANGED", 409)
        self.check_evidence(actor, current, current.supporting_evidence)

    def check_evidence(self, actor, current, refs):
        # Re-resolve identity/version before approval or follow-up; never replace frozen history.
        for ref in refs:
            latest = self.resolve_selection(actor, current.canonical_asset_id,
                EvidenceSelection(kind=ref.kind, record_id=ref.record_id, mode=ref.mode))
            if latest.stable_version != ref.stable_version:
                raise EngineeringError("EVIDENCE_VERSION_CHANGED", 409)

    def resolve_selection(self, actor, asset, selected):
        now = self.clock()
        ref = self.catalog.resolve(asset, selected.kind, selected.record_id, selected.mode, actor.principal_id, now)
        if not isinstance(ref, EvidenceReference):
            raise EngineeringError("EVIDENCE_IDENTITY_INVALID", 422)
        ref = EvidenceReference.model_validate(ref.model_dump(mode="json"))
        if (ref.canonical_asset_id, ref.kind, ref.record_id, ref.mode) != (asset, selected.kind, selected.record_id, selected.mode):
            raise EngineeringError("EVIDENCE_IDENTITY_INVALID", 422)
        if (ref.linked_by, ref.linked_at) != (actor.principal_id, now):
            raise EngineeringError("EVIDENCE_PROVENANCE_INVALID", 422)
        return ref

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
        evidence = [self.resolve_selection(actor, draft.canonical_asset_id, selected)
                    for selected in draft.evidence_selections]
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
        if action == "VERIFY_COMPLETION":
            if current.status != CaseStatus.APPROVED or current.follow_up_status != FollowUpStatus.COMPLETED or set(payload) != {"reason", "evidence_selections"}:
                raise EngineeringError("INVALID_TRANSITION", 409)
            self.validate_review(actor, current)
            selections = payload["evidence_selections"]
            if not isinstance(selections, list) or not 1 <= len(selections) <= 20:
                raise EngineeringError("COMPLETION_EVIDENCE_REQUIRED", 422)
            selected = [EvidenceSelection.model_validate(x) for x in selections]
            if len({(x.kind, x.record_id) for x in selected}) != len(selected) or any(x.mode != "FROZEN_SNAPSHOT" for x in selected):
                raise EngineeringError("COMPLETION_EVIDENCE_REQUIRED", 422)
            refs = [self.resolve_selection(actor, current.canonical_asset_id, x) for x in selected]
            data.update(follow_up_status=FollowUpStatus.VERIFIED,
                completion_verification=CompletionVerification(reviewer=actor.principal_id,
                verified_at=self.clock(), reason=payload["reason"], evidence=tuple(refs)))
            return
        if (
            action != "FOLLOWUP"
            or set(payload) != {"status", "reason"}
            or current.status != CaseStatus.APPROVED
        ):
            raise EngineeringError("INVALID_TRANSITION", 409)
        self.validate_review(actor, current)
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
