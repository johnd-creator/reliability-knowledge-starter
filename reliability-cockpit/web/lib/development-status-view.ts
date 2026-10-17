// Presentation of existing status DTO only; never approves a pair or alters server checks.
export type DevelopmentStatusValue={branch:string;sha:string;launched_sha?:string;dirty:boolean|null;backend:string;database:string;database_identity:string;factual_backend:string;engineering:boolean;stale:boolean;backend_sha:string;compatibility:string;compatibility_approval:string|null;launcher_sha256:string|null;launcher_source_sha:string|null};
export function developmentWarnings(status:DevelopmentStatusValue|null):string[]{
 if(!status)return ['Status development belum dapat diverifikasi (UNKNOWN). Periksa koneksi layanan.'];
 const warnings:string[]=[];
 if(status.stale)warnings.push('STALE / mismatch sumber. Hentikan perubahan runtime dan rekonsiliasi source sebelum melanjutkan.');
 if(!/^[a-f0-9]{40}$/.test(status.sha)||!/^[a-f0-9]{40}$/.test(status.backend_sha))warnings.push('Identitas SHA belum diketahui (UNKNOWN).');
 if(!['SAME_SOURCE','VERIFIED_SOURCE_EQUIVALENT'].includes(status.compatibility)||(status.sha!==status.backend_sha&&status.compatibility!=='VERIFIED_SOURCE_EQUIVALENT'))warnings.push('Kompatibilitas frontend/backend belum terverifikasi.');
 if(typeof status.dirty!=='boolean')warnings.push('Status perubahan source belum diketahui (UNKNOWN).');
 if(status.factual_backend!=='AVAILABLE')warnings.push('Backend faktual tidak tersedia.');
 if(status.backend!=='AVAILABLE')warnings.push('Backend Engineering QA tidak tersedia.');
 if(!status.database_identity||status.database_identity==='UNKNOWN'||status.database!=='DISPOSABLE_TEST')warnings.push('Identitas database QA belum terverifikasi.');
 return warnings;
}
