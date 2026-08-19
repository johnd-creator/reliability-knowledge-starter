# Maximo Object Knowledge (BSR-scoped, verified)

Object structures verified via live OSLC query with the discovery account
(site BSR, org IP). Each entry links to the full per-object record.

> **Forbidden objects** (account lacks object-level READ): failurecode, location,
> pm, meter, jobplan. See [`docs/unit-specific.md`](./unit-specific.md).

## ASSET — `mxasset` / `mxapiasset` (69–73 fields, verified)

Primary key: `assetnum`. Record: [`discovery/objects/mxasset.json`](../discovery/objects/mxasset.json).

Key fields: `assetnum`, `description`, `status`, `status_description`,
`location`, `siteid`, `orgid`, `parent`, `ancestor`, `children`, `failurecode`,
`assettype`, `priority`, `installalldate`, `changedate`, `changeby`,
`purchaseprice`, `totalcost`, `replacecost`, `isrunning`, `iscalibration`.

Relationships: `parent`/`ancestor`/`children` (asset hierarchy),
`assetspec_collectionref` (asset specs), `assetmeter_collectionref` (meters),
`failurecode` (→ failure list, currently forbidden).

Plant/unit context: `plant`, `eq11` (unit), `eq10` (category).

## WORK ORDER — `mxwodetail` (166 fields, verified)

Primary key: `wonum`. Record: [`discovery/objects/mxwodetail.json`](../discovery/objects/mxwodetail.json).

Key fields: `wonum`, `description`, `status`, `status_description`, `worktype`,
`assetnum`, `location`, `siteid`, `orgid`, `reportdate`, `changedate`,
`targcompdate`, `schedstart`, `schedfinish`, `actstart`(via actualfinish),
`supervisor`, `lead`, `reportedby`, `wopriority`, `estdur`, `downtime`,
`wo class`, `istask`, `parent`(WO hierarchy), `workorderid`.

Cost/labor: `estlabcost`, `estmatcost`, `actlabcost`, `actmatcost`,
`actlabhrs`, `wplabor_collectionref`, `wpmaterial_collectionref`.

Relationships: `assetnum` (→ asset), `wplabor`/`wpmaterial` (planned labor/materials),
`invreserve_collectionref`, `haschildren`/`istask`/`pctaskid` (WO hierarchy).

Custom IP fields: `seksi`, `bu`, `jumlahhidup`, `jumlahmati`, `luasareatanam`.

## PERSON — `mxperson` (34 fields, verified)

Primary key: `personid`. Record: [`discovery/objects/mxperson.json`](../discovery/objects/mxperson.json).

Key fields: `personid`, `displayname`, `firstname`, `status`,
`statusdate`, `personuid`, `locationorg`, `hiredate`, `birthdate`.

> Personal data (email, phone) are exposed only as `_collectionref` URLs, not
> inline values. The fetcher must redact/drop these per the sanitization rules.

## ITEM / MATERIALS — `mxitem` (40 fields, verified)

Primary key: `itemnum`. Record: [`discovery/objects/mxitem.json`](../discovery/objects/mxitem.json).

Key fields: `itemnum`, `itemid`, `description`, `status`, `itemtype`,
`lottype`, `issueunit`, `orderunit`, `rotating`, `iskit`, `iscrew`,
`metername`, `itemsetid`, `site`.

Relationships: `itemspec_collectionref`, `itemcondition_collectionref`,
`itemorginfo_collectionref`, `conversion_collectionref`.

## LABOR — `mxapilabor` (14 fields, verified)

Primary key: `laborcode`. Record: [`discovery/objects/mxapilabor.json`](../discovery/objects/mxapilabor.json).

Key fields: `laborcode`, `laborid`, `personid`, `status`, `status_description`,
`worksite`, `orgid`, `assigned`, `availfactor`, `reportedhrs`, `ytdothrs`,
`ytdhrsrefused`.

Relationship: `personid` (→ person).

## SERVICE REQUEST — `mxapisr` (96 fields, verified)

Primary key: `ticketid`. Record: [`discovery/objects/mxapisr.json`](../discovery/objects/mxapisr.json).

Key fields: `ticketid`, `ticketuid`, `description`, `status`,
`status_description`, `worktype`, `reportedby`, `reportedbyname`,
`reportdate`, `changedate`, `statusdate`, `assetnum`, `location`, `siteid`,
`site`, `orgid`, `assetorgid`, `affectedperson`, `affectedphone`,
`internalpriority`, `reportedpriority`, `class`, `class_description`.

Relationships: `assetnum` (→ asset), `worklog_collectionref`,
`ticketspec_collectionref`, `classstructure_collectionref`, `site_collectionref`.

Custom IP risk fields: `cxarlingkungan`, `cxarproses`, `cxarmanusia`,
`cxarreputasi` (custom area/risk classifications).

## Forbidden objects (pending read-enabled credential)

| Object | OS name | Underlying object | Error |
|---|---|---|---|
| Failure codes | `mxapifailurecode` | FAILURECODE | READ not allowed |
| Locations | `mxapilocation` | LOCHIERARCHY | READ not allowed |
| Preventive Maint. | `mxapipm` | PM | READ not allowed |
| Meters | `mxapimeter` | METER | READ not allowed |
| Job Plans | `mxapijobplan` | JOBPLAN | READ not allowed |

These are object-level permission issues (not site-related). Granting READ
sigoption (scoped to BSR) on the underlying objects will make them discoverable
on the next run.
