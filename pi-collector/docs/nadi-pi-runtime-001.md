# NADI-PI-RUNTIME-001 — production runtime evidence

Audit/deployment date: **7 October 2026 (UTC unless stated)**. Task scope is PI
runtime, existing-store migration and bounded source readiness. It does not
accept governed pilot signals or complete NADI Phase 1.

## STATUS

PI store migration/API/source readiness **PASS**. One managed snapshot owner
was activated after stored API acceptance and a successful one-GET canary.
The first cycle completed: **433/433 rows, 0 errors, 0 deactivations**. Wider NADI runtime
remains **PARTIAL**: the existing Mart has no `asset_af_mapping` table.
**GOVERNED CANARY DEFERRED TO NADI-IDN-002**; its existing-Mart prerequisite is
[NADI-RUNTIME-002](../../plans/NADI-RUNTIME-002.md). Operator/Compose changes are
submitted for review, not automatically merged.

## BASELINE

- Verified `origin/main`: `3e981a3c5e20e148feba5b01ec0b1c134ca89205`.
- PR #12 MERGED at `2026-10-07T10:27:39Z`; PR #13/#14 included.
- Fresh review branch `codex/nadi-pi-runtime-001`, directly from that main.
- Runtime control checkout remains `feature/pi-governed-source-adapter`,
  `0c800dac1da6ef863afdb193021176fe7feac073`. It was not switched/reset/merged.
- Reviewed PI image `reliability-cockpit-platform-pi-reviewed:3e981a3` was built
  from the clean merged-main PI context **before** candidate edits. Deployed
  Docker image reference `sha256:71d00590f0e806f62fbcaa9d376f448363fd2783a15150c92666572fb4f2e56c`;
  OCI revision label is full `3e981a3`. All **20 PI API Python source files** were
  hash-compared to main, matching exactly. API has no candidate module mounts.
- New migration runner and worker lease wrapper are this PR's operator scope,
  exercised through private read-only mounts alongside the reviewed main image.
  The candidate Docker image was built/tested separately and **not deployed**.
- Final review HEAD/PR are identified by the commit/PR containing this report;
  they are not embedded as a self-referential document hash.

## RUNTIME INVENTORY

Project `reliability-cockpit-platform`; primary runtime files `compose.yaml`,
`compose.dev.yaml`. Accepted ignored override
`secrets/maximo-wo-recency-002.runtime.yaml` pins Maximo collector/API/projector
image `reliability-cockpit-platform-maximo-reviewed:2eacce47` and the WO-only
serial collection/projection profile. It was preserved in every deployment
command. New ignored PI override `secrets/nadi-pi-runtime-001.runtime.yaml`
pins PI main and private operator/lease tooling. No broad Compose startup ran.

| Component before | Identity / state |
|---|---|
| PI DB | container prefix `08516a94ed6d`, healthy, Timescale image `2.16.1-pg16`, image ID `sha256:3adf01543c37b5b88d3c4998338e0f7f21cb3cdd02bbddea08b09bf60e2289b7` |
| PI API | container prefix `cff384f4b471`, old image `sha256:63809679c1e1e94f895783df0e9dc5f6271716d0d70c2504e129fbea51f7fd45`, started 03:11:01 UTC; replaced only after migration |
| PI init/registry | completed one-shot jobs, exit 0; not acquisition schedulers; not rerun/pruned here |
| PI acquisition | no active PI worker; observed host picollector process was `serve` |
| Scheduler audit | Docker/process inventory, system and user systemd units/timers, matching systemd/cron files and user crontab found no PI collector owner in the checked surfaces |
| Database/user | existing `pi_collector` / `pi_collector`, internal `pi-db:5432` |
| Volume | existing `reliability-cockpit-platform_pi-db`, `/var/lib/postgresql/data`; unchanged |

API was recreated with reviewed main at `2026-10-07T10:49:42.640813604Z`.
Worker started at `2026-10-07T10:52:26.311804973Z`, same reviewed PI image.
Source credentials exist only in the existing worker-side `pi-collector/.env`;
no credentials were copied into the API, migration service, report or repository.
This is bounded scheduler inventory, not proof that unknown external hosts have
no separately scheduled collector.

## PI STORE BEFORE

PostgreSQL **16.3**; TimescaleDB extension **2.16.1**. Database size
**49,877,475 bytes**. Six public operational tables, one `pi_timeseries`
hypertable, **2 chunks**, compression disabled. No dependent views; expected
`ts_insert_blocker` only, no unexpected trigger or active writer transaction.

| Existing table | Rows |
|---|---:|
| pi_attribute_registry | 490 (433 active, 57 retained inactive) |
| pi_snapshot | 433 |
| pi_timeseries | 133,570 |
| pi_collect_cursor | 3 |
| pi_collect_run | 600 |
| pi_backfill_progress | 433 |

Snapshot source timestamps: `1970-01-01T00:00:00Z` to
`2026-10-05T02:25:03.238006Z`; collected timestamps
`2026-10-05T02:10:47.615479Z` to `02:25:04.762775Z`.
Timeseries: `2026-08-12T11:09:52.813003Z` to
`2026-08-18T01:42:00Z`; collected Aug 14 11:11:56.218717 to
Aug 18 01:53:01.094317 UTC. Ancient/missing source timestamps are preserved.

Cursors: backfill_recorded Aug 14 11:12:05.354597 / 85,907 rows;
backfill:1h Aug 18 01:53:24.020102 / 0; snapshot Oct 5 02:15:44.330370 / 433.
Per-attribute backfill last timestamps range Aug 18 01:13:21–01:42:00 UTC.
Latest pre-task run started Oct 5 02:06:50.155594, finished 02:15:44.329194;
historical run errors sum 71,358, not errors introduced by this migration.

Actual partial historical quality schema: nullable `value_type VARCHAR(40)`,
three nullable boolean quality flags on both tables, and nullable timeseries
`units VARCHAR(40)` already exist, with no defaults. `source_value JSON` is
**missing on both**. There is no migration ledger. Migration filenames were
not used as proof of prior schema application.

## BACKUP

Private full custom `pg_dump -Fc`, completed
`2026-10-07T10:35:00.894509828Z` (17:35 WIB):
`secrets/backups/nadi-pi-runtime-001/pi-before.dump` in the original checkout.
Directory 0700, archive/catalog 0600. **1,108,926 bytes**;
SHA256 `569eabdf10118bf2f4c37ea23409cc7b0c82a128f9923891837b539dc45271de`.
`pg_restore --list` validates the archive and includes all six required tables.
Archive bytes remain ignored/private, not in Git.

Timescale catalog circular-FK warnings were emitted by pg_dump; this is a full
schema/data archive, not data-only. No restore drill was performed. Matching
versions, serial restore, Timescale pre/post restore and verification are the
reviewed recovery path in [operator runbook](runtime-migrations.md). Do not
restore over the live store or discard newer collection data.

## MIGRATION

Default status was **PENDING 001–004**, meaning untracked, not absent tables.
The tested minimal runner deliberately replayed guarded 001–003 DDL, verified
the existing hypertable and atomically recorded each file. It then applied the
unchanged main `004_signal_quality_fields.sql` (SHA256
`b40f87fe86097bf2e1eda7c63063629903166627b1cca6c182de74c0dd3f1ffe`).
All four ledger identities now **APPLIED**. No manually fabricated baseline.
Each file is atomic; 5s lock timeout / 30s statement timeout, shared owner lease.

Private existing-runtime command list, always preserving Maximo override:

```bash
# Run from the original runtime checkout; no secrets appear in arguments.
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml -f secrets/maximo-wo-recency-002.runtime.yaml -f secrets/nadi-pi-runtime-001.runtime.yaml --profile pi-maintenance run --rm --no-deps pi-migrate
# PI API only was quiesced; no source worker existed at this point.
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml -f secrets/maximo-wo-recency-002.runtime.yaml -f secrets/nadi-pi-runtime-001.runtime.yaml --profile pi-maintenance run --rm --no-deps pi-migrate python /operator/migrate.py --apply
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml -f secrets/maximo-wo-recency-002.runtime.yaml -f secrets/nadi-pi-runtime-001.runtime.yaml up -d --no-deps --no-build pi-api
```

Measured **0.405s total apply path**, including all four files; individual 004
DDL duration was not separately instrumented. No lock timeout/failure observed.
Only PI API experienced the brief stop/recreate window. Nullable/no-default
columns are expected to avoid a table rewrite; Timescale integration and
actual execution succeeded. Both `source_value JSON` columns are now present;
existing types/flags/units preserved. Existing 433 snapshot and 133,570 history
rows remained null in new source-value evidence immediately after DDL.

**Data counts and content preserved: YES**. All six legacy-table row counts and
order-independent row-content MD5 fingerprints match immediately before/after
migration. Source-value column was excluded because it was newly added; existing
quality, units, timestamps, cursors, run rows and registry data were included.
Hypertable/2 chunks preserved; only a ledger table was added. The initial guarded
001–003 replay also creates four previously missing secondary indexes:
`ix_registry_equipment`, `ix_registry_parameter`, `ix_ts_attr_time` (including
Timescale chunk indexes) and `ix_collect_run_finished`. The pre-migration full
backup catalog contained only the existing `pi_timeseries_timestamp_idx`
secondary index in public. This bootstrap therefore was not purely a metadata
no-op; the 0.405s duration includes those index builds. No legacy row was altered. Later legitimate
snapshot upserts are recorded separately from migration preservation.

## PI API ACCEPTANCE

Performed **before the first live PI call**:

| Endpoint | HTTP / evidence |
|---|---|
| /health | 200 / status ok |
| /attributes | 200 / 433 enabled technical attributes |
| /snapshots | 200 / all 433 old snapshots deserialize |
| /timeseries/{known-local-attribute} | 200 / bounded one-point sample |

Numeric value, Good and snapshot unit fields were compared to DB values in
memory, matching. Nullable new evidence fields are present; historical
`source_value` is null. API has no PI base/auth config; **0 PI source requests**.
Raw identifiers/measurements were neither saved nor printed by acceptance.

## COLLECTION RUNTIME

One opt-in managed `pi-worker` owns the advisory lease. Default snapshot mode,
300s pause **after each completed serial cycle**, 1800s cycle hard timeout,
GET-only source minimum 1s/request and 1MiB streaming cap. No history/backfill
job, registry reload or prune ran. Container restart policy is `no`; failures
require operator attention. Manual/legacy/API collection is outside the lease
and must stay disabled; no global collector-lock claim is made.

First-cycle summary: **433 attributes / 433 rows / 433 requests, 0 errors,
0 deactivations, not aborted**. Started `2026-10-07T10:52:27.690796Z`, finished
`2026-10-07T11:00:55.832534Z` (**508.142s**); snapshot cursor
`11:00:55.834926Z`. Maximum source timestamp `11:00:54.688003Z`; finish/cursor show collection freshness separately from source timestamps.
All 433 snapshots now contain new source evidence from real technical collection.
Registry stays 490/433 active; history stays 133,570; runs become 601; three
cursors and 433 backfill progress rows remain. Existing backfill state is untouched.
Follow-up API GET reads all 433 snapshots and matches source JSON/type/unit/all
quality flags exactly to DB in memory: 365 NUMERIC, 50 TEXT, 18 DIGITAL_STATE.
DB size after first cycle: **63,975,907 bytes**; no claim of constant DB size.
No 24h soak or all-signal freshness certification is claimed. Good=true does
not repair epoch timestamps or missing source units.

## LIVE SOURCE CANARY

Executed **YES**, exactly **1 GET**, **HTTP 200**, duration **4.376s**. Existing
worker-side credentials, TLS verification enabled, configured origin enforced,
redirects disabled; returned redirect=false. Used one active technical attribute
whose ID/WebId matches verified stream-ok knowledge, without discovery/crawl.
Source evidence: timestamp `1970-01-01T00:00:00+00:00`, type `NUMERIC`, source
unit absent, Good=true, Questionable/Substituted/Annotated=false. No numeric
measurement/identifier is published. This proves authentication/origin/response
shape, not fresh governed evidence. Canary source writes=0, local store writes=0.
Subsequent managed technical snapshot collection is separately authorized runtime.

Technical-registry comparison: knowledge catalog **541**, loader verified/ok
set **433**; actual DB **490**, active **433**, retained inactive **57**.
Active attribute ID/WebId pairs exactly match the loader set. DB is a persisted
subset/history of the broader catalog, not a required 541-row copy. No reload,
pruning or forced count correction was used. **TECHNICAL_PI_ATTRIBUTE !=
GOVERNED_ASSET_SIGNAL**.

## GOVERNED CANARY

Executed **NO**. The actual existing Maximo-owned Mart has no
`public.asset_af_mapping`; therefore no legitimate deployed VERIFIED /
PRIMARY_EQUIPMENT / CENTRAL_PI target is available. No mapping fabricated,
imported, verified or inferred. **GOVERNED CANARY DEFERRED TO NADI-IDN-002**;
NADI-RUNTIME-002 must reconcile the existing governance schema first.

## MART/NADI RUNTIME

Actual Mart owner: existing `maximo-db` / `maximo_collector`; Registry 845 rows.
NADI API receives its distinct Mart DSN from the original feature checkout's
**compose.yaml**, not the ignored Maximo image override. Legacy Cockpit DSN
still selects existing `cockpit-db` / `cockpit`; no fallback/new Mart store.
API/Mart/projector/WO worker were not restarted.

Merged main lacks this managed Mart DSN and PI worker; this PR adds minimal
managed API Mart DSN and PI opt-in services/psycopg DSNs. Broader init/projector
ordering, other legacy driver DSNs, actual missing governance DDL, read-only
role and external-mode Mart connection remain **NADI-RUNTIME-002**. Historical
`7149455` was inspected as context, never blindly cherry-picked. No full-platform
cold-start/external-mode acceptance claimed from the small config correction.

## TEST EVIDENCE

Exact test setup used a disposable `timescale/timescaledb:2.16.1-pg16` container
`pi-runtime-migration-test`, `--network none`, tmpfs data, no published ports or
operational volumes. Client containers share that isolated network namespace.
`PI_MIGRATION_TEST_DSN` is test-only and guarded by exact DB name
`pi_runtime_test`; destructive fixtures cannot target the owning production DB.

```bash
W=/home/john-d/.codex/worktrees/nadi-pi-001/reliability-knowledge-starter
# Baseline tests exported from exact main into /tmp/pi-main-tests.
docker run --rm --network none -v /tmp/pi-main-tests/pi-collector/tests:/app/tests:ro -v "$W/pi-collector/migrations:/app/migrations:ro" reliability-cockpit-platform-pi-reviewed:3e981a3 python -m unittest discover -s tests
# 127 passed, 0 skipped/failed.
docker run --rm --network container:pi-runtime-migration-test -e PI_MIGRATION_TEST_DSN=postgresql+psycopg://pi_test:temporary-test-only@127.0.0.1/pi_runtime_test -v "$W/pi-collector/src:/app/src:ro" -v "$W/pi-collector/tests:/app/tests:ro" -v "$W/pi-collector/migrations:/app/migrations:ro" -v "$W/compose.yaml:/compose.yaml:ro" reliability-cockpit-platform-pi-reviewed:3e981a3 python -m unittest discover -s tests
# 151 passed, 0 skipped/failed (127 baseline + 24 new; 11 real Timescale tests).
# Run each from $W/reliability-cockpit:
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p 'test_asset_af_mapping*.py'
# 22 passed.
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_reliability_mart.py
# 41 passed; pre-existing SQLite ResourceWarnings, no failures.
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_cli.py
# 3 passed.
docker build -t reliability-cockpit-platform-pi-runtime-candidate:nadi-pi-runtime-001 ./pi-collector
# Built successfully, not deployed.
docker run --rm --network container:pi-runtime-migration-test -e DATABASE_URL=postgresql+psycopg://pi_test:temporary-test-only@127.0.0.1/pi_runtime_test reliability-cockpit-platform-pi-runtime-candidate:nadi-pi-runtime-001 picollector migrate
# Packaged CLI reads 4 APPLIED identities without source access.
```

Additional packaged worker check holds the fixture DB lease in a parent session
and executes `picollector worker`; exit 2 / lease-owned message occurs before
source/child startup. New tests cover ordering/duplicates, read-only status,
real existing-schema upgrade, partial compatible columns, null legacy evidence,
hypertable/row preservation, idempotent ledger times, checksum drift/history
gaps, incompatible schema refusal, failed-file atomic rollback, empty/misdirected
store refusal, worker exclusion/release, snapshot ownership/interval, private
source config separation and existing-owner Mart DSN. Source requests are
patched to raise throughout integration migrations.

The initial baseline container check omitted its SQL fixture mount and failed
2 fixture-dependent tests; after adding the required read-only migration mount,
all 127 passed. Initial private operator status checks found UID/PYTHONPATH mount
issues; these were corrected before any DDL ran. No hidden failed migration was
ignored. Final checks above are successful runs.

## SAFETY

PI business writes=0; no AF crawl, history download or governed mapping writes.
Maximo changes initiated by this task=0; its existing approved worker continues
normally. CEMS changes=0; NK changes=0. No operational DB created/reset/truncated,
no volume recreated, no cursor/history deletion, no credentials in Git/output.
Only temporary isolated test storage was created and removed.

Post-deploy inventory confirms original container ID, image and start time
unchanged for PI DB, Maximo API/worker/projector, CEMS API/worker and NADI
API/web; all running. Maximo reviewed override preserved. No unrelated code
changes or mixed feature history included. Broader production rollback/soak
acceptance remains outside the evidence established here.

## ROADMAP EFFECT

NADI-PI-001 **MERGED**; existing PI migration 004 and runtime readiness checkpoint
recorded. Phase 0 factual COMPLETE + CURRENT remains; Phase 1 CURRENT/PARTIAL.
NADI-IDN-002 pilot is next after its Mart runtime prerequisite; NADI-ING-PI-001,
NADI-INTEGRATION-STATUS and NADI-PHASE-1-ACCEPTANCE remain pending.

## NEXT RECOMMENDATION

Review the open runtime PR without auto-merge. Complete scoped
**NADI-RUNTIME-002** existing-Mart governance/deployment acceptance, then execute
**NADI-IDN-002 — Pilot Verified Asset ↔ AF Mapping** with human verification.
Keep governed source/projection claims deferred until a real accepted target
exists; technical collection alone does not unlock Phase 1 acceptance.
