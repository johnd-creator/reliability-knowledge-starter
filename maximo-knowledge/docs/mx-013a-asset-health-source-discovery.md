# MX-013A Asset Health Source Discovery

## Executive Result

This bounded discovery did not identify a verified Maximo source for `Last
Wellness`, `Kondisi Saat ini`, ACR, MPI, `Tanggal Judgement`, or `Rekomendasi
Program`. The protected report remains secondary evidence: its column names do
not prove ownership by `IPBHM`, Engineering Judgement, Maintenance Strategy,
or any other Maximo object.

The existing `IPBHM` evidence remains valid and unchanged. It verifies an
`assetnum` relationship and the current BHM header fields, but it does not
contain any of the requested report columns. The documented `IPENGJUDGE`
resource is a candidate only; a bounded live request to it timed out before a
schema or record could be observed. No production data was changed.

## Existing NADI Boundary

NADI currently treats `IPBHM` as the canonical Asset Health evidence. The
verified fields are `bhmid`, `eid` (meaning still unknown), `revision`,
`status`, `description`, `fungsi`, `assetnum`, `createddate`,
`lastmodifieddate`, and `statusdate`. `IPBHM.assetnum` is the verified path to
the Asset identity.

NADI does not currently display or calculate a Health Score, Wellness Score,
Condition Score, or Risk Score. The local report is explicitly classified as
secondary evidence, and `WELLNESS_SOURCE_IDENTIFIED` remains `NO`.

## Candidate Applications

The repository evidence identifies these as candidates within the same Maximo
source boundary, not independent source systems:

| Candidate | Local evidence | Current limitation |
| --- | --- | --- |
| Reliability — BHM | `IPBHM`, `IPBHMLINE`, `IPBHMMEASUREMENT`, `IPBHMWORKSHOP` | Only `IPBHM` header fields and `assetnum` are verified; child lineage is unknown. |
| Reliability — Engineering Judgement | `IPENGJUDGE` / `/oslc/os/ipengjudge` | Catalog presence only; live bounded schema request timed out. |
| Reliability — failure mechanism | `IPMSMSFAILUREMECHANI` | Failure-mechanism candidate only; not a proven Maintenance Strategy source. |
| DIAMOND — operator condition/logsheets | `DMDKONDISIOPR`, `DMDLOGSHEET*`, `DMD_OPLOGABN` | No verified relationship to the report or Asset Health concepts. |
| DOMINION — inspection/overhaul | `DOM_INSPEKSIMESIN`, `IP_DOM_OH` | Existing evidence does not expose the requested report concepts; OH-to-Asset is unknown. |
| Efficiency Management | `IPEMLGWR`, `IPEMFB*`, `IPEMMP*` | No verified Performance Test or Asset Health lineage. |

Names and application labels were used only to make the candidate shortlist;
they were not used as semantic proof.

## Source Lineage Matrix

The report columns below have no verified source-object lineage. `IPENGJUDGE`
is included only as a documented candidate for manual judgement, not as a
source conclusion.

| Concept | Application | Object/MBO | Object Structure | REST Resource | Field | Asset Relationship | Stored/Derived | Evidence Class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Last Wellness | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown; report row is not source proof | Unknown | `UNKNOWN` | Report label only. It must not be called a score. |
| Kondisi Saat ini | Reliability — Engineering Judgement (candidate) | Unknown | `IPENGJUDGE` (candidate only) | `/oslc/os/ipengjudge` | Unknown | Unknown | Unknown | `UNKNOWN` | Candidate catalog entry; bounded live request timed out. |
| Last ACR | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | No ACR-named source was identified in bounded local evidence. |
| Last ACR Rank | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Raw-versus-report-derived rank is unknown. |
| Last MPI | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | No MPI-named source was identified in bounded local evidence. |
| Last MPI Rank | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Raw-versus-report-derived rank is unknown. |
| Tanggal Judgement | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Same-row appearance in the report does not prove a single source record. |
| Rekomendasi Program | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Same-row appearance in the report does not prove a relationship to judgement, Wellness, ACR, or MPI. |

No field type, value range, authoritative date, lifecycle/version rule, or
calculation rule was verified for any of these concepts.

## IPBHM Relationship Finding

**Overall: UNKNOWN — no verified relationship.**

The direct `IPBHM` field evidence contains no Wellness, condition, ACR, MPI,
judgement-date, or program-recommendation field. Existing repository evidence
also leaves `IPBHM` child/detail lineage unresolved. Therefore the current
finding is:

- direct IPBHM ownership: `NONE FOUND`;
- child/parent relationship to a candidate source: `UNKNOWN`;
- shared Asset relationship: technically verified for `IPBHM.assetnum`, but
  not verified for any report concept.

The report's six Asset numbers overlapping the current IPBHM Asset
representation are only a shared-value observation. They do not establish a
relationship between the records.

## Report Lineage Finding

**Result:** report lineage is not proven. The protected local report contains
845 Asset rows and the named columns; the existing aggregate audit records
non-empty values for most of those columns and six Asset overlaps with the
current IPBHM representation. No report definition, application metadata,
join expression, object relationship, or API response was available that
connects those columns to a Maximo source record.

The live catalog request returned no member names. The only specifically
targeted candidate request was `IPENGJUDGE`; it timed out on the bounded
collection request before a field or record could be inspected. No alternate
resource enumeration or unbounded collection request was attempted.

**Evidence class:** `UNKNOWN`.

The competing lineage hypotheses remain open: direct Asset report, joined
Asset query, Engineering Judgement report, Maintenance Strategy report, BHM
projection, or another report structure.

## BSR/IP Scope Evidence

The repository's existing verified `IPBHM` evidence records `siteid` and
`orgid`, and the established NADI scope is `SITE=BSR`, `ORG=IP`.

For this task, the candidate catalog entries are global-schema/documented
evidence only. The `IPENGJUDGE` probe did not return a record or scope field.
No BSR/IP applicability conclusion can therefore be made for Wellness,
Kondisi, ACR, MPI, judgement, or recommendation. Cross-site equivalence was
not inferred.

## Remaining Business Questions

- Which Maximo application/report definition produces each requested column?
- Does `Last Wellness` represent a score, category, status, date, rank, or an
  assessment result, and what are its units/range and validity period?
- Is `Kondisi Saat ini` manual judgement, a stored category, a status, or a
  calculated result?
- What does ACR mean in this Maximo instance, and where are its result, rank,
  lifecycle/version, and judgement date stored?
- What does MPI mean in this Maximo instance, and where are its result, rank,
  lifecycle/version, and judgement date stored?
- Are `Tanggal Judgement` and `Rekomendasi Program` attributes of one source
  record or joins from multiple objects?
- What is the authoritative Asset key for each candidate object, and is it
  mandatory or optional within `ORG=IP`, `SITE=BSR`?
- Is any candidate related to `IPBHM` directly, through a child/parent
  relationship, or only through a shared Asset?
- What report/application metadata can be inspected read-only to prove the
  lineage without changing report configuration?
- What are the business rules for scoring, weighting, thresholds, missing
  values, overrides, validity, and historical versions?

## NADI Readiness Decision

```text
WELLNESS_SOURCE_IDENTIFIED: NO
CURRENT_CONDITION_SOURCE_IDENTIFIED: NO
ACR_SOURCE_IDENTIFIED: NO
MPI_SOURCE_IDENTIFIED: NO
ASSET_RELATIONSHIP_VERIFIED: PARTIAL
REPORT_LINEAGE_VERIFIED: NO
HEALTH_SCORE_READY: NO
```

`ASSET_RELATIONSHIP_VERIFIED` is `PARTIAL` only because the existing IPBHM
source has a verified `assetnum` path. It is not verified for the report
columns or the `IPENGJUDGE` candidate.

Finding fields alone would not make a Health Score ready. A future score would
still require an authoritative numerical input, units/range, directionality,
weighting, aggregation, missing-data behavior, thresholds, validity period,
historical/version rules, and business governance.

## Request Audit

The task-local live audit was deliberately bounded. The first run performed a
catalog GET; three subsequent short-lived, in-memory sessions each attempted
one bounded GET for the already catalogued `IPENGJUDGE` resource and timed out
before a schema or record was returned. No detail GET was reached.

| Method | Count | Result |
| --- | ---: | --- |
| Authentication `POST /j_security_check` | 4 | Authentication-only handshakes; credentials/cookies were runtime-only. |
| Business `GET` | 4 | 1 catalog GET returned no member names; 3 bounded `IPENGJUDGE` GETs timed out. |
| `HEAD` | 0 | None issued. |
| `OPTIONS` | 0 | None issued. |
| Business writes | 0 | No POST/PUT/PATCH/DELETE/MERGE to a business resource. |

The 40-GET budget was not exceeded. No raw response, credential, cookie,
token, personal field, or report row was written to the repository. No
During MX-013A, no structured discovery JSON was changed because no new
verified object or field was obtained.

## MX-013B Metadata-First Follow-up

This section records the sequential follow-up only. The MX-013A result above
is preserved as the initial bounded discovery record. The follow-up did not
reinterpret the earlier `IPENGJUDGE` collection timeout as absence.

### Local Report Forensics

The protected `23496711.xls` file is an HTML-disguised Excel export. Local
inspection found:

- worksheet name: `List of Assets`;
- 846 HTML table rows, including one header row and 845 data rows;
- relevant visible labels: `Last Wellness`, `Kondisi Saat ini`, `Last ACR`,
  `Last MPI`, `Last ACR Rank`, `Last MPI RANK`, `Maintenance Strategi`,
  `Tanggal Judgement`, `Jadwal Program`, `Estimasi Jadwal Program`,
  `Rekomendasi Program`, `WO Eng. Judgement`, and `WO Eng. Judgement Status`;
- no HTML title or meta tag identifying a report;
- no BIRT metadata, application ID, report ID, dataset/query identifier,
  Maximo URL, or report servlet metadata;
- two HTML comment blocks contained no report/application/query metadata.

The file itself does not identify the Maximo report or application that
generated it. The worksheet and column labels remain useful clues only.

**Classification:** `CLUE_ONLY`.

Personal-owner and creator columns, employee values, Asset values, and raw
report rows were not copied into repository evidence.

### IPENGJUDGE Metadata

The local OAS contains the following documented paths and metadata:

| Evidence | Result |
| --- | --- |
| OAS collection path | `/os/ipengjudge` |
| OAS detail path | `/os/ipengjudge/{id}` |
| OAS tag | `IP LOADER ENGINEERING JUDGEMENT (LOADER) (IPENGJUDGE)` |
| OAS collection parameters | `oslc.where`, `oslc.select`, `oslc.pageSize`, `oslc.paging`, `oslc.searchTerms`, `savedQuery`, `action` |
| OAS detail parameters | `id`, `oslc.properties`, `accept`, read-only action metadata |
| Linked JSON Schema | `/oslc/jsonschemas/IPENGJUDGE` |
| Inline OAS response schema | Not present |

Live metadata requests then returned:

- `GET /oslc/apimeta/IPENGJUDGE`: HTTP 200; `osName=IPENGJUDGE`, title
  `IP LOADER ENGINEERING JUDGEMENT (LOADER)`, `useWith=INTEGRATION`, and
  `defaultPageSize=100`;
- `GET /oslc/jsonschemas/IPENGJUDGE`: HTTP 200; schema title `ENGJUDGE`,
  object type, and field definitions.

The live schema exposed these non-personal technical fields and types:

| Field | Type | Metadata interpretation |
| --- | --- | --- |
| `engjudgeid` | integer | Required schema field; uniqueness is not verified. |
| `assetnum` | string | Asset reference candidate; relationship is not verified. |
| `wellness` | string | Technical field present; meaning and report ownership are unknown. |
| `wellness_description` | string | Technical companion field; meaning is unknown. |
| `engdate` | string | Date-like candidate; format and semantics are unknown. |
| `est_date` | string | Date-like candidate; semantics are unknown. |
| `siteid` | string | Scope field candidate; BSR applicability is unknown. |
| `orgid` | string | Scope field candidate; IP applicability is unknown. |
| `location` | string | Location reference candidate; relationship is unknown. |
| `description`, `description2`, `description3`, `keterangan` | string | Business text fields; semantics are unknown. |
| `measurepointid` | integer | Technical measurement-point candidate; relationship is unknown. |
| `metername` | string | Technical meter candidate; relationship is unknown. |
| `engweek`, `engmonth`, `engyear` | string | Engineering-period candidates; semantics are unknown. |

The schema did not expose fields named ACR, MPI, current condition, judgement
date, or program recommendation. This is bounded schema evidence, not proof
that those concepts cannot exist in another related object or report query.

**OAS_PATH_IDENTIFIED:** YES

**OAS_RESPONSE_SCHEMA_IDENTIFIED:** YES, through the linked live JSON Schema; no inline OAS response schema

**OAS_FIELDS_IDENTIFIED:** YES, technical schema fields only

The underlying Maximo MBO/object name beyond schema title `ENGJUDGE` was not
exposed by the metadata responses. A distinct Maximo application ID was not
exposed.

### Engineering Judgement UI Evidence

Browser-assisted inspection used only the documented Maximo root and documented
login path. Both read-only navigations returned `404 Not Found` from the
network gateway/cPanel surface. No Engineering Judgement UI loaded, so there
is no UI evidence for field labels, tabs, Asset selection, or report actions.
No alternate URL variants were guessed or crawled.

**Classification:** `NOT_FOUND` for this browser inspection attempt; this does
not change the metadata evidence or the inherited collection `TIMEOUT`.

### Report/Application Association

Repository OAS/catalog metadata identifies report/query/application object
structures, and their live schemas expose useful technical fields:

- `MXL_REPORTDESIGN`: `reportname`, `reportfilename`, `description`, `design`,
  `reportdesignid`;
- `MXL_QUERY`: `app`, `clausename`, `description`, `clause`, `queryid`;
- `MXL_APPS`: `app`, `description`, `apptype`, `maxappsid`;
- `MXL_REPORT` schema endpoint returned HTTP 500 and was not retried.

Eight bounded literal searches were attempted with one page and minimal
selection: `wellness`, `acr`, `mpi`, and `judgement` across `MXL_REPORTDESIGN`
and `MXL_QUERY`. All returned HTTP 400. No report name, application name,
query name, dataset, or association was obtained. The 400 responses are not
reclassified as forbidden and do not prove that no report exists.

**REPORT_NAME_IDENTIFIED:** NO

**REPORT_APPLICATION_ASSOCIATION:** UNKNOWN

### Browser Network Evidence

No browser application loaded successfully, so no application-generated
network request could be observed. The only verified technical paths are the
OAS and metadata paths listed above. No cookies, authorization headers, raw
payloads, or personal values were persisted.

### ACR/MPI Literal Search

The report visibly contains `Last ACR`, `Last ACR Rank`, `Last MPI`, and `Last
MPI RANK`, but these remain report clues. The live `ENGJUDGE` schema contains
no ACR or MPI field. Bounded report-design/query metadata searches for `acr`
and `mpi` returned HTTP 400 without a match.

| Concept | Technical source result | Evidence |
| --- | --- | --- |
| ACR | No field in `ENGJUDGE`; no bounded report/query result | `UNKNOWN` overall; `NOT_FOUND` in bounded metadata scope |
| MPI | No field in `ENGJUDGE`; no bounded report/query result | `UNKNOWN` overall; `NOT_FOUND` in bounded metadata scope |
| Wellness | `IPENGJUDGE.wellness` and `wellness_description` fields exist in live schema | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` |
| Current Condition | No matching technical field or report association | `UNKNOWN` |

No acronym was expanded from general or external knowledge.

### Updated Lineage Matrix

The follow-up adds technical metadata evidence but proves no report join. The
following are the only new source-to-field edges:

```text
IPENGJUDGE
  └─ live JSON Schema → wellness, wellness_description, assetnum, engdate,
                       est_date, siteid, orgid, location
```

This is a metadata edge, not a proven business or report lineage edge. No
`ASSET → IPENGJUDGE` relationship and no `REPORT → IPENGJUDGE` relationship
was verified.

| Concept | Application | Object/MBO | Object Structure | REST Resource | Field | Asset Relationship | Stored/Derived | Evidence Class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Last Wellness | Reliability — Engineering Judgement | `ENGJUDGE` schema title; MBO unknown | `IPENGJUDGE` | `/oslc/os/ipengjudge` | `wellness`, `wellness_description` | `UNKNOWN`; `assetnum` field is present | Unknown | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Technical field exists; report ownership and score meaning are unproven. |
| Kondisi Saat ini | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | No direct field or report association proved. |
| Last ACR | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Report label only. |
| Last ACR Rank | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Raw versus derived rank unknown. |
| Last MPI | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Report label only. |
| Last MPI Rank | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Raw versus derived rank unknown. |
| Tanggal Judgement | Reliability — Engineering Judgement (candidate) | `ENGJUDGE` schema title; MBO unknown | `IPENGJUDGE` | `/oslc/os/ipengjudge` | `engdate`, `est_date` | `UNKNOWN` | Unknown | `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` | Date-like fields exist; they are not proven to be judgement date or report source. |
| Rekomendasi Program | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `UNKNOWN` | Report label only; no source field identified. |

### Updated Readiness

```text
IPENGJUDGE_APPLICATION_IDENTIFIED: YES
IPENGJUDGE_OBJECT_IDENTIFIED: YES
IPENGJUDGE_LIVE_READ: TIMEOUT
REPORT_NAME_IDENTIFIED: NO
REPORT_APPLICATION_ASSOCIATION: UNKNOWN
WELLNESS_SOURCE_IDENTIFIED: PARTIAL
CURRENT_CONDITION_SOURCE_IDENTIFIED: NO
ACR_SOURCE_IDENTIFIED: NO
MPI_SOURCE_IDENTIFIED: NO
ASSET_RELATIONSHIP_VERIFIED: PARTIAL
REPORT_LINEAGE_VERIFIED: NO
HEALTH_SCORE_READY: NO
```

`IPENGJUDGE_APPLICATION_IDENTIFIED=YES` means the Reliability/Engineering
Judgement technical identity is supported by the repository inventory, OAS
tag, `apimeta`, and live schema title. It does not mean that a distinct Maximo
application ID was found. `IPENGJUDGE_OBJECT_IDENTIFIED=YES` means the Object
Structure and schema title are identified; the underlying MBO remains unknown.

`WELLNESS_SOURCE_IDENTIFIED=PARTIAL` means a live technical field candidate
exists. It does not prove that `IPENGJUDGE.wellness` supplies the report's
`Last Wellness`, nor that it is a score, category, status, date, rank, or
assessment result.

### Request Audit

MX-013B used separate short-lived authenticated sessions for metadata and
bounded searches. Counts below cover this follow-up only; the MX-013A audit is
preserved above.

| Request class | Count | Result |
| --- | ---: | --- |
| Authentication `POST /j_security_check` | 6 | Authentication-only handshakes; no business writes. |
| Metadata/OAS GET | 8 | IPENGJUDGE schema ×2, IPENGJUDGE apimeta ×2, report/query/app schemas ×4; `MXL_REPORT` schema returned HTTP 500. |
| Business GET | 8 | Four literal searches each on `MXL_REPORTDESIGN` and `MXL_QUERY`; all HTTP 400. |
| Browser UI navigations | 2 | Documented root and login path; both HTTP 404. |
| Business writes | 0 | No POST/PUT/PATCH/DELETE/MERGE to a business resource. |

The MX-013B business GET budget was 15 and was not exceeded. No
`IPENGJUDGE` collection GET was repeated. No raw business payload, report row,
credential, cookie, authorization header, or personal value was written.
