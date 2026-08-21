# MX-011A — Maximo Asset Registry Reconciliation

## Scope and safety

MX-011A compares the local Maximo Collector Equipment and Work Order
populations with a local Maximo-generated **List of Assets** report. The report
is a production-data input and is intentionally not stored in Git. The
reconciliation command reads it from a caller-supplied local path and emits
aggregate metrics only.

The analysis made no Maximo requests. Collector and Reliability Mart tables
were read with `SELECT` statements only. No Collector row, Mart row,
`SyncCursor`, schema, contract, or NADI UI was changed.

```text
mxcollector reconcile-asset-registry --registry-file <local-path>
```

The implementation supports the HTML-table export form of `.xls`. Native
binary XLS/XLSX input fails explicitly with `UNSUPPORTED_REGISTRY_FILE_FORMAT`.
Person fields (`System Owner` and `Insert by`) are ignored completely.

## Registry snapshot

The analyzed local file was an HTML table with sheet/title `List of Assets`.
Its aggregate fingerprint is recorded for reproducibility; the file itself is
not a repository artifact.

| Metric | Result |
| --- | ---: |
| Data rows | 845 |
| Nonblank Asset rows | 845 |
| Unique Asset values | 845 |
| Duplicate Asset values | 0 |
| Blank Asset values | 0 |
| Unique Parent values | 352 |
| File bytes | 1,281,569 |
| SHA-256 | `aa0bd8fd22275aea3ecf8654ee37878106123b7dbdf58135fb783e853ee66a5f` |

All registry Asset identifiers have the same aggregate shape: length 18 and a
three-digit numeric suffix. This is an observation, not a classification rule.
Parent values are mostly length 13 (843 of 845), with two other lengths. All
845 rows have a Parent value; 352 distinct Parent values occur.

## Collector Equipment baseline

The local Collector contains 5,680 Equipment rows. IDs are present and unique
in all rows. The broad population is not equivalent to the business registry.

| Attribute | Distribution |
| --- | --- |
| Status | `OPERATING` 3,375 (59.4%); `INACTIVE` 2,292 (40.4%); `NOT READY` 13 (0.2%) |
| Equipment class | `PRODUCTION` 5,648 (99.4%); `IT` 17 (0.3%); `FACILITIES` 15 (0.3%) |
| Unit | `CS01` 4,988 (87.8%); `TU` 643 (11.3%); other units 49 (0.9%) |
| Parent present | 5,504 (96.9%) |
| Ancestor present | 5,504 (96.9%) |
| Has children | true 849; false 4,831; null 0 |

## Exact registry reconciliation

Matching is `trim + uppercase` between report `Asset` and Collector
`equipment.id`. It does not infer membership from ID shape, parent presence,
status, unit, or children.

| Metric | Result |
| --- | ---: |
| Registry Assets | 845 |
| Exact Equipment matches | 581 |
| Registry Assets absent from Collector | 264 |
| Exact match | 68.8% |
| Collector Equipment in registry | 581 |
| Non-registry Equipment | 5,099 |

The matched registry group is uniformly `OPERATING` and is mostly `PRODUCTION`
class. The non-registry group is also overwhelmingly `PRODUCTION` class and
contains both `OPERATING` and `INACTIVE` equipment. These characteristics do
not provide a safe standalone reliability-asset predicate. No production
classification rule was created.

## Parent and hierarchy reconciliation

Of 352 distinct registry Parent values, 75 were found in Collector Equipment
and 277 were absent. Among the 581 registry rows that matched Collector
Equipment, the report Parent and Collector `parent_id` agreed in all 581 rows.
There were no observed parent mismatches or missing-side disagreements among
those matched rows.

The in-memory hierarchy walk used cycle protection and did not modify the
database:

| Metric | Result |
| --- | ---: |
| Non-registry Equipment | 5,099 |
| Direct registry parent | 2,200 |
| Registry ancestor found | 2,200 |
| Indirect registry ancestor | 0 |
| No registry ancestor | 2,899 |
| Broken parent reference | 1,315 |
| Cycle encountered | 0 |
| Maximum observed walk depth | 5 |

The 2,200 resolved rows are direct-child relationships. A broken parent is a
subset of the rows for which no registry ancestor was found; it means the
referenced parent was not present in the local Collector population, not that
the source record is invalid.

## Work Order relationship analysis

The analysis used the locally collected Work Order table and did not query
Maximo. The full local population is broader than the current Equipment table,
so a missing Equipment target is reported separately from a known Equipment
row without a registry ancestor.

| Relationship class | All local Work Orders |
| --- | ---: |
| Total | 112,258 |
| With Equipment | 95,637 |
| Without Equipment | 16,621 |
| Directly targets registry Asset | 35,984 |
| Non-registry Equipment with registry ancestor | 21 |
| Equipment with no registry ancestor | 23,482 |
| Equipment target missing from Collector | 36,150 |

For a bounded recent view, the latest 30 days represented by local
`source_changed_at` ran from `2026-07-21T15:08:06+00:00` through
`2026-08-20T15:08:06+00:00` and contained 2,742 Work Orders:

| Relationship class | Recent local period |
| --- | ---: |
| With Equipment | 2,716 |
| Without Equipment | 26 |
| Directly targets registry Asset | 2,706 |
| Non-registry Equipment with registry ancestor | 0 |
| Equipment with no registry ancestor | 9 |
| Equipment target missing from Collector | 1 |

This is not evidence that lower-level relationships never occur. It is evidence
that the current local Work Order population does not establish a material or
recent Work Order-to-registry-ancestor path: 21 of 95,637 Work Orders with an
Equipment reference resolve that way overall, and zero do so in the recent
30-day slice. The large missing-target group also limits the strength of any
negative conclusion.

## Current Reliability Mart impact

The current controlled Mart is not the authoritative registry population:

| Metric | Result |
| --- | ---: |
| `asset_master` rows | 277 |
| `asset_master` rows matching registry | 258 |
| Registry Assets absent from current Mart | 587 |
| Mart assets not in registry | 19 |
| `maintenance_event` equipment references | 174 |
| Maintenance references resolved to current `asset_master` | 14 |
| Maintenance references unresolved to current `asset_master` | 160 |
| Unresolved references found in Collector Equipment | 61 |
| Unresolved references with registry ancestor | 7 |

The current Mart counts therefore describe a bounded initial load, not the
845-row registry snapshot and not the complete Equipment population.

## Business-field discovery

The report fields were measured for presence only. No values were ingested or
mapped to Contract v1.

| Report field | Present |
| --- | ---: |
| Last Wellness | 833 / 845 (98.6%) |
| Kondisi Saat ini | 832 / 845 (98.5%) |
| Last WO | 795 / 845 (94.1%) |
| Last ACR | 830 / 845 (98.2%) |
| Last MPI | 830 / 845 (98.2%) |
| Maintenance Strategi | 30 / 845 (3.6%) |
| Tanggal Judgement | 832 / 845 (98.5%) |
| Rekomendasi Program | 832 / 845 (98.5%) |
| WO Eng. Judgement | 253 / 845 (29.9%) |
| WO Eng. Judgement Status | 253 / 845 (29.9%) |

These fields may be useful future inputs for Asset Health, Maintenance
Strategy, Engineering Judgement, Recommendations, or an Action Board. Their
source semantics require verification before any mapping. No person fields
were processed.

## Architecture decision

**Decision: `MODEL_C_SEPARATE_REGISTRY_RELATION`**

The current evidence supports keeping the broad Equipment hierarchy for
relationship context while treating the Maximo report as a separate
registered-asset projection. The hierarchy is real and internally consistent
for the 581 matched registry rows, and 2,200 non-registry rows have a direct
registry parent. However, the observed Work Order ancestor relationship is
sparse overall and absent in the recent local period; many Work Order targets
are not present in the bounded local Equipment population. That is not enough
evidence to make ancestor roll-up the default reliability relationship.

Recommended meanings:

- **Equipment** — broad Maximo equipment identity used for source and hierarchy
  context.
- **Registered Reliability Asset** — an Asset present in the supplied current
  `List of Assets` registry snapshot.
- **Non-registry Equipment** — local Equipment not present in that snapshot;
  its role remains neutral and unclassified.

Recommended future treatment is a relationship-capable Equipment hierarchy plus
an evidence-backed registry relation/projection. NADI should default to
registered Reliability Assets, while retaining lower-level Equipment context
where a verified relationship exists. MX-011A intentionally does not add
`is_reliability_asset`, `asset_role`, a new registry table, or a Contract v1
field.

## Next decision

`MX-012R` is **not automatically green-lit** for a unified asset model from
this evidence alone. Before changing the Mart asset model, review the missing
Equipment-target population and verify whether the supplied registry is a
stable recurring snapshot. A future MX-012R design can use the separate
registry relation as its business-asset projection while retaining Collector
Equipment for relationship resolution.
