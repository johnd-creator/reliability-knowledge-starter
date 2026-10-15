"""Coordinated laptop-only source selection, through the existing nadi-dev lock.

Explicit reviewed refs, retained transition history, no checkout/reset or auto retry.
Normal edits in the selected worktree are expected and reported, not discarded.
"""
import hashlib
import json
import os
import re
import fcntl
import uuid
from contextlib import contextmanager
import ssl
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

DB = 'nadi_local_dev_01_test'
ROLE = 'nadi_local_dev_01'


def output(args, **kwargs):
    return subprocess.check_output([str(a) for a in args], text=True, timeout=30, **kwargs).strip()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def private(path):
    p = Path(path)
    st = p.lstat()
    if p.is_symlink() or not p.is_file() or st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise RuntimeError('PRIVATE_LOCAL_STATE_REQUIRED')
    return json.loads(p.read_text())


def source(root, base, sha, clean=False):
    root = Path(root)
    if root.is_symlink() or root.resolve() != root or root.parent != base:
        raise RuntimeError('EXCLUSIVE_MANAGED_SOURCE_REQUIRED')
    if not re.fullmatch('[0-9a-f]{40}', sha or '') or output(['git', 'rev-parse', 'HEAD'], cwd=root) != sha:
        raise RuntimeError('EXACT_REVIEWED_SOURCE_REQUIRED')
    if clean and output(['git', 'status', '--porcelain'], cwd=root):
        raise RuntimeError('INITIAL_CLEAN_SOURCE_REQUIRED')
    web = root / 'reliability-cockpit/web'
    if any((web / p).exists() for p in ['.env', '.env.local', '.env.development', '.env.development.local']):
        raise RuntimeError('UNREVIEWED_DOTENV_DENIED')
    return root


def old_source(root, sha):
    if output(['git', 'rev-parse', 'HEAD'], cwd=root) != sha:
        raise RuntimeError('ROLLBACK_SOURCE_CHANGED')
    paths = output(['git', 'diff', '--name-only', 'HEAD'], cwd=root).splitlines()
    if output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=root):
        raise RuntimeError('UNRELATED_ROLLBACK_EDITS')
    if paths:
        if paths != ['reliability-cockpit/web/next-env.d.ts']:
            raise RuntimeError('UNRELATED_ROLLBACK_EDITS')
        committed = subprocess.check_output(['git', 'show', sha+':'+paths[0]], cwd=root)
        actual = (Path(root) / paths[0]).read_bytes()
        if actual != committed.replace(b'./.next/types/routes.d.ts', b'./.next-primary-dev/types/routes.d.ts'):
            raise RuntimeError('UNRELATED_GENERATED_EDIT')
    return digest(Path(root) / 'reliability-cockpit/web/next-env.d.ts')


def node_pin(state):
    pin = private(state / 'frontend-runtime.json')
    node = Path(pin['node_path'])
    if (pin['node_version'] != '22.23.1' or digest(node) != pin['node_sha256'] or
            output([node, '-p', 'process.versions.node']) != '22.23.1'):
        raise RuntimeError('VERIFIED_NODE22_REQUIRED')
    for path, expected in pin['libnode_sha256'].items():
        if digest(path) != expected:
            raise RuntimeError('NODE_LIBRARY_CHANGED')
    return str(node)


class LocalDevelopment:
    def __init__(self, control):
        self.c = control
        self.state = control.STATE / 'local-dev-01'

    def save(self, name, value):
        self.c.write_private(self.state / name, json.dumps(value, indent=2))

    def unit(self, name):
        fields = 'MainPID,WorkingDirectory,ActiveState,ControlGroup,InvocationID,NRestarts'
        data = dict(line.split('=', 1) for line in output(['systemctl', '--user', 'show', name, '-p', fields]).splitlines())
        pid = data.get('MainPID', '0')
        if data.get('ActiveState') != 'active' or pid == '0':
            raise RuntimeError('OWNED_DEVELOPMENT_UNIT_REQUIRED')
        data['start_ticks'] = self.identity(int(pid))['start_ticks']
        return data

    def identity(self, pid):
        root = Path('/proc') / str(pid)
        stat = (root / 'stat').read_text().rsplit(') ', 1)[1].split()
        return {'pid': pid, 'ppid': int(stat[1]), 'start_ticks': int(stat[19]),
                'exe': os.readlink(root / 'exe'), 'cwd': os.readlink(root / 'cwd'),
                'cgroup': (root / 'cgroup').read_text().strip().split('::', 1)[1]}

    def owners(self, unit, cwd, port):
        value = self.unit(unit)
        if value['WorkingDirectory'] != str(cwd):
            raise RuntimeError('UNEXPECTED_DEVELOPMENT_CWD')
        rows = output(['ss', '-H', '-ltnpe', 'sport = :'+str(port)]).splitlines()
        if not rows:
            raise RuntimeError('EXPECTED_LISTENER_MISSING')
        identities = {}
        for row in rows:
            if row.split()[3] not in ['127.0.0.1:'+str(port), '[::1]:'+str(port)]:
                raise RuntimeError('NON_LOOPBACK_LISTENER')
            pids = re.findall(r'pid=(\d+)', row)
            if not pids:
                raise RuntimeError('UNVERIFIED_LISTENER_OWNER')
            for pid in pids:
                ident = self.identity(int(pid))
                if ident['cgroup'] != value['ControlGroup'] or ident['cwd'] != str(cwd):
                    raise RuntimeError('UNAUTHORIZED_LISTENER_OWNER')
                # Repeat identity after observation to reject PID reuse while collecting.
                if self.identity(int(pid)) != ident:
                    raise RuntimeError('LISTENER_IDENTITY_CHANGED')
                identities[pid] = ident
        inodes = re.findall(r'ino:(\d+)', '\n'.join(rows))
        if len(inodes) != len(rows):
            raise RuntimeError('LISTENER_INODE_UNVERIFIED')
        if self.unit(unit) != value:
            raise RuntimeError('DEVELOPMENT_UNIT_CHANGED_DURING_OBSERVATION')
        return {'unit': value, 'listeners': identities, 'socket_inodes': inodes}

    def request(self, url):
        context = ssl.create_default_context(cafile=str(self.c.STATE / 'localhost.pem')) if url.startswith('https:') else None
        with urlopen(url, context=context, timeout=25) as r:
            return json.load(r)

    def release(self):
        record = private(self.c.STATE / 'local-development-release.json')
        if (set(record['files']) != {'nadi-dev.py','local_development.py','local_fixture.py','frontend_preview.py'} or
                not re.fullmatch('[0-9a-f]{40}',record.get('source_sha',''))):
            raise RuntimeError('UNREVIEWED_LOCAL_CONTROLLER_RELEASE')
        for name, expected in record['files'].items():
            if digest(Path(__file__).with_name(name)) != expected:
                raise RuntimeError('LOCAL_CONTROLLER_RELEASE_CHANGED')
        return record['source_sha']

    def replace(self, name, value):
        # Exclusive temporary file plus atomic pointer replace. Immutable events use save().
        temporary = name + '.' + uuid.uuid4().hex + '.tmp'
        self.save(temporary, value)
        os.replace(self.state / temporary, self.state / name)

    @contextmanager
    def transaction(self):
        # CLI also holds the existing frontend-lifecycle.lock, shared with older commands.
        # This nested lock protects direct companion calls and deterministic simulations.
        self.state.mkdir(mode=0o700, exist_ok=True)
        info = self.state.lstat()
        if self.state.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise RuntimeError('PRIVATE_LOCAL_STATE_REQUIRED')
        fd = os.open(self.state/'selection.lock', os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError('DEVELOPMENT_LIFECYCLE_BUSY') from None
            yield
        finally:
            os.close(fd)

    def resolve(self, root, ref):
        if not ref or ref.startswith('-') or not re.fullmatch(r'[A-Za-z0-9_./-]+', ref):
            raise RuntimeError('EXPLICIT_REVIEWED_REF_REQUIRED')
        root = Path(root)
        # Validate path before using it as a git execution directory.
        if root.is_symlink() or root.resolve() != root or root.parent != self.c.BASE:
            raise RuntimeError('EXCLUSIVE_MANAGED_SOURCE_REQUIRED')
        sha = output(['git','rev-parse','--verify',ref+'^{commit}'],cwd=root)
        root = source(root,self.c.BASE,sha,clean=True)
        self.repository(root)
        return root, sha

    def repository(self, root):
        def git(*args, cwd):
            return output(['git',*args],cwd=cwd)
        common = ['rev-parse','--path-format=absolute','--git-common-dir']
        if git(*common,cwd=root) != git(*common,cwd=self.c.ROOT):
            raise RuntimeError('UNRELATED_SOURCE_REPOSITORY')
        remote = git('remote','get-url','origin',cwd=root)
        if remote not in {'https://github.com/johnd-creator/reliability-knowledge-starter.git',
                          'git@github.com:johnd-creator/reliability-knowledge-starter.git',
                          'https://github.com/johnd-creator/reliability-knowledge-starter'}:
            raise RuntimeError('UNTRUSTED_SOURCE_REPOSITORY')

    def fixture_contract(self, previous, root, sha):
        # Conservative schema/bootstrap/auth adapter compatibility, not inferred from SHA equality.
        # Changed persistence/dependencies require separate fixture compatibility preparation.
        paths = ('reliability-cockpit/application-migrations',
                 'reliability-cockpit/src/repositories',
                 'reliability-cockpit/src/services/local_authentication.py',
                 'reliability-cockpit/src/services/application_identity.py',
                 'reliability-cockpit/src/api/engineering_qa.py',
                 'reliability-cockpit/pyproject.toml',
                 'reliability-cockpit/tests/qa/live_server.py',
                 'reliability-cockpit/tests/test_condition_evidence.py',
                 'reliability-cockpit/tests/test_asset_af_mapping_admin.py',
                 'pi-collector/tests/fixtures/condition_source.py')
        hashes = {}
        for path in paths:
            a = output(['git','rev-parse',previous['sha']+':'+path],cwd=previous['root'])
            b = output(['git','rev-parse',sha+':'+path],cwd=root)
            if a != b:
                raise RuntimeError('FIXTURE_CONTRACT_CHANGE_REQUIRES_SEPARATE_APPROVAL: '+path)
            hashes[path] = b
        # The existing comparator validates required web/API contract files and dependencies.
        # Both selected applications must come from the same explicitly reviewed commit.
        return hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()

    def fixture_probe(self, value):
        # Read-only validation through the selected source, never prepare()/migration helpers.
        result = output(['/usr/bin/env','-i',*self.environment(Path(value['root'])),
                         'NADI_LOCAL_DEV_CONFIG='+value['config_path'],
                         str(self.c.STATE/'python-runtime/bin/python'),
                         str(Path(__file__).with_name('local_fixture.py')),'--check'])
        return json.loads(result)

    def previous(self):
        value = self.active_value()
        root = source(value['root'],self.c.BASE,value['sha'])
        self.repository(root)
        generated = old_source(root,value['sha'])
        data = self.readiness(value)
        if data.get('engineering_data') != 'SYNTHETIC_FIXTURES':
            raise RuntimeError('UNVERIFIED_APPLICATION_PROVENANCE')
        config_path = value.get('config_path',str(self.state/'config.json'))
        config = private(config_path)
        if config['source_root'] != str(root):
            raise RuntimeError('ACTIVE_FIXTURE_SOURCE_MISMATCH')
        return dict(value,config_path=config_path,generated_hash=generated,
                    before={'web':self.owners(self.c.UNITS[1],root/'reliability-cockpit/web',3000),
                            'api':self.owners(self.c.UNITS[0],root/'reliability-cockpit',13036)})

    def preflight(self, root, ref):
        release = self.release()
        root, sha = self.resolve(root,ref)
        if self.c.active(self.c.LEGACY_WEB):
            raise RuntimeError('COMPETING_FRONTEND')
        previous = self.previous()
        contract = self.fixture_contract(previous,root,sha)
        # Same exact source supplies frontend and API; still verify the approved contract surface exists.
        import importlib.util
        spec = importlib.util.spec_from_file_location('local_pair_compatibility',Path(__file__).with_name('frontend_preview.py'))
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        pair = module.compatible(root,root,sha,sha)
        db = self.c.db()
        if not db or not db['State']['Running'] or db['NetworkSettings']['Ports'].get('5432/tcp') != [{'HostIp':'127.0.0.1','HostPort':'15443'}]:
            raise RuntimeError('EXISTING_DEVELOPMENT_POSTGRES_REQUIRED')
        pin = node_pin(self.c.STATE)
        web = root/'reliability-cockpit/web'
        if not (web/'node_modules/next/dist/bin/next').is_file():
            raise RuntimeError('LOCKED_DEPENDENCIES_REQUIRED')
        # Installed package identity/lock, not a global npm install or automatic dependency update.
        if digest(web/'node_modules/.package-lock.json') != digest(Path(previous['root'])/'reliability-cockpit/web/node_modules/.package-lock.json'):
            raise RuntimeError('DEPENDENCY_INSTALL_CHANGED')
        for name in ['localhost.pem','localhost.key']:
            path = self.c.STATE/name; st = path.lstat()
            if path.is_symlink() or st.st_uid != os.getuid() or st.st_mode & 0o077:
                raise RuntimeError('PRIVATE_HTTPS_REQUIRED')
        output(['openssl','x509','-in',self.c.STATE/'localhost.pem','-checkend','3600','-noout'])
        output(['openssl','x509','-in',self.c.STATE/'localhost.pem','-checkhost','localhost','-noout'])
        value = {'root':str(root),'sha':sha,'backend_sha':sha,'ref':ref,'node':pin,
                 'previous':previous,'db_container_id':db['Id'],'workflow_sha':release,
                 'fixture_contract':contract,'pair_contract':pair,
                 'config_path':previous['config_path']}
        value['fixture'] = self.fixture_probe(value)
        value['config_hash'] = digest(previous['config_path'])
        value['accounts_hash'] = digest(private(previous['config_path'])['accounts_file'])
        return value

    def backup(self, value, token):
        target = self.state/('backup-'+token+'.dump')
        with target.open('xb') as stream:
            os.chmod(target,0o600)
            subprocess.run(['docker','exec',self.c.NAME,'pg_dump','-U','nadi_dev_fixture','-d',DB,'-Fc'],
                           stdout=stream,check=True,timeout=60)
        value['backup'] = str(target)
        value['backup_sha256'] = digest(target)
        value['backup_created'] = time.time()
        for unit,name in [(self.c.UNITS[1],'web.service'),(self.c.UNITS[0],'api.service')]:
            self.c.write_private(self.state/(token+'-'+name),output(['systemctl','--user','cat',unit]))
        self.validate_backup(value)

    def validate_backup(self, value):
        path = Path(value['backup']); st = path.lstat()
        if (path.parent != self.state or path.is_symlink() or st.st_uid != os.getuid() or
                st.st_mode & 0o077 or st.st_size < 1000 or not 0 <= time.time()-value['backup_created'] <= 3600 or
                digest(path) != value['backup_sha256']):
            raise RuntimeError('FRESH_PRIVATE_BACKUP_REQUIRED')
        for args in [['--list'],['--file=/dev/null']]:
            with path.open('rb') as stream:
                result = subprocess.run(['docker','exec','-i',self.c.NAME,'pg_restore',*args],
                                        stdin=stream,capture_output=True,timeout=30)
            if result.returncode or (args == ['--list'] and
                    any(name not in result.stdout for name in [b'nadi_human_record',b'nadi_application_session',b'nadi_application_migration'])):
                raise RuntimeError('BACKUP_UNREADABLE')

    def validate_recovery(self, value):
        self.release()
        previous = value['previous']
        root = source(previous['root'],self.c.BASE,previous['sha'])
        self.repository(root)
        if old_source(root,previous['sha']) != previous['generated_hash']:
            raise RuntimeError('ROLLBACK_SOURCE_CHANGED')
        if (digest(previous['config_path']) != value['config_hash'] or
                digest(private(previous['config_path'])['accounts_file']) != value['accounts_hash']):
            raise RuntimeError('ROLLBACK_CONFIG_CHANGED')
        db = self.c.db()
        if not db or not db['State']['Running'] or db['Id'] != value['db_container_id']:
            raise RuntimeError('ROLLBACK_FIXTURE_CONTAINER_CHANGED')
        node_pin(self.c.STATE)
        self.validate_backup(value)
        probe = self.fixture_probe(previous)
        if probe != value['fixture']:
            raise RuntimeError('FIXTURE_SCHEMA_OR_LEDGER_CHANGED')

    def environment(self, root):
        cockpit=Path(root)/'reliability-cockpit'
        return ['PATH='+str(self.c.STATE/'frontend-node-bin')+':/usr/bin:/bin','HOME='+str(Path.home()),'LANG=C.UTF-8',
            'PYTHONPATH='+':'.join(map(str,[cockpit,cockpit/'tests',cockpit/'tests/qa',Path(__file__).parent])),
            'PYTHONUNBUFFERED=1','NADI_LOCAL_DEV_ACK='+DB,'NADI_LOCAL_DEV_CONFIG='+str(self.state/'config.json')]

    def start(self, unit, root, command, extra, memory):
        self.c.run(['systemd-run','--user','--collect','--unit='+unit,'--service-type=exec','--working-directory='+str(root),
            '--property=Restart=no','--property=MemoryMax='+memory,'--property=CPUQuota=200%',
            '--property=TasksMax=256','--property=UMask=0077','--property=KillMode=control-group','--property=TimeoutStopSec=20',
            '/usr/bin/env','-i',*self.environment(Path(root).parents[0] if Path(root).name=='reliability-cockpit' else Path(root).parents[1]),*extra,*command])

    def start_pair(self, value):
        root=Path(value['root']);web=root/'reliability-cockpit/web'
        self.start('nadi-live-api',root/'reliability-cockpit',
            [str(self.c.STATE/'python-runtime/bin/python'),'-m','uvicorn','local_fixture:create_app','--factory','--host','127.0.0.1','--port','13036',
             '--reload','--reload-dir',str(root/'reliability-cockpit/src'),'--reload-dir',str(root/'reliability-cockpit/tests/qa'),'--no-access-log'],['NADI_LOCAL_DEV_CONFIG='+value['config_path']], '2G')
        self.start('nadi-primary-web',web,[value['node'],'node_modules/next/dist/bin/next','dev','--hostname','localhost','--port','3000',
             '--experimental-https','--experimental-https-key',str(self.c.STATE/'localhost.key'),'--experimental-https-cert',str(self.c.STATE/'localhost.pem')],
            ['NODE_ENV=development','NEXT_TELEMETRY_DISABLED=1','NODE_OPTIONS=--max-old-space-size=4096',
             'NADI_LIVE_DEV=true','NADI_PRIMARY_FRONTEND=true','NADI_ENGINEERING_WORKSPACE_ENABLED=true',
             'NADI_ENGINEERING_DEMO_ENABLED=true','NADI_ENGINEERING_QA_ENABLED=true','NADI_QA_BACKEND_URL=http://127.0.0.1:13036',
             'COCKPIT_API_BASE=http://127.0.0.1:8000','NADI_DEV_LAUNCHED_SHA='+value['sha']], '6G')

    def readiness(self, value):
        root = source(value['root'],self.c.BASE,value['sha'])
        front = self.owners(self.c.UNITS[1],root/'reliability-cockpit/web',3000)
        api = self.owners(self.c.UNITS[0],root/'reliability-cockpit',13036)
        python = str((self.c.STATE/'python-runtime/bin/python').resolve())
        if any(r['exe'] != python for r in api['listeners'].values()):
            raise RuntimeError('BACKEND_EXECUTABLE_CHANGED')
        if any(r['exe'] != value['node'] for r in front['listeners'].values()):
            raise RuntimeError('FRONTEND_NODE_PIN_CHANGED')
        if value.get('expected_web') and front != value['expected_web']:
            raise RuntimeError('UNEXPECTED_FRONTEND_PROCESS_OR_LISTENER_REPLACEMENT')
        if value.get('expected_api_parent') and self.unit(self.c.UNITS[0]) != value['expected_api_parent']:
            raise RuntimeError('UNEXPECTED_API_PARENT_REPLACEMENT')
        backend = self.request('http://127.0.0.1:13036/development/status')
        data = self.request(self.c.ORIGIN+'/api/development/status')
        sha = value['sha']
        if (data.get('sha') != sha or data.get('backend_sha') != sha or data.get('launched_sha') != sha or
                backend.get('source_sha') != sha or backend.get('current_sha') != sha or
                backend.get('bootstrap_sha') != value['workflow_sha'] or
                backend.get('source') != 'SYNTHETIC_LOCAL_DEVELOPMENT' or
                backend.get('database') != 'DISPOSABLE_TEST' or backend.get('environment') != 'DEVELOPMENT' or
                data.get('stale') is not False or data.get('database_identity') != DB or
                backend.get('database_identity') != DB or data.get('backend') != 'AVAILABLE' or
                data.get('factual_backend') != 'AVAILABLE' or not data.get('engineering')):
            raise RuntimeError('LOCAL_PAIR_NOT_READY')
        # Dirty source remains visible; it is never coerced to clean or discarded.
        return data

    def wait_ready(self, value):
        deadline = time.monotonic()+120
        while True:
            try:
                return self.readiness(value)
            except RuntimeError as error:
                if str(error) not in {'EXPECTED_LISTENER_MISSING','LOCAL_PAIR_NOT_READY'}:
                    raise
                if time.monotonic() >= deadline:
                    raise
            except OSError:
                if time.monotonic() >= deadline:
                    raise
            time.sleep(1)

    def attest(self, value):
        value['expected_web'] = self.owners(self.c.UNITS[1],Path(value['root'])/'reliability-cockpit/web',3000)
        value['expected_api_parent'] = self.unit(self.c.UNITS[0])

    def failure(self, token, error):
        code = str(error).split(':',1)[0]
        self.save(token+'-failed.json',{'id':token,'outcome':'FAILED','error_type':type(error).__name__,
                                      'code':code if re.fullmatch('[A-Z_]+',code) else 'PRIVATE_DIAGNOSTIC_REQUIRED'})

    def select(self, root, ref):
        # Identity is allocated even for rejected attempts; no deletion enables another attempt.
        self.state.mkdir(mode=0o700,exist_ok=True)
        info = self.state.lstat()
        if self.state.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise RuntimeError('PRIVATE_LOCAL_STATE_REQUIRED')
        token = 'selection-'+uuid.uuid4().hex
        self.save(token+'-requested.json',{'id':token,'candidate':str(root),'ref':ref,'at':time.time(),
                                         'before':self.active_value()['sha'],'after':'UNRESOLVED',
                                         'outcome':'REQUESTED','rollback':None})
        try:
            with self.transaction():
                self._select(root,ref,token)
        except Exception as error:
            self.failure(token,error)
            raise

    def _select(self, root, ref, token):
        value = self.preflight(root,ref)
        self.backup(value,token)
        again = self.preflight(root,ref)
        if again != {k:v for k,v in value.items() if k not in {'backup','backup_sha256','backup_created'}}:
            raise RuntimeError('BASELINE_CHANGED_BEFORE_TRANSITION')
        self.validate_recovery(value)
        self.save(token+'-prepared.json',value)
        config = private(value['previous']['config_path'])
        config.update(source_root=value['root'],workflow_sha=value['workflow_sha'])
        self.save(token+'-config.json',config)
        value['config_path'] = str(self.state/(token+'-config.json'))
        value['transition_id'] = token
        self.save(token+'-stopping.json',{'before':value['previous']['sha'],'after':value['sha'],
                                       'rollback':token+'-prepared.json'})
        source(root,self.c.BASE,value['sha'],clean=True)
        for key,unit,suffix,port in [('web',self.c.UNITS[1],'reliability-cockpit/web',3000),
                                     ('api',self.c.UNITS[0],'reliability-cockpit',13036)]:
            if self.owners(unit,Path(value['previous']['root'])/suffix,port) != value['previous']['before'][key]:
                raise RuntimeError('BASELINE_CHANGED_BEFORE_TRANSITION')
        try:
            self.c.stop_unit(self.c.UNITS[1]); self.c.stop_unit(self.c.UNITS[0])
            if self.c.primary_busy():
                raise RuntimeError('PORT_NOT_RELEASED')
            self.start_pair(value)
            data = self.wait_ready(value)
            self.attest(value)
            self.save(token+'-accepted.json',{'id':token,'before':value['previous']['sha'],
                                           'after':value['sha'],'outcome':'READY','rollback':token+'-prepared.json'})
            self.replace('active.json',value)
            print(json.dumps({'status':'READY','frontend_sha':value['sha'],'backend_sha':value['sha'],
                              'database':DB,'origin':self.c.ORIGIN,'transition':token}))
        except Exception:
            # One recovery only, never retry candidate startup. Keep all evidence on failure.
            self._recover(value,token+'-failure')
            raise

    def _recover(self, value, token):
        self.validate_recovery(value)
        previous = dict(value['previous'])
        # Existing old-format expected PIDs describe the process before stop, not restored ones.
        previous.pop('expected_web',None); previous.pop('expected_api_parent',None)
        for unit,port,suffix in [(self.c.UNITS[1],3000,'reliability-cockpit/web'),
                                 (self.c.UNITS[0],13036,'reliability-cockpit')]:
            if self.c.active(unit):
                current = self.unit(unit)
                roots = [Path(value['root'])/suffix,Path(previous['root'])/suffix]
                if current['WorkingDirectory'] not in {str(p) for p in roots}:
                    raise RuntimeError('UNEXPECTED_RECOVERY_UNIT_OWNER')
                # Known unit alone is insufficient: every extant socket must be owned.
                try:
                    self.owners(unit,Path(current['WorkingDirectory']),port)
                except RuntimeError as error:
                    if str(error) != 'EXPECTED_LISTENER_MISSING':
                        raise
        # All extant units/listeners are validated before stopping either process.
        for unit in (self.c.UNITS[1],self.c.UNITS[0]):
            self.c.stop_unit(unit)
        if self.c.primary_busy():
            raise RuntimeError('PORT_NOT_RELEASED')
        self.start_pair(previous)
        self.wait_ready(previous)
        self.attest(previous)
        self.save(token+'-recovered.json',{'outcome':'ROLLED_BACK','source':previous['sha'],
                                        'backup':value['backup'],'data_restored_or_deleted':False})
        self.replace('active.json',previous)

    def recover(self, value):
        if 'previous' not in value:
            raise RuntimeError('REUSABLE_RECOVERY_RECORD_REQUIRED: historical recovery artifacts retained')
        token = 'rollback-'+uuid.uuid4().hex
        self.save(token+'-requested.json',{'outcome':'REQUESTED','source':value['sha']})
        try:
            with self.transaction():
                if self.active_value() != value:
                    raise RuntimeError('ACTIVE_SELECTION_CHANGED')
                self.readiness(value)
                recovery = dict(value)
                self.backup(recovery,token)
                self.save(token+'-prepared.json',recovery)
                self._recover(recovery,token)
        except Exception as error:
            self.failure(token,error)
            raise

    def active_value(self):
        return private(self.state/'active.json')

    def status(self):
        self.release()
        return self.readiness(self.active_value())
