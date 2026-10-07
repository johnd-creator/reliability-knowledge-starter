# Governed PI source boundary — NADI-PI-001

Status: **MERGED** via PR #12 (`main 3e981a3`), 2026-10-07.
PI runtime checkpoint: [NADI-PI-RUNTIME-001](nadi-pi-runtime-001.md). NADI projection, real mapping
population and live pilot remain pending. Source acquisition belongs to PI
Collector; NADI must never own PI source credentials or source authentication.

## Ownership and governance

The technical YAML registry supports existing collection/trending. Its 433
verified/stream-ok entries are not governed canonical Asset signals. Existing
technical collection does not acquire new NADI identity semantics through this
change.

`GovernedSourceBoundary(PiClient(runtime_config))` is an internal library for a
future trusted collector-side orchestration layer. It does not query or write
the Reliability Mart, expose a public source-proxy endpoint, persist mapping
copies, or automatically persist the readings it returns. Future orchestration
must resolve exactly one active mapping using the existing Mart resolver and
validate caller authorization. A self-declared `VERIFIED` HTTP body would not
prove governance; do not wrap this library in such an endpoint.

`GovernedAfTarget` requires nonblank string identifiers without surrounding
whitespace:

```text
canonical_asset_id
pi_source_id       = CENTRAL_PI
af_server_ref
af_database_ref
af_element_ref
mapping_role       = PRIMARY_EQUIPMENT
mapping_status     = VERIFIED
```

AF references are explicit PI WebIds, not names, fuzzy matches or paths to
resolve automatically. The existing mapping-admin syntactic checks do not prove
those source identities. Pilot verification must establish them explicitly.
`PROPOSED`, `RETIRED`, `UNMAPPED`, `AMBIGUOUS` and resolution label `MAPPED` are
rejected as mapping_status. `MAPPED` resolution must supply its selected row's
actual `VERIFIED` status; ambiguity cannot supply a winner.

## Bounded operations

| Operation | Bound and evidence |
|---|---|
| `get_element(target)` | Read one Element and its explicitly named Database; require Element WebId, Database link/WebId and AssetServer link to match target |
| `list_attributes(target, max_count=100)` | Validate Element lineage, request at most 100 direct attributes once; reject oversized/missing/duplicate identities and wrong Element links |
| `get_attribute(target, attribute_ref)` | Require membership in that bounded list, then validate metadata WebId/Element link |
| `get_snapshot(target, attribute_ref)` | Read source-returned Value link only after metadata checks; require an aware source timestamp |
| `get_recorded(target, attribute_ref, start_time, end_time, max_count=20)` | Explicit ISO timestamps with zones, increasing interval ≤24h, at most 20 returned samples, all timestamps present/in-window; no pagination |

Element requests use `/elements/{WebId}`, database `/assetdatabases/{WebId}`,
attributes `/elements/{WebId}/attributes` and `/attributes/{WebId}`. Relationship
checks use source links `Database`, `AssetServer`, `Element`. Missing/inconsistent
relationships fail closed. These link requirements have synthetic test evidence;
instance/pilot link availability is not newly live-verified by this task.

No recursive traversal, unrestricted listing, automatic AF lookup, signal-name
heuristics or backfill is introduced. An attribute outside the first bounded
list is unavailable through this boundary. Counts must be positive integers;
requests above caps are clamped. Each operation uses at most five sequential
source requests; use one long-lived collector-owned client. A governed signal
business role is not inferred by listing AF attributes.

## Request safety

All requests pass through the existing GET/HEAD/OPTIONS guard. Missing/invalid
runtime base fails before transport. Scheme, host and effective port must match
the configured PI Web API origin; absolute and API-root-relative links must stay
under its root path. Credential URLs, traversal and foreign URLs are rejected
before auth is attached. Redirects are disabled and non-2xx JSON reads raise
sanitized errors. Recorded links containing query parameters are rejected so
source links cannot override bounded counts/time parameters. There are no auth retries.

TLS verification defaults on. HTTP request spacing has a 1s hard minimum (or a
larger configured delay), serialized per client and retained after failures.
Decoded streamed responses are capped at 1 MiB or a smaller configured limit;
reading stops at the cap and closes the response. Existing bulk off-hours,
request/circuit-breaker/chunk/resume controls remain in the technical collector.

## Source value semantics and API compatibility

The legacy numeric `value` and `value_good` fields remain. Additive nullable
fields carry `source_value`, `value_type`, `value_questionable`,
`value_substituted`, `value_annotated`; historical points also carry `units`.
`source_value` retains the JSON scalar or bounded digital-state shape
`{Name, Value, IsSystem?}`. Digital codes, strings (including numeric-looking
strings), booleans and null never become numeric zero. Only finite JSON numbers
populate `value`. Unknown quality flags remain null; false stays false. Source
`ValueType` is retained when present, otherwise the JSON value type is inferred.

Snapshot time is `source_timestamp`; history uses `timestamp`. Missing/naive
snapshot timestamps fail at the governed boundary. Legacy history parsers still
skip unusable timestamps, but the governed boundary detects any lost item and
fails the operation. Units prefer explicit sample/response units, then AF
DefaultUnitsName for governed operations. No engineering conversion is inferred.

The existing `/snapshots`, `/snapshots/{id}`, `/timeseries/{id}` models expose
these additive fields. These routes read the local store; they do not call PI.
Quality is source evidence, not an alarm, failure, condition score or PdM result.
The shared numeric `condition-reading` schema stays unchanged: adoption into a
vendor-neutral NADI projection contract belongs to NADI-ING-PI-001.

## Upgrade existing PI store

Migration `migrations/004_signal_quality_fields.sql` adds nullable columns in a
transaction with `ADD COLUMN IF NOT EXISTS` and no data rewrites. Run migrations
in numeric order: 001_init → 002_collect_runs → 003_backfill_progress →
004_signal_quality_fields. It requires existing PI tables, deliberately failing on a wrong/missing store. Apply only
after reviewing the existing owning database and migration window. This task
has **not** executed it against PostgreSQL/TimescaleDB or production.

Before starting upgraded workers/API, apply that migration deliberately to the
existing PI Collector store. `Base.metadata.create_all` / `init-db` creates fresh
test/development tables but does not add columns to existing tables. If an
experimental historical
`002_signal_quality_fields.sql` (including the old `d23f848` variant) was
previously applied outside main, running final `004` remains safe: every
addition uses `ADD COLUMN IF NOT EXISTS`, preserving existing columns/data and
adding missing evidence such as `source_value`. The renamed file is the final
migration; do not retain a second numbered 002 in the migration directory.
Old rows keep numeric values, timestamps and flags; new fields remain null because old text/digital
payloads cannot be reconstructed. History, cursors, volumes and DB ownership
must be preserved.

For code rollback, leave the nullable columns in place and revert the application
release; do not drop evidence or reset tables. Review PostgreSQL/TimescaleDB
ALTER lock/transaction behavior for the actual installation in a separate
runtime migration task. Offline tests verify SQL/model column parity and legacy
row preservation in temporary SQLite, not a production migration certificate.
