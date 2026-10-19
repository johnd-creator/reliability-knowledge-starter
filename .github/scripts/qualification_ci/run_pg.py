"""Own Unix-only disposable B1-B5 qualification; no input DSN/runtime services."""
import argparse,json,os,platform,re,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'maximo_ci'))
from owned_cluster import OwnedCluster

def clean_environment():
    env={k:os.environ[k] for k in ('PATH','HOME','LANG','LC_ALL') if k in os.environ}
    env.update(PYTHON_DOTENV_DISABLED='1',COCKPIT_CONFIG_MODE='managed',PYTHONDONTWRITEBYTECODE='1')
    return env

def validate_identity(context,data,system_id,listen,database,user):
    return (Path(data).resolve()==Path(context['directory'])/'data' and str(system_id)==context['system_id']
            and listen=='' and database=='nadi_b5_disposable' and user=='nadi_b5_fixture')

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--sha',required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',a.sha): p.error('exact SHA required')
    source=a.source.resolve(); report=a.report.resolve(); env=clean_environment()
    work=Path(tempfile.mkdtemp(prefix='nadi-b5-pg-',dir='/tmp'));work.chmod(0o700)
    # Parent libpq must not inherit service/hostaddr/password options either.
    for key in tuple(os.environ):
        if key.startswith('PG'):os.environ.pop(key)
    env['HOME']=str(work)
    sock=work/'socket';sock.mkdir(mode=0o700); data=work/'data'
    bindir=Path(shutil.which('initdb') or '/usr/lib/postgresql/16/bin/initdb').parent
    result={}; context={};error=None
    cluster=OwnedCluster(work,bindir,env,'nadi-b5-pg-')
    def command(*args):
        with (work/'cluster.log').open('a') as log:
            subprocess.run([str(bindir/args[0]),*args[1:]],env=env,stdout=log,stderr=log,check=True,timeout=30)
    try:
        command('initdb','-D',str(data),'--no-locale','--encoding=UTF8','-A','trust','-U','nadi_b5_fixture')
        cluster.before_start()
        command('pg_ctl','-D',str(data),'-l',str(work/'postgres.log'),'-w','start','-o',
            f"-h '' -k {sock} -p 16481 -c max_connections=12 -c shared_buffers=32MB -c fsync=on")
        import psycopg
        args=dict(host=str(sock),port=16481,user='nadi_b5_fixture',dbname='postgres',connect_timeout=3)
        with psycopg.connect(**args,autocommit=True) as c:
            system_id=c.execute('SELECT system_identifier::text FROM pg_control_system()').fetchone()[0]
            assert Path(c.execute('SHOW data_directory').fetchone()[0]).resolve()==data
            assert c.execute('SHOW listen_addresses').fetchone()[0]==''
            disk=subprocess.check_output([str(bindir/'pg_controldata'),str(data)],env=env,text=True)
            assert system_id in disk
            c.execute('CREATE DATABASE nadi_b5_disposable OWNER nadi_b5_fixture')
            c.execute('CREATE ROLE nadi_b5_reader LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION')
            c.execute("ALTER ROLE nadi_b5_reader SET default_transaction_read_only=on")
            c.execute('CREATE ROLE nadi_capture_lock_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS')
            for role in ('nadi_b5_projector','nadi_b5_source','nadi_b5_migrator'):
                c.execute('CREATE ROLE '+role+' LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION')
            c.execute('REVOKE CREATE,TEMPORARY ON DATABASE nadi_b5_disposable FROM PUBLIC')
        context=dict(directory=str(work),socket=str(sock),port=16481,system_id=system_id,
            sha=a.sha,server_version=None,workflow_sha=os.getenv('CI_WORKFLOW_SHA','LOCAL_WORKTREE'),
            run_url=os.getenv('CI_RUN_URL','LOCAL_WORKTREE'))
        args['dbname']='nadi_b5_disposable'
        with psycopg.connect(**args) as c:
            context['server_version']=c.execute('SHOW server_version').fetchone()[0]
            assert validate_identity(context,c.execute('SHOW data_directory').fetchone()[0],
                c.execute('SELECT system_identifier::text FROM pg_control_system()').fetchone()[0],
                c.execute('SHOW listen_addresses').fetchone()[0],c.execute('SELECT current_database()').fetchone()[0],
                c.execute('SELECT current_user').fetchone()[0])
        path=work/'context.json';path.write_text(json.dumps(context));path.chmod(0o600)
        worker=Path(__file__).with_name('pg_worker.py')
        for phase in ('prepare','read'):
            proc=subprocess.run([sys.executable,str(worker),'--source',str(source),'--context',str(path),'--phase',phase],
                           env=env,check=phase=='prepare',timeout=300)
            if phase=='read' and proc.returncode and not (work/'read-result.json').exists():
                raise RuntimeError('reader qualification unavailable')
        result=json.loads((work/'read-result.json').read_text())
        result['prepare']=json.loads((work/'prepare-result.json').read_text())
        from backup import qualify_restore
        result['restore']=qualify_restore(bindir,context,env)
    except Exception as ex:
        error=type(ex).__name__  # No raw driver/credential text in result.
    finally:
        cleanup=cluster.cleanup()
    if (work/'prepare-result.json').exists():
        try:
            prepared=json.loads((work/'prepare-result.json').read_text())
            if not isinstance(prepared,dict):raise ValueError('prepare evidence object required')
            result['prepare']=prepared
        except Exception as ex:
            result.pop('prepare',None)
            result['prepare_evidence_error']=type(ex).__name__
            error=error or type(ex).__name__
    success=bool(not error and not cleanup['cleanup_error'] and result.get('conclusion')=='PASS' and result.get('prepare',{}).get('conclusion')=='PASS' and result.get('restore',{}).get('conclusion')=='PASS')
    output=dict(result,python=platform.python_version(),tested_sha=a.sha,fixture=context,
                **cleanup,infrastructure_error=error,
                conclusion='PASS' if success else 'FAIL')
    report.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
    summary=os.getenv('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a') as out: out.write('## B5 cross-component PostgreSQL\n\n```json\n'+json.dumps(output,indent=2)+'\n```\n')
    return 0 if success else 1
if __name__=='__main__': sys.exit(main())
