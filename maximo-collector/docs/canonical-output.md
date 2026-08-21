# MX-008R — Canonical Collector Output

The collector now has an explicit, non-persisting canonical boundary for the
NADI Reliability Contract v1. The boundary is implemented by
`src/services/canonical.py` and `src/adapters/maximo/canonical_mappers.py`.

## Flow

```text
Maximo OSLC GET
  -> existing OslcClient normalization/coercion
  -> allowlisted source mapper
  -> deterministic canonical identity + provenance
  -> cached JSON Schema validation
  -> CanonicalCollection (in-memory)
```

The existing Postgres sync path and its legacy `Equipment`/`WorkOrder` models
remain unchanged. MX-008R does not create Reliability Mart tables. A future
consumer can use `CanonicalCollector.collect_assets()`,
`collect_workorders()`, `collect_fmea()`, `collect_rcfa()`, `collect_bhm()`,
`collect_overhauls()` or `collect_all()`.

## Sources and safety

The canonical source allowlist contains only `mxasset`, `mxwodetail`, `ipfmea`,
`iprcfa`, `ipbhm`, and `ip_dom_oh`. Every query uses the fixed `siteid="BSR"`
scope; the asset unit and Work Order prefix are also checked. The existing
GET-only OSLC client, authentication, rate limiting, response cap, pagination,
same-origin protection, and session-expiry handling are reused.

The four MX-007R deferred resources are not configured and cannot be collected
through this interface.

## Identity and provenance

Canonical IDs use a deterministic scoped representation:

```text
<namespace>:MAXIMO:<source_object>:<site>:<organization>:<source_record_id>
```

The source record ID is separate from source number and relationship references.
`siteid`, `orgid`, `assetnum`, and `wonum` are never silently promoted to an
unscoped record identity.

Every output includes `contract_version: "1.0"`, a uniform provenance block,
and an allowlisted `sources.maximo` block. Raw payloads, hrefs, collection
references, credentials, and person identifiers do not cross the boundary.

## Relationships

- IPFMEA asset and IPBHM asset are `DIRECT_VERIFIED` references.
- IP_DOM_OH `wonum` is a `DIRECT_VERIFIED` Work Order reference.
- IP_DOM_OH asset is resolved only from an already fetched Work Order via
  `IP_DOM_OH.wonum -> MXWODETAIL.wonum -> MXWODETAIL.assetnum`.
- Missing Work Orders leave Overhaul `asset_ref` null and do not trigger a
  Maximo lookup.
- RCFA asset, location, Work Order, and failure-event links remain null with
  `UNRESOLVED` evidence.

## Validation and errors

JSON Schema validators are cached by canonical entity. The canonical collector
isolates malformed rows and increments mapping/validation counters without
logging payload values. It does not write invalid records. The committed
mapping file is checked once when the collector is constructed; required
identity and relationship mappings failing that check raise a mapping-drift
error before collection starts.

`maintenance-event.schema.json` retains its legacy required shape. Source
`worktype` is preserved in the canonical `work_type` field and Maximo source
quarantine; the legacy `event_type` is populated only when its existing enum
accepts the value.

## MX-009R handoff

MX-009R may persist `CanonicalCollection.records` after choosing an upsert and
deduplication strategy. It should preserve canonical IDs, provenance,
relationship evidence, and nullability. Deferred source contracts remain out
of the v1 persistence path.
