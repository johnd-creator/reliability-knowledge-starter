# 05 — Roadmap Implementasi dan Backlog

## Cara membaca roadmap

Roadmap ini berurutan berdasarkan dependency, bukan janji kalender. Estimasi memakai
ukuran S/M/L karena kapasitas tim dan akses environment belum ditentukan.

- **S:** perubahan lokal kecil, risiko rendah;
- **M:** lintas beberapa module dengan migration/test;
- **L:** lintas subproyek atau memerlukan keputusan domain/operasional.

P0 harus selesai sebelum dashboard dianggap production-ready. P1 melengkapi lima
konsep. P2 adalah scale/advanced capability.

## Milestone 0 — Baseline dan keputusan formal

Tujuan: mengunci arah sebelum membuat container atau UI baru.

| ID | Prioritas | Ukuran | Deliverable |
|---|---|---:|---|
| ARCH-001 | P0 | S | ADR: satu Compose project, image per aplikasi, DB terisolasi |
| ARCH-002 | P0 | S | ADR: cockpit hanya mengonsumsi collector API |
| ARCH-003 | P0 | M | Audit dan test kontrak API collector saat ini |
| DATA-001 | P0 | M | Rekonsiliasi count/status CEMS registry dan dokumentasi |
| DATA-002 | P0 | M | Daftar PI P0/P1 yang disetujui engineering; benchmark cycle |
| DATA-003 | P0 | M | Daftar status WO completed/open/cancelled dan overdue definition |
| UX-001 | P0 | S | Traceability matrix widget konsep → endpoint → source/formula |

Exit criteria:

- tidak ada keputusan arsitektur utama yang masih bergantung pada asumsi "satu image";
- setiap widget konsep berlabel source, derived, workflow, atau not available;
- baseline test tiap subproyek tercatat;
- data PI/CEMS yang belum verified tidak dipakai untuk production scoring.

## Milestone 1 — Unified runtime

Tujuan: seluruh aplikasi dapat dibangun dan dinyalakan dengan satu command.

| ID | Pri | Size | Task |
|---|---|---:|---|
| PLAT-001 | P0 | M | Dockerfile non-root + `.dockerignore` Maximo collector |
| PLAT-002 | P0 | M | Dockerfile non-root + `.dockerignore` PI collector |
| PLAT-003 | P0 | M | Dockerfile non-root + `.dockerignore` CEMS collector |
| PLAT-004 | P0 | M | Dockerfile backend dan multi-stage web cockpit |
| PLAT-005 | P0 | L | Root `compose.yaml`, internal network, four DB volumes, health/dependency |
| PLAT-006 | P0 | M | Init/migration/registry one-shot service yang idempotent |
| PLAT-007 | P0 | S | `.env.platform.example` dan runbook start/stop/log/backfill |
| PLAT-008 | P0 | M | Dev override untuk port bind/hot reload tanpa mengubah baseline |

Exit criteria:

- clean checkout + secret runtime dapat menjalankan `docker compose up -d`;
- semua init selesai satu kali dan rerun tidak merusak data;
- stop/start mempertahankan cursor dan volume;
- hanya web/API yang sengaja dipublikasikan; DB internal;
- image tidak mengandung `.env`, credential, `.venv`, atau local samples sensitif.

## Milestone 2 — Collector scheduling dan reliability

### Maximo

| ID | Pri | Size | Task |
|---|---|---:|---|
| MXR-001 | P0 | M | Tambah daemon/scheduler per operational/asset/master group |
| MXR-002 | P0 | M | DB advisory lock/non-overlap dan graceful SIGTERM |
| MXR-003 | P0 | M | Retry bounded, jitter, last attempt/success/duration/next run |
| MXR-004 | P0 | M | Cursor boundary overlap + deterministic paging regression test |
| MXR-005 | P1 | S | Manual trigger memakai lock yang sama dan role/internal auth |

### PI

| ID | Pri | Size | Task |
|---|---|---:|---|
| PIR-001 | P0 | L | Satu scheduler yang mengatur tier P0/P1/history secara serial |
| PIR-002 | P0 | M | Global DB lease sehingga tidak ada dua source egress worker |
| PIR-003 | P0 | M | Registry operational fields/tier terpisah dari knowledge status |
| PIR-004 | P0 | M | Benchmark 433 dan subset semantic; tetapkan freshness SLO realistis |
| PIR-005 | P0 | M | Continuous history strategy untuk trend tanpa melanggar off-hours guard |
| PIR-006 | P1 | M | Coverage/gap/quality metrics per equipment/method |

### CEMS

| ID | Pri | Size | Task |
|---|---|---:|---|
| CER-001 | P0 | M | Aggregation daemon native, cursor recovery, graceful shutdown |
| CER-002 | P0 | M | Poll/aggregate advisory lock dan duplicate trigger guard |
| CER-003 | P0 | L | Retention/partition/index/compression plan + load test |
| CER-004 | P0 | M | Registry count/status/docs validation test |
| CER-005 | P1 | M | Gap/late sample/transform failure observability |

Exit criteria:

- ketiga collector berjalan 24 jam bersamaan di staging;
- restart/temporary source outage tidak menghilangkan cursor atau membuat duplicate;
- tidak ada overlapping source request worker;
- Maximo no-change cycle tidak menghasilkan perubahan palsu;
- PI rate limit total tetap dipatuhi;
- CEMS aggregation mengejar completed windows setelah downtime;
- source safety tests tetap lulus.

## Milestone 3 — Kontrak dan identity spine

| ID | Pri | Size | Task |
|---|---|---:|---|
| CON-001 | P0 | M | `asset-source-link` schema + verified mapping workflow |
| CON-002 | P0 | M | CEMS parameter/reading/aggregate schema + mapping doc |
| CON-003 | P0 | M | collector-run dan data-source-status contract |
| CON-004 | P0 | L | finding/recommendation/risk/health schemas |
| CON-005 | P0 | M | Cross-repo JSON Schema validation/contract fixtures |
| IDN-001 | P0 | L | Maximo asset ↔ PI equipment/attribute verified map seed |
| IDN-002 | P1 | M | CEMS stack relationship map tanpa memaksa asset-level identity |
| IDN-003 | P0 | M | Coverage report: linked/unlinked/documented/verified |

Exit criteria:

- semua identifier lintas sumber traceable ke mapping/version/verification;
- tidak ada fuzzy runtime join untuk production scoring;
- schema dan fixtures lulus Draft 2020-12 validation;
- backward compatibility test tersedia untuk API consumer.

## Milestone 4 — Cockpit ingestion dan observability

Current boundary: **Maximo Collector → Cockpit: IMPLEMENTED**. PI Collector API
and CEMS Collector API are **VERIFIED**, while **PI → Cockpit projection** and
**CEMS → Cockpit projection** remain **PENDING**. The current Cockpit worker does
not ingest all configurable collector APIs.

| ID | Pri | Size | Task |
|---|---|---:|---|
| ING-001 | P0 | M | Selaraskan cockpit CLI dengan `CollectorClient` Maximo |
| ING-002 | P0 | L | Pagination/cursor/overlap/transactional checkpoint Maximo pull |
| ING-003 | P0 | M | PI collector client untuk registry/snapshot/aggregate query |
| ING-004 | P0 | M | CEMS collector client untuk registry/latest/5-minute/status |
| ING-005 | P0 | M | Source projection cursors dan run audit |
| ING-006 | P0 | M | Integration status aggregator + readiness/degraded states |
| ING-007 | P0 | M | Hapus credential/source access dari normal cockpit deployment |
| ING-008 | P1 | M | Cache/bounded proxy untuk detailed time-series chart |

Exit criteria:

- cockpit dapat dibangun tanpa Maximo/PI credential;
- full + incremental pull lebih dari satu page terbukti tidak kehilangan row;
- source down menampilkan last-known data + stale status;
- `/integrations/status` menjelaskan last success, lag, row/error, dan coverage;
- direct Maximo code path tidak menjadi default dan docs konsisten.

## Milestone 5 — Derived reliability domain

| ID | Pri | Size | Task |
|---|---|---:|---|
| DOM-001 | P0 | M | Measurement method taxonomy + reviewed mapping |
| DOM-002 | P0 | L | Condition finding service + evidence/provenance/idempotency |
| DOM-003 | P0 | L | Versioned health score + data completeness behavior |
| DOM-004 | P0 | L | Versioned risk assessment + explainable breakdown |
| DOM-005 | P0 | L | Recommendation aggregate + append-only event history |
| DOM-006 | P1 | L | Maintenance/budget/RCA/risk-acceptance decision workflow |
| DOM-007 | P0 | M | Rework KPI schedule, lineage, and documented data limitations |
| DOM-008 | P1 | M | Repeat failure/RCA rule dengan rolling window versioned |

Exit criteria:

- formula dan threshold mempunyai owner/approval/version;
- missing/stale/bad quality tidak pernah dianggap healthy;
- recompute menghasilkan output idempotent;
- user decision tidak ditimpa recompute;
- recommendation hanya link existing WO dan tidak menulis Maximo;
- result dapat dijelaskan dari evidence sampai source timestamp.

## Milestone 6 — Cockpit API dan UI foundation

| ID | Pri | Size | Task |
|---|---|---:|---|
| API-001 | P0 | L | Dashboard aggregate endpoints + common pagination/filter contract |
| API-002 | P0 | M | Asset health/detail/PdM endpoints |
| API-003 | P0 | M | Recommendation/action workflow endpoints |
| API-004 | P0 | M | AuthN/AuthZ, audit, optimistic concurrency, CSRF/session policy |
| UI-001 | P0 | M | Tokens, AppShell, sidebar/top bar, responsive navigation |
| UI-002 | P0 | M | Common metric/chart/table/state/accessibility components |
| UI-003 | P0 | M | URL-backed filters, query cache, error boundary, freshness UI |
| UI-004 | P0 | M | System Integration page |

Exit criteria:

- API OpenAPI/contract tests lulus;
- dashboard tidak melakukan N+1 request;
- role tests mencegah unauthorized workflow mutation;
- UI memenuhi keyboard/contrast/semantic smoke test;
- tidak ada hardcoded business metrics.

## Milestone 7 — Lima layar konsep

| ID | Pri | Size | Deliverable |
|---|---|---:|---|
| UI-101 | P0 | L | Asset portfolio + Asset Health Detail |
| UI-102 | P0 | L | Executive Overview |
| UI-103 | P0 | L | PdM Center |
| UI-104 | P1 | L | Recommendations list/detail/workflow |
| UI-105 | P1 | L | Action Board + decision detail |
| UI-106 | P1 | M | Reports |
| UI-107 | P1 | M | Administration |

Exit criteria per halaman:

- visual hierarchy dan navigation mengikuti konsep;
- semua card/table/chart memiliki source/definition/freshness;
- filters, drilldown, pagination, deep link, dan back navigation berfungsi;
- loading/empty/not-configured/partial/stale/error/forbidden diuji;
- responsive dan accessibility acceptance terpenuhi;
- angka layar cocok dengan query backend untuk fixture yang sama.

## Milestone 8 — Hardening dan release

| ID | Pri | Size | Task |
|---|---|---:|---|
| OPS-001 | P0 | M | Metrics, structured logs, correlation/run IDs, alerts |
| OPS-002 | P0 | M | Backup/restore drill tiap DB dan documented RPO/RTO |
| OPS-003 | P0 | M | Retention/compression/purge policy + restore test |
| OPS-004 | P0 | L | 24–72 hour soak test + source outage/restart tests |
| OPS-005 | P0 | M | Image/dependency/security scan dan non-root verification |
| OPS-006 | P0 | M | Staging UAT dengan reliability engineer/management |
| OPS-007 | P0 | M | Rollback runbook dan release checklist |
| OPS-008 | P1 | M | Performance/load budget regression pipeline |

Exit criteria:

- no safety guard regression;
- restore dari backup terbukti, bukan hanya backup job sukses;
- alerts actionable dan tidak memuat secret/personal payload;
- UI/API tetap menyajikan last-known data ketika satu source down;
- stakeholder menandatangani formula, labels, dan workflow;
- rollback image + migration telah diuji di staging.

## Backlog per subproyek

### Root

- root Compose/dev override/env example/runbook;
- CI orchestration untuk build images, contract tests, compose smoke;
- platform version/release notes.

### Maximo collector

- scheduler/lock/status;
- stable paginated export contract;
- contract/version tests;
- tetap mempertahankan guard dan source scope.

### PI collector

- single-worker tier scheduler;
- global lease, capacity metrics, history strategy;
- reviewed measurement method/asset mapping inputs;
- aggregate query endpoint untuk cockpit.

### CEMS collector

- aggregator daemon/lock;
- registry/document count consistency;
- time-series retention/partitioning;
- environmental contract serializer dan aggregate API hardening.

### Reliability data contracts

- identity, observability, CEMS, finding, health, risk, recommendation contracts;
- mapping docs + fixtures + compatibility tests.

### Reliability Cockpit backend

- collector-only ingestion;
- new migrations/domain/services/read models/API;
- auth/RBAC/audit;
- observability/report export.

### Reliability Cockpit web

- design system/application shell;
- integration status;
- five concept routes;
- workflow, accessibility, responsive, error/freshness states.

## Keputusan yang memerlukan pemilik bisnis/engineering

Implementasi dapat memulai platform work tanpa jawaban ini, tetapi derived domain
tidak boleh masuk production sebelum diputuskan:

1. Aset/unit mana yang masuk scope dashboard pertama?
2. PI attribute mana yang masuk tier P0 dan method apa yang sah?
3. Standard/threshold vibration, temperature, current, oil, dan DGA per equipment?
4. Formula dan category boundary health score/risk score?
5. Definisi failure, repeat failure, overdue WO, dan WO backlog?
6. Siapa yang boleh membuat/assign/close recommendation dan menerima risiko?
7. Apakah CEMS tampil hanya sebagai environmental/compliance view atau ikut risk
   score asset tertentu?
8. Retention raw PI/CEMS, RPO, RTO, dan kebutuhan audit report?
9. Identity provider dan role mapping yang akan digunakan?
10. Apakah ada Maximo event/webhook/message interface yang verified dan diizinkan?

Jawaban disimpan sebagai ADR/configuration approval, bukan hanya percakapan.

## Status eksekusi — 20 Agustus 2026

Legenda: **DONE** berarti artefak dan validasi lokal ada; **PARTIAL** berarti fondasi ada tetapi exit criterion belum terbukti; **BLOCKED** menunggu data/keputusan yang tidak boleh diasumsikan.

| Milestone | DONE | PARTIAL | BLOCKED |
|---|---|---|---|
| M0 | ARCH-001, ARCH-002, ARCH-003 collector API audit, DATA-001 registry reconciliation, UX-001 (dokumentasi traceability) | DATA-003 (business definition WO) | DATA-002 hanya P0/P1/benchmark; baseline PI collection sudah verified dan tidak diblokir oleh tier |
| M1 | PLAT-001..008: Dockerfile non-root, Compose, init, env/runbook, dev port override | cold-start/restart dengan Docker image dan source nyata | — |
| M2 | MXR-001 (dua cadence + SIGTERM), CER-001 (aggregation daemon + SIGTERM), PI registry/API/data collection verified | MXR-002..004, CER-002..005, PIR-001..006; scheduler Cockpit berjalan tetapi tanpa distributed lock/run audit | MXR-005/CER manual-trigger auth perlu policy; PI tier is not a source-access blocker |
| M3 | CON-001 (schema workflow), bagian CON-003/CON-004, validasi 19 schema | CON-002, CON-003..005 karena schema/mapping/fixture belum lengkap | IDN-001..003 tanpa evidence mapping verified |
| M4 | ING-001, ING-002 (collector paging), ING-007 | ING-005 | ING-003/004/006/008: read model PI/CEMS/status belum dibangun |
| M5 | — | DOM-007 memakai KPI yang telah ada | DOM-001..006/008: formula, threshold, mapping, dan workflow approval belum ada |
| M6–M7 | — | — | API-001..004, UI-001..107; mengikuti dependency M3–M5 dan AuthZ |
| M8 | source guard regression suite Maximo/CEMS tercatat | OPS-005 static non-root/hygiene | OPS-001..004, OPS-006..008: perlu staging, security scan, backup/restore, dan owner operasional |

Validasi pada eksekusi ini: `docker compose config` berhasil dengan env dummy; Maximo 41 test dan CEMS 82 test lulus; Cockpit 37 test hermetic lulus; 19 schema valid. Dua smoke test Cockpit yang mengharapkan SQLite masih mencoba PostgreSQL default dan dicatat pada plan 01.
