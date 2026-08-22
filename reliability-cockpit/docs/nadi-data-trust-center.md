# NADI Data Trust Center

## Purpose

The Data Trust Center is the governance surface for NADI (Navigasi Analitik
Data dan Informasi). It answers what data is currently available, which
populations are broad or controlled, which relationships are verified, and
which analytics remain intentionally withheld.

It does not create a Data Quality Score, Trust Score, Reliability Readiness
Score, percentage confidence, or red/amber/green judgment. Trust dimensions
remain separate because their weighting and governance are not verified.

The product route is the existing `/data-quality` route and the read-only API
is:

```text
GET /v1/reliability/data-trust
```

The endpoint is scoped to `BSR` / `IP` and reads aggregate evidence from the
local Reliability Mart only. It does not call a source collector or persist
calculated metrics.

## Population types

| Population type | Meaning in NADI |
| --- | --- |
| `BUSINESS_REGISTRY` | `reliability_asset_registry`, the Registered Reliability Asset boundary. |
| `TECHNICAL_CONTEXT` | Broader `asset_master` equipment context outside the normal business Asset population. |
| `LOCAL_COLLECTOR_PROJECTION` | Broad Asset/Maintenance data projected from the local Collector into the Mart. |
| `CONTROLLED_MART_POPULATION` | A bounded, verified Mart dataset useful for evidence but not asserted as complete history. |

`asset_master` counts are never labelled as Registered Reliability Assets.
FMEA, Asset Health, RCFA, and Overhaul remain individually labelled controlled
populations; their maturity is not flattened into one dataset label.

## Domain maturity

The API provides one typed domain entry for Asset, Maintenance, FMEA, Asset
Health, RCFA, and Overhaul. Each entry carries its own source object, record
count, optional Registry-scoped count, population type, relationship state,
latest available source-record date, date basis, evidence class, and known
limitation.

The domain summary reuses the detailed decisions in:

- [Maintenance Investigation semantics](nadi-maintenance-investigation-semantics.md)
- [Asset Health semantics](nadi-asset-health-semantics.md)
- [FMEA semantics](nadi-fmea-semantics.md)
- [RCFA semantics](nadi-rcfa-semantics.md)
- [Overhaul semantics](nadi-overhaul-semantics.md)

The source system shown for these current domains is `MAXIMO`. IPFMEA, IPBHM,
IPRCFA, IP_DOM_OH, and MXWODETAIL are source objects/applications, not
separate source systems. PI, DCS, and CEMS are not represented as connected
live integrations in the current NADI decision model.

## Date semantics

The Data Trust Center calls these values **latest available record evidence**.
They are not automatically source freshness, sync freshness, or an SLA:

| Domain | Date basis |
| --- | --- |
| Asset | `asset_master.source_updated_at` for Registered Asset rows. |
| Maintenance | `COALESCE(actual_start, source_changed_at)` for Registry-scoped activity. |
| FMEA | `COALESCE(status_changed_at, source_updated_at)`. |
| Asset Health | `COALESCE(status_changed_at, source_updated_at, source_created_at)`. |
| RCFA | `requested_at`. |
| Overhaul | `COALESCE(source_updated_at, source_created_at)`. |

No Mart ingestion timestamp is substituted for a missing source-record date.
If a domain has no available date, the UI shows `Date unavailable`.

`SYNC_FRESHNESS` is `NOT_AVAILABLE` because the current architecture does not
make Collector operational metadata a Cockpit dependency. A legitimately old
business record is not labelled stale.

## Relationship readiness

The relationship matrix reports evidence and factual resolution counts
separately:

- Registry → Asset Master is verified and its resolved/unresolved counts are
  shown.
- Maintenance → Registered Asset is the direct Registry-scoped product path.
- FMEA and Asset Health Asset relationships are directly verified; Registered,
  technical, and unresolved references remain distinct.
- RCFA → Asset, RCFA → Work Order, and RCFA → Failure Event remain unresolved.
  No coverage or Asset link is manufactured.
- Overhaul → Work Order is direct verified source evidence.
- Overhaul Work Order → local `maintenance_event` resolution is measured
  separately.
- Overhaul → Asset is accepted only through the verified Work Order-derived
  path when an existing `asset_ref` resolves. No direct Overhaul-to-Asset join
  is inferred.

## Analytics readiness

The matrix reuses the evidence classes from the [KPI evidence catalog](nadi-kpi-evidence-catalog.md).
Safe factual surfaces are marked `AVAILABLE`, including Registered Assets,
Maintenance Activity, Repeat Activity, Activity Concentration, FMEA records,
Asset Health assessment records, global RCFA records, Overhaul records, raw
status/work-type distributions, and record recency.

The following remain gated or unavailable: Repeat Failure, MTBF, MTTR,
Availability, Health Score, Wellness Score, Risk Score, Reliability Score, Bad
Actor, FMEA RPN, Failure Mode analytics, RCFA Completion, RCFA root-cause
taxonomy, Overhaul Schedule Variance, Overhaul Completion, Overhaul Progress,
PdM alerts, and Recommendations.

A capability marked **blocked** is intentionally withheld because its business
semantics or required source evidence are not yet verified. It does not mean
the source system is defective. `NOT_AVAILABLE` means the required source
fields are not in the current model; `DEFERRED` means the concept is
intentionally postponed.

## Current product boundary

Available now:

- Asset Reliability within the Registered Asset boundary;
- factual Registry-scoped Maintenance Activity and Repeat Activity;
- FMEA header assessment records;
- Asset Health assessment records without a numerical score;
- global RCFA records without invented relationships;
- Overhaul execution evidence without schedule or completion KPIs.

Requires future source or business verification:

- FMEA item semantics;
- RCFA relationships, root-cause, and action objects;
- Asset Health Wellness, ACR, MPI, and condition semantics;
- Overhaul status, progress, inspection, and date boundaries;
- Maintenance failure-code semantics and repeat-failure identity.

Future data source: PI/DCS integration for a governed PdM model. No unfinished
feature menu entry or placeholder live status is added here.

## Office-network discovery backlog

The following are documentation-only future verification tasks:

- FMEA: verify IPFMEAITEM semantics and item-level identity.
- RCFA: discover Asset and Work Order relationships, root-cause/action objects,
  category semantics, status semantics, and completion rules.
- Asset Health: verify the source and semantics of Last Wellness, Kondisi Saat
  ini, ACR, and MPI; do not assume they are IPBHM fields.
- Overhaul: verify DOM_INSPEKSIMESIN relationship, Progress scale, lifecycle
  status, `perfomance_test`, date boundaries, and multiple Work Order rules.
- Maintenance: verify failure-code meaning and a governed repeat-failure
  identity.
- PI/DCS: define the future PdM evidence model and projection boundary.

No source discovery, Mart write, Collector write, Registry write, or Contract
change is part of NADI-009.
