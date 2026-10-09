"""Persistent laptop fixture, never imported by the operational API.

Setup applies canonical migrations to a verified dedicated *_test database only.
Reload reuses accounts, sessions and human records. No schema reset or source I/O.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url

TESTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TESTS))
from test_condition_evidence import ConditionProjectionTest, ASSET_ID
from src.api.engineering_qa import create_qa_app
from src.repositories.application_migrations import ApplicationMigrator
from src.services.local_authentication import ACCOUNT, LocalIdentityProvider
from src.services.application_identity import SessionAuthority
from src.domain.engineering import Role
from src.repositories.application_boundary import ApplicationStore
from src.repositories.engineering import CaseRepository
from src.repositories.human_records import HumanRecordRepository
from src.services.engineering_evidence import LocalEvidenceCatalog
from src.services.reviewed_inspection_evidence import ReviewedInspectionCatalog
from src.services.application_evidence import ApplicationEvidenceCatalog
from src.services.engineering import CaseService
from src.services.human_records import InspectionService
from src.services.recommendation import RecommendationService
from src.services.maximo_intelligence import LocalMaintenanceIntelligence
from src.services.asset_context import AssetContextService


def private_json(path):
    path = Path(path)
    info = path.lstat()
    if path.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise RuntimeError("PRIVATE_DEVELOPMENT_CONFIG_REQUIRED")
    return json.loads(path.read_text())


def checked_url(dsn):
    url = make_url(dsn)
    if (url.get_backend_name() != "postgresql" or url.host != "127.0.0.1"
            or url.port != 15443 or url.database != "nadi_live_dev_test"
            or url.username != "nadi_dev_fixture" or url.query):
        raise RuntimeError("DEDICATED_DEVELOPMENT_DATABASE_REQUIRED")
    return url


class PersistentFixture:
    def __init__(self, config):
        self.engine = create_engine(checked_url(config["application_dsn"]))
        ApplicationMigrator(self.engine, expected_database="nadi_live_dev_test", isolated=True).apply()
        self.store = ApplicationStore(self.engine, expected_database="nadi_live_dev_test", isolated=True)
        self.pi = ConditionProjectionTest()
        self.pi.setUp()
        self.pi.project(self.pi.source_document({"synthetic-current": {"Timestamp": "1970-01-01T00:00:00Z"}}))
        self.asset = ASSET_ID
        self.mart = self.pi.reader()  # In-memory synthetic Mart only; no operational DSN.

    def wire(self, provider):
        directory = lambda subject: provider.current_grant(subject).principal if provider.current_grant(subject) else None
        local = LocalEvidenceCatalog(self.mart)
        self.inspections = InspectionService(HumanRecordRepository(self.store), local, enabled=True)
        catalog = ReviewedInspectionCatalog(local, self.inspections, directory)
        self.cases = CaseService(CaseRepository(self.engine), catalog, directory, enabled=True)
        self.inspections.catalog = ApplicationEvidenceCatalog(catalog, self.cases)
        self.recommendations = RecommendationService(HumanRecordRepository(self.store),
            ApplicationEvidenceCatalog(catalog, self.cases), LocalMaintenanceIntelligence(self.mart), directory,
            lambda team, asset: team == "team:demo" and asset == self.asset, enabled=True)
        self.context = AssetContextService(self.mart, cases=self.cases, inspections=self.inspections,
            recommendations=self.recommendations, enabled=True)


def create_live_app():
    if os.environ.get("NADI_DISPOSABLE_QA_ACK") != "persistent-laptop-fixture":
        raise RuntimeError("EXPLICIT_DEVELOPMENT_ACK_REQUIRED")
    config = private_json(os.environ["NADI_DEV_CONFIG"])
    fixture = PersistentFixture(config)
    provider = LocalIdentityProvider(fixture.store)
    accounts_path = Path(config["accounts_file"])
    with fixture.engine.connect() as connection:
        count = len(connection.execute(select(ACCOUNT.c.user_id)).all())
    if not count:
        accounts = private_json(accounts_path)
        admin = provider.bootstrap(username=accounts["admin"]["username"],
            password=accounts["admin"]["password"], assets={fixture.asset}, operator_ref="laptop-fixture")
        accounts["admin"]["user_id"] = admin
        for name, role in (("engineer", Role.AUTHOR), ("reviewer", Role.REVIEWER)):
            accounts[name]["user_id"] = provider.create_account(provider.current_grant(admin),
                username=accounts[name]["username"], password=accounts[name]["password"],
                roles={role}, assets={fixture.asset}, require_change=False)
        accounts["asset"] = fixture.asset
        accounts_path.write_text(json.dumps(accounts, indent=2))
    else:
        accounts = private_json(accounts_path)
        with fixture.engine.connect() as connection:
            users = set(connection.execute(select(ACCOUNT.c.user_id)).scalars())
        if not {accounts[name].get("user_id") for name in ("admin", "engineer", "reviewer")} <= users:
            raise RuntimeError("EXPLICIT_FIXTURE_ACCOUNT_RECOVERY_REQUIRED")
    fixture.wire(provider)
    fixture.authority = SessionAuthority(fixture.store, provider,
        origins={"https://localhost:3000"}, idle_seconds=1800, absolute_seconds=28800)
    app = create_qa_app(authority=fixture.authority, cases=fixture.cases,
        inspections=fixture.inspections, recommendations=fixture.recommendations,
        context=fixture.context, environment="development")
    root = TESTS.parents[1]
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

    @app.get("/development/status")
    def development_status():
        from fastapi import HTTPException
        try:
            with fixture.engine.connect() as connection:
                if connection.scalar(text("SELECT current_database()")) != "nadi_live_dev_test":
                    raise ValueError()
        except Exception:
            raise HTTPException(503, detail={"code": "DEVELOPMENT_DATABASE_UNAVAILABLE"}) from None
        return {"environment": "DEVELOPMENT", "source_sha": sha,
                "database": "DISPOSABLE_TEST", "database_identity": "nadi_live_dev_test",
                "engineering": True,
                "source": "SYNTHETIC_FIXTURES", "reload_probe": "baseline"}

    app.state.fixture = fixture  # Keep synthetic engine/context alive for the process.
    return app
