"""Uncertain startup/cleanup regressions. No PostgreSQL or processes are started."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import signal
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS / 'maximo_ci'))
from owned_cluster import OwnedCluster


def controller(lane):
    path = TOOLS / lane / ('run_projection_pg.py' if lane == 'maximo_ci' else 'run_pg.py')
    spec = importlib.util.spec_from_file_location('cleanup_' + lane, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OwnedClusterTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='nadi-cleanup-test-', dir='/tmp')
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.work.chmod(0o700)
        for name in ('data', 'socket'):
            (self.work / name).mkdir(mode=0o700)
        self.cluster = OwnedCluster(self.work, Path('/private/binaries'), {}, 'nadi-cleanup-test-')

    def test_identity_change_refuses_cleanup_without_any_process_command(self):
        with patch.object(self.cluster, '_system_id', side_effect=['123', '456']), \
                patch('owned_cluster.subprocess.run') as run:
            self.cluster.before_start()
            result = self.cluster.cleanup()
        self.assertEqual(result['cleanup'], 'OWN_CLUSTER_CLEANUP_FAILED')
        run.assert_not_called()

    def test_symlink_and_replaced_directory_refused(self):
        with patch.object(self.cluster, '_system_id', return_value='123'):
            self.cluster.before_start()
            (self.work / 'data').rename(self.work / 'original-data')
            (self.work / 'data').symlink_to(self.work / 'original-data', target_is_directory=True)
            with patch('owned_cluster.subprocess.run') as run:
                result = self.cluster.cleanup()
        self.assertEqual(result['cleanup'], 'OWN_CLUSTER_CLEANUP_FAILED')
        run.assert_not_called()

    def test_unrelated_process_identity_refuses_stop(self):
        # A recycled/stale PID pointing at this Python process grants no authority.
        (self.work / 'data/postmaster.pid').write_text(str(os.getpid()) + '\n' + str(self.work / 'data') + '\n')
        with patch.object(self.cluster, '_system_id', return_value='123'), \
                patch('owned_cluster.subprocess.run', return_value=subprocess.CompletedProcess([], 0)) as run, \
                patch('owned_cluster.os.pidfd_open', return_value=42), \
                patch('owned_cluster.os.close'), \
                patch('owned_cluster.signal.pidfd_send_signal') as send:
            self.cluster.before_start()
            result = self.cluster.cleanup()
        self.assertEqual(result['cleanup'], 'OWN_CLUSTER_CLEANUP_FAILED')
        self.assertEqual(len(run.call_args_list), 1)  # status only; never stop.
        self.assertEqual(run.call_args.args[0][-1], 'status')
        send.assert_not_called()

    def test_owned_process_requires_exact_executable_arguments_and_pidfile(self):
        # Synthetic /proc tree: exercise identity checks without spawning anything.
        pid = '12345'
        proc_root = self.work / 'synthetic-proc'
        proc = proc_root / pid
        proc.mkdir(parents=True)
        (proc / 'exe').symlink_to(self.cluster.bindir / 'postgres')
        (proc / 'cmdline').write_bytes(b'postgres\0-D\0' + os.fsencode(self.cluster.data) + b'\0')
        (self.cluster.data / 'postmaster.pid').write_text(pid + '\n' + str(self.cluster.data) + '\n')
        with patch('owned_cluster.Path', side_effect=lambda value: proc_root if value == '/proc' else Path(value)):
            self.cluster._verify_process(int(pid), (self.cluster.data / 'postmaster.pid').read_bytes())
            (proc / 'cmdline').write_bytes(b'postgres\0-D\0/another/data\0')
            with self.assertRaises(RuntimeError):
                self.cluster._verify_process(int(pid), (self.cluster.data / 'postmaster.pid').read_bytes())

    def pinned_cleanup(self, mutation=None, unavailable=False, timeout=False):
        pid = '12345'
        proc_root = self.work / 'synthetic-proc'
        proc = proc_root / pid
        proc.mkdir(parents=True)
        (proc / 'exe').symlink_to(self.cluster.bindir / 'postgres')
        (proc / 'cmdline').write_bytes(b'postgres\0-D\0' + os.fsencode(self.cluster.data) + b'\0')
        pidfile = self.cluster.data / 'postmaster.pid'
        pidfile.write_text(pid + '\n' + str(self.cluster.data) + '\n')
        events = []
        verify = self.cluster._verify_process

        def open_fd(number, flags):
            events.append(('open', number))
            if unavailable:
                raise OSError('synthetic pidfd unavailable')
            if mutation == 'pidfile_before_verify':
                pidfile.write_text('99999\n' + str(self.cluster.data) + '\n')
            if mutation == 'process_before_verify':
                (proc / 'exe').unlink()
                (proc / 'exe').symlink_to('/unrelated/executable')
            return 42

        def verify_process(number, contents):
            events.append(('verify', number))
            verify(number, contents)

        def send(descriptor, signum):
            # A PID-file replacement AFTER verification still cannot redirect the
            # signal: only the descriptor opened before verification is used.
            if mutation == 'pidfile_after_verify':
                pidfile.write_text('99999\n' + str(self.cluster.data) + '\n')
            events.append(('signal', descriptor, signum))

        with patch.object(self.cluster, '_system_id', return_value='123'), \
                patch.object(self.cluster, '_status', side_effect=[0, 3]), \
                patch.object(self.cluster, '_verify_process', side_effect=verify_process), \
                patch('owned_cluster.Path', side_effect=lambda value: proc_root if value == '/proc' else Path(value)), \
                patch('owned_cluster.os.pidfd_open', side_effect=open_fd), \
                patch('owned_cluster.os.close') as close, \
                patch('owned_cluster.signal.pidfd_send_signal', side_effect=send), \
                patch('owned_cluster.select.poll') as poll, \
                patch('owned_cluster.subprocess.run') as run:
            poll.return_value.poll.return_value=[] if timeout else [(42,1)]
            self.cluster.before_start()
            result=self.cluster.cleanup()
        run.assert_not_called()  # No pg_ctl stop, raw-PID command or fallback.
        if unavailable:
            close.assert_not_called()
        else:
            close.assert_called_once_with(42)
        return result, events

    def test_positive_full_verification_pins_before_verify_and_signal(self):
        result, events=self.pinned_cleanup()
        self.assertEqual(result['cleanup'],'OWN_CLUSTER_STOPPED')
        self.assertEqual(events,[('open',12345),('verify',12345),('signal',42,signal.SIGINT)])

    def test_pidfile_or_process_replacement_before_verification_refuses_signal(self):
        for mutation in ('pidfile_before_verify','process_before_verify'):
            with self.subTest(mutation=mutation):
                result, events=self.pinned_cleanup(mutation=mutation)
                self.assertEqual(result['cleanup'],'OWN_CLUSTER_CLEANUP_FAILED')
                self.assertFalse(any(event[0]=='signal' for event in events))
                shutil.rmtree(self.work/'synthetic-proc')

    def test_replacement_after_verification_cannot_redirect_pinned_signal(self):
        result, events=self.pinned_cleanup(mutation='pidfile_after_verify')
        self.assertEqual(result['cleanup'],'OWN_CLUSTER_STOPPED')
        self.assertEqual(events[-1],('signal',42,signal.SIGINT))

    def test_pidfd_unavailable_has_no_pid_or_pg_ctl_fallback(self):
        result, events=self.pinned_cleanup(unavailable=True)
        self.assertEqual(result['cleanup_error'],'OSError')
        self.assertEqual(events,[('open',12345)])

    def test_shutdown_wait_timeout_fails_without_retrying_signal(self):
        result, events=self.pinned_cleanup(timeout=True)
        self.assertEqual(result['cleanup_error'],'TimeoutError')
        self.assertEqual(sum(event[0]=='signal' for event in events),1)

    def test_not_running_is_confirmed_and_does_not_issue_stop(self):
        with patch.object(self.cluster, '_system_id', return_value='123'), \
                patch('owned_cluster.subprocess.run', return_value=subprocess.CompletedProcess([], 3)) as run:
            self.cluster.before_start()
            self.assertEqual(self.cluster.cleanup(), dict(cleanup='OWN_CLUSTER_NOT_RUNNING', cleanup_error=None))
        self.assertEqual(len(run.call_args_list), 1)

    def test_stop_success_without_stopped_status_is_failure(self):
        with patch.object(self.cluster, '_system_id', return_value='123'), \
                patch.object(self.cluster, '_status', return_value=0), \
                patch.object(self.cluster, '_postmaster', return_value=(12345,b'pidfile')), \
                patch.object(self.cluster, '_verify_process'), \
                patch('owned_cluster.os.pidfd_open', return_value=42), \
                patch('owned_cluster.os.close'), \
                patch('owned_cluster.signal.pidfd_send_signal'), \
                patch('owned_cluster.select.poll') as poll:
            poll.return_value.poll.return_value=[(42,1)]
            self.cluster.before_start()
            self.assertEqual(self.cluster.cleanup()['cleanup'], 'OWN_CLUSTER_CLEANUP_FAILED')

    def exercise_controller(self, lane, start_error, stop_error=None, identity_changed=False, init_error=False, malformed=False):
        module = controller(lane)
        report = self.work / (lane + '-report.json')
        stopped = False
        calls = []

        def run(words, **kwargs):
            nonlocal stopped
            calls.append(words)
            if Path(words[0]).name == 'initdb':
                data = Path(words[words.index('-D') + 1])
                if init_error:
                    raise start_error
                data.mkdir(mode=0o700)
            elif words[-1] == 'status':
                return subprocess.CompletedProcess(words, 3 if stopped else 0)
            elif 'start' in words:
                if malformed:
                    (Path(words[words.index('-D') + 1]).parent / 'prepare-result.json').write_text('{invalid' if malformed is True else malformed)
                if start_error:
                    raise start_error
            else:
                raise AssertionError('unexpected subprocess')
            return subprocess.CompletedProcess(words, 0)

        def send(descriptor, signum):
            nonlocal stopped
            self.assertEqual((descriptor,signum),(42,signal.SIGINT))
            if stop_error:
                raise stop_error
            stopped=True

        flag = '--root' if lane == 'maximo_ci' else '--source'
        private = self.work / ('nadi-' + dict(maximo_ci='b1', coverage_ci='b4', qualification_ci='b5', source_lock_ci='lock')[lane] + '-pg-fixture')
        # Controller retains its private evidence; the test owns and removes it.
        # mkdtemp normally creates the directory itself.
        def mkdtemp(**kwargs):
            private.mkdir(mode=0o700)
            return str(private)
        identities = ['123', '456'] if identity_changed else ['123', '123']
        with patch.dict(os.environ, {}, clear=False), \
                patch.object(sys, 'argv', ['test', flag, str(self.work), '--sha', 'a' * 40, '--report', str(report)]), \
                patch.object(module.tempfile, 'mkdtemp', side_effect=mkdtemp), \
                patch.object(module.shutil, 'which', return_value='/private/binaries/initdb'), \
                patch('owned_cluster.subprocess.run', side_effect=run), \
                patch.object(OwnedCluster, '_directories', return_value=('owned-test-inodes',)), \
                patch.object(OwnedCluster, '_system_id', side_effect=identities), \
                patch.object(OwnedCluster, '_postmaster', return_value=(12345,b'pidfile')), \
                patch.object(OwnedCluster, '_verify_process'), \
                patch('owned_cluster.os.pidfd_open', return_value=42), \
                patch('owned_cluster.os.close'), \
                patch('owned_cluster.signal.pidfd_send_signal', side_effect=send) as send_signal, \
                patch('owned_cluster.select.poll') as poll, \
                patch.dict(sys.modules, {'psycopg':SimpleNamespace(connect=lambda **kw: (_ for _ in ()).throw(RuntimeError('synthetic fixture failure')))}), \
                patch('builtins.print'):
            poll.return_value.poll.return_value=[(42,1)]
            self.assertEqual(module.main(), 1)
        result = json.loads(report.read_text())
        self.assertEqual(result['conclusion'], 'FAIL')
        self.assertEqual(result['infrastructure_error'], type(start_error).__name__ if start_error else 'RuntimeError')
        return result, calls, send_signal.call_count

    def test_uncertain_timeout_and_nonzero_start_cleanup_in_all_controllers(self):
        for lane in ('maximo_ci', 'coverage_ci', 'qualification_ci', 'source_lock_ci'):
            for error in (subprocess.TimeoutExpired('synthetic-start', 30), subprocess.CalledProcessError(1, 'synthetic-start')):
                with self.subTest(lane=lane, error=type(error).__name__):
                    # Each exercise creates the same owned controller directory.
                    result, calls, signals = self.exercise_controller(lane, error)
                    self.assertEqual(result['cleanup'], 'OWN_CLUSTER_STOPPED')
                    self.assertIsNone(result['cleanup_error'])
                    self.assertEqual(signals, 1)
                    self.assertFalse(any(words[-1]=='stop' for words in calls))
                    shutil.rmtree(next(self.work.glob('nadi-*-pg-fixture')))

    def test_controller_cleanup_failure_preserves_original_start_failure(self):
        result, _, _ = self.exercise_controller('qualification_ci', subprocess.TimeoutExpired('synthetic-start', 30),
                                            subprocess.CalledProcessError(1, 'synthetic-stop'))
        self.assertEqual(result['cleanup'], 'OWN_CLUSTER_CLEANUP_FAILED')
        self.assertEqual(result['cleanup_error'], 'CalledProcessError')

    def test_controller_identity_mismatch_does_not_stop(self):
        result, calls, signals = self.exercise_controller('source_lock_ci', subprocess.TimeoutExpired('synthetic-start', 30),
                                                identity_changed=True)
        self.assertEqual(result['cleanup'], 'OWN_CLUSTER_CLEANUP_FAILED')
        self.assertFalse(any(words[-1] == 'stop' for words in calls))
        self.assertEqual(signals,0)

    def test_initdb_failure_reports_not_started(self):
        result, _, signals=self.exercise_controller('coverage_ci', RuntimeError('synthetic initdb failure'), init_error=True)
        self.assertEqual(result['cleanup'],'NOT_STARTED')
        self.assertEqual(signals,0)

    def test_fixture_failure_and_cleanup_failure_both_survive(self):
        result, _, _=self.exercise_controller('qualification_ci', None, PermissionError('synthetic cleanup failure'))
        self.assertEqual(result['infrastructure_error'],'RuntimeError')
        self.assertEqual(result['cleanup_error'],'PermissionError')

    def test_malformed_prepare_evidence_cannot_suppress_report(self):
        for lane in ('qualification_ci','source_lock_ci'):
            for content, expected in ((True,'JSONDecodeError'),('[]','ValueError')):
                with self.subTest(lane=lane, content=content):
                    result, _, _=self.exercise_controller(lane, subprocess.TimeoutExpired('synthetic-start',30), malformed=content)
                    self.assertEqual(result['prepare_evidence_error'],expected)
                    self.assertEqual(result['cleanup'],'OWN_CLUSTER_STOPPED')
                    shutil.rmtree(next(self.work.glob('nadi-*-pg-fixture')))


if __name__ == '__main__':
    unittest.main()
