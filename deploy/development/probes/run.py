"""Fail-stop isolated diagnostic. Never invokes the official runtime controller.

Archives only a reviewed SHA into a NEW private directory. All source changes
below are declared fixture/instrumentation variants, not application remediation.
No env file, database, operational endpoint or live worktree is used.
"""
import argparse,hashlib,io,json,os,socket,subprocess,tarfile,time
from pathlib import Path

def validate_output(value):
    path=Path(value)
    if not path.is_absolute() or '..' in path.parts or path.is_symlink() or path.exists():
        raise ValueError('Output must be a new absolute private directory')
    if path.parts[:3] != ('/','tmp','nadi-fix04-private'):
        raise ValueError('Disposable probes are confined to /tmp/nadi-fix04-private')
    # Refuse symlink ancestors as well as a symlink at the leaf.
    if any(parent.is_symlink() for parent in path.parents):
        raise ValueError('Symlink output ancestor denied')
    return path

def command(args,cwd=None):
    return subprocess.check_output(args,cwd=cwd,text=True).strip()

def write(path,data):
    path.write_text(json.dumps(data,indent=2));path.chmod(0o600)

def free_port(qa=False):
    for port in range(13100,13999) if qa else [0]:
        try:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',port));return sock.getsockname()[1]
        except OSError:
            pass
    raise RuntimeError('No free disposable loopback port')

def git_fixture(root):
    command(['git','init','-q',str(root)])
    command(['git','add','.'],root)
    command(['git','-c','user.name=Disposable fixture','-c','user.email=fixture@invalid','commit','-qm','Disposable source identity'],root)
    return command(['git','rev-parse','HEAD'],root)

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--sha',required=True);p.add_argument('--deps',required=True);p.add_argument('--output',required=True);p.add_argument('--mode',choices=['nav-poll','nav-no-poll','poll-only','nav-hmr'],required=True);p.add_argument('--seconds',type=int,default=4500);p.add_argument('--flight-graph',action='store_true');a=p.parse_args()
    repo=Path(a.repo).resolve();sha=command(['git','rev-parse',a.sha+'^{commit}'],repo)
    if not 1 <= a.seconds <= 10800:raise ValueError('Invalid bounded duration')
    if command(['/usr/bin/node-22','--version'])!='v22.23.1':raise ValueError('Exact Node22.23.1 required; no fallback')
    out=validate_output(a.output);out.mkdir(mode=0o700,parents=True,exist_ok=False)
    root=out/'runs'/'frontend';root.mkdir(parents=True);web=root/'reliability-cockpit/web';state=root.parent/'state';state.mkdir(mode=0o700)
    source=Path(__file__).resolve().parent
    archive=subprocess.check_output(['git','archive',sha,'reliability-cockpit/web'],cwd=repo)
    with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(root,filter='data')
    (root/'.gitignore').write_bytes(subprocess.check_output(['git','show',sha+':.gitignore'],cwd=repo))
    (web/'node_modules').symlink_to(Path(a.deps).resolve())
    backend=root.parent/'backend';backend.mkdir();(backend/'fixture.txt').write_text('DISPOSABLE IN MEMORY, NOT QA STORE\n');backend_sha=git_fixture(backend)
    fixture_port=free_port(qa=True);port=free_port();endpoint='http://127.0.0.1:'+str(fixture_port)
    status=web/'app/api/development/status/route.ts'
    status.write_text(status.read_text().replace('http://127.0.0.1:13036',endpoint).replace('http://127.0.0.1:8000',endpoint))
    config=web/'next.config.js';config.write_text(config.read_text()+f"\nconst originalWebpack=module.exports.webpack;module.exports.webpack=(config,options)=>{{config=originalWebpack(config,options);config.plugins.push(new(require({json.dumps(str(source/'webpack.cjs'))}))());return config;}};\n")
    if a.mode=='nav-no-poll':
        file=web/'components/DevelopmentStatus.tsx';file.write_text(file.read_text().replace('void read();const timer=setInterval(read,5000);','const timer=setInterval(()=>{},5000);setLoading(false);'))
    front_sha=git_fixture(root)
    token=os.urandom(16).hex();manifest=state/('frontend-approval-'+token+'.json');receipt=state/('frontend-worker-'+token+'.json')
    approval=dict(version=1,frontend_sha=front_sha,backend_sha=backend_sha,frontend_root=str(root),backend_root=str(backend),compatibility_digest='a'*64,launcher_sha256='b'*64,launcher_source_sha=sha,backup_sha256='c'*64,approved_at='DISPOSABLE FIXTURE ONLY')
    digest=hashlib.sha256(json.dumps(approval,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    write(manifest,dict(approval=approval,approval_id=digest))
    unit='nadi-fix04-disposable-'+a.mode+'-'+token[:6];fixture=None;browser=None;initial_worker=None;start=time.monotonic();failure=None;log=None
    probe_hashes={file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in sorted(source.iterdir()) if file.is_file() and file.suffix in ['.py','.mjs','.cjs']}
    write(out/'definition.json',dict(baseline_sha=sha,test_copy_sha=front_sha,probe_source_sha256=probe_hashes,mode=a.mode,seconds=a.seconds,node=command(['/usr/bin/node-22','--version']),heap_mib=2048,cgroup_mib=2500,cpu_percent=200,port=port,fixture_port=fixture_port,transport='DISPOSABLE HTTP LOOPBACK',unit=unit,source_changes=['fixed backend URLs to in-memory fixtures','compiler measurement plugin']+(['disable polling in disposable copy'] if a.mode=='nav-no-poll' else []),flight_graph=a.flight_graph,profiling='internal inspector sampling 512KiB; 120s; raw budget64MiB/process'))
    try:
        fixture=subprocess.Popen(['/usr/bin/node-22',str(source/'fixtures.cjs'),str(web),str(fixture_port),backend_sha],stdout=open(out/'fixture.log','w'),stderr=subprocess.STDOUT)
        env=['PATH=/usr/bin:/bin','HOME='+str(Path.home()),'NODE_ENV=development','NODE_OPTIONS=--max-old-space-size=2048 --require='+str(source/'heap.cjs'),'NEXT_TELEMETRY_DISABLED=1','NADI_PROBE_DIR='+str(out),'NADI_PRIMARY_FRONTEND=true','NADI_LIVE_DEV=true','NADI_ENGINEERING_QA_ENABLED=true','NADI_ENGINEERING_WORKSPACE_ENABLED=true','COCKPIT_API_BASE='+endpoint,'NADI_QA_BACKEND_URL='+endpoint,'NADI_DEV_FRONTEND_MANIFEST='+str(manifest),'NADI_DEV_FRONTEND_WORKER='+str(receipt),'NADI_DEV_LAUNCHED_SHA='+front_sha]
        if a.flight_graph:env.append('NADI_PROBE_FLIGHT_PATH='+str(Path(a.deps).resolve()/'next/dist/compiled/next-server/app-page.runtime.dev.js'))
        command(['systemd-run','--user','--collect','--unit='+unit,'--service-type=exec','--working-directory='+str(web),'-p','MemoryMax=2500M','-p','CPUQuota=200%','-p','TasksMax=128','-p','Restart=no','-p','UMask=0077','/usr/bin/env','-i',*env,'/usr/bin/node-22','node_modules/next/dist/bin/next','dev','--hostname','127.0.0.1','--port',str(port)])
        while time.monotonic()-start<120:
            props=dict(x.split('=',1) for x in command(['systemctl','--user','show',unit,'-p','MainPID','-p','ControlGroup','-p','InvocationID']).splitlines())
            group=Path('/sys/fs/cgroup'+props['ControlGroup'])
            for pid in (group/'cgroup.procs').read_text().split() if group.exists() else []:
                proc=Path('/proc')/pid
                if proc.exists() and b'next-server' in (proc/'cmdline').read_bytes():
                    stat=(proc/'stat').read_text().split(') ',1)[1].split();initial_worker=int(pid)
                    write(receipt,dict(approval_id=digest,worker_pid=int(pid),parent_pid=int(stat[1]),start_ticks=stat[19],generation=1,invocation_id=props['InvocationID']))
                    break
            if initial_worker:break
            time.sleep(1)
        if not initial_worker:raise RuntimeError('No initial disposable worker')
        # Exact generated transformation only, in a new disposable archive.
        original=subprocess.check_output(['git','show','HEAD:reliability-cockpit/web/next-env.d.ts'],cwd=root)
        generated=original.replace(b'./.next/types/routes.d.ts',b'./.next-primary-dev/types/routes.d.ts')
        file=web/'next-env.d.ts'
        for _ in range(60):
            if file.read_bytes()==generated:
                write(out/'generated-audit.json',dict(before=hashlib.sha256(generated).hexdigest(),after=hashlib.sha256(original).hexdigest(),scope='DISPOSABLE COPY ONLY'));file.write_bytes(original);break
            time.sleep(1)
        if file.read_bytes()!=original:raise RuntimeError('Unexpected disposable generated bytes')
        browser_log=open(out/'browser.log','w')
        browser=subprocess.Popen(['/usr/bin/node-22',str(source/'workload.mjs'),str(port),str(web),str(out),a.mode,str(a.seconds)],env={**os.environ,'NADI_PLAYWRIGHT_MODULE':'/home/john-d/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs'},stdout=browser_log,stderr=subprocess.STDOUT)
        observed=time.monotonic();log=open(out/'metrics.jsonl','a')
        while time.monotonic()-observed<a.seconds+300:
            props=dict(x.split('=',1) for x in command(['systemctl','--user','show',unit,'-p','MainPID','-p','MemoryCurrent','-p','MemoryPeak','-p','CPUUsageNSec','-p','ControlGroup','-p','ActiveState']).splitlines())
            group=Path('/sys/fs/cgroup'+props['ControlGroup']);processes=[]
            for pid in (group/'cgroup.procs').read_text().split() if group.exists() else []:
                proc=Path('/proc')/pid
                try:
                    proc_status=dict(x.split(':',1) for x in (proc/'status').read_text().splitlines() if ':' in x)
                    processes.append(dict(pid=int(pid),rss=proc_status.get('VmRSS',''),worker=b'next-server' in (proc/'cmdline').read_bytes()))
                except FileNotFoundError:pass
            workers=[x['pid'] for x in processes if x['worker']]
            available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
            log.write(json.dumps(dict(at=time.time()*1000,elapsed=time.monotonic()-observed,**props,processes=processes,events=(group/'memory.events').read_text() if group.exists() else None,memory_stat=(group/'memory.stat').read_text() if group.exists() else None,host_available=available))+'\n');log.flush()
            write(out/'progress.json',dict(elapsed=round(time.monotonic()-observed,1),workers=workers,expected_worker=initial_worker,memory_mib=round(int(props['MemoryCurrent'])/1048576,1),host_available_mib=round(available/1048576,1),browser_exit=browser.poll()))
            if workers!=[initial_worker]:failure='UNEXPECTED_WORKER_GENERATION';break
            if available<1200*1048576:failure='HOST_HEADROOM_SAFETY_STOP';break
            if browser.poll() is not None:
                if browser.returncode:failure='BROWSER_HARNESS_FAILURE'
                break
            time.sleep(5)
        write(out/'result.json',dict(failure=failure,elapsed=time.monotonic()-observed,worker=initial_worker,browser_exit=browser.poll()))
        print(json.dumps(dict(mode=a.mode,failure=failure,output=str(out))),flush=True)
    finally:
        if browser and browser.poll() is None:browser.terminate();browser.wait(timeout=30)
        subprocess.run(['journalctl','--user','-u',unit,'--no-pager','-o','short-iso'],stdout=open(out/'journal.log','w'),stderr=subprocess.DEVNULL)
        subprocess.run(['systemctl','--user','stop',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if fixture and fixture.poll() is None:fixture.terminate();fixture.wait(timeout=10)
        if log:log.close()
        for file in out.glob('*'):
            if file.is_file():file.chmod(0o600)

if __name__=='__main__':main()
