# NADI product roadmap — main quest

## Current product checkpoint — NADI-DOC-FOUNDATION-01 — 2026-10-10

This is the **official product roadmap**. Phase 0–5 remains intact; the UX track
below complements it. Verified main `f54643f3510bf505628a1400024784faab46e496`
contains merged Engineering PR29–61. PR62/63 remain OPEN, with exact heads and CI
in [Repository Status](REPOSITORY-STATUS.md). Older checkpoint language below,
including “current”, “OPEN” and the original phase table, is dated historical
evidence and does not override this reconciliation. No runtime/PO acceptance is
inferred from merge or documentation approval.

| Phase | Current status | Evidence and remaining scope |
|---|---|---|
| 0 — Factual Foundation | **COMPLETE within accepted factual scope** | PR1/release v0.1.0-rc.1; preserve factual semantics |
| 1 — Evidence Expansion | **CURRENT / PARTIAL** | Bounded governed pilot and provisional monitoring; condition freshness and independent reviews remain gates |
| 2 — Collaborative Engineering Workspace | **FOUNDATION MERGED / OPERATIONAL PARTIAL** | PR29–61; persisted isolated QA is not operational activation or actual engineer UAT |
| 3 — Diagnostic & PdM Intelligence | **DESIGN READY / NOT OPERATIONAL** | Existing diagnostic design; approved data, methods, thresholds and ground truth still required |
| 4 — Recommendation Action Loop | **LOCAL FOUNDATION / OPERATIONAL PARTIAL** | Reviewed NADI-owned recommendation/follow-up foundation; effectiveness/operational acceptance pending |
| 5 — Organizational Learning | **PLANNED** | Evidence and accepted outcome history prerequisites |

[PRD](../PRD.md) owns product requirements, [UI spec](../docs/design/NADI-UI-SPEC.md)
owns page design, and [M0–M8](reliability-cockpit-platform/05-roadmap-implementasi.md)
retains scoped engineering sequencing. No completion percentages are inferred.

### Product UI/UX Development track

| Task | Scope | Development status | Merge / acceptance boundary |
|---|---|---|---|
| UX-01 | Single Development Environment | **Development acceptance PASS** | PR62 OPEN at 0bfea1273f97ce96a08ef147b44f804aecb428d1; HTTPS3000 visible; PO/operational acceptance separate |
| UX-02 | NADI Design System V1 | **PLANNED** | Candidate documentation exists; token/contrast/visual review and UI implementation pending |
| UX-03 | Sidebar Information Architecture | **PLANNED** | Proposed map only; preserve existing routes; PO review pending |
| UX-04 | Executive Overview Visual Polish | **PLANNED** | Existing factual dashboard retained; design reference missing |
| UX-05 | Asset Health List & Detail UI | **PLANNED** | Existing factual list/detail retained; six-section target and visual acceptance pending |
| UX-06 | PdM Center UI | **PLANNED** | Existing DEMO/inspection foundation is not new method/trend UI acceptance; PR63 gates apply |
| UX-07 | Recommendations & Action Board UI | **PLANNED** | Local lifecycle exists; complete product UI/UAT pending |
| UX-08 | Global Login Page Design Only | **PLANNED** | Specification candidate; no global enforcement; existing QA gates unchanged |
| UX-09 | UI Regression & Visual Acceptance | **PLANNED** | Actual originals, responsive/accessibility checks and separate PO decision required |

UX-02/03 design review precedes visual implementation; UX-04/05 preserve accepted
factual functionality. UX-06/07 depend on engineer contracts and reviewed evidence.
UX-08 can be designed independently and grants no authentication activation.
UX-09 evaluates exact implementation SHA and original references. A specification
created by this task does not mark these delivery tasks complete.

### PdM and Phase1 continuity

PR63's [pinned requirements](https://github.com/johnd-creator/reliability-knowledge-starter/blob/89cfa0e50dbdaa1fa158558c890cc512c049b60f/reliability-cockpit/docs/nadi-pdm-requirements-01.md)
remain candidate R01–R08 with Q01–Q10 PENDING_ENGINEER_VALIDATION. Preserve M01–M07:
engineer samples/terminology → approved point/instrument contracts → irregular
measurement history → controlled import/diagnostic evidence → independent review
→ existing-WO/local recommendation linkage → engineer UAT. Portable events are
not continuous/daily; no portable/DCS/PI combination without approved comparability;
PD is not assumed DGA; “30% acr” remains undefined. No source write or new PdM
functionality is introduced. [Conflict reconciliation](../docs/NADI-DOC-FOUNDATION-01.md#pr62--pr63-reconciliation-plan)
preserves both open PRs without automatic merge.

[Phase1 acceptance](NADI-PHASE-1-ACCEPTANCE.md) retains its independent 24h/72h
reviews, 12 October20:00 WIB checkpoint and **13 October2026 00:00 WIB hard expiry**.
Operator review outcomes are UNKNOWN in available evidence. This task does not
activate, extend, reset or roll back any policy. Current operational readiness is
not re-certified by documentation or a successful frontend status response.

### Historical checkpoints and original phase backlog

All following checkpoints retain their original evidence, dates and limitations.

## NADI-E-INTEGRATION-02 — local authentication and final audit — 2026-10-09

Main `eda3595a9b8d86726dd0d89192ebf4657b66d27e` unchanged. Bundle E PR51–59 preserved;
E9 PR60 and E10 PR61 extend the OPEN/UNMERGED stack. Local username/password is the
selected initial-QA identity path; enterprise SSO is optional future work.
Tested implementation `1ec149de2d1acd4113987364e1f96c790bfaf63e`.
Argon2id accounts, private operator admin, versioned sessions/RBAC, actual HTTPS
login/workflow and disposable migration006 validated. Audit LOW stale-response
finding repaired; Compose preflight argv and migration docs corrected.
Cockpit687/Maximo181/PI191/contracts14 PASS,0FAIL/0SKIP including11 Timescale;
frontend143/browser40 +legacy25/type/build/32-file safety PASS. Actual source-free
preflight remains NO_GO with unapproved host/policy/storage references.
**Development acceptance PASS; merge READY pending explicit authorization/exact-head CI.**
**Phase1 CURRENT/PARTIAL; Phase2 CANDIDATE/PARTIAL; real QA NO_GO; activation OFF.**
Actual host/TLS, application DB/roles, admin custody/onboarding, reviewed startup and
secure frontend transport, password/session/resource policy, storage/scanner,
PdM fields/UAT and per-action deployment authority remain required. No SSO gate.
No production source GET/write, WO mutation, DB DDL, deployment or Phase1 mutation.
Older test counts/checkpoints below are historical.
[Final audit, tests, activation blockers and merge plan](../reliability-cockpit/docs/nadi-e-integration-02.md).

## Bundle D merged / Bundle E QA preparation — 2026-10-09

PR44–50 MERGED via merge commits; authoritative main
eda3595a9b8d86726dd0d89192ebf4657b66d27e. Older OPEN/candidate statements below
are historical. Bundle E stack51→59 is OPEN/UNMERGED, preparation only.
Dedicated QA architecture, enterprise trust contracts, fail-closed privilege
audit, attachment integrity/recovery, bounded HTTP, source-free preflight, exact
artifact binding and disposable restart/restore rehearsal validated.
Final Cockpit661/Maximo181/PI191/contracts14,11Timescale, frontend127/type/build/
safety and browser25 PASS. No real QA UAT or operational activation.
**Phase1 CURRENT/PARTIAL; Phase2 QA preparation CANDIDATE/PARTIAL; real QA NO-GO.**
Operator allowed naming; actual host/IdP/DB role provisioning/storage/scanner,
reviewed real-QA startup/frontend integration, PdM fields/UAT and explicit
deployment authority remain required. No new production source request/write,
WO changes, DB DDL, deployment or Phase1 mutation.
[Bundle E handoff](../reliability-cockpit/docs/nadi-phase2-bundle-e.md).


## Bundle D final integration review — NADI-D-INTEGRATION-01

Baseline main e836710 unchanged. Stack44→50 remains OPEN; no merge/deployment.
Session cancellation finding corrected6f66ecd in PR48; normal forward merges
preserve ancestry. Final implementation c03e57c; final documents at PR50 head.
Local acceptance Cockpit610/Maximo181/PI191/contracts14,11Timescale, HTTP11,
browser25 +proxy8, frontend110/type/build/safety PASS. Corrected scoped CI run
37892980855 SUCCESS; final PR50 CI must match its exact head before merge.
**Merge candidate READY pending explicit operator authorization.**
**Phase1 CURRENT/PARTIAL; Phase2 QA CANDIDATE/PARTIAL; operational activation BLOCKED.**
PUBLIC/default/schema-owner privilege audit, enterprise identity/deadlines,
attachment storage/recovery/scanner, PdM field approval and operational UAT remain
activation gates. QA proxy streaming caps are a non-operational follow-up.
[Final review, findings and controlled merge plan](../reliability-cockpit/docs/nadi-d-integration-01.md). Older checkpoints
retain historical evidence; no source/production/Phase1 mutation or new acquisition.

## Current development checkpoint — Phase 2 Bundle D

Baseline main `e836710d1984af7a4bfb739bad0bfbbb96d544ca`, Bundle C PR37–43 MERGED.
Tested implementation `ee20307a2664e7ca64737c3f43f1256f26cdf9f6`.
**Development/test acceptance PASS; operational activation BLOCKED.**
**Phase1 CURRENT/PARTIAL; Phase2 integrated QA CANDIDATE/PARTIAL.**
D1–D7 stack adds enterprise identity adapter/session bootstrap, deliberate
application migration ledger/writer grants, private attachment service and real
HTTP/PostgreSQL/frontend workflow. Operational Engineering routes remain unmounted.
No production/source/Phase1 mutation; Maximo/PI strictly READ-ONLY, NADI never
creates or changes Maximo WO. Original accepted runtime is unchanged.

Final local Cockpit600, Maximo181, PI191, contracts14 PASS;11 formerly skipped
Timescale tests now executed in disposable fixtures. HTTP11/browser25/frontend110,
29 safety files/typecheck/build/diff-check PASS. D6 actual GitHub backend/frontend
jobs SUCCESS, run37887690942. Security diff review found no concrete reportable
issue in15 changed source/config surfaces; production IdP/storage not certified.
Real enterprise IdP/directory, existing-store provisioning/privilege approval,
secure storage/scanning, PdM engineer field sign-off and operational UI/UAT remain
external activation gates. QA command editor is not final engineering form UX.
[Bundle D acceptance and activation manifest](../reliability-cockpit/docs/nadi-phase2-bundle-d.md) records the exact stack,
recovery proposal, test evidence and limits. Next: senior stack review, then
separately authorized identity/provisioning/field UAT. Older checkpoints below
retain historical measured evidence; they are not re-certified by this bundle.

## Current development checkpoint — Phase 2 Bundle C

Verified main `7a846ef2c7e25306f23da99dd011e1d54aa8f4a4`, BundleB PR30–36 MERGED.
**Phase1 CURRENT/PARTIAL; Phase2 CANDIDATE/PARTIAL; operational activation OFF.**
Stacked C1–C7 candidates add same-asset local context/maintenance chronology,
reviewed manual inspection evidence, case-linked recommendations and independent
local completion verification, integrated development-only concept screens and
trusted-session/PostgreSQL acceptance. Maximo/PI remain strictly source READ-ONLY;
NADI recommendations never create/update/close/approve/cancel Maximo WOs.

Local validation: Cockpit532 PASS (all disposable PG/Compose), Maximo181 PASS,
contracts14 PASS/35schemas, PI180 PASS/11 isolated Timescale SKIP;100 frontend
assertions,27 safety files,40 browser assertions, TypeScript/build/diff-check PASS.
No production access, DB/DDL, deployment, source acquisition or Phase1 mutation.
Enterprise identity/bootstrap, deliberate application provisioning/migration ledger,
PdM engineer fields, secure storage and operational UI integration/UAT remain BLOCKED.
Candidate UI is browser-memory DEMO only; no operational writer route is mounted.
Do not mark Phase1 or Phase2 COMPLETE. Historical operational evidence, GOV03 policy
approvals/checkpoints/expiry and accepted condition evidence are unchanged and not
re-certified by this software task.
[Bundle C report, stack and handoff](../reliability-cockpit/docs/nadi-phase2-bundle-c.md)
Next: trusted enterprise bootstrap/provisioning contracts → engineer field approval
→ operational UAT. New Maximo coverage requires separate collection authorization.


## Current development checkpoint — Phase 2 Bundle B

Main `02e887c56057611f112b7b652ba9a9aee8b382ea`, corrected PR29 MERGED.
**Phase 1 CURRENT/PARTIAL; Phase 2 CANDIDATE/PARTIAL; activation OFF.**
B1–B7 implement source-boundary policy/coverage, trusted identity/session adapters,
bounded local WO context, Manual PdM envelope, NADI-native recommendations,
development-only concept lab and isolated integrated acceptance. Maximo/PI remain
strictly source read-only. A recommendation is not a WO or maintenance authorization.
No production source GET, DB/DDL, deployment, activation or Phase-1 evidence mutation.

Local evidence: Cockpit 462 pass (isolated PG + Compose), Maximo 181 pass,
contracts 14 pass, PI 180 pass/11 fixture skips; frontend 25+37 assertions,
product safety/typecheck/build and 24 browser checks pass. Enterprise provider,
reviewed session bootstrap/provisioning/migration ledger, engineer-approved method
fields, directories and operational UI/UAT remain required. No phase is marked COMPLETE.
[Bundle report and review stack](../reliability-cockpit/docs/nadi-phase2-bundle-b.md) records limitations and migration/rollback proposals.
Next: trusted enterprise identity + PdM field sign-off + reviewed application
provisioning/backend integration. Earlier runtime checkpoints below are historical;
GOV03 approvals/checkpoints/expiry are unchanged and are not re-certified here.


## Current development checkpoint — overnight Engineering bundle 01

Baseline PR28 MERGED, main `e67c641e23214bf8851a05d312e1426c1e471ec3`.
**Phase 1 CURRENT/PARTIAL; Phase 2 IN DEVELOPMENT; Phase 3 DESIGN READY.**
Source-free candidate adds typed human cases, attributed independent review,
transactional audit/idempotency/concurrency, bounded local canonical references,
disabled isolated API contracts and an explicitly synthetic development-only UI.
Production write routes remain unmounted: trusted application identity/RBAC/session
and application writer/migration provisioning are BLOCKED, not simulated as users.
RCFA identity/Data Trust provider and operational UAT remain explicit gaps.

[Morning acceptance](../reliability-cockpit/docs/nadi-phase2-overnight-bundle-01.md)
and [Phase 3 design](../reliability-cockpit/docs/nadi-phase3-diagnostic-foundation.md)
record exact available tests and readiness. No source request, operational DB write,
deployment, worker/env/grant change or new operational database. Accepted R3 evidence,
GOV-03 policies/checkpoints/expiry and Phase-1 semantics remain untouched. This
checkpoint authorizes development reporting only; historical runtime evidence below
is not replaced by a new observation. Next: **NADI-PH2-02 — Trusted Engineering
Identity & Activation Contracts**. Do not mark Phase 2 COMPLETE or diagnostics live.

## Current runtime checkpoint — NADI-P1-FRESH-GOV-03 (8 October 2026)

**PASS — temporary internal monitoring ACTIVE; Phase 1 CURRENT/PARTIAL.**
Fauzi authorized MAXIMO_WO=660s, MART_FACTUAL=660s, PI_COLLECTOR=1800s as
project owner/accountable internal technical approver. External endorsements are
not required or claimed. Legacy and both condition policy settings remain UNSET.
Original 8 October owner approval stays DATE_ONLY; historical GOV02 is preserved.

Actual activation `2026-10-08T21:45:26.619585+07:00`; 24h review
`2026-10-09T21:45:26.619585+07:00`; 72h review `2026-10-11T21:45:26.619585+07:00`.
Explicit owner-revised hard expiry **2026-10-13T00:00:00+07:00**.
Fauzi confirms **12 October 20:00 WIB** checkpoint and rollback before expiry
without an approved extension. Enforcement is manual; no automatic scheduler.

Main `1f7c25a711e68afc87ee0c4b1322bfca4be6ba97` / PR27 MERGED; actual serving SHA `1cf7fed971594581913e8e7f635691f834133b6e`,
application source identical to main. Same-image API replacement only; other 22
containers preserved. R3 evidence/timestamps, VERIFIED1/PROPOSED0, approved signal1,
latest/state1/1 and 433 active technical attributes unchanged; source GET0.
Initial readiness **8 PASS / 1 UNKNOWN**. Final observation **7 PASS / 1 PARTIAL /
1 UNKNOWN**, overall UNKNOWN, require-pass exit2: unchanged background PI worker
completed 432/433 with 1 error; prior full-cycle success is preserved. No retry/probe.
Condition freshness acceptance remains outstanding; technical BAD_QUALITY18/epoch
anomalies remain visible and are independent of collection freshness.

[Activation and rollback evidence](../reliability-cockpit/docs/nadi-p1-fresh-gov-03.md)
and [migration handoff](../reliability-cockpit/docs/nadi-pre-migration-readiness-gov-03.md)
record remaining operator reviews, manual expiry risk and separately authorized
future cutover. No server migration, condition refresh/replay, DDL or approval changes.
Earlier sections below are historical and do not override this checkpoint.

Public SEC01 audit preserves approval scope, dates, thresholds and recorded readiness;
host-specific deployment and executable recovery details are retained privately.
Sanitization changes documentation only; runtime and accepted evidence are unchanged.
Git history is retained, so earlier public revisions remain accessible.

## Historical owner decision — NADI-P1-FRESH-GOV-02 (8 October 2026)

**PROJECT_OWNER_APPROVED**: Fauzi approved MAXIMO_WO=660s, MART_FACTUAL=660s,
PI_COLLECTOR=1800s for provisional monitoring; both condition policies stay UNSET.
This is conversational authorization reported directly in the user-supplied task,
not digitally signed or externally authenticated approval. Three component
endorsements remain PENDING; **ACTIVATION_NOT_AUTHORIZED / GOV-03 NOT EXECUTED**.

[Approval register and handoff](../reliability-cockpit/docs/nadi-p1-fresh-gov-02.md)
preserve the historical proposal, named reviewer gaps, date-only approval precision
and expiry rule. Calendar expiry reference is 15 October 2026; exact expiry instant
is NULL until approval-time/timezone evidence or explicit expiry clarification.
Activation, 24h/72h review dates remain NULL. No duplicate owner approval requested.

All eight runtime policies remain UNSET; R3 evidence/journal preserved. Actual
readiness 5 PASS / 4 UNKNOWN; hypothetical 8 PASS / 1 UNKNOWN; overall UNKNOWN. Phase1
CURRENT/PARTIAL, not COMPLETE. Next: component endorsements, exact expiry
resolution, reviewed release and separately authorized controlled GOV-03 activation.
No source GET, policy change, operational mutation or deployment occurred.

## Historical decision package — NADI-P1-FRESH-GOV-01 (8 October 2026)

**PASS: ready for owner review. Policies are not activated; approvals PENDING.**
Reviewed/serving release `1cf7fed971594581913e8e7f635691f834133b6e` includes PR26.
Accepted R3 real Coal Flow A evidence 54.84218978881836 Ton/h, original source/
collection/projection times and strict replay are preserved. VERIFIED=1 / PROPOSED=0,
approved signal=1, latest/state=1/1; all eight freshness settings remain UNSET.

[Engineering decision package](../reliability-cockpit/docs/nadi-p1-fresh-gov-01.md)
evaluates nearly 24h of local evidence: 278 WO attempts / 273 successes; 287 paired Mart
completion reports; 104 PI runs / 99 full 433/433 successes. Proposes 660/660/1800 seconds for
**provisional monitoring pending named owner/reviewer approval**, with proposed
7-day expiry. Condition source/projection remain DEFERRED: two manual samples
cannot establish cadence or acceptable use-age. No source GET/acquisition/replay,
production mutation, activation or restart occurred.

Source-free fourteen-case simulation passes; targeted 45 tests PASS / 9 PostgreSQL skips.
Actual readiness remains 5 PASS / 4 UNKNOWN, overall UNKNOWN. Hypothetical three
monitoring policies yield 8 PASS / 1 UNKNOWN, leaving product acceptance UNKNOWN. Phase 1 remains
**CURRENT/PARTIAL — FRESHNESS_POLICY_PENDING**. Next: accountable owner decision,
then separately authorized controlled activation; condition policies need further
engineering evidence. BFPT frozen/KKS issue unchanged. Earlier sections are
historical checkpoints, not current policy activation instructions.

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
17 locked factual count/content comparisons passed. The dedicated Mart reader remains
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

## Freshness governance proposal checkpoint — NADI-P1-FRESH-001A (8 October 2026)

Reviewed main `478cce1` is serving. Runtime evidence reconciliation is the separate
[documentation PR23](https://github.com/johnd-creator/reliability-knowledge-starter/pull/23),
head `b08a4fd`; review that documentation checkpoint first. The earlier R1 repair
blocker is historical: one VERIFIED mapping, one approved Coal Flow signal and
one accepted condition row now exist. This proposal does not duplicate that
acceptance patch or alter its measurement.

[Freshness engineering proposal](../reliability-cockpit/docs/nadi-phase1-freshness-policy-proposal.md)
records bounded local cadence/error evidence and proposes separate acquisition
monitoring boundaries. All proposals are **PROPOSED — NOT YET APPROVED**. Coal
Flow source/projection thresholds remain **POLICY_EVIDENCE_INSUFFICIENT**. Three
shared runtime knobs cannot express five independent policies; reviewed compatible
component wiring and controlled-refresh journal/chronology acceptance are next.
Production policies remain blank, handoff collector success remains null, actual
Phase1 readiness remains UNKNOWN; Phase1 stays CURRENT/PARTIAL, never COMPLETE.
No source GET, mapping/selection mutation, projection, deployment or restart
is performed by this task. Next: **NADI-P1-FRESH-001B**, engineering policy
decisions and separately authorized manual refresh; recurring scheduling stays
unconfigured. PI_AF_KKS_LOOKUP_UNRESOLVED and BFPT freeze remain in force.

## Component freshness implementation candidate — NADI-P1-FRESH-001B

PR #23/PR #24 are merged; base `4b6ae7d`. [Implementation and deployment runbook](../reliability-cockpit/docs/nadi-p1-freshness-implementation.md) adds five independent
blank-default policies with exclusive legacy compatibility, API-only runtime
wiring and a manually invoked one-asset/one-signal refresh coordinator. Private
journal, shared host lock, existing-Mart advisory lease, Collector-owned five-GET
cap, chronology/quality gates and read-only replay are implemented in the candidate.
No candidate code is deployed, no policy is activated and no production refresh
or mapping/selection mutation occurs. Runtime remains `478cce1`; Phase 1 remains
CURRENT/PARTIAL and actual readiness UNKNOWN. Threshold 660/660/1800 proposals,
source/projection policies and one live run require separate accountable approval
after software review/merge. Next: exact merged-SHA controlled deployment,
configuration preflight and separately authorized single manual Coal Flow refresh
plus real replay/API/UI/readiness acceptance. No recurring scheduler is enabled.
PI_AF_KKS_LOOKUP_UNRESOLVED and BFPT freeze remain unchanged.
