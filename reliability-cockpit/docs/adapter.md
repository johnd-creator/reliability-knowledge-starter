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
- First run = full (no watermark). Later runs filter
  `oslc.where=siteid="BSR" and changedate >= "<watermark>"`.
- A row with a failure to map is logged and skipped; the sync continues.

## Run

```bash
cockpit init-db      # create Postgres tables
cockpit sync         # delta-sync all verified objects
cockpit sync mxwodetail   # sync a single object
cockpit serve        # FastAPI on 127.0.0.1:8000
```