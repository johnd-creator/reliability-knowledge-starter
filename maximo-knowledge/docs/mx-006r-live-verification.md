# MX-006R Live Verification Report

## Status

`PARTIAL`

The hard start gate passed and the isolated branch was created from the clean
MX-005R HEAD. Live verification did not start because no approved authenticated
browser session was available.

`maximo-knowledge/.env` is configured for `form` authentication. The approved
discovery CLI allows only GET/HEAD/OPTIONS and intentionally refuses to automate
`POST /j_security_check`. The available browser context was `about:blank`; no
operator-authenticated Maximo session existed. No alternate authentication was
invented and no Maximo request was issued.

The machine-readable matrix is
[`discovery/mx-006r-live-verification.json`](../discovery/mx-006r-live-verification.json).

## Core credential delta

| Resource | Previous status | MX-006R status | Changed? |
|---|---|---|---|
| `mxapifailurecode` | FORBIDDEN | UNKNOWN — AUTHENTICATION REQUIRED | UNKNOWN |
| `mxapilocation` | FORBIDDEN | UNKNOWN — AUTHENTICATION REQUIRED | UNKNOWN |
| `mxapipm` | FORBIDDEN | UNKNOWN — AUTHENTICATION REQUIRED | UNKNOWN |
| `mxapimeter` | FORBIDDEN | UNKNOWN — AUTHENTICATION REQUIRED | UNKNOWN |
| `mxapijobplan` | FORBIDDEN | UNKNOWN — AUTHENTICATION REQUIRED | UNKNOWN |

No previous permission assumption was promoted or downgraded without a live
GET.

## Live verification matrix

| Resource | Live status | Primary key | Asset | Location | Site | WO | Timestamp | NADI relevance | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| `IPFMEA` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `IPFMEAITEM` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `IPRCFA` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `IPRCFAFDT` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | MX-005R catalog only |
| `IPBHM` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `IPBHMMEASUREMENT` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `IPMSMSFAILUREMECHANI` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `DMD_OPLOGABN` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI SUPPORTING CANDIDATE | MX-005R catalog only |
| `IP_DOM_OH` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `DOM_INSPEKSIMESIN` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `IP_DOM_OH_SCOPE_PM` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NADI CORE CANDIDATE | MX-005R catalog only |
| `IPEMLGWR` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | MX-005R catalog only |
| `IPEMMP/IPEMMPDTL` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | MX-005R catalog only |
| `IPEMFB/IPEMFBDTL` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | MX-005R catalog only |

These are candidates, not verified NADI contracts.

## Required answers still unresolved

- Previously forbidden core-object accessibility: UNKNOWN.
- FMEA/RCFA/BHM keys and asset/location/site joins: UNKNOWN.
- `IPBHMMEASUREMENT` condition semantics: UNKNOWN.
- `DMD_OPLOGABN` asset/location/time correlation: UNKNOWN.
- DOMINION overhaul/inspection joins to assets and standard Work Orders: UNKNOWN.
- Efficiency Management meaning and Performance Test mapping: UNKNOWN.
- Maintenance Strategy, OEE, Pareto Loss Output, and Engineering Service Sheet: UNKNOWN.

## Request safety

| Metric | Result |
|---|---:|
| Total Maximo requests | 0 |
| Successful | 0 |
| 401/403 | 0 |
| 404 | 0 |
| 429 | 0 |
| 5xx | 0 |
| Maximum concurrency | 0 |
| Minimum interval | N/A |
| Largest sample size | 0 |
| Cross-site samples | 0 |
| Request budget exceeded | NO |

## Follow-up

`MX-007R` should begin only after an operator completes the approved manual
Maximo browser login and confirms the in-memory session is available. Then run
the P0 matrix in order, with one BSR-scoped minimal GET at a time, 5–8 seconds
between requests, and no raw response persistence.
