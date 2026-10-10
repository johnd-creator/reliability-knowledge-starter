# NADI UX Bundle A — implementation and autonomous review

2026-10-10 · DEV-SYNC / UX-02 / UX-03 / UX-04 / REVIEW-01.
Implementation candidate; Product Owner visual approval and merge are separate gates.

## Baseline and source selection

| Checkpoint | Exact source |
|---|---|
| Original / final verified main | `963e7a8bf0b2a7cf62b1ee8a5661c95d62df7108` |
| Previous serving source | `0bfea1273f97ce96a08ef147b44f804aecb428d1` (`codex/nadi-dev-live-01`, clean) |
| A0 synchronized main | `963e7a8bf0b2a7cf62b1ee8a5661c95d62df7108` (clean detached source) |
| Implementation branch | `codex/nadi-ux-bundle-a` |
| Functional review source | `ab089a88a2a4be6cffb58857fbf30e8b56b84d3e`; final documentation/test-harness HEAD is independently verified in PR/runtime handoff |

PR62, PR63 and PR64 are MERGED. Main changes from the previous serving source were
17 documentation files; no dependency, application or schema delta. A separate
worktree `.nadi-dev/ux-bundle-a` was created from verified main. The original root
remained on `feature/pi-governed-source-adapter`; untracked `23496711.xls`, other
branches/worktrees and existing rollback resources were preserved.

A0 used the existing pinned launcher: `backup`, `stop`, `switch`, `start`.
Private fixture backup checkpoints were created at 09:27 and 09:37 WIB before main
and candidate selection. Both existing backends and the same fixture identity
were verified after each controlled switch. The status banner reports detached
HEAD accurately, the full SHA, clean/dirty state and backend/fixture identity.
Only the explicitly inspected Next-generated cache reference was restored after
startup. No dirty file discard or manual process replacement occurred.

## Implementation and factual compatibility

| Track | Implemented behavior | Remaining gate |
|---|---|---|
| UX-02 | Shared light/dark tokens, compatible existing primitives, button/input/breadcrumb/feedback, accessible states and contained tables | PO token/visual approval; broader legacy-form accessibility work |
| UX-03 | Navy product sidebar, green active state, specific-route matching, expandable technical groups, desktop collapse, modal responsive drawer | PO Engineering navigation placement |
| UX-04 | REF-EXEC hierarchy, six factual KPIs, three summary panels, full-width weekly trend, preserved evidence/distributions/integrity | PO visual approval; governed health/risk aggregation remains unavailable |
| REVIEW-01 | Distinct source/UI/data/security/regression review with fixes and retests below | Independent reviewer/PO acceptance |

The same Next15/React19 app and API clients remain. No runtime library was added;
ESLint/TypeScript hooks/accessibility packages are development tooling only.
`ui.tsx` remains the primitive entry point; AppShell delegates to AppNavigation.
ExecutiveOverview owns presentation/request state; `overview.ts` guards factual
formatting and existing integrity attention counts; no new engineering formula.

All specified existing routes, canonical asset/equipment detail and development
login/Engineering gates are retained. Technical routes appear under System
Integration. PdM Center, Recommendations, Action Board, Reports, Administration and
PI/CEMS product projections are honestly Planned. Existing Engineering/workflow
surfaces remain available through the authorized supplemental link and development
status links; this does not implement UX-05–09 product pages.

The overview keeps the existing Decision Overview endpoint and 7/30/90-day filter.
KPI values are the existing registered-asset count, 7/30/90-day maintenance counts,
30-day active assets, plus the already available assessment-record count. The latter
is a record count, never a health score. Concentration uses exact canonical links;
five rows appear initially and the full returned list remains accessible. Weekly
bars preserve exact counts and dates, including zero/UNKNOWN; an expandable table
provides every period and evidence class without color dependence. Original status,
work-type, controlled-record and relationship panels remain available.

No fixture import enters application code. Deterministic synthetic data is used
only by isolated tests/browser response interception. Actual browser regression
compares displayed factual values with the existing API for all three windows.
Loading has no temporary KPI zero; gated metrics are NOT ASSESSED; unavailable data
is UNKNOWN/UNAVAILABLE; sanitized errors have bounded user-initiated retry.
Query-as-of is labeled separately from source freshness.

## Reference comparison and responsive evidence

Official source: [REF-EXEC / konsep5.png](../../konsep5.png). The five original PNGs
retain the hashes/provenance in the [reference manifest](../../docs/design/references/README.md).
No original was duplicated, regenerated or modified.

Reference hierarchy is retained: navy sidebar/light content; context controls;
six KPI cards; evidence/activity/attention panels; a broad historical chart.
Required deviations: no fabricated healthy/warning/critical donut, risk ranking,
health-score line, overdue alerts, fake user/notification, search or unit filter.
Those contracts do not exist. Factual evidence/relationship panels and weekly
activity replace them. The development banner stays visible. Primary action green
is #0B7437 for readable white text; the existing dark theme remains supported.

Shareable screenshots use explicitly labeled **DEMO · SYNTHETIC UI REGRESSION**
responses in a separate disposable browser context. No operational measurements,
personal names or credentials are included. Generated and visually inspected evidence:
[desktop1440](../../docs/design/ux-bundle-a/executive-1440.png),
[tablet768](../../docs/design/ux-bundle-a/executive-768.png),
[mobile390](../../docs/design/ux-bundle-a/executive-390.png).
All three have no horizontal page overflow; tables/chart scroll within their own regions. The factual runtime uses
unchanged backend reads; screenshots do not certify plant condition or engineer UAT.

## Autonomous review findings and corrections

| Finding | Severity | Correction / regression |
|---|---|---|
| Minimum table width was placed on the outer overflow wrapper | MEDIUM | Move width to inner content, keyboard-focusable scroll region; component/browser width checks |
| Two breadcrumb items declared current page | LOW | Only final unlinked item is current; rendered-markup assertion |
| Ten concentration rows stretched the summary hierarchy | LOW | Top 5 initially; explicit show-all retains every row; browser row-count checks |
| Legacy WO/equipment pages nested main landmarks and uncontained tables | MEDIUM | Semantic section wrappers and shared TableFrame; same queries/calculations; one-landmark regression |
| Next development indicator overlapped collapsed sidebar control | MEDIUM | Development-only reserved bottom spacing; actual collapse/expand interaction retested |
| Legacy equipment errors stayed loading / late responses could replace identity | MEDIUM | Terminal error/loading states, guarded responses, UNKNOWN totals; primary context remains independent of secondary KPIs; isolated error browser check |
| Loading/error WO totals temporarily appeared as zero | LOW | Explicit UNKNOWN until matching data is available; fetched values/calculations unchanged |
| Redundant old shell styling obscured component ownership | LOW | Remove replaced shell rules; preserve domain styles and theme compatibility |

Meaningful unsuccessful attempts were retained: the first backend command used
`src:tests`, shadowing the QA test namespace; CI-compatible `.:tests` resolved it
without backend edits. Browser harness assertions were corrected to inspect full
identifier titles, scope same-name controls to navigation and await Next navigation and asynchronous development-status resolution.
The actual indicator-overlap finding was fixed in UI; no forced clicks/hidden
overlay were used to manufacture a pass. Accessible scrolling regions are explicitly
allowed by scoped lint, rather than stripping keyboard access to satisfy a rule.

Security review: unchanged production/dev gates, local authentication/proxy modules,
Secure/HttpOnly/SameSite session, trusted Origin/CSRF, server roles/scopes and source
read-only ownership. Global authentication was not activated. No new source request,
credential forwarding, operational mutation or WO control was introduced. Existing
security suites retain RBAC/reviewer-independence coverage. This presentation review
does not establish operational identity provisioning or real engineer UAT.

## Validation and runtime evidence

- Local TypeScript, scoped ESLint, product-safety check and production build PASS.
- Existing frontend suites:143 assertions PASS (37+25+38+10+8+9+16).
- New UX component/route/date/contrast checks:33 PASS.
- Backend: 707 discovered, 484 PASS, 223 optional database tests SKIP, 0 failures; hermetic
  SQLite configuration and persistent test DSN unset. Remote CI uses its own temporary
  PostgreSQL; persistent QA/operational databases are never test-reset targets.
- HMR/source rollback:18 checks PASS; actual component Fast Refresh retained document/filter state; main rollback and candidate restoration retained the same Secure session and exact old record payloads. Final browser regression:105 checks PASS on the functional source, including unchanged factual values,15 routes plus asset/equipment detail, Secure QA login, prior exact record payloads, keyboard/mobile drawer, theme, responsive layout and unavailable states.
- CI backend/frontend must match the final PR HEAD; links/status belong to the exact
  PR check rollup, independent of the functional source screenshot SHA. Final release HEAD is verified through the PR checks and live status; no success is inferred from CI alone.
- Markdown references:213 local links across12 changed/onboarding documents PASS; original-image SHA256 and `git diff --check` PASS.

Runtime remains one HTTPS frontend at 3000, managed by `nadi-primary-web.service`;
existing `nadi-live-api.service` 13036 and fixture `nadi-dev-live-postgres`
(`nadi_live_dev_test`) remain. Port 13035 stays retired. Operational Cockpit API 8000,
collector APIs/webs/workers, all managed databases, Mart and schedules are preserved.
All container IDs/start timestamps compare unchanged with the before inventory.
Only development API/web units restart for supported source selection; no Compose
recreation occurs. Prior inspections/cases/recommendations are compared byte-for-byte
through authorized read-only QA retrieval. New authentication session/audit events
are expected; existing application data is never reset.

The original workbook SHA256 remains
`aa0bd8fd22275aea3ecf8654ee37878106123b7dbdf58135fb783e853ee66a5f`.
Private backups, authenticated browser material, actual-data captures, container
inventory and runtime evidence stay under ignored `.nadi-dev/state/ux-bundle-a/`.
Only labeled synthetic screenshots are eligible for Git.

## Rollback and continuity

Follow the [existing runbook](nadi-dev-reset-01.md). Controlled source rollback is
candidate → reviewed main 963e7a8 → exact candidate, retaining HTTPS, session and
fixture records. The previous 0bfea source, its branch/worktree, private dumps and
original stopped production frontend container remain available. No database
restore or collector restart is involved. HMR proof changes a real component label,
checks unchanged document/filter state and true dirty status, then restores only
that test's exact bytes. Operational policies are untouched.

Phase1's 24h review checkpoint (9 October 21:45 WIB) has passed; operator result is
UNKNOWN in available evidence. The 72h review is11 October 21:45 WIB; the 12 October 20:00
checkpoint and 13 October 00:00 hard expiry remain unchanged. The operator must record
required review/actions under the existing governance process; this frontend task
neither performs nor extends them. PR63 Q01–Q10 and operational Engineering gates
remain pending. Next action: review the exact-head PR and visible candidate, record
PO visual/navigation/token acceptance, then explicitly decide merge. No automatic merge.

## Changed surfaces and review limits

- Design primitives: `web/app/design-tokens.css`, `web/app/globals.css`, `web/components/ui.tsx`.
- Shell/navigation: `web/components/AppNavigation.tsx`, `web/lib/navigation.ts`.
- Overview: `web/app/page.tsx`, `web/components/ExecutiveOverview.tsx`, `web/lib/overview.ts`.
- Legacy state/semantics: `web/app/work-orders/page.tsx`, `web/app/equipment/[id]/page.tsx`.
- Tests/tooling: `web/scripts/ux-check.mjs`, `web/scripts/ux-browser.mjs`, synthetic `web/fixtures/executive-overview.json`, product-safety check, ESLint config, package/lock and the existing CI workflow.
- Continuity: context, PRD, Design System, UI spec, official roadmap/status, append-only DEV-LOG, development runbook, this report and three labeled regression screenshots.

No backend, contracts, collector, deployment/controller configuration, environment
file, original PNG, workbook, migration or operational data file changed. No
runtime package version changed; new dependencies are lint tooling only. The code
graph was a stale original-root generation2026-08-24; coverage identified new
candidate files as missing. Exact candidate source was read directly. This is a
bounded Bundle A review, not a claim of exhaustive repository/security coverage.
No critical/high review finding remains. Nonblocking debt: full legacy-form
accessibility audit, Next-specific ESLint plugin integration (build reports an
advisory; scoped React/hooks/a11y lint passes), optional local PostgreSQL tests
covered by isolated remote CI, and PO navigation/token/visual decisions. No
engineer UAT or operational activation is asserted.
