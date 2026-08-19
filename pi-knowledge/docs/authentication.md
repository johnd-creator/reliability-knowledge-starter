# PI Authentication Notes (verified)

Verified against `https://pivision.plnindonesiapower.co.id/piwebapi`
(read-only probe, 2026-08-14).

## Working mechanism

- **Basic authentication** with a domain account works:
  `PI_USERNAME` = `DOMAIN\user` (NetBIOS domain\user format),
  `PI_PASSWORD` = account password.
- The PI Web API returns `200` with `application/json` for `GET /` using Basic
  auth. No `WWW-Authenticate` challenge is issued on a successful Basic auth
  request.
- A `PI_TOKEN` (Bearer) env var is also supported by the discovery script if a
  bearer token is available instead. Leave `PI_USERNAME`/`PI_PASSWORD` empty in
  that case.

## What the script does

- Credentials are read from `.env` (gitignored) only — never committed, never
  logged, never written to any discovery/sample file (the `sanitize()` helper
  strips token/authorization/cookie/password keys).
- All requests are `GET`/`HEAD`/`OPTIONS` only; any other method raises.
- Network access requires an explicit `--execute` flag.

Never commit credentials, cookies, NTLM/Kerberos artifacts, tokens, or session
data.
