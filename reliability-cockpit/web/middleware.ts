import {NextRequest,NextResponse} from 'next/server';
import {localGuardEnabled,verifyLocalSession,PRIVATE_HEADERS,LOCAL_ORIGIN} from './lib/local-session';
import {loginHref,safeReturnDestination} from './lib/login-navigation';
export async function middleware(request:NextRequest){
 if(!localGuardEnabled())return NextResponse.next();
 const path=request.nextUrl.pathname;
 const finish=(response:NextResponse)=>{for(const [k,v] of Object.entries(PRIVATE_HEADERS))response.headers.set(k,v);return response;};
 // Route handlers independently enforce auth. Do not trust middleware-only protection.
 if(path.startsWith('/api/'))return NextResponse.next();
 const who=await verifyLocalSession(request.headers);
 if(path==='/login'){
  if(who.state==='authenticated')return finish(NextResponse.redirect(new URL(safeReturnDestination(request.nextUrl.searchParams.get('returnTo')),LOCAL_ORIGIN)));
  return finish(NextResponse.next());
 }
 if(who.state==='unavailable')return finish(new NextResponse('Otoritas sesi tidak tersedia. Akses ditutup sementara.',{status:503}));
 if(who.state==='anonymous')return finish(NextResponse.redirect(new URL(loginHref(path+request.nextUrl.search,!!request.cookies.get('__Host-nadi_session')),LOCAL_ORIGIN)));
 return finish(NextResponse.next());
}
export const config={matcher:['/((?!_next/static|_next/image|favicon.ico|logo_nadi.png).*)']};
