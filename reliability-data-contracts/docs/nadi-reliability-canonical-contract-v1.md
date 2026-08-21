# NADI Reliability Canonical Data Contract v1

Contract version: `1.0`

This document freezes a small, vendor-neutral Reliability Mart boundary. It
canonicalizes verified meaning from Maximo; it does not rename Maximo objects
inside the source system and it does not implement collection or ingestion.

## Canonical entities

| Canonical entity | Verified source | Purpose |
|---|---|---|
| `asset_master` | `MXASSET` | Stable plant asset reference |
| `maintenance_event` | `MXWODETAIL` actuals | Maintenance execution evidence |
| `fmea_assessment` | `IPFMEA` | Failure-mode/risk assessment header |
| `rcfa_analysis` | `IPRCFA` | Root-cause analysis header |
| `asset_health_assessment` | `IPBHM` | Conservative BHM assessment header |
| `overhaul_event` | `IP_DOM_OH` | Dominion overhaul evidence |

`equipment.schema.json` and `work-order.schema.json` remain the existing
application-facing contracts. `asset-master.schema.json` is the explicit v1
asset-master boundary; the existing `maintenance-event.schema.json` is
backward-compatible and now carries optional v1 provenance/evidence fields.

## Identity strategy

Canonical IDs are organization-owned and must not be confused with source
numbers, foreign keys, or scope dimensions. A deterministic source identity is
formed from:

```text
(source_system, source_object, source_site, source_organization, source_record_id)
```

The tuple is scoped because a Maximo identifier is not assumed globally unique
across object, site, or organization. `fmeaid`, `rcfaid`, `bhmid`, and `domid`
are preferred source-record candidates from MX-006C; one sample does not prove
uniqueness. `fmeanum`, `norcfa`, and `domohnum` are secondary business-number
candidates. `siteid`, `orgid`, `assetnum`, and `wonum` are never promoted to
record identity by default.

Asset and Work Order references retain their scoped Maximo identity. The
canonical asset master is the resolution target; raw `assetnum` and `wonum`
remain in `sources.maximo` and provenance rather than becoming universal IDs.

## Source mappings

Machine-readable field mappings are in
[`mappings/maximo-nadi-reliability.json`](../mappings/maximo-nadi-reliability.json).
The existing [`mappings/maximo-to-contracts.md`](../mappings/maximo-to-contracts.md)
remains the source of truth for the established equipment and work-order
runtime contracts.

All source applications/modules are Maximo context:

```text
source_system = MAXIMO
source_application = RELIABILITY | DOMINION | null
```

`site_code` and `organization_code` are separate nullable dimensions. Current
verification scope is BSR/IP, but the schema does not hardcode those values.
Statuses preserve source values in `lifecycle_status` or `status`; a universal
OPEN/ACTIVE/COMPLETE mapping is deferred.

## Relationship evidence

The machine-readable graph is
[`catalog/nadi-reliability-relationship-graph.json`](../catalog/nadi-reliability-relationship-graph.json).

- `DIRECT_VERIFIED`: the source resource exposes the relationship field.
- `DERIVED_VERIFIED_PATH`: the join path is made of verified keys, but the
  source resource has no direct relationship field.
- `UNRESOLVED`: the relationship is represented as null and must not be guessed.
- `DEFERRED`: an extension is expected after a future bounded discovery.

Direct evidence includes `IPFMEA.assetnum`, `IPBHM.assetnum`, and
`IP_DOM_OH.wonum`. The overhaul asset link is derived only through
`IP_DOM_OH.wonum -> MXWODETAIL.wonum -> MXWODETAIL.assetnum -> asset_master`.
`IP_DOM_OH` has no direct verified asset mapping. RCFA asset, location, Work
Order, and failure-event links remain nullable and unresolved.

## Nullability and time

Canonical mechanics (`canonical_id`, `contract_version`, and provenance) are
required. Business fields and unresolved relationships are nullable. No
sentinel values such as `UNKNOWN_ASSET` or `N/A` are permitted.

Source and event timestamps use ISO-8601 date-time strings. A timezone is
preserved when Maximo provides one; no offset is invented. The contracts
distinguish created, updated, status-changed, planned, actual, requested, and
ingestion timestamps.

## Deferred contracts

[`catalog/nadi-reliability-deferred.json`](../catalog/nadi-reliability-deferred.json)
isolates the four unresolved resources: `IPFMEAITEM`, `IPBHMMEASUREMENT`,
`DMD_OPLOGABN`, and `IPMSMSFAILUREMECHANI`. They do not block v1 and do not
justify fabricated fields. They are extension points for FMEA detail,
condition measurement, operational findings, and failure-mechanism taxonomy.

`IP_DOM_OH.perfomance_test` is retained as an unresolved source attribute.
Its relation to Efficiency Management Performance Test is `UNKNOWN`.

## Lineage examples

```text
MAXIMO IPFMEA.assetnum
        -> fmea_assessment.asset_ref
        -> asset_master

MAXIMO IP_DOM_OH.wonum
        -> overhaul_event.workorder_ref
        -> maintenance_event
        -> asset_master via MXWODETAIL.assetnum

MAXIMO IPRCFA
        -> rcfa_analysis
        -> asset_ref/workorder_ref = null (UNRESOLVED)
```

## MX-008R implementation guidance

The collector implementation should normalize into these contracts without
redesigning their semantics. It must preserve source provenance, use scoped
identity resolution, emit null for unresolved relationships, and keep deferred
resources out of the v1 payload until their contracts are verified. This task
does not modify the collector, Cockpit, database, or UI.
