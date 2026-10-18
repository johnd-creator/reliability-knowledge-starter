'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {loginHref,safeReturnDestination} from '../lib/login-navigation';
import {SectionCard} from './ui';
export default function QaSignInRequired({expired=false}:{expired?:boolean}){
 const [destination,setDestination]=useState('/engineering/local');
 useEffect(()=>{setDestination(safeReturnDestination(window.location.pathname+window.location.search));},[]);
 return <SectionCard className="qa-sign-in-required"><div role="status"><h2>{expired?'Sesi berakhir atau dicabut':'Masuk diperlukan'}</h2><p>{expired?'Data akun sebelumnya telah ditutup. Masuk kembali untuk melanjutkan dengan hak akses yang diverifikasi server.':'Masuk melalui halaman NADI untuk membuka rekam Engineering QA yang diizinkan bagi akun Anda.'}</p></div><Link className="button primary" href={loginHref(destination,expired)}>Masuk ke NADI →</Link><p className="section-note">Tujuan kembali tetap diperiksa; login tidak memberi hak akses tambahan. Layar faktual tetap mengikuti kebijakan development yang ada.</p></SectionCard>;
}
