"""Fail closed on unapproved source-key case changes; no DB or source I/O."""
import unittest
from src.repositories.deferred_store import classify


def payload(equipment, present=True):
    return dict(equipment_id=equipment, local_equipment_present=present, status='CAN',
        work_type='PM', reported_at=None, scheduled_start=None, scheduled_finish=None,
        source_changed_at=None, downtime_hours=None, actual_labor_hours=None)


class IdentityCaseSafetyTest(unittest.TestCase):
    def test_case_change_is_failed_without_mutating_capture(self):
        raw = payload(' a ')
        before = dict(raw)
        self.assertEqual(classify('maintenance_event', 'BSR-1', raw),
                         (None, 'FAILED', 'INVALID_MAPPING'))
        self.assertEqual(raw, before)

    def test_dependency_arrival_cannot_authorize_case_alias(self):
        for present in (False, True):
            with self.subTest(present=present):
                self.assertEqual(classify('maintenance_event', 'BSR-1', payload('a', present)),
                                 (None, 'FAILED', 'INVALID_MAPPING'))

    def test_whitespace_only_preserves_exact_canonical_identity(self):
        record, disposition, reason = classify('maintenance_event', 'BSR-1', payload(' A '))
        self.assertEqual(record['equipment_id'], 'asset:MAXIMO:MXASSET:BSR:IP:A')
        self.assertIsNone(disposition)
        self.assertIsNone(reason)

    def test_approved_prefix_exclusion_is_not_reclassified(self):
        self.assertEqual(classify('maintenance_event', 'OTHER', payload('a')),
                         (None, 'EXPECTED_EXCLUSION', 'APPROVED_WO_PREFIX'))
