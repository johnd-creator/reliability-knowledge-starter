# Existing PI store migration and one scheduler owner

`NADI-PI-RUNTIME-001`, 7 October 2026. The owning managed service remains
`pi-db`, database/user `pi_collector`, project `reliability-cockpit-platform`.
Never create another PI store, reset a volume, truncate history, or migrate PI
measurements into Cockpit/Mart. Read [runtime acceptance](nadi-pi-runtime-001.md).

## Deliberate migration path

`init-db` creates missing tables; it does not upgrade existing columns. Use the
new operator command separately. Its default is read-only status/dry run:

```bash
# DATABASE_URL must already select the verified existing PI owner.
picollector migrate
# Only after private backup/catalog validation, schema inspection and quiescence:
picollector migrate --apply
# Optional explicit SQL directory (container default: /app/migrations):
picollector migrate --directory ./migrations
```

The runner requires PostgreSQL with psycopg, and all six existing PI tables
before apply. It creates no database and imports no PI client/configuration.
Numbered SQL is sorted numerically; duplicate prefixes, invalid names,
checksum/name drift, unknown applied files and non-prefix history fail loudly.
`public.pi_schema_migration` records number, filename, SHA256 and applied time.
Each file and its ledger record commit in one transaction. A failed file rolls
back; earlier successful files remain recorded, later files do not run. Repair
the cause and rerun the unchanged reviewed files; do not edit applied checksums
or fabricate ledger records to bypass a failure.

There was no ledger in this deployment. Initial execution deliberately replays
001–003's existing `IF NOT EXISTS` DDL, verifies the existing Timescale hypertable,
and records that guarded execution. Guarded DDL may also create missing indexes;
review existing indexes and allow for bounded index-build cost before bootstrap. This is not a claim that historical DDL had
never run. Subsequent executions skip recorded files. Migration 004 remains the
unchanged reviewed merged-main SQL. Its outer transaction is handled by the
runner, not nested inside a runner transaction.

Apply takes a session advisory lease, shared with the managed worker, and uses
`lock_timeout=5s`, `statement_timeout=30s` **per file**. Stop only PI acquisition
and, when necessary, PI API/manual source triggers before DDL. Existing quality
columns must have the expected nullable type/length and no default; otherwise
004 stops without forcing/retyping them. Nullable columns without defaults are
expected to avoid historical-row rewrites ([PostgreSQL 16 DDL](https://www.postgresql.org/docs/16/ddl-alter.html)).
Old `source_value` stays null; never reconstruct lost source evidence from the
legacy numeric field. A Timescale integration test and real-store pre/post
fingerprints verify compatibility; SQLite tests alone are insufficient.

## Compose operator and worker

Candidate source-controlled managed Compose contains `pi-migrate` under
`pi-maintenance`, status-only by default, and `pi-worker` under `pi-collection`.
Both reuse the PI DB. **Managed configuration comes only from `.env.platform`**;
worker receives explicit source URL/auth/timeout/rate/cap/TLS substitutions.
No managed `env_file` references `pi-collector/.env`. `PI_CONFIG_MODE=managed`
skips collector/home dotenv loading. Standalone development retains those files.
PI API gets the same non-secret pause metadata for /schedule; API, migration
and Cockpit receive no PI source credentials. Existing runtime may contain
ignored image/DSN overrides. Include **every accepted override**, including the
Maximo WO runtime pin, in each command. Never issue a broad `up`, `down -v`, or
switch deployment project/mode as part of this upgrade.

For an already reviewed image containing the new commands, reuse the same
Compose argument list and execute only:

```bash
# Append existing accepted -f overrides to these examples before execution.
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml --profile pi-maintenance run --rm --no-deps pi-migrate
# After backup + schema preflight + stopping acquisition/API as needed:
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml --profile pi-maintenance run --rm --no-deps pi-migrate picollector migrate --apply
# After stored API acceptance and one known-attribute live canary PASS:
docker compose --env-file .env.platform -f compose.yaml -f compose.dev.yaml --profile pi-collection up -d --no-deps --no-build pi-worker
```

The accepted deployment in this task uses the exact merged-main PI image,
plus private read-only operator/lease modules from this PR. Merged-main does
not yet contain the new CLI. See the acceptance report for its exact overlay
and operator commands; do not assume this candidate image was deployed.

Worker mode is snapshot only. It holds one DB session lease; another managed
worker or migration cannot acquire it. It forwards SIGTERM/SIGINT and stops its
child if the owning DB connection fails (checked every 5s between child waits).
Disable existing cron/systemd/manual collectors first. Legacy `run`, manual
collection/backfill and API source triggers are outside this lease: it is not
a global cross-process collector lock. API has no live source configuration in
this deployment. Heavy history/backfill is not enabled by either profile.

`PI_SNAPSHOT_INTERVAL_SECONDS` is retained compatibly as **post-cycle pause**.
Preferred CLI `--pause-seconds` and legacy `--interval-seconds` are aliases;
without an explicit flag both read that environment value (default 300).
Cadence is **one serial snapshot cycle plus a 300s pause**, not a fresh cycle
starting every five minutes; 433 streams at a minimum 1s/request take longer
than five minutes. Measured first cycle 508.142s + 300s pause gives estimated
808.142s (~13.5m) start-to-start, not a fixed five-minute cycle. Request spacing
and serial polling remain unchanged. Merged-main's cycle timeout is 1800s. `restart: no` makes
exit visible for operator intervention and avoids container crash retry loops.
The existing snapshot loop itself does not abort immediately on a later 401;
stop the owner on authentication/transport incident before repairing access.
A one-request auth canary gates initial activation. Do not silently enable
recorded-delta/history, relax TLS/auth/origin caps, or run parallel schedulers.

## Schedule and freshness interpretation

The API's `next_run_at` is an estimate of acquisition **start** at latest cycle
completion + configured pause; its old `interval_seconds` means pause.
Duration/pause/effective-cadence fields are separate and null duration does not
invent an effective cadence. Recent writes indicate activity, not a lease or
process certificate. A just-completed cycle is waiting through its pause, not
still collecting. Countdown does not promise fresh data at zero; UI says to
wait for observed activity if the estimate has passed.

`last_run_at` is completed-cycle time, possibly partial/failed. Determine latest
successful collection from persisted run outcome (rows/errors/aborted) separately
from individual source timestamps. A source value can remain stale even after a
successful collection; the accepted epoch-timestamp canary illustrates this.
Future NADI-INTEGRATION-STATUS must keep these dimensions distinct. No SLO,
all-signal freshness classification or new scheduler is introduced by FIX-01.

## Backup and recovery

Keep full `pg_dump -Fc` archives private (directory 0700, bytes 0600), record
versions/checksum and validate `pg_restore --list`. This deployment retains its
archive under the original checkout's ignored `secrets/backups/`.

First preference after an application regression is to stop only PI worker and
return PI API to its prior image while leaving additive evidence columns and
history intact. No downgrade/drop migration is provided. For actual corruption,
restore only after a separately reviewed recovery plan protects all newer data:
use matching PostgreSQL/Timescale versions, enable Timescale, call
`timescaledb_pre_restore()`, perform serial `pg_restore`, then call
`timescaledb_post_restore()` and verify counts/cursors/chunks before switching.
Do not overlay an old archive onto the running store or automatically create a
second production DB. A disposable isolated recovery environment may be used.
Full catalog validation is not a restore drill. See the
[official Timescale logical-backup procedure](https://github.com/timescale/Tiger-Data-Docs/blob/main/src/content/docs/deploy/self-hosted/backup-and-restore/logical-backup.mdx).
