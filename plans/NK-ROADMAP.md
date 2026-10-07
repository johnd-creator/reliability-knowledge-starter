# NK — child roadmap / sidequest

NK is an intentional second application of Power Plant Data Platform:
**coal calorific value prediction**, not part of NADI's Reliability domain.
NADI remains the main product priority. This document is authoritative for NK
roadmap status; implementation details stay with NK when its code is integrated.

## Git position and architecture

At audited `main ef07a26`, `NK/` is absent. The existing implementation is
**UNMERGED** at `0c800dac1da6ef863afdb193021176fe7feac073` on
`feature/pi-governed-source-adapter`. This PR documents that work without
copying its source, models, notebooks, images, binary data or training exports.

```text
PI → existing PI Collector → stored snapshots / timeseries → API → NK
Manual sliders / CSV ────────────────────────────────────────→ NK
```

NK owns model/scaler feature order, input mapping and validation, and prediction.
It does not own PI credentials/authentication, SQL credentials, a duplicate
collector or a new database. Manual input remains available for fallback and
simulation **by explicit mode choice**, never silently mixed into invalid PI
inputs. Prediction history is session-local and bounded, with JSON export.

## Child-roadmap status

Status distinguishes branch implementation from mainline acceptance.

| ID | Deliverable | Observed implementation | Mainline / acceptance status |
|---|---|---|---|
| NK-00 | Manual ML baseline | Streamlit predictor, saved model/scaler, sliders/CSV and manual predict flow exist | **UNMERGED**; manual implementation complete on feature, production model validation not certified |
| NK-01 | PI Collector integration | GET-only reader of stored `/attributes` and `/snapshots`, input-source choice | **CURRENT / PARTIAL / UNMERGED**; no approved 13-feature live dataset |
| NK-02 | Feature mapping governance | Mapping editor with source/training units, evidence and local JSON persistence | **PARTIAL / UNMERGED**; all 13 initial mappings are `unknown`; no approved complete feature map |
| NK-03 | One-click latest data and review | “Ambil data terbaru”, feature table, optional fragment refresh | **PARTIAL / UNMERGED**; reads/predicts also on render/refresh; explicit fetch → review → predict gate remains to implement |
| NK-04 | Quality and time alignment | Identity, finite value, quality, unit, timezone, age/skew checks and tests | **PARTIAL / UNMERGED**; code exists, real source/mapping acceptance not established |
| NK-05 | Historical / as-of prediction | Current path reads latest snapshots | **PLANNED**; choose coherent historical batch through existing collector API, never a new SQL store |
| NK-06 | Model validation | Existing model/report artifacts, not independent operational validation | **NEEDS_REVIEW**; accepted units/labels, leakage, time split, error/bias and uncertainty calibration |
| NK-07 | Operational pilot | No Git-backed pilot acceptance identified in audited branch | **PLANNED**; scope, engineering sign-off, safety and monitoring |

The feature commit contains tests; this docs-only task inspects their presence
and source behavior but does not rerun NK from `main`, retrain, or validate the
claimed accuracy figures. UI model accuracy/95% confidence wording is a model
validation review item, not platform acceptance evidence. Preserve the existing
model while evaluating those claims separately.

## Intended GET DATA semantics

```text
Input Source: Manual | PI Collector
  → [GET LATEST DATA]
  → resolve 13 approved mappings
  → fetch latest stored values
  → validate registry identity and numeric/type suitability
  → validate quality flags and units
  → validate timezone, source age and inter-feature timestamp skew
  → show reviewed 13-feature batch and validation state
  → user reviews values
  → [PREDICT NK]
```

A fetch action must identify its input batch and cannot simply pick arbitrary
latest numbers with unrelated timestamps. Current feature behavior predicts
automatically once validation succeeds; NK-03 must reconcile this with the
explicit user-review target without removing manual mode. Optional auto-refresh
must not imply that a new batch has been reviewed or approved automatically.

- Block missing, non-finite, bad/unknown quality, stale or misaligned data.
  Never substitute zero or previous manual values.
- Confirm units and meaning; preserve exact training feature order/model pair.
  Supported pressure conversions do not establish gauge/absolute equivalence.
- **PS = pemakaian sendiri**, confirmed in the feature documentation. Tag and
  W/MW source/training unit remain unconfirmed. Do not assume auxiliary sums.
- SFC requires an approved source/formula; Economizer mapping remains open.
  APH inlet/outlet are distinct measurements, not interchangeable name matches.
- A valid source snapshot is not evidence that ML predictions are operationally
  accurate. Review data drift, uncertainty and ground-truth labels in NK-06.

## Recommended NK sequence

1. Review/split the NK portion of `0c800da` into a dedicated future PR from main,
   with runtime artifacts/data publication and reproducibility reviewed explicitly.
   Do not merge the mixed feature branch as part of this roadmap task.
2. Resolve and evidence all 13 mappings/units; accept one complete bounded batch.
3. Complete separate fetch/review/predict semantics and quality/time acceptance.
4. Add as-of replay through existing collector capabilities if needed.
5. Validate the unchanged model against accepted operational labels, then pilot.

PI credential checking is currently deferred at the user's request following
HTTP 401 in the operational handoff. This is not a permanent data-source limit
or a reason to bypass the collector. No live request was made during this audit.

## Branch-only implementation references

Immutable evidence at `0c800da`:
[application](https://github.com/johnd-creator/reliability-knowledge-starter/blob/0c800dac1da6ef863afdb193021176fe7feac073/NK/nk_web_app.py),
[input validator](https://github.com/johnd-creator/reliability-knowledge-starter/blob/0c800dac1da6ef863afdb193021176fe7feac073/NK/pi_input.py),
[PI panel](https://github.com/johnd-creator/reliability-knowledge-starter/blob/0c800dac1da6ef863afdb193021176fe7feac073/NK/pi_panel.py),
[mapping config](https://github.com/johnd-creator/reliability-knowledge-starter/blob/0c800dac1da6ef863afdb193021176fe7feac073/NK/pi_feature_mapping.json),
[NK instructions](https://github.com/johnd-creator/reliability-knowledge-starter/blob/0c800dac1da6ef863afdb193021176fe7feac073/NK/AGENTS.md).
