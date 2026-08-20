# 02 — Arsitektur Target dan Docker Compose

## Keputusan: satu Compose project, multi-container

Target deployment memakai root `compose.yaml`. Ini adalah Docker Compose project,
bukan Docker Swarm `docker stack deploy`, dan bukan satu container berisi semua
proses.

```text
                         ┌──────────────────────────────┐
                         │ reliability-cockpit-web      │ :3000
                         └──────────────┬───────────────┘
                                        │ internal HTTP
                         ┌──────────────▼───────────────┐
                         │ reliability-cockpit-api      │ :8000
                         │ + projection/KPI worker      │
                         └───────┬────────┬────────┬─────┘
                                 │        │        │
                 ┌───────────────┘        │        └───────────────┐
                 ▼                        ▼                        ▼
          maximo-api :8002          pi-api :8001             cems-api :8003
                 ▲                        ▲                        ▲
          maximo-worker              pi-worker          cems-poller/aggregator
                 │                        │                        │
          maximo PostgreSQL          PI TimescaleDB          CEMS PostgreSQL
                 └──────────────── cockpit PostgreSQL ────────────┘
```

Garis terakhir hanya menunjukkan bahwa semuanya berada dalam satu deployment;
database **tidak** saling membaca atau menulis. Cockpit berkomunikasi dengan API.

## Image dan role

Satu image dibuat per codebase, lalu image yang sama dapat dipakai beberapa
container dengan command berbeda.

| Image | Container/role | Command target | Sifat proses |
|---|---|---|---|
| `reliability/maximo-collector` | `maximo-init` | migrate/init DB | one-shot |
| sama | `maximo-api` | `mxcollector serve --host 0.0.0.0` | long-running |
| sama | `maximo-worker` | scheduler delta sync | long-running, singleton |
| `reliability/pi-collector` | `pi-init` | init DB + load registry | one-shot |
| sama | `pi-api` | `picollector serve --host 0.0.0.0` | long-running |
| sama | `pi-worker` | orchestrated snapshot/history schedule | long-running, singleton |
| sama | `pi-backfill` | manual recorded backfill | Compose profile `backfill` |
| `reliability/cems-collector` | `cems-init` | init DB + load registry | one-shot |
| sama | `cems-api` | `cemscollector serve --host 0.0.0.0` | long-running |
| sama | `cems-poller` | `cemscollector collect` | long-running, singleton |
| sama | `cems-aggregator` | aggregation daemon | long-running, singleton |
| `reliability/cockpit-api` | `cockpit-init` | migration/init DB | one-shot |
| sama | `cockpit-api` | `cockpit serve --host 0.0.0.0` | long-running |
| sama | `cockpit-worker` | pull projections + derive KPI/finding | long-running, singleton |
| `reliability/cockpit-web` | `cockpit-web` | `next start` | long-running |

`*-init` harus idempotent. Untuk release awal, command dapat membungkus `create_all`
yang ada; sebelum perubahan schema domain dimulai, pindahkan ke migration versioned
agar upgrade/rollback dapat diaudit.

## Database target

### Baseline yang direkomendasikan

| Service | Engine | Database/volume | Alasan isolasi |
|---|---|---|---|
| `maximo-db` | PostgreSQL 16 pinned | `maximo_collector_data` | transactional sync, lifecycle sendiri |
| `pi-db` | TimescaleDB PG16 versi pinned | `pi_collector_data` | hypertable/time-series |
| `cems-db` | PostgreSQL 16 pinned | `cems_collector_data` | ingest frekuensi tinggi dan retention sendiri |
| `cockpit-db` | PostgreSQL 16 pinned | `cockpit_data` | read model dan workflow aplikasi |

Database hanya menggunakan `expose: 5432` pada network internal. Mapping host port
5432–5435 dipindahkan ke Compose override/profile development, bukan baseline
production.

### Alternatif yang ditunda

Maximo, CEMS, dan cockpit secara teknis dapat memakai satu PostgreSQL server dengan
database/user terpisah. Jangan lakukan pada fase pertama: penghematan container kecil,
sedangkan blast radius, tuning, backup/restore, dan contention menjadi lebih rumit.
PI tetap membutuhkan TimescaleDB. Konsolidasi hanya dipertimbangkan setelah volume dan
operasional terukur.

## File yang perlu dibuat

```text
compose.yaml                              # root production-like stack
compose.dev.yaml                          # port bind, hot reload, bind mount opsional
.env.platform.example                    # non-secret defaults dan daftar secret key
.dockerignore                             # root +/atau per app
maximo-collector/Dockerfile
pi-collector/Dockerfile
cems-collector/Dockerfile
reliability-cockpit/Dockerfile
reliability-cockpit/web/Dockerfile
deploy/compose/README.md                  # runbook
deploy/compose/healthcheck/               # hanya bila command app belum cukup
```

Dockerfile Python memakai base version pinned, non-root user, wheel/install layer,
dan tidak menyalin `.env`, test cache, `.venv`, knowledge response samples, atau
credential. Web memakai multi-stage build dan `next start`.

## Dependency dan startup ordering

Urutan boot:

1. database mencapai health `pg_isready`;
2. init/migration service selesai sukses;
3. registry PI/CEMS dimuat idempotent;
4. worker dan API collector dimulai;
5. cockpit DB/init dimulai;
6. cockpit projection worker menunggu collector API ready;
7. cockpit API dan web ready.

Gunakan `depends_on.condition` untuk DB health dan `service_completed_successfully`
untuk init service, tetapi setiap proses tetap harus retry dependency secara bounded.
Compose ordering bukan pengganti retry/reconnect.

## Scheduling yang dituju

Angka berikut adalah default proposal untuk staging. Jadwal production dikunci setelah
benchmark dan persetujuan engineering; semua schedule harus dapat diubah melalui env
dengan safety floor tetap aktif.

### CEMS

| Job | Cadence | Aturan |
|---|---|---|
| Poll realtime | default 5 detik | satu poller; FC03/FC04; current safety floor dipertahankan |
| Aggregate | setiap 1 menit memproses window 5 menit terakhir yang lengkap | cursor + unique upsert; aman saat restart |
| Retention/downsample | harian/off-hours | policy database, bukan delete loop ad-hoc |

Tambahkan command daemon native seperti `cemscollector run-aggregator`, bukan shell
`while true`. API trigger harus mengambil distributed/advisory lock yang sama agar
tidak beradu dengan worker.

### PI

Satu orchestrator PI harus mengatur seluruh request agar rate limit efektif secara
global. Proposal tier:

| Tier | Isi | Target freshness awal |
|---|---|---|
| P0 | subset PdM/operational kritis yang sudah semantically mapped dan disetujui | sekitar 5 menit bila benchmark memungkinkan |
| P1 | seluruh verified+stream-ok yang relevan | 15–30 menit, mengikuti durasi cycle aktual |
| Historical | interpolated/recorded | scheduled terkontrol; recorded full hanya off-hours |

Registry perlu field konfigurasi operasional terpisah, misalnya `collection_tier` dan
`poll_interval_seconds`; jangan memakai `status` knowledge untuk scheduling. Daftar P0
tidak boleh dibuat dengan tebakan string—harus disetujui reliability engineer dan
ditest terhadap registry verified.

Jangan menyalakan `snapshot` dan `recorded-delta` dalam dua container independen
sebelum ada global DB lease/rate limiter. Opsi aman adalah satu process yang
menjalankan kedua schedule secara serial atau satu task queue dengan concurrency=1.

### Maximo

| Kelompok | Object | Proposal cadence | Alasan |
|---|---|---|---|
| Operational | `mxwodetail`, `mxapisr` | 5 menit | perubahan status/progress/target |
| Asset status | `mxapiasset` | 30–60 menit atau setelah operational cycle tertentu | status/running/metadata lebih lambat |
| People/items | `mxperson`, `mxitem` | 6–24 jam | master data ber-watermark |
| Labor | `mxapilabor` | harian | tidak memiliki watermark; full sync |

Tambahkan `mxcollector run` dengan schedule per grup, jitter kecil, non-overlap lock,
graceful shutdown, dan run record. First full sync dijalankan eksplisit pada init/
bootstrap; daemon berikutnya hanya delta. Overlap watermark kecil diperbolehkan karena
upsert idempotent dan mengurangi risiko row pada timestamp boundary.

### Cockpit

| Job | Proposal cadence/trigger |
|---|---|
| Maximo projection pull | 1–5 menit setelah maximo cycle; cursor + pagination |
| PI/CEMS metadata/freshness pull | 1 menit |
| Condition feature/finding evaluation | setelah time window lengkap atau periodik |
| Health/risk projection | setelah perubahan input; fallback periodik |
| KPI 90 hari | incremental/harian dan on-demand rebuild terbatas |

Jangan membangun tight polling semua raw time-series ke cockpit. Untuk chart detail,
cockpit API melakukan server-side query ke collector API atau memakai cached
aggregation sesuai kebutuhan.

## Network dan port

Baseline:

- `source-net`: worker collector ke source network bila routing tersedia;
- `data-net`: setiap app ke database miliknya;
- `platform-net`: collector API ↔ cockpit API/worker ↔ web;
- hanya `cockpit-web:3000` yang dipublikasikan untuk pengguna;
- API dapat dipublikasikan hanya pada dev override atau melalui reverse proxy;
- database tidak dipublikasikan pada production.

Tambahkan reverse proxy/TLS hanya bila pola hosting memerlukannya. Jangan menaruh
credential source pada web container.

## Konfigurasi dan secret

- `.env.platform.example` hanya berisi placeholder dan default aman.
- Production memakai Docker secrets atau secret manager; `env_file` lokal tetap
  gitignored.
- Pisahkan credential Maximo/PI dari credential PostgreSQL.
- CEMS network address dikonfigurasi runtime; tidak ada write credential.
- Secret tidak dipakai sebagai build argument dan tidak dicetak oleh startup log.
- Semua timestamp disimpan UTC; scheduler berinterpretasi `Asia/Jakarta` untuk
  off-hours, lalu menyimpan hasil sebagai ISO-8601 ber-offset/UTC.

## Health dan restart

Health check tidak cukup hanya `{"status":"ok"}`. Target readiness:

- API process hidup dan query database sederhana berhasil;
- migration/schema version sesuai;
- worker heartbeat/freshness berada dalam batas atau health berstatus `degraded`;
- source tidak harus reachable agar API lokal tetap dapat menyajikan last-known data,
  tetapi status dependency harus terlihat;
- restart policy `unless-stopped` untuk long-running service, `no` untuk init/backfill;
- shutdown menangani SIGTERM dan menyelesaikan/rollback transaction aktif.

## Operasi harian yang dituju

```bash
# Start seluruh baseline
docker compose up -d

# Lihat kondisi semua service
docker compose ps

# Ikuti satu worker tanpa membanjiri terminal
docker compose logs -f --tail=200 maximo-worker

# Jalankan backfill PI secara eksplisit pada off-hours
docker compose --profile backfill run --rm pi-backfill \
  picollector backfill-recorded --start "2026-01-01T00:00:00Z" --end "*"

# Stop tanpa menghapus volume
docker compose down
```

Tidak ada default command yang menghapus volume. Penghapusan data harus menjadi
prosedur terpisah dengan backup dan konfirmasi eksplisit.

## Status eksekusi — 20 Agustus 2026

| Status | Butir | Bukti |
|---|---|---|
| DONE | Dua mode Compose tanpa duplicate polling | `compose.yaml` adalah **managed collectors** (DB/worker/API baru); `compose.external.yaml` adalah **external collectors** dan hanya menjalankan Cockpit terhadap API collector lama. |
| DONE | Image dan hygiene build | Dockerfile non-root serta `.dockerignore` dibuat untuk semua collector, backend Cockpit, dan web multi-stage. |
| DONE | Startup dependency/config wiring | One-shot `*-init`, healthcheck DB, volume persisten, network internal, `.env.platform.example`, `compose.dev.yaml`, external host gateway, dan runbook dibuat. CEMS memakai `CEMS_MODBUS_*`, PI memakai `PI_WEB_API_BASE_URL`, dan Maximo meneruskan login/token/cookie config. |
| DONE | Scheduling baseline | `mxcollector run`, `cemscollector run-aggregator`, dan `cockpit run` ditambahkan; Cockpit hanya memanggil API collector. |
| DONE | External collector discovery | NET-001 membuktikan API collector lama aktif di host `127.0.0.1:8001/8002/8003`; PI memiliki satu API + satu worker, CEMS satu API + satu worker. Tidak ada worker tambahan yang dinyalakan. |
| PARTIAL | Managed cold start | `docker compose config` tervalidasi dengan dummy env; cold start managed tidak dijalankan karena akan membuat worker baru terhadap source yang sudah dipoll. |
