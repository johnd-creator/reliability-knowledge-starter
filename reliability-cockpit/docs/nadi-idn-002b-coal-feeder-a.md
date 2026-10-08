# NADI-IDN-002B — Coal Feeder A human-reviewed pilot

Evidence reference: `NADI-IDN-002B-COAL-FEEDER-A-20261008`.
Baseline: main `1df5b96914db7bae9ad1b836489fe1c39202ed02`, PR21 MERGED;
branch `codex/nadi-idn-002b-first-verified-asset`. Runtime uses accepted c2fb0fc
consumer images and historical control checkout 0c800da with preserved overrides.

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

