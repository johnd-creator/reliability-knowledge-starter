// Sanitized header-only candidates. Source paths/hashes and raw cells stay private.
// Profiles describe one inspected worksheet variant, never all sheets in a workbook.
import {emptyRow,type EntryRow} from './pdm-input';
import type {Method} from './manual-pdm';
export type WorkbookBinding={id:string;label:string;unit:string;headerCells:string[];unitCell:string;valueRange:string;classification:'DIRECT'};
export type WorkbookProfile={id:string;context:string;label:string;version:string;sourceRef:string;filename:string;sheetIndex:number;methodTerm:Method;headerRange:string;approval:'PENDING_ENGINEER_VALIDATION';fields:WorkbookBinding[];unresolved:string[]};
export const workbookProfiles:readonly WorkbookProfile[]=[
 {id:'fan-s02-tribology',context:'AREA_FAN',label:'Profil sumber S02 · Tribology',version:'candidate-0.1.0',sourceRef:'WB-FAN-01',filename:'AREA FAN.xlsx',sheetIndex:1,methodTerm:'TRIBOLOGY',headerRange:'A5:T7',approval:'PENDING_ENGINEER_VALIDATION',fields:[
  {id:'viscosity',label:'Viscosity (Cst)',unit:'Cst',headerCells:['G6'],unitCell:'G6',valueRange:'G8:G136',classification:'DIRECT'},
  {id:'acid-number',label:'Acid Number (mgKOH/g)',unit:'mgKOH/g',headerCells:['I5'],unitCell:'I5',valueRange:'I8:I136',classification:'DIRECT'},
  {id:'ferrous',label:'Ferrous',unit:'ppm',headerCells:['K5'],unitCell:'K6',valueRange:'K8:K136',classification:'DIRECT'},
 ],unresolved:['Water Content di kolom F dan Result/Perhitungan memuat formula; tidak dipakai sebagai pembacaan asli.','Cleanliness ISO Code, PMI dan varian sheet lain menunggu definisi serta pemetaan engineer.']},
 {id:'mill-s01-tribology',context:'AREA_MILL',label:'Profil sumber S01 · Tribology',version:'candidate-0.1.0',sourceRef:'WB-MILL-01',filename:'AREA MILL.xlsx',sheetIndex:0,methodTerm:'TRIBOLOGY',headerRange:'A5:U7',approval:'PENDING_ENGINEER_VALIDATION',fields:[
  {id:'water-content',label:'Water Content\n(%)',unit:'%',headerCells:['F5'],unitCell:'F5',valueRange:'F8:F136',classification:'DIRECT'},
  {id:'acid-number',label:'Acid Number (mg KOH/g)',unit:'mg KOH/g',headerCells:['I5'],unitCell:'I5',valueRange:'I8:I136',classification:'DIRECT'},
  {id:'ferrous',label:'Ferrous\n(ppm)',unit:'ppm',headerCells:['J5'],unitCell:'J5',valueRange:'J8:J136',classification:'DIRECT'},
 ],unresolved:['Water Content % dipertahankan; tidak dikonversi menjadi ppm dari tabel lain.','Viscosity/Result memuat formula; PMI, unit varian sheet dan nilai teks perlu review engineer.']},
 {id:'logsheet-s01-mcsa',context:'LOGSHEET_6KV',label:'Profil sumber S01 · MCSA',version:'candidate-0.1.0',sourceRef:'WB-6KV-01',filename:'Logsheet 6 kV.xls',sheetIndex:0,methodTerm:'MCSA',headerRange:'B10:BA12',approval:'PENDING_ENGINEER_VALIDATION',fields:[
  {id:'load',label:'Load',unit:'%',headerCells:['E14'],unitCell:'F14',valueRange:'H14:AW14',classification:'DIRECT'},
  {id:'impedance-phase-1',label:'Impedance Phase 1 ',unit:'Ω',headerCells:['E35'],unitCell:'F35',valueRange:'H35:AW35',classification:'DIRECT'},
  {id:'upper-sideband',label:'Upper Sideband',unit:'dB',headerCells:['E39'],unitCell:'F39',valueRange:'H39:AW39',classification:'DIRECT'},
 ],unresolved:['RMS belum menetapkan A atau V; CF, PF dan baris tanpa unit tidak diberi satuan rekaan.','Warning, Rotorbar Health, Bearing dan Kondisi tidak menjadi severity atau diagnosis otomatis.','Header tanggal tidak selalu terisi dan tanpa zona waktu; identitas peralatan/titik belum terikat ke Registry.']},
];
export function workbookProfile(id:string){return workbookProfiles.find(x=>x.id===id);}
export function workbookRows(id:string,method:Method,nextKey:()=>string):EntryRow[]{
 const profile=workbookProfile(id);
 if(!profile)throw Error('Profil workbook tidak dikenali.');
 // Explicit user method selection is separate from choosing an area/context.
 if(method!==profile.methodTerm)throw Error('Pilih metode secara eksplisit sesuai istilah sumber; konteks area tidak memilih metode.');
 return profile.fields.map(field=>({...emptyRow(nextKey()),quantity:field.label,unit:field.unit}));
}
