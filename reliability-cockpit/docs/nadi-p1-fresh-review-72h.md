# NADI-P1-FRESH-REVIEW-72 H — audit source-free

**Verdict monitoring 72 jam: PARTIAL. Product readiness: UNKNOWN.**
Audit selesai dengan findings dan keterbatasan evidence; tidak ada policy action.
Phase 1 tetap CURRENT/PARTIAL, tidak dipromosikan menjadi COMPLETE.

## Window, baseline dan keputusan yang diperlukan

- Aktivasi: **8 Oktober 2026, 21:45:26.619585 WIB**.
- Cutoff tepat: **11 Oktober 2026, 21:45:26.619585 WIB**, 259.200 detik/72 jam.
- Cutoff ekstraksi histori terbaru: **12 Oktober 2026, 05:35:14.695531 WIB**.
- Snapshot readiness: **12 Oktober 2026, 05:36:07.692601 WIB**.
- Checkpoint Product Owner: **12 Oktober 2026, 20:00 WIB**.
- Hard expiry: **13 Oktober 2026, 00:00 WIB**, manual; tidak ada scheduler otomatis.

Pada cutoff ekstraksi, review terlambat 7 j 49 m 48 s; checkpoint berjarak 14 j 24 m 45 s
dan expiry 18 j 24 m 45 s. Angka countdown adalah pada waktu observasi, bukan countdown
live. Cutoff 72 h tidak mengubah hard expiry atau mengotorisasi extension otomatis.

Latest verified main: `3ad0da813db13c833ba513c0727becde1c73a081` (PR73 merged).
Preview frontend: `f06abce76f8ef9b967ee5b1c2e0802112d77b056`, clean/not stale;
QA backend: `b348235ce6f82c84873a65344ad2ef5fe276987d`. Preview tidak diganti.
Image label API faktual bersifat abbreviated/inherited; tidak digunakan sebagai
bukti full source SHA. Enam modul runtime monitoring/readiness/reader cocok byte
per byte dengan reviewed GOV03 source dan main terbaru. Ini verifikasi scope,
bukan attestation seluruh source API atau klaim deployment main.

Rekomendasi **CORRECTIVE REVIEW REQUIRED / INSUFFICIENT EVIDENCE** untuk menyatakan
ketiga threshold sudah layak menjadi SLA jangka panjang. Owner perlu memutuskan
langkah sebelum expiry; tidak ada rekomendasi yang dieksekusi oleh audit ini.

## Authority, metode dan coverage

[Register aktivasi](nadi-p1-fresh-gov-03-activation-register.json) dan
[acceptance GOV03](nadi-p1-fresh-gov-03.md) tetap historical dan tidak ditulis ulang.
[Ringkasan numerik/time-only](validation/nadi-p1-fresh-review-72h-summary.json)
memuat hasil audit. Evidence asli, raw log, topology dan prosedur recovery privat
tetap disimpan secara privat; tidak disertakan dalam PR.

| Evidence | Coverage dan pembatasan |
| --- | --- |
| E1 — local Maximo collect_run | Stored WO cycle start/end/outcome, seed last full success sebelum aktivasi, seluruh completion sampai cutoff; READ ONLY transaction |
| E2 — local PI pi_collect_run | Scope snapshot, expected population 433, full/partial outcomes, crossing-boundary cycles; READ ONLY transaction |
| E3 — retained worker Docker logs | 836 Maximo dan 322 PI completion summaries cocok satu-per-satu dengan E1/E2, bukan hanya jumlah; log delay masing-masing ≤0,034 s dan ≤0,173 s |
| E4 — retained projector Docker logs | 857 complete paired reports; pre-window success tersedia; exact historical per-domain commit clocks tidak diarsipkan |
| E5 — source-free local aggregate | Integration status, reader-compatible schema, governed pilot counts, current technical registry/snapshots; kemudian pure nine-gate evaluator pada captured document |
| E6 — historical activation evidence | Initial policies, initial pilot/evidence/state; effective API container tetap sama sejak aktivasi dan delapan policy states sesuai register |
| E7 — local host journal | Satu suspend 8 m 14 s pada 9 Oktober 21:03:18–21:11:32 WIB, mendukung activity gap; causal attribution setiap error tetap belum terbukti |

Graph generation 24 Agustus stale/missing untuk scope ini; semua material contract
diverifikasi dari source aktual. Local observation adapter target diverifikasi
mengarah ke collector API internal, bukan source asli; endpoint hanya query store.
Tidak menjalankan CLI collector, retry, discovery, replay, backfill atau source GET.

Count cycle adalah **recorded cycles**, bukan jumlah seluruh HTTP request atau
bukti tidak ada unrecorded crash. Threshold mengevaluasi age sejak **last complete
successful activity**, bukan changedate Work Order, source value age atau kesehatan.
Interval adalah (activation,cutoff] untuk completion, [activation,cutoff) untuk start.
PI mempunyai 1 crossing-in dan 1 crossing-out; jumlah start/completion sama 322 tetapi
cohort berbeda. Crossing-out tidak dipakai sebagai bukti sukses sebelum cutoff.

Freshness reconstruction: pada setiap success clock berubah; stale dimulai ketika
age>threshold hingga success berikutnya, di-clip ke window. State CURRENT tepat pada
age=threshold. Seed sukses sebelum aktivasi tersedia, sehingga unknown clock time
Maximo/PI yang direkonstruksi 0 detik. Ini **bukan** count alert yang benar-benar tampil.

## Statistik 72 jam yang terbukti

| Komponen | Recorded starts | Completed | Full success | Non-full / reported errors | Verdict |
| --- | ---: | ---: | ---: | --- | --- |
| Maximo WO | 836 | 836 | 822 (98,33%) | 14 partial /14 errors | PARTIAL |
| Mart asset | UNKNOWN | 857 reports | 857 completed=true | 0 failed reports; unreported attempts UNKNOWN | PARTIAL evidence/timing |
| Mart maintenance | UNKNOWN | 857 reports | 857 completed=true | 0 failed reports; unreported attempts UNKNOWN | PARTIAL evidence/timing |
| PI snapshot 433 | 322 | 322 | 304 (94,41%) | 18 partial /291 attribute-level errors | PARTIAL |

Maximo: maksimum 6 partial berturut-turut;12 SOURCE_ERROR/MaximoAuthError dan 2
SOURCE_ERROR/ConnectionError tercatat.20.600 row-seen dan 795 upsert events adalah
jumlah proses berulang, **bukan** distinct WO, failure count atau maintenance approval.
PI: semua completed cycles melihat 433 atribut;10 cycle 432/433+1 error, delapan lainnya
424/9,419/14,413/20,423/10,425/8,378/55,344/89,357/76 (collected/errors).0 aborted;
139.135 collected events across cycles, bukan unique equipment. Maksimum 4 partial
berturut-turut. Tidak mengubah partial menjadi full success.
Maintenance projector mencatat 1.460 skipped-missing-equipment occurrences berulang,
bukan 1.460 unique WO. Null-source-changed reports 0, unproven-scope skips 0.
Controlled domain loads/mappings tidak diperbaiki atau dilonggarkan.

| Timing detik | Median durasi cycle | P95 durasi | Maks durasi | Median full-success gap | P95 gap | Maks gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Maximo | 6,943 | 14,677 | 112,691 | 307,943 | 314,474 | 2307,878 |
| PI | 486,850 | 570,158 | 1218,945 | 789,251 | 878,146 | 5749,952 |
| Paired Mart report | UNKNOWN | UNKNOWN | UNKNOWN | 301,797 | 302,202 | 765,795 |

P95 memakai nearest rank. Maximo recorded-start gap maksimum 770,598 s; PI 1518,959 s.
Interarrival gap bukan missing-source-sample count atau continuous PdM sampling.

## Threshold dan stale windows

| Approved threshold | Reconstructed exceeded windows | Waktu exceeded | Last full success age pada cutoff | Penilaian |
| --- | ---: | ---: | ---: | --- |
| Maximo 660 s | 6 | 2190,086 s =36 m 30,086 s (0,845% window) | 253,266 s | CURRENT activity pada cutoff;72 h PARTIAL |
| PI 1800 s | 3 | 6279,663 s =1 j 44 m 39,663 s (2,423%) | 1529,433 s | Freshness clock CURRENT tetapi latest completed 432/433 dengan 1 error; activity gate pada cutoff tidak boleh diasumsikan PASS |
| Mart 660 s | 1 paired-log proxy gap | ≈105,795 s per domain; jangan dijumlahkan untuk paired downtime | ≈140,713 s paired-report age | Last reports mendukung recent completion; exact per-domain stale seconds UNKNOWN |

Mart report timestamp diambil **setelah** kedua commit. Nilai≈105,795 s adalah
estimasi clock proxy, bukan exact original last_success_at setiap domain. Log JSON
emission spread≤0,002 s tidak membatasi delay antara domain commit dan emission.
Tidak ada histori per-pass state yang cukup untuk merekonstruksi exact clock itu.

### Reconstructed Maximo stale episodes — WIB

- 2026-10-09T17:52:34.770240+07:00 → 2026-10-09T17:52:35.680182+07:00: 0.909942 s.
- 2026-10-09T21:14:08.128565+07:00 → 2026-10-09T21:16:01.260529+07:00: 113.131964 s.
- 2026-10-10T02:09:28.643250+07:00 → 2026-10-10T02:14:42.901896+07:00: 314.258646 s.
- 2026-10-11T01:42:17.965901+07:00 → 2026-10-11T01:42:18.366814+07:00: 0.400913 s.
- 2026-10-11T01:53:18.366814+07:00 → 2026-10-11T02:20:46.245185+07:00: 1647.878371 s.
- 2026-10-11T07:34:20.731941+07:00 → 2026-10-11T07:36:14.238543+07:00: 113.506602 s.

### Reconstructed PI stale episodes — WIB

- 2026-10-09T08:43:12.688222+07:00 → 2026-10-09T09:49:02.640428+07:00: 3949.952206 s.
- 2026-10-09T21:28:04.383375+07:00 → 2026-10-09T21:46:54.679194+07:00: 1130.295819 s.
- 2026-10-11T07:33:32.172425+07:00 → 2026-10-11T07:53:31.587052+07:00: 1199.414627 s.

Dua window Maximo subdetik(0,910 s/0,401 s) menunjukkan threshold-edge episodes;
tanpa sampled alert history tidak dapat diklaim sebagai false alert maupun alert
yang benar-benar terlihat. Host suspend memberi konteks satu common activity gap,
tetapi tidak membuktikan akar masalah semua authentication/connection/PI failures.

## Timestamp anomalies, quality dan false alerts

- E1/E2 completed cycle timestamps: null start 0, finish-before-start 0, duplicate
finished_at 0, future versus audit clock 0; stored starts dalamwindow tanpa recorded
finish 0. Ini tidak membuktikan setiap unrecorded attempt berhasil.
- Latest stored technical snapshot pada 12 Oktober 05:36:07 WIB:433 snapshots,
**54 epoch source timestamps**,22 BAD/questionable signals, null source 0,
future source 0, null/future collected 0, source-after-collected 0, unknown quality 0.
- Preactivation snapshot 8 Oktober 20:48:16 WIB juga mencatat 54 epoch dan 18 bad-quality;
activation observation 18 bad-quality.22 saat audit bukan klaim 22 anomalies sepanjang
72 h atau tepat cutoff. Snapshot table latest-only; per-signal transitions sepanjang
window dan snapshot state tepat cutoff **UNKNOWN**.
- Tidak ada retained sampled alert/event stream atau adjudikasi operator untuk
false positives/false negatives, duration setiap alert, atau alert delivery gaps.
**False-alert count/rate dan historical alert gaps: UNKNOWN**, bukan 0.
- Epoch invalid untuk condition-use; Good quality≠HEALTHY; full 433/433 acquisition
tidak mengesahkan physical condition, portable/PI comparability atau method rules.

## Sembilan readiness gates — snapshot terbaru, bukan retroactive PASS

Observed_at: **12 Oktober 05:36:07.692601 WIB**. Pure evaluator pada source-free
captured integration document: **8 PASS /1 UNKNOWN**, overall **UNKNOWN**.

| Gate | Latest verdict | Reason | Batas evidence 72 h/cutoff |
| --- | --- | --- | --- |
| P1-MAXIMO-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT | Recorded completion clocks dapat dihitung; enam stale windows dalam 72 h |
| P1-MART-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT | Paired reports tersedia; exact commit clock history UNKNOWN |
| P1-PI-COLLECTOR-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT | Latest snapshot PASS tidak menghapus 18 partial; cutoff latest cycle partial |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE | Reader schema sekarang compatible; tidak ada full historical nine-gate snapshots |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE | Condition query schema compatible; bukan method/policy acceptance |
| P1-IDENTITY-MAPPING-READY | PASS | VERIFIED_PILOT_AVAILABLE | VERIFIED1/PROPOSED0; mapping bytes sesuai activation baseline |
| P1-SIGNAL-SELECTION-READY | PASS | APPROVED_PILOT_SIGNALS_AVAILABLE | Approved signal 1; selection bytes sesuai baseline |
| P1-CONDITION-PROJECTION-READY | UNKNOWN | UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS | Condition source/projection policy tetap UNSET; source/projection freshness UNKNOWN |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID | Current aggregate schema valid; continuous historical route availability UNKNOWN |

Full nine-gate result tepat cutoff dan continuous 72 h history **UNKNOWN** karena
snapshot tersebut tidak diarsipkan. Tidak menempelkan current schema/coverage onto
cutoff lalu mengklaim canonical historical evaluation. Three activity reconstructions
di atas terpisah dari full nine-gate/availability contract. Initial/final GOV03
7 PASS/1 PARTIAL/1 UNKNOWN tetap bukti 8 Oktober, bukan bukti 11 Oktober.

Bounded pilot tetap 1 VERIFIED mapping,1 approved signal,1 latest/state. Mapping,
selection, accepted condition evidence dan projection state cocok tepat dengan
activation baseline. Technical registry 490 total/433 active dan 433 snapshots sekarang;
tidak meratakan 845 Registry assets menjadi mapped atau condition-assessed.
Condition-use-age, engineering validation, operational readiness dan actual UAT
tetap berbeda dari collector freshness dan UI/CI readiness.

## Recent observation terpisah dari 72 h

Window **11 Oktober 21:45:26.619585 →12 Oktober 05:35:14.695531 WIB**:
Maximo 91 completed/85 full/6 partial/6 errors; PI 36 completed/32 full/4 partial/78 errors.
Ini di luar 72 h dan tidak dimasukkan ke percentage/durasi 72 h. Mart current state
dan readiness snapshot tersedia, tetapi post-cutoff per-pass Mart history tidak
diekstrak; total post-cutoff Mart attempts/success/error/gaps **UNKNOWN** pada audit.
Tidak ada klaim rollout, repair atau quality recovery dari later successful cycle.

## Review 24 h dan evidence gaps

**24-hour review: NOT VERIFIED / UNKNOWN.** Register frozen masih PENDING_FUTURE_OPERATOR_REVIEW; tidak ditemukan named review artifact atau matching Git review
commit di scope inspected saat 9 Oktober checkpoint. Ini bukan bukti bahwa percakapan
/operator review tidak pernah terjadi; bukti operator independen perlu dilampirkan.
Tidak membuat retroactive 24 h PASS atau approval baru.

Missing: exact cutoff/full historical nine-gate documents, alert samples/adjudication,
per-domain Mart historical commit/start/failure receipts, historical quality/sample
transitions, unrecorded-attempt certainty dan approved false-alert/availability SLA.
Kesesuaian threshold jangka panjang **UNKNOWN** tanpa accepted target tersebut.

## Decision matrix — rekomendasi saja, tidak dieksekusi

| Opsi | Rekomendasi/trigger | Tindakan operator yang diperlukan |
| --- | --- | --- |
| KEEP TEMPORARILY | Hanya jika Owner memilih mempertahankan monitoring dalam authorization yang sudah berlaku sampai hard expiry; bukan extension atau operational acceptance | Catat keputusan/checkpoint, pahami PARTIAL/UNKNOWN dan siapkan manual expiry control |
| CORRECTIVE REVIEW REQUIRED | Maximo authentication/connection failures, PI partial streaks, common host activity gap dan boundary timing memerlukan review | Review evidence tersimpan dan alert adjudication; source probe/retry atau policy tuning membutuhkan otorisasi terpisah |
| ROLLBACK RECOMMENDED | Fallback governance bila tidak ada explicit approved extension sebelum hard expiry; juga jika kemudian ditemukan material drift | Fauzi harus membuat keputusan dan memakai approved private procedure; audit ini tidak menjalankan atau mengungkapkan prosedur privat |
| INSUFFICIENT EVIDENCE | False alerts, full historical gate history dan condition-use freshness belum terbukti | Jangan klaim PASS/Phase 1 COMPLETE; minta evidence/operator/engineer acceptance secara terpisah |

**Checkpoint 20:00 WIB menyisakan empat jam sebelum expiry.** Owner harus memilih
kelanjutan yang diotorisasi atau tindakan expiry sebelum 00:00 WIB. Dokumen bukan
scheduler/enforcement, tidak memperpanjang/mereset policy. Semua legacy dan kedua
condition thresholds tetap UNSET; tidak diubah menjadi 1800 atau threshold teknis.

## Safety dan perubahan task

No policy drift terdeteksi:660/660/1800 dan 5 UNSET sesuai register; running canonical
API container/config tetap sama sejak activation. During-audit preservation PASS:
35 container identities/start/restart counts, frontend dan QA process metadata,
5 PNG dan 23496711.xls,34 historical evidence bytes/mtime dan accepted pilot data/state
terpelihara. Worktree aktif tidak di-switch/clean; branch audit terisolasi.

Task-attributable original-source GET0, collector retries 0, database writes 0,
migration 0, restart 0, acquisition/replay 0, policy change/extension/rollback 0.
Normal autonomous background collection tetap berjalan; itu bukan source execution
oleh audit ini. Local aggregate GET dan bounded READ ONLY SQL tidak memicu acquisition.

Perubahan Git hanya report/derived summary dan reference dokumentasi bertanggal.
Tidak menjalankan operational test fixtures, deploy, production CI-as-runtime claim,
atau merger otomatis. Status deliverable **PARTIAL** karena evidence gaps, bukan
karena policy sedang diubah. Tindak lanjut dibatasi pada keputusan Owner dan
pemenuhan evidence; tidak mulai fitur/Phase 3 atau task operational berikutnya.
