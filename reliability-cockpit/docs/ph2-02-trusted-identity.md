# PH2-02 — trusted identity foundation, not activated

Injected TrustedIdentityProvider verifies assertions and supplies stable Principal,
exact asset scopes, grant version and validity. No production provider/users are
invented. Its guard MUST serialize permission changes with authorized request
commits. SessionAuthority uses shared application SQL sessions, hashed unpredictable
tokens and session-bound CSRF, configurable explicit idle/absolute expiry,
provider revalidation, revocation, exact HTTPS origin checks and secure HttpOnly
SameSite Strict host cookies. No browser role/header authority or dotenv lookup.

A leased PostgreSQL session row and provider grant guard span the isolated API
command. A revocation linearizes before or after an in-flight command, never
silently authorizing a later command. SQLite fixtures do not certify multiprocess
locking. Enterprise adapter atomic guard, verified assertion (issuer/audience/
signature/nonce/state/PKCE if OIDC selected), session policy, proxy and operational
load/timeout behavior require separate review. No public login is mounted.

ADMIN is limited to self/within-scope session revocation and own scoped security
activity; it does not imply AUTHOR or REVIEWER, bypass contributor exclusion,
write Maximo/PI or grant Mart ownership. Case audit remains authoritative for
human record mutations. General security activity includes sanitized session/access events and anonymous
allowlisted denial codes. Denial retention and custodian export remain
an explicit operational audit gap; no secret/assertion/note/body is logged.

ApplicationStore checks explicit database identity and application anchors and
rejects Mart relations; isolated test override is deliberate. Neither identity
metadata nor candidate migration003 is imported by init-db/mart-migrate/startup.
Provider, existing-store writer, reviewed migration runner/ledger/backup, retention,
HTTPS/proxy/quotas and production mounting remain BLOCKED. Rollback disables
mounting and revokes runtime authority; preserve session/audit/record history.
