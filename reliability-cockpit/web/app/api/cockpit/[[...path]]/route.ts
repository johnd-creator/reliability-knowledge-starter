import {factualGateway} from '../../../../lib/factual-gateway';
export const dynamic='force-dynamic';
async function gateway(request:Request,context:{params:Promise<{path?:string[]}>}){
 return factualGateway(request,(await context.params).path??[]);
}
export const GET=gateway;export const POST=gateway;export const PUT=gateway;export const PATCH=gateway;export const DELETE=gateway;export const OPTIONS=gateway;
export async function HEAD(request:Request,context:{params:Promise<{path?:string[]}>}){const response=await gateway(request,context);return new Response(null,{status:response.status,headers:response.headers});}
