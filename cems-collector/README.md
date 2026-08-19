# CEMS Collector

Read-only CEMS Modbus TCP collector for stack 1 (PLTU Suralaya, Beijer
Box2Base gateway). Polls 14 emission parameters (SO2, NOx, O2, PM, Hg,
CO2, …) every few seconds via Modbus FC03/FC04 only, normalizes them with
the ported DAZ legacy pipeline (gas conversion, threshold clamp,
maintenance overrides, O2-reference correction), aggregates 5-minute
windows, and serves everything through a FastAPI read-only API. Ported
from the DAZ project and restructured to follow the maximo-collector
architecture; the outbound KLHK/CEMS push was deliberately not ported.

See `AGENTS.md` for safety rules and architecture.

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
cp .env.example .env          # PLC host/port + DATABASE_URL
docker compose up -d postgres # Postgres on :5435
cemscollector init-db
cemscollector load-registry   # stack CB001 + 14 parameters from YAML
cemscollector collect         # continuous polling (or --once for one cycle)
cemscollector aggregate       # 5-minute window aggregation (or --start/--end)
cemscollector diagnose        # read-only probe of every parameter
cemscollector serve           # http://127.0.0.1:8003 (+ /docs)
.venv/bin/python -m unittest discover -s tests   # 81 tests, no network/DB
```

The parameter registry lives in `registry/cems-parameters.yaml`. Entries
are `status: documented` (DAZ production values, register map 3100–3150);
after verifying readings against the live PLC via `diagnose`, flip them to
`verified`. The registry is the only place register numbers exist — the
collector never hardcodes them.

The dashboard is a separate Next.js process:

```bash
cd web && npm install
CEMS_COLLECTOR_API_BASE=http://127.0.0.1:8003 npm run dev
# open http://127.0.0.1:3000
```

## API

Read-only views (vendor-neutral snake_case; Modbus details quarantined
under `sources.cems`):

- `GET /latest` — newest reading per parameter
- `GET /readings?parameter=…&status=…&since=…&until=…` — raw time-series
- `GET /readings/5min?parameter=…&since=…` — aggregates
- `GET /parameters`, `GET /stacks` — registry
- `GET /sync`-equivalents: `GET /stats`, `GET /collect-runs`, `GET /health`
- `POST /collect/once`, `POST /aggregate` — trigger local runs

All list endpoints support `offset` and `limit`. The dashboard buttons
only trigger local collection; requests to the PLC remain read-only.

## Data model

| table | contents |
|---|---|
| `stack` | monitored stacks (port of DAZ `cerobongs`) |
| `parameter` | registry rows; modbus config in `sources.cems` JSONB |
| `reading_realtime` | append-only raw/normalized/final values per poll |
| `reading_5min` | avg/min/max/count per 5-minute window (unique upsert) |
| `sync_cursor` | aggregation watermark |
| `collect_run` | per-run observability (collect + aggregate) |
