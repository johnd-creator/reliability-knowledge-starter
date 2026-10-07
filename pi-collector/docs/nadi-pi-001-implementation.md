# NADI-PI-001 — implementation and offline evidence

**IMPLEMENTED / MERGE-CANDIDATE**, 2026-10-07. Not merged, deployed, or live
validated. Phase 1 stays CURRENT / PARTIAL.

Current branch reconciliation and validation are recorded in
[FIX-01 evidence](#fix-01-reconciliation-and-migration-sequence). Original
preflight/test evidence below remains historical; no production PI deployment
or migration execution is claimed by either checkpoint.

## Original preflight

- Fetched `origin/main`: `a8393ba7d8dfddcae67b14b6153a8056c2f01d34` (matches task baseline).
- Separate managed worktree, clean before edits; new branch
  `codex/nadi-pi-001-governed-source-adapter` starts at that SHA.
- Original `feature/pi-governed-source-adapter` checkout and its untracked export
  remain untouched. No dataset/model/raw production export was copied.
- Read root/scoped instructions, authoritative plans, current PI code/schema,
  PI source-shape evidence, Mart mapping models/resolver/admin and their tests.
- Codebase-memory Tier 2 generation `2026-08-24T09:24:57Z` and graphify supplied
  initial pointers; graph coverage reported stale/missing paths. Exact main /
  candidate Git blobs and worktree source supplied implementation evidence.
  Migration 001's reported parse-gap lines were read directly. No graph
  completeness or new source-discovery claim is made.

## Candidate disposition

Candidate `d23f84851716cec88e43237654a1c58fa79e63d4` was **selectively adapted
and partially rewritten**, rather than committed unchanged. Its PI-only diff
was used as a working base. Existing client/keepalive, configuration, quality
fields, nullable migration columns and stored-data DTO extensions are reused.
No broad candidate merge occurred. `0c800da` was not imported.

Material corrections:

- Null/non-string targets now produce governance errors instead of AttributeError.
- Candidate's element-only assertion could read any supplied Attribute/WebId,
  or caller-supplied metadata. The new boundary requires explicit Database /
  AssetServer lineage, bounded direct Attribute membership and matching metadata
  identity/Element link. Caller-supplied metadata bypass was removed.
- Candidate bounded recorded request count but did not verify returned count.
  The new implementation rejects oversized responses, restricts explicit aware
  intervals to 24h, and rejects missing/out-of-window timestamps.
- Candidate origin guard was retained and strengthened to API root/path checks,
  redirect rejection, decoded streaming cap and per-client serialized rate floor.
  Errors no longer include source URLs, server bodies or transport secrets.
- Candidate discarded text/bool/digital content while keeping only its type.
  Added nullable JSON `source_value` through domain/ORM/upserts/query/API so
  source evidence remains available. Only finite JSON numbers populate legacy
  numeric `value`; malformed values/units/type are controlled errors.
- Recorded/interpolated parsing shares implementation to avoid divergence.
- Candidate README had nested/unclosed code fences and proposed the Cockpit DB
  as alternate PI storage. Corrected formatting and existing PI-store ownership.

No shared contract change is required for this internal source boundary. The
shared numeric condition-reading contract and Mart mapping API remain unchanged;
future NADI projection must deliberately adopt source evidence and lineage.

## Offline test evidence

Commands run from the corresponding component directories in this worktree:

```bash
# cwd: pi-collector
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python -m unittest discover -s tests -v
# cwd: reliability-cockpit
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p 'test_asset_af_mapping*.py' -v
# cwd: repository root
git diff --check
```

Results: **125 PI tests passed, 0 failed, 0 skipped**; **22 existing Mart mapping
registry/admin tests passed, 0 failed, 0 skipped**. Total: **147 passed**.
PI discovery includes all existing registry, collector, hang protection, bulk
safety, activity and scheduling regression tests, plus governance, source
failure/value and storage/API tests.

Tests use fake HTTP transports and in-memory SQLite. Actual ASGI GET responses
verify list/single snapshots and timeseries DTO serialization. Migration test
checks SQL/model column parity and runs corresponding additive column operations
on temporary SQLite, retaining legacy rows/null evidence. It does not run native
PostgreSQL/TimescaleDB migration syntax, acquire production locks, or validate
production data. No live source test is needed or claimed.

## Safety and review limits

- Production PI requests: **0**. Source writes: **0**.
- Production migrations: **0**. Credentials introduced: **0**.
- New operational databases/collectors: **0**; no existing state reset.
- NK, CEMS, deployment, NADI runtime/projection and shared schemas: untouched.
- The previous PI HTTP 401 credential investigation remains deferred.

Review [boundary and upgrade notes](governed-source-boundary.md) before merging.
Existing stores require deliberate idempotent 004 migration before upgraded
workers/API; `init-db` cannot alter old tables. Rollback leaves additive columns
and data intact. Senior review should assess the trusted-caller contract,
strict AF link/WebId lineage prerequisites, bounded-list/24h limits, nullable
JSON storage/API exposure and PostgreSQL/TimescaleDB upgrade procedure.

Next: separately reconcile Mart/runtime and deliberate migration readiness if
required, then **NADI-IDN-002** scoped human-verified Asset↔AF pilot. PI evidence
projection, integration-status acceptance, engineering signal semantics, health
scoring and PdM remain incomplete.


## FIX-01 reconciliation and migration sequence

2026-10-07, existing PR #12 continued; no new PR or automatic merge.
PR #14 was verified merged at 2026-10-07T10:09:16Z before fetching main.
Latest main: `52c67d41115b324e57c93bf82264a38951a6c275`.
Previous PR #12 HEAD: `417dbc8316e1bfbd9ffba0c8bd4777bd186cf8ff`.
Normal main merge: `f2404aeb835cc29dfa6d66e3bd7c3a8c7c7ed417`;
parents are the previous PR head and latest main. Merge had no conflicts;
no rebase or force-push. Maximo source and acceptance files match latest main.
Root/plans status retains Maximo WO and registered BSR/IP NADI CURRENT,
NADI Phase 1 CURRENT/PARTIAL, NADI-PI-001 IMPLEMENTED/MERGE-CANDIDATE and
MXR-004 PARTIAL. Remaining runtime wiring/read-only grants/global scheduler
work is not declared complete by the WO acceptance.

Migration `002_signal_quality_fields.sql` is renamed to
`004_signal_quality_fields.sql`, after existing 001_init, 002_collect_runs and
003_backfill_progress. SQL operations are unchanged; only the sequence comment
is updated. ADD COLUMN IF NOT EXISTS, nullable columns and transactional
additions are retained. README/boundary/tests/status references use final 004.
Historical 002 appears only as replay guidance or a synthetic collision fixture.
If that experimental 002 was applied outside main, final 004 preserves existing
columns/data and adds missing columns using the guards. Existing stores still
need a separately reviewed migration window; this task does not execute it.

The lightweight test_migrations.py checks every PI SQL filename for unique
numeric prefixes, asserts the first four ordered names, permits later unique
migrations, and verifies rejection of the historical 002 collision and a
zero-padding collision. It creates no migration framework or database.

FIX-01 validation:

```bash
# cwd: pi-collector
PYTHONDONTWRITEBYTECODE=1 /home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python -m unittest discover -s tests -v
# cwd: reliability-cockpit
PYTHONDONTWRITEBYTECODE=1 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p 'test_asset_af_mapping*.py' -v
# cwd: repository root
git diff --check
git diff origin/main -- maximo-collector
git merge-base --is-ancestor origin/main HEAD
```

**127 PI tests passed, 0 failed/skipped** (including 2 migration-prefix tests);
**22 Asset↔AF registry/admin tests passed, 0 failed/skipped**: 149 unique tests.
The initial restricted-sandbox suite stalled at ASGI dispatch and was stopped;
the same suite outside that execution restriction completed in 7.097 seconds,
with a 60-second process timeout and fake source transports. No application
change was needed for the test execution issue. Mapping suite: 0.364 seconds.
Repository checks: `git diff --check` passed; 40 relative Markdown references
and balanced fences checked; final SQL operation body matches the prior quality
migration exactly; no DROP/TRUNCATE/DELETE/UPDATE/NOT NULL additions. Guarded
columns stay nullable. Maximo source/evidence, Cockpit implementation, NK and
Compose paths match latest main; PI governed runtime code matches the previous
PR #12 head. Added files/diff were checked for credentials and operational
artifacts. No live source validation is claimed.

Governed source/runtime implementation remains unchanged from previous PR #12
HEAD: VERIFIED + PRIMARY_EQUIPMENT + CENTRAL_PI; trusted identity lineage,
same-origin checks, redirect refusal, GET-only governed reads, bounded direct
attributes, <=24h recorded interval, <=20 samples and preserved value/type/unit/
timestamp/quality evidence. Text/digital/bool/null never silently become zero.
NADI does not gain PI credentials, a live proxy or PI evidence projection.

FIX-01 safety: production PI requests 0; production migrations 0; Maximo
runtime/data/cursor changes 0; parked groups resumed 0; pilot mapping writes 0;
new operational stores 0; credential introduction/exposure 0. NK is untouched.
Tests use fake transports and temporary SQLite only. PR #12 remains open and
unmerged; senior merge review precedes separately scoped runtime/migration
readiness and NADI-IDN-002 human-verified pilot.
