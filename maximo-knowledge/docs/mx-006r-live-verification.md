# MX-006R Live Verification Report

## Status

`PARTIAL`

MX-006A authentication parity succeeded on the isolated MX-006A branch, so
the bounded MX-006R verification resumed immediately. All live calls were
single-threaded, restricted to site `BSR`, limited to one sample, and paced at
least five seconds apart. No raw production response was saved.

The machine-readable matrix is
[`discovery/mx-006r-live-verification.json`](../discovery/mx-006r-live-verification.json).

The authentication smoke test performed one controlled form login and one
`GET` of one `MXASSET` record. It returned HTTP 200 JSON. The bounded P0 run
used a separate in-memory session and performed one GET per 16 locally
catalogued targets. This resulted in two authentication POSTs overall (one
per short-lived process), with no session-expiry retry.

## Core credential delta

| Resource | Previous status | MX-006R status | Changed? |
|---|---|---|---|
| `mxapifailurecode` | FORBIDDEN | UNKNOWN — controlled query HTTP 400 | NO CONCLUSION |
| `mxapilocation` | FORBIDDEN | UNKNOWN — controlled query HTTP 400 | NO CONCLUSION |
| `mxapipm` | FORBIDDEN | UNKNOWN — controlled query HTTP 400 | NO CONCLUSION |
| `mxapimeter` | FORBIDDEN | UNKNOWN — controlled query HTTP 400 | NO CONCLUSION |
| `mxapijobplan` | FORBIDDEN | UNKNOWN — controlled query HTTP 400 | NO CONCLUSION |

The 400 responses were not treated as `FORBIDDEN`: the BSR `siteid` query was
rejected before a permission or object-field conclusion could be made. No
additional live request was made to broaden scope or bypass that result.

## Live verification matrix

| Resource | Live status | HTTP | Samples | Response evidence | Asset/location/site/WO/time |
|---|---:|---:|---:|---|---|
| `IPFMEA` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `IPFMEAITEM` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `IPRCFA` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `IPRCFAFDT` | UNKNOWN | 400 | 0 | BSR-scoped query rejected | UNKNOWN |
| `IPBHM` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `IPBHMMEASUREMENT` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `IPMSMSFAILUREMECHANI` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `DMD_OPLOGABN` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `IP_DOM_OH` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `DOM_INSPEKSIMESIN` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |
| `IP_DOM_OH_SCOPE_PM` | PARTIAL | 200 | 1 | JSON member exposed only `href` in lean response | UNKNOWN |

The endpoint-access results are useful, but `PARTIAL` is intentional: a
collection `href` proves the resource is reachable, not the business schema,
record grain, primary key, or relationship. The lean response did not expose
those fields, so no field or join was guessed.

The core objects `MXAPIFAILURECODE`, `MXAPILOCATION`, `MXAPIPM`,
`MXAPIMETER`, and `MXAPIJOBPLAN` plus `IPRCFAFDT` returned HTTP 400 under the
safe BSR query. They remain unresolved rather than being promoted to
`FORBIDDEN`.

## NADI interpretation

Current candidates remain:

- **NADI CORE CANDIDATE:** `IPFMEA`, `IPFMEAITEM`, `IPRCFA`, `IPBHM`,
  `IPBHMMEASUREMENT`, `IPMSMSFAILUREMECHANI`, `IP_DOM_OH`,
  `DOM_INSPEKSIMESIN`.
- **NADI SUPPORTING CANDIDATE:** `DMD_OPLOGABN`, `IP_DOM_OH_SCOPE_PM`.
- **UNRESOLVED:** all joins and exact fields until a minimally selected
  business response can be obtained safely.

DIAMOND header/detail resources and Efficiency Management resources were not
probed after the P0 requests. Maintenance Strategy, OEE, Pareto Loss Output,
Engineering Service Sheet, and Performance Test remain `UNKNOWN`.

## Request safety

| Metric | Result |
|---|---:|
| Total Maximo requests | 19 |
| Authentication POSTs | 2 |
| Business GETs | 17 |
| Successful | 13 |
| HTTP 400 | 6 |
| HTTP 401/403/404 | 0 |
| HTTP 429 | 0 |
| HTTP 5xx | 0 |
| Maximum concurrency | 1 |
| Minimum interval | 5 seconds |
| Largest sample | 1 record |
| Cross-site samples | 0 |
| Request budget exceeded | NO |

No authentication POST was a retry after expiry. No credentials, cookies,
session IDs, raw responses, personal data, or cross-site records were written.

## Follow-up

`MX-007R` is **not ready**. A future bounded verification should first obtain
schema fields for the reachable P0 resources using a documented minimal
selection or an approved resource-specific detail read, then prove the exact
asset/location/site/time and Work Order joins. It must keep one request active
at a time, preserve the BSR scope, and stop on 429 or repeated 5xx.

## MX-006B bounded detail follow-up

MX-006B added the reusable `--verify-detail` path in
[`scripts/discover.py`](../scripts/discover.py). It performs one BSR-scoped
collection GET, follows at most one explicitly recognized `href`/
`rdf:resource`/`resource`/`@id` link, validates the configured HTTP origin
before transmission, and stops at depth one. It does not follow pagination,
collection references, children, attachments, or related records.

The final bounded run used six short-lived in-memory form-auth sessions, 37
business GETs, and no business POST. Five resources produced meaningful detail
contracts from an earlier lean response:

| Resource | Detail | Verified structure |
|---|---:|---|
| `IPFMEA` | 200 | FMEA/status/description, `assetnum`, `siteid`, `orgid`, revision and timestamps |
| `IPRCFA` | 200 | RCFA/status/category, `siteid`, `orgid`, timestamps; asset/WO joins UNKNOWN |
| `IPBHM` | 200 | BHM identifier/status, `assetnum`, `siteid`, `orgid`, timestamps |
| `IP_DOM_OH` | 200 | OH identifiers/status, `wonum`, `siteid`, `orgid`, start/finish/change dates |
| `DOM_INSPEKSIMESIN` | 200 | inspection identifiers/status, `siteid`, description, measurement/range fields |

`IPFMEAITEM`, `IPBHMMEASUREMENT`, and `DMD_OPLOGABN` exceeded the mandatory
1 MiB response cap before a collection member could be safely read, including
the observed `href` projection. They remain `UNKNOWN` for fields and joins;
no alternate scope field or broad query was guessed. The six prior HTTP-400
resources were queried once more with the existing BSR clause and retain
sanitized diagnostics only; HTTP 400 was not reclassified as `FORBIDDEN`.

Detail artifacts use field names, lightweight types, metadata names, candidate
keys, relationship evidence, and type placeholders. They contain no raw
production values, cookies, credentials, personal data, or resource IDs.
