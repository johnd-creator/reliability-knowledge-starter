# GOV03 — laptop/server migration readiness handoff

**INVENTORY READY; MIGRATION NOT EXECUTED OR AUTHORIZED.** This source-free inventory
was recorded `2026-10-08T21:48:59.583922+07:00`. Target server, access, maintenance window and
source connectivity are NOT established. Temporary thresholds are not prerequisites
for DB migration and expire on 13 October regardless of cutover progress.

## Runtime baseline

Compose project `reliability-cockpit-platform`; original control checkout
`/home/john-d/Music/reliability-knowledge-starter` at `0c800dac1da6ef863afdb193021176fe7feac073` with `23496711.xls` preserved.
Release `/home/john-d/.codex/worktrees/nadi-pi-diagnostics-release/reliability-knowledge-starter` at `1cf7fed971594581913e8e7f635691f834133b6e`; reviewed main `1f7c25a711e68afc87ee0c4b1322bfca4be6ba97`, application source identical.
Private full container IDs/start times/mounts/dependency graph are in ignored
`secrets/nadi-p1-fresh-gov-03/migration-inventory.json`. Published identities below
contain no credentials. Pin immutable image IDs/digests during future review, not
mutable tag names alone; arrange image export/registry access under that task.

Accepted Compose file order:

1. `compose.yaml`
2. `compose.dev.yaml`
3. `secrets/maximo-wo-recency-002.runtime.yaml`
4. `secrets/nadi-pi-runtime-001.runtime.yaml`
5. `secrets/nadi-runtime-002.runtime.yaml`
6. `secrets/nadi-phase1-runtime-acceptance-001/runtime.yaml`
7. `secrets/nadi-idn-002b-r1/runtime-478cce1.yaml`
8. `secrets/nadi-p1-freshness-001c/runtime-a07d683.yaml`
9. `secrets/nadi-p1-freshness-001d-diag-02/runtime-1cf7fed.yaml`
10. `secrets/nadi-p1-fresh-gov-03/runtime-policy.yaml`

Existing overrides use laptop absolute paths. Future deployment must reconstruct
them explicitly, preserving service semantics and project/network/volume ownership;
do not blindly copy absolute paths or replace private config with examples.

## Container roles and immutable image IDs

| Service | State | Image tag | Image ID |
|---|---|---|---|
| cems-aggregator | running | `reliability-cockpit-platform-cems-aggregator` | `sha256:33d4e24007d55087469cf07f334ce81f2fdba23c480802e5c5ee5ddd72f7999f` |
| cems-api | running | `reliability-cockpit-platform-cems-api` | `sha256:47523526df4bf1ec376cb38f33c6848eb72155ab9c5b40188f66b610f18b764d` |
| cems-db | running | `postgres:16.4-alpine` | `sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c` |
| cems-init | exited | `reliability-cockpit-platform-cems-init` | `sha256:4d8aa1c13ebe803cae3c78cbabf39aca053524d3d06c0f2be8edb9be373790f5` |
| cems-web | running | `reliability-cockpit-platform-cems-web` | `sha256:f58aefe9a7281d4045e9fd7ab72e7d02502d27cbaa347d6440ac521395a4ae13` |
| cems-worker | running | `reliability-cockpit-platform-cems-worker` | `sha256:d52cf0b38cd3980f835bcfaf82f4a7c577dd1d429a1109079a39c534fd5dd4be` |
| cockpit-api | running | `reliability-cockpit-platform-diagnostics-cockpit-api:1cf7fed` | `sha256:ffb4da000b3372456bfd27adb38eb3ec335404d51f775439252338bafa4851e7` |
| cockpit-db | running | `postgres:16.4-alpine` | `sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c` |
| cockpit-init | exited | `reliability-cockpit-platform-cockpit-init` | `sha256:c32320b1b152687d90efe2a6de6d8ce53b60d2ef0d013d8e5dd3a07c1f5524c8` |
| cockpit-web | running | `reliability-cockpit-platform-phase1-cockpit-web:c2fb0fc` | `sha256:47a90f28db112f63dd6549b2536cf1089543047a26b2ca24c5befd14595254e1` |
| cockpit-worker | running | `reliability-cockpit-platform-cockpit-worker` | `sha256:c5fb2b2be3f2cf714a13f4c9bf032ecc0f033701534ac0fa1376c1e6a849f148` |
| mart-projector | running | `reliability-cockpit-platform-maximo-reviewed:2eacce47` | `sha256:670991160ecbd82d55d590ca0be90199ff957b8f9de7ab785b1af541e93a7753` |
| maximo-api | running | `reliability-cockpit-platform-maximo-reviewed:2eacce47` | `sha256:670991160ecbd82d55d590ca0be90199ff957b8f9de7ab785b1af541e93a7753` |
| maximo-db | running | `postgres:16.4-alpine` | `sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c` |
| maximo-init | exited | `reliability-cockpit-platform-maximo-init` | `sha256:6eb415e3fbd79408704ed8aac34fe893574d557a4c72140956a24c574fda56e4` |
| maximo-web | running | `reliability-cockpit-platform-maximo-web` | `sha256:18501e9ca0172d0650407597f4b1355e47eaf979e6da332b03f52b85e8dcc87f` |
| maximo-worker | running | `reliability-cockpit-platform-maximo-reviewed:2eacce47` | `sha256:670991160ecbd82d55d590ca0be90199ff957b8f9de7ab785b1af541e93a7753` |
| pi-api | running | `reliability-cockpit-platform-phase1-pi-api:c2fb0fc` | `sha256:04f86777d82030346218c009405d2b5f370c2293518f89229b8ca7cff6f7a7d7` |
| pi-db | running | `timescale/timescaledb:2.16.1-pg16` | `sha256:3adf01543c37b5b88d3c4998338e0f7f21cb3cdd02bbddea08b09bf60e2289b7` |
| pi-init | exited | `reliability-cockpit-platform-pi-init` | `sha256:d6162447a885cc6e5c8f5ff036b0bdfe4dd8c71e6dfccb52543dc079c2458600` |
| pi-registry | exited | `reliability-cockpit-platform-pi-registry` | `sha256:85195b64240aa5c261842a3341c6925954b02fdfb19c41206ff4aac2d70c1730` |
| pi-web | running | `reliability-cockpit-platform-pi-web` | `sha256:970f38e203d7b5b5bb12c9ccbddcefab60402245e9f1dacb67db44b275eca884` |
| pi-worker | running | `reliability-cockpit-platform-pi-reviewed:3e981a3` | `sha256:71d00590f0e806f62fbcaa9d376f448363fd2783a15150c92666572fb4f2e56c` |

Workers acquire only their approved source scope. API/web services read local data;
`mart-projector` writes existing owning Maximo/Mart DB. Init/migrate/ready one-shots
are not permission to rerun initialization or DDL on restored data. Preserve accepted
dependency ordering and recovery overrides. CEMS/NK relocation is separate scope.

## Persistence and database boundaries

| Owning service | Type | Volume or bind source | Container destination |
|---|---|---|---|
| cems-db | volume | `reliability-cockpit-platform_cems-db` | `/var/lib/postgresql/data` |
| cockpit-db | volume | `reliability-cockpit-platform_cockpit-db` | `/var/lib/postgresql/data` |
| mart-projector | bind | `/home/john-d/Music/reliability-knowledge-starter/reliability-data-contracts` | `/contracts` |
| maximo-db | volume | `reliability-cockpit-platform_maximo-db` | `/var/lib/postgresql/data` |
| pi-db | volume | `reliability-cockpit-platform_pi-db` | `/var/lib/postgresql/data` |
| pi-registry | bind | `/home/john-d/Music/reliability-knowledge-starter/pi-knowledge/mappings/bsr1-parameters.yaml` | `/registry/bsr1-parameters.yaml` |
| pi-worker | bind | `/home/john-d/Music/reliability-knowledge-starter/pi-knowledge/mappings/bsr1-parameters.yaml` | `/registry/bsr1-parameters.yaml` |
| pi-worker | bind | `/home/john-d/Music/reliability-knowledge-starter/secrets/nadi-pi-runtime-001/migrations.py` | `/app/src/services/migrations.py` |
| pi-worker | bind | `/home/john-d/Music/reliability-knowledge-starter/secrets/nadi-pi-runtime-001/runtime_worker.py` | `/app/src/services/runtime_worker.py` |

Existing Reliability Mart belongs to `maximo-db` / `maximo_collector`; Maximo rows,
registry, WO cursor/recovery-floor, Mart projectors, governance and condition evidence
remain there. Legacy Cockpit DB `cockpit` is separate; canonical reads use explicit
`RELIABILITY_MART_DATABASE_URL` as `nadi_mart_reader`, never `DATABASE_URL` fallback.
PI owns `pi_collector` in existing TimescaleDB; preserve hypertable/history/quality
migration004 and registry. Additional platform DB/storage roles listed above must
be included only in explicitly approved cutover scope; no new operational database.

Existing Mart ledger (read-only inventory, no apply):

| Migration | Checksum | Applied |
|---|---|---|
| `002_asset_af_mapping.sql` | `e2f2464031c0c710f1471863c5f55493165b95421bbe6bea711d19827af8bb6a` | 2026-10-07T13:09:12.413316+00:00 |
| `003_asset_af_mapping_provenance.sql` | `4cf35acd7979babe71069c05c5548a92252b17f5e1933f690f545a58fefa7d31` | 2026-10-07T13:09:12.414779+00:00 |
| `004_condition_evidence.sql` | `000dce2def0acb4f6e0fac33636ab9db946841fa72af3785f3300745867a7667` | 2026-10-07T23:20:33.704255+00:00 |

Future backup must include complete owning Maximo/Mart DB, legacy Cockpit if in
scope, PI TimescaleDB and roles/grants, plus separately scoped other persistent
services. Use private full dumps with catalog/checksum validation, recorded versions
and consistency window; prove restore on isolated fixtures before cutover.
GOV03 backs up private config only, not a new full database dump or restore drill.
Never reset volume, cursor, floor or migration ledger. Accepted R3 evidence,
mapping/selection/state fingerprints and timestamps must match after restore.
Factual populations may change only through normal approved background acquisition;
freeze/checkpoint the cutover snapshot deliberately.

## Private configuration and environment names

`.env.platform` is the managed NADI/API and operator-launcher authority, 0600/UID1000.
Working technical PI worker still has its accepted legacy collector configuration;
do not migrate its authority incidentally. Preserve the reconciled effective PI
auth material privately; a file does not prove a running container has identical
values. Compare only booleans inside a trusted local boundary, never password hashes.
Private launcher/operator writer credential files and journals must move only under
separately authorized secure channels with restricted ownership/permissions.
NADI reader, controlled writer, legacy DB and source credentials remain separated.
No credential values, URL secrets, backups or full environment payloads go into Git.

Current effective variable NAMES by service (values intentionally omitted):

### cems-aggregator

`DATABASE_URL`

### cems-api

`DATABASE_URL`

### cems-db

`POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER`

### cems-init

`DATABASE_URL`

### cems-web

`CEMS_COLLECTOR_API_BASE`

### cems-worker

`CEMS_MODBUS_HOST`, `CEMS_MODBUS_PORT`, `DATABASE_URL`

### cockpit-api

`COCKPIT_CONFIG_MODE`, `DATABASE_URL`, `MAXIMO_COLLECTOR_API_BASE`, `NADI_COLLECTOR_MAX_AGE_SECONDS`, `NADI_CONDITION_PROJECTION_MAX_AGE_SECONDS`, `NADI_CONDITION_SOURCE_MAX_AGE_SECONDS`, `NADI_MART_FACTUAL_PROJECTION_MAX_AGE_SECONDS`, `NADI_MAXIMO_WO_MAX_AGE_SECONDS`, `NADI_PI_COLLECTOR_MAX_AGE_SECONDS`, `NADI_PROJECTION_MAX_AGE_SECONDS`, `NADI_SOURCE_MAX_AGE_SECONDS`, `PI_COLLECTOR_API_BASE`, `RELIABILITY_MART_DATABASE_URL`

### cockpit-db

`POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER`

### cockpit-init

`DATABASE_URL`

### cockpit-web

`COCKPIT_API_BASE`

### cockpit-worker

`CEMS_COLLECTOR_API_BASE`, `DATABASE_URL`, `MAXIMO_COLLECTOR_API_BASE`, `PI_COLLECTOR_API_BASE`

### mart-projector

`DATABASE_URL`, `MART_PROJECTION_INTERVAL_SECONDS`, `RELIABILITY_CONTRACTS_ROOT`

### maximo-api

`DATABASE_URL`

### maximo-db

`POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER`

### maximo-init

`DATABASE_URL`

### maximo-web

`MAXIMO_COLLECTOR_API_BASE`

### maximo-worker

`DATABASE_URL`, `MAXIMO_AUTH_MODE`, `MAXIMO_BASE_URL`, `MAXIMO_PASSWORD`, `MAXIMO_READ_ONLY_TOKEN`, `MAXIMO_SESSION_COOKIE`, `MAXIMO_USERNAME`

### pi-api

`DATABASE_URL`, `PI_CONFIG_MODE`, `PI_SNAPSHOT_INTERVAL_SECONDS`

### pi-db

`POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER`

### pi-init

`DATABASE_URL`

### pi-registry

`DATABASE_URL`

### pi-web

`COLLECTOR_API_BASE`


## Network and source connectivity

Current Docker networks: `135990f91ccb reliability-cockpit-platform_platform`.
Current volumes: `reliability-cockpit-platform_cems-db`, `reliability-cockpit-platform_cockpit-db`, `reliability-cockpit-platform_maximo-db`, `reliability-cockpit-platform_pi-db`.
Future internal DNS must preserve service-addressed DB/collector API connectivity;
published local 8000/8001/3000 routes must resolve consistently with UI proxy config.
Target-server source routes, firewall allowlists, DNS, TLS/CA trust, proxies and
account authorization for PI metadata versus technical streams need independent
review. Validate private endpoint identity against approved config without exposing
its value. No source connection test occurred in this task.

Future authorized task should first validate local restore/roles/ledger/API/UI and
source-free launcher receipt/budget contracts, then obtain explicit bounded PI/
Maximo connectivity authority. Do not reuse consumed R3 authorization, discover AF,
run history or recollect Maximo WO bootstrap. Preserve PI 1-second request floor,
single managed worker lease and post-cycle pause semantics. Ensure only one
acquisition environment is active during cutover; avoid duplicate worker ownership.

## Cutover and recovery prerequisites

1. Named target server/operator/window and separately approved deployment plan.
2. Private backup/catalog/version evidence and isolated restore acceptance.
3. Source-free credential isolation, SELECT-only reader and canonical DSN checks.
4. R3 exact payload/timestamps, VERIFIED=1/PROPOSED=0, approved/latest/state1/1,
   registry 433, cursor/floor and factual projector validation.
5. Explicit bounded connectivity authorization and acquisition ownership transition.
6. Fixed private journal/launcher paths and reviewed executable checksums; never
   reset failed-attempt receipts or silently resume consumed authorizations.
7. Re-run actual nine readiness gates; condition UNKNOWN remains honest while unset.
8. Preserve laptop environment as rollback until server acceptance, and define
   whether fallback may keep laptop online during travel. If unavailable, document
   planned outage rather than leave parallel collectors or pretend CURRENT.

If server is not ready, keep this accepted runtime intact subject to owner-approved
availability, or arrange a separately approved stop/recovery window. GOV03 does not
authorize shutdown. Fauzi must still restore only temporary policy keys before
13 October 00:00 WIB without approved extension; migration cannot defer expiry.
Review/checkpoint details are in [activation evidence](nadi-p1-fresh-gov-03.md).
