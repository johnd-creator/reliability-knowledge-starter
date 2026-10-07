# Reliability Cockpit platform Compose

The platform has two deliberately separate deployment modes. Cockpit legacy
sync reads collector APIs; canonical NADI routes read the existing Reliability
Mart in the Maximo Collector database through `RELIABILITY_MART_DATABASE_URL`.
Cockpit has no production Maximo, PI, or PLC credential.

The current workspace uses **managed mode**, project
`reliability-cockpit-platform`, with `compose.yaml` + `compose.dev.yaml` and
existing volumes. Read root `AGENTS.md` before running setup commands. Reuse
existing databases and env files; do not switch projects/modes or overwrite
`.env.platform` to resume development. The installation examples below are
for explicitly chosen fresh deployments, not a migration procedure.

## Mode 1 — external collectors (alternative deployment)

Use this mode when Maximo, PI, and CEMS collectors already run on the host or
elsewhere. It creates **only** Cockpit's local database/API/worker/web and
never starts a source collector, preventing duplicate source polling. The
current Cockpit worker ingests Maximo collector resources only; PI and CEMS API
bases are configurable, but their Cockpit projections remain pending.

1. Only if absent, copy `.env.platform.example` to `.env.platform`.
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
starts isolated Maximo/CEMS Postgres and their collector workers/APIs plus the
PI TimescaleDB, init, and API services. It includes `pi-registry` (verified/ok registry load) and `pi-worker`
(GET-only snapshot collection every 300 seconds when the pi-collection profile is enabled). PI source
configuration is read only by the worker from `pi-collector/.env`; its
DATABASE_URL is overridden to the managed PI database. The registry YAML
is mounted read-only, outside the application image. It requires the
source-only environment names exactly as implemented:
`CEMS_MODBUS_HOST`, `CEMS_MODBUS_PORT`, `PI_WEB_API_BASE_URL`, and one valid
Maximo authentication mode (`login`, `token`, or `cookie`).

```bash
docker compose --env-file .env.platform up --build -d
```

For development ports for managed internal APIs, add `-f compose.dev.yaml`.

Managed web defaults are Cockpit 3000, Maximo 3001, PI 3002, and CEMS 3003.
Databases are never published. Attach source-network routes/firewall policy outside this file; do
not put a production Maximo, PI, or PLC endpoint on a public Docker network.

## Service responsibilities

| Service | Responsibility |
| --- | --- |
| `maximo-worker` | scheduled GET-only delta sync; operational data is frequent, asset master data is slow |
| `pi-api` | serves the existing PI collector store; `pi-registry` loads the verified registry; `pi-worker` collects snapshots; API has no source credentials |
| `cems-worker` / `cems-aggregator` | FC03/FC04 polling and separate completed-window aggregation |
| `cockpit-worker` | currently ingests Maximo collector resources and derives KPIs; PI/CEMS API bases are configurable, but their projections are pending |

PI baseline collection uses every registry record with `status: verified` and
`stream_status: ok`; P0/P1 selects priority/cadence/dashboard use only and is
not an access blocker. Do not start managed PI collection if its external
worker is already active.

## Existing deployment data and Mart projection

Managed Compose volumes are distinct from the per-project development volumes.
Starting managed mode does not migrate historical data automatically. Back up
active stores and merge existing local data before retiring old volumes; do not
remove old volumes or re-download history from production to fill a new DB.

NADI `/v1/reliability/*` pages read the Reliability Mart, including the governed
asset registry; legacy `/equipment` counts do not prove those pages have data.
`mart-projector` mounts `reliability-data-contracts` read-only for JSON Schema
validation and refreshes local Equipment/Work Order projections every 300
seconds by default, without Maximo access. FMEA/RCFA/health/overhaul historical
records must be migrated separately; the operational projector does not collect
them. Historical local records were restored during the deployment handoff;
no new source discovery was needed. Recheck current population rather than
rerunning that migration by default.

Start newly added services without restarting working source collectors:

```bash
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml up -d pi-registry mart-projector
```

API availability alone does not prove daemon collection. Check `pi-worker`
logs, `/stats`, and recent snapshot `collected_at` timestamps. The PI worker
uses snapshot mode; it does not bypass the off-hours guard for historical
backfills or automatically download historical recorded data.

`pi-auth-check` performs one GET to the configured PI root before worker
startup. A non-200 response prevents daemon startup; do not retry credentials
repeatedly. On HTTP 401, inspect PI_USERNAME/PI_PASSWORD in the local
`pi-collector/.env` (or PI_TOKEN), correct them out of band, then recreate
the check and worker:

**Current handoff (2026-10-07):** the user asked to defer the HTTP 401 issue.
Do not run the following collection-resume command until the user confirms
credentials are ready and requests resumption.

```bash
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml --profile pi-collection up -d --force-recreate pi-auth-check pi-worker
```

Source secrets remain confined to the auth-check and worker, and are never
passed to Cockpit or the PI API. Authentication failure does not hide already
stored snapshots/history; the API continues serving that local data.

The `pi-auth-check` and `pi-worker` services are opt-in under `pi-collection`.
Default `up -d` serves stored PI data without attempting source authentication.
Enable collection only after fixing source credentials and ensuring no other
worker is polling the same PI registry.
