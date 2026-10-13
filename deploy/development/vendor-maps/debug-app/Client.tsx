"use client";
import {useState,Children} from 'react';
import Link from 'next/link';
export default function DebugClient(){
 const [count,setCount]=useState(0);
 function applicationFailure(){
  throw new Error('FIX06_APPLICATION_SENTINEL');
 }
 function vendorFailure(){
  return Children.only(null);
 }
 return <main><h1>FIX06 SYNTHETIC DEBUG ONLY</h1><p>HMR_MARKER_BASE</p>
  <button onClick={()=>setCount(count+1)}>Counter {count}</button>
  <button onClick={()=>{try{applicationFailure();}catch(error){(window as any).__fix06Stack=(error as Error).stack;}}}>Application error</button>
  <button onClick={()=>{try{vendorFailure();}catch(error){(window as any).__fix06Vendor=(error as Error).stack;}}}>Vendor error</button>
  <Link href="/fix06-debug/server">RSC navigation</Link>
 </main>;
}
