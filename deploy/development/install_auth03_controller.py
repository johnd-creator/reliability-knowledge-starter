#!/usr/bin/env python3
"""Explicit AUTH-03 local controller update. No application lifecycle or DB mutation.

Retains the established immutable four-file release, exact ROOT binding and pinned
manifest/wrapper model. Requires independently verified candidate bytes and explicit
local operator acknowledgement. Does not select a source or start/stop any service.
"""
import argparse,hashlib,importlib.util,json,os,re,shlex,subprocess,tempfile,uuid,fcntl
from pathlib import Path
from types import SimpleNamespace
FILES=('nadi-dev.py','local_development.py','local_fixture.py','frontend_preview.py')
def digest(data):return hashlib.sha256(data).hexdigest()
def private_bytes(path):
 p=Path(path);s=p.lstat()
 if p.is_symlink() or not p.is_file() or s.st_uid!=os.getuid() or s.st_mode&0o077:raise RuntimeError('PRIVATE_UPDATE_STATE_REQUIRED')
 return p.read_bytes()
def write(path,data,mode=0o600):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
 with os.fdopen(fd,'wb') as f:f.write(data)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def install(repo,candidate,expected_release,expected_serving,session_file=None):
 repo=Path(repo).resolve();base=repo/'.nadi-dev';state=base/'state';wrapper=base/'nadi-dev';manifest=state/'local-development-release.json';active=state/'local-dev-01/active.json'
 for sha in [candidate,expected_release,expected_serving]:
  if not re.fullmatch('[0-9a-f]{40}',sha):raise RuntimeError('EXACT_UPDATE_SHA_REQUIRED')
 old_manifest=private_bytes(manifest);record=json.loads(old_manifest);old_wrapper=private_bytes(wrapper);old_active=private_bytes(active);value=json.loads(old_active)
 if record['source_sha']!=expected_release or value['sha']!=expected_serving:raise RuntimeError('UPDATE_BASELINE_CHANGED')
 if value['root']!=str(base/'pdm-ui-fix-01'):raise RuntimeError('APPROVED_ACTIVE_WORKTREE_REQUIRED')
 # Established pinned wrapper must name exactly one existing private four-file release.
 lines=old_wrapper.decode().splitlines()
 if len(lines)!=2 or lines[0]!='#!/bin/sh':raise RuntimeError('UNREVIEWED_WRAPPER')
 words=shlex.split(lines[1]);old_path=Path(words[2])
 if words!=['exec','/usr/bin/python3',str(old_path),'$@'] or old_path.name!='nadi-dev.py' or old_path.parent.parent!=state/'controller-releases':raise RuntimeError('UNREVIEWED_WRAPPER')
 if set(record['files'])!=set(FILES):raise RuntimeError('UNREVIEWED_MANIFEST')
 for name,h in record['files'].items():
  if digest(private_bytes(old_path.parent/name))!=h:raise RuntimeError('OLD_CONTROLLER_INTEGRITY_FAILED')
 root_binding=record.get('installation_binding',{}).get('ROOT')
 if root_binding!=str(base/'worktree'):raise RuntimeError('ROOT_BINDING_CHANGED')
 # Only established ROOT path substitution is allowed. Remaining bytes are exact Git blobs.
 blobs={n:subprocess.check_output(['git','-C',str(repo),'show',candidate+':deploy/development/'+n]) for n in FILES}
 original=b'ROOT = Path(__file__).resolve().parents[2]'
 if blobs['nadi-dev.py'].count(original)!=1:raise RuntimeError('ROOT_BINDING_TEMPLATE_CHANGED')
 upstream={n:digest(b) for n,b in blobs.items()};blobs['nadi-dev.py']=blobs['nadi-dev.py'].replace(original,('ROOT = Path('+repr(root_binding)+')').encode())
 ident='auth03-controller-'+candidate[:12]+'-'+uuid.uuid4().hex[:8];release=state/'controller-releases'/ident;release.mkdir(mode=0o700)
 for n,b in blobs.items():write(release/n,b)
 new={'source_sha':candidate,'files':{n:digest(b) for n,b in blobs.items()},'upstream_files_sha256':upstream,'installation_binding':record['installation_binding'],'previous_manifest':str(state/'local-dev-01'/(ident+'-manifest-before.json'))}
 staged=json.dumps(new,indent=2).encode();new_value=dict(value,readiness_controller_sha=candidate)
 # Independent read-only validation in private metadata sandbox; real TLS/process checks.
 with tempfile.TemporaryDirectory(prefix='nadi-auth03-controller-') as td:
  t=Path(td);(t/'local-dev-01').mkdir(mode=0o700);write(t/'local-dev-01/active.json',json.dumps(new_value).encode());write(t/'local-development-release.json',staged)
  write(t/'localhost.pem',private_bytes(state/'localhost.pem'));(t/'python-runtime').symlink_to(state/'python-runtime',target_is_directory=True)
  c=module('auth03_candidate_control',release/'nadi-dev.py');c.STATE=t;m=c.local_controller();verified=m.status(session_file=session_file)
  if verified['transport_process_readiness']!='VERIFIED':raise RuntimeError('CANDIDATE_READINESS_FAILED')
 lock=os.open(state/'frontend-lifecycle.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  c=module('auth03_install_control',release/'nadi-dev.py');m=c.local_controller()
  with m.transaction():
   if private_bytes(manifest)!=old_manifest or private_bytes(wrapper)!=old_wrapper or private_bytes(active)!=old_active:raise RuntimeError('CONCURRENT_CONTROLLER_CHANGE')
   # Validate pre-existing source/store contract read-only; never prepare()/apply migration.
   if m.fixture_probe(value)!=value['fixture']:raise RuntimeError('FIXTURE_LEDGER_OR_SCHEMA_CHANGED')
   write(state/'local-dev-01'/(ident+'-manifest-before.json'),old_manifest);write(state/'local-dev-01'/(ident+'-wrapper-before.sh'),old_wrapper,0o700);write(state/'local-dev-01'/(ident+'-active-before.json'),old_active)
   next_wrapper=('#!/bin/sh\nexec /usr/bin/python3 '+shlex.quote(str(release/'nadi-dev.py'))+' "$@"\n').encode()
   temp_manifest=state/(ident+'-manifest.tmp');temp_wrapper=base/(ident+'-wrapper.tmp');write(temp_manifest,staged);write(temp_wrapper,next_wrapper,0o700)
   manifest_changed=False;wrapper_changed=False;active_changed=False
   try:
    os.replace(temp_manifest,manifest);manifest_changed=True
    os.replace(temp_wrapper,wrapper);wrapper_changed=True
    m.replace('active.json',new_value);active_changed=True
    result=m.status(session_file=session_file)
    m.save(ident+'-accepted.json',{'source_sha':candidate,'previous_release':expected_release,'bootstrap_sha':value['workflow_sha'],'serving_sha':value['sha'],'source_selection_changed':False,'services_restarted':False,'readiness':result})
   except Exception:
    # Metadata recovery only. Never touch source, processes, accounts or application data.
    if manifest_changed or wrapper_changed or active_changed:
     if (private_bytes(wrapper)!=(next_wrapper if wrapper_changed else old_wrapper) or
         private_bytes(manifest)!=(staged if manifest_changed else old_manifest)):
      raise RuntimeError('UPDATE_RECOVERY_CONCURRENT_CHANGE') from None
     if wrapper_changed:
      w=base/(ident+'-restore-wrapper.tmp');write(w,old_wrapper,0o700);os.replace(w,wrapper)
     if manifest_changed:
      v=state/(ident+'-restore-manifest.tmp');write(v,old_manifest);os.replace(v,manifest)
     if active_changed:m.replace('active.json',value)
    raise
 finally:os.close(lock)
 return {'result':'PASS','controller_sha':candidate,'previous_controller_sha':expected_release,'application_bootstrap_sha':value['workflow_sha'],'serving_sha':value['sha'],'release_directory':str(release),'transport_process_readiness':result['transport_process_readiness'],'authentication':result['authentication'],'services_restarted':False}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--candidate-sha',required=True);p.add_argument('--expected-release-sha',required=True);p.add_argument('--expected-serving-sha',required=True);p.add_argument('--session-file');p.add_argument('--acknowledge-local-controller-update',action='store_true');a=p.parse_args()
 if not a.acknowledge_local_controller_update:raise RuntimeError('EXPLICIT_LOCAL_UPDATE_ACK_REQUIRED')
 print(json.dumps(install(a.repository,a.candidate_sha,a.expected_release_sha,a.expected_serving_sha,a.session_file),indent=2))
if __name__=='__main__':
 try:main()
 except Exception as e:raise SystemExit('CONTROLLER_UPDATE_FAILED: '+type(e).__name__) from None
