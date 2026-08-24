# PI Collector

Time-series data collector for PI Web API (AVEVA/OSIsoft). Pulls verified
attributes into a local TimescaleDB store and serves them via REST API to
multiple consumers: trending dashboards, ML feature pipelines, and the
reliability cockpit.

## Design Principles

1. **Read-only against PI** — GET/HEAD/OPTIONS only, enforced in code.
2. **Knowledge-driven** — the technical registry of attributes to collect comes
   from `pi-knowledge`, never hardcoded. It is not a governed Asset mapping.
3. **Time-series optimized** — TimescaleDB hypertable for efficient range
   queries and aggregation at scale.
4. **Multi-consumer** — clean REST API, no vendor payloads escape the layer.

## Architecture

```text
DCS / control systems
        │
        ▼ existing acquisition / OPC / PI Interface pipeline
Central PI Data Archive + AF
        │
        ▼ PI Web API / AF (Basic auth, runtime-only credentials)
PiClient (GET/HEAD/OPTIONS, same-origin only)
        │
        ├── technical collection mode ──▶ local pi_snapshot/pi_timeseries
        │                                  (trending and ML consumers)
        │
        └── governed source boundary ◀── VERIFIED Asset ↔ AF target supplied
                                         by future NADI orchestration

The broad `pi-knowledge/mappings/bsr1-parameters.yaml` inventory contains 541
technical attributes, including 433 stream-ok entries. It is a technical
collection registry, not a list of governed reliability signals:

```text
TECHNICAL_PI_ATTRIBUTE != GOVERNED_ASSET_SIGNAL
```

PI Vision is a visualization surface, not the ingestion API. The collector
does not crawl the AF hierarchy or infer Asset identity from names, tags, or
similarity. Existing raw registry identifiers are pre-existing technical debt;
this work adds no new production WebIds or tags.
```

## Setup

### Prerequisites

| Tool | Version |
|---|---|
| Python | ≥ 3.11 |
| Docker | any (for TimescaleDB) |

### Install

```bash
cd pi-collector
python3 -m venv .venv
.venv/bin/pip install -e .          # installs the `picollector` CLI
cp .env.example .env                # fill PI credentials + DATABASE_URL
```

`PI_WEB_API_BASE_URL` is required for live source operations and must be
provided as a runtime value. `PI_VERIFY_TLS` defaults to `1`. The currently
instance-verified authentication mode is Basic auth via `PI_USERNAME` and
`PI_PASSWORD`; credentials are never logged, persisted, or returned by the
collector. Bearer configuration remains compatibility-only and is not claimed
as verified for the current instance.

### Start TimescaleDB

```bash
docker-compose up -d postgres       # TimescaleDB on port 5433
```

Or use the cockpit's Postgres (change `DATABASE_URL` in `.env`).

### First run

```bash
.venv/bin/picollector init-db              # create tables + hypertable
.venv/bin/picollector load-registry        # load 433 stream-ok attributes from the 541-attribute registry
.venv/bin/picollector collect-snapshots    # fetch current values
.venv/bin/picollector backfill --start "*-7d" --end "*" --interval 1h  # 7-day history
```

### Download ALL historical data (recorded)

```bash
# Full raw history — only runs during off-hours (22:00-06:00 + weekend)
.venv/bin/picollector backfill-recorded --start "2024-01-01T00:00:00Z" --end "*"

# Single attribute (resumes where it stopped — upserts are idempotent)
.venv/bin/picollector backfill-recorded --start "2024-01-01T00:00:00Z" --attribute BSR-BSR1-turbine-...

# Emergency override of the off-hours gate (use with caution!)
.venv/bin/picollector backfill-recorded --start "*-30d" --end "*" --force
```

### Continuous collection (every 5 minutes)

```bash
# Snapshot mode: current values for all attributes, every 5 minutes
.venv/bin/picollector run --mode snapshot --interval-seconds 300

# Recorded-delta mode: fetch new raw points since the last cursor
.venv/bin/picollector run --mode recorded-delta --interval-seconds 300
```

### Serve

```bash
.venv/bin/picollector serve                # API on http://127.0.0.1:8001
```

Swagger docs: `http://127.0.0.1:8001/docs`

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/attributes` | GET | List registered attributes (`?equipment=&parameter=`) |
| `/snapshots` | GET | Latest values (`?equipment=&limit=`) |
| `/snapshots/{id}` | GET | Latest value of one attribute |
| `/timeseries/{id}` | GET | History (`?start=&end=&limit=`) |
| `/heatmap/{id}` | GET | Daily data coverage (GitHub-style) |
| `/collect/snapshots` | POST | Trigger snapshot collection |
| `/collect/backfill` | POST | Trigger backfill (`?start=&end=&interval=`) |
| `/stats` | GET | Collection statistics |

The API serves locally collected data. It is not a live PI proxy and does not
accept arbitrary WebIds or URLs. The existing collection trigger routes only
start the configured local collector modes; they do not create governed
Asset↔AF mappings.

## Governed source boundary

`src/domain/governed.py` defines `GovernedAfTarget`. The
`GovernedSourceBoundary` accepts only an explicit target with:

- `mapping_status=VERIFIED`
- `mapping_role=PRIMARY_EQUIPMENT`
- `pi_source_id=CENTRAL_PI`

`PROPOSED`, `RETIRED`, `UNMAPPED`, and `AMBIGUOUS` targets are rejected. The
boundary reads one AF Element, at most 100 direct Attributes, Attribute
metadata, a linked current value, or a bounded recorded window of at most 20
samples. It does not read or write the Reliability Mart and does not discover
Asset↔AF relationships.

The normalized local signal retains the source timestamp, numeric/text/digital
value classification, engineering unit, and the PI `Good`, `Questionable`,
`Substituted`, and `Annotated` flags. A digital state remains non-numeric;
quality is source evidence and is not interpreted as an alarm, failure, or
diagnosis.

## Safety guardrails (bulk downloads)

`backfill-recorded` is the heaviest operation — it downloads every raw point.
To protect the PI server from being overwhelmed or blocking the account, the
following layers are enforced in code (all configurable via `.env`):

| Layer | Default | Env var |
|---|---|---|
| Rate limit (per request) | 1 req/s | `PI_RATE_LIMIT_SECONDS` |
| Response size cap | 1 MiB | `PI_MAX_RESPONSE_BYTES` |
| **Off-hours gate** — aborts if run outside 22:00–06:00 or weekends | 22–06 + Sat/Sun | `PI_OFF_HOURS_START/END`, `PI_OFF_HOURS_WEEKEND` |
| **Circuit breaker** — hard stop after N requests per session | 5000 | `PI_MAX_REQUESTS_PER_SESSION` |
| **Consecutive error abort** — stop if PI fails 10 times in a row | 10 | `PI_MAX_CONSECUTIVE_ERRORS` |
| **Time-window chunking** — split ranges into 7-day windows | 7 days | `PI_BACKFILL_CHUNK_DAYS` |
| **Inter-attribute pause** — 2s cooldown between attributes | 2.0s | `PI_PAUSE_BETWEEN_ATTRIBUTES` |

Resumability: all inserts are idempotent upserts (by attribute_id + timestamp).
If a run aborts (circuit breaker, errors), re-running the same command resumes
from where it stopped — no duplicates, no lost data.

## Scheduling (night + weekend)

Ready-made units in `deploy/`:

```bash
# systemd (recommended for servers)
sudo cp deploy/pi-collector-backfill.{service,timer} /etc/systemd/system/
sudo systemctl enable --now pi-collector-backfill.timer   # nightly 22:15 + weekend
sudo systemctl enable --now pi-collector-snapshot.service  # continuous 5-min snapshots

# cron alternative — see deploy/crontab.example
crontab -e   # paste the lines, adjust paths
```

The timer/cron only **trigger** the run; the in-app off-hours gate remains the
final authority (a stray daytime cron entry still aborts safely).

## Tests

```bash
.venv/bin/python -m unittest discover -s tests
```

## Project structure

```
src/
├── cli.py                      # picollector CLI (7 commands)
├── config.py                   # PiApiConfig, DbConfig, CollectSafetyConfig
├── adapters/pi/client.py       # PiClient (GET-only, rate-limit, pagination)
├── domain/models.py            # normalized PI readings and registrations
├── domain/governed.py          # validated NADI Asset↔AF target boundary
├── repositories/
│   ├── database.py             # SQLAlchemy engine + TimescaleDB hypertable
│   ├── models.py               # ORM models
│   └── store.py                # CollectorStore (upsert/query/heatmap)
├── services/
│   ├── registry.py             # parse pi-knowledge YAML → registrations
│   ├── collector.py            # technical collection engine + safety gates
│   └── governed_source.py      # AF-linked reads for validated targets
└── api/app.py                  # FastAPI consumer endpoints
web/                            # Next.js UI (attribute list, heatmap, collect buttons)
deploy/                         # systemd timer/service + cron examples
tests/                          # 45 unit tests (no network, no DB)
```
