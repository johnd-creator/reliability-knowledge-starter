# Reliability Cockpit platform Compose

This Compose stack starts the three collectors concurrently while keeping their
databases isolated: Maximo/CEMS use Postgres and PI uses TimescaleDB. The
Cockpit reads collector APIs only; it has no Maximo, PI, or PLC credential.

## First start

1. Copy `.env.platform.example` to `.env.platform` and set passwords plus the
   collector-only source configuration.
2. Start the production-shaped local stack:

   ```bash
   docker compose --env-file .env.platform up --build -d
   ```

3. For development ports for the internal APIs, add `-f compose.dev.yaml`.

Only the Cockpit web port is published by default. Databases are never
published. Attach source-network routes/firewall policy outside this file; do
not put a production Maximo, PI, or PLC endpoint on a public Docker network.

## Service responsibilities

| Service | Responsibility |
| --- | --- |
| `maximo-worker` | scheduled GET-only delta sync; operational data is frequent, asset master data is slow |
| `pi-api` | serves the existing PI collector store; interval/tier worker remains an explicit deployment decision |
| `cems-worker` / `cems-aggregator` | FC03/FC04 polling and separate completed-window aggregation |
| `cockpit-worker` | pulls `maximo-api`, then derives KPIs; never accesses source systems |

PI registry loading and collection profiles are deliberately not auto-started
until verified PI WebIds and P0/P1 sampling policy are approved. See plan 02.
