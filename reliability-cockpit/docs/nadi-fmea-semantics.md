# NADI FMEA Semantics

## Purpose and boundary

NADI-006 presents the current `IPFMEA` Mart population as factual FMEA
assessment records for Registered Reliability Assets. It does not create an
RPN, risk score, criticality score, failure probability, or recommendation.

The normal workspace is Registry-scoped through
`reliability_asset_registry`. Technical and unresolved FMEA references remain
in the Mart and are reported as relationship evidence.

## Verified source fields

The existing approved contract maps these `IPFMEA` fields:

| Source field | Canonical field | Product boundary |
| --- | --- | --- |
| `fmeaid` | `source_record_id` | Technical source record identity; not the human-facing FMEA number. |
| `fmeanum` | `source_number` | Human-facing FMEA number when present. |
| `revision` | `revision` | Raw revision value. |
| `status` | `lifecycle_status` | Raw source status; business meaning is unverified. |
| `description` | `description` | Source text; not parsed into failure mode, effect, or risk. |
| `assetnum` | `asset_ref` | Direct verified relationship to `asset_master`. |
| `failurecode` | `failure_code_ref` and `sources.maximo.failurecode` | Source-qualified Failure Code evidence; hierarchy semantics are unverified. |
| `lastmodifieddate` | `source_updated_at` | Source timestamp. |
| `statusdate` | `status_changed_at` | Source timestamp. |

`fmeaid` and `fmeanum` remain distinct. The normal UI uses FMEA number
(`source_number`) and keeps the source record ID secondary.

## Local evidence audit

Aggregate-only local Mart evidence on 2026-08-22:

| Measure | Result |
| --- | ---: |
| FMEA records | 100 |
| Records with `asset_ref` | 83 |
| Records without `asset_ref` | 17 |
| Records resolved to `asset_master` | 61 |
| Records resolved to Registered Assets | 23 |
| Technical non-Registry references | 38 |
| Unresolved Asset references | 22 |
| Distinct Registered Assets represented | 23 |
| Registered Assets with one FMEA record | 23 |
| Registered Assets with multiple FMEA records | 0 |
| Maximum records per Registered Asset | 1 |

The current FMEA population is controlled and must not be described as full
plant-wide FMEA history, completion, or compliance.

## Identity and revision evidence

All 100 records have a `source_record_id`, and all 100 are unique in this
snapshot. All 100 have a source number, and all 100 source numbers are unique.
There are no duplicate source-number rows in the current snapshot.

All 100 records have a revision. Observed raw revision values are `0` (36),
`1` (38), and `2` (26). No source number has multiple revisions in this
snapshot, and no Registered Asset has multiple FMEA records. These observations
do not establish a general revision lineage rule.

`REVISION_LINEAGE: UNVERIFIED`. NADI does not assume that a higher revision is
current or approved, nor that the latest timestamp is an approved revision.

## Status and description semantics

Observed lifecycle statuses remain raw source values:

| Raw status | Count | Interpretation |
| --- | ---: | --- |
| `ENGDONE` | 3 | Unverified source status |
| `FDT-OK` | 1 | Unverified source status |
| `MONITORED` | 67 | Unverified source status |
| `REVISI` | 6 | Unverified source status |
| `VER-NOT-OK` | 1 | Unverified source status |
| `VER-OK` | 11 | Unverified source status |
| `WAPPR` | 1 | Unverified source status |
| `WHS-OK` | 10 | Unverified source status |

The UI uses neutral styling. Values are not mapped to Active, Approved,
Completed, Good, Bad, Current, Obsolete, Warning, or Critical.

FMEA descriptions are source text. NADI does not parse them into failure modes,
effects, causes, risk categories, or recommendations.

## Failure Code boundary

The local audit found 55 records with a non-empty source Failure Code and 55
records with the canonical `failure_code_ref`; there are 20 distinct source
Failure Code values. The workspace shows the raw source value when present and
keeps the canonical scoped reference secondary/internal.

`FAILURE_CODE_SOURCE_VALUE: VERIFIED`

`FAILURE_CODE_BUSINESS_HIERARCHY: UNVERIFIED`

`FAILURE_MODE_IDENTITY: UNVERIFIED`

Failure Code is not treated as a Failure Mode and does not define Repeat
Failure identity.

## FMEA record date and age

The workspace uses:

```text
COALESCE(status_changed_at, source_updated_at)
```

This is called the **FMEA record date**. It is not an approval date, failure
date, or risk assessment date. All 100 current records have a usable record
date. The oldest observed record date is 2015-08-14 03:03:24 UTC and the latest
is 2026-08-14 03:28:43 UTC.

FMEA record age is:

```text
as_of - FMEA record date
```

It is `DERIVED_SAFE` and means record recency only. No current/due/expired/
stale threshold is applied.

## Deferred item details

`IPFMEAITEM` remains deferred. NADI-006 therefore does not expose or imply
individual failure modes, effects, causes, controls, severity, occurrence,
detectability, RPN, or recommended actions.

`FAILURE_MODE_DETAILS_AVAILABLE: NO`

## RPN and risk readiness gates

`RPN_READY: NO`

`RISK_CLASSIFICATION_READY: NO`

Before a full FMEA analytics layer can be built, the product needs verified
item-level fields and semantics for failure mode, effect, cause, controls,
severity, occurrence, detectability, their scales, RPN formula, revision
applicability, business thresholds, approval lifecycle, and governance.
