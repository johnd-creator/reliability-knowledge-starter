'use client';
import {useEffect,useRef,useState,type FormEvent} from 'react';
import type {Inspection,QaSession} from '../lib/product-records';
import {buildDraft,emptyRow,fromInspection,inputContexts,newEntry,type Entry,type InspectionDraft,type ValueKind} from '../lib/pdm-input';
import {methods} from '../lib/manual-pdm';
import {statusLabel} from '../lib/id-copy';
import {engineeringRequest} from '../lib/engineering-http';
import {usePdmDraft} from './PdmDraftContext';
import {Button,Feedback,SectionCard} from './ui';
export default function PdmMeasurementForm({session,initial,busy,onSave,onCancel}:{session:QaSession;initial?:Inspection;busy:boolean;onSave:(draft:InspectionDraft,expectedRevision?:number)=>Promise<boolean>;onCancel:()=>void}){
 const cache=usePdmDraft();
 const recovered=cache?.recovery?.subject===session.subject&&cache.recovery.base?.record_id===initial?.record_id?cache.recovery:null;
 const base=useRef(recovered?.base??initial).current;
 const [entry,setEntry]=useState<Entry>(()=>recovered?.entry??(base?fromInspection(base):newEntry(session.asset_ids[0]??''))); 
 const [dirty,setDirty]=useState(!!recovered),[error,setError]=useState(''),[identity,setIdentity]=useState('Memuat konteks aset…');
 const sequence=useRef(100);
 useEffect(()=>{let active=true;setIdentity('Memuat konteks aset…');if(entry.asset)engineeringRequest('asset-context/'+encodeURIComponent(entry.asset)+'?limit=1').then(raw=>{const value=raw as {canonical_asset_id:string;identity?:{description?:string;location_ref?:string};identity_availability:string};if(active)setIdentity(value.canonical_asset_id===entry.asset&&value.identity_availability==='AVAILABLE'?`${value.identity?.description??'Deskripsi belum diketahui'} · ${value.identity?.location_ref??'Lokasi belum diketahui'}`:'Konteks aset belum tersedia; server tetap memverifikasi Registry saat menyimpan.');}).catch(()=>{if(active)setIdentity('Konteks aset tidak dapat dibaca; tidak membuat aset baru.');});return()=>{active=false;};},[entry.asset]);
 useEffect(()=>{const leave=(e:BeforeUnloadEvent)=>{if(dirty){e.preventDefault();e.returnValue='';}};const navigate=(e:MouseEvent)=>{const anchor=(e.target as Element).closest?.('a[href]');if(dirty&&anchor&&!anchor.getAttribute('href')?.startsWith('#')&&!window.confirm('Keluar dan buang isian inspeksi yang belum disimpan?')){e.preventDefault();e.stopImmediatePropagation();}};window.addEventListener('beforeunload',leave);document.addEventListener('click',navigate,true);return()=>{window.removeEventListener('beforeunload',leave);document.removeEventListener('click',navigate,true);};},[dirty]);
 function update(patch:Partial<Entry>){const next={...entry,...patch};setEntry(next);setDirty(true);cache?.keep({subject:session.subject,entry:next,base});}
 function cancel(){if(!dirty||window.confirm('Buang isian inspeksi yang belum disimpan?')){cache?.clear();onCancel();}}
 async function submit(event:FormEvent){event.preventDefault();setError('');try{const draft=buildDraft(entry,session.subject,session.asset_ids,base);if(await onSave(draft,base?.revision)){setDirty(false);cache?.clear();}}catch(e){setError(e instanceof Error?e.message:'Validasi isian gagal.');}}
 return <SectionCard className="pdm-entry"><h2>{base?'Ubah draf inspeksi':'Input Pengukuran'}</h2><p>QA SINTETIS · Inspector: <strong>{session.subject}</strong>. Nilai, observasi, dan hipotesis tetap terpisah. Persetujuan rekam bukan sertifikasi kondisi aset.</p>
 {base&&<p className="section-note">Isian terikat ke r{base.revision}; membaca revisi terbaru tidak mengubah basis CAS isian ini. Untuk merekonsiliasi konflik, tutup form secara eksplisit lalu pilih revisi terbaru.</p>}
 {error&&<Feedback error>{error} Isian belum disimpan tetap tersedia.</Feedback>}
 <form className="engineering-form" onSubmit={submit} aria-busy={busy}><fieldset disabled={busy}><legend>Konteks inspeksi</legend><div className="filter-grid">
 <label>Aset kanonis berotorisasi<select required disabled={!!initial} value={entry.asset} onChange={e=>update({asset:e.target.value})}>{session.asset_ids.map(id=><option key={id}>{id}</option>)}</select></label>
 <label>Konteks input kandidat<select value={entry.inputContext??''} onChange={e=>update({inputContext:e.target.value})}><option value="">Form umum v1.1</option>{inputContexts.map(x=><option key={x.id} value={x.id}>{x.label} · {x.version}</option>)}</select></label>
 <label>Metode<select value={entry.method} onChange={e=>update({method:e.target.value as Entry['method']})}>{methods.map(x=><option key={x} value={x}>{statusLabel(x)}</option>)}</select></label>
 <label>Versi metode / prosedur<input required value={entry.version} maxLength={80} onChange={e=>update({version:e.target.value})}/></label>
 <label>Waktu inspeksi asli (ISO + zona waktu)<input value={entry.time} maxLength={40} placeholder="2026-10-09T08:00:00+07:00" onChange={e=>update({time:e.target.value})}/></label>
 </div><p role="status" className="section-note">{identity}</p><p className="section-note">AREA FAN, AREA MILL, dan Logsheet 6 kV adalah konteks workflow, bukan metode atau field workbook yang disetujui. Menunggu Validasi Engineer. Pemilihan konteks tidak menyisipkan metadata di luar schema.</p>
 <div className="filter-grid"><label>Referensi instrumen (kandidat)<input value={entry.instrument} maxLength={2000} onChange={e=>update({instrument:e.target.value})}/></label><label>Referensi prosedur (kandidat)<input value={entry.procedure} maxLength={2000} onChange={e=>update({procedure:e.target.value})}/></label><label>Orientasi (kandidat, bila diketahui)<input value={entry.orientation} maxLength={2000} onChange={e=>update({orientation:e.target.value})}/></label></div>
 <p className="section-note">Instrumen, prosedur, orientasi, dan konteks operasi di sini berlaku untuk seluruh inspeksi v1.1. Bila konteks berbeda antar titik, gunakan inspeksi terpisah; field kandidat ini tidak menyetujui kesetaraan seri.</p>
 <label>Konteks operasi<textarea value={entry.context} maxLength={6000} onChange={e=>update({context:e.target.value})}/></label>
 <div className="section-heading"><h3>Titik dan measurement asli</h3><Button disabled={entry.rows.length>=100} onClick={()=>update({rows:[...entry.rows,emptyRow('row-'+ ++sequence.current)]})}>Tambah baris</Button></div><p className="section-note">Maksimal 100 baris. Tab untuk berpindah field. Nol adalah nilai valid; kosong bukan nol. Pilih Belum diketahui untuk null. Tidak ada konversi unit atau jadwal harian otomatis.</p>
 <div className="pdm-grid-scroll" role="region" aria-label="Grid input multi-titik" tabIndex={0}><div className="pdm-measurement-grid">{entry.rows.map((row,index)=>{
  const set=(key: keyof typeof row,value:string)=>update({rows:entry.rows.map(x=>x.key===row.key?{...x,[key]:value}:x)});
  return <fieldset className="pdm-measurement-row" key={row.key}><legend>Measurement {index+1}</legend>
   <label>Titik {index+1}<input value={row.point} maxLength={200} onChange={e=>set('point',e.target.value)}/></label>
   <label>Parameter {index+1}<input required value={row.quantity} maxLength={120} onChange={e=>set('quantity',e.target.value)}/></label>
   <label>Tipe nilai {index+1}<select aria-label={"Tipe nilai "+(index+1)} value={row.kind} onChange={e=>set('kind',e.target.value as ValueKind)}>{[['UNKNOWN','Belum diketahui (null)'],['NUMERIC','Angka'],['TEXT','Teks'],['BOOLEAN','Boolean']].map(([value,text])=><option key={value} value={value}>{text}</option>)}</select></label>
   <label>Nilai asli {index+1}{row.kind==='BOOLEAN'?<select aria-label={"Nilai asli "+(index+1)} value={row.value} required onChange={e=>set('value',e.target.value)}><option value="">Pilih nilai</option><option value="true">true</option><option value="false">false</option></select>:<input required={row.kind!=='UNKNOWN'} disabled={row.kind==='UNKNOWN'} value={row.value} maxLength={2000} inputMode={row.kind==='NUMERIC'?'decimal':'text'} onChange={e=>set('value',e.target.value)}/>}</label>
   <label>Unit asli {index+1}<input value={row.unit} maxLength={40} onChange={e=>set('unit',e.target.value)}/></label>
   <label>Waktu measurement {index+1}<input value={row.time} maxLength={40} placeholder="ISO + zona waktu" onChange={e=>set('time',e.target.value)}/></label>
   <Button aria-label={'Hapus measurement '+(index+1)} onClick={()=>update({rows:entry.rows.filter(x=>x.key!==row.key)})}>Hapus</Button>
  </fieldset>;
 })}</div></div>
 <div className="product-context-grid"><label>Observasi (satu per baris)<textarea value={entry.observation} onChange={e=>update({observation:e.target.value})}/></label><label>Interpretasi / Hipotesis (satu per baris)<textarea value={entry.hypothesis} onChange={e=>update({hypothesis:e.target.value})}/></label></div>
 <h3>Referensi evidence</h3><p>Metadata evidence yang sudah ada dipertahankan saat revisi. Upload, download, dan penyimpanan attachment belum diaktifkan.</p>{base?.attachments.map(x=><p key={x.attachment_ref}>{x.attachment_ref} · {x.filename} · {x.status}</p>)}
 <details><summary>Tambahkan rujukan evidence yang berhak Anda laporkan (metadata saja)</summary><p>Metadata dilaporkan inspector; tidak membuktikan keberadaan, keaslian, custody, atau akses file. Tidak membuka URL atau mengunggah berkas.</p><div className="filter-grid">{[['ref','Referensi attachment','attachment:identitas'],['filename','Nama berkas evidence','basename'],['type','Content type metadata','application/pdf'],['size','Ukuran evidence (byte)','0'],['sha256','SHA256 metadata (opsional)','']].map(([key,label,placeholder])=><label key={key}>{label}<input maxLength={key==='sha256'?64:200} placeholder={placeholder} value={entry.metadata?.[key as keyof NonNullable<Entry['metadata']>]??''} onChange={e=>update({metadata:{ref:'',filename:'',type:'',size:'',sha256:'',...entry.metadata,[key]:e.target.value}})}/></label>)}</div></details>
 <div className="engineering-actions"><Button type="submit" variant="primary">{busy?'Menyimpan…':initial?'Simpan revisi draf':'Simpan draf inspeksi'}</Button><Button onClick={cancel}>Batal input</Button>{dirty&&<span role="status">Isian belum disimpan</span>}</div>
 </fieldset></form></SectionCard>;
}
