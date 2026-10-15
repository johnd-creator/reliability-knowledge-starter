// Sanitized header-only candidates. Source paths/hashes and raw cells stay private.
// Profiles describe one inspected worksheet variant, never all sheets in a workbook.
import {emptyRow,type EntryRow} from './pdm-input';
import type {Method} from './manual-pdm';
export type WorkbookBinding={id:string;label:string;unit:string;headerCells:string[];unitCell:string;valueRange:string;classification:'DIRECT'|'AMBIGUOUS';sourcePointLabel?:string;sourceAxis?:string};
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
 {
   "id": "boiler-three-point-rms",
   "context": "VIBRATION_BOILER",
   "label": "Boiler · tiga titik / sembilan axis RMS",
   "version": "candidate-0.2.0",
   "sourceRef": "WB-VIB-BOILER-02",
   "filename": "TRENDING VIBRASI BOILER AREA.xlsx",
   "sheetIndex": 35,
   "methodTerm": "VIBRATION",
   "headerRange": "A1:N2",
   "approval": "PENDING_ENGINEER_VALIDATION",
   "fields": [
     {
       "id": "axis-1V",
       "label": "1V",
       "unit": "mm/s-rms",
       "headerCells": [
         "B2"
       ],
       "unitCell": "B1",
       "valueRange": "B3:B145",
       "classification": "DIRECT",
       "sourcePointLabel": "1V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-1H",
       "label": "1H",
       "unit": "mm/s-rms",
       "headerCells": [
         "C2"
       ],
       "unitCell": "B1",
       "valueRange": "C3:C145",
       "classification": "DIRECT",
       "sourcePointLabel": "1H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-1A",
       "label": "1A",
       "unit": "mm/s-rms",
       "headerCells": [
         "D2"
       ],
       "unitCell": "B1",
       "valueRange": "D3:D145",
       "classification": "DIRECT",
       "sourcePointLabel": "1A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-2V",
       "label": "2V",
       "unit": "mm/s-rms",
       "headerCells": [
         "E2"
       ],
       "unitCell": "B1",
       "valueRange": "E3:E145",
       "classification": "DIRECT",
       "sourcePointLabel": "2V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-2H",
       "label": "2H",
       "unit": "mm/s-rms",
       "headerCells": [
         "F2"
       ],
       "unitCell": "B1",
       "valueRange": "F3:F145",
       "classification": "DIRECT",
       "sourcePointLabel": "2H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-2A",
       "label": "2A",
       "unit": "mm/s-rms",
       "headerCells": [
         "G2"
       ],
       "unitCell": "B1",
       "valueRange": "G3:G145",
       "classification": "DIRECT",
       "sourcePointLabel": "2A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-3V",
       "label": "3V",
       "unit": "mm/s-rms",
       "headerCells": [
         "H2"
       ],
       "unitCell": "B1",
       "valueRange": "H3:H145",
       "classification": "DIRECT",
       "sourcePointLabel": "3V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-3H",
       "label": "3H",
       "unit": "mm/s-rms",
       "headerCells": [
         "I2"
       ],
       "unitCell": "B1",
       "valueRange": "I3:I145",
       "classification": "DIRECT",
       "sourcePointLabel": "3H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-3A",
       "label": "3A",
       "unit": "mm/s-rms",
       "headerCells": [
         "J2"
       ],
       "unitCell": "B1",
       "valueRange": "J3:J145",
       "classification": "DIRECT",
       "sourcePointLabel": "3A",
       "sourceAxis": "A"
     }
   ],
   "unresolved": [
     "Label titik/axis sumber bukan point_ref kanonis; arti axis, besaran, bandwidth, RMS/p-p, instrumen dan pemasangan perlu engineer.",
     "Tidak menggabungkan portable, DCS/Bently, displacement atau velocity. Unit asli tidak dikonversi.",
     "v1.1 hanya memiliki orientasi/instrumen/prosedur tingkat inspeksi; pisahkan inspeksi bila konteks titik berbeda. Waktu dan binding titik tetap kosong."
   ]
 },
 {
   "id": "boiler-five-axis",
   "context": "VIBRATION_BOILER",
   "label": "Boiler · lima axis sumber",
   "version": "candidate-0.2.0",
   "sourceRef": "WB-VIB-BOILER-02",
   "filename": "TRENDING VIBRASI BOILER AREA.xlsx",
   "sheetIndex": 12,
   "methodTerm": "VIBRATION",
   "headerRange": "A1:G2",
   "approval": "PENDING_ENGINEER_VALIDATION",
   "fields": [
     {
       "id": "axis-1V",
       "label": "1V",
       "unit": "mm/s",
       "headerCells": [
         "B2"
       ],
       "unitCell": "B1",
       "valueRange": "B3:B77",
       "classification": "DIRECT",
       "sourcePointLabel": "1V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-1H",
       "label": "1H",
       "unit": "mm/s",
       "headerCells": [
         "C2"
       ],
       "unitCell": "B1",
       "valueRange": "C3:C77",
       "classification": "DIRECT",
       "sourcePointLabel": "1H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-2V",
       "label": "2V",
       "unit": "mm/s",
       "headerCells": [
         "D2"
       ],
       "unitCell": "B1",
       "valueRange": "D3:D77",
       "classification": "DIRECT",
       "sourcePointLabel": "2V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-2H",
       "label": "2H",
       "unit": "mm/s",
       "headerCells": [
         "E2"
       ],
       "unitCell": "B1",
       "valueRange": "E3:E77",
       "classification": "DIRECT",
       "sourcePointLabel": "2H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-2A",
       "label": "2A",
       "unit": "mm/s",
       "headerCells": [
         "F2"
       ],
       "unitCell": "B1",
       "valueRange": "F3:F77",
       "classification": "DIRECT",
       "sourcePointLabel": "2A",
       "sourceAxis": "A"
     }
   ],
   "unresolved": [
     "Label titik/axis sumber bukan point_ref kanonis; arti axis, besaran, bandwidth, RMS/p-p, instrumen dan pemasangan perlu engineer.",
     "Tidak menggabungkan portable, DCS/Bently, displacement atau velocity. Unit asli tidak dikonversi.",
     "v1.1 hanya memiliki orientasi/instrumen/prosedur tingkat inspeksi; pisahkan inspeksi bila konteks titik berbeda. Waktu dan binding titik tetap kosong."
   ]
 },
 {
   "id": "bc-irregular-axis",
   "context": "VIBRATION_BC",
   "label": "BC · subset axis tidak lengkap",
   "version": "candidate-0.2.0",
   "sourceRef": "WB-VIB-BC-02",
   "filename": "TRENDING VIBRASI BC AREA EPA.xlsx",
   "sheetIndex": 0,
   "methodTerm": "VIBRATION",
   "headerRange": "A1:AB2",
   "approval": "PENDING_ENGINEER_VALIDATION",
   "fields": [
     {
       "id": "axis-1V",
       "label": "1V",
       "unit": "mm/s",
       "headerCells": [
         "B2"
       ],
       "unitCell": "B1",
       "valueRange": "B3:B59",
       "classification": "DIRECT",
       "sourcePointLabel": "1V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-1H",
       "label": "1H",
       "unit": "mm/s",
       "headerCells": [
         "C2"
       ],
       "unitCell": "B1",
       "valueRange": "C3:C59",
       "classification": "DIRECT",
       "sourcePointLabel": "1H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-1A",
       "label": "1A",
       "unit": "mm/s",
       "headerCells": [
         "D2"
       ],
       "unitCell": "B1",
       "valueRange": "D3:D59",
       "classification": "DIRECT",
       "sourcePointLabel": "1A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-2V",
       "label": "2V",
       "unit": "mm/s",
       "headerCells": [
         "E2"
       ],
       "unitCell": "B1",
       "valueRange": "E3:E59",
       "classification": "DIRECT",
       "sourcePointLabel": "2V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-2H",
       "label": "2H",
       "unit": "mm/s",
       "headerCells": [
         "F2"
       ],
       "unitCell": "B1",
       "valueRange": "F3:F59",
       "classification": "DIRECT",
       "sourcePointLabel": "2H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-2A",
       "label": "2A",
       "unit": "mm/s",
       "headerCells": [
         "G2"
       ],
       "unitCell": "B1",
       "valueRange": "G3:G59",
       "classification": "DIRECT",
       "sourcePointLabel": "2A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-3V",
       "label": "3V",
       "unit": "mm/s",
       "headerCells": [
         "H2"
       ],
       "unitCell": "B1",
       "valueRange": "H3:H59",
       "classification": "DIRECT",
       "sourcePointLabel": "3V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-3H",
       "label": "3H",
       "unit": "mm/s",
       "headerCells": [
         "I2"
       ],
       "unitCell": "B1",
       "valueRange": "I3:I59",
       "classification": "DIRECT",
       "sourcePointLabel": "3H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-3A",
       "label": "3A",
       "unit": "mm/s",
       "headerCells": [
         "J2"
       ],
       "unitCell": "B1",
       "valueRange": "J3:J59",
       "classification": "DIRECT",
       "sourcePointLabel": "3A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-6V",
       "label": "6V",
       "unit": "mm/s",
       "headerCells": [
         "Q2"
       ],
       "unitCell": "B1",
       "valueRange": "Q3:Q59",
       "classification": "DIRECT",
       "sourcePointLabel": "6V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-6A",
       "label": "6A",
       "unit": "mm/s",
       "headerCells": [
         "R2"
       ],
       "unitCell": "B1",
       "valueRange": "R3:R59",
       "classification": "DIRECT",
       "sourcePointLabel": "6A",
       "sourceAxis": "A"
     }
   ],
   "unresolved": [
     "Label titik/axis sumber bukan point_ref kanonis; arti axis, besaran, bandwidth, RMS/p-p, instrumen dan pemasangan perlu engineer.",
     "Tidak menggabungkan portable, DCS/Bently, displacement atau velocity. Unit asli tidak dikonversi.",
     "v1.1 hanya memiliki orientasi/instrumen/prosedur tingkat inspeksi; pisahkan inspeksi bila konteks titik berbeda. Waktu dan binding titik tetap kosong.",
     "Subset 11 dari 26 kolom axis. Sumber melewati 6H; tidak menambahkan axis hilang atau menyamakan konfigurasi sheet lain."
   ]
 },
 {
   "id": "turbine-four-point",
   "context": "VIBRATION_TURBINE",
   "label": "Turbin/pompa · empat titik / dua belas axis",
   "version": "candidate-0.2.0",
   "sourceRef": "WB-VIB-TURBINE-02",
   "filename": "TRENDING VIBRASI TURBIN AREA.xlsx",
   "sheetIndex": 14,
   "methodTerm": "VIBRATION",
   "headerRange": "A1:N2",
   "approval": "PENDING_ENGINEER_VALIDATION",
   "fields": [
     {
       "id": "axis-1V",
       "label": "1V",
       "unit": "mm/s",
       "headerCells": [
         "B2"
       ],
       "unitCell": "B1",
       "valueRange": "B3:B95",
       "classification": "DIRECT",
       "sourcePointLabel": "1V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-1H",
       "label": "1H",
       "unit": "mm/s",
       "headerCells": [
         "C2"
       ],
       "unitCell": "B1",
       "valueRange": "C3:C95",
       "classification": "DIRECT",
       "sourcePointLabel": "1H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-1A",
       "label": "1A",
       "unit": "mm/s",
       "headerCells": [
         "D2"
       ],
       "unitCell": "B1",
       "valueRange": "D3:D95",
       "classification": "DIRECT",
       "sourcePointLabel": "1A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-2V",
       "label": "2V",
       "unit": "mm/s",
       "headerCells": [
         "E2"
       ],
       "unitCell": "B1",
       "valueRange": "E3:E95",
       "classification": "DIRECT",
       "sourcePointLabel": "2V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-2H",
       "label": "2H",
       "unit": "mm/s",
       "headerCells": [
         "F2"
       ],
       "unitCell": "B1",
       "valueRange": "F3:F95",
       "classification": "DIRECT",
       "sourcePointLabel": "2H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-2A",
       "label": "2A",
       "unit": "mm/s",
       "headerCells": [
         "G2"
       ],
       "unitCell": "B1",
       "valueRange": "G3:G95",
       "classification": "DIRECT",
       "sourcePointLabel": "2A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-3V",
       "label": "3V",
       "unit": "mm/s",
       "headerCells": [
         "H2"
       ],
       "unitCell": "B1",
       "valueRange": "H3:H95",
       "classification": "DIRECT",
       "sourcePointLabel": "3V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-3H",
       "label": "3H",
       "unit": "mm/s",
       "headerCells": [
         "I2"
       ],
       "unitCell": "B1",
       "valueRange": "I3:I95",
       "classification": "DIRECT",
       "sourcePointLabel": "3H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-3A",
       "label": "3A",
       "unit": "mm/s",
       "headerCells": [
         "J2"
       ],
       "unitCell": "B1",
       "valueRange": "J3:J95",
       "classification": "DIRECT",
       "sourcePointLabel": "3A",
       "sourceAxis": "A"
     },
     {
       "id": "axis-4V",
       "label": "4V",
       "unit": "mm/s",
       "headerCells": [
         "K2"
       ],
       "unitCell": "B1",
       "valueRange": "K3:K95",
       "classification": "DIRECT",
       "sourcePointLabel": "4V",
       "sourceAxis": "V"
     },
     {
       "id": "axis-4H",
       "label": "4H",
       "unit": "mm/s",
       "headerCells": [
         "L2"
       ],
       "unitCell": "B1",
       "valueRange": "L3:L95",
       "classification": "DIRECT",
       "sourcePointLabel": "4H",
       "sourceAxis": "H"
     },
     {
       "id": "axis-4A",
       "label": "4A",
       "unit": "mm/s",
       "headerCells": [
         "M2"
       ],
       "unitCell": "B1",
       "valueRange": "M3:M95",
       "classification": "DIRECT",
       "sourcePointLabel": "4A",
       "sourceAxis": "A"
     }
   ],
   "unresolved": [
     "Label titik/axis sumber bukan point_ref kanonis; arti axis, besaran, bandwidth, RMS/p-p, instrumen dan pemasangan perlu engineer.",
     "Tidak menggabungkan portable, DCS/Bently, displacement atau velocity. Unit asli tidak dikonversi.",
     "v1.1 hanya memiliki orientasi/instrumen/prosedur tingkat inspeksi; pisahkan inspeksi bila konteks titik berbeda. Waktu dan binding titik tetap kosong."
   ]
 },
 {
   "id": "cep-bearing-cbm",
   "context": "CEP_CBM",
   "label": "CEP · temperatur bearing / CBM provisional",
   "version": "candidate-0.2.0",
   "sourceRef": "WB-CEP-02",
   "filename": "New Log Sheet_CEP_CBM1.xls",
   "sheetIndex": 0,
   "methodTerm": "OTHER",
   "headerRange": "D11:H31",
   "approval": "PENDING_ENGINEER_VALIDATION",
   "fields": [
     {
       "id": "current",
       "label": "Current (Ampere)",
       "unit": "Ampere",
       "headerCells": [
         "D17"
       ],
       "unitCell": "D17",
       "valueRange": "I17:BP17",
       "classification": "DIRECT"
     },
     {
       "id": "temperature-19",
       "label": "Motor Thrust Brg Temp (1)",
       "unit": "",
       "headerCells": [
         "D19"
       ],
       "unitCell": "",
       "valueRange": "I19:BP19",
       "classification": "AMBIGUOUS"
     },
     {
       "id": "temperature-20",
       "label": "Motor Inboard Brg Temp (2)",
       "unit": "",
       "headerCells": [
         "D20"
       ],
       "unitCell": "",
       "valueRange": "I20:BP20",
       "classification": "AMBIGUOUS"
     },
     {
       "id": "temperature-21",
       "label": "Pump Brg Temp (3)",
       "unit": "",
       "headerCells": [
         "D21"
       ],
       "unitCell": "",
       "valueRange": "I21:BP21",
       "classification": "AMBIGUOUS"
     }
   ],
   "unresolved": [
     "OTHER adalah konteks CBM provisional, bukan approval IR_THERMOGRAPHY atau MCSA.",
     "Unit oC hanya eksplisit pada BASELINE; tidak diasumsikan berlaku untuk pembacaan temperatur. Unit temperatur tetap kosong hingga diklarifikasi.",
     "IR Window tidak membuktikan kamera/thermogram/emissivity/reflected temperature. Label fase koneksi tanpa unit terverifikasi tidak diterapkan.",
     "Arus adalah observasi beban; tidak menjadi diagnosis atau otomatis sebanding dengan temperatur. Date/Time parsial dan timezone belum disetujui."
   ]
 },
 {
   "id": "cep-ir-window",
   "context": "CEP_CBM",
   "label": "CEP · konteks IR Window provisional",
   "version": "candidate-0.2.0",
   "sourceRef": "WB-CEP-02",
   "filename": "New Log Sheet_CEP_CBM1.xls",
   "sheetIndex": 2,
   "methodTerm": "OTHER",
   "headerRange": "C4:M18",
   "approval": "PENDING_ENGINEER_VALIDATION",
   "fields": [
     {
       "id": "current",
       "label": "Current (Ampere)",
       "unit": "Ampere",
       "headerCells": [
         "C9"
       ],
       "unitCell": "C9",
       "valueRange": "D9:M9",
       "classification": "DIRECT"
     }
   ],
   "unresolved": [
     "OTHER adalah konteks CBM provisional, bukan approval IR_THERMOGRAPHY atau MCSA.",
     "Unit oC hanya eksplisit pada BASELINE; tidak diasumsikan berlaku untuk pembacaan temperatur. Unit temperatur tetap kosong hingga diklarifikasi.",
     "IR Window tidak membuktikan kamera/thermogram/emissivity/reflected temperature. Label fase koneksi tanpa unit terverifikasi tidak diterapkan.",
     "Arus adalah observasi beban; tidak menjadi diagnosis atau otomatis sebanding dengan temperatur. Date/Time parsial dan timezone belum disetujui."
   ]
 },
];
export function workbookProfile(id:string){return workbookProfiles.find(x=>x.id===id);}
export function workbookRows(id:string,method:Method,nextKey:()=>string):EntryRow[]{
 const profile=workbookProfile(id);
 if(!profile)throw Error('Profil workbook tidak dikenali.');
 // Explicit user method selection is separate from choosing an area/context.
 if(method!==profile.methodTerm)throw Error('Pilih metode secara eksplisit sesuai istilah sumber; konteks area tidak memilih metode.');
 return profile.fields.map(field=>({...emptyRow(nextKey()),quantity:field.sourcePointLabel?'':field.label,unit:field.unit,...(field.sourcePointLabel?{sourceHint:field.sourcePointLabel}:{})}));
}
