import {pdmDate,pdmClockDate,formatRecordedInstant} from '../lib/pdm-date';
import {clockLabels,type CaptureClock,type Precision} from '../lib/pdm-capture';
export default function PdmDate({value,precision,raw=false}:{value:unknown;precision?:Precision;raw?:boolean}){
 const text=precision?pdmDate(value,precision):formatRecordedInstant(value);
 return <><span className="pdm-date">{text}</span>{raw&&<details className="record-time-details"><summary>Nilai waktu asli</summary><code>{typeof value==='string'?value:value===null?'null':value===undefined?'Tidak tersedia':String(value)}</code></details>}</>;
}
export function PdmSourceDates({clocks}:{clocks:CaptureClock[]}){
 return <>{clocks.length?clocks.map((c,i)=><div key={i}><small>{clockLabels[c.role]} (sumber)</small><br/><span className="pdm-date">{pdmClockDate(c)}</span></div>):<span>Tanggal sumber belum diketahui</span>}</>;
}
