# NADI UX Bundle B — implementation and self-review

2026-10-10 · B0 / UX-05 / UX-06 / UX-07 / B4.
Implementation, development acceptance, engineering validation, merge and PO acceptance are independent.

## B0 — baseline synchronization

Verified origin/main: `160737b3bfaeac94f4e8093b8566ca0e5d3585c9`; PR65 MERGED.
Previous serving SHA: `23b6a413f6d4f9e91afbcc631d4ab7d3d10d1858`.
Main has the same tree as that delivery; merge metadata is the only change.
The root checkout and all unrelated worktrees were preserved. Original `23496711.xls`
SHA256 remains `aa0bd8fd22275aea3ecf8654ee37878106123b7dbdf58135fb783e853ee66a5f`.

Supported launcher backup → stop → switch origin/main → start selected clean main
on https://localhost:3000. The only regenerated Next cache-path reference was
inspected and restored individually. Backend/source/launch SHA agree, both backends
AVAILABLE, fixture identity unchanged. Operational container IDs/start times compare
identical before/after. Previous source, worktrees and private fixture backup remain
rollback resources; no operational service restart or database modification.

Implementation branch: `codex/nadi-ux-bundle-b`, isolated worktree from verified main.
Five official original PNG hashes match the [reference manifest](../../docs/design/references/README.md).
The four Bundle B references were visually inspected; their metrics/colors are design
input only. The stale original-root graph was used for positive discovery, then
exact candidate source was read for missing/current contracts.

## Contract boundary

Canonical registered assets and controlled assessment/maintenance records remain
factual Mart reads. Inspection, case, recommendation and history HTTP APIs currently
exist only in the explicitly gated development QA factory. Product pages must label
authenticated records SYNTHETIC and must not merge them with operational asset facts.
No operational PdM writer, attachment download/upload, comparability approval or
health/severity rules are established. PR63 Q01–Q10 remain pending.

## Implementation checkpoint

Functional source: `0df4b47b951013aa03ae1bb97fad7e4167bb474e`.
Final documentation/test-harness HEAD, PR URL, exact-head CI and serving SHA are
verified independently in the PR checks and final delivery handoff; this checkpoint
records observed local evidence without inferring CI or merge success.

| Milestone | Local implementation / development validation | Separate gate |
|---|---|---|
| B0 | PASS — verified clean main, supported backup/source selection, existing backends | Production deployment not requested |
| B1 / UX-05 | PASS — register filters/page search, pagination, six detail sections, original evidence tabs | Health rules, source mapping and PO visual acceptance |
| B2 / UX-06 | PASS — authenticated synthetic QA method/asset/point register, exact detail/history | Q01–Q10, operational measurement contract and comparability |
| B3 / UX-07 | PASS — authorized register/detail/history and local review/follow-up board | Operational identities/UAT and PO acceptance |
| B4 | PASS — distinct review, corrections and local regression/visual checks | Exact release CI and senior/PO decision remain independent |

Asset Header, Health Summary, Technical Details, PdM Condition Summary, Maintenance /
WO History and Recommendations / Actions use the factual asset DTO. Health score
remains NOT ASSESSED, criticality/failure identity UNKNOWN when unsupported. The
secondary context may fail while canonical identity remains usable. Existing FMEA,
timeline, maintenance, assessment, overhaul and condition-evidence deep links remain.
Current-page search never claims a full-population result; server filters/pagination
retain their existing semantics and registered assets stay distinct from equipment.

New `/pdm`, `/recommendations` and `/action-board` use the existing server-side
NODE_ENV/development flag and trusted QA session. Production shows unavailable
states. Shared `useQaRecords`, `QaProductBoundary`, `QaRecordReader`, inspection and
recommendation detail components reuse V1 cards, tables, states and buttons. The
recommendation workspace serves both register and board. No dependency was added.
The existing `/engineering/local` console gains only allowlisted exact-record read
context; commands remain behind its original identity, CSRF, RBAC, revision and
independent-review boundaries. No write action was added to public product routes.

## Distinct self-review and corrections

| Finding / severity | Root cause / correction | Retest |
|---|---|---|
| Missing exact record reload loop / medium | A 404 detail response invalidated its parent repeatedly; only expired-session 401 invalidates parent, missing record is terminal with explicit retry | Browser NOT-FOUND test PASS |
| Stale immutable history / medium | Older async history could settle after record context changed; generation guard rejects old results and resets history | TypeScript/lint and detail/history regression PASS |
| Asset condition projection composition / medium | Presentation refactor moved the direct condition panel expected by canonical projection acceptance | Direct existing panel restored; all707 backend tests rerun PASS |
| Filter/technical-field visual regression / medium | Native selects lacked V1 dimensions and technical fields inherited truncation | Scoped44px select styling and wrapping key/value layout; 1440/768/390 screenshot and assertions PASS |
| Undefined spacing token / low | New grid referenced a nonexistent token | Existing V1 spacing token reused; build/responsive checks PASS |
| Immediate keyboard-scroll assertion / test issue | Assertion raced native scrolling animation | Wait for real scrollLeft before assertion; 129 browser checks PASS |

Architecture review found shared primitives/record reader reused, no alternate
frontend/design system, no new dependency or unsupported DTO. Data review checked
original zero values, units/point/sample time, exact canonical IDs, bounded counts,
empty versus unknown and completion versus verified effectiveness. Security review
checked production gating, server session/scope authority, loss of data on401/403/503,
plain attachment metadata (no arbitrary URL/download/upload), escaped text, exact
revision/evidence references and preserved commands. This is a task-scoped review,
not a claim of exhaustive repository security coverage.

The graph is stale relative to this candidate and most new paths are missing from
its index; candidate source and relevant tests were inspected directly after
coverage checks. No remaining critical/high implementation finding is known within
this bounded review. Operational dependencies below remain explicit.

## Validation evidence

- TypeScript and scoped ESLint PASS; production Next.js build PASS.
- 143 existing frontend assertions plus43 UX component/helper assertions PASS.
- Product-safety checks PASS across45 UI source files.
- Backend unittest discovery:707 tests,484 PASS,223 optional PostgreSQL SKIP locally;
  no persistent database is targeted. CI separately runs its isolated PostgreSQL suite.
- Canonical contract tests:14 PASS.
- Bundle A browser suite:105 PASS on the candidate, preserving factual dashboard,
  technical routes, navigation, mobile drawer, focus, contrast and original login/session.
- Bundle B browser suite:129 PASS, including actual backend/QA reads, asset tabs,
  synthetic filters/counts/history/zero/unknown/error/pagination and fifteen responsive views.
- HMR/source rollback:18 PASS; actual UI Fast Refresh keeps filter state without
  document reload, accurately reports dirty state, then restores original bytes.
- Original five PNG SHA256, workbook hash, diff whitespace and relative links checked.

The first backend run failed its source-composition regression; implementation was
corrected and the full suite rerun. The first responsive review exposed select and
field clipping; corrected screenshot pass was repeated. The immediate keyboard
assertion failed once before its wait correction. A sandbox-only compiler spawn
EPERM was rerun with authorized local test permissions. These attempts are not hidden.

## Visual comparison and accessibility

[Responsive screenshot index](../../docs/design/ux-bundle-b/README.md) links all15
sanitized1440/768/390 captures and machine-readable browser/rollback evidence.
Official targets remain [Asset Detail](../../konsep4.png), [PdM](../../konsep3.png),
[Recommendations](../../konsep2.png) and [Action Board](../../konsep1.png).
Navy shell, green active navigation, white card hierarchy, summary rows and registers
follow the references. Desktop detail uses paired evidence sections; tablet/mobile
stack cards and contain wide tables. Labeled filters have44px controls, V1 focus,
semantic headings/main, text-based status and keyboard scroll; Bundle A navigation
and contrast checks remain passing. All15 views were visually inspected.

Deliberate deviations: no invented score/criticality/failure total, no incompatible
trend/donut/WO monthly chart, no risk/urgency ranking or imported reference numbers.
Actual records and honest NOT ASSESSED/UNKNOWN/UNAVAILABLE states replace illustrative
metrics. Engineering coverage/QA boundary banners add information absent in concepts.
Mobile tables preserve columns via internal scrolling rather than hiding factual fields.

## Runtime, rollback and preservation

One managed development entry remains https://localhost:3000. Supported launcher
backup → stop → source selection → start touches only development frontend/QA API;
operational APIs, collectors and database containers retain original IDs/start times.
Both factual and Engineering backends AVAILABLE with matching clean source/backend/
launch SHA. Existing secure session survives a demonstrated rollback to main
`160737b3bfaeac94f4e8093b8566ca0e5d3585c9` and re-selection of the functional candidate.
Three prior persisted inspection/case/recommendation records compare exactly before,
on main and after candidate restoration. Session evidence/audit remain preserved.
Private backed-up fixture dumps and previous sources/worktrees remain rollback resources.
Port13035 stays retired. No operational configuration, schema, policy or data changed.
Final exact release source is selected after push/checks, with its final SHA reported
in the delivery handoff; CI alone is not runtime acceptance.

## Unresolved engineering and Product Owner gates

PR63 Q01–Q10, method definitions/units/points, instrument/regime comparability,
attachment custody/read authorization, operational application identity/writer,
asset linkage and actual engineer UAT remain pending. Generic episodic samples are
shown unchanged; no interpolation/portable-PI join or automatic diagnosis. DGA is
not treated as PD. Recommendations remain NADI-owned; WOs are unlinked or read-only
informational references. Missing owner/deadline/outcome stays explicit; local
completion does not prove operational effectiveness.

Phase1 original24h review result remains UNKNOWN;72h review is11October21:45WIB,
PO checkpoint12October20:00WIB, hard expiry13October00:00WIB. Operator review/action
belongs to separate governance; this task does not activate, extend or reset policy.
Senior/PO visual review and merge decision are next. Operational PdM acceptance is
separate and pending; UX-08/09 and global authentication enforcement remain out of scope.
