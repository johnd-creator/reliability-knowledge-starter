# NADI-PH2-UI-BUNDLE-01 — Engineering Workspace & PdM

17 Oktober 2026 · Implementasi frontend dan local development acceptance **PASS**.
Product Owner visual acceptance dan engineer UAT **PENDING**.

## Baseline dan delivery

- Preview: **https://localhost:3000**, Mode A, worktree `.nadi-dev/pdm-ui-fix-01`.
- Baseline dan final **active HEAD**: `7daab3a62866f19b30fb45462a94bafff8795dc5`.
- HEAD sengaja tetap detached. Perubahan presentasi tampil sebagai **UNCOMMITTED**;
  banner tetap melaporkan dirty state sebenarnya. Tidak ada source handover.
- Commit review disiapkan pada ref terpisah `codex/nadi-ph2-ui-bundle-01` melalui
  index sementara, tanpa mengubah HEAD/index preview. SHA commit dicatat pada
  handoff akhir; commit tidak mengubah launched/frontend/backend SHA.
- Tidak push, membuka PR, merge PR95–100, memasang controller, restart, atau deploy.
  Integrasi terhadap main terbaru dan CI GitHub memerlukan review terpisah.

Preflight memverifikasi exact HEAD, hanya dirty generated `next-env.d.ts` yang
sudah ada, ownership preview/API, dan tidak ada chat Codex lokal lain yang aktif.
Hash baseline disimpan privat sebelum edit. Indeks graph Agustus tidak mencakup
komponen terbaru; seluruh komponen/kontrak material dibaca langsung.

## Implementasi dan before/after

| Area | Sebelumnya | Sekarang |
|---|---|---|
| Case register | Identitas, status dan revisi | Prioritas manusia dan referensi engineer; filter server/pagination tetap; PdM mudah ditemukan |
| Case form | Satu fieldset panjang | Tiga bagian: identitas/tanggung jawab, masalah/konteks, investigasi manusia; label Indonesia, validasi Unicode/list, save/cancel/busy dan perlindungan isian |
| Draf dan konflik | Reload register dapat membuang isian; save memakai revisi detail terbaru | Recovery hanya di memori dengan subject/asset/role yang sama, intent idempotency dipertahankan; edit memakai revisi awal; pembacaan terbaru tidak merebase draf |
| Case detail | Paragraf metadata/review/history | Identitas, konteks, catatan manusia, evidence beku, waktu sumber, versi, reviewer/alasan, tabel audit dan tautan inspeksi yang exact |
| Independent review | Affordance hanya berdasarkan role reviewer | Affordance juga mengecualikan author/assignee/contributor; server tetap satu-satunya otoritas |
| PdM register | Filter form dan ID panjang | Navigasi metode kandidat, filter berlabel eksplisit, kolom dengan lebar aman dan disclosure titik; updated time dibedakan dari waktu ukur/pengajuan |
| Input PdM | Satu form panjang | Tiga tahap berlabel; workbook profile, multi-point grid, original types/units/time, metadata evidence dan workflow existing tetap |
| Riwayat | Pemilih sampel dapat melebar di mobile | Kontrol dibatasi panel; tabel dapat digeser lokal; sampel asli tanpa interpolasi, ketidakbandingan tetap eksplisit |

Komponen existing tetap digunakan: `PageHeader`, `SectionCard`, `Button`,
`InputControl`, `TableFrame`, `StatusBadge`, `Pagination`, `Feedback`,
`QaProductBoundary`, `useQaRecords`, `useQaCommand`, dan workflow inspeksi.
Tambahan: `CaseDraftContext` dan helper presentasi `case-form.ts`.
Tidak ada dependency/desain framework baru.

## Kontrak dan preservasi

Tidak ada perubahan URL, enum, DTO kanonis (`case-records.ts` tetap byte-identical),
backend, API proxy, cookie, session policy, CSRF, Origin, RBAC, schema atau migrasi.
List/count/filter/pagination tetap hasil server berotorisasi. Human priority bukan
risiko equipment. UNKNOWN, NOT ASSESSED, RETURNED, REJECTED dan APPROVED tetap
berbeda. APPROVED hanya review rekam NADI, bukan izin pekerjaan/Maximo WO.

Satu Case dan satu Inspection **baru, sintetis dan bertanda task** dipakai untuk
acceptance persisten. Case mengalami deliberate stale-CAS, rekonsiliasi, evidence
ASSET dan review akun independen. Inspection menyimpan original `0`, `null`,
`mm/s`, dan timestamp dengan zona waktu; tetap ada setelah reload. Keduanya
**dipertahankan**, tidak dihapus/reset. Tiga Case dan tiga Inspection terdahulu
kembali dibaca dan hash DTO dibandingkan selama fase akhir E2E; tidak berubah.
Scope bukti ini bukan audit menyeluruh seluruh database/session historis.

Frontend parent **21538**, worker **21559**, API parent **21536** dan invocation
IDs tetap. Restart count keduanya **0**. Fast Refresh tercatat `rebuilding` / `done
in 291ms`, dokumen browser yang sama mempertahankan nonce; tidak ada reload atau
restart untuk perubahan UI. Node22.23.1, heap4GiB dan MemoryMax6GiB tetap.
Generated file, lima PNG, workbook asli, backup dan worktree lain dipertahankan.
Collector, Mart, source cursor, freshness governance, dan operasional tidak disentuh.
Ini bukan sustained-runtime qualification.

## Validasi yang benar-benar dijalankan

Perintah dari `reliability-cockpit/web` menggunakan `/usr/bin/node-22`:

| Pemeriksaan | Hasil |
|---|---|
| `node_modules/typescript/bin/tsc --noEmit --incremental false` | PASS |
| ESLint melalui daftar pada `npm run lint` | PASS, 0 error; warning lama dependency effect `EngineeringWorkspace.tsx` dan target status-route `.ts` yang tidak dicakup konfigurasi lint existing |
| engineering / phase2 / workflow assertions | 37 / 25 / 38 PASS |
| http-qa / bounded-http / bounded-proxy / local-auth | 10 / 8 / 9 / 16 PASS |
| ux / eng-product | 43 / 8 PASS |
| pdm-input / pdm-workbook | 16 / 48 PASS |
| login-design / localization / phase2-ui | 10 / 10 / 8 PASS |
| development-provenance / product-safety | PASS; product scan 64 UI files |
| Next15.5.9 production build | PASS di salinan sementara dengan dependencies terkunci; cache/type file preview tidak ditimpa |
| `git diff --check` | PASS |
| Backend hermetik | 154 dijalankan: **99 PASS, 55 SKIP**, SQLite/sumber sintetis; bukan PostgreSQL persisten integration acceptance |
| GitHub CI pada prepared commit | **NOT RUN** — tidak ada push/PR pada task ini |

Backend command: `PYTHONPATH=.:tests <existing-python> -m unittest
 test_engineering test_manual_inspection test_inspection_workflow test_pdm_input
 test_pdm_workbook_contract`. Tidak ada destructive fixture terhadap QA persisten.

Browser Chrome154 memakai profil/HOME/NSS terisolasi dengan CA existing terverifikasi
SHA256 `125ee0237942a71f8c9d470371d745b3d956ef3b507500e5030ffb43e02d1a30`.
TLS verification aktif; tidak ada ignore flag, HTTP downgrade atau global trust edit.
E2E mencakup create/edit/validation/cancel/reload, stale save, history, server self-review
403, review independen, persistence/unit/time, dan unsupported trend. Pemeriksaan
lanjutan membuktikan filter DRAFT/MCSA, invalid time, anonymous401 dan invalid-CSRF403.

Screenshot aktual dan overflow/focus checks pada **390/768/1440**, light/dark,
serta response200 untuk `/`, `/assets`, `/asset-health`, `/maintenance`,
`/work-orders`, `/data-quality`, `/recommendations`, `/engineering/advisories`,
`/engineering/inbox`, `/login`. Ini bounded regression, bukan klaim semua kombinasi
workflow atau sertifikasi accessibility. [Indeks screenshot/evidence](evidence/nadi-ph2-ui-bundle-01/README.md).

## Self-review, kegagalan dan koreksi

- **Medium:** CAS memakai row terbaru saat form lama masih terbuka. Basis edit
  dipin; tombol Edit nonaktif selama edit. Live concurrent revision test PASS.
- **Medium:** draf hilang saat focus reload. Recovery in-memory identity-scoped,
  wipe pada denied/signed-out/role/asset change dan intent tetap. Live test PASS.
- **Medium:** history selector overflow390. Lebar kontrol/SVG dibatasi; tiga
  viewport diuji ulang dan screenshot diganti dengan hasil akhir PASS.
- **Low:** register titik panjang/kolom sempit. Fixed column budget, local scroll
  dan disclosure titik. Visual review desktop/mobile PASS.
- **Low:** label select menyertakan teks option. Accessible name eksplisit ditambah;
  browser filter tests PASS.
- Preflight NSS awal memerlukan inisialisasi slot lokal; fingerprint/trust diverifikasi
  sebelum browser berhasil. Source/server certificate tidak diganti.
- Iterasi awal TypeScript menemukan penutup JSX berlebih; diperbaiki. Validasi baru
  menemukan Unicode whitespace; disamakan dengan batas kanonis. Localization guard
  menolak edit helper DTO; DTO dikembalikan byte-identical dan helper baru dipisahkan.
- Compiler-child awal ditolak sandbox (`EPERM`); assertions hermetik dijalankan
  dengan host permission. Dua selector browser yang salah diperbaiki; acceptance
  dilanjutkan pada rekam task yang sama, tanpa membuat ulang atau membuang evidence.

## Gaps dan persetujuan yang tetap pending

- **Q01–Q10 PENDING_ENGINEER_VALIDATION**; workbook profile/classification hanya
  kandidat, bukan field/method/threshold approval. M01–M07 dan Phase1 tetap.
- Submitted timestamp/version terpisah tidak ada pada ringkasan DTO tertentu;
  tampil unavailable, bukan memakai updated time sebagai waktu pengajuan.
- Nama engineer tidak di-resolve/diterka; hanya referensi yang diizinkan DTO.
- WO references hanya melalui evidence yang tersedia; tidak ada reverse lookup
  rekomendasi/WO baru yang dibuat atau diasumsikan. Tautan register existing tetap.
- Attachment custody/upload/download, cross-inspection comparability, diagnosis,
  severity/health/risk scoring, global authentication dan operasional tidak diaktifkan.
- Backend/API pagination history dan inspection-history detail tetap memakai
  workflow existing; tidak ada alternatif review engine.

Product Owner checklist: review keterbacaan register, bagian form, disclosure titik,
scoping QA, wording review≠izin pekerjaan, urutan input/riwayat dan mobile/dark mode.
**Next: Senior Review → Product Owner UI Review → targeted corrections.**
