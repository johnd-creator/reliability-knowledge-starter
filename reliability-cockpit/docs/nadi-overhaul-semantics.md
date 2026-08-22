# NADI Overhaul Semantics

## Purpose and boundary

NADI-008 presents the current `IP_DOM_OH` Mart population as factual Overhaul
execution evidence. It does not calculate schedule performance, delay,
completion, project health, or risk KPIs.

The normal workspace keeps source identity, Work Order relationship, local Mart
resolution, and Asset resolution separate. An unresolved relationship is
visible as unresolved; it is not treated as invalid source data.

## Verified source fields

| Source field | Canonical field | Product boundary |
| --- | --- | --- |
| `domid` | `source_record_id` | Technical/source record identity. |
| `domohnum` | `source_number` | Human-facing Overhaul Number. |
| `status` | `lifecycle_status` | Raw source status; business meaning is unverified. |
| `wonum` | `workorder_ref` | Direct verified Work Order relationship. |
| `tgl_mulai` / `tgl_selesai` | `planned_start_at` / `planned_finish_at` | Planned source timestamps. |
| `tgl_actual_mulai` / `tgl_actual_selesai` | `actual_start_at` / `actual_finish_at` | Actual source timestamps. |
| `progress` | `progress` | Raw source value; scale is unverified. |
| `createdate` / `changedate` | `source_created_at` / `source_updated_at` | Source timestamps. |
| `inspeksinum` | `unresolved_source_attributes.inspection_number` | Source attribute; relationship is unverified. |
| `perfomance_test` | `unresolved_source_attributes.performance_test` | Source attribute; meaning and relationship are unverified. |

The approved source Work Order number is preserved under
`sources.maximo.wonum` and is used as the normal UI identity when available.
The canonical `workorder_ref` remains internal/secondary.

## Local evidence audit

Aggregate-only local Mart evidence on 2026-08-22:

| Measure | Result |
| --- | ---: |
| Overhaul records | 1 |
| `source_record_id` present / unique | 1 / 1 |
| Overhaul Number present / unique | 1 / 1 |
| Observed lifecycle status | `EKS-COMP` (1) |
| Work Order reference present | 1 |
| Work Order reference resolved in `maintenance_event` | 0 |
| Work Order reference unresolved in local Mart | 1 |
| Asset reference present | 0 |
| Asset reference absent | 1 |
| Asset resolved to `asset_master` | 0 |
| Registered Asset resolved | 0 |
| Technical non-Registry Asset | 0 |
| Planned Start / Finish present | 1 / 1 |
| Actual Start / Finish present | 1 / 1 |
| Planned / Actual duration available | 1 / 1 |
| Progress present | 1 |
| Progress observed range | 45.28 to 45.28 |
| Source Created / Updated present | 1 / 1 |
| Inspection number present | 1 |
| Performance test present | 1 |

The current population is a controlled Mart population. These numbers do not
establish complete Overhaul history or plant-wide execution coverage.

## Relationship semantics

The direct source relationship is verified:

```text
IP_DOM_OH.wonum -> MXWODETAIL.wonum
```

The Asset relationship is only accepted through the verified derived path:

```text
IP_DOM_OH.wonum
  -> MXWODETAIL.wonum
  -> MXWODETAIL.assetnum
  -> asset_master
  -> reliability_asset_registry (when it is a Registered Asset)
```

The query layer does not derive a new Asset link. It checks the existing Mart
`asset_ref`. Therefore the current record is globally visible, while it does
not enter an Asset-specific context because its Asset reference is null.

The product distinguishes:

- `SOURCE_LINK_VERIFIED_AND_MART_RESOLVED`;
- `SOURCE_LINK_VERIFIED_BUT_MART_UNRESOLVED`;
- `SOURCE_WORK_ORDER_MISSING`.

For Asset resolution it distinguishes Registered Asset, technical non-Registry
context, and unresolved context.

## Dates, duration, and progress

Planned and actual values are displayed with those source labels. When both
endpoints exist, the workspace may derive factual intervals:

```text
planned_duration_days = planned_finish_at - planned_start_at
actual_duration_days = actual_finish_at - actual_start_at
```

These are `DERIVED_SAFE` timestamp intervals. They are not schedule variance,
delay, overrun, outage duration, efficiency, or completion measures.

`progress` is a `VERIFIED_RAW_SOURCE` value. The observed value is shown as
`45.28` without a percentage suffix. `PROGRESS_SCALE: UNVERIFIED`; no
assumption is made that the field is a 0–100 percentage.

Lifecycle status remains a neutral raw source value. `EKS-COMP` is not mapped
to Planned, Running, Completed, Delayed, Successful, or Failed.

## Unresolved source attributes

The current record retains both an inspection number and a performance-test
source attribute. Their presence does not prove a relationship to inspection
result objects, performance-test results, or efficiency outcomes. No result
or pass/fail interpretation is exposed.

## Semantic gates

```text
OVERHAUL_RECORD: VERIFIED
WORKORDER_RELATIONSHIP: VERIFIED
ASSET_DIRECT_RELATIONSHIP: NO
ASSET_DERIVED_RELATIONSHIP: VERIFIED WHEN PATH RESOLVES
LIFECYCLE_STATUS: RAW SOURCE
PLANNED_DURATION: DERIVED_SAFE
ACTUAL_DURATION: DERIVED_SAFE
SCHEDULE_VARIANCE_READY: NO
PROGRESS_KPI_READY: NO
OVERHAUL_COMPLETION_KPI_READY: NO
INSPECTION_RELATIONSHIP_READY: NO
PERFORMANCE_TEST_SEMANTICS_READY: NO
```

## Future office-network discovery

Future bounded discovery must verify:

- what each Dominion lifecycle status means;
- whether Progress uses a 0–100 percentage scale;
- what defines Overhaul completion;
- whether planned/actual dates are workflow dates or outage boundaries;
- what `inspeksinum` relates to;
- what `perfomance_test` references;
- how `DOM_INSPEKSIMESIN` relates to `IP_DOM_OH`;
- whether additional Overhaul scope/detail objects exist;
- whether one Overhaul can have multiple Work Orders.

No source discovery or population expansion is part of NADI-008.
