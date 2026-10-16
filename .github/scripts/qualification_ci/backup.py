"""Backup/restore ONLY of the parent-created disposable cluster and fixed DBs."""
import hashlib,json,subprocess
from pathlib import Path
import psycopg
from psycopg import sql


def fingerprints(connection,schemas):
    result={}
    connection.execute("SET statement_timeout='10000ms'")
    for schema in schemas:
        tables=connection.execute("SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename",(schema,)).fetchall()
        for (table,) in tables:
            digest=hashlib.sha256();count=0
            query=sql.SQL('SELECT to_jsonb(t)::text FROM {}.{} t ORDER BY to_jsonb(t)::text').format(sql.Identifier(schema),sql.Identifier(table))
            with connection.cursor(name='b5_verify') as cursor:
                cursor.execute(query)
                while rows:=cursor.fetchmany(256):
                    for (row,) in rows:digest.update(row.encode()+b'\n');count+=1
            result[schema+'.'+table]={'rows':count,'sha256':digest.hexdigest()}
    return result


def qualify_restore(bindir,context,env):
    work=Path(context['directory']).resolve();data=work/'data'
    assert work.parent==Path('/tmp') and work.name.startswith('nadi-b5-pg-')
    args=dict(host=context['socket'],port=context['port'],user='nadi_b5_fixture',dbname='nadi_b5_disposable')
    scenarios=json.loads((work/'scenarios.json').read_text())
    schemas=[scenarios[k]['schema'] for k in ('partial','targeted','final')]
    with psycopg.connect(**args) as c:
        assert Path(c.execute('SHOW data_directory').fetchone()[0]).resolve()==data
        assert c.execute('SELECT system_identifier::text FROM pg_control_system()').fetchone()[0]==context['system_id']
        assert c.execute('SHOW listen_addresses').fetchone()[0]==''
        before=fingerprints(c,schemas)
    backup=work/'synthetic-evidence.dump'
    with (work/'backup.log').open('a') as log:
        subprocess.run([str(bindir/'pg_dump'),'-h',args['host'],'-p',str(args['port']),'-U',args['user'],'-d',args['dbname'],
            '-Fc','--no-owner','--no-acl',*[part for schema in schemas for part in ('-n',schema)],'-f',str(backup)],
            env=env,stdout=log,stderr=log,timeout=45,check=True)
        backup.chmod(0o600)
        assert backup.stat().st_size>0
        subprocess.run([str(bindir/'pg_restore'),'--list',str(backup)],env=env,stdout=log,stderr=log,timeout=15,check=True)
        with psycopg.connect(**(args|{'dbname':'postgres'}),autocommit=True) as c:
            c.execute('CREATE DATABASE nadi_b5_restored OWNER nadi_b5_fixture')
        subprocess.run([str(bindir/'pg_restore'),'-h',args['host'],'-p',str(args['port']),'-U',args['user'],
            '-d','nadi_b5_restored','--no-owner','--no-acl','--single-transaction','--exit-on-error',str(backup)],
            env=env,stdout=log,stderr=log,timeout=45,check=True)
    with psycopg.connect(**(args|{'dbname':'nadi_b5_restored'})) as c: after=fingerprints(c,schemas)
    assert before==after,'restored evidence differs'
    (work/'restore-fingerprints.json').write_text(json.dumps(before,indent=2)+'\n')
    return dict(conclusion='PASS',schemas=len(schemas),tables=len(before),rows=sum(v['rows'] for v in before.values()),
                backup_sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),backup_bytes=backup.stat().st_size,
                scope='three synthetic checkpoint schemas; separate destination DB; no live restore')
