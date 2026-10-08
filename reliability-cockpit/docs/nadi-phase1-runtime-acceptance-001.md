# NADI-PHASE1-RUNTIME-ACCEPTANCE-001

## Verdict and source baseline

**STATUS: PASS — bounded software runtime foundation.**
**PHASE 1 SOFTWARE RUNTIME FOUNDATION: ACCEPTED.**
**PHASE 1 PRODUCT ACCEPTANCE: BLOCKED.**
**HUMAN_CROSSWALK_REQUIRED; FRESHNESS_POLICY_PENDING.**

Date: 8 October 2026 Jakarta. Baseline inspection 2026-10-07T23:18:07.511941+00:00;
post-deploy inspection 2026-10-07T23:32:05.404710+00:00. Exactly merged origin/main
`c2fb0fc686396e79c19f42af46694673827493a9` was built/deployed. PR20 MERGED at
2026-10-07T22:27:11Z. Evidence branch
`codex/nadi-phase1-runtime-acceptance-001`; its documentation PR remains open
and unmerged. Branch evidence commits are not deployed application source.

GitHub metadata deviation: PR19 was **already** marked MERGED at
22:27:13Z, mergeCommit211faec4b0916361491d3ca8bc01ada2f0072284, although the task
expected superseded/unmerged. That commit is an ancestor of required main,
which remains exactly c2fb0fc. The executor merged neither PR, made no further
merge/reversion and did not deploy PR19 separately. This discrepancy does not
change the exact authorized source tree; it is recorded rather than hidden.

No new code patch or candidate code was deployed. A non-secret UI build setting
was corrected using Next.js's existing .env.production support; see deployment.
Prior bundle/test evidence remains historical, not rewritten as live projection.

## RA-01 / RA-02: actual runtime and deployment plan

Operational control checkout: `/home/john-d/Music/reliability-knowledge-starter`,
SHA `0c800dac1da6ef863afdb193021176fe7feac073`. It stays at this historical SHA deliberately.
Tracked files are clean; the unrelated untracked `23496711.xls` is preserved.
Build source was a fresh clean worktree at exact merged c2fb0fc,
`/home/john-d/.codex/worktrees/nadi-phase1-runtime-acceptance-001/reliability-knowledge-starter`.
Changing a control checkout is not necessary to replace reviewed immutable images.

Existing Compose project: `reliability-cockpit-platform`.
Existing network: `reliability-cockpit-platform_platform`.
Accepted invocation, in order, retains these files in the control checkout:

1. compose.yaml
2. compose.dev.yaml
3. secrets/maximo-wo-recency-002.runtime.yaml
4. secrets/nadi-pi-runtime-001.runtime.yaml
5. secrets/nadi-runtime-002.runtime.yaml
6. secrets/nadi-phase1-runtime-acceptance-001/runtime.yaml (new, private, consumer-only)

Private .env.platform remains the managed configuration authority, permissions
0600, content unchanged. Existing accepted overrides are byte-for-byte unchanged.
Controlled migration uses a separate0600 operator admin env, never the public API.
Effective Compose was evaluated internally; retained audit configuration is
redacted. Temporary interpolated working config and operator credential copy
were removed after use; original private authority remains unchanged. Only environment
**names**, sanitized DB identities and non-secret policy values were reported.
Comparison proves only pi-api/cockpit-api/cockpit-web definitions change;
all other services, volume/network definitions and source-worker commands match.
Historical source-control base/accepted overrides are preserved to avoid changing
parked Maximo groups, PI ownership, legacy initialization or CEMS/NK behavior.
Only changed consumer images/wiring are deployed from merged main; no broad up.

| Boundary | Actual DB target (password omitted) | Role |
|---|---|---|
| Mart / Collector owner | maximo-db / maximo_collector | maximo_collector |
| NADI RELIABILITY_MART_DATABASE_URL | maximo-db / maximo_collector | nadi_mart_reader |
| Legacy NADI DATABASE_URL | cockpit-db / cockpit | cockpit |
| PI store | pi-db / pi_collector | pi_collector |
| CEMS store, untouched | cems-db / cems_collector | cems_collector |

Four existing volumes remain mounted, never recreated:
reliability-cockpit-platform_maximo-db, _cockpit-db, _pi-db and _cems-db
(the latter three share the same full project prefix).
NADI reader DSN never falls back to legacy DATABASE_URL. Actual legacy DB
inspection confirms owner/database cockpit and zero condition relations; governance
was not initialized in that store.
PI source credentials remain only at the existing worker/source boundary;
pi-api and cockpit-api have no PI/Maximo source credential or Mart admin env.

Before deployment, all18 running container identities were recorded:

| Service | Before ID | Image | Started at UTC |
|---|---|---|---|
| cockpit-api | `09c8e0b560d2` | `reliability-cockpit-platform-nadi-runtime:runtime-002` | 2026-10-07T13:13:43.125850561Z |
| pi-worker | `af1c19eb1c6d` | `reliability-cockpit-platform-pi-reviewed:3e981a3` | 2026-10-07T10:52:26.311804973Z |
| pi-api | `415e9089e842` | `reliability-cockpit-platform-pi-reviewed:3e981a3` | 2026-10-07T10:49:42.640813604Z |
| maximo-worker | `c048faaddb64` | `reliability-cockpit-platform-maximo-reviewed:2eacce47` | 2026-10-07T09:32:17.207250815Z |
| mart-projector | `b4e968d59bf4` | `reliability-cockpit-platform-maximo-reviewed:2eacce47` | 2026-10-07T09:32:55.07104331Z |
| maximo-api | `ed047f359f0a` | `reliability-cockpit-platform-maximo-reviewed:2eacce47` | 2026-10-07T09:10:58.436744457Z |
| cockpit-web | `1a2c8ebe6b37` | `reliability-cockpit-platform-cockpit-web` | 2026-10-07T03:11:02.426556742Z |
| maximo-web | `92be590c71d3` | `reliability-cockpit-platform-maximo-web` | 2026-10-07T03:11:02.04157598Z |
| pi-web | `87fd26b3aad0` | `reliability-cockpit-platform-pi-web` | 2026-10-07T03:11:01.939584097Z |
| cems-web | `9cd8465ca59e` | `reliability-cockpit-platform-cems-web` | 2026-10-07T03:11:03.508479658Z |
| cems-api | `f371ba970c81` | `reliability-cockpit-platform-cems-api` | 2026-10-07T03:11:03.013630698Z |
| cockpit-worker | `235577cf0fbf` | `reliability-cockpit-platform-cockpit-worker` | 2026-10-07T02:08:19.96911512Z |
| cems-worker | `a10da3c8de94` | `reliability-cockpit-platform-cems-worker` | 2026-10-07T02:08:20.026449099Z |
| cems-aggregator | `f6ecba1fe0c4` | `reliability-cockpit-platform-cems-aggregator` | 2026-10-07T02:08:20.020393507Z |
| pi-db | `08516a94ed6d` | `timescale/timescaledb:2.16.1-pg16` | 2026-10-07T02:08:05.922667907Z |
| maximo-db | `81e2460cd91c` | `postgres:16.4-alpine` | 2026-10-07T02:08:05.93503126Z |
| cems-db | `0c5de699a381` | `postgres:16.4-alpine` | 2026-10-07T02:08:05.928491173Z |
| cockpit-db | `a3f2c64a97b6` | `postgres:16.4-alpine` | 2026-10-07T02:08:05.937823162Z |

Five completed/stopped one-shot containers were also inventoried privately;
none was started by this task. Twenty existing container identities, including
these one-shots and all other running services, remain unchanged after deployment.

## RA-03: full private backup

Full existing maximo_collector database, `pg_dump -Fc` (not table-only).
Started 2026-10-07T23:19:36.009156+00:00; completed 2026-10-07T23:19:40.008456+00:00.
Duration 3.999s; **13,198,605 bytes**.
Backup permissions0600; parent0700. SHA256:

`6ae19af92b30ac5d960755e40e289894e757e2621a1b755df98d8cf34c7a32c3`

`pg_restore --list` succeeds, 130 catalog entries.
Catalog explicitly contains TABLE DATA for asset_master, maintenance_event,
reliability_asset_registry, sync_cursor, mart_projection_state, asset_af_mapping,
plus the rest of the full owning DB. Ledger, Collector rows and recovery evidence
are included. Catalog validation is not a restore drill; no restore was performed.
Bytes/catalog stay ignored and private under
`secrets/nadi-phase1-runtime-acceptance-001/`; no backup export is committed.

Before DDL, one read-only repeatable-read snapshot recorded:

| Relation | Rows | Aggregate MD5 content fingerprint |
|---|---|---|
| asset_master | 11845 | `2dbf6f2cc45df6552fcf3557ced68495` |
| maintenance_event | 69619 | `a90394132fc762043bac723e7161c0cc` |
| reliability_asset_registry | 845 | `45301e59249148f1912e364ece5a7def` |
| sync_cursor | 1 | `6f69692fc7f29308171c762ce940f424` |
| mart_projection_state | 2 | `064dc844f5549499cf588d3df0bd2ca4` |
| asset_af_mapping | 0 | `d41d8cd98f00b204e9800998ecf8427e` |

These are aggregate hashes, not source payload exports. Background workers are
allowed to advance state outside the migration's locked preservation transaction.

## RA-04 / RA-05: canonical Mart004

Exact-main packaged runner, existing owner DSN and expected database explicitly
configured. `cockpit mart-migrate`:002APPLIED /003APPLIED /004PENDING;
no checksum/anchor/constraint drift, untracked or partial condition schema.
No legacy initializer or PI migration was run.

`cockpit mart-migrate --apply`: only004_condition_evidence.sql applied.
Duration **7.968s**. Ledger applied_at
2026-10-07T23:20:33.704255Z. SQL SHA256:

`000dce2def0acb4f6e0fac33636ab9db946841fa72af3785f3300745867a7667`

The canonical runner uses its existing advisory lease, bounded lock/statement
timeouts and SHARE locks across17 factual Collector/Mart tables. **All17 counts
and full aggregate content fingerprints before/after are identical**, including
collect_run, sync_cursor and mart_projection_state. Mapping count0 before/after;
no mappings are seeded or changed. Representative factual counts:11845 Asset
Master,113886 WO,69619 maintenance,845 Registry;185 collect_run inside the locked
transaction. Independent mapping fingerprint remains empty MD5d41d8cd98f00b204e9800998ecf8427e.

New tables: condition_signal_selection, condition_evidence_latest,
condition_projection_state. Canonical types, PKs, RESTRICT lineage FKs, approval
constraint and indexes pass runner validation. Each table has **0 rows**.
Second `--apply` is a no-op: applied[], readytrue,002/003/004APPLIED,0.068s.
002/003 checksum/applied timestamps remain unchanged. No source acquisition,
bootstrap, cursor/floor mutation or unrelated initializer is triggered.

## RA-06: reader access

Canonical `cockpit mart-reader` status then `--apply` reconciles the existing
nadi_mart_reader. It grants SELECT on the12 explicitly named canonical relations,
adding only the three condition tables to its existing nine-table boundary.
Existing role/password is reused; no credential rotation or owner change.

Actual catalog evidence, after grants:

- LOGIN, CONNECT to maximo_collector and USAGE public: true.
- SELECT on all three condition relations and approved factual/Mart tables: true.
- INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER: false on **every** public table.
- CREATE on database/in public: false; owned schemas0. No relation/database ownership, memberships,
  superuser, CREATEDB, CREATEROLE, REPLICATION, INHERIT or BYPASSRLS.
- ALTER of owned Mart relations is unavailable because the reader owns none and
  has no privileged membership/superuser capability.
- Authenticated deployed connection reports current_user=nadi_mart_reader,
  current_database=maximo_collector, transaction_read_only=on.

Operational checks use ACL/ownership inspection and real SELECT login, without
attempting operational DML/TRUNCATE. Disposable PostgreSQL tests independently
prove DML/ALTER denial even after SET TRANSACTION READ WRITE. PUBLIC privileges
are unchanged per accepted runbook; this proves the persistent Mart relation/DDL
boundary, not a new global prohibition on temporary PostgreSQL objects.
Admin/projector owner credentials remain separated from public readers/API.

## RA-07: exact merged software deployment

Each image is built from c2fb0fc tracked source, with OCI revision label equal to
that full SHA; builds completed before documentation edits. Immutable image IDs:

| Service | Tag | Final image ID |
|---|---|---|
| pi-api | `reliability-cockpit-platform-phase1-pi-api:c2fb0fc` | `sha256:04f86777d82030346218c009405d2b5f370c2293518f89229b8ca7cff6f7a7d7` |
| cockpit-api | `reliability-cockpit-platform-phase1-cockpit-api:c2fb0fc` | `sha256:fa71e47ef1ed240c944bf353be3bae297b142a3f0c43c4b00a6cf02b91716789` |
| cockpit-web | `reliability-cockpit-platform-phase1-cockpit-web:c2fb0fc` | `sha256:47a90f28db112f63dd6549b2536cf1089543047a26b2ca24c5befd14595254e1` |

Initial web build exposed a deployment configuration issue: Next rewrites were
compiled with default127.0.0.1:8000, which is the web container itself. SSR route
shells still returned200, but hydrated data/proxy requests failed. The existing
supported non-secret build environment was then supplied from effective accepted
Compose: **COCKPIT_API_BASE=http://cockpit-api:8000** via a temporary
web/.env.production. No tracked code, Dockerfile or credential changed. The file
was removed from the source worktree after build. The final image's routes
manifest proves the internal destination before web-only replacement; proxy
integration-status/data-trust now both return200 with actual JSON.

This is runtime build configuration, not an unmerged application repair.
Future builds must supply this setting at build time; runtime environment alone
does not rewrite a prebuilt Next manifest. Never copy the private .env.platform
or source/DB credentials into the web context.

| Service | Before ID | Final ID | Final started at UTC |
|---|---|---|---|
| cockpit-api | `09c8e0b560d2` | `b6e5ab9270e6` | 2026-10-07T23:21:38.194789866Z |
| pi-api | `415e9089e842` | `2212c52155c3` | 2026-10-07T23:21:38.200929693Z |
| cockpit-web | `1a2c8ebe6b37` | `eead1eadcfbe` | 2026-10-07T23:25:25.245500428Z |

pi-api replaced to serve local aggregate observations; cockpit-api replaced for
condition/status/readiness code; cockpit-web replaced for new panels. Web needed
one additional replacement after build configuration correction. Initial web
container/image and both deploy logs are retained privately. Only these three
services were addressed; all source workers, Maximo API, local projector, legacy
worker, DBs, collector UIs, CEMS and NK are preserved. Existing old images remain
available for service rollback; additive empty Mart schema is not dropped on
rollback. No migrations, initializers or dependency workers are started by up.

Reproduction uses exact source plus private config, not branch HEAD assumptions:

```bash
set -e
SOURCE=/home/john-d/.codex/worktrees/nadi-phase1-runtime-acceptance-001/reliability-knowledge-starter
RUNTIME=/home/john-d/Music/reliability-knowledge-starter
# At initial build, SOURCE HEAD was exactly c2fb0fc and tracked tree clean.
# Supply only the non-secret internal API URL through Next .env.production at
# build time, remove the generated file afterwards, and check routes-manifest.
# Refuse to overwrite an existing operator file.
test ! -e "$SOURCE/reliability-cockpit/web/.env.production"
printf '%s\n' 'COCKPIT_API_BASE=http://cockpit-api:8000' > "$SOURCE/reliability-cockpit/web/.env.production"
docker build --label org.opencontainers.image.revision=c2fb0fc686396e79c19f42af46694673827493a9 \
 -t reliability-cockpit-platform-phase1-cockpit-api:c2fb0fc "$SOURCE/reliability-cockpit"
docker build --label org.opencontainers.image.revision=c2fb0fc686396e79c19f42af46694673827493a9 \
 -t reliability-cockpit-platform-phase1-pi-api:c2fb0fc "$SOURCE/pi-collector"
docker build --label org.opencontainers.image.revision=c2fb0fc686396e79c19f42af46694673827493a9 \
 -t reliability-cockpit-platform-phase1-cockpit-web:c2fb0fc "$SOURCE/reliability-cockpit/web"
rm "$SOURCE/reliability-cockpit/web/.env.production"

# Existing platform network, local writer env; default status is read-only.
# This0600 task-only env was prepared from existing authorized operator config
# for the recorded commands and deleted afterwards; prepare it privately before
# repeating, never put owner credentials in API/evidence exports.
docker run --rm --network reliability-cockpit-platform_platform \
 --env-file "$RUNTIME/secrets/nadi-phase1-runtime-acceptance-001/mart-admin.env" \
 reliability-cockpit-platform-phase1-cockpit-api:c2fb0fc cockpit mart-migrate
# --apply was executed once after validated backup; second apply was no-op.
# mart-reader --apply reconciles existing role grants without replacing password.

# Preserve every accepted override and the exact Compose project identity.
docker compose --project-name reliability-cockpit-platform \
 --project-directory "$RUNTIME" --env-file "$RUNTIME/.env.platform" \
 -f "$RUNTIME/compose.yaml" -f "$RUNTIME/compose.dev.yaml" \
 -f "$RUNTIME/secrets/maximo-wo-recency-002.runtime.yaml" \
 -f "$RUNTIME/secrets/nadi-pi-runtime-001.runtime.yaml" \
 -f "$RUNTIME/secrets/nadi-runtime-002.runtime.yaml" \
 -f "$RUNTIME/secrets/nadi-phase1-runtime-acceptance-001/runtime.yaml" \
 up -d --no-deps --no-build pi-api cockpit-api cockpit-web
```

The new private override pins only three c2fb0fc images. cockpit-api receives
managed config mode, fixed local Collector API bases and the three optional
blank freshness settings. pi-api receives managed mode plus non-secret300s pause
metadata. Both retain their original DB DSNs. No operational worker image/command
is changed to mechanically match newer generic Compose acquisition assumptions.

## RA-08 / RA-09 / RA-10: local observation, API and UI

GET http://localhost:8001/integration-observation:200, **existing PI DB only**.
No PiClient construction/source credentials/trigger/history. Recorded aggregate:

| Field | Value |
|---|---|
| registry_total / registry_active / snapshots | 490 / 433 / 433 |
| last_successful_activity / latest_completed_at | 2026-10-07T23:30:24.257967+00:00 |
| errors | 0 |
| oldest_source_timestamp | 1970-01-01T00:00:00+00:00 |
| unknown / future source timestamps | 0 / 0 |
| bad / unknown quality signals | 18 / 0 |

These are **technical inventory** observations, not approved Asset signals.
Oldest source timestamp does not determine collector freshness. Epoch is explicit;
with blank policy source freshness is UNKNOWN, never manufactured CURRENT.
18 bad-quality technical signals do not mean18 collector request failures.

GET http://localhost:8000/v1/reliability/integration-status:200.
Both governance_schema_ready and condition_schema_ready true. Five components:

| Component | Actual state | Reason |
|---|---|---|
| MAXIMO | AVAILABLE / UNKNOWN freshness | Successful WO activity/cursor present, policy blank |
| PI_COLLECTOR | AVAILABLE / DEGRADED, freshness UNKNOWN | Collection433/433/errors0; technical BAD_QUALITY18 |
| RELIABILITY_MART | AVAILABLE / UNKNOWN freshness | Both factual projections succeeded, policy blank |
| ASSET_AF_MAPPING | AVAILABLE / BLOCKED / UNMAPPED | HUMAN_CROSSWALK_REQUIRED |
| PI_CONDITION_PROJECTION | AVAILABLE schema / BLOCKED | HUMAN_CROSSWALK_REQUIRED, NO_APPROVED_SIGNALS, NO_PROJECTED_EVIDENCE, UNKNOWN_QUALITY |

Coverage:845 registered Assets; verified_mapping_assets0, ambiguous_mapping_assets0,
approved_signal_assets0/approved_signals0, projected_assets0/projected_signals0.
Zero is legitimate because schema/read grants/query succeed; unavailable evidence
would remain UNKNOWN. Source/collection/projection/identity are separate dimensions.

Bounded registered Asset
asset:MAXIMO:MXASSET:BSR:IP:CS10HFC01AJ001-001: integration-status,
condition-evidence, pi-mapping and timeline each200. Mapping remains UNMAPPED;
condition items empty, NO_VERIFIED_MAPPING; no fake health state. No source lookup.
All25 actual `/v1/reliability` OpenAPI paths are GET-only, no public mutation.

UI http://localhost:3000/data-quality: real hydrated Data Trust view shows all
five components,845/0/0/0 coverage, UNKNOWN/BLOCKED/BAD_QUALITY explicitly.
Registered Asset overview renders Condition Evidence and Integration Status.
Visible empty-state states that verified identity and approved signals are
required and equipment condition remains unknown. No crash, mapping mutation or
signal approval control. Nine important web routes200; two data proxy routes200.
A shell200 alone was not used as UI acceptance evidence.

## RA-11 / RA-12: freshness and actual readiness

**FRESHNESS_POLICY_PENDING**. No approved engineering thresholds were found in
the accepted runtime/runbooks/Phase1 policy documents. Historical acquisition
measurements are observations, not SLAs. All three non-secret settings remain
explicitly blank in cockpit-api:
NADI_COLLECTOR_MAX_AGE_SECONDS, NADI_SOURCE_MAX_AGE_SECONDS,
NADI_PROJECTION_MAX_AGE_SECONDS. The private .env.platform was not overwritten.

Known historical PI cycle508s +300s post-cycle pause≈808s start-to-start remains
historical evidence; newer observed cycles vary. Actual worker command still uses
snapshot daemon interval compatibility alias default300 (pause after completion),
minimum1s source spacing and one advisory lease. No fixed five-minute claim,
parallel polling, cadence change or arbitrary freshness number is introduced.

Actual deployed `cockpit phase1-readiness`: originLOCAL_RUNTIME, overallBLOCKED,
normal exit0. `--require-pass`: same honest verdict, **exit2** as expected.

| Gate | Actual verdict | Reason |
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

PASS schema/query compatibility does not replace writer checksum/constraint
attestation; both were independently checked. Missing policy is UNKNOWN; identity
blocks downstream gates before any signals/projection can be claimed accepted.

## RA-13: regression

WO cursor baseline/current 2026-10-07T23:15:10+00:00 / 2026-10-07T23:29:59+00:00;
not reset. Recovery floor 2026-08-21T03:56:54+00:00, exactly one floor audit
run, preserved. Latest incremental finished2026-10-07T23:32:01.518943+00:00,
25 seen /5 upserted /20 skipped /0errors;
skips are unchanged/overlap outcomes, not failures. No bootstrap/recollection.
Both projector states SUCCEEDED; facts/Registry intact. NADI Registry/Decision
Overview200; factual7d765/30d1990/90d4228 (rolling date windows, no risk score).

PI registry490/433 and snapshots433 retained; timeseries133570, original
hypertable2chunks and all PI ledger entries unchanged. PI004quality applied at
2026-10-07T10:49:24.644410Z/checksum
b40f87fe86097bf2e1eda7c63063629903166627b1cca6c182de74c0dd3f1ffe preserved.
Latest worker success2026-10-07T23:30:24.257967+00:00,433/433/errors0; worker container,
command/image/lease/floor unchanged. No PI migration, registry load or history run.
Mart002/003/004 ready; mapping0 and all three condition tables empty.

## RA-14: targeted validation

**80 targeted tests PASS, zero skipped/failures**, plus production build, actual
API/proxy/hydrated UI smoke and product safety. Existing accepted PR20 full-suite
245Cockpit/177PI evidence is retained; no application code changed, so broad
suites were not repeated for ceremony. Disposable PostgreSQL container
nadi-ra-mart-test used tmpfs, networknone, no published port/operational volume;
removed after18 migration/ACL tests. No production DB was used as a test fixture.

Exact commands, with current directory indicated:

```bash
# SOURCE/reliability-cockpit (all hermetic; runtime cases use clean temp Compose)
DATABASE_URL=sqlite+pysqlite:///:memory: NADI_COMPOSE_TESTS=1 \
 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
 -m unittest discover -s tests -p 'test_runtime_wiring.py' -q # 11 PASS
DATABASE_URL=sqlite+pysqlite:///:memory: \
 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
 -m unittest discover -s tests -p 'test_integration*.py' -q # 22 PASS
DATABASE_URL=sqlite+pysqlite:///:memory: \
 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
 -m unittest discover -s tests -p 'test_phase1_readiness.py' -q # 11 PASS

# Disposable PostgreSQL16, source read-only; *_test guard ensures isolation.
docker run --rm --network container:nadi-ra-mart-test \
 -v "$SOURCE:/workspace:ro" -w /workspace/reliability-cockpit \
 -e RELIABILITY_MART_MIGRATIONS_ROOT=/workspace/reliability-cockpit/migrations \
 -e DATABASE_URL=sqlite+pysqlite:///:memory: \
 -e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test \
 nadi-phase1-acceptance-test:local python -m unittest discover \
 -s tests -p test_mart_migrations.py -q # 18 PASS

# SOURCE/pi-collector (no network/operational DB)
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python \
 -m unittest discover -s tests -p 'test_integration_observation.py' -q # 4 PASS
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python \
 -m unittest discover -s tests -p 'test_runtime_wiring.py' -q # 14 PASS

# SOURCE/reliability-cockpit/web
node scripts/product-safety-check.mjs # 18 UI source files PASS
NADI_WEB_BASE_URL=http://127.0.0.1:3000 node scripts/route-smoke.mjs # 9/9 PASS
# Docker web builds execute npm run build: final configured build PASS,13 routes.
# Live browser hydration: Data Trust and registered Asset overview both PASS.
# Live JSON proxy smoke: integration-status and data-trust200.

# Actual operational consumer (SELECT-only; no source calls)
docker exec reliability-cockpit-platform-cockpit-api-1 cockpit phase1-readiness
docker exec reliability-cockpit-platform-cockpit-api-1 cockpit phase1-readiness --require-pass
# exit0 reportBLOCKED / exit2 require-pass, intentionally not productPASS.

# Evidence branch, root: docs-only diff/relative-reference check and git diff --check.
```

Test-only image is not deployed. Source discovery graph metadata predates current
main; material source claims use fresh merged file reads, canonical runtime
queries and actual tests rather than stale graph completeness assumptions.

## RA-15: safety, roadmap and next execution

Task-attributable production PI business GET0 / Maximo business GET0;
PI/Maximo business writes0/0; mapping imports0 / verifies0;
signal approvals0 / condition projections0; history/backfill0;
AF discovery0; registry mutations0; DB reset/truncate0; volume recreation0;
new operational databases0; CEMS/NK changes0; secret/source-value disclosure0.
Existing workers continue normal approved background acquisition. This task's
only operational DDL is canonical additive Mart004 plus reader grants;
three consumer services replaced (web replacement twice), **source restarts0**.
PROPOSED0→0 / VERIFIED0→0; BFPT remains REJECTED / FROZEN / DO NOT VERIFY.

NADI-PI-001 MERGED; NADI-PI-RUNTIME-001 and NADI-RUNTIME-002 ACCEPTED;
PR20 software MERGED, runtime foundation ACCEPTED. NADI-IDN-002 human crosswalk
BLOCKED/EXTERNAL; production governed PI evidence still absent. Phase1 remains
CURRENT/PARTIAL, never COMPLETE. Remaining policy work is independent of human
identity; approved signals, canary, time/quality review and real bounded evidence
are subsequent product prerequisites. Technical BAD_QUALITY18 is visible and
requires signal-specific review if any affected signal is later selected.

**Runtime is READY for NADI-IDN-002B once controlled human MATCH evidence is
available.** Do not perform a canary now: first controlled PROPOSED dry-run/import,
attributable human verification and unique target resolution; then separately
authorized bounded governed PI canary. Afterwards approve signal semantics/units,
establish engineering freshness/quality policy, perform bounded real handoff/
projection and require all actual Phase1 gatesPASS. No gate is weakened.
