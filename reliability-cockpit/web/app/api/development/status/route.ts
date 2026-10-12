import {execFile} from "node:child_process";
import {promisify} from "node:util";
import {readApproval,approvedPair,workerStatus} from "../../../../lib/development-provenance";
import {NextResponse} from "next/server";
export const dynamic="force-dynamic";
const run=promisify(execFile);
export async function GET(){
 if(process.env.NODE_ENV!=="development"||process.env.NADI_LIVE_DEV!=="true")return new NextResponse(null,{status:404});
 const git=async(args:string[])=>(await run("git",args,{cwd:process.cwd(),timeout:1500,maxBuffer:1024*1024})).stdout.trim();
 let branch="UNKNOWN",sha="UNKNOWN",dirty:boolean|null=null;
 try{branch=await git(["branch","--show-current"])||"DETACHED";sha=await git(["rev-parse","HEAD"]);dirty=(await git(["status","--porcelain"])).length>0;}catch{}
 let backend="UNAVAILABLE",database="UNKNOWN",databaseIdentity="UNKNOWN",engineering=false,backendSha="UNKNOWN";
 try{
  // Fixed loopback endpoint; no user-supplied target or connection strings.
  const response=await fetch("http://127.0.0.1:13036/development/status",{cache:"no-store",signal:AbortSignal.timeout(1500)});
  const data=await response.json();
  if(response.ok&&data.environment==="DEVELOPMENT"&&data.database==="DISPOSABLE_TEST"){
   backend="AVAILABLE";database="DISPOSABLE_TEST";databaseIdentity=data.database_identity;engineering=data.engineering===true;backendSha=data.source_sha;
  }
 }catch{backend="UNAVAILABLE";}
 let factualBackend="UNAVAILABLE";
 try{
  const response=await fetch("http://127.0.0.1:8000/health",{cache:"no-store",signal:AbortSignal.timeout(1500),redirect:"error"});
  if(response.ok)factualBackend="AVAILABLE";
 }catch{}
 const envelope=await readApproval(process.env.NADI_DEV_FRONTEND_MANIFEST,process.cwd());
 let backendHead="UNKNOWN",backendDirty:boolean|null=null;
 if(envelope){try{
  const options={cwd:envelope.approval.backend_root,timeout:1500,maxBuffer:1024*1024};
  backendHead=(await run("git",["rev-parse","HEAD"],options)).stdout.trim();
  backendDirty=(await run("git",["status","--porcelain"],options)).stdout.trim().length>0;
 }catch{}}
 const worker=await workerStatus(process.env.NADI_DEV_FRONTEND_WORKER,process.env.NADI_DEV_FRONTEND_MANIFEST,envelope?.approval_id);
 const launchedSha=process.env.NADI_DEV_LAUNCHED_SHA??"UNKNOWN";
 const equivalent=worker.worker_integrity==="VERIFIED"&&backend==="AVAILABLE"&&approvedPair(envelope,sha,launchedSha,backendSha,dirty,backendHead,backendDirty);
 const compatibility=equivalent?"VERIFIED_SOURCE_EQUIVALENT":sha!=="UNKNOWN"&&sha===backendSha?"SAME_SOURCE":"UNVERIFIED";
 return NextResponse.json({...worker,frontend_node_version:process.versions.node,frontend_v8_version:process.versions.v8,environment:"DEVELOPMENT",branch,sha,dirty,backend,database,engineering,
  factual_backend:factualBackend,database_identity:databaseIdentity,primary_origin:"https://localhost:3000",
  launched_sha:launchedSha,frontend_sha:sha,backend_sha:backendSha,
  compatibility,compatibility_approval:equivalent?envelope?.approval_id:null,
  launcher_source_sha:equivalent?envelope?.approval.launcher_source_sha:null,
  launcher_sha256:equivalent?envelope?.approval.launcher_sha256:null,
  stale:worker.worker_integrity!=="VERIFIED"||sha==="UNKNOWN"||sha!==launchedSha||(sha!==backendSha&&!equivalent),
  factual_data:"OPERATIONAL_LOCAL_READ_ONLY",engineering_data:"SYNTHETIC_FIXTURES"},
  {headers:{"Cache-Control":"no-store"}});
}
