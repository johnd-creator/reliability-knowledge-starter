# NADI-PH2-UI-FIX-02 — Standalone login & compact development header

18 Oktober 2026 · **PASS — local implementation/browser acceptance**.
Product Owner visual acceptance **PENDING**. Tidak ada merge atau deployment.

## Baseline dan reconciliation

Preview tetap **https://localhost:3000**, worktree `.nadi-dev/pdm-ui-fix-01`.
Baseline/final serving HEAD `7daab3a62866f19b30fb45462a94bafff8795dc5`, detached,
dengan dirty state yang akurat. [Bundle01](NADI-PH2-UI-BUNDLE-01.md) dipertahankan;
prepared parent commit `61697806356918655ab2901d5e2ff2cc7a5bd902` tidak ditimpa.
Snapshot hash seluruh52 file perubahan sebelumnya disimpan privat sebelum edit.
Commit FIX02 disiapkan pada ref terpisah `codex/nadi-ph2-ui-fix-02` di atas parent
tersebut, melalui index sementara tanpa checkout atau perubahan index/HEAD preview.
SHA commit diberikan pada handoff, bukan disamakan dengan serving SHA. Tidak push/PR.

Root cause: layout `/login` sebenarnya sudah mandiri, tetapi `QaProductBoundary`
memanggil `LocalLogin` secara inline saat401. Callback itu hanya reload register;
login biasa selalu menuju `/engineering/local`. Selain itu DevelopmentStatus memakai
banyak baris metadata selalu terbuka. Task ini memperbaiki presentasi/pemilihan tujuan,
bukan authentication engine atau status API.

## Before / after

- Banner besar → bar **46px desktop1440** ketika sehat; identitas DEV/branch/SHA
  ringkas/dirty/service summary. Detail native disclosure mempertahankan full SHA
  frontend/startup/backend, compatibility/approval, DB identity, kedua API dan launcher.
  Escape menutup panel dan mengembalikan fokus. Mobile boleh membungkus.
- STALE, mismatch, UNKNOWN, backend unavailable dan DB identity yang belum terverifikasi
  tetap terlihat **di luar** panel tertutup. Dirty Mode A bukan diam-diam dianggap clean.
- PdM/Case/Recommendation/Advisory/Inbox → state masuk diperlukan dengan tautan `/login`,
  tanpa field username/password inline. Notice QA sintetis tetap terlihat secara ringkas.
- Login memakai logo/layout existing, tanpa sidebar/topbar/banner. Sesudah backend
  login/session berhasil, tujuan internal tervalidasi dipakai melalui router.replace.
- `login-navigation.ts` memakai allowlist route QA dan query record/resource terbatas;
  menolak external/protocol-relative URL, backslash/control, path ambigu, duplicate
  query dan query tidak dikenal. Fallback `/engineering/local`, bukan URL dari pengguna.
  Login tidak menyatakan user berhak atas record; server tetap memeriksa role/asset.
- Trusted401 setelah sesi pernah terverifikasi atau IDENTITY_REVOKED → expired/revoked;
  first401 tanpa bukti sesi terdahulu → signed-out. Data lama/draf scoped tetap dibersihkan.
  403/404 tetap denied;503/error berbeda dari schema blocked, disabled, loading dan ready.
- Workspace diagnostik memakai login mandiri juga. Existing proof-adapter diagnostic
  mode, revocation, identity epoch dan command guards tidak dibuat ulang/dilemahkan.

## Batas keamanan dan preservasi

Tidak ada perubahan backend, schema/migration, status endpoint calculation, proxy,
HTTP DTO/enum, cookie Secure/HttpOnly, session duration, Origin, CSRF, RBAC, factual KPI,
source credentials, source access, collector, Mart/cursor atau freshness policy.
Global authentication **UNCHANGED**; dashboard faktual masih HTTP200 saat signed out.

API development-status dan engineering proxy serta transport `engineering-http.ts`
dibandingkan byte-identical dengan baseline. PID frontend **21538**, API **21536**,
invocation/worker tetap dan restart count keduanya0. Kedua backend AVAILABLE,
SHA frontend/backend tetap7daab3a; stale=false. Generated next-env.d.ts, seluruh
artefak Bundle01 dan perubahan lama dijaga. CaseWorkspace/PdmCenter hanya mendapat
penambahan expired pada daftar state yang membersihkan draf; CSS/scripts/DEV-LOG
berubah additive. PNG asli, workbook, worktree/backup dan operational runtime tidak disentuh.

Browser hanya login ke identitas QA sintetis existing dan revoke/logout **session test
sendiri** melalui endpoint/CSRF existing. Tidak ada reset session lama, account edit,
Case/Inspection/Recommendation mutation, database SQL/DDL atau session cleanup.

## Validasi aktual

| Check | Hasil |
|---|---|
| TypeScript `tsc --noEmit --incremental false` | PASS |
| ESLint components/app dan helper baru | PASS, 0 error; warning existing effect dependency di EngineeringWorkspace |
| Existing frontend groups | engineering37, phase2 25, workflow38, http-qa10, bounded-http8, bounded-proxy9, local-auth16, ux43, eng-product8, pdm-input16, workbook48, login-design10, localization10, phase2-ui8 PASS |
| New `phase2-login-header-check.mjs` | 9 groups PASS: redirects, warnings/disclosure, all QA states, no inline credentials |
| Product safety / development provenance | PASS; endpoint guards dan canonical pins dipertahankan |
| Production build | PASS pada salinan sementara, locked dependencies/Node22; preview cache/type file tidak ditimpa |
| Authentication hermetic regression | 62 run: **43 PASS, 19 SKIP**; test_local_authentication/application_identity/identity_adapter |
| Browser actual HTTPS | PASS: 390/768/1440, light/dark, no page overflow, keyboard details, login return, real test-session revocation/logout, foreign Case denial, anonymous401, factual dashboard signed out |
| Critical mismatch browser check | PASS dengan **fault injection browser terisolasi**, bukan mismatch runtime aktual |
| Git diff/link checks | PASS |
| GitHub CI pada prepared commit | **NOT RUN** — tidak push atau membuka PR |

TLS tetap diverifikasi menggunakan Chrome dan profil/NSS terisolasi yang telah
terpercaya. CA SHA256 `125ee0237942a71f8c9d470371d745b3d956ef3b507500e5030ffb43e02d1a30`.
Tidak ada ignore HTTPS flag, warning exception, downgrade, server certificate change,
atau global trust edit. [Screenshot/evidence](evidence/nadi-ph2-ui-fix-02/README.md).

## Self-review dan koreksi

- Lint menolak keyboard handler pada elemen details non-interaktif. Escape ditangani
  listener scoped dengan cleanup dan return focus; lint final PASS.
- Browser test sempat membaca URL sebelum navigasi asynchronous selesai. Penantian URL
  diperbaiki; acceptance dilanjutkan, session test sebelumnya tidak dipaksakan pulih.
- Localization pin menandai perubahan useQaRecords. Hanya checksum hook presentation
  yang direview diperbarui dengan catatan scope; canonical DTO/API/proxy pins lainnya
  tetap. Browser trusted401/revocation dan test auth existing lulus; guard tidak dihapus.
- Live status sehat, tidak membuat mismatch pada source/runtime untuk screenshot.
  Skenario mismatch dinyatakan tegas fixture-only pada nama file dan hasil browser.

## Remaining gates

PO visual review diperlukan untuk kepadatan header, teks state QA, layout login dan
return-destination experience. Engineered method/point/threshold, Q01–Q10, engineer UAT,
operational activation serta global auth tetap **PENDING / tidak diaktifkan**.
Tidak ada dependency upgrade. PR100 **tidak merged**. Lanjut hanya setelah handoff:
Senior Review → Product Owner Visual Review.
