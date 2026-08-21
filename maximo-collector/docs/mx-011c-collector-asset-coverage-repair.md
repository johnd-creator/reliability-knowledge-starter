# MX-011C — Collector Asset Coverage Repair & Complete Current Baseline

Status: `PARTIAL`

The repair code and safety path are complete, but the current Maximo
`MXAPIASSET` population did not finish within the bounded live request budget.
The local progress is retained safely; no Asset cursor was created and the
partial run is explicitly auditable.

## Registry and pre-repair state

The external HTML-table report remained local and untracked throughout the
task.

- Sheet: `List of Assets`
- Rows: 845
- Unique Assets: 845
- Fingerprint:
  `aa0bd8fd22275aea3ecf8654ee37878106123b7dbdf58135fb783e853ee66a5f`
- Collector Equipment: 5,680
- Registry matches: 581
- Registry missing: 264
- Registry coverage: 68.8%
- Registry Parents present: 75 / 352
- `mxapiasset` cursor: absent
- `mxasset` cursor: absent
- Asset CollectRun history: none

Before repair, the recent 30-day local Work Order period contained 2,742
rows. It had 541 direct registry targets absent from local Equipment, one
category-D non-registry target missing, and 542 strict Equipment target gaps.
Historical direct registry targets absent locally totalled 6,437.

## Source safety and projection

The repair uses the existing `SyncService`, `equipment_from_payload`,
`CollectorStore`, and preferred `MXAPIASSET` source:

| Setting | Value |
| --- | --- |
| Object Structure | `MXAPIASSET` |
| Scope | `siteid="BSR"` |
| Required value | `eq11="CS01"` |
| Order | `-changedate` |
| Page size used | 50 |
| Max pages | 200 |
| Request budget per repair attempt | 150 |
| Max concurrency | 1 |
| Business methods | GET only |
| Response cap | 1 MiB |
| Cursor policy | create only after complete traversal with zero mapping errors |

The explicit scalar projection contains the existing approved Asset mapper
fields and approved Maximo extra fields. It avoids unrestricted raw payloads.

## Bounded probe results

The initial page-size-100 attempt returned an HTTP 200 response that exceeded
the 1 MiB response cap. It stopped before any row was written. A deliberate
adjustment was then tested once at page size 50:

- 50 source rows mapped successfully;
- zero missing required fields;
- zero scope violations;
- zero mapping errors;
- zero detail GETs;
- one business GET;
- bounded page correctly reported that another page exists.

A later page-size-75 probe also exceeded the response cap and stopped further
live repair attempts. Page size 50 is the largest page size verified safe in
this task.

## Partial baseline result

The page-size-50 baseline began after the successful page-size-50 probe. It
traversed 149 source pages and saw 7,450 source rows before the next request
was blocked by the hard budget. All 150 requests in that attempt returned
HTTP 200; there were no 429s, 5xx responses, timeouts, detail requests, or
scope violations.

| Metric | Result |
| --- | ---: |
| Source rows seen | 7,450 |
| Pages reached | 150 including the blocked next-page boundary |
| Equipment inserted | 2,429 |
| Equipment updated | 14 |
| Equipment upserted | 2,443 |
| Rows skipped | 5,007 |
| Mapping/transport errors | 1 budget interruption |
| Rows deleted | 0 |
| Cursor created | No |

The local Equipment population increased from 5,680 to 8,109. This is not
interpreted as a complete source count because the traversal was partial.

The database now records two `mxapiasset` CollectRuns, both `partial`: the
response-cap attempt with zero source rows and the later budget-bound attempt
with 7,450 source rows. There is still no `mxapiasset` cursor and no `mxasset`
cursor.

## Post-repair local reconciliation

| Metric | Before | After partial progress |
| --- | ---: | ---: |
| Collector Equipment | 5,680 | 8,109 |
| Registry exact matches | 581 | 823 |
| Registry missing | 264 | 22 |
| Registry coverage | 68.8% | 97.4% |
| Registry Parents present | 75 | 79 |
| Registry Parents missing | 277 | 273 |

The 22 remaining registry rows are not declared resolved because the source
traversal did not reach completion. Among matched rows, Parent agreement
remains exact: 823 of 823. No current registry row was hidden or deleted.

## Work Order validation after partial progress

The recent 30-day Work Order relationship profile now shows:

| Metric | Result |
| --- | ---: |
| Work Orders | 2,742 |
| With Equipment | 2,716 |
| Direct registry targets | 2,706 |
| Direct registry target absent locally | 61 |
| Non-registry target missing | 1 |
| Strict Equipment targets missing | 62 (2.3%) |

The partial repair reduced recent direct-registry absence from 541 to 61. It
did not repair the separate historical non-registry population: 29,149
non-registry targets remain missing in the >3-year bucket. That historical
lifecycle problem remains outside MX-011C.

Historical direct-registry absence fell from 6,437 to 620, but cannot be
declared zero until a complete current baseline is traversed.

## Cursor and CollectRun safety

- Cursor before: absent.
- Cursor after: absent.
- Cursor advanced during partial work: no.
- Complete traversal observed: no.
- Latest `mxapiasset` run mode: `partial`.
- Existing Equipment rows deleted: no.
- `mxasset` cursor changed: no.

The partial rows are valid local progress, but the local state must not be
treated as a complete current baseline.

## Next action

MX-011C remains incomplete. Do not start MX-012R yet.

The next controlled repair attempt should reuse the verified page-size-50
projection and receive an explicitly approved request budget large enough for
the measured source population, or use a separately verified bounded date
window strategy. It must still run one complete `MXAPIASSET` traversal,
establish the cursor only after exhaustion, and record a successful `full`
CollectRun. Do not switch to 22 individual Asset requests as the primary
repair and do not delete the safely collected Equipment rows.

## Mutation and privacy audit

- Maximo business writes: 0.
- Maximo business requests: 154 across bounded probe/repair attempts; every
  request was GET-only and each attempt honored its own budget.
- Collector Equipment inserts: 2,429.
- Collector Equipment updates: 14.
- Collector deletes: 0.
- Reliability Mart writes: 0.
- NADI changes: 0.
- Contract changes: 0.
- Production report and row-level production data: not committed.
- Credentials, cookies, identifiers, descriptions, and person fields: not
  emitted in evidence.

## MX-011C continuation

The continuation restarted from page 1 with the same external registry input
and the verified page-size-50 projection. The CLI upper bound was extended
only to permit an explicit continuation budget of 210; its default remains
150 and no unbounded option was added.

| Setting | Continuation result |
| --- | ---: |
| Object Structure | `MXAPIASSET` |
| Scope | `siteid="BSR"` and `eq11="CS01"` |
| Order | `-changedate` |
| Page size | 50 |
| Max pages | 200 |
| Request budget | 210 |
| Projection probe | 50 rows, mapping-safe, zero detail GETs |
| Business requests | 201 (one probe plus 200 source pages) |
| HTTP 200 | 201 |
| HTTP 429 / 5xx / timeout | 0 / 0 / 0 |
| Response-cap violations | 0 |
| Source rows seen | 10,000 |
| Equipment inserted | 2,529 |
| Equipment updated | 4 |
| Equipment skipped | 7,467 |
| Equipment deleted | 0 |

At page 200 the source still advertised another page. The existing bounded
pagination guard therefore recorded `OslcPaginationLimitError` and marked the
run `partial`. This is not natural source exhaustion. No residual per-Asset
verification was attempted, no cursor was created, and the prior partial runs
remain preserved.

Post-continuation local reconciliation:

- Equipment: 8,109 → 10,638.
- Registry matches: 823 / 845.
- Registry missing: 22.
- Registry coverage: 97.4%.
- Registry Parents: 79 / 352; 273 remain absent.
- Recent direct registry Work Order targets missing locally: 61.
- Recent non-registry target missing: 1.
- Recent strict Equipment target gaps: 62.
- Historical direct registry targets missing locally: 620.
- Historical non-registry gaps remain out of scope.

The 2,529 new rows did not recover the remaining 22 registry rows; they are
additional Equipment discovered within the bounded source traversal. The
current registry baseline is therefore still not complete or trustworthy, and
MX-012R remains blocked. A future continuation must explicitly address the
source population beyond the 10,000-row ceiling or use a separately verified
bounded date-window strategy. No additional live attempt was made in this
task.

Continuation safety audit:

- Cursor before and after: absent.
- Complete traversal: no.
- Latest `mxapiasset` CollectRun: `partial`, 10,000 rows, 2,533 upserted,
  7,467 skipped, one pagination-boundary error.
- Maximo business writes: 0; all business requests were GET-only.
- Reliability Mart, NADI, Contract, and `mxasset` cursor: unchanged.
- The production registry report remained external and untracked.
