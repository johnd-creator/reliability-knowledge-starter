# NADI UI specification V1

Updated: 2026-10-10 · NADI-DOC-FOUNDATION-01 · design specification with Bundle A implementation checkpoint.
Requirements: [PRD](../../PRD.md). Components: [Design System](../../DESIGN-SYSTEM.md).
Delivery sequence: [official roadmap](../../plans/NADI-ROADMAP.md).

## Evidence and shared acceptance

FIX-03 source baseline: main `0cb26882c870185a54282df3af4a136f31702b67`, including merged
PR62/63. Last recorded runtime source: `0bfea1273f97ce96a08ef147b44f804aecb428d1`;
documentation merge does not change runtime visibility.
Current functionality below means bounded source/historical acceptance evidence,
not new operational UAT. [Audit](../NADI-DOC-FOUNDATION-01.md) records provenance.

FIX-02 reference reconciliation (2026-10-10): Product Owner confirmed the existing
root PNGs as official references. All five are AVAILABLE and visually verified:

| Reference | Official root PNG | Page |
|---|---|---|
| REF-EXEC | [Executive Overview — konsep5.png](../../konsep5.png) | UI-01 |
| REF-ASSET | [Asset Health Detail — konsep4.png](../../konsep4.png) | UI-03 |
| REF-PDM | [PdM Center — konsep3.png](../../konsep3.png) | UI-04 |
| REF-REC | [Recommendations — konsep2.png](../../konsep2.png) | UI-06 |
| REF-ACTION | [Action Board — konsep1.png](../../konsep1.png) | UI-07 |

The [reference manifest](references/README.md) records SHA256, dimensions, size,
provenance and visual findings. No ZIP, JPG or duplicate is required. Prior
[concept alignment](NADI-CONCEPT-ALIGNMENT.md) and
[Bundle C coverage](NADI-BUNDLE-C-CONCEPT-COVERAGE.md) remain historical analyses.
Reference selection is approved by the PO; implementation fidelity and engineering
semantics are not approved by that selection.

All pages must preserve exact identity, approved factual semantics, explicit data
scope and time basis; distinguish source facts, human records and DEMO. UNKNOWN,
NOT ASSESSED, no matching rows, denied access and unavailable backend are separate
states. No invented scores, thresholds, health/risk classes or predictions.
API success is not freshness or equipment health. No page initiates source collection
or mutates Maximo WOs. Shared responsive review: 390/768/1440px, keyboard focus,
long names, table overflow, error/loading/empty states and accessible chart summaries.
Each page acceptance below is a future check, not a PASS claim.

## Navigation map

| Current route / label | Proposed placement | Compatibility requirement |
|---|---|---|
| `/` — Overview | Executive Overview | Retain factual landing route |
| `/assets` — Asset Reliability | Asset Health → Asset Register | Retain business Registry population |
| `/assets/[...canonicalId]` | Asset Health detail drilldown | Exact canonical ID; preserve deep links |
| `/asset-health` — Asset Health | Asset Health → assessment evidence | Keep existing assessment records distinct from calculated health |
| `/maintenance`, `/maintenance/investigation`, `/work-orders` | System Integration → Maximo → Maintenance / Work Orders | Retain routes and investigation behavior |
| `/fmea`, `/rcfa`, `/overhauls` | System Integration → Maximo | Preserve each domain's unresolved semantics |
| `/data-quality` — Data Trust | System Integration → Data Trust Center | Keep existing compatibility URL |
| `/equipment/[id]` | Technical context under System Integration | Do not imply Registry membership |
| `/engineering`, case detail, `/engineering/lab`, `/engineering/workflow` | Engineering workspace linked from asset/PdM/recommendation workflows | Preserve development gates and DEMO labeling |
| `/engineering/local`, `/engineering/qa`, `/login` | Development Engineering access | Keep persisted QA distinct from browser-memory concepts |

Proposed top-level order: **Executive Overview, Asset Health, PdM Center,
Recommendations, Action Board, Reports, System Integration, Administration**.
Engineering Workspace is a core module reached through relevant workflows; its
final navigation access point needs PO review and cannot remove existing access.
Candidate technical submenus: Data Trust Center; Maximo (Maintenance, Work Orders,
FMEA, RCFA, Overhaul); PI System; CEMS. PI/CEMS submenu proposals do not prove NADI
projections exist. Asset Detail is a drilldown, not necessarily a sidebar entry.
Bundle A implements this placement using existing routes. Engineering is a supplemental authorized link pending PO review; unavailable top-level modules and PI/CEMS remain Planned. No route rewrite or global authentication activation occurs.

## UI-01 — Executive Overview

- **Purpose / users:** factual portfolio orientation for Reliability Managers and
  Engineers; direct attention to evidence needing investigation.
- **Reference design:** [REF-EXEC / konsep5.png](../../konsep5.png), AVAILABLE; portfolio
  filters, KPI cards, summary/attention panels and historical chart visually verified.
- **Layout / components:** page context and scope filters; KPI cards; reliability
  overview; maintenance statistics; evidence-backed asset summaries; historical
  activity charts; management attention links with stated rationale.
- **Navigation:** `/` remains landing; drill to filtered registered assets,
  maintenance investigation and Data Trust, retaining filter context.
- **Data dependencies:** approved Mart read DTOs, Registry membership, maintenance
  evidence and controlled-domain availability; future assessment summaries require
  approved rules and reviewed records.
- **Implemented:** factual dashboard, Maintenance Activity and bounded distributions/
  trends; existing release semantics. No accepted numerical health/risk portfolio.
- **Bundle A implemented candidate:** REF-EXEC hierarchy, six factual KPI cards, three summary panels and a full-width weekly activity chart; all existing record, distribution and integrity evidence remains accessible.
- **Planned:** PO visual acceptance and approved assessment aggregation when eligible.
- **Unknown data behavior:** show unavailable/unknown scope and dates explicitly;
  missing condition evidence cannot count as healthy, zero failures or zero risk.
- **Security constraints:** stored-data reads only; no PII/source credentials; preserve
  easy factual development access while global login remains design-only.
- **Responsive requirements:** cards stack in reading order; charts retain labels and
  text summary; attention table scrolls within its own region.
- **Acceptance criteria:** approved factual values/populations match API evidence;
  filters/drilldowns work; no gated KPIs leak; all shared states pass; PO compares
  layout with actual REF-EXEC before visual acceptance.

## UI-02 — Asset Health / Asset Register

- **Purpose / users:** find a registered asset and inspect evidence coverage;
  Reliability, PdM and Maintenance Engineers and Managers.
- **Reference design:** Design System; REF-ASSET informs detail context, not an
  invented list screenshot.
- **Layout / components:** title/scope; search and approved filters; register table;
  identity, technical description, assessment availability and evidence timestamps.
- **Navigation:** preserve `/assets` and `/asset-health`; select exact asset to UI-03.
  Future unification must retain both factual populations and their labels.
- **Data dependencies:** governed Registry, canonical asset DTOs and assessment records;
  verified relationships only. Broader technical equipment is separate context.
- **Implemented:** registered asset list/detail and factual assessment-record list.
- **Planned:** UX-05 integrated health workspace, approved condition summaries and filters.
- **Unknown data behavior:** unknown classification/assessment is explicit; no assessment
  is NOT ASSESSED. Zero returned rows explains filters versus backend unavailability.
- **Security constraints:** no registry auto-enrollment, fuzzy identity join or source
  write; future scopes enforced server-side, not through hidden table rows alone.
- **Responsive requirements:** priority identity columns remain readable; filters wrap;
  optional columns use accessible detail disclosure or scoped scrolling.
- **Acceptance criteria:** list retains registered scope and pagination; detail opens
  correct canonical identity; no fabricated scores/status; missing/denied/error cases
  remain distinguishable and direct existing URLs continue to work.

## UI-03 — Asset Health Detail

- **Purpose / users:** one asset's factual and human evidence for Reliability,
  Maintenance and PdM Engineers and independent Reviewers.
- **Reference design:** [REF-ASSET / konsep4.png](../../konsep4.png) is the PO-confirmed
  official target, AVAILABLE; all six layout sections visually verified. Comparison
  of an implemented UI against this reference remains pending.
- **Layout sections:** (1) Asset Header with equipment identity/operating status;
  (2) Health Summary Cards with health/criticality and failure/WO indicators only
  when supported; (3) Asset Details technical information; (4) PdM Condition Summary
  by method; (5) WO History and historical chart; (6) Recommendations / Actions.
- **Key components:** asset breadcrumb, evidence/time labels, technical key-value
  table, method cards, chronology/chart, reviewed recommendation links.
- **Navigation:** preserve canonical detail URL and back-to-list filters; linked
  measurement, case and WO references retain the same asset binding.
- **Data dependencies:** Registry, exact Maximo asset/WO relationships, governed PI
  evidence, manual inspection records, NADI cases/recommendations; approved health
  and criticality rules separately required.
- **Implemented:** canonical asset context and factual evidence; synthetic Asset 360
  concept in Engineering workflows. The full target layout is not accepted operational UI.
- **Planned:** UX-05 layout may be implemented with explicit empty states before all
  source mappings finish; later bind independently approved data paths.
- **Unknown data behavior:** NOT ASSESSED for unsupported scores; UNKNOWN for unavailable
  operating status/criticality/failure identity; WO activity is not failure count.
  Fake illustrative content must be marked DEMO at page and value context.
- **Security constraints:** exact scoped identity; human edits only through authorized
  NADI workflows; never WO mutation or arbitrary external attachment URLs.
- **Responsive requirements:** preserve six-section reading order; cards stack, long
  identity wraps, chart has text alternative and WO table has local overflow.
- **Acceptance criteria:** all six sections recognizable against actual reference;
  each real value traces to governed evidence; no synthetic operational metric;
  cross-asset links denied, missing mappings remain visible; existing detail retained.

## UI-04 — PdM Center

- **Purpose / users:** inspect measurement events, investigate findings and document
  interpretations; PdM Engineers, Reliability Engineers and Reviewers.
- **Reference design:** [REF-PDM / konsep3.png](../../konsep3.png), AVAILABLE; method tabs,
  distribution/trend panels and findings table visually verified. Illustrated
  severity/standard labels do not approve operational thresholds or methods.
- **Layout / components:** method navigation; asset/point selectors; original value,
  unit and actual measured time; irregular-time history/trend; findings register;
  spectrum/waveform/thermogram reference viewer; interpretation/review context.
- **Navigation:** asset → method/point → measurement → evidence → case → recommendation;
  preserve selected point, method and time range when returning.
- **Data dependencies:** PR #63 R01–R08, Q01–Q10, approved point/instrument/method
  definitions, authorized attachment custody and actual measurement records.
- **Implemented:** development method/input concepts, generic manual inspection envelope
  and isolated QA review workflow. Method-specific operational trends/forms are pending.
- **Planned:** UX-06 and M01–M07 measurement/investigation capabilities after gates;
  Vibration, IR Thermography, MCSA and Tribology are candidates.
- **Unknown data behavior:** missing intervals stay empty; unknown unit/time/point blocks
  unsupported combination. No daily/continuous assumption; PD≠DGA unless validated.
- **Security constraints:** separate observations from interpretation; independent review;
  authorized version-bound attachments; no direct PI access, automatic source retry,
  parser or portable/DCS trend joining without reviewed comparability.
- **Responsive requirements:** method navigation wraps/scrolls accessibly; chart and
  evidence metadata retain units/time; diagnostic images have labeled zoom controls.
- **Acceptance criteria:** actual timestamps preserved; incompatible series kept apart;
  findings/review/provenance distinct; pending engineer fields stay pending; evidence
  access and reviewer denial tested; real engineer UAT separately recorded.

## UI-05 — Engineering Workspace

- **Purpose / users:** attributable investigation, independent review and durable
  decisions; Reliability/PdM/Maintenance Engineers and Engineering Reviewers.
- **Reference design:** existing case UI and reviewed technical workflows; no new
  dedicated screenshot supplied. Reuse Design System after approval.
- **Layout / components:** case list/filters; asset context; observations/hypotheses;
  inspection/evidence references; revision history; reviewer decision; audit history.
- **Navigation:** case list → case detail; asset/PdM context → case; accepted evidence
  → recommendation. Retain all existing development routes and back context.
- **Data dependencies:** application store, trusted identity/scopes, versioned case
  and inspection contracts, canonical read-only references and immutable audit.
- **Implemented:** merged domain/persistence/review foundation; browser-memory DEMO
  plus separate authenticated persisted development QA at `/engineering/local`.
- **Planned:** operational forms, reviewed deployment and engineer UAT; QA JSON-command
  interface is not final engineer-facing UX.
- **Unknown data behavior:** unresolved evidence remains unknown; missing assessment
  cannot be replaced by a hypothesis. Deleted/unavailable references remain explained.
- **Security constraints:** server-derived principal; independent reviewer exclusions;
  CSRF, revocation, expected revision and idempotency; no audit edit/delete shortcut.
- **Responsive requirements:** editor/read-only evidence stack; history remains accessible;
  unsaved changes and conflict feedback survive layout changes within authorized session.
- **Acceptance criteria:** create/revise/submit/review in isolated authorized QA persists
  across reload; self-review/stale revision denied; audit intact; DEMO unmistakable;
  operational activation and actual UAT require separate evidence.

## UI-06 — Recommendations

- **Purpose / users:** translate independently reviewed interpretation into an
  accountable NADI proposal; Engineers, Reviewers and Reliability Managers.
- **Reference design:** [REF-REC / konsep2.png](../../konsep2.png), AVAILABLE; status filters,
  KPI cards and recommendation register visually verified; Design System applies.
- **Layout / components:** search/status filters; local recommendation register;
  reviewed finding/case reference; rationale, responsibility/target date; review and
  follow-up history; optional existing WO reference and effectiveness evidence.
- **Navigation:** reviewed case → recommendation → Action Board; open referenced asset,
  evidence revision and existing WO read context without mutating them.
- **Data dependencies:** NADI recommendation lifecycle, reviewed case/evidence versions,
  trusted directory and exact authorized WO reference.
- **Implemented:** local lifecycle/review/follow-up foundation, synthetic concept UI
  and persisted isolated QA commands; no complete operational recommendation page.
- **Planned:** UX-07 product form/register, operational integration and effectiveness view.
- **Unknown data behavior:** no WO link is “not linked”; unknown outcome is not effective;
  human priority is not calculated risk or source maintenance authorization.
- **Security constraints:** server-scoped responsibility and independent review; NADI
  approval never creates/approves/updates/closes Maximo WOs.
- **Responsive requirements:** register scrolls locally; detail/edit sections stack;
  evidence links and validation errors remain keyboard reachable.
- **Acceptance criteria:** only eligible reviewed versions enter workflow; local status
  and WO status distinguished; unauthorized/self-review/conflict rejected; outcome
  claims require evidence; persisted history survives authorized reload.

## UI-07 — Action Board

- **Purpose / users:** see pending local review and follow-up; Engineers, Reviewers,
  Maintenance Engineers and Reliability Managers.
- **Reference design:** [REF-ACTION / konsep1.png](../../konsep1.png), AVAILABLE; attention
  cards and two detailed tables visually verified. Illustrated risk formula and
  decision categories remain unapproved engineering/product semantics.
- **Layout / components:** scoped attention counts; review queue; responsible person,
  target date and local follow-up table; completion verification and outcome evidence.
- **Navigation:** board items open exact local case/recommendation; back retains filters;
  informational existing-WO links remain read-only.
- **Data dependencies:** NADI recommendation/follow-up records, approved status/date
  semantics, scoped directory and independently verified completion evidence.
- **Implemented:** synthetic workflow board and local follow-up foundation; not an
  operational risk-ranked maintenance execution board.
- **Planned:** UX-07 integrated product board and approved effectiveness tracking.
- **Unknown data behavior:** missing date/owner/outcome explicit; overdue describes a
  local target date, never automatically failure risk or source WO delay.
- **Security constraints:** scoped queues, no admin review override, no assignment or
  scheduling command sent to Maximo; operational authority remains external.
- **Responsive requirements:** compact queue cards or table scrolling retain record,
  owner, date and status labels; actions remain accessible on narrow screens.
- **Acceptance criteria:** counts reconcile with authorized local records/filters;
  independent verification preserved; no unsupported priority/risk ordering or fake
  operational action; board-to-record links retain exact versions/context.

## UI-08 — Reports

- **Purpose / users:** communicate bounded factual/engineering results to Managers,
  Engineers and authorized Reviewers.
- **Reference design:** Design System proposal; no supplied report screenshot.
- **Layout / components:** report catalog, approved scope/period filters, preview,
  provenance/as-of summary, limitations and authorized export controls.
- **Navigation:** reports preserve source page context; report rows link to evidence
  only within user authority. Route allocation is a later implementation decision.
- **Data dependencies:** approved report definitions, governed DTOs, reviewed records,
  export/privacy policy and reproducible selection/time basis.
- **Implemented:** existing source/API evidence is reusable; this audit does not
  establish a complete Reports product page or scheduled delivery.
- **Planned:** FR-06 report templates, preview/export and permission design.
- **Unknown data behavior:** incomplete coverage and unknown metrics remain explicit in
  both screen and export; empty export must not imply normal plant condition.
- **Security constraints:** no raw vendor payload, credential or PII disclosure; no
  report-triggered source collection; export permissions and retention need review.
- **Responsive requirements:** preview fits readable width; wide tables have local
  scrolling; accessible summary remains available independent of export format.
- **Acceptance criteria:** approved definition/period/population reproducible; missing
  data disclosed; denied export tested; provenance survives export; PO approves template.

## UI-09 — System Integration

- **Purpose / users:** understand coverage, availability and trust; Engineers,
  Reliability Managers and System Administrators.
- **Reference design:** existing Data Trust semantics and proposed navigation map.
- **Layout / components:** component availability; source/collection/projection clocks;
  coverage/identity and policy states; Data Trust and Maximo/PI/CEMS technical links.
- **Navigation:** consolidate technical access while retaining `/data-quality` and all
  domain routes; navigation relocation does not transfer domain/data ownership.
- **Data dependencies:** existing local integration-status DTOs, governed mapping,
  collector observations, projector clocks and separately approved freshness policy.
- **Implemented:** factual Data Trust and integration evidence; bounded governed PI
  pilot recorded. Complete PI/CEMS product integration is not established.
- **Planned:** UX-03 hierarchy, consolidated integration page and approved future panels.
- **Unknown data behavior:** availability, age, quality and condition separate;
  missing policy remains UNKNOWN; no reset of clocks or recency-as-freshness shortcut.
- **Security constraints:** local stored-data reads only; no start-worker, retry-source,
  credential editor or automatic policy extension implied by status controls.
- **Responsive requirements:** status cards stack and long timestamps/identifiers wrap;
  gate details remain readable and labeled without relying on traffic lights.
- **Acceptance criteria:** scopes/clocks match approved DTO semantics; unknown/degraded
  states visible; factual URLs preserved; operator-review/expiry state not fabricated.

## UI-10 — Administration

- **Purpose / users:** bounded application administration for authorized administrators;
  auditor access only if explicitly designed and granted.
- **Reference design:** Design System proposal; no supplied administration screenshot.
- **Layout / components:** proposed account/scope overview, authorized grant controls,
  session/security history and configuration references; actions require explicit scope.
- **Navigation:** future Administration entry; no public route or mutation endpoint
  introduced by this specification. Preserve private operator boundary meanwhile.
- **Data dependencies:** trusted account directory, approved product role mapping,
  immutable security events, custody and recovery procedures.
- **Implemented:** bounded private operator CLI/local authentication foundation;
  this is not evidence of a finished administration web UI.
- **Planned:** FR-08 permission-reviewed product UI after operational readiness gates.
- **Unknown data behavior:** unavailable audit data is not “no events”; absent role
  mapping disables unsupported controls and explains the unresolved dependency.
- **Security constraints:** no public fixture bootstrap, password/hash exposure, client
  authority or Mart/source privileges; grant changes revoke sessions as contracted;
  ADMIN does not override independent review.
- **Responsive requirements:** account lists scroll locally; critical permissions and
  confirmation context remain readable; keyboard focus returns after dialogs.
- **Acceptance criteria:** approved role/scope matrix tested positively and negatively;
  audit and last-admin safeguards retained; no sensitive material in UI/log/export;
  activation separately approved before operational account management.

## UI-11 — Login Page (global design only)

- **Purpose / users:** future secure application entry for all authorized personas;
  current QA login continues to serve isolated Engineering development only.
- **Reference design:** Design System proposal; no supplied login screenshot.
- **Layout / components:** NADI identity, environment label, username/password inputs,
  optional password visibility control, submit/progress, generic error, expiry message
  and documented operator-help path; no invented self-service recovery.
- **Navigation:** future safe same-origin return destination after authentication;
  exact behavior awaits approved enforcement task. Preserve current QA `/login` flow
  and factual development pages; no global redirects or middleware introduced now.
- **Data dependencies:** existing local auth/session contract; approved onboarding,
  recovery, session/password policy and operational hosting/TLS before activation.
- **Implemented:** development-only `/login` and authenticated `/engineering/local`,
  merged foundation plus PR #62 live launcher. Global authentication is not activated.
- **Planned:** UX-08 visual design only; subsequent global enforcement is a separate task.
- **Unknown data behavior:** generic invalid credentials; distinguish service unavailable
  without disclosing account existence; no fake signed-in state or fallback identity.
- **Security constraints:** preserve HTTPS and Secure/HttpOnly/SameSite cookies,
  strict Origin/CSRF, server roles/scopes, rate limits, revocation and expiry; never
  weaken current QA gates to make a mockup work. No password/session browser storage.
- **Responsive requirements:** single readable form, mobile keyboard-friendly fields,
  visible labels/focus/error summary, no decorative obstruction or color-only error.
- **Acceptance criteria:** design reviewed with error/loading/expiry states; mockups
  clearly nonfunctional; existing QA login/security and factual access unchanged;
  no global enforcement claimed until separate approved implementation and UAT.

## Bundle A review evidence

UX-02/03/04 are implementation candidates, independent of merge and PO acceptance.
[Review and responsive screenshots](../../reliability-cockpit/docs/nadi-ux-bundle-a.md)
compare the actual UI with REF-EXEC. Screenshots use explicitly labeled synthetic
browser fixtures; the application keeps its factual API path. Missing health scores
are NOT ASSESSED, attention reflects exact unresolved relationships, and the chart
shows existing weekly event counts with an accessible full-period table. No search,
unit selector, alert feed or healthy/warning/critical distribution is fabricated.
UI-02–11 functional scope is unchanged except shared shell/primitives and legacy
semantic/scroll fixes. The original five reference PNGs retain their SHA256/provenance.

## Bundle B implementation checkpoint — 2026-10-10

Baseline main160737b includes MERGED PR65. [Bundle B review and responsive evidence](../../reliability-cockpit/docs/nadi-ux-bundle-b.md) implements UI-02/03/04/06/07 using
REF-ASSET, REF-PDM, REF-REC and REF-ACTION. `/assets`, canonical detail and
`/asset-health` remain factual. `/pdm`, `/recommendations`, `/action-board` are
working product layouts with server-gated authenticated QA reads only in development.
Outside that gate they disclose unavailable operational integration and request no QA
records. Candidate method controls are not operational-method approval.

Asset detail follows six sections; legacy tabs and governed PI Condition Evidence
remain. PdM exposes original episodic sample/unit/time/point, observations,
interpretations, review and metadata-only references; comparability/trends and
attachment custody remain gated. Recommendations expose exact local state, case,
provenance/history and responsibility; Action Board counts only filtered authorized
page records. Existing controlled commands remain in the original Engineering
workspace with server revision/independence/CSRF checks. No new product-page write
control, Maximo mutation, risk ranking or global authentication policy is introduced.

Known reference deviations are deliberate: no illustrative health scores, risk
colors/formula, diagnosis thresholds, interpolated trend or execution/budget
categories. Operational readiness, Q01–Q10 validation, PO visual approval and UX-09
acceptance remain separate pending gates. Original PNG assets/hashes are unchanged.

## Engineering product flow — ENG-UX-01/02 and ADV-01/02/03

Extend UI-05 with a permitted-asset case register, server pagination and structured
create/edit/detail forms. Present problem, observations versus hypotheses, evidence,
workflow, revisions and independent reviewer actions; retain `/engineering/local`
for diagnostics. Errors preserve local unsaved input and explain revision conflicts.
Extend UI-06/07 with advisory draft/review/publication, readable scoped recipient
inbox/detail and explicit authenticated acknowledgement where durable identity is
proven. Reuse the existing Action Board and NADI-owned recommendation lifecycle.
Every screen carries SYNTHETIC QA scope, unknown/empty/error states, exact identities,
V1 components, keyboard labels/focus, and 1440/768/390px responsive acceptance.
Publication must bind an eligible reviewed immutable source version on the same
asset. A read is not VIEWED/delivered without an explicit attributable event;
acknowledgement is not plant-work approval. Real channels, operational accounts and
activation remain gated. This specification records requirements, not completed UAT.
