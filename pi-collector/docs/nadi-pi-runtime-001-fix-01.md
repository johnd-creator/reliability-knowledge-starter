# NADI-PI-RUNTIME-001-FIX-01 — managed configuration and truthful cadence

Status: **PASS — ready for final senior review of existing PR #15**.
Branch stays `codex/nadi-pi-runtime-001`; previous reviewed HEAD
`851bdca6a46bc05a0bc6bb90e1338b26585deee8`. Final HEAD is the commit containing
this correction; PR #15 stays open/unmerged. No new PR or production redeploy.

## Configuration correction

Candidate `pi-worker` formerly used `env_file: [./pi-collector/.env]` alongside
platform env. It now receives explicit `.env.platform` substitutions only:

- PI_WEB_API_BASE_URL, PI_USERNAME, PI_PASSWORD, optional PI_TOKEN;
- PI_TIMEOUT_SECONDS (30), PI_RATE_LIMIT_SECONDS (1.0),
  PI_MAX_RESPONSE_BYTES (1048576), PI_VERIFY_TLS (1);
- PI_SNAPSHOT_INTERVAL_SECONDS (300): compatibility name for **post-cycle pause**.

These are actual PiApiConfig/snapshot timing inputs. Snapshot has an existing
1800s CLI cycle timeout. Bulk backfill/off-hours/per-attribute pause settings are
not blindly forwarded: the managed worker is snapshot-only and does not use
those backfill controls. Source client minimum 1s spacing, same-origin,
streaming 1MiB cap and TLS/auth behavior are unchanged.

`PI_CONFIG_MODE=managed` makes PI entrypoints skip `pi-collector/.env` and
`~/.pi-collector.env` entirely. Local standalone development keeps both files.
PI init/API/migrate have managed mode as well; API receives only the non-secret
pause for schedule metadata. PI source URL/auth/timeout/rate/cap/TLS go only to
worker; API/migrate/Cockpit remain free of PI source configuration/credentials.
No credentials were read/copied/printed in this fix. A clean managed deployment
requires only `.env.platform`, not another collector dotenv file. Actual private
runtime from the accepted operation remains unchanged; historical dotenv use
is preserved as provenance, not presented as the corrected deployment contract.

## Cadence and /schedule audit

Measured accepted first cycle remains **508.142s**. Daemon acquisition stays
serial followed by `time.sleep(pause)`. Configured pause 300s means expected
start-to-start **808.142s (~13.5 minutes)**, not a 300s fixed-rate start.
`PI_SNAPSHOT_INTERVAL_SECONDS` is retained without changing old environment
files. Preferred CLI `--pause-seconds` and old `--interval-seconds` are aliases;
without an explicit option worker/run read that environment value, default 300.
No parallel workers, source-request acceleration or backfill were introduced.

Existing backend countdown already used cycle **completion** + configured
pause; audit confirmed it did not use cycle start + 300. Its old UI labels and
cron-equivalence comments were misleading. FIX-01 removes those claims:

- `next_run_at` estimates next acquisition **start**, never fresh-data arrival.
- `interval_seconds` stays a compatibility alias; additive `pause_seconds`,
  `last_cycle_duration_seconds`, `effective_start_to_start_seconds` and
  `latest_collection_activity_at` distinguish timing dimensions.
- No known duration means null estimated effective cadence, not an invented rate.
- Fresh writes after the last completed cycle imply activity; writes belonging
  to a just-completed cycle no longer keep the UI incorrectly “running” for 90s.
- UI labels show post-cycle pause and estimated start. If estimate is past,
  it says to wait for observed collection activity; countdown zero is not a
  claim that data has arrived. Old API fields remain usable by existing clients.

This is stored-activity inference, not a scheduler/lease/process health monitor.
`last_run_at` means latest **completed** cycle, including partial/error runs.
Latest **successful** collection must separately inspect run outcome
(rows/errors/aborted). A signal's source timestamp and quality determine source
freshness independently. The accepted one-GET canary returned Unix epoch and
no source unit despite HTTP 200/Good=true; that evidence remains unchanged.
Future NADI-INTEGRATION-STATUS must distinguish cycle duration, pause, effective
cadence, completion/success/activity, and individual source timestamp.

## Tests and exact commands

Use worktree root:

```bash
W=/home/john-d/.codex/worktrees/nadi-pi-001/reliability-knowledge-starter
# Disposable test DB only: no ports, no external network, tmpfs, no production volume.
docker run -d --name pi-runtime-migration-fix01-test --network none --tmpfs /var/lib/postgresql/data:rw -e POSTGRES_DB=pi_runtime_test -e POSTGRES_USER=pi_test -e POSTGRES_PASSWORD=temporary-test-only timescale/timescaledb:2.16.1-pg16
docker exec pi-runtime-migration-fix01-test pg_isready -U pi_test -d pi_runtime_test
docker run --rm --network container:pi-runtime-migration-fix01-test -e PI_MIGRATION_TEST_DSN=postgresql+psycopg://pi_test:temporary-test-only@127.0.0.1/pi_runtime_test -v "$W/pi-collector/src:/app/src:ro" -v "$W/pi-collector/tests:/app/tests:ro" -v "$W/pi-collector/migrations:/app/migrations:ro" -v "$W/compose.yaml:/compose.yaml:ro" reliability-cockpit-platform-pi-reviewed:3e981a3 python -m unittest discover -s tests
# 165 passed, 0 failed/skipped; includes 11 real Timescale integration tests.
# Same Docker fixture/mounts, targeted patterns:
# python -m unittest discover -s tests -p test_runtime_wiring.py -> 14 passed
# python -m unittest discover -s tests -p test_schedule.py -> 15 passed
cd "$W/pi-collector"
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python tests/compose_clean_check.py
# PASS: clean temporary checkout/HOME, synthetic platform env, pause 420;
# no collector/home dotenv, worker-only source configuration, no container startup.
cd "$W/reliability-cockpit"
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p 'test_asset_af_mapping*.py'
# 22 passed.
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_reliability_mart.py
# 41 passed, pre-existing SQLite ResourceWarnings, no failures.
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_cli.py
# 3 passed.
cd "$W/pi-collector/web"
node node_modules/typescript/bin/tsc --noEmit
# PASS using existing local dependency tree; temporary dependency symlink removed.
```

Clean Compose check invokes `docker compose --env-file .env.platform -f
compose.yaml --profile pi-collection --profile pi-maintenance config --format
json` inside a temporary fixture. Only synthetic values are loaded. It verifies
explicit required env names, credential isolation across all services, no
worker env_file, opt-in snapshot owner, no backfill and non-default pause 420
propagating to worker and API. Managed dotenv skip/standalone preservation,
old env/CLI compatibility, explicit flag precedence, 508+300 cadence and actual
ASGI /schedule serialization are covered by unit tests. Old 151 tests remain;
14 additional checks yield 165.

The first integration attempt raced temporary DB startup and failed before
its integration fixture connected. After `pg_isready`, all 165 tests passed;
no production migration failure occurred. One repeat clean-check invocation
used the root rather than PI working directory; the corrected command above
passed. Candidate Docker build and network-disabled packaged CLI pause/legacy-env
compatibility smoke check passed. Final whitespace and local document links pass. Temporary test DB/dependency symlink are removed afterwards.

## Accepted runtime evidence preserved

Read-only local SQL confirms migration 004 remains APPLIED at
`2026-10-07T10:49:24.644410Z`, checksum unchanged. Existing history remains
133,570 rows; registry 490/433 active; one managed owner lease. PI DB container
`08516a94ed6d...` retains start `2026-10-07T02:08:05.922667907Z`; worker retains
start `2026-10-07T10:52:26.311804973Z`. They were not restarted/recreated.
Accepted first cycle **433/433, 0 errors**, numeric/text/digital evidence and
Timescale/hypertable preservation are historical accepted facts, not remeasured
or rewritten by this fix. Source business writes remain 0; no additional
production PI requests were initiated by correction/testing. Existing worker
continues its previously authorized schedule independently.

No production migration/apply command, ledger reset, registry reload/prune,
backfill, operational DB/volume creation/reset, parallel worker, lower request
floor, Asset↔AF mapping, NADI restart or Maximo/CEMS/NK change occurred.
NADI-RUNTIME-002 was not implemented. Governed NADI readiness stays PARTIAL.
Corrected candidate deployment awaits final PR review; accepted running images
and private runtime provenance remain unchanged.

## PR readiness

Both configuration/cadence blockers are corrected in existing PR #15. Ready
for **final senior merge review**, OPEN/UNMERGED; no automatic merge. Rollout
must use the corrected source-controlled Compose/image and platform env after
review, preserving accepted store/overrides and one acquisition owner.
