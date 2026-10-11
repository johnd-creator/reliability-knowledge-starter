"""QA-only distribution in the existing app store. No transport or source client."""
from hashlib import sha256
import json, re
from sqlalchemy import select, func
from src.domain.advisory import Advisory, AdvisoryDraft, Acknowledgement
from src.domain.engineering import EngineeringCase, EngineeringError, Role
from src.domain.recommendation import Recommendation
from src.repositories.engineering import CaseRow
from src.repositories.human_records import RecordRow, RevisionRow, HumanRecordRepository
from src.services.human_records import ReviewedRecordService


def digest(model):
    return sha256(model.model_dump_json().encode()).hexdigest()


def reviewed_content(record):
    # Local follow-up is independent of the approved recommendation statement.
    return record.model_dump(mode='json', exclude={'revision', 'updated_at', 'follow_up_status', 'completion_verification'})


class AdvisoryRepository(HumanRecordRepository):
    def __init__(self, repo):
        self.engine = repo.engine

    def get(self, c, kind, record_id):
        if kind == "ADVISORY":
            return c.scalar(select(RecordRow.document).where(RecordRow.kind == kind, RecordRow.record_id == record_id).with_for_update())
        return super().get(c, kind, record_id)


class AdvisoryService(ReviewedRecordService):
    extra_reviewer_actions = {'PUBLISH', 'WITHDRAW'}

    def __init__(self, recommendations, *, enabled=False, clock=None):
        super().__init__(AdvisoryRepository(recommendations.repo), recommendations.catalog, kind='ADVISORY',
            draft_model=AdvisoryDraft, record_model=Advisory, enabled=enabled, clock=clock)
        self.recommendations = recommendations

    def visible(self, actor, raw):
        row = super().visible(actor, raw)
        if row.created_by != actor.principal_id and Role.REVIEWER not in actor.roles:
            raise EngineeringError('NOT_FOUND', 404)
        return row

    def draft_data(self, actor, draft):
        rec = self.recommendations.get(actor, draft.recommendation_ref)
        case = self.catalog.validate_case(actor, draft.canonical_asset_id, rec.case_ref)
        if rec.canonical_asset_id != draft.canonical_asset_id or rec.status != 'APPROVED' or case.status != 'APPROVED' or not rec.reviewed_case or rec.reviewed_case.stable_version != digest(case):
            raise EngineeringError('REVIEWED_UPSTREAM_REQUIRED', 409)
        if not rec.supporting_evidence:
            raise EngineeringError('SUPPORTING_EVIDENCE_REQUIRED', 422)
        if draft.replaces:
            prior = self.get(actor, draft.replaces)
            if prior.canonical_asset_id != draft.canonical_asset_id or prior.availability != 'WITHDRAWN':
                raise EngineeringError('WITHDRAWN_SAME_ASSET_PREDECESSOR_REQUIRED', 409)
        excluded = sorted({case.created_by, *case.contributors, rec.created_by, *rec.contributors, *(x for x in (case.assigned_engineer, rec.responsible_person_ref) if x)})
        return dict(**draft.model_dump(mode='json'), upstream=dict(
            case_id=case.case_id, case_revision=case.revision, case_sha256=digest(case),
            recommendation_id=rec.record_id, recommendation_revision=rec.revision, recommendation_sha256=digest(rec),
            case_reviewer=case.review.reviewer, recommendation_reviewer=rec.review.reviewer,
            recommended_action=rec.proposed_action, rationale=rec.rationale,
            responsible_person_ref=rec.responsible_person_ref, responsible_team_ref=rec.responsible_team_ref,
            target_date=rec.model_dump(mode="json")["target_date"], existing_work_order_ref=rec.existing_work_order_ref,
            evidence=[dict(kind=e.kind, record_id=e.record_id, stable_version=e.stable_version, source_timestamp=e.source_timestamp.isoformat() if e.source_timestamp else None, mode=e.mode) for e in rec.supporting_evidence],
            excluded_reviewers=excluded, recommendation_content=reviewed_content(rec)))

    def guard(self, c, row, *, lock=False):
        # Same transaction, Case -> Recommendation lock order as existing workflow.
        u = row.upstream
        case_query = select(CaseRow.document).where(CaseRow.case_id == u['case_id'])
        rec_query = select(RecordRow.document).where(RecordRow.kind == 'RECOMMENDATION', RecordRow.record_id == u['recommendation_id'])
        if lock:
            case_query, rec_query = case_query.with_for_update(), rec_query.with_for_update()
        raw_case, raw_rec = c.scalar(case_query), c.scalar(rec_query)
        if not raw_case or not raw_rec:
            raise EngineeringError('REVIEWED_UPSTREAM_CHANGED', 409)
        case, rec = EngineeringCase.model_validate(raw_case), Recommendation.model_validate(raw_rec)
        frozen = c.scalar(select(RevisionRow.snapshot).where(RevisionRow.kind == 'RECOMMENDATION', RevisionRow.record_id == rec.record_id, RevisionRow.revision == u['recommendation_revision']))
        if case.canonical_asset_id != row.canonical_asset_id or rec.canonical_asset_id != row.canonical_asset_id or case.status != 'APPROVED' or rec.status != 'APPROVED' or digest(case) != u['case_sha256'] or not frozen or digest(Recommendation.model_validate(frozen)) != u['recommendation_sha256'] or reviewed_content(rec) != u['recommendation_content']:
            raise EngineeringError('REVIEWED_UPSTREAM_CHANGED', 409)
        return rec

    def validate_submission(self, actor, current, connection=None):
        self.guard(connection, current, lock=True)

    def validate_review(self, actor, current, connection=None):
        if actor.principal_id in current.upstream['excluded_reviewers']:
            raise EngineeringError('INDEPENDENT_REVIEWER_REQUIRED', 403)
        self.guard(connection, current, lock=True)

    def extra_transition(self, actor, action, payload, current, data, connection=None):
        reason = payload.get('reason')
        if set(payload) != {'reason'} or not isinstance(reason, str) or not reason.strip() or len(reason) > 6000 or current.status != 'APPROVED':
            raise EngineeringError('INVALID_TRANSITION', 409)
        if actor.principal_id in current.upstream['excluded_reviewers']:
            raise EngineeringError('INDEPENDENT_REVIEWER_REQUIRED', 403)
        if action == 'PUBLISH' and current.publication is None:
            self.guard(connection, current, lock=True)
            # Allowlisted reviewed snapshot, never raw case/evidence attachments.
            fields = ('record_id', 'canonical_asset_id', 'summary', 'finding', 'evidence_caveat', 'audiences', 'replaces', 'created_by', 'review', 'scope')
            snapshot = {k: data[k] for k in fields}
            snapshot['upstream'] = {k: v for k, v in current.upstream.items() if k not in {'excluded_reviewers', 'recommendation_content'}}
            data.update(availability='IN_APP_QA_AVAILABLE', publication=dict(version=data['revision'], published_at=data['updated_at'].isoformat(), published_by=actor.principal_id, snapshot=snapshot))
        elif action == 'WITHDRAW' and current.availability == 'IN_APP_QA_AVAILABLE':
            data['availability'] = 'WITHDRAWN'
        else:
            raise EngineeringError('INVALID_TRANSITION', 409)

    @staticmethod
    def audiences(actor):
        # Exercise memberships only. Existing roles are NOT organizational roles.
        result = set()
        if Role.AUTHOR in actor.roles:
            result.update({'MAINTENANCE_QA', 'ENGINEERING_QA'})
        if Role.REVIEWER in actor.roles:
            result.update({'OPERATIONS_QA', 'ENGINEERING_QA'})
        return result

    def recipient_row(self, actor, raw):
        self.gate(actor)
        if not raw:
            raise EngineeringError('NOT_FOUND', 404)
        row = Advisory.model_validate(raw)
        if row.canonical_asset_id not in actor.asset_ids or row.publication is None or not self.audiences(actor).intersection(row.audiences):
            raise EngineeringError('NOT_FOUND', 404)
        return row

    def ack_id(self, actor, row):
        return 'ack:' + sha256(f'{row.record_id}:{row.publication["version"]}:{actor.principal_id}'.encode()).hexdigest()

    def recipient_result(self, c, actor, row):
        state = row.availability
        follow = 'UNAVAILABLE'
        try:
            rec = self.guard(c, row)
            follow = rec.follow_up_status
        except EngineeringError:
            if state == 'IN_APP_QA_AVAILABLE':
                state = 'STALE_UPSTREAM'
        return dict(**row.publication, availability=state, current_revision=row.revision,
            acknowledgement=self.repo.get(c, 'ADVISORY_ACK', self.ack_id(actor, row)),
            follow_up_status=follow, viewed_status='NOT_RECORDED')

    def inbox(self, actor, *, offset=0, limit=25):
        self.gate(actor)
        if type(offset) is not int or type(limit) is not int or not 0 <= offset <= 10000 or not 1 <= limit <= 100:
            raise EngineeringError('INVALID_PAGINATION', 422)
        def read(c):
            doc = RecordRow.document
            audience = self.audiences(actor)
            # Fixed three slots, bounded by contract. No browser-supplied grants.
            audience_filter = doc['audiences'][0].as_string().in_(audience) | doc['audiences'][1].as_string().in_(audience) | doc['audiences'][2].as_string().in_(audience)
            where = [RecordRow.kind == 'ADVISORY', doc['canonical_asset_id'].as_string().in_(actor.asset_ids), doc['availability'].as_string().in_(['IN_APP_QA_AVAILABLE', 'WITHDRAWN']), audience_filter]
            total = c.scalar(select(func.count()).select_from(RecordRow).where(*where))
            rows = c.scalars(select(doc).where(*where).order_by(RecordRow.record_id).offset(offset).limit(limit))
            return dict(items=[self.recipient_result(c, actor, self.recipient_row(actor, raw)) for raw in rows], total=total, offset=offset, limit=limit, has_more=offset + limit < total)
        return self.repo.transact(read)

    def recipient_get(self, actor, record_id):
        return self.repo.transact(lambda c: self.recipient_result(c, actor, self.recipient_row(actor, self.repo.get(c, self.kind, record_id))))

    def acknowledge(self, actor, record_id, request_id, expected_revision):
        self.gate(actor)
        if not isinstance(request_id, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}', request_id) or type(expected_revision) is not int or expected_revision < 1:
            raise EngineeringError('INVALID_COMMAND', 422)
        fingerprint = sha256(json.dumps(['ADVISORY_ACK', record_id, expected_revision]).encode()).hexdigest()
        def write(c):
            raw = c.scalar(select(RecordRow.document).where(RecordRow.kind == self.kind, RecordRow.record_id == record_id).with_for_update())
            row = self.recipient_row(actor, raw)
            # Revoked scope and withdrawal checked before receipt replay.
            if row.availability != 'IN_APP_QA_AVAILABLE':
                raise EngineeringError('ADVISORY_NOT_AVAILABLE', 409)
            self.guard(c, row, lock=True)
            replay = self.repo.receipt(c, actor.principal_id, request_id, fingerprint)
            if replay:
                return Acknowledgement.model_validate(replay)
            if expected_revision != row.revision:
                raise EngineeringError('REVISION_CONFLICT', 409)
            existing = self.repo.get(c, 'ADVISORY_ACK', self.ack_id(actor, row))
            if existing:
                return Acknowledgement.model_validate(existing)
            ack = Acknowledgement(record_id=self.ack_id(actor, row), advisory_id=record_id, publication_version=row.publication['version'], canonical_asset_id=row.canonical_asset_id, actor=actor.principal_id, updated_at=self.clock())
            self.repo.save(c, 'ADVISORY_ACK', ack, 0, actor.principal_id, 'ACKNOWLEDGE', None, request_id, fingerprint)
            return ack
        return self.repo.transact(write)

    def list(self, actor, *, offset=0, limit=25):
        self.gate(actor)
        if type(offset) is not int or type(limit) is not int or not 0 <= offset <= 10000 or not 1 <= limit <= 100:
            raise EngineeringError('INVALID_PAGINATION', 422)
        def read(c):
            doc = RecordRow.document
            where = [RecordRow.kind == self.kind, doc['canonical_asset_id'].as_string().in_(actor.asset_ids)]
            if Role.REVIEWER not in actor.roles:
                where.append(doc['created_by'].as_string() == actor.principal_id)
            total = c.scalar(select(func.count()).select_from(RecordRow).where(*where))
            rows = c.scalars(select(doc).where(*where).order_by(RecordRow.record_id).offset(offset).limit(limit))
            return dict(items=[self.visible(actor, x) for x in rows], total=total, offset=offset, limit=limit, has_more=offset+limit<total)
        return self.repo.transact(read)
