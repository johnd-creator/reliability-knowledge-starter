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
| Maintenance work-type distribution | `DERIVED_SAFE` | Count grouped by quarantined source `sources.maximo.worktype`; fall back to canonical `event_type`, then `UNKNOWN` only when both are absent | Selected bounded window; canonical `event_type` is conservative and does not represent every source Work Type. Raw values such as `PDM`, `CD`, and `OH` remain source values. |
| Assets with highest Maintenance Activity | `DERIVED_SAFE` | Group Registry-scoped events by registered Asset and order by count descending, latest activity descending, then stable Asset identifiers | Selected bounded window; “high activity” is an investigation signal, not a bad-actor, risk, or condition ranking. |
| Weekly Maintenance Activity Trend | `DERIVED_SAFE` | Twelve backend aggregate weekly counts of Registry-scoped events | Weekly buckets use the same activity date basis; no client-side event download. |
| FMEA records available | `VERIFIED` | Count of current scoped `fmea_assessment` rows | Current controlled Mart population; not full FMEA completion. |
| Assets represented in current FMEA population | `DERIVED_SAFE` | Distinct non-null FMEA Asset refs that resolve to the Registry | Current controlled dataset representation; not an FMEA completion percentage. |
| Asset Health records available | `VERIFIED` | Count of current scoped `asset_health_assessment` rows | Current controlled Mart population; lifecycle status is not converted into a score. |
| Assets represented in current Asset Health population | `DERIVED_SAFE` | Distinct non-null Asset Health refs that resolve to the Registry | Current controlled dataset representation; not health coverage or condition. |
| Assets with multiple Asset Health assessments | `DERIVED_SAFE` | Registered Assets with two or more current Asset Health records | Record multiplicity only; matching Asset identity does not prove assessment lineage or revision history. |
| Latest Asset Health assessment record | `DERIVED_SAFE` | Latest record per Asset ordered by `COALESCE(status_changed_at, source_updated_at, source_created_at)` | Assessment record date; not condition measured-at time. |
| Assessment age | `DERIVED_SAFE` | `as_of - latest assessment record date` | Record recency only; no freshness, staleness, deterioration, or health meaning is assigned. |
| Asset Health lifecycle status | `VERIFIED` | Raw `lifecycle_status` preserved exactly, with null shown as `UNKNOWN` | Source status only; business meaning is unverified and is not mapped to Healthy, Warning, Critical, Open, or Closed. |
| RCFA records available | `VERIFIED` | Count of current scoped `rcfa_analysis` rows | Global factual count; RCFA Asset relationship remains unresolved. |
| Overhaul records available | `VERIFIED` | Count of current scoped `overhaul_event` rows | Global factual count; null/unresolved Asset refs remain unresolved. |
| Relationship integrity | `VERIFIED` | Existing Mart relationship totals and resolved/unresolved counts | Factual relationship checks; not a health score. |
| Registry completeness | `VERIFIED` | Registry rows resolved to `asset_master` versus total Registry rows | Relationship integrity for the current snapshot; not historical completeness. |

## Maintenance Investigation metrics

The investigation surface uses the same Registry join and factual activity date
as the Executive Overview. Its bounded windows are 30, 90, and 180 days; the
default is 90 days. Results are aggregated in SQL and paginated before they
reach the browser.

| Candidate | Class | Definition / formula | Boundary |
| --- | --- | --- | --- |
| Assets with 2+ Activity | `DERIVED_SAFE` | Registered Assets with at least two Maintenance Events in the selected window | Event repetition is an activity observation, not repeat failure, condition, or risk. |
| Assets with 3+ Activity | `DERIVED_SAFE` | Registered Assets with at least three Maintenance Events in the selected window | Same boundary; the threshold is an allowlisted investigation filter. |
| Repeat Activity Events | `DERIVED_SAFE` | `MAX(event_count - 1, 0)` per Asset, summed over the selected window | Events beyond the first observed event; no failure identity is inferred. |
| Maintenance Event count per Asset | `DERIVED_SAFE` | Count of Registry-scoped events grouped by registered Asset | Bounded selected window; technical non-Registry rows are excluded. |
| Consecutive Activity Gap | `DERIVED_SAFE` | Descriptive interval in days between consecutive activity dates; latest and minimum gaps are exposed | Uses `COALESCE(actual_start, source_changed_at)` and is not a rapid-failure or repair-duration measure. |
| Same Work-Type Activity | `DERIVED_SAFE` | Raw source Work Type counts per Asset, with latest and dominant Work Type | Repeated `PM`, `CM`, or another source Work Type does not establish failure. |
| Repeat Failure | `BUSINESS_SEMANTICS_REQUIRED` | Not implemented | Requires verified failure identity, failure-code meaning, qualifying Work Types/statuses, occurrence and repair semantics, interval rules, parent/child treatment, and business-owner validation. Current Mart failure-code coverage is unavailable. |

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
| Repeat Failure | `BUSINESS_SEMANTICS_REQUIRED` | Collector failure codes exist locally, but are not promoted into the Mart and their business meaning is unverified; a failure identity and governed repeat rule are still required. |
| PdM alerts | `DATA_NOT_AVAILABLE` | PI/DCS signals are not part of the current NADI decision model. |
| Recommendations | `DEFERRED` | No verified action rules or governance; no Action Board is generated here. |
| Health Score | `BUSINESS_SEMANTICS_REQUIRED` | No verified numerical source, normalization, directionality, thresholds, missing-data treatment, or governance. |
| Wellness Score | `BUSINESS_SEMANTICS_REQUIRED` | The local report contains a `Last Wellness` column, but its relationship to IPBHM and its calculation semantics are not verified. |
| Condition Classification | `BUSINESS_SEMANTICS_REQUIRED` | Source descriptions/statuses are available, but no verified condition taxonomy or mapping exists. |

`CAN`, `APPR`, `INPRG`, `WDONE`, and other source statuses remain source values.
They are not filtered or assigned management meanings by this overview.
