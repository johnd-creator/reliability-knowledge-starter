'use client';
import {idText} from '../lib/id-copy';
import Link from 'next/link';
import QaSignInRequired from './QaSignInRequired';
import {Button,EmptyState,LoadingState,SectionCard} from './ui';
import type {QaState} from './useQaRecords';
const labels:Record<QaState,string>={ready:'QA sintetis aktif',loading:'QA sintetis · memeriksa sesi','signed-out':'QA sintetis · belum masuk',expired:'QA sintetis · sesi tidak berlaku',denied:'QA sintetis · akses ditolak',error:'QA sintetis · backend tidak tersedia','blocked-schema':'QA sintetis · prasyarat schema belum siap',disabled:'Integrasi operasional belum diaktifkan'};
export default function QaProductBoundary({state,reload}:{state:QaState;reload:()=>void}) {
 return <>
  <aside className="qa-boundary-note" aria-label="Batas data Engineering QA"><strong>{labels[state]}</strong><span>Rekam NADI sintetis; bukan izin pekerjaan atau perubahan Work Order Maximo.</span><details><summary>Batas penggunaan</summary><p>{idText('Measurements, observations, interpretations and independent review remain separate. NADI records never authorize or mutate Maximo Work Orders.')}</p><Link href="/panduan/istilah#approved">Panduan persetujuan rekam →</Link></details></aside>
  {state==='disabled'&&<EmptyState title={idText('Operational application contract UNAVAILABLE')} detail={idText('The product layout is implemented. Operational identity, record APIs and engineering acceptance require separate activation; no fixture data is substituted.')} />}
  {state==='blocked-schema'&&<EmptyState title={idText('Advisory persistence BLOCKED — QA schema prerequisite')} detail={idText('The advisory workflow is proven in disposable tests. This persistent QA store has not been migrated; draft/publication/receipt actions stay disabled until a separately authorized schema change.')}/>}
  {state==='loading'&&<LoadingState label={idText('Reading trusted session and authorized application records…')} />}
  {(state==='signed-out'||state==='expired')&&<QaSignInRequired expired={state==='expired'}/>}
  {state==='denied'&&<SectionCard><div role="alert"><h2>{idText('Record access unavailable or denied')}</h2><p>{idText('Server role and asset scopes remain authoritative. No fallback identity or public record access.')}</p></div><Button onClick={reload}>{idText('Retry authorized access')}</Button></SectionCard>}
  {state==='error'&&<SectionCard><div role="alert"><h2>{idText('Engineering records UNAVAILABLE')}</h2><p>{idText('Previously displayed records have been cleared. No automatic retry.')}</p></div><Button onClick={reload}>{idText('Try again')}</Button></SectionCard>}
 </>;
}
