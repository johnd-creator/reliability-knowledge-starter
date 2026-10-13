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
import {useQaCommand} from './useQaCommand';
import QaProductBoundary from './QaProductBoundary';
import QaRecordReader from './QaRecordReader';
import PdmMeasurementForm from './PdmMeasurementForm';
import PdmInspectionWorkflow from './PdmInspectionWorkflow';
import PdmHistory from './PdmHistory';
import {Button,EmptyState,Feedback,PageHeader,Pagination,SectionCard,StatCard,StatusBadge,TableFrame} from './ui';
export default function PdmCenter({qaEnabled}:{qaEnabled:boolean}){return <PdmDraftProvider><PdmPage qaEnabled={qaEnabled}/></PdmDraftProvider>;}
function PdmPage({qaEnabled}:{qaEnabled:boolean}){
 const cache=usePdmDraft();const clearDraft=cache?.clear;
 const [offset,setOffset]=useState(0),[query,setQuery]=useState(''),[search,setSearch]=useState(''),[method,setMethod]=useState(''),[asset,setAsset]=useState(''),[status,setStatus]=useState(''),[since,setSince]=useState(''),[until,setUntil]=useState(''),[filterError,setFilterError]=useState(''),[selected,setSelected]=useState<string|null>(null),[view,setView]=useState('register');
 const {state,page,session,reload}=useQaRecords<Inspection>('inspections',qaEnabled,offset,query);
 useEffect(()=>{const id=new URLSearchParams(window.location.search).get('record');setSelected(validRecordId(id)?id:null);},[]);
 useEffect(()=>{if(['signed-out','denied','disabled'].includes(state)||session&&cache?.recovery&&(cache.recovery.subject!==session.subject||!session.roles.includes('AUTHOR')||!session.asset_ids.includes(cache.recovery.entry.asset)))clearDraft?.();},[state,session,cache?.recovery,clearDraft]);
 const invalidate=useCallback(()=>reload(),[reload]);
 function selectRecord(id:string|null){setSelected(id);setView('register');window.history.replaceState({},'',id?`/pdm?record=${encodeURIComponent(id)}`:'/pdm');}
 return <div className="product-workspace"><PageHeader eyebrow="Pengukuran & investigasi" title={idText('PdM Center')} description="Inspeksi episodik, measurement asli, dan review Engineering independen. Field metode masih menunggu validasi engineer."/>
 <QaProductBoundary state={state} reload={reload}/><section className="stat-grid product-stat-grid"><StatCard label="Inspeksi berotorisasi" value={page?page.total:'UNKNOWN'} detail="Populasi sesuai filter server QA sintetis"/><StatCard label="Pada halaman ini" value={page?page.items.length:'UNKNOWN'} detail="Pagination server; tidak mewakili semua event"/><StatCard label="Persetujuan metode" value="PENDING" detail="Menunggu Validasi Engineer Q01–Q10"/><StatCard label="Penilaian kondisi" value="NOT ASSESSED" detail="Review rekam bukan kondisi peralatan"/></section>
 {state==='ready'&&session&&page&&<>{view!=='entry'&&<SectionCard><form onSubmit={e=>{e.preventDefault();const params=new URLSearchParams();setFilterError('');for(const [key,value] of [['search',search],['method',method],['asset_id',asset],['status',status],['since',since],['until',until]]){if(value)params.set(key,value);}if([since,until].some(x=>x&&(!/(Z|[+-]\d\d:\d\d)$/.test(x)||!Number.isFinite(Date.parse(x))))||since&&until&&Date.parse(since)>Date.parse(until)){setFilterError('Gunakan waktu ISO dengan zona waktu dan rentang awal ≤ akhir.');return;}setOffset(0);setSelected(null);setQuery('&'+params.toString());}}><div className="filter-grid"><label>Cari inspeksi / observasi<input type="search" value={search} maxLength={200} onChange={e=>setSearch(e.target.value)}/></label><label>Metode filter<select value={method} onChange={e=>setMethod(e.target.value)}><option value="">Semua metode</option>{methods.map(x=><option value={x} key={x}>{statusLabel(x)}</option>)}</select></label><label>Aset filter berotorisasi<select value={asset} onChange={e=>setAsset(e.target.value)}><option value="">Semua aset berotorisasi</option>{session.asset_ids.map(x=><option key={x}>{x}</option>)}</select></label><label>Status inspeksi<select value={status} onChange={e=>setStatus(e.target.value)}><option value="">Semua status</option>{['DRAFT','SUBMITTED','UNDER_REVIEW','IN_REVIEW','APPROVED','RETURNED','REJECTED'].map(x=><option key={x} value={x}>{statusLabel(x)}</option>)}</select></label><label>Waktu awal (ISO + zona waktu)<input value={since} maxLength={40} onChange={e=>setSince(e.target.value)}/></label><label>Waktu akhir (ISO + zona waktu)<input value={until} maxLength={40} onChange={e=>setUntil(e.target.value)}/></label></div><div className="engineering-actions"><Button type="submit" variant="primary">Terapkan filter server</Button><Button onClick={reload}>Muat ulang register</Button><Button onClick={()=>{setSearch('');setMethod('');setAsset('');setStatus('');setSince('');setUntil('');setQuery('');setOffset(0);}}>Hapus filter</Button></div>{filterError&&<Feedback error>{filterError}</Feedback>}</form><p>Filter register memakai waktu inspeksi asli; filter riwayat memakai waktu measurement asli. UNKNOWN tidak dimasukkan ke rentang waktu yang dipilih.</p></SectionCard>}
 <PdmBody key={session.subject} session={session} rows={page.items} selected={selected} selectRecord={selectRecord} view={view} setView={setView} query={query} onExpired={invalidate} onChanged={reload}/>
 {view==='register'&&<SectionCard><Pagination meta={page} onChange={n=>{setOffset(n);setSelected(null);}}/></SectionCard>}
 </>}
 </div>;
}
function PdmBody({session,rows,selected,selectRecord,view,setView,query,onExpired,onChanged}:{session:QaSession;rows:Inspection[];selected:string|null;selectRecord:(id:string|null)=>void;view:string;setView:(s:string)=>void;query:string;onExpired:()=>void;onChanged:()=>void}){
 const draftCache=usePdmDraft();
 const cmd=useQaCommand(session,onExpired);
 async function save(draft:InspectionDraft){const row=await cmd.run<Inspection>('inspections','POST',{draft});if(row){selectRecord(row.record_id);onChanged();return true;}return false;}
 function changeView(next:string){if(view==='entry'&&next!=='entry'){if(draftCache?.recovery&&!window.confirm('Tutup dan buang input pengukuran yang belum disimpan?'))return;draftCache?.clear();}setView(next);}
 return <><nav className="product-methods" aria-label="Area PdM Center"><Button aria-pressed={view==='register'} onClick={()=>changeView('register')}>Register Inspeksi</Button>{session.roles.includes('AUTHOR')&&<Button variant="primary" aria-pressed={view==='entry'} onClick={()=>changeView('entry')}>Input Pengukuran</Button>}<Button aria-pressed={view==='history'} onClick={()=>changeView('history')}>Riwayat & Tren</Button><Link className="button secondary" href="/engineering/cases">Analisis Engineering</Link></nav>
 {cmd.error&&<Feedback error>{cmd.error}</Feedback>}{cmd.notice&&<Feedback>{cmd.notice}</Feedback>}
 {view==='entry'&&<PdmMeasurementForm session={session} busy={cmd.busy} onSave={save} onCancel={()=>setView('register')}/>}
 {view==='history'&&<PdmHistory query={query} onExpired={onExpired} onSelect={selectRecord}/>}
 {view==='register'&&<SectionCard><h2>Register inspeksi / temuan</h2>{rows.length?<TableFrame minWidth={1050} label="Register event inspeksi berotorisasi"><table><thead><tr><th>Inspeksi / revisi</th><th>Aset</th><th>Metode / titik</th><th>Waktu inspeksi / inspector</th><th>Observasi terbaru</th><th>Review rekam</th></tr></thead><tbody>{rows.map(row=><tr key={row.record_id}><td><Button onClick={()=>selectRecord(row.record_id)}>{row.record_id}</Button><small className="table-subtext">r{row.revision}</small></td><td>{row.canonical_asset_id}</td><td>{statusLabel(row.method)} · {row.method_version}<small className="table-subtext">{[...new Set(row.measurements.map(m=>m.point_ref??'UNKNOWN'))].join(' · ')||'UNKNOWN'}</small></td><td>{row.inspected_at??'UNKNOWN'}<small className="table-subtext">{row.inspector_ref}</small></td><td>{row.observations.at(-1)??'UNKNOWN'}<small className="table-subtext">Hipotesis: {row.interpretations.at(-1)??'NOT ASSESSED'}</small></td><td><StatusBadge mode="raw-neutral" value={row.status}/></td></tr>)}</tbody></table></TableFrame>:<EmptyState title="Tidak ada inspeksi dalam filter server ini." detail="Belum ada data tidak berarti kondisi normal."/>}</SectionCard>}
 {view==='register'&&selected&&<><Button onClick={()=>selectRecord(null)}>Tutup detail inspeksi</Button><QaRecordReader<Inspection> resource="inspections" id={selected} key={selected} render={row=><PdmInspectionWorkflow initial={row} session={session} onExpired={onExpired} onChanged={onChanged}/>} onInvalid={onExpired}/></>}
 </>;
}
