import {type CaseDraft,type CaseRecord,investigationFields} from './case-records';

// Presentation validation only; the existing strict backend remains authoritative.
const nonblank=/[^\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]/u;
export function validateCaseForm(draft:CaseDraft):void {
 if(!nonblank.test(draft.title)||!nonblank.test(draft.problem_statement))throw new Error('Judul dan uraian masalah wajib diisi.');
 for(const key of investigationFields){
  const values=draft.investigation[key];
  if(values.length>20)throw new Error('Gunakan maksimal 20 butir pada setiap bagian investigasi.');
  for(const value of values){
   if(!nonblank.test(value))throw new Error('Hapus baris kosong pada catatan investigasi, atau kosongkan seluruh bagian.');
   if(Array.from(value).length>2000)throw new Error('Setiap butir investigasi maksimal 2.000 karakter.');
  }
 }
}

// Presentation affordance only. The server enforces full review authority.
export function independentCaseReviewer(row:CaseRecord,subject:string):boolean {
 const contributors=(row as CaseRecord&{contributors?:string[]}).contributors??[];
 return ![row.created_by,row.assigned_engineer,...contributors].includes(subject);
}
