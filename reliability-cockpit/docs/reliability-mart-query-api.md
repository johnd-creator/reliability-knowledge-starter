# NADI Reliability Mart Query API v1

MX-010R adds a read-only, vendor-neutral query surface to the existing
Reliability Cockpit FastAPI application. MX-012R keeps the six canonical Mart
tables and adds the current `reliability_asset_registry` projection; it does
not call Maximo, start a collector, or copy Mart data into the legacy Cockpit
store.

## Architecture and database boundary

```text
Maximo → CanonicalCollector → MartWriter → Reliability Mart PostgreSQL
                                      ↓
                         MartQueryRepository (SELECT only)
                                      ↓
                         ReliabilityQueryService
                                      ↓
                         /v1/reliability (FastAPI)
```

The legacy Cockpit database remains configured by `DATABASE_URL`. The Mart
reader uses the separate `RELIABILITY_MART_DATABASE_URL`; it intentionally has
no fallback to the legacy DSN. Deployment should use a database role with
read-only grants. PostgreSQL transactions are marked `READ ONLY` and receive a
bounded statement timeout. The application query facade exposes no
`insert`/`update`/`delete`/`commit` API.

If the Mart DSN is absent or unavailable, Mart routes return HTTP 503 while the
legacy Cockpit routes can continue to serve their existing data.

## Public route catalog

All routes are GET-only and use canonical reliability concepts:

| Route | Purpose |
| --- | --- |
| `GET /v1/reliability/assets` | Bounded asset list with status, unit, and type filters |
| `GET /v1/reliability/registry` | Aggregate current Registry snapshot metadata |
| `GET /v1/reliability/assets/{canonical_id}` | Asset detail |
| `GET /v1/reliability/assets/{canonical_id}/context` | Bounded asset context: maintenance, FMEA, health, and overhaul |
| `GET /v1/reliability/assets/{canonical_id}/fmea` | Paginated FMEA assessments for an asset |
| `GET /v1/reliability/assets/{canonical_id}/health-assessments` | Paginated health assessments for an asset |
| `GET /v1/reliability/assets/{canonical_id}/health/latest` | Latest health assessment using the documented timestamp fallback |
| `GET /v1/reliability/assets/{canonical_id}/timeline` | Bounded reliability timeline |
| `GET /v1/reliability/maintenance-events` | Maintenance event list and filters |
| `GET /v1/reliability/fmea` | FMEA list and filters |
| `GET /v1/reliability/asset-health` | Health assessment list and filters |
| `GET /v1/reliability/rcfa` | RCFA list; no asset filter is offered |
| `GET /v1/reliability/overhauls` | Overhaul list and filters |
| `GET /v1/reliability/integrity` | Aggregate logical-reference health counts |

List responses contain `items` and `meta` (`total`, `offset`, `limit`, and
`has_more`). Defaults are 50 records and the maximum is 200. Sort values are
allowlisted per resource; arbitrary SQL column names are never accepted.

## Scope and provenance safety

The reader applies `site_code = BSR` and `organization_code = IP` in every
query. Public site and organization parameters, where present, are literal
validated values and cannot be used to request another site. This is defense
in depth after the Collector and Mart writer scope guards.

Normal `/assets` and global Maintenance views join the current Registry
relation. Technical `asset_master` rows outside that relation remain Mart
context and are not normal NADI Assets. Maintenance date filters and sorting
use `COALESCE(actual_start, source_changed_at)` because local Collector history
may not retain actual start timestamps.

Normal product DTOs expose canonical fields, scope, contract version, and
selected source timestamps. They do not expose `sources.maximo`, full
provenance, relationship JSON, raw OSLC responses, credentials, or database
state.

## Relationships and context

The following are safe canonical joins:

```text
fmea_assessment.asset_ref
asset_health_assessment.asset_ref
maintenance_event.equipment_id
overhaul_event.asset_ref (when populated)
        ↓
asset_master.canonical_id
```

Overhaul-to-maintenance joins use:

```text
overhaul_event.workorder_ref = maintenance_event.work_order_id
```

They never join to `maintenance_event.canonical_id`, and the reader does not
assume `work_order_id` is unique. RCFA asset, location, and Work Order
relationships are unresolved in Contract v1, so RCFA is not attached to an
asset context or timeline. The context response reports
`rcfa_relationship_status: UNRESOLVED`.

Asset context uses a fixed small section limit (five by default, capped at ten)
and does not return full child history. Unresolved Overhaul rows remain
available through `/overhauls`, but cannot enter an asset timeline without a
populated asset reference.

## Timeline semantics

The timeline contains only `MAINTENANCE`, `FMEA`, `ASSET_HEALTH`, and resolved
`OVERHAUL` events. It is newest-first, bounded by the same 50/200 limits, and
uses these timestamp fallbacks:

* maintenance: `actual_start`, then `source_changed_at`;
* FMEA: `status_changed_at`, then `source_updated_at`;
* health: `status_changed_at`, then `source_updated_at`, then `source_created_at`;
* overhaul: `actual_start_at`, then `planned_start_at`, then `source_updated_at`.

No health score, MTBF, MTTR, or other analytics are calculated here.

## Legacy coexistence and handoff

Existing `/equipment`, `/work-orders`, `/kpis/...`, `/sync/status`, and
`/health` routes remain unchanged and continue to use the legacy Cockpit store.
The new query layer is a separate read path. It contains no Maximo client or
collector control endpoint and does not perform a production load.

MX-011R can use these APIs after a controlled initial Mart load. That task may
configure deployment credentials and operational readiness; it must not require
an API redesign or knowledge of Maximo object-structure names.
