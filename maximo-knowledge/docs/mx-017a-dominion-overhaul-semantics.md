# MX-017A DOMINION Overhaul Semantics Discovery

## Executive Result

DOMINION is an application/module inside the same Maximo source boundary. This
task produced source knowledge only; it did not create or change an Overhaul,
inspection, Work Order, scope record, attachment, or KPI.

The bounded evidence establishes:

- `IP_DOM_OH` is live-verifiable. Its JSON Schema title is `DOM_OH` and its
  declared technical primary key is the composite `domohnum + siteid`.
- The source labels `Progress Keseluruhan`, `Tanggal Mulai`, `Tanggal Selesai`,
  `Tanggal Actual Mulai`, `Tanggal Actual Selesai`, and `Durasi OH (Hari)` are
  verified metadata. A bounded record exposed numeric progress `45.28`, but
  no percentage domain or calculation rule was exposed.
- `perfomance_test` is exactly the source spelling, has live type boolean, and
  the source label is `Perfomance Test Setelah OH`. Its pass/fail/result
  semantics and relationship remain unknown.
- `IP_DOM_OH.inspeksinum` exact-matches
  `DOM_INSPEKSIMESIN.dom_inspeksinum` for one BSR candidate. This is a direct
  Overhaul → Inspection relationship.
- `DOM_INSPEKSIMESIN.dom_scopeline` is an array with a live child-schema
  reference. The scope-line child fields and finding semantics were not
  retrieved.
- `IP_DOM_OH_SCOPE_PM.domohnum` exact-matches one `IP_DOM_OH.domohnum`. Two
  bounded Scope PM records under that parent expose two Work Order keys; both
  exact-match `MXWODETAIL.wonum` and both expose an Asset. This verifies a
  multi-Work-Order model through Scope PM, while the primary/related Work Order
  business role remains unresolved.

Status, completion, progress percentage, outage boundaries, inspection finding
meaning, performance-test meaning, and cost variance semantics remain
unresolved. No Overhaul KPI is ready.

## Existing Overhaul Boundary

The current factual boundary is preserved:

```text
IP_DOM_OH.wonum
  → MXWODETAIL.wonum
  → MXWODETAIL.assetnum
  → Asset
```

This is a derived Asset path. `IP_DOM_OH` did not expose a direct `assetnum`
field in the live schema. The existing direct Overhaul → Work Order evidence is
preserved; MX-017A adds the separate Scope PM relationship evidence.

DOMINION is not treated as an independent source system. It remains a Maximo
application/module and its records remain within the Maximo source boundary.

## IP_DOM_OH Metadata

Live metadata returned HTTP 200:

- `/oslc/apimeta/IP_DOM_OH`: title `DOMINION - MASTER OH PLANNING & SCHEDULLING`,
  query capability `All`.
- `/oslc/jsonschemas/IP_DOM_OH`: title `DOM_OH`, resource `IP_DOM_OH`, type
  `object`.
- Declared JSON Schema PK: `domohnum`, `siteid`.
- Required fields include `domid`, `perfomance_test`, document indicators,
  `absensi`, and `notulensi`.

Relevant live schema labels/types:

| Field | Live type | Source label/evidence |
| --- | --- | --- |
| `domid` | integer | required technical identifier |
| `domohnum` | string | `Nomor OH`; composite PK component |
| `status` | string | title `Status`; default `DRAFT` |
| `wonum` | string | `Nomor WO` |
| `inspeksinum` | string | `Inspeksi` |
| `progress` | number | `Progress Keseluruhan` |
| `tgl_mulai` / `tgl_selesai` | string | `Tanggal Mulai` / `Tanggal Selesai` |
| `tgl_actual_mulai` / `tgl_actual_selesai` | string | actual start/finish labels |
| `dur_oh` | integer | `Durasi OH (Hari)` |
| `dur_actual_oh` | integer | `Durasi Actual OH`; unit not stated |
| `rencana_scope` | integer | `Rencana Scope` |
| `realisasi_scope` | integer | `Realisasi Scope` |
| `jumlahworekom` | integer | source label only; meaning unresolved |
| `realisasi_cost` | number | `Realisasi Cost`; currency not exposed |
| `perfomance_test` | boolean | `Perfomance Test Setelah OH` |
| `siklus` | string | `Jenis OH` |

The schema also exposes boolean document indicators for
`dokumen_rekomendasi`, `laporan_teknik`, `laporan_evaluasi`,
`berita_acara_serahterima`, `berita_acara_syncron`, and `notulensi`.

## Lifecycle Semantics

The bounded BSR record exposed raw status `EKS-COMP`. The live schema also
exposes `status_description` and declares default `DRAFT`, but it exposes no
status enum, lifecycle description, workflow transition, or domain mapping in
the metadata inspected.

Classification:

- `OVERHAUL_STATUS_DOMAIN_IDENTIFIED`: `PARTIAL` — status field, default, and
  one raw instance value are verified; the domain is not.
- `OVERHAUL_COMPLETION_STATUS_IDENTIFIED`: `NO` — `EKS-COMP` was not translated
  to Completed.

No approved, execution, cancelled, closed, or completion stage was asserted.

## Progress Semantics

`progress` is a live-schema `number` with source title `Progress Keseluruhan`.
One bounded record exposed `45.28`; the observed value lies within a plausible
0–100 numeric range, but the source did not expose a minimum, maximum, unit,
percentage marker, calculation rule, or manual/calculated indicator.

The result is therefore:

- `PROGRESS_SCALE_IDENTIFIED`: `PARTIAL`
- `PROGRESS_PERCENTAGE_VERIFIED`: `NO`

The value must not be rendered or aggregated as a percentage KPI without
source or owner confirmation.

## Date & Duration Semantics

The source labels directly distinguish planned-looking fields from fields with
the `Actual` qualifier:

- `tgl_mulai` / `tgl_selesai`: `Tanggal Mulai` / `Tanggal Selesai`.
- `tgl_actual_mulai` / `tgl_actual_selesai`: `Tanggal Actual Mulai` /
  `Tanggal Actual Selesai`.

One bounded record contained both planned date fields and both actual date
fields. This verifies the source date labels and planned/actual distinction,
but not whether the dates are outage boundaries, maintenance windows, or
project schedule boundaries.

Duration evidence:

- `dur_oh` is an integer explicitly labelled `Durasi OH (Hari)`; planned
  duration unit is verified as days.
- `dur_actual_oh` is an integer labelled `Durasi Actual OH`; its unit and
  derivation from actual dates are not exposed.

Readiness:

- `PLANNED_DATE_SEMANTICS`: `VERIFIED`
- `ACTUAL_DATE_SEMANTICS`: `VERIFIED`
- `OUTAGE_BOUNDARY_VERIFIED`: `NO`
- `DURATION_SEMANTICS`: `PARTIAL`

No schedule delay or date difference was calculated.

## Overhaul → Work Order Model

The existing direct header relationship remains verified:

```text
IP_DOM_OH.wonum → MXWODETAIL.wonum
```

MX-017A also verified the Scope PM path:

```text
IP_DOM_OH.domohnum
  ← IP_DOM_OH_SCOPE_PM.domohnum
  └─ IP_DOM_OH_SCOPE_PM.wonum → MXWODETAIL.wonum
```

The Scope PM JSON Schema exposes `domohnum`, `wonum`, and a `workorder` array.
The bounded scalar response also exposed `workorder_collectionref`. One
bounded parent verification and two exact Work Order reads matched the keys;
both Work Orders carried BSR/IP scope and an `assetnum`.

## Multi-WO Evidence

Two bounded `IP_DOM_OH_SCOPE_PM` records shared one parent `domohnum` and
exposed two distinct Work Order keys. Each key matched exactly one
`MXWODETAIL.wonum` record.

Classification:

- `OVERHAUL_MULTI_WO_MODEL`: `VERIFIED` as a technical Scope PM model.
- `PRIMARY_WO_VS_RELATED_WO`: `UNKNOWN` — the source did not prove whether
  `IP_DOM_OH.wonum` is primary, parent, execution, or another role relative to
  Scope PM Work Orders.
- `WORKORDER_COLLECTION_CARDINALITY`: `PARTIAL` — an array/schema reference is
  present, but selecting the collection returned HTTP 400 and no child
  collection was crawled.

The two Work Order records are evidence of linkage, not evidence that every
Overhaul has the same number or type of Work Orders.

## Overhaul → Asset Model

No direct `IP_DOM_OH.assetnum` field was exposed.

The accepted derived path remains:

```text
IP_DOM_OH.wonum → MXWODETAIL.wonum → MXWODETAIL.assetnum → Asset
```

The two Scope PM Work Orders each returned an Asset reference in exact
`MXWODETAIL` reads. Their Asset values were not persisted or compared. The
evidence does not prove whether all related Work Orders resolve to one Asset or
whether a multi-Asset Overhaul is valid.

Classification: `PARTIAL` (`OVERHAUL_ASSET_MODEL`).

## DOM_INSPEKSIMESIN Metadata

Live metadata returned HTTP 200:

- `/oslc/apimeta/DOM_INSPEKSIMESIN`: title `DOMINION - MASTER INSPEKSI MESIN &
  DETAILS PM (Loader)`, query capability `All`.
- `/oslc/jsonschemas/DOM_INSPEKSIMESIN`: title `DOM_INSPEKSI`, type `object`.
- Declared JSON Schema PK: composite `siklus`, `mesin`.
- `dom_inspeksiid` is a required integer technical identifier candidate;
  `dom_inspeksinum` is a human-facing relationship candidate.

Technical fields include `dom_inspeksinum`, `scopenum`, `siklus`, `mesin`,
`interval`, `durasi`, `status`, `newstatus`, P/R fields (`p1`–`p3`, `r1`–`r3`),
unit fields, and `dom_scopeline`.

The live schema defines `dom_scopeline` as an array with a child schema
reference under the inspection resource. The child schema was not fetched in
this bounded task. `dom_merktype` is another array reference.

## Overhaul → Inspection Relationship

Exact source-key evidence:

```text
IP_DOM_OH.inspeksinum
  → DOM_INSPEKSIMESIN.dom_inspeksinum
```

One BSR-scoped bounded Overhaul record supplied an inspection key. A minimal
exact query against `DOM_INSPEKSIMESIN` returned HTTP 200, one record, and the
same technical key. Classification: `VERIFIED` / `DIRECT_VERIFIED`.

No description, machine, date, or text similarity was used.

## Inspection Scope / Finding Evidence

Scope-line relationship:

```text
DOM_INSPEKSIMESIN.dom_scopeline
  → inspection child schema `dom_scopeline`
```

Classification: `VERIFIED` at metadata level. The child object structure and
line fields were not fetched, so line identity, finding, result, measurement,
acceptance, defect, recommendation, and follow-up Work Order semantics remain
unknown.

The inspection schema exposes technical P/R integer fields and status fields,
but their meanings were not defined by live labels or domain metadata.

Readiness:

- `INSPECTION_RESULT_SOURCE_IDENTIFIED`: `PARTIAL` — technical result-looking
  fields exist, but no authoritative result meaning is proven.
- `INSPECTION_FINDING_SOURCE_IDENTIFIED`: `NO`.
- `INSPECTION_RECOMMENDATION_SOURCE_IDENTIFIED`: `NO`.

The first exact inspection shape that selected both large array fields hit the
1 MiB safety cap. The cap was not increased; the successful retry selected
only identity/scope/status fields.

## Planned vs Realized Scope

`rencana_scope` and `realisasi_scope` are live integer fields with source labels
`Rencana Scope` and `Realisasi Scope`. `jumlahworekom` is an integer field, but
its unit and relationship to scope are not exposed.

Classification:

- `PLANNED_SCOPE_SEMANTICS`: `PARTIAL`
- `ACTUAL_SCOPE_SEMANTICS`: `PARTIAL`

No scope percentage, completion ratio, efficiency, or recommendation count KPI
was calculated.

## Cost Evidence

`realisasi_cost` is a live numeric field labelled `Realisasi Cost`. No currency,
unit, planned-cost counterpart, accounting period, or cost category was
exposed. No live cost value was persisted.

Classification:

- `OVERHAUL_COST_SEMANTICS`: `PARTIAL`
- `COST_VARIANCE_READY`: `NO`

## Performance Test Evidence

The exact source spelling is preserved:

```text
perfomance_test
```

Live metadata proves:

- type: boolean
- source label: `Perfomance Test Setelah OH`
- default: false
- bounded record type: boolean

No relationship/resource path, result detail, pass/fail domain, test report, or
acceptance rule was exposed.

Classification:

- `PERFORMANCE_TEST_SOURCE_IDENTIFIED`: `YES`
- `PERFORMANCE_TEST_RELATIONSHIP`: `UNKNOWN`
- `PERFORMANCE_TEST_SEMANTICS_READY`: `NO`

The source spelling was not renamed to `performance_test`.

## Cycle / Siklus Evidence

`IP_DOM_OH.siklus` is a string labelled `Jenis OH`. The inspection schema also
exposes `siklus`, and it is part of the inspection composite PK with `mesin`.

No live domain identifier, value list, or shared-domain metadata was found
proving that the two fields have the same domain. The meaning of cycle/type or
frequency therefore remains `UNKNOWN`.

## Relationship Graph

Verified edges only:

```text
Asset
  ↑ MXWODETAIL.assetnum
MXWODETAIL
  ↑ MXWODETAIL.wonum
IP_DOM_OH.wonum

IP_DOM_OH.inspeksinum
  → DOM_INSPEKSIMESIN.dom_inspeksinum
  → dom_scopeline child-schema reference

IP_DOM_OH.domohnum
  ← IP_DOM_OH_SCOPE_PM.domohnum
  └─ IP_DOM_OH_SCOPE_PM.wonum
       → MXWODETAIL.wonum
       → MXWODETAIL.assetnum
```

The `IP_DOM_OH_SCOPE_PM.workorder` array is a verified technical collection
reference, but its child cardinality and business role remain unresolved.

## Remaining Business Questions

- What status domain defines `EKS-COMP`, `DRAFT`, and other lifecycle stages?
- Which source event proves Overhaul completion?
- Is `progress` a percentage, task completion ratio, scope completion, or
  another measure? Is it manual or calculated?
- Are the four date fields workflow dates, outage boundaries, or project
  schedule dates?
- What unit and derivation rule apply to `dur_actual_oh`?
- Is `IP_DOM_OH.wonum` the primary execution WO, and what roles do Scope PM
  WOs play?
- What is the exact cardinality and child schema of the `workorder` collection?
- Can related Work Orders resolve to more than one Asset in a valid Overhaul?
- What do P1/P2/P3 and R1/R2/R3 mean in the inspection model?
- What fields in the scope-line child object represent findings, results,
  measurements, recommendations, or follow-up Work Orders?
- What does `perfomance_test` assert, and where is the result stored?
- What are the units/taxonomy for scope, cost, `jumlahworekom`, and `siklus`?
- Are the document booleans presence indicators, workflow gates, or merely
  attachments/document flags?

## NADI Readiness

```text
IP_DOM_OH_SCHEMA_COMPLETE: YES
OVERHAUL_STATUS_DOMAIN_IDENTIFIED: PARTIAL
OVERHAUL_COMPLETION_STATUS_IDENTIFIED: NO
PROGRESS_SCALE_IDENTIFIED: PARTIAL
PROGRESS_PERCENTAGE_VERIFIED: NO
OVERHAUL_COMPLETION_RULE_IDENTIFIED: NO
PLANNED_DATE_SEMANTICS: VERIFIED
ACTUAL_DATE_SEMANTICS: VERIFIED
DURATION_SEMANTICS: PARTIAL
OVERHAUL_TO_INSPECTION: VERIFIED
INSPECTION_RESULT_SOURCE_IDENTIFIED: PARTIAL
INSPECTION_FINDING_SOURCE_IDENTIFIED: NO
OVERHAUL_MULTI_WO_MODEL: VERIFIED
OVERHAUL_ASSET_MODEL: PARTIAL
PLANNED_SCOPE_SEMANTICS: PARTIAL
ACTUAL_SCOPE_SEMANTICS: PARTIAL
OVERHAUL_COST_SEMANTICS: PARTIAL
PERFORMANCE_TEST_SOURCE_IDENTIFIED: YES
PERFORMANCE_TEST_RELATIONSHIP: UNKNOWN
SCHEDULE_VARIANCE_READY: NO
PROGRESS_KPI_READY: NO
OVERHAUL_COMPLETION_KPI_READY: NO
```

## Request Audit

| Request class | Count/result |
| --- | --- |
| Authentication POST `/j_security_check` | 10 short-lived authenticated probe sessions |
| Metadata GET | 15: apimeta/JSON Schema for the three target objects, array definitions, and IP_DOM_OH property metadata |
| Business GET | 13: bounded Overhaul/inspection/Scope PM/Work Order probes, including 2 initial invalid-filter HTTP 500 responses, 1 inspection response-cap stop, and 1 Scope PM collection-select HTTP 400 |
| HEAD / OPTIONS | 0 |
| Browser navigation | 0 |
| Business writes | 0 |
| Pagination followed | 0 |

All live requests used the read-only discovery client and BSR-scoped query
shapes. No response cap was increased. No attachment was downloaded, no
person value was queried for enrichment, and no raw production record was
persisted.
