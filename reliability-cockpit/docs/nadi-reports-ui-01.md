# NADI-REPORTS-UI-01 — Reports Center V1

15 Oktober 2026 · **Kandidat development IMPLEMENTED/TESTED; belum merged, live,
PO accepted atau operational approved.** Branch `codex/nadi-reports-ui-01`, dari
main `36203fe478e5a558fcf5ce4f8d5a9ff36fe92014` (PR87 merged). Exact source
implementation SHA: `8438adc3091eb1920cfd9514799ec8a5b5d2c8cc`.
Final documentation/evidence HEAD, DRAFT PR URL dan exact-head CI dicatat pada
delivery GitHub/handoff; SHA di atas mengidentifikasi source implementasi, bukan
self-reference commit laporan. [Manifest source/gambar](evidence/nadi-reports-ui-01/manifest.json).

## Dua definisi kandidat, bukan definisi report yang telah disahkan

Setiap template dan preview bertanda
**DEVELOPMENT CANDIDATE — NOT OPERATIONALLY APPROVED**. Versi0.1 berikut adalah
identitas definisi kandidat UI, bukan versi kontrak backend atau approval bisnis.

| Kandidat / ID | Sumber existing | Filter / batas |
|---|---|---|
| Data Coverage Report / `NADI-RPT-COVERAGE-CANDIDATE`0.1 | DataTrustView, GET `/v1/reliability/data-trust` | Tidak memiliki filter periode; populasi yang dikembalikan API, bukan report30 hari |
| Maintenance Activity Report / `NADI-RPT-MAINTENANCE-CANDIDATE`0.1 | DecisionOverviewView, GET `/v1/reliability/decision-overview?window_days=7|30|90` | Hanya pilihan7/30/90 via method existing `decisionOverview(windowDays)`; mismatch respons ditolak |

Rujukan authoritative: [DTO/client existing](../web/lib/api.ts),
[backend DTO/formatter](../src/api/reliability.py),
[semantik Mart](reliability-mart-query-api.md) dan
[repository query existing](../src/repositories/mart_reader.py).
Tidak mengubah backend, DTO, schema, query, enum, source acquisition atau store.
Tidak ada model data report backend kedua.

### Data Coverage

Preview menampilkan population Registry, technical context, maintenance lokal
beserta scope Registry, FMEA, assessment records, RCFA dan Overhaul. Angka langsung
`population` tidak memperoleh label VERIFIED rekaan: DTO tidak menyediakan
klasifikasi per field itu. Tabel domain menampilkan `population_type`,
`evidence_class`, jumlah/scope, selected source provenance, `latest_record_date`,
`date_basis`, relationship state dan limitation sebagaimana DTO.

Referensi Registry/aset/Work Order resolved/unresolved ditampilkan terpisah lewat
`integrity`; relasi rinci mengungkap evidence dan unresolved context. Populasi
bisnis tidak dijumlahkan dengan konteks teknis atau dianggap lengkap historis.
Assessment count bukan health score; RCFA global tidak otomatis mempunyai Asset
relationship. Null/missing count UNKNOWN; nol asli tetap nol.

DataTrustView tidak mempunyai independent observation/as-of timestamp atau period
filter. UI menyatakannya, tidak menaruh jam fetch/browser atau periode pemeliharaan
ke angka Coverage. Source-record dates bukan sync/collection freshness. Source
links menuju `/data-quality`, `/assets`, `/maintenance`, `/fmea`, `/asset-health`,
`/rcfa`, `/overhauls`; tidak ada operational source URL.

### Maintenance Activity

Ringkasan mengambil **key existing yang sesuai** periode pilihan:
`maintenance_activity_7d/30d/90d` dan `assets_active_7d/30d/90d`. Registered Asset
population adalah konteks Registry saat query, bukan count kejadian dalam periode.
Semua metrik berselubung EvidenceValue memakai shared `factualMetric`; hanya
VERIFIED/DERIVED_SAFE finite nonnegative value tampil sebagai angka. Null/invalid
UNKNOWN; BUSINESS_SEMANTICS_REQUIRED menjadi NOT ASSESSED; DEFERRED/unsupported
bukan numeric verified result. Grafik dan tabel sama-sama menolak nilai gated.

`window_days`, `window_start`, `as_of`, source/date basis disajikan tanpa membuat
rentang sendiri. Respons period yang berbeda dari request tidak boleh merender
angka. As-of adalah batas query DTO, bukan freshness produksi.

**Scope kronologi berbeda:** query existing selalu menghasilkan12 bucket minggu,
independen dari selected7/30/90 window. Status/work-type distribution dan
activity concentration memakai window pilihan; kronologi **tidak** difilter atau
dipotong di browser agar terlihat cocok. Setiap bucket memakai period_start/end
asli, memiliki equivalent visible data table, tanpa interpolasi/gap fill. Bucket
minggu terakhir dapat berakhir setelah as-of; itu bukan klaim minggu lengkap.
Tidak menjumlahkan bucket menjadi metrik periode. Konsentrasi mempertahankan
urutan/jumlah API, maksimum10 aset; bukan populasi lengkap atau ranking risiko.

Work Order status bukan physical completion; activity bukan failure. Integrity
adalah konteks populasi Mart yang dikembalikan, bukan angka berperiode. Tidak ada
MTBF, MTTR, Availability, PM Compliance, failure rate, scoring atau alarm baru.

## Arsitektur UI dan deployment gate

- `/reports` di `(workspace)` memakai AppShell/V1 existing; item navigation ID
  `reports` berubah dari PLANNED menjadi link kandidat. Seluruh source/detail/QA
  URL existing dipertahankan; tidak membuat aplikasi atau styling framework lain.
- [ReportsCenter](../web/components/ReportsCenter.tsx) hanya membaca DTO untuk
  report terpilih. [CoverageReport](../web/components/CoverageReport.tsx),
  [MaintenanceReport](../web/components/MaintenanceReport.tsx) dan
  [ReportEvidence](../web/components/ReportEvidence.tsx) memisahkan presentation
  tanpa mengubah kontrak; [catalog/helper](../web/lib/reports.ts) hanya metadata
  kandidat, pemilihan key existing dan formatting/guard presentation.
- Keyed reader per selection/window memulai loading kosong; cleanup effect
  menolak callback lama. Races7→90 dan Coverage→Maintenance teruji. Tidak ada
  background polling, refresh scheduler, report history/cache persistence atau
  sumber mutable. Manual retry mengulang read yang sama.
- Provenance ringkas membawa ID/versi kandidat, DTO/API, scope, supported period,
  authoritative as-of/date basis, evidence/unknown/limitations. Dua endpoint
  **bukan snapshot atomik**; tidak memakai browser clock sebagai source time.
- Route server hanya memasang reader saat `NODE_ENV=development`. Non-development
  menampilkan deployment prerequisite tanpa report reader/request. Seperti
  [System Integration Center](nadi-integration-ui-01.md), ini **bukan otorisasi
  endpoint underlying**. Existing factual API access masih memerlukan review
  auth/scope sebelum deployment umum; tidak memperluas/mengganti auth.
- 401/403/unavailable menampilkan pesan generik tanpa raw server exceptions.
  React escaping dan fixed source-page links dipertahankan; tidak ada arbitrary
  proxy, endpoint baru, raw vendor payload atau PII.

**Ekspor/distribusi OFF:** tidak ada PDF/XLSX/CSV generation, download, email,
sharing, publish, jadwal, private record extraction atau penyimpanan report.
Screenshot di bawah adalah evidence test yang diotorisasi, bukan fitur report
export. Tidak ada perubahan global login, CSRF, RBAC, cookie, session atau audit.

## Bukti pengujian dan autonomous review

Semua browser request diintersep ke reserved synthetic origin tanpa server/listener,
API QA, localhost aktif, database/session existing atau office/source network.
Fixture DTO terbatas berlabel **DEMO / QA SYNTHETIC**, tanpa nilai plant/PII.
CI existing persistence suites memakai PostgreSQL ephemeral milik CI, bukan
store laptop; local DTO/Mart tests memakai pure models/temporary SQLite.

| Gate lokal pada source kandidat | Hasil |
|---|---|
| Reports unit/presentation/production gate/navigation |26/26 PASS |
| Reports browser: selection, periods, late response, loading/empty/gated/null/zero, mismatch,503/401/403 |97/97 PASS |
| Existing System Integration browser |67/67 PASS |
| Existing factual/login/Engineering/Case/advisory workflow browser |395/395 PASS |
| Existing PdM/workbook/review/handoff/keyboard browser |573/573 PASS |
| Backend DTO/Mart regression |45/45 PASS (4 new fixture checks) |
| Existing frontend assertions, TypeScript, ESLint, production build, diff whitespace |PASS;2 existing lint warnings |
| Axe A/AA on16 report/width/theme combinations |0 violations; incomplete observations retained |
| Final exact-head GitHub backend/frontend |Recorded independently in PR checks/delivery; local PASS does not imply CI/runtime acceptance |

[Validation summary](evidence/nadi-reports-ui-01/validation-summary.json),
[full Reports browser requests/accessibility](evidence/nadi-reports-ui-01/reports-browser.json)
and [resolved findings](evidence/nadi-reports-ui-01/resolved-findings.json).
Distinct final self-review checked DTO semantics, unsupported evidence gating,
window/chronology distinction, stale-response lifecycle, error privacy, URL
compatibility, production reader gate, token reuse and absence of export/source
mutations. No critical/high development blocker remains; no engineer or PO visual
approval is inferred from self-review.

| Finding | Correction / retest |
|---|---|
| Medium: table region lacked visible keyboard outline | Add scoped `focus-visible` for Reports table/chart region; full browser outline/keyboard PASS |
| Low: initial scroll observation sampled before native animation settled | Wait up to1.5s for actual keyboard scroll; predicate/assertion unchanged, no app retry/workaround |
| Medium: period control accessible-name ambiguity | Explicit name matching visible label; supported options and7/30/90/race tests PASS |
| Known deployment prerequisite | Non-development reader blocked; no API authorization claim; production gate regression PASS |
| Existing lint warnings | Ignored development-status config coverage and EngineeringWorkspace dependency warning retained, no unrelated fix |
| Axe incomplete | Desktop0 incomplete; smaller widths include non-text menu and clipped/obscured scroll-table text. Preserve all nodes; no rule suppression or WCAG certification. Keyboard table scrolling/focus and [12 V1 contrast pairs](evidence/nadi-reports-ui-01/contrast-review.json) PASS |

Reproduction: `npm ci`, `npm run check:reports`, `npm run lint`,
`npx tsc --noEmit`, `COCKPIT_API_BASE=http://127.0.0.1:9 npm run build`.
For browser, set `NADI_PLAYWRIGHT_MODULE` to Playwright1.62.1/index.mjs and
`NADI_AXE_MODULE` to axe4.11.0/dist/index.mjs in a test-only tool environment;
run `node scripts/reports-browser.mjs`. No runtime/controller startup required.

## Screenshots — synthetic components, not live preview

| Preview / width | Light | Dark |
| Data Coverage / 1440 | [Image](evidence/nadi-reports-ui-01/coverage-light-1440.png) | [Image](evidence/nadi-reports-ui-01/coverage-dark-1440.png) |
| Data Coverage / 1920 | [Image](evidence/nadi-reports-ui-01/coverage-light-1920.png) | [Image](evidence/nadi-reports-ui-01/coverage-dark-1920.png) |
| Data Coverage / 768 | [Image](evidence/nadi-reports-ui-01/coverage-light-768.png) | [Image](evidence/nadi-reports-ui-01/coverage-dark-768.png) |
| Data Coverage / 390 | [Image](evidence/nadi-reports-ui-01/coverage-light-390.png) | [Image](evidence/nadi-reports-ui-01/coverage-dark-390.png) |
| Maintenance Activity / 1440 | [Image](evidence/nadi-reports-ui-01/maintenance-light-1440.png) | [Image](evidence/nadi-reports-ui-01/maintenance-dark-1440.png) |
| Maintenance Activity / 1920 | [Image](evidence/nadi-reports-ui-01/maintenance-light-1920.png) | [Image](evidence/nadi-reports-ui-01/maintenance-dark-1920.png) |
| Maintenance Activity / 768 | [Image](evidence/nadi-reports-ui-01/maintenance-light-768.png) | [Image](evidence/nadi-reports-ui-01/maintenance-dark-768.png) |
| Maintenance Activity / 390 | [Image](evidence/nadi-reports-ui-01/maintenance-light-390.png) | [Image](evidence/nadi-reports-ui-01/maintenance-dark-390.png) |

V1 navy/green, light/dark surfaces, responsive catalog/cards and contained table/chart
scrolling are preserved. All four widths have no page overflow; equivalent chart
data is accessible as a table. Screenshots contain no confidential plant data.

## Preserved gates and next action

No active frontend/source selection, controller, service restart, operational
source GET, collector/scheduler, database/session, Mart, freshness-policy action,
external QA/production deployment or merge. Original PNGs/workbook and other
worktrees preserved. No change to frozen PR75–81 or operational data ownership.

M02/M03/M07 stay **ON HOLD**, all26 [engineer decisions](nadi-pdm-eng-validation-01.md)
remain PENDING_ENGINEER_VALIDATION. Phase0–5/history and Phase1 review/checkpoint/
hard-expiry remain unchanged. Candidate report definitions do not approve an
engineering method, operational KPI or report delivery.

Before real operational reporting: authorized template/definition owner and version,
validated scope/evidence/as-of/completeness rules, deployment auth/privacy policy,
export/distribution/retention authorization and PO acceptance are still required.

**Next:** senior review, then a separately authorized conditional development
checkpoint. Do not merge/promote or begin another task automatically.
