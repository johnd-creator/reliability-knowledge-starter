# MX-011R Controlled Initial Mart Load

Date: 2026-08-21

This run used the existing Maximo Collector pipeline with production scope
`BSR/IP`:

```text
Maximo → OslcClient → CanonicalCollector → Contract v1 → MartWriter
```

No raw response, export, screenshot, credential, cookie, or production record
value is stored in this report.

## Controlled profile

| Source | Source ceiling | Effective page ceiling |
| --- | ---: | ---: |
| MXASSET | 300 | 3 |
| MXWODETAIL | 500 | 20 |
| IPFMEA | 100 | 1 |
| IPBHM | 100 | 1 |
| IPRCFA | 100 | 1 |
| IP_DOM_OH | 100 | 1 |

The business request ceiling was 100 per process. Maximo access used one
session, one concurrent execution, GET-only business requests, and the
existing response-size/rate-limit guards.

## Dry-run

The six-resource dry-run used a source ceiling of 3 and one page per resource.
It made 6 business requests, all HTTP 200, and performed no Mart writes.

| Source | Read | Emitted | Skipped | Result |
| --- | ---: | ---: | ---: | --- |
| MXASSET | 3 | 3 | 0 | CAPPED |
| MXWODETAIL | 3 | 2 | 1 | CAPPED |
| IPFMEA | 3 | 3 | 0 | CAPPED |
| IPBHM | 3 | 3 | 0 | CAPPED |
| IPRCFA | 3 | 3 | 0 | CAPPED |
| IP_DOM_OH | 1 | 1 | 0 | EXHAUSTED |

The dry-run gate passed: no authentication, scope, contract, response-cap,
429, or repeated-5xx failure occurred.

## Successful initial load

The final controlled run made 27 business requests, all HTTP 200. It used
resource-level Mart transactions and did not update any SyncCursor.

| Source → Mart entity | Read | Emitted | Inserted | Updated | Unchanged | Skipped | Pages | Result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| MXASSET → asset_master | 300 | 276 | 0 | 4 | 272 | 24 | 3 | CAPPED |
| MXWODETAIL → maintenance_event | 500 | 174 | 174 | 0 | 0 | 326 | 20 | CAPPED |
| IPFMEA → fmea_assessment | 100 | 100 | 100 | 0 | 0 | 0 | 1 | CAPPED |
| IPBHM → asset_health_assessment | 100 | 100 | 100 | 0 | 0 | 0 | 1 | CAPPED |
| IPRCFA → rcfa_analysis | 100 | 100 | 100 | 0 | 0 | 0 | 1 | CAPPED |
| IP_DOM_OH → overhaul_event | 1 | 1 | 1 | 0 | 0 | 0 | 1 | EXHAUSTED |

Work Order source rows included mapping skips; no source cap was exceeded.
Repeated canonical IDs within the bounded Work Order batch are de-duplicated
before MartWriter, while the source-read count remains unchanged.

An initial attempt stopped after the Asset transaction because the existing
`collect_run.mode` column is `VARCHAR(20)`. The controlled run marker was
shortened to `mart-initial`, and the complete run was rerun safely through the
canonical upsert path.

## Mart counts after load

All counts are BSR/IP-scoped:

| Entity | Before | After | Delta |
| --- | ---: | ---: | ---: |
| asset_master | 0 | 277 | +277 |
| maintenance_event | 0 | 174 | +174 |
| fmea_assessment | 0 | 100 | +100 |
| asset_health_assessment | 0 | 100 | +100 |
| rcfa_analysis | 0 | 100 | +100 |
| overhaul_event | 0 | 1 | +1 |

## Idempotency retry

`IPFMEA` was rerun with an explicit 10-source-record cap:

```text
read=10, emitted=10, inserted=0, updated=0, unchanged=10,
duplicate rows=0, pages=1, result=CAPPED
```

The retry made one HTTP 200 business request and did not create or advance a
SyncCursor.

## Integrity audit

The existing `MartIntegrityAuditor` reported aggregate counts only:

```text
asset references:    357 total, 48 resolved, 309 unresolved
Work Order refs:       1 total,  0 resolved,   1 unresolved
```

Unresolved references are retained intentionally. RCFA asset/location/Work
Order relationships remain unresolved by Contract v1. No direct Overhaul asset
inference was added; the bounded Overhaul record has no resolved Work Order
target in the retained Work Order sample.

## Data Explorer verification

The current API implementation was run on a temporary local port because an
older Collector API process already occupied port 8002 and returned 404 for
the new route. Against the current code, all six resources were non-empty and
the following checks passed without printing record values:

- `/data-explorer/resources` returned six `READY` resources;
- `/data-explorer/integrity` returned 200;
- all six Mart list views returned records;
- all six Source Data views returned records through the approved source-field
  allowlist;
- all six detail views returned mapping, provenance, and relationship evidence.

Restart the existing Collector API process on port 8002 before opening the
normal web proxy so it loads the current MX-010D code. No Maximo sync is
triggered by the Explorer.

## Safety outcome

- Maximo business writes: none;
- HTTP 429: none;
- HTTP 5xx: none;
- response-cap blocks: none;
- production data committed to Git: none;
- canonical contract changes: none;
- deferred resources requested: none;
- SyncCursor modified by MX-011R: no.
