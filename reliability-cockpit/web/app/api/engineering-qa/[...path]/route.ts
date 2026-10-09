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
 const body=request.method==='GET'?undefined:await request.text();
 if(body&&new TextEncoder().encode(body).length>1024*1024)return new NextResponse(null,{status:413});
 try {
  const url=new URL('/v1/engineering/'+path.map(encodeURIComponent).join('/'),base);url.search=request.nextUrl.search;
  const upstream=await fetch(url,{method:request.method,headers,body,cache:'no-store',redirect:'error',signal:AbortSignal.timeout(15000)});
  const result=new NextResponse(await upstream.text(),{status:upstream.status,headers:{'content-type':upstream.headers.get('content-type')??'application/json','cache-control':'no-store','x-content-type-options':'nosniff'}});
  for(const cookie of upstream.headers.getSetCookie())result.headers.append('set-cookie',cookie);
  return result;
 }catch{return NextResponse.json({detail:{code:'QA_BACKEND_UNAVAILABLE'}},{status:503});}
}
export const GET=proxy;export const POST=proxy;export const PUT=proxy;
