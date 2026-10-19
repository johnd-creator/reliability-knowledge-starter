"""Portable manual rehearsal guards; no PostgreSQL or external I/O."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]

def module(name):
 spec=importlib.util.spec_from_file_location('manual_'+name,TOOLS/(name+'.py'))
 result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
 return result

class F03RestoreSafetyTest(unittest.TestCase):
 def setUp(self):
  self.runner=module('f03_restore_rehearsal')
  self.worker=module('f03_restore_coverage_worker')
  self.temp=tempfile.TemporaryDirectory(prefix='nadi-f03-restore-test-',dir='/tmp')
  self.addCleanup(self.temp.cleanup)
  self.work=Path(self.temp.name);self.work.chmod(0o700)
  self.context=self.work/'context.json';self.context.write_text('{}');self.context.chmod(0o600)
  self.source=self.work/'source';self.source.mkdir()
  self.ctx={'item':{'directory':str(self.work),'socket':str(self.work/'socket'),'port':16521,'system_id':'123'},'component':str(self.source/'reliability-cockpit'),'schema':'lock_sql_synthetic','output':str(self.work/'out.json')}

 def test_import_has_no_database_process_or_fixture_side_effect(self):
  with patch('subprocess.run') as run,patch('subprocess.check_output') as output,patch('tempfile.mkdtemp') as create:
   module('f03_restore_rehearsal');module('f03_restore_coverage_worker')
  run.assert_not_called();output.assert_not_called();create.assert_not_called()

 def test_cli_requires_explicit_source_exact_sha_and_report(self):
  good=['--source',str(self.source),'--sha','a'*40,'--report',str(self.work/'report.json')]
  parsed=self.runner.parse_arguments(good)
  self.assertEqual(parsed.pg_bindir,Path('/usr/lib/postgresql/16/bin'))
  for args in ([],good[:2],good[:-2],['--source',str(self.source),'--sha','main','--report',str(self.work/'report.json')],good+['--dsn','postgresql://unapproved']):
   with self.subTest(args=args),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):self.runner.parse_arguments(args)

 def test_explicit_trusted_binary_directory_is_preserved(self):
  args=self.runner.parse_arguments(['--source',str(self.source),'--sha','b'*40,'--report',str(self.work/'report.json'),'--pg-bindir',str(self.work/'tools')])
  self.assertEqual(args.pg_bindir,self.work/'tools')

 def test_worker_accepts_only_requested_component_and_private_output(self):
  self.worker.validate_context(self.ctx,self.context,self.source)
  for change in ({'component':str(self.work/'different/reliability-cockpit')},{'output':str(self.work.parent/'escaped.json')},{'schema':'public;SELECT 1'}):
   with self.subTest(change=change),self.assertRaises(ValueError):self.worker.validate_context(self.ctx|change,self.context,self.source)

 def test_worker_refuses_nonprivate_context_or_fixture(self):
  self.context.chmod(0o644)
  with self.assertRaises(ValueError):self.worker.validate_context(self.ctx,self.context,self.source)
  self.context.chmod(0o600);self.work.chmod(0o755)
  with self.assertRaises(ValueError):self.worker.validate_context(self.ctx,self.context,self.source)

 def test_worker_refuses_host_socket_port_and_identity_changes(self):
  for change in ({'directory':'/var/lib/postgresql'},{'socket':'/var/run/postgresql'},{'port':5432},{'system_id':'unverified'}):
   with self.subTest(change=change),self.assertRaises((ValueError,FileNotFoundError)):
    self.worker.validate_context(self.ctx|{'item':self.ctx['item']|change},self.context,self.source)

 def test_direct_class_and_async_connectors_share_strict_fixture_guard(self):
  import psycopg
  endpoint=('/tmp/owned-fixture/socket',16521)
  good={'host':endpoint[0],'port':endpoint[1],'dbname':'nadi_lock_disposable','user':'nadi_lock_reader'}
  marker=object()
  with patch.object(psycopg.Connection,'connect',return_value=marker) as original:
   with self.runner.guard_postgres([endpoint],('nadi_lock_reader',),('nadi_lock_disposable',)) as blocked:
    for connector in (psycopg.connect,psycopg.Connection.connect):
     self.assertIs(connector(**good),marker)
     changes=({'host':'192.0.2.1'},{'hostaddr':'192.0.2.1'},{'service':'unapproved'},{'password':'synthetic'},{'options':'-c search_path=public'},{'dbname':'active'},{'user':'postgres'},{'context':object()})
     for change in changes:
      with self.subTest(connector=connector,change=change),self.assertRaises(AssertionError):connector(**(good|change))
     with self.assertRaises(AssertionError):connector('host=192.0.2.1 dbname=active user=postgres')
    with self.assertRaises(AssertionError):psycopg.AsyncConnection.connect(**good)
   self.assertEqual(original.call_count,2)  # Only both approved mocked calls.
   self.assertEqual(len(blocked),19)

 def test_early_preflight_and_initdb_failure_keep_structured_report(self):
  import json
  for startup in (False,True):
   with self.subTest(startup=startup):
    paths=[self.work/('early-'+str(startup)),self.work/('cluster-'+str(startup))]
    for path in paths:path.mkdir(mode=0o700)
    report=self.work/('failure-'+str(startup)+'.json')
    replies=['c'*40,' M synthetic',*['tool (PostgreSQL) 16.14']*5]
    failure=RuntimeError('synthetic failure before guarded source imports')
    with patch.object(self.runner.tempfile,'mkdtemp',side_effect=[str(p) for p in paths]), \
         patch.object(self.runner.subprocess,'check_output',side_effect=replies if startup else failure), \
         patch.object(self.runner.subprocess,'run',side_effect=failure) as run, \
         contextlib.redirect_stdout(io.StringIO()):
     code=self.runner.main(['--source',str(TOOLS.parents[2]),'--sha','c'*40,'--report',str(report)])
    result=json.loads(report.read_text())
    self.assertEqual(code,1)
    self.assertEqual((result['conclusion'],result['error_type'],result['blocked_postgres_io']),('FAIL','RuntimeError',0))
    if startup:
     self.assertEqual(result['cleanup'][0]['cleanup'],'NOT_STARTED')
     self.assertIsNone(result['cleanup'][0]['cleanup_error'])
     self.assertEqual(run.call_count,1)
    else:
     self.assertEqual(result['cleanup'],[])
     run.assert_not_called()

 def test_caught_external_attempt_is_still_recorded(self):
  import psycopg
  with patch.object(psycopg.Connection,'connect') as original:
   with self.runner.guard_postgres([('/tmp/owned/socket',16521)],('fixture',),('fixture',)) as blocked:
    try:psycopg.connect('host=192.0.2.1 dbname=active user=postgres')
    except AssertionError:pass
   self.assertEqual(blocked,['unapproved connection'])
   original.assert_not_called()

if __name__=='__main__':unittest.main()
