"""Real temporary Git archives; no retained source/service/store is mutated."""
import importlib.util,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
FILE=Path(__file__).resolve().parents[2]/'deploy/development/local_development.py'
spec=importlib.util.spec_from_file_location('sealed_local',FILE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SealedSourceTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.root=self.base/'source';self.root.mkdir();self.runtime={'controller':'reviewed','accounts_hash':'unchanged'}
  self.git('init','-q');self.git('config','user.name','Synthetic');self.git('config','user.email','synthetic@localhost');self.git('remote','add','origin','https://github.com/johnd-creator/reliability-knowledge-starter.git')
  (self.root/'.gitignore').write_text('node_modules/\n');(self.root/'code.py').write_text('committed\n');(self.root/'delete.py').write_text('removed\n');self.git('add','.');self.git('commit','-qm','base');self.head=self.git('rev-parse','HEAD')
  (self.root/'code.py').write_bytes(b'local\x00bytes\n');(self.root/'delete.py').unlink();(self.root/'new.py').write_text('untracked\n');(self.root/'new.py').chmod(0o750)
 def tearDown(self):self.tmp.cleanup()
 def git(self,*a):return subprocess.check_output(['git',*a],cwd=self.root,text=True).strip()
 def seal(self):return m.SealedSource.seal(self.root,self.base/'archive',self.runtime)
 def receipt(self):return m.SealedSource.prepare(self.seal(),self.base/'recovery',self.base)
 def test_exact_dirty_untracked_deleted_modes_and_git_provenance(self):
  original=m.SealedSource.scan(self.root);receipt=self.receipt();r=Path(receipt['root']);self.assertEqual(m.SealedSource.scan(self.root),original)
  self.assertEqual((r/'code.py').read_bytes(),b'local\x00bytes\n');self.assertEqual((r/'new.py').stat().st_mode&0o777,0o750);self.assertFalse((r/'delete.py').exists())
  self.assertEqual(subprocess.check_output(['git','status','--porcelain'],cwd=r),b'');self.assertNotEqual(receipt['sha'],self.head);self.assertEqual(m.SealedSource.verify_recovery(receipt)['source']['head'],self.head)
 def test_private_archive_and_recovery_without_original_git_writes(self):
  before=set((self.root/'.git/objects').rglob('*'));receipt=self.receipt();self.assertEqual(set((self.root/'.git/objects').rglob('*')),before)
  self.assertEqual(Path(receipt['root']).stat().st_mode&0o777,0o700)
  for p in (self.base/'archive').rglob('*'):self.assertFalse(p.stat().st_mode&0o077)
 def test_changed_original_blocks_prepare_without_overwrite(self):
  approval=self.seal();(self.root/'new.py').write_text('concurrent')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_SOURCE_CHANGED'):m.SealedSource.prepare(approval,self.base/'recovery',self.base)
  self.assertFalse((self.base/'recovery').exists())
 def test_added_untracked_detected(self):
  a=self.seal();(self.root/'added').touch()
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_SOURCE_CHANGED'):m.SealedSource.verify(a,original=True)
 def test_mode_change_detected(self):
  a=self.seal();(self.root/'new.py').chmod(0o700)
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_SOURCE_CHANGED'):m.SealedSource.verify(a,original=True)
 def test_git_head_change_detected(self):
  a=self.seal();self.git('add','.');self.git('commit','-qm','new')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_SOURCE_CHANGED'):m.SealedSource.verify(a,original=True)
 def test_branch_change_detected(self):
  a=self.seal();self.git('symbolic-ref','HEAD','refs/heads/different')
  with self.assertRaises(Exception):m.SealedSource.verify(a,original=True)
 def test_changed_origin_detected(self):
  a=self.seal();self.git('remote','set-url','origin','https://different')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_SOURCE_CHANGED'):m.SealedSource.verify(a,original=True)
 def test_archive_corruption_detected(self):
  a=self.seal();next((self.base/'archive/objects').iterdir()).write_bytes(b'corrupt')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_OBJECT_CORRUPT'):m.SealedSource.verify(a)
 def test_missing_archive_detected(self):
  a=self.seal();Path(a['manifest']).unlink()
  with self.assertRaises(FileNotFoundError):m.SealedSource.verify(a)
 def test_manifest_requires_exact_approval(self):
  a=self.seal();Path(a['manifest']).write_text('{}')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_APPROVAL_MISMATCH'):m.SealedSource.verify(a)
 def test_unsafe_archive_permissions_denied(self):
  a=self.seal();(self.base/'archive').chmod(0o755)
  with self.assertRaisesRegex(RuntimeError,'PRIVATE_PRESERVATION_ROOT_REQUIRED'):m.SealedSource.verify(a)
 def test_unsafe_original_permissions_denied(self):
  (self.root/'new.py').chmod(0o777)
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_UNSAFE_FILE_MODE'):self.seal()
 def test_symlink_source_denied(self):
  (self.root/'link').symlink_to('new.py')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_SYMLINK_DENIED'):self.seal()
 def test_symlink_archive_object_denied(self):
  a=self.seal();p=next((self.base/'archive/objects').iterdir());data=p.read_bytes();other=self.base/'other';other.write_bytes(data);p.unlink();p.symlink_to(other)
  with self.assertRaisesRegex(RuntimeError,'PRIVATE_PRESERVATION_OBJECT_REQUIRED'):m.SealedSource.verify(a)
 def test_path_traversal_and_secret_paths_denied(self):
  for name in ['../evil','/tmp/evil','a/../../evil','.git/config','.nadi-dev/accounts.json','a/.env','a/token.key','a/backup.dump']:
   with self.assertRaisesRegex(RuntimeError,'PRESERVATION_PATH_DENIED'):m.SealedSource.path(self.root,name)
 def test_ignored_frontend_dotenv_denied(self):
  p=self.root/'reliability-cockpit/web';p.mkdir(parents=True);(p/'.env.local').write_text('synthetic')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_PATH_DENIED|UNREVIEWED_DOTENV_DENIED'):self.seal()
 def test_existing_archive_not_replaced(self):
  self.seal()
  with self.assertRaises(FileExistsError):self.seal()
 def test_existing_recovery_not_replaced(self):
  a=self.seal();p=self.base/'recovery';p.mkdir();(p/'keep').touch()
  with self.assertRaisesRegex(RuntimeError,'NEW_MANAGED_RECOVERY_ROOT_REQUIRED'):m.SealedSource.prepare(a,p,self.base)
  self.assertTrue((p/'keep').exists())
 def test_recovery_content_cannot_be_substituted(self):
  r=self.receipt();(Path(r['root'])/'new.py').write_text('different')
  with self.assertRaisesRegex(RuntimeError,'SEALED_RECOVERY_SOURCE_CHANGED'):m.SealedSource.verify_recovery(r)
 def test_recovery_extra_file_denied(self):
  r=self.receipt();(Path(r['root'])/'extra').touch()
  with self.assertRaisesRegex(RuntimeError,'SEALED_RECOVERY_SOURCE_CHANGED'):m.SealedSource.verify_recovery(r)
 def test_recovery_permission_change_denied(self):
  r=self.receipt();(Path(r['root'])/'new.py').chmod(0o700)
  with self.assertRaisesRegex(RuntimeError,'SEALED_RECOVERY_SOURCE_CHANGED'):m.SealedSource.verify_recovery(r)
 def test_recovery_repository_alternate_change_denied(self):
  r=self.receipt();(Path(r['root'])/'.git/objects/info/alternates').write_text('/wrong\n')
  with self.assertRaises(Exception):m.SealedSource.verify_recovery(r)
 def test_private_recovery_push_must_stay_disabled(self):
  r=self.receipt();subprocess.check_call(['git','config','remote.origin.pushurl','https://different'],cwd=r['root'])
  with self.assertRaisesRegex(RuntimeError,'PRIVATE_RECOVERY_PUSH_DISABLED_REQUIRED'):m.SealedSource.verify_recovery(r)
 def test_original_concurrent_edit_not_overwritten_by_recovery_verification(self):
  r=self.receipt();(self.root/'new.py').write_text('later work');m.SealedSource.verify_recovery(r);self.assertEqual((self.root/'new.py').read_text(),'later work')

class PreservedLifecycleTest(unittest.TestCase):
 setUp=SealedSourceTest.setUp
 tearDown=SealedSourceTest.tearDown
 git=SealedSourceTest.git
 def setup_manager(self):
  from types import SimpleNamespace
  self.state=self.base/'state';self.state.mkdir(mode=0o700)
  self.c=SimpleNamespace(STATE=self.state,BASE=self.base,ROOT=self.root,UNITS=('api','web'),ORIGIN='https://localhost:3000',
      NAME='synthetic',LEGACY_WEB='legacy',stop_unit=Mock(),primary_busy=Mock(return_value=False),active=Mock(return_value=False))
  def write(p,s):
   fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
   with os.fdopen(fd,'w') as f:f.write(s)
  self.c.write_private=write;self.d=m.LocalDevelopment(self.c);self.d.state.mkdir(mode=0o700)
  self.d.save('accounts.json',{'synthetic':'no credentials'})
  self.d.save('config.json',{'source_root':str(self.root),'workflow_sha':'a'*40,'accounts_file':str(self.d.state/'accounts.json'),'application_dsn':'synthetic-unused'})
  self.value={'root':str(self.root),'sha':self.head,'workflow_sha':'a'*40,'config_path':str(self.d.state/'config.json'),'node':'/synthetic-node'}
  self.d.save('active.json',self.value);self.d.release=Mock(return_value='b'*40);self.d.owners=Mock(return_value={});self.d.readiness=Mock(return_value={'engineering_data':'SYNTHETIC_FIXTURES'})
  approval=self.d.preserve(self.base/'archive')
  self.receipt=self.d.prepare_preserved(approval,self.base/'recovery')
  dependency=Path(self.receipt['root'])/'reliability-cockpit/web/node_modules';dependency.mkdir(parents=True);(dependency/'.package-lock.json').write_text('synthetic-reviewed-lock')
  self.d.preservation={k:self.receipt[k] for k in ['receipt','receipt_sha256']}
 def test_preserved_previous_distinguishes_runtime_base_and_recovery_commit(self):
  self.setup_manager();p=self.d.previous()
  self.assertEqual(p['original_source']['sha'],self.head);self.assertNotEqual(p['sha'],self.head)
  self.assertEqual(p['before'],{'web':{},'api':{}});self.assertEqual(json.loads(Path(p['config_path']).read_text())['source_root'],p['root'])
  self.assertEqual(self.d.active_value(),self.value);self.c.stop_unit.assert_not_called()
 def test_preflight_repeat_does_not_write_recovery_config(self):
  self.setup_manager();self.d.previous()
  before={p.name:p.read_bytes() for p in self.d.state.iterdir() if p.is_file()}
  self.d.previous();self.assertEqual(before,{p.name:p.read_bytes() for p in self.d.state.iterdir() if p.is_file()})
 def test_wrong_controller_release_denied_before_any_stop(self):
  self.setup_manager();self.d.release.return_value='c'*40
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_RUNTIME_CHANGED'):self.d.previous()
  self.c.stop_unit.assert_not_called()
 def test_stale_runtime_process_denied(self):
  self.setup_manager();self.d.owners.return_value={'replaced_pid':9}
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_RUNTIME_CHANGED'):self.d.previous()
  self.c.stop_unit.assert_not_called()
 def test_account_drift_denied(self):
  self.setup_manager();(self.d.state/'accounts.json').write_text('{}')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_RUNTIME_CHANGED'):self.d.previous()
  self.c.stop_unit.assert_not_called()
 def test_configuration_drift_denied(self):
  self.setup_manager();p=Path(self.value['config_path']);p.write_text(p.read_text()+' ')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_RUNTIME_CHANGED'):self.d.previous()
 def test_receipt_approval_drift_denied(self):
  self.setup_manager();Path(self.receipt['receipt']).write_text('{}')
  with self.assertRaisesRegex(RuntimeError,'RECOVERY_RECEIPT_APPROVAL_CHANGED'):self.d.previous()
 def test_recovery_config_corruption_denied(self):
  self.setup_manager();Path(self.receipt['config_path']).write_text('{}')
  with self.assertRaisesRegex(RuntimeError,'RECOVERY_CONFIG_CHANGED'):self.d.previous()
 def test_concurrent_editor_after_archive_denied_without_overwrite(self):
  self.setup_manager();(self.root/'new.py').write_text('new user work')
  with self.assertRaisesRegex(RuntimeError,'PRESERVATION_SOURCE_CHANGED'):self.d.previous()
  self.assertEqual((self.root/'new.py').read_text(),'new user work')
 def test_lock_contention_no_snapshot_or_service_mutation(self):
  self.setup_manager()
  with self.d.transaction():
   with self.assertRaisesRegex(RuntimeError,'DEVELOPMENT_LIFECYCLE_BUSY'):self.d.preserve(self.base/'second')
  self.assertFalse((self.base/'second').exists());self.c.stop_unit.assert_not_called()
 def test_preserved_select_requires_authenticated_acceptance_before_stop(self):
  self.setup_manager()
  with self.assertRaisesRegex(RuntimeError,'AUTHENTICATED_ACCEPTANCE_PROOF_REQUIRED'):self.d.select(self.root,'HEAD')
  self.c.stop_unit.assert_not_called()
 def simulate_failure(self, failure):
  self.setup_manager();previous=self.d.previous();original=m.SealedSource.scan(self.root)
  # A real clean independent target, with process/DB boundaries simulated.
  target=m.SealedSource.prepare({k:self.receipt[k] for k in ['manifest','digest']},self.base/'target',self.base)
  value={'root':target['root'],'sha':target['sha'],'workflow_sha':'b'*40,'previous':previous,'config_path':previous['config_path']}
  self.d.preflight=Mock(side_effect=lambda *args:dict(value));self.d.backup=Mock(side_effect=lambda v,t:v.update(backup='synthetic-private-backup',backup_sha256='unchanged',backup_created=1))
  self.d.validate_recovery=Mock();self.d.acceptance_session_file='/synthetic-session-proof'
  self.d.start_pair=Mock(side_effect=[RuntimeError(failure),None]);self.d.wait_ready=Mock();self.d.attest=Mock()
  with self.assertRaisesRegex(RuntimeError,failure):self.d.select(Path(target['root']),target['sha'])
  self.assertEqual(self.d.active_value()['sha'],previous['sha']);self.assertEqual(m.SealedSource.scan(self.root),original)
  self.assertEqual(self.d.start_pair.call_count,2);self.assertTrue(list(self.d.state.glob('*-failure-recovered.json')))
 def test_first_service_start_failure_recovers_sealed_source_once(self):
  self.simulate_failure('SIMULATED_API_START_FAILURE')
 def test_second_service_start_failure_recovers_sealed_source_once(self):
  self.simulate_failure('SIMULATED_WEB_START_FAILURE_AFTER_API')
 def test_interrupted_transition_requires_review_before_stop(self):
  self.setup_manager();self.d.preservation=None
  self.d.save('selection-old-stopping.json',{'outcome':'STOPPING'})
  with self.assertRaisesRegex(RuntimeError,'INTERRUPTED_TRANSITION_REQUIRES_REVIEW'):self.d.select(self.root,'HEAD')
  self.c.stop_unit.assert_not_called()
 def test_failed_event_does_not_authorize_interrupted_retry(self):
  self.setup_manager();self.d.preservation=None
  self.d.save('selection-old-stopping.json',{});self.d.save('selection-old-failed.json',{})
  with self.assertRaisesRegex(RuntimeError,'INTERRUPTED_TRANSITION_REQUIRES_REVIEW'):self.d.select(self.root,'HEAD')
  self.c.stop_unit.assert_not_called()

 def test_wrong_database_identity_blocks_recovery_before_stop(self):
  self.setup_manager();previous=self.d.previous()
  value={'previous':previous,'config_hash':m.digest(previous['config_path']),'accounts_hash':m.digest(self.d.state/'accounts.json'),'db_container_id':'expected','fixture':{}}
  self.c.db=Mock(return_value={'Id':'wrong','State':{'Running':True}})
  with self.assertRaisesRegex(RuntimeError,'ROLLBACK_FIXTURE_CONTAINER_CHANGED'):self.d.validate_recovery(value)
  self.c.stop_unit.assert_not_called()
 def test_wrong_backup_blocks_recovery_before_stop(self):
  self.setup_manager();previous=self.d.previous()
  value={'previous':previous,'config_hash':m.digest(previous['config_path']),'accounts_hash':m.digest(self.d.state/'accounts.json'),'db_container_id':'expected','fixture':{}}
  self.c.db=Mock(return_value={'Id':'expected','State':{'Running':True}})
  self.d.validate_backup=Mock(side_effect=RuntimeError('BACKUP_UNREADABLE'))
  with patch.object(m,'node_pin'):
   with self.assertRaisesRegex(RuntimeError,'BACKUP_UNREADABLE'):self.d.validate_recovery(value)
  self.c.stop_unit.assert_not_called()
 def test_recovery_readiness_uses_existing_session_proof(self):
  self.setup_manager();self.d.acceptance_session_file='/private/proof'
  self.d.wait_ready(self.value)
  self.assertEqual(self.d.readiness.call_args.kwargs,{'session_file':'/private/proof'})
 def test_preserved_rollback_requires_authenticated_acceptance(self):
  self.setup_manager();previous=self.d.previous()
  with self.assertRaisesRegex(RuntimeError,'AUTHENTICATED_ACCEPTANCE_PROOF_REQUIRED'):self.d.recover({'previous':previous})
  self.c.stop_unit.assert_not_called()
 def test_recovery_failure_remains_explicit_without_publishing_candidate(self):
  self.setup_manager();previous=self.d.active_value()
  self.d.preflight=Mock(side_effect=RuntimeError('SIMULATED_GATE_FAILURE'))
  self.d.acceptance_session_file='/private/proof'
  with self.assertRaisesRegex(RuntimeError,'SIMULATED_GATE_FAILURE'):self.d.select(self.root,'HEAD')
  self.assertEqual(self.d.active_value(),previous);self.c.stop_unit.assert_not_called()
 def test_full_committed_contract_comparator_rejects_changed_backend(self):
  spec=importlib.util.spec_from_file_location('sealed_contract',FILE.with_name('frontend_preview.py'));contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
  with patch.object(contract,'git',side_effect=['unchanged','changed']):
   with self.assertRaisesRegex(RuntimeError,'FRONTEND_BACKEND_CONTRACT_DIFFERENCE'):contract.compatible(self.root,self.root,self.head,self.head)
  self.assertEqual(len(contract.COMPATIBILITY_PATHS),20)
 def test_dependency_sections_checked_after_source_surfaces(self):
  spec=importlib.util.spec_from_file_location('sealed_dependency_contract',FILE.with_name('frontend_preview.py'));contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
  calls=['same']*(2*len(contract.COMPATIBILITY_PATHS))+['{"dependencies":{"x":"1"}}','{"dependencies":{"x":"2"}}']
  with patch.object(contract,'git',side_effect=calls):
   with self.assertRaisesRegex(RuntimeError,'FRONTEND_DEPENDENCY_DIFFERENCE'):contract.compatible(self.root,self.root,self.head,self.head)
 def test_original_clean_source_guard_remains_strict(self):
  self.setup_manager()
  with self.assertRaisesRegex(RuntimeError,'INITIAL_CLEAN_SOURCE_REQUIRED'):m.source(self.root,self.base,self.head,clean=True)
 def test_foreign_repository_guard_remains_strict(self):
  self.setup_manager()
  with self.assertRaisesRegex(RuntimeError,'UNRELATED_SOURCE_REPOSITORY'):self.d.repository(self.base/'recovery')

 def test_dependency_drift_blocks_before_recovery_stop(self):
  self.setup_manager();previous=self.d.previous()
  value={'previous':previous}
  (Path(previous['root'])/'reliability-cockpit/web/node_modules/.package-lock.json').write_text('changed')
  with self.assertRaisesRegex(RuntimeError,'RECOVERY_DEPENDENCY_CHANGED'):self.d.validate_recovery(value)
  self.c.stop_unit.assert_not_called()

 def test_expired_existing_session_refused_before_backup_or_stop(self):
  self.setup_manager();self.d.acceptance_session_file='/private/proof'
  self.d.preflight=Mock(return_value={});self.d.backup=Mock()
  self.d.readiness.side_effect=RuntimeError('AUTHORIZED_SESSION_INVALID_OR_EXPIRED')
  with self.assertRaisesRegex(RuntimeError,'AUTHORIZED_SESSION_INVALID_OR_EXPIRED'):self.d.select(self.root,'HEAD')
  self.d.readiness.assert_called_with(self.value,session_file='/private/proof')
  self.d.backup.assert_not_called();self.c.stop_unit.assert_not_called()
 def test_failed_bounded_recovery_reports_failure_and_keeps_original_pointer(self):
  self.setup_manager();previous=self.d.previous();before=self.d.active_value()
  target=m.SealedSource.prepare({k:self.receipt[k] for k in ['manifest','digest']},self.base/'target',self.base)
  value={'root':target['root'],'sha':target['sha'],'workflow_sha':'b'*40,'previous':previous,'config_path':previous['config_path']}
  self.d.preflight=Mock(side_effect=lambda *args:dict(value));self.d.backup=Mock()
  self.d.validate_recovery=Mock();self.d.acceptance_session_file='/private/proof'
  self.d.start_pair=Mock(side_effect=[RuntimeError('SIMULATED_API_FAILURE'),RuntimeError('SIMULATED_RECOVERY_FAILURE')])
  with self.assertRaisesRegex(RuntimeError,'SIMULATED_RECOVERY_FAILURE'):self.d.select(Path(target['root']),target['sha'])
  self.assertEqual(self.d.active_value(),before)
  events=[json.loads(p.read_text()) for p in self.d.state.glob('selection-*-failed.json')]
  self.assertEqual(events[-1]['code'],'SIMULATED_RECOVERY_FAILURE')
  self.assertFalse(list(self.d.state.glob('*-failure-recovered.json')))
  self.assertEqual(self.d.start_pair.call_count,2)
