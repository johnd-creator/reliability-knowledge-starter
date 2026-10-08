# NADI-P1-FRESH-001B — component policies and manual refresh

Candidate software only. No runtime deployment, policy activation, source GET or
production refresh is authorized by this implementation task. Phase 1 remains
CURRENT/PARTIAL; actual runtime readiness remains UNKNOWN with blank policies.

## Baseline and preserved operational state

PR #23 merged at `685a721`; PR #24 merged at `4b6ae7d`. Implementation base:
`4b6ae7d353d12c04a73b3178bf559a7f536f0508` on
`codex/nadi-p1-freshness-implementation`. The reviewed runtime continues to serve
478cce1; this candidate is not deployed. Control checkout remains `0c800dac`.
Existing `.env.platform`, seven accepted Compose files/image pins, databases,
volumes, source workers and SELECT-only reader remain unchanged.

Local preflight verifies 845 registered assets, exactly 1 VERIFIED Coal Feeder A
mapping, 1 approved Coal Flow signal, 1 latest condition row and 1 projection state.
The accepted source Attribute reference is 203 characters, canonical bound 512;
technical PI registry remains 433 active. No new mapping or signal is created.
The accepted `Ton/h` unit, timestamps, quality and null handoff collector success
are preserved. Hidayat's equipment identity review and Fauzi's signal approval
are not freshness/SLA approvals. PI_AF_KKS_LOOKUP_UNRESOLVED stays open and BFPT
remains REJECTED/FROZEN/DO NOT VERIFY.

## Five independent configuration dimensions

| Environment value | Only affects | Proposal, not activated |
|---|---|---|
| `NADI_MAXIMO_WO_MAX_AGE_SECONDS` | Maximo WO successful acquisition age |660 seconds|
| `NADI_MART_FACTUAL_PROJECTION_MAX_AGE_SECONDS` | Both factual Mart projection success ages |660 seconds|
| `NADI_PI_COLLECTOR_MAX_AGE_SECONDS` | Technical PI complete-success age, plus nullable handoff collector dimension |1800 seconds|
| `NADI_CONDITION_SOURCE_MAX_AGE_SECONDS` | Approved condition source measurement age |UNSET / POLICY_EVIDENCE_INSUFFICIENT|
| `NADI_CONDITION_PROJECTION_MAX_AGE_SECONDS` | Accepted condition projection age |UNSET / POLICY_EVIDENCE_INSUFFICIENT|

Every default is blank/UNKNOWN. 660/660/1800 remain **PROPOSED — NOT YET APPROVED**,
operational monitoring windows rather than contractual SLAs. No numbers are
installed as code defaults or set in production. Setting only the first three
cannot make condition source or projection CURRENT. Component source policy does
not classify all 433 technical signals or promote them to governed signals.

Legacy explicit configurations keep their previous behavior when **all five new
values are unset**: `NADI_COLLECTOR_MAX_AGE_SECONDS`,
`NADI_SOURCE_MAX_AGE_SECONDS`, `NADI_PROJECTION_MAX_AGE_SECONDS`.
Any nonblank legacy value plus any nonblank component value is rejected, even if
numerically equal. There is no mixed-mode inference, precedence or cross-component
fallback. To move to component mode, clear all three legacy values deliberately.
Blank is empty string; whitespace/invalid/nonpositive/nonfinite/boolean values
are rejected. A configured threshold never overrides missing/future time, errors,
quality, coverage, mapping readiness or a failed schema query.

Managed and external Compose explicitly pass all eight optional values only to
`cockpit-api`, never init/projector/worker/migration services. API receives no PI
or Maximo source credentials or Mart owner DSN. No public refresh, arbitrary-plan,
attribute proxy or mapping mutation endpoint exists. The same policy selection
feeds asset condition reads, integration-status and Phase 1 gates.

## Time integrity and quality

Source time is measurement time; collected_at belongs to that evidence acquisition.
Collector completion is a separate optional source contract: null remains null,
and recent collection or global worker success cannot fill it. projected_at is
newly accepted evidence projection time; attempt state is not last success.
The canonical attempted_at column retains its existing semantics (evidence
collected_at, or writer clock for all-failure batches); it is not renamed into an
actual runner-start timestamp. Actual runner activity has its own journal clock.

Refresh validates aware timestamps and source ≤ collection ≤ acceptance clock.
Future explicit collector success is rejected. Unix epoch/nonpositive source time
is rejected as an invalid current-pilot timestamp. No clock-skew tolerance or
source freshness threshold is invented. Quality/NULL remain typed in the private
handoff; they cannot imply machine HEALTHY. This manual **acceptance runner**
rejects bad/unknown quality and null values before writing latest evidence. Generic
canonical projection retains its existing typed bad/null support; only this
bounded acceptance workflow adds the stricter gate. Rejected reads remain in
private handoff for audit, while prior accepted rows/times stay unchanged.
Missing collector completion does not substitute an invented time or automatically
block a schema-valid observation; its query dimension remains COLLECTOR_UNKNOWN.
Absent source policy leaves source UNKNOWN; accepted evidence is not Phase 1 PASS.
An approved source policy marking an incoming observation stale blocks acceptance.

## Manual coordinator and source boundary

New internal CLI: `cockpit condition refresh`. Default is dry-run; it exports the
canonical current plan and records a private dry-run without source requests or
Mart DML. There is no retry, cron, timer or scheduler. The only allowed target is
`asset:MAXIMO:MXASSET:BSR:IP:CS10HFB01AF001-001`, exactly one `coal_flow` signal.

A frozen accepted private handoff plus explicit SHA256 pins **all** mapping,
AF lineage, Attribute identity, selection and human approval fields. Canonical
plan re-resolution must equal that whole plan, not just its label. It must be
VERIFIED/CENTRAL_PI/PRIMARY_EQUIPMENT and exactly one approved signal. Writer
locks and revalidates current governance again after acquisition. Retired,
conflicting or changed approval is rejected; no new approval/identity is written.

One fixed private host lock under `~/.local/state/nadi-coal-flow-refresh/` is
shared even when journal directories differ. An existing-Mart PostgreSQL advisory
lease, keyed by canonical asset, serializes concurrent coordinators across DB
connections. Neither lock creates a new relation. The source process inherits
host lock FD; a terminated coordinator does not release it while that local
source process still runs. Launcher must **exec locally**, never daemonize, invoke
Docker/remote job dispatch or run on another host. The first live acceptance must
use one accountable operator account/host and prove contention before source GET.
A multi-host/orphan-resistant recurring scheduler is outside scope; do not infer
approval from the presence of the advisory lease.

The coordinator invokes a checksum-pinned, owner-controlled executable launcher
with a fixed Collector command, no shell interpolation and sanitized environment.
It never creates PiClient or reads PI source credentials. Admin DSNs, ambient
source secrets, proxies, PYTHONPATH and .netrc context are not forwarded. Launcher
hash is checked again immediately before execution. It must live in an operator-
controlled directory, be executable by the owner and not writable by group/others.
The Collector process alone reads explicit private source keys from `.env.platform`
via `--source-env-file`, rejecting duplicate keys and interpolation ambiguity.
It exports only PI URL/auth/timeout/rate/size/TLS values, not DB/admin or NADI
configuration. Managed mode prevents per-project/home dotenv fallback. File must
be owner-private, regular and bounded; no secret values are printed or journaled.

`picollector condition-evidence --max-source-gets 5 --report-file ...` adds a hard
per-invocation counter before each underlying PiClient call. Only governed
snapshot/lineage GET shapes are admitted; history, writes and a sixth request are
rejected before transport. Existing ≥1-second request floor, response cap,
origin/relationship checks and bounded direct attributes remain in force. No
automated retry or parallel request is added. Failed attempts count against the
budget. Receipt is separate from the canonical handoff and includes only count,
cap, contract version and handoff hash; both output files are exclusive 0600.
Coordinator validates canonical EvidenceBatch and receipt hash/count before
projection. Source exceptions/process output are never echoed or placed in journal.
An untrusted receipt/handoff cannot force acceptance.

Source failures and pre-commit schema/chronology/quality/stale or writer failures
preserve previous latest evidence/times. A commit with a lost journal receipt
is an uncertain outcome, not proof that the transaction rolled back. Failures before projection
are journaled locally rather than overwriting canonical projection state. NADI
still reports the accepted observation at its original age, while the operator
journal truthfully reports the failed new attempt. This journal is operational
metadata, not another DB or a source of public health scores.

## Private journal and replay

Use a stable owner-private 0700 journal root. Append-only `journal.jsonl` files and
all per-attempt artifacts are 0600, fsynced, no symlink/file overwrite. Each attempt
ID is unique and permanently consumed, including dry runs and failures; a repeated
ID is rejected before another source call. Clock regression/malformed/oversized
journal fails closed. No journal truncation/reset/automatic repair is provided.
Keep artifacts private and ignored; do not copy receipts/handoffs to Git.

Events record STARTED, DRY_RUN, ACQUIRED, WRITER_STARTED, ACCEPTED, FAILED,
REPLAYED, RECONCILED or ignored older batch. Separate last_attempt_at, last_acquisition_success_at,
last_evidence_success_at, last_failure_at and last_replay_at are derived from those
events. ACQUIRED is a successful typed governed acquisition (even if subsequent quality
or chronology acceptance fails),
not the technical PI worker's collector_last_success_at. Journal stores status,
phase, counts and non-secret authorization references, not process values, source
URLs, exception details or credentials. Failure request count can be unknown when
a source process/receipt fails; it is never falsely reported as zero.

Replay is explicit `--replay-file` with separate execute authorization, no source
launcher or GET. Canonical `replay_only` checks that every payload already equals
persisted latest evidence, with valid projection chronology, and returns written 0
without changing latest rows **or projection state**. It cannot create a new row,
clear a later failure, refresh timestamps or update the journal evidence-success
time. A different same-timestamp payload or unaccepted artifact is rejected.
Older batches remain ignored and do not become an evidence success. Stale original
source/projection timestamps remain stale after replay.

Journal and Mart cannot share one atomic transaction. A durable WRITER_STARTED
intent contains the handoff hash before the writer is invoked. Until ACCEPTED,
REPLAYED or IGNORED_OLDER_BATCH confirms that attempt, new acquisition is blocked
with WRITER_OUTCOME_UNKNOWN. Explicit replay of exactly that handoff may reconcile
an already committed row read-only, adding RECONCILED without inventing an evidence
success time. If the handoff was not committed, replay rejects it: stop and obtain
controlled administrative reconciliation; never truncate the journal or retry the
source automatically. Keep one authoritative journal root per pilot/operator;
a new empty root is not a recovery mechanism. A disk error after commit may leave
new evidence in Mart, so inspect the row before declaring a rollback.

## Deployment / rollback handoff — after review and merge only

1. Obtain accountable operational decisions on proposed monitoring windows and
   source/projection freshness. Keep source/projection blank where evidence is
   still insufficient. Approve one live manual refresh separately; a software PR
   merge does not authorize it or recurrence.
2. Resolve exact merged SHA, inventory existing overrides/images and back up private
   config. Build exact reviewed Cockpit API and Collector-owned operator tooling.
   Do not deploy this branch, use an arbitrary working tree, migrate, recreate
   volumes or replace accepted overrides. Worker/API source data stores stay intact.
3. Validate clean managed/external Compose and runtime policy parse. Use component
   mode with legacy values blank; initially all new values can also stay blank.
   Apply only separately approved values. Replace only required API/operator
   tooling; preserve normal collectors. No registry reload/backfill is needed.
4. Create reviewed private local launcher, pin its SHA, choose fixed operator/host
   and private journal root. Example launcher **template**, containing paths only:

```sh
#!/bin/sh
set -eu
exec /absolute/reviewed-release/pi-collector/.venv/bin/picollector "$@" \
  --source-env-file /absolute/private/platform/.env.platform
```

   Source process must use that reviewed release's environment. The coordinator
   separately uses the authorized Mart admin DSN and managed config; public API
   continues using `nadi_mart_reader`. No credentials belong in launcher text.

5. Read-only canonical migration/reader status and runtime regression, then dry-run:

```bash
COCKPIT_CONFIG_MODE=managed cockpit condition refresh \
  --state-directory /absolute/private/coal-flow-refresh \
  --baseline-file /absolute/private/accepted/handoff.json \
  --baseline-sha256 76f871f2993f17d8635ac852a56a3593c8cb0a129d97910845f37bd14398bd8e \
  --attempt-id unique-dry-run-id
```

6. Only after separate live authorization, use a **new** attempt ID and add
   `--execute --authorization-ref <non-secret-approval-ref>` plus
   `--collector-launcher <private-pinned-launcher> --collector-sha256 <checksum>`.
   Run at most once, maximum 5 GET, exactly one existing signal. No additional
   mapping, signal approval, history or automated retry. A new manual acquisition
   after failure requires a new accountable authorization decision.
7. For replay, use a new attempt ID and same baseline flags, `--execute`, the
   accountable replay authorization reference, and `--replay-file` pointing to
   the newly accepted private handoff; omit source launcher. Capture full row/time
   equality, no source calls, no new evidence success.
8. Verify actual condition/integration/factual APIs, asset/Data Trust UI and all
   nine readiness gates, including `--require-pass` nonzero while unknown policies
   persist. Decide whether new repeat evidence supports source/projection policy.
   Do not call Phase 1 COMPLETE from one successful refresh.

Rollback: stop invoking the manual runner; no daemon exists to disable. Restore
reviewed previous API image/config with accepted runtime pins. Previous `478cce1`
understands only legacy values, so clear new component values deliberately and
restore the exact previously approved legacy settings (blank in current runtime),
not synthetic SLA numbers. Never delete condition tables/evidence/mappings or
journal history. No DB rollback/restore, migration, source recollection or cursor
reset is part of this additive software rollback. If a source process is still
running, retain the host lock and let it finish or terminate/reap its local group
before another run. Inspect writer/hand-off outcome before retry; never relabel an
old artifact as a fresh reading.

## Engineering decisions still pending

| Decision | Accountable role | Current state |
|---|---|---|
| Maximo/Mart 660 monitoring allowance and scope | platform/Maximo/Mart owners with reliability engineer | PROPOSED, not activated |
| PI 1800 complete-cycle allowance | PI operations and platform owner | PROPOSED, not activated |
| Coal Flow sampling/compression / permitted age | Boiler/instrumentation engineer and project owner | POLICY_EVIDENCE_INSUFFICIENT |
| Condition projection/refresh age and operating budget | reliability integration owner and project owner | POLICY_EVIDENCE_INSUFFICIENT |
| Exact reviewed deployment and one manual live run | accountable runtime operator/project owner | separate authorization required |
| Recurrence, backoff, retry ceiling and alerting | source/runtime owners | not authorized, not installed |

Software implementation readiness is assessed by tests below. Production acceptance,
activation, source refresh and real replay remain subsequent controlled work.


## Candidate validation — 8 October 2026

All final runs have zero failures/errors. An earlier launcher fixture assumed
`/usr/bin/python3`; disposable-container testing exposed that portability defect.
It now uses the running interpreter. The final suite also tests a lost post-commit
journal receipt, strict reconciliation, mid-flight signal retirement, future
collector completion and over-budget handoff rejection.

Commands were executed from this branch's checkout. The host uses the existing
Cockpit/PI virtual environments and host test dependency bundle; PYTHONPATH pins
this candidate source, not the primary checkout's editable install.

```bash
# From repository root, host hermetic + clean managed/external Compose checks:
PYTHONPATH="$PWD/reliability-cockpit:/tmp/nadi-phase1-host-testdeps" \
DATABASE_URL=sqlite+pysqlite:///:memory: NADI_COMPOSE_TESTS=1 \
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
  -m unittest discover -s reliability-cockpit/tests

# From pi-collector, mocked source transport only:
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python \
  -m unittest discover -s tests

# From reliability-data-contracts:
PYTHONPATH="$PWD/../reliability-cockpit:/tmp/nadi-phase1-host-testdeps" \
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
  -m unittest discover -s tests

# Disposable PostgreSQL suite, from repository root; test-only credentials:
docker run --rm --network container:nadi-001b-mart-test \
  -v "$PWD:/workspace:ro" -w /workspace/reliability-cockpit \
  -e DATABASE_URL=sqlite+pysqlite:///:memory: \
  -e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test \
  -e RELIABILITY_MART_MIGRATIONS_ROOT=/workspace/reliability-cockpit/migrations \
  nadi-phase1-acceptance-test:local python -m unittest discover -s tests

git diff --check
```

| Final run | Discovered | Passed | Skipped | Failed/errors |
|---|---:|---:|---:|---:|
| Cockpit host, Compose enabled | 311 | 232 | 79 | 0 |
| Cockpit isolated PostgreSQL | 311 | 303 | 8 | 0 |
| PI Collector hermetic | 183 | 172 | 11 | 0 |
| Reliability data contracts | 14 | 14 | 0 | 0 |

The two Cockpit runs overlap: do not add their counts as unique tests. Host skips
are optional DB fixtures, exercised in the PostgreSQL run. The latter skips
host-only Compose checks and an environment-specific case; Compose was separately
validated in the host run. PI skips are optional PostgreSQL/Timescale fixtures;
no PI persistence/schema/worker code changes require a production integration run.
Existing resource-close warnings remain non-failing test-fixture diagnostics.
The test PostgreSQL container uses tmpfs and `--network none`; only the disposable
test runner joins its network namespace. It has no operational volume or network.

Read-only operational reconciliation confirms unchanged container IDs/start times,
private config authority, reader privileges and migration ledgers. Hashes of the
production mapping/selection and full condition row/projection state equal the
accepted baseline. The frozen handoff SHA256 remains
`76f871f2993f17d8635ac852a56a3593c8cb0a129d97910845f37bd14398bd8e`.
845 registered assets, PROPOSED=0, VERIFIED=1, approved signal=1, latest evidence=1,
projection state=1 and 433 active PI attributes/snapshots are retained. Latest WO
incremental and PI successful cycle report zero errors. WO recovery floor and its
single floor record remain intact; ordinary collector progress is not task DML.
Factual registry/overview, platform/asset integration-status and pilot condition
API return HTTP 200. The technical PI component remains DEGRADED where its existing
quality evidence warrants it; pilot mapping is CURRENT while platform mapping
coverage remains partial. No status is relabeled to healthy.

Actual deployed nine-gate readiness is unchanged:

| Gate | Verdict | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-PI-COLLECTOR-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-IDENTITY-MAPPING-READY | PASS | VERIFIED_PILOT_AVAILABLE |
| P1-SIGNAL-SELECTION-READY | PASS | APPROVED_PILOT_SIGNALS_AVAILABLE |
| P1-CONDITION-PROJECTION-READY | UNKNOWN | UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID |

`cockpit phase1-readiness` returns UNKNOWN/exit 0;
`cockpit phase1-readiness --require-pass` returns UNKNOWN/exit 2. These commands
were executed read-only in the existing cockpit-api, without candidate deployment.
Private raw inspection artifacts remain ignored; only aggregate evidence is here.

Task-attributable production PI/Maximo source GETs and writes, mapping import/verify,
signal approvals, condition projection, history/backfill, AF discovery, registry
mutation, DB resets/truncation/DDL, new operational DBs, volume recreation, policy
activation, service restart/deployment and CEMS/NK changes are all **0**.
Background accepted collectors continue normally. Software implementation is ready
for review; Phase 1 remains CURRENT/PARTIAL pending controlled runtime handoff,
accountable policy decisions and separately authorized single live refresh/replay.
