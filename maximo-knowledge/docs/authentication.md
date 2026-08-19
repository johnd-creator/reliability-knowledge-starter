# Authentication Notes

Document authentication behavior without storing secrets.

## Record

- authentication mechanism
- session/token type
- login flow
- token expiration behavior
- required headers
- CSRF behavior if any
- read-only account limitations

## Observed Maximo production flow

The Swagger page requests the OAS document with:

```text
GET /maximo/oslc/oas
```

When unauthenticated, the server redirects to:

```text
GET /maximo/webclient/login/login.jsp?appservauth=true
```

The browser login form submits to `/maximo/j_security_check` with
`j_username` and `j_password`. This flow is documented for manual or
browser-assisted use only. The repository's safety policy prohibits POST
requests against production, so the discovery CLI does not submit this form.
Use an approved read-only bearer/API credential for automated GET discovery.

## Never Store

- username
- password
- access token
- refresh token
- cookies
- session IDs
- private keys

Use placeholders such as:

```text
Authorization: Bearer <REDACTED>
```

## Authentication for the downstream application

The downstream data-fetcher app needs a way to obtain an authenticated session
so it can run unattended. Three strategies are possible; **programmatic login**
is the chosen default here because it needs no administrator action.

| Strategy | Needs admin? | Notes |
|---|---|---|
| **Programmatic login (chosen)** | No | POST `j_security_check` once to obtain a session cookie, then GET only. Works today. |
| API key / Bearer | Yes | Cleanest for automation; needs fix pack ≥ 7.6.1.2 + admin to issue key. |
| Basic Auth | Yes | Needs admin to enable Basic Auth on REST/OSLC + read-only account. |

### Crucial distinction: login POST vs. data mutation

A POST to `/j_security_check` is **authentication** — it establishes a session.
It does **not** create, update, or delete any Maximo business data. The hard
rule of this knowledge base is *no data mutation* (no POST/PUT/PATCH/DELETE to
`/oslc/os/*` or any business resource). A login handshake is compatible with
that intent.

Therefore:

- **This repository's discovery** (`scripts/discover.py`,
  `scripts/session_discover.py`) stays GET/HEAD/OPTIONS only. AGENTS.md forbids
  any POST to production from discovery, so discovery uses an interactive
  browser session where a human logs in manually.
- **The downstream app** (a separate codebase, not bound by AGENTS.md) may
  perform the login POST itself to obtain a cookie, then issue GET-only data
  requests. No business data is changed.

### Programmatic login recipe (for the downstream app)

The downstream app logs in once, stores the session cookie in memory, and reuses
it for GET-only OSLC requests.

1. POST the login form (URL-encoded body) and capture `Set-Cookie`:

   ```text
   POST /maximo/j_security_check HTTP/1.1
   Content-Type: application/x-www-form-urlencoded
   Accept: text/html

   j_username=<READ_ONLY_USER>&j_password=<READ_ONLY_PASSWORD>
   ```

   The response sets session cookies (typically `JSESSIONID`, and on WebSphere/
   Liberty, an `LtpaToken2`). Keep these in memory only.

2. Reuse the cookie on GET-only OSLC requests:

   ```text
   GET /maximo/oslc/os/MXASSET?_maxitems=1 HTTP/1.1
   Cookie: JSESSIONID=<REDACTED>; LtpaToken2=<REDACTED>
   Accept: application/json
   ```

3. Detect session expiry and re-login: a `302` to `login.jsp`, a `401/403`, or
   an HTML login page returned instead of JSON means the session expired —
   repeat step 1.

4. Use a **dedicated read-only service account** (not a human account). Load its
   credentials from a secret manager / env var at runtime.

### Alternatives (if the administrator can enable them)

- **API key** — send as a header (e.g. `apikey: <key>`) or Bearer token; no
  login round-trip. Requires fix pack ≥ 7.6.1.2 and an admin-issued key on a
  read-only account.
- **Basic Auth** — `Authorization: Basic <base64(user:pass)>` on every request.
  Requires the admin to enable Basic Auth on the REST/OSLC layer.

If either becomes available, switch the downstream app to it — it is simpler
than cookie-based login.

### What is never stored

Credentials, cookies, and session tokens are runtime-only. They are never
written to this repository, never logged, and never included in samples or
catalogs. Only placeholders appear in documentation:

```text
Authorization: Bearer <REDACTED>
Cookie: JSESSIONID=<REDACTED>
```

### Build checklist for the downstream fetcher

- [ ] Use a dedicated read-only service account (not a human account).
- [ ] After login, send GET / HEAD / OPTIONS only to business resources.
- [ ] Load credentials/cookies from a secret manager / env var at runtime.
- [ ] Never log or persist credentials, cookies, or Authorization headers.
- [ ] Detect session expiry (redirect to login / non-JSON body) and re-login.
- [ ] Implement a request timeout and conservative rate limiting
      (see `docs/etl-playbook.md`).
- [ ] Sanitize/redact any sensitive or personal fields before storing.
