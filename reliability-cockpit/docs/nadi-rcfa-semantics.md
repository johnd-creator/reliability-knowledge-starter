# NADI RCFA Semantics

## Purpose and boundary

NADI-007 presents the current `IPRCFA` Mart population as a factual global
Reliability analysis workspace. It does not infer an Asset, Work Order, or
Failure Event relationship and does not fabricate root-cause details,
corrective actions, recommendations, or completion KPIs.

The current canonical relationship fields remain null:

```text
asset_ref = NULL
location_ref = NULL
workorder_ref = NULL
failure_event_ref = NULL
```

Their relationship evidence remains `UNRESOLVED`. No text, date, number,
FMEA, Maintenance, or temporal matching is used to create a relationship.

## Verified source fields

The approved contract maps these `IPRCFA` fields:

| Source field | Canonical field | Product boundary |
| --- | --- | --- |
| `rcfaid` | `source_record_id` | Technical source record identity. |
| `norcfa` | `source_number` | Human-facing RCFA number. |
| `revisi` | `revision` | Raw revision value. |
| `status` | `lifecycle_status` | Raw source status; business meaning is unverified. |
| `kategori` | `category` | Raw source category; taxonomy is unverified. |
| `createddate` | `source_created_at` | Source timestamp. |
| `req_date` | `requested_at` | Source request timestamp. |

The normal UI uses RCFA Number and keeps `source_record_id` secondary. The
canonical ID is not used as the primary business label.

## Local evidence audit

Aggregate-only local Mart evidence on 2026-08-22:

| Measure | Result |
| --- | ---: |
| RCFA records | 100 |
| `source_record_id` present | 100 |
| `source_record_id` unique | 100 |
| RCFA number present | 100 |
| RCFA number unique | 100 |
| Revision present | 100 |
| Distinct revisions | 3 (`0`, `1`, `2`) |
| Category present | 100 |
| Requested date present | 91 |
| Source created date present | 0 |
| Both timestamps present | 0 |
| Both timestamps missing | 9 |

There are no duplicate RCFA numbers and no RCFA number with multiple revisions
in this snapshot. This does not establish a general revision lineage rule.

`REVISION_LINEAGE: UNVERIFIED`.

## Status and category semantics

Observed raw lifecycle statuses:

| Raw status | Count | Interpretation |
| --- | ---: | --- |
| `CLOSE` | 97 | Unverified source status |
| `KAJDONE` | 1 | Unverified source status |
| `VEROK` | 2 | Unverified source status |

Observed raw categories:

| Raw category | Count | Interpretation |
| --- | ---: | --- |
| `1` | 50 | Unverified source category value |
| `2` | 17 | Unverified source category value |
| `3` | 10 | Unverified source category value |
| `4` | 2 | Unverified source category value |
| `5` | 15 | Unverified source category value |
| `6` | 4 | Unverified source category value |
| `8` | 2 | Unverified source category value |

Status and category use neutral styling. NADI does not map them to Open,
Closed, Approved, Completed, Rejected, In Progress, failure mechanism, cause
category, risk category, or equipment category.

`CATEGORY_SOURCE_VALUE: VERIFIED`

`CATEGORY_BUSINESS_TAXONOMY: UNVERIFIED`

## Timestamp and record age semantics

All 100 current records have no `source_created_at`; 91 have `requested_at`.
Because the created-date field is unavailable in this population, the factual
workspace uses this explicit rule:

```text
RCFA record date = requested_at
```

It does not silently coalesce with `source_created_at`. The label is **RCFA
record date** or **Requested date**, not failure date, investigation start,
analysis completion, response time, or SLA date.

RCFA record age is:

```text
as_of - requested_at
```

It is `DERIVED_SAFE` and means source request-record recency only. No overdue,
stale, or completion threshold is applied.

The request-to-created interval is not exposed. Since no record has both
timestamps, its evidence class is `DATA_NOT_AVAILABLE`.

Oldest requested date: 2015-06-04 01:35:24 UTC. Latest requested date:
2021-07-27 03:05:58 UTC. Created-date bounds are unavailable.

## Relationship gates

| Relationship | Status | Product treatment |
| --- | --- | --- |
| RCFA → Asset | `UNRESOLVED` | No Asset filter, link, coverage, or Asset count. |
| RCFA → Work Order | `UNRESOLVED` | No Work Order filter or Maintenance join. |
| RCFA → Failure Event | `UNRESOLVED` | RCFA is not called a failure event. |

`ROOT_CAUSE_DETAILS_AVAILABLE: NO`.

The current contract has no verified root-cause statement, causal tree, 5-Why
details, corrective action, recommendation, responsible person, action due
date, or action completion fields.

## Future discovery requirements

Future office-network discovery must verify, rather than infer:

- which IPRCFA field or related object links an Asset;
- which field links a Work Order;
- which related object stores root-cause detail;
- which related object stores recommendations and actions;
- lifecycle status meanings;
- category taxonomy;
- what defines RCFA completion;
- how revisions relate to one RCFA analysis.

Until those questions are answered by approved evidence, the following remain
closed:

```text
ROOT_CAUSE_TAXONOMY_READY: NO
RCFA_COMPLETION_KPI_READY: NO
```
