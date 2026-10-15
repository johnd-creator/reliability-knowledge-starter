'use client';
import {workbookProfiles,type WorkbookProfile} from '../lib/pdm-workbook';
import type {Method} from '../lib/manual-pdm';
import {Button} from './ui';
export default function PdmWorkbookTemplate({context,method,editing,onApply}:{context?:string;method:Method;editing:boolean;onApply:(profile:WorkbookProfile)=>void}){
 const profile=workbookProfiles.find(x=>x.context===context);
 if(!profile)return null;
 const mismatch=method!==profile.methodTerm;
 return <section className="pdm-workbook-template" aria-label="Template kandidat workbook">
  <div className="section-heading"><div><h3>{profile.label}</h3><p className="section-note">{profile.filename} · {profile.version} · {profile.sourceRef} · sheet #{profile.sheetIndex+1} · {profile.headerRange}</p></div><span className="status-badge">Menunggu Validasi Engineer</span></div>
  <p>Subset header sumber terverifikasi. Tidak mengimpor nilai workbook atau menyetujui metode. Pilih aset, titik, versi metode dan waktu secara eksplisit.</p>
  <div className="product-context-grid">{profile.fields.map(field=><div key={field.id} className="workbook-field"><strong style={{whiteSpace:'pre-line'}}>{field.label}</strong><p>Unit asli: <strong>{field.unit}</strong></p><p className="section-note">DIRECT · header {field.headerCells.join(', ')} · unit {field.unitCell}</p></div>)}</div>
  <details><summary>Field yang belum dipakai dan batas mapping</summary><ul>{profile.unresolved.map(note=><li key={note}>{note}</li>)}</ul><p>Nama sheet/peralatan bukan identitas aset atau titik terverifikasi. Template ID hanya membantu presentasi; tidak ditambahkan ke record v1.1 atau metadata bebas. Belum mendukung semua sheet.</p></details>
  {mismatch&&<p role="status">Istilah metode pada sumber: {profile.methodTerm}. Ubah pilihan Metode sendiri sebelum memakai baris kandidat.</p>}
  {editing&&<p>Revisi memakai measurement existing. Template hanya dapat diterapkan pada draf baru; perlindungan revisi tetap berlaku.</p>}
  <Button disabled={mismatch||editing} onClick={()=>onApply(profile)}>Gunakan baris kandidat</Button>
 </section>;
}
