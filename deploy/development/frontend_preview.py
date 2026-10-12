"""Explicit single-frontend source selection. Never calls API/DB startup or migrations."""
import difflib
import hashlib
import json
import os
import re
import ssl
import subprocess
import time
import uuid
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlsplit

# Equality is deliberately conservative; a difference requires a separate integration review.
COMPATIBILITY_PATHS = (
    'reliability-cockpit/src', 'reliability-cockpit/tests/qa',
    'reliability-cockpit/tests/test_condition_evidence.py',
    'reliability-cockpit/tests/test_asset_af_mapping_admin.py',
    'pi-collector/tests/fixtures/condition_source.py',
    'reliability-cockpit/application-migrations', 'reliability-cockpit/pyproject.toml',
    'reliability-data-contracts', 'reliability-cockpit/web/package-lock.json',
    'reliability-cockpit/web/app/api/engineering-qa',
    *('reliability-cockpit/web/' + p for p in (
        'lib/api.ts', 'lib/bounded-http.ts', 'lib/engineering-http.ts',
        'lib/engineering.ts', 'lib/engineering-workflow.ts', 'lib/manual-pdm.ts',
        'lib/case-records.ts', 'lib/product-records.ts', 'lib/advisory-records.ts',
        'components/useQaRecords.ts')),
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def private_json(path):
    p = Path(path)
    info = p.lstat()
    if p.is_symlink() or not p.is_file() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise RuntimeError('PRIVATE_FRONTEND_STATE_REQUIRED')
    return json.loads(p.read_text())


def output(args, cwd=None):
    return subprocess.check_output([str(x) for x in args], cwd=cwd, text=True, timeout=20).strip()


def git(root, *args):
    if args and args[0] == 'status':
        return subprocess.check_output(['git', *args], cwd=root, text=True, timeout=20).rstrip('\n')
    return output(['git', *args], root)


def compatible(front, backend, front_sha, backend_sha):
    hashes = {}
    for path in COMPATIBILITY_PATHS:
        a = git(front, 'rev-parse', front_sha + ':' + path)
        b = git(backend, 'rev-parse', backend_sha + ':' + path)
        if a != b:
            raise RuntimeError('FRONTEND_BACKEND_CONTRACT_DIFFERENCE: ' + path)
        hashes[path] = a
    a = json.loads(git(front, 'show', front_sha + ':reliability-cockpit/web/package.json'))
    b = json.loads(git(backend, 'show', backend_sha + ':reliability-cockpit/web/package.json'))
    for key in ('dependencies', 'devDependencies', 'engines', 'overrides'):
        if a.get(key) != b.get(key):
            raise RuntimeError('FRONTEND_DEPENDENCY_DIFFERENCE')
    return hashlib.sha256(canonical(hashes).encode()).hexdigest()


class FrontendPreview:
    def __init__(self, control):
        self.c = control
        self.pointer = control.STATE / 'frontend-active.json'

    def request(self, url, https=False):
        kwargs = {'timeout': 10}
        if https:
            kwargs['context'] = ssl.create_default_context(cafile=str(self.c.STATE / 'localhost.pem'))
        with urlopen(url, **kwargs) as response:
            return json.load(response)

    def unit(self, name):
        data = output(['systemctl', '--user', 'show', name,
                       '--property=MainPID,ExecMainStartTimestamp,WorkingDirectory,ActiveState,ControlGroup'])
        value = dict(line.split('=', 1) for line in data.splitlines())
        group = value.get('ControlGroup', '')
        if group:
            value['ProcessIDs'] = Path('/sys/fs/cgroup' + group + '/cgroup.procs').read_text().strip()
        return value

    def active_source(self):
        if self.pointer.exists():
            value = private_json(self.pointer)
            approval = private_json(value['manifest'])['approval']
            return Path(approval['frontend_root']), approval['frontend_sha'], value['manifest']
        return self.c.ROOT, git(self.c.ROOT, 'rev-parse', 'HEAD'), None

    def verify_owner(self, root):
        unit = self.unit(self.c.UNITS[1])
        if unit.get('ActiveState') != 'active' or unit.get('MainPID') == '0' or unit.get('WorkingDirectory') != str(root / 'reliability-cockpit/web'):
            raise RuntimeError('UNEXPECTED_PRIMARY_FRONTEND_UNIT')
        listeners = output(['ss', '-H', '-ltnp', 'sport = :3000'])
        if not listeners:
            raise RuntimeError('PRIMARY_FRONTEND_LISTENER_MISSING')
        for line in listeners.splitlines():
            if line.split()[3] not in ('[::1]:3000', '127.0.0.1:3000'):
                raise RuntimeError('NON_LOOPBACK_FRONTEND_LISTENER')
            pids = re.findall(r'pid=(\d+)', line)
            if not pids or any(self.c.UNITS[1] not in Path('/proc/' + pid + '/cgroup').read_text() for pid in pids):
                raise RuntimeError('UNEXPECTED_PRIMARY_PORT_OWNER')
        return unit

    def backend(self):
        unit = self.unit(self.c.UNITS[0])
        if unit.get('ActiveState') != 'active' or unit.get('MainPID') == '0' or unit.get('WorkingDirectory') != str(self.c.ROOT / 'reliability-cockpit'):
            raise RuntimeError('UNCHANGED_QA_API_REQUIRED')
        if git(self.c.ROOT, 'status', '--porcelain'):
            raise RuntimeError('DIRTY_BACKEND_SOURCE_DENIED')
        data = self.request('http://127.0.0.1:13036/development/status')
        if (data.get('source_sha') != git(self.c.ROOT, 'rev-parse', 'HEAD') or
                data.get('database_identity') != 'nadi_live_dev_test' or
                data.get('environment') != 'DEVELOPMENT' or not data.get('engineering')):
            raise RuntimeError('UNVERIFIED_BACKEND_SOURCE')
        return unit, data['source_sha']

    def backup(self, path):
        path = Path(path).absolute()
        info = path.lstat()
        if (path.parent != self.c.STATE or path.is_symlink() or not path.is_file() or
                not re.fullmatch(r'backup-\d{8}-\d{6}\.dump', path.name) or
                info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size < 1000 or
                time.time() - info.st_mtime > 12 * 3600):
            raise RuntimeError('VALID_PRIVATE_RECENT_BACKUP_REQUIRED')
        with path.open('rb') as stream:
            value = subprocess.run(['docker', 'exec', '-i', self.c.NAME, 'pg_restore', '--list'],
                                   stdin=stream, capture_output=True, timeout=30)
        if value.returncode or b'nadi_human_record' not in value.stdout or b'nadi_application_session' not in value.stdout:
            raise RuntimeError('BACKUP_ARCHIVE_UNREADABLE')
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def source(self, root, sha):
        root = Path(root).absolute()
        if root.is_symlink() or root.resolve() != root or root.parent != self.c.BASE:
            raise RuntimeError('EXISTING_MANAGED_WORKTREE_REQUIRED')
        if not sha or not re.fullmatch('[0-9a-f]{40}', sha) or git(root, 'rev-parse', 'HEAD') != sha:
            raise RuntimeError('EXACT_REVIEWED_FRONTEND_SHA_REQUIRED')
        if Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')) != Path(git(self.c.ROOT, 'rev-parse', '--path-format=absolute', '--git-common-dir')):
            raise RuntimeError('UNRELATED_FRONTEND_REPOSITORY')
        if git(root, 'status', '--porcelain'):
            raise RuntimeError('DIRTY_FRONTEND_SOURCE_DENIED')
        web = root / 'reliability-cockpit/web'
        if any((web / name).exists() for name in ('.env', '.env.local', '.env.development', '.env.development.local')):
            raise RuntimeError('UNREVIEWED_FRONTEND_DOTENV')
        if not (web / 'node_modules/next/dist/bin/next').is_file():
            raise RuntimeError('REVIEWED_FRONTEND_DEPENDENCIES_REQUIRED')
        return root

    def launcher_release(self):
        release = private_json(self.c.STATE / 'controller-release.json')
        main_hash = hashlib.sha256(Path(self.c.__file__).read_bytes()).hexdigest()
        helper_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if (release.get('controller_sha256') != main_hash or release.get('helper_sha256') != helper_hash or
                not re.fullmatch('[0-9a-f]{40}', release.get('source_sha', ''))):
            raise RuntimeError('UNREVIEWED_FRONTEND_CONTROLLER_RELEASE')
        return release['source_sha'], hashlib.sha256((main_hash + helper_hash).encode()).hexdigest()

    def runtime(self):
        """Explicit private Node 22 pin. No PATH/Brew fallback, install or API effects."""
        try:
            pin = private_json(self.c.STATE / 'frontend-runtime.json')
        except (OSError, ValueError) as error:
            raise RuntimeError('PINNED_FRONTEND_NODE_CONFIG_REQUIRED') from error
        binary = Path(pin.get('node_path', ''))
        if (not binary.is_absolute() or binary.resolve() != binary or not binary.is_file() or
                binary.stat().st_uid not in (0, os.getuid()) or binary.stat().st_mode & 0o022 or
                not os.access(binary, os.X_OK)):
            raise RuntimeError('PINNED_FRONTEND_NODE_BINARY_REQUIRED')
        digest = hashlib.sha256(binary.read_bytes()).hexdigest()
        if digest != pin.get('node_sha256'):
            raise RuntimeError('PINNED_FRONTEND_NODE_HASH_CHANGED')
        script = "JSON.stringify({node:process.versions.node,v8:process.versions.v8,execPath:process.execPath,libnode:process.report.getReport().sharedObjects.filter(p=>p.includes('/libnode.so'))})"
        try:
            result = subprocess.run([str(binary), '-p', script], capture_output=True, text=True, timeout=10,
                                    env={'PATH': '/usr/bin:/bin', 'HOME': str(Path.home())}, check=True)
        except (OSError, subprocess.SubprocessError) as error:
            raise RuntimeError('PINNED_FRONTEND_NODE_EXECUTION_FAILED') from error
        actual = json.loads(result.stdout)
        if (not re.fullmatch(r'22\.\d+\.\d+', actual.get('node', '')) or
                actual.get('node') != pin.get('node_version') or actual.get('v8') != pin.get('v8_version') or
                Path(actual.get('execPath', '')).resolve() != binary):
            raise RuntimeError('PINNED_FRONTEND_NODE_22_VERSION_REQUIRED')
        libraries = pin.get('libnode_sha256', {})
        if not isinstance(libraries, dict) or set(actual.get('libnode', [])) != set(libraries):
            raise RuntimeError('PINNED_FRONTEND_NODE_LIBRARY_CHANGED')
        for name, expected in libraries.items():
            path = Path(name)
            if (not path.is_absolute() or path.stat().st_uid not in (0, os.getuid()) or
                    path.stat().st_mode & 0o022 or hashlib.sha256(path.read_bytes()).hexdigest() != expected):
                raise RuntimeError('PINNED_FRONTEND_NODE_LIBRARY_CHANGED')
        command = self.c.STATE / 'frontend-node-bin' / 'node'
        directory = command.parent
        if (directory.is_symlink() or directory.stat().st_uid != os.getuid() or directory.stat().st_mode & 0o077 or
                not command.is_symlink() or command.resolve() != binary):
            raise RuntimeError('PINNED_FRONTEND_CHILD_NODE_REQUIRED')
        return {'path': str(binary), 'version': actual['node'], 'v8': actual['v8'],
                'sha256': digest, 'digest': hashlib.sha256(canonical(pin).encode()).hexdigest()}

    def preflight(self, root, sha, backup):
        config = self.c.load()
        target = urlsplit(config['application_dsn'])
        if target.hostname != '127.0.0.1' or target.port != 15443 or target.path != '/nadi_live_dev_test' or target.username != 'nadi_dev_fixture':
            raise RuntimeError('EXISTING_LOOPBACK_QA_STORE_REQUIRED')
        launcher_sha, launcher_digest = self.launcher_release()
        runtime = self.runtime()
        root = self.source(root, sha)
        if self.c.active(self.c.LEGACY_WEB):
            raise RuntimeError('COMPETING_FRONTEND_DENIED')
        db = self.c.db()
        if not db or not db['State']['Running']:
            raise RuntimeError('EXISTING_QA_DATABASE_REQUIRED')
        ports = db['NetworkSettings']['Ports'].get('5432/tcp') or []
        if ports != [{'HostIp': '127.0.0.1', 'HostPort': '15443'}]:
            raise RuntimeError('EXISTING_LOOPBACK_QA_DATABASE_REQUIRED')
        for name in ('localhost.pem', 'localhost.key'):
            path = self.c.STATE / name
            info = path.lstat()
            if path.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise RuntimeError('EXISTING_PRIVATE_HTTPS_REQUIRED')
        previous, previous_sha, manifest = self.active_source()
        self.source(previous, previous_sha)
        self.verify_owner(previous)
        api, backend_sha = self.backend()
        evidence = compatible(root, self.c.ROOT, sha, backend_sha)
        compatible(previous, self.c.ROOT, previous_sha, backend_sha)
        backup_hash = self.backup(backup)
        self.readiness(previous_sha, backend_sha, manifest)
        return {'frontend_root': str(root), 'frontend_sha': sha, 'backend_root': str(self.c.ROOT),
                'backend_sha': backend_sha, 'compatibility_digest': evidence, 'version': 1,
                'launcher_sha256': launcher_digest, 'launcher_source_sha': launcher_sha,
                'backup_sha256': backup_hash, 'frontend_node_path': runtime['path'],
                'frontend_node_version': runtime['version'], 'frontend_v8_version': runtime['v8'],
                'frontend_node_sha256': runtime['sha256'], 'frontend_runtime_digest': runtime['digest'], 'approved_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}, {
                    'root': str(previous), 'sha': previous_sha, 'manifest': manifest,
                    'api_unit': api, 'backup': str(Path(backup).absolute())}

    def readiness(self, sha, backend_sha, manifest):
        data = self.request(self.c.ORIGIN + '/api/development/status', https=True)
        if (data.get('sha') != sha or data.get('launched_sha') != sha or data.get('backend_sha') != backend_sha or
                data.get('stale') is not False or data.get('dirty') is not False or
                data.get('backend') != 'AVAILABLE' or data.get('factual_backend') != 'AVAILABLE' or
                data.get('database_identity') != 'nadi_live_dev_test' or not data.get('engineering')):
            raise RuntimeError('FRONTEND_ONLY_READINESS_FAILED')
        if sha != backend_sha:
            envelope = private_json(manifest)
            if data.get('compatibility_approval') != envelope['approval_id'] or data.get('compatibility') != 'VERIFIED_SOURCE_EQUIVALENT':
                raise RuntimeError('UNAPPROVED_FRONTEND_BACKEND_PAIR')
        return data

    def web_start(self, root, sha, manifest):
        runtime = self.runtime()
        extra = ['NODE_ENV=development', 'NEXT_TELEMETRY_DISABLED=1', 'NODE_OPTIONS=--max-old-space-size=2048',
                 'NADI_LIVE_DEV=true', 'NADI_PRIMARY_FRONTEND=true', 'NADI_ENGINEERING_WORKSPACE_ENABLED=true',
                 'NADI_ENGINEERING_DEMO_ENABLED=true', 'NADI_ENGINEERING_QA_ENABLED=true',
                 'NADI_QA_BACKEND_URL=http://127.0.0.1:13036', 'COCKPIT_API_BASE=http://127.0.0.1:8000',
                 'NADI_DEV_LAUNCHED_SHA=' + sha,
                 'PATH=' + str(self.c.STATE / 'frontend-node-bin') + ':/usr/bin:/bin']
        if manifest:
            extra.append('NADI_DEV_FRONTEND_MANIFEST=' + str(manifest))
            extra.append('NADI_DEV_FRONTEND_WORKER=' + str(self.worker_path(manifest)))
        self.c.start_unit('nadi-primary-web', Path(root) / 'reliability-cockpit/web',
                         [runtime['path'], 'node_modules/next/dist/bin/next', 'dev',
                          '--hostname', 'localhost', '--port', '3000', '--experimental-https',
                          '--experimental-https-key', str(self.c.STATE / 'localhost.key'),
                          '--experimental-https-cert', str(self.c.STATE / 'localhost.pem')], extra)

    def worker_path(self, manifest):
        manifest = Path(manifest)
        if manifest.parent != self.c.STATE or not re.fullmatch(r'frontend-approval-[a-f0-9]+\.json', manifest.name):
            raise RuntimeError('PRIVATE_WORKER_MANIFEST_REQUIRED')
        return manifest.with_name(manifest.name.replace('frontend-approval-', 'frontend-worker-'))

    def worker_identity(self, root):
        """Capture actual HTTPS listener, PID reuse token, parent and service invocation."""
        unit = self.verify_owner(Path(root))
        lines = output(['ss', '-H', '-ltnp', 'sport = :3000'])
        pids = set(re.findall(r'pid=(\d+)', lines))
        if len(pids) != 1:
            raise RuntimeError('SINGLE_NEXT_WORKER_REQUIRED')
        pid = int(pids.pop())
        fields = Path('/proc/' + str(pid) + '/stat').read_text().rsplit(') ', 1)[1].split()
        if fields[1] != unit['MainPID']:
            raise RuntimeError('NEXT_WORKER_PARENT_CHANGED')
        invocation = output(['systemctl', '--user', 'show', self.c.UNITS[1], '--value', '-p', 'InvocationID'])
        return {'worker_pid': pid, 'parent_pid': int(fields[1]), 'start_ticks': fields[19],
                'invocation_id': invocation}

    def record_worker(self, root, manifest, identity):
        path = self.worker_path(manifest)
        envelope = private_json(manifest)
        previous = private_json(path) if path.exists() else None
        record = {**identity, 'approval_id': envelope['approval_id'],
                  'generation': (previous['generation'] + 1) if previous else 1,
                  'recorded_at': time.time()}
        # Preserve each officially observed generation rather than overwrite history.
        history = path.with_name(path.stem + '-generation-' + uuid.uuid4().hex + '.json')
        self.c.write_private(history, canonical(record))
        temporary = path.with_name(path.stem + '-' + uuid.uuid4().hex + '.tmp')
        self.c.write_private(temporary, canonical(record))
        os.replace(temporary, path)

    def restore_generated_types(self, root, sha):
        # Next rewrites only this generated cache reference during dev startup.
        # Restore exact committed bytes only when the entire difference is that
        # known generated line. Any unrelated edit remains dirty and fail-closed.
        path = Path(root) / 'reliability-cockpit/web/next-env.d.ts'
        if path.is_symlink() or git(root, 'rev-parse', 'HEAD') != sha:
            raise RuntimeError('GENERATED_TYPE_SOURCE_CHANGED')
        expected = git(root, 'show', sha + ':reliability-cockpit/web/next-env.d.ts') + '\n'
        actual = path.read_bytes().decode("utf-8")
        if actual == expected:
            return
        if expected.count('/// <reference path="./.next/types/routes.d.ts" />') != 1:
            raise RuntimeError('UNEXPECTED_GENERATED_TYPE_BASELINE')
        generated = re.sub(r'/// <reference path="\./\.next/types/routes\.d\.ts" />',
                           '/// <reference path="./.next-primary-dev/types/routes.d.ts" />', expected)
        if actual != generated or actual == expected:
            raise RuntimeError('UNEXPECTED_GENERATED_TYPE_EDIT')
        # No mutation if *any* other tracked/untracked/staged change exists.
        if git(root, 'status', '--porcelain') != ' M reliability-cockpit/web/next-env.d.ts':
            raise RuntimeError('UNRELATED_GENERATED_SOURCE_DIRT')
        if git(root, 'rev-parse', 'HEAD') != sha or path.read_bytes().decode('utf-8') != actual:
            raise RuntimeError('GENERATED_TYPE_SOURCE_CHANGED')
        event = {'source_sha': sha, 'root': str(root), 'at': time.time(),
                 'before_sha256': hashlib.sha256(actual.encode()).hexdigest(),
                 'after_sha256': hashlib.sha256(expected.encode()).hexdigest(),
                 'diff': ''.join(difflib.unified_diff(expected.splitlines(True), actual.splitlines(True))),
                 'original_generated_bytes': actual, 'result': 'VERIFIED_EXACT_TRANSFORMATION'}
        audit = self.c.STATE / ('frontend-generated-' + uuid.uuid4().hex + '.json')
        self.c.write_private(audit, canonical(event))
        path.write_text(expected)
        print('Audited exact Next generated type restoration: ' + audit.name)

    def wait_ready(self, sha, backend_sha, manifest):
        root = private_json(manifest)['approval']['frontend_root'] if manifest else self.c.ROOT
        identity = None
        recorded = False
        for _ in range(45):
            try:
                current = self.worker_identity(root) if manifest else None
                if identity is not None and current != identity:
                    raise RuntimeError('NEXT_WORKER_CHANGED_DURING_STARTUP')
                identity = current
                self.restore_generated_types(root, sha)
                if manifest and not recorded:
                    self.record_worker(root, manifest, identity)
                    recorded = True
                data = self.readiness(sha, backend_sha, manifest)
                if manifest and self.worker_identity(root) != identity:
                    raise RuntimeError('NEXT_WORKER_CHANGED_DURING_STARTUP')
                return data
            except RuntimeError as error:
                if str(error).startswith(('NEXT_WORKER_CHANGED', 'UNEXPECTED_GENERATED', 'UNRELATED_GENERATED', 'GENERATED_TYPE_SOURCE_CHANGED')):
                    raise
                time.sleep(1)
            except (OSError, ValueError):
                time.sleep(1)
        raise RuntimeError('FRONTEND_ONLY_STARTUP_FAILED')

    def save_pointer(self, value):
        path = self.pointer.with_name('frontend-active-' + uuid.uuid4().hex + '.json')
        self.c.write_private(path, json.dumps(value))
        os.replace(path, self.pointer)

    def restore(self, previous):
        self.c.stop_unit(self.c.UNITS[1])
        if self.c.primary_busy():
            raise RuntimeError('PRIMARY_PORT_NOT_RELEASED')
        self.web_start(previous['root'], previous['sha'], previous['manifest'])
        backend_sha = git(self.c.ROOT, 'rev-parse', 'HEAD')
        self.wait_ready(previous['sha'], backend_sha, previous['manifest'])
        if self.unit(self.c.UNITS[0]) != previous['api_unit']:
            raise RuntimeError('QA_API_CHANGED_DURING_RECOVERY')
        if previous['manifest']:
            self.save_pointer({'manifest': previous['manifest']})
        elif self.pointer.exists():
            # Preserve recovery history; only the active selection pointer changes.
            os.replace(self.pointer, self.pointer.with_name('frontend-inactive-' + uuid.uuid4().hex + '.json'))

    def select(self, root, sha, backup):
        approval, previous = self.preflight(root, sha, backup)
        token = uuid.uuid4().hex
        manifest = self.c.STATE / ('frontend-approval-' + token + '.json')
        approval_id = hashlib.sha256(canonical(approval).encode()).hexdigest()
        self.c.write_private(manifest, json.dumps({'approval': approval, 'approval_id': approval_id}))
        recovery = self.c.STATE / ('frontend-recovery-' + token + '.json')
        self.c.write_private(recovery, json.dumps({'previous': previous, 'candidate_manifest': str(manifest)}))
        try:
            self.c.stop_unit(self.c.UNITS[1])
            if self.c.primary_busy():
                raise RuntimeError('PRIMARY_PORT_NOT_RELEASED')
            if self.unit(self.c.UNITS[0]) != previous['api_unit']:
                raise RuntimeError('QA_API_CHANGED_BEFORE_FRONTEND_START')
            self.web_start(root, sha, manifest)
            self.wait_ready(sha, approval['backend_sha'], manifest)
            self.verify_owner(Path(root))
            if self.unit(self.c.UNITS[0]) != previous['api_unit']:
                raise RuntimeError('QA_API_CHANGED_DURING_FRONTEND_SELECTION')
            self.save_pointer({'manifest': str(manifest), 'recovery': str(recovery)})
        except Exception:
            self.restore(previous)
            raise
        print(json.dumps({'frontend_sha': sha, 'backend_sha': approval['backend_sha'],
                          'compatibility_approval': approval_id, 'rollback_record': str(recovery), 'origin': self.c.ORIGIN}, indent=2))

    def rollback(self, recovery):
        value = private_json(recovery)
        previous = value['previous']
        # Repeat full ownership, compatibility, backup and clean-tree preflight before mutation.
        self.select(previous['root'], previous['sha'], previous['backup'])

    def status(self):
        root, sha, manifest = self.active_source()
        data = self.request(self.c.ORIGIN + '/api/development/status', https=True)
        return {'frontend_root': str(root), 'frontend_sha': sha, 'backend_sha': data.get('backend_sha'),
                'source_sha': data.get('sha'), 'dirty': data.get('dirty'), 'stale': data.get('stale'),
                'compatibility': data.get('compatibility', 'SAME_SOURCE' if data.get('sha') == data.get('backend_sha') else 'UNVERIFIED'),
                'compatibility_approval': data.get('compatibility_approval'), 'manifest': manifest, 'worker_pid': data.get('worker_pid'),
                'parent_pid': data.get('parent_pid'), 'worker_generation': data.get('worker_generation'),
                'worker_integrity': data.get('worker_integrity', 'UNKNOWN')}
