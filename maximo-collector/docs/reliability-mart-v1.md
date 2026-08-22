# Reliability Mart v1

MX-009R adds a persistence boundary after `CanonicalCollector`. The Mart
stores validated NADI Contract v1 records, not OSLC responses:

```text
Maximo → OslcClient → CanonicalCollector → MartWriter → PostgreSQL
```

The legacy `equipment`, `work_order`, and other collector tables remain in
place. They are not renamed or replaced by the six canonical Mart tables.

## Entities and identity

The tables are:

`asset_master`, `maintenance_event`, `fmea_assessment`, `rcfa_analysis`,
`asset_health_assessment`, and `overhaul_event`.

Every table uses `canonical_id` as its primary key. The writer supports only
Contract v1 (`contract_version = "1.0"`) and rejects arbitrary entity names.
The legacy maintenance `id` is retained as a compatibility column; it is not
the Mart conflict key.

## Stored canonical boundary

Business fields are stored as relational columns. The approved structural
blocks are stored as JSON/JSONB:

- `provenance`
- `relationship_evidence`
- `sources` (only the contract-approved `sources.maximo` block)
- `unresolved_source_attributes` for Overhaul

There is no raw payload, response, OSLC blob, or generic source dump column.
`progress` and Asset `criticality` remain JSON scalar columns because Contract
v1 permits number, integer, string, or null values.

Source timestamps are parsed as timezone-aware ISO-8601 values. PostgreSQL uses
`TIMESTAMPTZ`; the SQLite test adapter preserves the timezone string so local
round-trip tests exercise the same semantic rule.

## Scope defense in depth

The collector already restricts reads to BSR/IP. `MartWriter` repeats that
authorization boundary before a write:

- `provenance.source_system` must be `MAXIMO`;
- `provenance.source_site` must be `BSR`;
- `provenance.source_organization` must be `IP`;
- non-null top-level `site_code` and `organization_code` must agree;
- present `sources.maximo.siteid` and `sources.maximo.orgid` must agree.

Any mismatch raises a classified `ScopeViolation` before opening a write
transaction. The schema remains capable of representing future sites; the
current ingestion service is not.

## Upsert and transactions

`MartWriter.persist_collection()` validates the complete collection before the
database transaction starts. Each entity collection is written in its own
transaction. A database error or rejected batch cannot be reported as a
partial successful batch.

Upserts are based only on `canonical_id`:

- first insert sets `mart_created_at` and `mart_updated_at`;
- identical input is counted as unchanged;
- a mutable change updates business/provenance/evidence/source columns and
  `mart_updated_at`;
- `mart_created_at` and `canonical_id` are preserved.

The implementation uses SQLAlchemy ORM operations so the hermetic tests can
use SQLite while the operational database remains PostgreSQL. The numbered
PostgreSQL migration is `migrations/002_reliability_mart.sql`; its intentional
rollback companion is `002_reliability_mart_down.sql`.

## Logical relationships

v1 uses indexed logical references rather than hard foreign keys. A referenced
record may arrive in a later resource transaction, so missing targets do not
reject an otherwise valid canonical record.

```text
asset_master
    ▲
    │ asset_ref / equipment_id
    ├── fmea_assessment
    ├── asset_health_assessment
    └── maintenance_event
                     ▲
                     │ overhaul_event.workorder_ref
               overhaul_event

rcfa_analysis
    ├── asset_ref      null / UNRESOLVED
    ├── workorder_ref  null / UNRESOLVED
    └── location_ref   null / UNRESOLVED
```

The Work Order identity invariant is explicit:

```text
overhaul_event.workorder_ref
    = maintenance_event.work_order_id
```

It must not target `maintenance_event.canonical_id`. The Overhaul asset path is
already resolved by the Collector when possible; the Mart stores the canonical
result and never calls Maximo during persistence.

`MartIntegrityAuditor.audit()` reports counts for resolved and unresolved
Asset and Work Order references. It does not delete or reject unresolved rows.

## Operational handoff

MX-010R can query the six canonical tables by `canonical_id`, site/org, status,
timestamps, Asset references, and Work Order references. It can call the
integrity auditor for reference-health summaries without understanding Maximo
object structures. Full production initial load and Mart read APIs remain
separate tasks.
