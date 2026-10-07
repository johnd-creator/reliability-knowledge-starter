# NADI-PI-001 — implementation and offline evidence

**IMPLEMENTED / MERGE-CANDIDATE**, 2026-10-07. Not merged, deployed, or live
validated. Phase 1 stays CURRENT / PARTIAL.

## Preflight

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
Existing stores require deliberate idempotent 002 migration before upgraded
workers/API; `init-db` cannot alter old tables. Rollback leaves additive columns
and data intact. Senior review should assess the trusted-caller contract,
strict AF link/WebId lineage prerequisites, bounded-list/24h limits, nullable
JSON storage/API exposure and PostgreSQL/TimescaleDB upgrade procedure.

Next: separately reconcile Mart/runtime and deliberate migration readiness if
required, then **NADI-IDN-002** scoped human-verified Asset↔AF pilot. PI evidence
projection, integration-status acceptance, engineering signal semantics, health
scoring and PdM remain incomplete.
