# NADI-IDN-002B — Coal Feeder A human-reviewed pilot

Evidence reference: `NADI-IDN-002B-COAL-FEEDER-A-20261008`.
Baseline: main `1df5b96914db7bae9ad1b836489fe1c39202ed02`, PR21 MERGED;
branch `codex/nadi-idn-002b-first-verified-asset`. Runtime uses accepted c2fb0fc
consumer images and historical control checkout 0c800da with preserved overrides.

Current R1-FIX-01 verdict: **PASS — bounded real pilot accepted**. Reviewed
512-character contract deployed; one approval, live canary, real projection
and replay accepted. Overall Phase1 readiness remains UNKNOWN with blank
freshness policy. See the runtime-promotion checkpoint below; previous pending
statements and measured checkpoints are historical.

## Human review and exact identity

Fauzi is the accountable project operator/recorder, explicitly identified by the
human in this task. Hidayat, System Owner Boiler / Senior Engineer, gave an
in-person verbal **MATCH** on 2026-10-08, reported by the project operator who
spoke to him. This authorizes the bounded innovation pilot. This record is not a
signed document, email, drawing, direct engineer authentication or engineer login.
The controlled verification records `verified_by=Fauzi`; Hidayat remains the
technical reviewer in its note. No automation identity is used as reviewer.

Canonical registered asset: `asset:MAXIMO:MXASSET:BSR:IP:CS10HFB01AF001-001`.
Maximo: `CS10HFB01AF001-001`, COAL FEEDER A, BSR/IP, CS01, OPERATING,
parent `CS10HFB01-001` (COAL FEEDER SYSTEM as supplied by operator). Local
Mart identity agrees with asset/site/org/unit/status/parent; source Asset ID 656454.
No new Maximo source request was made.

PI: CENTRAL_PI, PRIMARY_EQUIPMENT; server piaf; database Indonesia Power Corporate.
Exact AF path: `\\piaf\Indonesia Power Corporate\BSR\BSR1\Boiler System\BSR1.Coal Feeder\BSR1.Coal Feeder A`.

| Reference | Source-returned exact WebId from Round2 evidence |
|---|---|
| Server | `F1RSNOCpqPfunU-7w0-YUdQS0QUElBRg` |
| Database | `F1RDNOCpqPfunU-7w0-YUdQS0Q99202FF7lkibHr9gNLzHJAUElBRlxJTkRPTkVTSUEgUE9XRVIgQ09SUE9SQVRF` |
| Element | `F1EmNOCpqPfunU-7w0-YUdQS0QB8IwncUU7hG40gBQVrgiewUElBRlxJTkRPTkVTSUEgUE9XRVIgQ09SUE9SQVRFXEJTUlxCU1IxXEJPSUxFUiBTWVNURU1cQlNSMS5DT0FMIEZFRURFUlxCU1IxLkNPQUwgRkVFREVSIEE` |

The cross-system identity is established by the reported human MATCH, not
label similarity or technical Attribute collection. Existing R1/R2 structured
investigation remains preserved. Pulverizer A/G remain unverified; BFPT remains
REJECTED / FROZEN / DO NOT VERIFY. No other mapping is authorized here.

## Separate AF data-quality limitation

`PI_AF_KKS_LOOKUP_UNRESOLVED`: KKS returned No Data. Equipment Name
`%Coal Feeder A%`, Kode Equipment `%AF%`, Kode System `%HFB%`, Unit CS01
are prior observations, not independent exact identity proof. Lookup references
`[BLT ASSET]`; operator believes BLT represents Lontar, but its BSR authority is
unproven. No AF expression/table/KKS or Maximo data is changed.
PI Vision/Maximo identity observations here are operator-supplied task evidence;
no direct PI Vision session, screenshot or signed technical artifact was inspected.

## Coal Flow qualification

One exact known PI Knowledge verified/ok entry at
`pi-knowledge/mappings/bsr1-parameters.yaml:1540` identifies Coal Flow,
position BSR1.Coal Feeder A, data_type Double, knowledge unit `t/h`. Registry
WebId matches that entry exactly and has a local snapshot; direct-element
attribute list in Round2 contains Coal Flow. Registry `af_path` is a shortened
breadcrumb omitting feeder position and must not establish ownership alone.
Live canary, if approved, must recheck exact Element ownership through the
governed boundary before accepting evidence. NPHR similarly labelled signals
and total/system Coal Flow are not selected.

Technical attribute ID: `BSR-BSR1-bsr1_coal_feeder-coal_flow-coal_flow-bsr1_coal_feeder_a`.
Exact Attribute WebId: `F1AbENOCpqPfunU-7w0-YUdQS0QB8IwncUU7hG40gBQVrgiewNnelo9a3w1MaVpdZkrrtDAUElBRlxJTkRPTkVTSUEgUE9XRVIgQ09SUE9SQVRFXEJTUlxCU1IxXEJPSUxFUiBTWVNURU1cQlNSMS5DT0FMIEZFRURFUlxCU1IxLkNPQUwgRkVFREVSIEF8Q09BTCBGTE9X`.
Local snapshot: NUMERIC; source unit `Ton/h`, source timestamp
`2026-10-08T03:28:01.483001+00:00`, collected_at`2026-10-08T03:28:03.9557+00:00`;
Good=true, Questionable=false, Substituted=false, Annotated=false.
Source unit is preserved; `t/h`/`Ton/h` are reported without implicit conversion.
No process value or unrestricted source payload is committed.

Signal approval is separate from human physical identity. Accountable approval
for feeder-specific coal-flow meaning/use is pending at this checkpoint. No
production condition signal, live source canary or projection has occurred yet.
Freshness policy stays blank/UNKNOWN; a recent collection does not establish
source freshness or equipment health.

## Acceptance evidence

Runtime preflight 2026-10-08T03:37:26Z: registered 845, mappings 0/0,
condition selections/evidence/state 0; Mart 002/003/004 applied, reader write
privileges 0, PI 490total/433active/433snapshots, latest successful cycle 433/433
errors 0. WO cursor advances normally, recovery floor 2026-08-21T03:56:54Z
is intact. Private aggregate audit/controlled CSV remain ignored.

### Mapping operation accepted

Canonical read-only `cockpit mart-migrate` returned ready, 002/003/004 APPLIED;
no DDL was run. `cockpit mapping import --file /pilot/coal-feeder-a.csv --dry-run`
returned rows_seen=1 / valid=1 / accepted=1 / rejected=0 / conflicts=0 / duplicates=0 / unknown_assets=0.
The same command without --dry-run imported exactly one PROPOSED. Read API
returned UNMAPPED with PROPOSED candidate, showing the proposal was unusable.
Controlled `cockpit mapping verify --mapping-id nadi-map-a8c71ce66757ea9de50c21de3d8fd18b
--verified-by Fauzi --evidence-ref NADI-IDN-002B-COAL-FEEDER-A-20261008
--verification-note <reported human MATCH and KKS limitation>` then promoted it.
Actual verification timestamp: `2026-10-08T03:41:17.972722+00:00`.
Final PROPOSED=0 / VERIFIED=1, unique resolver MAPPED, ambiguous_assets=0.
No other identity or governance history was changed.

### Signal, canary and projection checkpoint

**PARTIAL — SIGNAL_APPROVAL_PENDING.** Exact known technical Coal Flow A
reference/unit/type/quality was inspected locally. Fauzi's explicit approval
of its intended feeder-specific meaning/use was requested in this task and
remains pending. Identity MATCH does not imply signal semantic approval.
No approved signal was manufactured. No plan/live canary/projection was executed.
Exact live Attribute→Element ownership must still be rechecked by the governed
canary after approval; local registry breadcrumbs are insufficient alone.

Production source GET counts: PI=0, Maximo=0. Canary value/type/timestamp/quality
are **NOT MEASURED**; the local snapshot above is not live governed acceptance.
Mart selected signals/evidence/state remain0/0/0. Projection idempotency is
tested synthetically, not claimed for a real batch that does not exist.

### API, UI and actual readiness

Platform status, bounded asset status, pi-mapping, condition-evidence and local
PI integration-observation returned HTTP200. Coverage: 845 registered / 1 verified /
0 approved / 0 projected. Asset condition response MAPPING_VERIFIED,
NO_APPROVED_SIGNALS, empty items and no successful condition collection.
Hydrated Coal Feeder A UI showed 246 maintenance events, verified mapping,
no approved signals, unknown equipment condition and explicit blocked projection.
All five Integration Status components render; technical quality degradation
remains distinct from collector success. No public governance mutation path.

`docker exec reliability-cockpit-platform-cockpit-api-1 cockpit phase1-readiness`
returned exit 0 / verdict BLOCKED; adding `--require-pass` returned exit 2.

| Gate | Verdict | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-PI-COLLECTOR-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-IDENTITY-MAPPING-READY | PASS | VERIFIED_PILOT_AVAILABLE |
| P1-SIGNAL-SELECTION-READY | BLOCKED | NO_APPROVED_SIGNALS |
| P1-CONDITION-PROJECTION-READY | BLOCKED | NO_APPROVED_SIGNALS |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID |

All three freshness policies remain blank: **FRESHNESS_POLICY_PENDING**.
Human identity blocker is resolved for this one pilot only, not all 845 assets.
Other assets remain unmapped and BFPT is still frozen.

### Regression and source safety

Baseline 03:37:26Z → final03:44:04Z on 2026-10-08. All 23 existing container
IDs/start times/mounts, configuration-authority checksum, DB/volume/network
identities, Mart/PI migration ledgers and reader ACL remained identical.
No source collector, API or UI was restarted/redeployed. Dedicated Mart reader
has SELECT with no INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER on public
tables; no owner/superuser/role-create/DB-create/bypass-RLS privileges. Public
NADI/source credentials remain separated from controlled writer.

Mart factual counts stayed 845 registry / 11,845 assets / 69,635 maintenance / 113,902 WO.
WO cursor 2026-10-08T03:35:02Z preserved, recovery-floor 2026-08-21T03:56:54Z
and its one ledger row intact; latest bounded incremental 25 seen / 0 upserted /
25 skipped / errors 0. Projector succeeded normally. PI 490 total / 433 active / 433 snapshots /
133,570 history preserved, latest normal background cycle 03:42:56Z, 433/433, errors 0.
No task source acquisition occurred; normal background collectors continued.
Factual API200 and current maintenance windows remain populated.

Task operations: mapping import=1, verify=1; signal approvals=0, condition projection=0;
PI source GET/write=0/0, Maximo source GET/write=0/0; history/backfill=0, AF discovery=0,
registry modifications=0, DB reset/truncate=0, new operational DB=0, DDL=0,
volume recreation=0, service restarts=0, CEMS/NK changes=0, credential exposure=0.
Private operator CSV/audit/admin env were excluded from Git; minimal transient
admin env is removed after operations. One disposable test DB was removed.

## Targeted regression commands and counts

Run from this baseline's respective component cwd. Cockpit interpreter:
`/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python`;
PI interpreter: analogous `pi-collector/.venv/bin/python`. Cockpit host tests use
`DATABASE_URL=sqlite+pysqlite:///:memory:` and
`PYTHONPATH=/tmp/nadi-phase1-host-testdeps`. No operational DSN enters tests.
Every command below is `python -m unittest discover -s tests -p <pattern> -q`.

| Component / pattern | Executed PASS | Skipped |
|---|---:|---:|
| Cockpit test_asset_af_mapping*.py |22|0|
| Cockpit test_condition_evidence.py (host) |25|26PG|
| Cockpit test_condition_evidence.py (disposable PostgreSQL) |51|0|
| Cockpit test_mart_migrations.py (disposable PostgreSQL) |18|0|
| Cockpit test_projection_acceptance.py (disposable PostgreSQL) |15|1Node-only|
| Cockpit test_reliability_mart.py |41|0|
| Cockpit test_api.py |5|0|
| Cockpit test_integration*.py |22|0|
| Cockpit test_phase1_readiness.py |11|0|
| PI test_governed*.py |26|0|
| PI test_condition_evidence.py |8|0|

244 successful test executions,27 skips across commands;219 distinct Python test
cases passed (25 SQLite cases repeated in PostgreSQL-enabled run). Node-only
synthetic UI case not rerun because no UI changes; real hydrated UI was smoked.
Python 3.14 emitted existing SQLite unclosed-connection ResourceWarnings in
fixture tests; assertions passed. No implementation changes or new tests.

Disposable PostgreSQL command prefix (never operational Mart):

```sh
docker run -d --name nadi-idn002b-mart-test --network none \
  --tmpfs /var/lib/postgresql/data -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test-only -e POSTGRES_DB=nadi_governance_test postgres:16.4-alpine
docker run --rm --network container:nadi-idn002b-mart-test \
  -v <exact-main-worktree>:/workspace:ro -w /workspace/reliability-cockpit \
  -e RELIABILITY_MART_MIGRATIONS_ROOT=/workspace/reliability-cockpit/migrations \
  -e DATABASE_URL=sqlite+pysqlite:///:memory: \
  -e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test \
  nadi-phase1-acceptance-test:local python -m unittest discover -s tests -p <pattern> -q
docker rm -f nadi-idn002b-mart-test
```

## Next controlled step

Obtain Fauzi's accountable approval for exactly this feeder-A coal-flow meaning/
use. Then approve one canonical signal, export trusted verified/approved plan,
use Collector-owned source credentials for at most 10 GETs / one current snapshot,
check real exact lineage/unit/quality/time, project accepted bounded handoff,
replay to prove idempotency and rerun API/UI/readiness. Separately approve
defensible freshness thresholds; no value can establish equipment health.
Phase 1 remains CURRENT/PARTIAL, product BLOCKED; this PR stays open/unmerged.

## R1 — explicit Coal Flow A signal approval (8 October 2026)

This round continues PR22 at2463f03, main1df5b969; earlier signal-pending
checkpoint is historical. Fauzi directly provided APPROVED for the one exact
Coal Flow A / coal_flow signal, for condition evidence in the bounded innovation
pilot. Evidence ref `NADI-SIGNAL-COAL-FLOW-A-20261008`. Hidayat approved
equipment identity only; no PI signal approval is attributed to him. No signed
document, engineering SLA or unit normalization approval is claimed.

Before selection, one guarded exact Attribute metadata GET proved WebId,
source Path ending `BSR1.Coal Feeder A|Coal Flow`, Name Coal Flow, TypeDouble
and source-returned Element link equal to the existing VERIFIED target.
Local current snapshot independently confirms NUMERIC/Ton/h with all four
quality flags. Source metadata DefaultUnitsName is `Tonne per hour`; observed
snapshot abbreviation `Ton/h` is preserved without conversion.

Approval recorded_at: `2026-10-08T04:07:10.208836+00:00`; approver `Fauzi`.

### Exact source identity and local metadata

The metadata request at `2026-10-08T04:06:19.063465Z` returned HTTP200 for
`GET /attributes/<the exact 203-character WebId above>`. The guarded PI client
validated the source-returned Element link against the exact already-VERIFIED
Element; the attribute Path exactly extends that Element path with `|Coal Flow`.
This was a single exact identity check, not enumeration, similarity matching or
a governed snapshot canary. Existing server/database/element lineage and human
MATCH remain as recorded above. No new mapping is created.

Local precheck snapshot: NUMERIC, `Ton/h`, source timestamp
`2026-10-08T03:57:09.464004Z`, collected_at `2026-10-08T03:57:10.403866Z`;
Good=true, Questionable=false, Substituted=false, Annotated=false. This is local
technical metadata, not live governed condition acceptance. Process value was
not read into this R1 evidence packet. Canary source/collection time, age and
value are NOT MEASURED; freshness remains UNKNOWN with all policies blank.
Good describes signal quality and never establishes equipment HEALTHY.

### Canonical approval blocked before production mutation

The intended one-signal canonical selection records signal ID
`nadi-signal-coal-flow-a-20261008`, existing mapping
`nadi-map-a8c71ce66757ea9de50c21de3d8fd18b`, CENTRAL_PI Attribute reference,
semantic_name `coal_flow`, APPROVED, approved_by `Fauzi`, actual recording
time above and evidence reference `NADI-SIGNAL-COAL-FLOW-A-20261008`.
The accountable approval was supplied directly by the project operator on
2026-10-08 for the NADI condition evidence innovation pilot.

Reviewed-runtime command:

```sh
cockpit condition approve-signal --file /pilot/selection.json
```

It exited2 before DML. Sanitized validation: `sources.pi.attribute_ref`,
`string_too_long`, `max_length=200`. Exact reference length is203. Production
selection count remained0; evidence/state remained0. There is no conflicting
selection. Truncating or guessing a shorter source identity would invalidate
ownership, and inserting a candidate-only long reference would break the merged
NADI read model. No ad-hoc SQL or validation bypass was used.

Candidate repair checkpoint `83638d8` changes only `attribute_ref` bounds from200 to512 in
SelectedPiAttribute / PiAttributeLineage and four corresponding JSON schemas.
Canonical exporter checks agreement. Mapping IDs/AF refs, signal-count bound,
approval/lifecycle gates, read-only/source guards and unit/time semantics remain
unchanged. This is an additive contract extension; existing1.0 documents still
validate. No DDL is needed because Attribute references are stored in JSON,
not a constrained new column. No migration or deployment occurred.

Synthetic tests prove exact203/512-character refs cross approval → guarded
Collector fixture → four schema/model validations → Mart → HTTP200 without
truncation; same approval conflicts without duplicate, same handoff replay
writes0 and does not change read documents. All four models/schemas reject513.
These disposable fixture results are not production canary/replay evidence.
The actual private selection203 validates with the candidate model/schema only.

### Production handoff, projection and NADI acceptance

Governed canary GET=0; no production plan/handoff/condition batch exists. Handoff
validation, first real projection and same-batch production replay are blocked
on reviewed compatible code. Production `condition_evidence_latest` has no pilot
row. No direct NADI-to-PI client/credentials or arbitrary source plan endpoint
was introduced. Existing Collector-owned boundary is unchanged.

Platform/asset integration-status, condition-evidence and local PI
integration-observation endpoints returned HTTP200. Hydrated Coal Feeder A asset
page showed246 maintenance events, VERIFIED mapping, NO_APPROVED_SIGNALS,
empty condition evidence and UNKNOWN condition. Data Trust at11:15:53 Jakarta
showed all five components and coverage845/1/0/0 (registered/verified/approved/
projected). PI technical quality degradation and epoch timestamps remain visible
independently of successful collector activity. No fake health/score or public
mapping/signal mutation UI was added. UI acceptance of actual projected evidence
remains pending because there is no production batch.

Actual runtime commands:

```sh
docker exec reliability-cockpit-platform-cockpit-api-1 cockpit phase1-readiness
docker exec reliability-cockpit-platform-cockpit-api-1 cockpit phase1-readiness --require-pass
```

Normal command exit0, overall BLOCKED; `--require-pass` exit2.

| Gate | Verdict | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-PI-COLLECTOR-CURRENT | UNKNOWN | UNKNOWN_FRESHNESS_POLICY |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-IDENTITY-MAPPING-READY | PASS | VERIFIED_PILOT_AVAILABLE |
| P1-SIGNAL-SELECTION-READY | BLOCKED | NO_APPROVED_SIGNALS |
| P1-CONDITION-PROJECTION-READY | BLOCKED | NO_APPROVED_SIGNALS |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID |

### R1 regression and safety

Read-only precheck04:05:26Z → final04:12:07Z, 2026-10-08. All23 existing
container IDs/start times/mounts, private configuration checksum, DB/volume/
network identities, Mart/PI migration ledgers and reader ACL unchanged.
Runtime control checkout remains0c800da; consumer images remain exact accepted
c2fb0fc. Main/PR baseline1df5b969/2463f03 is not silently treated as deployed
code. The private `.env.platform` remains managed configuration authority.
Transient writer env stays private and is removed after this task.

Owning Mart is existing maximo-db/maximo_collector, with dedicated
nadi_mart_reader SELECT-only; legacy Cockpit/PI stores remain separate.
Reader has no DML/TRUNCATE/REFERENCES/TRIGGER/CREATE, no relation ownership,
superuser/createDB/createRole/bypass-RLS powers. Public API remains credential-
free for source systems; local writer path remains separate.

Mart remains845 registered /11845 assets /69635 maintenance /113902 WO;
PROPOSED0 / VERIFIED1, selection/evidence/state0/0/0;002/003/004 preserved.
WO cursor03:35:02Z →04:02:51Z due normal background work; recovery floor
2026-08-21T03:56:54Z and exactly one recovery ledger row intact. Latest bounded
incremental04:07:45Z:25 seen/1 upserted/24 skipped/errors0. Asset/maintenance
projector succeeded04:09:35/36Z. Factual API200,7-day711/30-day1990 populated.
PI490 total/433 active/433 snapshots/133570 history; migration004 and Timescale
hypertable/two chunks preserved. Latest completed normal worker cycle
04:11:20.367134Z:433/433/errors0, single advisory lease, unchanged cadence and
source request floor. Background collector activity is distinct from task GETs.

R1 attributable operations: PI business GET1 (exact Attribute identity only),
live governed canary GET0; Maximo GET0; source writes0/0; mapping imports0,
additional verify0; canonical signal approval attempt1/persisted0; condition
projection0; history/backfill0; broad AF discovery0; registry mutation0;
collector/API/UI restart0; deployment0; DDL0; reset/truncate0; volume recreation0;
new operational DB0; CEMS/NK changes0; credential exposure0. Two disposable
test DB containers used private tmpfs/network isolation and are removed; their
synthetic approvals/projections never count as production governance.
PI_AF_KKS_LOOKUP_UNRESOLVED remains open; BFPT REJECTED/FROZEN/DO NOT VERIFY.

### R1 full test commands and counts

`W` denotes this PR22 worktree. `C` and `P` are the existing primary checkout's
Cockpit and PI venv Python paths. Host Cockpit/contracts tests use
`DATABASE_URL=sqlite+pysqlite:///:memory:` and
`PYTHONPATH=/tmp/nadi-phase1-host-testdeps` (plus `:tests` for named UI cases).
No operational database/source credentials are supplied to tests.

```sh
# Full Cockpit, cwd W/reliability-cockpit, disposable PostgreSQL16 fixture:
docker run --rm --network container:nadi-idn002b-r1-mart-test \
  -v "$W:/workspace:ro" -w /workspace/reliability-cockpit \
  -e RELIABILITY_MART_MIGRATIONS_ROOT=/workspace/reliability-cockpit/migrations \
  -e DATABASE_URL=sqlite+pysqlite:///:memory: \
  -e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test \
  nadi-phase1-acceptance-test:local python -m unittest discover -s tests -q
# 249 total:242 passed,7 opt-in skips.

# Close6 Compose opt-in skips; cwd W/reliability-cockpit:
NADI_COMPOSE_TESTS=1 "$C" -m unittest discover -s tests -p test_runtime_wiring.py -q
# 11 passed,0 skipped (5 repeat cases).

# Close1 Node/rendered Asset+Data Trust skip, same cwd with PYTHONPATH including tests:
"$C" -m unittest test_projection_acceptance.ProjectionAcceptanceTest.test_api_documents_render_actual_asset_evidence_and_trust_views -q
# 1 passed,0 skipped; transient existing node_modules symlink removed afterward.

# Full PI Collector; cwd W/pi-collector:
"$P" -m unittest discover -s tests -q
# 177 total:166 passed,11 Timescale opt-in skips.

# Close11 Timescale skips in disposable2.16.1-pg16 fixture:
docker run --rm --network container:nadi-idn002b-r1-pi-test \
  -v "$W:/workspace:ro" -w /workspace/pi-collector \
  -e PI_MIGRATION_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/pi_runtime_test \
  nadi-phase1-acceptance-test:local python -m unittest discover -s tests -p test_migration_runner.py -q
# 19 passed,0 skipped (8 repeat cases).

# Contracts; cwd W/reliability-data-contracts:
"$C" -m unittest discover -s tests -q
# 14 passed,0 skipped.

# Canonical model/generated-schema compatibility; cwd W/reliability-cockpit:
"$C" scripts/export_evidence_contracts.py --check
# PASS; all3 generated contracts match canonical Python models.

git diff --check
# PASS.
```

Across these environments **all440 distinct cases passed** (249Cockpit,
177PI Collector,14contracts); every full-suite skip was separately exercised.
The projection acceptance pattern was also rerun on host:20 total,9 PASS,
11 environment skips already covered above. After strengthening the duplicate-
approval assertion, the two new cases were rerun on SQLite and PostgreSQL:
2 PASS each,0 skips. No application change followed the full suites. Existing
Python3.14 fixture ResourceWarnings do not fail assertions. No UI implementation
change, so Next/TypeScript builds were not redundantly repeated; actual hydrated
pages and synthetic rendered-components acceptance both passed.

### R1 next controlled step and roadmap effect

Keep PR22 OPEN/UNMERGED for senior review. **PARTIAL — CODE_ACCEPTANCE_REQUIRED**:
approval is available; source identity is exact; the incompatible merged contract
is repaired only in candidate code. Review/merge and deliberately deploy compatible
Cockpit API/operator tooling (and packaged canonical contracts where used) using
accepted overrides. Then persist exactly the one authorized selection, reapply
safely without duplicate, export its trusted plan, execute Collector-owned bounded
canary within the10-GET budget, validate handoff, project one signal, replay locally
without extra source requests, and rerun actual API/UI/readiness. No new human
signal approval or asset mapping is required for this same scope.

Phase1 remains CURRENT/PARTIAL and product BLOCKED. Freshness policy remains an
independent engineering decision, not an inferred SLA; final readiness may remain
UNKNOWN after projection. The acceptance/roadmap/status latest checkpoints expose
this concrete software/runtime gap rather than declaring only human identity is
blocking. Identity/KKS limitations and BFPT frozen state are preserved.

## R1-FIX-01 — reviewed runtime promotion and first real evidence

8 October 2026, Asia/Jakarta. **PASS for the bounded pilot definition of done**;
Phase 1 product acceptance is not claimed. Main and PR22 merge result exactly
`478cce1958ab5800ce21d7b1e93b83ff43c1ac19`; PR22 merged at 04:45:37Z.
Release checkout `/home/john-d/.codex/worktrees/nadi-idn002b-r1-runtime/reliability-knowledge-starter`
was clean at that exact SHA when built. Subsequent documentation checkpoint is
on `codex/nadi-idn-002b-r1-runtime-promotion`; its commit is not application source
for this deployment. No source-code repair or new PR is required.

### Deployment and recovery checkpoint

Existing control checkout remains
`/home/john-d/Music/reliability-knowledge-starter` at
`0c800dac1da6ef863afdb193021176fe7feac073`; unrelated 23496711.xls untouched.
Existing managed project/network/DB owners, private `.env.platform` 0600 and
accepted overrides remain unchanged. Existing source code in PI Collector and
NADI web is byte-identical between accepted c2fb0fc and reviewed478cce1;
PI has no dependency on the changed Cockpit Pydantic bound. Only cockpit-api
needs replacement; local operator uses the same new immutable Cockpit image.

Before mutation, full private owning maximo_collector `pg_dump -Fc` backup:
Started 2026-10-08T04:55:40.668488+00:00, completed 2026-10-08T04:55:42.453912+00:00; 1.785s, **13,211,427 bytes**, catalog 149 entries. SHA256 `467ec22e253cc01e61a739b0219f6499fe027de7885dc83e0df05356d88d4eac`.
All nine inventoried relations have TABLE DATA in the validated catalog;
backup 0600/private 0700, bytes stay ignored. Repeatable-read/read-only counts
and aggregate content fingerprints captured before and after; no DDL is needed
because the exact Attribute reference is in existing JSON definitions/evidence.
Canonical `cockpit mart-migrate --require-ready`:002/003/004 APPLIED, ready=true,
applied=[], duration 0.067s; no initializer, migration apply or grant DDL.

Existing six Compose files:

1. compose.yaml
2. compose.dev.yaml
3. secrets/maximo-wo-recency-002.runtime.yaml
4. secrets/nadi-pi-runtime-001.runtime.yaml
5. secrets/nadi-runtime-002.runtime.yaml
6. secrets/nadi-phase1-runtime-acceptance-001/runtime.yaml

A new ignored private `secrets/nadi-idn-002b-r1/runtime-478cce1.yaml` pins only
cockpit-api image. Effective configuration comparison proves the only change
is cockpit-api.image; environment/credentials, freshness policy, profiles,
commands, ports, mounts/networks and all other services match exactly.
Deployment uses all six files plus that final pin, unchanged project and
.env.platform authority, `up -d --no-deps --no-build cockpit-api`.
No source acquisition/dependency/init service is started.

| Field | Before | After |
|---|---|---|
| Cockpit API source/image tag | c2fb0fc reviewed foundation |478cce1958ab5800ce21d7b1e93b83ff43c1ac19|
| Container ID |b6e5ab9270e6|51496e452740|
| Started (UTC) |2026-10-07T23:21:38.194789866Z|2026-10-08T04:56:45.34578124Z|
| Other23-service inventory |22 other identities|all 22 identical IDs/start times/mounts/networks|

New image `reliability-cockpit-platform-idn002b-cockpit-api:478cce1`, immutable
`sha256:130e57ae05f650fef7472b2d41c1968c744e0c0b83aa5480fce882f50d218c57`.
Image OCI revision label is the full 478cce SHA. The preserved historical Compose
container revision label remains 8d92c25 and must not be mistaken for serving
code provenance. Executed imported domain-module SHA256 matches the exact clean
merged release file: `81561d968655116f280ec60f238f8fac961570de0d6e8adc84d60f39a0a0b612`.
Image and actual running-container probes accept the real 203-character selection,
accept synthetic 512 and reject 513; no probe DML. Pre-approval API smoke200 and
SELECT-only reader/schema checks passed before signal insertion.

Rollback before approval: omit the final image override and target only
cockpit-api with the preserved six-file config/old immutable image. After the
203-character production selection is persisted, **do not roll back blindly to
200-character readers**. Preserve the compatible reviewed image; assess canonical
selection/evidence and explicit recovery separately. No automatic DB restore,
signal retirement, mapping rollback or destructive operation is authorized here.
Private pre-mutation full backup is a recovery checkpoint, not a restore drill.

### One canonical signal approval

The R1 approval document is used unchanged, exact source identity previously
proven. Human approver Fauzi, decision APPROVED, date 2026-10-08, semantic coal_flow,
purpose NADI condition evidence innovation pilot, reference
`NADI-SIGNAL-COAL-FLOW-A-20261008`. Hidayat remains equipment reviewer only.
No new human review/request, signed artifact, unit normalization or SLA claimed.
Existing mapping `nadi-map-a8c71ce66757ea9de50c21de3d8fd18b` remains uniquely
VERIFIED / PRIMARY_EQUIPMENT / CENTRAL_PI.

Canonical new-image `cockpit condition approve-signal --file /pilot/selection.json`
returns SIGNAL_APPROVED. Repeating it returns exit 2, count remains1. Trusted
`cockpit condition plan --asset-id <existing canonical asset> --output /pilot/plan.json`
returns selected_signals 1. Plan agrees exactly with approval identifiers and
aware approval instant; canonical JSON may serialize UTC as Z instead of+00:00.
Pre-canary gates all PASS: registered asset, unique VERIFIED mapping, CENTRAL_PI,
PRIMARY_EQUIPMENT, approved exact Attribute 203, no conflicting selection, evidence 0.
Unit is not invented in selection; original snapshot unit is preserved in evidence.

### Bounded real source canary and handoff

Only Collector-owned reviewed source code/runtime credentials used. Existing PI
API image c2fb0fc has identical relevant code to merged 478cce1 and is unchanged.
No source credentials/admin DSN added to public NADI or PI API. Credentials read
in process memory from the existing authorized worker configuration, not printed
or written into artifacts. Internal operator CLI consumes only the trusted Mart
plan, with the unchanged guarded source adapter.

Observed source value **53.48906326293945 Ton/h**, **NUMERIC**, unchanged.
Source timestamp `2026-10-08T05:01:15.404006+00:00` (12:01:15.404006 Jakarta); collected_at `2026-10-08T05:01:21.125301+00:00` (12:01:21.125301 Jakarta).
Observed source age at collection 5.721295s; this is a measurement, not an SLA.
Good=true, Questionable=false, Substituted=false, Annotated=false.
Freshness SOURCE_UNKNOWN with blank policy; quality is not equipment health.
Exact original203-character WebId and known AF element/database/server lineage
preserved, Attribute Name Coal Flow, semantic coal_flow, selection approver/ref/time
unchanged. No null-to-zero, unit conversion, score, prediction or recommendation.

Five additional business GETs, all HTTP 200:
Element → Database → bounded direct Attributes of that same known Element →
exact selected Attribute metadata → selected current value. The metadata repeat
is required by the existing adapter's per-operation ownership gate; no guard is
bypassed. No parent/child/AF-wide discovery or history. Previous R1 identity GET 1
plus this canary 5 = cumulative6/10. No second canary was issued for replay.
Rate floor and response/TLS/origin/read-only guards unchanged.

Four canonical JSON schemas validate batch/plan/selection/evidence and the merged
Python EvidenceBatch agrees. Accepted private handoff SHA256:
`76f871f2993f17d8635ac852a56a3593c8cb0a129d97910845f37bd14398bd8e`.
Raw/unrestricted source responses, auth and backup bytes are not committed.
This document records only the one explicitly approved bounded observation.
The CLI supplies collector_last_success_at=null; it is preserved as unknown,
not replaced with canary collection time. The platform's separate local PI
observation reports actual technical-worker success. These are distinct facts.

### First real projection and same-batch replay

Canonical `cockpit condition project --file /pilot/handoff.json` on the reviewed
image returns PROJECTED/written 1. Exactly one row in each condition relation:
selection 1, latest evidence 1, projection state 1, all for the existing pilot.
Original NUMERIC value, Ton/h, source/collection instant, four quality flags,
exact Attribute/AF lineage and Fauzi approval provenance agree with handoff.
UTC+00:00 and canonicalZ serialization are the same original timestamp instant;
no precision or data-time change. Projected_at 2026-10-08T05:02:50.342471Z
(12:02:50.342471 Jakarta); attempted_at equals collected_at 05:01:21.125301Z.

Real replay of the SAME private handoff returns PROJECTED/written 0. Full selection,
latest and projection-state JSON/row timestamps identical before/after; condition
HTTP document identical; no duplicate, new source timestamp or artificial
freshness update. Replay source GET 0. This is actual operational replay evidence,
not the earlier synthetic fixture. No recurring production projection enabled.

### API, UI and actual readiness

Platform/asset integration-status, pi-mapping, condition-evidence and PI local
integration-observation return HTTP 200. NADI public evidence preserves full
`sources.pi.attribute_ref`203, Attribute Name Coal Flow, server/database/element,
original value/type/unit/time/quality and mapping/approval provenance.
Public API remains SELECT-only, with separate local writer credentials.

Hydrated asset UI at 12:04:28 Jakarta displays 246 maintenance events, mapping
verified/evidence available/projected, exact 53.48906326293945 Ton/h, NUMERIC,
source12:01:15/collected12:01:21/projected12:02:50, all four flags and separate
collector/source/projection UNKNOWN. No HEALTHY state/health score.
Data Trust at 12:06:47 Jakarta displays five components and coverage845/1/1/1;
this asset-specific coverage is1/1/1/1. PI technical BAD_QUALITY 18/epoch timestamps
remain distinct from this Good pilot. Global mapping coverage remains PARTIAL,
not an assertion that all 845 assets are governed.

`cockpit phase1-readiness`: LOCAL_RUNTIME overall UNKNOWN, exit 0.
`cockpit phase1-readiness --require-pass`: overall UNKNOWN, exit 2.

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

The requested conceptual projection PASS is **not** forced: merged logic requires
CURRENT source and projection freshness for its acceptance gate. With neutral
policy, real evidence is PROJECTED but freshness-qualified gate stays UNKNOWN.
This is truthful and does not invalidate the bounded pilot's successful projection.
FRESHNESS_POLICY_PENDING remains an independent engineering acceptance step.
No new SLA is inferred from the short signal age or historical collector cadence.

### Post-promotion regression and fingerprints

Precheck 04:54:00Z → regression 05:06:20Z on 2026-10-08. Existing owners:
maximo-db/maximo_collector hosts Mart; cockpit-db/cockpit is distinct legacy store;
pi-db/pi_collector remains technical PI store. Config hash, volumes/networks,
Mart002/003/004 and PI 004 ledgers and nadi_mart_reader ACL unchanged. Reader
CONNECT/USAGE/SELECT only, no DML/TRUNCATE/REFERENCES/TRIGGER/CREATE or ownership,
superuser/createDB/createRole/bypass-RLS powers.22 other container identities unchanged.

Registry 845 / assets 11845 / maintenance 69635 / WO 113902 retained. Mapping content
fingerprint exactly unchanged (VERIFIED 1/PROPOSED 0). WO cursor04:21:34Z→04:58:27Z
via normal background collector; recovery floor 2026-08-21T03:56:54Z and single
recovery row intact. Latest bounded incremental 05:04:54Z→05:05:05Z: 25 seen / 0 upserted /
25 skipped / errors 0, local projector SUCCEEDED. Factual API 200 with 7d 711 / 30d 1987.
PI 490 total / 433 active / 433 snapshots / 133570 history, hypertable/two chunks and single
worker lease unchanged; last observed complete technical cycle 04:53:52Z: 433/433,
errors 0. Ongoing workers were not stopped to freeze data for this task.

| Relation | Rows before→after | MD5 before→after | Interpretation |
|---|---|---|---|
|asset_master|11845→11845|`6db931b83e0dbe1a5f7c93c507f620bb`→`6db931b83e0dbe1a5f7c93c507f620bb`|identical|
|maintenance_event|69635→69635|`34ce313e411aae2bc42c1b3d590a1722`→`38af81d9736724aaca485d7be66ede5a`|background source/projector activity|
|reliability_asset_registry|845→845|`72a334b340b4acefa108c73945f923cc`→`72a334b340b4acefa108c73945f923cc`|identical|
|sync_cursor|1→1|`10738cd4ccf7fc17548e9db20aca264d`→`c66b09ca1a238989aa393652d2e7ae6f`|background source/projector activity|
|mart_projection_state|2→2|`7afbba694c855e44dbbf9eaeb1f506b3`→`7eee1d6095d105dd57f0c8e6276d5cdb`|background source/projector activity|
|asset_af_mapping|1→1|`83594c18ebc8c2fc9bd0d0419b371f73`→`83594c18ebc8c2fc9bd0d0419b371f73`|identical|
|condition_signal_selection|0→1|`d41d8cd98f00b204e9800998ecf8427e`→`07047dadf8a3ff430c4d2ddfe2babb09`|authorized pilot row|
|condition_evidence_latest|0→1|`d41d8cd98f00b204e9800998ecf8427e`→`2b4f508899ee5799e090812067c8ac2f`|authorized pilot row|
|condition_projection_state|0→1|`d41d8cd98f00b204e9800998ecf8427e`→`d067d41adcafa07bd22e953c352f89d9`|authorized pilot row|


Background collector/projector legitimately changed maintenance content/cursor/
projection state while counts remain stable. These are **not** claimed byte-
identical factual fingerprints. The canonical approval/project commands write
only the three condition relations; task Maximo business GET/write0. Asset/Registry/
existing mapping fingerprints are exactly equal. No bootstrap/floor reset occurred.
PI_AF_KKS_LOOKUP_UNRESOLVED stays open; BFPT REJECTED/FROZEN/DO NOT VERIFY.

### Targeted checks and safety

No new code repair, so accepted PR22 full 440-case evidence remains historical;
no mechanical full-suite rerun or new test DB needed. This deployment ran:

| Component/pattern | PASS | Skipped |
|---|---:|---:|
| Cockpit test_condition_evidence.py |25|26PostgreSQL opt-in|
| Cockpit test_api.py |5|0|
| Cockpit test_integration*.py |22|0|
| Cockpit test_phase1_readiness.py |11|0|
| Cockpit test_runtime_wiring.py |11|0|
| PI test_governed*.py |26|0|
| PI test_condition_evidence.py |8|0|
| Contracts full suite |14|0|

**122 tests PASS, 26 explicitly skipped PG cases**; earlier accepted isolated PG
suite is not misreported as rerun. Real authorized PG approval/projection/replay
and SELECT-only reads are additional runtime acceptance, not a synthetic test DB.
Cockpit and PI were executed in existing component venvs with
`unittest.defaultTestLoader.discover("tests", pattern=...)` loops for the listed
patterns. Equivalent per-pattern reproduction:
`python -m unittest discover -s tests -p <pattern> -q`. Contracts executed
`python -m unittest discover -s tests -q`.
Cockpit uses DATABASE_URL=sqlite+pysqlite:///:memory:,
PYTHONPATH=/tmp/nadi-phase1-host-testdeps, NADI_COMPOSE_TESTS=1; all hermetic/config-only.
Canonical exporter `python reliability-cockpit/scripts/export_evidence_contracts.py --check`
passes all3 generated contracts. Real handoff validates4 schemas. Image/serving
contract203/512 acceptance and513 rejection PASS; git diff --check PASS.
No web change/build/restart required, actual hydrated UI smoke PASS.

FIX attributable: PI source GET 5; shared R1 cumulative 6/10; MaximoGET 0;
source business writes 0/0; new mappings/additional verify 0; persisted approval 1,
duplicateapproval rejected 1; latest evidence inserted 1 and projection state 1 in
one accepted batch; replay writes 0/sourceGET 0. API replacement 1, web/collector/
scheduler/DB restarts 0. DDL/init/grant changes 0; history/backfill 0; AF-wide
crawl 0; registry mutation 0; reset/truncate 0; volume recreation 0; new operational
DB 0; CEMS/NK changes 0; credential exposure 0. Transient administrative env is
removed; backup, trusted plan, handoff and aggregate audits remain private 0600.

### Remaining acceptance

Bounded Coal Feeder A identity, signal approval, source canary, controlled
projection and real replay are COMPLETE/ACCEPTED. Phase 1 stays CURRENT/PARTIAL;
product acceptance is NOT PASS pending defensible freshness policy and the
remaining reviewed operating/refresh acceptance. Other asset identities are
not authorized by this pilot. No continuous projection scheduler, expanded
signals, unit normalization, ML/PdM score or alarm is introduced. Next approve
policy/controlled refresh procedure and rerun readiness without weakening gates.

Final close audit 2026-10-08T05:13:30Z (12:13:30 Jakarta): all container identities
unchanged since the single API replacement; mappings0 PROPOSED/1 VERIFIED and
condition selection/latest/state1/1/1 remain exact. PI completed a post-promotion
normal worker cycle at05:08:03.416276Z, 433/433/errors0; Maximo bounded incremental
05:10:07→05:10:17Z:25 seen/0 upserted/25 skipped/errors0. Cursor04:58:27Z and
recovery floor unchanged. Minimal transient writer env removed; runtime image pin,
private backup/trusted handoff/audits retained. No additional source canary issued.
