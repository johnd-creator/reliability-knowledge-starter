# Maximo Collector Data Explorer

MX-010D adds an engineering-facing Explorer to the existing Maximo Collector
web application at `/data-explorer`.

## What it shows

The page has two deliberately separate views:

* **Downloaded Source Data** — the allowlisted Maximo fields selected by the
  committed `CanonicalSourceConfig.select` projections and retained in the
  canonical record's approved `sources.maximo` block.
* **Reliability Mart** — the six canonical Contract v1 records after mapping.

Source Data is not a complete OSLC response. The Explorer never stores or
returns raw OSLC payloads, hrefs, collection references, credentials, cookies,
or arbitrary JSON keys. A source preview is constructed by an explicit
per-resource field allowlist.

Supported source resources:

| Source object | UI label | Canonical target |
| --- | --- | --- |
| `MXASSET` | Asset | `asset_master` |
| `MXWODETAIL` | Work Orders | `maintenance_event` |
| `IPFMEA` | FMEA | `fmea_assessment` |
| `IPRCFA` | RCFA | `rcfa_analysis` |
| `IPBHM` | Asset Health / BHM | `asset_health_assessment` |
| `IP_DOM_OH` | Overhaul / DOMINION | `overhaul_event` |

`IPFMEAITEM`, `IPBHMMEASUREMENT`, `DMD_OPLOGABN`, and
`IPMSMSFAILUREMECHANI` are shown only as deferred resources. They have no
browse route or production download button.

## API boundary

The page uses the existing Next.js `/api/collector` rewrite and the same
Collector FastAPI process. The new endpoints are GET-only:

```text
GET /data-explorer/resources
GET /data-explorer/resources/{resource}
GET /data-explorer/resources/{resource}/records
GET /data-explorer/resources/{resource}/records/{canonical_id}
GET /data-explorer/mart/{entity}
GET /data-explorer/mart/{entity}/{canonical_id}
GET /data-explorer/mappings/{resource}
GET /data-explorer/integrity
```

Resources and Mart entities are allowlisted in
`src/services/data_explorer.py`; arbitrary object structures, table names,
SQL, and OSLC query clauses are not accepted. List endpoints use offset/limit
pagination with a default of 50 and a maximum of 200, plus a small sort
allowlist.

All Mart queries retain the Collector's BSR/IP scope. Record details expose
safe provenance and relationship evidence for engineering inspection, while
the canonical payload excludes the raw `sources` block. The Source Data tab
shows only the selected fields, so adding an unrelated key to upstream JSON
does not widen the browser response.

The integrity endpoint reuses the Mart logical-reference audit and returns
aggregate resolved/unresolved counts for Asset and Work Order references. It
does not expose record identifiers or raw source values.

## Empty Mart behavior

Before MX-011R performs an initial production load, counts can legitimately be
zero. The UI marks a resource `CONFIGURED_EMPTY` and explains:

> No records loaded into Reliability Mart yet. The Collector/Contract is
> configured, but the production initial load has not been executed.

After MartWriter inserts records, the Explorer reads the existing tables and
counts automatically; no frontend redesign or separate staging database is
required.

## Running locally

Start the Collector API using its existing command, then start the existing web
application:

```bash
cd maximo-collector
.venv/bin/mxcollector serve

cd web
npm run dev
```

The web proxy defaults to `http://127.0.0.1:8002` and can be changed with
`MAXIMO_COLLECTOR_API_BASE` in the existing ignored `.env.local`.

MX-010D does not trigger Maximo synchronization, production loading, or any
business write. Existing sync controls remain separate and retain their
authentication/read-only safeguards.
