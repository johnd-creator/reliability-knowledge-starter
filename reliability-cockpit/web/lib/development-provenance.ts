import {createHash} from 'node:crypto';
import {lstat,readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';

type Approval = {version:number;frontend_sha:string;backend_sha:string;frontend_root:string;backend_root:string;compatibility_digest:string;launcher_sha256:string;launcher_source_sha:string;backup_sha256:string;approved_at:string};
export type Envelope = {approval:Approval;approval_id:string};
const hex=(value:unknown)=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);
const sha=(value:unknown)=>typeof value==='string'&&/^[0-9a-f]{40}$/.test(value);
export function approvalDigest(approval:Approval):string {
 return createHash('sha256').update(JSON.stringify(Object.fromEntries(Object.entries(approval).sort(([a],[b])=>a<b?-1:a>b?1:0)))).digest('hex');
}
export function approvedPair(envelope:Envelope|null,front:string,launch:string,backend:string,dirty:boolean|null,backendHead:string,backendDirty:boolean|null):boolean {
 if(!envelope)return false;
 const a=envelope.approval;
 return a?.version===1&&sha(front)&&sha(backend)&&front===launch&&a.frontend_sha===front&&a.backend_sha===backend&&
  backend===backendHead&&dirty===false&&backendDirty===false&&sha(a.launcher_source_sha)&&hex(a.compatibility_digest)&&hex(a.launcher_sha256)&&hex(a.backup_sha256)&&
  hex(envelope.approval_id)&&approvalDigest(a)===envelope.approval_id;
}
export async function readApproval(path:string|undefined,cwd:string):Promise<Envelope|null>{
 if(!path)return null;
 try {
  const info=await lstat(path),value:Envelope=JSON.parse(await readFile(path,'utf8'));
  const root=resolve(cwd,'../..');
  const expectedState=resolve(root,'..','state');
  if(info.isSymbolicLink()||!info.isFile()||(info.mode&0o077)||info.uid!==process.getuid?.()||dirname(path)!==expectedState||
   !/^frontend-approval-[a-f0-9]+\.json$/.test(path.split('/').at(-1)??'')||value.approval.frontend_root!==root||
   dirname(value.approval.backend_root)!==dirname(root)||value.approval.backend_root===root||
   value.approval.version!==1||approvalDigest(value.approval)!==value.approval_id)return null;
  return value;
 }catch{return null;}
}

export type WorkerIdentity={worker_pid:number;parent_pid:number;start_ticks:string};
export type WorkerReceipt=WorkerIdentity&{approval_id:string;generation:number;invocation_id:string};
export function approvedWorker(receipt:WorkerReceipt|null,identity:WorkerIdentity,approvalId:string|undefined):boolean {
 return !!receipt&&hex(approvalId)&&receipt.approval_id===approvalId&&
  receipt.worker_pid===identity.worker_pid&&receipt.parent_pid===identity.parent_pid&&receipt.start_ticks===identity.start_ticks&&
  Number.isSafeInteger(receipt.generation)&&receipt.generation>0&&/^[a-f0-9]{32}$/.test(receipt.invocation_id);
}
export async function workerStatus(path:string|undefined,manifest:string|undefined,approvalId:string|undefined){
 const identity:WorkerIdentity={worker_pid:process.pid,parent_pid:process.ppid,start_ticks:"UNKNOWN"};
 let receipt:WorkerReceipt|null=null;
 try{
  const stat=await readFile("/proc/self/stat","utf8");identity.start_ticks=stat.slice(stat.lastIndexOf(") ")+2).trim().split(/\s+/)[19];
  if(!path||!manifest||path!==manifest.replace(/frontend-approval-([a-f0-9]+)\.json$/,"frontend-worker-$1.json")||path===manifest)throw new Error();
  const info=await lstat(path);
  if(info.isSymbolicLink()||!info.isFile()||(info.mode&0o077)||info.uid!==process.getuid?.())throw new Error();
  receipt=JSON.parse(await readFile(path,"utf8"));
 }catch{}
 return {...identity,approved_worker_pid:receipt?.worker_pid??null,worker_generation:receipt?.generation??null,
  worker_integrity:approvedWorker(receipt,identity,approvalId)?"VERIFIED":"UNVERIFIED"};
}
