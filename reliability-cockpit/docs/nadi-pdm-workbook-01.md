# NADI-PDM-WORKBOOK-01 — Kandidat template input berbasis workbook

15 Oktober 2026. Baseline main `106a4dc08b149576b2e84bbf8c70694288c7e9a7` (PR82 dan83 merged). Branch `codex/nadi-pdm-workbook-01`. **PARTIAL — kandidat subset terimplementasi/teruji; mapping seluruh varian dan persetujuan engineer belum selesai.** Tidak ada parser/import workbook, migration atau aktivasi operasional.

## Inventaris dan provenance

Ketiga workbook tersedia dan dibaca read-only setelah Product Owner mengonfirmasi direktori lokal. Original tidak diganti, disalin ke GitHub, di-rename atau disimpan ulang. Path absolut dan SHA256 exact disimpan privat pada `.nadi-dev/private-evidence/nadi-pdm-workbook-01/verified-inventory.json` bersama hasil ekstraksi privat. Lokasi privat relatif terhadap root checkout utama, bukan worktree kandidat. Tidak ada raw plant record, nama peralatan/asset source, formula mentah atau nilai limit yang dipublikasikan.

| Referensi | File asli | Format terverifikasi | Worksheet | Temuan struktur |
|---|---|---|---|---|
| WB-FAN-01 | AREA FAN.xlsx | XLSX/OOXML | 10 | Header bertingkat Tribology; unit dan kolom perhitungan berbeda antarvarian |
| WB-MILL-01 | AREA MILL.xlsx | XLSX/OOXML | 8 | Header Tribology; ada sheet tambahan dari konteks peralatan lain; tidak mengasumsikan satu populasi |
| WB-6KV-01 | Logsheet 6 kV.xls | OLE/BIFF8 | 5 | Header MONITORING PARAMETER PM MCSA; parameter vertikal, acquisition/tanggal horizontal |

[Inventaris struktur tersanitasi](evidence/nadi-pdm-workbook-01/source-inventory.json) mencatat seluruh23 sheet, dimensi, merged ranges dan jumlah formula. Nama sheet yang merupakan referensi peralatan tetap privat. Index sheet pada artefak teknis dimulai dari0; UI menampilkan nomor mulai1. WB-FAN-01/S02 berarti index1; WB-MILL-01/S01 dan WB-6KV-01/S01 berarti index0. Exact nama, hash dan seluruh sel sumber dapat ditelusuri melalui manifest privat tersebut.

XLSX dibaca memakai openpyxl bundled, tanpa evaluasi formula/refresh link. Formula disimpan terpisah dari cached values dalam evidence privat. XLS dibaca dengan xlrd2.0.2, ditambah pemeriksaan record FORMULA BIFF melalui pembaca OLE read-only; kelima sheet XLS memiliki0 record formula. Ini membuktikan penyimpanan sel saat diperiksa, **bukan** bahwa semua angka merupakan hasil ukur mentah atau rumus/standar tersebut disetujui. Library tambahan hanya berada di direktori sementara; dependency aplikasi tidak ditambah.

## Analisis dan keputusan mapping

AREA FAN/MILL adalah konteks input, bukan nama metode Vibration. Header sumber mendukung istilah **Tribology**; Logsheet memuat istilah **MCSA**. Metode tetap dipilih sendiri oleh pengguna dari kontrak existing. Pemilihan konteks tidak memilih metode, menetapkan versi, atau menyetujui prosedur. Dokumen revisi0 tidak dipetakan sebagai method_version.

Header fan S02 A5:T7 dan mill S01 A5:U7 memiliki gabungan Cleanliness ISO, Water Content, Viscosity Change/Viscosity, Acid Number, Ferrous, PMI dan Keterangan. Sebagian kolom Result/Perhitungan berisi formula atau campuran literal/formula. Tabel limit/referensi dan chart tambahan berada di luar area pembacaan terpilih dan tidak diaktifkan. Fan S02 kolom F memuat formula; mill S01 kolom G memuat formula. Keduanya dikecualikan dari kandidat pembacaan asli walaupun sebagian sel literal.

Mill S01 Water Content bertuliskan `%`, sedangkan konteks fan/tabel lain memakai `ppm`. Unit sumber yang berbeda tetap berbeda, tanpa konversi atau koreksi berdasarkan dugaan. `Cst`, `mgKOH/g`, `mg KOH/g`, `%`, `ppm`, `Ω` dan `dB` dipertahankan sesuai token unit yang terlihat; tanda kurung pembungkus header tidak menjadi bagian unit, tanpa normalisasi ejaan, kapitalisasi atau besaran. Label quantity mempertahankan teks header sumber, termasuk newline/spasi, hingga pengguna mengeditnya secara eksplisit.

Logsheet S01 B10:BA12 memuat dua kolom label equipment, Parameter Trending, Satuan, Warning, Tanggal dan Keterangan. E14/F14, E35/F35 dan E39/F39 mempunyai label/unit eksplisit. `RMS` tidak menetapkan A atau V; `-` dan unit kosong tidak diberi unit rekaan. Rotorbar Health/Bearing/Kondisi, label warning, dan catatan klasifikasi tidak diubah menjadi assessment, diagnosis atau threshold NADI. Beberapa label equipment antarkolom/sheet tidak konsisten; tidak dilakukan fuzzy matching.

Tanggal Excel/kolom acquisition tidak selalu lengkap, dan tidak menetapkan timezone maupun waktu pengukuran yang pasti. Nilai tanggal pada midnight dalam serial Excel tidak membuktikan pengambilan data pukul00:00. Candidate tidak menyalin timestamp; pengguna mengisi ISO dengan zona waktu atau membiarkan null. Tidak ada interpolasi, jadwal harian atau gabungan antarinspeksi.

## Kamus field kandidat

[Dictionary terbangkitkan dari registry presentasi](evidence/nadi-pdm-workbook-01/candidate-dictionary.json) memuat versi `candidate-0.1.0`, original label, header/unit cell dan window nilai. Registry aplikasi: [pdm-workbook.ts](../web/lib/pdm-workbook.ts). Dictionary dokumentasi bukan konfigurasi runtime kedua. Semua profil **PENDING_ENGINEER_VALIDATION**.

DIRECT berarti label/unit eksplisit dan window sumber bebas formula, bukan persetujuan engineering atau izin mengimpor data. DERIVED berarti kalkulasi/transformasi memerlukan justifikasi. AMBIGUOUS berarti arti/binding belum dapat dipastikan. UNMAPPED berarti belum ada mapping sah ke kontrak NADI.

| Profil / source sheet | Label sumber exact | Header; sel unit | Window sumber diperiksa | Klasifikasi | Tujuan kontrak |
|---|---|---|---|---|---|
| FAN S02 | `Viscosity (Cst)` | G6; G6 | G8:G136 | DIRECT | measurements[].quantity/value/unit |
| FAN S02 | `Acid Number (mgKOH/g)` | I5; I5 | I8:I136 | DIRECT | measurements[].quantity/value/unit |
| FAN S02 | `Ferrous` | K5; K6 | K8:K136 | DIRECT | measurements[].quantity/value/unit |
| MILL S01 | `Water Content` + newline + `(%)` | F5; F5 | F8:F136 | DIRECT | measurements[].quantity/value/unit |
| MILL S01 | `Acid Number (mg KOH/g)` | I5; I5 | I8:I136 | DIRECT | measurements[].quantity/value/unit |
| MILL S01 | `Ferrous` + newline + `(ppm)` | J5; J5 | J8:J136 | DIRECT | measurements[].quantity/value/unit |
| 6KV S01 | `Load` | E14; F14 | H14:AW14 | DIRECT | measurements[].quantity/value/unit |
| 6KV S01 | `Impedance Phase 1 ` (spasi akhir dipertahankan) | E35; F35 | H35:AW35 | DIRECT | measurements[].quantity/value/unit |
| 6KV S01 | `Upper Sideband` | E39; F39 | H39:AW39 | DIRECT | measurements[].quantity/value/unit |

Window nilai dipakai hanya untuk menolak kolom campuran/formula pada analisis offline. **Tidak ada nilai dari window tersebut yang disisipkan ke aplikasi.** Baris diisi manual oleh inspector, value awal UNKNOWN/null; inspector/session dan quality/provenance mengikuti foundation existing. Qty/unit adalah satu-satunya default sumber yang diterapkan. Titik dan waktu awal tetap kosong; asset existing tidak diubah oleh template.

| Field/struktur sumber | Klasifikasi saat ini | Tujuan potensial / penanganan |
|---|---|---|
| Equipment/sheet label | UNMAPPED | canonical_asset_id harus berasal dari pilihan Registry berotorisasi, tanpa binding workbook otomatis |
| Titik/axis/sample identity | AMBIGUOUS | measurements[].point_ref tetap null sampai identitas diklarifikasi |
| Istilah Tribology/MCSA | AMBIGUOUS sebagai metode tervalidasi | method dipilih eksplisit; gate UI mencocokkan istilah profil, bukan memberi approval |
| No. Dokumen/Revisi | UNMAPPED | Tidak menjadi method_version atau procedure_ref otomatis |
| Tanggal/acquisition header | AMBIGUOUS | inspected_at/measured_at memerlukan arti per-event, waktu dan zona; tidak ditebak |
| Load/operating regime | AMBIGUOUS untuk konteks seluruh inspeksi | Load hanya quantity literal terpilih; operating_context tidak diisi otomatis |
| Cleanliness ISO/PMI/CF/PF dan varian unit | AMBIGUOUS | Perlu definisi quantity, tipe dan unit per sheet; tetap tidak dipakai otomatis |
| Result/Perhitungan, termasuk campuran formula/literal | DERIVED | Tidak dihitung, dievaluasi atau dimasukkan sebagai pembacaan asli |
| Warning/reference/health labels | UNMAPPED | Tidak ada threshold, lampu warna, diagnosis, assessment atau risk scoring |
| Keterangan/abnormality text | AMBIGUOUS | Engineer harus memisahkan observation/interpretation/WO reference; tidak dicopy otomatis |
| Instrument, procedure, orientation yang belum teridentifikasi | UNMAPPED | Field existing tetap kosong/manual; tidak mengarang referensi |
| Source template version/lineage | UNMAPPED untuk persistence v1.1 | Tersedia pada panel dan dokumentasi saja; tidak diselundupkan ke method_extension |

## Implementasi desktop dan batas kontrak

`PdM Center → Input Pengukuran` mempertahankan form umum existing. Tiga konteks menampilkan panel profil sumber, versi, sheet/range, sembilan field DIRECT dan daftar unresolved. Metode tidak otomatis berubah. Tombol **Gunakan baris kandidat** memerlukan pilihan metode eksplisit sesuai istilah sumber; versi metode tetap wajib diisi pengguna. Tidak ada template auto-approval.

Penerapan hanya pada draf baru. Measurement yang belum disimpan tidak diganti tanpa konfirmasi; pembatalan mempertahankan isian. Template tidak menimpa revisi existing. Baris memakai grid/add/remove, dirty/session recovery, validasi typed value, expected revision/CAS, review independen dan exact-revision Case handoff existing. Quality, review status, asset authorization, CSRF, Origin dan persistence backend tidak diubah.

Unit/label terlihat per field dalam panel yang memakai tokens V1 dan grid desktop. Grid asli tetap dapat di-scroll dalam kontainernya. UNKNOWN/null, zero, timestamp asli dan error state dipertahankan; tidak ada input parser, arbitrary metadata, schema baru atau template ID persisten. Generic form tetap dapat merekam konteks lain secara manual tanpa mengklaim hasil mapping workbook ini.

## Validasi dan review

| Pemeriksaan | Hasil lokal |
|---|---|
| Label exact, token unit dan window bebas formula pada original | 9/9 PASS; evidence privat plus dictionary tersanitasi |
| Assertions PdM existing | 16/16 PASS |
| Assertions kandidat workbook | 18/18 PASS: metode/context, field bound, zero/null, unit/time, edit roundtrip, tanpa metadata/approval tersembunyi |
| Backend PdM/review/workflow | 45/45 PASS; hermetic fixture, tanpa DSN persistent/operasional |
| Browser komponen termasuk PdM existing | 92/92 PASS,0 uncaught errors; seluruh request diintersepsi |
| Desktop1440 dan1920 | PASS untuk3 profil; light/dark; screenshot sintetis, bukan live preview |
| TypeScript/lint/build | PASS; warning existing EngineeringWorkspace dan konfigurasi Next/ESLint dicatat, tidak disembunyikan |
| UX/localization/provenance assertions | PASS; kontrak existing dan hash/pemisahan label-enum tetap berlaku |
| Exact-head CI | Verifikasi terpisah pada DRAFT PR; tidak membuktikan visibility/engineer UAT |

[Screenshot dan hasil browser](evidence/nadi-pdm-workbook-01/README.md). Fixture browser tidak membuktikan enforcement server; 45 tes backend dan suite CI tetap menguji foundation tersebut. Security transport/backend source tidak berubah dalam task ini.

Distinct review: konfigurasi9 field dibandingkan kembali dengan original; tidak ada unit/quantity tebakan, formula tercampur yang masuk, automatic asset/point binding atau penyimpanan template metadata. Konfirmasi replacement dan larangan apply pada revisi existing dipertahankan. Layout kartu kandidat dirapikan menjadi auto-fit desktop; review menemukan token radius yang belum terdefinisi dan menggantinya dengan token V1 existing. Dictionary dokumentasi dibandingkan dengan registry aplikasi untuk mencegah drift. Tidak ada Design System baru.

Failed attempts yang dicatat: pencarian awal belum menemukan target sebelum konfirmasi direktori; pembacaan ulang berhasil. Beberapa perintah awal memakai working directory/path import yang tidak sesuai dan gagal sebelum edit/test yang dimaksud; diperbaiki pada worktree kandidat. Child compiler awal ditolak sandbox dan dijalankan kembali secara hermetik dengan izin host. Browser awal timeout pada label Metode yang mencakup option text; accessible label diperjelas, lalu92 checks lulus. Tidak satu pun kegagalan ini melibatkan runtime laptop, workbook write, atau sesi QA.

## Pertanyaan engineer dan approval

Q01 sekarang mempunyai original workbook dan inventaris struktur, tetapi approval mapping dan izin pemakaian operasional masih pending. **Q01–Q10 tidak ditutup oleh task ini.** Tidak ada kesimpulan PD=DGA, definisi “30% acr”, aturan cadence, severity, calibration atau Maximo abnormality yang dikarang. [Register otoritatif](nadi-pdm-requirements-01.md#engineer-validation-register) tetap berlaku.

Pertanyaan terarah berikut melengkapi register tersebut:

1. Q01/Q05: konfirmasi varian sheet dan exact binding equipment→canonical asset→physical measurement/sample point. Mengapa ada konteks peralatan lain dalam file MILL?
2. Q01/Q04: unit Water Content tiap sheet dan tabel referensi mana yang authoritative? Tidak ada otorisasi konversi `%`↔`ppm`.
3. Q01/Q04: kolom mana pembacaan asli, hasil alat/lab, atau formula? Kolom campuran tidak dapat diimpor sebagai raw reading tanpa keputusan.
4. Q01/Q09: arti tanggal event versus sample/report; waktu actual dan timezone. Apakah tanggal horizontal mencakup acquisition yang sama atau berbeda?
5. Q04/Q05: instrument, procedure/calibration/version, point dan orientation yang sah; doc revision bukan otomatis method_version.
6. Q01/Q07: unit arus/tegangan pada RMS dan arti CF/PF/indeks diagnostik. Menyimpan label literal tidak mengesahkan interpretasinya.
7. Q05/Q10: perbedaan label equipment antarkolom; catatan abnormality/WO harus diverifikasi tanpa source request atau source write.
8. Q06/Q08: dasar warning/classification dan istilah belum terdefinisi; tetap tidak diaktifkan. Q02/Q03 attachment/spectrum/thermogram dan Q07 PD/DGA tetap pending terpisah.

## Preservasi dan delivery

Worktree baru hanya dari reviewed main; active `.nadi-dev/local-dev-pr82` tetap pada `9895890a045a221998856a175d80c17270cd0d38`. Tidak memasang controller PR83, memilih source, membuka preview live, restart/reload HTTPS3000/API, membaca/mengubah fixture/session, mengakses Maximo/PI/CEMS/DCS, mengubah collector/Mart, schema, policy atau external QA. Workbooks asli, `23496711.xls`, PNG, backup dan worktree lain tetap dipertahankan.

Delivery satu **DRAFT PR**, tanpa merge. Scope candidate subset ini terimplementasi, tetapi field mapping/varian penuh dan engineer approval masih **PARTIAL/PENDING**. Next: senior review dan jawaban engineer, perluas profil hanya dari bukti exact; controlled local preview melalui controller baru memerlukan otorisasi terpisah. Tidak memulai task lanjutan secara otomatis.
