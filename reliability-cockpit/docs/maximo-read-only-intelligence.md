# Bundle B — Maximo read-only coverage and collection proposal

Local repository audit at main `02e887c56057611f112b7b652ba9a9aee8b382ea`.
AVAILABLE_AND_COLLECTED describes implemented collector/local projection paths,
not a new runtime population/permission certification. Source GETs in this audit: 0.
Historical verified catalogs are the authority; a catalog label or HTTP400 alone
is not proof of permission denial. Field availability is not semantic acceptance.

| Domain | Classification | Exact local evidence / mapping / limitation |
|---|---|---|
| Asset master/hierarchy | AVAILABLE_AND_COLLECTED | verified mxapiasset/mxasset; equipment parent/ancestor, exact scoped assetnum, canonical asset_master; registry membership remains controlled |
| Equipment specifications/classifications | AVAILABLE_NOT_COLLECTED / ENDPOINT_UNVERIFIED | assettype/manufacturer are collected scalars; richer specification relationships lack an approved collector contract; no inferred specification endpoint |
| Existing WO/status | AVAILABLE_AND_COLLECTED | verified mxwodetail; work_order and maintenance_event preserve raw status; WO is never an application command |
| WO history | AVAILABLE_AND_COLLECTED / ENDPOINT_UNVERIFIED | stored WO versions/current change/execution fields; not a complete source status-transition ledger; separate transition collection is unverified |
| Failure/problem/cause/remedy | AVAILABLE_AND_COLLECTED / AVAILABLE_NOT_COLLECTED / ENDPOINT_UNVERIFIED | failurecode preserved; MX-015A direct problemcode/schema cause candidates; cause/remedy/event semantics unproven; failure master access remains unresolved |
| Job plans / PM | ENDPOINT_UNVERIFIED / NOT_AUTHORIZED | older standalone discovery denied direct master structures; current mxapijobplan/mxapipm catalog is documented/http400, not verified; WO fields are references, not masters |
| Execution history | AVAILABLE_AND_COLLECTED | mxwodetail actual start/finish, reporting, change times through canonical maintenance_event; no universal failure/completion inference |
| Labor/material | AVAILABLE_AND_COLLECTED / ENDPOINT_UNVERIFIED | verified mxapilabor and mxitem, collector master references; transaction-level actual materials/labor relationship not approved |
| Operator logsheets | AVAILABLE_NOT_COLLECTED / ENDPOINT_UNVERIFIED | DMD_OPLOGABN bounded verified evidence but deferred canonical contract; DMDLOGSHEET/DTL/HDR catalog candidates unverified; no collection in bundle |
| Asset↔WO | AVAILABLE_AND_COLLECTED | scoped assetnum/site/org through exact canonical resolver; unresolved refs remain unresolved, no name join |

References: `maximo-knowledge/discovery/object-structures.json`, per-object
`discovery/objects/*.json`, `docs/mx-015a-maintenance-failure-semantics.md`,
`docs/extended-application-inventory.md`; `reliability-data-contracts/mappings/maximo-nadi-reliability.json`;
collector `src/services/canonical.py`, `local_mart_projector.py`, `data_explorer.py`,
`src/adapters/maximo/mappers.py`, `src/services/workorder_recency.py`.

## Identity, chronology and acquisition controls

Source identities live under sources.maximo with object, record ID/number, site
BSR and organization IP. Asset scope additionally follows verified CS01 rules.
Canonical asset ID is registry-owned, not assetnum alone. Source updated/reported/
execution timestamps, collected/ingested timestamp and Mart projection timestamp
remain different; missing timestamps are unknown. Source status is informational.

OSLC paging follows returned approved same-origin links with rate/response/page/
request guards. Current WO acquisition is bounded newest-first with changedate
cursor, tie replay, frozen recovery floor and completeness verification. Partial
runs do not advance cursor. No bootstrap, recovery-floor deletion or backfill.
Other verified master resources use their existing changedate/statusdate strategy;
labor has no verified incremental watermark. Do not invent one.

## Separately approvable plan — NOT EXECUTED

For each newly requested domain obtain owner/read-account approval, exact verified
resource and fields, scoped keys, direct relationship evidence, pagination and
source-change semantics before implementing acquisition. Prefer existing exact
record links; define a small explicit GET/page budget and response cap, no broad
search. Stop on 401/403, contract drift, ambiguous identity or exhausted budget.
Retain sanitized evidence, decide canonical contract/version and incremental cursor
with engineers, test locally, then request distinct collection authority. No
new source acquisition is authorized here; no guessed endpoint is a plan input.
Failure occurrence, cause/remedy hierarchy and logsheet joins require business
validation even when a field can be read. Personal labor data needs scoped exposure.
