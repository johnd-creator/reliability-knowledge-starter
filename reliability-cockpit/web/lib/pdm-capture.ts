// Provisional source input is deliberately separate from canonical measurements.
import {enteredValue} from './manual-pdm';
export type Scalar=string|number|boolean|null;
export type ClockRole='ACQUISITION'|'SAMPLE'|'ANALYSIS'|'REPORT'|'UNSPECIFIED';
export type Precision='DATE'|'DATETIME'|'LOCAL_DATETIME'|'TIME'|'RAW'|'UNKNOWN';
export interface CaptureClock {role:ClockRole;precision:Precision;raw_value:Scalar;value:string|null;source_label:string|null;}
export interface CaptureContext {role:'ACQUISITION'|'OPERATING_CONTEXT'|'LAB'|'INSTRUMENT'|'PROCEDURE'|'CAMERA'|'SAMPLE'|'REPORT';label:string;raw_value:Scalar;unit:string|null;}
export interface CaptureRow {row_id:string;source_field_id?:string|null;value_region?:string|null;source_label:string;raw_value:Scalar;unit:string|null;source_point:string|null;source_axis:string|null;header_cells:string[];value_origin:'SOURCE_LITERAL'|'SOURCE_FORMULA_RESULT'|'MANUAL_REPORTED'|'UNKNOWN';row_role:'INPUT'|'REFERENCE'|'SOURCE_ASSESSMENT';contexts:CaptureContext[];clock:CaptureClock|null;}
export interface InputCapture {source_asset_label?:string|null;source_sheet_label?:string|null;schema_version:'1.0';purpose:'PROVISIONAL_INPUT_ONLY';source_ref:string;source_sha256:string|null;sheet_index:number|null;profile_id:string;profile_version:string;clocks:CaptureClock[];rows:CaptureRow[];}
export type CaptureEntryRow=Omit<CaptureRow,'raw_value'> & {kind:'NUMERIC'|'TEXT'|'BOOLEAN'|'UNKNOWN';value:string};
export type CaptureEntry=Omit<InputCapture,'rows'> & {rows:CaptureEntryRow[]};
export const precisionLabels:Record<Precision,string>={DATE:'Tanggal saja',DATETIME:'Tanggal & jam dengan zona waktu',LOCAL_DATETIME:'Tanggal & jam lokal; zona belum diketahui',TIME:'Jam saja',RAW:'Teks / serial asli; belum ditafsirkan',UNKNOWN:'Belum diketahui'};
export const clockLabels:Record<ClockRole,string>={ACQUISITION:'Pengambilan data',SAMPLE:'Pengambilan sampel',ANALYSIS:'Analisis',REPORT:'Laporan',UNSPECIFIED:'Peran waktu belum diketahui'};
export function blankClock():CaptureClock{return {role:'UNSPECIFIED',precision:'UNKNOWN',raw_value:null,value:null,source_label:null};}
export function captureFromStored(c:InputCapture):CaptureEntry{return {...c,rows:c.rows.map(r=>{const {raw_value,...rest}=r;return {...rest,kind:raw_value===null?'UNKNOWN':typeof raw_value==='number'?'NUMERIC':typeof raw_value==='boolean'?'BOOLEAN':'TEXT',value:raw_value===null?'':String(raw_value)};})};}
export function blankCaptureRow(id:string):CaptureEntryRow{return {row_id:id,source_label:'',kind:'UNKNOWN',value:'',unit:null,source_point:null,source_axis:null,header_cells:[],value_origin:'MANUAL_REPORTED',row_role:'INPUT',contexts:[],clock:null};}
function text(v:string,max:number,label:string,required=false){if(Array.from(v).length>max||(required&&!v.trim()))throw Error(`${label}: teks ${required?'wajib diisi, ':''}maksimal ${max} karakter.`);return v;}
function calendar(v:string){const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(v);return !!m&&+m[1]>=1&&+m[2]>=1&&+m[2]<=12&&+m[3]>=1&&+m[3]<=new Date(Date.UTC(+m[1],+m[2],0)).getUTCDate();}
export function validateClock(c:CaptureClock):CaptureClock{
 const v=c.value??'';text(v,80,'Nilai waktu');if(c.source_label!==null)text(c.source_label,200,'Label waktu');
 if(c.precision==='UNKNOWN'||c.precision==='RAW'){if(c.value!==null)throw Error('Waktu mentah / belum diketahui tidak boleh memiliki timestamp tafsiran.');}
 else if(c.raw_value===null||typeof c.raw_value==='boolean')throw Error('Isi waktu asli / serial sebelum menyatakan nilai kalender.');
 else if(c.precision==='DATE'){if(!calendar(v))throw Error('Tanggal sumber: gunakan YYYY-MM-DD yang sah.');}
 else if(c.precision==='TIME'){if(!/^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d{1,6})?)?$/.test(v))throw Error('Jam sumber: gunakan HH:mm atau HH:mm:ss.');}
 else {const zone=c.precision==='DATETIME'?'(?:[Zz]|[+-](?:[01]\\d|2[0-3]):[0-5]\\d)':'';const pattern=new RegExp('^\\d{4}-\\d{2}-\\d{2}[Tt](?:[01]\\d|2[0-3]):[0-5]\\d(?::[0-5]\\d(?:\\.\\d{1,6})?)?'+zone+'$');if(!pattern.test(v)||!calendar(v.slice(0,10))||c.precision==='DATETIME'&&!Number.isFinite(Date.parse(v)))throw Error('Tanggal & jam sumber tidak sah; nyatakan zona waktu hanya bila diketahui.');}
 if(typeof c.raw_value==='string')text(c.raw_value,2000,'Waktu asli');if(typeof c.raw_value==='number'&&!Number.isFinite(c.raw_value))throw Error('Serial waktu harus finite.');return c;
}
export function buildCapture(c:CaptureEntry):InputCapture{
 if(c.source_asset_label!==undefined&&c.source_asset_label!==null)text(c.source_asset_label,2000,'Label aset sumber');if(c.source_sheet_label!==undefined&&c.source_sheet_label!==null)text(c.source_sheet_label,2000,'Label sheet sumber');
 text(c.source_ref,120,'Referensi workbook',true);text(c.profile_id,120,'Profil',true);text(c.profile_version,80,'Versi profil',true);
 if(c.source_sha256!==null&&!/^[0-9a-f]{64}$/.test(c.source_sha256))throw Error('Hash sumber tidak sah.');
 if(c.sheet_index!==null&&(!Number.isInteger(c.sheet_index)||c.sheet_index<0))throw Error('Indeks sheet tidak sah.');
 if(!c.rows.length||c.rows.length>100)throw Error('Input sumber memerlukan 1–100 baris.');if(c.clocks.length>12)throw Error('Maksimal 12 konteks waktu.');
 const ids=new Set<string>();const rows=c.rows.map((r,i)=>{text(r.row_id,80,'Identitas baris',true);if(!/^[A-Za-z0-9_.:-]+$/.test(r.row_id))throw Error('Identitas baris tidak sah.');if(ids.has(r.row_id))throw Error('Identitas baris harus unik.');ids.add(r.row_id);text(r.source_label,2000,`Label sumber ${i+1}`,true);if(r.source_field_id)text(r.source_field_id,120,'Identitas field sumber');if(r.value_region&&!/^\$?[A-Z]{1,3}\$?[1-9]\d{0,6}(?::\$?[A-Z]{1,3}\$?[1-9]\d{0,6})?$/.test(r.value_region))throw Error('Rentang nilai sumber tidak sah.');if(r.unit!==null)text(r.unit,80,'Unit');if(r.source_point!==null)text(r.source_point,200,'Label titik');if(r.source_axis!==null)text(r.source_axis,80,'Label axis');if(r.header_cells.length>20||r.header_cells.some(x=>!/^\$?[A-Z]{1,3}\$?[1-9]\d{0,6}(?::\$?[A-Z]{1,3}\$?[1-9]\d{0,6})?$/.test(x)))throw Error('Referensi sel header tidak sah.');
  const {kind,value,...rest}=r;if(['NUMERIC','BOOLEAN'].includes(kind)&&value==='')throw Error(`Baris ${i+1}: kosong bukan nol; pilih belum diketahui.`);let raw_value:Scalar;try{raw_value=enteredValue(value,kind);}catch{throw Error(`Baris ${i+1}: nilai tidak sah / bukan angka finite.`);}if(typeof raw_value==='string')text(raw_value,2000,'Nilai asli');
  if(r.contexts.length>20)throw Error('Maksimal 20 konteks per baris.');for(const x of r.contexts){text(x.label,200,'Label konteks',true);if(typeof x.raw_value==='string')text(x.raw_value,2000,'Konteks asli');if(typeof x.raw_value==='number'&&!Number.isFinite(x.raw_value))throw Error('Konteks angka harus finite.');if(x.unit!==null)text(x.unit,80,'Unit konteks');}
  return {...rest,raw_value,clock:r.clock?validateClock(r.clock):null};
 });return {...c,schema_version:'1.0',purpose:'PROVISIONAL_INPUT_ONLY',rows,clocks:c.clocks.map(validateClock)};
}
