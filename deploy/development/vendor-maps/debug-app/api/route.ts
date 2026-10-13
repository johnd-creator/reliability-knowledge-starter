export const dynamic='force-dynamic';
export function GET(){
 try {
  throw new Error('FIX06_SERVER_SENTINEL');
 }catch(error){return Response.json({stack:(error as Error).stack,nativeSourceMaps:process.sourceMapsEnabled});}
}
