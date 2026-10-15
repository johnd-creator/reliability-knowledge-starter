# NADI-PDM-WORKBOOK-02 — Vibration dan CEP/IR Window

15 Oktober 2026 · **PARTIAL — enam profil kandidat terimplementasi/teruji; unit temperatur dan pemetaan engineering penting masih ambigu.** Main terverifikasi `106a4dc08b149576b2e84bbf8c70694288c7e9a7`; sebelum perluasan PR85 `3aa2c015c8e8e0e591e7d239c37396e3f97eaebc`. Branch existing `codex/nadi-pdm-workbook-01`, satu PR85 **OPEN/DRAFT, UNMERGED**. Bukan aktivasi operasional atau live acceptance.

## Sumber dan inventaris penuh

| Referensi | Original read-only | Sheet | Formula tersimpan |
|---|---|---:|---:|
| WB-VIB-BOILER-02 | TRENDING VIBRASI BOILER AREA.xlsx | 69 | 69 |
| WB-VIB-BC-02 | TRENDING VIBRASI BC AREA EPA.xlsx | 32 | 5 |
| WB-VIB-TURBINE-02 | TRENDING VIBRASI TURBIN AREA.xlsx | 72 | 39 |
| WB-CEP-02 | New Log Sheet_CEP_CBM1.xls | 4 | 15 |

**4/4 sumber, 177/177 worksheet diperiksa**, termasuk sheet kosong/pendek dan catatan di luar tabel utama. XLSX dibaca openpyxl tanpa refresh link atau evaluasi formula; XLS OLE/BIFF dibaca xlrd2.0.2 dan record FORMULA BIFF dipisahkan dari literal. Cached formula tidak menjadi pembacaan asli. Original tidak ditulis ulang, diimpor, atau dimasukkan Git.

Path absolut, SHA256, ukuran, nama sheet/equipment, semua sel/tipe/format/merged ranges, formula versus literal, header, catatan operasi dan koordinat nilai khusus disimpan **privat** di `.nadi-dev/private-evidence/nadi-pdm-workbook-02/` pada checkout utama. `verified-inventory.json`, `analysis-0.json` sampai `analysis-3.json`, dan `structural-annotations.json` memiliki mode0600; direktori0700. Skrip analisis/lineage read-only ikut dipertahankan di sana. Manifest sebelum/sesudah memverifikasi hash sumber. Tidak memublikasikan nilai plant, formula mentah, threshold atau nama equipment sumber.

[Inventaris publik](evidence/nadi-pdm-workbook-02/source-inventory.json) berisi alias/index seluruh sheet, dimensi, merged ranges, posisi header tanggal/axis, token unit, formula/literal counts, duplikasi tanggal kandidat, flags DCS/Bently/IR/Time dan batas mapping. **65 signature struktur** dibedakan dari urutan/posisi axis, unit, posisi header tanggal dan flags acquisition; ini pengelompokan layout, bukan persetujuan kesetaraan instrumen atau metode. Header judul equipment tetap privat. Date-gap blank/merged dan special/error cells dicatat privat; cadence fisik tetap UNKNOWN.

## Enam profil representatif

[Kamus sumber dan 42 lineage checks](evidence/nadi-pdm-workbook-02/candidate-dictionary.json) dibandingkan dengan original: label exact, token unit literal bila tersedia, dan seluruh window terpilih bebas formula. Index sheet0-based; nomor S01 berarti index0. Profile version `candidate-0.2.0`; seluruhnya `PENDING_ENGINEER_VALIDATION`.

| Profil | Sumber | Subset | Unit asli | DIRECT / AMBIGUOUS |
|---|---|---|---|---:|
| Boiler tiga titik RMS | Boiler S36, B2:J2; B3:J145 | 1V/1H/1A hingga3V/3H/3A | `mm/s-rms` dari B1 | 9 / 0 |
| Boiler lima axis | Boiler S13, B2:F2; B3:F77 | 1V,1H,2V,2H,2A | `mm/s` dari B1 | 5 / 0 |
| BC axis tidak lengkap | BC S01, B2:J2 dan Q2:R2; baris3:59 | subset11 dari26 axis, termasuk6V/6A | `mm/s` dari B1 | 11 / 0 |
| Turbin/pompa empat titik | Turbin S15, B2:M2; B3:M95 | 1V/1H/1A hingga4V/4H/4A | `mm/s` dari B1 | 12 / 0 |
| CEP bearing/CBM provisional | CEP S01, D17,D19:D21; I:BP | Current dan3 label temperatur bearing | `Ampere`; temperatur kosong | 1 / 3 |
| CEP IR Window provisional | CEP S03, C9; D9:M9 | Current dalam konteks IR Window | `Ampere` | 1 / 0 |

**39 DIRECT baru + 9 DIRECT lama =48 DIRECT; 3 field input AMBIGUOUS.** Tiga profil/nine fields versi0.1.0 dan seluruh [evidence WORKBOOK-01](nadi-pdm-workbook-01.md) dipertahankan. DIRECT membuktikan label/unit/window sumber, bukan bahwa definisi besaran, acquisition, canonical binding atau metode sudah disetujui. Label1V/1H/1A dipertahankan sebagai istilah sumber; definisi V/H/A tidak ditebak. Tidak mengarang6H yang tidak ada pada layout BC terpilih. Sheet lain tidak otomatis mewarisi profil.

DCS/Bently, displacement, peak-to-peak, RMS, local/portable dan instrument/bandwidth berbeda ditemukan pada varian sumber. Kandidat tidak memasukkan kolom DCS/Bently campuran ke keluarga lokal terpilih dan tidak menyatakan semua angka mm/s adalah portable. Acquisition tetap perlu bukti engineer. Tidak ada konversi atau threshold.

## CEP: klasifikasi dan batas bukti

**THERMAL_IRT_CLASSIFICATION: Candidate**, bukan Verified IRT. Sumber memiliki bearing-temperature, Current, cooling/body context, IR Window connection, Date/Time, ambient label, humidity dan Delta T. Label IR Window tidak membuktikan thermogram, kamera, emissivity, reflected temperature atau prosedur. Tidak ada referensi thermogram/kamera terverifikasi dari pemeriksaan teks sel; custody/arti objek gambar tertanam tidak dikualifikasi sebagai thermogram.

`BASELINE (oC)` bukan bukti unit seluruh measurement. Karena itu ketiga label bearing-temperature memakai unit kosong/AMBIGUOUS; baseline/alarm/trip tidak disalin. Current tetap observasi literal `Ampere`, tidak otomatis MCSA. Kedua profil menggunakan **OTHER provisional CBM**, dipilih eksplisit pengguna, bukan IR_THERMOGRAPHY. Fase koneksi tanpa unit terverifikasi, ambient tanpa unit pasti, humidity dengan persoalan format fraction/percent, dan Delta T formula tidak dimasukkan sebagai pembacaan asli. Tidak mengarang ambient, delta, limit atau calibration.

## Kontrak historis usulan dan comparability register

Tidak ada import historic data atau parser aplikasi. Usulan berikut merupakan gate untuk pekerjaan terpisah, bukan schema/metadata baru pada v1.1.

| Elemen historis | Bukti yang harus dipertahankan / keputusan |
|---|---|
| Identitas sumber | Hash file privat + sheet/index + coordinate + raw type/format; canonical asset/point perlu exact binding berotorisasi, bukan fuzzy match |
| Tanggal | Bedakan YYYYMMDD numeric/text, ISO-like string, Excel serial/datemode, Date dan metadata dokumen. Tidak menebak serial dari angka generic |
| Waktu | CEP memiliki Time parsial/terpisah; date tanpa time tidak menjadi midnight. Timezone UNKNOWN; tidak mengambil timezone laptop |
| Duplikasi/gaps | Duplicate-date candidates bukan bukti duplikasi event; blank/merged header dan missing acquisition tetap dicatat. Tidak resample/interpolate |
| Nilai | Raw scalar/type dan unit literal, zero/negative/special/error ditinjau per field. Blank≠zero. Formula dan cached output dipisahkan; tidak dievaluasi sebagai raw reading |
| Revision | Equipment, physical point, axis, instrument/mounting/bandwidth, procedure dan operating regime memerlukan version-bound binding |
| Approval | Sumber, field, comparability, independent record review dan izin import terpisah; Q01/Q04/Q05/Q09 serta custodian/PO approval masih pending |

| Keputusan | Status / perilaku |
|---|---|
| Antar workbook/sheet/aset dengan nomor titik sama | PENDING; tidak digabung |
| Portable/local versus DCS/Bently/PI | PENDING; tidak digabung |
| `mm/s-rms` versus `mm/s`, displacement versus velocity, RMS versus p-p | PENDING; tidak dinormalisasi/dikonversi/digabung |
| Instrumen/mounting/bandwidth/prosedur/operating regime berbeda | PENDING; inspeksi terpisah bila konteks berbeda |
| Date-only atau timezone/waktu hilang | UNKNOWN; tidak membuat titik waktu palsu |
| Formula, Delta T, baseline/threshold | Bukan raw acquisition; tidak diaktifkan |
| Cross-inspection trend | PENDING; rawPlot existing tetap satu record/revision dan menolak mixed context/unit/point |
| Persetujuan rekam/Case handoff | Workflow existing; bukan persetujuan kesetaraan, diagnosis atau izin kerja |

## Implementasi dan keputusan arsitektur

Registry `pdm-workbook.ts` tetap menjadi konfigurasi presentasi tunggal; dictionary JSON adalah evidence terbangkitkan, bukan runtime config kedua. Empat konteks ditambahkan secara aditif. Enam keluarga baru memerlukan selector eksplisit; pemilihan area tidak memilih metode. Profil Tribology/MCSA lama tidak berubah.

Panel menampilkan label/unit/axis sumber, alamat lineage, approval pending dan batas mapping. Penerapan hanya pada draf baru, konfirmasi mengganti isian tetap wajib, revisi existing tidak dapat ditimpa. UNKNOWN/null awal, timestamp/point kosong, canonical asset tidak diubah, no template metadata persistence. Thermal unit ambigu kosong. Quantity Vibration tidak diisi label axis; field wajib ini menunggu input engineer. Tidak ada penambahan source values, backend action, schema, dependency atau migration.

InspectionDraft v1.1 hanya mempunyai scalar orientation/instrument/procedure tingkat inspeksi. Per-row axis/source lineage belum punya kontrak persistensi yang disetujui. Label raw axis terlihat pada panel dan petunjuk baris presentasi saja. **Quantity dan point_ref tetap kosong** untuk keluarga axis; engineer mengisi besaran dan binding yang sah. Petunjuk sourceHint tidak masuk DTO atau metadata. Engineer harus menetapkan point dan konteks; profil tidak memberi approval hidden. Konteks yang berbeda tidak diselundupkan ke metadata bebas. Generic form, CAS, session, CSRF, Origin, scope, independent review, history dan exact-revision Case handoff tetap existing.

## Engineer review packet

Semua Q01–Q10 [register otoritatif](nadi-pdm-requirements-01.md#engineer-validation-register) tetap pending. Follow-up berikut memperinci pertanyaan, bukan mengganti register:

| Follow-up | Q existing | Keputusan yang dibutuhkan |
|---|---|---|
| WB02-01 | Q01/Q05 | Exact source equipment→Registry asset→physical point; varian mana milik equipment/revision yang mana? |
| WB02-02 | Q02/Q04/Q05 | Arti V/H/A, lokasi bearing, mounting dan point-version; ketidaklengkapan/duplikasi axis apakah disengaja? |
| WB02-03 | Q04/Q05 | Instrument/calibration/procedure/version dan bandwidth; portable atau installed per column? |
| WB02-04 | Q01/Q04 | Besaran/unit exact; `mm/s-rms` versus mm/s dan um/p-p tidak otomatis ekuivalen. Unit tiga bearing-temperature apakah benar oC? |
| WB02-05 | Q01/Q09 | Arti measurement/report date, Excel epoch, Time parsial dan timezone; arti duplicate-date/gaps/zeros/negative/errors? |
| WB02-06 | Q04/Q05/Q06 | Bukti comparability portable/DCS/Bently; siapa menyetujui lokasi/operating regime dan temporal relationship? |
| WB02-07 | Q03/Q04 | IR Window acquisition, thermogram/image custody, kamera/emissivity/reflected/ambient/reference context; metode IRT atau thermal CBM? |
| WB02-08 | Q01/Q04/Q06 | Formula/cached/Delta T versus raw measurement; baseline/alarm/trip dan interpretasi harus disetujui terpisah |
| WB02-09 | Q01/Q09 | Izin custodian/PO untuk historical import serta kontrak lineage/rejection; belum diberikan task ini |
| WB02-10 | Q06/Q07/Q08/Q10 | Authority thresholds/diagnosis tetap terpisah; tidak menyelesaikan PD/DGA, “30% acr”, atau Maximo abnormality lewat workbook ini |

## Validasi, review dan batas acceptance

- Original lineage: **42/42 PASS**, 39 unit literal +3 unit sengaja unresolved; tidak ada formula dalam window kandidat. Old9/DIRECT evidence tidak berubah.
- PdM assertions:16 existing +48 workbook =**64/64 PASS**; dictionary drift, method refusal, raw units, null/zero/timezone, no automatic point/time, no hidden metadata, edit roundtrip dan date-only rejection.
- Browser komponen **169/169 PASS**,0 uncaught errors: semua9 profil, confirmation, workflow/review/CAS/Case handoff, old-backend refusal dan authorization UI. Request seluruhnya diintersepsi.
- [24 screenshot baru](evidence/nadi-pdm-workbook-02/README.md): enam profil ×1440/1920 ×light/dark; no page overflow. Screenshot nol adalah uji sintetis yang diisi manual, bukan nilai sumber.
- TypeScript, lint, build, product safety dan UX/provenance assertions PASS. Dua lint warnings existing EngineeringWorkspace/ignored status route tetap dicatat. Build memakai API base loopback port9, bukan API live.
- Backend PdM/strict DTO/review/CAS/security/Case regression **45/45 PASS**, SQLite in-memory fixtures. Total terhitung64+169+45 = **278/278**, ditambah42 original lineage checks. Exact-head backend/frontend CI dicatat pada PR85; tidak menyimpulkan live acceptance dari CI/browser fixture.

Distinct review membandingkan kembali original, profil lama, scope diff dan screenshot. Koreksi: assertion lama mengasumsikan hanya3 konteks; diganti pemeriksaan additive yang mempertahankan3 konteks awal. Unit temperatur baseline ditolak sebagai default. Semua keluarga baru memerlukan pemilihan eksplisit, termasuk single-family context. Review semantik menemukan label axis sempat dipakai sebagai quantity literal. Dikoreksi menjadi petunjuk presentasi; quantity/point tetap kosong dan wajib diklarifikasi sebelum menyimpan. sourceHint tidak dipersistensikan; regresi/screenshots diulang. Test compiler/TestClient sempat tertahan/ditolak sandbox; hanya proses unittest disposable dihentikan, lalu suite hermetik dijalankan dengan izin host. Satu invocation assertion sempat memakai cwd root, diperbaiki ke web. Tidak ada retry aplikasi/running service.

## Preservasi dan delivery

HTTPS3000 tetap frontend/API PR82 `9895890a045a221998856a175d80c17270cd0d38`, Node22.23.1. Parent frontend1348659/worker1348677 dan API1348657/listener1356390 serta invocation IDs/restart count tetap seperti checkpoint. Tidak ada HTTP status call, source selection/controller install, reload/restart, akses QA DB/session, source GET, collector/Mart, container, policy, backup atau external QA operation. Generated `next-env.d.ts` active worktree tidak disentuh; workbook asli, PNG dan `23496711.xls` dipertahankan.

**Implementation candidate teruji; mapping penting masih PARTIAL.** CI final dan exact SHA berada pada commit/PR85 yang melampirkan laporan ini. PR tetap DRAFT, tidak merge. Berikutnya: Product Owner visual review dan engineer field validation; live preview memerlukan otorisasi terpisah.
