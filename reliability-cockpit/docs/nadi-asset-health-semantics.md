# NADI Asset Health Semantics

## Purpose and boundary

NADI-005 turns the current IPBHM Mart population into a factual assessment
workspace. It does not create a numerical Health Score, Wellness Score, Risk
Score, Condition Score, remaining-life estimate, or probability of failure.

The current canonical source is `IPBHM`. Verified source fields represented by
the existing contract are:

| Source field | Canonical field | Evidence boundary |
| --- | --- | --- |
| `bhmid` | `source_record_id` | Direct source identifier candidate; uniqueness is not asserted by the UI. |
| `eid` | `sources.maximo.eid` | Preserved source attribute; meaning remains `UNKNOWN`. |
| `revision` | `revision` | Raw revision value. |
| `status` | `lifecycle_status` | Raw source status; business meaning is unverified. |
| `description` | `description` | Source text; not parsed into condition. |
| `fungsi` | `function_description` | Source text with conservative naming; no BHM expansion is asserted. |
| `assetnum` | `asset_ref` | Direct verified relationship to `asset_master`. |
| `createddate` | `source_created_at` | Source timestamp. |
| `lastmodifieddate` | `source_updated_at` | Source timestamp. |
| `statusdate` | `status_changed_at` | Source status timestamp. |

The normal workspace is scoped through `reliability_asset_registry`. Technical
or unresolved references are not deleted from the Mart; they are excluded from
the normal Registered Asset view and remain visible in aggregate evidence.

## Local evidence audit

The aggregate-only local audit on 2026-08-22 found:

| Measure | Result |
| --- | ---: |
| Asset Health records | 100 |
| Records with `asset_ref` | 100 |
| Records without `asset_ref` | 0 |
| Records resolved to `asset_master` | 100 |
| Records resolved to Registered Assets | 100 |
| Technical non-Registry references | 0 |
| Unresolved Asset references | 0 |
| Distinct Registered Assets represented | 6 |
| Assets with one record | 0 |
| Assets with multiple records | 6 |
| Maximum records per Asset | 41 |
| Assets with multiple distinct revisions | 0 |

All 100 current records have a non-empty `revision`, `description`,
`function_description`, `source_created_at`, `source_updated_at`, and
`status_changed_at`. The observed raw lifecycle status is `VER-OK` for all 100
records. The observed revision is `0` for all 100 records. These are source
observations, not condition classifications.

The record-count distribution across the six represented Assets is one Asset
each with 7, 8, 10, 14, 20, and 41 records. This demonstrates multiplicity in
the current controlled population. It does not prove that records with the
same Asset identity are revisions of one conceptual assessment.

## EID semantics

`eid` is present in all 100 current records and has 100 distinct values, with
no duplicate values in this snapshot. Repository evidence still classifies
its meaning as `UNKNOWN`. NADI does not use EID as a business identity,
relationship, or grouping key.

## Assessment record date and age

The workspace uses this transparent ordering/date basis:

```text
COALESCE(status_changed_at, source_updated_at, source_created_at)
```

This is called the **assessment record date**. It is not a condition measured-at
date. If all three source timestamps are null, the UI shows `Date unavailable`
and does not substitute Mart ingestion time.

Assessment age is:

```text
as_of - assessment record date
```

It is classified `DERIVED_SAFE` and means record recency only. It is not a
freshness score, staleness threshold, deterioration signal, or health warning.

## Status, description, and function

Lifecycle values remain raw source statuses. The workspace uses neutral status
styling and does not map values to Healthy, Warning, Critical, Good, Bad, Open,
or Closed. Description and Function are source text that may provide useful
context, but NADI does not parse them into condition, failure mode, risk, or
recommendation.

## Local report as secondary evidence

The protected local `23496711.xls` report was read locally as secondary
evidence only. It contains 845 Asset rows and all 845 match the current Asset
Registry by Asset number. Six report Asset numbers overlap with the current
IPBHM Asset representation. Aggregate non-empty counts were:

| Report column | Non-empty rows |
| --- | ---: |
| `Last Wellness` | 833 |
| `Kondisi Saat ini` | 832 |
| `Last ACR` | 830 |
| `Last MPI` | 830 |
| `Last ACR Rank` | 830 |
| `Last MPI RANK` | 830 |
| `Maintenance Strategi` | 30 |
| `Status` | 845 |
| `Tanggal Judgement` | 832 |
| `Rekomendasi Program` | 832 |

These columns are not ingested, persisted, or joined into the Asset Health
workspace. Names such as `Last Wellness`, `Kondisi Saat ini`, `ACR`, and `MPI`
do not establish a relationship to IPBHM or permission to treat them as a
Health Score. Their relationship is classified
`SOURCE_SEMANTICS_REQUIRE_VERIFICATION`.

## Semantic decision

| Concept | Classification | Product treatment |
| --- | --- | --- |
| Assessment records | `VERIFIED` | Factual count from the controlled Mart population. |
| Registered Assets represented | `DERIVED_SAFE` | Distinct Registry Asset refs with an Asset Health record; not health coverage or completion. |
| Multiple assessments | `DERIVED_SAFE` | Record multiplicity only; no lineage inference. |
| Latest assessment record | `DERIVED_SAFE` | Latest factual record date using the documented fallback. |
| Assessment age | `DERIVED_SAFE` | Record recency only. |
| Lifecycle status | `VERIFIED` | Raw source value; semantic interpretation remains unverified. |
| Health Score | `BUSINESS_SEMANTICS_REQUIRED` | Not displayed. |
| Wellness Score | `BUSINESS_SEMANTICS_REQUIRED` | Not displayed; report relationship is unverified. |
| Condition Classification | `BUSINESS_SEMANTICS_REQUIRED` | Not displayed. |
| Risk | `DATA_NOT_AVAILABLE` | No verified risk model or inputs in the current Asset Health evidence. |

## Health Score readiness gate

`HEALTH_SCORE_READY: NO`.

Before a genuine score could be implemented, NADI would need an authoritative
verified numerical input, source object and field ownership, units/range,
higher-is-better or lower-is-better directionality, normalization formula,
component weighting and aggregation, missing-data treatment, validity period,
business thresholds, manual override policy, historical versioning, and
business-owner approval/governance.

`WELLNESS_SOURCE_IDENTIFIED: NO`. The report column is a clue, not a verified
IPBHM source or semantic relationship.
