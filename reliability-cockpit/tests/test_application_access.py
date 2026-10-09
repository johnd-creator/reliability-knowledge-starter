"""Privilege faults are introduced only in the explicitly isolated *_test fixture."""
import os, unittest
from uuid import uuid4
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from src.repositories.application_migrations import ApplicationMigrator, MIGRATIONS, LEDGER
from src.repositories.application_access import audit_runtime_access
from src.repositories.application_boundary import ApplicationStore
from src.domain.engineering import EngineeringError


@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable PostgreSQL required")
class ApplicationAccessTest(unittest.TestCase):
    def setUp(self):
        url = make_url(os.environ["NADI_APPLICATION_TEST_DSN"])
        if url.host not in {"127.0.0.1", "localhost"} or not url.database.endswith("_test"):
            raise RuntimeError("isolated fixture only")
        self.engine = create_engine(url)
        suffix = uuid4().hex[:10]
        self.owner, self.cap, self.runtime = ["e_" + v + "_" + suffix for v in ("owner", "cap", "runtime")]
        with self.engine.begin() as c:
            c.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public")
            c.exec_driver_sql(f"CREATE ROLE {self.owner} NOLOGIN; CREATE ROLE {self.cap} NOLOGIN; CREATE ROLE {self.runtime} LOGIN")
            c.exec_driver_sql(f"GRANT USAGE, CREATE ON SCHEMA public TO {self.owner}")
        self.runner = ApplicationMigrator(self.engine, expected_database=url.database, isolated=True)
        self.runner.apply()
        with self.engine.begin() as c:
            for name in set().union(*MIGRATIONS.values()) | {LEDGER}:
                c.exec_driver_sql(f"ALTER TABLE {name} OWNER TO {self.owner}")
            # Fixture DBA owns the DB; capability/runtime never own it.
            q = c.dialect.identifier_preparer.quote(url.database)
            c.exec_driver_sql(f"REVOKE TEMPORARY ON DATABASE {q} FROM PUBLIC")
            c.exec_driver_sql(f"GRANT CONNECT ON DATABASE {q} TO {self.runtime}")
            c.exec_driver_sql(f"GRANT {self.cap} TO {self.runtime}")
        self.runner.grant_writer(self.cap)

    def tearDown(self):
        with self.engine.begin() as c:
            for role in (self.runtime, self.cap, self.owner):
                c.exec_driver_sql(f"DROP OWNED BY {role} CASCADE; DROP ROLE {role}")
            c.exec_driver_sql("CREATE SCHEMA IF NOT EXISTS public")
        self.engine.dispose()

    def audit(self):
        return audit_runtime_access(self.engine, expected_database=self.engine.url.database,
                                    owner=self.owner, capability=self.cap, runtime=self.runtime)

    def test_explicit_dedicated_database_preserves_legacy_boundary(self):
        ApplicationStore(self.engine, expected_database=self.engine.url.database, dedicated=True)
        with self.assertRaises(EngineeringError):
            ApplicationStore(self.engine, expected_database=self.engine.url.database)
        with self.assertRaises(EngineeringError):
            ApplicationStore(self.engine, expected_database="wrong_test", dedicated=True)
        with self.engine.begin() as c:
            c.exec_driver_sql("CREATE TABLE asset_af_mapping(id integer)")
        with self.assertRaises(EngineeringError):
            ApplicationStore(self.engine, expected_database=self.engine.url.database, dedicated=True)

    def test_audit_read_only_idempotent_and_runtime_denials(self):
        self.assertEqual(self.audit(), self.audit())
        with self.engine.begin() as c:
            c.exec_driver_sql(f"SET LOCAL ROLE {self.runtime}")
            c.exec_driver_sql("SELECT * FROM engineering_case_event")
        for command in ("UPDATE engineering_case_event SET case_id=case_id",
                        "DELETE FROM nadi_human_record_revision", "TRUNCATE nadi_security_activity",
                        "ALTER TABLE engineering_case ADD COLUMN unsafe text",
                        "CREATE TABLE unsafe(id integer)"):
            with self.assertRaises(Exception) as error:
                with self.engine.begin() as c:
                    c.exec_driver_sql(f"SET LOCAL ROLE {self.runtime}")
                    c.exec_driver_sql(command)
            self.assertEqual(error.exception.orig.sqlstate, "42501")

    def test_public_table_grant_is_rejected_before_grant_mutation(self):
        with self.engine.begin() as c:
            c.exec_driver_sql("GRANT UPDATE ON engineering_case_event TO PUBLIC")
        for action in (self.audit, lambda: self.runner.grant_writer(self.cap)):
            with self.assertRaises(EngineeringError) as error:
                action()
            self.assertEqual(error.exception.code, "APPLICATION_PUBLIC_PRIVILEGES_UNSAFE")

    def test_public_default_grant_is_rejected(self):
        with self.engine.begin() as c:
            c.exec_driver_sql(f"ALTER DEFAULT PRIVILEGES FOR ROLE {self.owner} GRANT UPDATE ON TABLES TO PUBLIC")
        with self.assertRaises(EngineeringError) as error:
            self.runner.grant_writer(self.cap)
        self.assertEqual(error.exception.code, "APPLICATION_DEFAULT_PRIVILEGES_UNSAFE")

    def test_schema_owner_and_create_capability_are_rejected(self):
        with self.engine.begin() as c:
            c.exec_driver_sql(f"GRANT CREATE ON SCHEMA public TO {self.cap}")
        with self.assertRaises(EngineeringError):
            self.runner.grant_writer(self.cap)
        with self.engine.begin() as c:
            c.exec_driver_sql(f"REVOKE CREATE ON SCHEMA public FROM {self.cap}; ALTER SCHEMA public OWNER TO {self.cap}")
        with self.assertRaises(EngineeringError) as error:
            self.runner.grant_writer(self.cap)
        self.assertEqual(error.exception.code, "APPLICATION_WRITER_OWNERSHIP_FORBIDDEN")

    def test_unexpected_membership_and_immutable_write_are_rejected(self):
        with self.engine.begin() as c:
            c.exec_driver_sql(f"GRANT {self.owner} TO {self.runtime}")
        with self.assertRaises(EngineeringError):
            self.audit()
        with self.engine.begin() as c:
            c.exec_driver_sql(f"REVOKE {self.owner} FROM {self.runtime}; GRANT UPDATE ON engineering_case_event TO {self.runtime}")
        with self.assertRaises(EngineeringError):
            self.audit()

    def test_database_temp_permission_is_rejected(self):
        with self.engine.begin() as c:
            q = c.dialect.identifier_preparer.quote(self.engine.url.database)
            c.exec_driver_sql(f"GRANT TEMPORARY ON DATABASE {q} TO {self.runtime}")
        with self.assertRaises(EngineeringError) as error:
            self.audit()
        self.assertEqual(error.exception.code, "APPLICATION_RUNTIME_DDL_FORBIDDEN")
