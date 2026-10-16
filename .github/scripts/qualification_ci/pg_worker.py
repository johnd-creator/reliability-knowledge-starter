"""Separate component interpreter. Guards before candidate imports or discovery."""
import argparse,contextlib,json,os,re,sys,unittest
from pathlib import Path
from unittest.mock import patch

def connection_allowed(parsed,context):
    from psycopg.adapt import AdaptersMap
    return (parsed.get('host')==context['socket'] and str(parsed.get('port'))==str(context['port'])
        and parsed.get('dbname')=='nadi_b5_disposable' and parsed.get('user') in ('nadi_b5_fixture','nadi_b5_reader','nadi_b5_projector','nadi_b5_source','nadi_b5_migrator')
        and set(parsed)<=set(('host','port','dbname','user','connect_timeout','context'))
        and ('context' not in parsed or isinstance(parsed['context'],AdaptersMap)))

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--context',type=Path,required=True);p.add_argument('--phase',choices=('prepare','read'),required=True)
    a=p.parse_args();ctx=json.loads(a.context.read_text());source=a.source.resolve();blocked=[]
    def deny(kind): blocked.append(kind);raise AssertionError('UNEXPECTED_EXTERNAL_IO:'+kind)
    import psycopg
    private=Path(ctx['directory']).resolve()
    if (private!=a.context.resolve().parent or private.parent!=Path('/tmp') or
            not private.name.startswith('nadi-b5-pg-') or private.stat().st_uid!=os.getuid() or
            private.stat().st_mode & 0o077 or Path(ctx['socket']).resolve()!=private/'socket' or
            (private/'data').resolve().parent!=private or not re.fullmatch('[0-9a-f]{40}',ctx['sha'])):
        raise RuntimeError('UNVERIFIED_PRIVATE_CONTEXT')
    import resource
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    resource.setrlimit(resource.RLIMIT_AS,(1024*1024*1024,1024*1024*1024))
    original=psycopg.Connection.connect
    def connect(cls,conninfo='',**kwargs):
        if not connection_allowed(psycopg.conninfo.conninfo_to_dict(conninfo,**kwargs),ctx): return deny('postgresql')
        return original(conninfo,**kwargs)
    from sqlalchemy.engine import Engine
    from sqlalchemy.engine.url import URL
    old_engine=Engine.connect
    def engine(engine,*args,**kwargs):
        if (engine.url.drivername!='postgresql+psycopg' or engine.url.host is not None or
                engine.url.port is not None or set(engine.url.query)!={'host','port'}) or not connection_allowed(dict(
            host=engine.url.query.get('host'),port=engine.url.query.get('port'),dbname=engine.url.database,
            user=engine.url.username,**({'password':engine.url.password} if engine.url.password else {})),ctx):
            return deny('unapproved_engine')
        return old_engine(engine,*args,**kwargs)
    def audit(event,args):
        if event in ('socket.connect','socket.getaddrinfo','socket.sendto','socket.sendmsg','subprocess.Popen','os.system'): deny(event)
    url=URL.create('postgresql+psycopg',username='nadi_b5_fixture',database='nadi_b5_disposable',
        query={'host':ctx['socket'],'port':str(ctx['port'])})
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(psycopg.Connection,'connect',classmethod(connect)))
        stack.enter_context(patch.object(psycopg,'connect',lambda conninfo='',**kw:connect(None,conninfo,**kw)))
        stack.enter_context(patch.object(psycopg.AsyncConnection,'connect',lambda *a,**k:deny('async_pg')))
        stack.enter_context(patch.object(Engine,'connect',engine))
        stack.enter_context(patch('dotenv.load_dotenv',return_value=False))
        sys.addaudithook(audit)
        with psycopg.connect(host=ctx['socket'],port=ctx['port'],dbname='nadi_b5_disposable',user='nadi_b5_fixture') as c:
            assert c.execute('SELECT system_identifier::text FROM pg_control_system()').fetchone()[0]==ctx['system_id']
            assert Path(c.execute('SHOW data_directory').fetchone()[0]).resolve()==private/'data'
            assert c.execute('SHOW listen_addresses').fetchone()[0]==''
        if a.phase=='prepare':
            sys.path[:0]=[str(source/'maximo-collector'),str(source/'maximo-collector/tests_postgres')]
            sys.path.insert(0,str(source/'maximo-collector/tests_qualification_pg'))
            import qualification_writer
            scenarios=qualification_writer.qualify(url,source/'maximo-collector',private)
            (a.context.parent/'scenarios.json').write_text(json.dumps(scenarios))
            assert not blocked
            print('B5_SCENARIOS_PREPARED='+str(len(scenarios)))
            return 0
        sys.path[:0]=[str(source/'reliability-cockpit'),str(source/'reliability-cockpit/tests_coverage_pg'),str(source/'reliability-cockpit/tests_qualification_pg')]
        import fixture_context
        fixture_context.owner_url=url;fixture_context.reader_url=url.set(username='nadi_b5_reader')
        fixture_context.scenarios=json.loads((a.context.parent/'scenarios.json').read_text())
        fixture_context.identity=ctx
        # Recheck the private fixture identity, not only its conventional name.
        with psycopg.connect(host=ctx['socket'],port=ctx['port'],dbname='nadi_b5_disposable',user='nadi_b5_fixture') as c:
            assert c.execute('SELECT system_identifier::text FROM pg_control_system()').fetchone()[0]==ctx['system_id']
            assert Path(c.execute('SHOW data_directory').fetchone()[0]).resolve()==Path(ctx['directory'])/'data'
            assert c.execute('SHOW listen_addresses').fetchone()[0]==''
        from integrated_coverage import IntegratedCoverageTest
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(IntegratedCoverageTest)
        count=suite.countTestCases();result=unittest.TextTestRunner(verbosity=2).run(suite)
        success=result.wasSuccessful() and result.testsRun==count and count>0 and not result.skipped and not result.expectedFailures and not blocked
        output=dict(tests=result.testsRun,discovered=count,failures=len(result.failures),errors=len(result.errors),
                    skips=len(result.skipped),blocked_io=len(blocked),conclusion='PASS' if success else 'FAIL')
        (a.context.parent/'read-result.json').write_text(json.dumps(output))
        return 0 if success else 1
if __name__=='__main__':sys.exit(main())
