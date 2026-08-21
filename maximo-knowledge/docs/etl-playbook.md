# ETL Playbook — Copying Maximo data to another database

> **Audience:** AI tools (Codex/GLM) and humans building the downstream
> application that fetches/copies Maximo data into its own database.
>
> **Hard constraint:** read-only. This playbook describes *fetch and copy* only.
> The sole POST exception is the authentication handshake at the exact
> `/j_security_check` endpoint; no POST / PUT / PATCH / DELETE / MERGE is
> allowed against business resources.

Read [`CONTEXT.md`](../CONTEXT.md) and [`authentication.md`](./authentication.md)
first.

## 1. The fetch loop (one object structure)

For each object structure in `discovery/object-structures.json`:

```
1. Determine the canonical endpoint: GET /oslc/os/{OBJECTSTRUCTURE}
2. Obtain a session. Default = programmatic login (POST /j_security_check once,
   reuse the session cookie); alternative = API key / Basic Auth if the admin
   has enabled them. See authentication.md.
3. Request one minimal record to confirm access and learn the response shape:
     GET /oslc/os/{OBJECTSTRUCTURE}?_maxitems=1
4. Page through the full collection (section 2).
5. Map each record to your DB schema (section 4).
6. Repeat on a schedule using incremental filters (section 3).
```

Always honor the per-object `status` in `discovery/objects/{name}.json`. Only
`verified` objects are a reliable contract.

## 2. Pagination

Maximo OSLC pagination uses these query parameters:

| Parameter | Purpose |
|---|---|
| `oslc.paging=true` | Enable OSLC paging |
| `pageno` | 1-based page number |
| `pagesize` | Page size (respect server limits; start small) |

The response advertises the next page via `oslc:responseInfo.oslc:nextPage` and
the total via `oslc:responseInfo.oslc:totalCount`. Treat both as hints — drive
the loop off the presence of `nextPage`/`_member` rather than the count alone.

Recommended loop:

```
pageno = 1
loop:
    GET /oslc/os/{OS}?oslc.paging=true&pageno={pageno}&pagesize={pagesize}
    members = response._member
    if members is empty: break
    persist(members)
    if not response["oslc:responseInfo"]["oslc:nextPage"]: break
    pageno += 1
    sleep(rate_limit)            # see section 5
```

> Verify the exact paging parameter names against this instance before relying
> on them. See `discovery/capabilities.json` → `pagination`.

## 3. Incremental / delta sync

To avoid re-fetching the whole collection each run, filter by a modification
timestamp. Candidate fields (verify per object in `discovery/objects/{name}.json`):

| Object | Typical delta field | Meaning |
|---|---|---|
| workorder | `changedate`, `reportdate` | record modified / reported |
| asset | `changedate` | record modified |
| pm | `changedate` | record modified |

### Site filter (mandatory for this knowledge base)

All queries are scoped to **site BSR** (org IP), matching the discovery
account. Always include the site filter:

```text
GET /oslc/os/{OS}?oslc.where=siteid="BSR"
```

Delta query example (site + incremental timestamp):

```
GET /oslc/os/MXWODETAIL?oslc.where=siteid="BSR" and changedate>"2026-08-11T00:00:00"
```

Persist the high-water mark (max `changedate` seen) after each successful run,
and request `changedate>"{last_watermark}"` on the next run. Store the
watermark in the downstream DB, not in this knowledge base.

> ⚠️ Filter capability (`oslc.where`) must be `verified` in
> `discovery/capabilities.json` before relying on incremental sync.

## 4. Column → database mapping

For each object, define a deterministic mapping from the Maximo field to your DB
column. Use `primary_key` from `discovery/objects/{name}.json` as the natural
key for upsert.

### Template (fill per object)

| Maximo field | DB column | Type | Notes |
|---|---|---|---|
| `<primary_key>` | `{resource}_natural_id` | string | natural key; upsert on this |
| `description` | `description` | string | |
| `status` | `status` | string | enumerate per object |
| `changedate` | `source_changed_at` | timestamp | delta watermark |
| `_rowstamp` | `source_rowstamp` | string | Maximo version token; skip if null |

### Naming conventions for the downstream DB

- Use `snake_case` for DB columns (Maximo fields are lowercase already).
- Keep Maximo field names as-is when unambiguous (`assetnum` → `assetnum`); only
  rename when it collides or obscures meaning.
- Prefix source-tracking columns with `source_` (`source_changed_at`,
  `source_rowstamp`, `source_object_structure`).
- Redact or drop sensitive/personal fields (see section 6) before persisting.

### Worked example — work order (illustrative, verify fields first)

Assuming `MXWODETAIL` returns `_member` records shaped like:

```json
{
  "wonum": "WO-1234",
  "assetnum": "PUMP-1A",
  "location": "BRAY-1",
  "status": "COMP",
  "worktype": "CM",
  "reportdate": "2026-01-01T00:00:00+07:00",
  "changedate": "2026-01-03T08:00:00+07:00"
}
```

Mapping:

| Maximo field | DB column |
|---|---|
| `wonum` | `work_order_num` (natural key) |
| `assetnum` | `asset_num` |
| `location` | `location_code` |
| `status` | `status` |
| `worktype` | `work_type` |
| `reportdate` | `reported_at` |
| `changedate` | `source_changed_at` (watermark) |

Insert/upsert pseudo-SQL:

```sql
INSERT INTO work_order
  (work_order_num, asset_num, location_code, status, work_type,
   reported_at, source_changed_at, source_object_structure)
VALUES ($1, $2, $3, $4, $5, $6, $7, 'MXWODETAIL')
ON CONFLICT (work_order_num) DO UPDATE SET
  asset_num = EXCLUDED.asset_num,
  status = EXCLUDED.status,
  work_type = EXCLUDED.work_type,
  reported_at = EXCLUDED.reported_at,
  source_changed_at = EXCLUDED.source_changed_at
WHERE EXCLUDED.source_changed_at > work_order.source_changed_at;
```

## 5. Rate limiting & reliability

- Keep at least 1 second between requests by default
  (`MAXIMO_RATE_LIMIT_SECONDS=1`).
- Set a request timeout (`MAXIMO_TIMEOUT_SECONDS=30`).
- Cap response size you are willing to buffer (`MAXIMO_MAX_RESPONSE_BYTES`).
- Retry on 5xx with exponential backoff; do **not** retry by hammering.
- On 403, stop and record `forbidden`; do not treat as transient.

## 6. Sanitization before persisting

Before writing Maximo records to the downstream DB, redact or drop:

- fields matching `password|secret|token|authorization|cookie|session|csrf|apikey`
- personal fields (`email`, `phone`, `username`, …) unless explicitly approved
  and required.

The discovery CLI already applies this redaction to samples; mirror the same
rules in the fetcher. See `scripts/discover.py` → `sanitize()`.

## 7. Idempotency

The copy must be safe to re-run. Concretely:

- key every row on the Maximo natural key (`primary_key` per object);
- upsert, never blind insert;
- gate updates on `source_changed_at` so older events cannot clobber newer ones;
- keep `_rowstamp` to detect in-place version changes if `changedate` is absent.

## 8. What this knowledge base does NOT cover

- Writing back to Maximo (forbidden by policy).
- Real-time streaming. This is batch/poll-based copy.
- Business rules or transformations specific to your downstream application —
  apply those in the downstream app, not here.
