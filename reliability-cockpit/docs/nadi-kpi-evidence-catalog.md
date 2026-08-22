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

## FMEA assessment workspace metrics

The FMEA workspace uses the current `IPFMEA` controlled Mart population and
joins `fmea_assessment.asset_ref` to `reliability_asset_registry.asset_ref` for
the normal product view. Technical and unresolved records remain in the Mart
and are reported as relationship evidence, not silently reclassified.

| Candidate | Class | Definition / formula | Boundary |
| --- | --- | --- | --- |
| FMEA records | `VERIFIED` | Count of current scoped `fmea_assessment` rows | Controlled Mart population; not full FMEA history or completion. |
| Registered Assets represented in FMEA | `DERIVED_SAFE` | `COUNT(DISTINCT asset_ref)` after the Registry join | Representation only; not FMEA coverage, completion, or compliance. |
| Assets with multiple FMEA records | `DERIVED_SAFE` | Registered Assets with at least two FMEA records | Record multiplicity only; no risk or condition interpretation. |
| FMEA record date | `DERIVED_SAFE` | `COALESCE(status_changed_at, source_updated_at)` | Factual source timestamp fallback; not approval date, failure date, or risk review date. |
| FMEA record age | `DERIVED_SAFE` | `as_of - FMEA record date` | Record recency only; no stale, due, or risk threshold is applied. |
| Lifecycle status | `VERIFIED` | Raw `lifecycle_status`, with null shown as `UNKNOWN` | Source status only; business meanings such as Approved or Current are unverified. |
| Revision | `VERIFIED` | Raw `revision` distribution | Source value; revision lineage and “latest approved revision” semantics are unverified. |
| Failure Code present | `VERIFIED` | Count of non-empty approved source `sources.maximo.failurecode` values | Source evidence only; hierarchy and failure-mode meaning are not asserted. |
| Failure Mode details | `DATA_NOT_AVAILABLE` | No IPFMEAITEM child population is available in the current dataset | Item details remain deferred. |
| RPN | `BUSINESS_SEMANTICS_REQUIRED` | Not implemented | Requires verified Severity, Occurrence, Detectability, scales, formula, thresholds, and governance. |
| Risk classification | `BUSINESS_SEMANTICS_REQUIRED` | Not implemented | No verified risk taxonomy, inputs, or business thresholds. |

## RCFA global analysis metrics

The RCFA workspace is intentionally global. `rcfa_analysis` has no verified
Asset, Work Order, or Failure Event relationship in Contract v1, so the normal
surface does not show Asset statistics or links and does not connect RCFA to
Maintenance, FMEA, or Repeat Activity.

| Candidate | Class | Definition / formula | Boundary |
| --- | --- | --- | --- |
| RCFA records | `VERIFIED` | Count of current scoped `rcfa_analysis` rows | Controlled Mart population; not all RCFA history or compliance. |
| RCFA Status Distribution | `DERIVED_SAFE` | Count grouped by raw `lifecycle_status`, with null shown as `UNKNOWN` | Source status only; no Open/Closed/Approved/Completed mapping. |
| RCFA Category Distribution | `DERIVED_SAFE` | Count grouped by raw `category`, with null shown as `UNKNOWN` | Source value only; category taxonomy is unverified. |
| RCFA Revision Distribution | `VERIFIED` | Count grouped by raw `revision`, with null shown as `UNKNOWN` | Revision lineage and approval semantics are unverified. |
| RCFA Record Age | `DERIVED_SAFE` | `as_of - requested_at` | Current population has no `source_created_at`; age means request-record recency only. |
| Request-to-created gap | `DATA_NOT_AVAILABLE` | Not exposed because no current record has both timestamps | Not a response-time, investigation-delay, or SLA metric. |
| RCFA by Asset | `DATA_NOT_AVAILABLE` | Not implemented; `asset_ref` relationship is unresolved | No fuzzy, text, date, number, FMEA, or Work Order join. |
| RCFA Completion | `BUSINESS_SEMANTICS_REQUIRED` | Not implemented | Requires verified completion status meanings and governance. |
| Root Cause category | `BUSINESS_SEMANTICS_REQUIRED` | Not interpreted from raw `category` | Requires verified taxonomy and root-cause field semantics. |
| Corrective Action completion | `DATA_NOT_AVAILABLE` | No approved action/completion fields in the current RCFA contract | Requires a verified related source object and completion rule. |

## Overhaul execution metrics

The Overhaul workspace uses the existing `IP_DOM_OH` population. Its Work
Order relationship is direct verified source evidence; its Asset relationship
is accepted only when the already-projected Work Order path resolves locally.

| Candidate | Class | Definition / formula | Boundary |
| --- | --- | --- | --- |
| Overhaul records | `VERIFIED` | Count of current scoped `overhaul_event` rows | Controlled Mart population; not all Overhaul history or compliance. |
| Records with Work Order | `VERIFIED` | Count of rows with `workorder_ref` | Source relationship present; not proof of local Mart resolution. |
| Work Order Mart resolution | `VERIFIED` | `workorder_ref` matches scoped `maintenance_event.work_order_id` | Resolution is measured separately from the direct source relationship. |
| Registered Assets resolved | `VERIFIED` | Existing `asset_ref` resolves through the verified Work Order path to `reliability_asset_registry` | No direct Overhaul-to-Asset inference; unresolved rows remain global only. |
| Planned Duration | `DERIVED_SAFE` | `planned_finish_at - planned_start_at` when both exist | Timestamp interval only; not schedule adherence or delay. |
| Actual Duration | `DERIVED_SAFE` | `actual_finish_at - actual_start_at` when both exist | Timestamp interval only; not efficiency or outage duration. |
| Progress Value | `VERIFIED` | Raw `progress` value preserved from source | Scale and percentage meaning are unverified; no `%` suffix. |
| Schedule Variance | `BUSINESS_SEMANTICS_REQUIRED` | Not implemented | Planned/actual boundaries, status rules, partial work, cancellation, timezone, and governance are unverified. |
| Overhaul Completion | `BUSINESS_SEMANTICS_REQUIRED` | Not implemented | Raw lifecycle status is not mapped to completion. |
| Inspection Number | `VERIFIED` | Presence of `unresolved_source_attributes.inspection_number` | Source attribute only; relationship to inspection records is unverified. |
| Inspection Result | `DATA_NOT_AVAILABLE` | Not implemented | No verified inspection-result relation in the current contract. |
| Performance Test | `BUSINESS_SEMANTICS_REQUIRED` | Presence of `unresolved_source_attributes.performance_test` | Source spelling/value is preserved; meaning and relation are unverified. |

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
