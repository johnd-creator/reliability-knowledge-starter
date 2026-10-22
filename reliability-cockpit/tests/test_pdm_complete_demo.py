"""No-connection negative controls for the separate demo adapter profile."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from sqlalchemy import create_engine
from src.services.pdm_complete_demo import checked_target,CompleteDemoAdapter
from src.services.pdm_complete_import import target,CompleteHistoryImporter
from src.domain.engineering import EngineeringError


class CompleteDemoGuardTest(unittest.TestCase):
    def test_wrong_profile_role_port_query_and_factual_targets_refused_before_connect(self):
        cases=[
            ('postgresql+psycopg://nadi_local_dev_01@127.0.0.1:15443/nadi_local_dev_01_test',True),
            ('postgresql+psycopg://history_demo_importer@127.0.0.1:15958/pdm_history_complete_demo_adapter_x_test',False),
            ('postgresql+psycopg://wrong@127.0.0.1:15443/nadi_local_dev_01_test',False),
            ('postgresql+psycopg://nadi_local_dev_01@127.0.0.1:15443/maximo_collector',False),
            ('postgresql+psycopg://nadi_local_dev_01@127.0.0.1:15443/nadi_local_dev_01_test?host=example.invalid',False),
            ('postgresql+psycopg://history_demo_importer@127.0.0.1:5432/pdm_history_complete_demo_adapter_x_test',True)]
        for dsn,qualification in cases:
            with self.subTest(dsn=dsn,qualification=qualification):
                engine=create_engine(dsn)
                try:
                    with patch.object(engine,'connect',side_effect=AssertionError('must not connect')):
                        with self.assertRaisesRegex(EngineeringError,'EXACT_COMPLETE_DEMO_TARGET_REQUIRED'):checked_target(engine,qualification=qualification)
                finally:engine.dispose()
    def test_default_qualification_importer_still_refuses_live_demo(self):
        engine=create_engine('postgresql+psycopg://nadi_local_dev_01@127.0.0.1:15443/nadi_local_dev_01_test')
        try:
            with patch.object(engine,'connect',side_effect=AssertionError('must not connect')):
                with self.assertRaisesRegex(EngineeringError,'DISPOSABLE_COMPLETE_HISTORY_ONLY'):target(engine)
        finally:engine.dispose()
    def test_inherited_run_cannot_apply_without_adapter_preflight(self):
        with self.assertRaisesRegex(EngineeringError,'USE_EXACT_PREFLIGHT_AND_EXPLICIT_APPLY'):
            object.__new__(CompleteDemoAdapter).run('unused','unused')
    def test_prepared_grant_version_is_required_on_each_chunk(self):
        adapter=object.__new__(CompleteDemoAdapter);adapter._applying={'subject':'synthetic-author','grant_version':1}
        with patch.object(CompleteHistoryImporter,'grant',return_value=SimpleNamespace(version=2)):
            with self.assertRaisesRegex(EngineeringError,'DEMO_PREFLIGHT_GRANT_CHANGED'):adapter.grant('synthetic-author','NADI-ASSET-001')
        with patch.object(CompleteHistoryImporter,'grant',return_value=SimpleNamespace(version=1)):
            with self.assertRaisesRegex(EngineeringError,'DEMO_PREFLIGHT_GRANT_CHANGED'):adapter.grant('foreign-author','NADI-ASSET-001')
            self.assertEqual(adapter.grant('synthetic-author','NADI-ASSET-001').version,1)

if __name__=='__main__':unittest.main()
