# MX-012R — Unified Collector-to-Mart Pipeline

## Purpose

MX-012R makes the local Maximo Collector operational store the downstream
source for the Asset and Maintenance portions of the Reliability Mart. The
bootstrap does not construct a Maximo client and does not download source rows
again.

The model remains `MODEL_C_SEPARATE_REGISTRY_RELATION`:

- `equipment` is broad technical Maximo identity and hierarchy context;
- `asset_master` is the approved local canonical technical projection;
- `reliability_asset_registry` is the current business Asset membership;
- NADI `/assets` is the Registry projection, not the raw `asset_master` count.

The Registry relation is a Mart projection and is not a seventh Contract v1
entity.

## Local-only bootstrap

The operator command is:

```text
mxcollector mart-bootstrap --registry-file <external-report.xls> \
  --expected-sha256 <migration-fingerprint>
```

It performs bounded local reads from Collector PostgreSQL, validates the
external HTML-table export, projects canonical Asset and Maintenance records
through the existing mappers and `MartWriter`, then atomically replaces the
current Registry relation. The current migration safety fingerprint is:

```text
aa0bd8fd22275aea3ecf8654ee37878106123b7dbdf58135fb783e853ee66a5f
```

That fingerprint is a one-time safety check for this migration, not a
permanent requirement for future Registry snapshots. Future snapshots are
validated semantically: report shape, nonblank unique Asset identities, BSR
scope, Collector resolution, and Mart `asset_master` resolution.

The report remains an external production input. Person fields such as System
Owner and Insert by, along with wellness, ACR, MPI, judgement, and recommendation
fields, are not ingested.

## Projection state and reruns

`mart_projection_state` is downstream state. It is intentionally separate from
Maximo `sync_cursor`. A full scan includes NULL `source_changed_at` rows and
only records its watermark after the scan succeeds. Incremental runs use
`source_changed_at` with a one-day overlap and canonical-ID idempotency; equal
timestamps are therefore safe. NULL-timestamp handling is reported and remains
eligible for repeat validation on later runs.

Projection batches default to 500 rows. Existing Mart rows are never
truncated, and source Collector rows are never deleted. A failed projection
does not advance its downstream state.

## Controlled bootstrap evidence

The controlled local bootstrap completed with zero Maximo business requests:

| Projection | Local rows seen | Inserted | Updated | Unchanged / skipped |
| --- | ---: | ---: | ---: | ---: |
| Asset context | 10,660 | 10,383 | 266 | 11 unchanged |
| Maintenance event | 112,258 | 67,826 current-prefix inserts | 82 prior controlled rows retained | 43,590 missing Equipment; 750 out-of-prefix skipped |

The resulting Mart counts were:

- `asset_master`: 10,660 technical context rows;
- `maintenance_event`: 68,000 rows, including prior controlled rows;
- `reliability_asset_registry`: 845 rows;
- Registry members resolved to `asset_master`: 845;
- Registry unresolved: 0.

The registry-scoped Maintenance read model contains 35,259 events. The final
projection state recorded `asset_master` rows seen/written as 10,660 and
`maintenance_event` rows seen/written as 112,258/67,918. Both downstream
projection states completed successfully; the source watermarks remain local
projection metadata and are not Maximo cursors.

All source Work Order statuses were retained, including `CAN`. Work Orders
without a local Equipment identity are not invented into a canonical Asset
relationship and remain in the Collector store.

The first local-only pass exposed 728 projected rows outside the configured
`BSR` Work Order prefix. Those rows were removed with an exact source-scope
predicate because they were created by that pass; no Collector source row and
no pre-existing in-scope history was deleted. The final rerun reports all 750
out-of-prefix Collector rows as skipped and leaves zero out-of-scope
`MXWODETAIL` rows in the Mart.

The local Work Order schema does not retain every optional source field used by
the direct MXWODETAIL projection, notably actual start and finish for older
rows. Those Mart fields remain NULL rather than being reconstructed. NADI
Maintenance sorts and filters by `COALESCE(actual_start, source_changed_at)`.
The local Work Order table is treated as the already-approved BSR/IP Collector
boundary; its configured BSR prefix is re-applied before canonical promotion.

The final Mart integrity snapshot was 68,183 asset references (68,079
resolved), one Work Order reference (zero resolved), 10,660 technical Asset
context rows, and 845 registered Assets with zero unresolved Registry members.

## NADI read behavior

The read-only Cockpit Mart repository joins normal Asset and Maintenance views
to `reliability_asset_registry`. A technical `asset_master` row outside the
current Registry is not a normal NADI Asset and its Asset detail returns 404.
The global unresolved Overhaul view remains available, while unresolved RCFA
relationships remain explicitly `UNRESOLVED` and are never manufactured by a
Registry join.

`GET /v1/reliability/registry` exposes only aggregate snapshot metadata. The
integrity response retains its existing reference fields and adds technical
context, registered count/resolution, and Registry-scoped Maintenance metrics.

## Known debt and mixed maturity

- The broad MXAPIASSET technical population is not claimed to be exhausted.
- Registry Parent coverage is technical hierarchy context and is not a
  prerequisite for the 845 business projection.
- Historical non-Registry Work Order equipment gaps remain technical debt.
- Historical local Work Orders may lack actstart/actfinish.
- RCFA Asset relationships remain unresolved.
- FMEA, Asset Health, RCFA, and Overhaul remain their existing controlled Mart
  populations; MX-012R does not imply full-history completion for those domains.

The next product work should build verified Reliability Cockpit decision
surfaces from these explicitly separated populations, not add unsupported
KPIs or broaden source collection.
