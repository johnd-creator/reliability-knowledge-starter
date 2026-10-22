"""Install only a reviewed local amendment; immutable releases, atomic metadata rollback."""
from pathlib import Path
import os,json,hashlib,importlib.util,shlex,uuid,fcntl,tempfile,shutil
T=Path(__file__).resolve().parent;SOURCE=T/'controller';R=Path('/home/john-d/Music/reliability-knowledge-starter');STATE=R/'.nadi-dev/state';FILES=('nadi-dev.py','local_development.py','local_fixture.py','frontend_preview.py','pdm_007_bridge.py')
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):
 p=Path(p);s=p.lstat()
 if p.is_symlink() or not p.is_file() or s.st_uid!=os.getuid() or s.st_mode&0o077 or s.st_nlink!=1:raise RuntimeError('PRIVATE_INSTALL_FILE_REQUIRED')
 return p.read_bytes()
def write(p,data,mode=0o600):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
 with os.fdopen(fd,'wb') as f:f.write(data)
def replace(p,data,mode=0o600):
 q=Path(str(p)+'.'+uuid.uuid4().hex+'.tmp');write(q,data,mode);os.replace(q,p)
def module(p):
 s=importlib.util.spec_from_file_location('compat_install_'+uuid.uuid4().hex,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def atomic_metadata(wrapper,manifest,new_wrapper,new_manifest,verify):
 oldw,oldm=read(wrapper),read(manifest);changedw=changedm=False
 try:
  replace(manifest,new_manifest);changedm=True
  replace(wrapper,new_wrapper,0o700);changedw=True
  verify()
 except BaseException:
  if read(wrapper) not in (oldw,new_wrapper) or read(manifest) not in (oldm,new_manifest):raise RuntimeError('CONTROLLER_RECOVERY_CONCURRENT_CHANGE') from None
  if read(wrapper)!=oldw:replace(wrapper,oldw,0o700)
  if read(manifest)!=oldm:replace(manifest,oldm)
  raise

def source_read(path):
 # Published code may be world-readable; runtime/config/review files remain private.
 p=Path(path);info=p.lstat()
 if (p.is_symlink() or not p.is_file() or info.st_uid!=os.getuid() or
     info.st_nlink!=1 or info.st_mode&0o022):raise RuntimeError('REVIEWED_SOURCE_FILE_REQUIRED')
 return p.read_bytes()

def install(approval_path=None):
 if approval_path is None or not Path(approval_path).is_absolute():raise RuntimeError('EXACT_PRIVATE_REVIEW_APPROVAL_REQUIRED')
 approved_path=Path(approval_path)
 approved=json.loads(read(approved_path));blobs={n:source_read(SOURCE/n) for n in FILES}
 if {n:sha(b) for n,b in blobs.items()}!=approved['files'] or approved['verdict']!='GO' or sha(Path(__file__).read_bytes())!=approved['installer_sha256']:raise RuntimeError('INDEPENDENT_REVIEW_BYTES_CHANGED')
 wrapper=R/'.nadi-dev/nadi-dev';manifest=STATE/'local-development-release.json';active=STATE/'local-dev-01/active.json';oldw,oldm,olda=read(wrapper),read(manifest),read(active);record=json.loads(oldm);current=json.loads(olda)
 if sha(oldm)!=approved['expected_installed_manifest_sha256'] or sha(oldw)!=approved['expected_installed_wrapper_sha256'] or sha(olda)!=approved['expected_active_state_sha256']:raise RuntimeError('REVIEWED_INSTALL_BASELINE_CHANGED')
 if record['source_sha']!='1ec93d6f3507321617903d169451d77fdcc1216e' or current['sha']!='e84eaec0e38e57cf0f057abaeda04e34739b01f8':raise RuntimeError('CONTROLLER_INSTALL_BASELINE_CHANGED')
 words=shlex.split(oldw.decode().splitlines()[1]);oldpath=Path(words[2]);expected=['exec','/usr/bin/python3',str(oldpath),'$@']
 if oldw.decode().splitlines()[0]!='#!/bin/sh' or words!=expected or oldpath.parent.parent!=STATE/'controller-releases':raise RuntimeError('UNREVIEWED_WRAPPER')
 if set(record['files'])!=set(FILES)-{'pdm_007_bridge.py'} or any(sha(read(oldpath.with_name(n)))!=h for n,h in record['files'].items()):raise RuntimeError('OLD_CONTROLLER_INTEGRITY_FAILED')
 c=module(oldpath);oldmanager=c.local_controller();oldmanager.status();baseprobe=oldmanager.fixture_probe(current)
 ident='pr111-history-bridge-'+uuid.uuid4().hex[:12];release=STATE/'controller-releases'/ident;release.mkdir(mode=0o700)
 for n,b in blobs.items():write(release/n,b)
 local={'id':ident,'approved_from':current['sha'],'approved_to':'85e6bb61eb5cb724e436846b9bdeee31709dffd4','bridge_schema_sha256':'7dc4b17be2b6281887fcd02fe2042794d8a5f1d67bf05cdad3856d54c8f56411','base_manifest_sha256':sha(oldm),'review_manifest_sha256':sha(read(approved_path))}
 newrecord=dict(record,files=approved['files'],local_amendment=local,base_files=record['files'],previous_local_amendment=record.get('local_amendment'));newm=json.dumps(newrecord,indent=2).encode();neww=('#!/bin/sh\nexec /usr/bin/python3 '+shlex.quote(str(release/'nadi-dev.py'))+' "$@"\n').encode()
 with tempfile.TemporaryDirectory(prefix='nadi-compat-install-') as tmp:
  stage=Path(tmp);stage.chmod(0o700);(stage/'local-dev-01').mkdir(mode=0o700);write(stage/'local-dev-01/active.json',olda);write(stage/'local-development-release.json',newm);write(stage/'localhost.pem',read(STATE/'localhost.pem'));(stage/'python-runtime').symlink_to(STATE/'python-runtime',target_is_directory=True)
  candidate=module(release/'nadi-dev.py');candidate.STATE=stage;staged=candidate.local_controller();assert staged.status()['transport_process_readiness']=='VERIFIED'
 candidate=module(release/'nadi-dev.py');newmanager=candidate.local_controller()
 probe=newmanager.fixture_probe(current)
 expected_pending={'name':'007_pdm_source_history.sql','checksum':'95806119fe0a131ec8c64733da9f41de85e59389cae3ee80820876f27abad524','status':'PENDING'}
 if (probe.get('ledger')!=baseprobe.get('ledger',[])+[expected_pending] or
     {k:v for k,v in probe.items() if k!='ledger'}!={k:v for k,v in baseprobe.items() if k!='ledger'}):
  raise RuntimeError('CONTROLLER_INSTALL_BRIDGE_BASELINE_CHANGED')
 lock=os.open(STATE/'frontend-lifecycle.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  with newmanager.transaction():
   if read(wrapper)!=oldw or read(manifest)!=oldm or read(active)!=olda:raise RuntimeError('CONCURRENT_CONTROLLER_CHANGE')
   oldmanager.status();before={u:oldmanager.unit(u) for u in c.UNITS}
   for suffix,data,mode in [('manifest-before.json',oldm,0o600),('wrapper-before.sh',oldw,0o700),('active-before.json',olda,0o600)]:write(STATE/'local-dev-01'/(ident+'-'+suffix),data,mode)
   def verify():
    nonlocal result
    result=newmanager.status()
    if result['transport_process_readiness']!='VERIFIED' or read(active)!=olda or any(newmanager.unit(u)!=v for u,v in before.items()):raise RuntimeError('CONTROLLER_INSTALL_CHANGED_RUNTIME')
   result=None;atomic_metadata(wrapper,manifest,neww,newm,verify)
   outcome={'result':'PASS','release':str(release),'local_amendment':local,'files':approved['files'],'processes_restarted':False,'active_state_bytes_unchanged':True,'readiness':result,'rollback_manifest':str(STATE/'local-dev-01'/(ident+'-manifest-before.json')),'rollback_wrapper':str(STATE/'local-dev-01'/(ident+'-wrapper-before.sh'))}
   write(STATE/'local-dev-01'/(ident+'-installed.json'),json.dumps(outcome,indent=2).encode());print(json.dumps(outcome,indent=2))
 finally:os.close(lock)
if __name__=='__main__':
 # Preparation is the default. Execution needs a fresh final reviewed release and
 # a separately authorized exact install request; no live action in this task.
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--apply',action='store_true')
 parser.add_argument('--approval-file',type=Path,help='Absolute owner-private final review/baseline manifest; never committed')
 args=parser.parse_args()
 if not args.apply:print(json.dumps({'mode':'PREPARATION_ONLY','runtime_changes':False,'separate_execution_authorization_required':True}))
 elif os.environ.get('NADI_PR111_CONTROLLER_EXECUTION_ACK')!='e84eaec0-to-85e6bb61-exact007':
  raise RuntimeError('SEPARATE_EXACT_CONTROLLER_INSTALL_APPROVAL_REQUIRED')
 else:install(args.approval_file)
