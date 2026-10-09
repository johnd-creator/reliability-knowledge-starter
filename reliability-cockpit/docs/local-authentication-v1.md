# NADI local authentication V1 — isolated candidate

## Selection and boundary

NADI-E-INTEGRATION-02 selects **local username/password** for initial QA.
Enterprise SSO, Entra registration and OIDC provider provisioning are future options,
not initial-QA prerequisites. Existing enterprise abstractions remain reusable.
This does not authorize real QA/production provisioning, DDL, deployment or activation.
The public application factory has no Engineering/login mount. Only the explicitly
injected development factory and loopback *_test database expose this contract.

LocalIdentityProvider implements the existing trusted directory/guard interface;
SessionAuthority remains the session owner. Login produces a server-side verified
grant, rechecked under the same advisory lock before session establishment. No
request DTO carries authoritative subject, role, asset scope or grant version.

## Account and password semantics

Application migration006 adds nadi_local_account, nadi_local_login_budget and
immutable nadi_local_security_event. It changes no Mart or prior migration bytes.
Normalized ASCII username is trimmed/lowercase, 3–64 characters, unique by database
constraint and serialized creation. Immutable local UUID identifies authorship;
usernames are not copied into accepted evidence as mutable identity.

Argon2id uses argon2-cffi25.1, memory65536KiB/time3/parallelism4 with library-generated
random salts. Passwords are never returned/logged/audited; reset does not reveal the
previous password/hash. Default minimum15 characters, configurable12–128; maximum
256 characters/1024UTF-8bytes, no truncation. Operators must approve and benchmark
runtime parameters/capacity before activation. This policy is independent of PdM
or engineering freshness thresholds.

[Maintained API](https://argon2-cffi.readthedocs.io/en/stable/api.html),
[OWASP authentication guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).

No public seed account, self-registration, startup administrator creation, password
in argv, browser storage secret or operational fixture user. Invalid/absent/disabled/
locked accounts return the same INVALID_CREDENTIALS response. Unknown/disabled
accounts use an ephemeral dummy Argon2 hash with the same parameters; no assertion
of perfectly constant timing. Malformed bodies return sanitized INVALID_REQUEST,
never FastAPI input echoes containing passwords. Infrastructure HTTP/access logs
must not capture request bodies, cookies or query credentials.

## Bounded login and sessions

One global PostgreSQL budget row caps100attempts/60seconds by default; it survives
restarts and applies to known/unknown accounts. Up to4local hashing admissions;
shared try-lock prevents waiting unbounded concurrent hashing. Generic429 can be
returned for overload. Per-account5failures lock300seconds; successful authentication
clears failure state. No per-untrusted-username bucket growth. This conservative
shared limit can degrade availability under attack; separately reviewed ingress
rate limiting is required for real QA. No retries or source calls.

Secure HttpOnly SameSite=strict __Host cookie, explicit idle/absolute session policy,
CSRF token in memory, trusted HTTPS Origin and application/json mutations. Login
uses strict origin/JSON protection before an authenticated session exists; no
cross-origin form or permissive origin fallback. Existing session endpoint exposes
only current server-authoritative directory metadata. Logout revokes the session.

Disable/reactivate, role/scope changes, password reset/change and explicit session
revocation increment grant_version; old sessions never revive. Directory guard
serializes changes with in-flight commands and session establishment across processes.
Password-change-required accounts cannot obtain a usable grant; valid temporary
password returns PASSWORD_CHANGE_REQUIRED. Login with explicit new_password changes
it atomically, invalidates previous versions, and establishes a new session after
revalidation. Password equality/reuse of the current password is denied. No email
reset/recovery or unattended reset exists.

## Operator CLI and administration

`python -m src.qa.users --help` describes a separate, private operator boundary.
Explicit NADI_APPLICATION_ADMIN_DSN and expected DB, operator reference, acknowledgement
and interactive TTY getpass are required. DSN is never printed; SQL parameters are
hidden. No dotenv, Mart fallback or migrations/grants are applied by this command.
All application migrations must already be reviewed/APPLIED.

Actions: bootstrap, create, disable, reactivate, reset-password, grants,
revoke-sessions and audit. Bootstrap accepts only operator-supplied password twice,
only an empty account store; administrator gets only explicitly supplied canonical
asset scopes. Subsequent operations require an authenticated ADMIN and exact current
grant version. New/reset accounts require password change. Admin can assign/revoke
roles/scopes only within their authorized asset scope; simultaneous last-admin removal
is denied. Recovery when all admins are inaccessible requires a separately approved
private operator procedure; no automatic account recovery/SQL shortcut is supplied.

Example shape only (supply private DSN outside argv, never substitute secrets in docs):

```sh
python -m src.qa.users --expected-database <approved_application_db> \
  --operator-ref <accountable_operator> --acknowledge-private-administration \
  --username <chosen_username> --assets <approved_canonical_asset> bootstrap
```

User creation/admin functionality has no public HTTP mutation endpoint or large admin
UI. Immutable security events hold actor/target IDs, action/outcome/time, no passwords,
hashes or session material. Scoped admin inspection is SQL-filtered then bounded
pagination; global/unknown-login events require private security-custodian access.
Application runtime is a privileged service, not per-end-user SQL/RLS isolation.
Existing least-privilege current/history grants include006; DBA/owner separation
and wrong-DB/Mart checks remain mandatory.

## Acceptance / limitations

Isolated tests cover real Argon2id, uniqueness races, failure/lock/rate behavior,
forced password change, reset/disable/grant session invalidation, forged session,
expiry, stale admin, self-review, origin/CSRF, immutable ACLs and wrong database.
Actual HTTPS sockets exercise password→session→inspection→independent review→case
→recommendation→follow-up→logout on disposable PostgreSQL. No production source or
application data is touched. Browser/CI/final full regression are reported in the
integration handoff checkpoint. Local tests are not real QA UAT.

Remaining: reviewed real QA startup/frontend integration, host/TLS/network, dedicated
DB/roles and least-privilege admin credential custody, session/password policy/capacity
approval, storage/scanner, authorized account onboarding, PdM fields, backup/rollback,
UAT and explicit deployment approval. OIDC registration is not in this list.
