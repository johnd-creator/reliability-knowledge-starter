"""Hermetic lifecycle simulations and Git identity tests; no live services/DB access."""
import importlib.util
import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

FILE=Path(__file__).resolve().parents[2]/'deploy/development/local_development.py'
spec=importlib.util.spec_from_file_location('reusable_local',FILE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
A='a'*40; B='b'*40; C='c'*40; D='d'*40

class ReusableTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
        self.root=self.base/'candidate';self.root.mkdir();self.state=self.base/'state';self.state.mkdir(mode=0o700)
        self.c=SimpleNamespace(STATE=self.state,BASE=self.base,ROOT=self.root,
            UNITS=('api','web'),LEGACY_WEB='legacy',ORIGIN='https://localhost:3000',NAME='isolated',
            stop_unit=Mock(),primary_busy=Mock(return_value=False),run=Mock(),active=Mock(return_value=False))
        def write(path,data):
            with Path(path).open('x') as f:
                os.chmod(path,0o600);f.write(data)
        self.c.write_private=write;self.d=m.LocalDevelopment(self.c);self.d.state.mkdir(mode=0o700)
        self.old={'before':{'web':{},'api':{}},'root':str(self.root),'sha':A,'workflow_sha':A,'config_path':str(self.d.state/'config.json')}
        self.d.save('config.json',{'source_root':str(self.root),'workflow_sha':A,'application_dsn':'not-used'})
        self.d.save('active.json',self.old)

    def tearDown(self):self.temp.cleanup()
    def denied(self,code,call):
        with self.assertRaises(RuntimeError) as e:call()
        self.assertEqual(str(e.exception),code)
    def simulate(self,sha):
        def preflight(*args):return {'root':str(self.root),'sha':sha,'workflow_sha':B,
                                    'previous':dict(self.d.active_value(),before={'web':{},'api':{}}),'config_path':self.old['config_path']}
        def backup(v,token):v.update(backup='private-dump',backup_sha256='verified',backup_created=1)
        self.d.preflight=Mock(side_effect=preflight);self.d.backup=Mock(side_effect=backup)
        self.d.validate_recovery=Mock();self.d.start_pair=Mock();self.d.wait_ready=Mock(return_value={})
        self.d.attest=Mock()
        self.d.owners=Mock(return_value={})
        with patch.object(m,'source',return_value=self.root):
            self.d.select(self.root,sha)
        self.assertEqual(self.d.active_value()['sha'],sha)
    def test_initial_second_third_selection_retains_unique_history(self):
        for sha in [B,C,D]:self.simulate(sha)
        for suffix in ['requested','prepared','stopping','accepted']:
            paths=list(self.d.state.glob('selection-*-'+suffix+'.json'));self.assertEqual(len(paths),3)
        accepted=[json.loads(p.read_text()) for p in self.d.state.glob('*-accepted.json')]
        self.assertEqual({(v['before'],v['after']) for v in accepted},{(A,B),(B,C),(C,D)})
        self.assertEqual(len({v['id'] for v in accepted}),3)
    def test_legacy_transition_file_is_preserved_without_blocking(self):
        self.d.save('transition.json',{'state':'HISTORICAL'});self.simulate(B)
        self.assertEqual(json.loads((self.d.state/'transition.json').read_text()),{'state':'HISTORICAL'})
    def test_failed_preflight_history_and_active_pointer_preserved(self):
        self.d.preflight=Mock(side_effect=RuntimeError('REJECTED'))
        before=(self.d.state/'active.json').read_bytes()
        self.denied('REJECTED',lambda:self.d.select(self.root,B))
        self.assertEqual((self.d.state/'active.json').read_bytes(),before)
        self.assertEqual(len(list(self.d.state.glob('*-failed.json'))),1)
        self.simulate(C)
        self.assertEqual(len(list(self.d.state.glob('*-failed.json'))),1)
        self.c.stop_unit.assert_called() # only successful simulation
    def test_simultaneous_selection_rejected_and_recorded(self):
        with self.d.transaction():
            self.denied('DEVELOPMENT_LIFECYCLE_BUSY',lambda:self.d.select(self.root,B))
        self.c.stop_unit.assert_not_called()
        self.assertEqual(len(list(self.d.state.glob('*-failed.json'))),1)
    def test_failed_start_recovers_once_without_data_restore_or_retry(self):
        self.simulate(B);previous=self.d.active_value();self.c.stop_unit.reset_mock()
        self.d.start_pair=Mock(side_effect=RuntimeError('FAILED_START'))
        self.d._recover=Mock()
        with patch.object(m,'source',return_value=self.root):
            self.denied('FAILED_START',lambda:self.d.select(self.root,C))
        self.d.start_pair.assert_called_once();self.d._recover.assert_called_once()
        self.assertEqual(self.d.active_value(),previous)
        self.assertTrue(list(self.d.state.glob('*-prepared.json')))
    def test_failed_recovery_does_not_publish_candidate(self):
        self.simulate(B);previous=self.d.active_value()
        self.d.start_pair=Mock(side_effect=RuntimeError('START_FAIL'))
        self.d._recover=Mock(side_effect=RuntimeError('RECOVERY_FAIL'))
        with patch.object(m,'source',return_value=self.root):
            self.denied('RECOVERY_FAIL',lambda:self.d.select(self.root,C))
        self.assertEqual(self.d.active_value(),previous)
        self.assertEqual(len(list(self.d.state.glob('*-failed.json'))),1)
    def test_explicit_rollback_preserves_data_and_republishes_previous(self):
        self.simulate(B);value=self.d.active_value();self.d.readiness=Mock()
        self.d.recover(value)
        self.assertEqual(self.d.active_value()['sha'],A)
        evidence=json.loads(next(self.d.state.glob('rollback-*-recovered.json')).read_text())
        self.assertFalse(evidence['data_restored_or_deleted'])
    def test_changed_active_pointer_rejects_rollback(self):
        self.simulate(B);value=self.d.active_value();self.d.replace('active.json',self.old)
        self.c.stop_unit.reset_mock()
        self.denied('ACTIVE_SELECTION_CHANGED',lambda:self.d.recover(value))
        self.c.stop_unit.assert_not_called()
    def test_stale_backup_rejected_before_command(self):
        p=self.d.state/'backup-test.dump';p.write_bytes(b'x'*1001);p.chmod(0o600)
        with patch.object(m.subprocess,'run') as run:
            self.denied('FRESH_PRIVATE_BACKUP_REQUIRED',lambda:self.d.validate_backup(
                {'backup':str(p),'backup_created':time.time()-3601,'backup_sha256':m.digest(p)}))
            run.assert_not_called()
    def test_backup_replacement_rejected(self):
        p=self.d.state/'backup-test.dump';p.write_bytes(b'x'*1001);p.chmod(0o600)
        self.denied('FRESH_PRIVATE_BACKUP_REQUIRED',lambda:self.d.validate_backup(
            {'backup':str(p),'backup_created':time.time(),'backup_sha256':'wrong'}))
    def test_contract_difference_rejected(self):
        with patch.object(m,'output',side_effect=['old','changed']):
            with self.assertRaisesRegex(RuntimeError,'FIXTURE_CONTRACT_CHANGE_REQUIRES_SEPARATE_APPROVAL'):
                self.d.fixture_contract(self.old,self.root,B)
        self.c.stop_unit.assert_not_called()
    def test_contract_same_object_evidence(self):
        with patch.object(m,'output',return_value='tree'):
            self.assertEqual(len(self.d.fixture_contract(self.old,self.root,B)),64)
    def test_explicit_ref_and_head_must_match(self):
        with patch.object(m,'output',side_effect=[B,C]):
            self.denied('EXACT_REVIEWED_SOURCE_REQUIRED',lambda:self.d.resolve(self.root,'feature'))
    def test_missing_or_option_ref_rejected(self):
        for ref in [None,'','--all','x\nHEAD']:
            self.denied('EXPLICIT_REVIEWED_REF_REQUIRED',lambda:self.d.resolve(self.root,ref))
    def test_missing_listener_owner_rejected(self):
        self.d.unit=Mock(return_value={'WorkingDirectory':str(self.root)})
        with patch.object(m,'output',return_value='LISTEN 0 1 127.0.0.1:3000 *:* ino:5'):
            self.denied('UNVERIFIED_LISTENER_OWNER',lambda:self.d.owners('web',self.root,3000))
    def test_active_status_preserves_dirty_reporting_and_allows_backend_child_reload(self):
        value=dict(self.old,node='/node22',expected_api_parent={'parent':'same'})
        self.d.owners=Mock(side_effect=[{'listeners':{'1':{'exe':'/node22'}}}, {'listeners':{'2':{'exe':str((self.state/'python-runtime/bin/python').resolve())}}}])
        self.d.unit=Mock(return_value={'parent':'same'})
        backend={'source':'SYNTHETIC_LOCAL_DEVELOPMENT','database':'DISPOSABLE_TEST','environment':'DEVELOPMENT','source_sha':A,'current_sha':A,'bootstrap_sha':A,'database_identity':m.DB}
        front={'sha':A,'backend_sha':A,'launched_sha':A,'stale':False,'dirty':True,
               'database_identity':m.DB,'backend':'AVAILABLE','factual_backend':'AVAILABLE','engineering':True}
        self.d.release=Mock(return_value=A);self.d.auth_readiness=Mock(return_value={'authorized_session':'NOT_PROBED_NO_SESSION'})
        front={'contract':'NADI_LOCAL_TRANSPORT_V1','origin':self.c.ORIGIN,'guard':'SERVER_SESSION_AUTHORITY','frontend_sha':A,'launched_sha':A,'dirty':True}
        backend['engineering']=True
        self.d.request=Mock(side_effect=[backend,front,{'status':'READY','authentication':'LOCAL_SESSION_AUTHORITY'},{'status':'ok'}])
        with patch.object(m,'source',return_value=self.root):
            self.assertTrue(self.d.readiness(value)['dirty'])
        self.assertEqual(self.d.owners.call_count,2)
    def test_mismatched_backend_rejected(self):
        value=dict(self.old,node='/node22');self.d.owners=Mock(side_effect=[{'listeners':{'1':{'exe':'/node22'}}}, {'listeners':{'2':{'exe':str((self.state/'python-runtime/bin/python').resolve())}}}])
        self.d.release=Mock(return_value=A)
        self.d.request=Mock(side_effect=[{'source_sha':C},{'contract':'NADI_LOCAL_TRANSPORT_V1','origin':self.c.ORIGIN,'guard':'SERVER_SESSION_AUTHORITY','frontend_sha':A,'launched_sha':A,'dirty':True},{'status':'READY','authentication':'LOCAL_SESSION_AUTHORITY'},{'status':'ok'}])
        with patch.object(m,'source',return_value=self.root):
            self.denied('LOCAL_PAIR_NOT_READY',lambda:self.d.readiness(value))
    def test_real_git_ref_repository_and_dirty_rejection(self):
        def git(*args):return subprocess.check_output(['git',*args],cwd=self.root,text=True,stderr=subprocess.DEVNULL).strip()
        git('init');git('config','user.name','Hermetic Test');git('config','user.email','test@example.invalid')
        git('remote','add','origin','https://github.com/johnd-creator/reliability-knowledge-starter.git')
        (self.root/'file').write_text('initial');git('add','file');git('commit','-m','fixture')
        head=git('rev-parse','HEAD');self.assertEqual(self.d.resolve(self.root,'HEAD'),(self.root,head))
        (self.root/'file').write_text('unsaved')
        self.denied('INITIAL_CLEAN_SOURCE_REQUIRED',lambda:self.d.resolve(self.root,'HEAD'))
        self.assertEqual((self.root/'file').read_text(),'unsaved')
        git('remote','set-url','origin','https://example.invalid/untrusted.git')
        self.denied('UNTRUSTED_SOURCE_REPOSITORY',lambda:self.d.repository(self.root))
    def test_command_surface_has_no_automatic_fixture_creation_or_migration(self):
        import ast
        tree=ast.parse(FILE.read_text());names={n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
        self.assertNotIn('create_fixture',names)
        for forbidden in ['CREATE DATABASE','CREATE ROLE','TRUNCATE','DROP TABLE','pg_restore --clean']:
            self.assertNotIn(forbidden,FILE.read_text())
        fixture=(FILE.parent/'local_fixture.py').read_text()
        entry=fixture[fixture.index("if __name__ == '__main__':"):]
        self.assertNotIn('prepare()',entry);self.assertIn('compatibility()',entry)

    def test_foreign_common_repository_rejected(self):
        with patch.object(m,'output',side_effect=['/other/.git','/trusted/.git']):
            self.denied('UNRELATED_SOURCE_REPOSITORY',lambda:self.d.repository(self.root))
    def test_listener_pid_reuse_during_observation_rejected(self):
        self.d.unit=Mock(return_value={'WorkingDirectory':str(self.root),'ControlGroup':'/owned'})
        self.d.identity=Mock(side_effect=[{'cwd':str(self.root),'cgroup':'/owned','start_ticks':1},
                                         {'cwd':str(self.root),'cgroup':'/owned','start_ticks':2}])
        with patch.object(m,'output',return_value='LISTEN 0 1 127.0.0.1:3000 *:* users:(("node",pid=123,fd=9)) ino:5'):
            self.denied('LISTENER_IDENTITY_CHANGED',lambda:self.d.owners('web',self.root,3000))
    def test_unit_replacement_during_observation_rejected(self):
        self.d.unit=Mock(side_effect=[{'WorkingDirectory':str(self.root),'ControlGroup':'/owned'},{}])
        self.d.identity=Mock(return_value={'cwd':str(self.root),'cgroup':'/owned'})
        with patch.object(m,'output',return_value='LISTEN 0 1 127.0.0.1:3000 *:* users:(("node",pid=123,fd=9)) ino:5'):
            self.denied('DEVELOPMENT_UNIT_CHANGED_DURING_OBSERVATION',lambda:self.d.owners('web',self.root,3000))
    def test_changed_recovery_unit_does_not_stop_either_process(self):
        value={'root':str(self.root),'previous':dict(self.old)}
        self.d.validate_recovery=Mock();self.c.active.return_value=True
        self.d.unit=Mock(side_effect=[{'WorkingDirectory':str(self.root/'reliability-cockpit/web')},
                                     {'WorkingDirectory':'/foreign'}])
        self.d.owners=Mock(return_value={})
        self.denied('UNEXPECTED_RECOVERY_UNIT_OWNER',lambda:self.d._recover(value,'test'))
        self.c.stop_unit.assert_not_called()
    def test_invalid_recovery_archive_never_stops_process(self):
        self.simulate(B);value=self.d.active_value();self.c.stop_unit.reset_mock()
        self.d.validate_recovery=Mock(side_effect=RuntimeError('BACKUP_UNREADABLE'))
        self.denied('BACKUP_UNREADABLE',lambda:self.d._recover(value,'test'))
        self.c.stop_unit.assert_not_called()
    def test_unreviewed_release_manifest_rejected(self):
        with patch.object(m,'private',return_value={'files':{},'source_sha':A}):
            self.denied('UNREVIEWED_LOCAL_CONTROLLER_RELEASE',self.d.release)
    def test_fixture_probe_has_exact_readonly_command_and_isolated_environment(self):
        value=dict(self.old)
        with patch.object(m,'output',return_value='{"database":"nadi_local_dev_01_test"}') as run:
            self.assertEqual(self.d.fixture_probe(value)['database'],m.DB)
            args=run.call_args.args[0]
            self.assertIn('-i',args);self.assertEqual(args[-1],'--check')
            self.assertIn('NADI_LOCAL_DEV_ACK='+m.DB,args)
            self.assertNotIn('--prepare',args)
            self.assertFalse(any('RELIABILITY_MART' in str(a) for a in args))
    def test_preserved_configuration_not_overwritten_on_selection(self):
        original=(self.d.state/'config.json').read_bytes();self.simulate(B)
        self.assertEqual((self.d.state/'config.json').read_bytes(),original)
        config=json.loads(Path(self.d.active_value()['config_path']).read_text())
        self.assertEqual(config['source_root'],str(self.root))
    def test_start_pair_uses_selected_sha_same_ports_and_reload_without_creation(self):
        value=dict(self.old,node='/node22');self.d.start=Mock()
        self.d.start_pair(value)
        api,web=self.d.start.call_args_list
        self.assertIn('--reload',api.args[2]);self.assertIn('13036',api.args[2])
        self.assertIn('3000',web.args[2]);self.assertEqual(web.args[2][0],'/node22')
        self.assertIn('NADI_DEV_LAUNCHED_SHA='+A,web.args[3])
        self.assertIn('NADI_LOCAL_DEV_CONFIG='+value['config_path'],api.args[3])
    def test_record_failure_does_not_write_active_pointer(self):
        self.d.preflight=Mock(side_effect=RuntimeError('INCOMPATIBLE'))
        self.denied('INCOMPATIBLE',lambda:self.d.select(self.root,B))
        self.c.stop_unit.assert_not_called();self.c.run.assert_not_called()
        self.assertEqual(self.d.active_value(),self.old)

class FixtureCompatibilityTest(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('checked_fixture',FILE.parent/'local_fixture.py')
        self.fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.fixture)
    def test_dsn_rejects_operational_or_other_store(self):
        for dsn in ['postgresql://nadi_local_dev_01:secret@127.0.0.1:15443/nadi_live_dev_test',
                    'postgresql://nadi_local_dev_01:secret@remote:15443/nadi_local_dev_01_test',
                    'postgresql://superuser:secret@127.0.0.1:15443/nadi_local_dev_01_test',
                    'sqlite:///fixture.db']:
            with self.assertRaisesRegex(RuntimeError,'LOCAL_FIXTURE_IDENTITY_REQUIRED'):
                self.fixture.checked({'application_dsn':dsn})
    def test_schema_probe_is_readonly_and_no_initialization(self):
        from unittest.mock import MagicMock
        engine=MagicMock();connection=engine.connect.return_value.__enter__.return_value
        connection.execute.side_effect=[None,[('nadi_human_record','kind','varchar','NO',None)], [('kind_check','approved')]]
        migrator=Mock();migrator.status.return_value=[{'name':'migration','checksum':'sha','status':'APPLIED'}]
        with patch.object(self.fixture,'load',return_value={}),patch.object(self.fixture,'engine_for',return_value=engine),\
             patch('src.repositories.application_migrations.ApplicationMigrator',return_value=migrator),\
             patch('src.repositories.qa_advisory_schema.qa_advisory_schema_ready',return_value=True):
            result=self.fixture.compatibility()
        self.assertEqual(result['database'],m.DB);self.assertEqual(len(result['schema_sha256']),64)
        migrator.apply.assert_not_called();engine.dispose.assert_called_once()
        commands=[str(call.args[0]) for call in connection.execute.call_args_list]
        self.assertEqual(commands[0],'SET TRANSACTION READ ONLY')
        self.assertTrue(all(s.startswith(('SELECT','SET TRANSACTION READ ONLY')) for s in commands))
    def test_pending_migration_and_advisory_schema_drift_fail_closed(self):
        from unittest.mock import MagicMock
        for pending,ready,code in [(True,True,'EXPLICIT_FIXTURE_PREPARATION_REQUIRED'),
                                   (False,False,'ADVISORY_ACK_SCHEMA_REQUIRED')]:
            engine=MagicMock();migrator=Mock();migrator.status.return_value=[{'status':'PENDING' if pending else 'APPLIED'}]
            with patch.object(self.fixture,'load',return_value={}),patch.object(self.fixture,'engine_for',return_value=engine),\
                 patch('src.repositories.application_migrations.ApplicationMigrator',return_value=migrator),\
                 patch('src.repositories.qa_advisory_schema.qa_advisory_schema_ready',return_value=ready):
                with self.assertRaisesRegex(RuntimeError,code):self.fixture.compatibility()
            migrator.apply.assert_not_called();engine.dispose.assert_called_once()


class PreflightBoundaryTest(unittest.TestCase):
    setUp=ReusableTest.setUp
    tearDown=ReusableTest.tearDown
    def test_previous_provenance_uses_actual_frontend_status_contract(self):
        value=dict(self.old);self.d.readiness=Mock(return_value={'engineering_data':'SYNTHETIC_FIXTURES'})
        self.d.repository=Mock();self.d.owners=Mock(return_value={})
        with patch.object(m,'source',return_value=self.root),patch.object(m,'old_source',return_value='generated'):
            previous=self.d.previous()
        self.assertEqual(previous['config_path'],self.old['config_path'])
        self.assertEqual(previous['generated_hash'],'generated')
    def test_complete_preflight_composes_same_source_pair_and_fixture_checks(self):
        web=self.root/'reliability-cockpit/web';(web/'node_modules/next/dist/bin').mkdir(parents=True)
        (web/'node_modules/next/dist/bin/next').touch();(web/'node_modules/.package-lock.json').write_text('locked')
        for name in ['localhost.pem','localhost.key']:
            (self.state/name).write_text('private');(self.state/name).chmod(0o600)
        self.d.save('accounts.json',{'synthetic':'no real identity'})
        config={'source_root':str(self.root),'accounts_file':str(self.d.state/'accounts.json')}
        self.d.replace('config.json',config)
        self.d.release=Mock(return_value=B);self.d.resolve=Mock(return_value=(self.root,B))
        self.d.previous=Mock(return_value=self.old);self.d.fixture_contract=Mock(return_value='fixture-contract')
        self.d.fixture_probe=Mock(return_value={'database':m.DB,'ledger':'applied'})
        self.c.db=Mock(return_value={'Id':'existing-container','State':{'Running':True},
            'NetworkSettings':{'Ports':{'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':'15443'}]}}})
        # No external command is executed: the existing contract comparator receives mocked Git objects.
        def command(args,**kwargs):return '{}' if 'show' in args else 'git-tree-object'
        with patch.object(m,'node_pin',return_value='/node22'),patch.object(m,'output',return_value=''),             patch.object(m.subprocess,'check_output',side_effect=command):
            result=self.d.preflight(self.root,B)
        self.assertEqual(result['sha'],B);self.assertEqual(result['backend_sha'],B)
        self.assertEqual(result['fixture']['database'],m.DB)
        self.assertEqual(len(result['pair_contract']),64)
        self.c.stop_unit.assert_not_called();self.c.run.assert_not_called()
