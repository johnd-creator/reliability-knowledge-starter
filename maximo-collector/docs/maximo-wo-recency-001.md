# MAXIMO-WO-RECENCY-001 — bounded recent WO sync

Status: **PARTIAL**, implemented for review; not deployed, no production catch-up.
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

**Empty cursor limitation:** bounded newest-first bootstrap can acquire current
rows but cannot declare historical coverage after a cap. It will replay that
bounded top population on later runs while the cursor remains empty. No cursor
is inferred from MAX(local changedate), no cursor is reset, and this PR does not
silently select a new history boundary. Establishing a reviewed initial coverage
policy/continuation strategy remains necessary for this deployment to become a
steady incremental worker. The cursor-independent historical `backfill` command
still traverses its explicitly capped population; it does not move this cursor.

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

**155 tests passed**, including 19 new recency cases, client page-shape/budget
regressions and CLI backfill isolation. Tests use fakes/local SQLite only, with
no live Maximo or production DB. `git diff --check` passes.

## NADI handoff and review gates

No runtime code deployment or broad catch-up was performed. Existing worker was
restored after every probe. Existing DB/credential/collector boundaries and Mart
schemas remain unchanged. No new database.

After review/merge, deploy the reviewed collector image and agree the empty-cursor
bootstrap/coverage policy before a broad acquisition. Then inspect the aggregate
recency completion reason and cursor alongside newly collected row timestamps.
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
and unmerged for senior review of bootstrap, source paging and deployment.
