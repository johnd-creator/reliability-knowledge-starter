# Reliability Cockpit — Knowledge Consumer Starter

The cockpit is the reference consumer of `reliability-knowledge-starter`
knowledge: it reads verified Maximo/PI knowledge, maps it through
`reliability-data-contracts`, stores a normalized copy in its own Postgres
database, and serves the data over a vendor-neutral API.

It never rediscovers Maximo or PI.

## Modules

```text
src/
├── domain/                 # vendor-neutral domain models (contracts)
├── adapters/
│   ├── maximo/             # GET-only OSLC client + field mappers
│   └── pi/                 # PI Web API placeholder (access not yet verified)
├── services/
│   ├── sync.py             # delta sync (changedate watermark)
│   └── kpi.py              # MTBF / MTTR / availability / PM compliance (+ KpiService)
├── repositories/           # SQLAlchemy store for the cockpit Postgres DB
│   ├── database.py
│   ├── models.py
│   └── store.py
└── api/
    └── app.py              # FastAPI, vendor-neutral endpoints
└── cli.py                  # init-db / sync / kpi / serve
```

## Quick start (sidecar)

```bash
python3 -m venv .venv
.venv/bin/pip install -e .        # installs deps + the `cockpit` console script
cp .env.example .env          # set read-only token; NEVER commit real values
cockpit init-db
cockpit sync                   # pull verified Maximo objects (delta-sync)
cockpit kpi                    # compute + persist MTBF/MTTR/availability/PM
cockpit serve
```

## Web app

```bash
cd web
npm install
cp .env.example .env.local    # COCKPIT_API_BASE=http://127.0.0.1:8000
npm run dev
```

The Next.js app proxies `/api/cockpit/*` to the FastAPI sidecar.

## Docs

- [`docs/source-resolution.md`](./docs/source-resolution.md) — which source
  answers which request
- [`docs/adapter.md`](./docs/adapter.md) — sync architecture & safety rules
- [`docs/kpi.md`](./docs/kpi.md) — reliability KPI formulas and data gaps

## Tests

```bash
.venv/bin/python -m unittest discover -s tests
```

## Safety

Production source systems (Maximo/PI) remain read-only. The client raises on
any non-read-only method and always scopes queries to `siteid="BSR"`.
Credentials are never stored in this repository.