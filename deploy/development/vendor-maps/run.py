"""FIX-06 disposable controller. Never calls the official development launcher."""
import argparse,hashlib,importlib.util,io,json,os,re,signal,subprocess,tarfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fixture_tools',HERE.parent/'probes/run.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
guard_spec=importlib.util.spec_from_file_location('pid_guard',HERE/'process_guard.py')
pid_guard=importlib.util.module_from_spec(guard_spec);guard_spec.loader.exec_module(pid_guard)

def private_output(value):
    p=Path(value)
    if len(p.parts) <= 3 or not p.is_absolute() or '..' in p.parts or p.exists() or any(x.is_symlink() for x in [p,*p.parents]) or p.parts[:3]!=('/','tmp','nadi-fix06-private'):
        raise ValueError('New private FIX06 output required')
    return p

def verify_source(root,sha):
    if helper.command(['git','rev-parse','HEAD'],root)!=sha:raise RuntimeError('PROVENANCE_MISMATCH')
    if helper.command(['git','diff','--cached','--name-only'],root):raise RuntimeError('PROVENANCE_MISMATCH')
    dirty=helper.command(['git','diff','--name-only','HEAD'],root).splitlines()
    allowed={'reliability-cockpit/web/components/DevelopmentStatus.tsx','reliability-cockpit/web/app/fix06-debug/Client.tsx'}
    if set(dirty)-allowed:raise RuntimeError('PROVENANCE_MISMATCH')
    for relative in dirty:
        original=subprocess.check_output(['git','show','HEAD:'+relative],cwd=root).decode()
        actual=(root/relative).read_text()
        normalized=re.sub(r'<span>DEV PROBE [0-9]{1,3}</span>','<span>DEV</span>',actual) if relative.endswith('DevelopmentStatus.tsx') else re.sub(r'HMR_MARKER_[1-3]','HMR_MARKER_BASE',actual)
        if normalized!=original:raise RuntimeError('PROVENANCE_MISMATCH')
    if helper.command(['git','ls-files','--others','--exclude-standard'],root):raise RuntimeError('PROVENANCE_MISMATCH')
    for base in [root,root/'reliability-cockpit/web']:
        if any((base/name).exists() for name in ['.env','.env.local','.env.development','.env.development.local']):raise RuntimeError('PROVENANCE_MISMATCH')

def process_evidence(pid):
    """Private evidence only; classification/rejection rules remain unchanged."""
    proc=Path('/proc')/str(pid)
    try:
        raw=(proc/'cmdline').read_bytes()
        stat=(proc/'stat').read_text().split(') ',1)[1].split()
        return dict(pid=int(pid),parent=int(stat[1]),start_ticks=stat[19],
                    executable=os.readlink(proc/'exe'),comm=(proc/'comm').read_text().strip(),
                    command_sha256=hashlib.sha256(raw).hexdigest(),
                    next_title_prefix=raw.startswith(b'next-server'))
    except (OSError,ValueError,IndexError):
        return dict(pid=int(pid),unverified_or_vanished=True)

def bounded_seconds(value):
    if not 60 <= value <= 180:raise ValueError('FAST VALIDATION ONLY: 60-180 seconds')
    return value

def main():
    args=argparse.ArgumentParser();args.add_argument('--repo',required=True);args.add_argument('--deps',required=True);args.add_argument('--output',required=True);args.add_argument('--seconds',type=int,default=180);args.add_argument('--sampling',action='store_true');args.add_argument('--debug',action='store_true');args.add_argument('--https',action='store_true');args.add_argument('--mode',choices=['baseline','candidate'],required=True);a=args.parse_args()
    bounded_seconds(a.seconds)
    repo=Path(a.repo).resolve();sha='63b61d09c45630a76657cdb54991349fb0528e7b'
    if helper.command(['/usr/bin/node-22','--version'])!='v22.23.1':raise ValueError('Pinned Node required')
    if helper.command(['git','rev-parse',sha+'^{commit}'],repo)!=sha:raise ValueError('Base mismatch')
    deps=Path(a.deps).resolve()
    for package,version in [('next','15.5.9'),('react','19.2.8')]:
        if json.loads((deps/package/'package.json').read_text())['version']!=version:raise ValueError('Locked dependency mismatch')
    if hashlib.sha256(Path('/usr/bin/node-22').read_bytes()).hexdigest()!='9d9f55f1f4497fe069d681020b728f77221c43b9a4e9576a89ff7cc537caf5cf':raise ValueError('Node binary mismatch')
    auxiliaries=pid_guard.reviewed_next_auxiliary(deps,os.path.realpath('/usr/bin/node-22'))
    available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
    if available<8000*1048576:raise RuntimeError('INITIAL_HOST_HEADROOM_REFUSAL')
    out=private_output(a.output);out.mkdir(parents=True,mode=0o700);root=out/'runs/frontend';root.mkdir(parents=True);web=root/'reliability-cockpit/web';state=root.parent/'state';state.mkdir(mode=0o700)
    with tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git','archive',sha,'reliability-cockpit/web'],cwd=repo))) as archive:archive.extractall(root,filter='data')
    (root/'.gitignore').write_bytes(subprocess.check_output(['git','show',sha+':.gitignore'],cwd=repo));(web/'node_modules').symlink_to(Path(a.deps).resolve())
    backend=root.parent/'backend';backend.mkdir();(backend/'fixture.txt').write_text('IN MEMORY ONLY');back_sha=helper.git_fixture(backend)
    api_port=helper.free_port(qa=True);port=helper.free_port();base='http://127.0.0.1:'+str(api_port)
    file=web/'app/api/development/status/route.ts';file.write_text(file.read_text().replace('http://127.0.0.1:13036',base).replace('http://127.0.0.1:8000',base))
    config=web/'next.config.js'
    config.write_text(config.read_text()+f"\nconst originalWebpack=module.exports.webpack;module.exports.webpack=(config,options)=>{{config=originalWebpack(config,options);config=require({json.dumps(str(HERE/'adapter.cjs'))}).adapt(config,options);config.plugins.push(new(require({json.dumps(str(HERE/'webpack.cjs'))}))());return config;}};\n")
    if a.debug:
        import shutil
        shutil.copytree(HERE/'debug-app',web/'app/fix06-debug')
    front_sha=helper.git_fixture(root);token=os.urandom(16).hex();unit='nadi-fix06-disposable-'+a.mode+'-'+token[:6]
    approval=dict(version=1,frontend_sha=front_sha,backend_sha=back_sha,frontend_root=str(root),backend_root=str(backend),compatibility_digest='a'*64,launcher_sha256='b'*64,launcher_source_sha=sha,backup_sha256='c'*64,approved_at='DISPOSABLE ONLY')
    digest=hashlib.sha256(json.dumps(approval,sort_keys=True,separators=(',',':')).encode()).hexdigest();manifest=state/'fixture-approval.json';receipt=state/'fixture-worker.json';helper.write(manifest,dict(approval=approval,approval_id=digest))
    scripts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}
    helper.write(out/'definition.json',dict(base_sha=sha,copy_sha=front_sha,mode=a.mode,unit=unit,node='22.23.1',heap_mib=4096,cgroup_mib=6144,cpu_percent=200,seconds=a.seconds,sampling=a.sampling,debug=a.debug,protocol='FIX04 corrected nav-hmr; 21 routes,15s dwell,5s polling,60s HMR; no forced GC',browser_cgroup_mib=768,scripts=scripts,reviewed_auxiliary_sources=pid_guard.NEXT_AUXILIARY_HASHES,port=port,fixture_port=api_port,scope='SYNTHETIC DISPOSABLE ONLY'))
    tls_args=[]
    if a.https:
        key=out/'disposable-key.pem';cert=out/'disposable-cert.pem'
        helper.command(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost,IP:127.0.0.1','-keyout',str(key),'-out',str(cert)])
        key.chmod(0o600);cert.chmod(0o600)
        tls_args=['--experimental-https','--experimental-https-key',str(key),'--experimental-https-cert',str(cert)]
    def observation_properties():
        try:
            output=subprocess.check_output(['systemctl','--user','show',unit,'-p','MainPID','-p','MemoryCurrent','-p','MemoryPeak','-p','CPUUsageNSec','-p','ControlGroup','-p','InvocationID'],text=True,timeout=.1)
            return dict(x.split('=',1) for x in output.strip().splitlines())
        except (OSError,subprocess.SubprocessError,ValueError) as error:
            raise pid_guard.AttributionError('UNREADABLE_SERVICE_EVIDENCE') from error
    def incomplete_observation(record):
        with (out/'incomplete-observations.jsonl').open('a') as log:log.write(json.dumps(dict(at=time.time(),**record))+'\n')
    fixture=browser=None;failure=None;worker=None;start=time.monotonic()
    try:
        fixture=subprocess.Popen(['/usr/bin/node-22',str(HERE.parent/'probes/fixtures.cjs'),str(web),str(api_port),back_sha],env={'PATH':'/usr/bin:/bin','HOME':str(Path.home())},stdout=open(out/'fixture.log','w'),stderr=subprocess.STDOUT)
        env=['PATH=/usr/bin:/bin','HOME='+str(Path.home()),'NODE_ENV=development','NODE_OPTIONS=--max-old-space-size=4096 --require='+str(HERE/'heap.cjs'),'NEXT_TELEMETRY_DISABLED=1','NADI_FIX06_VENDOR_MAPS='+('1' if a.mode=='candidate' else '0'),'NADI_FIX06_DISPOSABLE_ROOT='+str(web),'NADI_FIX06_SAMPLING='+('1' if a.sampling else '0'),'NADI_PROBE_DIR='+str(out),'NADI_PRIMARY_FRONTEND=true','NADI_LIVE_DEV=true','NADI_ENGINEERING_QA_ENABLED=true','NADI_ENGINEERING_WORKSPACE_ENABLED=true','COCKPIT_API_BASE='+base,'NADI_QA_BACKEND_URL='+base,'NADI_DEV_FRONTEND_MANIFEST='+str(manifest),'NADI_DEV_FRONTEND_WORKER='+str(receipt),'NADI_DEV_LAUNCHED_SHA='+front_sha]
        helper.command(['systemd-run','--user','--collect','--unit='+unit,'--service-type=exec','--working-directory='+str(web),'-p','RuntimeMaxSec=270','-p','TimeoutStopSec=10','-p','MemoryMax=6144M','-p','CPUQuota=200%','-p','TasksMax=128','-p','Restart=no','-p','UMask=0077','/usr/bin/env','-i',*env,'/usr/bin/node-22','node_modules/next/dist/bin/next','dev','--hostname','127.0.0.1','--port',str(port),*tls_args])
        while time.monotonic()-start<120:
            props=dict(x.split('=',1) for x in helper.command(['systemctl','--user','show',unit,'-p','MainPID','-p','ControlGroup','-p','InvocationID']).splitlines());group=Path('/sys/fs/cgroup'+props['ControlGroup'])
            try:
                view=pid_guard.snapshot(group,port=port)
                worker,_=pid_guard.listener_owner(view,port)
            except pid_guard.AttributionError as error:
                if str(error)!='MISSING_OR_AMBIGUOUS_LISTENER':raise
                time.sleep(1);continue
            guard=pid_guard.Guard(view,int(props['MainPID']),port,props['InvocationID'],os.path.realpath('/usr/bin/node-22'),props['ControlGroup'])
            initial_parent=props['MainPID'];initial_ticks=guard.worker['start_ticks']
            helper.write(out/'process-baseline.json',dict(records=pid_guard.sanitized(view),listener=guard.inode,port=port,https=a.https,invocation=props['InvocationID']))
            helper.write(receipt,dict(approval_id=digest,worker_pid=worker,parent_pid=int(initial_parent),start_ticks=initial_ticks,generation=1,invocation_id=props['InvocationID']))
            break
        if not worker:raise RuntimeError('No disposable listener worker')
        original=subprocess.check_output(['git','show','HEAD:reliability-cockpit/web/next-env.d.ts'],cwd=root);generated=original.replace(b'./.next/types/routes.d.ts',b'./.next-primary-dev/types/routes.d.ts');types=web/'next-env.d.ts'
        for _ in range(60):
            if types.read_bytes()==generated:types.write_bytes(original);break
            time.sleep(1)
        if types.read_bytes()!=original:raise RuntimeError('Generated shape mismatch')
        helper.write(out/'generated-audit.json',dict(before=hashlib.sha256(generated).hexdigest(),after=hashlib.sha256(original).hexdigest(),scope='DISPOSABLE COPY ONLY'))
        browser=subprocess.Popen(['systemd-run','--user','--collect','--wait','--pipe','--unit='+unit+'-browser','-p','RuntimeMaxSec=270','-p','TimeoutStopSec=10','-p','MemoryMax=768M','-p','CPUQuota=200%','-p','TasksMax=192','-p','Restart=no','-p','UMask=0077','/usr/bin/env','-i','PATH=/usr/bin:/bin','HOME='+str(Path.home()),'NADI_FIX06_HTTPS='+('1' if a.https else '0'),'NADI_PLAYWRIGHT_MODULE=/home/john-d/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs','/usr/bin/node-22',str(HERE/('debug.mjs' if a.debug else 'workload.mjs')),str(port),str(web),str(out),'nav-hmr',str(a.seconds)],stdout=open(out/'browser.log','w'),stderr=subprocess.STDOUT)
        with (out/'metrics.jsonl').open('a') as log:
            while time.monotonic()-start<a.seconds+120:
                workers=[]
                try:
                    pid_guard.reviewed_next_auxiliary(deps,os.path.realpath('/usr/bin/node-22'))
                    view,attribution,props=pid_guard.collect_observation(guard,group,observation_properties,auxiliaries,on_incomplete=incomplete_observation)
                    workers=[attribution['worker']]
                    helper.write(out/'process-latest.json',dict(at=time.time(),records=pid_guard.sanitized(view),attribution=attribution))
                except pid_guard.AttributionError as error:
                    failure=str(error)
                    if 'view' in locals():helper.write(out/'private-command-attribution.json',dict(scope='SYNTHETIC DISPOSABLE ONLY; NEVER PUBLISH',records=view['records']))
                    helper.write(out/'attribution-failure.json',dict(at=time.time(),failure=failure,evidence=error.evidence,last_verified=pid_guard.sanitized(view) if 'view' in locals() else {},last_verified_is_not_failed_snapshot=True))
                    break
                available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
                events=(group/'memory.events').read_text() if group.exists() else '';row=dict(at=time.time()*1000,**props,workers=workers,worker_evidence=[process_evidence(pid) for pid in workers],attribution=attribution,processes=pid_guard.sanitized(view),available=available,events=events);log.write(json.dumps(row)+'\n');log.flush()
                helper.write(out/'progress.json',dict(elapsed=round(time.monotonic()-start,1),workers=workers,expected=worker,memory_mib=round(int(props['MemoryCurrent'])/1048576,1),available_mib=round(available/1048576,1)))
                try:verify_source(root,front_sha)
                except RuntimeError:failure='PROVENANCE_MISMATCH';break
                if available<1200*1048576 or int(props['MemoryPeak'])>5900*1048576 or 'oom_kill 0' not in events:failure='RESOURCE_BREACH';break
                if browser.poll() is not None:
                    if browser.returncode:failure='BROWSER_FAILURE'
                    break
                time.sleep(1)
            else:failure='WORKLOAD_TIMEOUT'
        helper.write(out/'result.json',dict(failure=failure,worker=worker,parent=int(initial_parent),start_ticks=initial_ticks,elapsed=time.monotonic()-start));print(json.dumps(dict(mode=a.mode,failure=failure,output=str(out))),flush=True)
    except pid_guard.AttributionError as error:
        failure=str(error);helper.write(out/'result.json',dict(failure=failure,elapsed=time.monotonic()-start,scope='DISPOSABLE ONLY',evidence=error.evidence));raise
    finally:
        subprocess.run(['systemctl','--user','stop',unit+'-browser'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if browser and browser.poll() is None:browser.terminate();browser.wait(timeout=30)
        subprocess.run(['journalctl','--user','-u',unit,'--no-pager','-o','short-iso'],stdout=open(out/'journal.log','w'),stderr=subprocess.DEVNULL)
        subprocess.run(['systemctl','--user','stop',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if fixture and fixture.poll() is None:fixture.terminate();fixture.wait(timeout=10)
        for p in out.iterdir():
            if p.is_file():p.chmod(0o600)
    if failure:raise SystemExit(1)
if __name__=='__main__':main()
