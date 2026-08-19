# Unit-Specific Maximo Knowledge (BSR)

This knowledge base is scoped to **site BSR** (organization **IP**), matching the
read access of the discovery account. The downstream fetcher application should
filter all queries by site unless a broader credential is later obtained.

## Verified identifiers

| Field | Value | Source |
|---|---|---|
| `orgid` | `IP` | mxasset sample |
| `siteid` | `BSR` | mxasset sample (newsite also `BSR`) |
| Maximo version | `7.6.1 PRODUCTION` | login page |

## Standard query filter

Every OSLC query in the downstream app should include the site filter:

```text
GET /oslc/os/{OBJECTSTRUCTURE}?oslc.where=siteid="BSR"&oslc.paging=true&pageno=1&oslc.pageSize=100
```

This ensures only BSR data is fetched, consistent with the account's access
scope and the organization's data-isolation requirements.

## Account scope (lac.hirna)

The discovery account `lac.hirna` has:

- **READ access** (BSR-scoped) on: ASSET, WORKORDER, PERSON, ITEM, LABOR, SR.
- **No READ access** (object-level, `BMXAA0024E`) on: FAILURECODE, LOCHIERARCHY,
  PM, METER, JOBPLAN. These return 400 regardless of site filter because the
  account lacks the READ sigoption on the underlying object.

> If BSR data from the forbidden objects is needed, request a Maximo
> administrator to grant READ sigoption on those objects for the service account
> (scoped to site BSR). The knowledge base tooling will pick them up on the next
  discovery run without code changes.

## Plant / unit naming (observed in BSR asset data)

Observed custom asset fields carrying plant/unit context (verify usage per object):

- `plant` / `plant_description` — e.g. `TU` = "Pembangkit Listrik Tenaga Uap (PLTU)"
- `eq11` / `eq11_description` — e.g. `CS01` = "Unit 1"
- `eq10` — e.g. color/category code (`HIJAU`)
- `ancestor` / `parent` / `children` — asset hierarchy navigation
- `seksi` / `subseksi` — organizational section (Indonesian: section/sub-section)

## Asset hierarchy convention (observed)

Asset identifiers follow a hierarchical pattern, e.g.:

```text
ancestor: CS-001
parent:   CS10CV-001
assetnum: CS10CVA02GA000-001
```

Use `parent`, `ancestor`, `children`, and `hierarchypath` (mxapiasset) to
traverse the asset tree within BSR.

## Custom fields (IP / PLN Indonesia Power specific)

Several `plusg*` (Plus for Government / industry extension) and `eq*` custom
fields appear across objects. These are organization-specific and should be
treated as business-meaningful only when confirmed by a domain expert:

- `plusg*` fields — reliability/governance extensions
- `eq5`–`eq23` — equipment classification fields
- `cxar*` / `cxrl*` — custom risk/area classifications (seen on SR)

Avoid storing production secrets or unnecessary personal data.
