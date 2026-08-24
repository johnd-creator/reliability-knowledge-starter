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
structured discovery JSON was changed because no new verified object or field
was obtained.
