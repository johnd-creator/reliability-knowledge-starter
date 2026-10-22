"""Read-only controller bridge for two exact reviewed source snapshots.

No source monkeypatch, migration, grant, ledger filtering, or data recovery.
The full six-entry ledger is exposed, including explicitly pending migration007.
"""
import hashlib
import json
import subprocess
from pathlib import Path
from sqlalchemy import text

FROM_SHA = 'e84eaec0e38e57cf0f057abaeda04e34739b01f8'
TO_SHA = '85e6bb61eb5cb724e436846b9bdeee31709dffd4'
HISTORY_SCHEMA_SHA256 = '7dc4b17be2b6281887fcd02fe2042794d8a5f1d67bf05cdad3856d54c8f56411'
HISTORY_TABLES = {'nadi_history_source', 'nadi_history_profile', 'nadi_history_cell',
                  'nadi_history_event', 'nadi_history_alias', 'nadi_history_batch', 'nadi_history_receipt'}
RELATIONS = {
 '002_engineering_workspace.sql': {'engineering_case','engineering_case_event','engineering_case_receipt'},
 '003_application_identity.sql': {'nadi_application_session','nadi_security_activity'},
 '004_human_records.sql': {'nadi_human_record','nadi_human_record_revision','nadi_human_record_receipt'},
 '005_private_attachments.sql': {'nadi_attachment','nadi_attachment_event'},
 '006_local_authentication.sql': {'nadi_local_account','nadi_local_login_budget','nadi_local_security_event'},
 '007_pdm_source_history.sql': HISTORY_TABLES,
}


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True, timeout=10).strip()


def source_identity(root):
    root = Path(root)
    sha = git(root, 'rev-parse', 'HEAD')
    if sha not in {FROM_SHA, TO_SHA}:
        raise RuntimeError('HISTORY_BRIDGE_EXACT_SOURCE_REQUIRED')
    index = 0 if sha == FROM_SHA else 1
    if {p:git(root, 'rev-parse', sha+':'+p) for p in SOURCE_OBJECTS} != {p:v[index] for p,v in SOURCE_OBJECTS.items()}:
        raise RuntimeError('HISTORY_BRIDGE_SOURCE_OBJECTS_CHANGED')
    if git(root, 'diff', '--name-only', 'HEAD', '--', *SOURCE_OBJECTS):
        raise RuntimeError('HISTORY_BRIDGE_SOURCE_BYTES_CHANGED')
    if git(root, 'ls-files', '--others', '--exclude-standard', '--', *SOURCE_OBJECTS):
        raise RuntimeError('HISTORY_BRIDGE_UNREVIEWED_SOURCE_FILES')
    return sha


def catalog(c):
    """Exact PostgreSQL16 schema semantics, independent of source model imports."""
    scope = "c.relnamespace='public'::regnamespace AND c.relname LIKE 'nadi_history_%'"
    queries = {
      'relations': f"SELECT c.relname,c.relkind,c.relpersistence,c.relrowsecurity,c.relforcerowsecurity,c.relispartition FROM pg_class c WHERE {scope} AND c.relkind NOT IN ('i','I') ORDER BY c.relname",
      'columns': f"SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod),a.attnotnull,pg_get_expr(d.adbin,d.adrelid),a.attidentity,a.attgenerated,a.attcollation::regcollation::text FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE {scope} AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum",
      'constraints': f"SELECT c.relname,k.conname,k.contype,pg_get_constraintdef(k.oid,true),k.condeferrable,k.condeferred,k.convalidated FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid WHERE {scope} ORDER BY c.relname,k.conname",
      'indexes': f"SELECT c.relname,x.relname,pg_get_indexdef(i.indexrelid),i.indisvalid,i.indisready FROM pg_index i JOIN pg_class c ON c.oid=i.indrelid JOIN pg_class x ON x.oid=i.indexrelid WHERE {scope} ORDER BY c.relname,x.relname",
      'triggers': f"SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid,true) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid WHERE {scope} AND NOT t.tgisinternal ORDER BY c.relname,t.tgname",
      'policies': "SELECT tablename,policyname,permissive,roles,cmd,qual,with_check FROM pg_policies WHERE schemaname='public' AND tablename LIKE 'nadi_history_%' ORDER BY tablename,policyname",
      'rules': "SELECT tablename,rulename,definition FROM pg_rules WHERE schemaname='public' AND tablename LIKE 'nadi_history_%' ORDER BY tablename,rulename",
      'inheritance': f"SELECT c.relname,pn.nspname,p.relname FROM pg_inherits i JOIN pg_class c ON c.oid=i.inhrelid JOIN pg_class p ON p.oid=i.inhparent JOIN pg_namespace pn ON pn.oid=p.relnamespace WHERE {scope} ORDER BY c.relname,pn.nspname,p.relname",
    }
    return {name:[tuple(row) for row in c.execute(text(query))] for name,query in queries.items()}


def catalog_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def states(engine, root, *, require_history=False):
    sha = source_identity(root)
    with engine.begin() as c:
        c.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        if not 160000 <= int(c.scalar(text('SHOW server_version_num'))) < 170000:
            raise RuntimeError('HISTORY_BRIDGE_POSTGRES16_REQUIRED')
        if c.scalar(text('SELECT current_schemas(false)')) != ['public']:
            raise RuntimeError('HISTORY_BRIDGE_PUBLIC_SCHEMA_REQUIRED')
        names = set(c.scalars(text("SELECT relname FROM pg_class WHERE relnamespace='public'::regnamespace AND relkind IN ('r','p')")))
        if 'nadi_application_migration' not in names:
            raise RuntimeError('HISTORY_BRIDGE_BASE_MIGRATIONS_REQUIRED')
        records = dict(c.execute(text('SELECT name,checksum FROM public.nadi_application_migration')).all())
        if set(records)-set(MIGRATION_CHECKSUMS):
            raise RuntimeError('UNKNOWN_APPLICATION_MIGRATION')
        result = []
        for name, checksum in MIGRATION_CHECKSUMS.items():
            if name == '007_pdm_source_history.sql':
                continue
            if records.get(name) != checksum or not RELATIONS[name] <= names:
                raise RuntimeError('APPLICATION_MIGRATION_DRIFT')
            if hashlib.sha256((Path(root)/'reliability-cockpit/application-migrations'/name).read_bytes()).hexdigest() != checksum:
                raise RuntimeError('HISTORY_BRIDGE_MIGRATION_SOURCE_CHANGED')
            result.append({'name':name,'checksum':checksum,'status':'APPLIED'})
        schema = catalog(c)
        checksum = MIGRATION_CHECKSUMS['007_pdm_source_history.sql']
        if '007_pdm_source_history.sql' not in records:
            if any(schema.values()):
                raise RuntimeError('UNTRACKED_APPLICATION_SCHEMA')
            state = 'PENDING'
        else:
            if records['007_pdm_source_history.sql'] != checksum or catalog_digest(schema) != HISTORY_SCHEMA_SHA256:
                raise RuntimeError('HISTORY_BRIDGE_007_SCHEMA_OR_CHECKSUM_DRIFT')
            state = 'APPLIED'
        if (require_history or sha == TO_SHA) and state != 'APPLIED':
            raise RuntimeError('EXPLICIT_FIXTURE_PREPARATION_REQUIRED')
        result.append({'name':'007_pdm_source_history.sql','checksum':checksum,'status':state})
    if source_identity(root) != sha:
        raise RuntimeError('HISTORY_BRIDGE_SOURCE_CHANGED_DURING_PROBE')
    return result

SOURCE_OBJECTS = {'reliability-cockpit/application-migrations': ['f8584713e8c5ce4f86aecb0212d0e68665ff8aa9', 'a4c314c3f52116fcfe4d3ffb879bd798cb796d95'], 'reliability-cockpit/src/repositories': ['abaf256282df8433e05eda2f760ac7c9cddaf2a5', 'ee7f92d2ec9a21e3616b092a4158e4407819cf3b'], 'reliability-cockpit/src/services/local_authentication.py': ['f24f08f4b0993cfa730c1c88f5a8a1bc4038fae4', 'f24f08f4b0993cfa730c1c88f5a8a1bc4038fae4'], 'reliability-cockpit/src/services/application_identity.py': ['101149a2d096419bf49a1bf6668ea6c66b7e29e2', '101149a2d096419bf49a1bf6668ea6c66b7e29e2'], 'reliability-cockpit/src/api/engineering_qa.py': ['627be44f04b92a7d468322db2735715618c150f7', '8ae698ce751a810fa0783f9cc34c0c6139f65b2c'], 'reliability-cockpit/pyproject.toml': ['6cbf209cf390ed844bc8e1f89031a87f9855034e', '6cbf209cf390ed844bc8e1f89031a87f9855034e'], 'reliability-cockpit/tests/qa/live_server.py': ['033bc1bb534e92b51fee14de4cb8945e71a0eb6d', '033bc1bb534e92b51fee14de4cb8945e71a0eb6d'], 'reliability-cockpit/tests/test_condition_evidence.py': ['26c379ba59a2ef76f66ae44459c786181044ed44', '26c379ba59a2ef76f66ae44459c786181044ed44'], 'reliability-cockpit/tests/test_asset_af_mapping_admin.py': ['37b578d2b93f4d4740adc73c8cc7b9edabdfd5a0', '37b578d2b93f4d4740adc73c8cc7b9edabdfd5a0'], 'pi-collector/tests/fixtures/condition_source.py': ['9456d29bf54882c4f69515bea765682a5d63a160', '9456d29bf54882c4f69515bea765682a5d63a160']}
MIGRATION_CHECKSUMS = {'002_engineering_workspace.sql': 'b56246974ed9caccd44eebf8223dc23187b5a5cc989d2e5b7d7dd2bbad733d00', '003_application_identity.sql': 'e4898aae1f15e7016614b22523625709efcbae4aab4c2ea351b3d318268e5a6d', '004_human_records.sql': '89f1b7348b976b2db848861af1eb8eb29bd90b275549f3e06883b796cdc71455', '005_private_attachments.sql': 'fca9c2d5e494caf8dad9240ed346f4e9b7322afc7700f1916d93df24540698dd', '006_local_authentication.sql': 'd77c1ed91b638cb088cfef2c6e3ead86b1ae05241809da72c3d2414998c25e76', '007_pdm_source_history.sql': '95806119fe0a131ec8c64733da9f41de85e59389cae3ee80820876f27abad524'}
