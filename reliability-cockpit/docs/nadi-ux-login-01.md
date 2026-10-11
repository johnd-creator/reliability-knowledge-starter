# NADI-UX-LOGIN-01 — fullscreen QA login

Baseline verified 2026-10-11: `f8f8f2c9bcf8fc64375c1203b4627ac634dcbe26`.
PR69, PR70 and PR72 are merged. Implementation branch: `codex/nadi-ux-login-01`.
Previous frontend: `5d8b5c07531a9b8da9ee5f82a740ee7b519488bd`;
pinned QA API: `b348235ce6f82c84873a65344ad2ef5fe276987d`.

## Root cause and architecture

The root layout previously wrapped every page, including `/login`, in AppShell
and DevelopmentStatus. It now owns only document metadata, shared CSS and the
presentation ThemeProvider. `(authentication)` provides one full-viewport main;
`(workspace)` owns AppShell and the existing development banner. Route groups
change source organization without changing URLs. All existing pages, Engineering
error/loading boundaries and API handlers are retained; moved pages change relative
imports only. There is no middleware, global authentication redirect or second app.

The login is navy/white with the unchanged original logo, a readable Indonesian
form, visible synthetic-QA identification, compact mobile branding and an independent
theme control. It has no dashboard link, sidebar or application topbar. Technical
SHA/availability remains available at `/api/development/status` and on workspace
pages. Login is explicitly Engineering QA rather than a claim of production access.

## Authentication boundary

The server login gate still requires development plus `NADI_ENGINEERING_QA_ENABLED`.
LocalLogin retains the real `auth/login` then trusted `session` read and navigates to
`/engineering/local`; no identity, roles or scope comes from form fields. The backend,
proxy, transport, cookies, CSRF, Origin, session policy and persistence are unchanged.
A revoked/expired local-workspace session clears prior-user state before navigating
to `/login?expired=1`. Successful existing logout revokes only the current test
session, clears scoped state and returns to `/login`. Anonymous local workspace
redirect follows the backend's 401. Other protected pages retain their existing
gates; public factual pages retain their existing development policy.

## Distinct review and corrections

| Finding | Severity | Correction / verification |
| --- | --- | --- |
| Root shell also wrapped login | High UX | Route groups; static boundary checks and actual candidate browser assertions |
| Theme initialization coupled to sidebar | Medium UX | Shared root provider; login/workspace theme and reload coverage |
| Test router recreated its identity on each render | Medium test | Stable fixture router matching Next; logout no longer races redirects |
| Source-file assertions assumed old page paths | Medium regression | Updated assertions for groups; production route inventory preserves URLs |
| Existing factual render harness lacked alias/localized-module resolution | Medium test | Compile real views with TypeScript aliases and exact Indonesian UNKNOWN text; SQLite acceptance passes |
| Mobile marketing heading hid the only h1 | Medium accessibility | Login form has h1; inline QA forms retain h2; decorative branding is a paragraph |

No critical/high implementation finding remains after correction. Existing
EngineeringWorkspace hook warning remains baseline technical debt; lint has no
errors. Bounded keyboard/contrast/responsive checks are not a complete accessibility
certification. Product Owner visual/wording decisions remain pending.

## Validation and evidence boundaries

TypeScript, lint, production build and all existing frontend assertion suites PASS.
Backend scoped regression: 204 tests, 127 PASS / 77 optional SKIP, no failure;
canonical contracts: 14 PASS. Persistent PostgreSQL branches are independently
covered by exact-head GitHub CI in its disposable database, never the live QA store.
The network-isolated actual-component browser suite passes 395 checks and exercises Case → Recommendation
→ Advisory → Inbox/ACK, CAS/idempotency, denied access, login/error/expiry/logout,
keyboard, theme, and route layouts at 1440/768/390. These simulated mutations never
reach localhost or the existing records. Browser result and image index are in the
[evidence directory](evidence/nadi-ux-login-01/README.md).

Actual preview acceptance is a separate step after sealed source/CI checks through
the official frontend-only controller. Private snapshots and live reports reside
under `.nadi-dev/state/ux-login-01/`. Do not equate fixture screenshots or CI with
runtime visibility. Exact release SHA, CI and live acceptance are recorded in the
PR handoff and final report after controlled activation.

## Runtime preservation and rollback

Only `nadi-primary-web.service` may cycle. The installed reviewed controller must
approve exact frontend/backend source equivalence, clean source, process ownership,
TLS/configuration, private readable recent backup and previous-source rollback.
It must not checkout the QA API worktree or restart API/migration helpers.

Before runtime change: read-only schema/grant/ledger and all-row fingerprints,
86 existing sessions, 3 accounts, 10 cases, 17 human records (3 Advisory / 3 ACK),
35 container identities/start times and API process/cgroup identity captured.
All five original PNGs, workbook, worktrees, backups and collector services retained.
Live tests may append ordinary login/security audit records and revoke their own
new test session only; no existing business record/session reset or schema write.

Use the existing wrapper `./.nadi-dev/nadi-dev backup`, then `frontend-preflight`
and `frontend-select` with the exact clean managed worktree, 40-character SHA and
private backup. Keep the immutable recovery JSON emitted by selection. Rollback
uses `frontend-rollback <recovery-json>` or reviewed `frontend-preflight`/selection
of the retained former source, touching the frontend only. Do not run rollback just
to disrupt a passing preview. No merge, production activation or Phase1 policy change.
