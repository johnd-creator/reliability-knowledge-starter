# NADI-P1-FRESH-001A — freshness engineering decision package

**Proposal only. All proposed thresholds: PROPOSED — NOT YET APPROVED.**
No production policy, source request, selection, mapping or evidence changed.
Phase 1 remains CURRENT/PARTIAL; product readiness remains UNKNOWN.

## Baseline and documentation authority

GitHub main and merged PR22 resolve to `478cce1958ab5800ce21d7b1e93b83ff43c1ac19`.
This policy branch starts directly there. [PR23](https://github.com/johnd-creator/reliability-knowledge-starter/pull/23)
is the separate documentation-only runtime reconciliation, head
`b08a4fda7a991a7c980d913e6d7de04a653f54a4`, four Markdown files. Review/merge
that checkpoint before this proposal; this PR references it rather than copying
its runtime acceptance patch. Neither PR is auto-merged.

Serving Cockpit API image revision is the reviewed main SHA, image ID
`sha256:130e57ae05f650fef7472b2d41c1968c744e0c0b83aa5480fce882f50d218c57`.
The imported canonical model SHA256 is
`81561d968655116f280ec60f238f8fac961570de0d6e8adc84d60f39a0a0b612`.
The control checkout remains `0c800dac1da6ef863afdb193021176fe7feac073`;
its SHA and container's historical Compose label are not the running image SHA.
The seven accepted Compose files, existing image pin and private `.env.platform`
authority remain unchanged. PI worker, Maximo worker and projector were not restarted.

Operational Mart is `maximo-db/maximo_collector`, legacy Cockpit DB is separate,
and PI store remains `pi-db/pi_collector`. `nadi_mart_reader` remains SELECT-only.
Production inventory: 845 registered assets; 11,845 asset_master; 69,635 maintenance
records; 113,902 work orders; mapping PROPOSED=0 / VERIFIED=1; approved signals=1;
condition latest/state=1/1. PI inventory is 490 total / 433 active / 433 snapshots;
133,570 retained history rows. These are observations, not approved full-plant coverage.

## Bounded operational evidence

Audit measured 2026-10-08 05:31–05:35 UTC (12:31–12:35 Asia/Jakarta).
SQL queries read local stores only. Docker logs were reduced to timestamped,
numeric/status aggregates; no raw business descriptions or source payloads are
published. Samples are bounded and do not establish a long-term service SLA.
P95 for run intervals/durations uses nearest rank; snapshot lag P95 uses SQL
continuous percentile. No new historian/source requests were issued.

| Pipeline / sample | Configured pause | Actual cadence seconds: min / median / P95 / max | Duration / errors |
|---|---:|---|---|
| Maximo WO, last 120 attempts, 2026-10-07 19:14:58 to 2026-10-08 05:31:12 UTC | 300 s after command completes | start-to-start 305.046 / 309.355 / 317.999 / 333.398 (119 intervals) | duration 4.097 / 8.478 / 16.552 / 32.357 s; 118 successful, 2 partial/error attempts |
| Mart, 125 bounded JSON completion reports, 2026-10-07 19:06:24 to 2026-10-08 05:30:05 UTC | 300 s after projector completes | completion-to-completion 301.614 / 301.758 / 302.055 / 302.275 (124 intervals) | 125 COMPLETE reports; exact per-run acquisition/start duration is not recorded here |
| PI technical snapshots, last 64 recorded runs, 2026-10-07 14:54:15 to 2026-10-08 05:22:23 UTC | 300 s after acquisition completes | start-to-start 774.410 / 796.254 / 876.110 / 1292.292 (63 intervals) | duration 474.394 / 497.083 / 576.098 / 992.280 s; 59 complete 433/433 successes, 5 error runs |
| Coal Flow A source → one accepted handoff | No recurring condition refresh | one observation only | source-to-collection 5.721295 s |
| Coal Flow A collection → Mart | No recurring condition projection | one projection only | collection-to-projection 89.217170 s; end-to-end 94.938465 s |

Maximo's post-command pause measured median 301.002 s; PI's median 300.015 s.
The accepted Maximo override polls only WO; it is not the repository's broader
operational/asset scheduling loop. No recent automatic asset acquisition cadence
is asserted from that WO loop. Mart asset projection success means it projected
stored assets, not that Maximo assets were recently reacquired.

An additional bounded seven-run window explains the misleading 1669.914 s gap
between **successful** Maximo starts at 18:52:42 and 19:20:32 UTC: four partial
attempts intervened. There was no proof of a 27.8-minute scheduler pause. The main
120-attempt table includes partial runs; a separate success-only sample must not
be represented as all attempts. The smaller 612.679 s success gap likewise
contains a partial run. Latest WO attempt completed 05:31:12 UTC, errors=0.
Cursor at first audit was 05:19:49 UTC; the recovery floor remains
2026-08-21 03:56:54 UTC, exactly one recovery-floor record.

PI error runs had 1, 17, 1, 104 and 1 errors respectively; they collected
432, 416, 432, 329 and 432 of 433 attributes. Recent complete success was
05:13:03.431737 → 05:22:23.756495 UTC. Across 59 complete successes,
completion-to-next-success intervals have median 810.178 s, P95 1564.414 s,
maximum 2072.348 s (58 intervals). Start-to-start cadence is **cycle duration +
post-cycle pause**, not a fixed five-minute acquisition schedule. An in-progress
cycle can update snapshots before its completed run is visible in the ledger;
latest ledger attempt is not a claim that no acquisition is currently running.

### Timestamp / lag inventory and limits

At 05:32:36 UTC, PI snapshots had source timestamps from Unix epoch to
05:32:31.910919 UTC, collected times from 05:18:45.898903 to 05:32:35.318585 UTC.
433/433 timestamps are present, 54 are epoch-range (≤1970-01-02), future count=0,
bad-quality signals=18, unknown Good flags=0. Source-age-at-collection min=0.064675 s,
median=3.392506 s, P95≈1,791,436,804 s, max≈1,791,437,555 s. The upper tail reflects
non-current source timestamps, not slow collector acquisition. This technical
inventory cannot determine a Coal Flow A SLA or govern all 433 attributes.

Maximo asset source-update range: 2023-08-24 07:50:03 → 2026-10-01 05:40:10 UTC,
missing=0. Maintenance source-change range: 2014-07-08 02:51:54 →
2026-10-08 05:19:49 UTC, missing=0. These dates describe business changes and may
be old on unchanged equipment; they do not measure acquisition health.
A watermark-to-finish lag is a changed-record-tail proxy only. Its large idle
values cannot establish source transport latency or an SLA. Collector rows do
not record per-equipment acquisition timestamps sufficient to compute that lag
independently. Mart projection ledger holds current state, not an attempt history;
completion reports establish cadence but not per-record source-to-projection lag.
Both canonical projector states succeeded at 05:30:05 UTC; maintenance watermark
was 05:19:49 UTC (~617 s earlier), asset watermark was 1 October. Neither watermark
is substituted for projector success. Missing source_changed_at in these Mart
populations is zero; absent historical attempt/start timestamps remain unknown.

Accepted pilot source time is `2026-10-08T05:01:15.404006Z`, collected time
`2026-10-08T05:01:21.125301Z`, projected time
`2026-10-08T05:02:50.342471Z`, NUMERIC / `Ton/h`, Good=true, Questionable=false,
Substituted=false, Annotated=false. Quality does not establish equipment health.
`collector_last_success_at=null` remains untouched. A bounded lookup of 64 newest
**already stored** technical history timestamps for the exact Coal Flow registry
ID found 16–18 August data, last collection 18 August; it does not describe the
current October refresh distribution. No values/history were fetched from PI.
The one accepted October canary cannot establish variability or stale tolerance.

Both DB sessions report UTC. Source/handoff times include timezone offsets;
ISO `Z` and `+00:00` identify the same instant. Host and sequential DB observations
agree within query execution latency; this is a sanity check, not a certified NTP
error bound. Asia/Jakarta is UTC+7; do not reinterpret UTC source times as local
wall time. Future clocks fail closed; no undocumented skew allowance is adopted.

Private evidence is under ignored `secrets/nadi-p1-freshness-001a/` (directory 0700,
files 0600): `before.json`, `measured-summary.json`, `cadence-refined.json`,
`maximo-all-attempts.json`, `pi-runs.json`, `pi-snapshots.json`,
`mart-observation.json`, `pi-success-intervals.json`, plus final preservation proof.
Only aggregates and identity-safe conclusions are in Git; private DB evidence is
not an application configuration source. The initial success-only Maximo sample
is retained for audit, superseded for cadence by the all-mode sample above.

## Canonical timestamp contract and readiness

| Timestamp | Meaning / authority | Consumer and gate |
|---|---|---|
| `source_timestamp` | Time the source assigned the measurement; nullable, immutable in replay | condition SOURCE freshness; P1-CONDITION-PROJECTION-READY checks it independently of quality |
| `collected_at` | When Collector-owned adapter obtained that specific evidence; not worker success | immutable handoff ordering, older-batch protection; never fills a missing collector completion |
| `collector_last_success_at` | Explicit nullable collector success in handoff/state | ConditionQueryService collector dimension; current CLI leaves it null; query must remain COLLECTOR_UNKNOWN even while global PI is current |
| `projected_at` | Writer's completion time on newly accepted latest evidence | condition PROJECTION freshness; identical replay does not advance it |
| `projection_attempted_at` | Conceptual attempted time; actual column is `condition_projection_state.attempted_at` | currently max evidence collected_at, or writer clock when there is no evidence; **not** actual projection-start time or last successful refresh |
| pipeline `last_success_at` | Per-pipeline successful completion from its accepted ledger | Maximo WO finished_at with errors=0; PI snapshot finished_at with errors=0, not aborted, 433/433; Mart minimum of BOTH asset/maintenance last_success_at |
| operator refresh attempt / success / failure | Future private append-only operation journal, distinct from canonical measurement | needed to observe refresh execution and failures before handoff/project; cannot retrospectively fill accepted null metadata |

Gate P1-MAXIMO-CURRENT currently covers accepted WO collection, cursor existence
and latest errors, not an assertion about every Maximo resource. P1-MART-CURRENT
uses both factual projection success times and status. P1-PI-COLLECTOR-CURRENT
uses technical complete collection time and coverage/errors, not oldest source
measurement. Governance/schema/status gates remain independent. Identity and
selection readiness remain independent of freshness. Condition projection
requires coverage, source CURRENT, projection CURRENT, acceptable quality and
no degraded state; simply configuring a threshold cannot make it PASS.
Global PI collector success is separate from an asset handoff's nullable success.
Current global projection gate does not require the per-handoff collector field
to become non-null; that unknown dimension must continue to be displayed honestly.

Canonical typed transport rejects invalid/unzoned timestamps. Future aware
timestamps yield UNKNOWN; future collection is rejected at projection. Epoch
source is STALE under a defensible bounded threshold, UNKNOWN with blank policy;
it must never be declared valid/current by selecting a huge threshold. A future
refresh must check source ≤ collected ≤ projection clock where source exists;
clock contradiction stops acceptance and records UNKNOWN/clock investigation.
The current read model assesses source and projection ages independently; it
has no universal chronology-integrity rejection for a stored projected_at older
than source within both allowed windows. That integrity guard belongs in the
reviewed refresh preflight / subsequent scoped runtime correction, not a claim
that the current age-only model enforces chronology in every case.

## Proposed policy matrix — PROPOSED — NOT YET APPROVED

These are initial **operational monitoring** proposals, not contractual equipment
SLAs. CURRENT means age ≤ approved threshold; STALE means age > threshold. Failure,
unknown timestamp, coverage and quality can still make an overall gate PARTIAL /
UNKNOWN / BLOCKED even inside the CURRENT window. No green state is manufactured.

| Dimension | Proposed CURRENT / STALE boundary | Evidence and tolerance | Approval owner |
|---|---|---|---|
| Maximo WO acquisition | ≤660 s / >660 s since last successful WO completion | 2 × attempt P95 317.999 =635.998 s, rounded upward to an 11-minute monitoring allowance; permits one missed nominal cycle, flags sustained four-failure episode; latest error remains degraded immediately | platform/Maximo operations owner with reliability engineer acknowledgement of WO-only scope |
| Reliability Mart factual projection | ≤660 s / >660 s for BOTH projector success times | 2 × observed completion max 302.275 =604.551 s plus ~55 s monitoring margin; failed projector status still degraded immediately; no evidence of failure-tail distribution | platform/Mart owner and reliability data engineer |
| PI technical collector | ≤1800 s / >1800 s since last complete 433/433 success | 2 × start P95 876.110 =1752.220 s, rounded to 30 minutes; success-gap P95 1564.414 fits, observed max 2072.348 exceeds and should be stale; avoids fixed-five-minute assumption | PI/historian operations owner and platform owner |
| Coal Flow A source measurement | **POLICY_EVIDENCE_INSUFFICIENT — leave blank / UNKNOWN** | one live accepted age 5.721295 s; no current repeat distribution, compression/deadband/sample cadence or allowable evidence-use age approved; generic 433-signal distribution is not applicable | Boiler/instrumentation responsible engineer for this signal, project owner approves intended use |
| Coal Flow A condition projection | **POLICY_EVIDENCE_INSUFFICIENT — leave blank / UNKNOWN** | one latency 89.217170 s; no recurring service, run budget or repeat latency distribution; manual snapshot must not look continually current | reliability integration/runtime owner jointly with project owner |

The 660 / 660 / 1800 s values are **PROPOSED — NOT YET APPROVED**. Sample covers
roughly 10–15 hours, not representative long-term outages. Rounding and one-missed-
cycle tolerance are explicit proposed engineering choices, not measured SLAs.
Approve/reject/revise that tolerance, gather longer local ledger samples including
failures and peak workloads, and timebox review after controlled acceptance.
Normal PI acquisition can exceed a nominal cycle; last successful completion,
not last attempt or updated partial snapshot, determines acquisition freshness.
Bad quality and epoch timestamps stay separate from that worker activity.

Missing success/source/projection time → UNKNOWN. Invalid transport time → reject
handoff, preserve prior evidence and record failure. Future → UNKNOWN/clock
investigation, no tolerance silently applied. Delayed worker cycle never extends
last_success_at; long cycle crossing the threshold is STALE even if still running.
Recovery requires a real complete success; cursor presence or retry attempt does
not restore freshness. No source-rate reduction, parallel polling or expedited
retry is authorized by these proposed monitoring thresholds.

### NORMAL / DELAYED / MISSED_CYCLE / RECOVERY

| Scenario | Acquisition / Mart interpretation | Condition interpretation |
|---|---|---|
| NORMAL | Last successful completion within approved component window and error-free, complete coverage; neutral policy still UNKNOWN today | one approved signal, valid chronology, acceptable quality; CURRENT only with individually approved source/projection policies |
| DELAYED | Last success age still used; within window can remain CURRENT but latest error degrades; exceeding window STALE even while active | old accepted value remains visible with original times; no synthetic timestamp advancement |
| MISSED_CYCLE | Proposed Maximo/Mart windows tolerate one nominal missing cycle; repeated misses exceed window. PI window tolerates approximately one normal failed cycle, not all observed outage tails | absent/no new handoff cannot prove refresh; failed handoff marks degraded, keeps old evidence; policy still UNKNOWN where unset |
| RECOVERY | Only real complete success restores acquisition/Mart freshness; backlog/quality/coverage remains independently checked | fresh source + newly accepted projection may restore those dimensions; replay of an old handoff cannot restore freshness; a successful bad/null sample remains bad/unknown |

### Configuration implementation gap

Current `FreshnessPolicy` has only three shared environment values:
`NADI_COLLECTOR_MAX_AGE_SECONDS` (Maximo and PI),
`NADI_SOURCE_MAX_AGE_SECONDS` (technical PI aggregate and selected condition source),
`NADI_PROJECTION_MAX_AGE_SECONDS` (Mart and condition projection).
No five component-specific knobs exist. Setting collector=1800 would silently
relax the proposed Maximo 660; setting projection=660 would invent an unapproved
condition projection policy. **Do not configure the proposals with these shared
knobs.** Production all three stay blank. NADI-P1-FRESH-001B needs a reviewed,
backward-compatible per-component policy selection before activating distinct
values, preserving blank/default UNKNOWN and legacy explicitly configured policy
compatibility. Gate/model/UI contracts must agree; no universal PASS shortcut.
The source/projection blank prerequisites remain unresolved even if acquisition
monitoring thresholds are approved. Chronology anomaly handling and a truthful
refresh-attempt journal also require explicit implementation/acceptance then.

## Manual controlled refresh acceptance design (not executed here)

Scope pinned to existing Coal Feeder A canonical asset
`asset:MAXIMO:MXASSET:BSR:IP:CS10HFB01AF001-001`, mapping
`nadi-map-a8c71ce66757ea9de50c21de3d8fd18b`, signal
`nadi-signal-coal-flow-a-20261008`, semantic `coal_flow`, Fauzi approval reference
`NADI-SIGNAL-COAL-FLOW-A-20261008`, one exact approved 203-character Attribute.
No mapping/selection mutation is in this workflow. Preserve `Ton/h`; no unit
normalization, historian, fuzzy discovery or technical registry promotion.

Use a reviewed release containing the canonical commands below. The existing
accepted private handoff is a frozen identity/approval comparison baseline,
SHA256 `76f871f2993f17d8635ac852a56a3593c8cb0a129d97910845f37bd14398bd8e`;
never rewrite it or reuse its output path. Every run has a new private 0700 folder
and exclusive 0600 plan, handoff and journal artifacts. Capture actual UTC start,
completion, outcome, phase, plan/handoff hashes, GET count, projection result and
pre/post latest-row timestamps, without process values, credentials or raw errors.
Keep last acquisition success, last newly accepted projection success and last
failure separately; identical replay is not a new evidence success.

Executable canonical command sequence, **only after NADI-P1-FRESH-001B separately
authorizes the controlled run**:

```bash
# Hold one host-local asset lock for the whole plan → collect → project → audit.
# All refresh entrypoints on this runtime host must use this SAME private lock.
umask 077
exec 9>"$PRIVATE_OPERATIONS_DIR/coal-feeder-a.refresh.lock"
flock -n 9 || exit 75
# RUN_DIR is a newly created exclusive private directory, never the old pilot dir.
# Admin and collector commands run in separate operator contexts as below.
cockpit condition plan --asset-id \
  'asset:MAXIMO:MXASSET:BSR:IP:CS10HFB01AF001-001' --output "$RUN_DIR/plan.json"
# STOP unless canonical plan equals frozen accepted plan, with exactly one signal.
# Validate with ProjectionPlan + JSON schema and compare full lineage/approval.
picollector condition-evidence --plan-file "$RUN_DIR/plan.json"
# Above is the collector dry-run: validates the whole plan, makes zero source GETs.
picollector condition-evidence --plan-file "$RUN_DIR/plan.json" \
  --execute --output "$RUN_DIR/handoff.json"
# Validate all canonical schemas + EvidenceBatch; inspect collected/failure count,
# chronology and budget BEFORE writer transaction; never edit the source handoff.
cockpit condition project --file "$RUN_DIR/handoff.json"
# Project rechecks current governance inside the locked DB transaction.
# Read API and readiness, capture result. Keep lock until journal finalized.
cockpit phase1-readiness
```

These commands are a sequence across **two separate security contexts**, not a
shell that exports PI credentials to Cockpit. The plan/project/admin processes
use `COCKPIT_CONFIG_MODE=managed`, the existing private
`RELIABILITY_MART_ADMIN_DATABASE_URL` and expected owning DB identity; the query
process uses SELECT-only `RELIABILITY_MART_DATABASE_URL`. The Collector-owned
process alone uses `PI_CONFIG_MODE=managed` and the explicit accepted PI source
configuration derived from `.env.platform`; never copy source credentials into
Cockpit/API environment. Do not source an entire credentials file into a shared
shell. Use isolated short-lived operator containers or scoped process environments;
no worker/API restart, no new DB, no new collection daemon. Do not print private
environment values or command exceptions containing credentials.

The lock must remain held by a coordinator across both child contexts, not be
released between manual shells. The recipe's variables, trusted command contexts,
frozen-plan check, chronology check and journal are **implementation/acceptance
preconditions for 001B**, not a claim that a runner/scheduler was deployed here.
`flock` prevents overlap on this single host only; moving to multiple hosts needs
a reviewed distributed/advisory lease. Existing Mart transaction locks and plan
revalidation protect governance changes, but do not alone prevent two overlapping
source acquisitions. A future runner must test contention before real requests.

One selected signal uses at most **5 guarded PI business GETs per attempt**:
Element → Database → exact Element's bounded direct attributes → exact selected
Attribute → current value. Instrument a fail-closed per-run counter at the
Collector request boundary, reject non-GET/history paths; preserve ≥1-second
spacing, origin/TLS/response-size controls and direct-attribute bounds. No
pagination, other attributes or parallel polling. If adapter changes would exceed
budget, stop before execution; do not grow scope. No automatic retry in manual
acceptance. A separately authorized second attempt must export/recheck a fresh
trusted plan and has its own five-GET budget and journal.

Complete, schema-valid collected evidence may include BAD_QUALITY, NULL or stale
source time: preserve exact type/unit/time/flags and classify separately, never
coerce to zero or healthy. Missing source remains UNKNOWN. A source failure may
produce a valid SOURCE_UNAVAILABLE batch; project that **only within the future
run's authorization** to record degraded attempt, retaining the previous latest
row/projected_at. Schema/clock/governance failures stop before write and are
observable in private journal; current canonical state alone cannot observe those
pre-project failures. Collector handoff success metadata remains null unless a
separate explicit source contract supplies true worker completion. Do not patch
it with collected_at or the global observation after the fact.

After a successful future run, replay that SAME accepted handoff locally:
written=0, no extra PI GET, no timestamp/selection/row-count change. Compare full
latest row and state before/after; no advance of projected_at/attempted_at on
identical replay. A different payload at the same collected_at must reject; older
batch ignores. On source failure do not fall back to a new discovery or cached
value relabelled as fresh. On writer failure keep the private accepted handoff,
recheck governance and retry projection locally without new source calls; if
governance changed, reject and require review instead of bypassing the gate.

## Future recurring operation (not enabled)

A recurring runner requires separate approval of purpose, cadence, request budget,
source/projection thresholds, responsible operator, operating hours, failure
alerts and host/lease scope. It must schedule **completion + approved pause** or
explicit skip-on-overrun semantics, never overlapping catch-up runs. No proposed
numeric refresh cadence is justified from this single October observation.
One attempt consumes ≤5 business GETs; no history. Backoff and retry ceiling must
be approved before automation; manual mode currently has no auto retry. The
runner must retain accepted source/projection times on failure, journal phase and
last success/failure, re-export plan per attempt and stop on retired/conflicting
identity/selection. Technical worker remains independent; no piggyback projection
of all 433 attributes. This task installs no timer, cron or service.

## Synthetic regression and engineering decision

`tests/test_freshness_governance.py` adds 14 isolated cases: CURRENT boundary,
STALE, blank/missing UNKNOWN, epoch, future, equivalent UTC+7 instant, missing
handoff collector success despite recent collection/global worker, invalid/unzoned
transport times, Good-stale, Bad-fresh, source newer than stale projection,
identical replay and failed refresh preserving accepted evidence. Configured
thresholds do not override missing timestamps or quality/degraded state.
SQLite fixtures use synthetic governance and a hermetic Collector subprocess;
existing PostgreSQL acceptance covers canonical transaction/reader semantics.
The older-projection test proves age dimensions remain independent; it does not
claim arbitrary chronology anomalies are already rejected by the stored reader.
Tests modify no production mappings or evidence. Full commands/counts are
recorded in the validation section below after execution.

Required human decision package:

1. Platform/Maximo/Mart/PI owners approve/reject/revise proposed 660 / 660 / 1800 s
   monitoring boundaries and explicit one-missed-cycle tolerance, scope and review
   window. **No such approval is claimed by this task.**
2. Boiler/instrumentation responsible engineer states source sampling/compression,
   intended pilot use and acceptable Coal Flow age; project owner approves it.
   Signal-use approval by Fauzi is not freshness/SLA approval by Fauzi or Hidayat.
3. Runtime owner establishes source-to-projection budget from repeat controlled
   refresh samples and latency/failure evidence; keep blank until defensible.
4. Review the per-component policy wiring / chronology / runner-journal gap before
   activation. Approve exactly one manual refresh under 001B; decide recurrence
   separately after its evidence. Neither approval is implied here.
5. Keep PI_AF_KKS_LOOKUP_UNRESOLVED open and BFPT REJECTED/FROZEN/DO NOT VERIFY;
   neither issue is fixed by successful collection or by a freshness policy.

Next: **NADI-P1-FRESH-001B** — reviewed component-specific policy implementation,
explicit engineering decisions and separately authorized manual refresh acceptance.
No Phase1 COMPLETE claim is warranted while policies/refresh prerequisites remain.

## Validation and final preservation evidence

Final runtime audit: 2026-10-08 05:46:58 UTC (12:46:58 Asia/Jakarta).
All 23 existing containers retain identical IDs, image IDs, start times, restart
counts, mounts and networks; all 18 running services continue normally. Private
platform configuration hash, all reader privileges and Mart/PI migration ledgers
are unchanged. Full condition latest/state JSON and timestamps, mapping and
selection hashes equal their pre-investigation records. Latest PI complete cycle
05:27:23.771159 → 05:36:10.912052 UTC collected433/433, errors0. WO cursor moved
05:19:49 →05:34:08 UTC through normal background acquisition; recovery floor and
its single ledger record remain intact. Factual API registry/overview return200.
No condition refresh, replay, DDL or policy activation was executed on production.

Actual nine gates: MAXIMO, MART and PI-COLLECTOR UNKNOWN / UNKNOWN_FRESHNESS_POLICY;
GOVERNANCE, CONDITION-SCHEMA and INTEGRATION-STATUS PASS / compatible schema and
valid contract; IDENTITY PASS / VERIFIED_PILOT_AVAILABLE; SIGNAL-SELECTION PASS /
APPROVED_PILOT_SIGNALS_AVAILABLE; CONDITION-PROJECTION UNKNOWN /
UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS. Overall UNKNOWN; normal CLI exit0,
`--require-pass` exit2. Test thresholds are not runtime thresholds.

Commands run from the respective component in the policy worktree:

```bash
# reliability-cockpit: host venv, SQLite/mocks; Compose config checks opted in.
DATABASE_URL=sqlite+pysqlite:///:memory: \
PYTHONPATH=/tmp/nadi-phase1-host-testdeps NADI_COMPOSE_TESTS=1 \
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
-m unittest discover -s tests
# 272 discovered: 209 PASS, 63 opt-in integration skips; 14 new hermetic cases pass.

# pi-collector: hermetic full regression.
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python \
-m unittest discover -s tests
# 177 discovered: 166 PASS, 11 optional integration skips.

# reliability-data-contracts: canonical models/schemas.
PYTHONPATH=/tmp/nadi-phase1-host-testdeps \
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python \
-m unittest discover -s tests
# 14 PASS.
```

Disposable PostgreSQL fixture: postgres16.4-alpine, tmpfs data, `--network none`,
database `nadi_governance_test`, fixture-only user/password. Each test runner used
`--network container:nadi-fresh-governance-pg`, a read-only worktree mount and the
already established `nadi-phase1-acceptance-test:local` image. No route to the
operational Compose network. Test commands ran sequentially against that fixture:

```bash
# Common runner used for each pattern below:
docker run --rm --network container:nadi-fresh-governance-pg \
-v /home/john-d/.codex/worktrees/nadi-p1-freshness-governance/reliability-knowledge-starter:/workspace:ro \
-w /workspace/reliability-cockpit \
-e DATABASE_URL=sqlite+pysqlite:///:memory: \
-e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test \
-e RELIABILITY_MART_MIGRATIONS_ROOT=/workspace/reliability-cockpit/migrations \
nadi-phase1-acceptance-test:local python -m unittest discover -s tests \
-p test_freshness_governance.py -v
# 23 PASS: 14 hermetic +9 PostgreSQL-backed cases.
# Same runner, -p test_mart_migrations.py: 18 PASS.
# Same runner, -p test_condition_evidence.py: 51 PASS (SQLite + PostgreSQL).
```

The initial new PostgreSQL fixture failed because the existing migration fixture
has deliberately minimal projector anchors, lacking last_status/last_success_at.
The new test-only setup now adds those consumed columns to the disposable fixture;
all cases pass. No application or operational-schema repair was needed. Repeated
SQLite cases across runner commands are repetitions, not additional unique cases.
ResourceWarning messages from existing test fixture connections are not failed
assertions. Optional Timescale/API integration skips are disclosed; no PI storage
or application implementation changed in this task. Fixture containers are removed
at completion. `git diff --check` passes for both policy and docs branches.

Task-attributable production PI/Maximo business GETs=0, source writes=0, mapping
imports/verifications=0, signal approvals=0, condition projections=0, history/
backfill=0, AF discovery=0, registry changes=0, DDL/reset/truncate=0, volume
recreation=0, service restarts=0, policy/env changes=0, scheduler activation=0,
CEMS/NK changes=0. Normal background collection is separate and remains enabled.
