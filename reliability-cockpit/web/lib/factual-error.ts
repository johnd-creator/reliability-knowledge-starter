import {ApiError} from './api';

/** Presentation only: no backend body, account identity, or policy change. */
export function factualErrorMessage(error:unknown):string {
  if(error instanceof ApiError&&error.status===403)return 'Akses data faktual memerlukan capability atau scope yang disetujui. Akun ini belum memiliki akses ke ringkasan portfolio.';
  if(error instanceof ApiError&&error.status===401)return 'Sesi berakhir. Silakan masuk kembali.';
  return 'Layanan data faktual belum tersedia. Coba lagi; kegagalan ini tidak menyatakan data kosong.';
}
