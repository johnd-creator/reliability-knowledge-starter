# Lembar diskusi engineer — Input pengukuran PdM NADI

15 Oktober 2026 · Kandidat v0.1 · **Siap dibahas, belum disetujui engineer.**
Tujuan: memastikan form merekam pengukuran yang benar, sebelum membahas tren atau
penilaian kondisi. Semua keputusan masih **PENDING_ENGINEER_VALIDATION**.

Tujuh workbook sudah diinventarisasi; tidak perlu memeriksa200 sheet satu per satu.
Mulai dari **satu profil representatif** yang engineer kenal, catat cakupannya,
lalu lanjutkan metode lain/asinkron bila waktunya belum tersedia. Ada9 profil
kandidat,48 label/unit DIRECT dan3 unit temperatur ambigu. DIRECT berarti asal
label/unit dapat ditelusuri; **bukan definisi pengukuran yang sudah disetujui**.

## Identitas sesi dan ruang koreksi

| Isian | Catatan engineer / PO |
|---|---|
| Nama/kode engineer yang diizinkan; disiplin | ____________________ |
| Kewenangan/pemilik keputusan yang dikonfirmasi | ____________________ |
| Tanggal respons; bukti/prosedur rujukan | ____________________ |
| Profil K1–K9 / varian yang dibahas | ____________________ |
| Lingkup yang disetujui untuk dibahas dan pengecualian | ____________________ |
| Koreksi umum / yang belum diketahui | ____________________ |

Gunakan alias sumber dan bukti tersanitasi. Identitas peralatan riil, nilai plant,
berkas rahasia serta lokasi privat tetap bersama custodian berwenang. Jangan
menyalinnya ke GitHub. Bila belum bertemu engineer, isian tetap kosong; PO dapat
menyiapkan bukti dan pertanyaan tanpa mengisi jawaban atau persetujuan atas namanya.

## Mulai dari dua keputusan bersama

- **G01 — Aset:** bukti apa yang memastikan data di keluarga sheet ini milik aset
  dan lokasi pengukuran/sampling yang benar? NADI sekarang meminta pilihan aset
  berotorisasi; nama sheet/nomor titik tidak mengikat aset secara otomatis.
- **G02 — Otoritas/versi:** siapa yang boleh mengesahkan definisi untuk lingkup ini,
  dan dokumen/prosedur versi apa yang dipakai? Versi template bukan otomatis
  versi metode. Catat bukti dan tanggal hanya saat benar-benar diberikan.

Jawaban/koreksi G01–G02: ______________________________________________________

## Pertanyaan utama per metode

Contoh di bawah hanya **header/unit sumber**, bukan nilai pembacaan. Kode K dan
koordinat lengkap tersedia di [matriks rinci](nadi-pdm-eng-validation-01.md#1-bukti-yang-sudah-ada-dan-batas-penggunaannya).

| Metode / contoh sumber | Perilaku NADI sekarang | Keputusan yang diminta | ID |
|---|---|---|---|
| Vibration — K4/S36: 1V,1H,1A; mm/s-rms. K5–K7: mm/s | Label axis ditampilkan; titik, besaran dan waktu belum diisi otomatis | Nomor dan V/H/A menunjuk posisi apa? Besaran/unit apa yang sah; RMS atau peak-to-peak bila berlaku? Tidak menambah axis yang tidak ada | V01–V02 |
| Vibration — keluarga yang sama | Tidak menyatukan portable dengan DCS/Bently; konteks instrumen/prosedur berlaku untuk satu inspeksi | Sumber pengambilan, bandwidth, instrumen, mounting dan prosedur apa? Kapan diukur dan kondisi operasi apa yang perlu dicatat? | V03–V05 |
| Tribology — K1/K2: Viscosity (Cst), Acid Number, Ferrous; Water Content (%) pada K2 | Unit sumber tetap; kolom bercampur formula tidak menjadi pembacaan asli | Sampel berasal dari titik/aset mana? Konfirmasi arti hasil lab dan unit tiap parameter; mana hasil lapor asli dan mana perhitungan? | T01–T02 |
| Tribology — kolom tanggal/laporan | Waktu tidak ditebak; tidak mengubah % menjadi ppm | Lab/prosedur versi mana? Bedakan waktu ambil sampel, analisis dan laporan; mana yang harus dipakai sebagai waktu pengukuran? | T03–T04 |
| MCSA — K3: Load (%), Impedance Phase 1 (Ω), Upper Sideband (dB) | Tidak menebak unit RMS atau mengubah Warning/Rotorbar Health menjadi diagnosis | Aset/fase/lokasi listrik mana? Apa besaran/unit yang benar, dan apakah hasilnya pembacaan, perhitungan atau penilaian? | MC01–MC02 |
| MCSA — acquisition/tanggal | Input manual; waktu/konteks tidak diisi dari dugaan | Instrumen/prosedur, beban dan cara pengambilan apa yang diperlukan? Apa waktu capture asli dan zona waktunya? | MC03–MC04 |
| CEP — K8: Motor Thrust Brg Temp (1), Motor Inboard Brg Temp (2), Pump Brg Temp (3) | **Ketiga unit tetap kosong.** BASELINE (oC) tidak dianggap bukti unit measurement | Apa unit masing-masing, dan di mana bukti sumber/prosedurnya? Boleh jawab belum diketahui | TH01 |
| CEP/IR Window — K8/K9; Current (Ampere) | Masih OTHER/CBM provisional, bukan IRT yang disahkan | Monitoring temperatur rutin atau inspeksi termografi? Bila IRT, tunjukkan rujukan kamera, thermogram, titik/waktu dan prosedur; konteks ambient/reference apa yang diperlukan? | TH02–TH04 |
| CEP — Delta T dan penilaian pada struktur sumber | Tidak dihitung/disalin sebagai nilai asli; tidak ada alarm atau skor baru | Mana input asli dan mana hasil perhitungan/assessment? Apa rujukan asalnya? Persetujuan kalkulasi/limit tetap keputusan lain | TH05 |

Jawaban/koreksi Vibration: __________________________________________________

Jawaban/koreksi Tribology: __________________________________________________

Jawaban/koreksi MCSA: _______________________________________________________

Jawaban/koreksi CEP/thermal/IRT: ______________________________________________

## Bahas belakangan bila diperlukan

Keputusan P2 boleh **DEFERRED**; belum dijawab berarti tidak boleh menggabungkan
seri atau mengaktifkan penilaian. Ini tidak menghalangi diskusi form manual yang
jujur menampilkan data belum diketahui.

- **V06/T05/MC05/TH06:** kapan dua pengukuran boleh dibandingkan, dan kapan harus
  dipisah karena titik, besaran/unit, instrumen/prosedur, acquisition atau operasi?
- **X01:** berkala, saat gejala, atau investigasi? Jangan mengarang jadwal harian.
- **X02:** siapa custodian dan izin pemakaian historis/bukti diagnostik? Pembahasan
  ini belum mengizinkan import atau upload lampiran.

Catatan/yang ditunda: _______________________________________________________

## Tutup sesi tanpa kehilangan keputusan

Pindahkan setiap jawaban ke baris ID pada
[matriks yang dapat diedit](nadi-pdm-eng-validation-01.md#2-matriks-keputusan-yang-dapat-diisi):
isi koreksi, disposisi ACCEPTED/REJECTED/DEFERRED, bukti, pemilik keputusan,
versi dan tanggal bila benar-benar disahkan. Jangan memilih ACCEPTED hanya karena
form sudah berjalan. Jika satu jawaban mencakup beberapa ID, sebutkan setiap ID
serta cakupan/pengecualiannya; isian lain tetap pending.

Keputusan diterima untuk ID: __________ Bukti: __________ Versi/tanggal: _______

Ditolak/ditunda dan alasannya: ________________________________________________

Engineer/pemilik keputusan yang mengonfirmasi sesuai kewenangan: _______________

**Sesudah sesi:** implementasikan hanya keputusan M02 yang telah disetujui melalui
task terpisah. Persetujuan rekam inspeksi NADI tidak mengesahkan definisi metode,
kondisi peralatan, pekerjaan Maximo, historical import atau aktivasi operasional.
Nol tetap nilai, kosong tetap belum diketahui; pengukuran, observasi, interpretasi
dan independent review tetap terpisah.

## Bantuan visual opsional

Gambar existing berikut berlabel **DEMO/QA SINTETIS**, bukan nilai workbook asli,
bukan live acceptance dan bukan bukti engineer approval. Tidak perlu memeriksa
seluruh screenshot; pilih sesuai metode yang sedang dibahas.

[Contoh Vibration](evidence/nadi-pdm-workbook-02/boiler-three-point-rms-light-1440.png) ·
[Contoh Tribology](evidence/nadi-pdm-workbook-01/area_fan-1440.png) ·
[Contoh MCSA](evidence/nadi-pdm-workbook-01/logsheet_6kv-1440.png) ·
[Contoh CEP](evidence/nadi-pdm-workbook-02/cep-bearing-cbm-light-1440.png).
