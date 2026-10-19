"""Manual synthetic two-cluster PostgreSQL16.14 restore rehearsal.

No input DSN, active database, operational credentials or workflow invocation.
Preserves the reviewed v2 rehearsal; explicit CLI paths replace host-specific paths.
Private synthetic archives/logs are retained. Not operational F03 acceptance.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parent
STACK_PROVENANCE='952160cca72724e456b5a4e092301f5e475143e3'

def parse_arguments(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--sha',required=True,help='Expected exact source Git HEAD; dirty sources are labeled separately')
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--pg-bindir',type=Path,default=Path('/usr/lib/postgresql/16/bin'),help='Explicit trusted local PostgreSQL16.14 binary directory')
    args=parser.parse_args(argv)
    if not re.fullmatch('[0-9a-f]{40}',args.sha):parser.error('exact lowercase 40-character SHA required')
    if not args.source.is_dir():parser.error('existing source repository directory required')
    if not args.report.parent.is_dir():parser.error('explicit report parent directory must exist')
    return args

def connection_allowed(parsed,endpoints,users,databases):
    from psycopg.adapt import AdaptersMap
    return (set(parsed)<=set(('host','port','user','dbname','connect_timeout','context')) and
        any(parsed.get('host')==host and str(parsed.get('port'))==str(port) for host,port in endpoints) and
        parsed.get('user') in users and parsed.get('dbname') in databases and
        ('context' not in parsed or isinstance(parsed['context'],AdaptersMap)))

@contextlib.contextmanager
def guard_postgres(endpoints,users,databases):
    """Guard module alias AND class connector; libpq bypasses Python socket hooks."""
    import psycopg
    original=psycopg.Connection.connect
    blocked=[]
    def deny(kind):
        blocked.append(kind)
        raise AssertionError('unexpected PostgreSQL I/O:'+kind)
    def guarded(cls,conninfo='',**kwargs):
        if not connection_allowed(psycopg.conninfo.conninfo_to_dict(conninfo,**kwargs),endpoints,users,databases):
            return deny('unapproved connection')
        return original(conninfo,**kwargs)
    with patch.object(psycopg.Connection,'connect',classmethod(guarded)), \
         patch.object(psycopg,'connect',lambda conninfo='',**kwargs:guarded(None,conninfo,**kwargs)), \
         patch.object(psycopg.AsyncConnection,'connect',lambda *args,**kwargs:deny('async connection')):
        yield blocked

def main(argv=None):
    args=parse_arguments(argv)
    SOURCE=args.source.resolve();SHA=args.sha;REPORT=args.report.resolve();BINDIR=args.pg_bindir.resolve()
    sys.dont_write_bytecode=True
    ROLES=['nadi_lock_fixture','nadi_capture_lock_owner','nadi_lock_projector','nadi_lock_source','nadi_lock_reader','nadi_lock_migrator']
    DB='nadi_lock_disposable'
    PREFIX='nadi-f03-restore-'
    for key in tuple(os.environ):
        if key.startswith(('PG','MAXIMO_','NADI_','RELIABILITY_','COCKPIT_')) or key.endswith(('_DSN','_TOKEN','_PASSWORD','_SECRET')) or key in ('DATABASE_URL','GH_TOKEN'):
            os.environ.pop(key)
    os.environ['PYTHON_DOTENV_DISABLED']='1'
    sys.path.insert(0,str(TOOLS.parent/'maximo_ci'))
    from owned_cluster import OwnedCluster
    import psycopg
    from psycopg import sql
    from sqlalchemy.engine import URL
    from sqlalchemy import text,select
    from sqlalchemy.exc import DBAPIError

    work=Path(tempfile.mkdtemp(prefix=PREFIX,dir='/tmp'));work.chmod(0o700)
    env={k:os.environ[k] for k in ('PATH','LANG','LC_ALL') if k in os.environ}
    env.update(PATH=str(BINDIR)+':'+env.get('PATH','/usr/bin'),HOME=str(work),PYTHON_DOTENV_DISABLED='1',PYTHONDONTWRITEBYTECODE='1',LC_ALL='C')
    commands=[];clusters=[];connections=[];fixtures=[];blocked_io=[];result={'requested_source_head':SHA,'tested_source':'uncommitted_publication_candidate','stack_provenance_sha':STACK_PROVENANCE,'scope':'synthetic two independent clusters; no active-system backup or restore; no operational acceptance','private_directory':str(work)}

    def command(tool,*args,output=None):
        words=[str(BINDIR/tool),*map(str,args)]
        commands.append(words)
        with (work/'commands.json').open('w') as out:json.dump(commands,out,indent=2)
        with (work/'commands.log').open('a') as log:
            if output:
                with Path(output).open('wb') as out:subprocess.run(words,env=env,stdout=out,stderr=log,timeout=60,check=True)
                Path(output).chmod(0o600)
            else:subprocess.run(words,env=env,stdout=log,stderr=log,timeout=60,check=True)


    def new_cluster(name,owner,port):
        private=Path(tempfile.mkdtemp(prefix=PREFIX+name+'-',dir='/tmp'));private.chmod(0o700)
        (private/'socket').mkdir(mode=0o700)
        item={'directory':str(private),'owner':owner,'port':port,'socket':str(private/'socket')}
        cluster=OwnedCluster(private,BINDIR,env,PREFIX)
        clusters.append((cluster,item))
        command('initdb','-D',cluster.data,'--no-locale','--encoding=UTF8','-A','trust','-U',owner)
        cluster.before_start()
        command('pg_ctl','-D',cluster.data,'-l',private/'postgres.log','-w','start','-o',f"-h '' -k {private/'socket'} -p {port} -c max_connections=12 -c shared_buffers=32MB -c fsync=on")
        with connect(item,'postgres',owner) as c:
            assert Path(c.execute('SHOW data_directory').fetchone()[0]).resolve()==cluster.data
            assert c.execute('SHOW listen_addresses').fetchone()[0]==''
            item['system_id']=c.execute('SELECT system_identifier::text FROM pg_control_system()').fetchone()[0]
            assert item['system_id']==cluster.identity[1]
            item['server_version']=c.execute('SHOW server_version').fetchone()[0]
            assert c.execute('SHOW server_version_num').fetchone()[0]=='160014','manual restore qualification requires PostgreSQL16.14'
        return item


    def connect(item,dbname=DB,user='nadi_lock_fixture',**kwargs):
        assert any(item is owned for _,owned in clusters)
        assert dbname in ('postgres',DB) and user in ROLES+['nadi_restore_bootstrap']
        if set(kwargs)-{'autocommit'} or not isinstance(kwargs.get('autocommit',False),bool):
            raise ValueError('unreviewed fixture connection option')
        connection=psycopg.connect(host=item['socket'],port=item['port'],user=user,dbname=dbname,connect_timeout=3)
        connection.autocommit=kwargs.get('autocommit',False)
        return connection


    def query(c,statement,params=None):
        with c.cursor() as cursor:
            cursor.execute(statement,params)
            return [dict(zip([d.name for d in cursor.description],row)) for row in cursor.fetchall()]


    def acl(expr,owner,kind):
        return f"COALESCE((SELECT jsonb_agg(jsonb_build_array(CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,pg_get_userbyid(a.grantor),a.privilege_type,a.is_grantable) ORDER BY CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,pg_get_userbyid(a.grantor),a.privilege_type,a.is_grantable) FROM aclexplode(COALESCE({expr},acldefault('{kind}',{owner}))) a),'[]'::jsonb)"


    def catalog(item,schemas):
        with connect(item) as c:
            c.execute("SET statement_timeout='10000ms'")
            n={'schemas':schemas,'roles':ROLES,'db':DB}
            tables="n.nspname=ANY(%(schemas)s)"
            out={
              'roles':query(c,"SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolconnlimit,rolvaliduntil::text,rolbypassrls,rolconfig FROM pg_roles WHERE rolname=ANY(%(roles)s) ORDER BY rolname",n),
              'memberships':query(c,"SELECT pg_get_userbyid(roleid) AS role,pg_get_userbyid(member) AS member,pg_get_userbyid(grantor) AS grantor,admin_option,inherit_option,set_option FROM pg_auth_members WHERE pg_get_userbyid(roleid)=ANY(%(roles)s) OR pg_get_userbyid(member)=ANY(%(roles)s) ORDER BY 1,2,3",n),
              'database':query(c,"SELECT datname,pg_get_userbyid(datdba) AS owner,encoding,datcollate,datctype,datlocprovider,datallowconn,datconnlimit,"+acl('datacl','datdba','d')+" AS acl FROM pg_database WHERE datname=%(db)s",n),
              'schemas':query(c,"SELECT nspname,pg_get_userbyid(nspowner) AS owner,"+acl('nspacl','nspowner','n')+" AS acl FROM pg_namespace WHERE nspname=ANY(%(schemas)s) ORDER BY nspname",n),
              'relations':query(c,"SELECT n.nspname,c.relname,c.relkind,pg_get_userbyid(c.relowner) AS owner,c.relrowsecurity,c.relforcerowsecurity,c.relreplident,c.reloptions,"+acl('c.relacl','c.relowner','r')+" AS acl FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE "+tables+" AND c.relkind IN ('r','p','v','m','S','f') ORDER BY 1,2",n),
              'columns':query(c,"SELECT n.nspname,c.relname,a.attname,format_type(a.atttypid,a.atttypmod) AS type,a.attnotnull,a.attidentity,a.attgenerated,pg_get_expr(d.adbin,d.adrelid) AS default_value,COALESCE((SELECT jsonb_agg(jsonb_build_array(CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END,pg_get_userbyid(x.grantor),x.privilege_type,x.is_grantable) ORDER BY x.grantee::regrole::text,x.grantor::regrole::text,x.privilege_type) FROM aclexplode(a.attacl) x),'[]'::jsonb) AS acl FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE "+tables+" AND a.attnum>0 AND NOT a.attisdropped AND c.relkind IN ('r','p','v','m','S','f') ORDER BY 1,2,a.attnum",n),
              'functions':query(c,"SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid) AS arguments,pg_get_userbyid(p.proowner) AS owner,p.prosecdef,p.provolatile,p.proisstrict,p.proleakproof,p.proparallel,p.proconfig,pg_get_functiondef(p.oid) AS definition,"+acl('p.proacl','p.proowner','f')+" AS acl FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE "+tables+" ORDER BY 1,2,3",n),
              'constraints':query(c,"SELECT n.nspname,c.relname,k.conname,k.contype,k.condeferrable,k.condeferred,k.convalidated,pg_get_constraintdef(k.oid) AS definition FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE "+tables+" ORDER BY 1,2,3",n),
              'indexes':query(c,"SELECT n.nspname,c.relname,i.relname AS index_name,x.indisunique,x.indisprimary,x.indisvalid,x.indisready,pg_get_indexdef(x.indexrelid) AS definition FROM pg_index x JOIN pg_class c ON c.oid=x.indrelid JOIN pg_class i ON i.oid=x.indexrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE "+tables+" ORDER BY 1,2,3",n),
              'triggers':query(c,"SELECT n.nspname,c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid) AS definition FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE "+tables+" AND NOT t.tgisinternal ORDER BY 1,2,3",n),
              'default_acls':query(c,"SELECT pg_get_userbyid(d.defaclrole) AS role,n.nspname,d.defaclobjtype,d.defaclacl::text FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname=ANY(%(schemas)s) OR pg_get_userbyid(d.defaclrole)=ANY(%(roles)s) ORDER BY 1,2,3",n),
              'sequences':query(c,"SELECT * FROM pg_sequences WHERE schemaname=ANY(%(schemas)s) ORDER BY schemaname,sequencename",n),
            }
            return out


    def coverage(item,schema,name,version_override=None):
        output=work/(name+'-coverage.json')
        context=work/(name+'-context.json')
        context.write_text(json.dumps({'item':item,'schema':schema,'component':str(SOURCE/'reliability-cockpit'),'output':str(output),'reported_version_override':version_override}));context.chmod(0o600)
        words=[sys.executable,str(TOOLS/'f03_restore_coverage_worker.py'),str(context),'--source',str(SOURCE)]
        commands.append(words)
        with (work/'coverage.log').open('a') as log:subprocess.run(words,env=env,stdout=log,stderr=log,timeout=30,check=True)
        return json.loads(output.read_text())


    def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest()


    def rows(item,schemas):
        with connect(item) as c:return backup.fingerprints(c,schemas)


    def save(name,value):
        path=work/name;path.write_text(json.dumps(value,indent=2,default=str)+'\n');path.chmod(0o600)


    try:
        actual=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip()
        assert actual==SHA,'unexpected source Git HEAD'
        dirty=subprocess.check_output(['git','-C',str(SOURCE),'status','--porcelain','--untracked-files=normal'],text=True).strip()
        result['tested_source']='uncommitted_publication_candidate' if dirty else 'exact_git_head'
        result['source_head']=actual
        result['postgres_tool_versions']={tool:subprocess.check_output([str(BINDIR/tool),'--version'],env=env,text=True).strip() for tool in ('initdb','pg_ctl','pg_dump','pg_dumpall','pg_restore')}
        assert all(re.search(r'\b16\.14\b',version) for version in result['postgres_tool_versions'].values()),'manual restore qualification requires PostgreSQL16.14 tools'
        result['rehearsal_tools_sha256']={str(path.relative_to(TOOLS.parent)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (TOOLS/'f03_restore_rehearsal.py',TOOLS/'f03_restore_coverage_worker.py',TOOLS/'backup.py',TOOLS.parent/'maximo_ci/owned_cluster.py')}
        result['source_files_sha256']={name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() for name in ('maximo-collector/src/repositories/projection_store.py','maximo-collector/src/repositories/deferred_store.py','maximo-collector/src/repositories/replay_store.py','reliability-cockpit/src/repositories/projection_coverage.py')}
        result['cleanup_helper_sha256']=hashlib.sha256((TOOLS.parent/'maximo_ci/owned_cluster.py').read_bytes()).hexdigest()
        # No source credentials/config are loaded; libpq options were scrubbed above.
        source=new_cluster('source','nadi_lock_fixture',16521)
        target=new_cluster('target','nadi_restore_bootstrap',16522)
        assert source['system_id']!=target['system_id']
        result['clusters']=[source,target]
        with connect(source,'postgres',autocommit=True) as c:
            c.execute('CREATE DATABASE nadi_lock_disposable OWNER nadi_lock_fixture')
            for name in ('nadi_lock_projector','nadi_lock_source','nadi_lock_reader','nadi_lock_migrator'):
                c.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS').format(sql.Identifier(name)))
            c.execute('ALTER ROLE nadi_lock_reader SET default_transaction_read_only=on')
            c.execute('CREATE ROLE nadi_capture_lock_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS')
            c.execute('REVOKE CREATE,TEMPORARY ON DATABASE nadi_lock_disposable FROM PUBLIC')
        sys.path[:0]=[str(SOURCE/'maximo-collector'),str(SOURCE/'maximo-collector/tests_postgres'),str(SOURCE/'maximo-collector/tests_qualification_pg'),str(SOURCE/'maximo-collector/tests_source_lock_pg')]
        spec=importlib.util.spec_from_file_location('restore_backup',TOOLS/'backup.py')
        backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
        # Allow only our two exact Unix endpoints for every subsequent candidate import.
        def deny_network(event,args):
            if event in ('socket.connect','socket.getaddrinfo','socket.sendto','socket.sendmsg'):raise AssertionError('unexpected Python network I/O')
        sys.addaudithook(deny_network)
        with guard_postgres([(item['socket'],item['port']) for _,item in clusters],ROLES+['nadi_restore_bootstrap'],('postgres',DB)) as blocked_io,patch('dotenv.load_dotenv',return_value=False),patch('dotenv.main.load_dotenv',return_value=False):
            import source_lock_qualification as q
            from src.repositories.projection_store import CaptureError,ProjectionStore
            from src.services.projection_replay import ProjectionReplay
            q.URL=URL.create('postgresql+psycopg',username='nadi_lock_fixture',database=DB,query={'host':source['socket'],'port':str(source['port'])})
            q.ROOT=SOURCE/'maximo-collector';q.WORK=work
            fixture_variants={}
            for variant,sql_install in (('orm',False),('sql',True)):
                f=q.RestrictedFixture('two_cluster_restore_'+variant,sql_install=sql_install);fixtures.append(f)
                f.wo('BSR-HISTORIC','MISSING')
                ticket=f.store.capture('maintenance_event');f.store.process(ticket);f.store.register(ticket,f.current());f.store.release(ticket)
                original_run=f.store.inspect(ticket.run_id)
                f.asset('MISSING');f.capture('asset_master');f.finish()
                assert f.rows(q.rm.queue)[0]['phase']=='PENDING'
                f.original_ticket=ticket;f.original_run=original_run
                fixture_variants[variant]=f
            result['coverage_source']={name:coverage(source,fixture.schema,'source-'+name) for name,fixture in fixture_variants.items()}
            with connect(source) as c:schemas=[r[0] for r in c.execute("SELECT nspname FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname<>'information_schema' ORDER BY nspname")]
            source_catalog=catalog(source,schemas);source_rows=rows(source,schemas)
            save('source-catalog.json',source_catalog);save('source-rows.json',source_rows)
            globals_file=work/'synthetic-globals.sql';archive=work/'synthetic-full-database.dump'
            common=['-h',source['socket'],'-p',source['port'],'-U','nadi_lock_fixture']
            command('pg_dumpall',*common,'--globals-only','--no-role-passwords',output=globals_file)
            command('pg_dump',*common,'-d',DB,'-Fc','--create','-f',archive);archive.chmod(0o600)
            command('pg_restore','--list',archive,output=work/'archive-toc.txt')
            target_args=['-h',target['socket'],'-p',target['port'],'-U','nadi_restore_bootstrap']
            command('psql',*target_args,'-d','postgres','-v','ON_ERROR_STOP=1','-f',globals_file)
            command('pg_restore',*target_args,'-d','postgres','--create','--exit-on-error',archive)
            result['coverage_restored']={name:coverage(target,fixture.schema,'restored-'+name) for name,fixture in fixture_variants.items()}
            restored_catalog=catalog(target,schemas);restored_rows=rows(target,schemas)
            save('restored-catalog.json',restored_catalog);save('restored-rows.json',restored_rows)
            assert source_rows==restored_rows,'restored table data differs'
            catalog_equal=source_catalog==restored_catalog
            catalog_diffs={}
            for group in source_catalog:
                if source_catalog[group]!=restored_catalog[group]:
                    changes=[]
                    for before,after in zip(source_catalog[group],restored_catalog[group]):
                        if before!=after:changes.append({'identity':{k:before[k] for k in ('nspname','relname','conname','index_name') if k in before},'fields':{k:{'source':before.get(k),'restored':after.get(k)} for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}})
                    catalog_diffs[group]={'source_count':len(source_catalog[group]),'restored_count':len(restored_catalog[group]),'differences':changes}
            save('catalog-differences.json',catalog_diffs)
            assert set(catalog_diffs)<=set(('constraints','indexes')),'unreviewed metadata difference'
            result['restore']={'conclusion':'PASS_REVIEWED_DEPARSE_VARIANT','catalog_equal':catalog_equal,'different_catalog_groups':list(catalog_diffs),'schemas':len(schemas),'tables':len(source_rows),'rows':sum(x['rows'] for x in source_rows.values()),'row_digest':digest(source_rows),'catalog_digest':digest(source_catalog),'catalog_groups':{k:len(v) for k,v in source_catalog.items()},'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'globals_sha256':hashlib.sha256(globals_file.read_bytes()).hexdigest(),'credentials_scope':'no passwords created; --no-role-passwords; credentials not qualified'}
            # Restricted writers and read-only Cockpit both consume restored variants.
            q.URL=q.URL.set(query={'host':target['socket'],'port':str(target['port'])})
            result['functional']={}
            for variant,source_fixture in fixture_variants.items():
                r=q.RestrictedFixture.__new__(q.RestrictedFixture);r.schema=source_fixture.schema;r.cursor=source_fixture.cursor
                r.db=r.connection('nadi_lock_fixture');r.app=r.connection('nadi_lock_projector');r.writer=r.connection('nadi_lock_source');fixtures.append(r)
                r.store=r.fresh()
                source_pins={};restored_pins={}
                with source_fixture.db.session() as session:
                    source_pins={'deferred':q.ReplayStore._catalog_signature(session),'replay':q.ReplayStore._replay_catalog(session)}
                with r.db.session() as session:
                    restored_pins={'deferred':q.ReplayStore._catalog_signature(session),'replay':q.ReplayStore._replay_catalog(session)}
                outputs=ProjectionReplay(r.store,enabled=True).run('maintenance_event')
                assert len(outputs)==1 and outputs[0]['state']=='DONE',outputs
                assert r.rows(q.rm.queue)[0]['phase']=='DONE'
                assert any(v['state']=='RESOLVED' for v in r.rows(q.dm.version))
                assert r.store.inspect(source_fixture.original_ticket.run_id)==source_fixture.original_run
                assert r.cursors()==source_fixture.cursor
                denial=[]
                for statement in ('UPDATE work_order SET status=status','UPDATE equipment SET id=id','DELETE FROM work_order','TRUNCATE equipment','ALTER TABLE equipment DISABLE TRIGGER ALL','CREATE TABLE forbidden(x int)','CREATE TEMP TABLE forbidden(x int)','SET ROLE nadi_capture_lock_owner'):
                    try:
                        with r.app.engine.begin() as c:c.execute(text(statement))
                    except DBAPIError:denial.append(statement)
                    else:raise AssertionError('restricted mutation/admin unexpectedly allowed')
                after_replay=rows(target,schemas)
                for table in ('equipment','work_order','sync_cursor'):
                    assert after_replay[r.schema+'.'+table]==source_rows[r.schema+'.'+table]
                observed=coverage(target,r.schema,'replayed-'+variant)
                assert observed['snapshot']['capability']=='VERIFIED',observed
                domain=next(d for d in observed['snapshot']['domains'] if d['domain']=='maintenance_event')
                assert domain['latest']['state']=='PARTIAL' and domain['latest']['capture_mode']=='RECOVERY_BY_ID'
                assert domain['last_complete'] is None and not domain['proof_complete']
                assert domain['replay']['DONE']==1 and domain['debt']['outstanding']==0
                result['functional'][variant]={'restricted_replay':'DONE','old_evidence_preserved':True,'source_data_and_cursor_preserved':True,'denied_mutation_admin_actions':len(denial),'catalog_pins':{'source':source_pins,'restored':restored_pins},'coverage_after_replay':observed}
            baseline_catalog=catalog(target,schemas);baseline_rows=rows(target,schemas);negative=[]
            qualified=sql.Identifier(r.schema,'nadi_lock_source_exact')
            cases=[('helper_acl',sql.SQL('REVOKE EXECUTE ON FUNCTION {}(text,text,text) FROM nadi_lock_projector').format(qualified),sql.SQL('GRANT EXECUTE ON FUNCTION {}(text,text,text) TO nadi_lock_projector').format(qualified)),('helper_owner',sql.SQL('ALTER FUNCTION {}(text,text,text) OWNER TO nadi_lock_fixture').format(qualified),sql.SQL('ALTER FUNCTION {}(text,text,text) OWNER TO nadi_capture_lock_owner').format(qualified)),('guard_trigger',sql.SQL('ALTER TABLE {} DISABLE TRIGGER mart_capture_item_guard').format(sql.Identifier(r.schema,'mart_capture_item')),sql.SQL('ALTER TABLE {} ENABLE TRIGGER mart_capture_item_guard').format(sql.Identifier(r.schema,'mart_capture_item')))]
            for name,mutation,restore in cases:
                with connect(target,autocommit=True) as c:c.execute(mutation)
                try:
                    same_rows=rows(target,schemas)==baseline_rows
                    changed_catalog=catalog(target,schemas)!=baseline_catalog
                    refused=False
                    try:
                        if name=='guard_trigger':ProjectionStore(r.app,enabled=True,exclusive_writer=True)
                        else:
                            with r.app.session() as session:q.SourceLockBoundary(r.app,r.schema).verify(session)
                    except CaptureError:refused=True
                    assert same_rows and changed_catalog and refused,(name,same_rows,changed_catalog,refused)
                    negative.append({'case':name,'table_hash_unchanged':same_rows,'metadata_mismatch_detected':changed_catalog,'specific_guard_preflight_refused':refused,'guard_scope':'B1 trigger' if name=='guard_trigger' else 'source-lock helper'})
                finally:
                    with connect(target,autocommit=True) as c:c.execute(restore)
                assert catalog(target,schemas)==baseline_catalog,'negative-control metadata not restored'
            # Exact constraints/index variants must still reject real semantic drift.
            with connect(target) as c:
                enum_original=c.execute("SELECT pg_get_constraintdef(k.oid) FROM pg_constraint k JOIN pg_class t ON t.oid=k.conrelid JOIN pg_namespace n ON n.oid=t.relnamespace WHERE n.nspname=%s AND t.relname='mart_deferred_version' AND k.conname='deferred_state'",(r.schema,)).fetchone()[0]
                index_original=c.execute("SELECT indexdef FROM pg_indexes WHERE schemaname=%s AND indexname='deferred_one_active'",(r.schema,)).fetchone()[0]
                body_original=c.execute("SELECT pg_get_functiondef(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname=%s AND p.proname='mart_capture_item_guard'",(r.schema,)).fetchone()[0]
            table=sql.Identifier(r.schema,'mart_deferred_version');index=sql.Identifier(r.schema,'deferred_one_active')
            drop_enum=sql.SQL('ALTER TABLE {} DROP CONSTRAINT deferred_state').format(table)
            original_enum=sql.SQL('ALTER TABLE {} ADD CONSTRAINT deferred_state {}').format(table,sql.SQL(enum_original))
            changed_enum=sql.SQL("ALTER TABLE {} ADD CONSTRAINT deferred_state CHECK (state IN ('OPEN','ELIGIBLE_FOR_RETRY','BLOCKED_NEEDS_REVIEW','SUPERSEDED_BY_NEW_VERSION','RESOLVED','UNREVIEWED'))").format(table)
            drop_index=sql.SQL('DROP INDEX {}').format(index)
            index_nonunique=index_original.replace('CREATE UNIQUE INDEX','CREATE INDEX',1)
            index_columns=index_original.replace('(family_id)','(family_id, version)',1)
            index_predicate=index_original[:index_original.index(' WHERE ')] + " WHERE state='OPEN'"
            changed_body=sql.SQL('CREATE OR REPLACE FUNCTION {}() RETURNS trigger LANGUAGE plpgsql AS $$BEGIN RETURN NEW; END$$').format(sql.Identifier(r.schema,'mart_capture_item_guard'))
            semantic_cases=[('changed_enum',[drop_enum,changed_enum],[drop_enum,original_enum]),('changed_predicate',[drop_index,sql.SQL(index_predicate)],[drop_index,sql.SQL(index_original)]),('changed_uniqueness',[drop_index,sql.SQL(index_nonunique)],[drop_index,sql.SQL(index_original)]),('changed_index_columns',[drop_index,sql.SQL(index_columns)],[drop_index,sql.SQL(index_original)]),('changed_trigger_body',[changed_body],[sql.SQL(body_original)])]
            for name,changes,undo in semantic_cases:
                with connect(target) as c:
                    for statement in changes:c.execute(statement)
                try:
                    assert rows(target,schemas)==baseline_rows
                    assert catalog(target,schemas)!=baseline_catalog
                    refused=False
                    try:r.fresh()
                    except CaptureError:refused=True
                    assert refused,name+' writer accepted semantic catalog drift'
                    observed=coverage(target,r.schema,'negative-'+name)
                    assert observed['snapshot']['capability']=='BLOCKED',observed
                    reasons={reason for domain in observed['snapshot']['domains'] for reason in domain['reasons']}
                    assert 'CAPABILITY_DRIFT' in reasons
                    negative.append({'case':name,'table_hash_unchanged':True,'metadata_mismatch_detected':True,'restricted_writer_refused':True,'coverage_capability':'BLOCKED','coverage_reason':'CAPABILITY_DRIFT'})
                finally:
                    with connect(target) as c:
                        for statement in undo:c.execute(statement)
                assert catalog(target,schemas)==baseline_catalog
            # Test-only altered observed version reaches real query gate, not a
            # production caller flag and not a change to either PostgreSQL server.
            from sqlalchemy.orm import Session
            actual_scalar=Session.scalar
            version_refusals=[]
            for wrong_query in (1,2):
                observed_versions=[]
                def unqualified_version(session,statement,*args,**kwargs):
                    actual=actual_scalar(session,statement,*args,**kwargs)
                    if str(statement)=="SELECT current_setting('server_version_num')":
                        observed_versions.append(str(actual))
                        if len(observed_versions)==wrong_query:return '160015'
                    return actual
                version_refused=False
                failure_reason=None
                with patch.object(Session,'scalar',new=unqualified_version):
                    try:r.fresh()
                    except CaptureError as error:version_refused=True;failure_reason=str(error)
                assert version_refused and observed_versions==['160014']*wrong_query
                expected='deferred constraint/index definition drift' if wrong_query==1 else 'replay index/constraint/trigger drift'
                assert failure_reason==expected
                version_refusals.append({'gate':'B2' if wrong_query==1 else 'B3','actual_server_version_queries':observed_versions,'unqualified_observed_version':'160015','failure_reason':failure_reason})
            unknown_version=coverage(target,r.schema,'negative-wrong-observed-version',version_override='160015')
            assert unknown_version['snapshot']['capability']=='BLOCKED'
            assert any('CAPABILITY_DRIFT' in d['reasons'] for d in unknown_version['snapshot']['domains'])
            negative.append({'case':'wrong_observed_server_version','restricted_writer_refused':version_refused,'writer_query_gate_cases':version_refusals,'coverage_capability':'BLOCKED','actual_server_version_num':'160014','test_only_observed_version':'160015','no_server_configuration_change':True})
            # A real restored-source provenance change after sealed capture/reservation
            # must refuse without altering any committed target, receipt or raw input.
            r.wo('BSR-RESTORE-PROVENANCE','RESTOREPROV')
            deferred_ticket=r.store.capture('maintenance_event');r.store.process(deferred_ticket)
            family=next(row for row in r.rows(q.dm.family) if row['source_id']=='BSR-RESTORE-PROVENANCE')
            r.store.register(deferred_ticket,family['current_id']);r.store.release(deferred_ticket)
            r.asset('RESTOREPROV');r.capture('asset_master')
            provenance_ticket=r.store.claim_due('maintenance_event')
            assert provenance_ticket is not None
            assert r.store.capture_claim(provenance_ticket)['state']=='READY'
            assert r.store.reserve_attempt(provenance_ticket)
            assert r.store.inspect(provenance_ticket.run_id)['sealed']
            assert r.store.phase(provenance_ticket)['phase']=='WRITING'
            sealed_items=r.rows(q.pm.item)
            sealed_item=next(row for row in sealed_items if row['run_id']==provenance_ticket.run_id)
            assert sealed_item['source_id']=='BSR-RESTORE-PROVENANCE' and sealed_item['disposition'] is None
            before_provenance=rows(target,schemas)
            with r.writer.engine.connect() as c:
                original_sources=c.execute(text("SELECT sources FROM equipment WHERE id='RESTOREPROV'")).scalar_one()
            provenance_cases=[]
            for key in ('siteid','orgid'):
                changed=json.loads(json.dumps(original_sources));changed['maximo'][key]='UNREVIEWED'
                with r.writer.engine.begin() as c:
                    c.execute(text("UPDATE equipment SET sources=CAST(:sources AS jsonb) WHERE id='RESTOREPROV'"),{'sources':json.dumps(changed)})
                refused=False
                try:
                    try:r.store.process(provenance_ticket,max_items=1)
                    except CaptureError:refused=True
                    assert refused
                    assert r.rows(q.pm.item)==sealed_items,'sealed inputs/receipts changed'
                    after=rows(target,schemas)
                    assert {k:v for k,v in after.items() if k!=r.schema+'.equipment'}=={k:v for k,v in before_provenance.items() if k!=r.schema+'.equipment'}
                    assert r.store.phase(provenance_ticket)['phase']=='WRITING'
                    assert r.cursors()==r.cursor
                    provenance_cases.append({'changed_field':'Equipment.sources.maximo.'+key,'actual_post_restore_update':True,'restricted_process_refused':True,'sealed_raw_inputs_receipts_targets_and_ledger_preserved':True,'no_resolution_or_completion':True})
                finally:
                    with r.writer.engine.begin() as c:
                        c.execute(text("UPDATE equipment SET sources=CAST(:sources AS jsonb) WHERE id='RESTOREPROV'"),{'sources':json.dumps(original_sources)})
                assert rows(target,schemas)==before_provenance,'synthetic provenance restoration changed other evidence'
            result['restored_source_provenance_negative']={'sealed_reserved_claim_run':provenance_ticket.run_id,'cases':provenance_cases,'retained_input_fingerprint':sealed_item['fingerprint'],'original_input_payload_digest':digest(sealed_item['payload']),'final_table_hashes_equal_pre_drift':True,'source_cursor_unchanged':True}
            result['negative_controls']=negative
            assert rows(source,schemas)==source_rows and catalog(source,schemas)==source_catalog,'source cluster changed during target rehearsal'
            result['source_cluster_preserved']=True
            assert not blocked_io,'blocked external I/O attempt'
            result['blocked_postgres_io']=len(blocked_io)
            result['conclusion']='PASS'
    except Exception as error:
        result['conclusion']='FAIL';result['error_type']=type(error).__name__
        # Synthetic-only errors; keep bounded detail in private evidence, not credentials.
        (work/'failure.txt').write_text(type(error).__name__+': '+str(error)+'\n')
    finally:
        for fixture in fixtures:
            try:fixture.close()
            except Exception:pass
        result['cleanup']=[]
        for cluster,item in reversed(clusters):
            result['cleanup'].append({'directory':item['directory'],**cluster.cleanup()})
        if any(x['cleanup_error'] for x in result['cleanup']):result['conclusion']='FAIL'
        result['commands']=commands
        result['blocked_postgres_io']=len(blocked_io)
        result['limitations']=['Synthetic static logical backup, not PITR/WAL, physical volume restore, live concurrent backup or operational RTO/RPO acceptance.','No operational credentials, metadata, data, runtime, services or source systems were read or changed.','Independent global bootstrap role exists only on restored cluster and is excluded from source-role equivalence; all six restored source roles are compared.','Persistent access, source acquisition, F03 activation and acceptance are not authorized or performed.']
        REPORT.write_text(json.dumps(result,indent=2,default=str)+'\n');REPORT.chmod(0o600)
        print(json.dumps({k:v for k,v in result.items() if k not in ('commands',)},indent=2,default=str))
    return 0 if result.get('conclusion')=='PASS' else 1

if __name__=='__main__':
    sys.exit(main())
