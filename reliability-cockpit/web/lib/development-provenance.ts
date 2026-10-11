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
