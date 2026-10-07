# NADI product roadmap — main quest

NADI — **Navigasi Analitik Data dan Informasi**, Reliability / Engineering
Intelligence Platform pembangkit. Implementasinya berada di
`reliability-cockpit/`; shared collectors tetap menjadi kemampuan platform.
Basis audit awal: `main ef07a26`, 7 Oktober 2026; FIX-01 direkonsiliasi dengan
`main 52c67d4` setelah PR #13/#14 merged. [Repository Status](REPOSITORY-STATUS.md)
memuat full SHA, merged PR dan pekerjaan di luar `main`.

## Product phases

| Phase | Scope | Status |
|---|---|---|
| 0 — Factual Foundation | Maximo → canonical contracts → Mart → factual NADI views | **COMPLETE**, release faktual `v0.1.0-rc.1` |
| 1 — Evidence Expansion | source semantics, governed identity, PI evidence dan integration trust | **CURRENT / PARTIAL** |
| 2 — Collaborative Engineering Workspace | investigation, evidence, collaboration, review dan decision history | **PLANNED** |
| 3 — Diagnostic / PdM Intelligence | finding, patterns, diagnostic assistance, explainable PdM | **PLANNED**, evidence-gated |
| 4 — Recommendation & Action Loop | engineering review → action → existing maintenance → effectiveness | **PLANNED**, no implicit source write-back |
| 5 — Organizational Learning | accumulated engineering knowledge and maintenance outcomes | **PLANNED** |

### Phase 0 — completed factual scope

PR [#1](https://github.com/johnd-creator/reliability-knowledge-starter/pull/1)
merged as `af1d9bd`; tag `v0.1.0-rc.1` resolves to that commit and is an ancestor
of the audited `main`. Canonical contracts (`28a0d47`), Mart persistence
(`6ec2b22`, `9e6f2b5`), Mart queries (`7576214`), and local projection (`fa1bc05`)
are also on `main`.

The nine factual routes cover Executive Overview, Asset Reliability,
Maintenance, Maintenance Investigation, FMEA, RCFA, Asset Health, Overhaul and
Data Trust. Release QA evidence is in
[NADI V1 Release Candidate](../reliability-cockpit/docs/nadi-v1-release-candidate.md)
and [Product Readiness](../reliability-cockpit/docs/nadi-v1-product-readiness.md).
QA was recorded for that release; it is not rerun or a live-runtime certificate
by this documentation task.

Completeness is scoped: Registered Reliability Assets, local Collector
projection, controlled Mart populations and technical context remain distinct.
Repeat Activity is not Repeat Failure. Health/Wellness/Risk scores, RPN,
reliability failure KPIs and PdM remain gated. Legacy KPI code does not unlock
these metrics in the factual NADI decision surface. Runtime wiring debt remains
even though product foundation was accepted.

### Phase 1 — evidence already merged

Discovery completion means the bounded work was performed and its findings
recorded, not that all business semantics became verified.

| Workstream | Git evidence | Implemented evidence / remaining boundary |
|---|---|---|
| Asset Health discovery | PR #2, `6687f07` | MX-013A/B: Engineering Judgement metadata advanced; report lineage and Wellness/ACR/MPI meanings still partial/unknown |
| FMEA item discovery | PR #3, `596d799` | IPFMEAITEM → FMEA parent verified; item semantics/RPN policy and product projection not accepted |
| Maintenance failure semantics | PR #4, `44868d8` | Direct WO fields observed; governed failure identity/hierarchy and Repeat Failure still unknown |
| RCFA relationships | PR #5, `2c73b03` | Direct source Asset field and RCFA→FDT verified; NADI canonical Asset link remains unresolved; WO/failure-event meaning not verified |
| DOMINION Overhaul | PR #6, `2163be2` | Inspection and Scope-PM/WO paths advanced; KPI/progress/completion semantics still incomplete |
| Central PI topology + identity investigation | PR #7, `74e5dc3` | AF→PI Point and timestamp/quality/unit shapes verified in bounded samples; native Maximo→AF key not found in bounded probe |
| Maximo WO recency | PR #13/#14, main `52c67d4` | Bounded floor recovery, automatic cursor, cheap scheduled reads, local Mart and registered BSR/IP NADI CURRENT; MXR-004 moving-source/global concurrency remains PARTIAL |
| Governed Asset↔AF registry | PR #8, `1c24a78` | Existing Mart relation, explicit lifecycle, UNMAPPED/MAPPED/AMBIGUOUS resolution |
| Controlled mapping administration | PR #9, `883534c`; PR #10, `ef07a26` | Atomic PROPOSED import, human verify/retire, provenance; SQLite timestamp test correction merged |

Source findings are detailed in the linked
[Repository evidence catalog](REPOSITORY-STATUS.md#merged-evidence-catalog).
New discovery has not been projected into every canonical contract or product
view. Update those boundaries through separate reviewed technical changes;
never overwrite unknowns from labels or branch existence.

### Phase 1 — remaining acceptance

- NADI-PI-001 governed PI source boundary is **IMPLEMENTED / MERGE-CANDIDATE**
  on PR #12 / `codex/nadi-pi-001-governed-source-adapter`; originally based on
  `main a8393ba`, now incorporating `main 52c67d4` via normal merge.
  Review/merge and deliberate existing-store migration 004 remain pending. See
  [offline implementation evidence](../pi-collector/docs/nadi-pi-001-implementation.md).
- Approve a bounded real/pilot Registered Asset ↔ AF mapping set. Code and
  synthetic tests do not establish that production mappings are populated.
- Project PI measurement evidence into NADI with identity lineage, units,
  source timestamp and quality flags; define authorization and failure behavior.
- Make coverage, unmapped/ambiguous, stale/degraded and integration status
  visible without substituting business-record dates for collection freshness.
- Resolve required Mart deployment wiring and read-only role/migration readiness
  before pilot operation. Do not create a new Mart DB.
- Record Phase 1 acceptance against a scoped pilot, source-access authorization,
  quality/time rules, failures, contract compatibility and engineering review.
  Do not open diagnostic/scoring capabilities merely to finish this checklist.

### Phase 2 — collaborative engineering workspace

```text
problem → asset workspace → collect evidence → engineering investigation
        → collaboration / peer review → published engineering insight
        → decision log
```

The existing factual Asset workspace is a foundation, not implementation of
this collaboration lifecycle. Later work defines ownership, evidence snapshots,
versions, access control, review and publish rules. Investigation and decision
history must remain attributable and survive recomputation. No workflow tables,
forms or write endpoints are added by this roadmap task.

### Phase 3 — diagnostic / PdM intelligence

```text
Trend Detection → Condition Finding → Failure Pattern
                → Diagnostic Assistance → PdM Insight → Asset Health / Risk
```

Prerequisites: accepted measurement semantics, mapped evidence, units, time
alignment, quality/freshness rules, versioned thresholds/model, validation and
explainability. Missing/bad/stale data must not imply healthy equipment.

### Phase 4 — recommendation and action loop

```text
Finding → Recommendation → Engineering Review → Action
        → Existing WO / Maintenance → Execution → Closure → Effectiveness Review
```

Actions may refer to existing Maximo Work Orders. Direct creation/update of
Maximo WO requires a separately authorized and governed write-back architecture;
this vision does not authorize it. Human decisions must not be overwritten by
recomputed recommendations.

### Phase 5 — organizational learning

Equipment and failure history + PI condition + FMEA + RCFA + investigations +
recommendations + maintenance results become organizational reliability
knowledge. Preserve provenance, evidence versions, review decisions, outcome
feedback and reusable engineering insights. This is a long-term product goal,
not an already deployed knowledge engine.

## Next execution sequence

### 1. NADI-PI-001 — Governed PI Source Adapter (implemented / merge-candidate)

Offline integration originally started from verified `main a8393ba`, not the
mixed feature branch. FIX-01 incorporates latest `main 52c67d4` without
rewriting published history and corrects the quality-field migration to 004.
Candidate `d23f848` was selectively adapted, with lineage, streaming limits and lossless source values strengthened; `0c800da` was not imported.
No live source access, migration execution or NADI projection is claimed.

Original acceptance scope retained for review: review `d23f848`
as an implementation candidate: bounded verified AF target validation,
same-origin link guards, typed values and richer PI quality fields.
Integrate only the reviewed source-boundary scope, not NK/data/deployment
changes from `0c800da`. Decide the compatible shared contract exposure and
schema migration (quality-field migration is not proof it has run in production).
Source credentials stay in PI Collector, not NADI.

Acceptance for the technical PR:

- explicit governed target from the existing registry boundary; reject
  PROPOSED/RETIRED/UNMAPPED/AMBIGUOUS and never auto-select or fuzzy-match;
- bounded operations, origin validation, rate/response caps and runtime-only
  source config retained; no broad rediscovery or implicit history download;
- normalized evidence preserves value type, units, timestamp and source quality;
  digital/text/bool/null are not silently numeric zero;
- hermetic contract and failure-path tests, compatibility/migration review,
  clear ownership between collector source boundary and future orchestration;
- identify what remains for NADI orchestration/projection. Do not claim live
  NADI PI ingestion from a collector class alone.

No source requests are necessary for the initial offline technical review.
The previous HTTP 401 credential investigation remains deferred by the user;
resume live pilot access only when explicitly requested.

### 2. NADI-IDN-002 — pilot verified Asset ↔ AF mapping

Use controlled dry-run/import → PROPOSED → human verification → VERIFIED.
Bound the pilot population, approved evidence and units; test unmapped and
ambiguous states. Do not import a whole AF hierarchy or seed plausible names.
Address runtime fix `7149455` against current main/feature overlap in a separate
runtime PR before executing the pilot.

### 3. NADI-ING-PI-001 — PI evidence projection

Connect accepted mappings to approved collector evidence APIs/contracts and
project a bounded read model using existing owning stores. Preserve mapping
version, source identity/time/quality, idempotency and partial-failure behavior.
No new DB or diagnostic scores. Keep technical PI attributes distinct from
governed NADI Asset signals.

### 4. NADI-INTEGRATION-STATUS — trust in integration

Expose coverage, source last-success/attempt, collection lag, gaps, mapping
readiness and degraded state. Separate source freshness from business recency,
Mart projection freshness and API availability.

### 5. NADI-PHASE-1-ACCEPTANCE

Review the scoped end-to-end pilot and failure evidence, publish acceptance and
remaining domain gaps, then explicitly authorize Phase 2 planning/implementation.
[M0–M8](reliability-cockpit-platform/05-roadmap-implementasi.md) stays the
engineering implementation map underneath these product phases. M5 derived
intelligence and M7 PdM/actions now belong to later phases, not Phase 0 gaps.
