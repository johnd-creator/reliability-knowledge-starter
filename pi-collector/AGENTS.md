# AGENTS.md — PI Collector

## Existing deployment and consumers

Read `../AGENTS.md` first. Reuse the managed `pi-db` / database `pi_collector`
/ volume `pi-db` in Compose project `reliability-cockpit-platform`.
The old per-project host port 5433 and `.env` DSN may point to a stopped legacy
store; do not start another DB or source worker. Never overwrite existing env
files with examples. API default port is 8001; managed web default is 3002.

**NK has no DB**: it reads our stored `/attributes` and `/snapshots` through
the API. It must not receive source credentials, read production PI directly,
or trigger collection. Cockpit's PI ingestion projection is still pending;
a configured API base is not evidence that it is implemented.

Operational handoff (2026-10-07): source authentication returned HTTP 401 and
the user asked to skip it until they check credentials. Keep `pi-auth-check`
and `pi-worker` (profile `pi-collection`) disabled until the user requests
resumption. Do not retry credentials or backfill to compensate for stale data.
The API remains usable for stored history; show freshness honestly.

`pi-registry` is a one-shot local loader of verified/ok entries, not a daemon.
The managed worker reads `pi-collector/.env` source settings but its DB URL is
overridden to `pi-db`. Confirm no other worker polls the same registry before
enabling collection. All default standalone commands below require reconciling
their DB target and worker ownership with the root deployment first.

## Mission

Collect verified PI Web API time-series data into a local store and serve it
to multiple consumers (trending dashboards, ML pipelines, reliability cockpit)
without ever mutating production PI.

## Source of Truth

Before introducing a PI tag, WebId, or attribute into the collector:

1. The attribute **must** exist in `pi-knowledge` with `status: verified`.
2. The registry YAML (`../pi-knowledge/mappings/bsr1-parameters.yaml`) is the
   sole input for technical collection — never hardcode WebIds in collector
   code. A technical registry entry is not a governed NADI Asset signal.
3. If an attribute is missing, create a discovery task in `pi-knowledge` first.
4. Do not guess production identifiers.

## Mandatory Safety Rules

1. **READ ONLY.** Never execute POST, PUT, PATCH, DELETE, MERGE, or any
   state-changing request against PI production.
2. Never create/delete/update PI Points, AF Elements, Attributes, analyses,
   event frames, or configuration.
3. Never brute-force WebIds, tag names, or authentication.
4. Respect server rate limits (default 1 req/s).
5. Never store credentials, cookies, NTLM/Kerberos artifacts, tokens, or
   session data.
6. The collector writes only to its **own** Postgres/TimescaleDB store.

## Architecture

```text
pi-knowledge (registry YAML)
      │
      ▼
load-registry ──▶ pi_attribute_registry (Postgres)
                        │
collect-snapshots ──────┤  ◀── PiClient (GET-only, rate-limited)
backfill ───────────────┤
backfill-recorded ──────┤  (off-hours gate + circuit breaker + chunking)
run (daemon) ───────────┤
                        ▼
              pi_snapshot + pi_timeseries (TimescaleDB hypertable)
                        │
                        ▼
              FastAPI (read-only views for consumers)
```

## Commands

```bash
picollector init-db              # create tables + hypertable
picollector load-registry        # load verified attributes from pi-knowledge YAML
picollector collect-snapshots    # fetch current values for all active attributes
picollector backfill --start "*-7d" --end "*" --interval 1h
picollector backfill-recorded --start "2024-01-01T00:00:00Z" --end "*"  # heavy, off-hours only
picollector run --mode snapshot --interval-seconds 300  # continuous daemon
picollector serve                # FastAPI on 127.0.0.1:8001
```

## Bulk Download Safety (non-negotiable)

`backfill-recorded` downloads every raw archived point and is the highest-risk
operation for the shared PI server. These guardrails are enforced IN CODE and
must not be weakened without explicit authorization:

1. **Off-hours gate** — `backfill-recorded` refuses to run outside
   22:00–06:00 local time (weekends allowed all day). `--force` overrides it;
   never use `--force` during business hours on production PI.
2. **Circuit breaker** — max 5000 API requests per session, then a clean abort.
3. **Consecutive-error abort** — 10 failures in a row aborts the run (PI may be
   down or rate-blocking us; hammering it further risks an account ban).
4. **Chunking** — long ranges are split into 7-day windows so each request is
   bounded and progress is committable.
5. **Pause between attributes** — 2s cooldown after each attribute.
6. **Rate limit + size cap** — every request is ≥1s apart, responses capped at
   1 MiB (enforced in `PiClient.request`).
7. **Idempotent resume** — upserts by (attribute_id, timestamp). After any
   abort, re-running the same command resumes; NEVER retry with a fresh table.

Standalone scheduling templates (systemd units + cron in `deploy/`) support
night/weekend runs. Their presence does not prove they are enabled. Inspect
the current runtime before using them; never enable them alongside a worker
polling the same registry. The in-app off-hours gate stays active.

## Gotchas

- PI pagination links (`Links.Next`) may be absolute URLs; `iter_recorded()`
  validates scheme/host/port against the configured PI origin before using the
  link. Foreign origins must be rejected so credentials cannot be forwarded.
- `recorded-delta` run mode tracks its cursor in `pi_collect_cursor` keyed
  `recorded-delta`; do not reuse that scope name for other purposes.
- The heatmap endpoint uses `date_trunc('day', ...)` — TimescaleDB accelerates
  this on the hypertable, plain Postgres will be slow on large datasets.

## Git Rules

Use small, focused commits:

```text
feat(collector): add snapshot collection
feat(api): add timeseries endpoint
fix(client): handle PI digital state values
```

Do not merge, reset, force-push, or rewrite history unless explicitly authorized.
