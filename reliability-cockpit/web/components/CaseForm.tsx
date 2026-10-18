'use client';
import {idText,statusLabel,fieldLabels} from '../lib/id-copy';
import {type FormEvent,useEffect,useState} from 'react';
import type {CaseDraft,CaseRecord} from '../lib/case-records';
import {investigationFields} from '../lib/case-records';
import {validateCaseForm} from '../lib/case-form';
import {useCaseDraft} from './CaseDraftContext';
import {Button,Feedback,InputControl} from './ui';
export default function CaseForm({initial,assets,busy,onSave,onCancel,editing=false,subject,base}:{initial:CaseDraft;assets:string[];busy:boolean;onSave:(draft:CaseDraft)=>Promise<void>;onCancel:()=>void;editing?:boolean;subject?:string;base?:CaseRecord}){
 const cache=useCaseDraft();
 const recovered=cache?.recovery?.subject===subject&&cache?.recovery?.base?.case_id===base?.case_id?cache?.recovery:null;
 const [draft,setDraft]=useState(()=>recovered?.draft??initial),[dirty,setDirty]=useState(!!recovered),[error,setError]=useState('');
 useEffect(()=>{
  const unload=(e:BeforeUnloadEvent)=>{if(dirty){e.preventDefault();e.returnValue='';}};
  const navigate=(e:MouseEvent)=>{const a=(e.target as Element).closest?.('a[href]');if(dirty&&a&&!a.getAttribute('href')?.startsWith('#')&&!window.confirm('Keluar dan buang isian Case yang belum disimpan?')){e.preventDefault();e.stopImmediatePropagation();}};
  window.addEventListener('beforeunload',unload);document.addEventListener('click',navigate,true);
  return()=>{window.removeEventListener('beforeunload',unload);document.removeEventListener('click',navigate,true);};
 },[dirty]);
 function update(next:CaseDraft){setDraft(next);setDirty(true);if(subject)cache?.keep({subject,draft:next,base});}
 function text(key:typeof investigationFields[number]){return draft.investigation[key].join('\n');}
 async function submit(e:FormEvent){e.preventDefault();if(busy)return;setError('');try{validateCaseForm(draft);await onSave(draft);}catch(e){setError(e instanceof Error?e.message:'Periksa isian Case.');}}
 function cancel(){if(dirty&&!window.confirm('Buang isian Case yang belum disimpan?'))return;cache?.clear();onCancel();}
 return <form className="engineering-form case-form" onSubmit={submit} aria-busy={busy}>
 <div className="section-heading"><div><h2>{editing?idText('Edit draft case'):idText('Create Engineering Case')}</h2><p className="section-note">Draf tersimpan sebagai rekam NADI setelah Anda memilih Simpan. Isian sementara hanya berada di halaman ini.</p></div>{dirty&&<span className="status-badge" role="status">Isian belum disimpan</span>}</div>
 {error&&<Feedback error>{error} Isian tetap tersedia untuk dikoreksi.</Feedback>}
 <fieldset disabled={busy}><legend>1. Identitas & tanggung jawab</legend><div className="filter-grid">
 <InputControl id="case-title" label={idText('Case title')} required maxLength={200} value={draft.title} onChange={e=>update({...draft,title:e.target.value})}/>
 <label>{idText('Permitted QA asset')}<select required disabled={editing} value={draft.canonical_asset_id} onChange={e=>update({...draft,canonical_asset_id:e.target.value})}>{assets.map(id=><option key={id}>{id}</option>)}</select></label>
 <label>{idText('Case category')}<select value={draft.category} onChange={e=>update({...draft,category:e.target.value})}>{['INVESTIGATION','MAINTENANCE','CONDITION'].map(x=><option key={x} value={x}>{statusLabel(x)}</option>)}</select></label>
 <label>{idText('Human priority (not risk)')}<select value={draft.priority} onChange={e=>update({...draft,priority:e.target.value})}>{['LOW','NORMAL','HIGH'].map(x=><option key={x} value={x}>{statusLabel(x)}</option>)}</select></label>
 <InputControl id="case-assigned" label={idText('Assigned engineer reference (optional)')} maxLength={160} value={draft.assigned_engineer??''} onChange={e=>update({...draft,assigned_engineer:e.target.value||null})}/>
 </div><p className="section-note">Prioritas investigasi ditentukan manusia; bukan klasifikasi risiko peralatan. Referensi engineer diverifikasi server; nama tidak ditebak.</p></fieldset>
 <fieldset disabled={busy}><legend>2. Masalah & konteks operasi</legend>
 <label htmlFor="case-problem">{idText('Problem statement')}<textarea id="case-problem" required maxLength={12000} value={draft.problem_statement} onChange={e=>update({...draft,problem_statement:e.target.value})}/></label>
 <label htmlFor="case-context">{idText('Operating context')}<textarea id="case-context" maxLength={6000} value={draft.investigation.operating_context} onChange={e=>update({...draft,investigation:{...draft.investigation,operating_context:e.target.value}})}/></label></fieldset>
 <fieldset disabled={busy}><legend>3. Catatan investigasi manusia</legend><p className="section-note">Pisahkan observasi, dugaan penyebab, dan pemeriksaan lanjutan. Catatan ini tidak otomatis menjadi fakta sumber atau diagnosis.</p>
 <div className="product-context-grid">{investigationFields.map(key=><label key={key} htmlFor={'case-'+key}>{fieldLabels[key]??key}<small>Satu per baris · maksimal 20 butir, masing-masing 2.000 karakter</small><textarea id={'case-'+key} value={text(key)} onChange={e=>update({...draft,investigation:{...draft.investigation,[key]:e.target.value===''?[]:e.target.value.split(/\r?\n/)}})}/></label>)}</div>
 <p className="section-note">{idText('Observations and hypotheses remain separate human statements. Blank lists are allowed; remove empty lines before saving. No condition score is generated.')}</p></fieldset>
 {base&&<p className="feedback">Draf terikat ke revisi {base.revision}. Membaca revisi terbaru tidak mengubah basis penyimpanan; konflik harus direkonsiliasi secara sengaja.</p>}
 <div className="engineering-actions form-actions"><Button type="submit" variant="primary" busy={busy}>{busy?idText('Saving…'):idText('Save case')}</Button><Button disabled={busy} onClick={cancel}>{idText('Cancel form')}</Button></div>
 </form>;
}
