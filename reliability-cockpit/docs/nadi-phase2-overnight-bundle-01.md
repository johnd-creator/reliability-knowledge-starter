# NADI overnight Engineering bundle 01 — morning handoff

## Executive disposition

**STATUS: PARTIAL — isolated implementation accepted by local tests; operational
Engineering activation BLOCKED on trusted application authentication.**
Starting main: `e67c641e23214bf8851a05d312e1426c1e471ec3`, PR #28 MERGED and
repository PUBLIC verified before work. Branch: `codex/nadi-phase2-overnight-bundle-01`.
The final immutable HEAD and open/unmerged PR are recorded in the delivery report
and GitHub branch. No operational deployment is implied by this candidate.

The original workspace, its unrelated files, operational release and private
configuration were preserved. All changes were developed in a separate worktree.
Canonical Mart ownership and SELECT-only product readers remain unchanged.

## Milestone acceptance

| Gate | Result | Implemented and validated | Limit |
|---|---|---|---|
| A Architecture | PASS for disabled/isolated scope | ADR, scoped threat model, independent read-only architecture review | Operational writes BLOCKED; no trusted product authentication/RBAC exists to reuse |
| B Case domain | PASS | Typed v1.0 case, investigation, attributed lifecycle, independent review, revisions/events, bounded evidence | Human judgment is not source truth; no operational approval created |
| C Evidence | PARTIAL | Exact local asset/maintenance/WO/FMEA references; governed condition fixture; frozen/live semantics, type/unit/time/quality/freshness preservation | RCFA Asset relation remains unresolved; local Data Trust aggregate provider is not configured; factual snapshots intentionally summarize rather than copy records |
| D Backend | PASS isolated; production BLOCKED | Explicit repository/service/authorization layers, versioned strict API contracts, atomic rollback, idempotency and SQL compare-and-swap | Production factory never mounts these routes; trusted identity, writer provisioning and migration runner remain future work |
| E UI | PASS development prototype | Search/filter/pagination, draft editor, notes, bounded evidence, lifecycle/review simulation, timeline, themes/responsive states | Clearly synthetic/browser-memory-only; reload discards demo state; no authenticated product interaction |
| F Quality | PASS available suites | Cockpit, PI, contracts, PostgreSQL, Compose, TypeScript/build, product safety and route/UI smoke | Timescale extension-specific tests skipped; no live operational UAT or full repository security scan claimed |
| G Phase 3 | DESIGN READY | Six use-case assessments, temporal/quality/data-readiness matrix, offline explainable architecture | No deployed analytics, rules, prediction, scoring or synthetic accuracy claim |

## Actual features versus demonstrations

Reusable implementation: frozen typed case/reference contracts; Python-generated
JSON schema with drift test; trusted-principal/asset/owner/reviewer policy;
transactional repository; scoped receipt replay; exact canonical local evidence
adapter; isolated typed REST routes. These work in disposable SQLite/PostgreSQL
and injected API fixtures. They are not exposed by operational create_app.

Development demonstration: Engineering list/detail, create/edit, plain-text notes,
evidence panel, review simulation and activity history. The simulated actor dropdown
is explicitly not authentication; data is synthetic and in browser memory. The
UI never fetches an Engineering backend or source system.

Documentation/design: ADR, threat model, candidate application migration and Phase 3
architecture. Future operational login/session/CSRF, product permissions/directory,
writer role/bootstrap, deliberate migration/rollback, audit retention and end-user
UAT are not implemented. Navigation from factual assets to real cases is deferred
until authorized operational case reads exist.

## Architecture and contracts

Cases belong to the existing separate application-owned Cockpit store, not the
collector-owned Reliability Mart. Independent EngineeringBase metadata has three
candidate tables: engineering_case, engineering_case_event and
engineering_case_receipt. The additive candidate SQL is in application-migrations;
legacy init-db and canonical mart-migrate neither import nor deploy it. There is
no new operational DB or hidden administrative DSN fallback.

A server adapter must supply Principal, roles and exact asset scopes. Authors must
own or be assigned the case; reviewers must have asset scope and be independent
of creator, current assignee and all actual contributors. Former assignees who
never acted are not automatically excluded. Request DTOs cannot supply actor,
reviewer identity, lifecycle status or arbitrary evidence snapshots.

DRAFT → IN_REVIEW → APPROVED/REJECTED; rejected cases may be revised and approved
cases reopened only through explicit authorized transitions/reasons. Review is
never automatic. Atomic SQL expected-revision checks prevent silent overwrites;
case, event and actor-scoped idempotency receipt commit or roll back together.
Full immutable revision snapshots support history; no audit mutation endpoint.
Privileged owner tampering is a residual deployment risk, not solved by a table.

Evidence carries exact asset/record/source/kind, original timestamps, linking actor,
stable version, identity/signal approval, original unit/quality and policy context.
Snapshots are canonical/allowlisted, at most 16 KiB and never raw vendor payloads.
Frozen references preserve original evidence and freshness; live references explicitly
re-resolve accepted local records and can fail as missing/unavailable. Governing
condition identity must be VERIFIED with separately approved signal; retired,
unapproved or ambiguous evidence is unusable. Text/digital/boolean/null are retained;
null is not zero and Good quality is not equipment health. RCFA/Data Trust gaps
fail closed rather than inventing an identity/provider.

## API and activation boundary

The isolated /v1/engineering contracts implement list/get/history/evidence reads,
create/update/note/link/submit/review/revise/reopen mutations. List/history pagination,
asset/status filtering, bounded fields and sanitized typed error codes are tested.
The factory requires explicit enabled service and a trusted principal dependency;
production create_app remains unchanged and does not mount any Engineering route,
even if an environment feature flag is set.

UI defaults OFF. Only development mode with both
NADI_ENGINEERING_WORKSPACE_ENABLED=true and NADI_ENGINEERING_DEMO_ENABLED=true
renders the synthetic prototype. Production with both flags shows an authentication
integration blocker and no forms/demo. Default-off/list and detail paths render the
framework not-found state. In the tested production build these responses stream
with HTTP 200 plus the explicit 404 fallback marker; HTTP status alone is not used
as proof of feature access. No Engineering controls or fixture payload are present.
Existing factual routes and navigation remain available.

Example local development workflow after reviewed dependency setup:

```sh
cd reliability-cockpit/web
NADI_ENGINEERING_WORKSPACE_ENABLED=true NADI_ENGINEERING_DEMO_ENABLED=true npm run dev
```

Use an isolated preview and a test/unreachable COCKPIT_API_BASE for source-free UI
acceptance. This command is not an operational enablement instruction.

## Test evidence

Commands below are repository-relative. PYTHON names the existing project test
interpreter, PYTHONPATH includes the source and tests plus temporary test-only
packages, and disposable DSN variables are supplied privately. No production DSN
or source configuration is loaded; COCKPIT_CONFIG_MODE/PI_CONFIG_MODE are managed.

| Working directory | Exact test/check command | Result |
|---|---|---|
| reliability-cockpit | COCKPIT_CONFIG_MODE=managed NADI_ENGINEERING_TEST_DSN=<disposable local *_test> NADI_MART_TEST_DSN=<disposable local *_test> "$PYTHON" -m unittest discover -s tests | 388 run / 381 pass / 7 Compose opt-in skipped / 0 fail |
| reliability-cockpit | NADI_COMPOSE_TESTS=1 "$PYTHON" -m unittest test_runtime_wiring -v | 12 run / 12 pass / 0 skip / 0 fail |
| pi-collector | PI_CONFIG_MODE=managed "$PYTHON" -m unittest discover -s tests | 191 run / 180 pass / 11 Timescale opt-in skipped / 0 fail |
| reliability-data-contracts | "$PYTHON" -m unittest discover -s tests | 14 run / 14 pass / 0 skip / 0 fail |
| reliability-cockpit/web | npx --no-install tsc --noEmit | PASS |
| reliability-cockpit/web | npm run check:engineering | 21 assertions PASS |
| reliability-cockpit/web | npm run check:product-safety | 23 UI source files PASS |
| reliability-cockpit/web | npm run build | PASS, including dynamic Engineering list/detail |
| reliability-cockpit/web | NADI_WEB_BASE_URL=<isolated preview> npm run smoke:routes | 9 existing routes HTTP 200; no operational upstream |
| repository root | git diff --check | PASS |

PostgreSQL coverage includes canonical Mart migrations 002/003/004, existing factual
preservation, SELECT-only Mart reader tests and Engineering application DDL against
disposable test databases. Two truly simultaneous case edits produce one revision2
and one REVISION_CONFLICT; only one note/event/receipt is added. A restricted fixture
writer is denied audit UPDATE/DELETE/TRUNCATE and relation ALTER. SQLite also covers
rollback, lifecycle, ownership/role/asset gates, actor spoofing, duplicate requests,
unknown evidence, stale source, non-numeric types and strict API serialization.
JSON schema/Python model equality and synthetic UI contract validation are tested.

Initial sandboxed PI runs stalled in a baseline ASGI fixture. A bounded source-free
recheck outside the restrictive sandbox passed both affected tests, then the unchanged
full PI suite passed; no PI code repair or operational dependency change was required.
Timescale is not installed in the disposable plain PostgreSQL fixture, so its 11
opt-in tests remain SKIPPED rather than claimed PASS. Existing tests emit SQLite
ResourceWarnings; no leak-free runtime claim is made.

UI smoke exercised malicious-looking plain text, note attribution, submit and
independent synthetic approval/revision history, disabled actions, source/unit/quality
and UNKNOWN/UNSET presentation, light/dark themes, keyboard focus, 1365px desktop,
768px tablet and 390px mobile without horizontal overflow. Screenshots remain local
synthetic review evidence; no actual user or production measurement is shown.

## Public disclosure and production safety

Changed files and newly reachable candidate commits are reviewed before publication
for credentials, private endpoints/paths, infrastructure IDs/digests and raw source
payloads. Fixtures and local test identifiers are synthetic. No private env,
connection receipt, runtime inventory or backup is committed. The previously recorded
GOV-03 SEC01 history limitation remains: sanitizing documents does not erase older
public revisions; this task does not rewrite shared history or resolve historical
exposure. No actual secret was identified in this candidate audit.

Task-attributable counts: PI/Maximo/CEMS source GET0; business source writes0;
operational DB writes/DDL0; production mapping import/verify0; signal approvals0;
condition acquisition/projection/replay0; history/backfill/discovery0; registry
mutation0; worker/service restart0; deployment0; operational env/credential/grant
change0; DB reset/volume recreation0; CEMS/NK change0; new operational databases0.
Disposable fixture databases/DDL and isolated preview processes are testing only.

No operational inventory was refreshed merely to make a stronger claim. Preservation
is supported by the absence of operational commands/configuration/DB access and the
bounded source diff, not a new live status measurement. Previously accepted mapping,
signal, evidence, WO cursor/floor, workers and private journals are untouched. BFPT
remains REJECTED/FROZEN/DO NOT VERIFY. The approved GOV-03 660/660/1800 settings and
both condition UNSET settings, manual checkpoint and 13 October 2026 00:00 WIB expiry
are unchanged and not extended by development.

## Outstanding blockers and safe next actions

| Gap | Cause / milestone | Tested evidence | Safe next action / authority |
|---|---|---|---|
| SOFTWARE — trusted identity | No product auth/RBAC/session adapter; D/operational E | No-auth and impersonation denied; production routes absent | NADI-PH2-02 identity/session/CSRF + asset permission/directory design and isolated implementation; owner review before operational activation |
| RUNTIME — application writer/migration/audit | Candidate DDL has no operational runner/bootstrap; D/F | Disposable PostgreSQL schema, rollback, CAS and restricted-writer denial | Fail-closed application migration preflight/rollback and minimal grants/retention design; separate deployment/DDL authority required |
| DATA — RCFA/Data Trust references | RCFA asset relation unresolved; aggregate provider absent; C | Explicit fail-closed errors and bounded synthetic Data Trust reference | Reuse reviewed local aggregate contracts; no source calls or inferred RCFA relationships; production data changes require separate authority |
| PRODUCT — real workflow UAT | UI is intentionally local demo; E | Build, flags, synthetic lifecycle and responsive checks | Connect UI to trusted authenticated API only after identity/writer gates; authorized-user UAT after separate rollout review |
| DATA/HUMAN — diagnostic readiness | Latest-only governed condition record; policies/context/history/labels missing; G | Canonical preservation and design matrix | Named engineering review of use case, thresholds/time windows and labeling; no cadence-derived SLA or prediction claim |
| OPTIONAL INFRASTRUCTURE — Timescale regression | Extension unavailable in isolated fixture; F | PI hermetic full suite passes; 11 tests skipped | Run existing Timescale opt-in suite in a separately disposable established fixture; never borrow operational DB for coverage |

## Checkpoints and readiness

Implementation commits: c6af185 ADR; 5a59d51 domain/contracts; 841b148 local evidence;
f37431b isolated backend; 46a0425 historical-contributor review rejection; b1863c5
synthetic UI; 09cc253 concurrency/security. Subsequent design/acceptance commits are
visible on the branch. Repairs are retained as named checkpoints, not hidden.

PHASE 1: CURRENT/PARTIAL, operational acceptance unchanged.
PHASE 2: IN DEVELOPMENT, isolated foundation/prototype ready for review; not COMPLETE.
PHASE 3: DESIGN READY, neither operational nor prediction ready.

Recommended next task: **NADI-PH2-02 — Trusted Engineering Identity & Activation
Contracts**. Select the real identity/session boundary and exact asset/RBAC policy,
implement a reviewed Principal/directory adapter with revocation and browser
CSRF/origin tests, then define deliberate application migration/writer/audit grants.
Continue isolated tests first; do not mount writes or deploy merely by setting flags.
Phase 3 can continue source-free contract work independently, but real diagnostic
claims require engineering evidence/ground truth and operational review.

Related: [ADR](adr/006-engineering-workspace.md),
[threat model](engineering-workspace-threat-model.md),
[Phase 3 design](nadi-phase3-diagnostic-foundation.md),
[roadmap](../../plans/NADI-ROADMAP.md).
