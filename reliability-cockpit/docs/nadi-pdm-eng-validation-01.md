# NADI-PDM-ENG-VALIDATION-01 — Validasi field dan kesiapan M02

15 Oktober 2026 · Paket dokumentasi kandidat v0.1. Baseline main terverifikasi
`05ce1c060605defb58a74467a38acb43ff4d04f9`. **Paket READY; seluruh keputusan engineer
PENDING_ENGINEER_VALIDATION. M02_CONTRACT_READINESS: CANDIDATE**, bukan kontrak
metode yang sudah disahkan atau izin implementasi/aktivasi.

Mulai diskusi dari [paket singkat engineer](nadi-pdm-engineer-review-packet.md).
Dokumen ini adalah lampiran analisis/matriks keputusan, bukan roadmap kedua.
[Roadmap resmi](../../plans/NADI-ROADMAP.md) dan
[R01–R08 / Q01–Q10 / M01–M07](nadi-pdm-requirements-01.md) tetap authoritative.

## 1. Bukti yang sudah ada dan batas penggunaannya

Tujuh workbook/200 worksheet sudah diinventarisasi: INV1 mencakup3 sumber/23 sheet,
INV2 mencakup4 sumber/177 sheet. Task ini membaca inventaris/kamus dan manifest
lineage privat yang sudah ada; tidak membuka ulang seluruh worksheet, mengekstrak
nilai sumber atau mengadakan wawancara baru. Struktur bukan approval engineer.

- **INV1:** [laporan WORKBOOK-01](nadi-pdm-workbook-01.md),
  [inventaris23 sheet](evidence/nadi-pdm-workbook-01/source-inventory.json),
  [kamus kandidat0.1.0](evidence/nadi-pdm-workbook-01/candidate-dictionary.json).
- **INV2:** [laporan WORKBOOK-02](nadi-pdm-workbook-02.md),
  [inventaris177 sheet](evidence/nadi-pdm-workbook-02/source-inventory.json),
  [kamus kandidat0.2.0](evidence/nadi-pdm-workbook-02/candidate-dictionary.json).
- Manifest exact file/hash dan sheet/equipment asli tetap privat di bawah custodian;
  tidak disalin ke paket publik. Gunakan alias sumber/nomor sheet/sel di bawah
  untuk meminta custodian menampilkan bukti yang diizinkan. Nomor S mulai1;
  `sheetIndex` teknis mulai0. Tidak ada nilai ukur, private path atau ID aset riil
  pada paket ini. Tidak ada klaim bahwa setiap sheet cocok dengan profil terpilih.

| Kode | Profil kandidat | Sumber / sheet / subset representatif | DIRECT / AMBIGUOUS |
|---|---|---|---:|
| K1 | fan-s02-tribology | WB-FAN-01/S02; G6, I5, K5/K6 | 3 / 0 |
| K2 | mill-s01-tribology | WB-MILL-01/S01; F5, I5, J5 | 3 / 0 |
| K3 | logsheet-s01-mcsa | WB-6KV-01/S01; E14/F14, E35/F35, E39/F39 | 3 / 0 |
| K4 | boiler-three-point-rms | WB-VIB-BOILER-02/S36; B2:J2, unit B1 | 9 / 0 |
| K5 | boiler-five-axis | WB-VIB-BOILER-02/S13; B2:F2, unit B1 | 5 / 0 |
| K6 | bc-irregular-axis | WB-VIB-BC-02/S01; B2:J2 dan Q2:R2, unit B1 | 11 / 0 |
| K7 | turbine-four-point | WB-VIB-TURBINE-02/S15; B2:M2, unit B1 | 12 / 0 |
| K8 | cep-bearing-cbm | WB-CEP-02/S01; D17, D19:D21 | 1 / 3 |
| K9 | cep-ir-window | WB-CEP-02/S03; C9 | 1 / 0 |

Total51 field kandidat = **48 DIRECT +3 AMBIGUOUS**. DIRECT mempertahankan bukti
label/unit/window sumber, bukan48 definisi measurement yang disetujui, persetujuan
metode, atau izin import. Tiga unit temperatur tetap kosong/ambigu. Vibration
menampilkan label axis sumber tetapi quantity/point/time belum diikat. Tribology
mempertahankan ejaan unit asli; MCSA tidak menebak unit RMS. CEP memakai OTHER
provisional; bukan IR_THERMOGRAPHY atau otomatis MCSA hanya karena ada arus.

## 2. Matriks keputusan yang dapat diisi

**20 keputusan P1 kritis** untuk menyusun definisi form/metode per lingkup yang
benar-benar disetujui. P1 menghalangi pengesahan definisi M02, bukan mematikan
form QA umum yang sudah ada. **6 P2** membahas perbandingan/lanjutan; boleh ditunda sambil
entry episodik tetap tidak mengklaim comparability. Menunda keputusan tidak
membuka tren, assessment atau fitur lain. Tidak perlu meminta validasi200 sheet
satu per satu: pilih satu keluarga representatif, catat cakupan dan pengecualian.

Disiplin di tabel adalah usulan penanggungjawab, belum penunjukan seseorang.
Semua jawaban/bukti/versi/tanggal masih kosong. Isi jawaban/koreksi dan rujukan
bukti; pilih disposisi `ACCEPTED`, `REJECTED`, atau `DEFERRED` hanya setelah ada
keputusan berwenang yang dapat ditelusuri. `ACCEPTED` di matriks berarti keputusan
field terdokumentasi, bukan status APPROVED inspeksi, grant aplikasi atau izin
operasi. Bila belum ada bukti/otoritas, status tetap `PENDING_ENGINEER_VALIDATION`.
Jangan menafsirkan tanda —, ketidakhadiran engineer, atau diam sebagai persetujuan.

### P1 — Kritis untuk definisi M02

| ID | Kandidat / bukti sumber | Klarifikasi yang diperlukan | Disiplin usulan | Jawaban / koreksi engineer | Disposisi | Status validasi | Rujukan bukti jawaban | Versi disetujui / tanggal |
|---|---|---|---|---|---|---|---|---|
| G01 | Aset dan binding sumber; K1–K9; Q01/Q05 | Bukti apa yang mengikat varian sumber ke satu aset Registry berotorisasi? Sheet/nama mirip bukan bukti; tentukan lingkup yang benar-benar dicakup. | Owner aset + PdM | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| G02 | Otoritas dan versi definisi; K1–K9; Q04/Q05/Q06 | Siapa engineer berwenang untuk masing-masing metode, dokumen/prosedur versi apa yang berlaku, dan bukti apa yang membatasi cakupan persetujuannya? | Lead engineering/PdM | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| V01 | Titik fisik, 1V/1H/1A; K4–K7; B2:D2 dan subset axis; Q05 | Apa lokasi fisik setiap nomor dan arti V/H/A pada keluarga ini? Beri sketsa/rujukan titik serta binding aset; jangan mengisi 6H yang tidak ada di subset K6. | Engineer Vibration + owner aset | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| V02 | Besaran, unit, RMS/p-p; K4 B1/B2:J2; K5–K7 B1; Q01/Q04 | Besaran apa yang diukur? Apakah token mm/s-rms dan mm/s mempunyai definisi yang sama di sini? Tetapkan RMS/peak-to-peak jika memang berlaku; jangan konversi berdasarkan dugaan. | Engineer Vibration | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| V03 | Acquisition dan bandwidth; K4–K7; varian acquisition pada INV2; Q02/Q04 | Untuk subset yang dipilih: portable, installed DCS/Bently, atau belum diketahui? Apa mode pengambilan dan bandwidth yang dibuktikan prosedur? Sumber campuran tetap dipisahkan. | Engineer Vibration + pemilik instrumentasi | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| V04 | Instrumen, mounting, prosedur; K4–K7; metadata belum terikat; Q04 | Rujukan instrumen, kalibrasi bila relevan, cara pemasangan, dan versi prosedur apa yang dipakai? Apakah sama untuk semua titik satu inspeksi? | Engineer Vibration | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| V05 | Waktu ukur dan kondisi operasi; K4–K7; header tanggal; Q09 | Apakah tanggal adalah waktu pengukuran, rekap, atau laporan? Konfirmasi jam/zona/ketelitian dan kondisi operasi yang harus dicatat; yang tidak diketahui tetap kosong. | Engineer Vibration | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| T01 | Titik sampling dan equipment; K1 G6/I5/K5; K2 F5/I5/J5; Q05 | Dari aset/titik mana sampel berasal dan bagaimana rujukan sampelnya dibuktikan? Apakah varian FAN dan MILL ini memang memiliki lingkup yang sama? | Engineer Tribology + owner aset | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| T02 | Besaran/unit lab dan raw/derived; K1–K2; sel unit pada kamus; Q01 | Konfirmasi Viscosity (Cst), Acid Number (mgKOH/g atau mg KOH/g), Water Content (%) dan Ferrous (ppm) sesuai laporan lab. Mana hasil lapor asli dan mana perhitungan? Tidak menyamakan % dengan ppm. | Engineer Tribology/laboratorium | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| T03 | Laboratorium dan prosedur; K1–K2; rujukan belum tersedia; Q04 | Laporan/metode laboratorium serta instrumen/prosedur versi mana yang authoritative untuk parameter ini? Bukti apa yang boleh dirujuk secara tersanitasi? | Engineer Tribology/laboratorium | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| T04 | Waktu sampel, analisis, laporan; K1–K2; header tanggal; Q01/Q09 | Bedakan waktu ambil sampel, analisis dan penerbitan laporan. Waktu mana mewakili measurement untuk kebutuhan ini; waktu lain harus dipertahankan di mana? Jangan memakai waktu input sebagai pengganti. | Engineer Tribology/laboratorium | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| MC01 | Equipment, fase, lokasi listrik; K3 B10:BA12; Q05 | Tentukan aset dan lokasi pengukuran listrik/fase untuk profil ini melalui rujukan berwenang. Label equipment/sheet belum otomatis menjadi aset atau titik kanonis. | Engineer MCSA/kelistrikan | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| MC02 | Besaran/unit dan hasil turunan; K3 E14/F14, E35/F35, E39/F39; Q01 | Konfirmasi Load (%), Impedance Phase 1 (Ω), Upper Sideband (dB). Mana pembacaan/hasil hitung/assessment? Label RMS belum membuktikan A atau V; Warning/Rotorbar Health tidak menjadi diagnosis otomatis. | Engineer MCSA/kelistrikan | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| MC03 | Acquisition, instrumen, beban; K3; acquisition belum terikat; Q04 | Instrumen/prosedur versi apa dan konteks beban/pengambilan apa yang perlu dicatat? Pisahkan hasil pengukuran, kondisi operasi dan interpretasi engineer. | Engineer MCSA/kelistrikan | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| MC04 | Timestamp pengukuran; K3 kolom acquisition/tanggal; Q09 | Tanggal/jam mana merupakan capture aktual dan apa zona waktunya? Bagaimana sumber parsial/tanpa jam ditandai tanpa menciptakan midnight atau jadwal harian? | Engineer MCSA/kelistrikan | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| TH01 | Tiga unit temperatur bearing; K8 D19:D21; unit tidak terverifikasi; Q01/Q04 | Untuk Motor Thrust Brg Temp (1), Motor Inboard Brg Temp (2), Pump Brg Temp (3): apa unit masing-masing dan bukti sel/prosedurnya? BASELINE (oC) tidak cukup untuk menetapkan unit measurement. | Engineer thermal/CBM + pemilik instrumentasi | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| TH02 | Routine thermal atau IRT; K8–K9; IR Window; Q03/Q04 | Apakah setiap profil adalah pembacaan temperatur rutin, inspeksi termografi, atau konteks lain? Apa arti IR Window dalam pekerjaan tersebut? Nama tab saja tidak mengesahkan IRT. | Engineer thermal/IRT | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| TH03 | Kamera dan thermogram; K9 C4:M18; Q03 | Bila benar IRT: kamera/prosedur dan bukti thermogram apa yang mengikat waktu, aset dan titik? Jika tidak tersedia, nyatakan belum terbukti; metadata attachment bukan bukti custody. | Engineer IRT | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| TH04 | Kondisi referensi dan prosedur; K8–K9; konteks ambient/reference; Q03/Q04 | Bila relevan menurut engineer, konteks ambient/reference, emissivity/reflected temperature dan langkah acquisition apa yang dibutuhkan? Jangan mengambil nilai/parameter dari screenshot atau default aplikasi. | Engineer thermal/IRT | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| TH05 | Asal Delta T dan assessment; K8–K9; Delta T/hasil formula di luar input; Q01/Q06 | Mana input asli, hasil perhitungan, baseline/alarm dan interpretasi? Sebutkan rujukan asal/rumus tanpa memublikasikan nilai sensitif. Hasil turunan tetap dikecualikan sampai definisinya disetujui terpisah. | Engineer thermal/IRT | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |

### P2 — Perbandingan dan lanjutan, tidak aktif otomatis

| ID | Kandidat / bukti sumber | Klarifikasi yang diperlukan | Disiplin usulan | Jawaban / koreksi engineer | Disposisi | Status validasi | Rujukan bukti jawaban | Versi disetujui / tanggal |
|---|---|---|---|---|---|---|---|---|
| V06 | Comparability Vibration; K4–K7; Q04/Q05; R08 | Kondisi titik, besaran/unit, bandwidth, pemasangan, instrumen/prosedur dan operasi apa yang harus setara agar dua inspeksi atau portable/DCS/Bently boleh dibandingkan? UNKNOWN tetap memblokir penggabungan. | Engineer Vibration | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| T05 | Comparability Tribology; K1–K2; Q01/Q04/Q05 | Perubahan titik sampling, pelumas, lab/metode atau konteks apa yang membuat hasil tidak sebanding? Daftar kriteria harus berasal dari engineer; nama/unit sama belum cukup. | Engineer Tribology/laboratorium | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| MC05 | Comparability MCSA; K3; Q04/Q05; R08 | Fase/lokasi, beban, instrumen dan acquisition apa yang harus sama untuk perbandingan? Tidak menyatukan hasil hitung dan pembacaan tanpa justifikasi. | Engineer MCSA/kelistrikan | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| TH06 | Perbandingan/assessment thermal; K8–K9; Q03/Q06 | Jika kelak diperlukan, apa definisi reference/Delta T, kriteria kesetaraan dan otoritas penilaian? Belum ada kalkulasi, threshold atau lampu kondisi yang boleh diaktifkan. | Engineer thermal/IRT | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| X01 | Cadence dan pemicu; K1–K9; Q09 | Metode/peralatan mana berkala, berdasarkan gejala, atau investigasi? Konfirmasi ketidaktersediaan data; jangan mengisi gap atau mengasumsikan pengukuran kontinu/harian. | Owner PdM | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |
| X02 | Bukti dan izin historis; INV1/INV2; Q01/Q02/Q03; R04/R06 | Siapa custodian dan bukti pemakaian yang sah untuk sampel historis/diagnostik? Custody attachment, mapping waktu/identitas dan izin import dibahas pada M03/M04 terpisah. | Custodian + owner PdM/PO | — | BELUM_DIPUTUSKAN | PENDING_ENGINEER_VALIDATION | — | — / — |

## 3. Alur persetujuan yang dapat diaudit

1. PO/custodian memilih profil K dan varian/sel yang akan dibahas; catat bukti
   struktur tersanitasi. Engineer boleh mengoreksi atau menyatakan UNKNOWN.
2. Catat identitas/kode engineer sesuai izin, disiplin dan kewenangan yang
   dikonfirmasi; jawaban harus menyebut scope, pengecualian dan sumber prosedur.
   Jangan memublikasikan nama/ID peralatan, nilai plant atau dokumen rahasia.
3. Lengkapi per-ID: jawaban/koreksi, disposisi, rujukan bukti, versi definisi yang
   benar-benar disetujui, tanggal keputusan dan siapa yang mengesahkan. Versi
   kandidat workbook tidak otomatis menjadi versi metode/prosedur.
4. PO/pemilik engineering memverifikasi keterlacakan dan otoritas. Untuk koreksi,
   simpan jawaban terdahulu dan tambahkan revisi pengganti dengan alasan/rujukan;
   jangan mengubah DIRECT menjadi engineer-approved tanpa bukti atau menulis
   ulang historical acceptance. Keputusan parsial hanya berlaku pada scope itu.
5. Jawaban yang diterima menjadi input task M02 terpisah. Review kontrak, keamanan,
   kompatibilitas histori dan kebutuhan schema dilakukan sebelum implementasi.
   Tidak menambahkan field/enum/metadata runtime dari spreadsheet keputusan ini.

Bila engineer belum bisa ditemui, PO dapat mengisi daftar pertanyaan dan bukti
tersedia, menandai seluruh jawaban belum diterima, lalu mengirim/membahas paket
melalui proses organisasi yang diizinkan. Task ini sendiri tidak menghubungi
personel atau mengirim workbook. [Form diskusi singkat](nadi-pdm-engineer-review-packet.md)
dapat dipakai offline/asinkron. Tidak ada tanda tangan/approval yang direka.

## 4. M02 — usulan definisi minimum berversi

Berikut konsep kontrak **USULAN**, bukan schema baru, nama properti API baru,
konfigurasi runtime, atau definisi engineering yang telah disetujui.

| Definisi yang diusulkan | Isi minimum setelah engineer menjawab | Keputusan / gerbang |
|---|---|---|
| Binding aset | Identitas Registry exact, alias sumber yang diizinkan, scope varian dan bukti binding | G01; tanpa fuzzy match atau registrasi otomatis |
| Titik fisik | Identitas titik stabil + versi, aset pemilik, lokasi fisik, arti nomor/axis dan alias sumber | G01/V01/T01/MC01; nomor sama bukan titik sama |
| Metode / quantity | Metode dan versi definisi, besaran/tipe, raw vs derived, unit asli, required/nullable dengan arti UNKNOWN | V02/T02/MC02/TH01–TH02/TH05; tidak menciptakan limit |
| Acquisition | Sumber portable/installed/UNKNOWN, teknik pengambilan, RMS/p-p dan bandwidth bila berlaku, konteks operasi yang dibutuhkan | V03/V05/MC03/TH04; aturan berasal dari engineer |
| Axis/orientasi | Rujukan definisi orientasi per titik bila diperlukan; arti label sumber disahkan terpisah | V01/V04; V/H/A belum didefinisikan di paket |
| Instrumen / prosedur | Rujukan dan versi authoritative, pemasangan/kalibrasi yang relevan, lingkup satu atau beberapa titik | V04/T03/MC03/TH03–TH04 |
| Semantik waktu | Arti acquisition vs sampel/analisis/report, waktu asli, zona/offset dan precision/unknown, terpisah dari waktu entri/submission | V05/T04/MC04; date-only tidak menjadi midnight |
| Konteks perbandingan | Daftar kondisi yang harus kompatibel dan bukti persetujuannya; mismatch/UNKNOWN menghalangi penggabungan | V06/T05/MC05/TH06; bukan aturan inferensi UI |
| Provenance / keputusan | Alias sumber/sel + bukti exact dikelola privat, versi mapping, keputusan per scope, engineer/otoritas, bukti dan tanggal yang benar-benar tersedia | G02/X02; struktur sumber, approval definisi, review rekam dan izin import berbeda |

Tidak ada nilai default besaran, unit temperatur, threshold, frekuensi sampling,
standar alarm, arti axis atau identitas titik yang ditetapkan oleh tabel ini.
Q06/Q07/Q08/Q10 tetap terbuka: severity, arti PD/DGA yang belum dipastikan, “30% acr” dan abnormality
Maximo tidak terselesaikan oleh paket. Sumber Maximo/PI tetap read-only.

### Muat di v1.1 atau perlu proposal berikutnya?

Rujukan implementasi: [InspectionDraft](../src/domain/manual_inspection.py),
[ManualMeasurement](../src/domain/inspection_measurement.py),
[schema rekam v1.1](../../reliability-data-contracts/schemas/manual-inspection.schema.json),
[builder UI](../web/lib/pdm-input.ts). Versi1.1 adalah versi envelope rekam;
`method_version` adalah teks versi metode, bukan otomatis ID registry yang approved.

| Kebutuhan M02 | Kemampuan aktual v1.1 | Batas / tindak lanjut usulan |
|---|---|---|
| Identitas aset | canonical_asset_id existing; pilihan/scope otorisasi server tetap | Persetujuan binding workbook→aset bukan hasil kesamaan nama |
| Titik / quantity / unit | Per measurement ada point_ref opsional, quantity wajib, unit opsional | point_ref adalah rujukan teks terbatas, bukan registry titik/versioned binding yang sudah divalidasi |
| Nilai / waktu | Scalar asli/null dan measured_at opsional; inspected_at terpisah | Peran sampel/analisis/report serta precision waktu belum memiliki field terpisah; perlu proposal ketat bila harus disimpan bersama |
| Metode / versi | Enum metode existing + method_version | Tidak ada registry definisi quantity/acquisition/version approval yang ditegakkan oleh envelope |
| Instrument/procedure/orientation | Form native menulis scalar instrument_ref, procedure_ref, orientation di method_extension tingkat inspeksi | Bukan metadata per-row; konteks berbeda memakai inspeksi terpisah sampai kontrak baru disetujui |
| Operating context | operating_context tingkat inspeksi; history membawa konteks existing | Struktur acquisition/bandwidth/mounting per titik yang tervalidasi membutuhkan proposal, bukan JSON tersembunyi |
| Review / provenance | Human-entered provenance, quality UNKNOWN/INSPECTOR_REPORTED, lifecycle dan immutable revisions existing | field_approval tetap ENGINEER_FIELDS_PENDING, assessment NOT_ASSESSED; jawaban engineer tidak mengubah konstanta ini |
| Lampiran / lineage | Attachment metadata terbatas, case_refs dan referensi versi existing | Tidak ada upload/custody aktif atau field per-row template/hash/sheet/sel yang disetujui; metadata checksum bukan autentikasi berkas |

`method_extension` menerima scalar terbatas secara teknis; itu bukan izin membuat
metadata bebas atau menyisipkan approved_point_version, source-map, acquisition
JSON, sample/report clocks, approval atau aturan comparability. UI saat ini hanya
menyediakan tiga scalar konteks tersebut. Proposal selanjutnya harus memiliki
schema eksplisit, versi, migrasi kompatibel bila dibutuhkan, exposure/otorisasi,
review dan tes; task ini tidak mengubah schema atau melakukan migrasi.

### History dan Case: readiness yang terpisah

[API history](../src/api/human_records.py) dan
[service inspeksi](../src/services/human_records.py) menyediakan filter populasi
berotorisasi; measurement history memakai measured_at, identitas record/revision,
point/quantity dan konteks existing. `rawPlot` di builder UI membatasi sampel ke
satu inspeksi/revisi dan menolak unit/titik/konteks yang tidak cocok, null dan
waktu tidak diketahui. Ini bukan tren antarinspeksi yang sudah disahkan.

[Workflow inspeksi](manual-inspection-workflow.md) dan
[reviewed evidence](../src/services/reviewed_inspection_evidence.py) mengikat Case
ke rekam APPROVED dengan independent reviewer, exact revision dan digest penuh;
[guard handoff](../src/services/engineering.py) menolak revisi evidence yang berubah.
Namun [snapshot ReviewedInspectionEvidence](../src/domain/reviewed_inspection.py)
memuat measurement/method/version/reviewer tetapi **tidak memproyeksikan
method_extension maupun operating_context**. Hash mengikat rekam penuh, bukan berarti setiap field konteks
terlihat di snapshot Case. Usulan M02 harus menilai kebutuhan reference-versi dan
snapshot konteks sebelum dipakai untuk interpretasi/perbandingan; jangan mengklaim
instrument/procedure per-row sudah tersedia atau diselundupkan ke observations.

M03 historical readiness tetap memerlukan definisi/binding/waktu yang disetujui,
lineage terkontrol dan izin penggunaan/import terpisah. Tidak ada parser/import,
konversi, interpolasi, attachment custody atau assessment baru dari paket ini.

## 5. Checkpoint pengembangan dan batas acceptance

| Checkpoint terverifikasi | Hasil |
|---|---|
| PR82 — foundation | MERGED; merge8397b53df29280082d1382dfa3e40a5e4e2a97af |
| PR83 — reusable workflow | MERGED; merge106a4dc08b149576b2e84bbf8c70694288c7e9a7 |
| PR85 — workbook + keyboard | MERGED; merge05ce1c060605defb58a74467a38acb43ff4d04f9;9 profil/48 DIRECT/3 AMBIGUOUS |
| Development browser acceptance | Keyboard1280/1440/1920, light/dark, actual125% zoom, draft/review/Case dan HMR lulus; final visual PO PENDING |
| QAO-PDM-01 | Satu ERR_TOO_MANY_RETRIES; root UNKNOWN, diterima NON_BLOCKING hanya untuk checkpoint development |
| Engineer / operasional | Seluruh definisi/mapping/komparabilitas/UAT dan aktivasi operasional tetap belum disetujui |

Bukti checkpoint: [keputusan merge](https://github.com/johnd-creator/reliability-knowledge-starter/pull/85#issuecomment-6192024336),
[CI exact-head7daab3a](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38727418216),
[CI main05ce1c0](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38734062455).
Event console asli tidak memiliki URL/status/timestamp khusus; run bersih berikutnya
tidak mengulang semua write/review/Case/HMR dan tidak membuktikan root cause.

Task dokumentasi ini tidak memeriksa ulang runtime atau operator-review Phase1,
memperpanjang expiry, mengubah kebijakan, mengakses fixture/session/DB atau
melakukan source request. Tidak membuka investigasi proses/memori. Tidak ada
perubahan UI/backend/collector/Mart maupun deployment QA/produksi. PASS paket
berarti pertanyaan, matriks dan analisis siap direview; bukan engineer approval.
