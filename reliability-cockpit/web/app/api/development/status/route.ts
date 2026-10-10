import {execFile} from "node:child_process";
import {promisify} from "node:util";
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
 const launchedSha=process.env.NADI_DEV_LAUNCHED_SHA??"UNKNOWN";
 return NextResponse.json({environment:"DEVELOPMENT",branch,sha,dirty,backend,database,engineering,
  factual_backend:factualBackend,database_identity:databaseIdentity,primary_origin:"https://localhost:3000",
  launched_sha:launchedSha,backend_sha:backendSha,
  stale:sha==="UNKNOWN"||sha!==launchedSha||sha!==backendSha,
  factual_data:"OPERATIONAL_LOCAL_READ_ONLY",engineering_data:"SYNTHETIC_FIXTURES"},
  {headers:{"Cache-Control":"no-store"}});
}
