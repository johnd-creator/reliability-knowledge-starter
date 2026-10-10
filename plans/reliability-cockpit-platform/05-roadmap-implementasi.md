# 05 — Roadmap Implementasi dan Backlog

## Documentation continuity — 2026-10-10

M0–M8 remains the technical implementation roadmap under the single
[official NADI product roadmap](../NADI-ROADMAP.md), which now owns the UX-01–09
track. Requirements/design are [PRD](../../PRD.md) and
[UI specification](../../docs/design/NADI-UI-SPEC.md). Main 0cb26882c870185a54282df3af4a136f31702b67 includes merged
PR29–63. PR62 supplies the persistent single frontend; PR63 supplies PdM requirements
and engineer-validation gates. Older OPEN statements below are dated history.
[FIX-03 reconciliation evidence](../../docs/NADI-DOC-FOUNDATION-01.md) records the
merge into PR64; no runtime source selection or restart is performed.
No implementation sequence or operational acceptance is completed by this docs task.

## Historical NADI-DEV-RESET-01 — single development address — 2026-10-09

Review current development at **https://localhost:3000/** using the existing PR #62
launcher/isolated fixture. Latest verified main baseline: `f54643f3510bf505628a1400024784faab46e496`.
Default selection is merged main; the unmerged foundation requires explicit feature
preview. No automatic merge of #62/#63. Follow the [startup, cutover and rollback
runbook](../../reliability-cockpit/docs/nadi-dev-reset-01.md); 13035 is retired only
after primary browser acceptance. Full SHA/branch/dirty state, both backends and exact
fixture identity are visible. Operational factual routes remain reads of existing
stored data; Engineering records remain isolated and SYNTHETIC. Phase1
CURRENT/PARTIAL and real QA NO_GO remain. No new PdM capability in this task.

## NADI-E-INTEGRATION-02 — local authentication and final audit — 2026-10-09

Main `eda3595a9b8d86726dd0d89192ebf4657b66d27e` unchanged. Bundle E PR51–59 preserved;
E9 PR60 and E10 PR61 extend the OPEN/UNMERGED stack. Local username/password is the
selected initial-QA identity path; enterprise SSO is optional future work.
Tested implementation `1ec149de2d1acd4113987364e1f96c790bfaf63e`.
Argon2id accounts, private operator admin, versioned sessions/RBAC, actual HTTPS
login/workflow and disposable migration006 validated. Audit LOW stale-response
finding repaired; Compose preflight argv and migration docs corrected.
Cockpit687/Maximo181/PI191/contracts14 PASS,0FAIL/0SKIP including11 Timescale;
frontend143/browser40 +legacy25/type/build/32-file safety PASS. Actual source-free
preflight remains NO_GO with unapproved host/policy/storage references.
**Development acceptance PASS; merge READY pending explicit authorization/exact-head CI.**
**Phase1 CURRENT/PARTIAL; Phase2 CANDIDATE/PARTIAL; real QA NO_GO; activation OFF.**
Actual host/TLS, application DB/roles, admin custody/onboarding, reviewed startup and
secure frontend transport, password/session/resource policy, storage/scanner,
PdM fields/UAT and per-action deployment authority remain required. No SSO gate.
No production source GET/write, WO mutation, DB DDL, deployment or Phase1 mutation.
Older test counts/checkpoints below are historical.
[Final audit, tests, activation blockers and merge plan](../../reliability-cockpit/docs/nadi-e-integration-02.md).

## Bundle D merged / Bundle E QA preparation — 2026-10-09

PR44–50 MERGED via merge commits; authoritative main
eda3595a9b8d86726dd0d89192ebf4657b66d27e. Older OPEN/candidate statements below
are historical. Bundle E stack51→59 is OPEN/UNMERGED, preparation only.
Dedicated QA architecture, enterprise trust contracts, fail-closed privilege
audit, attachment integrity/recovery, bounded HTTP, source-free preflight, exact
artifact binding and disposable restart/restore rehearsal validated.
Final Cockpit661/Maximo181/PI191/contracts14,11Timescale, frontend127/type/build/
safety and browser25 PASS. No real QA UAT or operational activation.
**Phase1 CURRENT/PARTIAL; Phase2 QA preparation CANDIDATE/PARTIAL; real QA NO-GO.**
Operator allowed naming; actual host/IdP/DB role provisioning/storage/scanner,
reviewed real-QA startup/frontend integration, PdM fields/UAT and explicit
deployment authority remain required. No new production source request/write,
WO changes, DB DDL, deployment or Phase1 mutation.
[Bundle E handoff](../../reliability-cockpit/docs/nadi-phase2-bundle-e.md).


## Bundle D final integration review — NADI-D-INTEGRATION-01

Baseline main e836710 unchanged. Stack44→50 remains OPEN; no merge/deployment.
Session cancellation finding corrected6f66ecd in PR48; normal forward merges
preserve ancestry. Final implementation c03e57c; final documents at PR50 head.
Local acceptance Cockpit610/Maximo181/PI191/contracts14,11Timescale, HTTP11,
browser25 +proxy8, frontend110/type/build/safety PASS. Corrected scoped CI run
37892980855 SUCCESS; final PR50 CI must match its exact head before merge.
**Merge candidate READY pending explicit operator authorization.**
**Phase1 CURRENT/PARTIAL; Phase2 QA CANDIDATE/PARTIAL; operational activation BLOCKED.**
PUBLIC/default/schema-owner privilege audit, enterprise identity/deadlines,
attachment storage/recovery/scanner, PdM field approval and operational UAT remain
activation gates. QA proxy streaming caps are a non-operational follow-up.
[Final review, findings and controlled merge plan](../../reliability-cockpit/docs/nadi-d-integration-01.md). Older checkpoints
retain historical evidence; no source/production/Phase1 mutation or new acquisition.

## Current development checkpoint — Phase 2 Bundle D

Baseline main `e836710d1984af7a4bfb739bad0bfbbb96d544ca`, Bundle C PR37–43 MERGED.
Tested implementation `ee20307a2664e7ca64737c3f43f1256f26cdf9f6`.
**Development/test acceptance PASS; operational activation BLOCKED.**
**Phase1 CURRENT/PARTIAL; Phase2 integrated QA CANDIDATE/PARTIAL.**
D1–D7 stack adds enterprise identity adapter/session bootstrap, deliberate
application migration ledger/writer grants, private attachment service and real
HTTP/PostgreSQL/frontend workflow. Operational Engineering routes remain unmounted.
No production/source/Phase1 mutation; Maximo/PI strictly READ-ONLY, NADI never
creates or changes Maximo WO. Original accepted runtime is unchanged.

Final local Cockpit600, Maximo181, PI191, contracts14 PASS;11 formerly skipped
Timescale tests now executed in disposable fixtures. HTTP11/browser25/frontend110,
29 safety files/typecheck/build/diff-check PASS. D6 actual GitHub backend/frontend
jobs SUCCESS, run37887690942. Security diff review found no concrete reportable
issue in15 changed source/config surfaces; production IdP/storage not certified.
Real enterprise IdP/directory, existing-store provisioning/privilege approval,
secure storage/scanning, PdM engineer field sign-off and operational UI/UAT remain
external activation gates. QA command editor is not final engineering form UX.
[Bundle D acceptance and activation manifest](../../reliability-cockpit/docs/nadi-phase2-bundle-d.md) records the exact stack,
recovery proposal, test evidence and limits. Next: senior stack review, then
separately authorized identity/provisioning/field UAT. Older checkpoints below
retain historical measured evidence; they are not re-certified by this bundle.

## Current development checkpoint — Phase 2 Bundle C

Verified main `7a846ef2c7e25306f23da99dd011e1d54aa8f4a4`, BundleB PR30–36 MERGED.
**Phase1 CURRENT/PARTIAL; Phase2 CANDIDATE/PARTIAL; operational activation OFF.**
Stacked C1–C7 candidates add same-asset local context/maintenance chronology,
reviewed manual inspection evidence, case-linked recommendations and independent
local completion verification, integrated development-only concept screens and
trusted-session/PostgreSQL acceptance. Maximo/PI remain strictly source READ-ONLY;
NADI recommendations never create/update/close/approve/cancel Maximo WOs.

Local validation: Cockpit532 PASS (all disposable PG/Compose), Maximo181 PASS,
contracts14 PASS/35schemas, PI180 PASS/11 isolated Timescale SKIP;100 frontend
assertions,27 safety files,40 browser assertions, TypeScript/build/diff-check PASS.
No production access, DB/DDL, deployment, source acquisition or Phase1 mutation.
Enterprise identity/bootstrap, deliberate application provisioning/migration ledger,
PdM engineer fields, secure storage and operational UI integration/UAT remain BLOCKED.
Candidate UI is browser-memory DEMO only; no operational writer route is mounted.
Do not mark Phase1 or Phase2 COMPLETE. Historical operational evidence, GOV03 policy
approvals/checkpoints/expiry and accepted condition evidence are unchanged and not
re-certified by this software task.
[Bundle C report, stack and handoff](../../reliability-cockpit/docs/nadi-phase2-bundle-c.md)
Next: trusted enterprise bootstrap/provisioning contracts → engineer field approval
→ operational UAT. New Maximo coverage requires separate collection authorization.


## Current development checkpoint — Phase 2 Bundle B

Main `02e887c56057611f112b7b652ba9a9aee8b382ea`, corrected PR29 MERGED.
**Phase 1 CURRENT/PARTIAL; Phase 2 CANDIDATE/PARTIAL; activation OFF.**
B1–B7 implement source-boundary policy/coverage, trusted identity/session adapters,
bounded local WO context, Manual PdM envelope, NADI-native recommendations,
development-only concept lab and isolated integrated acceptance. Maximo/PI remain
strictly source read-only. A recommendation is not a WO or maintenance authorization.
No production source GET, DB/DDL, deployment, activation or Phase-1 evidence mutation.

Local evidence: Cockpit 462 pass (isolated PG + Compose), Maximo 181 pass,
contracts 14 pass, PI 180 pass/11 fixture skips; frontend 25+37 assertions,
product safety/typecheck/build and 24 browser checks pass. Enterprise provider,
reviewed session bootstrap/provisioning/migration ledger, engineer-approved method
fields, directories and operational UI/UAT remain required. No phase is marked COMPLETE.
[Bundle report and review stack](../../reliability-cockpit/docs/nadi-phase2-bundle-b.md) records limitations and migration/rollback proposals.
Next: trusted enterprise identity + PdM field sign-off + reviewed application
provisioning/backend integration. Earlier runtime checkpoints below are historical;
GOV03 approvals/checkpoints/expiry are unchanged and are not re-certified here.


## Current development checkpoint — overnight Engineering bundle 01

Baseline PR28 MERGED, main `e67c641e23214bf8851a05d312e1426c1e471ec3`.
**Phase 1 CURRENT/PARTIAL; Phase 2 IN DEVELOPMENT; Phase 3 DESIGN READY.**
Source-free candidate adds typed human cases, attributed independent review,
transactional audit/idempotency/concurrency, bounded local canonical references,
disabled isolated API contracts and an explicitly synthetic development-only UI.
Production write routes remain unmounted: trusted application identity/RBAC/session
and application writer/migration provisioning are BLOCKED, not simulated as users.
RCFA identity/Data Trust provider and operational UAT remain explicit gaps.

[Morning acceptance](../../reliability-cockpit/docs/nadi-phase2-overnight-bundle-01.md)
and [Phase 3 design](../../reliability-cockpit/docs/nadi-phase3-diagnostic-foundation.md)
record exact available tests and readiness. No source request, operational DB write,
deployment, worker/env/grant change or new operational database. Accepted R3 evidence,
GOV-03 policies/checkpoints/expiry and Phase-1 semantics remain untouched. This
checkpoint authorizes development reporting only; historical runtime evidence below
is not replaced by a new observation. Next: **NADI-PH2-02 — Trusted Engineering
Identity & Activation Contracts**. Do not mark Phase 2 COMPLETE or diagnostics live.

## Current accepted Phase-1 runtime — 2026-10-08

PR20 merged main c2fb0fc foundation deployed; see
[acceptance matrix](../NADI-PHASE-1-ACCEPTANCE.md) and
[runtime evidence](../../reliability-cockpit/docs/nadi-phase1-runtime-acceptance-001.md).
M1 existing Mart004/reader grants and reviewed consumer images ACCEPTED.
M3 typed selected condition/handoff/status contracts MERGED. M4 synthetic projection
acceptance PASS, production identity/signals/evidence still0. M6 integration-status,
Data Trust and Asset condition panels LIVE with independent UNKNOWN/BLOCKED/quality
states. M8 actual readonly9-gate preflight captures BLOCKED; schema/status PASS.
No new DB, worker restart, source request, mapping or signal approval/projection.

Phase1 software runtime foundation ACCEPTED; product BLOCKED/CURRENT/PARTIAL.
HUMAN_CROSSWALK_REQUIRED plus FRESHNESS_POLICY_PENDING remain explicit; controlled
human MATCH, approved signals, governed canary/time-quality review and bounded real
projection must precede final product PASS. Wider M0–M8 is not marked complete.
Historical snapshots below preserve their earlier backlog and measured evidence.

## Historical Phase-1 bundle candidate — 2026-10-08

Main remains f8c37f0; this bundle includes unmerged PR #19 foundation211faec and
B0–B4. [Phase-1 acceptance](../NADI-PHASE-1-ACCEPTANCE.md) is the current authority
for software/runtime/data/human gaps. Older milestone snapshots below retain
historical scope, not current missing-schema/open-PR assertions.

- M1: PI/Mart runtime PR #15/#16 are MERGED/ACCEPTED. Condition migration004
  and candidate API/collector/UI deployment are separate pending runtime work.
- M3: condition/selected-signal/handoff/status contracts are synthetic-tested
  candidates. Production mappings remain0/0; human crosswalk BLOCKED/EXTERNAL.
- M4: explicit selected PI evidence projection and PostgreSQL acceptance work
  with synthetic VERIFIED fixtures. Production PI projection is not performed;
  CEMS projection remains future scope.
- M6: integration status API/Data Trust/Asset panel and neutral freshness policy
  are candidates; no public write/source proxy is added.
- M8: read-only phase1-readiness evaluates nine product gates. Synthetic all-green
  PASS and real-like/actual zero-mapping BLOCKED are tested. Wider platform restore,
  soak/security/UAT acceptance is not claimed by this bounded bundle.

Phase1 software readiness PASS (candidate scope); product acceptance BLOCKED.
Do not mark Phase1 or all M0–M8 COMPLETE. Human identity, reviewed runtime, signal
semantics/approval and live governed evidence acceptance remain separate gates.

> Current roadmap entry point: [Power Plant Data Platform](../README.md).
> Product priority: NADI Phase 0–5; this document owns the M0–M8 engineering backlog.

## Historical NADI-ING-PI-001A checkpoint — 2026-10-07

PR #18 MERGED; baseline origin/main `f8c37f068102a06906cb3ca464fe08745e0351cf`.
[NADI-ING-PI-001A](../../reliability-cockpit/docs/nadi-ing-pi-001a.md) implementation
**CURRENT / candidate**, synthetic acceptance **PASS**: explicit separately
approved selected signals, governed collector boundary, canonical typed evidence,
additive latest-only existing-Mart migration, read-only API/Asset view and four
independent freshness dimensions. No production deployment/projection is claimed.

NADI-PI-001 ✅ MERGED; NADI-PI-RUNTIME-001 ✅ ACCEPTED;
NADI-RUNTIME-002 ✅ ACCEPTED. NADI-IDN-002A R1/R2 evidence rounds are completed;
NADI-IDN-002 human crosswalk **BLOCKED / EXTERNAL**, human verification PENDING.
PROPOSED0 / VERIFIED0 remain unchanged. BFPT stays REJECTED / FROZEN.
Task source GET/write0, no operational DDL/restart/new DB. Phase 1 remains
**CURRENT / PARTIAL**. Next: **NADI-INTEGRATION-STATUS-001**. Real governed PI
projection still requires human identity plus signal approval and deployment review.

## Status eksekusi terkini — rekonsiliasi 7 Oktober 2026

Basis: `main ef07a263b122d30e7dbec451e6094f9016b603c3`. Roadmap ini adalah
**engineering implementation roadmap di bawah [NADI Phase 0–5](../NADI-ROADMAP.md)**,
bukan roadmap produk yang terpisah. [Repository Status](../REPOSITORY-STATUS.md)
menyimpan bukti PR/branch dan batas audit. NK mempunyai [child roadmap](../NK-ROADMAP.md).

Status milestone menggunakan seluruh exit criteria, bukan sekadar keberadaan
file. Karena acceptance luas belum terbukti, M0–M8 dinilai **PARTIAL**; tabel
berikut tetap mengakui artefak yang sudah selesai. `NEEDS_REVIEW` berarti belum
ada bukti yang cukup untuk menerima exit criterion, bukan klaim implementasi
itu pasti tidak ada. Test/QA lama dicatat sebagai evidence historis, tidak
sebagai test run baru pada audit dokumentasi ini.

| Milestone | Status / kemajuan yang terbukti di main | Remaining / acceptance | Product relationship |
|---|---|---|---|
| M0 Architecture | PARTIAL: baseline/proposal/collector API boundary tersedia (`5f87013`, `87486cc`); factual NADI scope dan semantic trust matang lewat PR #1–#10 | ARCH-002 API-only harus dibaca dengan pengecualian Mart SELECT-only; DATA-002 cadence/SLO dan DATA-003 governed failure meaning belum diterima | Foundation untuk semua phase |
| M1 Runtime | PARTIAL: backend/web Dockerfile, root Compose/dev override, empat DB volume, init/env/runbook tersedia | NADI-PI-RUNTIME-001 mengusulkan managed Mart DSN dan PI worker opt-in; existing PI migration/API/source checkpoint tersedia, Mart governance schema masih perlu NADI-RUNTIME-002; cold-start/restart/restore acceptance perlu review. `7149455` dan `0c800da` adalah kandidat UNMERGED, bukan DONE | Phase 0 runtime debt / Phase 1 readiness |
| M2 Collectors | PARTIAL: Maximo cadence/run, PI snapshot/history CLI, CEMS collect/aggregation daemon dan source safety sudah menjadi artefak main | Global lease/non-overlap, benchmark tier/freshness, gap metrics, retention dan 24h multi-source acceptance belum terbukti lengkap | Shared foundation / Phase 1 evidence |
| M3 Contracts & Identity | PARTIAL: canonical Contract v1 (`28a0d47`, `0213402`), Mart (`6ec2b22`, `9e6f2b5`), governed Asset↔AF registry/admin (PR #8–#10) merged | IDN pilot VERIFIED mappings belum dibuktikan; migration/read-only grants/runtime acceptance terpisah. Richer PI quality exposure/contracts serta CEMS/status/decision contracts perlu review | Phase 0 canonical foundation + Phase 1 identity; future domain contracts |
| M4 Ingestion | PARTIAL: Maximo API→legacy Cockpit path, canonical Mart query (`7576214`), local Collector→Mart projection (`fa1bc05`) tersedia | ING-003/004/006/008 PI/CEMS projection, integration freshness/degraded/coverage dan acceptance belum diterima. Configurable API bases tidak membuktikan ingestion | Phase 1 current execution |
| M5 Derived Reliability Domain | PARTIAL: legacy KPI code dan evidence catalog tersedia; factual Maintenance Activity accepted | DOM-001..006/008 belum diterima sebagai NADI intelligence; DOM-007 lineage/failure definition tetap dibatasi. Health/risk/failure/PdM/recommendation tidak dibuka oleh legacy KPI | Phase 3–4; bukan syarat mengada-ada untuk factual Phase 0 |
| M6 API / UI Foundation | PARTIAL: read-only canonical API, AppShell, factual aggregates, paging/filter/error/accessibility evidence ada dalam PR #1 | API-003/004 workflow/AuthZ/concurrency, UI-004 integration status dan wider freshness/caching acceptance perlu pekerjaan/verification | Phase 0 factual scope COMPLETE; Phase 1–2 expansion |
| M7 Product Screens | PARTIAL: sembilan factual NADI routes accepted PR #1, `v0.1.0-rc.1`; Overview, Assets, Maintenance, FMEA, RCFA, Health, Overhaul, Data Trust | UI-103 PdM, UI-104 Recommendations, UI-105 Action Board sengaja belum exposed; Reports/Admin tetap scope/acceptance mendatang, bukan placeholder dianggap DONE | Phase 0 factual screens COMPLETE; Phase 2–4 later screens |
| M8 Hardening / Release | PARTIAL: factual RC freeze, recorded backend/web/type/build/route/contract/privacy QA; mapping timestamp fix PR #10; RC tag exists | OPS backup/restore, RPO/RTO, retention, soak, performance/security scan/UAT dan broader release acceptance NEEDS_REVIEW. No tracked GitHub workflow config at baseline | Phase-specific acceptance; full operational platform later |

### Rekonsiliasi ID dan klaim lama

- ARCH-002 / ING-007: consumer tidak memiliki credential sumber. Legacy memakai
  API collector; canonical Mart memakai approved local SELECT-only reader.
- M1 PLAT artefacts “ada” tidak sama dengan exit criteria runtime diterima.
  Jangan membuat ulang DB untuk mencapai cold-start checklist pada deployment existing.
- M3 IDN-001: mekanisme governance sudah merged; pilot data VERIFIED belum
  tersertifikasi. IDN-002 CEMS stack identity tidak dipaksa menjadi PI/Asset identity.
- M4 ING-001/002: Maximo legacy path implemented; Mart projection adalah jalur
  berbeda. PI/CEMS projection tetap pending di main, bukan source-access claim.
- M6–M7: tabel lama “seluruh UI blocked” superseded oleh factual V1 release.
  Domain baru/kolaborasi/prediktif tetap future scope.
- M8: PR #1 dan tag sudah ada; status release PR/tag pending pada snapshot lama
  tidak lagi berlaku. Operational sign-off/soak/restore tidak disimpulkan dari tag.

**NADI-PI-001 / PR #12: MERGED** (`main 3e981a3`).
**Current runtime checkpoint: NADI-PI-RUNTIME-001** — existing PI migration 004,
API compatibility, bounded technical source canary and single snapshot owner.
[Evidence](../../pi-collector/docs/nadi-pi-runtime-001.md) distinguishes reviewed
PI main image from new operator/Compose changes awaiting PR review.
[NADI-RUNTIME-002](../NADI-RUNTIME-002.md) reconciles actual Mart governance
schema/deployment before NADI-IDN-002 pilot mapping; then NADI-ING-PI-001 →
NADI-INTEGRATION-STATUS → NADI-PHASE-1-ACCEPTANCE. Phase 1 and full M0–M8
acceptance remain PARTIAL. NK/deployment `0c800da` is not bulk-merged.

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
| MXR-004 | P0 | M | Cursor boundary overlap + deterministic paging regression test — PARTIAL: bounded WO recency and tie/error regressions implemented; live scoped recent read verified. FIX-01 explicit retry-stable empty-cursor recovery implemented/tested; merged main deployed and production recovery/routine/Mart/NADI acceptance verified on 2026-10-07; moving-source deterministic paging and global concurrency guarantees remain open. Other Maximo groups remain parked under the WO-only acceptance profile. See [implementation](../../maximo-collector/docs/maximo-wo-recency-001.md) and [operational evidence](../../maximo-collector/docs/maximo-wo-recency-002.md). |
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

## Historical snapshot — Status eksekusi 20 Agustus 2026

> HISTORICAL: tabel dan hasil test di bawah dipertahankan sebagai audit trail.
> Gunakan rekonsiliasi di atas untuk status aktif; angka test/schema bukan target permanen.


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
