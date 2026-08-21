# MX-011W — Work Order Population Profile

Status: **PARTIAL — bounded live profiling stopped after two read timeouts**

This document records aggregate evidence only. It intentionally excludes Work
Order numbers, Asset numbers, descriptions, raw OSLC payloads, credentials, and
session details.

## Scope and safety

- Source: `MXWODETAIL`
- Scope: `siteid="BSR"`, organization values profiled and reported only as aggregates
- Prefix analysis: configured `BSR` Work Order prefix
- Default slice: `order_by=NONE`, page size 25, source ceiling 500, maximum 20 pages
- Recent probe: exactly one `order_by=-changedate`, page size 25, maximum one page
- Live client: existing GET-only `OslcClient`, one process at a time
- No MartWriter, collector store, or SyncCursor was called
- No production canonical configuration was changed

The live request ceiling was 60 business requests. The first compare attempt
completed 19 pages and timed out on the next page. A conservative follow-up
profile used 19 pages (475 rows), then one recent-order probe was attempted and
timed out before a page was returned. No further live requests were issued.

## Current Reliability Mart profile

The current Mart contains 174 `maintenance_event` rows in BSR/IP.

### Status

| Source status | Count | Percentage |
|---|---:|---:|
| CAN | 170 | 97.7% |
| APPR | 4 | 2.3% |

The literal source codes are retained. A friendly label for `CAN` was not
verified from committed Maximo knowledge during this task.

### Work Type

The allowlisted source projection contains the following literal `worktype`
values:

| Work Type | Count | Percentage |
|---|---:|---:|
| PM | 153 | 87.9% |
| CD | 10 | 5.7% |
| CM | 6 | 3.4% |
| EM | 1 | 0.6% |
| PDM | 1 | 0.6% |
| PRO | 1 | 0.6% |
| RTF | 1 | 0.6% |
| S | 1 | 0.6% |

The canonical Mart `event_type` field is conservative. Its API view reports
15 null values because not every source Work Type is in the existing enum.
This is not a reason to discard those Work Orders or to change the Contract v1
schema in MX-011W.

### Dates and measures

- `source_changed_at`: 2014-07-08 through 2026-08-21; present on 174/174 rows
- `actual_start`: present on 2/174 rows; range 2024-04-05 through 2024-10-15
- `actual_finish`: present on 0/174 rows
- `downtime_hours > 0`: 0 rows
- `labor_hours > 0`: 0 rows

### Asset references

- Maintenance rows: 174
- Rows with an equipment reference: 174
- Rows whose reference resolves to the current Asset Mart: 14
- Rows unresolved against the current Asset Mart: 160
- Distinct equipment references: 139
- Distinct resolved references: 12
- Distinct unresolved references: 127

These unresolved counts are consistent with the controlled initial dataset and
must not be interpreted as automatic source corruption.

## Default-order source profile

The completed conservative profile read 475 rows across 19 pages. The page-20
request in the original 500-row attempt timed out, so this is not a claim about
the complete 500-row slice.

| Metric | Measured result |
|---|---:|
| Source rows read | 475 |
| Prefix matched | 237 (49.9%) |
| Prefix skipped | 238 (50.1%) |
| Organization `IP` | 475 (100.0%) |
| Prefix-matched rows with site BSR/org IP | 237 |
| Prefix-matched rows eligible for canonical required identity fields | 174 |
| Prefix-matched rows missing `assetnum` | 63 |
| Prefix-matched rows missing `wonum`, `siteid`, or `orgid` | 0 |
| Asset present among prefix matches | 174 (73.4%) |
| Actual start present | 2 (0.8%) |
| Actual finish present | 0 (0.0%) |
| Downtime > 0 | 0 |
| Labor hours > 0 | 0 |

Status before prefix filtering:

| Source status | Count | Percentage |
|---|---:|---:|
| CAN | 452 | 95.2% |
| APPR | 23 | 4.8% |

Status after the configured prefix filter:

| Source status | Count | Percentage |
|---|---:|---:|
| CAN | 233 | 98.3% |
| APPR | 4 | 1.7% |

Work Type after the configured prefix filter:

| Work Type | Count | Percentage |
|---|---:|---:|
| PM | 214 | 90.3% |
| CD | 10 | 4.2% |
| CM | 6 | 2.5% |
| EM | 1 | 0.4% |
| PDM | 1 | 0.4% |
| PRO | 2 | 0.8% |
| RTF | 1 | 0.4% |
| S | 2 | 0.8% |

The prefix filter changes CAN from 95.2% to 98.3% in this partial slice.
That is a measurable interaction, but the 3.1 percentage-point change is not
large enough by itself to explain CAN dominance.

The current controlled load reported 500 source rows read, 174 canonical rows
emitted, and 326 rows skipped. The partial source profile accounts for 238
prefix exclusions and 63 missing `assetnum` values in its first 475 rows. The
remaining 25 source rows were not safely profiled after the page-20 timeout;
therefore this document does not invent an exact 326-row reason partition.

## Recent ordering result

The required single `-changedate` probe did not return an HTTP response; it
ended with a bounded `ReadTimeout`. Therefore:

`RECENT_ORDER_SUPPORTED = UNKNOWN`

This is not evidence that Maximo rejects the syntax, and it is not evidence
that the syntax is supported. No alternate ordering syntax was tried.

The recent-first 500-row comparison was not executed. Consequently, CAN
dominance classification remains **INCONCLUSIVE** for the specific question
of default-order sampling bias versus source-population dominance. The Mart
and partial default slice are both CAN-heavy, but a recent-first comparison is
still required before selecting a bootstrap strategy.

## Changedate watermark assessment

`changedate` is available on all current Mart rows and all prefix-matched rows
in the partial source profile, with a broad 2014–2026 range. It is a credible
candidate because it is already mapped to `source_changed_at` and is present
on the observed rows.

The assessment is **NEEDS_MORE_EVIDENCE**, not `SUITABLE`, because this task did
not complete the recent-order probe or verify stable descending pagination and
tie behavior. A future implementation must also use overlap/reconciliation for
equal timestamps and canonical-ID deduplication.

## Strategy recommendation

No ingestion change is approved by MX-011W.

For MX-012R, the evidence supports the following guarded direction, subject to
completion of the recent-order probe:

1. Preserve all legitimate source statuses, including `CAN`.
2. Test a recent operational bootstrap ordered by `-changedate` only after a
   successful bounded probe and stable pagination verification.
3. Perform historical backfill separately with explicit date windows or
   cursor-independent bounded pages; do not use a status exclusion.
4. Add an incremental tail using `changedate` only after watermark suitability
   is confirmed, with overlap, tie handling, and canonical-ID deduplication.

The NADI product may later offer a deliberate status view/filter, but ingestion
must retain source history and must not be changed to hide `CAN`.

## Request audit

- Authentication requests: 3 in-memory login handshakes, one per bounded CLI process
- Business requests: 40 attempted in total across the live attempts
- HTTP 200: 38 observed
- HTTP 400: 0
- HTTP 401/403: 0
- HTTP 429: 0
- HTTP 5xx: 0
- Read timeouts: 2
- Response-cap interruptions: 0
- Maximum concurrency: 1
- Request ceiling exceeded: NO

The two timeouts are the reason the final task status is PARTIAL. No retry was
made after the recent probe timeout, preserving the hard request budget.
