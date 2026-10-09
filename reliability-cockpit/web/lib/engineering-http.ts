// HTTP contract only. Actor, roles and asset authority are never supplied here.
export class EngineeringHttpError extends Error {
 constructor(public status:number,public code:string){super(code);}
}
export async function engineeringRequest(path:string,method='GET',body?:unknown,csrf?:string):Promise<unknown>{
 const headers:Record<string,string>={'Content-Type':'application/json'};
 if(csrf)headers['X-CSRF-Token']=csrf;
 let response:Response;
 try{response=await fetch('/api/engineering-qa/'+path,{method,headers,body:body===undefined?undefined:JSON.stringify(body),credentials:'same-origin',cache:'no-store'});}catch{throw new EngineeringHttpError(503,'QA_BACKEND_UNAVAILABLE');}
 const raw=await response.json().catch(()=>null);
 if(!response.ok)throw new EngineeringHttpError(response.status,raw?.detail?.code??'INVALID_RESPONSE');
 return raw;
}
