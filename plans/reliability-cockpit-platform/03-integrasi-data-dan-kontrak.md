# 03 — Integrasi Data, Kontrak, dan Domain Cockpit

## Sasaran aliran data

Cockpit menjadi consumer dan decision-support application. Collector tetap menjadi
anti-corruption layer terhadap vendor/protocol.

```text
source systems
  │
  ├─ Maximo OSLC ─▶ maximo collector ─▶ contract API ─┐
  ├─ PI Web API ──▶ PI collector ─────▶ contract API ├─▶ cockpit ingestion
  └─ CEMS Modbus ─▶ CEMS collector ───▶ contract API ┘        │
                                                              ▼
                                                identity + derived services
                                                              │
                                    ┌─────────────────────────┼─────────────┐
                                    ▼                         ▼             ▼
                              read models               workflows      audit/lineage
                                    │                         │             │
                                    └──────────── Cockpit API/BFF ─────────┘
```

## Aturan ownership

| Data | System of record lokal | Consumer |
|---|---|---|
| Maximo contract copy | Maximo collector DB | Cockpit ingestion/API |
| PI registry, snapshot, raw/interpolated series | PI collector DB | Cockpit feature/query service |
| CEMS realtime dan 5-minute aggregates | CEMS collector DB | Cockpit environment/integration view |
| Equipment projection, KPI, health/risk snapshot | Cockpit DB | Cockpit API/web |
| Finding/recommendation/action workflow | Cockpit DB | Cockpit API/web |
| Vendor identifiers | `sources.*` block | adapter/lineage only |

Tidak ada cross-database foreign key dan tidak ada collector yang menulis database
collector lain.

## Fase pertama: selesaikan seam Maximo collector

1. Ubah CLI/runtime cockpit agar membuat `CollectorClient`, bukan `OslcClient`.
2. Gunakan satu `SyncService` pull dari Maximo collector API.
3. Tambahkan config `MAXIMO_COLLECTOR_API_BASE` dan timeout/retry bounded.
4. Implementasikan pagination sampai page kosong/total selesai:
   - deterministic sort oleh change timestamp + primary key;
   - `limit` bounded dan `offset`/cursor;
   - overlap kecil pada watermark;
   - dedup berdasarkan contract ID dan source change time;
   - cursor hanya maju setelah seluruh page sukses.
5. Tambahkan contract test yang menjalankan serializer Maximo collector → parser
   cockpit terhadap semua resource.
6. Hapus credential Maximo dari baseline cockpit Compose.
7. Perbarui README/adapter docs agar hanya satu production path yang dinyatakan.
8. Setelah parity dan rollback window selesai, hapus atau arsipkan direct source
   adapter cockpit agar arah data tidak kembali bercabang.

## Identity resolution lintas sumber

### Masalah

- Maximo memiliki stable `assetnum` dan hierarchy.
- PI registry saat ini memiliki nama kelompok seperti `BSR1.Turbine` dan position,
  bukan jaminan `assetnum` Maximo.
- CEMS berpusat pada `stack_id`/parameter; stack bukan otomatis equipment rotating.

Name matching fuzzy tidak boleh digunakan sebagai identity production.

### Kontrak/tabel yang dibutuhkan

`asset_source_link`:

| Field | Fungsi |
|---|---|
| `id` | stable UUID/internal key |
| `equipment_id` | FK logical ke Equipment.id cockpit |
| `source_system` | `maximo`, `pi`, atau `cems` |
| `source_entity_type` | asset, PI equipment group, attribute, stack, parameter |
| `source_entity_id` | vendor-neutral source-side key; raw identifier detail di `sources` |
| `relationship` | measures, belongs_to, represents, influences |
| `status` | unknown/documented/verified/deprecated |
| `valid_from`, `valid_to` | temporal validity |
| `verified_by`, `verified_at` | audit verification |
| `sources` | quarantined vendor identifiers |

Seed link dibuat dari mapping file reviewable di knowledge/contracts, bukan dari SQL
manual tanpa provenance. Cockpit hanya memakai link `verified` untuk scoring; link
documented boleh tampil sebagai coverage gap.

## Kontrak yang perlu ditambah

Semua schema memakai JSON Schema Draft 2020-12, core snake_case, timestamp ISO-8601,
dan perubahan backward-compatible bila mungkin.

### Identity dan observability

- `asset-source-link.schema.json`
- `collector-run.schema.json`
- `data-source-status.schema.json`

`data-source-status` minimal memuat source, component, last success/attempt,
watermark, freshness state, row/error count, lag, registry coverage, dan detail
read-only. Secret/error payload mentah tidak boleh ikut.

### CEMS

CEMS adalah environmental/emission data, bukan dipaksakan menjadi PdM condition
reading. Tambahkan:

- `emission-parameter.schema.json`
- `emission-reading.schema.json`
- `emission-aggregate.schema.json`
- `mappings/cems-to-contracts.md`

`sources.cems` menampung register, function/register type, byte/word order, dan stack
source. Core memuat code, name, unit, observed/window time, final/aggregate value,
quality/transformation status, dan knowledge status. Raw/normalized/correction value
boleh tetap di collector extension dan tidak wajib masuk read model cockpit.

### Reliability decision domain

- `condition-finding.schema.json`
- `recommendation.schema.json`
- `recommendation-event.schema.json`
- `risk-assessment.schema.json`
- `asset-health-snapshot.schema.json`
- `maintenance-decision.schema.json` bila Action Board memerlukan budget/window/risk
  acceptance sebagai workflow formal.

Schema harus memuat provenance berikut:

- `source_type` dan references ke measurement/WO/SR/report;
- `rule_or_model_id` dan `rule_or_model_version` untuk hasil otomatis;
- `observed_at`, `detected_at`, `computed_at`, `valid_until`;
- quality/freshness/confidence;
- status lifecycle dan actor/time untuk perubahan manual;
- unit serta threshold yang dipakai;
- `sources.*` tanpa memindahkan vendor field ke core.

## Domain/tabel baru di Cockpit

| Tabel/read model | Kunci penting | Tujuan |
|---|---|---|
| `asset_source_link` | equipment + source entity | identity verified |
| `measurement_method` | method code/version | taxonomy Vibration, Thermography, MCSA, Tribology, DGA, CEMS, dll. |
| `condition_finding` | finding ID + equipment + detected time | severity, evidence, method, state, trend |
| `finding_evidence` | finding + source reference | PI/CEMS series window, WO/SR, report link |
| `recommendation` | recommendation ID | action text, impact, target, owner, status, WO reference |
| `recommendation_event` | recommendation + event time | append-only lifecycle/audit |
| `risk_assessment` | asset/finding + assessment time | likelihood, consequence, score, tolerance, residual risk |
| `asset_health_snapshot` | equipment + computed time + model version | health score/category dan input breakdown |
| `maintenance_decision` | decision ID | maintenance window, budget, RCA, risk acceptance |
| `source_projection_cursor` | source/resource | pull watermark/page recovery |
| `data_source_status` | source/component | integration status/freshness |

Gunakan migration versioned. Index minimum: equipment/time, status/target date,
severity/open, method/time, source reference, dan unique idempotency key.

## Finding generation

PI/CEMS menyediakan measurement; collector tidak boleh langsung menyatakan diagnosis
engineering tanpa rule yang disetujui. Pipeline:

1. resolve verified asset/parameter link;
2. query window time-series dari collector;
3. validasi unit, quality, completeness, dan freshness;
4. hitung feature (current value, slope, rolling mean/max, exceedance duration, dsb.);
5. evaluasi rule/model versioned;
6. upsert finding dengan idempotency key;
7. attach evidence, provenance, dan review status;
8. recalculate health/risk projection;
9. jangan overwrite keputusan manusia; catat event baru.

Rule awal dipisah menjadi:

- quality/freshness finding (data buruk/stale);
- threshold/trend finding yang telah disetujui engineering;
- maintenance correlation dari WO/SR;
- anomaly/ML sebagai fase lanjutan setelah baseline dan label valid tersedia.

Tidak boleh menurunkan severity hanya dari warna atau angka contoh pada gambar.

## Health dan risk model

### Health score

Health score 0–100 menjadi output model versioned, bukan kolom source. Input kandidat:

- severity/recency open condition findings;
- criticality equipment;
- overdue/high-priority WO;
- repeat corrective work/failure proxy;
- open/overdue recommendation;
- data quality/freshness penalty.

Bobot, decay, threshold Healthy/Warning/Critical, dan missing-data behavior harus
disetujui reliability engineering. UI selalu menampilkan `model_version`,
`computed_at`, category, serta data completeness. Missing data tidak boleh dianggap
healthy.

### Risk score

Gunakan dimensi eksplisit, misalnya likelihood × consequence/impact, dengan scale dan
normalisasi terdokumentasi. Service Request risk areas dan Maximo priority dapat
menjadi input, bukan otomatis nilai final. Simpan input breakdown agar score dapat
diaudit.

## Recommendation dan action lifecycle

State minimum:

```text
DRAFT → OPEN → IN_PROGRESS → CLOSED
           └──────────────▶ REJECTED
OPEN/IN_PROGRESS + target terlewati = OVERDUE (derived view, bukan state destruktif)
```

Setiap recommendation mengacu pada finding/asset, method, risk impact, target,
owner/PIC, dan optional existing WO reference. Perubahan status dicatat append-only.

Action Board dibentuk dari query/rule:

- **Needs Maintenance Window:** recommendation open dengan flag outage/window dan
  risk di atas threshold.
- **Needs Budget Decision:** estimated cost/benefit tersedia dan approval pending.
- **Repeat Failure — RCA Required:** repeat event dalam rolling period memenuhi rule
  RCA versioned.
- **Risk Acceptance Needed:** residual risk di atas tolerance dan belum ada decision
  yang valid.

Kategori tidak boleh dihitung dari string description bebas saja.

## API target Cockpit

### Dashboard/read models

| Endpoint | Isi |
|---|---|
| `GET /dashboard/executive` | cards, asset health distribution, top risk, attention summary, reliability/WO trend |
| `GET /assets` | paginated/filterable health list |
| `GET /assets/{id}/health` | detail, health/risk, PdM summary, WO summary, recommendations |
| `GET /pdm/summary` | asset/method/severity counts dan trend |
| `GET /pdm/findings` | server-side finding table |
| `GET /pdm/trends` | aggregated series by method/category |
| `GET /recommendations` | status/risk/owner/date/search filters |
| `GET /actions/summary` | empat attention category dan counts |
| `GET /actions` | actionable records/top risks/open critical findings |
| `GET /integrations/status` | collector/API/worker/DB freshness dan coverage |
| `GET /reports/*` | reproducible report datasets/exports |

Endpoint dashboard mengembalikan `as_of`, applied filters, definition/model version,
freshness, dan data-quality flags. Aggregation dilakukan server-side agar UI tidak
menarik ribuan raw row lalu menghitung sendiri.

### Workflow commands

Endpoint mutation hanya terhadap database cockpit dan harus memakai auth/RBAC,
optimistic concurrency, audit, validation, dan idempotency key:

- create/update/assign/transition recommendation;
- record budget/window/RCA/risk-acceptance decision;
- link existing WO reference;
- acknowledge/close finding bila policy mengizinkan.

Tidak ada endpoint untuk menulis Maximo, PI, atau PLC.

## API collector yang perlu diperkuat

- pagination metadata atau cursor yang konsisten;
- stable sort dan upper-bound watermark untuk snapshot pull;
- endpoint status dengan last success/attempt, duration, errors, next schedule;
- read-only contract version header/field;
- health readiness terpisah dari liveness;
- ETag/conditional GET untuk registry/master data bila berguna;
- query aggregation PI/CEMS agar cockpit tidak meminta raw points berlebihan;
- API-triggered collect dilindungi lock, RBAC/internal token, dan duplicate-run guard.

## Idempotency dan consistency

- Source rows: upsert oleh stable source key + source change timestamp.
- Time-series: unique `(attribute_id, timestamp)` atau source-specific equivalent.
- Finding: hash/rule key dari asset + method + rule/model version + detection window.
- Health snapshot: asset + model version + computation time/window.
- Recommendation event: append-only event ID; transition memakai expected version.
- Cursor baru disimpan setelah batch transaction selesai.
- UI menampilkan last-known data saat source down, tetapi diberi status stale/degraded.

## Data yang tidak boleh dipalsukan

- PIC dari avatar/nama contoh;
- ISO severity tanpa parameter/unit/threshold yang tepat;
- bearing defect/diagnosis dari satu nilai tanpa rule atau model;
- failure code ketika source memang nullable/forbidden;
- PdM method untuk atribut `unclassified`;
- hubungan stack CEMS ke motor/aset tanpa mapping verified;
- recommendation target/WO reference/approval yang belum pernah dibuat pengguna atau
  workflow.

