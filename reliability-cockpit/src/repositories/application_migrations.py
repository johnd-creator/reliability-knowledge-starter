"""Deliberate application migration owner. No environment or startup integration."""
from hashlib import sha256
from pathlib import Path
from sqlalchemy import inspect, text
from src.repositories.application_boundary import ApplicationStore
from src.domain.engineering import EngineeringError
ROOT=Path(__file__).resolve().parents[2]/'application-migrations'
MIGRATIONS={
 '002_engineering_workspace.sql':{'engineering_case','engineering_case_event','engineering_case_receipt'},
 '003_application_identity.sql':{'nadi_application_session','nadi_security_activity'},
 '004_human_records.sql':{'nadi_human_record','nadi_human_record_revision','nadi_human_record_receipt'},
 '005_private_attachments.sql':{'nadi_attachment','nadi_attachment_event'},
 '006_local_authentication.sql':{'nadi_local_account','nadi_local_login_budget','nadi_local_security_event'},
}
CURRENT={'engineering_case','nadi_application_session','nadi_human_record','nadi_local_account','nadi_local_login_budget'}
LEDGER='nadi_application_migration'
class ApplicationMigrator:
    def __init__(self,engine,*,expected_database,isolated=False,dedicated=False):
        self.store=ApplicationStore(engine,expected_database=expected_database,isolated=isolated,dedicated=dedicated)
        if engine.dialect.name!='postgresql':raise EngineeringError('POSTGRESQL_REQUIRED',503)
    def _status(self,c):
        tables=set(inspect(c).get_table_names())
        records=dict(c.execute(text('SELECT name,checksum FROM nadi_application_migration')).all()) if LEDGER in tables else {}
        if set(records)-set(MIGRATIONS):raise EngineeringError('UNKNOWN_APPLICATION_MIGRATION',503)
        result=[];pending=False
        for name,relations in MIGRATIONS.items():
            checksum=sha256((ROOT/name).read_bytes()).hexdigest()
            if name in records:
                if pending or records[name]!=checksum or not relations<=tables:
                    raise EngineeringError('APPLICATION_MIGRATION_DRIFT',503)
                state='APPLIED'
            else:
                if relations&tables:raise EngineeringError('UNTRACKED_APPLICATION_SCHEMA',503)
                pending=True;state='PENDING'
            result.append({'name':name,'checksum':checksum,'status':state})
        return result
    def status(self):
        with self.store.engine.connect() as c:return self._status(c)
    def apply(self):
        with self.store.engine.begin() as c:
            c.execute(text('SELECT pg_advisory_xact_lock(793245102)'))
            states=self._status(c)
            c.exec_driver_sql('CREATE TABLE IF NOT EXISTS nadi_application_migration (name varchar(100) PRIMARY KEY,checksum varchar(64) NOT NULL,applied_at timestamptz NOT NULL DEFAULT now())')
            for row in states:
                if row['status']=='PENDING':
                    c.exec_driver_sql((ROOT/row['name']).read_text())
                    c.execute(text('INSERT INTO nadi_application_migration(name,checksum) VALUES (:name,:checksum)'),{'name':row['name'],'checksum':row['checksum']})
            return self._status(c)
    def grant_writer(self,role):
        # Provision an existing NOLOGIN role, never credentials or role creation.
        with self.store.engine.begin() as c:
            if any(r['status']!='APPLIED' for r in self._status(c)):raise EngineeringError('APPLICATION_SCHEMA_NOT_READY',503)
            from src.repositories.application_access import assert_writer_capability, assert_no_public_application_grants
            assert_writer_capability(c,role)
            assert_no_public_application_grants(c,set().union(*MIGRATIONS.values())|{LEDGER})
            row=c.execute(text('SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolbypassrls FROM pg_roles WHERE rolname=:role'),{'role':role}).first()
            if row is None or any(row):raise EngineeringError('APPLICATION_WRITER_ROLE_UNSAFE',503)
            if c.scalar(text('SELECT count(*) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member WHERE r.rolname=:role'),{'role':role}):raise EngineeringError('APPLICATION_WRITER_ROLE_UNSAFE',503)
            q=c.dialect.identifier_preparer.quote(role)
            c.exec_driver_sql(f'GRANT USAGE ON SCHEMA public TO {q}')
            for relations in MIGRATIONS.values():
                for table in sorted(relations):
                    if c.scalar(text('SELECT pg_get_userbyid(relowner)=:role FROM pg_class WHERE oid=to_regclass(:name)'),{'role':role,'name':table}):raise EngineeringError('APPLICATION_WRITER_OWNERSHIP_FORBIDDEN',503)
                    c.exec_driver_sql(f'REVOKE ALL ON TABLE {table} FROM {q}')
                    privileges='SELECT, INSERT, UPDATE' if table in CURRENT else 'SELECT, INSERT'
                    c.exec_driver_sql(f'GRANT {privileges} ON TABLE {table} TO {q}')

            c.exec_driver_sql(f'REVOKE ALL ON TABLE {LEDGER} FROM {q}')
            c.exec_driver_sql(f'GRANT SELECT ON TABLE {LEDGER} TO {q}')
