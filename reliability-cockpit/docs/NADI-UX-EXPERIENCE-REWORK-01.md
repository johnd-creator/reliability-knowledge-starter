# NADI-UX-EXPERIENCE-REWORK-01

Product Owner visual acceptance: **PENDING**. Current live preview: **UNCHANGED**.
Base: `260c4f9f5f9a17aea3b36476ca4a0e202069e19d` (PR #102).
Branch: `codex/nadi-ux-experience-rework-01`. This is the next design proposal, not approval or deployment.

## Design critique and chosen direction

Before implementation, reviewed the actual V2 ExecutiveOverview, PdmCenter,
PdmMeasurementForm and CaseWorkspace source, the private live 1440px PdM and Case
detail captures from activation, and all five official `konsep1.png`–`konsep5.png`
references. Those references inform restrained navy/teal hierarchy, clear workspace
controls and contextual detail; their illustrative health/risk scores and thresholds
are not authorized data or proposed calculations.

The critique distinguishes product friction from necessary safety boundaries:

1. **Records begin too far down the page.** Four large PdM status cards, workspace
   navigation, seven repeated method buttons, search, advanced filters and repeated
   instructions compete before an engineer can see an inspection. Status limitations
   are necessary; presenting them as equally prominent KPI cards is not.
2. **Selection loses the working context.** Case details sit below the whole register,
   with no concise record navigator. Inspecting another case requires returning up the
   page. The same vertical-stack problem affects PdM detail.
3. **The measurement editor reads as administration.** A numbered step strip promises
   stages but the form is continuous; asset context, acquisition and grid occupy
   separate full-width blocks. Repeated instruction blocks push the actual readings
   down. Original units, null/zero and timestamp semantics must remain explicit.
4. **The dashboard gives everything equal weight.** Six similar KPI cards precede
   several identical evidence panels; the maintenance chart is separated from the
   counts it explains. Counts, source scope and unsupported health assessment need
   different visual treatment, not invented scores or priority rankings.
5. **Case meaning and actions lack a hierarchy.** Human notes, hypotheses, source
   snapshots, review decisions and revision controls flow through one long card.
   Provenance cannot be removed; it needs a distinct reading structure and actions
   need to accompany the review context.

Chosen direction: **an analytical overview and an engineer's continuous workbench**.
No new UI framework, chart dependency, engineering standard or backend capability.
This is implemented in the real React pages, not a mockup overlay.

## Anchor implementation

- Executive: one portfolio identity metric anchors four comparative activity counts.
  The weekly activity plot and management relationship attention now share the first
  analytical row. Secondary controlled evidence, concentration and distributions
  follow. The fixed BSR/IP scope is presented as context, not a pretend scope selector;
  the existing 7/30/90-day selector retains its actual query contract. The weekly series
  still represents the last 12 weeks, independently labeled. Health record counts
  remain in controlled record availability, not a new health conclusion.
- PdM: compact scope facts replace decorative status cards; one navigation bar leads
  to register, history or Engineering. Integrated search/asset/status filters retain
  explicit server apply/reset, optional method/date fields and date-basis disclosure.
  Opening an inspection replaces the full table with a record navigator and detail
  pane. Register navigation returns to the list; unsaved inspection input requires
  explicit discard before switching the selected record.
- Editor: continuous context/acquisition workbench above an ergonomic measurement
  grid; direct section links, add/remove controls, original value/unit/time fields,
  visible unsaved state and local-draft limits. No wizard, automatic conversion,
  local-storage persistence, template auto-approval or silent data substitution.
- Cases: search and server filters share one toolbar, with explicit distinction
  between page-local search and population filtering. Selection opens a record
  navigator and focused detail pane. Separate sections identify human statements,
  hypothesis, exact evidence provenance and independent review. Review commands
  accompany decision context. In-page jumps keep edit forms mounted and preserve
  their original CAS revision. No conclusion field exists in this DTO: an explicit
  note prevents equating hypotheses or approval with a verified engineering conclusion.
- Narrow layouts: labeled record rows replace horizontally clipped registers;
  detail columns stack and record navigation remains collapsible. The editor uses
  paired input fields on mobile and keyboard-reveal scrolling on intermediate widths.

## Reusable patterns and scope

`ExperienceWorkspace.tsx`: WorkspaceToolbar, CompactFacts, RecordNavigator,
DetailSection and SectionJump. `experience.css` scopes the visual direction to these
anchor experiences. The approved logo/login, shell authentication, session, transport,
CSRF/Origin policy, roles, asset scopes, backend state machines and DTOs remain intact.
Case and inspection mutations still use existing commands, revision checks and
identity-bound in-memory draft providers. The original measurement validation and
workbook candidate modules are unchanged.

After PO selection, proposed second rollout: Asset list/detail and condition evidence;
Recommendations and Action Board; Reports and Data Trust; then Integration and the
remaining factual/Engineering screens. Do not apply this proposal to those pages
before the anchor design is accepted.

## Evidence and verification

[40 matching before/after pairs, hashes and reproduction instructions](evidence/nadi-ux-experience-rework-01/README.md).
[Interactive comparison](evidence/nadi-ux-experience-rework-01/compare.html).
[Machine-readable results](evidence/nadi-ux-experience-rework-01/verification.json).

| Verification | Result |
|---|---|
| Fifteen frontend design/contract/auth/workflow check groups | PASS |
| TypeScript, ESLint, production build | PASS; one pre-existing EngineeringWorkspace effect-dependency warning |
| New anchor browser suite | 107 checks; 40 WCAG A/AA scans; zero detected violations/exceptions |
| Existing PdM browser regression | 575 checks PASS |
| Existing localization / cross-page browser | 399 checks PASS |
| Existing Reports / Integration / login browser | 96 / 67 / 56 checks PASS |
| All browser assertions / axe scans | 1,300 assertions; 74 scans; zero detected violations |
| Focused local backend / Engineering / input tests | 195 run; 117 pass, 78 skipped without disposable PostgreSQL |
| Diff integrity and protected source boundaries | PASS |

Focused new interactions cover period queries, activity expansion, server filtering and
reset, page-local Case search, selected-record deep links and focus, navigation collapse,
section jumps without unmounting, cancelled draft discard, original zero/UNKNOWN values,
revision history and a stale form retaining r3 when the latest record becomes r4.
The existing suites also cover CSRF, identity, independent review, idempotent retry,
workbook candidates, measurement validation and backend-unavailable states.

After inspecting the first actual renders, refined mobile/tablet registers into labeled
rows, changed Case evidence from an inner scrolling table to readable provenance
references, corrected definition-list semantics and muted-surface contrast, removed
background fades through unreadable intermediate colors, and corrected Register navigation.
These are test-driven refinements, not Product Owner acceptance. The screenshots show a
proposal; premium quality remains a product judgment.

All public screenshots use network-intercepted synthetic fixtures; no live plant data
or protected account state. Full live backend UAT was intentionally not performed because
this iteration must not mutate or restart the current preview. The backend/auth contract
suites and exact-head CI provide regression evidence; they do not certify live activation.
Private source/controller/process/container fingerprints are outside Git. Read-only
before/after comparisons passed for both service process identities (frontend PID
1879726; backend PID 1879724), all 35 container identities, 75 protected controller /
configuration files, 1,365 eligible active V2 source files and 1,213 original Mode A
source files. No controller command, DB command, collector action or service restart
was performed. PR #102 / #103 remain open Drafts at their original SHAs.

Graph discovery used Tier 2, generation 2026-08-24T09:24:57Z. Newer anchor and test files
were missing from the graph; after coverage checks the exact source was read directly.
No exhaustive graph-coverage claim is made.

## Final review record

| Field | Result |
|---|---|
| TASK | NADI-UX-EXPERIENCE-REWORK-01 |
| STATUS | PASS (implementation and bounded verification; PO acceptance pending) |
| BASE_V2_SHA | 260c4f9f5f9a17aea3b36476ca4a0e202069e19d |
| BRANCH | codex/nadi-ux-experience-rework-01 |
| FINAL_HEAD | this delivery commit; exact SHA is recorded on the Draft PR and final handoff |
| DRAFT_PR / EXACT_HEAD_CI | recorded on the final handoff and PR checks after publication |
| EXECUTIVE_OVERVIEW / PDM_CENTER / MEASUREMENT_EDITOR / ENGINEERING_CASES | PASS |
| SHARED_DESIGN_SYSTEM / RESPONSIVE_AND_DARK_MODE / ACCESSIBILITY | PASS within tested anchor scope |
| FUNCTIONAL_REGRESSIONS | PASS |
| LOGIN_AUTH_AND_BACKEND | UNCHANGED |
| BEFORE_AFTER_EVIDENCE | evidence/nadi-ux-experience-rework-01/README.md |
| TOP_5_UX_IMPROVEMENTS | compact inspection discovery; contextual record navigation; continuous measurement workbench; analytical KPI/chart hierarchy; distinct investigation/evidence/review sections |
| CURRENT_LIVE_PREVIEW | UNCHANGED |
| DATA_AND_SERVICES | PRESERVED |
| PRODUCT_OWNER_VISUAL_ACCEPTANCE | PENDING |

Next: **Senior Design Review → Product Owner Visual Selection → Extend Approved Design to Remaining NADI Pages**.
