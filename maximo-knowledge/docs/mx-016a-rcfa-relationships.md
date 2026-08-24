# MX-016A RCFA Relationship Discovery

## Executive Result

MX-016A established new, bounded source evidence for the RCFA workspace without
changing Maximo data or any NADI implementation:

- `IPRCFA` exposes a direct `assetnum` field. Three BSR-scoped exact reads
  returned a non-empty Asset reference, so RCFA → Asset is
  `DIRECT_VERIFIED`.
- `IPRCFA` exposes a direct `root_cause` string. The field was non-empty in the
  three bounded records, but its narrative meaning and taxonomy are not yet
  governed source semantics.
- `IPRCFAFDT` is live-verifiable through metadata and a bounded collection
  request. A bounded FDT member and one exact parent RCFA read matched on
  `norcfa` and `siteid/orgid`, establishing RCFA → FDT as
  `DIRECT_VERIFIED`.
- No `wonum`, Work Order identifier, Failure Event identifier, or verified
  relationship link was found in the live RCFA schema or bounded records.
  RCFA → Work Order and RCFA → Failure Event therefore remain `UNKNOWN`.
- FDT fields such as `actionplan`, `feedback`, and `progress` are technical
  candidates only. Recommendation/action semantics and completion rules remain
  unresolved.

This is knowledge evidence only. No RCFA, FDT, Work Order, or other Maximo
business record was written.

## Existing RCFA Boundary

NADI already exposes IPRCFA as factual RCFA evidence. Existing canonical
relationship fields remain unresolved unless source evidence proves them:

| Canonical field | MX-015 state before MX-016A | MX-016A result |
| --- | --- | --- |
| `asset_ref` | `NULL` | Direct source field now verified; product mapping remains a separate task |
| `location_ref` | `NULL` | `UNKNOWN` |
| `workorder_ref` | `NULL` | `UNKNOWN` |
| `failure_event_ref` | `NULL` | `UNKNOWN` |

The evidence is scoped to the authenticated Maximo instance and the bounded
`BSR` / `IP` sample. It does not generalize to other sites or organizations.

## IPRCFA Metadata

Live metadata requests returned HTTP 200:

- `/oslc/apimeta/IPRCFA`: title `IP LOADER RCFA`, query capability `All`.
- `/oslc/jsonschemas/IPRCFA`: title `RCFA`, resource `IPRCFA`, type `object`.
- The live JSON Schema lists `norcfa` as `pk` and requires `rcfaid`,
  `kategori`, and `ispronia`. `norcfa` and `rcfaid` remain identity
  candidates; uniqueness across revisions was not tested.

Relationship-relevant technical fields present in the live schema include:

`assetnum`, `root_cause`, `failure_code`, `fcdesc`, `micode`, `engterkait`,
`amaterkait`, `kd_mesin_maximo`, `lv1code`, `lv2code`, `lv1_equipment`,
`tgl_gangguan`, `act_selesai_kaj`, `targ_selesai_kaj`, `ren_tglworkshop`, and
`act_tglworkshop`.

The schema proves technical field presence. It does not by itself prove that a
field is a Work Order reference, Failure Event identity, or business KPI date.

## IPRCFAFDT Metadata

Live metadata requests returned HTTP 200:

- `/oslc/apimeta/IPRCFAFDT`: title `IP LOADER RCFA FDT`, query capability `All`.
- `/oslc/jsonschemas/IPRCFAFDT`: title `FDT_RCFA`, resource `IPRCFAFDT`, type
  `object`.
- The live JSON Schema lists `fdt_rcfaid` as `pk`; `fdt_rcfaid` is the best
  technical identity candidate, with `nofdt` retained as an untested business
  number candidate.

The schema exposes `fdt_rcfaid`, `nofdt`, `norcfa`, `siteid`, `orgid`,
`progress`, `progress_description`, `actionplan`,
`actionplan_description`, `feedback`, `activity`, `activity_description`,
`worktype`, `worktype_description`, `type`, `type_description`, and
`description`.

The previous documented FDT request returned HTTP 400. MX-016A did not treat
that result as absence. A metadata-supported bounded collection request
returned HTTP 200 with one member. The exact parent filter attempted in this
task also returned HTTP 400, so the successful relationship proof uses the
bounded FDT member plus a reverse exact RCFA verification rather than claiming
that the parent filter syntax is supported.

## RCFA → Detail Relationship

The verified edge is:

`IPRCFA.norcfa ↔ IPRCFAFDT.norcfa`

Evidence:

1. One bounded `IPRCFAFDT` member returned non-empty `norcfa`, `siteid`, and
   `orgid`.
2. A separate exact `IPRCFA` GET for that transient parent key returned HTTP
   200.
3. The two records matched on `norcfa` and on `BSR/IP` scope.

Classification: `DIRECT_VERIFIED`.

The relationship is source-key evidence, not a description or date match. The
FDT member was inline in the bounded collection response; no next page and no
deeper child collection were followed.

## RCFA → Asset Relationship

Verified path:

`IPRCFA.assetnum → Asset.assetnum`

The live schema proves the direct `assetnum` field and three BSR-scoped exact
RCFA reads returned it non-empty. Classification: `DIRECT_VERIFIED`.

This task did not resolve the Asset endpoint or change the NADI canonical
mapping. It establishes source relationship evidence for a later, separately
reviewed implementation task.

## RCFA → Work Order Relationship

No live `wonum`, `workorderid`, `wo`, Work Order collection reference, or
explicit Work Order relationship was found in the IPRCFA JSON Schema or the
minimal bounded RCFA records.

Fields such as `engterkait`, `micode`, and equipment-related fields were not
interpreted as Work Order references. No exact linked Work Order was available
to verify against `MXWODETAIL`.

Classification: `UNKNOWN`.

## RCFA → Failure Event Relationship

The IPRCFA schema contains `failure_code` and the date-like `tgl_gangguan`, but
the bounded records did not expose a non-empty selected failure-code value, and
no Failure Event identifier, event object, or source relationship link was
verified. A failure-code field alone does not define a Failure Event.

Classification: `UNKNOWN`.

RCFA → Work Order, if discovered later, must not be promoted automatically to
RCFA → Failure Event.

## Root Cause Detail Evidence

`IPRCFA.root_cause` is a direct string field in the live JSON Schema and was
non-empty in all three bounded exact RCFA records. Classification for technical
source identification: `VERIFIED`.

The field may contain narrative or source-entered analysis, but this task did
not persist its values and did not derive a cause taxonomy, causal tree,
failure mechanism, or governed root-cause class. Those semantics are
`SOURCE_SEMANTICS_REQUIRE_VERIFICATION`.

No separate root-cause child object or verified FDT-to-root-cause edge was
observed.

## Recommendation / Action Evidence

The FDT JSON Schema exposes technical candidates:

- recommendation/action candidate: `actionplan`, `actionplan_description`
- feedback/progress candidates: `feedback`, `progress`,
  `progress_description`
- activity/type candidates: `activity`, `activity_description`, `type`,
  `type_description`

The bounded member exposed `progress` but did not expose non-empty selected
values for `actionplan`, `feedback`, `activity`, or `type`. The schema proves
field presence, not that these fields represent an approved recommendation,
corrective action, preventive action, owner, or completion state.

Classification:

- `RCFA_RECOMMENDATION_SOURCE`: `PARTIAL`
- `RCFA_ACTION_SOURCE`: `PARTIAL`

No person values or action narratives were persisted.

## Status Semantics

The live IPRCFA schema exposes `status` and `status_description`. Existing
local factual RCFA evidence includes raw status values such as `CLOSE`,
`KAJDONE`, and `VEROK`, but no live domain metadata, lifecycle definition, or
owner-confirmed label semantics were obtained in this task.

Classification: `UNKNOWN`.

The raw status values must not be translated into completion semantics for an
RCFA KPI.

## Category Semantics

The live schema exposes `kategori` and `kategori_description`. Existing local
factual records contain raw category values, including numeric-looking values,
but no source domain/value-list definition or verified business taxonomy was
obtained.

Classification: `UNKNOWN`.

## Relationship Graph

Only the following edges are source-backed:

```text
Asset
  ↑ direct assetnum
IPRCFA (norcfa)
  ↕ direct key match on norcfa
IPRCFAFDT (fdt_rcfaid; nofdt)
```

Additional verified direct field evidence:

```text
IPRCFA.root_cause  [direct string field; semantics unresolved]
```

The following edges remain deliberately absent:

```text
IPRCFA  → MXWODETAIL              UNKNOWN
IPRCFA  → Failure Event           UNKNOWN
IPRCFAFDT → Root Cause object     UNKNOWN
IPRCFAFDT → Recommendation object UNKNOWN
IPRCFAFDT → Action object         UNKNOWN
```

## Scope Evidence

All live bounded business evidence used for the relationship findings carried
`siteid=BSR` and `orgid=IP`, including the matched IPRCFAFDT member and its
exact IPRCFA parent. The structured evidence records this as verified
`BSR/IP` scope.

This is `BSR/IP` applicability evidence, not a claim that the same custom
objects, domains, or relationships are identical at another site or
organization.

## Remaining Business Questions

- Does `root_cause` have a governed taxonomy or is it narrative-only?
- What source object, if any, defines the Failure Event associated with an RCFA?
- Does `failure_code` refer to a Maximo failure hierarchy, an RCFA-specific
  classification, or another source namespace?
- Does the instance expose a direct RCFA→Work Order link through another
  relationship or application-specific object?
- What does FDT mean in this instance, and is it one-to-many per RCFA across
  revisions?
- Do `actionplan`, `feedback`, and `progress` represent recommendation/action
  lifecycle states, and what are their completion rules?
- What are the verified domain meanings of `status` and `kategori`?
- Which dates represent request, failure, analysis completion, workshop
  planning, workshop execution, or KPI completion?

## NADI Readiness

```text
IPRCFA_SCHEMA_COMPLETE: YES
IPRCFAFDT_OBJECT_IDENTIFIED: YES
RCFA_TO_DETAIL_RELATIONSHIP: VERIFIED
RCFA_TO_ASSET: DIRECT_VERIFIED
RCFA_TO_WORKORDER: UNKNOWN
RCFA_TO_FAILURE_EVENT: UNKNOWN
ROOT_CAUSE_DETAILS_IDENTIFIED: YES
RCFA_RECOMMENDATION_SOURCE: PARTIAL
RCFA_ACTION_SOURCE: PARTIAL
RCFA_STATUS_SEMANTICS: UNKNOWN
RCFA_CATEGORY_TAXONOMY: UNKNOWN
RCFA_ASSET_WORKSPACE_READY: YES
RCFA_COMPLETION_KPI_READY: NO
```

`ROOT_CAUSE_DETAILS_IDENTIFIED=YES` means the direct technical field was
identified; it does not mean root-cause semantics or taxonomy are ready for a
new product metric. `RCFA_COMPLETION_KPI_READY` remains `NO` because status,
date, and completion governance are unresolved.

## Request Audit

| Request class | Count/result |
| --- | --- |
| Authentication POST `/j_security_check` | 4 attempts; first failed before any business GET, later sessions authenticated |
| Metadata GET | 4: apimeta and JSON Schema for IPRCFA and IPRCFAFDT |
| Business GET | 7: three exact RCFA reads, one exact-parent FDT HTTP 400, two bounded FDT HTTP 200 reads, one exact RCFA parent HTTP 200 |
| Separate href detail dereferences | 0; the FDT relationship used bounded collection evidence and exact parent verification |
| HEAD / OPTIONS | 0 |
| Browser navigation | 0 |
| Business writes | 0 |

All business requests were bounded and read-only. No pagination was followed,
no raw business payload was committed, and the local Mart was used only for
selecting bounded candidate identifiers.
