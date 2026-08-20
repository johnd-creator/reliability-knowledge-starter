# Adapter & Sync Architecture

Read-only against Maximo/PI. Writes only to the cockpit's own Postgres store.

## Flow

```text
Maximo OSLC (read-only)          Cockpit sidecar                     Web UI
┌──────────────────────┐   ┌─────────────────────────────┐   ┌───────────────┐
│ /oslc/os/<object>    │──▶│ OslcClient (GET-only)        │   │ Next.js app   │
│  - siteid="BSR"      │   │   ├─ rate limit (1 req/s)    │   │  /api/cockpit/│
│  - oslc.paging       │   │   ├─ oslc.select             │   │  proxy → Fast │
│  - oslc.orderBy      │   │   └─ delta watermark         │   │  API          │
└──────────────────────┘   └───────────┬─────────────────┘   └──────┬────────┘
                                       │ mappers (contract fields) │
┌──────────────────────┐   ┌───────────▼─────────────────┐   ┌──────▼────────┐
│ Cockpit Postgres     │◀──│ SyncService  ──▶ CockpitStore │   │ FastAPI       │
│ (normalized store)   │   │   │ KPI service               │   │ /equipment    │
└──────────────────────┘   └─────────────────────────────┘   │ /work-orders  │
                                                             │ /kpis/*       │
                                                             └───────────────┘
```

## Safety rules (see AGENTS.md)

1. The client raises on any method outside `GET/HEAD/OPTIONS`.
2. `siteid="BSR"` is applied to every sync query by default.
3. Rate limiting (default 1s between requests) is mandatory — the discovery
   repository enforces the same value.
4. Credentials are never stored; a read-only token is supplied at runtime.
   The `MAXIMO_SESSION_COOKIE` supports an out-of-band manual-login session.
5. KPI values are computed by the cockpit; Maximo/PI are never written to.

## Verified objects (site BSR)

Source of truth: `../maximo-knowledge/discovery/objects/` (or the
`reliability-data-contracts/mappings/maximo-to-contracts.md` translation).

| Object structure | Resource      | Endpoint           | Watermark |
|---|---|---|---|
| `mxasset`        | equipment     | `/oslc/os/mxasset` | `changedate` |
| `mxwodetail`     | workorder     | `/oslc/os/mxwodetail` | `changedate` |
| `mxapisr`        | servicerequest | `/oslc/os/mxapisr` | `changedate` |
| `mxperson`       | person        | `/oslc/os/mxperson` | `statusdate` |
| `mxitem`         | item          | `/oslc/os/mxitem`  | `statusdate` |
| `mxapilabor`     | labor         | `/oslc/os/mxapilabor` | — |

Forbidden objects (FAILURECODE, LOCATION, PM, METER, JOBPLAN) fall back to
derived data until a read-enabled credential is verified.

## Delta sync

- Watermark persisted per object in `sync_cursor`.
- First run = full (no watermark). The BSR `mxwodetail` instance rejects the
  range comparator used by the legacy delta query, so work-order collection
  uses the verified site scope and local changedate comparison/upsert
  idempotency; its cursor remains metadata and is never advanced on a partial
  traversal.
- A row with a failure to map is logged and skipped; the sync continues.

## Work Orders API pagination

`GET /work-orders` returns a bounded envelope rather than an unbounded array.
The example below is illustrative only; live totals come from the database:

```json
{"items": [], "total": 0, "offset": 0, "limit": 50, "has_more": false}
```

The default page size is 50 and the maximum is 200. Omitted `status` means all
statuses, including `CLOSE` and `CAN`; `status=CLOSE` (or another explicit
value) filters both `total` and `items`. `equipment_id` applies to both
`total` and `items`; ordering is stable by `reported_at DESC NULLS LAST, id
ASC`. The web UI requests one page at a time and displays all-status and
filtered totals separately.

## Run

```bash
cockpit init-db      # create Postgres tables
cockpit sync         # delta-sync all verified objects
cockpit sync mxwodetail   # sync a single object
cockpit serve        # FastAPI on 127.0.0.1:8000
```
