# PI-001A Central PI Source Topology Discovery

## Executive Result

The central PI Web API is reachable with an authorized read-only Basic-auth
session. The API exposes both Data Archive and Asset Framework navigation. A
bounded AF walk for the BSR scope verified a site → unit → system → equipment
shape, and three sampled AF attributes explicitly declare the `PI Point` data
reference with value, recorded-data, and point links.

This is sufficient to treat PI Web API / AF as a technically viable
read-only time-series evidence boundary. It is not sufficient to map the
current Maximo Registered Reliability Asset identifiers to AF equipment. No
NADI signal mapping or analytics is justified by this task.

## Safety Boundary

- PI requests were GET-only; no PI write, annotation, configuration, or
  digital-state operation was attempted.
- Direct DCS, OPC, and PI Interface requests: 0. Their role is recorded as
  existing architecture, not independently probed here.
- Credentials, cookies, Authorization headers, WebIds, point names, and live
  process values are excluded from this artifact.
- The browser navigation to PI Vision was blocked by a certificate hostname
  mismatch. The TLS warning was not bypassed.

## PI Vision Evidence

The intended visual surface is the existing corporate PI Vision application.
The current browser inspection could not establish a page session because the
certificate hostname did not match the requested host. Therefore a browser
network trace proving PI Vision → PI Web API is `UNKNOWN` in this task.

Repository evidence and the direct API probe independently establish the
central PI Web API root, but that is not a substitute for a captured PI Vision
network request.

Evidence class: `UNKNOWN` for the browser linkage; `VERIFIED` for the API root.

## PI Web API

The sanitized API shape is:

```text
https://<central-pi-host>/piwebapi/...
```

`GET /` returned HTTP 200 and exposed links for `AssetServers`, `DataServers`,
`System`, and `Self`. The OMF controller was also exposed, but it was not used:
its write channel is outside the read-only boundary.

Observed authentication is Basic authentication using a runtime-only account.
The discovery script supports this model without logging or persisting the
credential.

Evidence class: `VERIFIED`.

## Authentication

The instance-verified model is Basic authentication. This does not establish
that NADI should own or distribute the credential. A future adapter must use a
dedicated least-privilege runtime secret outside Git and retain GET/HEAD/OPTIONS
guards.

## Data Archive

The current bounded Data Archive inventory returned two server entries. One
central server was connected during the live probe; a second entry was
disconnected. The server identities are deliberately represented as
`PI_DATA_ARCHIVE_1` and `PI_DATA_ARCHIVE_2` here.

Existing verified stream capabilities include:

- current snapshot value;
- recorded values;
- interpolated values;
- summary values;
- plot data; and
- end-of-stream value.

The point-level sample did not provide engineering units reliably. Units are
available at the AF Attribute level and should be taken from AF context.

Evidence class: `VERIFIED` for API access and stream capability; server
business role remains `SOURCE_SEMANTICS_REQUIRE_VERIFICATION`.

## Asset Framework

The live API returned one visible Asset Server in the bounded response and 14
AF database entries. One database was selected for the BSR walk and is
represented as `AF_DATABASE_1` in the sanitized evidence.

The following hierarchy was observed without exporting the complete tree:

```text
BSR
└── UNIT_SAMPLE
    ├── SYSTEM_SAMPLE (Boiler)
    ├── SYSTEM_SAMPLE (Generator)
    ├── SYSTEM_SAMPLE (NPHR)
    └── SYSTEM_SAMPLE (Turbine)
        └── ASSET_SAMPLE
            └── SIGNAL_SAMPLE
```

The names above are aliases. The exact business hierarchy remains in the
source system and was not copied into the new structured artifact.

Evidence class: `VERIFIED` for the observed AF navigation path, scoped to the
bounded BSR walk.

## AF Hierarchy

The root collection returned 47 elements in the bounded response. The BSR
element resolved to one unit child, and that unit resolved to four system
children. This proves the observed path but does not prove that every plant
uses the same shape.

Scope: BSR/IP applicability is supported by the Maximo site boundary and the
AF BSR walk. Cross-site generalization is not established.

## AF Attribute Model

Three BSR unit attributes were inspected as metadata samples:

| Alias | Role | Type | AF unit | Data reference | Classification |
|---|---|---|---|---|---|
| `SIGNAL_SAMPLE_1` | bearing temperature | Double | degree Celsius | PI Point | PI_POINT_BACKED |
| `SIGNAL_SAMPLE_2` | bearing vibration | Double | Micrometer | PI Point | PI_POINT_BACKED |
| `SIGNAL_SAMPLE_3` | rotational speed | Double | revolution per minute | PI Point | PI_POINT_BACKED |

Each detail response included an explicit `ConfigString` presence and links
for `Point`, `Value`, `RecordedData`, `InterpolatedData`, and `SummaryData`.
The config string itself was not retained.

Evidence class: `VERIFIED` for technical presence and type/unit metadata;
business reliability meaning of each signal still requires engineering review.

## AF → PI Point

The relationship is technically verified for the three sampled attributes:

```text
AF_ELEMENT
  → AF_ATTRIBUTE (DataReferencePlugIn = PI Point)
  → PI_POINT / STREAM (Point and stream links present)
```

This is an explicit source relationship, not a name match. It does not by
itself prove that a signal is a governed condition indicator.

## Maximo → AF Mapping

Three candidate identifiers were selected from the local Registered
Reliability Asset registry for BSR/IP. Exact identifier comparison against the
sampled AF evidence found no match. No `assetnum`, Maximo external ID, or
governed lookup key was observed in the bounded AF evidence.

Result: `MAXIMO_TO_AF_MAPPING: NOT_FOUND` for this bounded sample. This is not
a claim that no mapping exists anywhere in AF; it is a decision not to promote
name similarity or a PI tag name into canonical asset identity.

## Stream Contract

For three PI Point-backed attributes, current snapshot responses exposed:

- timestamp;
- value, represented as a floating-point number;
- engineering-unit abbreviation;
- `Good`;
- `Questionable`;
- `Substituted`; and
- `Annotated`.

A single 15-minute recorded-data request, capped at 20 items, returned 20
items with timestamp, value, and `Good` fields. No values were retained.

Evidence class: `VERIFIED` for the response shape and bounded historical
contract.

## Signal Candidates

Three technically available signal roles were observed: bearing temperature,
bearing vibration, and rotational speed. They are source signal candidates,
not health scores, diagnoses, thresholds, anomalies, or recommendations.

## Time-Series Quality

Timestamp and quality-field presence are verified. Engineering units are
verified at the AF Attribute level and observed in the snapshot response.
The semantics of a bad/questionable/substituted/annotated value and the
business acceptance policy remain to be governed before KPI or model use.

## Existing DCS/OPC/PI Interface Boundary

The architecture remains:

```text
DCS / control systems
    ↓
existing acquisition pipeline
    ↓
Central PI Data Archive / AF
    ↓
PI Web API
    ↓
future NADI operational evidence
```

The DCS, OPC, and PI Interface legs were not contacted and are treated as
`EXISTING_ARCHITECTURE_REPORTED`.

## Unknowns

- A fresh PI Vision browser network trace is unavailable because of the
  certificate mismatch.
- The authoritative Maximo Asset → AF Element identifier/lookup is unresolved.
- AF attribute business semantics, alarm thresholds, validity windows, and
  engineering acceptance rules are not established.
- The disconnected secondary Data Archive's intended role is unknown.
- Authentication provisioning, least-privilege role design, and production
  adapter ownership remain deployment decisions.

## NADI Readiness

```text
PI_WEB_API_IDENTIFIED: YES
PI_DATA_ARCHIVE_IDENTIFIED: YES
AF_SERVER_IDENTIFIED: YES
AF_DATABASE_IDENTIFIED: YES
AF_ATTRIBUTE_MODEL_IDENTIFIED: YES
AF_TO_PI_POINT_RELATIONSHIP: VERIFIED
MAXIMO_TO_AF_MAPPING: NOT_FOUND
TIMESTAMP_SEMANTICS_IDENTIFIED: YES
QUALITY_FIELDS_IDENTIFIED: YES
ENGINEERING_UNIT_AVAILABLE: YES
TIME_SERIES_EVIDENCE_READY: YES
ASSET_SIGNAL_MAPPING_READY: NO
CONDITION_FINDING_READY: NO
PDM_DATA_FOUNDATION_READY: PARTIAL
PDM_MODEL_READY: NO
ANOMALY_DETECTION_READY: NO
RECOMMENDATION_READY: NO
```

The PI source adapter is technically justified only for a separate follow-up
that consumes verified Web API contracts and retains the unresolved Maximo
mapping as an explicit boundary. A condition or PdM implementation is not
justified.

## Request Audit

- PI GET requests: 22, including root, Data Archive, AF navigation, attribute
  metadata, and three current snapshots.
- Historical window GET requests: 1, limited to 15 minutes and 20 samples.
- Browser PI Vision network trace: 0 (blocked before page load by TLS mismatch).
- PI writes: 0.
- OPC direct requests: 0.
- PI Interface direct requests: 0.
- DCS direct requests: 0.
- Response-size cap: preserved at 1 MiB.
