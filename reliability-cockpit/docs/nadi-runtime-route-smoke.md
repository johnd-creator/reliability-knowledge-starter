# NADI-003A Runtime Route Smoke

## Root cause

The operator runtime was `npm run dev` on port 3000. The generated `.next`
directory contained a mixed/partial App Router build: the root and some pages
could render, while several route server files and the fallback document were
missing. Those routes returned HTTP 500 with `ENOENT`; the sidebar `Link`
definitions were correct and the Mart API was healthy.

The stale generated directory was moved aside locally and `next dev` was
restarted. The Next configuration now uses `.next-dev` for development and
`.next` for production, preventing a production build from sharing output with
the live development server.

## Runtime contract

- Development UI: `npm run dev -- --port 3000`
- Production UI: `npm run build && npm start -- --port 3000`
- Local Cockpit API: `127.0.0.1:8000`
- API proxy: `/api/cockpit/*`
- Mart access: read-only local Reliability Mart

No source collector or corporate endpoint is required for route serving.

## Route smoke

The lightweight smoke command checks direct local responses for `/`, `/assets`,
`/maintenance`, `/fmea`, `/rcfa`, `/asset-health`, `/overhauls`, and
`/data-quality`. It also checks that the root response contains all expected
sidebar hrefs:

```bash
npm run smoke:routes
```

Set `NADI_WEB_BASE_URL` when the UI uses another local port. The smoke command
does not download Mart rows or write test artifacts.

## Regression result

All eight routes must return HTTP 200 after a clean development start or a
successful production build. Existing pages retain their shell and bounded
`ErrorState` when a read API is unavailable; API failure must not remove route
navigation.
