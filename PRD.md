# NADI Product Requirements Document

Version: 1 · Updated: 2026-10-10 · Task: NADI-DOC-FOUNDATION-01.
Product Owner direction is recorded below; detailed designs remain review candidates.
This document specifies the product, not deployment authorization or completed UAT.

## 1. Vision and business objectives

NADI — Reliability Data Platform integrates factual data and governed engineering
evidence for PLTU Banten 1 Suralaya. It supports traceable reliability and maintenance
decisions while preserving the Shared Data Foundation's source ownership.

Objectives: make factual asset context easy to find; preserve measurements and
reasoning through independent review; connect reviewed findings to accountable
local recommendations; expose evidence limitations; and retain a history usable by
future engineers. Quantified business benefit targets require an agreed baseline;
no availability, failure-reduction or prediction-accuracy benefit is claimed here.

## 2. Users

| Product persona | Primary need |
|---|---|
| Reliability Manager | Portfolio context, evidence limitations and follow-up visibility |
| Reliability Engineer | Asset investigation, cases and supported interpretations |
| PdM Engineer | Measurement points, episodic histories and diagnostic evidence |
| Maintenance Engineer | Maintenance context and informational existing WO references |
| Engineering Reviewer | Independent version-bound review and decision history |
| System Administrator | Authorized account, configuration and audit administration |

Personas are not an implemented permission matrix. Current trusted-session roles,
asset scopes and review exclusions are defined by the existing Engineering contracts;
future role mapping requires separate approval and tests.

## 3. Requirements and traceability

IDs below are stable. All are product requirements from the task unless explicitly
marked PROPOSED. Their presence is not implementation acceptance. Status evidence
lives in [the roadmap](plans/NADI-ROADMAP.md) and [development log](DEV-LOG.md).

| ID | Functional requirement | UI specification | Delivery dependency / acceptance |
|---|---|---|---|
| FR-01 | Preserve factual Executive Overview and approved semantics | UI-01 | UX-04; factual route/data regression |
| FR-02 | Asset register, health overview and contextual detail | UI-02/03 | UX-05; exact asset identity, unknown states |
| FR-03 | PdM measurement and investigation workspace | UI-04 | UX-06; PR #63 R01–R08/Q01–Q10 gates |
| FR-04 | Attributed cases, inspections, evidence, independent review, revision/audit history | UI-05 | Phase 2; trusted identity, application persistence, engineer UAT |
| FR-05 | Reviewed local recommendations and follow-up | UI-06/07 | UX-07; existing WO references only |
| FR-06 | Governed reports with explicit scope and provenance | UI-08 | PLANNED; report definitions and export policy |
| FR-07 | Integration trust and technical navigation | UI-09 | UX-03; preserve factual routes and ownership |
| FR-08 | Bounded administration | UI-10 | PLANNED; approved product role mapping |
| FR-09 | Future authenticated access to application pages | UI-11 | UX-08 DESIGN ONLY; enforcement needs separate approved task |
| FR-10 | One primary HTTPS development address with accurate status | Shared shell | UX-01; PR #62 development acceptance, independent merge state |

The corresponding [page specs](docs/design/NADI-UI-SPEC.md) give testable behavior.
The [authority and decision register](docs/NADI-DOC-FOUNDATION-01.md) records
provenance and conflicts; technical ADRs/contracts retain their scoped authority.

## 4. Executive Overview — FR-01

Maintain the existing factual dashboard. Future layout includes KPI cards,
reliability overview, maintenance statistics, asset condition summaries, historical
charts and management attention indicators. Each metric needs a definition,
population, period, unit, evidence path and missing-data behavior.

Accepted Maintenance Activity is not Repeat Failure. Raw source status is neutral.
Health/risk summaries require approved engineering rules and sufficient evidence;
illustrative concept numbers cannot become values. Preserve
[factual V1 semantics](reliability-cockpit/docs/nadi-v1-release-candidate.md) and
[KPI evidence boundaries](reliability-cockpit/docs/nadi-kpi-evidence-catalog.md).

## 5. Asset Health — FR-02

The target primary asset workspace includes Asset Register, health overview, Asset
Detail, technical information, maintenance history, PdM evidence, recommendations
and existing WO references. Preserve current `/assets`, canonical detail and
`/asset-health` functionality while future navigation is reviewed.

Asset Detail follows the Product Owner's declared visual target in this order:

1. Asset Header.
2. Health Summary Cards.
3. Asset Details.
4. PdM Condition Summary.
5. WO History.
6. Recommendations / Actions.

Dependencies: governed Maximo Asset Registry and WOs, approved PI condition evidence,
manual PdM inspections, NADI Engineering records and recommendations. Equipment
identity must be exact. Broader technical equipment is not automatically registered.
UNKNOWN means unavailable/unverified; NOT ASSESSED means no supported assessment.
An empty WO history is not proof of no failures. No fabricated health score,
criticality or operating status. The PO-confirmed official reference is
[existing konsep4.png](konsep4.png), verified under FIX-02. The six-section layout
matches the reference; implemented UI fidelity remains a separate acceptance gate.

## 6. PdM Center — FR-03

Target capabilities: method navigation, measurement history/point selection, actual
measurement timestamps, trending, findings, engineering interpretation, authorized
spectrum/waveform references and IR thermograms, independent review and linked
recommendations. Candidate methods: Vibration, IR Thermography, MCSA, Tribology;
other methods require engineering validation.

Preserve the [merged NADI-PDM-REQ-01 requirements](reliability-cockpit/docs/nadi-pdm-requirements-01.md)
from PR63. Merge does not approve the candidate method fields or thresholds.
R01–R08 cover episodic events, point/instrument context, original values/units/times,
diagnostic references, separated interpretation/review, controlled Excel mapping,
existing-WO context and comparability. Q01–Q10 all remain PENDING_ENGINEER_VALIDATION:
samples, export formats, instrument metadata, point identity, severity definitions,
PD meaning, “30% acr”, inspection cadence and exact Maximo abnormality semantics.
M01–M07 remain the proposed Phase 2 measurement/investigation backlog.

Portable readings are not continuous or assumed daily. Plot actual timestamps;
missing intervals remain missing. Do not merge portable and DCS/PI series without
reviewed point, quantity, unit, bandwidth, method and operating-context comparability.
PD must not be equated with DGA. Existing enums do not approve engineering methods.
No workbook parser, source acquisition, threshold or diagnosis is approved here.

## 7. Engineering Workspace — FR-04

Existing merged foundations include Engineering Cases, inspections, bounded
evidence references, independent review, revision history, audit history and local
recommendations. Browser-memory DEMO routes differ from authenticated persisted QA.
The latter uses isolated synthetic context and existing test data.

Measurements, observations, interpretations and review decisions remain distinct.
Accepted review does not convert human judgment into source fact. Preserve exact
asset binding, immutable versions, concurrency handling and server-enforced reviewer
independence. See [ADR006](reliability-cockpit/docs/adr/006-engineering-workspace.md),
[inspection workflow](reliability-cockpit/docs/manual-inspection-workflow.md) and
[integration acceptance](reliability-cockpit/docs/nadi-e-integration-02.md).
Development acceptance has evidence; real engineer UAT and operational activation
remain unproven/gated. Do not report them as passed.

## 8. Recommendations and Action Board — FR-05

Target flow: Finding → Engineering Interpretation → Independent Review →
Recommendation → Follow-Up → Existing WO Reference → Effectiveness Review.
An existing WO reference is optional context, not a prerequisite to invent a WO.

Recommendations are NADI-owned records. Preserve reviewed case/evidence versions,
responsible person, rationale, target date, local follow-up and independent completion
verification. Effectiveness requires supported outcome evidence; local completion
does not prove operational effectiveness. Maximo WOs remain read-only references;
no create, approve, assign, update, close or cancel action is allowed.
See [recommendation lifecycle](reliability-cockpit/docs/recommendation-workflow.md).

## 9. Reports, integration and administration — FR-06–08

Reports require approved definitions, filters, provenance, as-of time and export
privacy policy. System Integration consolidates existing Data Trust and technical
surfaces without changing their domains or starting source requests. Administration
must expose only authorized application capabilities; a system administrator does
not gain Mart/source write authority or an independent-review override.
These complete product screens are planned, not established by existing APIs/CLIs.

## 10. Login and authentication — FR-09

Eventually application pages should require authenticated access. **Design the
global login page first; do not activate global enforcement in this phase.** Keep
factual development screens easy to access. Existing `/login` is a development QA
entry, not an implemented global access policy.

Preserve HTTPS, Secure/HttpOnly/SameSite cookies, trusted Origin, CSRF protection,
server-derived roles/scopes, revocation and session expiry. No client-side role
selector establishes authority. Existing isolated Engineering gates remain intact.
Activation requires a separately approved task covering routing, account onboarding,
recovery, session policy, provisioning and regression. Local username/password is the
current initial-QA path; enterprise SSO is a future option, not an invented blocker.

## 11. Nonfunctional requirements

| ID | Requirement | Acceptance gate |
|---|---|---|
| NFR-01 | Clear provenance and unknown states | Every operational value is evidence-backed; DEMO is explicit |
| NFR-02 | Accessible, responsive interactions | Keyboard/focus, labels, non-color cues, readable charts and 390/768/1440 review; contrast verified before approval |
| NFR-03 | Bounded loading and failure behavior | Preserve navigation; scoped error/retry; no fabricated success or silent fallback |
| NFR-04 | Durable Engineering history | Persist approved records/revisions/audit; prove recovery in authorized isolated tests |
| NFR-05 | Safe concurrency and authorization | Stale-version conflict, independent review, revocation and denied scope tested |
| NFR-06 | Maintainable development | Task/PR trace, exact-head CI, visible runtime SHA, separate PO acceptance |
| NFR-07 | Performance and operational observability | Bounded paging/requests and observable API states; numeric performance budget remains TBD by measurement |

## 12. Data and security governance

Contracts own identity, units, timestamps and nullability. Source acquisition belongs
to collectors; source clients/credentials must not enter NADI consumers. Mart access
is SELECT-only; human records use the existing application owner. No new operational
store is implied. Controlled test fixtures are synthetic and never source truth.

No invented scores, thresholds, risk classes or predictions. Preserve accepted scope,
raw status semantics, freshness governance, unresolved relationships and source guards.
No operational policy activation, extension, reset or rollback is authorized here.
Secrets, source payloads and personal data must not be placed in GitHub or design
references. The [root safety rules](AGENTS.md) remain binding.

## 13. Acceptance and open dependencies

Implementation acceptance requires requirement IDs → changed artifacts → scoped
tests → exact tested SHA/CI → runtime observation → separately recorded PO decision.
IMPLEMENTED, TESTED, MERGED, VISIBLE and ACCEPTED are independent, not synonyms.
Design approval cannot satisfy a runtime or engineering evidence gate.

The five [official PNG references](docs/design/references/README.md) are AVAILABLE
and their mapping is PO-confirmed under FIX-02; no ZIP/JPG or duplicate is required.
Open dependencies: token/contrast and navigation review;
PR #62/#63 are merged; remaining gates include Q01–Q10 engineer validation; approved assessment semantics;
authorized operational identity/application writer/storage/scanner provisioning;
real engineer UAT; report definitions and product role matrix; measured performance
targets; global authentication activation task. Phase 1 operator-review results are
UNKNOWN where no result is available, with the existing expiry preserved.

## Bundle A delivery checkpoint — 2026-10-10

FR-01, FR-07, FR-10 and NFR-01/02/03/06 have a frontend implementation candidate
against merged main963e7a8. [Bundle A review](reliability-cockpit/docs/nadi-ux-bundle-a.md)
records its bounded regression and runtime evidence. FR-01 preserves the same
Decision Overview contract and 7/30/90-day filters; query-as-of is explicitly distinct
from source freshness. No portfolio health/risk calculation or global authentication
activation is introduced. The sidebar exposes planned modules honestly; Engineering
placement and actual visual acceptance require Product Owner review. UX-05–09 and
PR63 engineer-validation gates retain their existing scope/status.

## Bundle B delivery checkpoint — 2026-10-10

FR-02/03/05 now have a [Bundle B frontend implementation candidate](reliability-cockpit/docs/nadi-ux-bundle-b.md) on main160737b / MERGED PR65. Asset identity and factual
APIs remain unchanged. The working PdM, Recommendation and Action Board surfaces
reuse authenticated isolated QA contracts; their data is explicitly SYNTHETIC.
Operational APIs/identity/writer activation, approved method/point/comparability,
attachment custody and engineer UAT are still dependencies. UI completion grants no
engineering approval. Commands reuse existing authorized Engineering workflows;
there is no new Maximo action, risk metric or global login enforcement.

## Engineering Advisory & Distribution — binding PO scope, 2026-10-11

NADI-ENG-BUNDLE-A adds FR-11 structured Case Management (ENG-UX-01/02), FR-12
reviewed immutable advisory publication (ADV-01), FR-13 authenticated scoped
recipient readability/acknowledgement (ADV-02), and FR-14 existing local follow-up
traceability (ADV-03). ADV-04 real distribution remains future gated work.
Operations and Maintenance are audience categories, not fabricated operational
accounts/roles. Browser inputs cannot grant roles or choose their own audience.

Acceptance: exact asset access on list/detail/history/mutation; trusted server
identity and independent version-bound review/publication; source observations,
hypotheses, conclusion, evidence limitations and recommended follow-up remain
separate. Idempotency, stale-revision recovery, immutable snapshots, withdrawal,
explicit acknowledgement audit and denied-access tests must pass. In-app availability
is not delivery; acknowledgement is not recommendation acceptance or authorization.
Local planned/completed/independently verified follow-up never proves physical work.
No Maximo mutation, real notification, source request, global login or operational DB
migration is authorized. Delivery is SYNTHETIC QA pending PO/engineer UAT and rollout.
The [official track](plans/NADI-ROADMAP.md#engineering-delivery-track--nadi-eng-bundle-a--2026-10-11)
owns statuses and dependencies.
