'use client';
import {useEffect} from 'react';

/** History navigation retains the draft in its workspace provider. Full unload cannot. */
export function useUnsavedDraftGuard(dirty:boolean){
 useEffect(()=>{
  if(!dirty)return;
  const unload=(event:BeforeUnloadEvent)=>{event.preventDefault();event.returnValue='';};
  const navigate=(event:MouseEvent)=>{
   const target=event.target instanceof Element?event.target:null;
   const anchor=target?.closest('a[href]');
   if(!anchor||anchor.getAttribute('href')?.startsWith('#')||event.defaultPrevented)return;
   if(!window.confirm('Isian belum disimpan. Tinggalkan halaman? Draf tetap tersedia selama sesi ini; memuat ulang penuh akan membuangnya.')){
    event.preventDefault();event.stopImmediatePropagation();
   }
  };
  window.addEventListener('beforeunload',unload);document.addEventListener('click',navigate,true);
  return()=>{window.removeEventListener('beforeunload',unload);document.removeEventListener('click',navigate,true);};
 },[dirty]);
}
