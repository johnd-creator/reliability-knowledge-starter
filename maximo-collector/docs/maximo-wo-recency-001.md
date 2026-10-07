# MAXIMO-WO-RECENCY-001 — bounded recent WO sync

FIX-01 status: **PASS (code-complete)**, pending review/deployment.

- SOURCE CAPABILITY VERIFIED: prior bounded live evidence below.
- IMPLEMENTATION VERIFIED: 181 hermetic tests pass.
- BOOTSTRAP NOT YET EXECUTED in production.
- ROUTINE NOT CURRENT in production; reviewed code is not deployed.
- NADI NOT CURRENT / recent Maintenance not yet verified.
Baseline: `a8393ba7d8dfddcae67b14b6153a8056c2f01d34` (latest main verified before
and after implementation). Branch: `codex/maximo-wo-recency-001`. Independent
PR #12 remains open at `417dbc8316e1bfbd9ffba0c8bd4777bd186cf8ff`; no changes.

## Root cause and preserved state (2026-10-07)

Previously WO used `order_by=None`, `prefix_query=False`, `watermark_query=False`,
page size 25 and max pages 1000. The store cursor affected mode/idempotency but
neither the source query nor local early termination. The 25 × 1000 cap explains
the 25,000-row historical/out-of-prefix cycles. Cursor state is actually empty,
not a persisted August cursor; a logged provisional watermark is not a cursor.

| State | Before probes | After probes |
|---|---|---|
| Local WO count | 112,259 | 112,259 |
| `mxwodetail` cursor | no row | no row |
| Newest local WO changedate | 2026-08-21 03:56:54 UTC | same |
| Maintenance Mart watermark | 2026-08-21 03:56:54 UTC | same |
| Asset Mart watermark | 2026-10-01 05:40:10 UTC | same |

Latest recorded WO run remains partial: started 2026-10-07 07:23:41.162486 UTC,
finished 07:24:13.892478 UTC, 0 seen/upserted, 1 error. Both Mart projections are
SUCCEEDED; latest observed maintenance projection success 08:05:10.545938 UTC.
Success means local projection ran, not that Maximo input is current.

## Source capability evidence

The prior [MX-011W profile](mx-011w-workorder-population-profile.md) verified
`-changedate` over 8 pages/200 rows, including ties/duplicates and no descending
order violations. This task used existing guarded client/profiler and actual
worker environment, pausing/restoring the worker around probes. No credentials,
WO identities/descriptions, raw payloads or full URLs were saved.

| Probe | Budget | Actual business GETs | Result |
|---|---|---:|---|
| Profiler `-changedate`, site only, small select | shared 4, 1 page × 5 | 1 | ReadTimeout, 40.76 s including authentication; no returned timestamps |
| `siteid="BSR" and wonum in ["BSR%"]`, small select, default order | shared 4, 1 page × 5 | 1 | 16.23 s; 5/5 prefix match; dates 2014-07-08 09:51:59 to 2014-12-03 18:40:47 +07:00 |
| New recency code with prefix + descending order, existing select | 2, 1 page × 5 | 1 | 5.50 s, 5 rows; latest 2026-10-07 14:48:19 +07:00; failed scope validation because select lacked orgid; zero simulated upserts |
| Corrected code including orgid, after tests | 2, 1 page × 5 | 1 | 6.83 s; 5/5 prefix match, BSR/IP and descending order valid; dates 2026-10-07 14:37:38–14:48:19 +07:00; PAGE_LIMIT; 5 simulated upserts |

Total: **4 business GET attempts**, 3 HTTP 200 and 1 timeout. Login uses only the
existing authentication handshake; business-source writes **0**. All probes
performed **0 local DB writes**, including no cursor/collect_run writes. Last
two runs use an in-memory store mirroring the actual empty cursor. PAGE_LIMIT
is expected: source advertised another page and the probe refused it. This
proves current source visibility, not full population/cursor coverage.

No `LIKE` or date comparator probe was made. `changedate >= cursor` remains
disabled because prior unsupported capability is not re-verified. Server-side
prefix is now enabled based on the accepted IN form and current probe.

## Algorithm and cursor correctness

Routine WO configuration: `-changedate`, site BSR, configured IN-prefix plus
local prefix validation; page size 25, max pages 20 (at most 500 collection rows),
max **40 business requests** per run including linked details and expiry retries.
The request budget cannot enlarge an enclosing stricter budget. Source throttling
at least 1 second and response cap at most 1 MiB remain enforced. Org IP is
validated on returned rows. No fallback to historical/default-order traversal.

`iterate_pages` completes normalization/detail retrieval and next-link validation
before releasing a page; `iterate` remains the row interface for other callers.
Recency additionally rejects malformed collections, missing timestamps, bad
scope, and ascending movement within/across pages before writing that page.

For an existing cursor, process changes **greater than or equal to** it; continue
through tied pages and stop only after a fully validated page contains a strictly
older change. Equal timestamps replay via idempotent identity/change upserts.
Duplicate identities retain their first/newest version. The cursor advances to
max(old cursor, newest accepted successful change) only on successful ordered
boundary completion or natural source exhaustion. Mapping/store failures, source
errors, pagination loops/caps and request budgets retain the old cursor. Earlier
valid committed rows can replay on restart. `cursor_requires_zero_errors=True`
is mandatory in the routine recency path.

**Empty cursor recovery (FIX-01):** routine sync now returns
BOOTSTRAP_REQUIRED with zero source requests. It records aggregate local run
state but never traverses the top population or invents a cursor.

The explicit `bootstrap-workorders-recent` command takes required finite
`--max-pages` (1..1000) and `--request-budget` (1..2000), plus `--page-size`
(1..25, default 25). No unlimited mode. It uses the verified prefix/order/site
query and the same full-page BSR/IP, order and mapping validation. Ordinary
routine limits remain 20 pages/40 business requests.

Its initial recovery floor comes from MAX(work_order.source_changed_at) in the
existing Collector, not the Mart. A standalone `latest_work_order_change()`
store query is read-only and never mutates a cursor. Before any source reads or
WO upserts, the operator command saves this floor as a reserved
`mxwodetail-recovery-floor` / `recovery-floor` evidence row in the existing
collect_run table. It is **not** a sync_cursor. Retries reuse that original
marker, because partial upserts may raise the current local MAX. Never remove
or replace the floor marker merely to make recovery appear complete. No new
DB/table/migration. A PG session advisory lock serializes explicit bootstrap
attempts and is released on success/failure. Empty/missing/unusable local
floor returns BOOTSTRAP_BLOCKED without source access. A pre-existing runtime
cursor returns BOOTSTRAP_NOT_REQUIRED and is never reset.

Traverse from source newest through **all floor timestamp ties**, then stop
strictly below the floor. Natural source exhaustion is acceptable only when
its validated oldest row has reached the floor (including equality). Exhaustion
above the floor returns RECOVERY_FLOOR_NOT_REACHED. Every partial/error leaves
the runtime cursor absent; valid committed rows remain idempotent local progress.
Retry starts newest-first with the same durable floor and deliberately chosen
larger finite ceilings if needed. It does not resume an unstable offset token.

After successful reconciliation, set the cursor to the newest successful
accepted change, capped at bootstrap start time. Changes made after bootstrap
started therefore remain eligible for the next normal sync. The CLI immediately
runs a conservative routine verification and reports its result separately. If
that verification fails, bootstrap success is not undone or equated with routine
freshness. Historical `backfill` remains independent and does not establish the
operational cursor.

Additional stop states: BOOTSTRAP_REQUIRED, BOOTSTRAP_BLOCKED, BOOTSTRAP_BUSY,
BOOTSTRAP_NOT_REQUIRED, RECOVERY_FLOOR_REACHED, RECOVERY_FLOOR_NOT_REACHED,
CURSOR_STORE_ERROR. Evidence includes recovery floor, floor reached, configured
page/request ceilings, consumed requests/pages, source range and cursor before/after.

**Paging limitation:** tie overlap/local order validation assumes the source
honors its descending-order contract over the traversed population. A moving
source/offset paging may still omit rows without an observable order violation;
no snapshot or secondary-key capability was proved here. Deterministic source
paging under concurrent changes remains part of MXR-004; it is not marked done.

## Observability and tests

`SyncStats.recency`, local trigger API response, CLI JSON and structured INFO logs
carry source row count, prefix accepted/skipped, source timestamp range, cursor
before/after, pages attempted/validated, business requests, completion and stop
reason. Existing collect_run persistence retains coarse counters/watermark;
aggregate detailed evidence is in logs/API output, with no DB schema addition.
Stop reasons include CURSOR_REACHED, NO_NEW_ROWS, SOURCE_EXHAUSTED, PAGE_LIMIT,
PAGINATION_ERROR, REQUEST_BUDGET, SOURCE_ERROR, ORDER_VIOLATION, SCOPE_ERROR and
MAPPING_OR_STORE_ERROR.

From the isolated worktree's `maximo-collector` directory:

```sh
/home/john-d/Music/reliability-knowledge-starter/maximo-collector/.venv/bin/python -m unittest discover -s tests
```

**181 tests passed**: the previous 155-test regression coverage plus 26 FIX-01
cases for bootstrap/floor/retry/concurrency/CLI/store behavior. Two earlier
cursorless expectations were updated to the reviewed explicit-recovery policy.
The local store query/anchor tests use actual isolated SQLite storage; source,
CLI and PG advisory-lock tests use fakes/mocks. Tests use fakes/local SQLite only, with
no live Maximo or production DB. `git diff --check` passes.

## NADI handoff and review gates

No runtime code deployment or broad catch-up was performed. Existing worker was
restored after every probe. Existing DB/credential/collector boundaries and Mart
schemas remain unchanged. No new database.

After review/merge, deploy the reviewed collector image. Stop the old worker
before switching code so it cannot perform the legacy historical walk. Confirm
new routine WO cycles report BOOTSTRAP_REQUIRED without source requests. Choose
and review finite operator ceilings for recovery; for example after deployment:

```sh
docker compose --env-file .env.platform -p reliability-cockpit-platform \
  -f compose.yaml -f compose.dev.yaml run --rm --no-deps -T maximo-worker \
  mxcollector bootstrap-workorders-recent --page-size 25 \
  --max-pages 40 --request-budget 60
```

This example has **not been executed**. Inspect oldest reached versus the frozen
floor and the stop reason before deciding whether a larger bounded retry is
reasonable. Require successful recovery and the CLI's immediate routine
verification before treating the Collector current tail as recovered. Then
inspect newly collected factual dates and the existing local projection.
Current rows feed the existing local Mart incremental projector; the managed
runtime already runs it every 300 seconds. To trigger local projection explicitly,
from the configured runtime checkout (with its existing `.env.platform`):

```sh
docker compose --env-file .env.platform -p reliability-cockpit-platform \
  -f compose.yaml -f compose.dev.yaml exec -T mart-projector \
  mxcollector mart-project --incremental
```

This reads/writes only the existing local Collector/Mart store and does not query
Maximo. Serialize with the running projector (or wait for its scheduled cycle).
NADI maintenance windows depend on actual start when available, otherwise source
change time; inspect factual dates and registered-asset linkage after projection.
Do not equate a recent changedate with a recent actual maintenance start.
Until collection and projection are verified, NADI 7/30-day activity remains
unproven. Phase 1 remains incomplete; MXR-004 remains PARTIAL. PR must remain open
and unmerged for senior review of recovery ceilings, source paging and deployment.


## FIX-01 execution evidence

Previous HEAD: `83992835e37b14f7475b19285b4ae54acd393e53`; continued on the same
branch and PR #13. No new PR or merge. This correction performed **zero Maximo
requests** and **zero production DB writes**. Only aggregate local state was
read: 112,259 WOs, recovery-floor candidate 2026-08-21 03:56:54 UTC, no runtime
WO cursor, zero recovery-floor markers, Maintenance Mart watermark unchanged
at 2026-08-21 03:56:54 UTC (projection status SUCCEEDED). No production bootstrap
has been attempted. Current capability timestamps in the earlier table remain
historical probe evidence; they are not a new bootstrap execution claim.

The hermetic bootstrap-success test immediately followed by routine sync uses
one routine page/request, reports NO_NEW_ROWS and performs zero repeat upserts.
Post-start changes, floor ties across pages, all required partial/error branches,
retry-stable floor and independent backfill are covered. Paging under a moving
source remains unproven; MXR-004 remains PARTIAL and Phase 1 incomplete.
