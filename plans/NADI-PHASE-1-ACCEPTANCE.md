# NADI Phase 1 acceptance

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

## Current accepted runtime — NADI-PHASE1-RUNTIME-ACCEPTANCE-001

8 October 2026 Jakarta. Exact merged main
`c2fb0fc686396e79c19f42af46694673827493a9`, PR20 MERGED.
[Full operational report](../reliability-cockpit/docs/nadi-phase1-runtime-acceptance-001.md)
records backup, migrations, ACL, exact images/configuration, actual readiness and
post-deploy smoke. This supersedes the historical candidate/runtime-gap labels
below without changing their measured evidence.

**PHASE 1 SOFTWARE READINESS: PASS — bounded merged foundation.**
**PHASE 1 SOFTWARE RUNTIME FOUNDATION: ACCEPTED.**
**PHASE 1 PRODUCT ACCEPTANCE: BLOCKED.**
Primary external identity blocker: **HUMAN_CROSSWALK_REQUIRED**.
Independent engineering-policy prerequisite: **FRESHNESS_POLICY_PENDING**.
Phase 1 remains CURRENT / PARTIAL. Human identity is not the only prerequisite
for final product PASS: policy, approved pilot signals, governed source time/quality
acceptance and bounded real evidence must follow in their controlled scopes.

| Capability | Implementation | Actual runtime / evidence | Status | Remaining prerequisite |
|---|---|---|---|---|
| Maximo factual evidence | Merged bounded WO/local Mart path |845 Registry,113886 WO,69619 maintenance; post-deploy25-row incremental errors0; cursor advances, recovery floor intact; factual7d765/30d1990 | ACCEPTED factual/current activity; freshness gate UNKNOWN | Approved collection policy; global MXR-004 remains separate PARTIAL scope |
| PI technical collection | Guarded accepted single owner |490 total/433 active/433 snapshots; post-deploy433/433/errors0; existing PI004/history/hypertable preserved | ACCEPTED collection; technical quality DEGRADED |18 bad-quality technical signals visible; source timestamps/selected signals require separate review |
| Asset↔AF governance | Canonical002/003/admin/resolver | Owning Maximo Mart unchanged, mapping table empty, SELECT-only reader | ACCEPTED mechanism | Real controlled identity absent |
| Human crosswalk | Safe R1/R2 completed | PROPOSED0/VERIFIED0; BFPT frozen; no new discovery/import/verify | BLOCKED / EXTERNAL | Responsible MATCH naming exact identities/date/evidence |
| Governed PI boundary | Merged adapter | Accepted technical worker preserved; governed canary deliberately not run | SOFTWARE ACCEPTED | Human-VERIFIED target plus separately authorized bounded canary |
| Condition contract | Merged PR20 typed/provenance foundation | Exact main API deployed; numeric/text/digital/boolean/null tested previously, no real condition values | ACCEPTED foundation | Real selected-signal time/quality acceptance |
| Signal selection | Explicit approval contract | condition_signal_selection exists and empty | ACCEPTED foundation; product BLOCKED | Identity then controlled signal meaning/unit/role approval |
| Condition projection | Bounded handoff/local writer | Mart004 applied after backup;17 locked counts/fingerprints equal; latest/state tables empty; API no-mapping UNKNOWN | ACCEPTED runtime; production NOT_AVAILABLE | VERIFIED identity, approved signals, bounded trusted handoff/projection |
| Integration status | Typed five-component API/UI | Local PI observation/status/proxy200; real Data Trust and Asset panels;845/0/0/0 coverage; no source auth | ACCEPTED runtime | Neutral policies intentionally UNKNOWN; no fake health score |
| Acceptance automation | Read-only9-gate CLI | Actual LOCAL_RUNTIME BLOCKED, normal exit0; require-pass exit2; schema/status PASS | ACCEPTED runtime; product BLOCKED | Satisfy real identity/policy/signal/evidence gates without weakening logic |

Current nine gates:

| Gate | Verdict | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-PI-COLLECTOR-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-IDENTITY-MAPPING-READY | BLOCKED | HUMAN_CROSSWALK_REQUIRED |
| P1-SIGNAL-SELECTION-READY | BLOCKED | HUMAN_CROSSWALK_REQUIRED |
| P1-CONDITION-PROJECTION-READY | BLOCKED | HUMAN_CROSSWALK_REQUIRED |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID |

| Gap class | Current state |
|---|---|
| SOFTWARE | Bounded Phase1 foundation merged/tested, no unmerged code deployed |
| RUNTIME | Exact main consumer images, Mart004 and reader grants accepted; source workers preserved |
| POLICY | FRESHNESS_POLICY_PENDING; no approved SLA inferred from measured cycle durations |
| DATA | No production approved signals/governed condition evidence; technical BAD_QUALITY18 visible |
| HUMAN | HUMAN_CROSSWALK_REQUIRED; attributable review not supplied by executor |
| OPTIONAL/FUTURE | Wider semantics/MXR-004, scheduling/soak/restore, CEMS evidence, scoring and Phase2–5 remain separate scope |

Private full backup13,198,605bytes/catalog130, SHA256
6ae19af92b30ac5d960755e40e289894e757e2621a1b755df98d8cf34c7a32c3.
Mart004 transaction7.968s, second apply no-op. No condition DDL in legacy Cockpit.
80 targeted tests PASS (62Cockpit/18PI),9 web route shells plus2 hydrated views,
2 real JSON proxy routes and final Next build PASS. Accepted prior full-suite
245Cockpit/177PI evidence remains below; not mechanically rerun for doc/config work.

Only pi-api/cockpit-api/cockpit-web replaced; web rebuilt once with the existing
supported non-secret Next build configuration to fix baked localhost proxy.
All tracked application code is exact merged main. .env.platform/accepted overrides,
20 other container identities, workers/projector/DB volumes/networks unchanged.
Task source business GET/write0, mapping imports/verifies0, signal approvals0,
condition projections0, history/discovery/registry/reset/volume recreation0,
new operational DB0, CEMS/NK changes0. Background approved collection continues.

GitHub metadata already marks PR19 MERGED, contrary to superseded/unmerged
expectation;211faec is an ancestor of required main. This task merged neither PR.
Runtime-acceptance evidence branch/PR remains open/unmerged for senior review.

Next: obtain controlled human MATCH, execute NADI-IDN-002B attributable verification
and separately authorized governed canary, then approved signals/policy/bounded
real projection and actual phase1-readiness --require-pass. Runtime is ready for
that controlled next step; full product acceptance is not claimed.

---

# Historical software-bundle acceptance — NADI-PHASE1-OVERNIGHT-BUNDLE-01

Audit: 8 October 2026 Jakarta; operational aggregate inspection
7 October 21:55 UTC. Main `f8c37f068102a06906cb3ca464fe08745e0351cf`;
bundle base is exact PR #19 HEAD `211faec4b0916361491d3ca8bc01ada2f0072284`.
Branch `codex/nadi-phase1-overnight-bundle-01`. PR #19 remains open/unmerged,
branch untouched; this bundle incorporates its foundation and supersedes it
only after acceptance. Candidate artifacts do not prove mainline/runtime deployment.

**PHASE 1 SOFTWARE READINESS: PASS — candidate, bounded B0–B4 scope.**
**PHASE 1 PRODUCT ACCEPTANCE: BLOCKED.**
**Human identity blocker: HUMAN_CROSSWALK_REQUIRED.**

Human identity is the outstanding external cross-system evidence gate, but is
**not the only remaining product prerequisite**. Condition runtime deployment,
reader grants, freshness policy, signal approval and real evidence acceptance
remain deliberately unexecuted. Phase 1 stays CURRENT / PARTIAL. This document
does not accept scoring, all discovery semantics or the entire platform M0–M8.

## Acceptance matrix

| Capability | Implementation | Runtime | Evidence | Status | Remaining blocker |
|---|---|---|---|---|---|
| Maximo factual evidence | Merged Collector/cursor/local projector/Mart/NADI | Existing Maximo owner; WO incremental current | 845 registered; 113884 WO; 69617 maintenance; repeated25-row unchanged overlap, errors0; factual routes200 | CURRENT within accepted BSR/IP scope | Wider MXR-004 global/concurrent-source guarantee remains PARTIAL outside pilot |
| PI technical collection | Merged guarded single worker and Timescale migrations | Existing PI store; 433 active and433 snapshots | Latest complete433/433/errors0; PI004 checksum/applied time unchanged | ACCEPTED / CURRENT technical scope | Technical inventory is not governed Asset evidence |
| Asset↔AF governance | Merged canonical002/003/admin/resolver | Operational asset_af_mapping exists; reader SELECT-only | Operational count0; fixture lifecycle/ACL/migration tests | ACCEPTED mechanism | No usable production identity |
| Human crosswalk | R1/R2 safe investigation exhausted | PROPOSED0 / VERIFIED0 | Three controlled human review rows; BFPT contradiction frozen | BLOCKED / EXTERNAL | Responsible reviewer MATCH naming exact identities/date/evidence |
| Governed PI source boundary | Merged NADI-PI-001 | Accepted Collector runtime; governed canary deferred | Real guarded adapter used with synthetic HTTP replies; lineage/type/source guards tested | Software PASS; real mapping-gated canary pending | VERIFIED target plus separately authorized bounded source operation |
| Condition evidence contract | PR19 foundation plus timestamp/handoff compatibility repair | Not deployed to NADI | Strict numeric/text/digital/boolean/null, timestamps/unit/quality/provenance; JSON/Python acceptance | Candidate PASS | Review/deploy candidate |
| Signal selection | Separate explicit approval; max5 selected attributes per mapping | No production approvals | Immutable definitions, retirement/recheck, no registry promotion | Candidate PASS | Governed pilot signal meaning/unit/role and responsible approval |
| Condition projection | Trusted Collector-owned file handoff → local Mart writer → SELECT-only API | No operational condition tables/004 or projection | Real disposable PostgreSQL002→003→004, replay/conflict/older/mid-flight/quality tests | Candidate PASS; production NOT_AVAILABLE | Runtime004/grants, identity, selected signals, quality/time acceptance |
| Integration status | Typed five-component read model/API/Data Trust/Asset view | Candidate only; older PI API lacks aggregate endpoint | Local-only observations, schema/coverage/degraded/unknown tests and rendered React views | Candidate PASS | Reviewed API/PI stored-observation/UI deployment and explicit freshness policy |
| Acceptance automation | Read-only cockpit phase1-readiness, nine typed gates | One-shot candidate reader audit executed; not installed deployment | Synthetic PASS; real-like and actual runtime BLOCKED | Candidate PASS; product BLOCKED | Pass real governed pilot gates without weakening them |

Canonical condition tables are latest-only in the **existing** Maximo-owned
Reliability Mart: condition_signal_selection, condition_evidence_latest,
condition_projection_state. No new operational DB, unrestricted history copy,
PI credential in NADI, public mutation or arbitrary source proxy is introduced.

## Actual runtime and preserved evidence

Control checkout remains `0c800dac1da6ef863afdb193021176fe7feac073`.
Compose project `reliability-cockpit-platform`; actual files compose.yaml,
compose.dev.yaml and private accepted Maximo-WO/PI-runtime/NADI-runtime overrides.
The inspected nine DB/API/worker/projector/web identities remain running; no
service was restarted or deployed by this bundle. Private aggregate audit is ignored under secrets/nadi-phase1-overnight-bundle-01;
the temporary0600 reader-only preflight env was removed after inspection;
no secret/DSN or backup bytes are committed.

Mart remains maximo-db / maximo_collector, owner maximo_collector. Public NADI
uses nadi_mart_reader, distinct from legacy cockpit-db / cockpit. Reader has
mapping SELECT, no UPDATE and no superuser privilege. Writer/admin stays separate.
Operational governance ledger contains002/003; condition table absent and Mart004
not applied. Canonical query compatibility is inspected without reader access to
writer migration ledger; controlled writer checksum/constraints preflight is
still mandatory for actual deployment.

Registry845, Asset Master11845, WO113884, maintenance69617 remain intact.
WO cursor `2026-10-07T14:59:45Z`; one recovery-floor audit run retains
`2026-08-21T03:56:54Z`. The floor lives in recovery evidence/configuration,
not a second invented sync cursor. Latest inspected WO completed21:54:29 UTC,
errors0, 25 rows seen/0 upserted/25 unchanged-or-overlap skips. No bootstrap.
Both factual projector states SUCCEEDED at21:52:22 UTC. NADI Registry and
Decision Overview HTTP200; current registered845, activity7d763 /30d1988 /90d4226.
Moving-window changes are not a table/cursor reset or a failure score.

PI registry490 total/433 active; snapshots433. Latest inspected snapshot success
21:44:33 UTC, 433 seen/433 collected/errors0. Existing PI migration004
`004_signal_quality_fields.sql` remains applied at10:49:24 UTC with checksum
`b40f87fe86097bf2e1eda7c63063629903166627b1cca6c182de74c0dd3f1ffe`.
This PI migration is distinct from new Mart004_condition_evidence.sql.
Accepted historical508-second acquisition +300-second post-cycle pause remains
historical evidence, not fixed five-minute cadence. No broad source re-verification.

## Actual one-shot candidate preflight

Executed against existing Mart **reader** and fixed local stored-data Collector
APIs, without source authentication/trigger, DDL or candidate deployment.
Output origin LOCAL_RUNTIME; overall BLOCKED. Empty policy stays UNKNOWN.

| Gate | Actual result | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY; accepted repeated WO acquisition remains current separately |
| P1-MART-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-PI-COLLECTOR-CURRENT | UNKNOWN | LOCAL_EVIDENCE_UNAVAILABLE: old runtime lacks new aggregate endpoint; accepted433/433 DB/run evidence preserved |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | BLOCKED | CONDITION_SCHEMA_NOT_READY |
| P1-IDENTITY-MAPPING-READY | BLOCKED | HUMAN_CROSSWALK_REQUIRED |
| P1-SIGNAL-SELECTION-READY | BLOCKED | HUMAN_CROSSWALK_REQUIRED |
| P1-CONDITION-PROJECTION-READY | BLOCKED | HUMAN_CROSSWALK_REQUIRED |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID in the one-shot candidate, not a deployed API claim |

Coverage: registered845, uniquely usable VERIFIED0, ambiguity0; approved/
projected counts UNKNOWN because their schema is absent. Operational production
condition projections performed0. No missing schema is presented as a healthy
zero-valued signal. Synthetic configured full chain reaches nine PASS gates.

## Gap classification

| Class | Gap | Consequence / next action |
|---|---|---|
| SOFTWARE | No hard blocker found in bounded B0–B4 implementation after fixes/tests; candidate review/merge still required | One bundle PR, open/unmerged; PR19 superseded only if accepted |
| RUNTIME | Candidate API/PI aggregate/UI not deployed; Mart004/read grants absent; blank policies | Separate authorized backup/preflight/additive004/grants/deployment acceptance; preserve overrides/source workers; establish policy from engineering evidence |
| DATA | No selected/approved production signals or governed evidence | Define bounded meanings/units, explicit approval after identity; real source time/quality acceptance, no automatic433-attribute projection |
| HUMAN | Exact Maximo↔AF identity not proven; responsible review pending | HUMAN_CROSSWALK_REQUIRED; MATCH/NOT_MATCH/UNKNOWN for bounded packet; never automation verified_by |
| OPTIONAL/FUTURE | Scheduled projection owner, bounded history, wider mapping coverage, global MXR-004, other domain semantics/scoring, CEMS evidence, Phase2–5, broad operational soak/restore | Not claimed or implemented to make this pilot green; separate scope/acceptance |

An offline/operator all-green document is labelled OPERATOR_DOCUMENT; it cannot
stand in for live runtime/human acceptance. No arbitrary production SLA is added.
Collector/source/projection/identity dimensions remain independent; future times,
missing metadata and non-finite policies cannot produce fabricated CURRENT.

## Test evidence and reproduction

Candidate tests: Cockpit245 total. PostgreSQL container run238 PASS /7 skipped
(6 clean Compose cases and1 Node-render case executed on host). Host run194 PASS /
51 PostgreSQL cases skipped (all51 executed in the container). Together all245
cases execute successfully. PI177 PASS including11 established Timescale cases.
Contracts14 PASS, validating all30 schemas. Runtime11 PASS within host suite;
synthetic rendered React/ASGI tests PASS; typecheck PASS; Next production build
13 routes; product safety18 source files; route smoke9/9; git diff --check PASS.

Environment preparation used a test-only image based on the existing accepted
Cockpit runtime with jsonschema4.26.0 installed under /tmp/testdeps, not a
production image redeploy. Host jsonschema dependencies were installed under
/tmp/nadi-phase1-host-testdeps; existing component environments were reused.

Exact commands (PROJECT_WORKTREE points to this candidate worktree):

```bash
# Cockpit directory, host: isolated legacy DSN, clean Compose config and Node case.
DATABASE_URL=sqlite+pysqlite:///:memory: NADI_COMPOSE_TESTS=1 \
PYTHONPATH=/tmp/nadi-phase1-host-testdeps \
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
-m unittest discover -s tests -q

# Disposable PostgreSQL16, no host ports/operational volumes; candidate source read-only.
docker run --rm --network container:nadi-phase1-mart-test \
-v "$PROJECT_WORKTREE:/workspace:ro" -w /workspace/reliability-cockpit \
-e RELIABILITY_MART_MIGRATIONS_ROOT=/workspace/reliability-cockpit/migrations \
-e DATABASE_URL=sqlite+pysqlite:///:memory: \
-e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test \
nadi-phase1-acceptance-test:local python -m unittest discover -s tests -q

# Disposable Timescale2.16.1/PG16; no operational PI migration or source.
docker run --rm --network container:nadi-phase1-pi-test \
-v "$PROJECT_WORKTREE:/workspace:ro" -w /workspace/pi-collector \
-e PI_MIGRATIONS_PATH=/workspace/pi-collector/migrations \
-e PI_MIGRATION_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/pi_runtime_test \
nadi-phase1-acceptance-test:local python -m unittest discover -s tests -q

# Contracts directory (14 tests, all30 schemas).
/home/john-d/Music/reliability-knowledge-starter/maximo-knowledge/.venv/bin/python \
-m unittest discover -s tests -q

# Cockpit directory: 3 reproducible status/handoff exports.
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
scripts/export_evidence_contracts.py --check

# Cockpit web directory.
node_modules/.bin/tsc --noEmit
npm run build
node scripts/product-safety-check.mjs
NADI_WEB_BASE_URL=http://127.0.0.1:3319 node scripts/route-smoke.mjs
# Next start :3319 was a temporary test process, stopped after smoke.

# Repository root.
git diff --check
```

Initial host full-suite invocation without isolated legacy DSN failed two legacy
API tests at localhost authentication; rerun with explicit SQLite test DSN passed.
No operational write resulted. Host Python3.14 reports SQLite fixture
ResourceWarnings; no test failure is suppressed. The PostgreSQL acceptance path
uses the real SELECT-only reader and separated writer, with network confined to
its disposable DB container. Disposable schema resets are intentional test setup,
not operational resets. Both temporary DB containers are removed after tests.

## Safety and next execution

Task-initiated production PI GET0 / Maximo GET0; business writes0/0.
Production mapping import0 / verify0, PROPOSED0→0 / VERIFIED0→0; signal approvals0;
condition projection0; operational DDL/migration0040; history/backfill0; broad AF
crawl0; registry changes0; operational reset/truncate/volume replacement0;
service restarts/redeployments0; CEMS/NK changes0; credential exposure0;
new operational DB0. Existing accepted collector workers continued their normal
activity; their own background GETs are not requests initiated by this task.
Private reader credentials were used only for a one-shot SELECT-only audit.

Next independently: senior review/merge this bundle, then separately authorized
condition runtime acceptance (backup, existing-store004, reader grants, candidate
API/PI aggregate/UI deployment and evidence-based policy). This bundle performs
none of those deployment steps.

When one controlled human MATCH becomes available: NADI-IDN-002B — bounded
PROPOSED dry-run/import, mandatory attributable human verification, unique target
resolution and separately authorized governed PI canary. Obtain approved signal
semantics/units/time/quality policy; use the accepted runtime for trusted bounded
handoff/projection and rerun phase1-readiness. A MATCH is not automatic approval
of arbitrary signals, unsafe source calls or production deployment. BFPT remains
REJECTED / FROZEN / DO NOT VERIFY.

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
