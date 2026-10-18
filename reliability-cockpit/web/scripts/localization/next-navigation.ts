// Test-only substitute for Next navigation. URLs and browser history remain original.
export const usePathname=()=>location.pathname;
// Next refresh after a route replacement refreshes the destination tree; it does not cancel navigation.
let navigating=false;
const router={push:(url:string)=>{navigating=true;location.assign(url);},replace:(url:string)=>{navigating=true;location.replace(url);},refresh:()=>{if(!navigating)location.reload();}};
export const useRouter=()=>router;
export const useSearchParams=()=>new URLSearchParams(location.search);
export const useParams=()=>({canonicalId:[decodeURIComponent(location.pathname.split('/').at(-1)??'')],id:location.pathname.split('/').at(-1)});
