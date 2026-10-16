"""Deterministic qualification negatives; never connect to external databases."""
import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
import yaml
TOOLS=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,TOOLS/(name+'.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

class CoverageCiTest(unittest.TestCase):
    def invoke(self,body=None,component='contracts'):
        with tempfile.TemporaryDirectory(prefix='nadi-b4-negative-') as name:
            root=Path(name);tests=root/'reliability-data-contracts/tests';tests.mkdir(parents=True)
            if body is not None: (tests/'test_negative.py').write_text('import unittest\n'+body)
            report=root/'result.json'
            run=subprocess.run([sys.executable,str(TOOLS/'run_offline.py'),'--root',str(root),
                '--component',component,'--sha','a'*40,'--report',str(report)],capture_output=True,
                env={k:v for k,v in os.environ.items() if k not in ('GH_TOKEN','GITHUB_STEP_SUMMARY')},timeout=30)
            return run.returncode,json.loads(report.read_text())

    def test_empty_suite_fails(self): self.assertNotEqual(self.invoke()[0],0)
    def test_unavailable_cockpit_suite_fails(self): self.assertNotEqual(self.invoke(component='cockpit')[0],0)
    def test_skipped_suite_fails(self):
        code,r=self.invoke('class T(unittest.TestCase):\n @unittest.skip("synthetic unavailable")\n def test_x(self): pass\n')
        self.assertNotEqual(code,0);self.assertEqual(r['skips'],1)
    def test_failed_suite_fails(self):
        code,r=self.invoke('class T(unittest.TestCase):\n def test_x(self): self.fail("synthetic")\n')
        self.assertNotEqual(code,0);self.assertEqual(r['failures'],1)
    def test_network_attempt_fails_even_if_exception_caught(self):
        code,r=self.invoke('class T(unittest.TestCase):\n def test_x(self):\n  import socket\n  with self.assertRaises(AssertionError): socket.create_connection(("127.0.0.1",9))\n')
        self.assertNotEqual(code,0);self.assertGreater(r['blocked_external_io'],0)
    def test_unapproved_subprocess_fails(self):
        code,r=self.invoke('class T(unittest.TestCase):\n def test_x(self):\n  import subprocess\n  with self.assertRaises(AssertionError): subprocess.run(["echo","forbidden"])\n')
        self.assertNotEqual(code,0);self.assertGreater(r['blocked_external_io'],0)
    def test_unapproved_database_fails_before_connection(self):
        code,r=self.invoke('class T(unittest.TestCase):\n def test_x(self):\n  from sqlalchemy import create_engine\n  with self.assertRaises(AssertionError): create_engine("postgresql+psycopg://x@127.0.0.1/no").connect()\n')
        self.assertNotEqual(code,0);self.assertGreater(r['blocked_external_io'],0)
    def test_only_private_fixture_socket_and_roles_allowed(self):
        m=module('pg_worker');ctx={'socket':'/tmp/private/socket','port':16480}
        good=dict(host=ctx['socket'],port=16480,dbname='nadi_b4_disposable',user='nadi_b4_reader')
        self.assertTrue(m.connection_allowed(good,ctx))
        for change in ({'host':'127.0.0.1'},{'dbname':'nadi_live_dev_test'},{'user':'postgres'},
                       {'port':5432},{'password':'forbidden'},{'hostaddr':'127.0.0.1'},{'service':'fallback'},{'options':'unapproved'},{'context':'not-an-adapters-map'}):
            with self.subTest(change=change): self.assertFalse(m.connection_allowed(good|change,ctx))
    def test_independent_identity_mismatch_refused(self):
        m=module('run_pg');ctx={'directory':'/tmp/private','system_id':'123'}
        good=['/tmp/private/data','123','','nadi_b4_disposable','nadi_b4_fixture']
        self.assertTrue(m.validate_identity(ctx,*good))
        for i,value in enumerate(('/other/data','different','*','operational','other')):
            args=good[:];args[i]=value
            self.assertFalse(m.validate_identity(ctx,*args))
    def test_cross_component_lane_is_required_and_read_only(self):
        path=TOOLS.parents[1]/'workflows/nadi-maximo-collector.yml'
        workflow=yaml.load(path.read_text(),Loader=yaml.BaseLoader);job=workflow['jobs']['coverage']
        self.assertEqual(job['strategy']['matrix']['python'],['3.11','3.12'])
        self.assertIn('coverage',workflow['jobs']['gate']['needs'])
        self.assertNotIn('services',job)
        self.assertNotIn('secrets.',path.read_text());self.assertNotIn('continue-on-error',path.read_text())
        self.assertFalse(any('GH_TOKEN' in step.get('env',{}) for step in job['steps']))
        gate=next(s for s in workflow['jobs']['gate']['steps'] if 'COVERAGE_RESULT' in s.get('env',{}))
        for value in ('failure','skipped','cancelled',''):
            run=subprocess.run(['bash','-e','-c',gate['run']],capture_output=True,timeout=5,
                env={'SELECTION_RESULT':'success','COLLECTOR_RESULT':'success','POSTGRES_RESULT':'success','COVERAGE_RESULT':value,'INTEGRATED_RESULT':'success','SOURCE_LOCK_RESULT':'success'})
            self.assertNotEqual(run.returncode,0)
