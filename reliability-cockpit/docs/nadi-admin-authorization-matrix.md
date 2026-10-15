# NADI Administration — candidate authorization matrix

16 Oktober 2026 · source baseline `5af41294745d7eb78eb14f617cacdbc223844564`.
**PROPOSED organizational mapping; no new permission granted.** This distinguishes
existing enforcement from future product intent. Role combinations are explicit
unions of grants, never inheritance. Personas such as Reliability Manager/System
Administrator are not automatically mapped to server roles.

[Architecture/evidence catalog](nadi-admin-readiness-01.md#metode-sumber-dan-batas-bukti)
provides S01–S13. [Decisions D01–D12](nadi-admin-implementation-plan.md#pending-decisions)
require Product Owner/security/operator review; engineer PdM gates are separate.

## Server roles and enforcement dimensions

Exact existing enum: AUTHOR, REVIEWER, ADMIN ([S01 source](../src/domain/engineering.py)).
There is no AUDITOR, SUPERADMIN, RECIPIENT or SECURITY_CUSTODIAN enum. Recipient
eligibility belongs to the authorized Advisory record workflow; do not create a
role mapping by naming a persona. Custodian below describes private operational
responsibility, not an application role.

All granted roles require a current trusted server identity/session. Scope is an
explicit set of canonical asset IDs, maximum1000 in the existing grant checks;
syntactic scope validation does not certify Registry membership. Engineering
catalog checks governed membership separately. No wildcard or name-based mapping.
ADMIN does not imply AUTHOR, REVIEWER, DB owner, source operator or Mart writer.

## Existing enforcement — not new browser permissions

Y = available through stated boundary when all guards hold. N = not granted by
that role alone. SERVICE = internal method, not an existing web endpoint. P =
private CLI only. Q = injected development/QA HTTP route. M = missing web contract.

| Capability | AUTHOR alone | REVIEWER alone | ADMIN alone | Actual boundary and constraints |
|---|---|---|---|---|
| View own identity/session | Y/Q | Y/Q | Y/Q | S03/S05 current session only; server subject/roles/assets, local CSRF resume; not account status directory |
| Logout own session | Y/Q | Y/Q | Y/Q | Current token, Origin/CSRF/JSON; preserves audit/history |
| View directory/status of other accounts | M | M | M | No list/detail DTO or HTTP reader; not granted by direct table access |
| Create account | N | N | Y/P | S02/S04 fresh ADMIN IdentityGrant; requested scope ⊆ actor scope; normalized username/explicit password; no web operation |
| Disable/reactivate account | N | N | Y/P | Existing and requested target scopes union ⊆ actor scope; current grant; active-admin safety when disabling ADMIN |
| Assign/revoke roles | N | N | Y/P | Only existing enum, fresh actor; target scope and last-admin checks; not an organizational delegation approval |
| Assign/revoke canonical asset scopes | N | N | Y/P | Full old∪new subset; no automatic Registry validation by directory; no implied source privilege |
| Revoke own current session | Y/Q | Y/Q | Y/Q | S05 logout, not a session-management API |
| Revoke another individual session | N | N | Y/SERVICE | S03 `revoke` needs current target grant and full asset subset, internally receives token; no inventory/opaque handle HTTP contract |
| Revoke all target sessions via grant version | N | N | Y/P | S02 `change_account(revoke=True)` logical invalidation; affected session rows preserved |
| Reset another account password | N | N | Y/P | Explicit temporary secret, forced change, grant version bump; no browser reset/recovery API |
| Change own password during authenticated credentials flow | Y/Q | Y/Q | Y/Q | Existing login `new_password`, valid old credential, policy/reuse check, fresh session; not forgotten-password recovery |
| Read application security activities | N | N | Y/SERVICE | S03 only own-subject and within actor assets; not organization-wide audit; no reader router |
| Read local account security events | N | N | Y/P | S02 target accounts full-subset SQL before bounded paging; global/unknown target events excluded |
| Inspect deployment security configuration | M | M | M | S09 config types/S07 private tooling are not authenticated web status DTOs |
| Author/update Engineering records | Y/Q with ownership | N | N | S10 AUTHOR plus asset scope and creator/assignment restrictions; no ADMIN override |
| Independent Engineering review | N | Y/Q if independent | N | Explicit REVIEWER, asset scope, workflow state and exclusions; ADMIN+REVIEWER still cannot review own contribution |
| Bootstrap first administrator | N | N | N | Separate P empty-store operator action; not a role permission or recovery method; never available from browser |
| Global anonymous/denial audit or all-admin recovery | N | N | N | Restricted private custody procedures; not a supported browser capability |
| Maximo/PI/CEMS/Mart writes or collector controls | N | N | N | Outside application roles and Administration scope, no grant inheritance |

S02 `_authorize` demands the current **entire IdentityGrant**, not an ID/role copied
from a request. Status/grant/reset/revoke changes increment target `grant_version`;
S03 revalidates it under provider guard. Reactivation does not restore old sessions.
Future API must preserve this without returning or editing security tokens.

Existing last-admin check counts another **active ADMIN**, not password usability
or proven recovery authority. Existing private ADMIN self-changes are not generally
forbidden. Current mutation methods have no expected target revision/request receipt
argument. Do not claim a no-self-grant policy, usable-admin guarantee or admin CAS
already exists; these are D04/D05/D08 and AG-03/07 prerequisites.

## Candidate product permissions — all PROPOSED

No permission names below are new implemented enums/scopes. They are requirement
labels for review and tests. Default deny applies until an approved server contract.

| Proposed product capability | Proposed eligibility / constraint | Required decision |
|---|---|---|
| Self identity/session | Existing authenticated identity, current session only; no expansion to directory | D01/D02 |
| Administration overview/readiness | ADMIN with explicit deployment authorization; server-redacted allowlist | D02/D09 |
| Scoped account list/detail | ADMIN, full target scope containment and explicit handling of empty/global accounts; SQL filter/count/paging before response | D03 |
| Create/status/grant changes | ADMIN plus explicit delegated authority and reauthentication; old∪new scope, expected revision, idempotency/audit; own role/scope/admin-status changes proposed denied | D04/D05 |
| Independent approval of sensitive grants | Separately approved authority and distinct actor; existing REVIEWER is **not** automatically an account-grant approver | D01/D04 |
| Sessions list/revoke | Own-only metadata first; ADMIN target access only after scoped opaque-handle contract; no raw token/hash or IP/device data by default | D06 |
| Local security event view | Approved sanitized target-scoped events; own application activities remain separate; anonymous/global events restricted to custodian | D07 |
| Password reset/recovery | Keep P only until separate approved custody/abuse/recovery protocol; no public reset or email distribution implied | D08 |
| Engineering review | Preserve existing REVIEWER/independence rules unchanged; cannot be overridden by Administration or PO role label | Existing S10; organizational mapping D01 |

Server denies unauthenticated, stale, disabled, wrong-role and cross-scope access
before records, counts or target existence are exposed. Frontend hidden/disabled
controls improve UX but never enforce authority. No request may supply authoritative
actor, effective permissions, asset scope or grant version for authentication.
Expected target revision is a concurrency precondition, not authority to grant it.

## Required authorization test matrix for future implementation

Positive: current permitted ADMIN can read only authorized records; exact delegated
change succeeds once and emits permitted audit; distinct eligible reviewer can review
Engineering; own session remains readable and logout works.

Negative: anonymous and every single wrong role; forged role/subject/scope; partial
scope overlap, empty/global target ambiguity, guessed subject/handle, count/search
enumeration; stale actor/target revision; concurrent grant and last-admin changes;
self-grant policy; missing/foreign Origin, missing/forged/cross-session CSRF;
revoked/expired/disabled identity; receipt replay/conflict; secrets/error leakage;
reset misuse; ADMIN self-review and attempted source/Mart privilege expansion.

These are acceptance requirements, not tests claimed executed by this docs task.
Current reproduction and PostgreSQL evidence limits are in the architecture report.
