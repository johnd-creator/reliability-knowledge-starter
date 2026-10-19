"""Identity safety pending an approved raw-key/alias contract; private PG only."""
import unittest
from unittest.mock import patch
from sqlalchemy import select, update
import test_replay_postgres as baseline
from src.repositories import deferred_models as dm, mart_models, models, projection_models as pm
from src.repositories.projection_store import CaptureError
from src.repositories.projection_store import map_input
from src.services.asset_registry_reconciliation import normalize_identifier


class CaseIdentitySafetyTest(baseline.ReplayPostgreSQLTest):
    def test_case_changing_wo_reference_is_blocked_with_raw_provenance(self):
        self.add_asset('A')
        self.add_wo('BSR-CASE', eq=' a ')
        ticket = self.store.capture('maintenance_event')
        outcome = self.store.process(ticket)
        item = self.rows(pm.item)[0]
        self.assertEqual((item['disposition'], item['reason']), ('FAILED', 'INVALID_MAPPING'))
        self.assertEqual(item['payload']['equipment_id'], ' a ')
        self.assertEqual(outcome['status'], 'PARTIAL')
        self.assertEqual(self.current()['state'], 'BLOCKED_NEEDS_REVIEW')
        self.assertEqual(self.rows(mart_models.MaintenanceEventMartOrm.__table__), [])
        self.assertIsNone(self.rows(pm.lease)[0]['last_complete_run'])
        with self.assertRaises(CaptureError):
            self.store.register(ticket, self.current()['id'])

    def test_distinct_asset_keys_are_not_joined_by_case_fold(self):
        self.add_asset('a')
        self.add_asset('A')
        assets = self.store.capture('asset_master')
        self.store.process(assets)
        self.store.release(assets)
        ids = {r['canonical_id'] for r in self.rows(mart_models.AssetMasterMartOrm.__table__)}
        self.assertEqual(ids, {'asset:MAXIMO:MXASSET:BSR:IP:a', 'asset:MAXIMO:MXASSET:BSR:IP:A'})
        self.add_wo('BSR-COLLISION', eq='a')
        ticket = self.store.capture('maintenance_event')
        self.assertEqual(self.store.process(ticket)['status'], 'PARTIAL')
        item = self.rows(pm.item, pm.item.c.run_id == ticket.run_id)[0]
        self.assertEqual((item['disposition'], item['reason']), ('FAILED', 'INVALID_MAPPING'))
        self.assertEqual(self.rows(mart_models.MaintenanceEventMartOrm.__table__), [])
        self.assertEqual(self.rows(pm.target, pm.target.c.domain == 'maintenance_event'), [])

    def test_whitespace_only_matching_preserves_exact_case(self):
        self.add_asset('A')
        self.add_wo('BSR-TRIM', eq=' A ')
        ticket = self.store.capture('maintenance_event')
        self.assertEqual(self.store.process(ticket)['status'], 'COMPLETE')
        record = self.rows(mart_models.MaintenanceEventMartOrm.__table__)[0]
        self.assertEqual(record['equipment_id'], 'asset:MAXIMO:MXASSET:BSR:IP:A')
        self.assertEqual(self.rows(pm.item)[0]['payload']['equipment_id'], ' A ')

    def test_uppercase_reference_does_not_invent_lowercase_alias(self):
        self.add_asset('a')
        self.add_wo('BSR-NO-ALIAS', eq='A')
        ticket = self.store.capture('maintenance_event')
        self.assertEqual(self.store.process(ticket)['status'], 'PARTIAL')
        item = self.rows(pm.item)[0]
        self.assertEqual((item['disposition'], item['reason']), ('DEFERRED', 'MISSING_LOCAL_EQUIPMENT'))
        self.assertEqual(self.rows(mart_models.MaintenanceEventMartOrm.__table__), [])

    def test_case_only_source_change_after_capture_refuses_stale_replay(self):
        self.debt()
        self.add_asset('A')
        ticket = self.store.claim_due('maintenance_event')
        self.store.capture_claim(ticket)
        self.store.reserve_attempt(ticket)
        with self.db.session() as session, session.begin():
            session.execute(update(models.WorkOrderOrm).values(equipment_id='a'))
        with self.assertRaises(CaptureError):
            self.store.process(ticket, max_items=1)
        self.assertEqual(self.rows(mart_models.MaintenanceEventMartOrm.__table__), [])
        self.assertFalse(any(r['state'] == 'RESOLVED' for r in self.rows(dm.version)))

    def test_old_accepted_same_fingerprint_requires_review_without_rewrite(self):
        # Model the old mapper's case-folding only; preserve actual raw capture,
        # target, receipt, ledger and fencing transactions in the real fixture.
        def old_mapping(domain, source_id, payload):
            historical = dict(payload)
            if domain == 'maintenance_event':
                historical['equipment_id'] = normalize_identifier(payload['equipment_id'])
            return map_input(domain, source_id, historical)

        self.add_wo('BSR-OLD', eq='a')
        with patch('src.repositories.deferred_store.map_input', side_effect=old_mapping):
            ticket = self.store.capture('maintenance_event')
            self.store.process(ticket)
            self.store.register(ticket, self.current()['id'])
            self.store.release(ticket)
            self.add_asset('A')
            self.assertEqual(self.service().run('maintenance_event')[0]['state'], 'DONE')
        targets = self.rows(pm.target)
        versions = self.rows(dm.version)
        receipts = self.rows(pm.item)
        records = self.rows(mart_models.MaintenanceEventMartOrm.__table__)
        ticket = self.store.capture('maintenance_event')
        with self.assertRaisesRegex(CaptureError, 'resolved fingerprint produced incompatible disposition'):
            self.store.process(ticket)
        self.assertEqual(self.rows(pm.target), targets)
        self.assertEqual(self.rows(dm.version), versions)
        self.assertEqual(self.rows(mart_models.MaintenanceEventMartOrm.__table__), records)
        self.assertTrue(all(row in self.rows(pm.item) for row in receipts))
        self.assertIsNone(self.rows(pm.item, pm.item.c.run_id == ticket.run_id)[0]['disposition'])
        self.assertNotEqual(self.store.inspect(ticket.run_id)['status'], 'COMPLETE')


def load_tests(loader, tests, pattern):
    # The baseline fixture is reused, not its inherited test methods duplicated.
    names = [name for name in CaseIdentitySafetyTest.__dict__ if name.startswith('test_')]
    return unittest.TestSuite(CaseIdentitySafetyTest(name) for name in sorted(names))
