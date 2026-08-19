# AGENTS.md — Maximo Collector

## Mission

Collect verified Maximo OSLC objects (site BSR, org IP) into a local
contract-shaped store and serve them to consumers (the reliability cockpit)
without ever mutating production Maximo.

## Source of Truth

1. Object structures must exist in `maximo-knowledge` with `status: verified`.
2. Verified objects (release 1): `mxapiasset` (preferred equipment source),
   `mxwodetail`, `mxapisr`, `mxperson`, `mxitem`, `mxapilabor`. `mxasset`
   remains available for explicit backwards-compatible runs.
3. Field translation source of truth:
   `reliability-data-contracts/mappings/maximo-to-contracts.md`.
4. If knowledge is missing, add a discovery task in `maximo-knowledge` — never
   guess identifiers in this repo.

## Mandatory Safety Rules

1. **READ ONLY against business data.** Every request to `/oslc/*` is
   GET/HEAD/OPTIONS only; anything else raises `OslcError`
   (`src/adapters/maximo/oslc_client.py`, `READ_ONLY_METHODS`).
2. **The single exception is authentication**: one POST to
   `/j_security_check` per session (programmatic login), prescribed by
   `maximo-knowledge/docs/authentication.md` for downstream apps. Login is
   authentication, not data mutation. It lives in `src/adapters/maximo/auth.py`
   only — the OSLC client guard stays untouched.
3. Never create/update/delete Maximo business data, no POST/PUT/PATCH/DELETE
   to `/oslc/os/*` or any business resource.
4. BSR/IP scope is applied on every query: `siteid="BSR"` for site-scoped
   objects, `worksite="BSR"` for labor, `site="BSR"` for items, and the
   verified org-level `locationorg="IP"` scope for persons.
5. Rate limit 1 req/s and 1 MiB response cap on every request (including
   login).
6. Credentials and session cookies live in memory only — never logged, never
   persisted. `.env` is gitignored.
7. On login failure: raise a clear error. No retry loops (anti brute-force).
8. On session expiry mid-sync: re-login ONCE and retry the page.
9. The collector writes only to its **own** Postgres store.

## Architecture

```text
maximo-knowledge (verified object maps)
      │
      ▼
mxcollector sync ──▶ OslcClient (GET-only, rate-limited)
      │                 ▲
      │        MaximoAuth (POST /j_security_check once, cookie in memory,
      │                 re-login once on expiry)
      ▼
Postgres (contract-shaped: equipment, work_order, service_request,
          person, item, labor, sync_cursor, collect_run)  :5434
      │
      ▼
FastAPI read-only views (contract field names, vendor under sources.maximo)
                                          :8002
      │
      ▼
reliability-cockpit (dashboard — pulls from this API, never touches Maximo)
```

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
cp .env.example .env                    # fill MAXIMO_USERNAME/PASSWORD (read-only account)
docker compose up -d postgres           # Postgres on :5434
mxcollector init-db
mxcollector sync                        # WO/SR + operational master data
mxcollector sync mxapiasset             # preferred equipment object (or: equipment)
mxcollector serve                       # FastAPI on 127.0.0.1:8002
.venv/bin/python -m unittest discover -s tests
```

The optional `web/` Next.js app provides a local BSR dashboard. Its sync
buttons call the collector's local trigger endpoint; the collector still uses
POST only for the prescribed login handshake and GET/HEAD/OPTIONS for Maximo
business data.

## Watermarks

Delta sync per object (mirrors the cockpit engine this project replaced):

| object | watermark |
|---|---|
| mxasset / mxwodetail / mxapisr | `changedate` |
| mxperson / mxitem | `statusdate` |
| mxapilabor | — (full sync each run; small table) |

A row that fails to map is logged and skipped — one bad row never aborts a
sync. Cursors persist in `sync_cursor`; collect runs are logged in
`collect_run` for observability.

## Gotchas

- OSLC records live under the `_member` key (fallbacks `member`,
  `oslc:member`, `rdfs:member`).
- Next-page link is nested under `oslc:responseInfo.oslc:nextPage`.
- Maximo scalars arrive as strings — use the `oslc_*` coercion helpers.
- Session expiry signature: 302 to `login.jsp`, 401/403, or an HTML body
  where JSON was expected.

## Git Rules

```text
feat(auth): add programmatic login
feat(sync): delta sync with changedate watermark
feat(api): contract-shaped views
```

Do not merge, reset, force-push, or rewrite history unless explicitly authorized.
