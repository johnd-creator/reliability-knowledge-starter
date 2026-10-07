# NADI-RUNTIME-002 — existing Mart governance/runtime acceptance

**PASS / candidate for senior review. READY — NADI-IDN-002.**
No real pilot mapping was created. Phase 1 remains CURRENT / PARTIAL.

## Baseline and provenance

PR #15 confirmed MERGED at `2026-10-07T12:45:45Z`. Fetched `origin/main`
`c052d7d7d007c2a670300d0eb9d08dda8d93f473` is its merge result. Fresh managed
worktree/branch `codex/nadi-runtime-002` starts there, not the unmerged PI branch.
Implementation/image revision is `8d92c25cd62f7fad21b92b0abd224f52f78bba58`;
subsequent report/roadmap commit changes documentation only. Historical
`71494550714f77af8f9cb68c90722732e18b5ca8` was inspected for file-level evidence,
not merged, copied wholesale or cherry-picked.

Runtime control remains `/home/john-d/Music/reliability-knowledge-starter`,
checkout `feature/pi-governed-source-adapter` at
`0c800dac1da6ef863afdb193021176fe7feac073`. Candidate development is isolated in
`/home/john-d/.codex/worktrees/nadi-runtime-002/reliability-knowledge-starter`.
User's untracked spreadsheet and existing source dotenv/overrides are untouched.
Graph generation `2026-08-24T09:24:57Z` was used for Tier 2 discovery; its older
checkout/missing/partial paths were directly read against this merged baseline.

## Runtime inventory

Compose project/network: `reliability-cockpit-platform` /
`reliability-cockpit-platform_platform`. Actual base files: `compose.yaml` and
`compose.dev.yaml` in the control checkout. Existing ignored overrides retained:

- `secrets/maximo-wo-recency-002.runtime.yaml`: Maximo worker/API/projector
  image `reliability-cockpit-platform-maximo-reviewed:2eacce47`; WO-only loop
  `mxcollector sync mxwodetail`, post-cycle pause 300s. Recovery floor unchanged.
- `secrets/nadi-pi-runtime-001.runtime.yaml`: accepted PI image `3e981a3` and
  private operator/lease mounts; not redeployed by this task.
- New ignored `secrets/nadi-runtime-002.runtime.yaml`: **cockpit-api only**,
  tested image `reliability-cockpit-platform-nadi-runtime:runtime-002`, explicit
  SELECT-only reader and original legacy target, managed dotenv bypass.

| Service | Container before / after | Runtime image / start |
|---|---|---|
| maximo-db | `81e2460cd91c` unchanged | postgres 16.4-alpine; 02:08:05.93503126Z |
| maximo-api | `ed047f359f0a` unchanged | reviewed 2eacce47; 09:10:58.436744457Z |
| maximo-worker | `c048faaddb64` unchanged | reviewed 2eacce47; 09:32:17.207250815Z |
| mart-projector | `b4e968d59bf4` unchanged | reviewed 2eacce47; 09:32:55.07104331Z |
| cockpit-api | `fd0f2a0be33d` → `09c8e0b560d2` | candidate runtime-002; 2026-10-07T13:13:43.125850561Z |
| pi-db / pi-api / pi-worker | `08516a94ed6d` / `415e9089e842` / `af1c19eb1c6d` unchanged | accepted PG/PI images and start times retained |

All dates above are 2026-10-07 UTC. Machine comparison confirms **only**
cockpit-api changed among all platform containers/images/start times, including
CEMS, Maximo/projector, PI, legacy worker, web and all DBs. NADI web was not
restarted. Candidate API image digest `sha256:ff51c93ae5483d0c14cad3dd2421ddcd48605b57c8e944ad5fbad4ecb143c6fc`.

Existing DB/volume owner is `maximo-db/maximo_collector`, role
`maximo_collector`; volume `reliability-cockpit-platform_maximo-db` unchanged.
Before: no dedicated reader role, API Mart DSN used owner/superuser account.
After: API `RELIABILITY_MART_DATABASE_URL` → maximo-db/maximo_collector as
`nadi_mart_reader`; legacy `DATABASE_URL` → cockpit-db/cockpit as `cockpit`.
No full DSN/credential is reported. Owner stays maximo_collector. Actual
`.env.platform` received only new private Mart reader/admin settings, preserving
existing values; private previous platform copy retained. Public API receives
no admin URL/reader-provision password or PI/Maximo source credentials.

## Mart before and preservation

Operational catalog contained **17 public tables**, all owned by
maximo_collector. No Mart governance migration ledger. `asset_af_mapping`
**ABSENT**; not inferred from model/migration existence. Registry **845**,
asset_master/equipment **11,845**, maintenance **69,617**, work_order **113,884**.
Controlled FMEA/RCFA/health each **100**, overhaul **1**. Existing PK/index
inspection verified canonical asset and registry identities and projection key.

Initial WO cursor: `2026-10-07T12:19:33Z`; recovery-floor marker remains exactly
one row with watermark `2026-08-21T03:56:54Z`. Initial projection watermarks:
asset `2026-10-01T05:40:10Z`, maintenance `2026-10-07T12:19:33Z`, SUCCEEDED.
The source/independent projector continued normally throughout the task.

Inside the bounded governance transaction, **all 17 pre/post counts AND sorted
row-content MD5 aggregate fingerprints were identical**. Counts at DDL:

| Existing table | Before = after |
|---|---:|
| asset_health_assessment | 100 |
| asset_master | 11,845 |
| collect_run | 67 |
| equipment | 11,845 |
| equipment_status_history | 13,035 |
| fmea_assessment | 100 |
| item | 0 |
| labor | 97 |
| maintenance_event | 69,617 |
| mart_projection_state | 2 |
| overhaul_event | 1 |
| person | 16,929 |
| rcfa_analysis | 100 |
| reliability_asset_registry | 845 |
| service_request | 4,978 |
| sync_cursor | 1 |
| work_order | 113,884 |

Fingerprints include full sync_cursor, collect_run recovery evidence, Registry,
controlled records and mart_projection_state; payload never leaves PostgreSQL.
No row loss, cursor overwrite, registry mutation or projection reset occurred.

## Private backup

Full `pg_dump -Fc`, existing maximo_collector owning DB, before any DDL.
Started `2026-10-07T12:57:02.642483+00:00`, completed `2026-10-07T12:57:04.393083+00:00`.
Size **13,186,179 bytes**; SHA256:

`39ef841935868aa965c59ebc15746f161827fcaaa8fb808e4d08436703f5bb28`

Private ignored directory `secrets/nadi-runtime-002/`, directory 0700 and dump
0600. `pg_restore --list` catalog validated all required Collector/Mart/cursor/
recovery/registry/projection tables. Backup covers all existing tables and
state, not merely governance. No restore drill is claimed and no backup bytes
or raw source records were published. Operational DB/volume never replaced.

## Canonical governance migration

Sources are unchanged merged Cockpit SQL **002_asset_af_mapping.sql** and
**003_asset_af_mapping_provenance.sql**. Runner `src/services/mart_migrations.py`
selects only these, not unrelated legacy 001 or Maximo initializer. Default
status read-only creates no schema/ledger. Explicit admin DSN + expected DB and
existing Collector/Mart anchors fail closed on wrong DB/unknown schema. One
transaction advisory lease, 5s lock / 30s statement bounds, short local SHARE
locks and pre/post preservation checks; ledger records filenames/SHA256/time.

Applied **8.027s** at 13:09:12 UTC. Ledgers:

- 002 SHA256 `e2f2464031c0c710f1471863c5f55493165b95421bbe6bea711d19827af8bb6a`.
- 003 SHA256 `4cf35acd7979babe71069c05c5548a92252b17f5e1933f690f545a58fefa7d31`.

Post-apply status ready; explicit second apply is **no-op (0.054s)**. Eight
validated constraints (PK, Asset FK RESTRICT, status/role/evidence and three
provenance checks) and four indexes including active-exact partial uniqueness.
Schema represents canonical Asset, PI source, AF server/database/element,
PRIMARY_EQUIPMENT, PROPOSED/VERIFIED/RETIRED, creation/update/verification/
retirement timestamps, actors/evidence/notes and optional identity snapshots.
No independent mapping table, undocumented seed or source call.

## Asset↔AF administration and reader access

Operational mapping table **exists and remains 0 rows**. Real registered Asset
mapping GET HTTP 200 / UNMAPPED. Actual-Mart CLI admin factory/readiness and
CSV dry-run were exercised with clearly nonexistent synthetic Asset; rejected
UNKNOWN_ASSET, zero writes. Full dry-run → PROPOSED import → human verify →
MAPPED resolution → retire → UNMAPPED tested on canonical migrated PostgreSQL
**disposable fixture only**, not operational identities. Synthetic fixture is
not production mapping evidence. No real pilot execution or AF discovery.

Role `nadi_mart_reader`: LOGIN, NOSUPERUSER/NOCREATEDB/NOCREATEROLE,
NOINHERIT/NOREPLICATION/NOBYPASSRLS, no membership/ownership, transaction read-only
by default; explicit SELECT only on nine named Mart tables plus CONNECT/USAGE.
Real login returns registry 845; SELECT mapping true, any mapping table-write
privilege false, transaction_read_only on. No blanket future-table grants.
Fixture attempts DELETE/INSERT/ALTER fail even after SET TRANSACTION READ WRITE.
PUBLIC/global privileges are preserved; SELECT-only refers to Mart relations,
not a global prohibition on PostgreSQL temporary objects.

Mapping administration needs separate `RELIABILITY_MART_ADMIN_DATABASE_URL`
and expected owner DB; it has **no reader/legacy fallback** and checks schema
readiness before opening command store. Local projector keeps existing owner
writer DSN; public API retains query facade and PostgreSQL read-only transactions.

## Managed/external reconciliation

Source-controlled managed Compose explicitly supplies reader/admin DSNs from
platform env with packaged psycopg v3 URLs. `mart-migrate` and `mart-reader` are
opt-in status-by-default maintenance services. `mart-ready --require-ready`
checks existing owner schema without DDL/source acquisition. Projector/API wait
for gate; local incremental projector has contracts read-only at /contracts,
explicit existing writer DSN, no source credentials/bootstrap/registry load.
Cockpit init creates only legacy tables and receives no Mart DSN.

Existing operator runtime remains on its inspected older control checkout;
only API was replaced using `--no-deps --no-build` and all accepted overrides.
The running projector was already locally initialized and remains untouched;
new gate defines reproducible future starts, not an unnecessary source restart.
Mainline source-controlled reconciliation is in this candidate. Do not deploy
all mainline services mechanically or drop the reviewed WO override.

External Compose requires explicit reachable **existing** Mart reader DSN,
with Linux host-gateway for host-local external stores; missing DSN fails config.
No external Mart DB/init/projector/admin credential/source worker. Legacy init
stays separate. External runtime is clean-config tested, not separately deployed
by switching this managed production's project/mode/volume.

## Regression / PI isolation

NADI factual routes and web proxy HTTP 200. At `2026-10-07T13:16:40.561565Z`:
Registry 845, 7-day activity **801**, 30-day **1,988**, 90-day **4,226**.
Pre-check at 12:55:56Z was 806 / 1,988 / 4,226; five events aged out of the
7-day rolling window. Independent live projection updates changed source dates
normally. Old accepted API image and new image with the **same fixed as_of and
current Mart** produce identical summary (803 / 1,985 / 4,223 at that earlier
as_of); those values are query comparison evidence, not a frozen source snapshot.
No factual reader code change/regression is inferred from wall-clock counts.

WO cursor naturally advanced to `2026-10-07T13:03:52Z`; recovery floor remains
unchanged. Latest observed cycles: 25 rows, 0 errors, ~6.84/7.67/8.60s; no
bootstrap repeated. Projection succeeded at 13:14:21Z, maintenance watermark
matches source cursor; maintenance population remains 69,617.

PI container/image/start identities unchanged. Migration 004 applied_at
`2026-10-07T10:49:24.644410Z`, checksum
`b40f87fe86097bf2e1eda7c63063629903166627b1cca6c182de74c0dd3f1ffe`, unchanged.
433 active registry, 433 snapshots, history 133,570, existing Timescale
hypertable, accepted worker and stored health 200. Accepted first 433/433,
0 errors evidence preserved. No additional PI source requests, migration apply,
registry reload, backfill, cadence/config change or PI restart by this task.

## Test commands and counts

```bash
W=/home/john-d/.codex/worktrees/nadi-runtime-002/reliability-knowledge-starter
docker build -t reliability-cockpit-platform-nadi-runtime:runtime-002 "$W/reliability-cockpit"
docker run -d --name nadi-runtime-002-test --network none --tmpfs /var/lib/postgresql/data:rw -e POSTGRES_DB=nadi_runtime_test -e POSTGRES_USER=fixture_owner -e POSTGRES_PASSWORD=fixture-only postgres:16.4-alpine
docker exec nadi-runtime-002-test pg_isready -U fixture_owner -d nadi_runtime_test
docker run --rm --network container:nadi-runtime-002-test -e DATABASE_URL=sqlite+pysqlite:///:memory: -e COCKPIT_CONFIG_MODE=managed -e NADI_MART_TEST_DSN=postgresql+psycopg://fixture_owner:fixture-only@127.0.0.1/nadi_runtime_test -v "$W/reliability-cockpit/src:/app/src:ro" -v "$W/reliability-cockpit/tests:/app/tests:ro" reliability-cockpit-platform-nadi-runtime:runtime-002 python -m unittest discover -s tests
# 140 total: 135 passed, 5 Compose tests skipped inside image (Docker CLI absent).
# Includes all mapping 22, Mart 41 and CLI 3; 14 real PostgreSQL governance tests.
# Targeted same fixture/args: -p test_mart_migrations.py -> 15 passed (14 PG + 1 config).
cd "$W/reliability-cockpit"
NADI_COMPOSE_TESTS=1 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_runtime_wiring.py
# 9 passed, including all 5 clean managed/external Compose checks skipped above.
cd "$W/pi-collector"
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python tests/compose_clean_check.py
# PASS: PI credential isolation unaffected by Mart Compose additions.
```

Across image/host runs all 140 distinct checks execute/pass; four config tests
are repeated on host, not counted as extra unique tests. Fixture has no external
network, published port or operational volume; synthetic lifecycle identities
never enter production. Candidate Docker package CLI, real read-only status,
wrong-DB/anchor/schema/ledger drift, atomic rollback, lease exclusivity,
idempotency and actual reader/API/proxy checks pass. Temporary test DB removed
after verification. Relevant changed-source whitespace/document links checked.

Initial failures were safely corrected before DDL: PostgreSQL reflected type
rendering, Compose extra_hosts output shape and explicit SQLite legacy fixture.
First packaged status lacked explicit SQL path and failed without DDL; image
now pins /app/migrations. Two PI read-only metadata queries initially used wrong
column names, corrected from actual catalog; no PI schema/runtime change.
Rolling-window nondecreasing assertion was replaced by fixed-as_of old/new
query equality. None of these were hidden production DDL failures.

## Safety and roadmap

Maximo business writes **0**, PI business writes **0**, CEMS changes **0**, NK
changes **0**, new operational DBs **0**. No owning-store drop/truncate/reset,
WO cursor/floor deletion, volume recreation, raw sample/credential publication,
auto-mapping, AF crawl, source history download, score or projection invention.
Authorized local governance DDL/ledger/reader grants are the only new DB state;
accepted collectors continue their original authorized background schedules.

NADI-PI-001 ✅ MERGED; NADI-PI-RUNTIME-001 ✅ ACCEPTED (PR #15 MERGED);
NADI-RUNTIME-002 current/candidate with runtime scope PASS; NADI-IDN-002 next.
Phase 1 stays **CURRENT / PARTIAL**: no real VERIFIED pilot mapping, governed
PI canary/projection/integration status or broader Phase 1 acceptance claimed.
Existing Mart now legitimately hosts/resolves governed identity without schema
ambiguity. **READY — NADI-IDN-002** under its separate bounded human-evidence
workflow. Keep this task's PR OPEN/UNMERGED for final senior review.
