import messages from './id-messages.json';

/** Presentation only. Never use localized labels in URLs, API commands or stored records. */
export function idText(key: keyof typeof messages): string {
  return messages[key];
}

const statuses: Record<string, string> = {
  CURRENT: 'Mutakhir pada dimensi bukti', NOT_CONFIGURED: 'Belum dikonfigurasi', GOOD: 'Kualitas data baik', BAD: 'Kualitas data buruk', AMBIGUOUS: 'Ambigu',
  UNKNOWN: 'Belum diketahui', NOT_ASSESSED: 'Belum dinilai', 'NOT ASSESSED': 'Belum dinilai',
  UNAVAILABLE: 'Tidak tersedia', 'NOT AVAILABLE': 'Tidak tersedia',
  DRAFT: 'Draf', IN_REVIEW: 'Dalam review', APPROVED: 'Rekam disetujui', REJECTED: 'Rekam ditolak',
  RETURNED: 'Dikembalikan', PENDING: 'Menunggu', BLOCKED: 'Terblokir', DEFERRED: 'Ditunda',
  VERIFIED: 'Terverifikasi', NOT_VERIFIED: 'Belum terverifikasi', 'NOT VERIFIED': 'Belum terverifikasi',
  'NOT REVIEWED': 'Belum direview', 'NOT RECORDED': 'Belum tercatat', 'NOT ASSIGNED': 'Belum ditugaskan',
  'NOT LINKED': 'Belum terkait', COMPLETED: 'Selesai secara lokal', CANCELLED: 'Dibatalkan',
  ACKNOWLEDGED: 'Penerimaan dikonfirmasi', 'NOT ACKNOWLEDGED': 'Penerimaan belum dikonfirmasi',
  ACK: 'Konfirmasi penerimaan', IN_APP_QA_AVAILABLE: 'Tersedia di kotak masuk QA',
  WITHDRAWN: 'Ditarik', STALE: 'Usang', NOT_VIEWED: 'Belum dilihat', VIEWED: 'Dilihat',
  NOT_STARTED: 'Belum dimulai', IN_PROGRESS: 'Dalam proses', AVAILABLE: 'Tersedia',
  CLEAN: 'Bersih', UNCOMMITTED: 'Belum di-commit', ENABLED: 'Aktif',
  OPERATIONS_QA: 'Operasi QA', MAINTENANCE_QA: 'Pemeliharaan QA', ENGINEERING_QA: 'Engineering QA',
  LOW: 'Rendah', NORMAL: 'Normal', HIGH: 'Tinggi', AUTHOR: 'Penulis', REVIEWER: 'Reviewer independen',
  ADMIN: 'Administrator', INVESTIGATION: 'Investigasi', MAINTENANCE: 'Pemeliharaan', CONDITION: 'Kondisi',
  SUBMITTED: 'Diajukan', UNDER_REVIEW: 'Sedang direview', PROPOSED: 'Diusulkan', PLANNED: 'Direncanakan',
  VIBRATION: 'Vibrasi', IR_THERMOGRAPHY: 'IR Thermography', TRIBOLOGY: 'Tribologi', OTHER: 'Lainnya',
  OK: 'Baik pada dimensi data', FRESH: 'Mutakhir', PARTIAL: 'Sebagian', DEGRADED: 'Terbatas', UNMAPPED: 'Belum dipetakan', UNRESOLVED: 'Belum terselesaikan', PUBLISH: 'Publikasi QA', UNPUBLISHED: 'Belum dipublikasikan', FROZEN_SNAPSHOT: 'Snapshot beku', LIVE_REFERENCE: 'Referensi aktif', NOT_RECORDED: 'Belum tercatat', REVOKED: 'Dicabut', EXPIRED: 'Kedaluwarsa', ALL: 'Semua', NUMERIC: 'Numerik', TEXT: 'Teks', BOOLEAN: 'Boolean', NOTE: 'Catatan', SUBMIT: 'Ajukan review', BEGIN_REVIEW: 'Mulai review', CREATE: 'Buat rekam', UPDATE: 'Perbarui rekam', WITHDRAW: 'Tarik rekam', REVISE: 'Revisi rekam', REOPEN: 'Buka kembali', 'NOT LOADED': 'Belum dimuat', DISPOSABLE_TEST: 'Fixture QA terisolasi',
};

/** Keep the exact backend code inspectable; unknown/vendor values are returned verbatim. */
export function statusLabel(value: string | null | undefined): string {
  if (value == null || value === '') return '—';
  const label = statuses[value];
  return label ? `${label} (${value})` : value;
}

/** Known application field names, never a translation of user-entered evidence. */
export const fieldLabels: Record<string, string> = {
  observed_symptoms: 'Gejala teramati', observations: 'Observasi', hypotheses: 'Hipotesis',
  evidence_gaps: 'Kesenjangan bukti', proposed_next_checks: 'Usulan pemeriksaan berikutnya',
  questions: 'Pertanyaan', proposed_actions: 'Usulan tindakan', alternatives: 'Alternatif',
  limitations: 'Batasan', operating_context: 'Konteks operasi',
  open_questions: 'Pertanyaan terbuka',
};

/** Localize known UI errors without changing their codes or exposing server details. */
export function errorLabel(error: unknown): string {
  const raw = error instanceof Error ? error.message : String(error ?? '');
  if (Object.hasOwn(messages, raw)) return messages[raw as keyof typeof messages];
  if (Object.values(messages).includes(raw)) return raw;
  const prefix = raw.match(/^([A-Z][A-Z0-9_]+)(?::|$)/)?.[1];
  const errors: Record<string, string> = {
    REVISION_CONFLICT: 'Revisi telah berubah. Isian Anda dipertahankan; baca revisi terbaru, bandingkan, lalu coba lagi secara sengaja.',
    AUTHENTICATION_REQUIRED: 'Silakan masuk dengan akun QA berizin.',
    SESSION_EXPIRED: 'Sesi berakhir. Silakan masuk kembali.',
    ACCESS_DENIED: 'Akses ditolak untuk identitas atau lingkup aset Anda.',
    INDEPENDENT_REVIEWER_REQUIRED: 'Review memerlukan reviewer independen.',
    CSRF_DENIED: 'Permintaan tidak lolos pemeriksaan keamanan sesi. Muat ulang sesi.',
    INVALID_TRANSITION: 'Tindakan tidak tersedia pada status rekam saat ini.',
    INVALID_INPUT: 'Isian tidak valid. Periksa kolom yang diperlukan.',
    REVIEWED_CASE_CHANGED: 'Kasus yang direview telah berubah. Periksa versi terkait.',
    EVIDENCE_VERSION_CHANGED: 'Versi bukti telah berubah. Periksa bukti terkait.',
    CROSS_ASSET_REFERENCE: 'Referensi bukti tidak memiliki identitas aset yang sama.',
  };
  if (prefix) return `${errors[prefix] ?? 'Tindakan ditolak atau data tidak tersedia. Periksa akses, isian, dan versi rekam.'} (${prefix})`;
  // Do not render arbitrary transport/server exception text. User evidence is never passed here.
  return 'Tidak dapat memproses permintaan. Periksa isian atau coba beberapa saat lagi.';
}
