# Asal pekerjaan PdM — lokal, item 1

Baseline: main `44bc1def5ba18802838bc5d40e04165685197696` (PR108).
Implementasi ini belum dipublikasikan atau diaktifkan pada preview utama.

## Konteks dan perilaku

Satu inspeksi dapat mencatat asal pekerjaan berikut:

- **Permintaan bidang** (`DEPARTMENT_REQUEST`): bidang peminta wajib berupa teks
  nonkosong ≤160 karakter; contoh EPA. Bukan directory organisasi atau role grant.
- **Temuan PdM · PM 52 week** (`PDM_PM_52_WEEK`): tidak memiliki bidang peminta.
- **Belum dicatat (tidak diketahui)**: `work_origin` absen, termasuk rekam lama.
  Tidak ada inferensi asal berdasarkan author, metode, jadwal atau workbook.

Label aset pada permintaan/temuan opsional, nonkosong bila diberikan, ≤200 karakter.
Teks dipertahankan persis, termasuk whitespace yang bermakna. Label ini dilaporkan
manusia dan belum diverifikasi; tidak memilih/menciptakan/mengikat aset kanonis.
Label workbook tetap berada di `input_capture.source_asset_label`, terpisah karena
berasal dari dokumen, bukan deskripsi permintaan/temuan pekerjaan.

Identitas inspeksi tetap `canonical_asset_id` dari pilihan aset sesi berotorisasi,
diperiksa ulang server terhadap Registry dan scope. Form revisi mempertahankan aset
rekam yang sama. Asumsi minimal: pekerjaan dicatat untuk satu aset inspeksi yang
sudah tersedia dalam mekanisme identitas existing. Label sumber yang belum terikat
tidak membuat aset baru; tidak ada pemetaan fuzzy atau canonical binding otomatis.

Pilihan asal bersifat opsional agar ketidaktahuan dapat dicatat jujur. Memilih
asal baru mengosongkan isian khusus asal sebelumnya di form. PM52 tidak menyimpan
bidang peminta tersembunyi. Tidak ada kewajiban kontak/persetujuan operator.

## Kontrak, persistence dan keamanan

`work_origin` adalah union typed pada `InspectionDraft`/`ManualInspection`, bukan
metadata bebas `method_extension`. Record dengan origin memakai kontrak1.3 untuk
native maupun capture. Record1.0/1.1 native dan1.2 capture tetap valid; serializer
menghilangkan origin absen sehingga JSON/hash evidence lama tidak berubah.
Contract1.3 memerlukan origin. Provenance measurement dan penolakan provisional
capture sebagai evidence Case tetap berlaku. Origin bukan penilaian kondisi.

Owning JSON store, transaction receipt request_id, CAS expected_revision, immutable
history, existing role/asset/CSRF/session authority dan review independen digunakan
kembali. Tidak ada tabel, DDL, database atau migrasi baru. Save/readback/revision
membawa origin; snapshot historis menampilkan nilai pada revisi tersebut, termasuk
unknown pada rekam lama. Detail inspeksi dan histori PdM menampilkan konteks sama.

Draft belum disimpan tetap hanya di provider workspace existing, tanpa localStorage
atau browser persistence baru. Fokus/auth checking/navigasi sementara pada sesi
sama dapat memulihkan isian. Identitas, role, asset scope berubah atau sesi dicabut
menghapus konteks privat sesuai mekanisme existing. Simpan sebelum menutup browser.
Retry lost ACK tetap memakai intent/receipt yang sama; penggantian isian membuat
intent baru sesuai perilaku existing. Tidak ada klaim draft tahan browser restart.

## Batas scope dan pengujian

Tidak menambah diagnosis, analisis/rekomendasi, referensi/pembuatan SR, write Maximo,
operator approval, collector atau perubahan controller. Suite backend existing dan
`test_pdm_work_origin` mencakup kontrak, exact legacy hashes, SQLite/Postgres, retry,
CAS, history, conditional validation, CSRF, role, scope, atribusi dan revocation.
CI Engineering menyertakan modul baru. Frontend `check:pdm-input` menambah origin
roundtrip/validation; `pdm-auth-browser-check.py` menguji konteks pada13 skenario
komponen aktual dengan semua URL diintersepsi.

`web/scripts/pdm-origin-api-browser-check.py` menerima `--bundle`, `--css`,
`--chromium`, `--report`, memakai `NADI_APPLICATION_TEST_DSN` **fixture disposable**.
Bundle berasal dari `browserBundle('scripts/pdm-auth/entry.tsx')`. Test menghubungkan
komponen aktual ke trusted-session FastAPI TestClient dan PostgreSQL sementara;
semua traffic browser `.invalid` diintersepsi sebelum network, tanpa TLS ignore.
Mencakup native department → committed503 → retry → satu record → edit PM52 →
histori tiap revisi → form390px. Identity/session bootstrap UI disediakan fixture,
bukan login user/Maximo. Hasil lokal dan identitas patch ada di evidence handoff.

Aktivasi berikutnya memerlukan izin publikasi/integrasi source FE+BE yang sama dan
pemeriksaan kompatibilitas controller terhadap target baru. Binary/source lama
44bc tidak membaca kontrak1.3; rollback harus menolak format baru yang tak terbaca,
bukan menghapus rekam. Tidak ada perubahan launcher dalam patch ini. Browser utama
masih menunggu handoff warning sertifikat dan login user; trust tidak diubah.


## Package continuation — 21 October 2026

The preceding item1 checkpoint retains its local-only historical authorization.
The subsequent PO request authorizes the reviewed item1–3 package branch/draft PR,
without merge or activation. See [NADI-PDM-MANUAL-FOLLOW-UP-01](nadi-pdm-manual-follow-up-01.md).
Package1.4 includes manual analysis and reported-unverified SR references; the
original item1 worktree/patch remain preserved.
