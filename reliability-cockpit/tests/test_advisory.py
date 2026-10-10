"""Isolated advisory trust, provenance, immutable publication and acknowledgement."""
import unittest
from sqlalchemy import select, update
from src.repositories.engineering import EngineeringBase, CaseRow
from src.repositories.human_records import RecordRow, RevisionRow
from src.domain.engineering import Principal, Role, EngineeringError
from src.services.advisory import AdvisoryService
from test_recommendation import RecommendationTest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.advisory import build_advisory_router, build_inbox_router

class AdvisoryTest(unittest.TestCase):
    setUpBase = RecommendationTest.setUpBase
    tearDown = RecommendationTest.tearDown
    code = RecommendationTest.code

    def setUp(self):
        RecommendationTest.setUp(self)
        self.create = lambda: RecommendationTest.create(self)
        self.change = lambda row, action, payload, actor=None, request=None: RecommendationTest.change(self, row, action, payload, actor, request)
        self.rec = RecommendationTest.approved(self)
        self.recommendations = self.service
        case = self.catalog.validate_case(self.author, self.rec.canonical_asset_id, self.rec.case_ref)
        EngineeringBase.metadata.create_all(self.engine)
        with self.engine.begin() as c:
            c.execute(CaseRow.__table__.insert().values(case_id=case.case_id, revision=case.revision, document=case.model_dump(mode='json')))
        self.service = AdvisoryService(self.recommendations, enabled=True, clock=lambda: self.now)
        self.draft = dict(canonical_asset_id=self.rec.canonical_asset_id, recommendation_ref=self.rec.record_id,
            summary='SYNTHETIC reviewed investigation', finding='Observed evidence; hypothesis remains a hypothesis', evidence_caveat='Synthetic; not plant evidence or instructions', audiences=['OPERATIONS_QA', 'MAINTENANCE_QA'])

    def make(self, request='adv-create'):
        return self.service.command(self.author, 'CREATE', self.draft, request)

    def act(self, row, action, payload=None, actor=None, request=None):
        return self.service.command(actor or self.author, action, payload or {}, request or 'adv-'+action+str(row.revision), record_id=row.record_id, expected_revision=row.revision)

    def publish(self):
        row = self.act(self.make(), 'SUBMIT')
        row = self.act(row, 'REVIEW', dict(decision='APPROVED', reason='Independent synthetic review'), self.reviewer)
        return self.act(row, 'PUBLISH', dict(reason='QA inbox only'), self.reviewer)

    def test_review_publication_and_minimal_snapshot(self):
        row = self.publish()
        item = self.service.recipient_get(self.author, row.record_id)
        self.assertEqual(item['availability'], 'IN_APP_QA_AVAILABLE')
        self.assertEqual(item['snapshot']['upstream']['recommended_action'], self.rec.proposed_action)
        self.assertNotIn('recommendation_content', item['snapshot']['upstream'])
        self.assertNotIn('excluded_reviewers', item['snapshot']['upstream'])
        self.assertEqual(item['viewed_status'], 'NOT_RECORDED')
        self.assertEqual(self.service.inbox(self.author)['total'], 1)
        self.assertEqual(self.service.inbox(self.author, offset=1)['items'], [])
        self.assertEqual(len(self.service.history(self.author, row.record_id)), 4)

    def test_self_review_publish_upstream_contributors_denied(self):
        row = self.act(self.make(), 'SUBMIT')
        dual = Principal(principal_id='author', roles={Role.AUTHOR, Role.REVIEWER}, asset_ids=self.author.asset_ids)
        self.code('INDEPENDENT_REVIEWER_REQUIRED', lambda: self.act(row, 'REVIEW', dict(decision='APPROVED', reason='self'), dual))
        upstream = Principal(principal_id='case-author', roles={Role.REVIEWER}, asset_ids=self.author.asset_ids)
        self.code('INDEPENDENT_REVIEWER_REQUIRED', lambda: self.act(row, 'REVIEW', dict(decision='APPROVED', reason='self'), upstream))
        row = self.act(row, 'REVIEW', dict(decision='APPROVED', reason='independent'), self.reviewer)
        self.code('INDEPENDENT_REVIEWER_REQUIRED', lambda: self.act(row, 'PUBLISH', dict(reason='self'), dual))

    def test_denied_asset_audience_private_draft_and_history(self):
        self.draft['audiences'] = ['OPERATIONS_QA']
        draft = self.make()
        other = Principal(principal_id='other', roles={Role.AUTHOR}, asset_ids=self.author.asset_ids)
        self.code('NOT_FOUND', lambda: self.service.get(other, draft.record_id))
        self.code('NOT_FOUND', lambda: self.service.history(other, draft.record_id))
        self.assertEqual(self.service.list(other)['total'], 0)
        row = self.act(draft, 'SUBMIT'); row = self.act(row, 'REVIEW', dict(decision='APPROVED', reason='checked'), self.reviewer)
        row = self.act(row, 'PUBLISH', dict(reason='QA only'), self.reviewer)
        self.assertEqual(self.service.inbox(self.author)['total'], 0)
        self.code('NOT_FOUND', lambda: self.service.recipient_get(self.author, row.record_id))
        self.code('NOT_FOUND', lambda: self.service.acknowledge(self.author, row.record_id, 'ack', row.revision))
        self.assertEqual(self.service.inbox(self.foreign)['total'], 0)
        self.code('NOT_FOUND', lambda: self.service.recipient_get(self.foreign, row.record_id))
        self.code('NOT_FOUND', lambda: self.service.history(self.foreign, row.record_id))

    def test_acknowledgement_durable_idempotent_audited_not_work(self):
        row = self.publish()
        self.code('REVISION_CONFLICT', lambda: self.service.acknowledge(self.author, row.record_id, 'stale-ack', 1))
        ack = self.service.acknowledge(self.author, row.record_id, 'ack', row.revision)
        self.assertEqual(ack, self.service.acknowledge(self.author, row.record_id, 'ack', row.revision))
        self.assertEqual(ack, self.service.acknowledge(self.author, row.record_id, 'second-ack', row.revision))
        self.assertEqual(self.service.get(self.author, row.record_id), row)
        with self.engine.connect() as c:
            events = c.execute(select(RevisionRow.action).where(RevisionRow.kind == 'ADVISORY_ACK')).scalars().all()
        self.assertEqual(events, ['ACKNOWLEDGE'])
        self.assertEqual(self.service.recipient_get(self.author, row.record_id)['acknowledgement']['meaning'], 'RECEIPT_ONLY_NOT_APPROVAL_OR_WORK_AUTHORIZATION')
        self.assertIsNone(self.service.recipient_get(self.reviewer, row.record_id)['acknowledgement'])

    def test_withdraw_immutable_snapshot_and_reviewed_replacement(self):
        row = self.publish()
        withdrawn = self.act(row, 'WITHDRAW', dict(reason='QA replacement needed'), self.reviewer)
        self.assertEqual(withdrawn.publication, row.publication)
        self.assertEqual(self.service.recipient_get(self.author, row.record_id)['availability'], 'WITHDRAWN')
        self.code('ADVISORY_NOT_AVAILABLE', lambda: self.service.acknowledge(self.author, row.record_id, 'ack', withdrawn.revision))
        self.draft['replaces'] = withdrawn.record_id
        replacement = self.make('replacement')
        self.assertEqual(replacement.replaces, row.record_id)
        self.assertIsNone(replacement.publication)
        self.code('INVALID_TRANSITION', lambda: self.act(replacement, 'PUBLISH', dict(reason='skip'), self.reviewer))
        self.code('INVALID_TRANSITION', lambda: self.act(withdrawn, 'PUBLISH', dict(reason='republish'), self.reviewer))

    def test_stale_upstream_blocks_publish_and_ack_preserves_history(self):
        row = self.publish()
        with self.engine.begin() as c:
            raw = c.scalar(select(CaseRow.document)); raw['revision'] += 1
            c.execute(update(CaseRow).values(document=raw, revision=raw['revision']))
        self.assertEqual(self.service.recipient_get(self.author, row.record_id)['availability'], 'STALE_UPSTREAM')
        self.code('REVIEWED_UPSTREAM_CHANGED', lambda: self.service.acknowledge(self.author, row.record_id, 'ack', row.revision))
        self.assertEqual(self.service.get(self.author, row.record_id).publication, row.publication)
        self.act(row, 'WITHDRAW', dict(reason='Stale upstream'), self.reviewer)

    def test_follow_up_does_not_invalidate_approved_statement(self):
        row = self.publish()
        self.recommendations.command(self.author, 'FOLLOWUP', {'status':'PLANNED','reason':'Local only'}, 'follow', record_id=self.rec.record_id, expected_revision=self.rec.revision)
        item = self.service.recipient_get(self.author, row.record_id)
        self.assertEqual(item['availability'], 'IN_APP_QA_AVAILABLE')
        self.assertEqual(item['follow_up_status'], 'PLANNED')
        self.assertEqual(item['snapshot']['upstream']['recommendation_revision'], self.rec.revision)

    def test_stale_revision_retry_and_snapshot_mutation_denied(self):
        row = self.make()
        updated = self.act(row, 'UPDATE', {**self.draft, 'summary':'New summary'})
        self.assertEqual(updated, self.act(row, 'UPDATE', {**self.draft, 'summary':'New summary'}))
        self.code('REVISION_CONFLICT', lambda: self.act(row, 'UPDATE', self.draft, request='stale'))
        self.code('IDEMPOTENCY_CONFLICT', lambda: self.act(row, 'UPDATE', self.draft))
        row = self.act(updated, 'SUBMIT'); row = self.act(row, 'REVIEW', dict(decision='APPROVED',reason='checked'), self.reviewer)
        row = self.act(row, 'PUBLISH', dict(reason='QA only'), self.reviewer)
        self.code('INVALID_TRANSITION', lambda: self.act(row, 'UPDATE', self.draft))

    def test_routes_fail_closed_and_browser_cannot_select_audience(self):
        self.assertFalse(build_advisory_router(self.service, enabled=True).routes)
        self.assertFalse(build_inbox_router(self.service, enabled=True).routes)
        app = FastAPI()
        app.include_router(build_inbox_router(self.service, enabled=True, trusted_principal_dependency=lambda:self.author))
        self.draft['audiences'] = ['OPERATIONS_QA']; row = self.publish()
        with TestClient(app) as c:
            r = c.get('/v1/engineering/inbox?audience=OPERATIONS_QA')
            self.assertEqual(r.json()['total'], 0)
            self.assertEqual(c.get('/v1/engineering/inbox/'+row.record_id).status_code, 404)
            self.assertEqual(c.post('/v1/engineering/inbox/'+row.record_id+'/acknowledge', json={'request_id':'forged','expected_revision':row.revision,'actor':'reviewer'}).status_code,422)
