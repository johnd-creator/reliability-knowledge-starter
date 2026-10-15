# NADI-ADMIN-READINESS-01 — Administration readiness

16 Oktober 2026 · baseline main `5af41294745d7eb78eb14f617cacdbc223844564`.
Status: **arsitektur kandidat siap direview; Administration web belum diimplementasikan**.
Analisis source dan dokumentasi saja. Tidak ada izin akun, deployment, migration,
global authentication, atau perubahan runtime dari dokumen ini.

Pasangan otoritatif untuk task ini: [matriks izin](nadi-admin-authorization-matrix.md)
dan [rencana implementasi/keputusan](nadi-admin-implementation-plan.md). Product
roadmap tetap [plans/NADI-ROADMAP.md](../../plans/NADI-ROADMAP.md), Phase 0–5 tetap.
FR-08/FR-09 dalam [PRD](../../PRD.md) dan UI-10/UI-11 dalam
[UI Spec](../../docs/design/NADI-UI-SPEC.md) tetap membatasi aktivasi.

## Metode, sumber dan batas bukti

Verifikasi Tier 2 menggunakan graph lalu source/diff baseline yang tepat. Graph
generation `2026-08-24T09:24:57Z` belum mencakup identity baru; coverage pada path
terkait missing/changed. Seluruh klaim penting berikut diverifikasi langsung,
bukan klaim kelengkapan graph. Scope inventory negatif: router `src/api`, mount
QA/operasional, CLI, layanan identity, proxy/frontend login dan migration terkait.
Tidak menilai runtime, session nyata, DB/grant deployment atau semua container.

| Bukti | Source baseline dan simbol/rentang relevan |
|---|---|
| S01 | [Role / Principal](../src/domain/engineering.py), baris 33–44; tepat AUTHOR, REVIEWER, ADMIN |
| S02 | [LocalIdentityProvider](../src/services/local_authentication.py), 77–298; `authenticate`, `guard`, `_authorize`, `change_account`, `security_events` |
| S03 | [SessionAuthority](../src/services/application_identity.py), 83–412; `establish_verified`, `lease`, `revoke`, `activities` |
| S04 | [Private users CLI](../src/qa/users.py), 24–97; boundary operator, bukan HTTP |
| S05 | [Local login router](../src/api/local_authentication.py), 15–39 dan [session router](../src/api/application_session.py), 9–42 |
| S06 | [QA factory](../src/api/engineering_qa.py), `create_qa_app`; [operational factory](../src/api/app.py), `create_app` |
| S07 | [ApplicationStore](../src/repositories/application_boundary.py), explicit identity/Mart rejection; [privilege audit](../src/repositories/application_access.py), 6–97 |
| S08 | [ApplicationMigrator](../src/repositories/application_migrations.py), checksum/ledger/owner tooling; [003](../application-migrations/003_application_identity.sql) / [006](../application-migrations/006_local_authentication.sql), session/account/security relations |
| S09 | [Enterprise adapter](../src/services/identity_adapter.py), injected verifier/directory; [trust configuration](../src/services/identity_configuration.py), not an OIDC verifier |
| S10 | [CaseService](../src/services/engineering.py), `authorize`, `visible`, `assignment`; [ReviewedRecordService](../src/services/human_records.py), role/contributor exclusion |
| S11 | [Login route](../web/app/(authentication)/login/page.tsx), [layout](../web/app/(authentication)/layout.tsx), [LocalLogin](../web/components/LocalLogin.tsx), [QA proxy](../web/app/api/engineering-qa/[...path]/route.ts), [HTTP client](../web/lib/engineering-http.ts) |
| S12 | [Identity tests](../tests/test_application_identity.py), [adapter tests](../tests/test_identity_adapter.py), [configuration tests](../tests/test_identity_configuration.py), [Engineering tests](../tests/test_engineering.py) |
| S13 | [Local authentication tests](../tests/test_local_authentication.py), [HTTPS login tests](../tests/test_local_login_http.py), [DB privilege tests](../tests/test_application_access.py); disposable PostgreSQL prerequisites |

Historical design references remain scoped: [local authentication V1](local-authentication-v1.md),
[PH2-02](ph2-02-trusted-identity.md), [identity decision](bundle-e-identity.md),
[Engineering threat model](engineering-workspace-threat-model.md). Early descriptions
of an in-memory-only UI/no migration runner predate merged QA foundations; current
S02–S11 take precedence for implementation inventory, without rewriting history or
inferring operational activation. Local credentials are the initial QA choice;
enterprise SSO remains a seam, not a deployed provider or mandatory initial blocker.

## Current capability inventory

Legend: **T** implemented with isolated test evidence; **P** private operator only;
**Q** explicit development/QA mount only; **M** missing web contract; **F** proposed
future capability. Multiple labels describe different dimensions, not readiness scores.

| Capability | State and actual boundary | Evidence / remaining gate |
|---|---|---|
| Username/password login, forced change | T/Q; server directory, Argon2id, normalized unique username, generic invalid-account response, bounded shared budget/lockout | S02/S05/S13; policy capacity and deployment approval separate |
| Own identity/session, logout | T/Q; GET current subject/roles/assets plus local session-bound CSRF, POST logout revokes current session | S03/S05/S12; this is not account directory or session inventory |
| Trusted identity / enterprise seam | T; verifier and serialized directory injected, no production issuer/account provisioning | S09; real verifier/SSO integration is F |
| Create, disable/reactivate, roles/scopes, reset, revoke all sessions | T/P; provider methods with fresh ADMIN grant and target scope checks, invoked through private CLI | S02/S04/S13; not existing browser permissions or public mutation endpoints |
| Initial administrator | P; explicit empty-store bootstrap only, private input and accountable operator | S04; not an Administration button or recovery path; never invoked here |
| Account directory and status views | M/F; no safe list/detail HTTP DTO in reviewed routers | Raw account table is not a DTO; `current_grant` omits inactive/password-change-required accounts |
| Individual session revoke | T service; own or ADMIN full target scope, current grant revalidated; current public QA logout only supplies own token | S03/S05; no browser inventory/revoke-other API or token display authorized |
| Local account security events | T/P; ADMIN full-subset target scope filtered in SQL, bounded 1–100/offset 0–10000 | S02/S04; no web audit reader; anonymous/global events stay custodian-only |
| Application security activity | T service; ADMIN own-subject events, then asset subset check; no public reader | S03; do not generalize to all scoped users' events |
| Independent Engineering review | T/Q; explicit REVIEWER plus exact asset scope and contributor exclusions | S10/S12/S13; ADMIN has no override; QA test is not engineer UAT |
| Application DB boundary / ACL verification | T/P preparation; explicit owner DB, Mart rejection, current/history/ledger ACL checks | S07/S08/S13; no live privileges assessed; no automatic apply/grants here |
| Security configuration overview | M/F; source configuration types/guards exist, sanitized admin status DTO does not | S06/S07/S09; host TLS/password/session/backup readiness UNKNOWN until authorized evidence |
| Account recovery and web resets | M/F; temporary reset via P exists, all-admin recovery has no approved automatic path | Separate custody/security authority; no self-registration/email reset/default accounts |

## Existing trust boundaries

Browser credentials → development-only Next proxy → injected QA login router →
LocalIdentityProvider → SessionAuthority → shared application session store.
Server dependency obtains Principal from a valid session/provider grant; Engineering
services enforce asset/role/contributor rules. Browser role labels are not authority.
POST login requires exact HTTPS Origin and JSON before authentication; protected
mutations also require session-bound CSRF. Cookies are Secure/HttpOnly/Strict,
host-only, Path=/; successful login generates a fresh unpredictable token.

QA factory requires environment development, loopback PostgreSQL `_test` target
and shared service engine. Operational `create_app` does not mount these identity
or Administration routers. Login/Engineering pages and proxy additionally check
development plus explicit QA enablement. These availability guards do not create
API authorization. Factual pages retain current access policy; global enforcement
is unchanged. Do not extend the generic QA proxy as an admin authorization shortcut.

The CLI uses explicit administrative DB identity, applied migration ledger, private
TTY password entry and ADMIN authentication for non-bootstrap operations. It never
loads source credentials, migrates, grants DB roles or bootstraps on startup. Host
access and custody of this privileged DSN are a separate operator trust boundary.
The CLI's required operator reference is used in bootstrap event identity; subsequent
events use authenticated actor ID, not a complete per-invocation operator trail.

Grant changes increment `grant_version`; session validation rejects prior versions,
including after reactivation. This is logical invalidation, not deletion of session
rows. Account/grant changes and their success security events already share the
provider transaction; missing future HTTP revision/idempotency contracts do not
mean this existing atomicity is absent. Provider guard serializes subject changes with session establishment and
authorized commands. **GET session is not DB read-only:** it updates last-seen/CSRF
binding and appends access activity. No such endpoint was called in this audit.

## Candidate Administration information architecture

All five sections are **PROPOSED**, with no new route, component, endpoint or account
operation. Proposed `/administration` is a future route name, not a current link.
Existing navigation remains planned. Reuse NADI V1 navy/green, Bahasa Indonesia,
light/dark, keyboard/focus patterns and contained tables at390/768/1440/1920.

| Section | Intended presentation / minimum safe data | Failure and acceptance boundary |
|---|---|---|
| A — Ringkasan Administrasi | Server-authorized capability/readiness states, auth mode, deployment boundary, directory/audit availability and prerequisites | No health/security score; UNKNOWN/unavailable differs from configured/verified; authorization before fetching |
| B — Akun Aplikasi | Scoped search/paging and detail: stable subject, permitted username, active flag, password-change-required flag, grant revision, approved updated timestamp | No hash, failed-login counters, lock timestamps or credential material by default; account PII visibility requires D03; unavailable is not empty/zero |
| C — Peran dan Lingkup Aset | Exact server role grants and canonical IDs, explicit full scope and proposed changes | No wildcard, fuzzy mapping, source/Mart privilege or optimistic success; mutations disabled until ADMIN-03 approval |
| D — Session dan Riwayat Keamanan | Own-session context; later approved scoped status/event summaries with timestamps and provenance | Never show cookie/token/hash/CSRF/reset material; no events is not no incident; other-user inventory requires AG-04 |
| E — Kesiapan Konfigurasi | Enumerated prerequisites and sanitized reason codes, evidence scope/time when actually observed | No DSN, host inventory, env values or live editing/toggles; no migration/restart/collector/policy controls |

DTO and permission prerequisites are specified in the [plan](nadi-admin-implementation-plan.md#backend-prerequisites).
Catalog data must come from authorized server contracts; synthetic fixtures must
remain explicitly DEMO / QA SYNTHETIC, never a representation of organizational accounts.

## Threat and gap register

Severity below describes potential impact **if a future web capability were exposed
without its contract**, not a demonstrated current public vulnerability or live test.
Seven API gap groups: **5 HIGH, 2 MEDIUM**. Their contract IDs are stable in the plan.

| Threat | Current mitigation and exact limitation | Future required control / gap |
|---|---|---|
| Unauthorized admin page / account enumeration | No Administration route/reader; S05 login failures generic; no directory API | Server authorization before read; generic cross-scope not-found; no search/count leakage, AG-01/02 HIGH |
| IDOR / cross-scope account visibility | S02 mutation checks old∪new target scope subset of actor; account list is absent | SQL filter before paging/counts, stable opaque subject, no partial-overlap visibility, D03; AG-01 HIGH |
| Privilege escalation / forged grants | S02 requires current equal IdentityGrant with ADMIN; S01 typed enum; browser cannot construct trusted grant | Do not accept actor/authority fields; dedicated action contracts; AG-02/03 HIGH |
| Self-admin changes | Private provider permits some ADMIN self-grant changes within scope; no blanket no-self-change rule | PROPOSED deny own role/scope/admin-status mutations; independent approver/custody decision D04; AG-03 HIGH |
| Last-admin lockout | S02 locks admin-safety and checks another active ADMIN before disable/remove ADMIN | Active count is not proof another admin can sign in or recover; reset/lockout and simultaneous target changes need approved usable-admin policy and dedicated concurrency evidence, AG-03/07 HIGH |
| Concurrent grant changes | S02 actor/target advisory locks and fresh actor version serialize writes | No caller-supplied expected target revision or request receipt in `change_account`; no claim of Engineering CAS/idempotency for admin changes, AG-03 HIGH |
| Stale sessions after revocation | S02 version bump; S03 grant recheck/guard; old versions cannot revive on reactivation | Preserve invalidation and in-flight ordering; session inventory/revoke handles and bulk consequences need AG-04 HIGH |
| Session fixation / CSRF / Origin | S03 fresh random login token, hashed stored tokens, stable session-bound CSRF, exact Origin/JSON; S05 login guard | Reuse dependency for new routes, reauthentication decisions and negative tests; never relax cookie flags, AG-02/03 HIGH |
| Sensitive audit disclosure | S02 local events target-scope SQL filtered; S03 own-subject activities only; records contain IDs/action/outcome/time | Distinct sanitized DTOs, actor-ID privacy/retention decisions, inaccessible/global events custodian-only, AG-05 MEDIUM |
| Password-reset misuse / enumeration | P only, TTY secret input, forced change and version invalidation; no unattended recovery | Separate channel/custody, reauthentication, abuse controls and non-echoing API decision; no recovery shortcut, AG-07 HIGH |
| CLI bypass / public mutation exposure | S04 private DSN, expected DB/ledger, ADMIN grant; no browser bridge | Do not call CLI from web or reuse administrative DSN in runtime; audit approved operator invocation if needed, AG-03/07 HIGH |
| Excessive DB privilege / audit tampering | S07 rejects unsafe ownership/membership/ACL drift; S08 separates current from append-only history | Application runtime remains trusted privileged service, not per-user RLS. Owner can tamper; audit/retention/custody and all relevant schemas need operator verification before activation, D07/D10 |
| Configuration/secret disclosure | Existing types validate bounds, no admin readiness endpoint | Allowlisted reason codes/observations only, no env dump or automatic probing; AG-06 MEDIUM |

Full-subset scope does not define an organization/tenant boundary. Empty target scopes
are mathematically contained in every scope and current service accepts empty role/
asset sets. Therefore global/unscoped account visibility and delegation must be
explicitly decided, not inferred from ADMIN or zero asset count. No organization
permission mapping is accepted by this documentation task.

## Verification and disposition

Local hermetic reproduction:27 existing identity/adapter/configuration tests and4
Engineering anti-spoofing/independent-review tests PASS, using in-memory SQLite,
synthetic providers and TestClient only; no PostgreSQL DSN, external network or CLI.
PostgreSQL-local-auth/ACL/concurrency tests were inspected and their unchanged
baseline CI evidence is [backend/frontend PASS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38768396811).
SQLite is not PostgreSQL multiprocess proof. Exact documentation-HEAD CI is recorded
independently on the DRAFT PR; baseline CI is not substituted for it.

Documentation verification checks relative files/anchors, exact role identifiers,
source/route/migration bytes unchanged, original PNGs/workbook preservation, no
credential/session samples, append-only updates and26 engineer decisions unchanged.
No production-security acceptance, penetration test, real user-directory verification,
new browser screenshot or live runtime acceptance is claimed. Deployment state is
UNKNOWN because no runtime/DB/session access is permitted here.

Architecture/matrix READY means review-ready documentation. All12 decisions in the
plan remain **PENDING**, all organizational permissions **PROPOSED**. ADMIN-01 is
the recommended first separately authorized task, not permission to implement now.
M02/M03/M07 remain ON HOLD;26 PdM engineer decisions and Phase1 review/expiry policy
are unchanged. STOP after DRAFT delivery; no Administration functionality activated.
