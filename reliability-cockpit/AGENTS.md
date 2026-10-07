# AGENTS.md — Reliability Cockpit

## Existing NADI stack and data ownership

Read root `../AGENTS.md` first. NADI is the product UI for this project.
Backend: Python FastAPI / SQLAlchemy. Web: Next.js 15 / React 19 / TypeScript.
The current deployment is root Compose project `reliability-cockpit-platform`;
web default 3000, API 8000 with `compose.dev.yaml`.

**Do not create a new NADI database or a separate Reliability Mart database.**
Reuse the existing stores with these distinct paths:

| Path | Configuration / owner | Purpose |
|---|---|---|
| Legacy sync/KPIs | `DATABASE_URL` → `cockpit-db` / `cockpit` | `cockpit-worker` consumes Maximo Collector API; legacy equipment/work orders/KPIs |
| Canonical NADI | `RELIABILITY_MART_DATABASE_URL` → `maximo-db` / `maximo_collector` | `/v1/reliability/*` reads the existing Mart; no legacy-store fallback |

The Mart DSN is a separate connection setting, **not a request for another
database**. Public Mart query transactions stay read-only; governed mapping
administration has its own documented internal workflow and existing Mart
tables. Do not add public write endpoints or auto-verify mappings.

NADI Asset lists require `reliability_asset_registry` membership. Technical
Equipment / `asset_master` counts alone do not prove NADI data availability.
Investigate DSN, scope, Registry, canonical tables and projection state before
starting collection. `mart-projector` refreshes local Equipment/Work Order
projections in the Maximo DB; `cockpit run` does not populate that Mart.
Do not fuzzy-match identities, fabricate unresolved RCFA links or invent health
scores. Preserve the semantics in `docs/reliability-mart-query-api.md` and the
domain-specific `docs/nadi-*-semantics.md` files.

Browser requests use `/api/cockpit/*`, proxied to `COCKPIT_API_BASE`.
Cockpit's PI/CEMS API bases are configurable but their projections are pending.
Never put production Maximo/PI credentials in Cockpit; source collection belongs
to the collectors. Do not switch to `compose.external.yaml`, use old localhost
DB defaults, or run another worker as a routine fix for empty pages.

## Mission

Build reliability applications by consuming verified organizational knowledge rather than rediscovering production systems.

## Source of Truth

Before introducing a Maximo field, PI tag, endpoint, WebId, or parameter:

1. Search the relevant knowledge repository.
2. Prefer entries with `status: verified`.
3. If knowledge is missing, create a discovery task in the appropriate source-knowledge repository.
4. Do not guess production identifiers.

## Architecture Rule

Application domain models must prefer `reliability-data-contracts`.

Vendor-specific fields belong in source adapters.

## Safety

Production source systems remain read-only unless a separate explicit authorization exists.
