# 06 — Operasional, Keamanan, dan Pengujian

## Safety invariants

Perubahan arsitektur tidak boleh mengubah batas berikut:

| Source | Invariant | Test wajib |
|---|---|---|
| Maximo | business request hanya GET/HEAD/OPTIONS; login POST hanya `/j_security_check` | unit guard + integration fake transport |
| Maximo | site/org/unit/prefix scope tetap dipaksa | query construction + negative config test |
| Maximo | rate ≥1 detik dan body ≤1 MiB | boundary tests |
| PI | GET/HEAD/OPTIONS only; verified WebId registry only | method guard + registry filter tests |
| PI | rate limiter/circuit breaker/off-hours tetap aktif | clock/fake client tests |
| CEMS | hanya FC03/FC04; register cap/safety floors | guard + protocol fake tests |
| CEMS | tidak ada outbound KLHK/CEMS push | dependency/network allowlist + code scan |
| Semua | secret tidak di source/image/log/database cockpit | secret scan + image inspection + log test |

Compose worker/API tidak boleh mem-bypass class guard dengan memanggil underlying
library secara langsung.

## Security architecture

### Trust boundaries

1. Source network: hanya worker collector yang memerlukan akses.
2. Collector data/API network: internal; write hanya ke DB milik sendiri.
3. Cockpit API: satu-satunya browser backend.
4. Cockpit web/user boundary: session/auth, CSRF, RBAC, input validation.
5. Administration boundary: rule/model/mapping approval dan audit.

### AuthN/AuthZ

Untuk read-only technical APIs antar-container, gunakan internal network plus
service credential/mTLS sesuai infrastructure standard. Jangan expose manual collect
trigger ke public tanpa auth.

Role awal cockpit:

| Role | Hak minimum |
|---|---|
| Viewer | membaca dashboard/report |
| Reliability Engineer | review finding, membuat/edit recommendation |
| Assignee | update progress recommendation yang ditugaskan |
| Manager | maintenance/budget/RCA/risk decision |
| Administrator | taxonomy/config/user role; tidak dapat mengubah source evidence |
| Service Account | ingestion/projection only |

Gunakan deny-by-default, object/action authorization di backend, dan audit untuk
setiap mutation. UI hiding bukan authorization.

### Secret dan container

- secret runtime dari secret store/Docker secrets;
- filesystem container read-only bila memungkinkan, temp path eksplisit;
- non-root UID/GID, drop Linux capabilities, no privileged mode;
- dependency dan base image dipin, dipindai, dan diupdate terjadwal;
- database user per service dengan privilege minimum;
- TLS untuk user-facing traffic dan source connection sesuai kemampuan source;
- sanitized structured log; Authorization, cookie, password, WebId detail sensitif,
  raw personal values, dan DB DSN tidak dicetak;
- backup dienkripsi dan access/restore diaudit.

## Observability model

### Structured logs

Field minimum:

```text
timestamp, level, service, role, version, environment
run_id/correlation_id, source, operation, scope
started_at, finished_at, duration_ms
rows_seen, rows_written, rows_skipped, errors
watermark, freshness_seconds, retry_count, outcome
```

Error log hanya memuat error class dan pesan yang disanitasi; response payload source
tidak dicetak.

### Metrics

Per collector:

- run success/failure/abort total;
- last success timestamp dan cycle duration;
- rows/request/error/deactivation/transform failure;
- watermark lag/data freshness;
- active/verified/unmapped registry coverage;
- worker heartbeat dan lock contention;
- rate limiter wait/circuit breaker state;
- DB connection/query latency dan storage growth.

Cockpit:

- projection lag per source/resource;
- finding/recommendation count by severity/status/age;
- health/risk recompute duration/failure;
- API rate/error/latency by route;
- dashboard partial/stale responses;
- auth failure dan forbidden action;
- web vitals serta frontend error rate.

### Alert proposal

Threshold final mengikuti benchmark. Baseline staging:

- CEMS: tidak ada successful poll >2–3 cadence atau aggregate window tertinggal >2
  window;
- PI: last successful tier cycle melewati 2× target freshness;
- Maximo operational: no successful sync melewati 2× schedule;
- projection cockpit: lag melewati satu source cycle tambahan;
- error ratio/row skip meningkat dari baseline;
- disk/volume, connection saturation, backup/restore failure;
- repeated auth/guard violation selalu high priority.

Satu source down membuat platform `degraded`, bukan mematikan seluruh dashboard.

## Data lifecycle

### CEMS

Karena estimasi raw sekitar 259.200 row/hari pada registry 15 parameter/poll 5 detik:

- ukur row size/index growth pada staging;
- partition/hypertable per time interval bila diperlukan;
- retention raw ditentukan bisnis/compliance;
- 5-minute aggregates disimpan lebih lama;
- purge memakai policy/migration teruji, bukan delete manual tanpa batas;
- archive/restore sample diverifikasi sebelum retention diaktifkan.

### PI

- `pi_snapshot` adalah latest-value upsert dan kecil;
- `pi_timeseries` memakai TimescaleDB chunk/index/compression/retention;
- bedakan raw recorded, interpolated, dan snapshot-derived provenance;
- backfill progress tidak ikut terhapus oleh retention tanpa desain eksplisit;
- large query mempunyai time range/row limit.

### Maximo dan cockpit

- transactional data/upsert dipertahankan sesuai audit kebutuhan;
- collect run/audit event retention lebih panjang daripada verbose log;
- recommendation/decision audit append-only;
- report export sementara mempunyai expiry.

## Backup dan disaster recovery

Tentukan RPO/RTO per database sebelum production. Minimal:

1. scheduled logical/physical backup sesuai ukuran;
2. volume snapshot bukan satu-satunya backup;
3. encrypted off-host copy;
4. restore drill berkala ke isolated environment;
5. verifikasi schema version, row counts, cursor, Timescale extension/hypertable,
   recommendation audit chain;
6. runbook kehilangan satu DB tanpa menghapus volume lain;
7. collector dapat melanjutkan dari cursor atau bounded backfill setelah restore.

Jangan menguji restore langsung ke production.

## Test pyramid

### Unit tests per subproyek

- safety guard dan config floors;
- mapping/coercion/unit/timestamp;
- scheduler decision, lock, retry, signal shutdown;
- cursor/watermark boundary dan idempotency;
- finding/risk/health formulas termasuk missing/stale/bad quality;
- recommendation state machine/RBAC;
- CEMS normalization/aggregation dan PI backfill safety;
- frontend formatter/state reducers/component accessibility.

Semua source client memakai fake transport; unit test tidak membutuhkan network/DB.

### Contract tests

- validate seluruh schema Draft 2020-12;
- collector serializer output valid terhadap contract;
- cockpit parser menerima contract version saat ini;
- backward-compatible fixture dari release sebelumnya;
- unknown extension tetap di `sources.*` dan tidak bocor ke core;
- OpenAPI response schema dan pagination/filter/error envelope;
- time zone/unit/null semantics.

### Database integration tests

Jalankan ephemeral PostgreSQL/TimescaleDB container:

- migration fresh dan upgrade dari previous version;
- unique/idempotent upsert dan cursor transaction;
- concurrent worker/manual trigger lock;
- CEMS window catch-up dan PI hypertable query;
- query/index plan pada representative data volume;
- retention policy tidak menghapus data/cursor yang salah.

### Compose end-to-end tests

Fake source service/simulator digunakan agar tidak menyentuh production:

1. start root Compose dari volume kosong;
2. init/registry sehat;
3. fake Maximo mengubah status WO → delta sync → cockpit projection → UI berubah;
4. fake PI stream menghasilkan trend/quality gap → finding/health berubah;
5. fake Modbus menghasilkan reading → aggregate → integration/environment view;
6. restart setiap worker di tengah cycle → resume tanpa duplicate/loss;
7. matikan satu source/API/DB → platform partial/stale/degraded yang benar;
8. recovery menghapus stale alert setelah successful cycle;
9. auth/RBAC menolak mutation yang tidak berhak;
10. no outbound write assertion pada capture/fake server.

### Frontend visual dan interaction tests

- component stories/fixtures untuk semua state;
- screenshot/visual regression pada desktop/tablet/mobile;
- filter/query URL, pagination, drilldown, back navigation;
- metric card vs table count consistency;
- keyboard/focus/accessible name/contrast/chart alternative;
- locale/timezone/large number/long label/null/partial data;
- concept comparison tidak memaksa pixel-perfect bila mengorbankan responsive atau
  accessibility.

### Performance dan soak

- seed representative equipment/WO/findings/recommendations;
- CEMS volume setara retention target;
- PI chart range dan aggregation limits;
- dashboard API p50/p95/p99 dan DB query plan;
- 24–72 jam semua worker bersama;
- memory/connection/file descriptor growth;
- cycle overrun behavior dan lock queue;
- web bundle/route performance.

## CI/CD gates

Urutan pipeline:

1. format/lint/type check;
2. hermetic unit tests per subproject;
3. schema + cross-service contract tests;
4. build images dan scan secret/vulnerability/SBOM;
5. database migration integration tests;
6. Compose smoke/E2E dengan fake sources;
7. frontend build/accessibility/visual checks;
8. signed/versioned image publish;
9. staging deploy + migration + smoke;
10. manual approval untuk production.

Tidak ada CI yang menjalankan production discovery atau membutuhkan production
credential.

## Rollout strategy

1. **Shadow platform:** root Compose berjalan dengan collector DB sendiri; existing
   process tetap menjadi pembanding, tanpa duplicate source concurrency.
2. **Collector cutover:** satu per satu pindahkan scheduler ke Compose dan matikan
   scheduler lama setelah cursor/row parity.
3. **Cockpit projection:** aktifkan collector-only path, bandingkan equipment/WO/KPI.
4. **Read-only UI pilot:** Executive/Asset/Integration untuk kelompok user kecil.
5. **PdM pilot:** hanya verified identity + approved P0 methods/rules.
6. **Workflow pilot:** Recommendations/Action Board setelah auth/RBAC/audit.
7. **Full release:** reports/admin dan operational handover.

Setiap tahap memiliki rollback image/config dan tidak melakukan destructive schema
change pada release yang sama dengan feature cutover.

## Release checklist

- [ ] Source guards, scope, rate limits, response/register caps lulus.
- [ ] Tidak ada credential source di cockpit/web/image/log.
- [ ] Semua service sehat dari cold start dan restart.
- [ ] Registry/contract/migration version tercatat.
- [ ] Cursor parity dan no-loss pagination terbukti.
- [ ] Identity coverage dan unresolved mappings terlihat.
- [ ] Formula/model/rule mendapat approval dan version.
- [ ] UI tidak berisi hardcoded business metrics.
- [ ] Stale/partial/error behavior diuji.
- [ ] Auth/RBAC/audit mutation diuji.
- [ ] Backup **dan restore** diuji.
- [ ] Retention dan storage forecast disetujui.
- [ ] Monitoring/alert/runbook/on-call owner tersedia.
- [ ] Rollback drill selesai.

## Status eksekusi — 20 Agustus 2026

| Status | Butir | Bukti / batasan |
|---|---|---|
| DONE | Safety boundary dipertahankan | Scheduler baru memanggil service read-only yang sudah ada; tidak ada method Maximo mutasi atau Modbus write ditambahkan. Cockpit worker hanya mengakses API collector. |
| DONE | Container hygiene dasar | Semua image aplikasi menggunakan user non-root; `.dockerignore` mengecualikan `.env`, venv, log, dan output web. DB tidak dipublish pada baseline Compose. |
| DONE | Test baseline | Maximo 41, CEMS 82, Cockpit 37 test non-DB, serta 19 JSON Schema lulus. Compose config tervalidasi tanpa menjalankan source. |
| PARTIAL | Test Cockpit penuh | Dua smoke test perlu diperbaiki agar benar-benar memakai SQLite/in-memory seperti dokumennya; database integration dan Compose E2E belum dijalankan. |
| BLOCKED | Metrics/alert, backup-restore, retention, security scan, soak/UAT, RBAC, dan rollback drill | Memerlukan staging, secret/route terotorisasi, storage policy/RPO-RTO, identity provider, dan pemilik on-call. Semua release checklist tetap belum dicentang agar tidak memberi kesan siap produksi. |

### NET-001 — status operasional collector lokal

- **COLLECTOR API VERIFIED:** Maximo, PI, dan CEMS health/stats endpoint HTTP 200
  dari shell agent di LAN; metadata response tidak memuat credential.
- **DATA COLLECTION VERIFIED:** PI scheduler aktif pada 433 stream verified/ok;
  CEMS run poll terakhir 0 error; Maximo memiliki data equipment/WO dan run sukses
  historis.
- **STALE_COLLECTOR:** Maximo tidak memiliki worker yang terdeteksi dan run
  terakhir stale. Tidak ada worker baru dijalankan oleh task ini agar source
  polling tidak terduplikasi; tindak lanjut harus memakai worker existing/owner
  credential, bukan inisialisasi database baru.
- **REMAINING BLOCKERS UNCHANGED:** formula/risk, identity mapping, AuthZ, UAT,
  backup/restore, retention, dan release tetap di luar NET-001.
