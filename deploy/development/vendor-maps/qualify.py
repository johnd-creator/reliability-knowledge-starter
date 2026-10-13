"""Bounded synthetic HTTPS process-attribution qualification; no NADI services.

A new private output and new user unit per scenario. Helpers are fixed test
programs, not permissions for real Next helpers. No sustained mode exists here.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import ssl
import subprocess
import time
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("pid_guard",HERE/"process_guard.py")
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
NODE="/usr/bin/node-22"
NODE_SHA="9d9f55f1f4497fe069d681020b728f77221c43b9a4e9576a89ff7cc537caf5cf"
PROGRAM=r"""
const fs=require('node:fs'),https=require('node:https'),{spawn}=require('node:child_process');
const [role,out,port,mode]=process.argv.slice(2);
if(role==='parent') {
  const child=spawn(process.execPath,[__filename,'worker',out,port,mode],{stdio:'inherit'});
  if(mode==='replacement')child.on('exit',()=>spawn(process.execPath,[__filename,'worker',out,port,'stay'],{stdio:'inherit'}));
  setInterval(()=>{},1000);
} else if(role==='worker') {
  process.title='next-server (v15.5.9)';
  const server=https.createServer({key:fs.readFileSync(out+'/key.pem'),cert:fs.readFileSync(out+'/cert.pem')},(req,res)=>res.end('SYNTHETIC QUALIFICATION ONLY'));
  server.listen(Number(port),'127.0.0.1');
  const timer=setInterval(()=>{
    if(!fs.existsSync(out+'/trigger'))return;
    clearInterval(timer);
    if(mode==='replacement')process.exit(0);
    else spawn(process.execPath,[__filename,'helper',out,'0',mode,'next-server marker'],{stdio:'inherit'});
  },100);
} else {
  if(mode==='duplicate')process.title='next-server (v15.5.9)';
  if(mode==='listener')https.createServer({key:fs.readFileSync(out+'/key.pem'),cert:fs.readFileSync(out+'/cert.pem')},(req,res)=>res.end('SYNTHETIC')).listen(0,'127.0.0.1');
  setInterval(()=>{},1000);
}
"""
def command(args):return subprocess.check_output(args,text=True).strip()
def properties(unit):
    return dict(line.split('=',1) for line in command(['systemctl','--user','show',unit,'-p','MainPID','-p','ControlGroup','-p','InvocationID']).splitlines())
def main():
    args=argparse.ArgumentParser();args.add_argument('--output',required=True);a=args.parse_args()
    out=Path(a.output)
    if not out.is_absolute() or out.parts[:3]!=('/','tmp','nadi-pid-qual-private') or len(out.parts)<=3 or '..' in out.parts or out.exists() or any(p.is_symlink() for p in [out,*out.parents]):raise ValueError('NEW PRIVATE OUTPUT REQUIRED')
    if command([NODE,'--version'])!='v22.23.1' or hashlib.sha256(Path(NODE).read_bytes()).hexdigest()!=NODE_SHA:raise ValueError('NODE PIN REFUSAL')
    out.mkdir(mode=0o700,parents=True)
    program=out/'fixture.cjs';program.write_text(PROGRAM)
    with open(out/'openssl.log','w') as log:
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1','-keyout',str(out/'key.pem'),'-out',str(out/'cert.pem')],stdout=log,stderr=log,check=True)
    results=[]
    for mode,expected in [('helper',None),('duplicate','UNVERIFIED_ADDITIONAL_NEXT_PROCESS'),('listener','UNAUTHORIZED_LISTENER'),('replacement','APPROVED_PROCESS_IDENTITY_CHANGED')]:
        case=out/mode;case.mkdir(mode=0o700)
        (case/'key.pem').symlink_to(out/'key.pem');(case/'cert.pem').symlink_to(out/'cert.pem')
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        unit='nadi-pid-qual-'+mode+'-'+os.urandom(4).hex();start=time.monotonic();failure=None;seen=False;tls=False
        subprocess.run(['systemd-run','--user','--collect','--unit='+unit,'--service-type=exec','-p','MemoryMax=256M','-p','CPUQuota=100%','-p','TasksMax=32','-p','Restart=no','-p','UMask=0077','/usr/bin/env','-i','PATH=/usr/bin:/bin','HOME='+str(out),NODE,'--max-old-space-size=128',str(program),'parent',str(case),str(port),mode],check=True,stdout=subprocess.DEVNULL,stderr=open(case/'launch.log','w'))
        try:
            while time.monotonic()-start<10:
                props=properties(unit);group=Path('/sys/fs/cgroup'+props['ControlGroup'])
                try:
                    view=g.snapshot(group,port=port);g.listener_owner(view,port)
                except g.AttributionError as error:
                    if str(error)!='MISSING_OR_AMBIGUOUS_LISTENER':raise
                    time.sleep(.1);continue
                guard=g.Guard(view,int(props['MainPID']),port,props['InvocationID'],NODE,props['ControlGroup']);break
            else:raise RuntimeError('BOOTSTRAP_TIMEOUT')
            context=ssl.create_default_context(cafile=str(out/'cert.pem'))
            with socket.create_connection(('127.0.0.1',port),timeout=2) as connection:
                with context.wrap_socket(connection,server_hostname='127.0.0.1') as secure:
                    secure.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
                    tls=b'200 OK' in secure.recv(4096)
            (case/'trigger').write_text('SYNTHETIC TEST ONLY')
            approved=((NODE,str(program),'helper',str(case),'0',mode,'next-server marker'),) if mode=='helper' else ()
            while time.monotonic()-start<8:
                props=properties(unit)
                try:
                    view=g.snapshot(group,port=port);record=guard.validate(view,int(props['MainPID']),props['InvocationID'],approved)
                    seen=seen or bool(record['auxiliaries'])
                except g.AttributionError as error:
                    failure=str(error);break
                time.sleep(.1)
            success=tls and ((failure is None and seen) if expected is None else failure==expected)
            results.append(dict(scenario=mode,expected=expected,actual=failure,helper_observed=seen,tls=tls,pass_=success,elapsed=round(time.monotonic()-start,3)))
            (case/'last-process.json').write_text(json.dumps(g.sanitized(view),indent=2))
        finally:
            subprocess.run(['journalctl','--user','-u',unit,'--no-pager'],stdout=open(case/'journal.log','w'),stderr=subprocess.DEVNULL)
            subprocess.run(['systemctl','--user','stop',unit],check=True,stdout=subprocess.DEVNULL)
    report=dict(scope='SYNTHETIC DISPOSABLE ONLY; NOT HISTORICAL PID ATTRIBUTION',node='22.23.1',results=results,pass_=all(item['pass_'] for item in results))
    (out/'result.json').write_text(json.dumps(report,indent=2))
    for path in out.rglob('*'):
        if path.is_file() and not path.is_symlink():path.chmod(0o600)
    print(json.dumps(report))
    if not report['pass_']:raise SystemExit(1)
if __name__=='__main__':main()
