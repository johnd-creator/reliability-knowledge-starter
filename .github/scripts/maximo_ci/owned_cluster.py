"""Cleanup only a controller-created disposable PostgreSQL data directory.

Startup can succeed even when pg_ctl's wait fails. Capture on-disk identity before
the attempt, and never use a port or an unverified PID as cleanup authority.
"""
import os
from pathlib import Path
import re
import select
import signal
import stat
import subprocess


class OwnedCluster:
    def __init__(self, work, bindir, env, prefix):
        self.work = Path(work)
        self.data = self.work / 'data'
        self.bindir = Path(bindir)
        self.env = env
        self.prefix = prefix
        self.identity = None
        self.attempted = False

    def _directories(self):
        if (self.work.parent != Path('/tmp') or not self.work.name.startswith(self.prefix)
                or self.work.resolve() != self.work):
            raise RuntimeError('unverified private cluster directory')
        result = []
        for path in (self.work, self.data, self.work / 'socket'):
            info = path.lstat()
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                    or info.st_mode & 0o077):
                raise RuntimeError('unverified private cluster ownership')
            result.append((info.st_dev, info.st_ino))
        return tuple(result)

    def _system_id(self):
        # Force the diagnostic label language, without inheriting libpq options.
        output = subprocess.check_output(
            [str(self.bindir / 'pg_controldata'), str(self.data)],
            env=dict(self.env, LC_ALL='C'), text=True, stderr=subprocess.STDOUT,
            timeout=10)
        match = re.search(r'^Database system identifier:\s*(\d+)\s*$', output, re.M)
        if not match:
            raise RuntimeError('cluster system identity unavailable')
        return match.group(1)

    def before_start(self):
        self.identity = (self._directories(), self._system_id())
        # Set before invoking pg_ctl: timeout/nonzero is an uncertain outcome.
        self.attempted = True

    def _status(self):
        result = subprocess.run(
            [str(self.bindir / 'pg_ctl'), '-D', str(self.data), 'status'],
            env=self.env, capture_output=True, timeout=10)
        if result.returncode not in (0, 3):
            raise RuntimeError('cluster status unavailable')
        return result.returncode

    def _postmaster(self):
        pidfile = self.data / 'postmaster.pid'
        info = pidfile.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise RuntimeError('unverified cluster PID file')
        contents = pidfile.read_bytes()
        lines = contents.decode().splitlines()
        if len(lines) < 2 or not lines[0].isdigit() or Path(lines[1]) != self.data:
            raise RuntimeError('cluster process data directory mismatch')
        return int(lines[0]), contents

    def _verify_process(self, pid, contents):
        proc = Path('/proc') / str(pid)
        command = (proc / 'cmdline').read_bytes().split(b'\0')
        expected = [b'-D', os.fsencode(self.data)]
        if (proc.stat().st_uid != os.getuid()
                or (proc / 'exe').resolve() != (self.bindir / 'postgres').resolve()
                or not any(command[i:i+2] == expected for i in range(len(command)-1))
                or (self.data / 'postmaster.pid').read_bytes() != contents):
            raise RuntimeError('cluster process identity mismatch')

    def cleanup(self):
        if not self.attempted:
            return dict(cleanup='NOT_STARTED', cleanup_error=None)
        try:
            if self.identity != (self._directories(), self._system_id()):
                raise RuntimeError('cluster on-disk identity changed')
            if self._status() == 3:
                return dict(cleanup='OWN_CLUSTER_NOT_RUNNING', cleanup_error=None)
            pid, contents = self._postmaster()
            # Pin this process before verifying it. A replaced PID file or recycled
            # numeric PID must never redirect a later pg_ctl/raw-PID signal.
            descriptor = os.pidfd_open(pid, 0)
            try:
                self._verify_process(pid, contents)
                signal.pidfd_send_signal(descriptor, signal.SIGINT)
                waiter = select.poll()
                waiter.register(descriptor, select.POLLIN)
                if not any(fd == descriptor and mask & select.POLLIN
                           for fd, mask in waiter.poll(30000)):
                    raise TimeoutError('owned cluster shutdown unconfirmed')
            finally:
                os.close(descriptor)
            if self._status() != 3:
                raise RuntimeError('owned cluster still running')
            return dict(cleanup='OWN_CLUSTER_STOPPED', cleanup_error=None)
        except Exception as error:
            # Keep startup/test failure separately; never replace it with cleanup.
            return dict(cleanup='OWN_CLUSTER_CLEANUP_FAILED', cleanup_error=type(error).__name__)
