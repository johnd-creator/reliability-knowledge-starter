# Platform roadmap — mulai di sini

## Current onboarding — 2026-10-10

Start with [NADI Context](../NADI-CONTEXT.md), [PRD](../PRD.md),
[Design System](../DESIGN-SYSTEM.md), [UI specification](../docs/design/NADI-UI-SPEC.md),
[official product roadmap](NADI-ROADMAP.md), [Repository Status](REPOSITORY-STATUS.md)
and [append-only DEV-LOG](../DEV-LOG.md). Root/scoped AGENTS safety rules apply first.
Verified main f54643f3510bf505628a1400024784faab46e496 includes Engineering foundations;
PR62/63 remain open. Primary development frontend is https://localhost:3000 on
explicit PR62 preview; documentation work does not switch it.

The paragraphs below preserve the 7–8 October audit sequence. Their “current” and
“next” labels are historical; use the linked latest roadmap/status checkpoint.

**Power Plant Data Platform** memiliki shared data foundation, **NADI sebagai
main quest**, dan **NK sebagai child roadmap**. Audit PLATFORM-ROADMAP-001
menggunakan `origin/main` pada `ef07a263b122d30e7dbec451e6094f9016b603c3`,
7 Oktober 2026. Branch implementation yang belum merged tidak dihitung sebagai
kemampuan `main`.

## Current Phase-1 acceptance — 2026-10-08

Read [Phase-1 acceptance](NADI-PHASE-1-ACCEPTANCE.md) and
[operational report](../reliability-cockpit/docs/nadi-phase1-runtime-acceptance-001.md).
PR20 merged main c2fb0fc is deployed; existing Mart004/reader grants, local PI
observation and NADI integration-status/UI/readiness are ACCEPTED. Product remains
BLOCKED: HUMAN_CROSSWALK_REQUIRED, FRESHNESS_POLICY_PENDING and subsequent
signal/canary/real-evidence acceptance. Production mapping0/0, signals0/evidence0;
Phase1 stays CURRENT/PARTIAL. Historical paragraphs below retain their dated
scope, not current candidate/absent-schema status.

## Baca dalam urutan ini

| Dokumen | Pertanyaan yang dijawab |
|---|---|
| [Platform Vision](PLATFORM-VISION.md) | Apa platform ini, siapa pemilik data, siapa konsumennya? |
| [NADI Roadmap](NADI-ROADMAP.md) | Phase 0–5, apa yang selesai, dan technical PR berikutnya? |
| [Engineering Roadmap M0–M8](reliability-cockpit-platform/05-roadmap-implementasi.md) | Bagaimana product roadmap diimplementasikan? |
| [NK Roadmap](NK-ROADMAP.md) | Mengapa NK ada, apa yang bekerja di branch, apa yang belum siap? |
| [Repository Status](REPOSITORY-STATUS.md) | Baseline, PR, branch debt, dokumen stale, governance? |

**Posisi NADI:** Phase 0 COMPLETE + CURRENT untuk scope faktual; Phase 1
CURRENT / PARTIAL untuk ekspansi evidence. **NADI-PI-001: MERGED** via PR #12,
`main 3e981a3`. Maximo WO acceptance PR #13/#14 tetap CURRENT dalam registered
BSR/IP population; MXR-004 tetap PARTIAL.
**NADI-PI-RUNTIME-001:** ACCEPTED, PR #15 MERGED; existing-store migration004,
stored API compatibility and one snapshot owner remain accepted.
**NADI-RUNTIME-002:** MERGED via PR #16 (`main a1c9270`), existing Mart governance
and SELECT-only reader ACCEPTED.
**Current:** [NADI-IDN-002A-R2](../reliability-cockpit/docs/nadi-idn-002-round2.md),
from merged PR17/main83c529f. Evidence/proposal PARTIAL, human verification
PENDING. Three exact hypotheses remain insufficient; BFPT stays rejected.
AF lookup configuration exists, but no exact Asset identity bridge was obtained.
**HUMAN CROSSWALK REQUIRED** before small PROPOSED import and NADI-IDN-002B
human verification/governed canary. NADI-ING-PI-001, NADI-INTEGRATION-STATUS and
NADI-PHASE-1-ACCEPTANCE remain pending; Phase1 CURRENT/PARTIAL.
NK tetap child roadmap; technical PI collection bukan governed Asset signal.

## Aturan status

- `COMPLETE`: scope yang disebutkan mempunyai bukti merged/accepted; bukan
  klaim bahwa semua exit criteria platform atau deployment produksi terpenuhi.
- `PARTIAL`: artefak ada, tetapi dependency/acceptance tertentu belum terbukti.
- `UNMERGED`: implementasi/bukti hanya ada pada branch di luar baseline `main`.
- `PLANNED`: product intent, belum dinyatakan selesai.
- `NEEDS_REVIEW`: bukti tidak cukup atau ada konflik yang harus diselesaikan.
- `HISTORICAL` / `SUPERSEDED`: simpan konteks, tetapi jangan pakai sebagai status aktif.

Status implementasi, verifikasi sumber, business semantics, dan kesiapan runtime
adalah empat hal berbeda. Discovery yang selesai dapat tetap menghasilkan
`UNKNOWN`; unit test passing tidak membuktikan live mapping atau pilot.

## Hierarki dan pemeliharaan

Dokumen di atas menjadi entry point otoritatif untuk vision/status/sequence.
[Proposal 20 Agustus](reliability-cockpit-platform/README.md) tetap menyediakan
backlog/detail desain. Bagian status M0–M8 terbaru menggantikan tabel snapshot
lamanya; backlog tidak dihapus. Scoped domain/discovery docs mengatur semantik
lebih rinci dan tidak ditimpa oleh roadmap aspiratif.

Setiap technical PR menyebut task ID, evidence/acceptance dan roadmap yang
terpengaruh. Saat status berubah, perbarui dokumen pemiliknya serta tanggal/SHA
basis audit, bukan menyalin tabel status ke banyak dokumen.
