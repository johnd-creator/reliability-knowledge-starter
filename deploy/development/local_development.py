"""Coordinated laptop-only source selection, through the existing nadi-dev lock.

One explicit transition, fail closed preflight, no checkout/reset, no auto retry.
Normal edits in the selected worktree are expected and reported, not discarded.
"""
import hashlib
import json
import os
import re
import shutil
import ssl
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

SHA = '9895890a045a221998856a175d80c17270cd0d38'
DB = 'nadi_local_dev_01_test'
ROLE = 'nadi_local_dev_01'


def output(args, **kwargs):
    return subprocess.check_output([str(a) for a in args], text=True, timeout=30, **kwargs).strip()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def private(path):
    p = Path(path)
    st = p.lstat()
    if p.is_symlink() or st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise RuntimeError('PRIVATE_LOCAL_STATE_REQUIRED')
    return json.loads(p.read_text())


def source(root, base, clean=False):
    root = Path(root)
    if root.is_symlink() or root.resolve() != root or root.parent != base:
        raise RuntimeError('EXCLUSIVE_MANAGED_SOURCE_REQUIRED')
    if output(['git', 'rev-parse', 'HEAD'], cwd=root) != SHA:
        raise RuntimeError('EXACT_PR82_SOURCE_REQUIRED')
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
                identities[pid] = ident
        inodes = re.findall(r'ino:(\d+)', '\n'.join(rows))
        if len(inodes) != len(rows):
            raise RuntimeError('LISTENER_INODE_UNVERIFIED')
        return {'unit': value, 'listeners': identities, 'socket_inodes': inodes}

    def request(self, url):
        context = ssl.create_default_context(cafile=str(self.c.STATE / 'localhost.pem')) if url.startswith('https:') else None
        with urlopen(url, context=context, timeout=25) as r:
            return json.load(r)

    def release(self):
        record = private(self.c.STATE / 'local-development-release.json')
        for name, expected in record['files'].items():
            if digest(Path(__file__).with_name(name)) != expected:
                raise RuntimeError('LOCAL_CONTROLLER_RELEASE_CHANGED')
        return record['source_sha']

    def preflight(self, root):
        self.release()
        root = source(root, self.c.BASE, clean=True)
        if output(['git', 'rev-parse', '--git-common-dir'], cwd=root) != output(['git', 'rev-parse', '--git-common-dir'], cwd=self.c.ROOT):
            raise RuntimeError('UNRELATED_SOURCE_REPOSITORY')
        if (self.state / 'transition.json').exists():
            raise RuntimeError('ONE_TRANSITION_ALREADY_USED')
        if self.c.active(self.c.LEGACY_WEB):
            raise RuntimeError('COMPETING_FRONTEND')
        front = self.c.frontend_controller()
        previous, previous_sha, manifest = front.active_source()
        generated_hash = old_source(previous, previous_sha)
        if output(['git', 'status', '--porcelain'], cwd=self.c.ROOT):
            raise RuntimeError('ROLLBACK_API_SOURCE_DIRTY')
        before = {'web': self.owners(self.c.UNITS[1], previous/'reliability-cockpit/web', 3000),
                  'api': self.owners(self.c.UNITS[0], self.c.ROOT/'reliability-cockpit', 13036)}
        db = self.c.db()
        if not db or not db['State']['Running'] or db['NetworkSettings']['Ports'].get('5432/tcp') != [{'HostIp':'127.0.0.1','HostPort':'15443'}]:
            raise RuntimeError('EXISTING_DEVELOPMENT_POSTGRES_REQUIRED')
        backend = self.request('http://127.0.0.1:13036/development/status')
        if backend.get('source_sha') != self.c.git('rev-parse', 'HEAD') or backend.get('database_identity') != 'nadi_live_dev_test':
            raise RuntimeError('ROLLBACK_API_IDENTITY_UNVERIFIED')
        pin = node_pin(self.c.STATE)
        web = root/'reliability-cockpit/web'
        if not (web/'node_modules/next/dist/bin/next').is_file():
            raise RuntimeError('LOCKED_DEPENDENCIES_REQUIRED')
        for name in ['localhost.pem','localhost.key']:
            st=(self.c.STATE/name).lstat()
            if st.st_uid != os.getuid() or st.st_mode & 0o077 or (self.c.STATE/name).is_symlink():
                raise RuntimeError('PRIVATE_HTTPS_REQUIRED')
        output(['openssl','x509','-in',self.c.STATE/'localhost.pem','-checkend','3600','-noout'])
        output(['openssl','x509','-in',self.c.STATE/'localhost.pem','-checkhost','localhost','-noout'])
        return {'root':str(root),'sha':SHA,'node':pin,'backend_sha':SHA,'before':before,
                'previous_root':str(previous),'previous_sha':previous_sha,'previous_manifest':manifest,
                'previous_backend_sha':backend['source_sha'],'old_generated_hash':generated_hash,
                'db_container_id':db['Id'],'workflow_sha':self.release()}

    def fingerprint(self):
        # Only the historical development store; return digests/counts, never rows.
        args=['docker','exec',self.c.NAME,'psql','-XAt','-U','nadi_dev_fixture','-d','nadi_live_dev_test','-c']
        tables=output([*args,"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"]).splitlines()
        if not tables or any(not re.fullmatch('[a-z_]+',name) for name in tables):
            raise RuntimeError('UNEXPECTED_FIXTURE_TABLES')
        rows={}
        for name in tables:
            sql=f"SELECT count(*)::text||':'||md5(coalesce(string_agg(v,'' ORDER BY v),'')) FROM (SELECT md5(row_to_json(t)::text) v FROM {name} t) q"
            rows[name]=output([*args,sql])
        rows['constraints']=hashlib.sha256(output([*args,"SELECT conname,pg_get_constraintdef(oid) FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY conname"]).encode()).hexdigest()
        return rows

    def backup(self, snapshot):
        # Fresh original-store backup; never run a migration/restore against it.
        target = self.state/'original-qa.dump'
        with target.open('xb') as stream:
            os.chmod(target,0o600)
            subprocess.run(['docker','exec',self.c.NAME,'pg_dump','-U','nadi_dev_fixture','-d','nadi_live_dev_test','-Fc'],stdout=stream,check=True,timeout=60)
        for args in [['--list'],['--file=/dev/null']]:
            with target.open('rb') as stream:
                result=subprocess.run(['docker','exec','-i',self.c.NAME,'pg_restore',*args],stdin=stream,capture_output=True,timeout=30)
            if result.returncode or (args==['--list'] and (b'nadi_human_record' not in result.stdout or b'nadi_application_session' not in result.stdout)):
                raise RuntimeError('BACKUP_UNREADABLE')
        snapshot['backup_sha256']=digest(target)
        self.save('original-db-fingerprint.json',self.fingerprint())
        for unit,name in [(self.c.UNITS[1],'previous-web.service'),(self.c.UNITS[0],'previous-api.service')]:
            self.c.write_private(self.state/name,output(['systemctl','--user','cat',unit]))
        self.c.write_private(self.state/'original-next-env.diff', output(['git','diff','--binary'],cwd=snapshot['previous_root']))
        for name in ['config.json','accounts.json','frontend-active.json','controller-release.json','controller.py','frontend_preview.py']:
            destination=self.state/('original-'+name)
            self.c.write_private(destination,(self.c.STATE/name).read_text())
        self.save('baseline.json',snapshot)

    def environment(self, root):
        cockpit=Path(root)/'reliability-cockpit'
        return ['PATH='+str(self.c.STATE/'frontend-node-bin')+':/usr/bin:/bin','HOME='+str(Path.home()),'LANG=C.UTF-8',
            'PYTHONPATH='+':'.join(map(str,[cockpit,cockpit/'tests',cockpit/'tests/qa',Path(__file__).parent])),
            'PYTHONUNBUFFERED=1','NADI_LOCAL_DEV_ACK='+DB,'NADI_LOCAL_DEV_CONFIG='+str(self.state/'config.json')]

    def create_fixture(self, value):
        # Only a new named fixture DB/role on the already verified laptop container.
        import secrets
        password=secrets.token_urlsafe(32)
        sql=("SELECT 1 FROM pg_database WHERE datname='"+DB+"' UNION ALL SELECT 1 FROM pg_roles WHERE rolname='"+ROLE+"';")
        exists=output(['docker','exec',self.c.NAME,'psql','-XAt','-U','nadi_dev_fixture','-d','postgres','-c',sql])
        if exists:
            raise RuntimeError('FIXTURE_NAME_ALREADY_EXISTS_PRESERVE_IT')
        sql=(f"CREATE ROLE {ROLE} LOGIN PASSWORD '{password}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;\n"
             f"CREATE DATABASE {DB} OWNER {ROLE};\nREVOKE ALL ON DATABASE {DB} FROM PUBLIC;\n")
        created=subprocess.run(['docker','exec','-i',self.c.NAME,'psql','-Xq','-v','ON_ERROR_STOP=1','-U','nadi_dev_fixture','-d','postgres'],input=sql,text=True,capture_output=True,timeout=30)
        if created.returncode:raise RuntimeError('NEW_FIXTURE_CREATION_FAILED_PRIVATE_EVIDENCE_RETAINED')
        config={'application_dsn':f'postgresql+psycopg://{ROLE}:{password}@127.0.0.1:15443/{DB}',
                'accounts_file':str(self.state/'accounts.json'),'source_root':value['root'],'workflow_sha':value['workflow_sha']}
        self.save('config.json',config)
        subprocess.run(['/usr/bin/env','-i',*self.environment(value['root']),str(self.c.STATE/'python-runtime/bin/python'),
                        str(Path(__file__).with_name('local_fixture.py'))],check=True,timeout=60)

    def start(self, unit, root, command, extra, memory):
        self.c.run(['systemd-run','--user','--collect','--unit='+unit,'--service-type=exec','--working-directory='+str(root),
            '--property=Restart=no','--property=MemoryMax='+memory,'--property=CPUQuota=200%',
            '--property=TasksMax=256','--property=UMask=0077','--property=KillMode=control-group','--property=TimeoutStopSec=20',
            '/usr/bin/env','-i',*self.environment(Path(root).parents[0] if Path(root).name=='reliability-cockpit' else Path(root).parents[1]),*extra,*command])

    def start_pair(self, value):
        root=Path(value['root']);web=root/'reliability-cockpit/web'
        self.start('nadi-live-api',root/'reliability-cockpit',
            [str(self.c.STATE/'python-runtime/bin/python'),'-m','uvicorn','local_fixture:create_app','--factory','--host','127.0.0.1','--port','13036',
             '--reload','--reload-dir',str(root/'reliability-cockpit/src'),'--reload-dir',str(root/'reliability-cockpit/tests/qa'),'--no-access-log'],[], '2G')
        self.start('nadi-primary-web',web,[value['node'],'node_modules/next/dist/bin/next','dev','--hostname','localhost','--port','3000',
             '--experimental-https','--experimental-https-key',str(self.c.STATE/'localhost.key'),'--experimental-https-cert',str(self.c.STATE/'localhost.pem')],
            ['NODE_ENV=development','NEXT_TELEMETRY_DISABLED=1','NODE_OPTIONS=--max-old-space-size=4096',
             'NADI_LIVE_DEV=true','NADI_PRIMARY_FRONTEND=true','NADI_ENGINEERING_WORKSPACE_ENABLED=true',
             'NADI_ENGINEERING_DEMO_ENABLED=true','NADI_ENGINEERING_QA_ENABLED=true','NADI_QA_BACKEND_URL=http://127.0.0.1:13036',
             'COCKPIT_API_BASE=http://127.0.0.1:8000','NADI_DEV_LAUNCHED_SHA='+SHA], '6G')

    def readiness(self, value):
        root=source(value['root'],self.c.BASE)
        front=self.owners(self.c.UNITS[1],root/'reliability-cockpit/web',3000)
        self.owners(self.c.UNITS[0],root/'reliability-cockpit',13036)
        if any(r['exe'] != value['node'] for r in front['listeners'].values()):
            raise RuntimeError('FRONTEND_NODE_PIN_CHANGED')
        if value.get('expected_web') and front != value['expected_web']:
            raise RuntimeError('UNEXPECTED_FRONTEND_PROCESS_OR_LISTENER_REPLACEMENT')
        if value.get('expected_api_parent') and self.unit(self.c.UNITS[0]) != value['expected_api_parent']:
            raise RuntimeError('UNEXPECTED_API_PARENT_REPLACEMENT')
        data=self.request(self.c.ORIGIN+'/api/development/status')
        if (data.get('sha')!=SHA or data.get('backend_sha')!=SHA or data.get('launched_sha')!=SHA or data.get('stale') is not False
                or data.get('database_identity')!=DB or data.get('backend')!='AVAILABLE' or not data.get('engineering')):
            raise RuntimeError('LOCAL_PAIR_NOT_READY')
        return data

    def select(self, root):
        self.state.mkdir(mode=0o700,exist_ok=True)
        value=self.preflight(root)
        self.backup(value)
        self.create_fixture(value)
        # Recheck exact original ownership and source after preparation, before any stop.
        again=self.preflight(root)
        if again['before']!=value['before'] or again['old_generated_hash']!=value['old_generated_hash']:
            raise RuntimeError('BASELINE_CHANGED_BEFORE_TRANSITION')
        self.save('transition.json',{'state':'ATTEMPT_STARTED','value':value})
        try:
            self.c.stop_unit(self.c.UNITS[1]);self.c.stop_unit(self.c.UNITS[0])
            if self.c.primary_busy():raise RuntimeError('PORT_NOT_RELEASED')
            self.start_pair(value)
            deadline=time.monotonic()+120
            while True:
                # Poll readiness only; never retry starting a process or replace a worker.
                try:
                    data=self.readiness(value)
                    break
                except RuntimeError as error:
                    if str(error) not in {'EXPECTED_LISTENER_MISSING', 'LOCAL_PAIR_NOT_READY'}:raise
                    if time.monotonic()>=deadline:raise
                    time.sleep(1)
                except OSError:
                    if time.monotonic()>=deadline:raise
                    time.sleep(1)
            value['expected_web']=self.owners(self.c.UNITS[1],Path(value['root'])/'reliability-cockpit/web',3000)
            value['expected_api_parent']=self.unit(self.c.UNITS[0])
            self.save('active.json',value)
            self.save('acceptance-start.json',data)
            print(json.dumps({'status':'READY','origin':self.c.ORIGIN,'frontend_sha':SHA,'backend_sha':SHA,'database':DB}))
        except Exception:
            self.recover(value)
            raise

    def recover(self, value):
        # Recover the preserved pair. No database restore/reset or source edit.
        for unit,cwd in [(self.c.UNITS[1],Path(value['root'])/'reliability-cockpit/web'),(self.c.UNITS[0],Path(value['root'])/'reliability-cockpit')]:
            if self.c.active(unit):
                current=self.unit(unit)
                old=Path(value['previous_root'])/'reliability-cockpit/web' if unit==self.c.UNITS[1] else self.c.ROOT/'reliability-cockpit'
                if current['WorkingDirectory'] not in {str(cwd),str(old)}:
                    raise RuntimeError('UNEXPECTED_RECOVERY_UNIT_OWNER')
            self.c.stop_unit(unit)
        old_source(Path(value['previous_root']),value['previous_sha'])
        self.c.api_start()
        self.c.frontend_controller().web_start(Path(value['previous_root']),value['previous_sha'],value['previous_manifest'])
        deadline=time.monotonic()+90
        while True:
            try:
                self.owners(self.c.UNITS[1],Path(value['previous_root'])/'reliability-cockpit/web',3000)
                api=self.request('http://127.0.0.1:13036/development/status')
                if api.get('source_sha')!=value['previous_backend_sha'] or api.get('database_identity')!='nadi_live_dev_test':
                    raise RuntimeError('ROLLBACK_API_NOT_READY')
                break
            except Exception:
                if time.monotonic()>=deadline:raise
                time.sleep(1)
        active=self.state/'active.json'
        if active.exists():
            os.replace(active,self.state/'rolled-back-active.json')
        self.save('rollback-complete.json',{'previous_frontend_sha':value['previous_sha'],'previous_backend_sha':value['previous_backend_sha']})

    def active_value(self):
        return private(self.state/'active.json')

    def status(self):
        return self.readiness(self.active_value())
