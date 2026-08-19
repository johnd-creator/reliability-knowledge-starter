# Maximo Collector

Read-only Maximo OSLC collector for site BSR. Auto-login (programmatic
`j_security_check`), GET-only data requests, delta sync via `changedate` /
`statusdate` watermarks, contract-shaped local Postgres store, and a FastAPI
read-only API for consumers such as the reliability cockpit. The verified
`mxapiasset` structure is the preferred equipment source; its additional
scalar fields are retained under `sources.maximo.extra`.

See `AGENTS.md` for safety rules and architecture.

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
cp .env.example .env          # fill MAXIMO_USERNAME / MAXIMO_PASSWORD
docker compose up -d postgres # Postgres on :5434
mxcollector init-db
mxcollector sync              # WO/SR and operational master data
mxcollector sync mxapiasset   # explicit asset baseline/status refresh
mxcollector serve             # http://127.0.0.1:8002 (+ /docs)
```

The dashboard is a separate Next.js process:

```bash
cd web && npm install
MAXIMO_COLLECTOR_API_BASE=http://127.0.0.1:8002 npm run dev
# open http://127.0.0.1:3000
```

## API

Read-only views whose field names follow `reliability-data-contracts`:

- `GET /equipment?changed_since=…`
- `GET /equipment/{asset_id}/status-history`
- `GET /work-orders?changed_since=…`
- `GET /service-requests?changed_since=…`
- `GET /persons?changed_since=…`
- `GET /items?changed_since=…`
- `GET /labor`
- `GET /sync/status`, `GET /health`
- `GET /stats`, `GET /collect-runs`
- `POST /sync/{object}` — trigger one object's sync

Vendor identifiers are quarantined under `sources.maximo`.
The dashboard's sync button only triggers the local collector; business data
requests to Maximo remain GET-only.
