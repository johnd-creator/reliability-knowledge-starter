/** Presentation of existing integration DTO fields only; no freshness or health derivation. */
export const integrationComponents: Record<string, { title: string; context: string }> = {
  MAXIMO: { title: "Maximo Collector", context: "Observasi akuisisi Work Order pada Collector lokal; bukan konektivitas Maximo saat ini." },
  PI_COLLECTOR: { title: "PI Collector", context: "Inventaris teknis dan snapshot tersimpan; bukan sinyal kondisi aset yang otomatis disetujui." },
  RELIABILITY_MART: { title: "Reliability Mart", context: "Proyeksi lokal dalam store Maximo Collector; terpisah dari tanggal perubahan rekam sumber." },
  ASSET_AF_MAPPING: { title: "Pemetaan Aset / AF", context: "Kesiapan identitas governed; kesamaan nama tidak membuktikan hubungan aset." },
  PI_CONDITION_PROJECTION: { title: "Proyeksi Bukti Kondisi PI", context: "Cakupan sinyal yang disetujui dan diproyeksikan; bukan penilaian kesehatan peralatan." },
};
export function evidenceCount(value: number | null | undefined): string {
  return typeof value === "number" && Number.isSafeInteger(value) && value >= 0 ? value.toLocaleString("id-ID") : "UNKNOWN";
}
export function evidenceTime(value: string | null | undefined): string | null {
  if (!value || !/(Z|[+-]\d{2}:\d{2})$/.test(value)) return null;
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? null : date.toISOString();
}
export function schemaReadiness(value: boolean | null | undefined): string {
  return value === true ? "Kompatibel untuk pembacaan DTO" : value === false ? "Belum siap untuk pembacaan DTO" : "Belum diketahui (UNKNOWN)";
}
