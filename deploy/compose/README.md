# Reliability Cockpit platform Compose

The platform has two separate deployment modes. Legacy Cockpit sync reads
collector APIs. Canonical NADI routes use a SELECT-only Reliability Mart reader
against the existing Maximo Collector DB. Cockpit has no production Maximo, PI
or PLC credential.

> NADI-PI-RUNTIME-001 proposes managed `cockpit-api` Mart DSN to the existing
> Maximo DB, PI psycopg DSNs, and opt-in migration/worker profiles. Existing
> deployment evidence is [here](../../pi-collector/docs/nadi-pi-runtime-001.md);
> these candidate changes are not a clean-platform acceptance certificate.
> [NADI-RUNTIME-002](../../plans/NADI-RUNTIME-002.md) owns missing actual Mart
> governance schema, projection/init ordering, remaining driver debt and
> external-mode Mart DSN. Historical `7149455` is not blindly cherry-picked.

Reuse the existing project identity, stores, volumes and env files. Preserve
all accepted ignored overrides. The commands below describe deliberately
selected installations; never switch modes or run a broad startup to restart
one existing service. Source credentials stay only in the source collector.

## Mode 1 — external collectors (default for an existing local deployment)

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
PI TimescaleDB, init, and API services. A single leased `pi-worker` is defined
under the opt-in `pi-collection` profile; default startup does not acquire PI.
`pi-maintenance` provides deliberate status/apply migrations after backup.
See [PI operator runbook](../../pi-collector/docs/runtime-migrations.md). It requires the
source-only environment names exactly as implemented:
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
| `pi-api` | serves existing stored PI data without source credentials |
| `pi-migrate` | opt-in maintenance: status by default, deliberate local DDL with `--apply` |
| `pi-worker` | opt-in single leased snapshot owner; cycle plus 300s pause, no automatic history jobs |
| `cems-worker` / `cems-aggregator` | FC03/FC04 polling and separate completed-window aggregation |
| `cockpit-worker` | currently ingests Maximo collector resources and derives KPIs; PI/CEMS API bases are configurable, but their projections are pending |

PI baseline collection uses every registry record with `status: verified` and
`stream_status: ok`; P0/P1 selects priority/cadence/dashboard use only and is
not an access blocker. Do not start managed PI collection if its external
worker is already active.
