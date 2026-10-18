// Internal presentation navigation only. API role/asset/session checks remain authoritative.
const routes=new Set(['/reports','/system-integration','/', '/assets','/asset-health','/maintenance','/maintenance/investigation','/work-orders','/fmea','/rcfa','/overhauls','/data-quality','/engineering/qa','/engineering/lab','/engineering/workflow','/panduan/istilah','/engineering','/pdm','/engineering/cases','/engineering/local','/engineering/advisories','/engineering/inbox','/recommendations','/action-board']);
const record=/^[A-Za-z0-9_.:-]{1,100}$/;
export function safeReturnDestination(value:unknown):string {
 const fallback='/';
 if(typeof value!=='string'||value.length>1024||!value.startsWith('/')||value.startsWith('//')||/[\\\u0000-\u0020\u007f]/.test(value))return fallback;
 try{
  const url=new URL(value,'https://localhost:3000');
  if(url.origin!=='https://localhost:3000'||url.hash||!(routes.has(url.pathname)||/^\/assets\/[A-Za-z0-9_.:%-]{1,600}$/.test(url.pathname))||value.split('?')[0]!==url.pathname)return fallback;
  for(const key of url.searchParams.keys()){
   if(url.searchParams.getAll(key).length!==1)return fallback;
   const item=url.searchParams.get(key)??'';
   if(key==='record'&&record.test(item))continue;
   if(key==='resource'&&url.pathname==='/engineering/local'&&['cases','inspections','recommendations'].includes(item))continue;
   return fallback;
  }
  return url.pathname+url.search;
 }catch{return fallback;}
}
export function loginHref(destination:unknown,expired=false):string {
 const params=new URLSearchParams({returnTo:safeReturnDestination(destination)});
 if(expired)params.set('expired','1');
 return '/login?'+params.toString();
}
