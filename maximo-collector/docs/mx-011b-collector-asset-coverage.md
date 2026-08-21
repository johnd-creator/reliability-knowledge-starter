# MX-011B — Collector Asset Coverage Integrity & Registry Gap Diagnosis

Status: evidence complete for the current local snapshot.

This diagnosis separates the Maximo **List of Assets** business registry from
the broader Collector Equipment population. It does not change Collector rows,
the Reliability Mart, cursors, configuration, or NADI.

## Scope and inputs

- Registry input: local HTML-table export, sheet `List of Assets`.
- Registry fingerprint: SHA-256
  `aa0bd8fd22275aea3ecf8654ee37878106123b7dbdf58135fb783e853ee66a5f`.
- Registry shape: 845 rows, 845 nonblank Asset values, 845 unique values,
  zero duplicates, zero blank Asset values, and 352 unique Parent values.
- Collector and Mart access: local database `SELECT` statements only.
- Maximo verification: optional bounded read-only sample; 20 business GET
  requests, one at a time, no persistence.

The report file is production data and is intentionally not part of Git.
Identifiers, descriptions, person fields, raw source rows, credentials, and
business URLs are excluded from this evidence.

## Current registry coverage

| Population | Count |
| --- | ---: |
| Registered Reliability Assets in report | 845 |
| Exact matches in Collector Equipment | 581 |
| Registry Assets absent from Collector Equipment | 264 |
| Exact registry coverage | 68.8% |
| Collector Equipment total | 5,680 |
| Collector Equipment not in registry | 5,099 |

The missing 264 are not explained by an obvious inactive or out-of-scope
pattern: all are `BSR`, `OPERATING`, and `CS01`. All have an 18-character
identifier with a three-digit numeric suffix, an Install Date, a Created Date,
and a Parent value. Their `Area SERP` distribution is:

| Area SERP | Count | Percentage |
| --- | ---: | ---: |
| CS01 | 58 | 22.0% |
| CS0A | 61 | 23.1% |
| CS0B | 31 | 11.7% |
| CS0C | 114 | 43.2% |

### Unit coverage matrix

| Registry Unit | Registry | Exact match | Missing | Coverage |
| --- | ---: | ---: | ---: | ---: |
| CS01 | 837 | 573 | 264 | 68.5% |
| CS02 | 1 | 1 | 0 | 100.0% |
| CS03 | 1 | 1 | 0 | 100.0% |
| Blank | 6 | 6 | 0 | 100.0% |

The gap is therefore concentrated in the dominant current registry unit, not
in the six non-CS01 rows.

For matched rows, the report Parent and Collector `parent_id` agree exactly
for 581 of 581 rows. The issue is absence of records, not a broad parent-value
normalization mismatch among rows that are present.

## Collector population and synchronization audit

Collector Equipment has 5,680 unique IDs. Its stored population includes
multiple unit values: CS01 4,988, TU 643, CS0B 39, CS0C 5, CS0A 3, CS02 1,
and CS03 1. Status is OPERATING 3,375, INACTIVE 2,292, and NOT READY 13.
Equipment class is PRODUCTION 5,648, IT 17, and FACILITIES 15.

Parent and ancestor values are present for 5,504 rows (96.9%); `has_children`
is true for 849 and false for 4,831. `source_changed_at` spans
2024-02-22 through 2026-08-20, while `status_changed_at` spans
2014-04-16 through 2026-08-18. The Equipment ORM has no created-at or
observed-at column, so freshness cannot be proved from those fields.

The mixed-unit population is consistent with an accumulated local population
from more than one historical scope/configuration. Existing rows were not
deleted or reclassified.

The current configuration audit is the same for both verified Asset object
structures:

| Setting | `mxapiasset` / `mxasset` |
| --- | --- |
| Scope | `siteid="BSR"` |
| Required field/value | `eq11=CS01` |
| Runtime equipment unit | CS01 |
| Order | `-changedate` |
| Watermark | `changedate` |
| Page size | 100 |
| Max pages | 1000 |
| Watermark query | enabled |

The local database has no `mxapiasset` or `mxasset` SyncCursor and no Asset
CollectRun history. This means the current table cannot be certified as the
result of a complete cursor-managed traversal. It also means the local state
is not provenance-complete enough to prove when the 264 rows were skipped.

## `eq11=CS01` semantic check

Among the 581 matched registry rows, report Unit and Collector Unit agree for
575 (99.0%). For the 575 rows with source `eq11`, report Unit equals
`sources.maximo.eq11` for 575 (100.0%), and Collector Unit equals that source
value for 575 (100.0%). The source `plant` value is `TU` for all 581 matched
rows, so `plant` is not a substitute for the report Unit field in this
reconciliation.

Conclusion: `eq11=CS01` is semantically aligned with the registry Unit in the
available matched evidence. The 264 missing rows are all CS01, so the current
required-value filter does not explain their absence. Do not remove or change
the filter solely from this diagnosis; repair the missing coverage with an
auditable follow-up first.

## Parent gap and hierarchy evidence

Of 352 registry Parent values, 75 are present in Collector and 277 are
missing, for 21.3% parent coverage. The missing Parent population has 276
identifiers of length 13 and one of length 11; all have the same three-digit
numeric suffix shape. They are parents of 638 registry rows, 630 of which are
CS01. Children per missing Parent range from one to 42, so the gap is not
limited to isolated single-child records.

In the in-memory hierarchy of 5,680 Equipment rows:

- 5,099 rows are not in the registry snapshot;
- 2,200 non-registry rows resolve to a registry ancestor, all as direct
  registry parents in the stored hierarchy;
- 2,899 have no registry ancestor;
- 1,315 have a broken parent reference;
- no cycles were observed;
- maximum observed hierarchy depth is five.

This supports retaining broader Equipment relationship context while keeping
registered Reliability Assets as a separate business projection. It does not
justify calling every non-registry row a component or spare part.

## Work Order relationship analysis

The local Collector contains 112,258 Work Orders: 95,637 with an equipment
reference and 16,621 without one. Using category precedence from MX-011A
(direct registry identity first), the aggregate relationship counts are:

| Relationship | Count |
| --- | ---: |
| Direct registry Asset target | 35,984 |
| Direct registry target absent from Collector Equipment | 6,437 |
| Non-registry Equipment with registry ancestor | 21 |
| Equipment with no registry ancestor | 23,482 |
| Non-registry target missing from Collector | 36,150 |

The two “missing” measures must not be conflated. A Work Order can name a
registered Asset that is absent from the local Equipment table; that is a
current registry coverage issue. The 36,150 figure is the non-registry,
historical target gap after direct registry identity has been classified
separately.

The latest local `source_changed_at` is 2026-08-20 15:08 UTC. The recent
period is the exact 30-day interval ending at that timestamp. The age profile
below reports both strict Equipment absence and the category-D non-registry
absence:

| Age band | WO | With equipment | Direct registry | Direct registry absent locally | Strict Equipment absent | Category-D non-registry absent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0–30 days | 2,742 | 2,716 | 2,706 | 541 | 542 (20.0%) | 1 |
| 31–90 days | 2,166 | 2,157 | 2,142 | 383 | 386 (17.9%) | 3 |
| 91–365 days | 8,516 | 8,482 | 8,298 | 1,505 | 1,518 (17.9%) | 13 |
| 1–3 years | 21,798 | 21,667 | 19,956 | 3,587 | 4,098 (18.9%) | 511 |
| >3 years | 77,036 | 60,615 | 2,882 | 421 | 36,043 (59.5%) | 35,622 |

The earlier “one missing target in the latest 30-day period” is the category-D
number. The strict 542 also includes 541 direct registry IDs that are known
from the business report but are not yet present in Collector Equipment. This
distinction is material: current registry coverage affects recent Work Orders
even when their business Asset identity is recognizable.

The sharp increase in category-D missing targets after three years supports
`HISTORICAL_EQUIPMENT_COVERAGE_GAP`. It may reflect retired, removed, renamed,
or otherwise no-longer-current Equipment; this task does not assign one of
those meanings without source evidence.

## Current Reliability Mart impact

The current Mart contains 277 `asset_master` rows. Of these, 258 match the
registry snapshot; 587 registry Assets are absent from the Mart and 19 Mart
rows are not in the registry snapshot. This confirms that 277 is a bounded Mart
load, not the authoritative business registry.

The Mart contains 174 maintenance references: 14 resolved and 160 unresolved
against `asset_master`. Of the unresolved references, 61 exist in local
Collector Equipment and seven resolve to a registry ancestor through the local
hierarchy. No Mart rows were modified.

## Bounded source verification

Phase A showed an incomplete/stale local synchronization history, so a bounded
verification was run against the two already-verified Asset structures. A
deterministic in-memory sample of 10 missing registry identities was queried
with exact identity constraints, once through each structure. Results:

| Result | Count |
| --- | ---: |
| Sample size | 10 |
| Found in `MXAPIASSET` | 10 |
| Found in `MXASSET` | 10 |
| Found in both | 10 |
| Found in neither | 0 |
| Business requests | 20 |
| HTTP 200 | 20 |

This bounded sample does not prove all 264 source rows, but it provides no
evidence of an MXAPIASSET-versus-MXASSET coverage difference or identifier
normalization mismatch. It is consistent with incomplete or stale local
Equipment synchronization.

## Diagnosis

Primary classifications:

- `COLLECTOR_SYNC_INCOMPLETE`: current registry coverage is only 68.8%, all
  missing rows satisfy the configured CS01 unit, and no complete Asset run or
  cursor is recorded locally.
- `COLLECTOR_LOCAL_STATE_STALE`: the table contains multiple unit populations,
  but current cursor/run provenance is absent; the state cannot be treated as a
  deliberately complete current snapshot.
- `HISTORICAL_EQUIPMENT_COVERAGE_GAP`: non-registry Work Order target loss is
  concentrated in the >3-year band.

Not supported by the evidence:

- `COLLECTOR_SCOPE_FILTER_GAP` as the explanation for the 264 current registry
  rows: all 264 are inside the configured CS01 value.
- `REGISTRY_IDENTIFIER_MISMATCH`: matched identifiers and parent values agree,
  and all 10 bounded source samples were found in both verified structures.
- `MXAPIASSET_COVERAGE_DIFFERENCE`: not observed in the bounded sample.

## Recommended repair and architecture

MX-011C should perform a cursor-independent, bounded reconciliation/backfill
of the missing current registry population through the existing verified Asset
structures, with an explicit collect-run audit and cursor semantics. It should
compare `MXAPIASSET` and `MXASSET` results before writing, preserve all existing
Equipment rows, and measure coverage against the 845-row registry after the
repair. Do not reset the current cursor or delete rows as part of MX-011B.

Keep the current working architecture decision:

`MODEL_C_SEPARATE_REGISTRY_RELATION`

- Equipment: broad Maximo technical identity and hierarchy.
- Registered Reliability Asset: a row in the current Maximo List of Assets
  registry snapshot.
- Non-registry Equipment: neutral supporting Equipment; role unclassified.
- Mart: retain relationship-capable Equipment context and represent registry
  membership as a separate evidence-backed relation/projection.
- NADI: default to registered Reliability Assets only after Collector coverage
  is repaired and measured.

The report has future discovery value: Last Wellness, Current Condition, Last
WO, Last ACR, Last MPI, Judgement Date, and Recommended Program are populated
for most registry rows; Maintenance Strategy is sparse (30/845, 3.6%), while
Engineering Judgement fields are present for 253/845 (29.9%). These are
opportunities for Asset Health, Maintenance Strategy, Engineering Judgement,
and Action Board work, but their source semantics require verification and no
field is added to Contract v1 here.

## Mutation and privacy audit

- Maximo requests: 20 GET, zero business writes.
- Collector writes: 0.
- Mart writes: 0.
- SyncCursor writes: 0.
- NADI changes: 0.
- Contract changes: 0.
- Production report, raw rows, identifiers, descriptions, and person fields:
  not committed.

MX-012R remains held until the current registry coverage repair is completed
or deliberately accepted with measured compensating behavior. The recommended
next task is `MX-011C — Collector Asset Coverage Repair`.
