'use client';
import {useCallback,useEffect,useState} from 'react';
import Link from 'next/link';
import type {Inspection,QaSession} from '../lib/product-records';
import {validRecordId} from '../lib/product-records';
import {methods} from '../lib/manual-pdm';
import type {InspectionDraft} from '../lib/pdm-input';
import {idText,statusLabel} from '../lib/id-copy';
import {PdmDraftProvider,usePdmDraft} from './PdmDraftContext';
import {useQaRecords} from './useQaRecords';
import {usePdmCommand} from './usePdmCommand';
import QaProductBoundary from './QaProductBoundary';
import QaRecordReader from './QaRecordReader';
import PdmMeasurementForm from './PdmMeasurementForm';
import PdmInspectionWorkflow from './PdmInspectionWorkflow';
import PdmFollowUpDetail from './PdmFollowUpDetail';
import PdmWorkOriginDetail from './PdmWorkOriginDetail';
import PdmCaptureDetail from './PdmCaptureDetail';
import PdmHistory from './PdmHistory';
import {CompactFacts,RecordNavigator,WorkspaceToolbar} from './ExperienceWorkspace';
import {Button,EmptyState,Feedback,HelpDetails,SearchField,PageHeader,Pagination,SectionCard,StatusBadge,TableFrame} from './ui';
export default function PdmCenter({qaEnabled}:{qaEnabled:boolean}){const cache=usePdmDraft();return cache?<PdmPage qaEnabled={qaEnabled}/>:<PdmDraftProvider><PdmPage qaEnabled={qaEnabled}/></PdmDraftProvider>;}
function PdmPage({qaEnabled}:{qaEnabled:boolean}){
 const cache=usePdmDraft();const clearDraft=cache?.clear;
 const [offset,setOffset]=useState(0),[query,setQuery]=useState(''),[search,setSearch]=useState(''),[method,setMethod]=useState(''),[asset,setAsset]=useState(''),[status,setStatus]=useState(''),[since,setSince]=useState(''),[until,setUntil]=useState(''),[filterError,setFilterError]=useState(''),[selected,setSelected]=useState<string|null>(null),[view,setView]=useState('register');
 const {state,page,session,reload,invalidate}=useQaRecords<Inspection>('inspections',qaEnabled,offset,query);
 useEffect(()=>{const id=new URLSearchParams(window.location.search).get('record');setSelected(validRecordId(id)?id:null);},[]);
 useEffect(()=>{if(['signed-out','expired','denied','disabled'].includes(state)||session&&cache?.recovery&&(cache.recovery.subject!==session.subject||!session.roles.includes('AUTHOR')||!session.asset_ids.includes(cache.recovery.entry.asset)))clearDraft?.();},[state,session,cache?.recovery,clearDraft]);
 const proof=page as typeof page & {filter_scope?:string;event_time_basis?:string};
 const contractReady=proof?.filter_scope==='AUTHORIZED_POPULATION'&&proof?.event_time_basis==='INSPECTED_AT';
 const expire=useCallback(()=>invalidate(),[invalidate]);
 const completed=cache?.completed,consumeCompletion=cache?.consumeCompletion;
 useEffect(()=>{if(state!=='ready'||!session||!completed)return;consumeCompletion?.();if(completed.created_by!==session.subject||!session.asset_ids.includes(completed.canonical_asset_id))return;setSelected(completed.record_id);setView('register');window.history.replaceState({},'',`/pdm?record=${encodeURIComponent(completed.record_id)}`);reload();},[completed,consumeCompletion,state,session,reload]);
 function selectRecord(id:string|null){setSelected(id);setView('register');window.history.replaceState({},'',id?`/pdm?record=${encodeURIComponent(id)}`:'/pdm');}
 function changeView(next:string){if(cache?.busy)return;if(next==='entry'&&cache?.recovery?.base&&!cache.discard())return;if(view==='entry'&&next!=='entry'){if(cache?.recovery&&!window.confirm('Tutup dan buang input pengukuran yang belum disimpan?'))return;cache?.clear();}if(next==='register'){selectRecord(null);}else setView(next);}
 function applyFilters(nextMethod=method){
  setFilterError('');
  if([since,until].some(x=>x&&(!/(Z|[+-]\d\d:\d\d)$/.test(x)||!Number.isFinite(Date.parse(x))))||since&&until&&Date.parse(since)>Date.parse(until)){setFilterError('Gunakan waktu ISO dengan zona waktu dan rentang awal ≤ akhir.');return;}
  const params=new URLSearchParams();for(const [key,value] of [['search',search],['method',nextMethod],['asset_id',asset],['status',status],['since',since],['until',until]])if(value)params.set(key,value);
  setOffset(0);setSelected(null);setQuery('&'+params.toString());
 }
 return <div className="product-workspace pdm-workspace experience-workspace"><PageHeader eyebrow="Pengukuran & investigasi" title={idText('PdM Center')} description="Pengukuran asli, riwayat inspeksi, dan review Engineering independen." actions={state==='ready'&&contractReady&&session?.roles.includes('AUTHOR')?<Button variant="primary" aria-pressed={view==='entry'} onClick={()=>changeView('entry')}>Input Pengukuran</Button>:undefined}/>
 <QaProductBoundary state={state} reload={reload}/>{view!=='entry'&&<CompactFacts items={[
 {label:'Inspeksi berotorisasi',value:contractReady&&page?page.total:'UNKNOWN',detail:'Populasi sesuai filter server QA sintetis'},
 {label:'Pada halaman ini',value:contractReady&&page?page.items.length:'UNKNOWN',detail:'Satu inspeksi per halaman; detail sumber tidak diringkas diam-diam'},
 {label:'Persetujuan metode',value:'PENDING',detail:'Menunggu Validasi Engineer Q01–Q10'},
 {label:'Penilaian kondisi',value:'NOT ASSESSED',detail:'Review rekam bukan kondisi peralatan'},
 ]}/>}
 {state==='ready'&&!contractReady&&<Feedback error>Kontrak filter PdM belum tersedia pada backend ini. Filter global dan input dinonaktifkan; diperlukan backend kandidat yang sudah direview.</Feedback>}
 {state==='ready'&&session&&page&&contractReady&&<><WorkspaceToolbar label="Navigasi dan tindakan PdM"><nav className="pdm-workspace-nav" aria-label="Area PdM Center"><Button aria-pressed={view==='register'} onClick={()=>changeView('register')}>Register Inspeksi</Button><Button aria-pressed={view==='history'} onClick={()=>changeView('history')}>Riwayat & Tren</Button><Link className="button tertiary" href="/engineering/cases">Analisis Engineering →</Link></nav></WorkspaceToolbar>{view!=='entry'&&<SectionCard className="pdm-filter-panel"><form onSubmit={e=>{e.preventDefault();applyFilters();}}><div className="filter-grid"><SearchField label="Cari inspeksi / observasi" value={search} maxLength={200} onChange={e=>setSearch(e.target.value)} placeholder="ID inspeksi atau observasi"/><label>Aset filter berotorisasi<select aria-label="Aset filter berotorisasi" value={asset} onChange={e=>setAsset(e.target.value)}><option value="">Semua aset berotorisasi</option>{session.asset_ids.map(x=><option key={x}>{x}</option>)}</select></label><label>Status inspeksi<select aria-label="Status inspeksi" value={status} onChange={e=>setStatus(e.target.value)}><option value="">Semua status</option>{['DRAFT','SUBMITTED','UNDER_REVIEW','IN_REVIEW','APPROVED','RETURNED','REJECTED'].map(x=><option key={x} value={x}>{statusLabel(x)}</option>)}</select></label></div><details className="workspace-filters"><summary>Metode & interval waktu</summary><div className="filter-grid"><label>Metode filter<select aria-label="Metode filter" value={method} onChange={e=>setMethod(e.target.value)}><option value="">Semua metode</option>{methods.map(x=><option value={x} key={x}>{statusLabel(x)}</option>)}</select></label><label>Waktu awal (ISO + zona waktu)<input value={since} maxLength={40} onChange={e=>setSince(e.target.value)}/></label><label>Waktu akhir (ISO + zona waktu)<input value={until} maxLength={40} onChange={e=>setUntil(e.target.value)}/></label></div></details><div className="engineering-actions filter-apply-actions"><Button type="submit" variant="primary">Terapkan filter server</Button><Button onClick={reload}>Muat ulang register</Button><Button onClick={()=>{setSearch('');setMethod('');setAsset('');setStatus('');setSince('');setUntil('');setQuery('');setOffset(0);setSelected(null);setFilterError('');}}>Hapus filter</Button></div>{filterError&&<Feedback error>{filterError}</Feedback>}</form><HelpDetails title="Dasar waktu & batas filter"><p>Filter register memakai waktu inspeksi asli; filter riwayat memakai waktu measurement asli. UNKNOWN tidak dimasukkan ke rentang waktu yang dipilih.</p></HelpDetails></SectionCard>}
 <PdmBody key={session.subject} session={session} rows={page.items} selected={selected} selectRecord={selectRecord} view={view} setView={setView} query={query} onExpired={expire} onChanged={reload}/>
 {view==='register'&&!selected&&<SectionCard className="register-pagination"><Pagination meta={page} onChange={n=>{setOffset(n);setSelected(null);}}/></SectionCard>}
 </>}
 </div>;
}
function PdmBody({session,rows,selected,selectRecord,view,setView,query,onExpired,onChanged}:{session:QaSession;rows:Inspection[];selected:string|null;selectRecord:(id:string|null)=>void;view:string;setView:(s:string)=>void;query:string;onExpired:()=>void;onChanged:()=>void}){
 const draftCache=usePdmDraft();
 const cmd=usePdmCommand(session,onExpired);
 function navigate(id:string|null){if(draftCache?.busy)return;if(id===selected)return;if(draftCache?.recovery){if(!window.confirm('Tutup dan buang input pengukuran yang belum disimpan?'))return;draftCache.clear();}selectRecord(id);if(id)requestAnimationFrame(()=>document.getElementById('pdm-record-pane')?.focus({preventScroll:true}));}
 async function save(draft:InspectionDraft){const row=await cmd.run<Inspection>('inspections','POST',{draft});if(row){selectRecord(row.record_id);onChanged();return true;}return false;}
 return <>
 {cmd.error&&<Feedback error>{cmd.error}</Feedback>}{cmd.notice&&<Feedback>{cmd.notice}</Feedback>}
 {view==='entry'&&session.roles.includes('AUTHOR')&&<PdmMeasurementForm session={session} busy={cmd.busy} onExpired={onExpired} onSave={save} onCancel={()=>setView('register')}/>}
 {view==='entry'&&!session.roles.includes('AUTHOR')&&<EmptyState title="Input pengukuran hanya tersedia bagi author berotorisasi."/>}
 {view==='history'&&<PdmHistory query={query} onExpired={onExpired} onSelect={selectRecord}/>}
 {view==='register'&&<div className={selected?'experience-master-detail':'experience-register'}>
 {selected?<RecordNavigator title="Inspeksi pada halaman ini"><Button variant="outline" onClick={()=>navigate(null)}>Tutup detail inspeksi</Button>{rows.map(row=><Button key={row.record_id} className="record-nav-item" aria-pressed={selected===row.record_id} onClick={()=>navigate(row.record_id)}><strong>{statusLabel(row.method)}</strong><span>{row.canonical_asset_id}</span><small>{row.record_id} · r{row.revision}</small><StatusBadge mode="raw-neutral" value={row.status}/></Button>)}</RecordNavigator>:<SectionCard className="inspection-register-panel"><div className="section-heading"><div><p className="eyebrow">Rekam pengukuran manual · QA sintetis</p><h2>Register inspeksi / temuan</h2></div><span className="section-note">{rows.length} rekam pada halaman ini</span></div>{rows.length?<TableFrame minWidth={940} label="Register event inspeksi berotorisasi"><table className="pdm-register"><thead><tr><th>Inspeksi / aset</th><th>Metode / titik</th><th>Waktu inspeksi / inspector</th><th>Observasi & hipotesis</th><th>Review rekam / revisi</th></tr></thead><tbody>{rows.map(row=><tr key={row.record_id}><td data-label="Inspeksi / aset"><Button className="record-open" onClick={()=>navigate(row.record_id)}>Buka inspeksi<small className="table-subtext identifier">{row.record_id}</small></Button><small className="table-subtext identifier">{row.canonical_asset_id}</small></td><td data-label="Metode / titik"><strong>{statusLabel(row.method)}</strong><small className="table-subtext">{row.method_version}</small><div className="table-subtext"><MeasurementPoints row={row}/></div></td><td data-label="Waktu inspeksi / inspector"><time>{row.inspected_at??'UNKNOWN'}</time><small className="table-subtext identifier">{row.inspector_ref}</small></td><td data-label="Observasi & hipotesis"><p className="register-observation">{row.observations.at(-1)??'UNKNOWN'}</p><small className="table-subtext">Hipotesis: {row.interpretations.at(-1)??'NOT ASSESSED'}</small></td><td data-label="Review rekam / revisi"><StatusBadge mode="raw-neutral" value={row.status}/><small className="table-subtext">r{row.revision}</small><details className="record-time-details"><summary>Pembaruan rekam</summary><time>{row.updated_at}</time><p>Bukan waktu measurement atau pengajuan</p></details></td></tr>)}</tbody></table></TableFrame>:<EmptyState title="Tidak ada inspeksi dalam filter server ini." detail="Belum ada data tidak berarti kondisi normal."/>}</SectionCard>}
 {selected&&<div className="experience-record-pane" id="pdm-record-pane" tabIndex={-1}><QaRecordReader<Inspection> resource="inspections" id={selected} key={selected} renderRevision={row=><><PdmWorkOriginDetail row={row}/><PdmFollowUpDetail row={row}/>{row.input_capture?<PdmCaptureDetail capture={row.input_capture}/>:<p>Revisi native: {row.measurements.length} measurement.</p>}</>} render={row=><PdmInspectionWorkflow initial={row} session={session} onExpired={onExpired} onChanged={onChanged}/>} onInvalid={onExpired}/></div>}
 </div>}

 </>;
}

function MeasurementPoints({row}:{row:Inspection}){if(row.input_capture)return <span>Input provisional · {row.input_capture.rows.length} field sumber · sheet {(row.input_capture.sheet_index??-1)+1}</span>;const points=[...new Set(row.measurements.map(m=>m.point_ref??'UNKNOWN'))];return points.length>1?<details><summary>{points.length} referensi titik</summary><ul>{points.map(x=><li key={x}>{x}</li>)}</ul></details>:<span>{points[0]??'UNKNOWN'}</span>;}
