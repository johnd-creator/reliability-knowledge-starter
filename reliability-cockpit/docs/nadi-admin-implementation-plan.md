# NADI Administration — proposed implementation plan

16 Oktober 2026 · main `5af41294745d7eb78eb14f617cacdbc223844564`.
**PROPOSED, NOT AUTHORIZED TO EXECUTE.** Reuse existing identity/session services,
application store and reviewed migrations. No duplicate identity service/database,
new public endpoint or operational administrator capability is introduced here.

Read [readiness/evidence](nadi-admin-readiness-01.md) and
[authorization matrix](nadi-admin-authorization-matrix.md). The sole product roadmap
is [NADI-ROADMAP](../../plans/NADI-ROADMAP.md); ADMIN-01–05 are candidate task slices,
not new product phases or accepted organizational permission mappings.

## Backend prerequisites

Seven grouped API gaps, rated for the potential impact of unsafe future exposure:
**5 HIGH, 2 MEDIUM**. Not current deployed vulnerability findings. Endpoint paths
below are intentionally unspecified until ADMIN-01; do not add routes or map generic
QA proxy paths merely to make an admin mockup functional.

| ID / severity | Missing contract | Minimum proposed DTO / authorization behavior |
|---|---|---|
| AG-01 HIGH | Scoped account directory/list/detail/status | Stable subject; approved username visibility; active/password-change-required flags; grant revision and approved update time. Bounded list items/page metadata; server full-subset scope filter before count/search/paging; exact target checks. No raw ACCOUNT serialization, password/hash, lock budget or credential data |
| AG-02 HIGH | Administration authorization/mount and capabilities | Server derives current principal, allowed actions and deployment boundary, not browser role parameters. Reuse SessionAuthority/provider guard; no anonymous/non-admin fetch. Explicit mount approval; no global authentication activation as side effect |
| AG-03 HIGH | Account/grant/status mutation contract | Explicit action and target, expected target grant revision, request ID, approved reason schema, confirmation/reauth policy. Actor authority from dependency; typed canonical scope; fresh actor and old∪new target checks inside transaction; last-admin/self-change policy, CAS/idempotency and event atomicity. Request ID/revision are untrusted preconditions, never authority |
| AG-04 HIGH | Session metadata inventory / revoke handle | Allowlisted status/created/last-seen/expiry and own-current indicator; opaque non-token identifier for authorized target operation. No cookie/token hash/CSRF/IP/device information by default. Full target scope, version invalidation and stale/replay handling; preserve retained history |
| AG-05 MEDIUM | Sanitized audit presentation | Event reference, approved actor/target IDs, allowlisted action/outcome, authoritative timestamp, restricted scope marker and bounded paging. Separate own application activities from local target-account events. No raw SELECT*, credentials, notes, payloads or global/unknown events in admin view |
| AG-06 MEDIUM | Configuration readiness | Enumerated states and reason codes for auth/session/directory/audit prerequisites, evidence time/scope if actually observed; unavailable/UNKNOWN distinct. No env values, DSN, hostname inventory, keys, SQL roles, policy-edit controls or fabricated security score |
| AG-07 HIGH | Password reset / recovery custody | No browser contract proposed for execution yet. Decide proof/reauth, temporary secret delivery, forced-change/version invalidation, anti-enumeration/rate control, usable-admin continuity and dual-accountable recovery. Existing P reset is not authorization for web reset, self-service email or SQL shortcut |

Future reader DTOs must declare nullability, exact timestamp basis, pagination and
scope limitations. Unknown status cannot become inactive/secure/zero implicitly.
Account directory must represent inactive and change-required accounts explicitly;
`current_grant` returning None is not an account-detail response. Configuration DTO
must not call migration `apply`, grant helpers or operational/source APIs.

Source services currently use JSON roles/scopes and existing migration006; no new
schema is assumed necessary for a bounded reader. If durable admin command receipts,
session handles or audit requirements need schema, propose a separate compatible
application-store migration/approval. Do not reuse Engineering receipts as a generic
admin writer or alter accepted migration bytes. No DB access or DDL is authorized now.

## Pending decisions

All **12 PENDING**. Product decisions do not substitute for security custody or
infrastructure approval. No engineer approval is needed to review this architecture;
the26 independent PdM engineer decisions remain unchanged and ON HOLD.

| ID | Decision needed | Accountable approval / current state |
|---|---|---|
| D01 | Product personas → exact server roles; whether account-grant approver is distinct from Engineering REVIEWER | Product Owner + security authority; PENDING, all mappings PROPOSED |
| D02 | Authenticated Administration exposure/mount boundary and minimal permitted read capabilities | Security authority + Product Owner; PENDING; no global login activation |
| D03 | Account visibility: full-subset scopes, empty/global accounts, multi-scope targets, username privacy, counts/search and organization boundary | Product Owner + security/privacy authority; PENDING |
| D04 | Delegated role/scope authority, self-change denial, sensitive grant approval and reauthentication | Security authority + Product Owner; PENDING; current P rules are not approved browser delegation |
| D05 | Mutation target revision, idempotency/replay, atomic audit, concurrency and last-admin error semantics | Security authority; PENDING |
| D06 | Own/other session metadata, opaque handles, bulk revoke and idle/absolute policy presentation | Security authority; PENDING; no token disclosure |
| D07 | Audit field visibility, actor privacy, retention/custodian access and operator invocation accountability | Security/privacy custodian + Product Owner; PENDING; no export approval |
| D08 | Password-reset custody, usable-admin continuity and separately accountable all-admin recovery/break-glass procedure | Security custodian + authorized operator; PENDING; no automatic recovery |
| D09 | Trusted TLS/proxy/origin boundary and sanitized config-readiness vocabulary | Infrastructure/security operator; PENDING; no environment editing |
| D10 | Application DB owner/runtime separation, least privilege, capacity, backup and rollback evidence for eventual activation | Authorized DB/infrastructure operator; PENDING; source analysis is not live grant attestation |
| D11 | Administration UX/read-only scope, navigation, accessible confirmations and prohibited controls | Product Owner + security reviewer; PENDING; no new reference screenshot supplied |
| D12 | Isolated acceptance dataset/people, release checklist, privacy and separately authorized deployment boundary | Product Owner + security/infrastructure authority; PENDING; tests ≠ rollout |

## Independently reviewable slices

| Proposed task | Scope / prerequisites | Exit evidence and hard stop |
|---|---|---|
| ADMIN-01 | Approve D01–D03/D09 for the first read slice; specify AG-01/02/06 DTOs, authorization/pagination/error schema and mount boundary; resolve other D items before corresponding future slices | Versioned approved contracts and positive/negative test plan, fresh threat review; **no mutation/activation**. Recommended next task |
| ADMIN-02 | Only after reader contract approval: authenticated read-only overview, account list/detail, grants/scope presentation and readiness, reusing V1/source services | Synthetic fixtures and server tests prove no unauthorized fetch/count/IDOR, no secrets, responsive keyboard/light/dark; prohibited actions absent. No runtime promotion implied |
| ADMIN-03 | Separate explicit operation authorization; D04/D05/D08/D10/D11 and AG-03 approved; controlled create/status/grant operations only | Concurrency/CAS/idempotency, fresh authority, old∪new scope, self-change/last-admin protection and atomic history; password reset stays P unless separately approved |
| ADMIN-04 | D06/D07/D08; scoped audit/session metadata and separately approved revoke actions; custody/recovery readiness | No token-bearing URLs, anonymous/global event disclosure, destructive audit cleanup or unapproved recovery; demonstrate invalidation, retention and non-destructive rollback |
| ADMIN-05 | D10/D12; authorized disposable QA security acceptance plus operator preparation | Real PostgreSQL locking/privileges and isolated browser/security regression; explicit PO/security rollout authorization still required before any live change |

First implementable development task is **ADMIN-01**, not a browser list backed by
direct table reads or operator CLI invocation. ADMIN-02 needs an approved server
reader and authorization contract, which do not exist at baseline. A disabled
navigation item or development flag cannot substitute for that contract.

## Future validation and rollback requirements

Use in-memory/pure contracts for early DTO rules and bounded disposable PostgreSQL
for grant/session locking, owner/writer/history ACL and actual concurrency. Synthetic
identities only; never point tests at persistent development or operational stores.
Server cases: unauthorized/expired/revoked/disabled, forged browser authority,
cross-scope/empty/global accounts, pagination/count privacy, stale target revisions,
two simultaneous grants and last-admin changes, replay/conflict, self-grants, Origin/
CSRF/content type, password/reset misuse, denial/audit redaction and ADMIN attempting
independent self-review. Do not claim these new admin cases are implemented today.

UI: no request before authorization; session-expiry clears prior-account responses;
late-response refusal; loading/error/UNKNOWN states; no cached sensitive browser
storage; no source privileges/operational controls; focus/keyboard/responsive and
V1 light/dark checks. Architecture review is not a penetration test or deployment
security certification. Readiness API must itself be protected/redacted server-side.

Future code rollback: disable/unmount only the newly approved Administration
capability through its reviewed release procedure and return to compatible source.
Preserve account/session/audit data and grant versions; never delete records, reset
schema or revive invalidated sessions. DB rollback/recovery and permission changes
need operator approval, backups and a separate plan. This task executes no rollback,
controller command, service restart, account change, SQL or live request.

## Delivery gate

Current deliverables are documentation and a DRAFT PR only. Review-ready architecture
does not grant any D decision. PRD/roadmap/log append-only updates record this fact;
exact-head CI and local verification are reported separately. Stop after delivery.
Next: senior security/product review, then select the first explicitly authorized
Administration slice. No PdM M02/M03/M07, Phase1 policy or production work resumes.
