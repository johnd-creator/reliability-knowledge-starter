# Platform roadmap — mulai di sini

**Power Plant Data Platform** memiliki shared data foundation, **NADI sebagai
main quest**, dan **NK sebagai child roadmap**. Audit PLATFORM-ROADMAP-001
menggunakan `origin/main` pada `ef07a263b122d30e7dbec451e6094f9016b603c3`,
7 Oktober 2026. Branch implementation yang belum merged tidak dihitung sebagai
kemampuan `main`.

## Baca dalam urutan ini

| Dokumen | Pertanyaan yang dijawab |
|---|---|
| [Platform Vision](PLATFORM-VISION.md) | Apa platform ini, siapa pemilik data, siapa konsumennya? |
| [NADI Roadmap](NADI-ROADMAP.md) | Phase 0–5, apa yang selesai, dan technical PR berikutnya? |
| [Engineering Roadmap M0–M8](reliability-cockpit-platform/05-roadmap-implementasi.md) | Bagaimana product roadmap diimplementasikan? |
| [NK Roadmap](NK-ROADMAP.md) | Mengapa NK ada, apa yang bekerja di branch, apa yang belum siap? |
| [Repository Status](REPOSITORY-STATUS.md) | Baseline, PR, branch debt, dokumen stale, governance? |

**Posisi NADI:** Phase 0 COMPLETE untuk release faktual; Phase 1 CURRENT /
PARTIAL untuk ekspansi evidence. **NADI-PI-001:** IMPLEMENTED / MERGE-CANDIDATE di PR terpisah, belum merged.
**Next:** rekonsiliasi runtime/Mart bila diperlukan → NADI-IDN-002 pilot mapping.
PI evidence projection dan acceptance masih pending.
Lihat [evidence implementasi offline](../pi-collector/docs/nadi-pi-001-implementation.md).
NK tidak menggantikan prioritas NADI dan tidak memperluas domain Reliability.

## Aturan status

- `COMPLETE`: scope yang disebutkan mempunyai bukti merged/accepted; bukan
  klaim bahwa semua exit criteria platform atau deployment produksi terpenuhi.
- `PARTIAL`: artefak ada, tetapi dependency/acceptance tertentu belum terbukti.
- `UNMERGED`: implementasi/bukti hanya ada pada branch di luar baseline `main`.
- `PLANNED`: product intent, belum dinyatakan selesai.
- `NEEDS_REVIEW`: bukti tidak cukup atau ada konflik yang harus diselesaikan.
- `HISTORICAL` / `SUPERSEDED`: simpan konteks, tetapi jangan pakai sebagai status aktif.

Status implementasi, verifikasi sumber, business semantics, dan kesiapan runtime
adalah empat hal berbeda. Discovery yang selesai dapat tetap menghasilkan
`UNKNOWN`; unit test passing tidak membuktikan live mapping atau pilot.

## Hierarki dan pemeliharaan

Dokumen di atas menjadi entry point otoritatif untuk vision/status/sequence.
[Proposal 20 Agustus](reliability-cockpit-platform/README.md) tetap menyediakan
backlog/detail desain. Bagian status M0–M8 terbaru menggantikan tabel snapshot
lamanya; backlog tidak dihapus. Scoped domain/discovery docs mengatur semantik
lebih rinci dan tidak ditimpa oleh roadmap aspiratif.

Setiap technical PR menyebut task ID, evidence/acceptance dan roadmap yang
terpengaruh. Saat status berubah, perbarui dokumen pemiliknya serta tanggal/SHA
basis audit, bukan menyalin tabel status ke banyak dokumen.
