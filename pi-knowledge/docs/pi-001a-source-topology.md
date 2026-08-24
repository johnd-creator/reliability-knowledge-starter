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

## PI-002A Maximo → AF Identity Follow-up

This section is the sequential PI-002A follow-up. It preserves the PI-001A
result: AF → PI Point and the stream contract are verified, while Maximo Asset
→ AF Element remains unresolved. The evidence below is bounded to BSR/IP and
does not claim global absence of a mapping.

### Maximo Identity Candidates

The verified Maximo Asset evidence identifies `assetnum` as the Object
Structure primary key for `mxapiasset`. The collector keeps this value in its
Maximo source quarantine and uses it as the source Asset number. It is the
strongest candidate for a cross-system identity, but it is not promoted into a
PI mapping without an explicit AF match.

Other verified Asset fields that remain candidates for a future bridge are
`assetid`, `location`, `parent`, `ancestor`, `plant`, `eq11`, `eq9`, `eq10`,
`eq23`, and `eq5`, together with the scoped `siteid` and `orgid`. These fields
describe source identity or context; their presence does not prove that AF
uses the same key. The bounded scope is Maximo `BSR/IP`.

Evidence class: `VERIFIED` for the Maximo field presence and `UNKNOWN` for a
cross-system interpretation.

### AF Equipment Identity Model

Ten equipment Elements were resolved from existing verified AF attribute
evidence and inspected through Element metadata. All ten exposed an Element
name and a Description field; all ten exposed parent/child navigation links.
Nine of ten exposed an Element Template link. This confirms contextual AF
metadata and hierarchy navigation, not a Maximo identity bridge.

No inspected Element metadata exposed a field explicitly verified as the
Maximo `assetnum`, a Maximo `assetid`, or another governed external equipment
identifier. Element names and descriptions were therefore treated only as
possible discovery clues, not canonical identity.

Evidence class: `VERIFIED` for the observed AF metadata shape; `UNKNOWN` for
Maximo identity ownership.

### AF Template Evidence

Three referenced AF templates were inspected within the five-template bound.
The sampled template responses did not expose an attribute collection that
could be used to verify a Maximo, CMMS, EAM, or external-equipment key. No
template field was promoted from naming similarity.

`AF_ELEMENT_TEMPLATE_IDENTIFIED: YES` records the observed template
references. `AF_STATIC_IDENTITY_ATTRIBUTE_IDENTIFIED: PARTIAL` records that
identity-looking metadata was sampled but its source semantics and values were
not verified.

### Static Attribute Evidence

Sixty non-PI-Point AF attribute metadata entries were inspected. Twenty-six
had names that were candidate-like under literal identity tokens such as
asset, equipment, location, plant, unit, ID, or code. This is naming evidence
only. Ten bounded value requests for candidate attributes did not return a
usable value, so no AF identifier value was available for exact comparison.

No raw AF names, WebIds, ConfigStrings, or attribute values were retained.
The existing PI-001A result remains unchanged: PI Point-backed Attributes are
technically linked to streams, but that does not establish Asset identity.

Evidence class: `SOURCE_SEMANTICS_REQUIRE_VERIFICATION` for the
identity-looking names; `UNKNOWN` for their business ownership.

### Reverse Mapping Evidence

The reverse direction was evaluated from the sampled AF Element metadata and
candidate static attributes toward the local Maximo/Collector Asset identity.
Ten local Registered Reliability Asset candidates were selected in memory;
their raw identifiers were not persisted. No AF Element name/description and
no usable static-attribute value produced an exact match to a candidate
`assetnum`.

The local bounded platform contains 845 registered BSR/IP Assets and 10,660
Asset Master rows. Those counts establish candidate-selection context only;
they do not create an AF relationship.

Evidence class: `NOT_FOUND` for the tested bounded exact-match paths, with the
overall native mapping still unresolved.

### Location Mapping

Maximo `location` is a verified source field and remains a possible bridge.
The sampled AF Element metadata did not expose a verified location identifier
or an exact location value that could be joined to Maximo. Hierarchy position,
Element name, and description are supporting context only.

`MAXIMO_LOCATION_TO_AF: PARTIAL` for this bounded metadata probe. A direct
Asset → AF mapping must not be inferred from location or hierarchy alone.

### Mapping Candidate Matrix

| Maximo candidate | AF evidence tested | Exact result | Classification |
|---|---|---:|---|
| `assetnum` | Element name/description and usable static values | 0 | `NOT_FOUND` in bounded sample |
| `assetid` | Element metadata and static-attribute metadata | 0 usable values | `UNKNOWN` |
| `location` | Element metadata and hierarchy context | 0 | `SUPPORTING_CONTEXT_ONLY` |
| `parent` / `ancestor` | AF parent/child navigation | no identity edge | `SUPPORTING_CONTEXT_ONLY` |
| `plant` / unit / equipment fields | AF hierarchy and candidate static names | no governed key | `NAME_SIMILARITY_ONLY` at most |

No candidate meets `DIRECT_VERIFIED_IDENTIFIER`, `DERIVED_VERIFIED_PATH`, or
`GOVERNED_LOOKUP`.

### Exact Match Results

- Maximo Registered Reliability Asset candidates tested: 10.
- AF equipment Elements sampled: 10.
- AF templates sampled: 3.
- Non-PI-Point AF attributes inspected: 60.
- Usable candidate identity values read: 0.
- Exact Element identifier matches: 0.
- Exact static-attribute identifier matches: 0.
- Ambiguous matches: 0.
- Unmatched candidates: 10.
- Mapping-key uniqueness: `UNKNOWN`, because no candidate key was verified.

The previous PI-001A three-candidate result is preserved. This follow-up
expands bounded metadata inspection and still does not establish a native
Maximo → AF key.

### Mapping Readiness

```text
AF_ELEMENT_TEMPLATE_IDENTIFIED: YES
AF_STATIC_IDENTITY_ATTRIBUTE_IDENTIFIED: PARTIAL
MAXIMO_ASSET_IDENTITY_FIELD_IDENTIFIED: YES
MAXIMO_LOCATION_TO_AF: PARTIAL
NATIVE_MAXIMO_AF_MAPPING: NOT_FOUND_BOUNDED
MAPPING_KEY_UNIQUENESS: UNKNOWN
GOVERNED_MAPPING_REGISTRY_REQUIRED: YES
MAXIMO_TO_AF_MAPPING: NOT_FOUND_BOUNDED
ASSET_TO_AF_ELEMENT_READY: NO
ASSET_SIGNAL_MAPPING_READY: NO
TIME_SERIES_EVIDENCE_READY: YES
CONDITION_FINDING_READY: NO
PDM_DATA_FOUNDATION_READY: PARTIAL
```

Decision: `CASE C — governed mapping registry required`. The bounded discovery
did not establish a native Maximo → AF key or governed lookup. This is not a
claim that a native key can never exist; it is the current architecture
decision for safe NADI operation. An explicit, auditable Maximo Asset ↔ AF
Element mapping registry is required rather than a name-based join. A future
authoritative native key may still be recorded with `NATIVE_IDENTIFIER`.

### PI-002A Request Audit

- PI GET requests: 42 total in the bounded AF metadata probe; 32 returned
  HTTP 200 and 10 returned non-success responses while probing candidate
  attribute values.
- Maximo GET requests: 0; existing verified Maximo Asset schema and local
  collector data were sufficient for candidate selection.
- PI writes: 0.
- DCS direct requests: 0.
- OPC direct requests: 0.
- PI Interface direct requests: 0.
- Historical stream GET requests: 0.
- Response-size cap: preserved at 1 MiB.
