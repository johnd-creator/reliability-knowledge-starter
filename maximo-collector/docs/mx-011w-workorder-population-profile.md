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

## MX-011W2 Recent-First Verification

MX-011W2 repeated one bounded recent-order probe with a temporary timeout
override. The committed production default remains 30 seconds.

### Targeted probe

- Attempt A: timeout 60 seconds, `-changedate`, page size 25, maximum one page,
  source cap 25
- Result: **success**; 25 source rows returned
- Attempt B: not required and not executed
- Business requests used by the probe plus its bounded sample: 2
- Recent order: operationally verified

Attempt A aggregate result:

| Metric | Result |
|---|---:|
| Source rows | 25 |
| Prefix matched | 4 |
| Prefix skipped | 21 |
| Canonical eligible | 4 |
| Missing `assetnum` | 0 |
| Status before prefix | WDONE 25 (100.0%) |
| Status after prefix | WDONE 4 (100.0%) |
| Work Type after prefix | CD 1, CM 1, PM 1, RTF 1 |
| `changedate` after prefix | 2026-08-21 17:03:23–17:04:30 +07:00 |
| Actual start present | 4 |
| Actual finish present | 0 |
| Asset present | 4 |
| Downtime > 0 | 0 |
| Labor hours > 0 | 0 |
| Missing `changedate` | 0 |
| Order violations | 0 |
| Duplicate identities | 0 |
| Adjacent timestamp ties | 20 |

### Comparable 200-row slices

Both slices used page size 25, maximum 8 pages, source cap 200, and timeout 60
seconds. Date and presence metrics below are calculated after the configured
BSR prefix filter; status-before-prefix is reported separately.

#### Default order (`order_by=NONE`)

| Metric | Result |
|---|---:|
| Source rows | 200 |
| Prefix matched / skipped | 68 / 132 |
| Canonical eligible | 38 |
| Missing `assetnum` | 30 |
| Status before prefix | CAN 177 (88.5%), APPR 23 (11.5%) |
| Status after prefix | CAN 64 (94.1%), APPR 4 (5.9%) |
| Work Type after prefix | PM 45 (66.2%), CD 10 (14.7%), CM 6 (8.8%), PRO 2 (2.9%), S 2 (2.9%), EM/PDM/RTF 1 each (1.5%) |
| `changedate` after prefix | 2014-07-08 09:51:53–2026-08-21 10:56:54 +07:00 |
| Actual start / finish present | 2 / 0 |
| Asset present | 38 |
| Downtime > 0 / Labor > 0 | 0 / 0 |
| Order violations | 34 |
| Missing `changedate` | 0 |
| Duplicate identities | 0 |
| Adjacent timestamp ties | 150 |

#### Recent-first (`order_by=-changedate`)

| Metric | Result |
|---|---:|
| Source rows | 200 |
| Prefix matched / skipped | 19 / 181 |
| Canonical eligible | 19 |
| Missing `assetnum` | 0 |
| Status before prefix | INPRG 103 (51.5%), WDONE 97 (48.5%) |
| Status after prefix | INPRG 8 (42.1%), WDONE 11 (57.9%) |
| Work Type after prefix | PM 8 (42.1%), PDM 6 (31.6%), CD 3 (15.8%), CM 1 (5.3%), RTF 1 (5.3%) |
| `changedate` after prefix | 2026-08-21 16:05:21–17:04:30 +07:00 |
| Actual start / finish present | 19 / 0 |
| Asset present | 19 |
| Downtime > 0 / Labor > 0 | 0 / 0 |
| Order violations | 0 |
| Missing `changedate` | 0 |
| Duplicate identities | 4 |
| Adjacent timestamp ties | 161 |

The recent-first result is strictly non-increasing by `changedate` across the
returned source rows. The duplicate and tie counts are aggregate observability
only; no source identities are emitted. The high tie count means an incremental
implementation must use an overlap window and canonical-ID idempotency rather
than treating a timestamp boundary as a unique cursor position.

### MX-011W2 classification

Primary classification: **DEFAULT_ORDER_SAMPLING_BIAS**.

The comparable post-prefix CAN percentage changes from 94.1% in the default
slice to 0.0% in the recent-first slice. The recent slice instead contains
current operational statuses `INPRG` and `WDONE`, while the default slice is
dominated by `CAN`. Prefix interaction remains measurable, but it is not the
primary explanation: the default pre-prefix slice is already 88.5% CAN, and
recent-first has no CAN before or after prefix filtering.

### Watermark decision

`changedate` is **SUITABLE** as a candidate future Work Order incremental
watermark, subject to implementation controls:

- it was present on all eligible rows observed in both bounded profiles;
- descending ordering returned successfully within the bounded timeout;
- the recent sample was monotonic with zero order violations;
- eight-page bounded pagination completed;
- ties and four duplicate source identities were observed and are measurable;
- future sync must use overlap, tie-safe reconciliation, and canonical-ID
  idempotency.

No watermark synchronization was implemented in MX-011W2.

### MX-012R recommendation

1. Use a recent operational bootstrap ordered by `-changedate`, retaining all
   source statuses including `CAN`.
2. Run historical backfill separately, bounded by explicit operational policy
   or verified date windows; do not exclude status values.
3. Use a `changedate` incremental tail with overlap and canonical-ID
   reconciliation after the production strategy is reviewed.

This supports a representative recent bootstrap plus historical coverage and
does not turn NADI into a status-filtered view of incomplete ingestion.
