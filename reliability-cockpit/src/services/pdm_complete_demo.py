"""Local full-history demo adapter preparation; no DDL, grants or automatic restore.

Qualification uses a separate exact profile. Default calls are read-only; applying
requires a current, exact preflight and a separate explicit execution reference.
"""
from pathlib import Path
from hashlib import sha256
import re
from sqlalchemy import select, text, inspect, func
from src.domain.engineering import EngineeringError
from src.repositories.application_migrations import ApplicationMigrator
from src.repositories.pdm_source_history import TABLES, Batch
from src.services.pdm_complete_import import CompleteHistoryImporter, frozen_plan, plan_lines, budget, LOCK_ID
from src.services.pdm_history_recovery import validate_snapshot, identity, business, history, BUSINESS
from src.services.pdm_source_history import digest
from src.services.local_authentication import ACCOUNT

PLAN_ID = 'e87f84abf7a32a223ff5c3568cd41b1748ac8f05c55f4524b393e46688f17b88'
COUNTS = {'sources':7,'profiles':426,'cells':173147,'events':25278}
BASELINE = {'nadi_human_record':35,'nadi_human_record_revision':46,'nadi_human_record_receipt':46,
            'engineering_case':4,'engineering_case_event':12,'engineering_case_receipt':12}
APPROVED_CATALOG_MISMATCHES = {'WB-VIB-BOILER','WB-VIB-TURBINE'}
ASSET = 'NADI-ASSET-001'
DEMO = ('127.0.0.1',15443,'nadi_local_dev_01_test','nadi_local_dev_01')


def checked_target(engine, *, qualification=False):
    """Verify URL before connecting; no credentials, query overrides or guesses."""
    u=engine.url
    valid=(u.host,u.port,u.database,u.username)==DEMO
    if qualification:
        valid=(u.host=='127.0.0.1' and u.port not in {None,5432,15443} and
               (u.database or '').startswith('pdm_history_complete_demo_adapter_') and
               u.database.endswith('_test') and u.username=='history_demo_importer')
    if engine.dialect.name!='postgresql' or u.query or not valid:
        raise EngineeringError('EXACT_COMPLETE_DEMO_TARGET_REQUIRED',403)
    with engine.connect() as c:
        if c.execute(text('SELECT current_database(),current_user')).one()!=(u.database,u.username):
            raise EngineeringError('COMPLETE_DEMO_TARGET_CHANGED',409)
        if c.scalar(text('SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolbypassrls FROM pg_roles WHERE rolname=current_user')):
            raise EngineeringError('UNSAFE_DEMO_IMPORT_ROLE',403)
        if {'asset_master','reliability_asset_registry','asset_af_mapping'}&set(inspect(c).get_table_names()):
            raise EngineeringError('FACTUAL_STORE_FORBIDDEN',403)
    return {'host':u.host,'port':u.port,'database':u.database,'role':u.username,
            'profile':'ISOLATED_QUALIFICATION' if qualification else 'ALLOWLISTED_LOCAL_DEMO'}


def migration_preflight(engine, *, qualification=False):
    """Read-only plan only. Never calls apply(), prepare() or grant_writer()."""
    destination=checked_target(engine,qualification=qualification)
    states=ApplicationMigrator(engine,expected_database=engine.url.database,isolated=True).status()
    expected=[r for r in states if r['name']!='007_pdm_source_history.sql']
    last=[r for r in states if r['name']=='007_pdm_source_history.sql']
    if len(expected)!=5 or any(r['status']!='APPLIED' for r in expected) or len(last)!=1:
        raise EngineeringError('ONLY_007_MAY_BE_PENDING',409)
    if last[0]['status']=='APPLIED':assert_history_schema(engine)
    with engine.begin() as c:
        c.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        rows=business(c);counts={name:len(rows[name]) for name in BUSINESS}
    if counts!=BASELINE:raise EngineeringError('DEMO_BASELINE_RECONCILIATION_REQUIRED',409)
    return {'dry_run':True,'target':destination,'migration_007':last[0],
            'business_counts':counts,'business_hash':digest(rows),
            'migration_executed':False,'grant_change_executed':False,
            'runtime_gate':'EXACT_CONTROLLER_AND_POST_007_ROLLBACK_BRIDGE_REQUIRED'}


def assert_history_schema(engine):
    """Require the reviewed column/PK/FK contract, not merely existing names."""
    inspector=inspect(engine)
    for name,table in TABLES.items():
        actual=[(c['name'],str(c['type']),c['nullable']) for c in inspector.get_columns(name,schema='public')]
        expected=[(c.name,c.type.compile(dialect=engine.dialect),c.nullable) for c in table.c]
        if actual!=expected or inspector.get_pk_constraint(name,schema='public')['constrained_columns']!=[c.name for c in table.primary_key]:
            raise EngineeringError('COMPLETE_DEMO_SCHEMA_DRIFT',409)
        actual_fks={(tuple(f['constrained_columns']),f['referred_table'],tuple(f['referred_columns'])) for f in inspector.get_foreign_keys(name,schema='public') if f.get('referred_schema') in {None,'public'}}
        expected_fks={(tuple(e.parent.name for e in fk.elements),fk.referred_table.name,tuple(e.column.name for e in fk.elements)) for fk in table.foreign_key_constraints}
        if actual_fks!=expected_fks or len(actual_fks)!=len(inspector.get_foreign_keys(name,schema='public')):
            raise EngineeringError('COMPLETE_DEMO_SCHEMA_DRIFT',409)


def assert_history_privileges(c):
    """Read-only prerequisite; never grants privileges or changes role ownership."""
    privileges={}
    for name in TABLES:
        actual={right:c.scalar(text('SELECT has_table_privilege(current_user,:relation,:right)'),{'relation':'public.'+name,'right':right})
                for right in ('SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER')}
        expected={right:right in ({'SELECT','INSERT','UPDATE'} if name=='nadi_history_batch' else {'SELECT','INSERT'}) for right in actual}
        owner=c.scalar(text("SELECT pg_get_userbyid(relowner)=current_user FROM pg_class WHERE oid=to_regclass(:relation)"),{'relation':'public.'+name})
        if owner or actual!=expected:raise EngineeringError('EXACT_HISTORY_WRITER_PRIVILEGES_REQUIRED',403)
        privileges[name]=actual
    return privileges


def source_binding(plan, paths):
    meta=list(plan_lines(plan,'sources'))
    if set(paths)!={r['sha256'] for r in meta}:raise EngineeringError('SOURCE_FILE_BINDING_REQUIRED',409)
    for row in meta:
        p=Path(paths[row['sha256']])
        if p.is_symlink() or p.suffix.lower() not in {'.xls','.xlsx'} or not 0<p.stat().st_size<=32*1024*1024 or sha256(p.read_bytes()).hexdigest()!=row['sha256']:
            raise EngineeringError('ORIGINAL_WORKBOOK_CHANGED',409)
    return {r['source_ref']:r['sha256'] for r in meta}


class CompleteDemoAdapter(CompleteHistoryImporter):
    def __init__(self, inspections, provider, *, qualification=False):
        if type(qualification) is not bool:raise EngineeringError('EXPLICIT_DEMO_PROFILE_REQUIRED',403)
        self.qualification=qualification
        self._applying=None
        super().__init__(inspections,provider)

    def _target(self):
        return checked_target(self.engine,qualification=self.qualification)

    def grant(self,subject,asset):
        grant=super().grant(subject,asset)
        if self._applying is not None and (subject!=self._applying['subject'] or grant.version!=self._applying['grant_version']):
            raise EngineeringError('DEMO_PREFLIGHT_GRANT_CHANGED',409)
        return grant

    def _validate_prewrite(self,c):
        prepared=self._applying
        if prepared is None:raise EngineeringError('EXPLICIT_DEMO_PREFLIGHT_REQUIRED',403)
        grants=[dict(r) for r in c.execute(select(ACCOUNT.c.user_id,ACCOUNT.c.active,ACCOUNT.c.password_change_required,ACCOUNT.c.grant_version,ACCOUNT.c.roles,ACCOUNT.c.asset_ids).order_by(ACCOUNT.c.user_id)).mappings()]
        if (assert_history_privileges(c)!=prepared['history_writer_privileges'] or identity(c)!=prepared['database_identity'] or digest(business(c))!=prepared['business_hash'] or
            digest(history(c))!=prepared['history_hash'] or digest(grants)!=prepared['grants_hash']):
            raise EngineeringError('DEMO_PREFLIGHT_CHANGED',409)

    def run(self,*args,**kwargs):
        raise EngineeringError('USE_EXACT_PREFLIGHT_AND_EXPLICIT_APPLY',403)

    def preflight(self,directory,subject,*,source_paths,recovery_snapshot,expected_snapshot_sha256):
        destination=self._target()
        with frozen_plan(directory,PLAN_ID) as plan:
            manifest=plan['manifest']
            if manifest['counts']!=COUNTS or len(manifest['coverage'])!=200 or sum(s['populated_cells'] for s in manifest['coverage'])!=173147:
                raise EngineeringError('EXACT_COMPLETE_DEMO_COVERAGE_REQUIRED',409)
            sources=source_binding(plan,source_paths)
            mismatches={s['source_ref'] for s in manifest['coverage'] if not s['catalog_hash_match']}
            if len(sources)!=7 or mismatches!=APPROVED_CATALOG_MISMATCHES:
                raise EngineeringError('EXACT_SEVEN_SOURCE_FINGERPRINTS_REQUIRED',409)
            # The reviewed plan pins actual source bytes; catalog mismatch never gains certainty.
            for item in plan_lines(plan,'events'):
                if item['source_ref'] in mismatches and item['document']['classification']!='RAW_UNRESOLVED':
                    raise EngineeringError('CATALOG_MISMATCH_MUST_REMAIN_RAW',409)
        assert_history_schema(self.engine)
        states=ApplicationMigrator(self.engine,expected_database=self.engine.url.database,isolated=True).status()
        if any(s['status']!='APPLIED' for s in states):raise EngineeringError('DEMO_007_PREPARATION_REQUIRED',409)
        grant=self.grant(subject,ASSET)
        with self.provider.guard(subject,grant.version), self.engine.begin() as c:
            c.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
            privileges=assert_history_privileges(c)
            recovery=validate_snapshot(c,recovery_snapshot,expected_snapshot_sha256)
            rows=business(c)
            if {k:len(v) for k,v in rows.items()}!=BASELINE:raise EngineeringError('DEMO_BASELINE_RECONCILIATION_REQUIRED',409)
            grants=[dict(r) for r in c.execute(select(ACCOUNT.c.user_id,ACCOUNT.c.active,ACCOUNT.c.password_change_required,ACCOUNT.c.grant_version,ACCOUNT.c.roles,ACCOUNT.c.asset_ids).order_by(ACCOUNT.c.user_id)).mappings()]
            current=history(c);size=budget(c)
            batch_id=digest([PLAN_ID,subject,ASSET])
            known={r['batch_id'] for r in recovery['history']['nadi_history_batch']}
            actual={r['batch_id'] for r in current['nadi_history_batch']}
            if actual-known-{batch_id}:raise EngineeringError('HISTORY_NEW_BATCH_REQUIRES_FRESH_BACKUP',409)
            if c.scalar(select(func.count()).select_from(TABLES['nadi_history_event']).where(
                    TABLES['nadi_history_event'].c.source_sha.in_(sources.values()),
                    (TABLES['nadi_history_event'].c.owner_id!=subject)|(TABLES['nadi_history_event'].c.access_asset_id!=ASSET))):
                raise EngineeringError('SOURCE_CUSTODY_CONFLICT',409)
            binding={'schema':'NADI_COMPLETE_DEMO_PREFLIGHT_V1','plan_id':PLAN_ID,'sources':sources,'catalog_mismatch_sources':sorted(mismatches),'target':destination,
                     'database_identity':identity(c),'migrations':states,'subject':subject,'grant_version':grant.version,
                     'asset':ASSET,'backup_sha256':expected_snapshot_sha256,'business_hash':digest(rows),
                     'history_hash':digest(current),'grants_hash':digest(grants),'history_writer_privileges':privileges,
                     'implementation_hash':digest([sha256(Path(__file__).read_bytes()).hexdigest(),
                         sha256(Path(__import__('src.services.pdm_complete_import',fromlist=['CompleteHistoryImporter']).__file__).read_bytes()).hexdigest()])}
        return {**binding,'preflight_id':digest(binding),'dry_run':True,'counts':COUNTS,'budget':size,
                'maximum_new_chunks_per_apply':250,'recovery':'NO_AUTOMATIC_DELETE_OR_RESTORE',
                'canonical_eligible':False,'runtime_gate':'EXACT_CONTROLLER_AND_POST_007_ROLLBACK_BRIDGE_REQUIRED'}

    def apply(self,directory,subject,*,source_paths,recovery_snapshot,expected_snapshot_sha256,
              expected_preflight_id,authorization_ref,max_new_chunks=250,after_commit=None):
        if not isinstance(authorization_ref,str) or not re.fullmatch('[A-Za-z0-9_.:@-]{8,120}',authorization_ref):
            raise EngineeringError('SEPARATE_DEMO_IMPORT_APPROVAL_REQUIRED',403)
        if type(max_new_chunks) is not int or not 1<=max_new_chunks<=250:
            raise EngineeringError('BOUNDED_DEMO_CHUNKS_REQUIRED',422)
        prepared=self.preflight(directory,subject,source_paths=source_paths,recovery_snapshot=recovery_snapshot,
                                expected_snapshot_sha256=expected_snapshot_sha256)
        if prepared['preflight_id']!=expected_preflight_id:raise EngineeringError('DEMO_PREFLIGHT_CHANGED',409)
        if self._applying is not None:raise EngineeringError('DEMO_ADAPTER_BUSY',409)
        self._applying=prepared
        try:
            result=super().run(directory,subject,access_asset_id=ASSET,expected_plan_id=PLAN_ID,source_paths=source_paths,
                               recovery_snapshot=recovery_snapshot,expected_snapshot_sha256=expected_snapshot_sha256,
                               max_chunks=max_new_chunks,after_commit=after_commit)
            return dict(result,scope='ALLOWLISTED_PROVISIONAL_DEMO_SOURCE_HISTORY',
                        authorization_ref=authorization_ref,preflight_id=expected_preflight_id)
        finally:self._applying=None
