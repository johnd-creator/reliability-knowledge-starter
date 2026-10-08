# NADI-IDN-002B — Coal Feeder A human-reviewed pilot

Evidence reference: `NADI-IDN-002B-COAL-FEEDER-A-20261008`.
Baseline: main `1df5b96914db7bae9ad1b836489fe1c39202ed02`, PR21 MERGED;
branch `codex/nadi-idn-002b-first-verified-asset`. Runtime uses accepted c2fb0fc
consumer images and historical control checkout 0c800da with preserved overrides.

Current R1 verdict: **PARTIAL — CODE_ACCEPTANCE_REQUIRED**. Direct Fauzi signal
approval is RECEIVED; production selection/canary/projection remain blocked by
the merged 200-character Attribute-reference limit. See the R1 checkpoint below.
The first-round observations and pending statements below are historical.

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
