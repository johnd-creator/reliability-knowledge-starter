# AGENTS.md — Reliability Knowledge Starter (workspace root)

This is a **single mono repository containing seven separate projects**, not one
combined application. There is **no top-level build, test, or run command** —
each subproject has its own. Read this file first, then the `AGENTS.md` /
`CONTEXT.md` inside the subproject you are working in.

> Each subproject also has its **own `AGENTS.md`** with project-specific safety
> rules. Those are authoritative for their scope; this file covers cross-cutting
> knowledge and how the pieces fit together.

## 1. Workspace layout & git model

```text
reliability-knowledge-starter/        <- mono repo root
├── maximo-knowledge/                 <- source knowledge
├── pi-knowledge/                     <- source knowledge
├── reliability-data-contracts/       <- vendor-neutral schemas
├── reliability-cockpit/              <- consumer app: transactional
├── pi-collector/                     <- consumer app: time-series
├── maximo-collector/                 <- consumer app: Maximo read-only sync
└── cems-collector/                   <- consumer app: CEMS Modbus read-only polling
```

- The root directory is the **only Git repository**. Subproject `.git`
  directories are intentionally absent so GitHub receives one coherent tree.
  Run Git commands from the root and use each subproject's own commands for
  setup, tests, and runtime.
- `manifest.json` is a generated snapshot of the starter's file list, not a
  package manifest. It is not used by any build.

## 2. The architectural mental model (read this before changing anything)

The projects form a **one-way data pipeline**. This directionality is the
most important rule in the workspace:

```text
maximo-knowledge   ─┐
                    ├──▶  reliability-data-contracts  ──▶  reliability-cockpit
pi-knowledge       ─┘     (vendor-neutral contracts)       (transactional app)
      │                                              ──▶  pi-collector
      └─────────────────── (verified WebIds)              (time-series app)
(SOURCE OF TRUTH)                                           (trending + ML)
```

- **`maximo-knowledge` / `pi-knowledge`** are *read-only knowledge bases*, **not
  applications**. They record what the source systems expose, how to read it
  safely, and what it means. They contain discovery scripts, JSON catalogs, and
  docs.
- **`reliability-data-contracts`** is the vendor-neutral contract layer. JSON
  Schemas (Draft 2020-12) plus field-mapping tables. Core fields are
  snake_case; **vendor fields are quarantined under `sources.maximo` /
  `sources.pi`** and must never leak into core contract fields.
- **`reliability-cockpit`** is the only application. It **syncs** verified
  Maximo objects into its own local Postgres, **computes** reliability KPIs, and
  **serves** a FastAPI + Next.js UI.

**Non-negotiable rule:** the cockpit **never rediscovers** Maximo/PI. Before
introducing any source field, tag, endpoint, or WebId into the cockpit, look it
up in the knowledge repos and prefer entries with `status: verified`. If the
knowledge is missing, the correct action is to add a discovery task in the
relevant knowledge repo — not to guess an identifier in the app.

## 3. Commands — there is no unified entrypoint

Each project is independent. The correct setup/test cycle differs per project.

### maximo-knowledge (Python, stdlib + playwright)
```bash
cd maximo-knowledge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium   # only for session discovery
cp .env.example .env                              # fill MAXIMO_READ_ONLY_TOKEN
.venv/bin/python -m unittest discover -s tests    # 37 tests
```
Discovery CLIs (`scripts/discover.py`, `scripts/session_discover.py`) are
GET/HEAD/OPTIONS only. **All network discovery requires an explicit `--execute`
flag** — without it they run offline/dry-run against local fixtures.

### pi-knowledge (Python, stdlib)
```bash
cd pi-knowledge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests    # 7 tests
```
PI access is **not yet verified**. `discovery/*.json` entries are
`status: documented` (public OSIsoft behavior), never instance-verified. The
cockpit's PI adapter is a placeholder that raises `NotImplementedError`.

### reliability-data-contracts (JSON Schemas, no own venv)
This project has **no virtual environment of its own** — it is pure data.
Validate schemas by borrowing the maximo-knowledge venv (which has `jsonschema`):
```bash
cd reliability-data-contracts
../maximo-knowledge/.venv/bin/python -c "
import json, glob
from jsonschema import Draft202012Validator
for f in sorted(glob.glob('schemas/*.schema.json')):
    Draft202012Validator.check_schema(json.load(open(f)))
"
# 12 schemas expected
```

### reliability-cockpit (Python app + Postgres + Next.js web)
```bash
cd reliability-cockpit
python3 -m venv .venv && .venv/bin/pip install -e .   # -e . installs the `cockpit` CLI
cp .env.example .env                                  # MAXIMO_READ_ONLY_TOKEN + DATABASE_URL
.venv/bin/cockpit init-db                             # create Postgres tables
.venv/bin/cockpit sync                                # delta-sync Maximo objects
.venv/bin/cockpit kpi                                 # compute + persist KPIs
.venv/bin/cockpit serve                               # FastAPI on 127.0.0.1:8000
.venv/bin/python -m unittest discover -s tests        # 34 tests (no DB needed)
```
Web UI (separate process):
```bash
cd reliability-cockpit/web
npm install && cp .env.example .env.local && npm run dev   # Next.js on :3000
```

`USERGUIDE.md` (root) is a detailed end-to-end runbook for these three projects
(written in Indonesian; `pi-knowledge` is intentionally not covered there).

### pi-collector (Python app + TimescaleDB + FastAPI)
```bash
cd pi-collector
python3 -m venv .venv && .venv/bin/pip install -e .   # installs `picollector` CLI
cp .env.example .env                                  # PI credentials + DATABASE_URL
docker-compose up -d postgres                         # TimescaleDB on port 5433
.venv/bin/picollector init-db                         # create tables + hypertable
.venv/bin/picollector load-registry                   # load 150 BSR1 attributes from pi-knowledge YAML
.venv/bin/picollector collect-snapshots               # fetch current values for all attributes
.venv/bin/picollector backfill --start "*-7d" --end "*" --interval 1h  # 7-day history
.venv/bin/picollector serve                           # FastAPI on 127.0.0.1:8001
.venv/bin/python -m unittest discover -s tests        # 23 tests (no DB/network needed)
```
The collector reads verified WebIds from `../pi-knowledge/mappings/bsr1-parameters.yaml`
(never hardcoded). Two collection modes: `collect-snapshots` (lightweight, current
values) and `backfill` (heavy, interpolated history for trending/ML). Time-series
data stored in a TimescaleDB hypertable for efficient range queries.

### cems-collector (Python app + Postgres + FastAPI)
```bash
cd cems-collector
python3 -m venv .venv && .venv/bin/pip install -e .   # installs `cemscollector` CLI
cp .env.example .env                                  # PLC host/port + DATABASE_URL
docker compose up -d postgres                         # Postgres on port 5435
.venv/bin/cemscollector init-db                       # create tables
.venv/bin/cemscollector load-registry                 # load 14 parameters from registry/cems-parameters.yaml
.venv/bin/cemscollector collect                       # continuous Modbus polling (read-only)
.venv/bin/cemscollector aggregate                     # 5-minute window aggregation
.venv/bin/cemscollector diagnose                      # read-only probe of every parameter
.venv/bin/cemscollector serve                         # FastAPI on 127.0.0.1:8003
.venv/bin/python -m unittest discover -s tests        # 81 tests (no DB/network needed)
```
Ported from the DAZ production collector (Beijer Box2Base Modbus TCP gateway,
stack 1 PLTU Suralaya). Modbus access is **FC03/FC04 read function codes
only** — the guard raises on any write/mask call. The registry YAML is the
single source for register numbers; entries are `status: documented` until
re-verified against the live PLC. Normalization (gas conversion, threshold
clamp, maintenance overrides, O2-reference correction) runs inside the
collector; the DAZ outbound KLHK/CEMS push was deliberately not ported.
Optional Next.js dashboard under `web/` (proxy `CEMS_COLLECTOR_API_BASE`).

## 4. Hard safety boundary (enforced in code, not just convention)

All access to production Maximo/PI is **READ ONLY**. This is not a guideline —
it is implemented as a guard:

- `maximo-knowledge/scripts/discover.py` and
  `reliability-cockpit/src/adapters/maximo/oslc_client.py` both define
  `READ_ONLY_METHODS = {"GET", "HEAD", "OPTIONS"}` and **raise** on any other
  method. Do not "relax" these checks.
- `cems-collector/src/adapters/modbus/client.py` defines
  `READ_ONLY_FUNCTIONS = {"read_holding_registers", "read_input_registers"}`;
  any write/mask-shaped call raises `ModbusGuardError`. Same rule: do not
  relax it.
- Every Maximo sync query is scoped `oslc.where=siteid="BSR"` (org `IP`) by
  default. This site scope matches the read-only discovery account.
- Rate limiting (default **1 request/second**) and a **1 MiB response size cap**
  are mandatory and applied on every request.
- **Never commit credentials, tokens, cookies, API keys, or Authorization
  headers.** `.env*` is gitignored (except `.env.example`). All saved response
  samples must be sanitized (sensitive + personal key regexes live in
  `discover.py`).
- Never brute-force paths, IDs, object names, WebIds, or tags. If access
  behavior is uncertain, record the record as `status: unknown` and stop.

> Boundary nuance: the *knowledge repos' own tooling* stays GET-only. A
> **downstream app** (e.g. the cockpit) may use programmatic login
> (`POST /j_security_check`) to obtain a session, because login is
> authentication, not data mutation. See `maximo-knowledge/CONTEXT.md` §5.

## 5. Status vocabulary — trust only `verified`

Every catalog/sample record carries a `status`. This vocabulary is identical
across all repos:

| status | meaning |
|---|---|
| `unknown` | not tested — do not rely on it |
| `documented` | present in vendor docs/seed, not verified on this instance |
| `verified` | tested with authorized read-only access — **trust this** |
| `forbidden` | endpoint exists but the current account cannot access it |
| `deprecated` | known but should not be used |

Treat anything that is not `verified` as "probably correct, must be re-verified
against the live instance before depending on it."

## 6. reliability-cockpit internals (the application)

### Data flow within the app
```text
OslcClient (GET-only) ──▶ mappers ──▶ domain models ──▶ CockpitStore ──▶ Postgres
                                                          ▲
                                KpiService (reads store, writes KPIs back)
                                                          ▲
                                FastAPI (read-only views) ──▶ Next.js UI
```
- `src/adapters/maximo/oslc_client.py` — paginates OSLC collections, enforces
  read-only + rate-limit + size cap. OSLC records live under the **`_member`**
  key (with `member`/`oslc:member`/`rdfs:member` fallbacks) — not `data`/`items`.
- `src/adapters/maximo/mappers.py` — raw OSLC payload → frozen dataclass domain
  models. The field-by-field translation source of truth is
  `reliability-data-contracts/mappings/maximo-to-contracts.md`.
- `src/domain/` — frozen dataclasses (`Equipment`, `WorkOrder`, `ServiceRequest`,
  `Person`, `Item`, `Labor`, `ReliabilityKpi`, …). Vendor fields live in
  `*Source` nested dataclasses (e.g. `MaximoEquipmentSource`).
- `src/services/sync.py` — delta sync using the `changedate` watermark. First
  run = `full`; later runs append `changedate >= "<watermark>"` to `oslc.where`.
  Watermarks persist in the `sync_cursor` table. A row that fails to map is
  **logged and skipped** — one bad row never aborts a sync.
- `src/services/kpi.py` — computes MTBF, MTTR, AVAILABILITY, PM_COMPLIANCE from
  normalized work orders. KPIs are **derived by the cockpit**, never read
  directly from Maximo. Default period = last 90 days (`--from`/`--to`/`--equipment`
  to override). PM compliance counts `work_type == "PM"`; "completed" status set
  is `{CLOSE, CLOSED, COMP, COMPLETE, COMPLETED}`.
- `src/repositories/` — SQLAlchemy 2.0 (declarative `Base`). Tables are created
  via `Base.metadata.create_all` (`cockpit init-db`); the ORM in `models.py` is
  the source of truth and `migrations/001_init.sql` mirrors it. 8 tables:
  `equipment`, `work_order`, `service_request`, `person`, `item`, `labor`,
  `reliability_kpi`, `sync_cursor`.
- `src/api/app.py` — FastAPI. Endpoints use Pydantic `*View` models whose field
  names mirror the contracts. No raw vendor payload escapes this layer. Swagger
  at `/docs`.

### Web UI
- Next.js 15 (App Router) + React 19 + TypeScript under `web/`.
- The browser never calls FastAPI directly: requests go to `/api/cockpit/*` and a
  `next.config.js` rewrite proxies them to `COCKPIT_API_BASE`
  (default `http://127.0.0.1:8000`). Set this in `web/.env.local` if the API
  runs on another host/port.
- API client lives in `web/lib/api.ts`.

### CLI object → resource map (`src/cli.py`)
| object structure | resource | watermark |
|---|---|---|
| `mxasset` | equipment | `changedate` |
| `mxwodetail` | workorder | `changedate` |
| `mxapisr` | servicerequest | `changedate` |
| `mxperson` | person | `statusdate` |
| `mxitem` | item | `statusdate` |
| `mxapilabor` | labor | — |

`cockpit sync` accepts either the object-structure name or the resource name
(e.g. `cockpit sync mxasset` or `cockpit sync equipment` both work).

## 7. Non-obvious gotchas

- **`cockpit: command not found`** — the CLI is only available after
  `pip install -e .` (editable install) **in the cockpit venv**. Run it from
  `.venv/bin/cockpit` or activate the venv.
- **Postgres is required for the cockpit to run** (not for its unit tests). Use
  `docker-compose up -d postgres` or a local instance; default DSN is
  `postgresql://cockpit:cockpit@localhost:5432/cockpit`.
- **6 Maximo objects are `forbidden`** (`failurecode`, `location`, `pm`, `meter`,
  `jobplan`, `mxapiwodetail`) for the current discovery account — they return
  `BMXAA0024E`. This is **not a bug**; the account lacks object-level READ
  sigoptions. Derived concepts (`failure`, `location`, `maintenance-event`) fall
  back to data drawn from the verified objects until a read-enabled credential
  exists.
- **PI is a placeholder end-to-end.** `pi-knowledge` has only `documented`
  records and the cockpit `src/adapters/pi/client.py` raises
  `NotImplementedError`. Do not wire the cockpit to PI until `pi-knowledge`
  records `verified` entries.
- **Maximo scalar values arrive as strings.** Booleans (`"true"`, `"1"`) and
  numbers are frequently stringified in OSLC payloads. Always use the coercion
  helpers (`oslc_boolean`, `oslc_number`, `oslc_timestamp`, `oslc_pop_*`) in
  `oslc_client.py` rather than casting directly.
- **Site scope is always BSR.** Omitting the `siteid="BSR"` filter returns data
  from other sites. The sync engine and client apply it by default — preserve
  that when adding queries.
- **CEMS registry codes must be quoted in YAML.** YAML 1.1 parses bare
  `NO`/`YES`/`ON`/`OFF` as booleans; the cems-collector registry loader
  rejects non-string codes with a hint. Registry `status` is the knowledge
  vocabulary; the operational on/off switch is `collect: true|false`.
- **Tests use `unittest`, not `pytest`**, and do **not** require a database or
  network — `OslcClient` and `CockpitStore` are replaced with lightweight fakes
  (`FakeClient`/`FakeStore`) in `reliability-cockpit/tests/`. Keep new tests
  hermetic the same way.

## 8. Conventions

- **Contract field naming:** snake_case for core/vendor-neutral fields; vendor
  (Maximo) identifiers isolated under a `sources.maximo` object, PI under
  `sources.pi`, CEMS Modbus details under `sources.cems`. Never copy vendor
  field names into core fields.
- **Schema files:** `<entity>.schema.json`, JSON Schema Draft 2020-12, in
  `reliability-data-contracts/schemas/`. Breaking changes require a version bump;
  prefer backward-compatible additions.
- **Timestamps:** ISO-8601. The delta-sync watermark is `changedate`.
- **Domain models:** frozen `@dataclass` instances in `src/domain/`.
- **Commit messages** (per-subproject AGENTS.md): scoped conventional style, e.g.
  `docs(maximo): …`, `feat(discovery): …`, `docs(mapping): …`, `feat(pi): …`.
- **Config:** all secrets via environment / `.env` (never source control). The
  cockpit loads `.env` from the repo root and `~/.reliability-cockpit.env`.
  Auth is either `MAXIMO_READ_ONLY_TOKEN` (bearer) or an out-of-band
  `MAXIMO_SESSION_COOKIE`.

## 9. Where to look next (progressive disclosure)

| If you are working on… | read this first |
|---|---|
| Maximo discovery / catalogs | `maximo-knowledge/CONTEXT.md` → `AGENTS.md` |
| PI discovery | `pi-knowledge/CONTEXT.md` → `AGENTS.md` |
| Contracts / schemas | `reliability-data-contracts/README.md` → `AGENTS.md` |
| The cockpit app | `reliability-cockpit/docs/adapter.md`, `docs/source-resolution.md` → `AGENTS.md` |
| CEMS collection | `cems-collector/AGENTS.md` (registry → guard → normalization) |
| End-to-end runbook | `USERGUIDE.md` (root) |
