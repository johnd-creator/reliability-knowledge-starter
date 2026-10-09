#!/usr/bin/env python3
"""Explicit laptop-only supervisor. Never sources dotenv or operational configuration."""
import argparse
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT.parent
STATE = BASE / 'state'
NAME = 'nadi-dev-live-postgres'
UNITS = ('nadi-live-api.service', 'nadi-live-web.service')

def run(args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def load():
    p=STATE/'config.json'; info=p.lstat()
    if p.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise RuntimeError('PRIVATE_CONFIG_REQUIRED')
    return json.loads(p.read_text())

def db():
    result=subprocess.run(['docker','inspect',NAME],capture_output=True,text=True)
    if result.returncode:return None
    value=json.loads(result.stdout)[0]
    if value['Config']['Labels'].get('nadi.scope')!='disposable-laptop-development':
        raise RuntimeError('UNEXPECTED_DATABASE_CONTAINER')
    return value

def write_private(path, data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:f.write(data)

def setup():
    STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
    if (STATE/'config.json').exists():
        load();print('Existing private configuration retained');return
    if db():raise RuntimeError('UNTRACKED_DEVELOPMENT_DATABASE')
    password=secrets.token_urlsafe(32)
    accounts={name:{'username':'fixture-'+name,'password':secrets.token_urlsafe(24)} for name in ('admin','engineer','reviewer')}
    write_private(STATE/'accounts.json',json.dumps(accounts,indent=2))
    write_private(STATE/'postgres.env','POSTGRES_DB=nadi_live_dev_test\nPOSTGRES_USER=nadi_dev_fixture\nPOSTGRES_PASSWORD='+password+'\n')
    config={'application_dsn':'postgresql+psycopg://nadi_dev_fixture:'+password+'@127.0.0.1:15443/nadi_live_dev_test',
            'accounts_file':str(STATE/'accounts.json')}
    write_private(STATE/'config.json',json.dumps(config,indent=2))
    (STATE/'attachments').mkdir(mode=0o700,exist_ok=True)
    (STATE/'postgres-data').mkdir(mode=0o700,exist_ok=True)
    run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',STATE/'localhost.key','-out',STATE/'localhost.pem',
         '-days','365','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost,IP:127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    os.chmod(STATE/'localhost.key',0o600)
    os.chmod(STATE/'localhost.pem',0o600)
    print('Private disposable configuration generated; no credentials printed')

def common_env():
    return ['PATH=/home/linuxbrew/.linuxbrew/bin:/usr/local/bin:/usr/bin:/bin',
            'HOME='+str(Path.home()),'LANG=C.UTF-8','COCKPIT_CONFIG_MODE=managed',
            'PYTHONPATH='+str(ROOT/'reliability-cockpit')+':'+str(ROOT/'reliability-cockpit/tests'),
            'PYTHONUNBUFFERED=1','NADI_DISPOSABLE_QA_ACK=persistent-laptop-fixture',
            'NADI_DEV_CONFIG='+str(STATE/'config.json'),'NADI_DEV_LAUNCHED_SHA='+git('rev-parse','HEAD')]

def start_unit(name, cwd, command, extra=()):
    run(['systemd-run','--user','--collect','--unit='+name,'--service-type=exec',
         '--working-directory='+str(cwd),'--property=Restart=on-failure',
         '--property=RestartSec=3','--property=MemoryMax=2500M','--property=CPUQuota=200%',
         '--property=TasksMax=128','--property=UMask=0077','--property=TimeoutStopSec=20',
         '/usr/bin/env','-i',*common_env(),*extra,*command])

def active(unit):
    return subprocess.run(['systemctl','--user','is-active','--quiet',unit]).returncode==0

def start():
    load()
    required=['reliability-cockpit/tests/qa/live_server.py','reliability-cockpit/web/components/DevelopmentStatus.tsx']
    if any(not (ROOT/p).is_file() for p in required):raise RuntimeError('SELECTED_REF_MISSING_DEVELOPMENT_FOUNDATION')
    if any((ROOT/'reliability-cockpit/web'/p).exists() for p in ['.env','.env.local','.env.development','.env.development.local']):raise RuntimeError('UNREVIEWED_DOTENV_CONFIGURATION_DENIED')
    if any(active(u) for u in UNITS):raise RuntimeError('PREVIEW_ALREADY_RUNNING_USE_STATUS_OR_RELOAD')
    value=db()
    if value is None:
        run(['docker','run','-d','--name',NAME,'--label','nadi.scope=disposable-laptop-development',
            '--restart','no','--cpus','1','--memory','512m','--pids-limit','128','--shm-size','128m',
            '-p','127.0.0.1:15443:5432','--env-file',STATE/'postgres.env',
            '-v',str(STATE/'postgres-data')+':/var/lib/postgresql/data:Z','postgres:16.4-alpine'],stdout=subprocess.DEVNULL)
    elif not value['State']['Running']:run(['docker','start',NAME],stdout=subprocess.DEVNULL)
    for _ in range(30):
        if subprocess.run(['docker','exec',NAME,'pg_isready','-U','nadi_dev_fixture','-d','nadi_live_dev_test'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
        time.sleep(1)
    else:raise RuntimeError('DEVELOPMENT_DATABASE_NOT_READY')
    python=STATE/'python-runtime/bin/python'
    start_unit('nadi-live-api',ROOT/'reliability-cockpit',[str(python),'-m','uvicorn','live_server:create_live_app','--app-dir','tests/qa',
          '--factory','--host','127.0.0.1','--port','13036','--reload','--reload-dir','src','--reload-dir','tests/qa','--no-access-log'])
    start_unit('nadi-live-web',ROOT/'reliability-cockpit/web',
        ['/home/linuxbrew/.linuxbrew/bin/node','node_modules/next/dist/bin/next','dev','--hostname','localhost','--port','13035',
         '--experimental-https','--experimental-https-key',str(STATE/'localhost.key'),'--experimental-https-cert',str(STATE/'localhost.pem')],
        ['NODE_ENV=development','NEXT_TELEMETRY_DISABLED=1','NODE_OPTIONS=--max-old-space-size=2048',
         'NADI_LIVE_DEV=true','NADI_ENGINEERING_WORKSPACE_ENABLED=true','NADI_ENGINEERING_DEMO_ENABLED=true',
         'NADI_ENGINEERING_QA_ENABLED=true','NADI_QA_BACKEND_URL=http://127.0.0.1:13036','COCKPIT_API_BASE=http://127.0.0.1:8000'])
    print('Started development only: https://localhost:13035; backend 127.0.0.1:13036')

def stop():
    run(['systemctl','--user','stop',*UNITS],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    value=db()
    if value and value['State']['Running']:run(['docker','stop',NAME],stdout=subprocess.DEVNULL)
    print('Development stopped; database files retained')

def status():
    print(json.dumps({'branch':git('branch','--show-current') or 'DETACHED','source_sha':git('rev-parse','HEAD'),
        'dirty':bool(git('status','--porcelain')),'services':{u:active(u) for u in UNITS},
        'database':'DISPOSABLE_TEST_RUNNING' if (db() or {}).get('State',{}).get('Running') else 'STOPPED_OR_ABSENT'},indent=2))

def switch(ref):
    if any(active(u) for u in UNITS):raise RuntimeError('STOP_PREVIEW_BEFORE_SWITCH')
    if git('status','--porcelain'):raise RuntimeError('DIRTY_WORKTREE_SWITCH_DENIED')
    git('rev-parse','--verify',ref+'^{commit}')
    # Operator chooses the reviewed ref; no implicit fetch/pull/reset/rebase.
    run(['git','switch','--detach',ref],cwd=ROOT)
    print('Selected reviewed ref; run start after dependency/migration compatibility review')

def backup():
    value=db()
    if not value or not value['State']['Running']:raise RuntimeError('START_DEVELOPMENT_DATABASE_FIRST')
    target=STATE/('backup-'+time.strftime('%Y%m%d-%H%M%S')+'.dump')
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:run(['docker','exec',NAME,'pg_dump','-U','nadi_dev_fixture','-d','nadi_live_dev_test','-Fc'],stdout=f)
    print('Private development backup created:',target)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['setup','start','status','logs','stop','reload','switch','backup'])
    parser.add_argument('ref',nargs='?');args=parser.parse_args()
    if args.command=='switch':
        if not args.ref:parser.error('switch requires an explicitly reviewed ref')
        switch(args.ref)
    elif args.command=='reload':stop();start()
    elif args.command=='logs':run(['journalctl','--user','-u',UNITS[0],'-u',UNITS[1],'-n','80','--no-pager'])
    else:globals()[args.command]()
if __name__=='__main__':
    try:main()
    except Exception:sys.exit('DEVELOPMENT_COMMAND_FAILED: inspect private service logs; no automatic retry')
