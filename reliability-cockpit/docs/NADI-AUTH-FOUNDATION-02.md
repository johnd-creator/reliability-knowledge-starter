# NADI-AUTH-FOUNDATION-02 — Local authentication integration

18 October 2026 (WIB). **PARTIAL — local login/security boundary active and tested;
factual portfolio grants and launcher authentication integration remain pending.**
Development evidence only; Product Owner acceptance and operational/production acceptance
are not granted. This supersedes the execution blocker in [AUTH-01](NADI-AUTH-FOUNDATION-01.md)
for the actions explicitly authorized by AUTH-02. Historical evidence is not rewritten.

## Source and ownership

- Single URL: `https://localhost:3000`; same active worktree `.nadi-dev/pdm-ui-fix-01`.
- Frontend/backend Git HEAD remains `7daab3a62866f19b30fb45462a94bafff8795dc5`, detached,
  with reviewed Mode A changes. HEAD alone does not identify the served source:
  [file SHA256 manifest](evidence/nadi-auth-foundation-02/source-manifest.json).
- Review parent `59b192a31d0aafadd6ab71b276b9daa399543d00` preserves Bundle01,
  FIX02 and AUTH01 reports. New task-owned review ref: `codex/nadi-auth-foundation-02`;
  exact review commit is supplied in the delivery response, not substituted for serving HEAD.
- Frontend systemd parent21538 unchanged; worker21559 →728443 at06:56:19 WIB,
  **expected Next config reload** after removing the public rewrite. Journal attribution
  was checked; no service stop/start command or additional worker replacement occurred.
- QA API parent21536 and its listener identities unchanged; both units NRestarts0.
  Node22.23.1, 4GiB heap and6GiB frontend MemoryMax preserved.
- Installed launcher files/release hashes unchanged. Official `attest` records the one
  expected config reload in an immutable local checkpoint. No replacement was silently
  accepted. [Attestation](evidence/nadi-auth-foundation-02/runtime-attestation.json).
- Dirty generated `next-env.d.ts` preserved exactly, SHA256
  `42519ed219a7f50dd811c8d87a1ed7e4e1a5b61e6fd977ffc0b732b104f2b82b`.
  Prior uncommitted UI work, all worktrees, original workbook and five PNGs preserved.

## Root cause and implementation

Previously, Engineering APIs had trusted sessions, but the workspace layout and factual
rewrite were public. Protecting login presentation alone could not secure factual reads.

The new middleware verifies each protected page request through the existing PostgreSQL
`SessionAuthority`; the server workspace layout independently verifies the session before
rendering the shell. Middleware is not the sole security boundary. The factual route
handler independently authenticates and authorizes each read. Cookie presence and
client role headers are never authority. No new identity store/provider is introduced.

Activation requires **all** existing explicitly approved laptop launch settings:
`NODE_ENV=development`, primary frontend, live development and Engineering QA flags true,
and exact QA backend `http://127.0.0.1:13036`. Production builds and other configurations
cannot activate this guard. Outside that configuration the new factual gateway fails
closed with503; the old unauthenticated rewrite has been removed. This is not a QA or
production authentication rollout.

Session verification uses the fixed loopback authority, bounded256KiB JSON, 3s deadline,
no redirects/cache, and only the exact bounded `__Host-nadi_session` cookie. No CSRF
secret is serialized through the server verifier. Layout/API failures close access.
Session-sensitive responses are private/no-store. Client focus/visibility checks,30s
polling, pagehide/pageshow handling, and hard logout navigation clear cached views;
these are presentation safeguards in addition to server enforcement.

## Network boundary and controlled recreate

The running container's labels identified the established Compose project plus **10
complete configuration files**, including existing private freshness/runtime overrides.
All were retained; only effective port publishing changed. Image startup source was
inspected in the running image: `cockpit serve` creates the read-only API and starts
uvicorn; it does not invoke init-db, migration, synchronization or collection.

| Property | Before | After |
|---|---|---|
| Host binding | all IPv4/IPv6 interfaces,8000 | `127.0.0.1:8000:8000` only |
| Container | `8145de57e40f…` | `7d6a470b507d…` |
| Image | `sha256:ffb4da000b3372456bfd27adb38eb3ec335404d51f775439252338bafa4851e7` | identical |
| Environment/mounts/network/command | existing approved effective config | preserved |
| Health |200 |200 |
| Non-target container identities/start times/PIDs |34 existing containers | identical |

Only `cockpit-api` was recreated once using the full original Compose configuration,
`--no-deps --no-build --pull never --force-recreate cockpit-api`. No init/dependency
service ran. Root `compose.dev.yaml` and the review candidate record the loopback binding.
Known host client: active frontend fixed loopback API. Known Docker consumer configuration:
legacy cockpit-web uses internal `cockpit-api:8000` and remains stopped. No unidentified
LAN consumer is asserted absent. Docker-internal routing is unchanged.

Own Wi-Fi-address port8000 connection was refused; loopback health remained200. No LAN
scan was performed. **Trusted host processes and Docker-network peers can still read
this unauthenticated internal factual upstream.** Loopback is defense in depth, not
an API authentication or hostile-local-user boundary. External firewall topology remains
outside this evidence. [Recreate evidence](evidence/nadi-auth-foundation-02/api-cutover.json),
[network/TLS evidence](evidence/nadi-auth-foundation-02/network-tls.json).

## Route and gateway matrix

| Surface | Anonymous/invalid session | Valid session |
|---|---|---|
| `/` and workspace pages, including RSC requests | login redirect; no shell | authenticated shell |
| `/login` | standalone login | safe return target, default `/` |
| Static logo, Next static/image assets | available | available |
| `/api/cockpit/*` |401 before factual read | read authorization below |
| `/api/engineering-qa/*` | existing server401/403 | existing roles/scope/CAS/CSRF |
| `/api/development/status` |401 | ADMIN only; other roles403 |
| Engineering password login | bounded existing login contract | same contract |

Factual gateway only admits GET, fixed `127.0.0.1:8000`, approved paths/unique bounded
query parameters,10s upstream deadline,2MiB responses, JSON, no redirects, private/no-store.
It forwards no browser cookie, source credential, role, Authorization or Set-Cookie.
A second authority check discards the response on revocation/grant change during the read.
Denied requests do not call factual upstream (instrumented hermetic tests).

| Factual read | Policy |
|---|---|
| `/health` | authenticated |
| Exact asset detail/context/condition/timeline/FMEA/health/integration paths | exact granted canonical asset ID |
| Maintenance/FMEA/health/overhaul lists | explicit granted `asset_ref`; actual running API filter checked |
| RCFA | denied; relationship/filter unavailable, no invented association |
| Portfolio aggregates, Asset Register, Registry, Data Trust, unscoped legacy reads |403 `FACTUAL_SCOPE_GRANT_REQUIRED`; no portfolio grant inferred |
| Writes, unknown paths, traversal, unknown/duplicate query, untrusted targets | denied |

**Remaining product gate:** current QA account scopes do not grant factual portfolio
access. Dashboard/register routes render an explicit grant-required error rather than
exposing unapproved assets, zero counts or fixtures. Global factual KPI values and SQL
semantics are unchanged upstream, but end-to-end factual dashboard/register acceptance
is **PENDING**, not PASS. A Product Owner-approved factual-read entitlement/filter policy
is needed; no broad scope or role correction was executed.

## Identity/capability matrix

| Existing account | Roles | Approved asset IDs | Capabilities |
|---|---|---|---|
| local-operator | ADMIN | NADI-ASSET-001; asset:SYNTHETIC:FOREIGN | login, shell, permitted views and diagnostics; existing private operator CLI |
| local-engineer | AUTHOR | NADI-ASSET-001 | existing authored/scoped Engineering workflow |
| local-reviewer | REVIEWER | NADI-ASSET-001 | independent scoped review |
| local-outsider | AUTHOR | asset:SYNTHETIC:FOREIGN | foreign NADI-ASSET-001 Case denied |
| Combined roles | only when explicitly granted | exact grant | review exclusions still apply to creator/assignee/contributor |

ADMIN does not imply AUTHOR/REVIEWER or all Cases. Actual valid review requests returned
AUTHOR403 `INDEPENDENT_REVIEWER_REQUIRED`, ADMIN404 `NOT_FOUND` (existing visibility
concealment). REVIEWER could read the authorized existing Case; outsider could not.
[Review denials](evidence/nadi-auth-foundation-02/review-denials.json).

No password reset, account creation, grant/scope mutation or default credential was
introduced. Existing generated fixture credentials were used privately for test accounts,
including `local-operator`; this proves executor QA login, not Product Owner acceptance.
The header displays the **trusted canonical account subject and roles**, plus Logout.
Human-readable username after refresh remains a UX/contract limitation: the current session
DTO exposes subject/roles/assets, not username. No client-asserted name is treated as authority.
Administration remains the existing private authorized operator mechanism; no account-management
web UI, SUPERUSER, external distribution or production activation is claimed.

## Validation and distinct self-review

- Frontend:20 groups successful,311 named assertions, plus product-safety and provenance
  checks; TypeScript PASS; ESLint0 errors/one pre-existing EngineeringWorkspace hook warning.
  Production build PASS in isolated copy using locked dependencies. Active-source TypeScript,
  changed security tests and lint also PASS. No dependency upgrade.
- Backend first run:260 tests,214 PASS/46 SKIP. Supplemental PostgreSQL/HTTPS/access run:
  46 PASS/0 SKIP, including the34 initially skipped Engineering PostgreSQL tests.
  The12 remaining PdM integration cases explicitly require CI and were not enabled by
  pretending to be GitHub Actions. No test reset was directed at retained QA/operational DBs.
- Disposable PostgreSQL: unique loopback15451, tmpfs,1CPU/512MiB/128PIDs, separate random
  credential and explicit exact database validation. Only that test container was cleaned up.
- Existing backend tests cover expired/revoked sessions, password-change requirements,
  rate limits, concurrency, idempotency, CSRF/Origin, self-review and role/scope restrictions.
- Real browser: trusted dedicated NSS profile plus explicit verified CA for Node HTTP
  test client. No certificate bypass, global trust modification or HTTP downgrade.
- Anonymous root and14 protected paths, forged cookie/actor/middleware headers, APIs,
  actual admin login/default root/refresh, authorized navigation, wrong credential,
  safe/external return URLs, logout/revocation/back navigation, role denials and scopes passed.
- Six login plus six record-ready PdM screenshots:390/768/1440px, light/dark, no page overflow.
  The initial loading-state PdM captures were replaced with record-ready captures.
- Actual Fast Refresh: temporary authenticated marker appeared in the same browser document;
  source restored byte-for-byte, no restart/new port/permanent test UI.
- Legacy disposable socket fixtures emit InsecureRequestWarning and do not establish CA trust;
  actual trusted-browser/HTTP acceptance above uses verified TLS independently.
- No GitHub CI run is claimed: delivery is a local task-owned review commit, not merged main.

[Validation summary](evidence/nadi-auth-foundation-02/validation-summary.json),
[browser results](evidence/nadi-auth-foundation-02/browser-results.json),
[Fast Refresh and final browser checks](evidence/nadi-auth-foundation-02/browser-final-results.json).

Distinct review corrections: reject RCFA rather than assuming an asset relationship; preserve
scope denial through the upstream read; remove stale factual-public-access login copy; add
pagehide cache clearing; authenticate unsupported methods/HEAD before denial. Deterministic denial tests and final build were rerun.

Meaningful failed attempts were retained privately: initial isolated-copy tests lacked sibling
fixtures/backend source; a misnamed test module and old login-copy assertion were corrected.
Playwright's HTTP client initially lacked the CA although Chromium trusted NSS; explicit CA
fixed it without bypass. Compose logical/physical network-name comparison blocked before any
change; corrected physical-name comparison passed. Post-recreate environment array order
caused a false alarm; key/value equality confirmed no drift and **no second recreate** occurred.
Archive extraction needed explicit stdout mode; no restore target was ever supplied. Account
preservation comparison correctly separated login-updated timestamps from immutable grants.
A malformed/unmapped review probe was not counted as authorization proof; valid-route follow-up
proved403/404. Automatic approval review rejected broadening diagnostic access; it was not
executed. ADMIN diagnostics remain restricted.

## Preservation, readiness and recovery

[Backup evidence](evidence/nadi-auth-foundation-02/backup-readiness.json) and
[preservation comparison](evidence/nadi-auth-foundation-02/preservation.json): readable
private before/after pg_dump archives retained under the existing ignored controller state,
mode0600. No restore into the active DB. Schema/constraints/ledger identical. Four Cases,
four human records, histories/receipts/attachments unchanged. All28 pre-existing sessions
retained with revocation/expiry/identity unchanged; only routine activity/CSRF renewal may
change. Test sessions/audit append normally; no deletion. Four existing accounts keep IDs,
password hashes, roles, asset scopes, active status and grant version. Login-related updated_at
is expected metadata. Operational database contents were not queried for this comparison.

**Launcher limitation:** installed `readiness()` still requests full frontend status anonymously.
It now fails closed. Official readiness was verified using a temporary in-memory HTTP adapter
with a genuine ADMIN test session and normal TLS, preserving every original source/process/
backend/schema comparison. The adapter was not installed and its own test session was revoked.
The installed controller release is unchanged. Do not attempt a worktree handover/cold restart
until an authenticated controller status workflow or separately reviewed minimal control-plane
health contract is integrated. Do not reopen anonymous full diagnostics to obtain PASS.

Recovery resources: private exact pre-change file copies, original active checkpoint, both
QA archives and prior source refs retained. Source-only rollback must target only this task's
files after hash/concurrency checks; preserve all prior dirty UI edits and next-env. Removing
the guard would reopen anonymous frontend access and requires an explicit security decision;
prefer fail-closed maintenance while fixing forward. Keep loopback binding. If the API binding
must be restored for a demonstrated dependency, use the recorded complete Compose config and
same image, one service only/no-deps/no-build/no-pull, with separately approved exposure controls.
Never restore/reset the active QA DB or restart collectors as an authentication recovery.

Source and services remain visible as dirty, not relabeled clean. At final runtime observation:
frontend parent21538/worker728443, QA parent21536, NRestarts0; frontend cgroup≈1.60GB and API≈161MB.
This bounded functional test is not sustained runtime qualification.

## Product Owner review and final gate

Open `https://localhost:3000` in a fresh/reloaded browser, use the existing assigned account,
check default dashboard and scope-required messaging, then PdM/Engineering, theme and Logout.
Use AUTHOR/REVIEWER identities only for their existing scoped workflows. Credentials are not
included in this report. Product Owner visual/login acceptance remains **PENDING**.

| Evidence | Desktop | Tablet | Mobile |
|---|---|---|---|
| Login | [1440](evidence/nadi-auth-foundation-02/login-light-1440.png) | [768](evidence/nadi-auth-foundation-02/login-light-768.png) | [390](evidence/nadi-auth-foundation-02/login-light-390.png) |
| PdM authenticated | [1440](evidence/nadi-auth-foundation-02/authenticated-pdm-light-1440.png) | [768](evidence/nadi-auth-foundation-02/authenticated-pdm-light-768.png) | [390](evidence/nadi-auth-foundation-02/authenticated-pdm-light-390.png) |
| PdM dark | [1440](evidence/nadi-auth-foundation-02/authenticated-pdm-dark-1440.png) | [768](evidence/nadi-auth-foundation-02/authenticated-pdm-dark-768.png) | [390](evidence/nadi-auth-foundation-02/authenticated-pdm-dark-390.png) |

Final: loopback/anonymous/session/security boundaries verified; overall **PARTIAL** until
factual portfolio authorization, authenticated launcher readiness and username UX are resolved.
No main/PR95–100 mutation, merge, collector/source request, migration, freshness change or
QA/production deployment. Next: Senior Review → Product Owner scope/Login/Admin Review →
Phase2 resume after the remaining gates, not automatic feature expansion.

## Delivery flags

```text
TASK: NADI-AUTH-FOUNDATION-02
STATUS: PARTIAL
COCKPIT_API_LOOPBACK_BINDING: VERIFIED
COCKPIT_API_RECREATE: EXECUTED_SCOPE_ONLY
NON_TARGET_SERVICES_PRESERVED: YES
GLOBAL_LOGIN_GUARD: PASS (approved local-development configuration only)
ANONYMOUS_ROOT: LOGIN_ONLY
PROTECTED_PAGES: VERIFIED (architecture plus bounded route/browser coverage)
FACTUAL_API_GUARD: VERIFIED (portfolio/register functionality pending grant decision)
DIRECT_UPSTREAM_EXPOSURE: RESTRICTED (loopback; trusted-host/Docker-peer caveat)
SESSION_AUTHORITY: EXISTING_REUSED
DEVELOPMENT_ADMIN: EXISTING_LOCAL_OPERATOR
ADMIN_AUTHENTICATION: VERIFIED (executor synthetic QA test; not PO acceptance)
ADMIN_ROLE_MATRIX: VERIFIED
INDEPENDENT_REVIEW_SECURITY: PRESERVED
SESSION_LOGOUT_REVOCATION: PASS
HTTPS_LOCALHOST3000: PASS
FRONTEND_TESTS: 20 groups PASS; 311 named assertions; TypeScript/lint/build PASS
BACKEND_TESTS: 214 PASS/46 SKIP; supplemental 46 PASS/0 SKIP
BROWSER_E2E: PASS within granted QA scope; factual portfolio acceptance PENDING
EXISTING_DATA_PRESERVED: YES
WORKTREES_PRESERVED: YES
OPERATIONAL_SOURCE_IO: NONE initiated by task
PR100_MERGED: NO
GITHUB_MAIN_CHANGED: NO
PRODUCT_OWNER_ACCEPTANCE: PENDING
NEXT_ACTION: Senior Review -> Product Owner scope/Login/Admin Review -> Phase 2 Resume
```

Discovery evidence: Tier2 graph generation2026-08-24 was stale/missing the current
frontend/auth symbols. Coverage was checked; material conclusions therefore use current
worktree source, actual running image source, deterministic tests and runtime observations,
not graph completeness. Existing accepted Phase1 governance is unchanged.
