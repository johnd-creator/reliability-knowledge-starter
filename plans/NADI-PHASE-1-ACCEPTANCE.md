# NADI Phase 1 acceptance

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
