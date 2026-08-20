# Reliability Cockpit platform Compose

The platform has two deliberately separate deployment modes. The Cockpit always
reads collector APIs only; it has no Maximo, PI, or PLC credential.

## Mode 1 — external collectors (default for an existing local deployment)

Use this mode when Maximo, PI, and CEMS collectors already run on the host or
elsewhere. It creates **only** Cockpit's local database/API/worker/web and
never starts a source collector, preventing duplicate source polling.

1. Copy `.env.platform.example` to `.env.platform`.
2. Set `COCKPIT_DB_PASSWORD` and the three `*_COLLECTOR_API_BASE` values.
   For host-local collector APIs from Docker on Linux, use
   `http://host.docker.internal:800{1,2,3}`; the file supplies the required
   `host-gateway` mapping.
3. Start external mode:

   ```bash
   docker compose --env-file .env.platform -f compose.external.yaml up --build -d
   ```

## Mode 2 — managed collectors

Use this only when no existing worker polls the same source. `compose.yaml`
starts isolated Maximo/CEMS Postgres and PI TimescaleDB plus collector workers
and APIs. It requires the source-only environment names exactly as implemented:
`CEMS_MODBUS_HOST`, `CEMS_MODBUS_PORT`, `PI_WEB_API_BASE_URL`, and one valid
Maximo authentication mode (`login`, `token`, or `cookie`).

```bash
docker compose --env-file .env.platform up --build -d
```

For development ports for managed internal APIs, add `-f compose.dev.yaml`.

Only the Cockpit web port is published by default. Databases are never
published. Attach source-network routes/firewall policy outside this file; do
not put a production Maximo, PI, or PLC endpoint on a public Docker network.

## Service responsibilities

| Service | Responsibility |
| --- | --- |
| `maximo-worker` | scheduled GET-only delta sync; operational data is frequent, asset master data is slow |
| `pi-api` | serves the existing PI collector store; interval/tier worker remains an explicit deployment decision |
| `cems-worker` / `cems-aggregator` | FC03/FC04 polling and separate completed-window aggregation |
| `cockpit-worker` | pulls configurable collector APIs, then derives KPIs; never accesses source systems |

PI baseline collection uses every registry record with `status: verified` and
`stream_status: ok`; P0/P1 selects priority/cadence/dashboard use only and is
not an access blocker. Do not start managed PI collection if its external
worker is already active.
