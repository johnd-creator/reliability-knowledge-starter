"""FIX-01 offline CI and helper-artifact guards. No external database access."""
import ast,hashlib,importlib.util,json,os,re,subprocess,unittest
from pathlib import Path
import yaml
TOOLS=Path(__file__).resolve().parents[1];ROOT=TOOLS.parents[2]
def module(name):
    spec=importlib.util.spec_from_file_location('lock_ci_'+name,TOOLS/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class LockCiTest(unittest.TestCase):
    def test_original_and_additive_migration_manifest(self):
        doc=ROOT/'maximo-collector/docs';old=json.loads((doc/'NADI-AUD-02B-B5-MIGRATIONS.json').read_text())
        new=json.loads((doc/'NADI-AUD-02B-B5-FIX-01-MIGRATIONS.json').read_text())
        self.assertEqual(hashlib.sha256((doc/'NADI-AUD-02B-B5-MIGRATIONS.json').read_bytes()).hexdigest(),new['unchanged_prior_manifest_sha256'])
        for row in [*old['order'],new['additive_migration']]:
            self.assertEqual(hashlib.sha256((ROOT/'maximo-collector/migrations'/row['file']).read_bytes()).hexdigest(),row['sha256'])
    def test_privileged_body_read_only_fixed_and_pinned(self):
        migration=(ROOT/'maximo-collector/migrations/007_restricted_source_lock_candidate.sql').read_text()
        body=migration.split('AS $body$',1)[1].split('$body$;',1)[0]
        self.assertNotRegex(body,r'\b(?:EXECUTE|INSERT|UPDATE|DELETE|TRUNCATE|GRANT|CREATE|ALTER|DROP)\b')
        self.assertEqual(body.count('FOR SHARE'),2)
        self.assertIn('%1$I.work_order',body);self.assertIn('%1$I.equipment',body)
        source=(ROOT/'maximo-collector/src/repositories/source_lock.py').read_text()
        digest=re.search(r"BODY_SHA256='([a-f0-9]{64})'",source).group(1)
        self.assertEqual(hashlib.sha256(body.replace('%1$I.','CAPTURE_SCHEMA.').encode()).hexdigest(),digest)
        self.assertIn('SET search_path=pg_catalog,pg_temp',migration)
        self.assertIn('FROM PUBLIC',migration)
    def test_bound_private_roles_only(self):
        m=module('pg_worker');ctx={'socket':'/tmp/private/socket','port':16482}
        good=dict(host=ctx['socket'],port=16482,dbname='nadi_lock_disposable',user='nadi_lock_projector')
        self.assertTrue(m.connection_allowed(good,ctx))
        for change in ({'user':'nadi_capture_lock_owner'},{'user':'postgres'},{'dbname':'nadi_live_dev_test'},
                       {'host':'127.0.0.1'},{'hostaddr':'127.0.0.1'},{'service':'other'},{'options':'other'},{'password':'other'}):
            self.assertFalse(m.connection_allowed(good|change,ctx))
    def test_cluster_identity_mismatch_fails(self):
        m=module('run_pg');ctx={'directory':'/tmp/private','system_id':'123'}
        good=['/tmp/private/data','123','','nadi_lock_disposable','nadi_lock_fixture']
        self.assertTrue(m.validate_identity(ctx,*good))
        for i,v in enumerate(('/other/data','bad','127.0.0.1','operational','postgres')):
            x=good[:];x[i]=v;self.assertFalse(m.validate_identity(ctx,*x))
    def test_required_lane_and_matrix(self):
        doc=yaml.load((ROOT/'.github/workflows/nadi-maximo-collector.yml').read_text(),Loader=yaml.BaseLoader)
        self.assertIn('source_lock',doc['jobs']['gate']['needs'])
        self.assertEqual(doc['jobs']['source_lock']['strategy']['matrix']['python'],['3.11','3.12'])
        gate=next(s for s in doc['jobs']['gate']['steps'] if 'SOURCE_LOCK_RESULT' in s.get('env',{}))
        for value in ('failure','skipped','cancelled',''):
            env={k:'success' for k in ('SELECTION_RESULT','COLLECTOR_RESULT','POSTGRES_RESULT','COVERAGE_RESULT','INTEGRATED_RESULT')};env['SOURCE_LOCK_RESULT']=value
            self.assertNotEqual(subprocess.run(['bash','-e','-c',gate['run']],env=env,capture_output=True,timeout=5).returncode,0)
    def test_no_token_in_candidate_job(self):
        doc=yaml.load((ROOT/'.github/workflows/nadi-maximo-collector.yml').read_text(),Loader=yaml.BaseLoader)
        job=doc['jobs']['source_lock'];self.assertNotIn('services',job)
        self.assertFalse(any('GH_TOKEN' in s.get('env',{}) for s in job['steps']))
        self.assertNotIn('continue-on-error',str(job));self.assertNotIn('secrets.',str(job))
    def test_environment_has_no_source_credentials(self):
        env=module('run_pg').clean_environment()
        self.assertFalse(set(env)&{'DATABASE_URL','PGSERVICE','PGHOST','MAXIMO_PASSWORD','GH_TOKEN'})
    def test_new_python_sources_parse(self):
        for path in ('maximo-collector/src/repositories/source_lock.py','maximo-collector/tests_source_lock_pg/source_lock_qualification.py'):
            ast.parse((ROOT/path).read_text(),path)
