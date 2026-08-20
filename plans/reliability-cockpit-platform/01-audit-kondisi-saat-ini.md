# 01 — Audit Kondisi Saat Ini dan Inventaris Data

## Metode dan batas audit

Audit ini membaca kode, konfigurasi contoh, schema, registry, migration, API, dan
frontend yang ada di repositori pada 20 Agustus 2026. Audit tidak menjalankan
discovery ke sistem produksi dan tidak menganggap contoh UI sebagai data nyata.

Sumber utama:

- [Maximo collector](../../maximo-collector/README.md)
- [PI collector](../../pi-collector/README.md)
- [CEMS collector](../../cems-collector/README.md)
- [Cockpit](../../reliability-cockpit/README.md)
- [Reliability data contracts](../../reliability-data-contracts/README.md)

## Ringkasan runtime saat ini

| Komponen | Cara berjalan saat ini | Database | Cadence aktual | API lokal |
|---|---|---|---|---|
| Maximo collector | `mxcollector sync` one-shot dan `serve` terpisah | PostgreSQL `:5434` | Belum ada daemon/scheduler | `:8002` |
| PI collector | `run` daemon, `serve` terpisah, backfill manual | TimescaleDB `:5433` | Default sleep 300 detik setelah cycle | `:8001` |
| CEMS collector | `collect` daemon; `aggregate` one-shot; `serve` terpisah | PostgreSQL `:5435` | Poll default 5 detik; agregasi harus dipicu | `:8003` |
| Reliability Cockpit | `sync`, `kpi`, dan `serve` masih dijalankan manual | PostgreSQL `:5432` | Belum ada projection/KPI worker | `:8000` |
| Cockpit web | Next.js dev/start terpisah | — | Request on demand | `:3000` |

Keempat Compose file yang ada sekarang hanya menyalakan database masing-masing.
Belum ada Dockerfile aplikasi dan belum ada root Compose yang menyatukan service.

## Inventaris data Maximo

### Data yang sudah tersedia

| Resource | Kunci/watermark | Data yang relevan untuk cockpit |
|---|---|---|
| Equipment (`mxapiasset`) | `assetnum`; `changedate` | identitas aset, unit, lokasi, class, status/running, hierarchy, criticality flags, manufacturer/vendor, cost, downtime total |
| Work Order (`mxwodetail`) | `wonum`; `changedate` | status/type/class, asset, priority, jadwal/target, downtime, supervisor/lead, cost dan labor aktual |
| Service Request (`mxapisr`) | `ticketid`; `changedate` | status, asset, target/actual time, priority, pelapor, risk area environment/process/human/reputation |
| Person (`mxperson`) | `personid`; `statusdate` | display name, status, org location |
| Item (`mxitem`) | `itemnum`; `statusdate` | status, type, units, rotating/inspection flags, meter reference |
| Labor (`mxapilabor`) | `laborcode`; tanpa watermark | person link, status, work site, availability, reported hours |
| Status history lokal | append-only observation | perubahan status/running equipment yang diamati collector |
| Collect run/cursor | per object | last run, mode, row count, error, watermark |

### Kekuatan

- Delta sync sudah memakai `changedate`/`statusdate` dan upsert idempotent.
- Scope BSR/IP, prefix WO BSR, unit equipment CS01, rate limit 1 detik, dan cap
  respons 1 MiB sudah dipaksa di kode.
- API sudah memiliki `changed_since`, `changed_until`, `offset`, `limit`, filter,
  pencarian, `/stats`, `/collect-runs`, dan `/sync/status`.
- API memisahkan field core dan `sources.maximo`.

### Keterbatasan data

- Failure master, PM schedule, location master, meter, dan job plan masih tidak dapat
  dibaca oleh credential saat ini. Failure/PM yang ditampilkan harus diberi label
  derived dari WO, bukan dianggap data master lengkap.
- Labor tidak memiliki watermark sehingga full sync tidak cocok dijalankan sering.
- Tidak ada event subscription yang terverifikasi. Perubahan WO hanya dapat diketahui
  dengan polling delta aman.

## Inventaris data PI

Registry [BSR1 parameters](../../pi-knowledge/mappings/bsr1-parameters.yaml)
mencatat:

- 541 atribut ditemukan;
- 433 atribut `status=verified` dan `stream_status=ok` dapat dikoleksi;
- 98 stream `gone`, 10 error;
- 150 atribut sudah mempunyai semantic mapping, sisanya banyak yang masih
  `unclassified`.

Distribusi kelompok equipment di registry:

| Kelompok | Jumlah atribut |
|---|---:|
| BSR1.BFPT | 1 |
| BSR1.Boiler Temp | 187 |
| BSR1.Coal Feeder | 73 |
| BSR1.Generator | 12 |
| BSR1.NPHR | 100 |
| BSR1.Pulverizer | 98 |
| BSR1.Turbine | 70 |
| **Total** | **541** |

Kategori semantik yang sudah tampak antara lain bearing temperature, current,
temperature, turbine vibration, speed, power output, coal/steam/spray flow,
pressure, efficiency, dan heat rate. Registry tetap menjadi sumber WebId tunggal.

### Tabel/API yang tersedia

| Data | Penyimpanan | Kegunaan |
|---|---|---|
| Attribute registry | `pi_attribute_registry` | catalog parameter, equipment group, parameter class, unit, position, WebId/AF path |
| Latest snapshot | `pi_snapshot` | nilai terbaru, quality, unit, source timestamp, collected timestamp |
| Historical series | `pi_timeseries` hypertable | trend, feature ML, interpolated/raw history |
| Backfill progress/cursor | local tables | resume idempotent dan delta progress |
| Collect run | `pi_collect_run` | jumlah atribut/row/error/request dan abort reason |

API menyediakan attributes, snapshots, time-series, heatmap, activity, schedule, dan
stats. Data digital/non-numeric disimpan sebagai `value=null` dan `value_good=false`.

### Constraint throughput yang harus masuk desain

Snapshot sekarang melakukan satu `GET /streams/{WebId}/value` per atribut. Dengan
433 atribut dan rate limit minimum 1 request/detik, batas bawah cycle adalah 433
detik (7 menit 13 detik), belum termasuk latency. Komentar runtime mencatat cycle
normal sekitar 9 menit. Karena daemon tidur 300 detik **setelah** cycle selesai,
"setiap 5 menit" untuk seluruh 433 atribut belum realistis.

PI knowledge juga mencatat `/streamsets/{webId}/value` mengembalikan item kosong pada
instance ini dan `/batch` membutuhkan POST sehingga dilarang. Karena itu rencana
tidak boleh mengasumsikan batching atau parallel request. Solusi aman:

- satu worker egress PI;
- tier parameter yang disetujui engineering (misalnya critical/standard);
- SLO freshness mengikuti hasil benchmark aktual;
- historical raw backfill tetap off-hours;
- jangan menjalankan beberapa PI worker yang masing-masing memiliki rate limiter
  sendiri karena total rate ke server tidak lagi terkontrol.

## Inventaris data CEMS

Registry [CEMS parameters](../../cems-collector/registry/cems-parameters.yaml) pada
working tree saat audit berisi 15 parameter: SO2, NOx, O2, PM, Hg, CO2,
`Laju_alir`, NO, NO2, CO, Flow, Opacity, Temp, Humidity, dan Pressure. Semua entry
masih memakai status knowledge `documented`, walaupun dokumen subproyek juga
mencatat hasil pembandingan produksi untuk sejumlah transformasi. Status dan jumlah
registry harus direkonsiliasi sebelum cockpit menganggapnya verified; README/AGENTS
yang masih menyebut 14 parameter perlu dibuat konsisten.

| Data | Penyimpanan | Kegunaan |
|---|---|---|
| Stack | `stack` | status stack dan maintenance window |
| Parameter | `parameter` | code, unit, threshold, adjustment, status/collect flag, `sources.cems` |
| Realtime reading | `reading_realtime` | raw, normalized, correction, final, transform status, observed time |
| 5-minute aggregate | `reading_5min` | average/min/max/sample count/window |
| Cursor/run | local tables | watermark agregasi dan observability cycle |

API menyediakan latest, raw readings, 5-minute readings, registry, stats, dan runs.
Collector hanya memakai FC03/FC04 dan tidak mempunyai outbound push.

### Estimasi volume

Dengan 15 parameter dan poll 5 detik:

```text
15 × 12 poll/menit × 60 × 24 = 259.200 row realtime/hari
                              ≈ 94,6 juta row/tahun
```

Angka ini membuat retention, partitioning/index, compression/downsampling, dan
backup menjadi bagian fase awal—bukan optimasi belakangan. Agregat 5 menit hanya
sekitar 4.320 row/hari untuk 15 parameter dan cocok untuk dashboard jangka panjang.

## Kondisi Reliability Cockpit saat ini

Cockpit menyimpan equipment, WO, SR, person, item, labor, empat KPI, dan sync cursor.
API publik baru mencakup:

- `/equipment` dan `/equipment/{id}`;
- `/work-orders`;
- satu KPI per equipment/metric;
- satu sync status per object;
- `/health` yang baru memeriksa proses, belum dependency/freshness.

Frontend baru berupa list equipment, detail equipment + KPI + WO, dan list WO.
Belum ada application shell, chart, server-side filtering, finding, recommendation,
risk, action board, integration monitoring, report, administration, auth, atau audit
trail seperti konsep.

### Integrasi Maximo yang masih transisional

Kode sudah mempunyai `CollectorClient` dan `SyncService` pull dari API Maximo
collector. Namun CLI cockpit dan beberapa dokumen masih membangun `OslcClient`
langsung dan memakai kontrak service lama. Sebelum fitur baru, satu jalur produksi
harus dipilih dan diuji: **cockpit → maximo-collector API**. Direct Maximo adapter di
cockpit kemudian hanya dipertahankan sementara untuk migrasi/test atau dihapus
setelah parity tercapai.

Pull client saat ini juga mengambil satu page. Full data di atas limit harus memakai
pagination sampai habis, deterministic ordering, overlap watermark, dan dedup agar
tidak kehilangan row.

## Ketersediaan data terhadap lima konsep

Legenda: **Ada** = dapat dipakai sekarang; **Derived** = perlu rule/formula;
**Baru** = perlu domain/workflow baru; **Gap** = sumber/identity belum tersedia.

| Kebutuhan konsep | Maximo | PI | CEMS | Status implementasi |
|---|---|---|---|---|
| Asset master/detail/status | utama | equipment group saja | stack saja | Ada dari Maximo |
| WO backlog/open/overdue | utama | — | — | Derived dari status/target WO |
| Last failure/repeat failure | WO terbatas | signal context | — | Derived; failure master gap |
| MTBF/MTTR/availability/PM compliance | WO/downtime | running context opsional | — | Sebagian sudah ada, kualitas terbatas |
| Condition trend | — | utama | emission/environment trend | Ada di collector, belum di cockpit |
| PdM method dan severity | WO context | measurement data | bukan PdM default | Baru: taxonomy + threshold/rules |
| Condition finding | link WO/SR | signal/anomaly | compliance signal | Baru: finding engine/workflow |
| Health score/criticality/risk score | asset/WO/priority | condition severity | environmental risk opsional | Derived, formula belum disepakati |
| Recommendation lifecycle | WO reference/person | evidence | evidence opsional | Baru |
| PIC | person/labor/supervisor | — | — | Ada sebagai kandidat; assignment workflow baru |
| Maintenance window | schedule WO terbatas | condition driver | maintenance state | Derived + workflow baru |
| Budget decision | cost WO/equipment | — | — | Baru |
| RCA required | WO/failure pattern | recurring signal | — | Derived + workflow baru |
| Risk acceptance | SR risk areas | condition severity | environmental exceedance | Baru |
| Collector health/freshness | run/cursor | run/cursor/activity | run/cursor | Ada per collector, perlu agregasi |

## Gap prioritas

1. Belum ada root Compose dan image aplikasi.
2. Maximo dan CEMS belum mempunyai scheduler lengkap; PI scheduling belum sesuai
   throughput seluruh registry.
3. Tidak ada lock lintas API/worker; tombol trigger dapat menabrak daemon aktif.
4. Jalur cockpit ke Maximo collector belum selesai dan dokumentasi masih bercabang.
5. Tidak ada identity mapping yang tervalidasi dari Maximo `assetnum` ke PI equipment/
   attribute; CEMS bersifat stack-level dan tidak boleh otomatis dianggap asset-level.
6. Tidak ada kontrak CEMS pada `reliability-data-contracts`.
7. Finding, recommendation, action/decision, risk, health snapshot, dan provenance
   belum mempunyai kontrak, tabel, service, atau API.
8. Formula visual pada konsep belum mempunyai definisi/owner/version.
9. Cockpit API belum menyediakan endpoint agregat dan pagination/filter yang
   dibutuhkan dashboard.
10. Frontend masih starter UI dan belum mempunyai design system/accessibility plan.
11. Retention dan storage lifecycle CEMS/PI belum dinyatakan.
12. Auth/RBAC/audit untuk workflow management belum ada.

