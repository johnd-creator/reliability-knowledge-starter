# NADI UX Bundle C — login design and visual readiness

2026-10-10 · UX-08 / UX-09 preparation. Presentation, development acceptance,
merge, runtime visibility, final visual approval and operational activation are separate.

## Stage A — Bundle B finalization

The Product Owner's NADI-UX-BUNDLE-C directive gives provisional development
acceptance to PR66, with final visual review Monday, 12 October 2026. Exact head
`c840d88f360a24263550b665842b42edbded2e07` had backend/frontend SUCCESS,
PR OPEN/CLEAN/MERGEABLE, no change-request review or dirty serving worktree.
Controlled merge used that exact head without branch/worktree deletion.
[PR66](https://github.com/johnd-creator/reliability-knowledge-starter/pull/66) MERGED
2026-10-10T08:59:19Z at `cc90fc73bea6ae399383d8538035c6454dc7e65a`.
Its tree equals the reviewed Bundle B candidate; merge metadata is the only change.

Supported launcher backup → stop → switch origin/main → start selected merged
main on https://localhost:3000. Main/source/backend/launch SHA agree, clean, both
backends AVAILABLE. Same Secure/HttpOnly/Strict session survives source synchronization;
three original persisted inspection/case/recommendation payloads compare exactly.
Ten factual/product/Engineering routes render; operational container identities/start
times remain unchanged. Stage A PASS before new implementation branch creation.
Private fixture backups, prior source and all worktrees remain rollback resources.

Development accepted is provisional PO scope; final visual polish remains correctable.
This does not approve operational PdM methods, Q01–Q10 or actual engineer UAT.

## Stage B — UX-08 implementation

Branch `codex/nadi-ux-bundle-c` from verified latest main above. Functional source
`64eb1f73152267d454056abf798aed5bf89f9b27`; final introducing evidence HEAD,
exact-head CI, PR and serving SHA are independently verified in the final PR/task handoff.

- `web/components/LoginPage.tsx`: existing logo/product context, navy brand and form
  panels, factual Executive Overview link and explicit Engineering development boundary.
- `web/components/LocalLogin.tsx`: reusable V1 Button/input presentation, 48 px controls,
  labeled required guidance, unique IDs, keyboard focus on generic error, busy/spinner,
  expiry and existing password-change states. Inline QA callbacks remain compatible.
- `web/app/login/page.tsx`: presentation composition only; unchanged development opt-in
  and production 404 gate.
- `web/app/globals.css`: scoped login styles using current tokens; narrow screens compact
  decorative brand copy while preserving identity/context and form access. Dark theme retained.
- `web/scripts/login-design-check.mjs`, `login-browser.mjs`: rendered/presentation and
  actual/mock browser regressions. Existing UX CI invokes 9 new rendered assertions;
  lint scope includes both login components and route. No dependency or lockfile change.

Authentication submit function is byte-identical to merged main. Existing POST login,
GET session, callback or `/engineering/local` transition, 64/256 input bounds, required
fields, password clearing, error mapping and no automatic retry remain. Backend,
HTTP proxy, middleware, cookies/CSRF/RBAC/session policy, account directory and defaults
are unchanged. No self-registration/recovery, global redirect or extra frontend.
Synthetic errors use browser response interception, never invalid real-account attempts
or temporary-password changes on the actual backend. Actual acceptance uses one
existing assigned QA identity and read-only retained-record checks, without record writes.

## Review findings and corrections

Initial browser run found decorative required asterisks changed exact label lookup,
breaking existing Username/Password selectors. Labels were restored exactly;
native required semantics plus textual guidance retained. Rendered checks and browser
regressions were repeated. Narrow-screen brand copy was compacted to prioritize the
form; submit spinner contrast uses currentColor. These corrections affect presentation.
A subsequent test selector matched both the form alert and Next.js route announcer;
the test was scoped to the form, preserving both accessibility behaviors. The actual
login assertion initially raced the resumed session UI after route navigation; it now
waits for the trusted session heading before checking success. No authentication logic
was changed to fix these test races.
Medium accessibility finding: input/control boundaries initially used a pale shared
border token. Scoped login boundaries now use existing `--muted-2`; computed
contrast regression verifies both sides of form boundaries (3:1) and error text
(4.5:1), including dark-form text/boundaries. The final login browser run passes
96 checks. No shared token or authentication policy was changed.
Initial shell checks also exposed a wrong component directory and sandbox compiler
spawn EPERM; corrected working directories/authorized hermetic compiler runs passed.

Review verifies scoped styles/shared V1 primitives, no extra design system/dependency,
unique labels, 48 px controls, keyboard focus, explicit disabled reason, escaped generic
feedback and no credentials in browser storage/defaults. Auth/API files and operational
settings remain byte-unchanged. Graph generation 2026-08-24 lacks the login paths;
coverage was checked and exact candidate source read directly. This is bounded
implementation review, not exhaustive security or accessibility certification.

## Stage C — visual readiness and validation

Local TypeScript, scoped ESLint, production build, 143 existing frontend assertions,
43 shared UX assertions, 9 rendered login assertions (195 total) and product-safety
checks PASS. Login browser: 96 PASS including computed contrast, all three widths,
mocked errors/password-change, real assigned-account session and unchanged original
inspection/case/recommendation payloads. Fourteen sanitized state screenshots were
inspected. Existing Bundle A browser regression: 105 PASS; Bundle B: 129 PASS. Combined
browser evidence: 330 checks PASS at the exact functional SHA above. Final
evidence-only release has identical frontend source; its exact-head CI and source
activation are independently verified in the PR/task handoff. No CI result is
inferred from screenshots.

[Responsive/state screenshots](../../docs/design/ux-bundle-c/README.md) use sanitized
synthetic state interception; original logo and five official PNGs remain unchanged.
Comparison is against implemented Design System V1, since no official login screenshot
was supplied. Navy, green primary, white/surface panels, spacing, shape and focus use
existing tokens. Sidebar and factual navigation are retained. Desktop presents paired
panels; tablet/mobile compact decorative wording and stack the usable form. Dark
mode, required, pending, error, expiry and password-policy presentation are inspectable.
Screenshots do not establish PO approval. Final exact-head CI is recorded in the PR
check rollup independently of local/browser readiness and runtime status.

## Remaining visual decisions and safety gates

PO/senior review: brand tagline and language, logo scale/white surround, compact
mobile brand layout, Engineering navigation placement and final spacing/density.
Final visual review is Monday, 12 October 2026; no final acceptance is claimed here.
UX-09 remains preparation, not completed visual acceptance. Operational Q01–Q10,
engineer UAT and PdM readiness remain pending. No Phase 3 intelligence or global
authentication activation is included. Phase 1 review results remain UNKNOWN;
11 Oct 21:45 review,12 Oct 20:00 checkpoint and 13 Oct 00:00 hard expiry are unchanged.

Main source rollback uses supported stop → switch origin/main → start after clean
source checks. Prior candidate and private backed-up fixture remain retained. Final
runtime proof and public PR links are in the task handoff; only development source
selection is authorized, with collector/database process identities preserved.
