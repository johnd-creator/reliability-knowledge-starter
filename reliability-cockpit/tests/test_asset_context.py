"""Source-free same-asset context, source timestamps and graceful local failures."""
import unittest
from unittest.mock import patch
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.domain.engineering import EngineeringError
from src.services.asset_context import AssetContextService
from src.api.asset_context import build_asset_context_router
import test_maximo_intelligence as mx

class AssetContextTest(unittest.TestCase):
    def setUp(self):
        self.fixture = mx.MaintenanceIntelligenceTest()
        self.fixture.setUp()
        self.service = AssetContextService(self.fixture.db, enabled=True, clock=lambda: mx.NOW)
    def tearDown(self):
        self.fixture.tearDown()
    def test_local_context_retains_identity_times_and_unmapped(self):
        result = self.service.read(self.fixture.actor, mx.ASSET, limit=2)
        self.assertEqual(len(result.maintenance.items), 2)
        self.assertTrue(result.maintenance.has_more)
        self.assertEqual(result.condition.mapping_readiness, "MAPPING_UNVERIFIED")
        self.assertEqual(result.inspections.availability, "NOT_CONFIGURED")
        self.assertIsNone(result.inspections.total)
        self.assertEqual(result.assessment, "NOT_ASSESSED")
        self.assertIsNone(result.identity.classification_ref)
        self.assertEqual(result.identity.projection_freshness, "UNKNOWN")
        self.assertEqual(result.maintenance.items[0].collected_at, mx.NOW)
        self.assertNotIn("secret", result.model_dump_json())
    def test_scope_is_checked_before_database_access(self):
        with patch.object(self.service.assets, "get_asset", side_effect=AssertionError("must not query")):
            with self.assertRaises(EngineeringError) as e:
                self.service.read(self.fixture.actor, "asset:SYNTHETIC:OTHER")
            self.assertEqual(e.exception.status, 404)
    def test_missing_registered_asset_is_not_invented(self):
        with patch.object(self.service.assets, "get_asset", return_value=None):
            with self.assertRaises(EngineeringError):
                self.service.read(self.fixture.actor, mx.ASSET)
    def test_unavailable_mart_is_not_empty_healthy_or_exception_disclosure(self):
        failure = OperationalError("private query", {}, Exception("must-not-escape"))
        with patch.object(self.service.assets, "get_asset", side_effect=failure), patch.object(self.service.maintenance, "work_orders", side_effect=failure), patch.object(self.service.conditions, "asset_evidence", side_effect=failure):
            result = self.service.read(self.fixture.actor, mx.ASSET)
        self.assertEqual(result.identity_availability, "UNAVAILABLE")
        self.assertEqual(result.maintenance.availability, "UNAVAILABLE")
        self.assertIsNone(result.maintenance.total)
        self.assertEqual(result.condition_availability, "UNAVAILABLE")
        self.assertNotIn("must-not-escape", result.model_dump_json())
    def test_invalid_pagination_and_missing_identity_denied(self):
        for args in ({"limit": True}, {"offset": -1}, {"limit": 101}):
            with self.assertRaises(EngineeringError):
                self.service.read(self.fixture.actor, mx.ASSET, **args)
        with self.assertRaises(EngineeringError):
            self.service.read(None, mx.ASSET)
    def test_router_default_off_and_read_only(self):
        self.assertEqual(build_asset_context_router(self.service).routes, [])
        app = FastAPI()
        app.include_router(build_asset_context_router(self.service, enabled=True, trusted_principal_dependency=lambda: self.fixture.actor))
        with TestClient(app) as client:
            response = client.get('/v1/engineering/asset-context/' + mx.ASSET)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(client.post('/v1/engineering/asset-context/' + mx.ASSET).status_code, 405)
