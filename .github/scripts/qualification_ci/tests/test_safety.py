"""B5 offline CI protections; no database or runtime service access."""
import hashlib,importlib.util,json,os,subprocess,unittest
from pathlib import Path
import yaml
TOOLS=Path(__file__).resolve().parents[1]
ROOT=TOOLS.parents[2]
def module(name):
    spec=importlib.util.spec_from_file_location('b5_'+name,TOOLS/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class B5SafetyTest(unittest.TestCase):
    def test_migration_bytes_match_manifest(self):
        manifest=json.loads((ROOT/'maximo-collector/docs/NADI-AUD-02B-B5-MIGRATIONS.json').read_text())
        self.assertEqual([x['file'][:3] for x in manifest['order']],['001','002','003','004','005','006'])
        for x in manifest['order']:self.assertEqual(hashlib.sha256((ROOT/'maximo-collector/migrations'/x['file']).read_bytes()).hexdigest(),x['sha256'])
    def test_private_connection_allowlist(self):
        m=module('pg_worker');ctx={'socket':'/tmp/private/socket','port':16481}
        good=dict(host=ctx['socket'],port=16481,dbname='nadi_b5_disposable',user='nadi_b5_projector')
        self.assertTrue(m.connection_allowed(good,ctx))
        for change in ({'dbname':'nadi_live_dev_test'},{'dbname':'nadi_b5_restored'},{'host':'127.0.0.1'},{'user':'postgres'},{'password':'no'},{'service':'fallback'},{'options':'unreviewed'}):self.assertFalse(m.connection_allowed(good|change,ctx))
    def test_role_allowlist_is_not_administrative_fallback(self):
        m=module('pg_worker');ctx={'socket':'/tmp/private/socket','port':16481}
        for user in ('nadi_b5_fixture','nadi_b5_reader','nadi_b5_migrator','nadi_b5_source','nadi_b5_projector'):
            self.assertTrue(m.connection_allowed(dict(host=ctx['socket'],port=16481,dbname='nadi_b5_disposable',user=user),ctx))
        self.assertFalse(m.connection_allowed(dict(host=ctx['socket'],port=16481,dbname='nadi_b5_disposable',user='nadi_b4_fixture'),ctx))
    def test_independent_identity_and_socket(self):
        m=module('run_pg');ctx={'directory':'/tmp/private','system_id':'123'}
        args=['/tmp/private/data','123','','nadi_b5_disposable','nadi_b5_fixture']
        self.assertTrue(m.validate_identity(ctx,*args))
        for i,v in enumerate(('/other/data','bad','127.0.0.1','maximo_collector','postgres')):
            changed=args[:];changed[i]=v;self.assertFalse(m.validate_identity(ctx,*changed))
    def test_integrated_lane_required_and_no_tokens(self):
        workflow=yaml.load((ROOT/'.github/workflows/nadi-maximo-collector.yml').read_text(),Loader=yaml.BaseLoader)
        self.assertIn('integrated',workflow['jobs']['gate']['needs'])
        self.assertEqual(workflow['jobs']['integrated']['strategy']['matrix']['python'],['3.11','3.12'])
        self.assertFalse(any('GH_TOKEN' in s.get('env',{}) for s in workflow['jobs']['integrated']['steps']))
        gate=next(s for s in workflow['jobs']['gate']['steps'] if 'INTEGRATED_RESULT' in s.get('env',{}))
        for value in ('failure','skipped','cancelled',''):
            env={k:'success' for k in ('SELECTION_RESULT','COLLECTOR_RESULT','POSTGRES_RESULT','COVERAGE_RESULT')};env['INTEGRATED_RESULT']=value
            self.assertNotEqual(subprocess.run(['bash','-e','-c',gate['run']],env=env,capture_output=True,timeout=5).returncode,0)
    def test_child_environment_drops_private_values(self):
        m=module('run_pg')
        old=dict(os.environ)
        try:
            os.environ.update(DATABASE_URL='do-not-copy',PGSERVICE='do-not-copy',GH_TOKEN='do-not-copy',MAXIMO_PASSWORD='do-not-copy')
            self.assertFalse(set(m.clean_environment()) & {'DATABASE_URL','PGSERVICE','GH_TOKEN','MAXIMO_PASSWORD'})
        finally:os.environ.clear();os.environ.update(old)
