# Governed PI source boundary

This document describes the boundary between the existing technical PI
collector and future NADI orchestration.

## Two distinct modes

The `pi-knowledge/mappings/bsr1-parameters.yaml` file is a broad technical
inventory. It contains 541 discovered attributes, of which 433 are currently
stream-ok. Loading that registry enables technical snapshots and historian
collection into the collector's own database. It does not establish a
canonical Maximo Asset identity or a governed reliability signal.

```text
TECHNICAL_PI_ATTRIBUTE != GOVERNED_ASSET_SIGNAL
```

The governed mode accepts an explicit `GovernedAfTarget` from an external NADI
orchestration layer. The PI collector does not query the Mart, duplicate
`asset_af_mapping`, choose an ambiguous winner, or perform fuzzy discovery.

## Accepted target

All of these values are required and explicit:

```text
canonical_asset_id
pi_source_id       = CENTRAL_PI
af_server_ref
af_database_ref
af_element_ref
mapping_role       = PRIMARY_EQUIPMENT
mapping_status     = VERIFIED
```

Only `VERIFIED` establishes usable Asset→PI lineage. `PROPOSED`, `RETIRED`,
`UNMAPPED`, and `AMBIGUOUS` are rejected at the source boundary. A future
correction retires the old mapping and supplies a separately reviewed target.

## Bounded AF operations

Using the existing `PiClient`, the governed boundary can read:

1. one AF Element metadata document;
2. at most 100 direct AF Attributes;
3. one Attribute metadata document;
4. the Attribute's linked current value;
5. the Attribute's linked recorded data, capped at 20 samples per operation.

No recursive AF traversal, whole-site enumeration, bulk registry sweep, or
backfill is part of governed source use. PI Web API links are validated before
use and foreign scheme/host/port origins are rejected, so credentials cannot
be forwarded to an unexpected server.

## Normalized evidence

Snapshots and historical points preserve:

- source timestamp;
- numeric, text, boolean, null, or digital-state value type;
- engineering unit;
- `Good`, `Questionable`, `Substituted`, and `Annotated` flags.

Digital states are represented with `value=null` and a non-numeric type. A
quality flag is factual source evidence only; this boundary does not infer
failure, alarm, anomaly, or health.

The shared `condition-reading` contract currently exposes `value_good` but not
all four additional PI quality flags. The collector preserves the richer
fields in its domain, local schema, and local API; extending the shared
contract is a separate compatibility decision.

## Source and security boundary

The source path is:

```text
DCS / control systems
  → existing acquisition / OPC / PI Interface pipeline
  → Central PI
  → PI Web API / AF
  → pi-collector source boundary
  → future governed NADI orchestration
```

The current instance-verified authentication is runtime-only Basic auth.
`PI_WEB_API_BASE_URL`, `PI_USERNAME`, and `PI_PASSWORD` come from runtime
configuration. TLS verification remains enabled by default. The collector
does not log credentials, Authorization headers, response bodies, live values,
or unnecessary WebIds. Existing raw identifiers in the broad registry are
pre-existing technical debt; this task adds no production identifiers.
