import type {EvidenceReference} from '../lib/engineering';
import {statusLabel} from '../lib/id-copy';

const flag=(value:boolean|null|undefined)=>value==null?'UNKNOWN':String(value);
function originalValue(value:NonNullable<NonNullable<EvidenceReference['snapshot']>['condition']>['value']){
 if(value===null)return 'UNKNOWN';
 if(typeof value==='object')return `${value.name??'UNKNOWN'} · code ${value.code??'UNKNOWN'} · system ${flag(value.is_system)}`;
 return String(value);
}
/** Render the submitted snapshot, never fetch a current replacement for review. */
export default function FrozenCaseEvidence({evidence}:{evidence:EvidenceReference}){
 const condition=evidence.mode==='FROZEN_SNAPSHOT'?evidence.snapshot?.condition:null;
 return <div className="case-evidence-trust">
  {condition?<><h4>Nilai CONDITION pada snapshot beku</h4><p><strong>{originalValue(condition.value)}</strong> <span>{condition.unit??'UNKNOWN'}</span></p><dl>
   <div><dt>Jenis nilai / sinyal</dt><dd>{condition.value_type} · {condition.semantic_name}</dd></div>
   <div><dt>Waktu sumber snapshot / dikoleksi</dt><dd>{condition.source_timestamp??'UNKNOWN'} / {condition.collected_at??'UNKNOWN'}</dd></div>
   <div><dt>Status evidence snapshot</dt><dd>{condition.evidence_status}</dd></div>
  </dl></>:<p>{evidence.mode==='LIVE_REFERENCE'?'Referensi aktif: nilai snapshot beku tidak tersedia; nilai terkini tidak diambil otomatis.':'Snapshot ini tidak memuat nilai CONDITION.'}</p>}
  <dl>
   <div><dt>Sumber / unit referensi</dt><dd>{evidence.source??'UNKNOWN'} / {evidence.unit??'UNKNOWN'}</dd></div>
   <div><dt>Freshness / kebijakan saat ditautkan</dt><dd>{statusLabel(evidence.freshness??'UNKNOWN')} / {evidence.freshness_policy_ref??'UNKNOWN'}</dd></div>
   <div><dt>Kualitas: Good / Questionable / Substituted / Annotated</dt><dd>{flag(evidence.quality_good)} / {flag(evidence.quality_questionable)} / {flag(evidence.quality_substituted)} / {flag(evidence.quality_annotated)}</dd></div>
   <div><dt>Status identitas / persetujuan sinyal</dt><dd>{evidence.identity_status??'UNKNOWN'} / {evidence.signal_approval??'UNKNOWN'}</dd></div>
   <div><dt>Diamati / ditautkan</dt><dd>{evidence.observed_at??'UNKNOWN'} / {evidence.linked_at??'UNKNOWN'}</dd></div>
   <div><dt>Ditautkan oleh</dt><dd className="identifier">{evidence.linked_by??'UNKNOWN'}</dd></div>
  </dl><p className="section-note">Nilai, waktu, kualitas, dan freshness di atas berasal dari versi evidence yang ditautkan. Good menyatakan kualitas data; bukan kondisi peralatan baik. UNKNOWN tetap belum diketahui.</p>
 </div>;
}
