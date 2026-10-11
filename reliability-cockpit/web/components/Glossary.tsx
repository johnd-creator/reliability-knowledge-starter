'use client';
import {useState} from 'react';
import {searchGlossary} from '../lib/glossary';
import {Breadcrumbs,EmptyState,InputControl,PageHeader,SectionCard} from './ui';

export default function Glossary() {
  const [query,setQuery]=useState('');
  const terms=searchGlossary(query);
  return <div className="glossary-workspace">
    <Breadcrumbs items={[{label:'NADI',href:'/'},{label:'Panduan & Istilah'}]}/>
    <PageHeader eyebrow="Panduan NADI" title="Kamus Istilah" description="Padanan Indonesia/Inggris, makna sederhana, dan contoh penggunaan. Panduan ini tidak memberi izin pekerjaan atau menetapkan aturan engineering baru."/>
    <SectionCard><InputControl id="glossary-search" label="Cari istilah atau pengertian" type="search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Mis. ACK, kondisi aset, kemutakhiran" aria-describedby="glossary-count"/>
      <p id="glossary-count" role="status" aria-live="polite">{terms.length} istilah ditemukan</p>
      <p className="section-note">Rekam disetujui ≠ izin kerja. ACK hanya konfirmasi penerimaan. Bukti QA sintetis ≠ bukti pembangkit operasional.</p>
    </SectionCard>
    {terms.length ? <div className="glossary-grid">{terms.map(term=><SectionCard key={term.id}>
      <article id={term.id}><h2>{term.indonesian}</h2><p className="glossary-english" lang="en">{term.english}</p>
        {term.pending&&<p className="status-badge neutral">Menunggu Validasi Engineer</p>}
        <p>{term.meaning}</p><p className="section-note"><strong>Contoh di NADI: </strong>{term.example}</p>
      </article>
    </SectionCard>)}</div> : <EmptyState title="Istilah tidak ditemukan." detail="Coba padanan Indonesia, istilah Inggris, atau singkatannya."/>}
  </div>;
}
