"""Local workflow safety checks. No service, Docker, network or database calls."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

FILE = Path(__file__).resolve().parents[2]/'deploy/development/local_development.py'
spec = importlib.util.spec_from_file_location('local_workflow', FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class LocalDevelopmentTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base/'source'
        self.root.mkdir()
        self.state = self.base/'state'
        self.state.mkdir()
        self.control = SimpleNamespace(STATE=self.state, BASE=self.base, ROOT=self.root,
            UNITS=('nadi-live-api.service','nadi-primary-web.service'), ORIGIN='https://localhost:3000',
            run=Mock(), stop_unit=Mock(), primary_busy=Mock(return_value=False), write_private=Mock())
        self.manager = m.LocalDevelopment(self.control)

    def tearDown(self):
        self.tmp.cleanup()

    def denied(self, code, action):
        with self.assertRaises(RuntimeError) as e: action()
        self.assertEqual(str(e.exception), code)

    def test_clean_selection_required_before_mutation(self):
        with patch.object(m,'output',side_effect=[m.SHA,' M application.py']):
            self.denied('INITIAL_CLEAN_SOURCE_REQUIRED', lambda:m.source(self.root,self.base,clean=True))
        self.control.stop_unit.assert_not_called()

    def test_dirty_files_permitted_only_during_active_development(self):
        with patch.object(m,'output',return_value=m.SHA):
            self.assertEqual(m.source(self.root,self.base,clean=False),self.root)

    def test_wrong_head_rejected(self):
        with patch.object(m,'output',return_value='f'*40):
            self.denied('EXACT_PR82_SOURCE_REQUIRED',lambda:m.source(self.root,self.base))

    def test_symlink_worktree_rejected(self):
        alias=self.base/'alias';alias.symlink_to(self.root)
        self.denied('EXCLUSIVE_MANAGED_SOURCE_REQUIRED',lambda:m.source(alias,self.base))

    def test_dotenv_is_not_inherited(self):
        web=self.root/'reliability-cockpit/web';web.mkdir(parents=True);(web/'.env.local').touch()
        with patch.object(m,'output',return_value=m.SHA):
            self.denied('UNREVIEWED_DOTENV_DENIED',lambda:m.source(self.root,self.base))

    def test_original_generated_file_exact_transform_only(self):
        name='reliability-cockpit/web/next-env.d.ts';path=self.root/name;path.parent.mkdir(parents=True)
        committed=b'/// <reference path="./.next/types/routes.d.ts" />\n'
        actual=committed.replace(b'./.next/',b'./.next-primary-dev/');path.write_bytes(actual)
        with patch.object(m,'output',side_effect=[m.SHA,name,'']),patch.object(m.subprocess,'check_output',return_value=committed):
            m.old_source(self.root,m.SHA)
        self.assertEqual(path.read_bytes(),actual)
        path.write_bytes(actual+b'// unrelated edit\n')
        with patch.object(m,'output',side_effect=[m.SHA,name,'']),patch.object(m.subprocess,'check_output',return_value=committed):
            self.denied('UNRELATED_GENERATED_EDIT',lambda:m.old_source(self.root,m.SHA))

    def test_unrelated_old_source_edit_blocks(self):
        with patch.object(m,'output',side_effect=[m.SHA,'other.ts','']):
            self.denied('UNRELATED_ROLLBACK_EDITS',lambda:m.old_source(self.root,m.SHA))

    def test_unknown_listener_is_rejected(self):
        self.manager.unit=Mock(return_value={'WorkingDirectory':str(self.root),'ControlGroup':'/owned'})
        self.manager.identity=Mock(return_value={'cwd':str(self.root),'cgroup':'/foreign'})
        with patch.object(m,'output',return_value='LISTEN 0 1 127.0.0.1:3000 0.0.0.0:* users:(("node",pid=123,fd=9)) ino:456'):
            self.denied('UNAUTHORIZED_LISTENER_OWNER',lambda:self.manager.owners('web',self.root,3000))

    def test_wildcard_listener_is_rejected(self):
        self.manager.unit=Mock(return_value={'WorkingDirectory':str(self.root),'ControlGroup':'/owned'})
        with patch.object(m,'output',return_value='LISTEN 0 1 0.0.0.0:3000 0.0.0.0:* users:(("node",pid=123,fd=9)) ino:456'):
            self.denied('NON_LOOPBACK_LISTENER',lambda:self.manager.owners('web',self.root,3000))

    def test_listener_inode_required(self):
        self.manager.unit=Mock(return_value={'WorkingDirectory':str(self.root),'ControlGroup':'/owned'})
        self.manager.identity=Mock(return_value={'cwd':str(self.root),'cgroup':'/owned'})
        with patch.object(m,'output',return_value='LISTEN 0 1 127.0.0.1:3000 0.0.0.0:* users:(("node",pid=123,fd=9))'):
            self.denied('LISTENER_INODE_UNVERIFIED',lambda:self.manager.owners('web',self.root,3000))

    def test_node_hash_failure_has_no_fallback(self):
        pin={'node_path':'/node22','node_version':'22.23.1','node_sha256':'expected'}
        with patch.object(m,'private',return_value=pin),patch.object(m,'digest',return_value='wrong'),patch.object(m,'output') as run:
            self.denied('VERIFIED_NODE22_REQUIRED',lambda:m.node_pin(self.state))
            run.assert_not_called()

    def test_failed_transition_recovers_once_without_retry(self):
        value={'before':{},'old_generated_hash':'a','root':str(self.root)}
        self.manager.preflight=Mock(return_value=value)
        self.manager.backup=Mock();self.manager.create_fixture=Mock();self.manager.save=Mock()
        self.manager.start_pair=Mock(side_effect=RuntimeError('START_FAILED'))
        self.manager.recover=Mock()
        self.denied('START_FAILED',lambda:self.manager.select(self.root))
        self.manager.start_pair.assert_called_once()
        self.manager.recover.assert_called_once_with(value)

    def test_backup_failure_never_stops_a_service(self):
        self.manager.preflight=Mock(return_value={});self.manager.backup=Mock(side_effect=RuntimeError('BACKUP_FAILED'))
        self.denied('BACKUP_FAILED',lambda:self.manager.select(self.root))
        self.control.stop_unit.assert_not_called()

    def test_baseline_change_blocks_before_stop(self):
        one={'before':{'pid':1},'old_generated_hash':'a'};two={'before':{'pid':2},'old_generated_hash':'a'}
        self.manager.preflight=Mock(side_effect=[one,two]);self.manager.backup=Mock();self.manager.create_fixture=Mock()
        self.denied('BASELINE_CHANGED_BEFORE_TRANSITION',lambda:self.manager.select(self.root))
        self.control.stop_unit.assert_not_called()

    def test_startup_does_not_apply_migrations(self):
        import ast
        source=(FILE.parent/'local_fixture.py').read_text()
        tree=ast.parse(source)
        create=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='create_app')
        calls=[n.func.attr for n in ast.walk(create) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
        self.assertNotIn('apply',calls)
        self.assertNotIn('bootstrap',calls)
        self.assertNotIn('create_account',calls)

    def test_resource_limits_and_no_restart(self):
        self.manager.start('web',self.root/'reliability-cockpit/web',['node'],[], '6G')
        args=self.control.run.call_args.args[0]
        self.assertIn('--property=Restart=no',args)
        self.assertIn('--property=MemoryMax=6G',args)
        self.assertIn('--property=KillMode=control-group',args)
        self.assertIn('-i',args)

    def test_invalid_recovery_source_never_stops_working_candidate(self):
        self.manager.release=Mock()
        self.control.frontend_controller=Mock()
        with patch.object(m,'old_source',side_effect=RuntimeError('ROLLBACK_SOURCE_CHANGED')):
            self.denied('ROLLBACK_SOURCE_CHANGED',lambda:self.manager.recover({'previous_root':str(self.root),'previous_sha':m.SHA}))
        self.control.stop_unit.assert_not_called()
