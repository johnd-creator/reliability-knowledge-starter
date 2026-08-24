# MX-014A FMEA Item Semantics Discovery

## Executive Result

`IPFMEAITEM` is now technically identified through the repository OAS and a
live Maximo JSON Schema. A bounded BSR-scoped collection request returned one
inline item with technical fields including `fmea_lineid`, `fmeanum`,
`failuremode`, `criticality`, `function`, `riskprioritynumber`, `siteid`, and
`orgid`.

The highest-priority parent relationship is verified:

```text
IPFMEAITEM.fmeanum → IPFMEA.fmeanum
```

The item-to-Asset path is therefore derived through the already verified
header relationship `IPFMEA.assetnum → Asset`. The item has no verified direct
`assetnum` field.

This task identifies technical fields, not their business rules. Failure mode,
severity, occurrence, detectability, criticality, and risk-priority semantics
remain subject to source/business verification. No RPN was calculated and no
NADI product implementation is justified by this discovery alone.

## Existing FMEA Header Boundary

The existing `IPFMEA` evidence is the factual FMEA-header boundary. Verified
header fields include:

- `fmeaid`, `fmeanum`, `revision`, `status`, `description`
- `assetnum`, `failurecode`
- `lastmodifieddate`, `statusdate`

`IPFMEA.assetnum → Asset` is verified. The header's `failurecode` remains a
failure-code fact; it is not treated as an item-level failure mode.

## IPFMEAITEM Technical Identity

The repository OAS documents both collection and detail paths:

- `/os/ipfmeaitem` — collection
- `/os/ipfmeaitem/{id}` — detail
- OAS tag: `IP LOADER FMEA ITEM (IPFMEAITEM)`

The live JSON Schema path `/oslc/jsonschemas/IPFMEAITEM` returned HTTP 200 and
identified the schema title as `FMEA_LINE`. The schema requires:

- `fmea_lineid` — integer
- `criticality` — boolean

The preferred item identity candidate is `fmea_lineid`, because it is required
in the live schema and was present in the bounded member. Uniqueness was not
tested. `fmeaitemcode` is a second integer identity candidate from the schema,
but it was not present in the selected bounded member. Neither `rowstamp` nor
an `href` is promoted to business identity.

The underlying MBO name was not separately exposed by the bounded metadata
requests. `FMEA_LINE` is the live schema title, not an assertion that all
business semantics are established.

## Metadata / Schema Evidence

The live schema exposed these fields and primitive types. The source spelling
`occurence` is retained exactly as exposed by Maximo.

| Field | Type | Required in schema | Conservative role |
|---|---|---:|---|
| `fmea_lineid` | integer | yes | identifier candidate |
| `fmeaitemcode` | integer | no | identifier candidate |
| `fmeanum` | string | no | parent FMEA reference candidate |
| `parent` | integer | no | parent reference candidate |
| `function` | string | no | business attribute candidate |
| `failuremode` | string | no | failure-mode candidate; semantics unverified |
| `failurecause` | string | no | failure-cause candidate; semantics unverified |
| `problemcode` | string | no | problem/failure reference candidate |
| `failurelist` | integer | no | failure reference candidate |
| `failuredetectedmethod` | string | no | business attribute candidate |
| `criticality` | boolean | yes | business attribute candidate |
| `severity` | integer | no | severity candidate; scale unverified |
| `occurence` | integer | no | occurrence candidate; scale unverified |
| `detection` | integer | no | detectability candidate; scale unverified |
| `riskprioritynumber` | integer | no | source risk-priority candidate |
| `severity_description` | string | no | descriptive business attribute |
| `occurence_description` | string | no | descriptive business attribute |
| `detection_description` | string | no | descriptive business attribute |
| `description` | string | no | business attribute |
| `rev` | integer | no | revision candidate |
| `revdate` | string | no | timestamp/revision-date candidate |
| `siteid` | string | no | site scope |
| `orgid` | string | no | organization scope |
| `href` | string | no | resource reference |

The schema also exposes `note`, `localref`, `type`, `componen`,
`nexthigerassembly`, `functionalassembly`, `system`, `_id`, and the fields
listed above. No enum, domain, scale, directionality, formula, or lifecycle
rule was exposed by the schema.

The live `/oslc/apimeta/IPFMEAITEM` request returned HTTP 301. Because the
redirect target was not independently captured and verified, it is not used
as field evidence. The JSON Schema is the authoritative metadata evidence in
this task.

## Item → FMEA Relationship

A bounded `IPFMEAITEM` request returned a non-empty `fmeanum` field. A separate
bounded `IPFMEA` request, scoped using that transient value and selecting only
header identity, scope, and Asset fields, returned one header with the same
`fmeanum`. Raw identifiers were not persisted.

Evidence class: `DIRECT_VERIFIED`.

```text
IPFMEAITEM.fmeanum → IPFMEA.fmeanum
```

This proves the parent-header path for the observed bounded record. It does
not prove historical/version selection rules for all item records.

## Item → Asset Relationship

The live item schema and bounded member did not expose `assetnum`. The verified
header relationship supplies the following path:

```text
IPFMEAITEM.fmeanum
    → IPFMEA.fmeanum
    → IPFMEA.assetnum
    → Asset.assetnum
```

Evidence class: `DERIVED_VERIFIED_PATH`.

This is not a direct item-to-Asset relationship. No direct item-level
`assetnum` edge is claimed.

## Field Semantic Matrix

| Field | Type | Candidate Meaning | Evidence | Evidence Class | NADI Relevance |
|---|---|---|---|---|---|
| `fmea_lineid` | integer | Item identity | Required by live schema and present in one bounded member; uniqueness not tested | `VERIFIED` technical field; identity `CANDIDATE` | Possible stable item key; not yet uniqueness-proven |
| `fmeaitemcode` | integer | Alternate item identity | Present in live schema; not in bounded selected member | `VERIFIED` technical field; identity `CANDIDATE` | Candidate only |
| `fmeanum` | string | Parent FMEA reference | Bounded item value matched one bounded `IPFMEA` header request | `DIRECT_VERIFIED` | Parent navigation |
| `parent` | integer | Parent reference | Live schema only; target object not proven | `DOCUMENTED_ONLY` | Unknown |
| `function` | string | FMEA function text/code | Field present in schema and one bounded member | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Potential item fact |
| `failuremode` | string | Failure-mode candidate | Field present in schema and one bounded member; label semantics not independently confirmed | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Potential failure-mode detail |
| `failurecause` | string | Failure-cause candidate | Field present in schema; not present in the selected bounded member | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Potential failure-cause detail |
| `problemcode` | string | Problem/failure code candidate | Field present in schema; no relationship or domain verified | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Not mapped to Failure Code |
| `failurelist` | integer | Failure reference candidate | Field present in schema; target list/object unknown | `UNKNOWN` | Unknown |
| `failuredetectedmethod` | string | Detection method text/code | Field present in schema; business domain unknown | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Potential control/detail fact |
| `criticality` | boolean | Criticality indicator candidate | Required schema field and present in bounded member | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | No NADI risk mapping yet |
| `severity` | integer | Severity candidate | Integer field in live schema; no scale or directionality | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Cannot calculate risk |
| `occurence` | integer | Occurrence candidate | Integer field in live schema; source spelling retained; no scale or directionality | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Cannot calculate risk |
| `detection` | integer | Detectability candidate | Integer field in live schema; no scale or directionality | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Cannot calculate risk |
| `riskprioritynumber` | integer | Source risk-priority candidate | Integer field in schema and present in bounded member | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Source field exists; RPN governance unknown |
| `severity_description` | string | Severity description candidate | Schema only | `UNKNOWN` | Unknown |
| `occurence_description` | string | Occurrence description candidate | Schema only | `UNKNOWN` | Unknown |
| `detection_description` | string | Detection description candidate | Schema only | `UNKNOWN` | Unknown |
| `rev` | integer | Revision candidate | Schema only; no lifecycle rule | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Version handling unknown |
| `revdate` | string | Revision date candidate | Schema only; date format/lifecycle not tested | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Version validity unknown |
| `siteid` | string | Site scope | Schema field and bounded BSR query | `VERIFIED` field/scope path | BSR applicability |
| `orgid` | string | Organization scope | Schema field and one bounded BSR/IP scope match | `VERIFIED` field/scope path | IP applicability |

Technical field presence is not treated as proof of business meaning. In
particular, names resembling FMEA textbook dimensions do not establish a
1–10 scale, directionality, or a scoring rule.

## Failure Mode Evidence

`failuremode` is a live string field and was present in the bounded item
member. This is the strongest current technical candidate for an item-level
failure-mode field, but the business label, controlled domain, code/display
relationship, and relationship to `failurecode` remain unverified.

Evidence class: `SOURCE_SEMANTICS_REQUIRE_VERIFICATION`.

`IPFMEA.failurecode` is not substituted for `IPFMEAITEM.failuremode`.

## Effect / Cause Evidence

No field named `effect` or an equivalent failure-effect field was identified in
the live JSON Schema or the bounded selected member. This is `NOT_FOUND` within
the bounded evidence scope, not proof that no effect is available through
another relationship or report projection.

`failurecause` is present as a string in the schema, but it was not in the
selected bounded member and its business semantics, domain, and linkage to a
failure mode are not verified.

## Severity / Occurrence / Detectability Evidence

The schema exposes integer candidates:

- `severity`
- `occurence` (Maximo's source spelling)
- `detection`

The schema provides no allowed values, scale bounds, directionality, label
mapping, or validity rule. No assumption is made that the scale is 1–10 or
that a higher value is worse. These fields cannot be used to calculate or
classify risk in NADI V1.

## RPN Evidence

`riskprioritynumber` is an integer field in the live schema and was present in
the bounded item member. This establishes a source-field candidate only.

Unknowns include:

- whether the field is stored or calculated;
- the formula and component scales;
- directionality and rounding;
- missing-value behavior;
- revision and lifecycle applicability;
- thresholds, rank bands, and business governance.

Evidence class: `SOURCE_SEMANTICS_REQUIRE_VERIFICATION`.

No RPN was calculated. `RPN_READY` remains `NO`.

## Recommendation / Strategy Evidence

No recommendation, proposed maintenance, maintenance strategy, PM, Job Plan,
or engineering-action field or relationship was verified in the live schema or
bounded item structure. Any relationship to Maintenance Strategy remains
`UNKNOWN`.

## Scope Evidence

The live schema exposes both `siteid` and `orgid`. The item request used the
bounded `siteid="BSR"` shape. One returned member's scope fields matched the
NADI product scope `BSR/IP`; raw record values were not persisted.

This is one BSR/IP observation. It is not a claim about other sites or
organizations.

## Relationship Graph

Only verified edges are shown:

```text
Asset
  ↑ assetnum (VERIFIED on IPFMEA)
IPFMEA
  ↑ fmeanum (DIRECT_VERIFIED)
IPFMEAITEM
```

There is no verified direct `IPFMEAITEM.assetnum` field. No edge to Failure
Code, Maintenance Strategy, Recommendation, Effect, Control, or another item
object is drawn.

## Remaining Business Questions

- Does `failuremode` carry the authoritative business meaning of Failure Mode,
  and is it text, a code, or a related record?
- What are the labels, allowed domains, scales, directionality, and validity
  rules for `severity`, `occurence`, `detection`, and `criticality`?
- Is `riskprioritynumber` calculated or stored, and what formula, missing-data
  rule, revision rule, and governance apply?
- Is there an item-level Failure Effect field or relationship outside the
  bounded schema view?
- What is the relationship between `failurecause`, `failuremode`,
  `problemcode`, and `failurelist`?
- What are the controls, recommendations, maintenance strategies, actions, or
  Job Plan relationships, if any?
- Is `fmea_lineid` unique across organization/site/revision, or is a composite
  identity required?
- How do item revisions and historical validity relate to the parent FMEA?

## NADI Readiness

```text
IPFMEAITEM_SCHEMA_IDENTIFIED: YES
IPFMEAITEM_OBJECT_IDENTIFIED: YES
ITEM_IDENTITY_IDENTIFIED: PARTIAL
ITEM_TO_FMEA_RELATIONSHIP: VERIFIED
ITEM_TO_ASSET_RELATIONSHIP: DERIVED_VERIFIED_PATH
FAILURE_MODE_FIELD_IDENTIFIED: YES
FAILURE_EFFECT_FIELD_IDENTIFIED: NO
FAILURE_CAUSE_FIELD_IDENTIFIED: YES
SEVERITY_FIELD_IDENTIFIED: YES
OCCURRENCE_FIELD_IDENTIFIED: YES
DETECTABILITY_FIELD_IDENTIFIED: YES
RPN_SOURCE_IDENTIFIED: YES
RPN_READY: NO
ITEM_LEVEL_FMEA_READY: PARTIAL
```

The `YES` values for technical fields do not imply that the corresponding
business semantics are ready for a product contract. Item-level FMEA remains
partial until identity, labels/domains, relationships, revision behavior, and
risk governance are verified.

## Request Audit

All Maximo business access was read-only.

| Request class | Count | Result |
|---|---:|---|
| Authentication POST `/j_security_check` | 7 attempts | Authentication only; no business mutation |
| Metadata GET | 2 | `/oslc/apimeta/IPFMEAITEM` HTTP 301; `/oslc/jsonschemas/IPFMEAITEM` HTTP 200 |
| Business GET | 6 | Bounded `IPFMEAITEM`/`IPFMEA` probes only; one scope query returned HTTP 400 |
| Detail dereference GET | 0 | No detail link was followed |
| HEAD | 0 | Not used |
| OPTIONS | 0 | Not used |
| Business writes | 0 | No POST/PUT/PATCH/DELETE/merge/status action |

The request budget was not exceeded: metadata/OAS live GET usage was 2/15 and
business GET usage was 6/10. No next page was followed, no response cap was
relaxed, and no raw production payload or identifier was committed.
