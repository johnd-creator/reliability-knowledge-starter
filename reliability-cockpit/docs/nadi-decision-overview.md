# NADI Executive Overview

## Purpose

The Executive Overview is the first bounded Reliability Cockpit decision
surface for NADI (Navigasi Analitik Data dan Informasi). It gives management a
concise factual picture of the current `BSR` / `IP` Reliability Mart without
turning activity into an unverified condition, risk, or reliability score.

The guiding principle is: a management cockpit should simplify evidence, not
simplify uncertainty away.

## Evidence policy

Every displayed metric carries an evidence class in the API contract and is
listed in [the KPI evidence catalog](nadi-kpi-evidence-catalog.md). The API is
read-only over the Mart; it does not persist dashboard metrics, call a source
collector, or load raw maintenance rows into Python.

The public endpoint is:

```text
GET /v1/reliability/decision-overview?window_days=30
```

`window_days` is allowlisted to `7`, `30`, or `90`; the default is `30`.

## Implemented metrics

### Scope and date basis

- Site and organization are fixed to `BSR` / `IP`.
- The business Asset boundary is `reliability_asset_registry`, not all
  `asset_master` technical context rows.
- Maintenance metrics join `maintenance_event.equipment_id` to the Registry.
- Activity chronology is `COALESCE(actual_start, source_changed_at)`. The
  fallback is called source change time, not execution date.
- The activity trend is twelve backend-aggregated weekly buckets.

### Summary and activity

The overview provides Registry count, 7/30/90-day Maintenance Activity,
distinct registered Assets with activity in 30/90 days, a selected-window
concentration table, and raw status/work-type distributions. These are factual
activity metrics. A larger event count is not presented as a failure rate,
condition, risk, bad actor, or recommendation.

The concentration table uses `source_asset_number` and description as the
management-facing identity. The canonical `asset_ref` remains an internal link
target. Rows are deterministically ordered by event count, latest activity,
source Asset number, and canonical reference.

Status values are preserved, including `CAN`. Null status is shown as
`UNKNOWN`; no status is filtered or mapped to Open, Closed, Backlog, or
Overdue. Work Type distribution reads the quarantined source value at
`sources.maximo.worktype`, falls back to canonical `event_type` only when the
source value is absent, and uses `UNKNOWN` only when both are absent. The
canonical enum is conservative, so it does not represent every source Work
Type.

## Data maturity

The UI uses a reusable maturity pattern:

- `CURRENT LOCAL PROJECTION`: Asset and Maintenance data from local Collector
  to Mart projection.
- `CONTROLLED MART POPULATION`: FMEA, Asset Health, RCFA, and Overhaul factual
  records in their current controlled Mart populations.
- `RELATIONSHIP UNRESOLVED`: RCFA Asset relationship is not used for Asset
  coverage or concentration.
- `TECHNICAL CONTEXT`: non-Registry technical equipment is secondary context,
  not the NADI business Asset population.

FMEA and Asset Health represented-Asset counts are labelled as record
representation in the current controlled dataset, not completion rates. RCFA
is exposed as a global record count only. Overhaul rows with null Asset refs
remain available but are not assigned to an Asset.

## Intentionally unsupported

MTBF, MTTR, Availability, Health Score, Risk Score, Reliability Score,
Bad-Actor ranking, Critical Asset count, Backlog, Repeat Failure, PdM alerts,
and Recommendations are not decision metrics in this release. The missing
failure definitions, operating exposure, source semantics, thresholds, PI/DCS
signals, or governed action rules are documented in the evidence catalog.

There is no Action Board, PdM Center, anomaly detection, predictive failure,
RBAC, or new KPI storage table in this task.

## Future decision-layer roadmap

Choose the next surface from verified evidence and business semantics:

1. Maintenance Investigation / Repeat Activity analysis is now available as a
   factual, bounded investigation surface; Repeat Failure remains gated until
   failure identity and business semantics are verified.
2. Asset Health business-semantics verification before any condition metric.
3. FMEA coverage and workspace maturity after population completeness is
   established.
4. Governed Action Board rule design after actions and thresholds are
   approved.
5. PI/DCS integration for PdM only after the signals enter the verified NADI
   decision model.
