# NADI product roadmap — main quest

## Latest runtime promotion — NADI-IDN-002B-R1-FIX-01 (8 October 2026)

**PASS — bounded first real Coal Flow A evidence pilot.** PR22 MERGED;
authoritative source `478cce1958ab5800ce21d7b1e93b83ff43c1ac19` deployed to
Cockpit API/operator tooling only. No application repair or unmerged code was
needed. Existing control checkout, private configuration and all accepted
worker/PI/web/DB images remain preserved. Image ID plus serving-source checksum
prove the reviewed 512-character contract; actual 203 and synthetic 512 accepted,
513 rejected. Historical Compose revision label is not the image source SHA.

Fauzi's existing 2026-10-08 approval for precisely Coal Flow A / `coal_flow`
is now persisted through canonical administration. Exactly one approved signal,
one latest condition evidence and one projection state; VERIFIED mapping 1 /
PROPOSED 0 unchanged. No new identity review or approval was requested.
Five guarded current-source GETs (six cumulative including R1 identity GET)
produced NUMERIC evidence with original `Ton/h`, time/quality/lineage; four
canonical schema/model checks passed. Real replay writes 0 and preserves every
condition row, source/projection timestamp, state and API document.

[Operational evidence](../reliability-cockpit/docs/nadi-idn-002b-coal-feeder-a.md#r1-fix-01--reviewed-runtime-promotion-and-first-real-evidence)
records backup, immutable image, counts, actual response, replay, API/UI and
all nine gates. Coverage 845 registered / 1 VERIFIED / 1 approved-signal asset /
1 projected asset. Source policy remains blank; Good is signal quality only.
Actual readiness: governance/schema/identity/selection/status PASS; three
collector/Mart freshness gates UNKNOWN; projection gate UNKNOWN due
UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS. Overall UNKNOWN, require-pass exit 2.
The measured real projection is accepted; freshness-qualified readiness is not.

**PHASE 1 SOFTWARE RUNTIME FOUNDATION: ACCEPTED.**
**BOUNDED REAL PILOT: ACCEPTED.**
**PHASE 1 PRODUCT ACCEPTANCE: NOT PASS — FRESHNESS_POLICY_PENDING.**
Phase 1 remains CURRENT/PARTIAL. Identity approval, signal approval, bounded
canary, controlled handoff and real replay are complete for this one asset only.
Other equipment identities remain unverified. The live technical inventory
remains 433 active; technical BAD_QUALITY 18 and epoch timestamps are independent
of this Good pilot evidence. PI_AF_KKS_LOOKUP_UNRESOLVED remains open;
BFPT stays REJECTED/FROZEN/DO NOT VERIFY.

Task-attributable mutations: one signal selection and one evidence/state batch;
replay 0 writes, mapping mutations 0, source writes 0. Collector/web restarts,
DDL/history/discovery/registry/reset/volume recreation/new operational DB,
CEMS/NK changes and credential exposure 0. Only cockpit-api replaced once;
22 other existing container identities remain unchanged. No recurring condition
projection was enabled. No unnecessary repair PR; documentation checkpoint
is separate from deployed source. Earlier checkpoints below are historical.

Next: approve defensible collector/source/projection freshness policies and
controlled refresh/acceptance procedure, then rerun actual readiness without
weakening gates. No new mapping, broader signal selection or health scoring
is implied by this successful one-signal pilot.

## Historical R1 checkpoint — signal approved, runtime contract repair pending (8 October 2026)

**PARTIAL — CODE_ACCEPTANCE_REQUIRED.** Fauzi directly approved exactly one
Coal Flow A / `coal_flow` signal on 2026-10-08, evidence reference
`NADI-SIGNAL-COAL-FLOW-A-20261008`. Human signal approval is now RECEIVED.
One exact guarded Attribute metadata GET proved ownership by the existing
VERIFIED Coal Feeder A AF Element. NUMERIC and local source unit `Ton/h` are
preserved; no unit conversion, engineering SLA or Hidayat signal approval is claimed.

Canonical production approval failed before DML: the exact Attribute WebId has
203 characters, exceeding the merged contract's 200-character limit. PR22
contains an additive, bounded 512-character Attribute-reference correction,
consistent Python/JSON contracts and synthetic SQLite/PostgreSQL/API acceptance.
No candidate application code was deployed. This is a concrete independent
SOFTWARE/RUNTIME blocker for this pilot; historical foundation acceptance below
remains evidence of its earlier bounded validation.

Production remains PROPOSED=0 / VERIFIED=1, selected signals=0, condition
latest/state=0/0. Source canary/handoff/projection/replay NOT RUN. R1 PI source
GET=1 (identity metadata), Maximo GET=0; business writes/mapping mutation/
signal persistence/projection/deployment/restart/DDL=0. Blank freshness policies
remain UNKNOWN / FRESHNESS_POLICY_PENDING. Identity gate PASS for this pilot,
signal/projection BLOCKED NO_APPROVED_SIGNALS; overall readiness BLOCKED.
**PHASE 1 PRODUCT ACCEPTANCE: BLOCKED; Phase 1 CURRENT/PARTIAL.**

[Full R1 evidence and test commands](../reliability-cockpit/docs/nadi-idn-002b-coal-feeder-a.md#r1--explicit-coal-flow-a-signal-approval-8-october-2026)
records 440 distinct Cockpit/PI/contracts test cases passing across isolated
fixtures and opt-in environments. Accepted runtime, 433 active PI attributes,
Maximo recovery floor and SELECT-only reader are preserved.
PI_AF_KKS_LOOKUP_UNRESOLVED stays open; BFPT REJECTED/FROZEN/DO NOT VERIFY.

Next: review/merge PR22's compatible contract repair, deliberately deploy reviewed
compatible consumer/operator tooling with accepted overrides, then resume the
already authorized one-signal approval → bounded governed canary → schema-valid
handoff → Mart projection/replay → API/UI/readiness. No repeat human approval is
required for the recorded scope. Approve freshness policy separately before
claiming final Phase-1 PASS. Earlier checkpoints below are historical.

## Historical pilot checkpoint — NADI-IDN-002B (8 October 2026)

[Coal Feeder A evidence](../reliability-cockpit/docs/nadi-idn-002b-coal-feeder-a.md)
records **PARTIAL**: one BSR/IP CS01 Coal Feeder A mapping is VERIFIED via
canonical dry-run → PROPOSED → explicit human-review transition.
`verified_by=Fauzi`; technical reviewer Hidayat, System Owner Boiler / Senior
Engineer, in-person verbal MATCH reported by operator on 2026-10-08.
No signed artifact or direct engineer authentication is claimed.
Production PROPOSED=0 / VERIFIED=1, ambiguity=0, approved signals=0, condition evidence=0.
**SIGNAL_APPROVAL_PENDING**: exact local Coal Flow A reference identified,
accountable meaning/use approval pending; canary/projection not run, source GET=0.
Identity gate PASS for this pilot; signal/projection BLOCKED NO_APPROVED_SIGNALS.
Maximo/Mart/PI freshness UNKNOWN with blank policy; governance/schema/status PASS.
**PHASE 1 PRODUCT ACCEPTANCE: BLOCKED**, Phase 1 CURRENT/PARTIAL.
HUMAN_CROSSWALK_REQUIRED is resolved for this one asset only; other identities
remain unverified. PI_AF_KKS_LOOKUP_UNRESOLVED is separate and unchanged;
BFPT REJECTED/FROZEN/DO NOT VERIFY. No runtime redeploy/DDL or source changes.
Next: one accountable signal approval → bounded governed canary → accepted
handoff/idempotent projection, plus approved freshness policy and actual readiness.
Older checkpoint populations below are historical as of their respective audits.

## Current Phase-1 runtime acceptance — 2026-10-08

PR20 MERGED; exact main `c2fb0fc686396e79c19f42af46694673827493a9` deployed
for PI API, NADI API and UI. Existing control checkout/accepted overrides,
workers, projector and DB volumes remain preserved. See
[operational acceptance](../reliability-cockpit/docs/nadi-phase1-runtime-acceptance-001.md)
and [authoritative Phase-1 matrix](NADI-PHASE-1-ACCEPTANCE.md).

**PHASE 1 SOFTWARE RUNTIME FOUNDATION: ACCEPTED.**
**PHASE 1 PRODUCT ACCEPTANCE: BLOCKED.** Phase 1 stays **CURRENT / PARTIAL**.
Existing Mart canonical002/003/004 ready; validated private full backup and
17 locked factual count/content comparisons passed. nadi_mart_reader remains
SELECT-only, including three empty condition relations. PI local stored-data
observation and NADI integration-status/Data Trust/Asset condition panels live.
Readiness: governance/condition-schema/status PASS; collection/projection freshness
UNKNOWN because **FRESHNESS_POLICY_PENDING**; identity/selection/projection BLOCKED
with **HUMAN_CROSSWALK_REQUIRED**. Registry845, PI active433, mapping0/0,
approved signals0 and projected evidence0. Technical BAD_QUALITY18 remains visible;
a complete collector cycle does not prove source freshness or equipment health.

NADI-IDN-002 human crosswalk remains BLOCKED / EXTERNAL; BFPT remains
REJECTED / FROZEN / DO NOT VERIFY. Runtime is ready for NADI-IDN-002B **when a
controlled human MATCH becomes available**, then attributable human verification
and separately authorized bounded governed canary. Approved signal semantics,
engineering freshness/quality policy and real bounded projection remain subsequent
product prerequisites. No production source GET/mapping/signal/projection was
initiated by runtime acceptance. Documentation/evidence PR remains OPEN/UNMERGED.

GitHub already marked PR19 MERGED separately; this differs from expected
superseded/unmerged metadata. Its211faec commit is already an ancestor of required
main; executor merged neither PR and did not deploy PR19 separately.
Older checkpoints below preserve historical evidence and do not override this state.

## Historical overnight bundle checkpoint — 2026-10-08

NADI-PHASE1-OVERNIGHT-BUNDLE-01 branches from exact unmerged PR #19 HEAD
`211faec4b0916361491d3ca8bc01ada2f0072284`, with authoritative main unchanged at
`f8c37f068102a06906cb3ca464fe08745e0351cf`. PR #19 remains OPEN/UNMERGED and its
branch is untouched. The new bundle includes that foundation and supersedes
PR #19 **only if the bundle is accepted**. Neither PR is automatically merged.

[Authoritative Phase-1 acceptance](NADI-PHASE-1-ACCEPTANCE.md) distinguishes
candidate software tests from operational deployment and human/data acceptance.
B0 freshness wiring, B1 integration status/Data Trust, B2 synthetic PostgreSQL
projection acceptance and B3 read-only Phase-1 preflight are implemented candidates.
NADI-IDN-002 human crosswalk remains BLOCKED / EXTERNAL; verification PENDING.
Production PROPOSED0 / VERIFIED0 remain unchanged; BFPT stays REJECTED / FROZEN.

**PHASE 1 SOFTWARE READINESS: PASS (candidate, bounded bundle scope)**
**PHASE 1 PRODUCT ACCEPTANCE: BLOCKED**
External identity blocker: **HUMAN_CROSSWALK_REQUIRED**. It is not the only
outstanding product prerequisite: reviewed runtime deployment, existing-Mart
condition migration 004/reader grants, explicit freshness policy, approved pilot
signals and real governed evidence acceptance are still required. No operational
condition migration or projection was performed. Phase 1 remains CURRENT / PARTIAL.
Next: senior bundle review; separately authorized runtime acceptance can proceed
independently of human crosswalk. With controlled MATCH evidence, execute
NADI-IDN-002B human verification/governed canary, then approved bounded projection.

## Historical NADI-ING-PI-001A checkpoint — 2026-10-07

PR #18 MERGED; baseline origin/main `f8c37f068102a06906cb3ca464fe08745e0351cf`.
[NADI-ING-PI-001A](../reliability-cockpit/docs/nadi-ing-pi-001a.md) implementation
**CURRENT / candidate**, synthetic acceptance **PASS**: explicit separately
approved selected signals, governed collector boundary, canonical typed evidence,
additive latest-only existing-Mart migration, read-only API/Asset view and four
independent freshness dimensions. No production deployment/projection is claimed.

NADI-PI-001 ✅ MERGED; NADI-PI-RUNTIME-001 ✅ ACCEPTED;
NADI-RUNTIME-002 ✅ ACCEPTED. NADI-IDN-002A R1/R2 evidence rounds are completed;
NADI-IDN-002 human crosswalk **BLOCKED / EXTERNAL**, human verification PENDING.
PROPOSED0 / VERIFIED0 remain unchanged. BFPT stays REJECTED / FROZEN.
Task source GET/write0, no operational DDL/restart/new DB. Phase 1 remains
**CURRENT / PARTIAL**. Next: **NADI-INTEGRATION-STATUS-001**. Real governed PI
projection still requires human identity plus signal approval and deployment review.

NADI — **Navigasi Analitik Data dan Informasi**, Reliability / Engineering
Intelligence Platform pembangkit. Implementasinya berada di
`reliability-cockpit/`; shared collectors tetap menjadi kemampuan platform.
Basis audit awal: `main ef07a26`, 7 Oktober 2026; FIX-01 direkonsiliasi dengan
`main 3e981a3` setelah PR #12/#13/#14 merged; runtime evidence ada pada NADI-PI-RUNTIME-001. [Repository Status](REPOSITORY-STATUS.md)
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
| Governed PI source adapter | PR #12, `3e981a3` | MERGED; lineage/origin guards and typed quality evidence; governed pilot/projection remain pending |
| Controlled mapping administration | PR #9, `883534c`; PR #10, `ef07a26` | Atomic PROPOSED import, human verify/retire, provenance; SQLite timestamp test correction merged |

Source findings are detailed in the linked
[Repository evidence catalog](REPOSITORY-STATUS.md#merged-evidence-catalog).
New discovery has not been projected into every canonical contract or product
view. Update those boundaries through separate reviewed technical changes;
never overwrite unknowns from labels or branch existence.

### Current controlled identity checkpoint — 2026-10-07

PR #17 MERGED14:00:31 UTC; fresh main
`83c529fd2d9ea5e3d3233f8d3b6025937a97054f`. NADI-PI-001 ✅ MERGED;
NADI-PI-RUNTIME-001 ✅ ACCEPTED; NADI-RUNTIME-002 ✅ MERGED / runtime ACCEPTED.
[Round1](../reliability-cockpit/docs/nadi-idn-002-pilot.md) remains preserved.
[NADI-IDN-002A-R2](../reliability-cockpit/docs/nadi-idn-002-round2.md): local exact
identity search then PI25/30 GETs and Maximo3/10 exact scoped GETs. Three
hypotheses remain INSUFFICIENT_EVIDENCE; BFPT stays REJECTED/FROZEN. AF KKS has
an ASSETNUM lookup expression, but no usable result or governed table authority.
No confirmed bridge, replacement, dry-run/import or production verification.
PROPOSED0 / VERIFIED0. Evidence/proposal **PARTIAL**, human verification **PENDING**.
**HUMAN CROSSWALK REQUIRED**: three-row MATCH/NOT_MATCH/UNKNOWN packet requires a
responsible reviewer/date/controlled evidence naming both exact identities.
NADI-IDN-002B follows qualified proposals and human verification; production
canary cannot start now. Phase1 stays **CURRENT / PARTIAL**.

### Phase 1 — remaining acceptance

- NADI-PI-001 governed PI source boundary is **MERGED** via PR #12 in
  `main 3e981a3`. NADI-PI-RUNTIME-001 applied migration 004 to the existing PI
  Timescale store, verified stored API and one technical source GET, and wired
  one snapshot owner. Operator/Compose changes are merged via PR #15; accepted
  runtime provenance and overrides remain distinct from source-controlled wiring. [Runtime evidence](../pi-collector/docs/nadi-pi-runtime-001.md).
- NADI-RUNTIME-002 reconciled the accepted existing Mart schema/runtime via
  merged PR #16: `asset_af_mapping` exists, mappings remain zero, NADI uses the
  dedicated reader. Preserve that store and the separately authorized writer.
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

### 1. NADI-PI-001 MERGED; NADI-PI-RUNTIME-001 runtime checkpoint

PR #12 merged at `2026-10-07T10:27:39Z`, merge SHA `3e981a3`. The historical
implementation/FIX-01 notes remain offline evidence for that scope, not current
merge status. Runtime uses this exact PI main image, preserving Maximo/CEMS/NK
and existing stores. Migration 004 and stored-data API acceptance were performed
before the explicitly authorized one-GET technical source canary.

Technical registry collection remains distinct from governed NADI signals.
No production VERIFIED target is established. PR #16 now provides governance
in the actual existing Mart, but NADI-IDN-002A found no identity-qualified
proposal. **GOVERNED CANARY DEFERRED** until controlled identity evidence and
human verification. PR #15/#16 are merged; their runtime acceptance is preserved.
No PI projection or Phase 1 completion is claimed.

### 2. NADI-IDN-002 — pilot verified Asset ↔ AF mapping

Use controlled dry-run/import → PROPOSED → human verification → VERIFIED.
Bound the pilot population, approved evidence and units; test unmapped and
ambiguous states. Do not import a whole AF hierarchy or seed plausible names.
Complete NADI-RUNTIME-002 existing-Mart schema/runtime acceptance before executing
the pilot; `7149455` is historical evidence only, never a blind cherry-pick.

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
