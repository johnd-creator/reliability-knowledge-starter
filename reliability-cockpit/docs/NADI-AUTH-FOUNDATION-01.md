# NADI-AUTH-FOUNDATION-01 — Security preflight BLOCKED

18 Oktober 2026. **BLOCKED before application implementation/activation.**
Global login is not active. Anonymous factual access still exists. A login-page redirect
alone would not meet this task's security objective.

## Immutable runtime and preservation

- Active worktree `.nadi-dev/pdm-ui-fix-01`; HEAD
  `7daab3a62866f19b30fb45462a94bafff8795dc5`, still detached/dirty Mode A.
- Bundle01 prepared commit `61697806356918655ab2901d5e2ff2cc7a5bd902` and FIX02
  `01053d77c64b9c755a6a2ba1250c294fcb2dcf7a` preserved.
- Frontend parent21538/worker21559 and QA API parent21536 remain active, restart0.
- No application/auth/backend/config/controller/firewall changes, account grants,
  session writes, SQL mutations, migrations, source acquisition or service restart.
- Only this preflight report/evidence and append-only DEV-LOG are added.

## Blocking findings and actual evidence

**AUTH-F01 — direct factual upstream bypass.** `cockpit-api` publishes8000 on both
`0.0.0.0:8000` and `[::]:8000`. Anonymous local GET
`http://127.0.0.1:8000/v1/reliability/assets?limit=1` returns200. This is a stored
Mart read, not a production source request. No asset payload is printed or committed.
Root `compose.dev.yaml` explicitly declares `ports: ["8000:8000"]`.

Firewalld is running. Its active `docker-forwarding` policy has targetACCEPT,
ingressANY, egressdocker. Wi-Fi and Docker bridge zones are active. Complete nftables
rules could not be verified with available privileges. Therefore non-loopback publishing
and a permissive forwarding path are confirmed; end-to-end remote reachability and
other host/network controls remain **UNKNOWN**, not verified restricted. No LAN scan,
external connection or firewall modification was attempted. Direct upstream protection
is **BLOCKED** for acceptance.

**AUTH-F02 — factual authorization scope is not defined by QA admin identity.** The
existing ADMIN scope must not implicitly grant access to every factual Registry asset.
A bounded first page of100 factual assets (API total845 at inspection) had0 matches
with current admin asset IDs; this is **not** an exhaustive absence claim. A reviewed
factual-read entitlement/filtering policy is required before permitting portfolio,
list/detail or aggregate API access. No broad scope or role is silently assigned.

**AUTH-F03 — operational/config approval gate.** Task §7 explicitly requires necessary
backend/auth configuration to be isolated, reviewed and separately approved before
changing the active service. Restricting Docker's existing host port requires either
controlled recreation of only `cockpit-api`, or separately approved host firewall controls.
Neither is performed. No cosmetic global page guard is activated while this bypass
and scope boundary remain unresolved.

## Current and desired architecture

Current: standalone login → PostgreSQL-backed SessionAuthority/LocalIdentityProvider
for Engineering QA only. Factual pages and the `/api/cockpit/*` rewrite remain public.
The operational API factory does not mount the QA local directory. Node22/HTTPS/Secure
cookies and existing session/CSRF/Origin/revision rules remain intact.

Desired after approvals: explicit local-development enablement → trusted **server-side**
session validation before protected page/RSC rendering → independent guarded factual
proxy (bounded, read-only allowlist, trusted scope) → private factual upstream.
Do not rely on client roles, cookie presence, AppShell hiding or middleware-injected
headers alone. Every relevant API must enforce its own verified authority. No result
or identity may be cached across users; no-store and logout/expiry invalidation are required.
Default login return should become `/`, with a reviewed internal route/query allowlist;
current FIX02 allowlist/default remains unchanged until implementation is safe.

## Page/API protection matrix — actual current state

| Surface | Current | Required; not implemented in this task |
|---|---|---|
| `/`, `/assets` | Anonymous HTTPS GET200, no login redirect | Server guard before content/shell |
| Other workspace/factual routes | Existing policy unchanged; not exhaustively HTTP-tested here | Explicit protected route matrix, no RSC/cache bypass |
| `/pdm`, Engineering/recommendations | Page shell visible; record APIs use existing session/scopes | Server page guard plus current record authorization |
| `/login` | Existing standalone development-only login | Remain public; validated return destination, default `/` |
| Essential static assets | Existing policy | Narrow public allowlist, not broad path-prefix bypass |
| `/api/cockpit/*` | Anonymous sample returns200 through rewrite | Verified session, approved role/scope, explicit GET/HEAD path/query allowlist and bounded JSON proxy |
| `http://*:8000` | Wildcard published upstream, anonymous local factual200 | Trusted host/internal network only, with owner-approved controls and direct-exposure evidence |
| `/api/engineering-qa/*` | Existing authoritative session, Origin/CSRF and roles/scopes | Preserve; narrow unauthenticated login/session-denial endpoints |
| `/api/development/status` | Existing development-only diagnostic | Restrict sensitive provenance to authenticated authorized session |

Only root/assets/proxy/upstream samples were probed in this preflight. Other current
security behavior is source-reviewed and historical evidence, not fresh full acceptance.

## Administrator directory and capability matrix

Read-only PostgreSQL transaction verified exact loopback127.0.0.1:15443 database
`nadi_local_dev_01_test`, configured application user `nadi_local_dev_01`. Selected
only username/active/roles/asset_ids/grant_version/password-change flag; no password
hash, session token, CSRF, login budget or security-event content was selected.
Four active accounts, grant_version1, all unchanged:

| Existing identity | Role | Asset scopes |
|---|---|---|
| local-operator | ADMIN | NADI-ASSET-001; asset:SYNTHETIC:FOREIGN |
| local-engineer | AUTHOR | NADI-ASSET-001 |
| local-reviewer | REVIEWER | NADI-ASSET-001 |
| local-outsider | AUTHOR | asset:SYNTHETIC:FOREIGN |

A Development Administrator **already exists**. No provisioning/default password is needed.

| Capability | Current authority |
|---|---|
| Private account administration | Existing `python -m src.qa.users`; current ADMIN grant, exact database and interactive getpass; only within ADMIN asset scope |
| Create/edit Engineering records | AUTHOR and existing ownership/assignment/scope rules; ADMIN alone is not AUTHOR |
| Case visibility | CaseService.visible requires asset scope and REVIEWER or creator/assignee; ADMIN alone does not gain arbitrary Case access |
| Independent review | REVIEWER, matching scope, contributor/author/assignee exclusions; ADMIN does not override |
| Public admin HTTP mutations | Not implemented; no new public account endpoint |
| Factual portfolio access | New trusted entitlement/scope policy required; never infer all-assets from ADMIN |
| Mart/Maximo/PI mutation | Forbidden; identity roles never grant SQL/source write privileges |
| Unimplemented modules | Remain PLANNED |

Do not add AUTHOR/REVIEWER, reset accounts or expand scopes automatically. Any grant
change requires separate operator approval and the existing private interactive CLI.
Separate reviewer remains intact. No CLI audit action was run because it authenticates
and creates security events; directory inspection was strictly SELECT-only.

## Concrete approval package — proposal only

1. Review and approve restricting only the existing Cockpit API host publish:

   ```diff
    cockpit-api:
   -  ports: ["8000:8000"]
   +  ports: ["127.0.0.1:8000:8000"]
   ```

   [Unapplied patch](evidence/nadi-auth-foundation-01/proposed-loopback.patch).
   No database or collector change. Applying a Compose file alone does not change the
   existing container: separately authorized, dependency-free recreation of **only
   cockpit-api** would be necessary. Its entrypoint/config/state/health and consumer
   dependencies must be revalidated first; no broad Compose action. Laptop-local
   processes would still be trusted to reach8000; this trust assumption needs owner
   acknowledgement. A host firewall alternative requires approved network-owner controls.
2. Define approved factual read scope/portfolio entitlement and explicitly decide the
   Development ADMIN read capabilities. Prefer scope-bounded read authority; keep author
   and reviewer permissions separate. No automatic persistent grant change.
3. Implement and test the complete page/API/diagnostic boundary in isolation, reusing
   SessionAuthority. Introduce explicit local-only enablement default OFF outside the
   approved laptop environment. Review its launcher/config integration before activation;
   any required controlled service cycle needs authorization.
4. Run all requested PostgreSQL/session, method/path/scope/cookie/cache/revocation and
   browser tests before claiming acceptance. Preserve the HTTPS origin, credentials,
   all records/sessions, Node pin and single preview. No production/QA activation.

## Tests, limitations and rollback

Actual checks: trusted-CA HTTPS anonymous root200, assets200 and factual proxy200;
anonymous local upstream factual200/health200; listener/Docker port inspection;
read-only firewall policy inspection; PostgreSQL account metadata transaction;
source review of session lease/cookie/revocation/operator/Case ACL and proxy.

No new guard exists, so **global browser E2E, frontend/security regression, build,
PostgreSQL mutation/session qualification and exact-head CI are NOT RUN**. Earlier
FIX02 tests remain historical evidence and cannot prove this new requirement.
No screenshots are presented as proof of a protected dashboard. Documentation links
and `git diff --check` are validated. Graph coverage for current code is missing/stale;
material code was read directly, not inferred absent from the graph.

No runtime rollback is needed: application/config/process/account bytes were not
changed. Existing controller, worktrees and backups remain. Future rollback must
retain session/audit/records, reverse only reviewed code/config and use authorized
controller/recovery procedures; never restore/delete data to force acceptance.

**PO acceptance checklist:** upstream restriction evidence; factual entitlement/scopes;
existing admin and separate reviewer; authenticated root/refresh/logout; anonymous API
and forged cookie/header denial; revocation/cache/cross-asset/self-review; responsive
login and identity/logout shell; explicit local enablement; independent review.

## Final status

TASK: NADI-AUTH-FOUNDATION-01\
STATUS: BLOCKED\
GLOBAL_LOGIN_GUARD: BLOCKED; not implemented/activated\
ANONYMOUS_ROOT: FAILED (current anonymous200, not login-only)\
PROTECTED_PAGES: PARTIAL (existing QA record security only)\
FACTUAL_API_GUARD: BLOCKED\
DIRECT_UPSTREAM_EXPOSURE: BLOCKED; full remote reachability UNKNOWN\
EXISTING_SESSION_AUTHORITY: existing QA authority retained; global integration pending\
ADMIN_ROLE_MATRIX: VERIFIED for directory/operator/Case scopes; broader module ACL audit partial\
DEVELOPMENT_ADMIN_ACCOUNT: EXISTING_VERIFIED\
ADMIN_MODULE_ACCESS: PARTIAL\
INDEPENDENT_REVIEW: PRESERVED, unchanged\
SESSION_LOGOUT_REVOCATION: NOT_RETESTED; existing implementation unchanged\
ACTIVE_PREVIEW: https://localhost:3000\
BROWSER_E2E / FRONTEND_TESTS / BACKEND_TESTS: NOT_RUN; blocked before implementation\
EXISTING_DATA_PRESERVED: YES\
OPERATIONAL_SERVICES_CHANGED: NO\
PRODUCT_OWNER_ACCEPTANCE: PENDING\
PR100_MERGED: NO\
NEXT_ACTION: approve reviewed upstream/network and factual-scope plan, then implement and qualify global guard.
