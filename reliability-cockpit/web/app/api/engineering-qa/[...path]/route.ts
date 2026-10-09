import {readBounded, HttpLimitError} from '../../../../lib/bounded-http';
import {NextRequest, NextResponse} from 'next/server';
export const dynamic='force-dynamic';
async function proxy(request:NextRequest,context:{params:Promise<{path:string[]}>}) {
 if(process.env.NODE_ENV!=='development'||process.env.NADI_ENGINEERING_QA_ENABLED!=='true')return new NextResponse(null,{status:404});
 let base:URL;
 try {base=new URL(process.env.NADI_QA_BACKEND_URL??'');}catch{return NextResponse.json({detail:{code:'QA_NOT_CONFIGURED'}},{status:503});}
 if(base.protocol!=='http:'||!['localhost','127.0.0.1'].includes(base.hostname)||!/^13\d{3}$/.test(base.port)||base.username||base.password||base.pathname!=='/'||base.search||base.hash)return NextResponse.json({detail:{code:'QA_TARGET_DENIED'}},{status:503});
 const {path}=await context.params;
 if(path.some(p=>!p||p==='.'||p==='..'||p.includes('/')||p.includes('\\')))return new NextResponse(null,{status:400});
 const headers=new Headers();for(const name of ['cookie','origin','content-type','x-csrf-token']){const value=request.headers.get(name);if(value)headers.set(name,value);}
 if(!['GET','POST','PUT'].includes(request.method))return new NextResponse(null,{status:405});
 const declared=request.headers.get('content-length');
 if(declared&&(!/^\d+$/.test(declared)||Number(declared)>1024*1024))return new NextResponse(null,{status:413});
 let receivingUpstream=false;
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),15000);
 const abort=()=>controller.abort();request.signal.addEventListener('abort',abort,{once:true});
 try {
  const body=request.method==='GET'?undefined:await readBounded(request.body,1024*1024,controller.signal);
  const url=new URL('/v1/engineering/'+path.map(encodeURIComponent).join('/'),base);url.search=request.nextUrl.search;
  receivingUpstream=true;
  const upstream=await fetch(url,{method:request.method,headers,body,cache:'no-store',redirect:'error',signal:controller.signal});
  const result=new NextResponse([204,304].includes(upstream.status)?null:await readBounded(upstream.body,2*1024*1024,controller.signal),{status:upstream.status,headers:{'content-type':upstream.headers.get('content-type')??'application/json','cache-control':'no-store','x-content-type-options':'nosniff'}});
  for(const cookie of upstream.headers.getSetCookie())result.headers.append('set-cookie',cookie);
  return result;
 }catch(error){
  if(error instanceof HttpLimitError&&error.code==='BODY_TOO_LARGE')return NextResponse.json({detail:{code:'QA_BODY_LIMIT_EXCEEDED'}},{status:receivingUpstream?502:413});
  return NextResponse.json({detail:{code:'QA_BACKEND_UNAVAILABLE'}},{status:503});
 }finally{clearTimeout(timer);request.signal.removeEventListener('abort',abort);}
}
export const GET=proxy;export const POST=proxy;export const PUT=proxy;
