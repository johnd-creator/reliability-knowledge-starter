# NADI-AUTH-FOUNDATION-03

18 October 2026 WIB. Local implementation and acceptance PASS; Product Owner acceptance PENDING.
This task implements the Product Owner's explicit BSR/IP factual-read authorization,
login-aware readiness and trusted self username. It preserves the
[AUTH-02 boundary](NADI-AUTH-FOUNDATION-02.md) and earlier Phase2 UI changes.

## Authorization

Only the verified retained directory subject
`local:c759c2d1-19a4-4291-9b66-9218dbd12dea`, with current ADMIN, receives the code-only
`BSR_IP_FACTUAL_PORTFOLIO_READ` capability in the approved primary local-development
runtime. A username, browser header, generic ADMIN role, synthetic asset grant or query
parameter cannot confer this capability. No directory grant or SQL permission changes.

Approved canonical portfolio aggregates and Registry lists remain BSR/IP; exact detail
and asset-ref requests require a server-side Registry lookup with matching canonical ID,
siteBSR and organizationIP. Scoped AUTHOR/REVIEWER do not inherit portfolio totals via
asset context/integration responses. Existing Engineering permissions, review independence,
canonical audit subject, CSRF, Origin, revisions and persistence remain authoritative.

Legacy `/equipment`, `/work-orders`, `/kpis` are deliberately not newly authorized:
their published DTO/query contracts do not prove BSR/IP/Registry scoping. Export, unknown
routes and writes remain denied. This is not a blanket access grant to every backend route.
RCFA asset relationships remain unresolved; approved global BSR/IP RCFA reads do not
create such relationships or permit cross-inspection diagnosis/scoring.

## Self identity

The current-session route adds only the actor's `username`, read from the existing local
directory inside the valid session lease. It does not accept a target username/subject,
expose another account, return security metadata, or replace immutable subject/roles/assets.
The header shows the recognized username, canonical subject as audit tooltip, role labels
and existing Logout. Missing username falls back to the canonical subject.

## Controller readiness design

Full development diagnostics remain ADMIN-only. New local-only
`/api/development/health` exposes a narrow transport contract: source/launch SHA, dirty
state, expected origin and guard identity; no DB/account/session data or full diagnostics.
QA `/health/ready` reports the initialized local SessionAuthority capability plus DB
connectivity. The launcher combines these with existing process/socket/start-time/Node,
source, bootstrap, QA database identity, factual health and compatibility checks.

Anonymous root must give the exact known login redirect with no-store; anonymous factual
health must give the exact401 contract; a fake session must be rejected through the actual
Engineering session route. An optional owner-only current session file additionally tests
real session verification and authenticated factual health. Absence of that proof is reported
NOT_PROBED_NO_SESSION, never falsely labeled a positive session test; an explicitly supplied
expired/revoked proof fails closed. No arbitrary302/401 alone establishes authentication health.

The source controller preserves existing lifecycle, backup, clean-initial/dirty-active,
checkpoint, schema compatibility and recovery checks. A focused metadata-only installer uses
the existing immutable four-file release/manifest/wrapper model, exact Git source blobs and
the already established ROOT-path binding. It validates candidate readiness independently
before changing pointers, retains the old release/configuration, locks against concurrent
updates, and recovers metadata only on failure. No source handover, service restart, database
restore/migration or lifecycle command is part of installing this readiness update.

Application bootstrap SHA and installed controller implementation SHA are separate provenance
fields. Updating the readiness implementation never relabels the already running QA bootstrap.

## Pre-activation evidence

- Active HEAD remains `7daab3a62866f19b30fb45462a94bafff8795dc5`, dirty ModeA;
  AUTH-02 review parent `d17450d4811d8978d01f919032e7d319c523a4c1` retained.
- Existing controller/bootstrap release `106a4dc08b149576b2e84bbf8c70694288c7e9a7` retained.
- Frontend parent21538/worker728443 unchanged. QA parent21536 unchanged; source reloader
  replaced child21549 with834916 after the three reviewed auth files changed. No unit restart.
- Cockpit API remains127.0.0.1:8000, all35 baseline containers retained without recreation.
- Staged frontend21 groups PASS; TypeScript/lint/build PASS (one pre-existing hook warning).
  Backend210 PASS/0 SKIP on disposable PostgreSQL. Launcher/update/lifecycle119 PASS/0 SKIP.
- Actual trusted HTTPS browser checks passed for ADMIN factual dashboard, Registry/detail,
  scoped canonical modules, username refresh, restricted AUTHOR, review denial and logout.
  Register response matches direct factual API exactly. Executive DTO stable fields match;
  query-time as_of/window_start differ naturally between requests with identical window basis.
- Six responsive light/dark dashboard captures plus Registry capture retain real UI and redact
  sensitive asset rows only during screenshot capture; no intercepted data or fixtures.

## Final local acceptance

Code and installed controller checkpoint: `fef7bccd61d3d6a5dd184f2fff94453242ff2056`.
Review parent: `d17450d4811d8978d01f919032e7d319c523a4c1` (AUTH-02).
Branch: `codex/nadi-auth-foundation-03`; final evidence commit is a documentation-only
child of this checkpoint. All19 application/controller/test file blobs in the
[source manifest](evidence/nadi-auth-foundation-03/source-manifest.json) match that code SHA.

Serving Git HEAD remains `7daab3a62866f19b30fb45462a94bafff8795dc5`, with explicitly
reported dirty ModeA source containing Bundle01/FIX02/AUTH02/AUTH03. It is not falsely
reported as serving the clean review commit. Worktree remains `.nadi-dev/pdm-ui-fix-01`.
Frontend and QA backend use that same selected worktree; no handover. Node22.23.1,
heap4096MiB, MemoryMax6GiB preserved. Source graph generation2026-08-24 is stale/missing
these additions; exact active source, tests and file hashes were used for verification.

| Capability | Authorized local-operator ADMIN | Scoped AUTHOR/REVIEWER | Anonymous/invalid session |
|---|---|---|---|
| Canonical BSR/IP portfolio/Registry/overviews | Approved read | Denied | Denied |
| Exact registered Asset/detail/evidence | Registry identity + BSR/IP required | Exact asset grant + Registry identity + BSR/IP | Denied |
| Context/integration asset DTO containing portfolio totals | Approved read | Denied despite exact asset grant | Denied |
| Canonical maintenance/FMEA/health/overhaul collection | Approved read | Exact permitted asset_ref required | Denied |
| RCFA unresolved asset linkage | No invented link; global approved read only | Denied | Denied |
| Legacy equipment/Work Order/KPI populations | Not newly granted | Denied | Denied |
| Full development diagnostics | Existing ADMIN check | Denied | Denied |
| Narrow local transport health | Local runtime only; no private diagnostics | Same narrow contract | Same narrow contract |
| Engineering write/review/ACK | Existing role/scope rules; no ADMIN bypass | Existing role/scope/revision/independence rules | Denied |
| Export/source mutation/account grants | No new permission | No new permission | Denied |

Actual administrator login, dashboard, Asset Register/detail, canonical maintenance,
FMEA/RCFA/overhaul, integrity/Data Trust and integration API reads passed. Registry DTO
matched actual stored factual API, total845 at observation; this is an observed count,
not a fixed fixture/acceptance constant. Unknown condition/risk remains NOT ASSESSED.
PdM/Cases/Recommendations/Action Board authenticated read screens and QA boundary passed.
Write-oriented workflow/security tests ran only against disposable PostgreSQL; no retained
business record was created or edited. No new source requests or source-system writes.

## Installed launcher acceptance

The explicit installer verified all four old private release hashes and the wrapper,
read four exact Git blobs at the checkpoint, applied only the established ROOT binding,
and independently verified candidate TLS/process/source/DB/auth readiness before updating
metadata under both existing lifecycle/selection locks. It retained previous release,
manifest/wrapper/active records in the existing private rollback directory. New release:
`auth03-controller-fef7bccd61d3-b3e87194`. No service lifecycle command was executed.

- Installed controller implementation SHA: `fef7bccd61d3d6a5dd184f2fff94453242ff2056`.
- Application bootstrap SHA remains `106a4dc08b149576b2e84bbf8c70694288c7e9a7`.
- Both frontend/backend selected source HEAD remain `7daab3a62866f19b30fb45462a94bafff8795dc5`.
- `nadi-dev local-status`: transport/process VERIFIED; exact anonymous login redirect,
  anonymous API denial and invalid-session rejection VERIFIED; positive session NOT_PROBED_NO_SESSION.
- Same command with owner-only genuine test-session file: positive session VERIFIED.
- Existing CSRF-protected Logout revoked only this task's own ADMIN session. Gateway/session
  then401; explicitly supplying the revoked proof failed AUTHORIZED_SESSION_INVALID_OR_EXPIRED.
  Default status still passed. No stale credential was accepted or silently downgraded.
- Source/DB/bootstrap/controller mismatch, unknown redirect, missing backend, invalid/expired
  proof and replaced frontend are rejected by deterministic regressions. These failure cases
  were simulated; no live service was intentionally broken for testing.

See [readiness results](evidence/nadi-auth-foundation-03/readiness-results.json).

## Validation and distinct self-review

| Check | Actual final result |
|---|---|
| Frontend | 21 groups PASS;321 named assertions plus provenance/product-safety checks |
| TypeScript | PASS |
| ESLint | PASS,0errors;1 pre-existing EngineeringWorkspace hook dependency warning |
| Production build | PASS in isolated copy with locked dependencies, active dev build untouched |
| Backend | 210 PASS,0SKIP, temporary synthetic PostgreSQL only |
| Launcher/readiness/update/lifecycle | 119 PASS,0SKIP, hermetic |
| Actual HTTPS browser | 12 checks PASS,0page errors, normal trusted TLS |
| Responsive/theme | 1440/768/390, light/dark, no page overflow |
| Source/diff | Exact code blobs matched checkpoint; git diff --check PASS |
| GitHub CI | NOT_RUN; local review delivery, no push/PR mutation |

Self-review identified that context/integration DTOs include portfolio totals. Exact asset
permission alone was insufficient; both are now denied to scoped users, with focused
regression coverage. Readiness distinguishes absent session proof from verified proof.
Installer recovery handles failure after manifest replacement; interrupted swap/post-install
failure tests retain old metadata. No unresolved HIGH/CRITICAL finding in the changed scope.

Meaningful test corrections are retained in the [validation summary](evidence/nadi-auth-foundation-03/validation-summary.json):
separate query timestamps made the first DTO comparison too strict; the harness now compares
stable values exactly and separately checks query-time/window consistency. A supplementary
logout check initially called nonexistent `/logout`404, then used the existing verified
`session/logout` route; no application patch was needed. Final preservation initially assumed
QA child could not change despite the intentional source edit; journal evidence established
the expected reload, which is explicitly recorded rather than hidden as unchanged.

## Browser evidence

Real existing HTTPS3000 and local APIs, no intercepted responses/synthetic factual values.
Only sensitive asset table bodies are redacted during screenshot capture; source and actual
UI remain unchanged. Captures are local-development evidence, not plant acceptance.

- [Desktop light](evidence/nadi-auth-foundation-03/dashboard-light-1440.png) /
  [dark](evidence/nadi-auth-foundation-03/dashboard-dark-1440.png).
- [Tablet light](evidence/nadi-auth-foundation-03/dashboard-light-768.png) /
  [dark](evidence/nadi-auth-foundation-03/dashboard-dark-768.png).
- [Mobile light](evidence/nadi-auth-foundation-03/dashboard-light-390.png) /
  [dark](evidence/nadi-auth-foundation-03/dashboard-dark-390.png).
- [Asset Register, rows redacted](evidence/nadi-auth-foundation-03/asset-register-1440-redacted.png).
- [Browser results](evidence/nadi-auth-foundation-03/browser-results.json).

## Preservation and rollback

[Runtime attestation](evidence/nadi-auth-foundation-03/runtime-attestation.json) and
[data preservation](evidence/nadi-auth-foundation-03/preservation.json) confirm:

- Frontend parent21538/worker728443 unchanged; QA unit parent21536 unchanged; both NRestarts0.
  QA child21549→834916 is the journal-proven source reloader at08:42:07WIB after three
  reviewed auth modules changed. Same invocation, parent start time and listener inode;
  no unit restart. This expected backend source reload is not claimed as no backend change.
- All35 original containers have identical IDs/start times/PIDs/mounts, including Cockpit API.
  API publish remains exactly127.0.0.1:8000. No collector, operational API, Mart or DB restart.
- Existing4 Cases,4 human records,12 Case events/receipts,15 human revisions/receipts and
  migration ledger5 unchanged. Schema and all constraints, including Advisory/ACK, identical.
- All39 pre-existing sessions retain identity/expiry/revocation fields; no deletion/revocation.
  Three test sessions appended. Normal last_seen/CSRF metadata changes permitted. Audit rows
  retained append-only. Account identity, roles, grants, activity flags and password hashes
  unchanged; only normal login metadata can change. Four existing accounts preserved.
- Before/after private QA archives, readable TOC/full archive parsing verified, retained under
  `.nadi-dev/state/local-dev-01/auth03-retained-{before,after}.dump`,0600. No restore attempted.
  Private original source/baseline and old controller metadata retained there, not committed.
- Disposable test container removed only after exact label/port/tmpfs verification; original35
  remain. Original workbook/five PNG SHA256 unchanged; next-env.d.ts original dirty hash retained.
- No main, PR100/F03, source cursor, freshness policy, operational identity or collection change.

Rollback is scoped, reviewed and non-destructive: under the existing lifecycle/selection lock,
verify current candidate hashes and no intervening edits, then restore only AUTH03-owned source
from retained exact originals (remove only newly introduced task files after hash verification).
This restores AUTH02 global guards; never reset/clean the worktree or revert unrelated UI code.
For controller failure use retained exact manifest/wrapper/active metadata, preserving current
source selection and all database data. The old readiness may again fail closed under AUTH02;
that is not permission to expose diagnostics or relax authentication. Live rollback was not
performed because current acceptance passed; metadata recovery was tested hermetically.
Do not restore a DB backup over the active database or delete records for rollback.

## Delivery limitation and next gate

Local-only review ref preserves prior5-commit UI/auth lineage. Cached origin/main is
`4914a73fc7b640b6dd0667d0450fdb12aa04c452`; it diverges from this active development lineage
(19 main-side commits,5 task-lineage commits before final evidence). It is not a freshly
verified remote main. Creating a PR against main would mix earlier local tasks and unrelated
history; no rebase/handover/push or CI was performed. A separately scoped history reconciliation
is needed before GitHub delivery; current local implementation acceptance is not remote CI.

Required flags: GLOBAL_LOGIN_GUARD PRESERVED; ADMIN_FACTUAL_PORTFOLIO_READ VERIFIED;
ASSET_REGISTER_ACCESS VERIFIED; FACTUAL_API_SCOPE_ENFORCEMENT PASS; ANONYMOUS_DATA_ACCESS DENIED;
DEVELOPMENT_ADMIN_ACCOUNT PRESERVED; USERNAME_DISPLAY PASS; CANONICAL_AUDIT_IDENTITY PRESERVED;
LAUNCHER_AUTH_READINESS PASS; SHA_DATABASE_COMPATIBILITY_GATES PRESERVED;
ADMIN_INDEPENDENT_REVIEW_BYPASS DENIED; COCKPIT_API_LOOPBACK VERIFIED;
LOCALHOST3000 AVAILABLE; EXISTING_DATA_PRESERVED YES; NON_TARGET_SERVICES_PRESERVED YES;
GITHUB_CI NOT_RUN; PRODUCT_OWNER_ACCEPTANCE PENDING; PR100_MERGED NO.

Next: Senior Review → Product Owner Final Authentication Acceptance → Resume Phase2.
STOP after delivery. No merge/deployment or automatic next task.
