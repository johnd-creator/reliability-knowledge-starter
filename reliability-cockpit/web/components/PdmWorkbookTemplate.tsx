'use client';
import {useState} from 'react';
import {workbookProfiles,type WorkbookProfile} from '../lib/pdm-workbook';
import type {Method} from '../lib/manual-pdm';
import {Button} from './ui';
export default function PdmWorkbookTemplate({context,method,editing,onApply}:{context?:string;method:Method;editing:boolean;onApply:(profile:WorkbookProfile)=>void}){
 const [selected,setSelected]=useState('');
 const candidates=workbookProfiles.filter(x=>x.context===context);
 // A single legacy profile keeps its established behavior. New families require explicit selection.
 const requiresSelection=candidates.some(x=>x.version!=='candidate-0.1.0');
 const profile=requiresSelection?candidates.find(x=>x.id===selected):candidates[0];
 if(!candidates.length)return null;
 const mismatch=profile&&method!==profile.methodTerm;
 return <section className="pdm-workbook-template" aria-label="Template kandidat workbook">
  {requiresSelection&&<label>Keluarga template kandidat<select value={profile?.id??''} onChange={e=>setSelected(e.target.value)}><option value="">Pilih profil sumber secara eksplisit</option>{candidates.map(x=><option key={x.id} value={x.id}>{x.label}</option>)}</select></label>}
  {!profile?<p role="status">Pilih satu keluarga; kesamaan area tidak menyamakan titik atau metode.</p>:<>
  <div className="section-heading"><div><h3>{profile.label}</h3><p className="section-note">{profile.filename} · {profile.version} · {profile.sourceRef} · sheet #{profile.sheetIndex+1} · {profile.headerRange}</p></div><span className="status-badge">Menunggu Validasi Engineer</span></div>
  <p>Subset header sumber terverifikasi. Tidak mengimpor nilai workbook atau menyetujui metode. Pilih aset, titik, versi metode dan waktu secara eksplisit.</p>
  <div className="product-context-grid">{profile.fields.map(field=><div key={field.id} className="workbook-field"><strong style={{whiteSpace:'pre-line'}}>{field.label}</strong><p>Unit asli: <strong>{field.unit||'BELUM DIKETAHUI — isi setelah validasi'}</strong></p>{field.sourcePointLabel&&<p>Label titik sumber: {field.sourcePointLabel} · axis {field.sourceAxis} · belum terikat ke titik kanonis</p>}<p className="section-note">{field.classification} · header {field.headerCells.join(', ')} · unit {field.unitCell||'belum terverifikasi'}</p></div>)}</div>
  <details><summary>Field yang belum dipakai dan batas mapping</summary><ul>{profile.unresolved.map(note=><li key={note}>{note}</li>)}</ul><p>Nama sheet/peralatan bukan identitas aset atau titik terverifikasi. Template ID hanya membantu presentasi; tidak ditambahkan ke record v1.1 atau metadata bebas. Belum mendukung semua sheet.</p></details>
  {profile.methodTerm==='OTHER'&&<p role="status">CBM provisional: temperatur/IR Window belum membuktikan inspeksi IRT lengkap. Unit yang ambigu tetap kosong; tidak diambil dari baseline atau alarm.</p>}
  {mismatch&&<p role="status">Istilah metode pada sumber/konteks kandidat: {profile.methodTerm}. Ubah pilihan Metode sendiri sebelum memakai baris kandidat.</p>}
  {editing&&<p>Revisi memakai measurement existing. Template hanya dapat diterapkan pada draf baru; perlindungan revisi tetap berlaku.</p>}
  <Button disabled={!!mismatch||editing} onClick={()=>onApply(profile)}>Gunakan baris kandidat</Button>
  </>}
 </section>;
}
