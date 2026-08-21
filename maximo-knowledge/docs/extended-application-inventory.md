# Maximo Extended Application Inventory

MX-005R records the metadata already present in the authenticated-OAS object
structure catalog for Reliability, DIAMOND, DOMINION, and Efficiency
Management. These are Maximo applications/modules, not external systems.

## Evidence boundary

The local catalog at `discovery/oslc/catalog.json` contains 462 object
structures and provides names, labels, OSLC endpoint patterns, and documented
support for filter, sort, paging, and select. It does not provide field-level
schemas or relationship definitions for these extensions.

The configured `maximo-knowledge/.env` uses form authentication. The
knowledge-repository discovery CLI is intentionally GET/HEAD/OPTIONS-only for
business data; one in-memory `POST /j_security_check` is permitted for the
bounded MX-006B follow-up. MX-005R itself made zero live Maximo requests.
The MX-006B detail records below promote only directly observed field names;
all fields and joins not present in those records remain `UNKNOWN`.
The machine-readable records are in
[`discovery/extended-applications.json`](../discovery/extended-applications.json).

## Summary matrix

| Application | Object structures / API resources from local catalog | NADI relevance | Confidence |
|---|---|---:|---|
| Reliability — FMEA | `IPFMEA`, `IPFMEAITEM`, `IPFMEAWORKSHOP` | HIGH | PARTIAL |
| Reliability — RCFA | `IPRCFA`, `IPRCFAFDT`, `IPRCFAWORKSHOP` | HIGH | PARTIAL |
| Reliability — BHM / failure mechanism | `IPBHM`, `IPBHMLINE`, `IPBHMMEASUREMENT`, `IPBHMWORKSHOP`, `IPMSMSFAILUREMECHANI` | HIGH | PARTIAL |
| Reliability — engineering judgement | `IPENGJUDGE` | POTENTIAL | PARTIAL |
| DIAMOND — logsheets | `DMDLOGSHEET`, `DMDLOGSHEETDTL`, `DMDLOGSHEETHDR`, `DMD_OPLOGABN`, `DMD_OPLOGINFO`, `DMD_OPOPLOG` | POTENTIAL/HIGH | PARTIAL |
| DOMINION — overhaul | `IP_DOM_OH`, `IP_DOM_OH_SCOPE_PM`, `IPPROJECTOH`, `DOM_INSPEKSIMESIN` | HIGH | PARTIAL |
| DOMINION — supporting master/scope | `DOM_MERKTIPE`, `DOM_PMLINE`, `DOM_SCOPEDETAILS`, `DOM_SCOPELINE`, `DOM_SCOPESTD`, `IPPERSONDOMOH` | POTENTIAL | PARTIAL |
| Efficiency Management — war room | `IPEMLGWR` | POTENTIAL | PARTIAL |
| Efficiency Management — formula/master parameters | `IPEMFB`, `IPEMFBDTL`, `IPEMMP`, `IPEMMPDTL` | POTENTIAL | PARTIAL |

All entries use the OSLC pattern `GET /oslc/os/{object_structure}`. The local
catalog marks these entries `documented`; its capability flags say filter,
sort, paging, and select are supported, but that behavior is not re-verified
for the extended resources in this task.

## Reliability findings

### FMEA and RCFA

The catalog names three FMEA resources and three RCFA resources, including
detail/workshop variants. They are high-value NADI candidates because their
labels directly describe failure-mode and root-cause workflows. The catalog
does not establish whether the parent key is an asset, location, work order,
or an extension identifier. A downstream contract must wait for a sanitized
minimal GET that exposes the keys and status/timestamp fields.

`IPPRONIAIFACE` (ProNIA–RCFA integration interface) is also present in the
catalog, but is not treated as a verified RCFA business record resource.

### BHM and failure mechanism

`IPBHM`, `IPBHMLINE`, `IPBHMMEASUREMENT`, and `IPBHMWORKSHOP` form a plausible
header/line/measurement/workshop family based on names only. `IPMSMSFAILUREMECHANI`
is a failure-mechanism candidate. It must not be conflated with the already
separately documented Maximo failure-code structures until fields and keys are
sampled.

No object named OEE, Pareto Loss Output, or Maintenance Strategy was identified
by the local catalog search. Those remain explicit `UNKNOWN` discovery targets.

## DIAMOND findings

DIAMOND is documented here as a Maximo module. The strongest logsheet
candidates are:

| Object structure | Endpoint | Why it matters | Asset/event relation |
|---|---|---|---|
| `DMDLOGSHEET` | `/oslc/os/dmdlogsheet` | logsheet candidate | UNKNOWN |
| `DMDLOGSHEETDTL` | `/oslc/os/dmdlogsheetdtl` | logsheet detail candidate | UNKNOWN |
| `DMDLOGSHEETHDR` | `/oslc/os/dmdlogsheethdr` | logsheet header candidate | UNKNOWN |
| `DMD_OPLOGABN` | `/oslc/os/dmd_oplogabn` | abnormal operator observation candidate | UNKNOWN |
| `DMD_OPLOGINFO` | `/oslc/os/dmd_oploginfo` | operator-log information candidate | UNKNOWN |
| `DMD_OPOPLOG` | `/oslc/os/dmd_opoplog` | operator-log candidate | UNKNOWN |

The local catalog cannot prove an asset, location, unit, shift, or event
timestamp field. Consequently NADI should treat DIAMOND observations as
potential reliability evidence only after a verified correlation key is found.

## DOMINION findings

The catalog supports the hypothesis that DOMINION contains overhaul planning,
scope, inspection, and manpower resources:

| Object structure | Endpoint | NADI use | Standard WORKORDER relation |
|---|---|---:|---|
| `IP_DOM_OH` | `/oslc/os/ip_dom_oh` | overhaul plan/schedule candidate | UNKNOWN |
| `IP_DOM_OH_SCOPE_PM` | `/oslc/os/ip_dom_oh_scope_pm` | overhaul scope/PM candidate | UNKNOWN |
| `IPPROJECTOH` | `/oslc/os/ipprojectoh` | overhaul project candidate | UNKNOWN |
| `DOM_INSPEKSIMESIN` | `/oslc/os/dom_inspeksimesin` | inspection/finding candidate | UNKNOWN |
| `DOM_PMLINE` | `/oslc/os/dom_pmline` | PM-to-scope mapping candidate | UNKNOWN |
| `DOM_SCOPEDETAILS` | `/oslc/os/dom_scopedetails` | scope detail candidate | UNKNOWN |
| `DOM_SCOPELINE` | `/oslc/os/dom_scopeline` | inspection scope line candidate | UNKNOWN |
| `DOM_SCOPESTD` | `/oslc/os/dom_scopestd` | standard scope candidate | UNKNOWN |
| `IPPERSONDOMOH` | `/oslc/os/ippersondomoh` | manpower context only | UNKNOWN |

This is enough to keep DOMINION in the Maximo conceptual model and to justify
future reliability-history discovery. It is not enough to claim that DOMINION
can currently supply asset overhaul history.

## Efficiency Management findings

The local catalog identifies `IPEMLGWR` (Logsheet War Room), `IPEMFB` and
`IPEMFBDTL` (Formula Baseline), and `IPEMMP` and `IPEMMPDTL` (Master
Parameter). These are potential candidates for decision support, but the
catalog does not establish whether values are performance tests, operating
targets, or master-data definitions. No resource explicitly named Performance
Test was found. No interpretation is made here.

## Relationship contract required before NADI use

For every candidate above, a future live read should request only a minimal,
sanitized sample and establish:

- primary key and record grain;
- status and important timestamps;
- asset, location, unit, site, and organization keys;
- relationship to standard `WORKORDER` or `MXWODETAIL`;
- parent/detail key for FMEA, RCFA, BHM, logsheet, or overhaul records.

Until then, these resources are Maximo knowledge only and must not be added to
the Cockpit or another ingestion contract.

## MX-006B verified detail contracts

The bounded follow-up used one collection record and at most one same-origin
detail record per explicit target. Five resources yielded structural contracts:

| Resource | Key candidate | Verified joins/fields | NADI classification |
|---|---|---|---|
| `IPFMEA` | `orgid` (CANDIDATE) | `assetnum`, `siteid`, `orgid`, `status`, revision, timestamps | CORE CANDIDATE |
| `IPRCFA` | `orgid` (CANDIDATE) | `siteid`, `orgid`, `status`, timestamps; asset/WO UNKNOWN | CORE CANDIDATE |
| `IPBHM` | `bhmid` (CANDIDATE) | `assetnum`, `siteid`, `orgid`, `status`, timestamps | CORE CANDIDATE |
| `IP_DOM_OH` | `wonum` (CANDIDATE) | `wonum`, `siteid`, `orgid`, status, start/finish/change dates | CORE CANDIDATE |
| `DOM_INSPEKSIMESIN` | `dom_inspeksinum` (CANDIDATE) | inspection identifier, `siteid`, status, description and measurement fields | SUPPORTING CANDIDATE |

`IPFMEAITEM`, `IPBHMMEASUREMENT`, and `DMD_OPLOGABN` exceeded the 1 MiB
response cap before a safe member could be obtained. They remain unresolved;
the tool did not broaden the query or try alternative scope names. The full
sanitized records are in `discovery/objects/`, and the six HTTP-400 follow-ups
are recorded as diagnostics without a permission conclusion.

## MX-005R request audit

| Metric | Result |
|---|---:|
| Total Maximo requests | 0 |
| Successful | 0 |
| HTTP 401/403 | 0 |
| HTTP 404 | 0 |
| HTTP 429 | 0 |
| HTTP 5xx | 0 |
| Other | 0 |
| Maximum concurrency | 0 |
| Minimum interval | N/A |
| Budget exceeded | NO |

The zero-request result is intentional: form-login credentials were present,
but this repository's discovery boundary does not permit automating the login
POST. No production data, credentials, cookies, or raw responses were saved.
