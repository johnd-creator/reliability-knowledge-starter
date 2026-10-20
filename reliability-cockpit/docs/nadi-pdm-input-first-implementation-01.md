# Pusat PdM — input sesuai workbook, 20 Oktober 2026

Kandidat lokal ini menambahkan input manual sesuai tujuh workbook engineer. Nilai
historis dari workbook tidak diimpor. Pemilihan aset aplikasi tetap mengikuti
otorisasi server; label aset/sheet sumber tidak membuktikan binding fisik.

Baseline adalah main `35f3c101129241745e1795edd78a34c3617dccd7` ditambah patch
Engineering lokal yang belum dikomit, SHA256
`fe7395ca12372b34f3c5fa5f06a1cbdeb5f7b27e20183ac47e04934336b15290`.
Worktree Engineering asal tetap dipertahankan. Kandidat PdM juga belum dikomit,
dipush, dibuat PR, dimerge, atau dijalankan pada preview utama.

## Cakupan sumber dan formulir

Ketujuh file dimaterialisasi melalui Library ke workspace laptop sendiri,
diverifikasi ukuran/SHA256 terhadap inventaris terdahulu, lalu dibaca ulang
langsung: lima XLSX dengan openpyxl, dua XLS dengan parser privat xlrd. Tidak ada
macro, formula, external link, atau pembacaan riwayat aplikasi yang dijalankan.

| Workbook | Sheet | Profil/blok input | Deskriptor field |
|---|---:|---:|---:|
| AREA FAN.xlsx | 10 | 10 | 268 |
| AREA MILL.xlsx | 8 | 8 | 182 |
| Logsheet 6 kV.xls | 5 | 32 | 928 |
| New Log Sheet_CEP_CBM1.xls | 4 | 4 | 93 |
| TRENDING VIBRASI BC AREA EPA.xlsx | 32 | 32 | 744 |
| TRENDING VIBRASI BOILER AREA.xlsx | 69 | 68 | 656 |
| TRENDING VIBRASI TURBIN AREA.xlsx | 72 | 72 | 753 |
| Total | 200 | 226 | 3.624 |

Boiler S016 kosong. Angka field adalah instans header/kolom sumber, termasuk
pengulangan blok, bukan jumlah besaran ilmiah unik. Terdapat 3.221 isian sumber,
166 referensi, dan 237 penilaian yang dilaporkan sumber. Sebanyak 2.253 unit
belum dapat ditentukan dan tetap null. Struktur header terpilih diverifikasi;
ini bukan klaim kesetaraan penuh seluruh semantik, catatan bebas, objek gambar,
chart/OLE, atau formula dependency workbook.

Katalog mempertahankan label/unit literal dan identitas sheet/field/rentang,
termasuk kolom berbeda di bawah merged header yang sama. Tidak ada nilai aktual,
identitas peralatan nyata, formula, atau angka alarm yang ditanam pada katalog.
Profil berisi paling banyak 60 field; pengguna dapat menambah field sumber
manual hingga batas kontrak 100 baris per rekam.

## Perilaku input dan batas makna

Jenis formulir baru menyimpan `input_capture` bertipe, kontrak inspeksi 1.2,
terpisah dari `measurements` native 1.1. Form native dan sembilan template
kandidat terdahulu tetap tersedia. Server menolak pencampuran kedua representasi.

Nilai berupa angka finite, teks, boolean, atau null. Teks kosong berbeda dari
null; nol bukan pengganti kosong. Format leksikal seperti `001.00` atau `-0`
dapat disimpan sebagai teks asli; angka JSON tidak menjamin format leksikal atau
tanda negative-zero. Unit tidak dikonversi. Label titik/axis adalah label sumber,
bukan canonical point.

Waktu sampel, analisis, laporan dan pengambilan data dipisahkan. Tanggal saja,
jam saja, waktu lokal tanpa zona, datetime ber-offset dan serial/teks mentah
memiliki presisi eksplisit; tidak dibuat midnight atau zona laptop. Jam sumber
belum otomatis menjadi `inspected_at`/`measured_at`. Filter waktu register native
karenanya tidak menggunakan tanggal sumber provisional.

Input disimpan ke pemilik JSON store yang sudah ada; tidak ada tabel, database,
migrasi, atau grant baru. Create/revisi memakai receipt idempotency, pemeriksaan
revisi (CAS), audit immutable dan batas role/aset existing. Detail dan riwayat
menampilkan isi capture exact; register dan riwayat inspeksi memuat satu rekam/snapshot per halaman untuk
menjaga batas respons proxy existing tanpa melonggarkannya. Hal ini merupakan
tradeoff input-first; indeks ringkas dapat dipertimbangkan kemudian untuk
menampilkan lebih banyak rekam tanpa mengirim seluruh isi capture.

Cache input hanya berada dalam memori workspace. Pemeriksaan sesi menutup
private view tetapi tidak membuang isian saat identitas sama. Hasil simpan yang
tiba ketika editor terlepas dipulihkan sebagai rekam tersimpan, sehingga retry
tidak membuat rekam baru. Gangguan otoritas sesi sementara tetap menutup tampilan privat; tombol periksa
kembali mengulangi pemeriksaan yang sama tanpa reload yang membuang isian.
Perubahan identitas/role/scope serta 401/403 menutup
akses dan membersihkan pemulihan; tidak ada penyimpanan browser permanen.

Capture dapat menjalani review rekam independen. Status tetap
`ENGINEER_FIELDS_PENDING` dan `NOT_ASSESSED`; review bukan pengesahan kondisi.
Server menolak capture provisional sebagai evidence Case sampai pemetaan dan
proyeksi snapshot sumber dapat divalidasi. Capture tidak masuk tren measurement,
konversi, diagnosis, severity, atau rekomendasi otomatis.

Dua puluh P1 kini dibedakan sebagai informasi sumber yang boleh dilaporkan
versus keputusan engineering yang tetap pending. Enam P2 mengenai comparability,
assessment, cadence, custody/izin import tetap deferred dan tidak menghalangi
input provisional. Lihat kontrak rinci dan matriks keputusan pada
[nadi-pdm-input-first-contract-01.md](nadi-pdm-input-first-contract-01.md).

## Ambiguitas yang sengaja dipertahankan

- Label CEP S001 berulang/bertentangan dengan tipe data; tidak menyalin arti dari
  sheet sebelah atau menganggap semuanya satu titik phase T.
- Beberapa kolom lab/PMI/ISO memiliki merged header tanpa nama subkolom. Identitas
  kolom dibedakan, arti quantity/channel dan unit tidak ditebak.
- 6 kV S005 memiliki label sumber yang tidak konsisten. Tidak ada binding otomatis.
- Kolom campuran literal/formula ditandai sebagai peringatan sumber. Asal nilai
  default UNKNOWN; pengguna melaporkan apakah nilai literal atau hasil rumus.
  Aplikasi tidak mengevaluasi formula atau mengesahkan batas/assessment.

Kapabilitas terverifikasi sebelum perubahan adalah penerapan sembilan kandidat
ke form manual dan metadata attachment tanpa upload/download. Pada jalur PdM
yang ditinjau tidak ditemukan import historis Excel yang didukung; ini bukan
audit seluruh repository. Tidak ada record sumber nyata yang diimpor atau dibuat.

## Verifikasi

Bukti terperinci berada di workspace review lokal `review-evidence/`, meliputi
manifest transfer/hash, audit katalog, suite backend, exact HTTP/PostgreSQL,
browser tujuh workbook, wrapper sesi aktual, build/lint/TypeScript dan preservasi
runtime. Laporan akhir mencatat jumlah tes yang benar-benar berjalan serta skip,
bukan menyamakan hasil helper dengan uji HTTP atau runtime operasional.

Backend 1.2 dan UI ini harus diaktifkan sebagai satu kandidat yang cocok dalam
pekerjaan terpisah bila pengguna kelak mengizinkan. Preview utama, controller,
collector, data operasional, sesi login, serta konfigurasi autentikasi/network
existing tidak diubah oleh implementasi ini. F03 dan keputusan diagnosis PdM
tetap memiliki gate tersendiri.

## Kebutuhan workflow yang dilaporkan user — belum menjadi kebijakan terverifikasi

Sumber: pesan user `Sentinel_235deea2dd0c8191b9e82457ad6ad671`,
2026-10-20 08:48:58 UTC, diteruskan melalui task induk. Konteks ini dicatat sebagai
laporan user, bukan hasil verifikasi independen atas prosedur organisasi.

User menyampaikan bahwa pekerjaan PdM dapat berasal dari permintaan departemen
terkait, misalnya EPA meminta pengukuran vibrasi belt conveyor. Metode yang
disebut mencakup vibration, tribology dan MCSA. PdM menganalisis pengukuran dan
dapat membuat SR bila hasilnya buruk atau memerlukan tindakan. PdM juga dapat
membuat SR dari temuan PM 52 minggu sendiri tanpa menghubungi operator terlebih
dahulu. Karena itu persetujuan operator tidak boleh dianggap syarat universal.

Dukungan yang sudah ada dalam lingkup input: pilihan metode terkait, nilai dan
label sumber, konteks operasi, observasi dan interpretasi manusia yang terpisah,
serta identitas/revisi inspeksi. Asal permintaan dapat dicatat sebagai konteks
naratif atau field sumber manual; ini belum menjadi field workflow yang
terstruktur atau otoritatif.

Gap berikutnya adalah model traceability eksplisit untuk asal pekerjaan
(permintaan departemen / PM 52 minggu / asal lain yang dilaporkan), departemen
peminta, pengukuran, analisis manusia, dan referensi/status SR eventual. Referensi
Work Order existing pada rekomendasi tidak sama dengan referensi SR. Dukungan
workflow native Case yang sudah ada juga tidak mengesahkan capture provisional
menjadi evidence Case atau menciptakan SR.

Konteks ini tidak menambah implementasi workflow pada kandidat input-first.
Tidak ada pembuatan SR otomatis, operasi tulis Maximo, atau keputusan approval
baru yang diaktifkan. Perancangan traceability SR merupakan pekerjaan terpisah;
aturan organisasi dan izin operasionalnya tetap perlu diverifikasi sebelum
aktivasi, dengan menghormati laporan user bahwa operator bukan gate universal.
