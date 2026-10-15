// Native presentation mapping to the unchanged strict InspectionDraft v1.1.
import {enteredValue,methods,type Method} from './manual-pdm';
import type {Inspection,Measurement} from './product-records';
export const inputContexts = [
 {id:'AREA_FAN',label:'AREA FAN',version:'candidate-1'},
 {id:'AREA_MILL',label:'AREA MILL',version:'candidate-1'},
 {id:'LOGSHEET_6KV',label:'Logsheet 6 kV',version:'candidate-1'},
 {id:'VIBRATION_BOILER',label:'Vibration · Boiler',version:'candidate-2'},
 {id:'VIBRATION_BC',label:'Vibration · BC/conveyor',version:'candidate-2'},
 {id:'VIBRATION_TURBINE',label:'Vibration · Turbin/pompa',version:'candidate-2'},
 {id:'CEP_CBM',label:'CEP · Thermal / IR Window provisional',version:'candidate-2'},
] as const;
// No workbook columns/units/limits are approved. Definitions bind schema paths only.
export const inputFields={inspection:['canonical_asset_id','method','method_version','inspected_at','operating_context'],measurement:['point_ref','quantity','value','unit','measured_at'],optionalContext:['instrument_ref','procedure_ref','orientation']} as const;
export type ValueKind='NUMERIC'|'TEXT'|'BOOLEAN'|'UNKNOWN';
export type EntryRow={key:string;point:string;quantity:string;kind:ValueKind;value:string;unit:string;time:string};
export interface Entry {inputContext?:string;asset:string;method:Method;version:string;time:string;context:string;rows:EntryRow[];observation:string;hypothesis:string;instrument:string;procedure:string;orientation:string;metadata?:{ref:string;filename:string;type:string;size:string;sha256:string};}
export interface InspectionDraft {canonical_asset_id:string;method:Method;method_version:string;inspector_ref:string;inspected_at:string|null;operating_context:string|null;measurements:Measurement[];observations:string[];interpretations:string[];attachments:Inspection['attachments'];case_refs:string[];method_extension:Record<string,string|number|boolean|null>;}
export function emptyRow(key:string):EntryRow{return {key,point:'',quantity:'',kind:'UNKNOWN',value:'',unit:'',time:''};}
export function newEntry(asset:string):Entry{return {asset,method:'VIBRATION',version:'',time:'',context:'',rows:[emptyRow('row-1')],observation:'',hypothesis:'',instrument:'',procedure:'',orientation:''};}
export function fromInspection(row:Inspection):Entry{return {asset:row.canonical_asset_id,method:row.method as Method,version:row.method_version,time:row.inspected_at??'',context:row.operating_context??'',rows:row.measurements.map((m,i)=>({key:`row-${i}`,point:m.point_ref??'',quantity:m.quantity,kind:m.value===null?'UNKNOWN':typeof m.value==='number'?'NUMERIC':typeof m.value==='boolean'?'BOOLEAN':'TEXT',value:m.value===null?'':String(m.value),unit:m.unit??'',time:m.measured_at??''})),observation:row.observations.join('\n'),hypothesis:row.interpretations.join('\n'),instrument:String(row.method_extension?.instrument_ref??''),procedure:String(row.method_extension?.procedure_ref??''),orientation:String(row.method_extension?.orientation??'')};}
function bounded(value:string,max:number,label:string,required=false){if(Array.from(value).length>max||required&&!value.trim())throw Error(`${label}: isi teks yang tidak kosong, maksimal ${max} karakter.`);return value;}
export function eventTime(value:string,label:string,now:number):string|null{
 if(value==='')return null;
 const parts=/^(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(Z|[+-]\d\d:\d\d)$/.exec(value);
 const validCalendar=parts&&Number(parts[2])>=1&&Number(parts[2])<=12&&Number(parts[3])>=1&&Number(parts[3])<=new Date(Date.UTC(Number(parts[1]),Number(parts[2]),0)).getUTCDate()&&Number(parts[4])<24&&Number(parts[5])<60&&Number(parts[6])<60;
 if(!validCalendar||!Number.isFinite(Date.parse(value)))throw Error(`${label}: gunakan timestamp ISO dengan zona waktu, misalnya 2026-10-09T08:00:00+07:00.`);
 if(Date.parse(value)>now)throw Error(`${label}: waktu tidak boleh di masa depan.`);
 return value; // Keep the entered timezone/time; no invented samples.
}
function lines(value:string,label:string){if(value==='')return [];const values=value.split('\n');if(values.length>20)throw Error(`${label}: maksimal 20 baris.`);return values.map(x=>bounded(x,2000,label,true));}
export function buildDraft(entry:Entry,subject:string,assets:string[],base?:Inspection,now=Date.now()):InspectionDraft{
 if(!assets.includes(entry.asset))throw Error('Pilih identitas aset dari direktori berotorisasi.');
 if(!methods.includes(entry.method))throw Error('Metode tidak tersedia dalam kontrak.');
 if(entry.rows.length>100)throw Error('Maksimal 100 measurement per inspeksi.');
 const measurements=entry.rows.map((row,i)=>{
  const label=`Baris ${i+1}`;
  if(row.kind!=='UNKNOWN'&&row.value==='')throw Error(`${label}: nilai kosong bukan nol; pilih Belum diketahui untuk null.`);
  let value:Measurement['value'];try{value=enteredValue(row.value,row.kind);}catch{throw Error(`${label}: masukkan angka finite, teks asli, true/false, atau pilih Belum diketahui untuk null.`);}if(typeof value==='string')bounded(value,2000,label);
  return {point_ref:bounded(row.point,200,label)||null,quantity:bounded(row.quantity,120,label+' parameter',true),value,unit:bounded(row.unit,40,label)||null,measured_at:eventTime(row.time,label+' waktu',now),quality:base?.measurements[Number(row.key.replace('row-',''))]?.quality??'INSPECTOR_REPORTED',provenance:'HUMAN_ENTERED_MEASUREMENT'};
 });
 const extension={...base?.method_extension};
 for(const [key,value] of [['instrument_ref',entry.instrument],['procedure_ref',entry.procedure],['orientation',entry.orientation]]){
  // Explicit candidate scalar fields only, never an arbitrary metadata editor.
  if(value!=='')extension[key]=bounded(value,2000,key);else delete extension[key];
 }
 let attachments=base?.attachments??[];
 const metadata=entry.metadata;
 if(metadata&&Object.values(metadata).some(Boolean)){
  if(!/^attachment:[A-Za-z0-9_.:-]{1,90}$/.test(metadata.ref))throw Error('Referensi metadata harus berformat attachment:identitas.');
  if(!metadata.filename.trim()||/[\\/]/.test(metadata.filename)||['.','..'].includes(metadata.filename)||Array.from(metadata.filename).length>200)throw Error('Nama evidence harus berupa basename yang aman.');
  if(!['application/pdf','image/png','image/jpeg','text/csv','text/plain'].includes(metadata.type))throw Error('Tipe metadata tidak didukung.');
  if(!/^\d+$/.test(metadata.size)||Number(metadata.size)>10485760)throw Error('Ukuran metadata harus integer 0–10485760 byte.');
  if(metadata.sha256&&!/^[0-9a-f]{64}$/.test(metadata.sha256))throw Error('SHA256 harus 64 karakter hex lowercase, atau kosong bila belum diketahui.');
  if(attachments.length>=10||attachments.some(x=>x.attachment_ref===metadata.ref))throw Error('Maksimal 10 referensi metadata unik.');
  attachments=[...attachments,{attachment_ref:metadata.ref,filename:metadata.filename,content_type:metadata.type,size_bytes:Number(metadata.size),sha256:metadata.sha256||null,status:'METADATA_ONLY_NOT_UPLOADED'}];
 }
 return {canonical_asset_id:entry.asset,method:entry.method,method_version:bounded(entry.version,80,'Versi metode',true),inspector_ref:subject,inspected_at:eventTime(entry.time,'Waktu inspeksi',now),operating_context:bounded(entry.context,6000,'Konteks operasi')||null,measurements,observations:lines(entry.observation,'Observasi'),interpretations:lines(entry.hypothesis,'Hipotesis'),attachments,case_refs:base?.case_refs??[],method_extension:extension};
}
export interface MeasurementEvent {record_id:string;revision:number;measurement_index:number;canonical_asset_id:string;method:string;method_version:string;inspector_ref:string;status:string;measurement:Measurement;operating_context:string|null;method_extension:Record<string,string|number|boolean|null>;field_approval:string;provenance:string;}
// Within ONE acquisition only. Equal labels never authorize cross-inspection comparison.
export function rawPlot(events:MeasurementEvent[]):{reason:string;points:{time:number;value:number;label:string}[];unit:string}{
 const deny=(reason:string)=>({reason,points:[],unit:''});
 if(!events.length)return deny('Belum ada measurement untuk konteks ini.');
 const first=events[0],m=first.measurement;
 if(events.some(e=>e.record_id!==first.record_id||e.revision!==first.revision))return deny('Kesetaraan antarinspeksi belum disetujui engineer. Pilih satu inspeksi; nama/unit yang sama tidak membuktikan kompatibilitas.');
 if(!m.point_ref||!m.unit||!first.operating_context||!first.method_version)return deny('Titik, unit, versi metode, atau konteks operasi belum tersedia. Tidak membentuk seri yang sebanding.');
 const ctx=first.method_extension;
 if(!ctx?.instrument_ref||!ctx.procedure_ref||!ctx.orientation)return deny('Referensi instrumen, prosedur, atau orientasi belum tersedia. Kesetaraan tetap belum diketahui.');
 if(events.some(e=>e.method!==first.method||e.method_version!==first.method_version||e.operating_context!==first.operating_context||JSON.stringify(e.method_extension)!==JSON.stringify(ctx)||e.measurement.point_ref!==m.point_ref||e.measurement.quantity!==m.quantity||e.measurement.unit!==m.unit||e.measurement.provenance!=='HUMAN_ENTERED_MEASUREMENT'))return deny('Titik, parameter, unit, atau konteks berbeda. Measurement tidak digabungkan.');
 if(events.some(e=>typeof e.measurement.value!=='number'||!Number.isFinite(e.measurement.value)||!e.measurement.measured_at||!Number.isFinite(Date.parse(e.measurement.measured_at))))return deny('Nilai nonnumerik/null atau waktu yang belum diketahui tetap ditampilkan di tabel; tidak diubah menjadi sampel angka.');
 return {reason:'Sampel asli dalam satu inspeksi, titik terpisah tanpa interpolasi. Bukan tren lintas inspeksi, diagnosis, atau kesetaraan yang disetujui.',unit:m.unit,points:events.map(e=>({time:Date.parse(e.measurement.measured_at!),value:e.measurement.value as number,label:e.measurement.measured_at!})).sort((a,b)=>a.time-b.time)};
}
