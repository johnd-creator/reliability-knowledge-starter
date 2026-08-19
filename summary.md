# Summary of Work Done

## Objective
Separate the Maximo data collection into a dedicated `maximo-collector` project (mirroring `pi-collector` patterns) so the cockpit dashboard reads from the collector's local store instead of directly connecting to Maximo. Enable programmatic login via `j_security_check` (as documented in `maximo-knowledge`) and serve contract-shaped data via FastAPI. The cockpit then becomes a pure dashboard reading from the collector's store.

## Important Details
- **Architecture**: New `maximo-collector/` project (sibling to `pi-collector`) with its own Postgres (:5434), FastAPI (:8002), and CLI (`mxcollector`). Cockpit reads from collector API instead of direct Maximo connection.
- **Auth**: Programmatic login via POST `/j_security_check` (once per session), as prescribed by `maximo-knowledge/docs/authentication.md`. No Basic Auth or API token needed.
- **Data contracts**: All domain models and API responses follow `reliability-data-contracts` field names; vendor values quarantined under `sources.maximo`.
- **Scope**: 6 verified objects (`mxasset`, `mxwodetail`, `mxapisr`, `mxperson`, `mxitem`, `mxapilabor`); `forbidden` objects excluded.
- **Auth mode**: `MAXIMO_AUTH_MODE=login` (default); username/password from `.env`; no admin action required.
- **Safety**: `READ_ONLY_METHODS` guard on `/oslc/*` untouched; only whitelisted POST to `/j_security_check`; credentials in memory only; rate 1 req/s; scope `siteid="BSR"`.
- **Current state**: 77 unit tests pass, `tsc --noEmit` clean, daemon and API running.

## Work State
### Completed
- Scaffolded `maximo-collector/` project (pyproject.toml, .env.example, docker-compose.yml, AGENTS.md, README.md, migrations/001_init.sql).
- Implemented `src/config.py` with `MaximoConfig` (auth_mode, username, password, token).
- Implemented `src/adapters/maximo/auth.py` — programmatic login (`j_security_check`), session management, expiry detection.
- Implemented `src/adapters/maximo/oslc_client.py` — READ_ONLY guard, rate-limit, size cap, iterate() with re-login-on-expiry.
- Implemented `src/adapters/maximo/mappers.py` — 6 mapper functions (`equipment_from_payload`, `work_order_from_payload`, `service_request_from_payload`, `person_from_payload`, `item_from_payload`, `labor_from_payload`).
- Implemented `src/domain/models.py` — 7 frozen dataclasses (`Equipment`, `WorkOrder`, `ServiceRequest`, `Person`, `Item`, `Labor`, `MaximoEquipmentSource`).
- Implemented `src/repositories/database.py`, `models.py` (ORM with `EquipmentOrm`, `WorkOrderOrm`, `ServiceRequestOrm`, `PersonOrm`, `ItemOrm`, `LaborOrm`, `SyncCursorOrm`, `CollectRunOrm`), `store.py` (CollectorStore with upsert, list_rows, count, cursor/run log).
- Implemented `src/services/sync.py` — delta sync (`changedate`/`statusdate`), full/incremental, skip bad rows, observability (collect_run).
- Implemented `src/api/app.py` — FastAPI :8002 with contract-shaped views (`/equipment`, `/work-orders`, `/service-requests`, `/persons`, `/items`, `/labor`, `/sync/status`, `/health`, `POST /sync/{object}`).
- Implemented `src/cli.py` — `mxcollector init-db | sync [objects] | serve`.
- Implemented `src/domain/models.py` — 7 frozen dataclasses mirroring contract shape.
- Created `tests/` hermetic test suite (77 tests passing): guard, mapper, sync, config, auth.

### Active
- Cockpit refactor to pure dashboard (removing Maximo adapter, adding collector_client pull) — **planned but not yet started**.
- Live verification: filling `MAXIMO_USERNAME`/`MAXIMO_PASSWORD` in `.env` and running `mxcollector sync mxasset` → verify login + data landing → `mxcollector serve` → cockpit reads data.

### Blocked
- None (plan mode constraint prevents changes; awaiting user execution trigger).

## Next Move
1. **User fills** `MAXIMO_USERNAME` / `MAXIMO_PASSWORD` in `maximo-collector/.env` (read-only BSR credentials).
2. Run `mxcollector init-db` → verify DB tables.
3. Run `mxcollector sync mxasset` → verify login + data landing.
4. Run `mxcollector serve` → verify API at `http://127.0.0.1:8002`.
5. Refactor cockpit: remove `src/adapters/maximo/` + `services/sync.py`; add `src/adapters/collector_client.py` (HTTP pull from :8002); update `cockpit/` config to use `MAXIMO_COLLECTOR_API_BASE`.
6. Verify cockpit dashboard displays data without ever hitting Maximo.

## Relevant Files
- `maximo-collector/` — new project (scaffold + all source files).
- `pi-collector/` — reference implementation (mirror for auth + sync patterns).
- `reliability-cockpit/` — to be refactored (remove Maximo adapter, add collector_client pull).
- `reliability-data-contracts/` — shared schema layer (untouched).
- `maximo-knowledge/` — auth docs and object catalogs (reference).
- `AGENTS.md` (root) — to add `maximo-collector` section; `AGENTS.md` cockpit — to update for dashboard-only mode.
- `.env.example` — updated with `MAXIMO_USERNAME`/`MAXIMO_PASSWORD`.
- `tests/` — maximo-collector tests + adjusted cockpit tests.