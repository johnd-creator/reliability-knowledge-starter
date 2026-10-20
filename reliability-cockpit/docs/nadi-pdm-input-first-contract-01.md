# NADI PdM input-first — provisional contract

20 October 2026. Local implementation candidate; no merge, runtime activation,
historical import, real-record entry, source request, or operational acceptance.
The user's input-first authorization permits provisional input coverage while
engineering decisions remain pending. It does not retrospectively approve the
method definitions in [the validation matrix](nadi-pdm-eng-validation-01.md).

## Capture contract and existing storage

Native measurement records retain versions1.0/1.1. New source-transcription
records use version1.2 with optional typed `input_capture`, schema version1.0,
and constant `purpose=PROVISIONAL_INPUT_ONLY`. Capture and native `measurements`
cannot coexist in one record. No source label is substituted for an approved
quantity or canonical point. The selected canonical asset remains the existing
record-authorization subject; selection does not verify a workbook's asset binding.

[InputCapture](../src/domain/pdm_input_capture.py) and
[its generated schema](../../reliability-data-contracts/schemas/pdm-input-capture.schema.json)
retain source alias/hash (nullable), literal source asset/sheet labels (nullable,
private authorized record data, up to2000 characters), sheet index (nullable), profile ID/version,
1–100 uniquely identified source rows and up to12 source clocks. Each row retains
its literal label, original scalar/type/unit, source point/axis labels, header
cells, optional source-field ID and value region. Value regions describe a source
data region, not proof of the exact cell transcribed. They distinguish columns
under merged headers without inventing measurement-point identity. SHA256 and
operator-entered coordinates are lineage claims, not file authentication or custody.

Row values distinguish source literal, reported formula result, manually reported,
and UNKNOWN origins. Row roles INPUT, REFERENCE, and SOURCE_ASSESSMENT retain
reported readings, explanatory limits/baselines, and reported assessments separately.
All remain provisional source input, never canonical measurements or automatic
diagnoses. Formulas are not evaluated; source results are not relabelled as raw
acquisitions. Literal units are preserved; no conversion/default unit is applied.
Context entries have explicit acquisition, operation, lab, instrument, procedure,
camera, sample or report roles, scalar values and optional units. This is not an
arbitrary method-extension object or an engineering procedure registry.

Scalar values retain string/integer/float/boolean/null types, including zero/null
and text-number distinctions. Strings are bounded to2000 characters, row labels
to2000, units/axis to80, source-point labels to200, contexts to20 per row, and
header references to20 per row. Unknown objects/arrays/fields, nonfinite numbers,
duplicate row IDs and forged purpose/approval fields are rejected. These are
explicit new input-protocol bounds, not changes to canonical Mart field contracts.

## Time precision and source claims

Each source clock retains its raw scalar independently of an explicit interpreted
`value` and a role: ACQUISITION, SAMPLE, ANALYSIS, REPORT or UNSPECIFIED. Precision
DATE validates a real `YYYY-MM-DD` calendar date; DATETIME requires a real ISO
date/time with explicit offset; LOCAL_DATETIME preserves a local date/time with
no timezone; TIME preserves time-only; RAW/UNKNOWN require interpreted value null.
Invalid calendar dates, time/offset mismatches and nonfinite raw numbers fail.
No source clock is copied into `measured_at` or `inspected_at`; date-only never
becomes midnight. Raw Excel serial/text remains raw unless an interpretation is
explicitly supplied. No epoch/timezone is inferred. Source-reported future dates
can be retained as source claims without overriding record-creation chronology or
claiming a future measurement. Sample, analysis and report dates are not merged.

## Revisions, review and evidence boundary

Existing authenticated authors, exact permitted assets, CAS, receipts and immutable
revision snapshots are reused in the existing application JSON store. No DDL or
new store is introduced. Native absent capture fields are omitted during canonical
serialization, preserving old1.0/1.1 full-record digests byte-for-byte. Existing
native records are not rewritten. Capture edits retain all typed metadata in the
new revision, including source-row lineage and clocks. A new native draft defaults
to1.1; a new capture draft becomes1.2 on the server.

Capture record review reuses the existing independent lifecycle. It remains
`NADI_RECORD_REVIEW_ONLY`, `ENGINEER_FIELDS_PENDING`, and `NOT_ASSESSED` after
approval. It does not approve field definitions, source transcription authority,
physical asset binding, method competence, thresholds, or engineering conclusions.
The authenticated recording inspector remains distinct from any source-reported
operator name retained as report context.

Both reviewed-evidence resolution and the owning-store guard reject capture records
with409 `PROVISIONAL_INPUT_NOT_CASE_EVIDENCE`. This applies even after record
approval. Typed frozen projection, exact revision presentation and the existing
16KiB snapshot bound require separate work before capture can become Case evidence.
Capture rows do not enter native measurement history or rawPlot, and do not create
factual Mart records. Native inspection→Case behavior remains unchanged.

## Twenty P1 decisions: input coverage without operational approval

Each row below remains `PENDING_ENGINEER_VALIDATION` for engineering semantics.
Provisional capture permits storing the stated source claims, not accepting them.

| ID | Safe provisional input | Engineering decision still pending |
|---|---|---|
| G01 | Source equipment labels and explicitly selected authorized record subject | Workbook/equipment→canonical asset binding |
| G02 | Input-profile version and reported method/procedure reference | Authorized engineer and approved definition version |
| V01 | Literal source point/axis labels | Physical location and orientation meaning |
| V02 | Literal quantity/unit/RMS/p-p labels | Quantity definition, equivalence and conversions |
| V03 | Reported acquisition/bandwidth context or UNKNOWN | Approved portable/installed scope and acquisition semantics |
| V04 | Instrument, mounting, calibration/procedure source context | Authoritative validity and scope across points |
| V05 | Precision-aware source clocks and operating context | Which time represents measurement and required operating conditions |
| T01 | Sample ID/point/equipment source labels | Exact sampling relationship and custody |
| T02 | Original lab scalars/units and value-origin classification | Lab quantity meaning, raw/derived approval and conversion |
| T03 | Laboratory/report/procedure source references | Authoritative method and laboratory scope |
| T04 | Separate sample, analysis and report source clocks | Approved measurement-time meaning |
| MC01 | Source phase/electrical-location labels | Physical electrical-point and asset binding |
| MC02 | Reported measurements/results/warnings in separate row roles | Quantity meaning, diagnosis, threshold and assessment |
| MC03 | Reported instrument/acquisition/load context | Required procedure and compatible operating scope |
| MC04 | Raw/partial/timezone-aware source clocks at their actual precision | Approved acquisition timestamp |
| TH01 | Temperature source values with nullable UNKNOWN unit | Unit evidence for each field |
| TH02 | Source method label/OTHER provisional context | Classification as routine thermal or IRT |
| TH03 | Reported camera/thermogram references as context/metadata | Actual thermogram custody, source binding and acquisition evidence |
| TH04 | Reported ambient/reference/emissivity context without defaults | Required method settings and approved reference meaning |
| TH05 | Reported formula result/reference/assessment classification | Formula evaluation, Delta T semantics, thresholds and diagnosis |

The six P2 decisions V06/T05/MC05/TH06/X01/X02 remain deferred. No comparability,
cross-inspection trend, severity calculation, cadence assumption, historical import
permission or custody acceptance follows from input coverage.

## Validation boundaries

Synthetic tests cover strict scalar/clock/schema behavior, legacy hash witnesses,
create/edit/replay/CAS, independent review, immutable snapshots, authorized asset
and self-review denials, absence from measurement history, and server Case refusal.
Actual QA malformed-input422, nonfinite rejection, sanitized responses, store503,
CSRF/revocation and PostgreSQL persistence are separately qualified in the owned
disposable fixture. Structural workbook coverage is an independent catalog result;
this contract alone does not claim every sheet/profile is covered or import data.

The pre-existing session-lease cleanup bug translated downstream FastAPI request
validation into a provider-outage503. The narrow fix lets RequestValidationError
propagate to the QA app's existing sanitized422 handler after rollback and guard
release. Store/provider failure classification, authentication policy, CSRF,
revocation and grant checks are unchanged. The initial bare-fixture failure is
retained as evidence; direct model checks do not substitute for actual HTTP422.
