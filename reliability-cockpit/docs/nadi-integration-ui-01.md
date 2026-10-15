# NADI-INTEGRATION-UI-01 — Pusat Integrasi Sistem

15 Oktober 2026 · **Implementasi development siap direview; belum merge, belum live, belum operational accepted.**

- Baseline main: `1ac1d5e709724c2b5433beba8f0305c19b5d3a0e` (terverifikasi sebelum implementasi dan delivery).
- Branch: `codex/nadi-integration-ui-01`.
- Exact implementation/source SHA: `f85e7fc3eecce0ca188234fd59ec738ec8544fd9`.
- [PR #87 — OPEN/DRAFT](https://github.com/johnd-creator/reliability-knowledge-starter/pull/87). Final evidence/documentation HEAD dan hasil CI exact-head dicatat pada PR/checks serta handoff; SHA source di atas tidak diklaim sebagai SHA commit dokumentasi yang memuat laporan ini.
- [Manifest source dan gambar](evidence/nadi-integration-ui-01/manifest.json) mengikat bukti ke source implementation tersebut.

## Kontrak existing yang digunakan

| Kontrak | Jalur browser / metode | Penggunaan dan batas |
|---|---|---|
| [IntegrationStatus](../src/domain/integration_status.py) / [schema](../../reliability-data-contracts/schemas/integration-status.schema.json) | GET `/api/cockpit/v1/reliability/integration-status` | Komponen, coverage, schema-readiness dan `observed_at`; bukan health score |
| [DataTrustView](../src/api/reliability.py) / [client existing](../web/lib/api.ts) | GET `/api/cockpit/v1/reliability/data-trust` | Populasi Registry vs teknis, domain, relasi dan provenance terpilih; tidak menyediakan timestamp observasi mandiri |

Tidak mengubah API, enum, DTO, schema, service atau repository backend. Kontrak
[status existing](nadi-integration-status-001.md) dan
[semantik Mart](reliability-mart-query-api.md) tetap authoritative.
IntegrationStatusService membaca fixed **local Collector GET** dan SELECT Mart;
[adapter existing](../src/adapters/integration_observations.py) tidak mengakses
sistem produksi. Halaman hanya memakai dua method read client tersebut. Tidak ada
polling, source refresh, arbitrary proxy, start/stop, scheduling, credential,
export atau mutation control. “Baca ulang bukti lokal” mengulang GET yang sama
secara sengaja, tidak memicu koleksi.

## Arsitektur dan akses

`/system-integration` berada pada route group `(workspace)`, memakai AppShell
existing. Link “Ringkasan Integrasi” ditambahkan pada grup ID `integration`;
seluruh child link dan active-route boundary existing dipertahankan. Tidak
menciptakan URL teknis PI/CEMS yang belum didukung.

[SystemIntegrationCenter](../web/components/SystemIntegrationCenter.tsx) menangani
dua read state secara independen dan membatalkan pembaruan state setelah unmount.
Kegagalan satu DTO tidak menutupi yang lain. Loading/empty/error/401/403 eksplisit;
teks exception server tidak diteruskan ke UI. [IntegrationComponentCards](../web/components/IntegrationComponentCards.tsx)
merender DTO existing tanpa model/status turunan. Formatter
[integration.ts](../web/lib/integration.ts) hanya memformat jumlah/waktu dan label
kesiapan schema. IntegrationStatusPanel/View existing di Data Trust dan Asset
tetap dipertahankan; tidak ada model status pesaing.

**Development-only:** audit source router factual existing menemukan tidak ada
authentication dependency pada endpoint ini. Halaman server hanya memasang
reading workspace pada `NODE_ENV=development`; production menampilkan prasyarat
akses tanpa memasang komponen pembaca. Ini bukan penambahan auth pada API atau
klaim bahwa API menjadi terlindungi. Review autentikasi/otorisasi dan lingkup
deployment diperlukan sebelum aktivasi selain development. Authentication
Engineering, RBAC, CSRF, cookie/session dan kebijakan global tidak disentuh.

## Semantik trust dan freshness

- Availability, collection, source, projection, identity/mapping dan quality
  tetap berlabel independen; state API tidak dihitung ulang memakai jam browser.
- Timestamp UTC eksplisit dan batas usia dari DTO ditampilkan terpisah. Kebijakan
  hilang = UNKNOWN/tidak dikonfigurasi; tidak ada default threshold. DTO tidak
  membuktikan status operator-review/expiry atau persetujuan kebijakan; task ini
  tidak menilai, mereset, memperpanjang atau mengaktifkannya.
- Aktivitas sukses lama bukan konektivitas saat ini; latest source-record date
  bukan freshness pengumpulan. Tidak ada interpretasi equipment sehat dari GOOD,
  AVAILABLE atau CURRENT. Semua badge `raw-neutral`.
- Null/missing count tetap UNKNOWN, nol asli tetap nol. Registry bisnis tidak
  dijumlahkan dengan asset_master teknis atau PI registry. Dua DTO memiliki read
  time terpisah; tidak dipaksakan sebagai satu snapshot atomik.
- Data Trust menyajikan domain record dates dengan date basis, bukan observation
  time yang dikarang. Tidak menyalin seluruh Data Trust Center; detail tetap di
  `/data-quality`.
- Komponen hanya dirender dari respons. CEMS tanpa DTO dicatat belum dapat
  diverifikasi, bukan disconnected/healthy. Diagram pipeline hanya arsitektur,
  bukan bukti semua source/proyeksi aktif. PI teknis bukan otomatis sinyal kondisi
  approved; koleksi CEMS bukan validasi reporting emisi.

## Validasi dan review mandiri

Seluruh pengujian memakai fixture sintetis; **tidak membuka localhost3000, API QA,
PostgreSQL, jaringan kantor atau source produksi**. Harness browser mengintersep
semua request dan membatasi dua GET di `integration.synthetic.invalid`, tanpa
server/listener. Suite existing juga seluruhnya diintersep. Ini validasi actual
React components dengan substitute Next navigation, bukan end-to-end deployment.

| Pemeriksaan | Hasil |
|---|---|
| Komponen/presentation/production gate/navigation | 22/22 PASS |
| Browser integrasi, error/unknown/policy/empty, keyboard/drawer, 4 ukuran × 2 tema | 67/67 PASS |
| Existing browser factual/login/session/Case/recommendation/advisory/inbox | 395/395 PASS |
| Existing PdM input/review/handoff/workbook/keyboard browser | 573/573 PASS |
| Backend integration observations/Mart (temporary SQLite/mocks) | 63/63 PASS |
| Pydantic fixture compatibility/defaults | 3/3 PASS |
| Existing engineering/phase2/workflow/HTTP/bounded/local-auth/product-safety/UX/PdM assertions | PASS |
| TypeScript / ESLint / production build / diff whitespace | PASS; dua lint warning existing |
| Axe WCAG A/AA pada 8 ukuran/tema | Nol violation; incomplete contrast pada shell/tabel clipped dijelaskan di bawah |
| CI backend/frontend final exact-head | Lihat checks pada PR #87; dipisahkan dari hasil lokal |

[Summary terstruktur](evidence/nadi-integration-ui-01/validation-summary.json) dan
[hasil browser/requests/accessibility](evidence/nadi-integration-ui-01/integration-browser.json).
Reproduksi: `npm ci`, `npm run check:integration`, `npm run lint`,
`npx tsc --noEmit`, `COCKPIT_API_BASE=http://127.0.0.1:9 npm run build`.
Browser memakai Playwright1.62.1 + axe4.11.0 di tool environment terpisah; set
`NADI_PLAYWRIGHT_MODULE` ke `playwright/index.mjs` dan `NADI_AXE_MODULE` ke
`@axe-core/playwright/dist/index.mjs`, lalu jalankan
`node scripts/integration-browser.mjs`. CI memakai fixture PostgreSQL ephemeral
milik CI untuk suite persistence existing, bukan store laptop.

| Temuan / severity | Koreksi dan retest |
|---|---|
| Medium — initial product-safety menolak 6 badge tanpa explicit mode | Menambahkan `raw-neutral`, tanpa mematikan guard; product-safety, 22 component dan browser67 PASS |
| High deployment prerequisite — endpoint factual tidak memiliki route-level auth | Kandidat dibatasi development oleh server; production mount/read ditolak; SSR regression PASS. Tidak mengubah API/security boundary |
| Low tooling — compiler subprocess dibatasi sandbox; initial browser module path dan satu cwd test belum tepat | Perintah hermetik dijalankan dengan izin subprocess yang sesuai dan path/cwd eksplisit; seluruh gate tersebut PASS |
| Existing low — dua warning lint | Ignored config coverage status route dan dependency `current` di EngineeringWorkspace; tidak disentuh karena di luar scope |
| Accessibility limitation — axe incomplete pada shell dan tabel bergulir | Chevron/menu non-text, sebagian catatan Engineering, serta sel tabel di luar bagian scroll yang terlihat pada768/390. Detail per ukuran tersimpan; tidak disembunyikan/suppressed. [Review12 pasangan warna V1](evidence/nadi-integration-ui-01/contrast-review.json) semuanya ≥4.5:1. Focus/keyboard, contained overflow dan visual screenshot diperiksa; bukan sertifikasi konformitas penuh |

Review terpisah setelah feature complete mencakup source/API boundary, tidak ada
health calculation, independent error states, escaping konten, neutral badge,
production gate, semua URL existing, token reuse dan diff terbatas. Tidak ada
critical/high implementation finding terbuka dalam scope development. Approval
visual Product Owner dan review deployment tetap terpisah.

## Screenshot — seluruhnya DEMO / QA SINTETIS

| Layar | Light | Dark |
|---|---|---|
| Desktop1440 | [Gambar](evidence/nadi-integration-ui-01/integration-light-1440.png) | [Gambar](evidence/nadi-integration-ui-01/integration-dark-1440.png) |
| Desktop1920 | [Gambar](evidence/nadi-integration-ui-01/integration-light-1920.png) | [Gambar](evidence/nadi-integration-ui-01/integration-dark-1920.png) |
| Tablet768 | [Gambar](evidence/nadi-integration-ui-01/integration-light-768.png) | [Gambar](evidence/nadi-integration-ui-01/integration-dark-768.png) |
| Mobile390 | [Gambar](evidence/nadi-integration-ui-01/integration-light-390.png) | [Gambar](evidence/nadi-integration-ui-01/integration-dark-390.png) |

Tidak ada unintended horizontal page overflow; tabel bergulir dalam region
focusable. Nav desktop/drawer tablet-mobile, Escape, disclosure Enter, focus
indicator, heading/table labels dan kedua tema diuji. Reuse V1 navy/green,
spacing, surface dan typography; tanpa library komponen/desain kedua atau metrik
ilustratif dari PNG asli. Review visual dilakukan atas hasil sintetis, bukan
jaminan semua populasi real telah diinspeksi.

## Preservasi dan langkah berikutnya

Tidak ada akses runtime aktif, DB/session, collector/Mart, source request,
controller install, cutover, restart, deployment, policy change atau merge.
Original PNG, workbook, worktree lain, PR75–81 dan seluruh rekam existing tidak
dimodifikasi. Git diff hanya UI/presentation, tests/CI hermetik dan dokumentasi.
Tidak ada klaim verifikasi health runtime yang tidak dilakukan.

M02/M03/M07 tetap **ON HOLD**; [26 keputusan engineer](nadi-pdm-eng-validation-01.md)
masih PENDING_ENGINEER_VALIDATION; tidak ada respons/approval baru. Phase0–5 dan
Phase1 review/checkpoint/hard-expiry tidak berubah.

**Next:** senior/product review DRAFT PR, kemudian conditional integration
checkpoint dengan otorisasi terpisah. Belum ada izin runtime promotion atau merge.
