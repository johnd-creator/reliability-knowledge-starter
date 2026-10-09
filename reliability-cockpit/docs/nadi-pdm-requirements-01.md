# NADI-PDM-REQ-01 — Engineer voice and measurement investigation

Date: 2026-10-09. Documentation acceptance only; requirements below are proposals,
not approved method fields, thresholds, acquisition authority or runtime activation.
Baseline: `f54643f3510bf505628a1400024784faab46e496` (main, including merged PR61).

## Evidence and uncertainty

The statements below come from the project-owner task NADI-PDM-REQ-01. They are
reported engineer practice, not an independently witnessed interview, validated
plant inventory or reviewed instrument specification. No Excel/export sample was
opened, no source request was made and no instrument accuracy was tested.

| Statement ID | Reported observation | Requirement trace |
|---|---|---|
| V01 | Vibration, IRT, MCSA, Tribology and PD were mentioned | R01, Q07 |
| V02 | Portable readings occur during inspection, investigation or symptoms; continuous 24-hour acquisition is not the manual workflow | R01, R03, Q09 |
| V03 | Engineers use Excel trends | R03, R06, Q01 |
| V04 | Abnormal readings lead to spectrum/thermal evidence and interpretation | R04, R05, Q02, Q03, Q06 |
| V05 | Maximo may contain abnormality context | R07, Q10 |
| V06 | Installed DCS vibration measurements exist according to the report; suitability/accuracy concerns were raised | R02, R08, Q04, Q05 |
| V07 | “30% acr” was mentioned without an established definition | Q08; no metric or rule proposed |

PD is unresolved. The existing DGA method enum is implementation evidence, not
proof that the reported PD means DGA. Routine inspection frequency is unknown;
no daily normal measurement requirement follows from V02. Bearing-housing sensors
are not classified as inherently inaccurate. Instrument, mounting, measurement
point, bandwidth, operating condition and comparability require engineering review.

## Repository-confirmed foundation

The [inspection schema](../../reliability-data-contracts/schemas/manual-inspection.schema.json)
preserves canonical asset, method/version, inspector, inspection/submission times,
original measurements, operating context, observations, interpretations, attachment
metadata, case references and revisions. `ENGINEER_FIELDS_PENDING` and
`NOT_ASSESSED` remain explicit. Generic extension fields do not constitute an
approved method specification.

[Inspection workflow](manual-inspection-workflow.md) separates submission,
independent review and accepted revisions. [Recommendation workflow](recommendation-workflow.md)
requires reviewed case/evidence and retains informational existing-WO references.
Approval means NADI record review, not source fact, equipment health or maintenance
authorization. [ADR006](adr/006-engineering-workspace.md) separates application
writes from the SELECT-only Mart. Historical candidate wording records its original
checkpoint; merged implementation does not establish operational acceptance.

Concept coverage follows the existing [five-image analysis](../../docs/design/NADI-CONCEPT-ALIGNMENT.md)
and [Bundle C coverage](../../docs/design/NADI-BUNDLE-C-CONCEPT-COVERAGE.md): PdM Center
supports method/evidence navigation; Asset Health 360 supplies asset context;
Recommendations and Action Board support reviewed local follow-up. This task read
those analyses, not a new visual inspection. Concept scores/colors are not approved
engineering semantics. Irregular-time trends and diagnostic attachment interactions
remain proposed coverage, not a claim of implemented functionality.

## Intended engineer journey

1. Select a registered canonical asset and an explicit measurement point/method.
2. Review irregular measurement events on their actual timestamps; filter point,
   orientation and compatible operating context. Missing periods remain missing.
3. Select a reported abnormal reading. Preserve original value/unit and the
   engineer's abnormality annotation; no automatic threshold or traffic light.
4. Open authorized spectrum, waveform, thermogram or laboratory evidence references.
5. Record an interpretation/hypothesis separately from measurement and source facts.
6. Submit an Engineering Case with version-bound evidence for independent review.
7. Create a local NADI recommendation from reviewed findings, retaining rationale,
   provenance, revisions and optional existing WO reference. Never create, update,
   approve, close or cancel a Maximo WO.

## Candidate requirements and acceptance criteria

All R rows are CANDIDATE / NOT_APPROVED. Implementation claims are limited to the
foundation described above; new forms, parsers and trends need separately scoped work.

| ID | Proposed requirement / field envelope | Acceptance criterion | Dependencies |
|---|---|---|---|
| R01 | Episodic inspection event; canonical asset, method/version, inspector, measured/submitted times | Preserve unknown time/frequency; do not manufacture daily or continuous records | Q07, Q09; existing envelope |
| R02 | Measurement point, orientation, instrument/procedure reference and operating context | Engineer-controlled point identity; original location/mounting/bandwidth/context recorded where applicable | Q04, Q05; approved field dictionary |
| R03 | Original value/type/unit/time and selectable irregular-time history | Plot actual samples only; gaps remain visible; no silent interpolation, resampling or conversion | Q01, Q05, Q09; R02 |
| R04 | Spectrum/waveform/thermogram/lab evidence references with provenance | Version-bound authorized references; attachment custody/access/integrity reviewed before real upload | Q02, Q03, Q04; secure storage approval |
| R05 | Measurement, observation, interpretation, review decision and recommendation remain distinct | Independent reviewer; revisions immutable; unknown never becomes approved finding or healthy state | existing lifecycle; engineer UAT |
| R06 | Controlled Excel discovery/import proposal | Obtain sanitized authorized samples and explicit column/unit/time/point mapping before choosing parser; preserve source-row lineage and reject unresolved identity | Q01, Q04, Q05; custody and mapping approval |
| R07 | Existing WO/abnormality context as read-only references | Exact approved source field/record and asset binding; absence remains UNKNOWN; zero Maximo mutation | Q10; separate collection authorization if needed |
| R08 | Portable versus installed DCS/PI comparability review | No merged series until method/location/unit/bandwidth/operating compatibility explicitly approved | Q04, Q05, Q06; engineering comparison decision |

Method-specific proposed fields are in the [engineer input packet](manual-pdm-engineer-input.md).
They remain proposals: no acceptance limits, required method fields, alarm limits,
unit normalization, health score, risk metric or diagnosis is approved here.

## Engineer validation register

All owners below are proposed responsibilities; no individual appointment or approval
is asserted. Every unresolved item remains `PENDING_ENGINEER_VALIDATION`.

| ID | Required artifact / controlled question | Proposed owner | Decision acceptance | Status |
|---|---|---|---|---|
| Q01 | Sanitized Excel trend sample, columns, sheets, units and time semantics | PdM engineer/data custodian | Approved mapping and sample-use permission; parser pending | PENDING_ENGINEER_VALIDATION |
| Q02 | Spectrum/waveform export sample and acquisition metadata | Vibration engineer | Export format, point, axes and acquisition context identified | PENDING_ENGINEER_VALIDATION |
| Q03 | IRT thermogram plus associated data/export sample | IRT engineer | Image/data relationship and required context approved | PENDING_ENGINEER_VALIDATION |
| Q04 | Instrument maker/model, procedure and export formats | Method engineer | Documented acquisition capability/calibration/mounting/bandwidth where relevant | PENDING_ENGINEER_VALIDATION |
| Q05 | Asset and measurement-point identification rules | Asset/PdM owner | Exact canonical binding, orientation and point-version rules approved | PENDING_ENGINEER_VALIDATION |
| Q06 | Green/yellow/red and abnormal semantics, technical authority | Responsible engineering owner | Explicit approved definitions or continued NOT_ASSESSED; no inferred threshold | PENDING_ENGINEER_VALIDATION |
| Q07 | What does PD mean; relationship, if any, to DGA? | Method engineer | Exact method name/scope confirmed; no automatic alias | PENDING_ENGINEER_VALIDATION |
| Q08 | What does “30% acr” mean? | Reporting engineer | Exact definition, unit/context and intended use established or excluded | PENDING_ENGINEER_VALIDATION |
| Q09 | Routine versus condition-triggered frequency by method/equipment | PdM owner | Actual cadence/triggers documented; no assumed daily schedule | PENDING_ENGINEER_VALIDATION |
| Q10 | Exact source and interpretation of Maximo abnormality records | Maximo/reliability owner | Authorized object/field semantics and source-vs-human distinction established | PENDING_ENGINEER_VALIDATION |

## Phase 2 PdM Measurement & Investigation backlog

| Backlog | Deliverable | Gate / dependency |
|---|---|---|
| M01 | Engineer sample and terminology discovery packet | Q01–Q10 answers; no production collection |
| M02 | Versioned method/point/instrument field contracts | M01; approved field dictionary, not generic enum inference |
| M03 | Irregular measurement chronology and point filters | M02; R01–R03; missing-data behavior tests |
| M04 | Controlled import and diagnostic attachment workflow | M01/M02; R04/R06; secure attachment custody and provisioning |
| M05 | Measurement-to-case interpretation and independent review | M03/M04; R05; trusted identity and revision/concurrency acceptance |
| M06 | Informational WO context and local recommendation handoff | R07/Q10; reviewed case, no Maximo writes |
| M07 | Engineer UAT with representative episodic histories | M03–M06; field sign-off and isolated/authorized environment |

No backlog item is implemented by this documentation task. Operational identity,
application writer provisioning, secure storage, field approval and UAT remain gates.

## Phase 3 acquisition and diagnostic separation

Continuous/periodic installed DCS/PI signals, episodic portable readings and human
diagnostic interpretations are separate evidence regimes. Source quality, source
freshness, collection time and human review status remain separate dimensions.
No combined trend or derived feature is valid solely because asset names agree.
Compatibility requires approved measurement method/quantity, physical point and
orientation, original units, bandwidth/acquisition procedure, instrument context
and operating regime. Unknown compatibility blocks combination. No automatic
interpolation bridges sparse events to continuous series.

[Phase 3 design](nadi-phase3-diagnostic-foundation.md) stays DESIGN READY / not
operational. Diagnostics, alerts, scoring and ML additionally require approved
use case, sufficient governed data, method/threshold policy, reviewable provenance
and ground truth. Engineer concerns are investigation inputs, not model labels.

## Acceptance, roadmap and safety

Documentation acceptance requires all statements traceable to proposals or explicit
unknowns; all ten Q rows pending; no method/threshold approval implied; and the
measurement → interpretation → independent review → local recommendation boundary
preserved. Phase0 COMPLETE (accepted factual scope); Phase1 CURRENT/PARTIAL;
Phase2 foundations MERGED, operational/UAT PARTIAL; Phase3 DESIGN READY, not
operational; Phase4 recommendation foundation implemented, operational acceptance
pending; Phase5 PLANNED. These are repository reconciliation states, not a runtime audit.

This task changes Markdown only. Production source GET/write, WO mutation, DB
write/DDL, deployment/restart, source approval and Phase1 evidence/journal/cursor
mutation are zero. Active LiveDev is preserved. No workbook inspection, parser,
collector, threshold activation or new PdM functionality was performed.
