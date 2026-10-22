"""Laptop-only fixture bootstrap. Imports the selected source's QA services.

Schema/account initialization is an explicit prepare command, never API startup.
No operational config, DSN, collector, legacy worker or source adapter is loaded.
"""
import hashlib
import argparse
import json
import os
import secrets
import subprocess
from pathlib import Path

DB = 'nadi_local_dev_01_test'
ROLE = 'nadi_local_dev_01'


def checked(config):
    from sqlalchemy.engine import make_url
    url = make_url(config['application_dsn'])
    if (url.get_backend_name() != 'postgresql' or url.host != '127.0.0.1'
            or url.port != 15443 or url.database != DB or url.username != ROLE or url.query):
        raise RuntimeError('LOCAL_FIXTURE_IDENTITY_REQUIRED')
    return url


def load():
    from live_server import private_json
    if os.environ.get('NADI_LOCAL_DEV_ACK') != DB:
        raise RuntimeError('LOCAL_FIXTURE_ACK_REQUIRED')
    config = private_json(os.environ['NADI_LOCAL_DEV_CONFIG'])
    checked(config)
    return config


def engine_for(config):
    from sqlalchemy import create_engine, text
    engine = create_engine(checked(config), hide_parameters=True)
    with engine.connect() as c:
        if c.scalar(text('SELECT current_database()')) != DB or c.scalar(text('SELECT current_user')) != ROLE:
            raise RuntimeError('LOCAL_FIXTURE_IDENTITY_REQUIRED')
        if c.scalar(text('SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolbypassrls FROM pg_roles WHERE rolname=current_user')):
            raise RuntimeError('UNSAFE_FIXTURE_ROLE')
    return engine


def prepare():
    from sqlalchemy import inspect
    from src.repositories.application_migrations import ApplicationMigrator
    from src.repositories.application_boundary import ApplicationStore
    from src.repositories.qa_advisory_schema import change_qa_advisory_schema
    from src.services.local_authentication import LocalIdentityProvider
    from test_condition_evidence import ASSET_ID
    config = load()
    engine = engine_for(config)
    if inspect(engine).get_table_names():
        raise RuntimeError('NEW_EMPTY_FIXTURE_REQUIRED')
    ApplicationMigrator(engine, expected_database=DB, isolated=True).apply()
    change_qa_advisory_schema(engine, expected_database=DB, acknowledgement='isolated-advisory-qa-only')
    provider = LocalIdentityProvider(ApplicationStore(engine, expected_database=DB, isolated=True))
    accounts = {'asset': ASSET_ID, 'database': DB, 'source': 'SYNTHETIC_LOCAL_DEVELOPMENT'}
    password = secrets.token_urlsafe(28)
    admin = provider.bootstrap(username='local-operator', password=password,
        assets={ASSET_ID, 'asset:SYNTHETIC:FOREIGN'}, operator_ref='NADI-LOCAL-DEV-01')
    accounts['admin'] = {'username': 'local-operator', 'password': password, 'user_id': admin}
    for name, role, assets in [('engineer', 'AUTHOR', {ASSET_ID}), ('reviewer', 'REVIEWER', {ASSET_ID}),
                              ('outsider', 'AUTHOR', {'asset:SYNTHETIC:FOREIGN'})]:
        password = secrets.token_urlsafe(28)
        user = provider.create_account(provider.current_grant(admin), username='local-'+name,
            password=password, roles={role}, assets=assets, require_change=False)
        accounts[name] = {'username': 'local-'+name, 'password': password, 'user_id': user}
    target = Path(config['accounts_file'])
    with target.open('x') as f:
        os.chmod(target, 0o600)
        json.dump(accounts, f)
    engine.dispose()


def selected_source_root():
    from src.repositories.application_migrations import ROOT
    return ROOT.parent.parent


def migration_states(engine, config):
    """Exact controller-owned bridge; unrelated source behavior is unchanged."""
    from pdm_007_bridge import FROM_SHA, TO_SHA, git, states
    # A selection probe intentionally retains the old config while importing
    # the candidate through PYTHONPATH. Bind the code actually being probed.
    root = selected_source_root()
    sha = git(root, 'rev-parse', 'HEAD')
    if sha in {FROM_SHA, TO_SHA}:
        return states(engine, root)
    from src.repositories.application_migrations import ApplicationMigrator
    return ApplicationMigrator(engine, expected_database=DB, isolated=True).status()


def require_startup_states(states, config):
    from pdm_007_bridge import FROM_SHA, git
    old = git(selected_source_root(), 'rev-parse', 'HEAD') == FROM_SHA
    if any(row['status'] != 'APPLIED' and not (
            old and row['name'] == '007_pdm_source_history.sql' and row['status'] == 'PENDING') for row in states):
        raise RuntimeError('EXPLICIT_FIXTURE_PREPARATION_REQUIRED')


def create_app():
    from sqlalchemy import text
    from src.repositories.application_migrations import ApplicationMigrator
    from src.repositories.application_boundary import ApplicationStore
    from src.services.local_authentication import LocalIdentityProvider
    from src.services.application_identity import SessionAuthority
    from src.api.engineering_qa import create_qa_app
    from test_condition_evidence import ConditionProjectionTest, ASSET_ID
    from live_server import PersistentFixture, private_json
    config = load()
    if Path(config['source_root']).resolve() != selected_source_root().resolve():
        raise RuntimeError('LOCAL_FIXTURE_IMPORTED_SOURCE_MISMATCH')
    # Reuse the selected source fixture wiring, without its historical fixed DB initializer.
    fixture = PersistentFixture.__new__(PersistentFixture)
    fixture.engine = engine_for(config)
    states = migration_states(fixture.engine, config)
    require_startup_states(states, config)
    fixture.store = ApplicationStore(fixture.engine, expected_database=DB, isolated=True)
    fixture.pi = ConditionProjectionTest()
    fixture.pi.setUp()
    fixture.pi.project(fixture.pi.source_document({'synthetic-current': {'Timestamp': '1970-01-01T00:00:00Z'}}))
    fixture.asset, fixture.mart = ASSET_ID, fixture.pi.reader()
    provider = LocalIdentityProvider(fixture.store)
    accounts = private_json(config['accounts_file'])
    for name in ['admin', 'engineer', 'reviewer', 'outsider']:
        if not provider.current_grant(accounts[name]['user_id']):
            raise RuntimeError('LOCAL_FIXTURE_ACCOUNT_UNAVAILABLE')
    fixture.wire(provider)
    fixture.authority = SessionAuthority(fixture.store, provider, origins={'https://localhost:3000'},
                                         idle_seconds=1800, absolute_seconds=28800)
    app = create_qa_app(authority=fixture.authority, cases=fixture.cases, inspections=fixture.inspections,
        recommendations=fixture.recommendations, context=fixture.context, environment='development')
    root = Path(config['source_root'])
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True, timeout=5).strip()
    loaded_sha = git('rev-parse', 'HEAD')

    @app.get('/development/status')
    def status():
        with fixture.engine.connect() as c:
            if c.scalar(text('SELECT current_database()')) != DB:
                raise RuntimeError('LOCAL_FIXTURE_IDENTITY_CHANGED')
        return {'environment': 'DEVELOPMENT', 'source_sha': loaded_sha, 'current_sha': git('rev-parse', 'HEAD'),
            'branch': git('branch', '--show-current'), 'dirty': bool(git('status', '--porcelain')),
            'database': 'DISPOSABLE_TEST', 'database_identity': DB, 'engineering': True,
            'source': 'SYNTHETIC_LOCAL_DEVELOPMENT', 'reload_probe': 'baseline',
            'bootstrap_sha': config['workflow_sha']}
    app.state.fixture = fixture
    return app


def records_readiness(engine):
    """Read-only bounded existing-document validation; never export private content."""
    from sqlalchemy import text
    from src.domain.manual_inspection import ManualInspection
    from src.domain.recommendation import Recommendation
    from src.domain.advisory import Advisory
    from src.domain.engineering import EngineeringCase
    models={'INSPECTION':ManualInspection,'RECOMMENDATION':Recommendation,'ADVISORY':Advisory,'CASE':EngineeringCase}
    queries=[('human','SELECT kind,document FROM nadi_human_record ORDER BY kind,record_id'),
             ('revision','SELECT kind,snapshot FROM nadi_human_record_revision ORDER BY kind,record_id,revision'),
             ('receipt','SELECT kind,result FROM nadi_human_record_receipt ORDER BY actor,request_id'),
             ('case',"SELECT 'CASE',document FROM engineering_case ORDER BY case_id"),
             ('case_event',"SELECT 'CASE',snapshot FROM engineering_case_event ORDER BY case_id,revision"),
             ('case_receipt',"SELECT 'CASE',result FROM engineering_case_receipt ORDER BY actor,request_id")]
    raw=hashlib.sha256();normalized=hashlib.sha256();counts={};total=0;size=0
    try:
        with engine.connect() as c:
            c.execute(text('SET TRANSACTION READ ONLY'))
            for name,query in queries:
                counts[name]=0
                for kind,document in c.execution_options(stream_results=True).execute(text(query)):
                    total+=1;counts[name]+=1
                    if total>10000:raise RuntimeError('COMPATIBILITY_RECORD_SCAN_LIMIT')
                    encoded=json.dumps([name,kind,document],sort_keys=True,separators=(',',':')).encode()
                    size+=len(encoded)
                    if size>128*1024*1024:raise RuntimeError('COMPATIBILITY_RECORD_SCAN_LIMIT')
                    model=models[kind].model_validate(document)
                    raw.update(encoded+b'\n')
                    normalized.update(json.dumps([name,kind,model.model_dump(mode='json')],sort_keys=True,separators=(',',':')).encode()+b'\n')
    except RuntimeError:raise
    except Exception:raise RuntimeError('EXISTING_RECORD_NOT_READABLE') from None
    return {'counts':counts,'raw_sha256':raw.hexdigest(),'normalized_sha256':normalized.hexdigest()}


def compatibility():
    """Read-only existing fixture check. Never initializes tables, accounts or sessions."""
    from sqlalchemy import text
    from src.repositories.application_migrations import ApplicationMigrator
    from src.repositories.qa_advisory_schema import qa_advisory_schema_ready
    config = load()
    engine = engine_for(config)
    try:
        ledger = migration_states(engine, config)
        require_startup_states(ledger, config)
        if not qa_advisory_schema_ready(engine):
            raise RuntimeError('ADVISORY_ACK_SCHEMA_REQUIRED')
        with engine.connect() as c:
            c.execute(text('SET TRANSACTION READ ONLY'))
            # Catalogs only; no session content or operational store is inspected.
            columns = [tuple(r) for r in c.execute(text("SELECT table_name,column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position"))]
            constraints = [tuple(r) for r in c.execute(text("SELECT conname,pg_get_constraintdef(oid) FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY conname"))]
        return {'database':DB,'role':ROLE,'ledger':ledger,
                'schema_sha256':hashlib.sha256(json.dumps([columns,constraints],default=str).encode()).hexdigest(),
                'records':records_readiness(engine)}
    finally:
        engine.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', required=True,
                        help='Read-only compatibility check; fixture preparation requires separate authorization')
    parser.parse_args()
    print(json.dumps(compatibility()))
