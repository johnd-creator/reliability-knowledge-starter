// Test-only substitute for Next navigation. URLs and browser history remain original.
export const usePathname=()=>location.pathname;
export const useRouter=()=>({push:(url:string)=>location.assign(url),replace:(url:string)=>location.replace(url),refresh:()=>location.reload()});
export const useSearchParams=()=>new URLSearchParams(location.search);
export const useParams=()=>({canonicalId:[decodeURIComponent(location.pathname.split('/').at(-1)??'')],id:location.pathname.split('/').at(-1)});
