# CONTEXT — Start Here (for AI tools & humans)

> This is the **entry point** for anyone — or any AI tool (Codex / GLM / Claude) —
> building a Maximo data application on top of this knowledge base.
>
> **Read this file first**, then follow the pointers below.

## 1. What this repository is

`maximo-knowledge` is a **read-only knowledge base** that maps the Maximo (IBM)
API surface available to this organization. It is **not an application**.

Its purpose: capture *what data Maximo exposes, how to read it safely, and what
it means* — so a downstream application (built elsewhere, by a human or an AI)
can **fetch/copy Maximo data into its own database** without ever mutating
production.

### Hard rules (non-negotiable)
- **READ ONLY for business data.** The sole POST exception is one controlled
  authentication handshake to the exact `/j_security_check` endpoint. No POST /
  PUT / PATCH / DELETE / MERGE is allowed against OSLC or business resources.
- No brute forcing paths, IDs, or credentials.
- No storing credentials, tokens, cookies, or Authorization headers anywhere.
- All saved samples are sanitized.
- If access behavior is uncertain, record it as `unknown` and stop.

These rules live in [`AGENTS.md`](./AGENTS.md) and are enforced in code by
`scripts/discover.py` (business GET / HEAD / OPTIONS only, with the exact
authentication exception).

## 2. How Maximo exposes data (the key mental model)

Maximo's OpenAPI document at `/oslc/oas` has an **empty `paths` object** — it is
not a full endpoint catalog. The real data surface is the **OSLC Object
Structure** API:

```
GET /oslc/os                         → list available object structures (catalog)
GET /oslc/os/{OBJECTSTRUCTURE}       → query records of one object structure
```

Examples of object structures: `MXASSET` (assets), `MXWODETAIL` (work orders),
`MXLOCATIONS` (locations). Query capabilities are passed as URL parameters:

| Capability | Parameter | Example |
|---|---|---|
| Filter | `oslc.where` | `oslc.where=assetnum="PUMP-1A"` |
| Sort | `oslc.orderBy` | `oslc.orderBy=-reportdate` |
| Field selection | `oslc.select` | `oslc.select=assetnum,description,status` |
| Pagination | `oslc.paging`, `pageno`, `pagesize` | `oslc.paging=true&pageno=1&pagesize=100` |

Response shape (Maximo OSLC flavor) wraps records under `_member`:

```json
{
  "oslc:responseInfo": {"oslc:totalCount": 123, "oslc:nextPage": "..."},
  "_member": [ { ...one record... } ]
}
```

> ⚠️ Everything in this section is **documented** OSLC behavior. The
> capability flags (filter/sort/pagination/field-selection) for *this specific
> instance* must be confirmed by discovery. See `discovery/capabilities.json`.

## 3. Repository map

| Path | What it is | When to read it |
|---|---|---|
| `CONTEXT.md` (this file) | AI/human entry point | First |
| `AGENTS.md` | Safety rules & discovery procedure | Before any work |
| `docs/authentication.md` | How to authenticate read-only | Before fetching |
| `docs/objects.md` | Business meaning of each object | When modeling data |
| `docs/relationships.md` | Verified entity relationships | When joining data |
| `docs/etl-playbook.md` | How to copy data into another DB | When building a fetcher |
| `docs/unit-specific.md` | Site/unit naming conventions | When filtering per unit |
| `discovery/object-structures.json` | Canonical object catalog | To know what exists |
| `discovery/objects/{name}.json` | Per-object fields, PK, pagination, sample | To map one object |
| `discovery/capabilities.json` | Verified OSLC capability flags | To know what queries work |
| `discovery/endpoints.json` | OAS endpoint catalog | For OAS-level endpoints |
| `samples/{name}.sample.json` | Sanitized response examples | To see response shape |
| `schemas/object.schema.json` | JSON Schema for per-object records | To validate/generate models |
| `schemas/endpoint.schema.json` | JSON Schema for endpoint records | To validate catalogs |
| `mappings/` | Unit/equipment semantic mappings | For local context |
| `scripts/discover.py` | Read-only discovery CLI | To run discovery |

## 4. Status vocabulary (read it before trusting data)

Every record carries a `status`:

- `unknown` — not tested. Do not rely on it.
- `documented` — present in docs/seed but not verified on this instance.
- `verified` — tested successfully with authorized read-only access. ✅ Trust this.
- `forbidden` — endpoint exists but the current account cannot access it.
- `deprecated` — known but should not be used.

> Rule of thumb for AI builders: only treat `verified` records as a reliable
> contract. Treat `documented`/`unknown` as *probably* correct but to be
> re-verified against the live instance.

## 5. Authentication for downstream applications

The downstream data-fetcher app must obtain an authenticated session and then
issue **GET-only** data requests (no data mutation). The chosen default is
**programmatic login**: POST `/j_security_check` once to obtain a session
cookie, then reuse it for GET-only OSLC requests.

A login POST is **authentication**, not data mutation — it does not create,
update, or delete any Maximo business data, so it is compatible with the
read-only intent. API key / Basic Auth are cleaner alternatives if the
administrator can enable them.

> **Important boundary:** this repository's own business discovery
> (`scripts/discover.py`, `scripts/session_discover.py`) stays GET/HEAD/OPTIONS
> only per AGENTS.md. `scripts/discover.py` may perform the exact
> authentication-only POST to `/j_security_check`; it may not POST anywhere
> else. Programmatic login in the downstream app follows the same boundary.

See [`docs/authentication.md`](./docs/authentication.md) for the full recipe,
session-expiry handling, and what never to store.

## 6. How to build a read-only data fetcher (AI workflow)

If you are an AI tool building the *other* application, follow this order:

1. Read this file, then [`docs/authentication.md`](./docs/authentication.md).
2. Read [`discovery/object-structures.json`](./discovery/object-structures.json)
   to see what is available and which objects are `verified`.
3. For each object you need, open
   `discovery/objects/{name}.json` for fields, primary key, and pagination.
4. Read [`docs/etl-playbook.md`](./docs/etl-playbook.md) for pagination,
   incremental sync, and **column → database mapping** examples.
5. Read [`docs/relationships.md`](./docs/relationships.md) to model joins.
6. Generate DB models from [`schemas/object.schema.json`](./schemas/object.schema.json).
7. Respect the hard rules in section 1. Read-only. Sanitize. Rate-limit.

## 7. Canonical object set (priority)

The reliability knowledge base prioritizes these object structures (mapped in
`discovery/object-structures.json` once verified):

| Resource | Object structure(s) | Reliability use |
|---|---|---|
| asset | MXASSET | asset reliability & history |
| workorder | MXWODETAIL, MXWORKORDER | work order history, failure analysis |
| location | MXLOCATIONS | location hierarchy, asset context |
| preventivemaintenance | MXPM | preventive maintenance analysis |
| failurecode | MXFAILURECODE | failure analysis |
| meter | MXMETER | condition monitoring |
| labor | MXLABOR, MXLABORCRAFT | work order resource analysis |
| materials | MXINVSTEM, MXINVENTORY, MXITEM | spare parts analysis |
| jobplan | MXJOBPLAN | maintenance planning |
| sr | MXSR, MXSERVICEITEM | service request tracking |
| person | MXPERSON | reporter / owner tracking |

Any additional object structures discovered via `/oslc/os` are also cataloged
and listed in `discovery/object-structures.json`.

## 8. Running discovery (operators only)

```bash
# Parse a local OAS fixture (no network)
python scripts/discover.py --oas-file openapi.json --scope reliability-core

# Enumerate OSLC object structures (GET-only, requires --execute)
python scripts/discover.py --enumerate-oslc --execute --scope reliability-core
python scripts/discover.py --enumerate-oslc --execute --resource asset workorder

# Interactive browser-session discovery (manual login, GET-only after)
python scripts/session_discover.py run --scope reliability-core --verify-samples
```

All network discovery requires explicit `--execute` and is limited to
GET / HEAD / OPTIONS.

## 9. Current maturity

- **Scope:** site **BSR** (org IP) — matches the read-only discovery account.
  All downstream queries must filter `oslc.where=siteid="BSR"`.
  See [`docs/unit-specific.md`](./docs/unit-specific.md).
- `discovery/oslc/catalog.json`: **462 object structures** from authenticated OAS.
- `discovery/object-structures.json`: 13 priority structures — **7 verified**
  (asset, workorder, person, item, labor, sr) with real field lists, **6
  forbidden** (account lacks object-level READ on failurecode, location, pm,
  meter, jobplan).
- `discovery/objects/*.json`: per-object records with verified fields, primary
  keys, and sanitized samples.
- `discovery/capabilities.json`: filtering, sorting, pagination, field
  selection, search — all **verified**.
- `docs/unit-specific.md`: BSR site identifiers, plant/unit naming, asset
  hierarchy conventions from real data.
