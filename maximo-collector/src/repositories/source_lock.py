"""Explicit opt-in restricted source lock capability. Never installs SQL/roles.

Trusted installer/admin and source ownership remain independent rollout gates.
No source payload returned; application retains SELECT-only source privileges.
"""
import hashlib
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.repositories.projection_store import CaptureError

OWNER='nadi_capture_lock_owner'
FUNCTION='nadi_lock_source_exact'
BODY_SHA256='d084e770f5b95a0770f90feb75061a67f17c21b5730e1f89b234cde450b874d0'

class SourceLockBoundary:
    def __init__(self,db,schema):
        if not isinstance(schema,str) or not schema or len(schema.encode())>63 or '\x00' in schema:
            raise CaptureError('explicit reviewed source lock schema required')
        self.db=db;self.schema=schema
        self.qualified=db.engine.dialect.identifier_preparer.quote_identifier(schema)+'.'+FUNCTION

    def verify(self,s):
        try:
            self._verify(s)
        except (SQLAlchemyError,ValueError,KeyError,TypeError):
            raise CaptureError('restricted source lock capability unverified') from None

    def _verify(self,s):
        current=s.execute(text('SELECT current_user AS role,pg_catalog.current_database() AS db,pg_catalog.current_schema() AS schema,pg_catalog.current_schemas(false) AS schemas,pg_catalog.current_schemas(true) AS all_schemas')).mappings().one()
        if current['schema']!=self.schema or current['schemas']!=[self.schema] or any(n.startswith('pg_temp') for n in current['all_schemas']):raise CaptureError('restricted source lock schema mismatch')
        roles=s.execute(text('''SELECT oid,rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit
            FROM pg_catalog.pg_roles WHERE rolname IN (:owner,current_user)'''),{'owner':OWNER}).mappings().all()
        byname={r['rolname']:r for r in roles}
        if current['role']==OWNER or set(byname)!={OWNER,current['role']}:raise CaptureError('restricted source lock role missing')
        owner=byname[OWNER];app=byname[current['role']]
        flags=('rolsuper','rolcreatedb','rolcreaterole','rolreplication','rolbypassrls','rolinherit')
        if owner['rolcanlogin'] or any(r[f] for r in roles for f in flags):raise CaptureError('privileged source lock role')
        members=s.scalar(text('''SELECT count(*) FROM pg_catalog.pg_auth_members
            WHERE member IN (:owner,:app) OR roleid IN (:owner,:app)'''),{'owner':owner['oid'],'app':app['oid']})
        if members:raise CaptureError('source lock role membership forbidden')
        ownership=s.scalar(text('''SELECT n.nspowner IN (:owner,:app) OR d.datdba IN (:owner,:app)
            FROM pg_catalog.pg_namespace n CROSS JOIN pg_catalog.pg_database d
            WHERE n.nspname=:schema AND d.datname=pg_catalog.current_database()'''),
            {'owner':owner['oid'],'app':app['oid'],'schema':self.schema})
        if ownership:raise CaptureError('source lock schema/database ownership forbidden')
        for role in (OWNER,current['role']):
            authority=s.scalar(text('''SELECT pg_catalog.has_schema_privilege(:role,:schema,'CREATE') OR
                pg_catalog.has_database_privilege(:role,pg_catalog.current_database(),'CREATE,TEMPORARY')'''),{'role':role,'schema':self.schema})
            if authority:raise CaptureError('source lock creation privilege forbidden')
        tables=s.execute(text('''SELECT c.oid,c.relname,c.relowner,c.relkind,c.relrowsecurity,c.relforcerowsecurity
            FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname=:schema AND c.relname IN ('equipment','work_order')'''),{'schema':self.schema}).mappings().all()
        if len(tables)!=2:raise CaptureError('source lock relations missing')
        for table in tables:
            if table['relkind']!='r' or table['relowner'] in (owner['oid'],app['oid']) or table['relrowsecurity'] or table['relforcerowsecurity']:
                raise CaptureError('source ownership/RLS incompatible')
            for role in (OWNER,current['role']):
                forbidden=s.scalar(text("SELECT pg_catalog.has_table_privilege(:role,:oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR pg_catalog.has_any_column_privilege(:role,:oid,'INSERT,REFERENCES')"),{'role':role,'oid':table['oid']})
                if forbidden:raise CaptureError('source mutation privilege forbidden')
            columns=s.execute(text('''SELECT attname,
                pg_catalog.has_column_privilege(:owner,attrelid,attnum,'SELECT') AS owner_read,
                pg_catalog.has_column_privilege(:owner,attrelid,attnum,'UPDATE') AS owner_update,
                pg_catalog.has_column_privilege(current_user,attrelid,attnum,'UPDATE') AS app_update
                FROM pg_catalog.pg_attribute WHERE attrelid=:oid AND attnum>0 AND NOT attisdropped'''),
                {'owner':OWNER,'oid':table['oid']}).mappings().all()
            expected={'id','equipment_id'} if table['relname']=='work_order' else {'id','sources'}
            if ({c['attname'] for c in columns if c['owner_read']}!=expected or
                {c['attname'] for c in columns if c['owner_update']}!={'id'} or any(c['app_update'] for c in columns)):
                raise CaptureError('source column privileges incompatible')
        functions=s.execute(text('''SELECT p.oid,CASE WHEN pg_catalog.octet_length(p.prosrc)<=8192 THEN p.prosrc ELSE NULL END AS prosrc,p.proowner,p.prosecdef,p.provolatile,p.proisstrict,
            p.proleakproof,p.proparallel,p.proconfig,p.prorettype,p.pronargs,p.proargtypes::text AS args,l.lanname
            FROM pg_catalog.pg_proc p JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace
            JOIN pg_catalog.pg_language l ON l.oid=p.prolang
            WHERE n.nspname=:schema AND p.proname=:name LIMIT 2'''),{'schema':self.schema,'name':FUNCTION}).mappings().all()
        if len(functions)!=1:raise CaptureError('source lock helper missing or overloaded')
        f=functions[0]
        if f['prosrc'] is None:raise CaptureError('source lock helper body budget')
        body=f['prosrc'].replace(self.db.engine.dialect.identifier_preparer.quote(self.schema)+'.','CAPTURE_SCHEMA.')
        if (hashlib.sha256(body.encode()).hexdigest()!=BODY_SHA256 or f['proowner']!=owner['oid'] or
            not f['prosecdef'] or f['provolatile']!='v' or f['proisstrict'] or f['proleakproof'] or
            f['proparallel']!='u' or f['proconfig']!=['search_path=pg_catalog, pg_temp'] or
            f['prorettype']!=2278 or f['pronargs']!=3 or f['args']!='25 25 25' or f['lanname']!='plpgsql'):
            raise CaptureError('source lock helper definition drift')
        acl=s.execute(text('''SELECT a.grantee,a.grantor,a.privilege_type,a.is_grantable FROM pg_catalog.pg_proc p,
            LATERAL pg_catalog.aclexplode(COALESCE(p.proacl,pg_catalog.acldefault('f',p.proowner))) a WHERE p.oid=:oid'''),{'oid':f['oid']}).all()
        if set(tuple(r) for r in acl)!={(owner['oid'],owner['oid'],'EXECUTE',False),(app['oid'],owner['oid'],'EXECUTE',False)}:
            raise CaptureError('source lock helper ACL drift')

    def lock(self,s,domain,source_id,equipment_id):
        self.verify(s)  # Check capability again on the actual target transaction.
        try:
            s.execute(text(f'SELECT {self.qualified}(CAST(:domain AS text),CAST(:source AS text),CAST(:equipment AS text))'),
                {'domain':domain,'source':source_id,'equipment':equipment_id})
        except SQLAlchemyError:
            raise CaptureError('source lock refused') from None
