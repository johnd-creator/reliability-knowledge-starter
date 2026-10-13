# NADI-PDM-CENTER-INPUT-01 — development candidate

Date: 2026-10-13 (Asia/Jakarta). Base main:
`2e190c2b51fde50e0467d6d5165ebb1060902867`.
Branch: `codex/nadi-pdm-center-input-01`. Delivery: separate DRAFT PR, no merge.

## Outcome and independent gates

| Gate | State |
|---|---|
| IMPLEMENTED | Native multi-point entry, authorized register/history, raw-sample plot and existing review/Case handoff |
| TESTED | Hermetic backend, presentation safety, responsive component browser and existing regression |
| MERGED | NO — DRAFT candidate |
| VISIBLE on official HTTPS3000 | NO — deliberately untouched |
| ENGINEER APPROVED | PENDING — Q01–Q10, field dictionary and comparability |
| OPERATIONALLY ACCEPTED | NO — identity, activation, custody and UAT require separate approval |

[Responsive evidence and hashes](evidence/nadi-pdm-center-input-01/README.md) are
explicitly synthetic intercepted component screenshots, not live acceptance.
[DRAFT PR82](https://github.com/johnd-creator/reliability-knowledge-starter/pull/82) records exact delivery HEAD/backend/frontend CI and handoff;
local tests cannot prove deployment or production readiness.

## Functional decisions

`/pdm` has Register Inspeksi, Input Pengukuran, Riwayat & Tren and Engineering
analysis access. Existing detail, revision history and diagnostic workbench remain.
New entry selects exact IDs from the trusted session's permitted asset directory;
existing asset-context provides available identity/context, and the server verifies
Registry membership before writes. Unavailable descriptions do not create an asset.

InspectionDraft v1.1 remains unchanged: up to 100 native measurement rows retain
scalar type, zero/null distinction, original quantity/unit/timestamp, point,
observation and hypothesis. Inspector comes from the authenticated session, not a
browser field. Method enums VIBRATION/IR_THERMOGRAPHY/MCSA/TRIBOLOGY/DGA/OTHER remain;
PD is not DGA. Blank numeric/text/boolean entry is rejected; explicit UNKNOWN maps
to null. No averaging, conversion, daily schedule, score or diagnosis.

Shared optional `instrument_ref`, `procedure_ref`, `orientation` map to the existing
bounded scalar `method_extension`. They apply to the entire acquisition, remain
candidates, and never approve comparison. Different per-point acquisition contexts
need separate inspections with the current strict v1.1 envelope. Existing extension
fields, attachment metadata and case references survive edits. There is no arbitrary
JSON editor. Native metadata reference inputs use the existing attachment allowlist,
byte/hash/name bounds and METADATA_ONLY_NOT_UPLOADED; no URL, upload or file custody
claim. Metadata is inspector-reported, not proof of content or access.

AREA FAN, AREA MILL and Logsheet 6 kV are versioned candidate **input contexts**, not
methods. Their selection survives an authorized refresh, but no unvalidated workbook
fields/units/formulas are injected or persisted outside the schema. `inputFields`
defines reusable shared/point/context paths. Two additional contexts can extend the
same versioned registry without a new store or lifecycle. Workbook-specific layouts
and durable approved template identity await the field mapping decision. No Excel
parser/discovery or workbook re-upload was performed.

## Narrow compatible QA HTTP extensions

- `GET /v1/engineering/inspections`: optional asset/method/status/search/since/until
  filters before counting and pagination. Search covers ID, asset, inspector,
  observations and hypotheses. Date bounds are inclusive actual inspection times.
- `GET /v1/engineering/inspections/measurement-history`: same authorization plus
  exact point/quantity filters and measured-time date bounds. Pages count individual
  events across all matching authorized records, not a loaded inspection page.
- `POST /v1/engineering/cases/{id}/evidence`: optional
  `expected_inspection_revision` for MANUAL_INSPECTION/FROZEN_SNAPSHOT only. Existing
  requests remain compatible; mismatch returns EVIDENCE_VERSION_CHANGED/409.

List/event responses declare AUTHORIZED_POPULATION and INSPECTED_AT/MEASURED_AT respectively. The UI requires those markers; an older backend that ignores filters or lacks history is refused instead of claiming global filtering. This candidate requires the reviewed QA backend containing the extensions. No frontend-only compatibility approval or backend restart is granted by this task.

No schema/migration/table or new persistence engine. Auth, Origin, CSRF, leases,
RBAC, asset ownership, contributor exclusions, transactional receipts and CAS are
reused. These router factories remain excluded from operational `create_app`.

Reads stream authorized existing JSON documents in batches, retain only the result
page, and use deterministic record-ID/measurement-index order. They do not claim
chronological ordering or unlimited operational-scale performance: filtered totals
require a scan of the authorized QA population. Operational scale/index qualification
is pending. Pagination remains bounded to offset 10000 and limit 100, with existing
QA ingress/deadline/body safeguards. Unknown timestamps are excluded only when an
explicit time range is selected. Superseded values remain in immutable revision
history; the measurement register shows events from the current inspection version
without duplicating every audit snapshot as a new measurement event.

## Trend safety

The table always retains original samples and provenance. The chart is an unconnected
scatter of numeric, timestamped samples from **one inspection revision**, point,
quantity, unit and shared acquisition context, within the explicitly disclosed loaded
measurement page. Axes use actual timestamps; no intermediate values are generated.
Instrument/procedure/orientation/regime must be present and consistent. Null, text,
boolean, missing time/context, different points/units/quantities/provenance, mixed
revisions or acquisitions block plotting with a reason. Even a displayed scatter is
not engineer-approved comparability or an operational trend. Cross-inspection and
portable/DCS/PI series joining remain unavailable until approved compatibility.

## Workflow, conflicts and security

DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED/RETURNED/REJECTED is reused, including
legacy IN_REVIEW reading. Accepted records remain immutable without the existing
reviewer-controlled reopen. Self-review and another assigned reviewer are denied by
the server. APPROVED means record review, not asset health or maintenance authority.

The command hook locks duplicate clicks and retains the same receipt ID on retry of
the same failed intent. Its optional PdM-scoped memory ref preserves that ID through
trusted-session rereads/remounts; identity/scope loss or explicit discard clears it. Unsaved native input is protected on unload/links and kept
only in component memory during trusted-session rereads. Recovery is bound to the
same identity, permitted asset and **original** edit revision; it is cleared for
signed-out/denied/changed identity or removed scope. Reading a new revision does not
silently rebase CAS or overwrite input. Discard/reopen on the latest revision is an
explicit user action. No session/password/draft browser storage is introduced.

An authorized engineer supplies a Case title/problem after record review. Existing
Case create/link commands preserve human facts and hypotheses; the selected inspection
revision is checked and locked before freezing evidence. Case creation and evidence
link are separate existing transactions: a link failure retains and identifies the
Case draft, offering a retry of the same exact evidence instead of duplicating the
Case. No automatic Case diagnosis/recommendation or Maximo WO mutation.

## Validation and distinct self-review

- Backend: 41 focused inspection/PdM/review tests PASS. Broader local backend/auth
  selection: 177 discovered, 119 executed PASS, 58 PostgreSQL-dependent skips. No
  persistent QA DSN was configured. The CI job adds the PdM suite on its named
  disposable `nadi_application_test` PostgreSQL store as a separate qualification.
- Presentation: 16 PdM original-value, metadata, template and trend safety checks
  PASS; existing engineering/phase2/workflow/HTTP/bounded proxy/auth/product/UX/login/
  localization/provenance suites PASS. TypeScript and lint PASS; one existing
  EngineeringWorkspace hook warning is unchanged.
- Browser: 41 checks in [PdM result](evidence/nadi-pdm-center-input-01/results.json) passes native
  entry, refresh recovery, retry ID, zero/null, raw sparse samples, review, exact Case
  handoff, denied-session clearing and 1440/768/390 layouts. Existing network-isolated
  localization/all-route regression: 395 checks PASS. Both use intercepted fixtures;
  server enforcement is proven separately by trusted HTTP tests, not browser mocks.
- Production build PASS; `git diff --check` PASS. Exact-head CI must independently
  pass before this candidate is recommended for implementation review.

Meaningful first-pass findings and corrections:

| Finding | Severity / correction | Retest |
|---|---|---|
| Select label included option content, breaking exact lookup | Medium: explicit measurement select labels | Keyboard/browser PASS |
| New draft absent from old register page after save | Medium: reload authorized register on acknowledged mutation | Full journey PASS |
| Refresh could discard unsaved form, context or failed receipt ID | High: identity/scope-bound memory recovery, preserve original CAS base and same failed intent ID | Refresh/retry/browser/type checks PASS |
| Retained entry view after AUTHOR role removal | Medium: native form clears/hides when trusted role or scope is removed | Active-form role-loss browser PASS |
| Older backend could ignore filter parameters silently | High: explicit authorized-population/time-basis response markers, fail-closed UI | Older-backend negative fixture and HTTP proof PASS |
| Native grid controls lacked V1 styling/touch size | Medium: shared tokens, 44px controls, narrow row cards | Three widths/light-dark PASS |
| Potential silently newer evidence at Case handoff | High: optional exact inspection revision and owning-store lock | Positive/stale/re-reviewed HTTP PASS |
| Plot fixture selection reset after filter / review input reset after reload | Harness: wait for acknowledged page/state and reselect context, enter new review rationale | Browser PASS |
| Screenshot HTML charset absent | Harness: UTF-8 head metadata | Screenshots/rendered copy reviewed |
| Historical localization hash intentionally changed by optional Inspection read fields | Reviewed additive typing; updated pinned hash, original transport/enum checks retained | Localization PASS |

Initial sandbox TestClient runs stalled and child compiler launch was denied; those
owned test runs were stopped and repeated outside the restrictive test sandbox using
only hermetic fixtures. One invalid-pagination assertion in the bare inherited HTTP
fixture exposed its pre-existing unhandled-validation/lease cleanup limitation; that
assertion was removed from this filter test (pagination bounds are unchanged and
covered by existing service tests). No authentication-policy change was made to force
this harness result. Failed attempts are not runtime crashes or live acceptance.

## Preservation and remaining gates

Official HTTPS3000, QA API, operational APIs, collectors, DB/schema/session/audit,
backup/controller/runtime configuration, Phase1 policy and PR75–81 were not accessed
or changed by runtime operations. No service was started/restarted, no live URL opened,
no source GET, no persistent record inspection/mutation, and no FIX06 experiments.
Five original PNG hashes match reference provenance; original untracked `23496711.xls`
and other worktrees/evidence remain. PR75–81 remain OPEN at their original heads.
This is scope-based preservation, not a new database/container-state attestation.

Rollback needs no runtime action because this candidate was never selected. Original
main and all previous source worktrees remain available. Source rollback would revert
this separate candidate only; any future runtime selection requires separate approval
and the official controller with source compatibility checks.

Pending: PO visual review, Q01–Q10 engineer field/point/instrument/procedure signoff,
workbook mappings, approved cross-acquisition comparability, secure attachment custody,
operational identities, engineer UAT and operational activation. Phase0–5 milestones
are unchanged. Phase1 hard-expiry/operational action remains a separate PO/operator
matter; this task does not read, reset or extend the policy.
