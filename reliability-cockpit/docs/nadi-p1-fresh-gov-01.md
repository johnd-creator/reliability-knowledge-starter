# NADI-P1-FRESH-GOV-01 — engineering freshness decision package

## Current owner decision — GOV-02

**PROJECT_OWNER_APPROVED** on 8 October 2026: Fauzi approved 660/660/1800 seconds
for provisional monitoring and keeping both condition policies UNSET.
**COMPONENT_ENDORSEMENT_PENDING / ACTIVATION_NOT_AUTHORIZED.**
[Current decision and approval register](nadi-p1-fresh-gov-02.md) records the
conversational provenance, date-only expiry limitation, pending reviewers and
prepared GOV-03 gates. Historical PENDING recommendations below are preserved
as the GOV-01 checkpoint; they do not negate the later owner decision. Numeric
condition policies remain deferred and all eight production settings remain UNSET.

## Historical GOV-01 decision package

**Decision package: PASS / ready for owner review. Approval: PENDING.**
Proposal date: 8 October 2026. Production policy activation: **NONE**.
Phase 1 remains **CURRENT/PARTIAL**, actual readiness **UNKNOWN**.

## Release and accepted R3 baseline

Latest fetched `origin/main`, PR26 reviewed merge, and clean serving release:
`1cf7fed971594581913e8e7f635691f834133b6e`.
Documentation branch: `codex/nadi-p1-fresh-gov-01`. The original control workspace
remains `0c800dac1da6ef863afdb193021176fe7feac073`; its existing untracked
`23496711.xls` is preserved. No deployment or application change is part of this
package. R3 operational records are stronger evidence than older roadmap labels.

Actual local Mart: `maximo-db / maximo_collector`. Registry=845, VERIFIED=1,
PROPOSED=0, approved `coal_flow` signal=1, latest evidence=1, projection state=1.
Coal Feeder A: `asset:MAXIMO:MXASSET:BSR:IP:CS10HFB01AF001-001`.
Mapping `nadi-map-a8c71ce66757ea9de50c21de3d8fd18b` remains uniquely VERIFIED /
PRIMARY_EQUIPMENT / CENTRAL_PI; signal `nadi-signal-coal-flow-a-20261008` remains
approved. Hidayat reviewed equipment identity; Fauzi approved signal use under
`NADI-SIGNAL-COAL-FLOW-A-20261008`, at `2026-10-08T04:07:10.208836Z`.
Neither action is a freshness-policy approval.

R3's existing owner authorization was consumed by its successful five-GET
acquisition. Its receipt reports ACCEPTED/written1; existing strict replay reports
REPLAYED/GET0/written0. Full latest/state JSON, governance fingerprints, original
handoffs and historical journal are preserved by this task. **No acquisition or
replay was repeated.** Collector success in the pilot state remains NULL.
`PI_AF_KKS_LOOKUP_UNRESOLVED` stays open; BFPT remains
**REJECTED / FROZEN / DO NOT VERIFY**.

## G02 — observed operating evidence

Observation cut: `2026-10-08T13:48:16.203800Z` (20:48:16 Asia/Jakarta).
All SQL used explicit READ ONLY transactions. Queries selected up to2000 local
run rows started within24h; returned counts below do not hit the cap. WO ledger
mode inventory contains273 incremental and5 partial rows; both are included.
No failure rows were excluded to manufacture normal cadence. P95 is nearest rank.

| Dimension and exact source | Window UTC / sample | Median / P95 / maximum seconds | Failure evidence |
|---|---|---|---|
| Maximo WO: `collect_run`, `object_structure=mxwodetail`, modes incremental/partial | 7 Oct13:50:10.177859 →8 Oct13:44:40.496634;23.9084h;278 attempts,273 successes | starts309.564 /317.999 /369.082; success completions309.614 /317.200 /1642.565; duration8.541 /17.020 /68.051 |5 partials; four consecutive errors18:58–19:15 UTC;1 of272 success gaps>660 |
| Factual Mart: `docker logs --timestamps --since 24h …-mart-projector-1`, parsed COMPLETE envelopes containing both explicit projector keys | 7 Oct13:49:34.519845 →8 Oct13:48:12.281423;23.9772h;287 reports,286 intervals for each key | completion reports301.778 /302.136 /302.873 |0 partial reports; no unfinished parsed envelope or stderr lines at cut |
| Technical PI: `pi_collect_run`, `scope=snapshot`, complete=finished/errors0/not aborted/attributes_seen=rows_collected=433 | 7 Oct14:01:13.873033 →8 Oct13:33:10.902851;23.5325h;104 attempts,99 full successes | starts818.032 /872.254 /1292.292; successful completions821.151 /1561.229 /2072.348; duration518.232 /572.239 /992.280 |5 partial/error cycles; maximum consecutive failed cycles1;1 of98 success gaps>1800 |

Maximo attempts pause after command completion: median301.021s. Actual worker
command is `mxcollector sync mxwodetail; sleep 300` in a loop. The four-error
episode explains the long *success* gap; it is not a27-minute polling pause.
Zero new/changed rows can be a successful WO poll; the business-change watermark
does not become a transport/acquisition timestamp.

Mart runs `mart-project --incremental`, then configured sleep300. Each complete
envelope includes `asset_master` and `maintenance_event` with completed=true.
The two log distributions share the envelope completion timestamp, **not separate
per-projector start/end histories**. Current canonical states independently show
SUCCEEDED at13:48:11.816283 and13:48:12.110575 UTC. Gate evaluation requires both
states' actual success timestamps, with either missing, stale or failing preventing
PASS. No historical projector-failure distribution or per-record latency is
available from this rolling state table; no inference from zero observed errors.

Technical PI uses the existing leased snapshot owner with legacy
`--interval-seconds` meaning post-cycle pause. Measured median pause300.015s;
effective acquisition starts equal cycle duration plus pause, approximately
818s median, not a fixed five-minute cadence. Failed cycles collected432,416,432,
329,432 of433; errors1,17,1,104,1. A partial update must not advance full-success
freshness. The stored `requests_made` field in these older technical runs matches
collected rows and is not used here as a complete transmitted-HTTP audit.

Latest success at this cut: WO13:44:46.988804Z; PI13:42:00.148780Z.
An in-progress background cycle may update individual snapshots before its ledger
completion appears. Normal background work is separate from task operations.

### Quality, timestamps and limitations

PI local inventory490 total /433 active /433 snapshots;54 source timestamps in
epoch range≤1970-01-02;18 bad-quality signals (Good=false or Questionable=true),
0 future timestamps,0 missing source timestamps,0 unknown Good flags. Oldest
source1970-01-01; newest source13:48:11.342010Z and collected13:48:15.690305Z.
These are inventory-level anomalies, not a Coal Flow freshness threshold.
Worker completion cannot make these source measurements current or healthy.

Maximo stored asset source-update range2023-08-24 to2026-10-01; maintenance
source-change range2014-07-08 to2026-10-08T13:10:03Z; no nulls at cut. Recent WO
polling does **not** establish current acquisition of every Maximo asset record.
Mart reprojection of old stored asset data does not establish source currentness.
WO cursor13:10:03Z and the one existing recovery-floor record
2026-08-21T03:56:54Z are retained, never used as freshness substitutes.

One day is not a long-term service SLA, seasonal/peak-load distribution, outage
probability estimate or certified clock bound. No outage cause was diagnosed from
error counts. Success-gap exceedance counts are events, not percentage of wall
time classified STALE. Failure tails, missing historical per-projector clocks,
per-asset acquisition clocks and source sampling/compression behavior are explicit
measurement limitations. Read-only observations are sequential, not one atomic
cross-database snapshot. Graph generation2026-08-24 lacks current freshness paths;
this assessment uses direct exact-release source and current runtime records.

## Historical G03 / G05 — five-policy proposal before owner decision

All values below are engineering **recommendations**, not approvals or SLAs.
Date proposed2026-10-08. Accountable project operator is Fauzi; component owner
endorsements and technical policy review must be recorded explicitly. Hidayat's
identity review does not imply he approved a signal SLA.

| Dimension / setting | Proposed value and scope | Evidence / tolerance trade-off | Recommendation / actual approval | Proposed owner and technical review | Review / expiry and rollback |
|---|---|---|---|---|---|
| MAXIMO_WO / `NADI_MAXIMO_WO_MAX_AGE_SECONDS` |660s, last successful WO completion only |2×start P95≈636s; normal success P95≈317s. Allows roughly one missed cycle; four-failure gap1643s should be STALE. Can delay stale detection to11min; tighter value may flag a tolerated missed cycle. Latest errors still degrade immediately |APPROVE FOR PROVISIONAL MONITORING / **PENDING** |Fauzi obtains Maximo operations owner endorsement; platform/reliability data engineer verifies WO-only scope |First24h and after72h; expires approval+7days unless reapproved; clear this setting on rollback |
| MART_FACTUAL / `NADI_MART_FACTUAL_PROJECTION_MAX_AGE_SECONDS` |660s, BOTH asset/maintenance projector successes |2×observed max≈606s plus54s proposed allowance. Tolerates one missed nominal cycle; no observed failure tails. A healthy projector can still reproject outdated source data, so acquisition gate stays independent |APPROVE FOR PROVISIONAL MONITORING / **PENDING** |Fauzi obtains Mart/platform owner endorsement; reliability data engineer reviews both-state requirement |First24h/72h, expires approval+7days; clear this setting on rollback |
| PI_COLLECTOR / `NADI_PI_COLLECTOR_MAX_AGE_SECONDS` |1800s, full433/433 success only |2×start P95≈1745s rounded to30min; success P95≈1561s fits, max2072s should be STALE. Allows an ordinary failed cycle; delays stale detection. Does not waive failed/partial cycles or18 bad-quality signals |APPROVE FOR PROVISIONAL MONITORING / **PENDING** |Fauzi obtains PI/historian operations owner endorsement; platform engineer verifies full-success observation |First24h/72h, expires approval+7days; clear this setting on rollback |
| CONDITION_SOURCE / `NADI_CONDITION_SOURCE_MAX_AGE_SECONDS` |UNSET, selected Coal Flow measurement only |Two manual source ages5.721295s/1.161323s; no cadence/deadband/use-age evidence. Numeric threshold risks false CURRENT for unsuitable evidence or false STALE for unchanged legitimate readings |DEFER / **DEFERRED; no numeric approval** |Project owner; responsible Boiler/instrumentation reviewer, Hidayat or explicitly delegated engineer |Revisit after controlled-source sampling/use-age assessment; leave UNSET |
| CONDITION_PROJECTION / `NADI_CONDITION_PROJECTION_MAX_AGE_SECONDS` |UNSET, newly accepted Mart evidence only |Observed delays89.217170s/0.101573s; first staged operator delay differs from coordinated R3. No recurrence or latency distribution; fast replay cannot restore freshness |DEFER / **DEFERRED; no numeric approval** |Project owner and reliability integration/runtime owner |Revisit with bounded approved refresh evidence and intended consumption age; leave UNSET |

Expiry is an operator obligation to remove/reapprove configuration, **not an
installed timer or automatic lease**. Owner review must name responsible people,
approval date, accepted monitoring tolerance, review/expiry timestamps and rollback
operator. Role suggestions are not evidence that a person has reviewed this matrix.

### Observation handling applies to every approval

| Observation | Required interpretation |
|---|---|
| Policy absent |UNKNOWN; no implicit inherited or cadence-derived policy |
| Success/source/projected timestamp missing |UNKNOWN; never replace with cursor, source changedate, collection time, current clock, worker activity or journal replay time |
| Invalid/unzoned transport timestamp |Canonical handoff rejects; preserve accepted evidence; do not activate a policy to mask failure |
| Future timestamp |UNKNOWN/clock investigation; no implicit tolerance or CURRENT |
| Age exactly threshold / greater than threshold |CURRENT / STALE respectively, only for that time dimension; errors/quality/coverage are independent |
| Failed/partial acquisition or projector |Retain prior successful time; failed attempt cannot reset age. Readiness PARTIAL/UNKNOWN as applicable |
| Bad or unknown quality |Preserve exact flags; does not mean HEALTHY, and condition acceptance cannot PASS when quality is not accepted |
| Epoch source time |With an approved age policy STALE; with UNSET policy UNKNOWN. Record anomaly independently; do not manufacture a production threshold |
| Identical replay |No new evidence timestamp or acquisition success; latest source/projection ages continue increasing |
| Unmapped/proposed/retired/ambiguous identity |No usable VERIFIED signal projection; no name-based promotion |

## G04 — two accepted Coal Flow observations

| Field, preserved UTC | First real accepted evidence | Accepted R3 |
|---|---|---|
| Value / type / unit |53.48906326293945 / NUMERIC / Ton/h |54.84218978881836 / NUMERIC / Ton/h |
| Source timestamp |2026-10-08T05:01:15.404006Z |2026-10-08T13:17:39.051010Z |
| Collected timestamp |2026-10-08T05:01:21.125301Z |2026-10-08T13:17:40.212333Z |
| Projected timestamp |2026-10-08T05:02:50.342471Z |2026-10-08T13:17:40.313906Z |
| Source age at collection |5.721295s |1.161323s |
| Collection → projection |89.217170s |0.101573s |
| Quality Good/Questionable/Substituted/Annotated |true/false/false/false |true/false/false/false |
| Collector success in handoff/state |NULL |NULL |

Both retain exact lineage,203-character Attribute identity, Fauzi signal approval
and GOVERNED_PI_SOURCE provenance. Source unit is not converted to`t/h`.
Elapsed time between manual *collection timestamps* is29779.087032s
(8h16m19.087032s). This is **not a scheduler interval or source sampling rate**;
the first acquisition start is not supplied by these two evidence rows. R3
STARTED13:17:27.852689Z, ACQUIRED13:17:40.307031Z, ACCEPTED13:17:40.328221Z
are journal events, distinct from measurement and evidence collection times.

The independently running technical worker has an exact-WebId local snapshot
for this same attribute at source13:41:39.441009Z / collected13:41:43.179070Z,
source age3.738061s, Good=true, remaining flags=false. This stored technical
observation is later than R3 but **not newly accepted NADI condition evidence**.
It does not replace the pilot's NULL collector-success field or advance its
projection time. Full-worker completion13:42:00.148780Z is another distinct clock.
No historical query or new PI request was used for this comparison.

Two manual samples cannot establish continuous acquisition cadence. Proposed
future study: obtain responsible engineer documentation of sampling/compression,
equipment-use purpose and allowable evidence age first; gather aggregate local
worker/ledger observations for72h without additional acquisition. If gaps remain,
request a separate bounded set of up to3 individually authorized manual one-signal
observations, each≤5GET, no retries/history, across engineer-selected operating
conditions. Stop after that set and review rather than repeatedly probing.
Even these samples supplement engineering judgment; they do not prove an SLA.
No scheduler, recurrence, source request or future-run authorization is created.

## G06 — source-free readiness simulation

Reviewed `FreshnessPolicy` and `phase1_readiness` are used with a frozen aggregate
R3 integration document plus independently observed local ledger successes at
the observation cut. No DB/client/source function is invoked by the simulator.
Its `evidence_origin=OPERATOR_DOCUMENT`; hypothesis output is not a runtime result.
The fixture contains no credentials, raw source payload or arbitrary PI query plan.

| Case | WO / Mart / technical PI | Condition gate | Overall |
|---|---|---|---|
| Actual eight policies UNSET |UNKNOWN /UNKNOWN /UNKNOWN |UNKNOWN |UNKNOWN (5PASS/4UNKNOWN) |
| Hypothetical660/660/1800; source/projection UNSET |PASS /PASS /PASS |UNKNOWN |UNKNOWN (8PASS/1UNKNOWN) |
| WO661s old; other acquisition inputs current |PARTIAL /PASS /PASS |UNKNOWN |UNKNOWN |
| One projector661s old, other recent |PASS /PARTIAL /PASS |UNKNOWN |UNKNOWN |
| One projector success missing |PASS /UNKNOWN /PASS |UNKNOWN |UNKNOWN |
| Technical PI1801s old |PASS /PASS /PARTIAL |UNKNOWN |UNKNOWN |
| PI success missing or unavailable |PASS /PASS /UNKNOWN |UNKNOWN |UNKNOWN |
| Future WO completion |UNKNOWN /PASS /PASS |UNKNOWN |UNKNOWN |
| Latest WO error despite recent success |PARTIAL /PASS /PASS |UNKNOWN |UNKNOWN |
| Good quality + epoch source, synthetic60s source/projection policies |PASS /PASS /PASS |PARTIAL /SOURCE_STALE |PARTIAL |
| Synthetic current source +61s-old projection |PASS /PASS /PASS |PARTIAL /PROJECTION_STALE |PARTIAL |
| Synthetic recent times +BAD quality |PASS /PASS /PASS |PARTIAL /QUALITY_NOT_ACCEPTED |PARTIAL |
| Synthetic unverified scope |acquisition policies unchanged |BLOCKED /HUMAN_CROSSWALK_REQUIRED |BLOCKED |

Fourteen cases and threshold-boundary assertions pass. The synthetic60s values
only exercise negative logic; **not proposed production condition policies**.
Missing pilot collector success is additionally validated by existing query-service
tests, with a current independent technical collector unable to fill that NULL.
No simulation claims equipment HEALTHY or generalizes the single pilot to845 assets.

Reproduce from`reliability-cockpit` with installed reviewed dependencies:

```bash
python docs/validation/nadi-p1-fresh-gov-01-simulation.py
DATABASE_URL=sqlite+pysqlite:///:memory: COCKPIT_CONFIG_MODE=managed \
python -m unittest discover -s tests -p test_component_freshness.py -v
DATABASE_URL=sqlite+pysqlite:///:memory: COCKPIT_CONFIG_MODE=managed \
python -m unittest discover -s tests -p test_freshness_governance.py -v
DATABASE_URL=sqlite+pysqlite:///:memory: COCKPIT_CONFIG_MODE=managed \
python -m unittest discover -s tests -p test_phase1_readiness.py -v
DATABASE_URL=sqlite+pysqlite:///:memory: COCKPIT_CONFIG_MODE=managed \
python -m unittest discover -s tests -p test_integration_status.py -v
```

Actual test executable was the exact-release Cockpit`.venv/bin/python`; test
commands also used`PYTHONPATH=/tmp/nadi-phase1-host-testdeps` for existing host
dependencies. Counts: component7 PASS; governance14 PASS / 9 isolated PostgreSQL skips;
readiness 11 PASS; integration 13 PASS. **45 PASS / 9 SKIP**, plus 14 decision simulations.
No broad/full-suite rerun or PostgreSQL fixture provisioning was necessary for
this documentation-only task. Existing suites and product code are unchanged.
One initial invocation used the repository root instead of Cockpit and failed
test-directory discovery before tests ran; corrected command results above are
the executed evidence, not additional cases.

Actual deployed `cockpit phase1-readiness` at13:53:03.239019Z returns UNKNOWN:
WO/Mart/PI gates UNKNOWN_FRESHNESS_POLICY; condition projection
UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS; governance, condition schema, identity,
signal selection and integration status PASS. Hypothetical policies were never
exported into API/worker/private configuration.

## Historical G07 — approval points before GOV-02

Required owner decisions (not supplied by this task):

1. Fauzi/project owner and relevant component operations owners explicitly
   approve/revise/reject660/660/1800 **monitoring-only** windows, failure tolerance
   and the proposed7-day expiry. Record named technical reviewer endorsements.
2. Keep legacy three and both condition settings blank. Responsible source
   engineer supplies condition source/use-age evidence; runtime owner supplies
   condition projection/use-age evidence before numeric decisions.
3. Authorize a separate controlled activation task and accountable rollback
   operator. Repository PR merge alone is not policy activation authorization.

Future approved rollout: private backup preserving permissions and unrelated
settings; change only the three approved component keys in`.env.platform`;
validate parser exclusive-component mode and effective Compose without secrets;
replace only cockpit-api if required to load reviewed configuration; compare
accepted evidence/governance/journal before/after, inspect five independent
components and nine gates, require condition policies remain UNSET/UNKNOWN.
No worker restart, new collection, mapping/signal mutation, DDL or clock rewrite.
Monitor local aggregate ledgers and errors, evaluate actual false-alert and delay
experience at24h/72h. None of these rollout actions were executed here.

Rollback if parser conflict, wrong scope/inheritance, missing/future timestamp
promoted CURRENT, quality/coverage hidden, accepted evidence changed, or unexpected
regression: stop rollout; restore only the newly activated keys to blank using
private approved backup, preserve unrelated PI settings and operator artifacts;
reload only the required API component and verify UNKNOWN plus intact evidence.
Do not restore/truncate DB, retry PI or extend thresholds to conceal failures.
At expiry absent reapproval, the owner returns proposed keys to blank; no automatic
expiry tooling is implied.

Remaining pilot acceptance blockers: pending component monitoring approval and
controlled activation; insufficient condition source/projection freshness evidence
and owner-approved policies; actual freshness-qualified readiness after those
steps. Recurring condition operation is a separate optional design/authorization,
not activated by this matrix. Other assets still need human identity evidence.
The accepted Coal Feeder pilot no longer has HUMAN_CROSSWALK_REQUIRED; the frozen
BFPT/KKS issues remain independently open. Policy approval does not close them.

## Preservation and safety

Private aggregate/forensic records remain ignored under
`secrets/nadi-p1-fresh-gov-01/`; original R3/journal files are never rewritten.
The reviewable fixture/simulation output is aggregate-only. No secret value or
secret-derived fingerprint is included. Reader remains SELECT-only;845registered,
VERIFIED1/PROPOSED0, signals/evidence/state1/1/1;433technical active preserved.
All eight policy values remain UNSET. All 23 existing container identities/start/image/restart
states are preserved. Background WO/PI/projector activity may advance normally.

Task-attributable PI/Maximo/CEMS live GET=0; source writes=0; condition acquisition/
replay=0; Mart evidence/approval/mapping writes=0; policy/credential changes=0;
DDL/reset/truncate=0; deployment/restart=0; registry/scheduler changes=0;
new operational DB=0; CEMS/NK changes=0. PR remains open/unmerged.

Final preservation verification: full R3 latest/state and mapping/selection JSON
unchanged; all 34 sampled historical artifact bytes and mtimes preserved; reader
SELECT-only; private configuration metadata unchanged since R3; clean reviewed
release and original workspace preserved. Actual `--require-pass` exit2/UNKNOWN.
