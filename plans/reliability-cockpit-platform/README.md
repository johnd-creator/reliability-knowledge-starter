# Rencana Integrasi Collector dan Reliability Cockpit

Status: **proposal implementasi**

Tanggal audit repositori: **20 Agustus 2026**

Ruang lingkup: `maximo-collector`, `pi-collector`, `cems-collector`,
`reliability-data-contracts`, dan `reliability-cockpit`.

## Tujuan

Rencana ini membawa repositori dari beberapa aplikasi yang dijalankan sendiri-sendiri
menjadi satu platform yang dapat dinyalakan dengan satu perintah, tanpa mencampur
tanggung jawab collector dan tanpa melemahkan batas read-only terhadap Maximo, PI,
atau PLC CEMS.

Target pengguna:

```bash
docker compose up -d
```

Perintah tersebut menyalakan database, worker collector, API collector, backend
cockpit, dan web cockpit dalam satu **Docker Compose project**.

## Keputusan arsitektur utama

### 1. Satu stack, bukan satu image untuk semua aplikasi

Istilah Docker yang tepat untuk kebutuhan ini adalah **satu Docker Compose stack
berisi beberapa service/container**. Tidak disarankan menggabungkan ketiga collector
dan cockpit ke dalam satu image atau satu container karena:

- PI, CEMS, dan Maximo mempunyai cadence, dependency, failure mode, serta kebijakan
  restart yang berbeda;
- satu proses yang macet tidak boleh menghentikan collector lain;
- PI memerlukan TimescaleDB, sedangkan komponen lain cukup memakai PostgreSQL;
- image per aplikasi tetap dapat dipakai ulang oleh beberapa role, misalnya image
  CEMS yang sama untuk `cems-api`, `cems-poller`, dan `cems-aggregator`;
- upgrade dan rollback dapat dilakukan per aplikasi.

Rekomendasi awal adalah empat database/volume terisolasi: Maximo, PI, CEMS, dan
cockpit. Database tidak dipublikasikan ke jaringan luar pada konfigurasi produksi.

### 2. Collector tetap menjadi pemilik data sumber

```text
Maximo ──read-only──▶ maximo-collector DB/API ──┐
PI     ──read-only──▶ pi-collector DB/API ──────┼──▶ cockpit projection/API ──▶ web
CEMS   ──read-only──▶ cems-collector DB/API ────┘
```

- Setiap collector hanya menulis ke database miliknya.
- Cockpit tidak membaca database collector secara langsung.
- Cockpit tidak lagi menghubungi Maximo/PI/PLC secara langsung pada runtime normal.
- Cockpit menarik kontrak vendor-neutral melalui API collector, menyimpan read model
  dan hasil turunan, lalu menyajikan API khusus produk.
- Raw PI/CEMS time-series tetap berada di collector; cockpit menyimpan metadata,
  ringkasan, finding, health score, dan recommendation yang diperlukan UI.

### 3. Cadence dibedakan menurut sifat sumber

- **CEMS:** polling terus-menerus (default 5 detik), agregasi 5 menit.
- **PI:** worker tunggal terjadwal; parameter kritis diprioritaskan dan semua akses
  tetap melewati rate limiter global. Full historical backfill hanya lewat profile
  manual/off-hours.
- **Maximo:** polling delta ringan untuk WO/SR; tidak melakukan full refresh terus-
  menerus. `changedate`/`statusdate` membuat cycle tanpa perubahan menjadi murah dan
  idempotent. Master data dan equipment memakai jadwal lebih jarang.

Maximo tidak dapat benar-benar "berjalan hanya ketika data berubah" tanpa mekanisme
event/webhook yang sudah diverifikasi. Dengan kemampuan yang tersedia saat ini,
polling delta berkala adalah opsi aman; event integration menjadi fase lanjutan bila
kemudian tersedia dan mendapat otorisasi.

### 4. Lima gambar adalah target pengalaman, bukan bukti ketersediaan data

Konsep UI menjadi acuan untuk:

1. Executive Overview (`konsep5.png`)
2. Asset Health Detail (`konsep4.png`)
3. PdM Center (`konsep3.png`)
4. Recommendations (`konsep2.png`)
5. Action Board (`konsep1.png`)

Angka, nama aset, tanggal, avatar, dan status pada gambar adalah contoh visual.
Implementasi tidak boleh meng-hardcode data tersebut. Setiap widget harus mempunyai
definisi metrik, provenance, timestamp, serta state loading/empty/error/stale.

## Urutan dokumen

1. [Audit kondisi saat ini dan inventaris data](01-audit-kondisi-saat-ini.md)
2. [Arsitektur target dan Docker Compose](02-arsitektur-target-docker-compose.md)
3. [Integrasi data, kontrak, dan domain cockpit](03-integrasi-data-dan-kontrak.md)
4. [Rencana produk dan UI Reliability Cockpit](04-rencana-produk-ui.md)
5. [Roadmap implementasi dan backlog](05-roadmap-implementasi.md)
6. [Operasional, keamanan, dan pengujian](06-operasional-keamanan-pengujian.md)

## Prinsip yang tidak boleh berubah

- Maximo business API hanya `GET`/`HEAD`/`OPTIONS`; satu-satunya POST yang
  dibolehkan adalah login yang sudah ditentukan di `maximo-collector`.
- PI hanya read-only; WebId/tag hanya berasal dari `pi-knowledge` berstatus
  `verified`.
- CEMS hanya FC03/FC04; tidak ada write/mask call dan tidak ada outbound push KLHK.
- Site Maximo tetap BSR, org IP, dan scope unit tetap tervalidasi.
- Identifier vendor tetap berada di `sources.maximo`, `sources.pi`, atau
  `sources.cems`.
- Cockpit tidak membuat atau memperbarui WO di Maximo. Recommendation hanya dapat
  menyimpan referensi WO yang sudah ada sampai ada komponen write-back terpisah dan
  otorisasi eksplisit.
- Secret hanya masuk melalui runtime environment/secret store, tidak di image,
  Compose file, log, database cockpit, atau source control.

## Definition of done tingkat platform

Platform dianggap mencapai target awal ketika:

- satu `docker compose up -d` menghasilkan semua service sehat dan restart-safe;
- ketiga collector berjalan bersamaan sesuai cadence masing-masing tanpa concurrent
  source calls yang tidak terkendali;
- cockpit menggunakan API collector dan tidak memerlukan credential sumber;
- identity link Maximo–PI–CEMS tervalidasi dan tidak dibentuk dengan tebakan nama;
- lima halaman konsep menampilkan data nyata/derived yang traceable, tanpa dummy
  business data;
- status/freshness ketiga collector terlihat pada halaman System Integration;
- contract, unit, time zone, formula, dan aturan status mempunyai test otomatis;
- backup/restore, retention, rollback, dan failure recovery telah diuji.
