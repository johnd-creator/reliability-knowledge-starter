# MX-013H Home Maximo Access & Asset Health Source Discovery

## Purpose

MX-013H validates whether the approved read-only Maximo discovery workflow can
run from the current home network. If access is available, it performs a
bounded source discovery for the Asset Health report labels Last Wellness,
Kondisi Saat ini, Last ACR, and Last MPI.

This run stopped before authentication and business-resource discovery because
the configured Maximo HTTPS endpoint did not pass local TLS certificate
verification. No source-system data was read or changed.

## Home Access Result

- DNS reachable: **YES**
- TCP endpoint reachable: **YES**
- HTTPS reachable: **NO** — TLS certificate verification failed with
  `SSLCertVerificationError`.
- Maximo web reachable: **NO** — no HTTP response was accepted.
- Authentication successful: **NO — NOT ATTEMPTED**
- OAS readable: **NO — TLS BLOCKED**
- Bounded business GET successful: **NO — NOT ATTEMPTED**

No hostname, private endpoint, credential, cookie, or response payload is
stored in this document.

## Safety

- Business writes: **0**
- Authentication POST: **0**
- Metadata/OAS GET attempts: **1**, unsuccessful at TLS verification
- Known Maximo web GET attempts: **1**, unsuccessful at TLS verification
- Candidate Asset Health requests: **0**
- HEAD/OPTIONS requests: **0**
- GET/HEAD/OPTIONS business requests: **0**
- Secrets persisted: **NO**
- Cookies or session identifiers persisted: **NO**
- Request budget exceeded: **NO**

The approved discovery tooling was not used to bypass certificate validation.
No alternate endpoint, port, credential, or authentication technique was
probed.

## Offline Candidate Search

The existing local Maximo knowledge base was searched before any candidate
request. No existing curated field list contains the four report labels or a
verified mapping to them.

Ranked candidates, limited to four live candidates if access becomes
available:

1. **IPBHM** — `/oslc/os/ipbhm` — strongest candidate because it is an
   existing verified BHM header-like object and has a directly verified
   `assetnum` relationship. Its curated field list contains BHM identity,
   status, description, function, revision, asset, site, organization, and
   timestamps, but not the four requested report labels.
2. **IPBHMLINE** — `/oslc/os/ipbhmline` — documented BHM line/detail candidate;
   parent relationship and fields remain unknown.
3. **IPBHMMEASUREMENT** — `/oslc/os/ipbhmmeasurement` — bounded local evidence
   exists for the object, but business fields were not exposed and the
   observed collection shape reached the response cap. Measurement meaning,
   parent relationship, and fields remain unknown.
4. **IPBHMWORKSHOP** — `/oslc/os/ipbhmworkshop` — documented BHM workshop
   candidate; fields and Asset relationship remain unknown.

The candidate ranking is a discovery plan, not a claim that any candidate owns
Wellness, ACR, MPI, or current-condition semantics.

## Live Verification

| Application | Object | Object Structure | REST Resource | Result | Evidence class |
|---|---|---|---|---|---|
| Reliability | IPBHM | IPBHM | `/oslc/os/ipbhm` | Not attempted; home TLS blocked | UNKNOWN |
| Reliability | IPBHMLINE | IPBHMLINE | `/oslc/os/ipbhmline` | Not attempted; home TLS blocked | UNKNOWN |
| Reliability | IPBHMMEASUREMENT | IPBHMMEASUREMENT | `/oslc/os/ipbhmmeasurement` | Not attempted; home TLS blocked | UNKNOWN |
| Reliability | IPBHMWORKSHOP | IPBHMWORKSHOP | `/oslc/os/ipbhmworkshop` | Not attempted; home TLS blocked | UNKNOWN |

No live source field, datatype, sample value, or Asset linkage was verified in
this run.

## Asset Health Source Matrix

| Business label | Source object | Source field | REST resource | Datatype | Asset relationship | Source evidence | Business semantics | Notes |
|---|---|---|---|---|---|---|---|---|
| Last Wellness | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | UNVERIFIED | Not present in the existing curated candidate field lists. |
| Kondisi Saat ini | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | UNVERIFIED | Not present in the existing curated candidate field lists. |
| Last ACR | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | UNVERIFIED | Not present in the existing curated candidate field lists. |
| Last MPI | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNRESOLVED | UNVERIFIED | Not present in the existing curated candidate field lists. |

The existing IPBHM evidence verifies an `assetnum` field relationship for BHM
records. That relationship does not identify the source of the four report
labels and does not prove any Health, Wellness, ACR, or MPI business meaning.

## Conclusions

**HOME_ACCESS_BLOCKED**

Source status: **SOURCE_NOT_IDENTIFIED**. The result is caused by local TLS
certificate verification failure before authentication, not by an authorization
decision. Authentication and bounded business GET status therefore remain
unverified.

## NADI Impact

No NADI capability is unlocked by this run. No Health Score, Wellness Score,
condition classification, ACR metric, or MPI metric should be implemented from
the current evidence.

## Next Recommended Task

Resolve the approved home environment's TLS trust/configuration with the
Maximo service owner or use an approved workstation/network where the existing
read-only certificate chain is trusted. Then rerun MX-013H with the same
request budget, beginning with the web/OAS read checks. Do not disable TLS
verification or expand discovery scope.
