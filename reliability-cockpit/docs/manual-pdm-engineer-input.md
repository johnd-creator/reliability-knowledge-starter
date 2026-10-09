# PH2-03A — manual PdM envelope and engineer validation packet

## Current requirements reconciliation — 2026-10-09

The foundation is merged at main `f54643f3510bf505628a1400024784faab46e496`;
operational field approval and UAT remain pending. Earlier candidate wording below
records historical checkpoints. See the [engineer voice and validation register](nadi-pdm-requirements-01.md)
for episodic measurement history, point/instrument requirements and M01–M07 backlog.
All method-field proposals remain NOT_APPROVED / PENDING_ENGINEER_VALIDATION.
Reported PD is unresolved; the existing DGA enum does not establish PD = DGA.
No daily cadence, acceptance threshold or installed-sensor accuracy conclusion is approved.

Candidate, isolated only. Existing application store, never Reliability Mart.
Measurements retain original value/type/unit, nullable unknown, measured time;
inspection/submission/record times are separate. Observations and interpretations
are separately labelled human content. Review approves a NADI record only, not
an equipment condition, standard limit, source mapping, signal or maintenance action.
No numeric severity/health/failure predictions. All methods NOT_ASSESSED with
ENGINEER_FIELDS_PENDING. Empty/unknown measurement sets are representable rather
than converted to zero/healthy. Inspector is the authenticated recording inspector;
delegated transcription/technical-review authority requires a separate decision.

Method registry covers VIBRATION, IR_THERMOGRAPHY, MCSA, TRIBOLOGY, DGA, OTHER.
Versioned bounded optional extension values allow evolution without pretending
field proposals are approved method schemas. Future registered procedure/field
versions require engineer signoff before operational use.

| Method | Optional field proposals | Responsible engineer questions |
|---|---|---|
| Vibration | point, axis, quantity, frequency band, sensor, load | Which quantities/units/points, instrument calibration and speed/load context? Which approved procedure version? |
| IR | target area, emissivity, ambient context, camera, reference area | Which thermal settings/context and image annotations are required? How should reported units be preserved? |
| MCSA | phase, sensor, sampling/load/frequency context | Which capture quantities and instrument/sample context permit comparison? |
| Tribology | sample point/id, lubricant reference, laboratory/context | Which sample chain-of-custody, lab report quantities and original units? |
| DGA | sample id/location, lab, reported gas quantity, report version | Which lab method/report fields and transformer context are authoritative? |
| Other | procedure/name, quantity, equipment context | Who owns method/version and approves required/optional fields? |

For every method confirm inspector/reviewer qualifications, delegation, exact
asset/measurement-point identity, original units, nullable/required fields,
attachment confidentiality/retention and operational procedure. Technical limits,
severity rules and normalization are deliberately NOT proposed as accepted.

Attachments are allowlisted bounded METADATA_ONLY_NOT_UPLOADED references;
no file fetch/upload/URL, claim of scanning or downloadable content. Actual secure
upload, antivirus/content verification, private object ownership and retention
are separate activation work. Metadata checksum does not prove file authenticity.

Bundle C candidate: DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED/RETURNED/REJECTED;
legacy1.0 IN_REVIEW remains readable. See [inspection workflow](manual-inspection-workflow.md).
Independent review excludes creator,
inspector and all contributors. Revisions/CAS/receipts are transactional;
approved snapshots persist in immutable history. Source evidence links resolve
exactly through local catalogs; manual measurements need canonical asset identity,
not an invented PI AF mapping. Session-authenticated operational mounting,
writer/migration preflight and real field approval remain BLOCKED.
