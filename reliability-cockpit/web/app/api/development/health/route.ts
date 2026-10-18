import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {NextResponse} from 'next/server';
import {localGuardEnabled,PRIVATE_HEADERS,LOCAL_ORIGIN} from '../../../../lib/local-session';
export const dynamic='force-dynamic';
const run=promisify(execFile);
/** Narrow local transport identity. No backend/DB/session/user data or full diagnostics. */
export async function GET(){
 if(!localGuardEnabled())return new NextResponse(null,{status:404,headers:PRIVATE_HEADERS});
 try{
  const git=async(args:string[])=>(await run('git',args,{cwd:process.cwd(),timeout:1500,maxBuffer:1024*1024})).stdout.trim();
  const sha=await git(['rev-parse','HEAD']),dirty=(await git(['status','--porcelain'])).length>0;
  if(!/^[0-9a-f]{40}$/.test(sha))throw new Error('SOURCE_UNKNOWN');
  return NextResponse.json({contract:'NADI_LOCAL_TRANSPORT_V1',origin:LOCAL_ORIGIN,frontend_sha:sha,
   launched_sha:process.env.NADI_DEV_LAUNCHED_SHA??'UNKNOWN',dirty,guard:'SERVER_SESSION_AUTHORITY'},
   {headers:PRIVATE_HEADERS});
 }catch{return NextResponse.json({detail:{code:'LOCAL_SOURCE_UNAVAILABLE'}},{status:503,headers:PRIVATE_HEADERS});}
}
