# NADI KPI evidence catalog

This catalog is the gate for metrics shown in NADI. A metric is not exposed
because it is visually useful; it must have a definition, source entities,
scope, time basis, formula, limitation, maturity, and interpretation boundary.

## Evidence classes

| Class | Meaning |
| --- | --- |
| `VERIFIED` | Direct factual Mart/Registry count or an already verified relationship. |
| `DERIVED_SAFE` | Transparent aggregation that does not imply reliability causality. |
| `BUSINESS_SEMANTICS_REQUIRED` | Data exists, but its management meaning is not verified. |
| `DATA_NOT_AVAILABLE` | Required source fields are unavailable. |
| `DEFERRED` | Intentionally postponed from the current product stage. |

## Implemented in the Executive Overview

All implemented activity metrics use the `BSR` / `IP` scope and join
`maintenance_event.equipment_id` to `reliability_asset_registry.asset_ref`.
Technical `asset_master` rows without a Registry relationship are excluded
from normal Asset and Maintenance metrics.

| Candidate | Class | Definition / formula | Time basis and boundary |
| --- | --- | --- | --- |
| Registered Reliability Assets | `VERIFIED` | `COUNT(reliability_asset_registry.asset_ref)` | Current Registry snapshot; factual business Asset boundary. |
| Maintenance Events | `VERIFIED` | Count of Registry-scoped `maintenance_event` rows | Current Mart population; not a complete historical claim. |
| Maintenance Activity — 7 days | `DERIVED_SAFE` | Count of Registry-scoped events where `COALESCE(actual_start, source_changed_at)` is in the last 7 days | Calendar interval ending at query time; activity, not failure or condition. |
| Maintenance Activity — 30 days | `DERIVED_SAFE` | Same count over 30 days | Same date basis; default decision window. |
| Maintenance Activity — 90 days | `DERIVED_SAFE` | Same count over 90 days | Same date basis; bounded trend context. |
| Assets with Maintenance Activity — 30 days | `DERIVED_SAFE` | `COUNT(DISTINCT equipment_id)` in the Registry-scoped 30-day event set | Registered Asset references only; not Asset coverage or health. |
| Assets with Maintenance Activity — 90 days | `DERIVED_SAFE` | `COUNT(DISTINCT equipment_id)` in the Registry-scoped 90-day event set | Registered Asset references only; not Asset coverage or health. |
| Maintenance status distribution | `DERIVED_SAFE` | Count grouped by source `status`, with null shown as `UNKNOWN` | Selected 7/30/90-day window; values are preserved exactly, including `CAN`. No Open/Closed/Backlog mapping. |
| Maintenance work-type distribution | `DERIVED_SAFE` | Count grouped by canonical `event_type`, which preserves source `worktype`; null shown as `UNKNOWN` | Selected bounded window; no normalization beyond the verified source mapping. |
| Assets with highest Maintenance Activity | `DERIVED_SAFE` | Group Registry-scoped events by registered Asset and order by count descending, latest activity descending, then stable Asset identifiers | Selected bounded window; “high activity” is an investigation signal, not a bad-actor, risk, or condition ranking. |
| Weekly Maintenance Activity Trend | `DERIVED_SAFE` | Twelve backend aggregate weekly counts of Registry-scoped events | Weekly buckets use the same activity date basis; no client-side event download. |
| FMEA records available | `VERIFIED` | Count of current scoped `fmea_assessment` rows | Current controlled Mart population; not full FMEA completion. |
| Assets represented in current FMEA population | `DERIVED_SAFE` | Distinct non-null FMEA Asset refs that resolve to the Registry | Current controlled dataset representation; not an FMEA completion percentage. |
| Asset Health records available | `VERIFIED` | Count of current scoped `asset_health_assessment` rows | Current controlled Mart population; lifecycle status is not converted into a score. |
| Assets represented in current Asset Health population | `DERIVED_SAFE` | Distinct non-null Asset Health refs that resolve to the Registry | Current controlled dataset representation; not health coverage or condition. |
| RCFA records available | `VERIFIED` | Count of current scoped `rcfa_analysis` rows | Global factual count; RCFA Asset relationship remains unresolved. |
| Overhaul records available | `VERIFIED` | Count of current scoped `overhaul_event` rows | Global factual count; null/unresolved Asset refs remain unresolved. |
| Relationship integrity | `VERIFIED` | Existing Mart relationship totals and resolved/unresolved counts | Factual relationship checks; not a health score. |
| Registry completeness | `VERIFIED` | Registry rows resolved to `asset_master` versus total Registry rows | Relationship integrity for the current snapshot; not historical completeness. |

## Evaluated but not exposed as decision KPIs

| Candidate | Class | Missing evidence or boundary |
| --- | --- | --- |
| MTBF | `BUSINESS_SEMANTICS_REQUIRED` | Requires a verified failure-event definition, operating exposure, and censoring rules. Maintenance activity alone is not failure data. |
| MTTR | `BUSINESS_SEMANTICS_REQUIRED` | Requires verified failure start/end semantics and repair completion semantics; `actual_start` is not sufficient. |
| Availability | `DATA_NOT_AVAILABLE` | Requires verified operating-time and outage boundaries, not only maintenance events. |
| Health Score | `BUSINESS_SEMANTICS_REQUIRED` | Asset Health lifecycle/status semantics and scoring method are not verified. |
| Risk Score | `DATA_NOT_AVAILABLE` | No verified risk formula, consequence/likelihood inputs, or threshold policy. |
| Reliability Score | `DEFERRED` | Intentionally postponed until reliability formulas and business semantics are verified. |
| Bad Actor ranking | `DEFERRED` | Activity concentration is available only as an investigation signal; no bad-actor rule is verified. |
| Critical Asset count | `BUSINESS_SEMANTICS_REQUIRED` | Criticality field and management threshold semantics require verification. |
| Backlog | `BUSINESS_SEMANTICS_REQUIRED` | Source status semantics are not verified for Open/Closed/Overdue/Backlog mapping. |
| Repeat Failure | `DATA_NOT_AVAILABLE` | Requires verified failure identity and repeat window rules. |
| PdM alerts | `DATA_NOT_AVAILABLE` | PI/DCS signals are not part of the current NADI decision model. |
| Recommendations | `DEFERRED` | No verified action rules or governance; no Action Board is generated here. |

`CAN`, `APPR`, `INPRG`, `WDONE`, and other source statuses remain source values.
They are not filtered or assigned management meanings by this overview.
