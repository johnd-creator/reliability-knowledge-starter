# NADI-AUD-01 — Generic Maximo cursor recovery

16 Oktober 2026 WIB. Isolated source correction, **not deployed or merge-approved**.

- Main baseline: `919428a906c5ef0c7fd02fe0d64e33b537c39570`.
- Source/test commit: `753a65034129949c0c1bc770d8d476a2b67b7312`.
- Audit: [PR90](https://github.com/johnd-creator/reliability-knowledge-starter/pull/90),
  immutable [Astra F-02](https://github.com/johnd-creator/reliability-knowledge-starter/blob/c20a764ccae892a5bb0972a59591e3f83984b0d9/docs/audits/NADI-ASTRA-HIGH-INDEPENDENT-AUDIT.md#f-02--generic-maximo-sync-can-advance-past-a-failed-row).
  The audit remains independent and unmodified.

## Cause and counter-evidence

The generic [sync loop](../src/services/sync.py) previously accumulated raw maximum
timestamps before mapping/upsert and allowed errorful completed traversals to save
them by default. [Object configuration](../src/api/app.py) also defaulted to the
permissive policy. Maximum **successful** timestamp would still strand older failures.

Deterministic fake source: C0=10 August, A/T1=11 August fails mapping, B/T2=12 August
succeeds. Baseline reports complete=true/errors=1 and saves T2. After repairing only
the local mapper, ordinary incremental `>=T2` returns B; A stays absent despite its
unchanged T1. No Maximo or operational omission was measured.

Counter-evidence: existing transport/pagination failures already suppress cursor
advancement, inclusive `>=` replays ties, explicit asset-baseline strict mode already
blocks mapping-error checkpoints, and current WO recovery is a different early-return
path. Those protections do not repair the generic default. Existing bad-row unit
coverage asserted skip/error counts without asserting recovery on the next run.

Baseline final regression file was evaluated against the immutable baseline sync
and API modules in a separate Python process, without checkout/source replacement.
It executes21 tests and records15 assertion-failure events (including subtests) and5
errors; do not subtract subtest events to invent a passing-case count. The explicit
two-run omission is retained in [baseline evidence](evidence/nadi-aud01/baseline-reproduction.json).

## Corrected invariant

For the generic path, write a watermark only after traversal finishes **and all
processing succeeds**. Any mapping, comparison, primary persistence or equipment
status-history error leaves the previous persisted cursor unchanged (or absent on
first sync), marks mode=partial/complete=false, and records the run when the local
run store is available. The old `cursor_requires_zero_errors` argument remains for
call compatibility, defaults true and cannot opt out of this generic invariant.
No source query, source mapper, schema, cursor reset or replay ledger is added.

Failed batches detach from pending once, report sanitized exception class only and
are not implicitly retried during that traversal. Later independent batches can
still persist; terminal flush failures now produce partial run evidence instead of
escaping without a run. Batch upsert counters count acknowledged writes, not a claim
about uncertain commits. Legacy `MAPPING_ERRORS` reason also covers comparison/local
persistence errors; `pagination_error` retains transport/pagination reason when present.

Equipment primary upsert and status history use separate local transactions. Status
now follows acknowledged persistence; an already-unchanged primary row still performs
the existing idempotent status reconciliation. Otherwise a status failure after the
primary commit would never be retried. [Store](../src/repositories/store.py) itself is
unchanged; status appends only when different from its last observation.

`stats.watermark` retains its existing meaning as the observed candidate maximum,
including on partial runs; it is **not** proof of a stored checkpoint. Completion,
errors and the actual cursor must be distinguished. Non-watermarked acquisition
still never reads/creates a source cursor; processing failures now report partial
instead of a misleading fully completed run.

## Object compatibility

| Object | Existing scope / watermark | Candidate effect |
|---|---|---|
| mxapiasset | siteid BSR + required eq11 configured unit (default CS01); changedate, source_changed_at comparison | Routine generic checkpoint strict; asset-baseline bounded projection/config unchanged |
| mxasset | Explicit legacy equipment, same BSR/configured-unit guards; changedate | Same strict recovery; not added to default sources or collected alongside mxapiasset |
| mxapisr | siteid BSR; changedate | Older failed record remains reachable from retained cursor |
| mxperson | locationorg IP; statusdate/status_changed_at; batch100 | Strict checkpoint, bounded detached batch failure; original paging/select/order preserved |
| mxitem | site BSR; statusdate/status_changed_at; batch100 | Same strict generic handling; no scope broadening |
| mxwodetail | siteid BSR, configured BSR wonum prefix; specialized recent/recovery path, max20 pages/request budget | Early dispatch and specialized algorithm/store/floor/bootstrap unchanged; dedicated regression PASS. Explicit non-recency generic callers also cannot checkpoint errors |
| mxapilabor | worksite BSR; no watermark, full acquisition each run, batch100 | No cursor introduced; successful acquisition stays full, failed processing reports partial |

The baseline configuration keeps its explicit strict flag and disables watermark
query only for its reviewed bounded baseline traversal. Current WO config already
sets strict=true; changing generic defaults does not change its returned config.
No rate, request/page cap, authentication, BSR/IP restriction, prefix/required field,
source-read guard, default source list or synchronization schedule is changed.

## Tests and review

From `maximo-collector`, using its existing environment (no private dotenv loading):

```sh
PYTHONPATH=.:tests .venv/bin/python tests/run_offline.py test_cursor_recovery test_sync test_workorder_recency test_asset_baseline
PYTHONPATH=.:tests .venv/bin/python tests/run_offline.py
```

In the isolated worktree `.venv` is not copied: execution reused the existing
component interpreter at the original checkout, with imports rooted in this worktree.
The committed runner rejects network and non-in-memory DB access, clears inherited
source/DB environment settings and suppresses private dotenv loading. Existing tests
that need SQLite use only `:memory:`; no operational PostgreSQL is accessed.

| Verification at unchanged candidate source/tests | Result |
|---|---|
| New generic recovery |21/21 PASS; includes all five generic object configurations, retained cursor across new service instances/repeated retries, full-first-run failure, ties, row/batch/comparison errors, transport/page errors, expected exclusions and status-history recovery |
| Focused recovery + existing mapper/sync/WO/asset-baseline |86/86 PASS,0 skip |
| Full collector unittest suite |202/202 PASS,0 error/failure/skip;0 blocked external-I/O attempts |
| Source guards / specialized path preservation |Existing auth/OSLC/scope/bounded-query tests included; WO service, baseline service, store and original specialized tests byte-identical to main |
| Publication checks |Diff whitespace, relative links, evidence hashes and intended-path review; results recorded at delivery |

[Validation manifest](evidence/nadi-aud01/validation.json) pins source/test commit and
SHA256 of both changed source files and both test files. Local environment used
Python3.14; supported-version CI still needs explicit collector qualification.

Meaningful failed attempts are retained privately: initial relative-path harness/edit
invocations targeted the wrong working directory and did not mutate source; corrected
to explicit paths. Initial safety runner rejected29 valid SQLite fixture connections
(199 tests); narrowed to SQLite in-memory only, with network/other DB rejection
retained. These are harness errors, not collector regression failures. Initial18
baseline tests were red as expected; the final21-test baseline replay is separately
recorded above. No failed application run was hidden or retried operationally.

## Replay cost, limitations and operational gate

A persistent poison record can hold the generic checkpoint indefinitely. Subsequent
scheduled runs may re-read all eligible rows since C0; a failed initial full run has
no new cursor and naturally traverses again. Every run retains existing page/request
limits; no infinite in-run retry is added. Successful rows are upserted/compared
idempotently; equipment may perform an extra local status-history lookup on unchanged
rows. This costs source/local work and can delay later coverage when bounded pages
are exhausted. Mapping repair and authorized operator review are required, not an
automatic cap increase, source reset, cursor rewind or forced backfill.

This prevents **new** failed-record stranding from candidate checkpoints. It does
not recover omissions already below an operational cursor, establish a consistent
source snapshot, solve arbitrary concurrent source mutation, or certify PostgreSQL
commit-failure behavior. If local run recording is itself unavailable, the exception
still propagates; no successful durable run evidence is fabricated. Existing data
and scheduled policy must be assessed separately before any authorized rollout.

**COLLECTOR_EXACT_HEAD_CI: NOT_AVAILABLE. AUD04_CI_GAP: OPEN.** The candidate workflow
path filters cover Cockpit/contracts/development tooling, not collector-only changes;
its backend/frontend jobs do not certify this correction. No workflow redesign or
unrelated dispatch is included. Local PASS qualifies this DRAFT implementation only;
collector-specific exact-head CI (AUD-04 or independently proven existing check) and
senior review are mandatory before code merge approval. Merge authorization PENDING.

Rollout requires a separate operator decision, current cursor/backup evidence,
bounded replay/load assessment and controlled compatible release. None is executed.
Code rollback to the permissive version would reintroduce this risk; do not advance
held cursors to mask failures. Preserve successful local records/run history/cursors
and plan a compatible corrective release; no reset/schema deletion is a rollback.
No Maximo GET, live synchronization, operational PostgreSQL/DDL or Mart/PI/CEMS/DCS action, frontend/source
selection, deployment or PR merge took place. Stop after DRAFT review delivery.
