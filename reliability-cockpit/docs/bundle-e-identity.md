# E2 — enterprise identity decision and trust readiness


**NADI-E-INTEGRATION-02 selection:** local username/password is initial QA auth.
Enterprise SSO/Entra/OIDC registration is an optional future path, not an initial
activation prerequisite. Local account custody/onboarding and existing host/DB/
TLS/storage/PdM/UAT/explicit deployment gates remain. See local-authentication-v1
and the final integration report; historical enterprise-specific evidence below
remains reusable, not initial-QA authorization.

No provider is selected or contacted. No registrations, credentials or accounts
are created. Test proofs belong only to fixtures. Production identity readiness
remains REQUIRED_OPERATOR_INPUT.

| Option | Trust integration | Decision prerequisite |
|---|---|---|
| Existing enterprise OIDC (including Entra) | Reviewed server authorization-code client, PKCE, JWKS signature validation | Tenant/issuer/client ownership, lifecycle and MFA approval |
| Existing SAML broker → OIDC | Broker trust and reviewed OIDC seam | Federation/security owner; no handwritten SAML parser |
| Existing trusted enterprise gateway | Cryptographically verified assertions, no unsigned X-Actor/header trust | Gateway signature audience/replay contract and key rotation |
| Local fixture verifier | Disposable tests only | Never real QA authority |

OIDC validation must bind exact issuer, approved audience/client and asymmetric
algorithm; verify signature/key rotation, expiry/not-before, nonce/state, PKCE and
one-use authorization response before deriving subject. Stable identity uses
verified issuer + subject, not mutable email/display name. OIDC configuration is
a contract, NOT a verifier. See [OIDC Core](https://openid.net/specs/openid-connect-core-1_0.html)
and [Entra OIDC](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc).
Provider SDK, discovery origin, JWKS/cache/rotation, redirect and token exchange
require a reviewed integration; no network in source-free tests.

Exact HTTPS redirect and post-logout URIs use the approved browser origin.
Server stores state/nonce/PKCE context; browser cannot provide principal/roles.
Session uses Secure HttpOnly __Host cookie, Path=/, SameSite=Strict, no Domain;
CSRF + exact Origin required for application writes. OIDC callback state is an
independent login-CSRF defense; validate provider-specific callback compatibility
with SameSite, without relaxing cookies automatically.

Durable directory owns AUTHOR/REVIEWER/ADMIN and explicit canonical asset scopes.
Role assignment is separately audited; no wildcard scope, email-based authority
or IdP groups silently mapped. Independent reviewer cannot approve own or previous
contribution. Directory guard and deprovisioning serialize grant revision with
authorized commits; version change/revocation denies existing sessions.

Admin recovery: two accountable administrators, reviewed break-glass scope/time,
separate activity audit and immediate revocation. Do not seed hardcoded users.
Local logout revokes SQL session first; IdP logout/front-channel/back-channel
semantics must be approved. Provider outage is unavailable, never anonymous.

Session/connection/provider policy values are explicit operator engineering input;
configuration bounds are safety caps, not approved production defaults.
No source policy/credential is inherited. Pool max_overflow=0, connect/statement/
lock timeouts, bounded async lease admission and cancellation-safe cleanup are
required. The statement/lock ceiling helper is a test/preparation limit, not SLA.

Proposed labels authorized by operator: nadi-qa, nadi_qa_application,
nadi_qa_owner, nadi_qa_writer, nadi_qa_runtime. example.invalid remains placeholder,
not an approved DNS/host. IdP, real TLS/storage/scanner and UAT people are undecided.
