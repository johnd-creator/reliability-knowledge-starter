# NADI-P1-FRESH-GOV-03 — controlled freshness activation

## Accepted scope

**PASS — three temporary activity-monitoring policies activated.** Phase 1 remains
**CURRENT/PARTIAL**, product readiness **UNKNOWN**. No condition freshness policy,
source acquisition, evidence projection, mapping or signal approval was performed.
This is a measured operational checkpoint, not a claim that future reviews passed.

Fauzi explicitly authorized activation as project owner and accountable internal
technical approver. Separate external Maximo/PI owner endorsements are not required
for this internal monitoring-only scope and are not claimed. The original 8 October
approval remains DATE_ONLY with timestamp NULL. No signed document is claimed.

[Current activation register](nadi-p1-fresh-gov-03-activation-register.json) supplements
the unchanged [historical GOV02 register](nadi-p1-fresh-gov-02-approval-register.json).
The owner's explicit earlier expiry replaces its unresolved 15 October reference:
**2026-10-13T00:00:00+07:00**, Asia/Jakarta. This is not seven days after activation.

## Exact release and deployment

Latest reviewed main: `1f7c25a711e68afc87ee0c4b1322bfca4be6ba97`; PR27 MERGED. Operational release and serving API
image revision: `1cf7fed971594581913e8e7f635691f834133b6e`. Diff verification of `reliability-cockpit/src`, Dockerfile,
pyproject and managed/external Compose proves application source is identical
between these commits. Installed Python source checksums match the reviewed release.
New documentation on this task branch is not deployed application code.

The original control checkout remains `/home/john-d/Music/reliability-knowledge-starter`, SHA
`0c800dac1da6ef863afdb193021176fe7feac073`; untracked `23496711.xls` preserved.
Clean release checkout: `/home/john-d/.codex/worktrees/nadi-pi-diagnostics-release/reliability-knowledge-starter`. Audit branch: `codex/nadi-p1-fresh-gov-03`.
Private configuration authority remains `.env.platform`, UID 1000,
mode 0600. Backup `secrets/nadi-p1-fresh-gov-03/env.platform.before` is private
0600 inside a 0700 directory. Backup bytes and credentials are not in Git; no
credential fingerprints were produced. Other settings, including reconciled PI
authentication, remain byte-for-byte intact.

All eight policy keys were absent from the file and effectively blank in API.
Only three approved keys were appended. Existing 001C override pins all eight
values blank, so a minimal private `runtime-policy.yaml` was appended to the
accepted nine-file Compose chain, substituting only these three API keys from
`.env.platform`. All old override bytes remain preserved. Effective Compose
comparison allows exactly three API environment differences, with other services
identical. No image rebuild or dependency replacement was needed.

Only `cockpit-api` was replaced using the existing image
`reliability-cockpit-platform-diagnostics-cockpit-api:1cf7fed` (ID `sha256:ffb4da000b3372456bfd27adb38eb3ec335404d51f775439252338bafa4851e7`).
Old container `97500740f1f79df4fb534aaf5152276d0e55340e9572024b26a71baa87a95d41` → new `8145de57e40fd6686fe37d46457e77e38add650d1aca9cef89acfd01af6dcfa2`,
started `2026-10-08T14:45:24.831531327Z`. All other 22 container IDs, image IDs,
start times, restart counts, mounts, networks and statuses are unchanged.
Command scope: `docker compose` with recorded project/env/files,
`up -d --no-deps --no-build cockpit-api`. No technical worker was restarted.

Effective accepted Compose files, in order:

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

## Effective policy and interpretation

| Setting | Seconds / state |
|---|---|
| NADI_MAXIMO_WO_MAX_AGE_SECONDS | 660 |
| NADI_MART_FACTUAL_PROJECTION_MAX_AGE_SECONDS | 660 |
| NADI_PI_COLLECTOR_MAX_AGE_SECONDS | 1800 |
| NADI_COLLECTOR_MAX_AGE_SECONDS | UNSET |
| NADI_SOURCE_MAX_AGE_SECONDS | UNSET |
| NADI_PROJECTION_MAX_AGE_SECONDS | UNSET |
| NADI_CONDITION_SOURCE_MAX_AGE_SECONDS | UNSET |
| NADI_CONDITION_PROJECTION_MAX_AGE_SECONDS | UNSET |

Runtime parser proves exclusive component mode, rejects mixed legacy/component
configuration, and leaves missing/future timestamps UNKNOWN. MAXIMO uses only
successful WO collector activity; it does not imply source-record freshness.
MART_FACTUAL requires both `asset_master` and `maintenance_event` successful
projectors. Their recorded successes at acceptance were
`2026-10-08T14:43:33.519283Z` and `2026-10-08T14:43:33.669579Z`.
PI_COLLECTOR uses full successful snapshot cycles, not oldest source timestamp.
Condition source/projection remain UNKNOWN with thresholds NULL. No timestamp
was updated to manufacture freshness. These thresholds are provisional monitoring,
not long-term SLAs, equipment health limits, or condition acquisition cadence.

## Preservation and local acceptance

Exact R3 mapping/selection fingerprints plus complete latest evidence/state JSON
match before/after and the accepted R3 snapshot. Coal Flow A remains NUMERIC,
54.84218978881836 `Ton/h`, source `2026-10-08T13:17:39.051010Z`, collected
`2026-10-08T13:17:40.212333Z`, projected `2026-10-08T13:17:40.313906Z`.
Good=true, Questionable/Substituted/Annotated=false; source WebId still 203 characters.
VERIFIED=1 / PROPOSED=0; approved signal/latest evidence/projection state=1/1/1.
No replay, new measurement or artificial projection timestamp occurred.

Registry 490 total / 433 active, snapshots 433, latest full cycle successful with
zero errors at `2026-10-08T14:38:27.535663+00:00`. 18 technical bad-quality signals
and oldest source timestamp at Unix epoch remain visible. UI correctly shows
PI collection CURRENT and aggregate PI quality DEGRADED/BAD simultaneously.
Good describes evidence quality, not equipment HEALTHY.

845 registered assets; factual asset context 11845 / maintenance
69645 at the checkpoint. Background approved collection continues;
WO cursor may advance normally. Recovery floor remains
`2026-08-21T03:56:54Z`, exactly one floor record, latest incremental cycle errors=0.
Both projector success states are preserved. Mart canonical ledger still contains
002/003/004; no DDL was run. Reader has SELECT and no relation ownership, write
privileges, schema/database CREATE, superuser, role/DB creation, replication or
RLS bypass. API receives no PI/Maximo source credentials or administrative Mart DSN.
34 historical journal/receipt artifacts retain bytes and modification timestamps.
PI_AF_KKS_LOOKUP_UNRESOLVED remains open; BFPT stays REJECTED/FROZEN/DO NOT VERIFY.

Six local API routes return HTTP200: health, factual overview, platform integration
status, asset detail, asset condition evidence, asset integration status.
Web `/`, `/data-quality`, and exact Coal Feeder A asset route return HTTP200.
Browser verification confirms condition value/quality/timestamps, activity CURRENT,
technical bad quality/epoch evidence and condition UNKNOWN. An initial smoke request
to guessed `/data-trust` returned404; the actual Data Trust route is `/data-quality`.
No application defect or web replacement was needed.

## Initial post-activation nine-gate readiness

Observed `2026-10-08T14:46:10.787545Z`. `cockpit phase1-readiness --require-pass` exits2,
overall **UNKNOWN**. This remains a bounded one-asset pilot, not fleet-wide coverage.

| Gate | Verdict | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT |
| P1-MART-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT |
| P1-PI-COLLECTOR-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-IDENTITY-MAPPING-READY | PASS | VERIFIED_PILOT_AVAILABLE |
| P1-SIGNAL-SELECTION-READY | PASS | APPROVED_PILOT_SIGNALS_AVAILABLE |
| P1-CONDITION-PROJECTION-READY | UNKNOWN | UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID |

## Final background-cycle observation

At `2026-10-08T14:54:51.142814Z`, final readiness is **7 PASS / 1 PARTIAL /
1 UNKNOWN**, overall UNKNOWN (require-pass exit2). The unmodified technical worker
completed a normal cycle that began at `2026-10-08T14:43:27.549193Z` before policy
activation and ended at `2026-10-08T14:52:23.943397Z`: 433 seen / 432 collected,
1 error, not aborted. The previous full 433/433 success remains
`2026-10-08T14:38:27.535663Z`; partial completion does not reset that success time.
PI collector gate now reports PARTIAL / LOCAL_EVIDENCE_DEGRADED even while the last
full success is inside 1800 seconds. Registry/snapshots433, accepted R3 evidence,
reader boundary and other 22 containers remain preserved. The cause of the single
background error was not investigated or inferred; no retry/probe/restart occurred.
This is a real monitoring observation, not a task-attributable acquisition or mutation.

| Gate | Final verdict | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT |
| P1-MART-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT |
| P1-PI-COLLECTOR-CURRENT | PARTIAL | LOCAL_EVIDENCE_DEGRADED |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-IDENTITY-MAPPING-READY | PASS | VERIFIED_PILOT_AVAILABLE |
| P1-SIGNAL-SELECTION-READY | PASS | APPROVED_PILOT_SIGNALS_AVAILABLE |
| P1-CONDITION-PROJECTION-READY | UNKNOWN | UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID |

## Manual review and expiry

- Actual activation: **2026-10-08T21:45:26.619585+07:00**.
- 24-hour review: **2026-10-09T21:45:26.619585+07:00**.
- 72-hour review: **2026-10-11T21:45:26.619585+07:00**.
- Fauzi-confirmed pre-expiry checkpoint: **2026-10-12T20:00:00+07:00**.
- Hard expiry: **2026-10-13T00:00:00+07:00**.
- Accountable rollback operator: **Fauzi**.

Each future review remains PENDING. Fauzi inspects only local collector runs,
cursor/floor, both factual projector states, integration observations/readiness,
missing/future times, incomplete/error cycles, stale intervals and false alerts.
Record review time, local evidence window, degraded reasons and decision separately;
never probe source systems for this monitoring review. Separate source quality
from collection activity and condition freshness from technical collector cadence.

No expiry timer, cron, reminder or automatic rollback exists. Fauzi directly
confirmed checkpoint execution and rollback before expiry if no extension.
Do not treat this documentation as enforcement. Explicit owner approval before
expiry is necessary to extend; travel/server plans do not extend the deadline.

Private persistent helper: `/home/john-d/Music/reliability-knowledge-starter/secrets/nadi-p1-fresh-gov-03/rollback.py`; common helper adjacent.
Use the pinned release interpreter, first dry-run (no arguments), then explicit
`--execute` at the accountable operator checkpoint. It restores only the three
policy keys (removes them because originally absent), preserves unrelated current
config, verifies the same accepted API image, reloads only API and checks unchanged
then-current pilot evidence and all other containers. Stop and reconcile if release
or condition/legacy authorization changed since activation. Never restore the whole
old env file over unrelated later changes. Config backup exists for inspection only.

After rollback, require all eight effective API values blank, collection/projection
policy states UNKNOWN, reader SELECT-only, accepted evidence unchanged and no
source request. Save the actual rollback timestamp and readiness. For API failure,
retain the same image and accepted override chain; do not restart workers or DBs.
The helper was successfully dry-run from its persistent private location; live
expiry rollback has not been executed yet.

## Additional source-free governance validation

From `reliability-cockpit`, reviewed release interpreter and `PYTHONPATH=.`:
`python docs/validation/nadi-p1-fresh-gov-01-simulation.py` — 14 cases PASS;
`python docs/validation/nadi-p1-fresh-gov-02-validation.py` — historical register
and all five component records PASS. These describe frozen GOV01/GOV02 checkpoints,
not current activation. GOV03 register checks confirm preserved date-only approval,
24h/72h arithmetic, checkpoint-before-expiry, three active/five UNSET fields,
manual enforcement and no external endorsement claims. An initial invocation from
repo root with system Python failed import resolution; the commands above passed
with correct project directory/interpreter. No implementation change was required.
`git diff --check` passes.

## Tests and safety

From `reliability-cockpit`, exact reviewed release interpreter:

```sh
PYTHONPATH=tests:/tmp/nadi-phase1-host-testdeps DATABASE_URL=sqlite+pysqlite:///:memory: COCKPIT_CONFIG_MODE=managed /home/john-d/.codex/worktrees/nadi-pi-diagnostics-release/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest test_component_freshness test_freshness_governance test_phase1_readiness test_integration_status
```

54 discovered: **45 PASS, 9 optional PostgreSQL fixture tests skipped**. No disposable
PG fixture was configured; operational read-only privilege/ledger checks passed.
API parser checks passed (approved values, exclusive mode, missing/future safety).
Private preflight Compose diff and rollback byte-roundtrip passed. Full application
build/suites were not repeated because no application changes were made.

Task-attributable upstream PI/Maximo/CEMS GET=0; source writes=0; acquisition/replay=0;
mapping/signal/evidence/state mutations=0; DDL/reset/backfill/registry/credential
rotation=0; new DB/volume recreation/scheduler=0; technical worker restarts=0;
CEMS/NK changes=0; server migration/cutover=0. Authorized operations: three non-secret
private monitoring setting additions, one API-only wiring override, one same-image
API replacement. Existing approved background acquisition is separate.

## Handoff

[Pre-migration inventory](nadi-pre-migration-readiness-gov-03.md) is prepared;
future-server address/access, backup/restore drill and cutover remain unapproved
and unexecuted. Policy activation is not a database-migration prerequisite.
Next: Fauzi's 24h/72h reviews and 12 October checkpoint; separately authorize the
server deployment/cutover and condition freshness engineering work. Phase 1 is not
COMPLETE. Remaining operational risk is manual expiry enforcement during travel.
