# AGENTS.md — Power Plant Data Platform

Read [plans/README.md](plans/README.md) first, then the scoped `AGENTS.md` and
`CONTEXT.md` for any component you touch. Root rules govern platform ownership;
scoped rules govern source safety, normalization and implementation details.

## Current Phase-1 runtime handoff — 2026-10-08

Read [authoritative acceptance](plans/NADI-PHASE-1-ACCEPTANCE.md) and
[runtime report](reliability-cockpit/docs/nadi-phase1-runtime-acceptance-001.md).
Merged main c2fb0fc/PR20 foundation is deployed in PI API/NADI API/UI. Existing
Maximo-owned Mart002/003/004 and SELECT-only reader grants are ready; PI004quality
is a separate already accepted migration. Actual control checkout remains0c800da
with accepted private overrides; source workers/projector/volumes are preserved.
PROPOSED0/VERIFIED0, approved signals0, projected condition evidence0. Do not
seed mappings/signals or project technical registry merely because schema exists.
Human crosswalk remains required; API freshness policy is blank/UNKNOWN pending
approved engineering policy. Software runtime ACCEPTED; product BLOCKED, Phase1
CURRENT/PARTIAL. PI technical BAD_QUALITY18 is visible separately from433/433
collection success. Runtime is ready for controlled human-MATCH-gated IDN002B,
not an authorization for autonomous mapping verification/source canary.
Older checkpoint paragraphs below retain historical context; this handoff and
acceptance override their absent-schema/open-PR/candidate deployment statements.

## Existing Mart runtime checkpoint

NADI-RUNTIME-002 uses the existing Maximo Collector DB for Mart, never a new DB.
Public NADI `RELIABILITY_MART_DATABASE_URL` is SELECT-only; legacy `DATABASE_URL`
is separate. Controlled schema/mapping commands require explicit
`RELIABILITY_MART_ADMIN_DATABASE_URL` and expected owner DB, no fallback.
Read [Mart runtime runbook](reliability-cockpit/docs/mart-runtime.md) before DDL
or Compose operations; preserve accepted ignored Maximo/PI overrides, cursors,
recovery floor, volumes and other services. Governance is deliberately applied,
not legacy init-db or automatic source collection. No real pilot mapping is
created by runtime reconciliation; Phase 1 remains CURRENT/PARTIAL.

## 1. Identity, priorities and source of truth

This is one Git monorepo for **Power Plant Data Platform**, evolved from
Reliability Knowledge Starter. Shared foundation: Maximo Knowledge/Collector,
PI Knowledge/Collector, CEMS Collector, Reliability Data Contracts/governance.
**NADI is the main product** (`reliability-cockpit/`). **NK is an intentional
child application** for coal calorific value prediction, outside NADI's
Reliability domain. Future consumers can reuse the same collectors.

At PLATFORM-ROADMAP-001 audit (`main ef07a26`, 2026-10-07), seven components
are merged; NK's eighth logical component is still on
`feature/pi-governed-source-adapter`. Do not invent a local NK path on main,
copy feature binaries/data into a docs task, or count branch work as DONE.

Authority by purpose:

- `plans/PLATFORM-VISION.md`: shared ownership, storage and consumer boundaries.
- `plans/NADI-ROADMAP.md`: Phase 0–5, current Phase 1, next technical task.
- `plans/reliability-cockpit-platform/05-roadmap-implementasi.md`: M0–M8 engineering
  backlog and reconciled milestone status. Old 20-Aug snapshot is historical.
- `plans/NK-ROADMAP.md`: NK child roadmap and branch-only implementation state.
- `plans/REPOSITORY-STATUS.md`: baseline/PR/branch/documentation debt and evidence.
- Scoped contracts, discovery and domain docs: exact accepted source semantics.

Factual NADI Phase 0 is complete within `v0.1.0-rc.1`; Phase 1 is current/partial.
**NADI-PI-001 — Governed PI Source Adapter** is MERGED via PR #12 in
`main 3e981a3c5e20e148feba5b01ec0b1c134ca89205` (2026-10-07). PR #13/#14
Maximo WO acceptance is preserved: registered BSR/IP factual views are CURRENT,
MXR-004 remains PARTIAL. NADI-PI-RUNTIME-001 upgrades the existing PI store with
migration 004 and deploys that reviewed PI main image. New operator/lease/Compose
changes are separately reviewable in its unmerged PR; never confuse the runtime
control checkout, reviewed image, and candidate branch.
See [PI runtime evidence](pi-collector/docs/nadi-pi-runtime-001.md).
NADI-IDN-002 pilot mapping follows PI readiness; first reconcile existing Mart
schema/runtime debt through NADI-RUNTIME-002. PI evidence projection,
integration status and Phase 1 acceptance remain pending. Do not implement
Phase 2–5 or import unrelated feature/NK work merely because it is on a roadmap.

## 2. Reuse stores — no new application database

Continue development using existing collectors, APIs, databases and volumes.
Do not create a database, duplicate collector or new Compose project for a
routine feature or empty-page fix. Explicit architecture/data-migration work
must separately establish ownership and acceptance. Compatible schema additions
belong in the existing owning store. Temporary hermetic test DBs are allowed;
they never replace operational history or contact production.

| Owner | Existing managed service/database | Responsibilities |
|---|---|---|
| Maximo Collector | `maximo-db` / `maximo_collector` | source records, canonical Reliability Mart, Registry and governed mappings |
| PI Collector | `pi-db` / `pi_collector` (TimescaleDB) | source registry, snapshots, history and collection state |
| CEMS Collector | `cems-db` / `cems_collector` | raw/final readings, aggregation and collection state |
| Legacy Cockpit | `cockpit-db` / `cockpit` | Maximo API ingestion and legacy KPIs |
| NK | **No database** | model/scaler/mapping files and session history; PI Collector API consumer |

Compose volumes `maximo-db`, `pi-db`, `cems-db`, `cockpit-db` are project-scoped.
Managed `reliability-cockpit-platform` and alternate external mode have distinct
volumes. Changing project name, `-p`, mode, DB identity or volume can produce
empty parallel stores. Never use `down -v`, delete volumes, truncate tables,
reset cursors or redownload history as a routine fix.

Correct an incorrect DSN only after verifying the documented existing owner;
do not create a replacement DB. Preserve newer rows, cursors and sequences in
any deliberately reviewed local migration. Never overwrite existing `.env` with
an example. Never print full DSNs or interpolated environment/inspect output.

## 3. NADI data paths and semantic boundaries

```text
Maximo → Maximo Collector → local DB
                         ├→ API → cockpit-worker → legacy Cockpit DB/KPIs
                         └→ canonical Mart in SAME Maximo DB
                                    ↓ read-only
                               NADI /v1/reliability/* → Next.js UI
```

`DATABASE_URL` owns the legacy Cockpit store; `RELIABILITY_MART_DATABASE_URL`
selects the existing Mart. They are different read paths, not a request for a
new Mart database. Missing Mart DSN has no legacy-store fallback. Public Mart
queries remain SELECT-only; internal mapping administration is a separate
controlled local write boundary.

Normal Asset membership comes from `reliability_asset_registry`, not every
technical Equipment/Asset Master row. `asset_af_mapping` is governance in that
same Mart. Only one VERIFIED PRIMARY_EQUIPMENT target resolves to MAPPED;
PROPOSED/RETIRED/UNMAPPED/AMBIGUOUS are not usable identity. Never fuzzy-match
names or silently seed verified mappings.

Local Equipment/Work Order projection does not acquire all FMEA/RCFA/health/
overhaul histories. Controlled population is not full history. New merged source
discovery does not automatically update canonical projection/product semantics.
Do not manufacture unresolved relationships, failure identity or health scores.
Legacy KPI code does not authorize presenting blocked factual NADI analytics.

PI/CEMS API bases are configurable, but their NADI projections remain pending.
Do not add PI/Maximo source credentials to NADI. Browser requests go through
`/api/cockpit/*` proxy to `COCKPIT_API_BASE`.

## 4. Runtime checks before changing services

1. Check Git status/branch and the actual Compose definitions/configuration.
   Main and feature have different runtime capabilities; verify the checkout.
2. Inspect Docker, local processes, systemd and cron for worker ownership. Use
   one acquisition worker per source/registry; do not run local venv collection
   alongside an existing worker.
3. Verify DB/API targets without revealing secrets. Managed DBs are internal
   port 5432; old standalone localhost ports are not proof of the active store.
4. Inspect worker completion, cursor and collection timestamps; HTTP 200 and
   recent business-record dates are not proof of source sync freshness.
5. Diagnose NADI DSN, canonical tables, Registry membership and projection state
   before source collection. Keep source and projection cursors distinct.
6. Restart only affected services when authorized work requires it. Successful
   init/registry-loader exits are normal one-shot jobs, not collection daemons.

At merged baseline `3e981a3`, main lacked a managed PI worker and Mart DSN.
NADI-PI-RUNTIME-001 adds opt-in PI migration/worker wiring and managed API Mart
DSN in its review branch. The accepted runtime still uses the original feature
checkout with private reviewed-image overrides. Preserve these overrides; the
new branch does not authorize a broad platform redeploy. Existing Mart is owned
by `maximo-db`; its `asset_af_mapping` table is absent in the audited deployment.
NADI-RUNTIME-002 owns deliberate Mart governance migrations, projection/init
reconciliation and external-mode wiring; do not create a new Mart database.

The earlier deferred HTTP 401 investigation was superseded by the explicit
NADI-PI-RUNTIME-001 source-canary authorization. One known technical GET returned
HTTP 200 with TLS/origin guards intact; one managed snapshot owner was then
started. This does not approve broad AF discovery, history download, automatic
Asset mapping, or governed NADI PI ingestion. See the runtime acceptance and
[operator runbook](pi-collector/docs/runtime-migrations.md) before restarting.

## 5. NK consumer rules

NK supports explicit manual sliders/CSV or PI Collector input. It reads stored
attributes/snapshots through API, without direct production PI/SQL access,
source credentials, collection triggers or a new DB. Do not silently fallback
from invalid automatic inputs to manual values or zero.

Preserve all 13 model feature names/order and model/scaler compatibility.
Confirm mappings, feature meaning, source/training units and evidence; candidate
tags are not approved mappings. Validate finite values, quality, timezone-aware
timestamps, source age and time skew. PS means pemakaian sendiri; exact tag and
W/MW remain unconfirmed. Never infer SFC formula or APH inlet/outlet equivalence.
Manual simulation and ML prediction are not operational control authorization.
Do not retrain or change artifacts incidentally. NK roadmap describes remaining
fetch/review/predict and validation acceptance rather than claiming production
readiness from model files or UI accuracy figures.

## 6. Source safety and contracts

- Production business data is read-only. Maximo OSLC/PI allow GET/HEAD/OPTIONS;
  the sole Maximo POST exception is the controlled `/j_security_check` auth
  handshake prescribed by scoped rules. Never relax source guards or brute-force.
- Preserve BSR/IP and validated equipment scope; field predicates differ per
  object. Verified mappings, not guessed `siteid` filters, govern each request.
- Preserve HTTP rate/1 MiB caps, bounded paging/retry and partial-run cursor
  safety. CEMS only FC03/FC04, register caps/poll floors and operator overrides.
  Preserve PI bulk off-hours/circuit-breaker/chunking/resume controls.
- Source fields/tags/WebIds come from owning knowledge with appropriate verified
  evidence. Missing knowledge creates a bounded discovery task, not an app-side
  guessed identifier. Production discovery execution is explicit opt-in.
- Knowledge statuses unknown/documented/verified/forbidden/deprecated are distinct
  from ingestion eligibility, business semantic approval and runtime health.
- Core contracts: snake_case, explicit units, ISO-8601; vendor fields under
  `sources.maximo/pi/cems`. Public DTO exposure may be narrower than contracts.
- No direct Maximo WO create/update from NADI; future write-back needs separately
  governed authorization. No outbound CEMS reporting implicitly added.
- Never commit/log credentials, cookies, tokens, Authorization headers, raw
  production exports or personal samples. Secrets remain in ignored runtime
  environment files. Report auth status without printing values.

## 7. Code discovery and workflow

Prefer codebase-memory MCP over grep/glob for structural queries. Confirm nearest
project and generation at session start/compaction. Tier 2 verification by
default: search_graph → trace_path → get_code_snippet; check_index_coverage for
all evidence paths and scopes behind exhaustive/negative claims. Query_graph
and get_architecture support wider relationships. Coverage is best-effort;
read stale/partial/skipped/excluded/unknown source directly. Read config/docs or
use `rg` for literal/config searches. A graph from another checkout is not Git
acceptance evidence. Do not count unmerged work as mainline implementation.

Only root is a Git repo. Use scoped conventional commits and a task branch → PR
against latest main. Do not merge, reset, force-push, delete branches or modify
protection unless explicitly requested. Preserve unrelated local changes.

There is no root test command. Each Python component uses its own environment
and mostly hermetic unittest suite; Mart tests can use temporary SQLite. Inspect
web package.json for relevant checks. Do not start operational DBs or call
production to run tests. Documentation-only work uses Markdown/reference checks,
`git diff --check` and a docs-only diff gate; no runtime restart is necessary.


## 11. NADI documentation onboarding and continuity

Before implementing a NADI task, read in order:

1. This `AGENTS.md`, then relevant scoped `AGENTS.md` and any available `CONTEXT.md`.
2. [NADI-CONTEXT.md](NADI-CONTEXT.md) for concise product/runtime context.
3. [PRD.md](PRD.md) for product requirements and acceptance boundaries.
4. [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md) and [UI specification](docs/design/NADI-UI-SPEC.md)
   for proposed tokens, page requirements and reference availability.
5. [Official roadmap](plans/NADI-ROADMAP.md), [Repository Status](plans/REPOSITORY-STATUS.md)
   and [DEV-LOG.md](DEV-LOG.md) for current priorities and independent milestones.
6. Scoped ADRs, contracts, semantic/acceptance reports and the task's exact PR diff.

Verify latest main, open/merged PRs, exact-head CI, active runtime source/dirty state
and data ownership; never infer current status from an old “current” heading.
`plans/NADI-ROADMAP.md` is the sole product roadmap. M0–M8 remains its technical
implementation roadmap; domain documents retain their own authority.

Record requirement IDs and evidence in each task/PR. Treat IMPLEMENTED, TESTED,
MERGED, VISIBLE and ACCEPTED independently, with date, exact SHA and scope. CI
cannot prove runtime visibility or Product Owner/engineer UAT. Record actual PO
decisions separately from proposals; do not infer method/threshold approval from
schema enums, screenshots, design approval or test success. UNKNOWN remains explicit.

Update the owning PRD/design/roadmap/status documents when their scope changes and
append DEV-LOG events at material milestones. Preserve historical evidence and
append corrections instead of rewriting prior log entries. Cite pending PRs at
immutable heads; reconcile overlap without dropping their requirements. Never
silently merge a candidate or create a duplicate implementation/roadmap.

For documentation-only tasks, use a separate clean worktree when the running source
is active. Do not switch it, restart services, modify env/data/collectors or delete
untracked files. Preserve `23496711.xls` and existing isolated Engineering records.
The primary development address is https://localhost:3000; follow the reviewed
single-frontend launcher runbook for separately authorized runtime work. Do not
create another permanent NADI frontend. Existing HTTPS/session/CSRF/RBAC protections
remain intact. Global login design grants no authority to enforce it globally.

Missing design originals must be reported and tracked; never regenerate/substitute
images or claim files were committed without the actual supplied bytes. Design
metrics are illustrative and cannot become engineering evidence. Phase1 review
checkpoints/expiry and accepted facts stay independent of UI/documentation work.
