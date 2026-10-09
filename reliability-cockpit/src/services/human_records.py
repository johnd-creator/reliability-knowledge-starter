"""Disabled human draft/review workflow; all factual links supplied locally."""

from datetime import datetime, timezone
from hashlib import sha256
import json, re
from uuid import uuid4
from sqlalchemy import select, func
from src.domain.engineering import (
    Principal,
    Role,
    CaseStatus,
    ReviewDecision,
    EngineeringError,
)
from src.repositories.human_records import RecordRow, RevisionRow
from src.domain.manual_inspection import InspectionDraft, ManualInspection


class ReviewedRecordService:
    submission_status = "IN_REVIEW"
    reviewable_statuses = {"IN_REVIEW"}
    revisable_statuses = {"REJECTED"}
    review_decision_model = ReviewDecision
    extra_reviewer_actions = set()

    def validate_submission(self, actor, current):
        pass

    def validate_review(self, actor, current):
        pass

    def __init__(
        self,
        repo,
        catalog,
        *,
        kind,
        draft_model,
        record_model,
        enabled=False,
        clock=None
    ):
        self.repo, self.catalog, self.kind, self.draft_model, self.record_model = (
            repo,
            catalog,
            kind,
            draft_model,
            record_model,
        )
        self.enabled = enabled
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def gate(self, actor):
        if not self.enabled:
            raise EngineeringError("FEATURE_DISABLED", 404)
        if (
            not isinstance(actor, Principal)
            or not actor.roles
            or len(actor.asset_ids) > 1000
        ):
            raise EngineeringError("AUTHENTICATION_REQUIRED", 401)

    def visible(self, actor, raw):
        self.gate(actor)
        if not raw:
            raise EngineeringError("NOT_FOUND", 404)
        row = self.record_model.model_validate(raw)
        if row.canonical_asset_id not in actor.asset_ids or (
            Role.REVIEWER not in actor.roles and row.created_by != actor.principal_id and row.status != "APPROVED"
        ):
            raise EngineeringError("NOT_FOUND", 404)
        return row

    def get(self, actor, record_id):
        self.gate(actor)
        return self.repo.transact(
            lambda c: self.visible(actor, self.repo.get(c, self.kind, record_id))
        )

    def list(self, actor, *, asset_id=None, offset=0, limit=25):
        self.gate(actor)
        if (
            type(offset) is not int
            or type(limit) is not int
            or not 0 <= offset <= 10000
            or not 1 <= limit <= 100
        ):
            raise EngineeringError("INVALID_PAGINATION", 422)

        if asset_id is not None and asset_id not in actor.asset_ids:
            raise EngineeringError("NOT_FOUND", 404)

        def read(c):
            doc = RecordRow.document
            where = [
                RecordRow.kind == self.kind,
                doc["canonical_asset_id"].as_string().in_(actor.asset_ids),
            ]
            if Role.REVIEWER not in actor.roles:
                where.append((doc["created_by"].as_string() == actor.principal_id) | (doc["status"].as_string() == "APPROVED"))
            if asset_id is not None:
                where.append(doc["canonical_asset_id"].as_string() == asset_id)
            total = c.scalar(select(func.count()).select_from(RecordRow).where(*where))
            rows = c.scalars(
                select(doc)
                .where(*where)
                .order_by(RecordRow.record_id)
                .offset(offset)
                .limit(limit)
            )
            return dict(
                items=[self.visible(actor, row) for row in rows],
                total=total,
                offset=offset,
                limit=limit,
                has_more=offset + limit < total,
            )

        return self.repo.transact(read)

    def history(self, actor, record_id, *, offset=0, limit=50):
        self.gate(actor)
        if (
            type(offset) is not int
            or type(limit) is not int
            or not 0 <= offset <= 10000
            or not 1 <= limit <= 100
        ):
            raise EngineeringError("INVALID_PAGINATION", 422)

        def read(c):
            self.visible(actor, self.repo.get(c, self.kind, record_id))
            return [
                dict(row)
                for row in c.execute(
                    select(RevisionRow.__table__)
                    .where(
                        RevisionRow.kind == self.kind,
                        RevisionRow.record_id == record_id,
                    )
                    .order_by(RevisionRow.revision)
                    .offset(offset)
                    .limit(limit)
                ).mappings()
            ]

        return self.repo.transact(read)

    def draft_data(self, actor, draft):
        return draft.model_dump(mode="json")

    def extra_transition(self, actor, action, payload, current, data):
        raise EngineeringError("INVALID_TRANSITION", 409)

    def command(
        self, actor, action, payload, request_id, *, record_id=None, expected_revision=0
    ):
        self.gate(actor)
        if (
            not isinstance(request_id, str)
            or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", request_id or "")
            or not isinstance(payload, dict)
        ):
            raise EngineeringError("INVALID_COMMAND", 422)
        if (
            type(expected_revision) is not int
            or (
                action == "CREATE" and (record_id is not None or expected_revision != 0)
            )
            or (action != "CREATE" and (not record_id or expected_revision < 1))
        ):
            raise EngineeringError("INVALID_REVISION", 422)
        fingerprint = sha256(
            json.dumps(
                [self.kind, action, payload, record_id, expected_revision],
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()

        def write(c):
            current = (
                self.visible(actor, self.repo.get(c, self.kind, record_id))
                if record_id
                else None
            )
            draft = (
                self.draft_model.model_validate(payload) if action == "CREATE" else None
            )
            asset = draft.canonical_asset_id if draft else current.canonical_asset_id
            if asset not in actor.asset_ids:
                raise EngineeringError("NOT_FOUND", 404)
            reviewer = action in ({"REVIEW", "REOPEN"} | self.extra_reviewer_actions)
            excluded = (
                {
                    current.created_by,
                    *current.contributors,
                    getattr(current, "inspector_ref", None),
                    getattr(current, "responsible_person_ref", None),
                }
                if current
                else set()
            )
            if reviewer:
                if Role.REVIEWER not in actor.roles or actor.principal_id in excluded:
                    raise EngineeringError("INDEPENDENT_REVIEWER_REQUIRED", 403)
            elif Role.AUTHOR not in actor.roles or (
                current and current.created_by != actor.principal_id
            ):
                raise EngineeringError("FORBIDDEN", 403)
            replay = self.repo.receipt(c, actor.principal_id, request_id, fingerprint)
            if replay:
                return self.record_model.model_validate(replay)
            if not self.catalog.registered(asset):
                raise EngineeringError("ASSET_NOT_REGISTERED", 422)
            now = self.clock()
            reason = (
                payload.get("reason") if action not in {"CREATE", "UPDATE"} else None
            )
            if current and current.revision != expected_revision:
                raise EngineeringError("REVISION_CONFLICT", 409)
            if action == "CREATE":
                data = self.draft_data(actor, draft)
                data.update(
                    record_id=self.kind.lower() + ":" + str(uuid4()),
                    created_by=actor.principal_id,
                    created_at=now,
                    updated_at=now,
                    revision=1,
                    contributors=(actor.principal_id,),
                )
            else:
                data = current.model_dump(mode="json")
                data.update(revision=current.revision + 1, updated_at=now)
                if action == "UPDATE":
                    if current.status != CaseStatus.DRAFT:
                        raise EngineeringError("INVALID_TRANSITION", 409)
                    draft = self.draft_model.model_validate(payload)
                    if draft.canonical_asset_id != asset:
                        raise EngineeringError("ASSET_IMMUTABLE", 422)
                    data.update(self.draft_data(actor, draft))
                elif action == "SUBMIT":
                    if payload or current.status != CaseStatus.DRAFT:
                        raise EngineeringError("INVALID_TRANSITION", 409)
                    data.update(self.validate_submission(actor, current) or {})
                    data.update(status=self.submission_status, submitted_at=now)
                elif action == "REVIEW":
                    if (
                        set(payload) != {"decision", "reason"}
                        or current.status not in self.reviewable_statuses
                        or not isinstance(reason, str)
                        or not reason.strip()
                    ):
                        raise EngineeringError("INVALID_TRANSITION", 409)
                    self.validate_review(actor, current)
                    decision = self.review_decision_model(
                        reviewer=actor.principal_id,
                        decision=payload["decision"],
                        rationale=reason,
                        decided_at=now,
                    )
                    data.update(status=decision.decision, review=decision)
                elif action in {"REVISE", "REOPEN"}:
                    if (
                        set(payload) != {"reason"}
                        or not isinstance(reason, str)
                        or not reason.strip()
                        or len(reason) > 6000
                        or current.status not in (self.revisable_statuses if action == "REVISE" else {"APPROVED"})
                    ):
                        raise EngineeringError("INVALID_TRANSITION", 409)
                    data.update(status="DRAFT", submitted_at=None, review=None)
                    if self.kind == "INSPECTION":
                        data.update(review_started_at=None, review_started_by=None)
                else:
                    self.extra_transition(actor, action, payload, current, data)
                if not reviewer:
                    data["contributors"] = tuple(
                        dict.fromkeys((*current.contributors, actor.principal_id))
                    )
            result = self.record_model.model_validate(data)
            self.repo.save(
                c,
                self.kind,
                result,
                expected_revision,
                actor.principal_id,
                action,
                reason,
                request_id,
                fingerprint,
            )
            return result

        return self.repo.transact(write)


class InspectionService(ReviewedRecordService):
    submission_status = "SUBMITTED"
    reviewable_statuses = {"UNDER_REVIEW", "IN_REVIEW"}
    revisable_statuses = {"RETURNED", "REJECTED"}
    extra_reviewer_actions = {"BEGIN_REVIEW"}

    def validate_submission(self, actor, current):
        if not current.measurements and not current.observations:
            raise EngineeringError("INSPECTION_EVIDENCE_REQUIRED", 422)

    def validate_review(self, actor, current):
        if current.review_started_by and current.review_started_by != actor.principal_id:
            raise EngineeringError("REVIEWER_MISMATCH", 403)

    def extra_transition(self, actor, action, payload, current, data):
        reason = payload.get("reason")
        if action != "BEGIN_REVIEW" or current.status != "SUBMITTED" or set(payload) != {"reason"} or not isinstance(reason, str) or not reason.strip() or len(reason) > 6000:
            raise EngineeringError("INVALID_TRANSITION", 409)
        data.update(status="UNDER_REVIEW", review_started_by=actor.principal_id, review_started_at=data["updated_at"])

    def __init__(self, repo, catalog, **kwargs):
        super().__init__(
            repo,
            catalog,
            kind="INSPECTION",
            draft_model=InspectionDraft,
            record_model=ManualInspection,
            **kwargs
        )

    @property
    def review_decision_model(self):
        from src.domain.manual_inspection import InspectionReview
        return InspectionReview

    def draft_data(self, actor, draft):
        if draft.inspector_ref != actor.principal_id:
            raise EngineeringError("INSPECTOR_ATTRIBUTION_REQUIRED", 422)
        for case in draft.case_refs:
            self.catalog.validate_case(actor, draft.canonical_asset_id, case)
        return super().draft_data(actor, draft)
