# MX-008S — Bounded Live Canonical Smoke Verification

Date: 2026-08-21

This report records sanitized structural evidence only. No production record
identifiers, descriptions, cookies, credentials, or raw Maximo responses are
stored here.

## Scope and safety

- Authentication: one in-memory form-login session (`POST /j_security_check`).
- Business methods: `GET` only.
- Scope: `siteid="BSR"`, organization `IP`.
- Business requests: 6; one bounded collection request per resource.
- Maximum records consumed per resource: 1.
- Pagination beyond the first page: none.
- Response cap: unchanged at 1 MiB.
- Concurrency: 1.
- Deferred resources requested: none.
- Cross-origin requests: none.
- Raw production payload persisted: no.

## Results

| Source | Canonical entity | Source read | Emitted | Schema | Structural result |
| --- | --- | ---: | ---: | --- | --- |
| MXASSET | `asset_master` | 1 | 1 | PASS | Canonical ID, scoped source asset number, provenance, BSR/IP scope present. |
| MXWODETAIL | `maintenance_event` | 1 | 1 | PASS | Canonical ID, scoped `work_order_id`, equipment reference, provenance, BSR/IP scope present. |
| IPFMEA | `fmea_assessment` | 1 | 1 | PASS | Asset reference present with `DIRECT_VERIFIED` evidence; failure-code reference handled. |
| IPRCFA | `rcfa_analysis` | 1 | 1 | PASS | Asset, location, Work Order, and failure-event references remain null; evidence is `UNRESOLVED`. |
| IPBHM | `asset_health_assessment` | 1 | 1 | PASS | Asset reference present; `eid` remains an approved Maximo source attribute and is not identity. |
| IP_DOM_OH | `overhaul_event` | 1 | 1 | PASS | Work Order reference is `DIRECT_VERIFIED`; unresolved source attributes are preserved. |

All six records had `contract_version = "1.0"`, a canonical ID, MAXIMO
provenance, and BSR/IP scope evidence. No mapping or schema-validation errors
occurred.

## Reference integrity

- Asset reference namespace is consistent across the live FMEA, BHM, and Work
  Order outputs with the `asset_master` scoped identity domain.
- Work Order reference namespace is consistent: `overhaul_event.workorder_ref`
  targets the same scoped Work Order identity domain as
  `maintenance_event.work_order_id`, not the maintenance event canonical ID.
- The bounded Work Order sample did not naturally match the bounded Overhaul
  sample. Therefore the live run did not claim an Overhaul-to-Asset join.
- The existing synthetic derived-path test proves the allowed path:
  `IP_DOM_OH.wonum → MXWODETAIL.wonum → MXWODETAIL.assetnum → asset_master`.
- No canonical identity collision was observed.

## Error classification

No `AUTH_FAILURE`, `TRANSPORT_FAILURE`, `SOURCE_CONTRACT_DRIFT`,
`MAPPING_FAILURE`, `SCHEMA_VALIDATION_FAILURE`, or `RESPONSE_CAP_BLOCKED`
condition occurred.

## Test evidence

- Collector tests before live: 69/69 passed.
- Canonical contract tests before live: 5/5 passed.
- Live canonical outputs: 6/6 schema-valid.
- HTTP status summary: 7 × 200 (one authentication response and six business responses).
- HTTP 429: 0.
- HTTP 5xx: 0.

## MX-009R interpretation

The six canonical runtime paths are live-verified for bounded read-only
execution and schema validation. Overhaul asset resolution remains a
non-blocking derived relationship whose matching behavior is covered by
synthetic tests; this smoke run did not perform an N+1 lookup.
