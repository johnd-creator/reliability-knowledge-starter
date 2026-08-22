# NADI Maintenance Investigation Semantics

## Purpose

Maintenance Investigation answers a bounded factual question: what repeated
Maintenance Activity is observed on Registered Reliability Assets in a selected
period? It is an investigation signal, not a failure, condition, risk, or
recommendation surface.

## Scope and date basis

- Site and organization are fixed to `BSR` / `IP`.
- The business Asset boundary is `reliability_asset_registry`.
- Maintenance rows are included only when `maintenance_event.equipment_id`
  resolves to a Registry Asset.
- Activity date is `COALESCE(actual_start, source_changed_at)`.
- Historical local Work Orders commonly have no `actual_start`, so the
  fallback is source change time. It is not execution, failure, repair, or
  completion time.
- Analysis windows are allowlisted to 30, 90, and 180 days; the default is 90.

## Repeat Activity definition

Repeat Activity means multiple Registry-scoped Maintenance Events belonging to
the same Registered Reliability Asset within the selected bounded period.

For an Asset with `event_count` events:

```text
repeat_activity_events = MAX(event_count - 1, 0)
```

The API also reports latest activity, previous activity, the latest descriptive
gap, the minimum consecutive gap, and the event count per Asset. These are
descriptive temporal aggregates. No interval threshold is labelled rapid,
chronic, or problematic.

The product banner is intentional:

> Repeat Activity means more than one Maintenance Event on the same Asset
> within the selected period. It does not by itself mean repeat failure.

## Work Type source and status boundary

Reporting prefers `sources.maximo.worktype`, then falls back to canonical
`event_type`, then `UNKNOWN`. The raw source Work Type is preserved in the
quarantined source payload. Canonical Contract v1 `event_type` is conservative;
values such as `PDM`, `CD`, `OH`, `EM`, `PRO`, `RTF`, and `S` may be present in
the source without being representable by that enum. This is not treated as
bad data and the Contract is not expanded by this task.

Source statuses remain source values, including `CAN`, `APPR`, `INPRG`, and
`WDONE`. No status is translated to success, failure, open, closed, backlog,
or overdue.

## Failure-code coverage gate

The local Collector Work Order store has populated `failure_code` values, but
the current local Mart `maintenance_event.failure_code` population is empty.
The field's business meaning and its relationship to a verified failure event
are also unverified. Therefore:

- failure code is available in the Collector: **YES**;
- failure code is available in the Mart: **NO**;
- failure-code business semantics: **UNVERIFIED**;
- Repeat Failure ready: **NO**.

No failure-code promotion or Mart re-projection is performed in NADI-004.

## Local evidence audit

The aggregate-only audit of the local snapshot on 2026-08-22 found:

| Measure | Result |
| --- | ---: |
| Mart Maintenance Events | 68,000 |
| Registry-scoped Maintenance Events | 35,259 |
| Registry-scoped activity date available | 35,259 |
| `actual_start` present | 0 |
| `source_changed_at` present | 35,259 |
| Both activity dates missing | 0 |
| Canonical `event_type` populated | 20,134 |
| Canonical `event_type` NULL | 15,125 |
| Raw source Work Type populated | 35,259 |
| Distinct raw source Work Types | 9 |
| Collector `failure_code` populated | 62,330 |
| Mart `failure_code` populated | 0 |
| Collector descriptions populated | 111,391 |

The seven raw Work Types not represented by the conservative canonical enum
were `CD`, `EM`, `OH`, `PDM`, `PRO`, `RTF`, and `S`. Registry-scoped raw Work
Type counts were `CD` 6,515, `CM` 1,493, `EM` 81, `OH` 975, `PDM` 6,939,
`PM` 18,641, `PRO` 31, `RTF` 471, and `S` 113. These are source activity
values, not failure categories.

Registry-scoped source status counts were `APPR` 4, `CAN` 185, `CLOSE`
33,792, `COMP` 17, `INPRG` 65, `PLANTOK` 25, `SCHED-OK` 81, `WAPPR` 40,
`WDONE` 18, `WMATL` 371, `WPCOND` 34, and `WSCH` 627. `CAN` remains included
and is not assigned a quality or failure meaning.

## Potential sequence duplication

Collector rows contain task/parent/child indicators, but those semantics are
not exposed in the current Maintenance Contract or Mart analysis model. A
parent and its task rows could therefore contribute separate observed events.
This is recorded as `POTENTIAL_SEQUENCE_DUPLICATION`; the task does not apply
an unverified deduplication rule.

## Why Repeat Activity is not Repeat Failure

Repeated events may represent preventive work, inspections, planned work,
administrative updates, or other source Work Types. Event count does not prove
that the same failure occurred, that a repair failed, or that an Asset is a bad
actor or high risk. The UI therefore uses Maintenance Activity, Activity
Concentration, and investigation language only.

## Requirements before using “Repeat Failure”

The phrase should remain gated until a business owner validates all of the
following:

- a verified failure-event identity;
- failure-code meaning and hierarchy;
- which Work Types represent failures;
- which source statuses qualify;
- a failure occurrence timestamp;
- repair completion semantics;
- a repeat interval rule;
- treatment of planned PM;
- treatment of cancelled Work Orders;
- treatment of parent/child Work Orders;
- business-owner validation and acceptance criteria.

Until then, `Repeat Failure` is classified
`BUSINESS_SEMANTICS_REQUIRED` and is not shown as a product KPI.
