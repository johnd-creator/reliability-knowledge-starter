import type {CaptureClock,Precision} from './pdm-capture';

// Presentation only: use calendar fields as reported, never the browser timezone.
// A source DATE must not pass through Date.parse (which would invent midnight).
const months=['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
const unknown='Belum diketahui';
function calendar(value:string):string|null {
 const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(value);if(!m)return null;
 const [year,month,day]=m.slice(1).map(Number),leap=year%4===0&&(year%100!==0||year%400===0);
 const days=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
 return year>0&&month>=1&&month<=12&&day>=1&&day<=days[month-1]?`${day} ${months[month-1]} ${m[1]}`:null;
}
function clock(value:string):string|null {
 return /^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d{1,6})?)?$/.test(value)?value.split('.').map((part,i)=>i===0?part.replace(/:/g,'.'):part).join(','):null;
}
function zone(value:string):string|null {
 if(/^[Zz]$/.test(value))return 'UTC';
 if(!/^[+-](?:[01]\d|2[0-3]):[0-5]\d$/.test(value))return null;
 // RFC3339 -00:00 means the local offset is unknown, not UTC.
 return ({'+07:00':'WIB','+08:00':'WITA','+09:00':'WIT','+00:00':'UTC','-00:00':'zona waktu belum diketahui'} as Record<string,string>)[value]??`UTC${value}`;
}
export function pdmDate(value:unknown,precision?:Precision):string {
 if(precision==='RAW')return 'Teks / serial belum ditafsirkan';
 if(precision==='UNKNOWN'||value===null||value===undefined||value===''||value==='UNKNOWN')return unknown;
 if(typeof value!=='string')return 'Format waktu tidak valid';
 if(precision==='DATE'||!precision&&/^\d{4}-\d{2}-\d{2}$/.test(value))return calendar(value)??'Format tanggal tidak valid';
 if(precision==='TIME'){const time=clock(value);return time?`${time} · tanggal dan zona waktu belum diketahui`:'Format jam tidak valid';}
 const m=/^(\d{4}-\d{2}-\d{2})[Tt](\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?)([Zz]|[+-]\d{2}:\d{2})?$/.exec(value);
 if(!m||!calendar(m[1])||!clock(m[2]))return 'Format waktu tidak valid';
 if(precision==='LOCAL_DATETIME'&&m[3]||precision==='DATETIME'&&!m[3])return 'Format waktu tidak sesuai presisi';
 const label=m[3]?zone(m[3]):'zona waktu belum diketahui';
 return label?`${calendar(m[1])}, ${clock(m[2])} ${label}`:'Format zona waktu tidak valid';
}
export function pdmClockDate(c:CaptureClock):string {
 return pdmDate(c.value,c.precision);
}

// Known canonical/application instants share one explicit reading zone. Source
// clocks use pdmDate instead, retaining their reported calendar/offset claims.
export function formatRecordedInstant(value:unknown):string {
 const fallback=pdmDate(value);
 if(typeof value!=='string'||fallback.includes('tidak valid')||fallback.includes('belum diketahui')||!/(?:[Zz]|[+-]\d{2}:\d{2})$/.test(value))return fallback;
 const instant=new Date(value);if(!Number.isFinite(instant.getTime()))return 'Format waktu tidak valid';
 const seconds=/T\d{2}:\d{2}:\d{2}/i.test(value),fraction=/\.([0-9]+)(?:[Zz]|[+-]\d{2}:\d{2})$/.exec(value)?.[1];
 // Proleptic WIB is fixed UTC+07:00; Etc/GMT uses the reversed IANA sign.
 const parts=new Intl.DateTimeFormat('id-ID',{timeZone:'Etc/GMT-7',year:'numeric',month:'long',day:'numeric',hour:'2-digit',minute:'2-digit',...(seconds?{second:'2-digit' as const}:{}),hourCycle:'h23'}).formatToParts(instant);
 const part=(name:Intl.DateTimeFormatPartTypes)=>parts.find(p=>p.type===name)?.value??'';
 return `${part('day')} ${part('month')} ${part('year')}, ${part('hour')}.${part('minute')}${seconds?'.'+part('second'):''}${fraction?','+fraction:''} WIB`;
}
