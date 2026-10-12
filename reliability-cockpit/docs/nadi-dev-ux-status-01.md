# NADI-DEV-UX-STATUS-01 — compact developer status

Date: 2026-10-12 (Asia/Jakarta). Scope: frontend presentation, focused assertions and evidence. Implementation/checks PASS; delivery PARTIAL until safe actual-preview verification. Product Owner review remains pending. No automatic merge.

## Baseline and runtime

- Verified main/base: `2e190c2b51fde50e0467d6d5165ebb1060902867`.
- Isolated branch: `codex/nadi-dev-ux-status-01`; exact implementation HEAD is recorded in the PR/GitHub check run, rather than a self-referential commit field.
- Existing sole frontend: `https://localhost:3000`, serving `f06abce76f8ef9b967ee5b1c2e0802112d77b056`.
- Existing QA backend: `b348235ce6f82c84873a65344ad2ef5fe276987d`, unchanged.
- Frontend `nadi-primary-web.service`: PID 2250511, started 2026-10-11 22:18:20 WIB. QA API `nadi-live-api.service`: PID 1664250, started 2026-10-11 07:53:34 WIB. No lifecycle operation performed.

## Before / after and implementation

Before: a full-width dark DevelopmentStatus banner consumes main-page space. After in the candidate: an explicitly development-gated `● DEV ▾` control sits beside the topbar theme control; the main content contains only application content. AppShell accepts a gated status slot; fullscreen authentication remains outside the Application Shell.

The disclosure preserves branch, full frontend/loaded/backend SHAs, clean/dirty state, compatibility approval, both backend availability states, isolated DB identity, Engineering fixture scope, launcher provenance and existing development links. No credential, DSN or private path is added. Verified split-source compatibility is valid only with the existing explicit approval and clean/current process identity. Dirty/stale/unapproved/service-failure states remain amber; endpoint failure is a distinct unavailable state. Color is supplemented with text and symbols.

Native buttons, named region, focus on opening, Escape/close focus return, outside pointer/focus dismissal and route-change dismissal support keyboard use. V1 tokens, wrapping full SHAs and a bounded scrollable panel support light/dark and mobile. No dashboard, sidebar information architecture, data contract or authentication behavior changed. Production rendering and development-without-authorization both omit the control.

## Root cause of current warning

The original serving checkout has one tracked modification, `reliability-cockpit/web/next-env.d.ts`: Next replaced the generated route-type cache reference `./.next/types/routes.d.ts` with `./.next-primary-dev/types/routes.d.ts`. This is generated development dirt, not a new serving SHA, stale process or demonstrated API contract drift. Frontend/backend version separation was previously explicitly approved, but the existing provenance guard requires both sources clean. The dirty source therefore invalidates that approval and honestly produces UNCOMMITTED / UNVERIFIED / stale release status.

No whitelist, fabricated approval, hidden warning or altered endpoint guard was introduced. The task explicitly prohibits overwriting/resetting dirty running worktrees. The controller's frontend-only preflight calls `source(previous, previous_sha)` and refuses dirty previous source with `DIRTY_FRONTEND_SOURCE_DENIED`, before any service stop. Candidate activation and actual-after verification must wait for separately authorized safe handling of that checkout. No backend/process intervention is required or attempted for this UI change.

## Validation and distinct review

- TypeScript, production build and product safety: PASS (58 UI files). Build uses a non-serving backend address; no source acquisition.
- UX assertions, including 12 new status/gating assertions: PASS. Same-source and explicitly approved split-source, dirty/stale/unknown/unavailable, full process identity and production gates verified.
- Existing Engineering, Phase 2, workflow, bounded HTTP/proxy, local-auth and product assertions: PASS.
- Network-isolated actual-component browser regression: PASS, 455 checks; desktop 1440px, tablet 768px, mobile 390px, light/dark, keyboard, full disclosures, lifecycle warnings and existing Case → Recommendation → Advisory → Inbox/ACK synthetic workflows. No real database writes or second frontend service.
- Lint: PASS with one pre-existing unrelated EngineeringWorkspace effect-dependency warning. The new named disclosure was changed from redundant section-role markup to a div region; missing endpoint lint coverage was restored without editing the endpoint.
- Review repaired two harness findings: outside-click target intercepted by the open tablet panel, and a nonexistent translated unavailable-string key. Retests PASS; no production behavior workaround.
- Visual review: compact closed control, readable full SHA panel, internal viewport bounds and light/dark checked. Explicit panel focus outline added. [Screenshots/provenance](evidence/nadi-dev-ux-status-01/README.md).
- `git diff --check`: PASS. Dependencies/lockfile, status endpoint, compatibility library, official launcher, backend, authentication and business workflow sources unchanged.
- Exact-head GitHub backend/frontend CI is verified after push and linked at PR handoff. Local tests are not runtime deployment evidence.

## Preservation, rollback and pending gate

Private before/after snapshots compare all 35 container identities/start times/restart counts, frontend/API ownership, original serving SHA and exact existing dirty diff, plus five original PNG and workbook hashes. No database/schema/migration/session/account mutation, source GET, collector retry, service restart, freshness policy change or additional frontend was performed. Original worktrees, untracked workbook, persistent QA records and backups were retained. Database content was not re-audited or rewritten by this presentation task.

Current runtime is retained, so runtime rollback is unnecessary. Existing previous frontend/backend release resources remain present, but executing rollback/source selection has the same dirty-source safety gate and is not claimed ready for immediate mutation. Reverting the isolated presentation commit is a separate source-level rollback option. Actual HTTPS before screenshots remain private; published after screenshots use synthetic fixtures only. Final release/visual acceptance cannot be claimed until official preflight succeeds and actual preview is checked.
